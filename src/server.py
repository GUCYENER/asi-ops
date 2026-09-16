"""Alert Storm Correlator — stdlib HTTP sunucusu.

Harici bagimlilik yoktur (http.server + json). Aksiyon durumu bellek icinde tutulur;
brifing kalici veritabanini acikca kapsam disi birakiyor.
"""

import json
import os
import sys
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(BASE_DIR)
WEB_DIR = os.path.join(BASE_DIR, "web")

sys.path.insert(0, BASE_DIR)
import correlator  # noqa: E402
import explain as explain_mod  # noqa: E402

STATE = {"result": None, "actions": {}, "narratives": {}}

CONTENT_TYPES = {
    ".html": "text/html; charset=utf-8",
    ".js": "application/javascript; charset=utf-8",
    ".css": "text/css; charset=utf-8",
}


def compute(data_dir):
    result = correlator.run(data_dir)
    for card in result["events"]:
        STATE["actions"][card["id"]] = {"owner": card["owner"], "status": card["status"]}
    STATE["result"] = result
    return result


def current_payload():
    result = STATE["result"]
    for card in result["events"]:
        action = STATE["actions"].get(card["id"])
        if action:
            card["owner"] = action["owner"]
            card["status"] = action["status"]
        card["narrative"] = STATE["narratives"].get(card["id"])
    return result


class Handler(BaseHTTPRequestHandler):
    def log_message(self, fmt, *args):
        pass  # demo sirasinda konsolu temiz tut

    def _send(self, code, body, content_type="application/json; charset=utf-8"):
        payload = body if isinstance(body, bytes) else json.dumps(body, ensure_ascii=False).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(payload)))
        self.end_headers()
        self.wfile.write(payload)

    def do_GET(self):
        path = urlparse(self.path).path

        if path == "/api/data":
            self._send(200, current_payload())
            return

        if path.startswith("/api/explain/"):
            event_id = path.rsplit("/", 1)[-1]
            card = next((c for c in STATE["result"]["events"] if c["id"] == event_id), None)
            if not card:
                self._send(404, {"error": "olay bulunamadi"})
                return
            narrative, source = explain_mod.narrate(card)
            STATE["narratives"][event_id] = {"text": narrative, "source": source}
            self._send(200, {"text": narrative, "source": source})
            return

        rel = "index.html" if path in ("/", "") else path.lstrip("/")
        file_path = os.path.join(WEB_DIR, rel)
        if not os.path.abspath(file_path).startswith(WEB_DIR) or not os.path.isfile(file_path):
            self._send(404, {"error": "bulunamadi"})
            return
        ext = os.path.splitext(file_path)[1]
        with open(file_path, "rb") as fh:
            self._send(200, fh.read(), CONTENT_TYPES.get(ext, "application/octet-stream"))

    def do_POST(self):
        path = urlparse(self.path).path
        if not path.startswith("/api/actions/"):
            self._send(404, {"error": "bulunamadi"})
            return
        event_id = path.rsplit("/", 1)[-1]
        if event_id not in STATE["actions"]:
            self._send(404, {"error": "olay bulunamadi"})
            return
        length = int(self.headers.get("Content-Length", 0))
        try:
            body = json.loads(self.rfile.read(length) or b"{}")
        except json.JSONDecodeError:
            self._send(400, {"error": "gecersiz JSON"})
            return
        action = STATE["actions"][event_id]
        if "owner" in body:
            action["owner"] = str(body["owner"])[:80]
        if "status" in body:
            action["status"] = str(body["status"])[:40]
        self._send(200, {"id": event_id, **action})


def main():
    data_dir = sys.argv[1] if len(sys.argv) > 1 else os.path.join(ROOT_DIR, "data", "katilimci_paketi")
    port = int(os.environ.get("PORT", "8000"))

    print("Veri okunuyor: %s" % data_dir)
    result = compute(data_dir)
    metrics = result["metrics"]
    print("%d alarm islendi -> %d olay karti (gurultu %d, belirsiz %d)"
          % (metrics["total_alarms"], metrics["event_count"],
             metrics["noise_count"], metrics["unclear_count"]))
    print("Arayuz: http://localhost:%d" % port)
    HTTPServer(("127.0.0.1", port), Handler).serve_forever()


if __name__ == "__main__":
    main()
