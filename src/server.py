"""Local demo HTTP API, static allowlist and in-memory action history."""
from copy import deepcopy
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
import json
import threading
from urllib.parse import parse_qs, urlsplit

from .narrative import Narrator

STATUSES = {"open", "investigating", "resolved"}
TRANSITIONS = {"open": {"open", "investigating"}, "investigating": STATUSES, "resolved": {"resolved", "open"}}


class State:
    def __init__(self, report, narrator=None):
        self.report = report
        self.lock = threading.Lock()
        self.narrator = narrator or Narrator()

    def snapshot(self, full=False):
        with self.lock:
            result = deepcopy({k: v for k, v in self.report.items() if full or k != "alarms"})
        result["narrative"] = self.narrator.status()
        return result

    def incident(self, ident):
        with self.lock:
            found = next((x for x in self.report["incidents"] + self.report.get("review_candidates", []) if x["id"] == ident), None)
            return deepcopy(found)

    def update_action(self, ident, body):
        if not isinstance(body, dict):
            raise ValueError("JSON nesnesi gerekli.")
        owner, status, note, version = (body.get(k) for k in ("owner", "status", "note", "version"))
        if not isinstance(owner, str) or not 1 <= len(owner.strip()) <= 120:
            raise ValueError("Sorumlu alanı 1–120 karakter olmalı.")
        if not isinstance(status, str) or status not in STATUSES:
            raise ValueError("Geçersiz durum.")
        if not isinstance(note, str) or len(note) > 1000:
            raise ValueError("Not en fazla 1000 karakter olmalı.")
        if type(version) is not int:
            raise ValueError("Sayısal sürüm gerekli.")
        with self.lock:
            incident = next((x for x in self.report["incidents"] + self.report.get("review_candidates", []) if x["id"] == ident), None)
            if incident is None:
                raise LookupError("Olay bulunamadı.")
            action = incident["action"]
            if version != action["version"]:
                raise RuntimeError("Aksiyon başka bir işlemde güncellendi. Yenileyip tekrar deneyin.")
            if status not in TRANSITIONS[action["status"]]:
                raise ValueError("Önce incelemeye alın; çözülmüş kaydı tekrar açarak inceleyebilirsiniz.")
            if status != action["status"] and status == "resolved" and not note.strip():
                raise ValueError("Çözüm kaydı için doğrulama notu gerekli.")
            entry = {"at": datetime.now(timezone.utc).isoformat(timespec="seconds"), "from_status": action["status"],
                     "to_status": status, "previous_owner": action["owner"], "owner": owner.strip(), "note": note.strip()}
            action["owner_kind"] = "user_entered" if owner.strip() != action["owner"] else action["owner_kind"]
            action.update(owner=owner.strip(), status=status, version=version + 1)
            action["history"].append(entry)
            return deepcopy(action)


def make_server(report, host="127.0.0.1", port=8000, narrator=None):
    state = State(report, narrator)
    static = Path(__file__).resolve().parent.parent / "static"
    assets = {"/": ("index.html", "text/html"), "/app.js": ("app.js", "text/javascript"),
              "/styles.css": ("styles.css", "text/css")}

    class Handler(BaseHTTPRequestHandler):
        def setup(self):
            super().setup()
            self.connection.settimeout(15)

        def send(self, status, value, mime="application/json", download=False):
            data = json.dumps(value, ensure_ascii=False).encode() if mime == "application/json" else value
            self.send_response(status)
            self.send_header("Content-Type", mime + "; charset=utf-8")
            self.send_header("Content-Length", str(len(data)))
            self.send_header("Cache-Control", "no-store")
            self.send_header("X-Content-Type-Options", "nosniff")
            self.send_header("Content-Security-Policy", "default-src 'self'; script-src 'self'; style-src 'self'; img-src 'self' data:; connect-src 'self'; frame-ancestors 'none'; base-uri 'none'; form-action 'self'")
            if download:
                self.send_header("Content-Disposition", 'attachment; filename="asi-ops-report.json"')
            self.end_headers()
            self.wfile.write(data)

        def local_request(self):
            # Bind locally and reject browser requests whose host/origin is foreign.
            host_header = self.headers.get("Host", "")
            allowed = {f"127.0.0.1:{self.server.server_port}", f"localhost:{self.server.server_port}"}
            origin = self.headers.get("Origin")
            return host_header in allowed and (not origin or origin == "http://" + host_header)

        def do_GET(self):
            if not self.local_request():
                return self.send(403, {"error": "Yalnızca yerel arayüz erişimi kabul edilir."})
            url = urlsplit(self.path)
            if url.path in assets:
                filename, mime = assets[url.path]
                return self.send(200, (static / filename).read_bytes(), mime)
            if url.path == "/api/health":
                return self.send(200, {"status": "ok", "schema_version": state.report["schema_version"]})
            if url.path in {"/api/report", "/api/export"}:
                full = url.path == "/api/export"
                return self.send(200, state.snapshot(full), download=full)
            if url.path == "/api/alarms":
                query = parse_qs(url.query)
                try:
                    offset = max(0, int(query.get("offset", [0])[0]))
                    limit = min(200, max(1, int(query.get("limit", [50])[0])))
                    decision = query.get("decision", [""])[0]
                    if decision and decision not in {"incident", "noise", "uncertain"}:
                        raise ValueError()
                except ValueError:
                    return self.send(400, {"error": "Geçersiz filtre veya sayfalama."})
                ident, search = query.get("incident_id", [""])[0], query.get("q", [""])[0].lower()[:200]
                rows = [a for a in state.report["alarms"] if (not decision or a["decision"] == decision)
                        and (not ident or a["incident_id"] == ident or a.get("review_candidate_id") == ident) and (not search or search in " ".join(
                            str(a[k]) for k in ["alarm_id", "host", "service", "alarm_type", "message", "reason"]).lower())]
                return self.send(200, {"total": len(rows), "offset": offset, "limit": limit, "items": rows[offset:offset + limit]})
            self.send(404, {"error": "Adres bulunamadı."})

        def do_POST(self):
            if not self.local_request():
                return self.send(403, {"error": "Yabancı kaynaktan değişiklik kabul edilmedi."})
            if self.headers.get("Content-Type", "").split(";")[0] != "application/json":
                return self.send(415, {"error": "Content-Type application/json olmalı."})
            try:
                size = int(self.headers.get("Content-Length", "0"))
                if not 0 < size <= 8192:
                    return self.send(413, {"error": "Gövde 1–8192 bayt olmalı."})
                body = json.loads(self.rfile.read(size))
                parts = urlsplit(self.path).path.strip("/").split("/")
                if len(parts) != 4 or parts[:2] != ["api", "incidents"]:
                    return self.send(404, {"error": "Adres bulunamadı."})
                ident, operation = parts[2:]
                if operation == "action":
                    return self.send(200, state.update_action(ident, body))
                if operation == "narrative":
                    incident = state.incident(ident)
                    if not incident:
                        raise LookupError("Olay bulunamadı.")
                    return self.send(200, state.narrator.explain(incident))
                self.send(404, {"error": "İşlem bulunamadı."})
            except (ValueError, UnicodeDecodeError) as exc:
                self.send(400, {"error": str(exc)})
            except LookupError as exc:
                self.send(404, {"error": str(exc)})
            except RuntimeError as exc:
                self.send(409, {"error": str(exc)})

        def log_message(self, format, *args):
            # No request bodies, API keys or provider responses in logs.
            pass

    server = ThreadingHTTPServer((host, port), Handler)
    server.state = state
    return server
