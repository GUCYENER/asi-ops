"""Deterministic, evidence-based alarm correlation. Python standard library only.

No hidden labels, alarm-id ranges, event counts, service names or dates are used
as detection rules. Heuristics are explicit and exported in every decision.
"""
from __future__ import annotations

from collections import Counter, defaultdict, deque
from datetime import datetime, timedelta
from pathlib import Path
import csv
import hashlib
import json
import math
import re
import statistics
import time

from . import history

# Bonus B3: benzer gecmis olay arsivi (opsiyonel, yoksa ozellik sessizce kapanir)
HISTORY_ARCHIVE = history.load_archive(
    str(Path(__file__).resolve().parent.parent / "data" / "AO_SA1_Historical_Data_5_Cases"))

VERSION = "1.1"
STRONG = {
    "network": {"network_down", "pkt_loss"},
    "storage": {"disk_full"},
    "memory": {"gc_pressure", "oom_risk"},
    "external": {"ext_unreach", "ext_slow"},
    "batch": {"batch_overlap"},
}
SYMPTOMS = {
    "network": {"network_down", "pkt_loss", "network_flap", "timeout", "conn_refused", "http_5xx", "thread_pool", "latency_high"},
    "storage": {"disk_full", "db_write_fail", "db_conn_pool", "txn_fail", "timeout", "http_5xx", "latency_high"},
    "memory": {"mem_high", "gc_pressure", "oom_risk", "timeout", "http_5xx", "latency_high"},
    "external": {"ext_unreach", "ext_slow", "txn_fail", "timeout", "http_5xx", "latency_high", "conn_refused"},
    "batch": {"batch_overlap", "batch_slow", "cpu_high", "db_conn_pool", "latency_high", "timeout", "queue_backlog"},
    "unresolved": set(),
}
GENERIC = {"mem_high", "cpu_high", "latency_high", "network_flap", "disk_warn"}
MAINTENANCE = {"cert_expiry", "backup_warn", "ntp_drift", "log_rotate"}
KNOWN = set().union(*SYMPTOMS.values(), GENERIC, MAINTENANCE)
LABELS = {"network": "Ortak ağ erişim sorunu", "storage": "Depolama kapasitesi ve yazma sorunu",
          "memory": "Zamana yayılan bellek baskısı", "external": "Dış servis erişim sorunu",
          "batch": "Batch çakışması ve kaynak baskısı", "unresolved": "Birlikte incelenmesi gereken belirtiler"}
OWNERS = {"network": "Ağ nöbetçisi", "storage": "DBA nöbetçisi", "memory": "Uygulama / JVM nöbetçisi",
          "external": "Entegrasyon nöbetçisi", "batch": "Batch operasyon nöbetçisi", "unresolved": "Operasyon nöbetçisi"}
ACTIONS = {
    "network": "Belirtilen veri merkezi/kabinde bağlantı ve port durumunu doğrula; etkilenen host'ların erişimini karşılaştır.",
    "storage": "Disk/tablespace kapasitesini ve yazma hatalarını doğrula; alan büyütme veya temizlik öncesinde DBA değerlendirmesi yap.",
    "memory": "Heap ve GC eğilimini kontrol et; trafik/kapasite artışı ile bellek sızıntısı ihtimalini ayır.",
    "external": "Gateway'den dış hedefe erişim ve hata kodlarını kontrol et; sağlayıcı sorunu ile yerel çıkış ağını ayır.",
    "batch": "Çakışan işlerin zamanlarını ve ortak kaynak havuzunu incele; yeniden zamanlama kararını batch ekibiyle doğrula.",
    "unresolved": "Ortak belirtileri incele; kök hipotezi için servis ve bağımlılık durumunu doğrula.",
}
ALTERNATIVES = {
    "network": [("Bağımsız host veya uygulama arızaları", "Aynı fiziksel alandaki erken ağ belirtileri ortak ağ açıklamasını destekliyor; hostlar arasındaki yayılım ayrıca incelenmeli.", "Switch/port ölçümleri verilmedi; kesin cihaz kökü bilinmiyor.")],
    "storage": [("Bağımsız bağlantı havuzu problemi", "Disk doluluk sinyali, yalnızca aşağıdaki timeout/havuz belirtilerinden daha doğrudan kanıt.", "Disk ve tablespace ölçümüyle doğrulanmalı; alarm gecikmesi mümkün.")],
    "memory": [("Trafik veya kapasite artışı", "GC/OOM sinyalleri bellek baskısını destekler; tek başına sızıntıyı kanıtlamaz.", "Heap profili ve trafik ölçümü yok; memory leak kesin değildir.")],
    "external": [("Yerel ağ çıkışı veya gateway sorunu", "Dış hedefi belirten erişim alarmı mevcut; sağlayıcının kendisindeki arızayı tek başına kanıtlamaz.", "Farklı çıkış noktalarından erişim ve sağlayıcı durumu kontrol edilmeli.")],
    "batch": [("Bağımsız veritabanı kapasite sorunu", "Çakışma alarmı ve ortak kaynak kullanan işler birlikte değerlendirilir.", "Yük/SQL ölçümü yok; batch→kaynak nedenselliği doğrulanmalı.")],
    "unresolved": [("Birden fazla bağımsız olay", "Yalnızca tekrarlayan belirtiler bulundu; güçlü kök sinyali yok.", "Kök neden belirsizdir; insan incelemesi gerekir.")],
}


def iso(dt):
    return dt.isoformat(timespec="seconds")


def read_csv(path):
    with path.open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def parse_message(message):
    target = re.search(r"([\w-]+) servisine", message)
    if not target:
        target = re.search(r"^([\w-]+) baglantisi", message)
    if not target:
        target = re.search(r"Dis servis ([\w-]+)", message)
    values = {}
    patterns = {"percent": r"yuzde\s+(\d+(?:[.,]\d+)?)", "milliseconds": r"(\d+(?:[.,]\d+)?)\s*ms\b",
                "days": r"(\d+)\s*gun\b", "http_status": r"HTTP\s+(\d{3})\b"}
    for key, pattern in patterns.items():
        match = re.search(pattern, message)
        if match:
            values[key] = float(match[1].replace(",", "."))
    return (target[1] if target else None), values


def load_inputs(data_dir):
    data_dir = Path(data_dir)
    alarm_path = data_dir / "alarms.json"
    if alarm_path.exists():
        raw = json.loads(alarm_path.read_text(encoding="utf-8-sig"))
        if not isinstance(raw, list):
            raise ValueError("alarms.json bir JSON dizisi olmalı.")
    else:
        alarm_path = data_dir / "alarms.csv"
        raw = read_csv(alarm_path)
    inventory = read_csv(data_dir / "host_inventory.csv")
    dependencies = read_csv(data_dir / "service_dependencies.csv")
    hosts = {}
    for row in inventory:
        if not all(row.get(k) for k in ["host", "servis", "veri_merkezi", "kabin", "ortam", "is_kritikligi"]):
            raise ValueError("Envanter alanı eksik.")
        if row["host"] in hosts:
            raise ValueError("Envanterde tekrar host: " + row["host"])
        if row["is_kritikligi"] not in {"kritik", "yuksek", "orta", "dusuk"}:
            raise ValueError("Envanterde bilinmeyen iş kritikliği.")
        hosts[row["host"]] = row
    alarms, seen, warnings = [], set(), []
    aware = set()
    for index, original in enumerate(raw, 1):
        if not isinstance(original, dict):
            raise ValueError(f"Alarm {index}: nesne bekleniyor.")
        required = ["alarm_id", "timestamp", "source_system", "host", "service", "severity", "alarm_type", "message"]
        if any(k not in original or original[k] is None or original[k] == "" for k in required):
            raise ValueError(f"Alarm {index}: zorunlu alan eksik; kısmi işleme yapılmadı.")
        row = {k: original[k] for k in required}
        if any(not isinstance(row[k], str) for k in required if k != "severity"):
            raise ValueError(f"Alarm {index}: metin alanı geçersiz.")
        if row["alarm_id"] in seen:
            raise ValueError("Tekrarlanan alarm_id: " + row["alarm_id"])
        seen.add(row["alarm_id"])
        try:
            if isinstance(row["severity"], bool) or str(row["severity"]) not in {"1", "2", "3", "4", "5"}:
                raise ValueError()
            row["severity"] = int(row["severity"])
            dt = datetime.fromisoformat(row["timestamp"].replace("Z", "+00:00"))
        except (ValueError, TypeError):
            raise ValueError(f"Alarm {index}: zaman veya severity geçersiz.")
        aware.add(dt.tzinfo is not None)
        host = hosts.get(row["host"])
        if host is None:
            raise ValueError("Envanterde bulunamayan host: " + row["host"])
        tags = original.get("tags", {k: original.get(k) for k in ["veri_merkezi", "kabin", "ortam"]})
        if not isinstance(tags, dict):
            raise ValueError(f"Alarm {index}: tags nesne olmalı.")
        if row["service"] != host["servis"] or any(tags.get(k) != host[k] for k in ["veri_merkezi", "kabin", "ortam"]):
            raise ValueError(f"Alarm {index}: envanter/etiket uyuşmazlığı.")
        row["tags"] = {k: tags[k] for k in ["veri_merkezi", "kabin", "ortam"]}
        row["_dt"] = dt
        row["message_target"], row["numeric_signals"] = parse_message(row["message"])
        alarms.append(row)
    if not alarms:
        raise ValueError("Alarm dosyası boş.")
    if len(aware) > 1:
        raise ValueError("Saat dilimli ve saat dilimsiz kayıtlar karışık; açık normalizasyon gerekir.")
    for dep in dependencies:
        if not all(dep.get(k) for k in ["kaynak_servis", "hedef_servis", "bagimlilik_tipi", "kritiklik"]):
            raise ValueError("Bağımlılık alanı eksik.")
        if dep["bagimlilik_tipi"] not in {"senkron", "asenkron"}:
            raise ValueError("Bilinmeyen bağımlılık tipi.")
    alarms.sort(key=lambda a: (a["_dt"], a["alarm_id"]))
    if not next(iter(aware)):
        warnings.append("Zaman damgalarında saat dilimi yok; dosyanın yerel zamanı korunuyor.")
    unknown = sorted({a["alarm_type"] for a in alarms} - KNOWN)
    if unknown:
        warnings.append("Bilinmeyen alarm tipleri belirsiz incelemeye alınır: " + ", ".join(unknown))
    manifest = {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in
                [alarm_path, data_dir / "host_inventory.csv", data_dir / "service_dependencies.csv"]}
    return alarms, hosts, dependencies, warnings, manifest


class Graph:
    def __init__(self, dependencies):
        self.adj, self.reverse = defaultdict(set), defaultdict(set)
        for d in dependencies:
            self.adj[d["kaynak_servis"]].add(d["hedef_servis"])
            self.reverse[d["hedef_servis"]].add(d["kaynak_servis"])
        self.cache = {}

    def path(self, source, target):
        key = (source, target)
        if key in self.cache:
            return self.cache[key]
        queue, seen = deque([(source, [source])]), {source}
        while queue:
            node, path = queue.popleft()
            if node == target:
                self.cache[key] = path
                return path
            for nxt in sorted(self.adj[node]):
                if nxt not in seen:
                    seen.add(nxt)
                    queue.append((nxt, path + [nxt]))
        self.cache[key] = None
        return None

    def dependents(self, roots):
        seen, queue = set(roots), deque(roots)
        while queue:
            node = queue.popleft()
            for nxt in sorted(self.reverse[node]):
                if nxt not in seen:
                    seen.add(nxt); queue.append(nxt)
        return seen


def split_runs(rows, gap_minutes):
    groups = []
    for row in sorted(rows, key=lambda a: (a["_dt"], a["alarm_id"])):
        if not groups or (row["_dt"] - groups[-1][-1]["_dt"]).total_seconds() > gap_minutes * 60:
            groups.append([])
        groups[-1].append(row)
    return groups


def baseline_stats(alarms):
    origin = alarms[0]["_dt"].replace(minute=alarms[0]["_dt"].minute // 10 * 10, second=0, microsecond=0)
    bins = int((alarms[-1]["_dt"] - origin).total_seconds() // 600) + 1
    by_type = defaultdict(lambda: [0] * bins)
    local = Counter()
    for a in alarms:
        idx = int((a["_dt"] - origin).total_seconds() // 600)
        a["_bin"] = idx
        by_type[a["alarm_type"]][idx] += 1
        local[(a["service"], a["alarm_type"], idx)] += 1
    stats = {}
    for typ, counts in sorted(by_type.items()):
        median, mean = statistics.median(counts), statistics.mean(counts)
        sd = statistics.pstdev(counts)
        stats[typ] = {"alarm_type": typ, "count": sum(counts), "bins": counts,
                      "median": median, "denominator": max(median, 1), "peak": max(counts),
                      "ratio": round(max(counts) / max(median, 1), 3),
                      "peak_z": round((max(counts) - mean) / sd, 3) if sd else 0.,
                      "role": "yoğunlaşmış" if max(counts) / max(median, 1) >= 4 else "yaygın / bağlam gerekli"}
    return origin, stats, local


def rising_memory(rows, before, window_start):
    """Longest rising subsequence with <=8min steps; isolated high values don't seed a trend."""
    selected = []
    by_host = defaultdict(list)
    for a in rows:
        if a["alarm_type"] == "mem_high" and window_start <= a["_dt"] <= before and "percent" in a["numeric_signals"]:
            by_host[a["host"]].append(a)
    for items in by_host.values():
        paths = [[i] for i in range(len(items))]
        for i in range(len(items)):
            for j in range(i):
                gap = (items[i]["_dt"] - items[j]["_dt"]).total_seconds()
                delta = items[i]["numeric_signals"]["percent"] - items[j]["numeric_signals"]["percent"]
                if 30 <= gap <= 480 and 0 < delta <= 15 and len(paths[j]) + 1 > len(paths[i]):
                    paths[i] = paths[j] + [i]
        valid = [path for path in paths if len(path) >= 4 and
                 (items[path[-1]]["_dt"] - items[path[0]]["_dt"]).total_seconds() >= 600 and
                 items[path[-1]]["numeric_signals"]["percent"] - items[path[0]]["numeric_signals"]["percent"] >= 6]
        if valid:
            best = max(valid, key=lambda v: (len(v), items[v[-1]]["numeric_signals"]["percent"]))
            # A stray early low reading can extend an increasing subsequence.
            # Split unusually large jumps relative to this host's own steps.
            deltas = [items[b]["numeric_signals"]["percent"] - items[a]["numeric_signals"]["percent"]
                      for a, b in zip(best, best[1:])]
            typical = statistics.median(deltas)
            segments = [[best[0]]]
            for previous, current, delta in zip(best, best[1:], deltas):
                if delta > typical * 2.5:
                    segments.append([])
                segments[-1].append(current)
            best = max(segments, key=len)
            if len(best) >= 4 and (items[best[-1]]["_dt"] - items[best[0]]["_dt"]).total_seconds() >= 600:
                selected.extend(items[i] for i in best)
    return selected


def find_episodes(alarms, graph, external_tail_minutes=22):
    episodes = []
    for kind, types in STRONG.items():
        grouped = defaultdict(list)
        for a in alarms:
            if a["alarm_type"] in types:
                key = (a["tags"]["veri_merkezi"], a["tags"]["kabin"]) if kind == "network" else a["service"]
                grouped[key].append(a)
        for scope, rows in sorted(grouped.items()):
            for seeds in split_runs(rows, 30 if kind == "memory" else 10):
                if len(seeds) < (3 if kind == "network" else 2):
                    continue
                original_start, end = seeds[0]["_dt"], seeds[-1]["_dt"]
                roots = {a["service"] for a in seeds}
                trend = []
                if kind == "memory":
                    trend = rising_memory([a for a in alarms if a["service"] in roots], original_start, original_start - timedelta(minutes=75))
                seeds = sorted(seeds + trend, key=lambda a: (a["_dt"], a["alarm_id"]))
                start = seeds[0]["_dt"]
                tail = {"network": 15, "storage": 22, "memory": 10, "external": external_tail_minutes, "batch": 30}[kind]
                until = end + timedelta(minutes=tail)
                resources, jobs = set(), set()
                if kind == "batch":
                    jobs = {s for root in roots for s in graph.reverse[root] if any(
                        a["service"] == s and a["alarm_type"] == "batch_slow" and start <= a["_dt"] <= until for a in alarms)}
                    support = Counter(target for job in jobs for target in graph.adj[job] if target not in roots)
                    resources = {s for s, n in support.items() if n >= 2}
                affected = graph.dependents(roots | resources) | jobs
                scope_text = "/".join(scope) if isinstance(scope, tuple) else scope
                ident = "INC-" + hashlib.sha256(f"{kind}|{scope_text}|{iso(start)}".encode()).hexdigest()[:8].upper()
                episodes.append({"id": ident, "kind": kind, "scope": scope_text, "roots": roots,
                                 "location": scope if kind == "network" else None, "seeds": seeds,
                                 "seed_ids": {a["alarm_id"] for a in seeds}, "start": start, "seed_end": end,
                                 "symptom_start": original_start if kind == "memory" else start - timedelta(minutes=1),
                                 "until": until, "affected": affected, "resources": resources, "jobs": jobs,
                                 "trend": trend})
    return sorted(episodes, key=lambda e: (e["start"], e["kind"], e["scope"]))


def candidate_score(a, e, graph, local):
    if a["alarm_id"] in e["seed_ids"]:
        return {"incident_id": e["id"], "score": 100., "codes": ["root_signature"], "reasons": ["Kök belirti veya yükselen seri kuralını karşılayan öncül."], "path": []}
    if not (e["symptom_start"] <= a["_dt"] <= e["until"]) or a["alarm_type"] not in SYMPTOMS[e["kind"]]:
        return None
    service, target, typ = a["service"], a["message_target"], a["alarm_type"]
    local_network = e["location"] == (a["tags"]["veri_merkezi"], a["tags"]["kabin"])
    if service not in e["affected"] and not local_network:
        return None
    paths = [graph.path(service, root) for root in e["roots"] | e["resources"]]
    paths = [p for p in paths if p]
    path = min(paths, key=lambda p: (len(p), p)) if paths else []
    score, codes, reasons = 3., ["type_compatible", "time_window"], ["Belirti ailesi ve adayın zaman penceresi uyumlu."]
    if service in e["roots"]:
        score += 4; codes.append("same_root_service"); reasons.append("Kök adayının servisiyle aynı servis.")
    elif path:
        score += max(2., 5. - .6 * (len(path) - 1)); codes.append("dependency_path")
        reasons.append("Bağımlılık yolu: " + " → ".join(path))
    if local_network and e["kind"] == "network":
        score += 5; codes.append("same_fault_domain"); reasons.append("Aynı veri merkezi ve kabin: " + e["scope"])
    if e["kind"] == "batch" and (service in e["jobs"] or service in e["resources"]):
        score += 3; codes.append("shared_resource"); reasons.append("Çakışan iş veya ortak kaynakla ilişkili servis.")
    if target:
        relevant = target in e["roots"] | e["resources"] or any(graph.path(target, r) for r in e["roots"] | e["resources"])
        if relevant and service != target and graph.path(service, target):
            score += 6; codes.append("validated_message_target"); reasons.append("Mesaj hedefi grafikte doğrulanıyor: " + target)
        elif not relevant:
            score -= 3; codes.append("different_message_target"); reasons.append("Mesaj hedefi bu kökü desteklemiyor: " + target)
        else:
            codes.append("unverified_message_target"); reasons.append("Mesaj hedefi var; kaynak→hedef yolu doğrulanamadı.")
    if typ in GENERIC:
        local_count = local[(service, typ, a["_bin"])]
        # Generic alarms require local repetition as well as incident context.
        if local_count < 3:
            return None
        score -= 1; codes.append("local_repetition"); reasons.append(f"Aynı servis/tip için 10 dakikada {local_count} kayıt.")
        value = a["numeric_signals"].get("percent")
        if typ == "mem_high" and e["kind"] == "memory" and e["trend"]:
            floor = min(t["numeric_signals"]["percent"] for t in e["trend"])
            if value is None or value < floor:
                return None
        if typ == "network_flap" and not local_network:
            return None
    else:
        score += 2; codes.append("specific_symptom"); reasons.append("Genel kaynak uyarısından daha özgül hata belirtisi.")
    if e["start"] <= a["_dt"] <= e["seed_end"]:
        score += 1; codes.append("anchor_overlap"); reasons.append("Doğrudan kök belirtileriyle zaman çakışması.")
    return {"incident_id": e["id"], "score": round(score, 3), "codes": codes, "reasons": reasons, "path": path}


def noise_decision(a, stats):
    typ = a["alarm_type"]
    ratio = stats[typ]["ratio"]
    if typ == "cert_expiry" and a["numeric_signals"].get("days", 0) >= 7:
        return "noise", "Yakın kesintiye bağlanan kanıt yok; sertifika için en az 7 gün var. Bakım uyarısı olarak korundu.", ["maintenance_horizon"]
    if typ in MAINTENANCE and a["severity"] <= 3 and ratio <= 3:
        return "noise", f"Bakım tipi, düşük zamansal yoğunlaşma ({ratio:.2f}×) ve olay bağlantısı bulunmaması; gürültü adayı.", ["maintenance", "low_concentration", "no_incident_evidence"]
    if typ in GENERIC and a["severity"] <= 3 and ratio <= 3:
        return "noise", f"Yaygın tip ({ratio:.2f}×); kök, trend veya yerel olay bağlamı bulunamadı. Gürültü adayı; kesin etiket değil.", ["low_concentration", "no_incident_evidence"]
    return "uncertain", "Yeterli olay bağlantısı yok; güçlü veya bilinmeyen belirti sessizce elenmedi.", ["insufficient_evidence"]


def public_alarm(a):
    return {k: v for k, v in a.items() if not k.startswith("_")}


def connection_evidence(alarms, seeds, graph):
    """Corroborate refused targets with observed target network alarms, not invented edges."""
    result = []
    targets = Counter(a["message_target"] for a in alarms if a["alarm_type"] == "conn_refused" and a["message_target"])
    for target, count in targets.most_common():
        roots = [a for a in seeds if a["service"] == target and a["alarm_type"] == "network_down"]
        if not roots:
            continue
        matched = [a for a in alarms if a["alarm_type"] == "conn_refused" and a["message_target"] == target]
        paths = [{"alarm_id": a["alarm_id"], "source": a["service"], "path": graph.path(a["service"], target),
                  "relation": a["target_relation"]} for a in matched]
        verified = sum(p["relation"] in {"direct", "transitive"} for p in paths)
        result.append({"target": target, "refused_count": count, "verified_path_count": verified,
                       "target_network_alarms": [{k: a[k] for k in ["alarm_id", "timestamp", "host", "message"]} for a in roots],
                       "calls": paths,
                       "interpretation": f"{target} hedefli {count} bağlantı reddi ve hedefte network_down var; {verified} çağrının bağımlılık yolu doğrulanıyor. Erişim kaybıyla uyumlu; uygulama işlevinin veya DNS çözümlemesinin kesin kesildiğini kanıtlamaz."})
    return result


def build_incident(e, members, hosts, graph):
    alarms = [a for a in members if a["incident_id"] == e["id"]]
    services = sorted({a["service"] for a in alarms})
    earliest, latest = min(a["_dt"] for a in alarms), max(a["_dt"] for a in alarms)
    severity = max(a["severity"] for a in alarms)
    criticality_map = {"kritik": 4, "yuksek": 3, "orta": 2, "dusuk": 1}
    criticality = max(criticality_map.get(hosts[a["host"]]["is_kritikligi"], 1) for a in alarms)
    depths = [len(p) - 1 for s in services for root in e["roots"] for p in [graph.path(s, root)] if p]
    type_weight = {"network": 5, "storage": 5, "memory": 4, "external": 5, "batch": 4, "unresolved": 1}[e["kind"]]
    span = max((latest - earliest).total_seconds(), 1)
    early = 1 + max(0, (latest - min(s["_dt"] for s in e["seeds"])).total_seconds()) / span
    factors = {"type_priority": type_weight, "earliness": round(early, 3), "severity": severity / 5,
               "downstream_depth": 1 + min(max(depths, default=0), 5) / 5}
    root_score = round(math.prod(factors.values()), 3)
    priority_score = round(criticality * 10 + severity * 5 + min(len(services), 15), 2)
    evidence = []
    seen_types = set()
    for a in e["seeds"]:
        if a["alarm_type"] not in seen_types:
            evidence.append({"alarm_id": a["alarm_id"], "timestamp": a["timestamp"], "host": a["host"],
                             "service": a["service"], "alarm_type": a["alarm_type"], "message": a["message"]})
            seen_types.add(a["alarm_type"])
    for a in e["seeds"][-2:]:
        if a["alarm_id"] not in {x["alarm_id"] for x in evidence}:
            evidence.append({k: a[k] for k in ["alarm_id", "timestamp", "host", "service", "alarm_type", "message"]})
    title = LABELS[e["kind"]] + " · " + e["scope"]
    root_types = dict(Counter(a["alarm_type"] for a in e["seeds"]))
    direct_alarms = [a for a in e["seeds"] if a["alarm_type"] in STRONG.get(e["kind"], set())]
    direct_hosts = sorted({a["host"] for a in direct_alarms})
    checks = []
    if direct_alarms:
        domain = f"{e['scope']} fiziksel alanında" if e["kind"] == "network" else f"{e['scope']} servisinde"
        checks.append({"text": f"{len(direct_alarms)} doğrudan kök sinyali, {len(direct_hosts)} host üzerinde {domain} bulundu.",
                       "alarm_ids": [a["alarm_id"] for a in direct_alarms]})
    applications = [a for a in alarms if a["alarm_type"] in {"conn_refused", "timeout", "http_5xx", "thread_pool", "db_write_fail", "txn_fail", "batch_slow"}]
    if direct_alarms and applications:
        first_root, first_effect = min(direct_alarms, key=lambda a: a["_dt"]), min(applications, key=lambda a: a["_dt"])
        delta = int((first_effect["_dt"] - first_root["_dt"]).total_seconds())
        if delta >= 0:
            checks.append({"text": f"İlk {first_root['alarm_type']} sinyalinden {delta} saniye sonra ilk {first_effect['alarm_type']} belirtisi gözlendi.",
                           "alarm_ids": [first_root["alarm_id"], first_effect["alarm_id"]]})
    validated = [a for a in alarms if "validated_message_target" in a.get("evidence_codes", [])]
    if validated:
        checks.append({"text": f"{len(validated)} alarmın mesaj hedefi, yönlü bağımlılık yoluyla aynı kök hipotezini destekliyor.",
                       "alarm_ids": [a["alarm_id"] for a in validated]})
    if e["trend"]:
        values = [a["numeric_signals"]["percent"] for a in e["trend"]]
        checks.append({"text": f"{len({a['host'] for a in e['trend']})} host'ta {len(e['trend'])} bellek öncülü: %{min(values):g} → %{max(values):g}; rastgele düşük ölçümler zincire alınmadı.",
                       "alarm_ids": [a["alarm_id"] for a in e["trend"]]})
    if e["resources"]:
        checks.append({"text": "Yavaşlayan işlerin ortak kaynak adayı: " + ", ".join(sorted(e["resources"])) + ". Yük yönü ayrıca doğrulanmalı.",
                       "alarm_ids": [a["alarm_id"] for a in alarms if a["service"] in e["resources"]]})
    checks.append({"text": f"{len(services)} serviste {len({a['alarm_type'] for a in alarms})} farklı alarm tipi aynı hipotez altında ilişkili; tipler ayrı olaylara parçalanmadı.",
                   "alarm_ids": []})
    support_text = ", ".join(f"{n} {t}" for t, n in sorted(root_types.items()))
    explanation = f"{e['scope']} için {support_text} kök/öncül kanıtı bulundu. "
    explanation += f"Zaman, konum ve bağımlılık uyumuyla {len(alarms)} alarm, {len(services)} gözlenen servise bağlandı. "
    if e["trend"]:
        vals = [a["numeric_signals"]["percent"] for a in e["trend"]]
        explanation += f"Bellek öncüllerinde %{min(vals):g}→%{max(vals):g} yükseliş var. "
    if e["resources"]:
        explanation += "Ortak kaynak adayları: " + ", ".join(sorted(e["resources"])) + ". "
    explanation += "Bu bir kök neden hipotezidir; doğrulama ölçümleri gereklidir."
    timeline = Counter(a["_dt"].replace(minute=a["_dt"].minute // 5 * 5, second=0, microsecond=0) for a in alarms)
    return {"id": e["id"], "kind": e["kind"], "title": title,
            "root": {"scope": e["scope"], "services": sorted(e["roots"]), "location": list(e["location"]) if e["location"] else None,
                     "hypothesis": LABELS[e["kind"]], "score": root_score, "factors": factors,
                     "score_meaning": "Hipotez içi kanıt sıralama skoru; olasılık veya doğruluk değildir.",
                     "resources": sorted(e["resources"]), "seed_count": len(e["seeds"])},
            "start": iso(earliest), "end": iso(latest), "alarm_count": len(alarms), "services": services,
            "hosts": sorted({a["host"] for a in alarms}), "potential_services": sorted(e["affected"] - set(services)),
            "direct_hosts": direct_hosts, "evidence_checks": checks,
            "priority": {"score": priority_score, "level": "P1" if criticality == 4 and severity >= 4 else "P2",
                         "reason": f"İş kritikliği {criticality}/4 ×10 + en yüksek şiddet {severity}/5 ×5 + {min(len(services),15)} servis."},
            "confidence": {"level": "yüksek" if len(e["seeds"]) >= 4 and e["kind"] != "batch" else "orta",
                           "meaning": "Kanıt yeterliliği; kalibre edilmiş olasılık değil."},
            "evidence": evidence, "explanation": explanation,
            "dependency_evidence": connection_evidence(alarms, e["seeds"], graph) if e["kind"] == "network" else [],
            "memory_trend": [{"alarm_id": a["alarm_id"], "host": a["host"], "timestamp": a["timestamp"],
                              "percent": a["numeric_signals"]["percent"]} for a in e["trend"]],
            "alternatives": [{"hypothesis": h, "comparison": c, "next_check": n} for h, c, n in ALTERNATIVES[e["kind"]]],
            "similar_incidents": history.match_signature(
                e["kind"], services, {a["alarm_type"] for a in alarms}, HISTORY_ARCHIVE),
            "action": {"owner": OWNERS[e["kind"]], "owner_kind": "role", "status": "open", "version": 1,
                       "recommendation": ACTIONS[e["kind"]], "history": []},
            "timeline": [{"time": iso(t), "count": n} for t, n in sorted(timeline.items())]}


def review_candidates(decisions, hosts, graph):
    """Evidence-backed review cards; keep every underlying decision UNCERTAIN.

    These are not additional proven incidents. Existing incident links are shown
    explicitly so unresolved membership is not presented as a new root cause.
    """
    groups = defaultdict(list)
    for alarm in decisions:
        if alarm["decision"] != "uncertain" or alarm["alarm_type"] in MAINTENANCE:
            continue
        code = alarm["evidence_codes"][0]
        groups[(alarm["service"], code)].append(alarm)
    cards = []
    for (service, code), group in sorted(groups.items()):
        for rows in split_runs(group, 5):
            types = {a["alarm_type"] for a in rows}
            if len(rows) < 8 or len({a["host"] for a in rows}) < 2 or (rows[-1]["_dt"] - rows[0]["_dt"]).total_seconds() < 300:
                continue
            if code != "competing_incidents" and len(types) < 2:
                continue
            if code == "insufficient_evidence" and sum(a["severity"] >= 4 for a in rows) < 4:
                continue
            ident = "REV-" + hashlib.sha256(f"{service}|{code}|{iso(rows[0]['_dt'])}".encode()).hexdigest()[:8].upper()
            linked = sorted({c["incident_id"] for a in rows for c in a["candidate_scores"]})
            target_counts = dict(Counter(a["message_target"] for a in rows if a["message_target"]))
            label = {"competing_incidents": "Çakışan olaylara aidiyeti belirsiz belirtiler",
                     "weak_incident_evidence": "Olay bağlantısı zayıf kalan belirtiler",
                     "insufficient_evidence": "Kökü doğrulanamayan tekrarlayan belirtiler"}[code]
            candidate = {"id": ident, "kind": "unresolved", "scope": service, "roots": {service}, "location": None,
                         "seeds": rows, "trend": [], "resources": set(), "affected": {service}}
            card = build_incident(candidate, [dict(a, incident_id=ident) for a in rows], hosts, graph)
            card.update(title=label + " · " + service, card_type="review", linked_incident_ids=linked,
                        review_alarm_ids=[a["alarm_id"] for a in rows], message_targets=target_counts)
            card["root"]["hypothesis"] = label
            card["root"]["score"] = None
            card["root"]["factors"] = {}
            card["root"]["score_meaning"] = "Kök belirlenmediği için kök skoru üretilmedi."
            card["confidence"] = {"level": "düşük", "meaning": "İnceleme adayı; yeni bağımsız olay olduğu doğrulanmadı."}
            card["explanation"] = (f"{service} üzerinde {len(rows)} belirsiz alarm, {len(types)} tip ve "
                                   f"{len(card['hosts'])} host'ta tekrar ediyor. "
                                   + ("Mevcut olaylara aidiyet çözülmedi: " + ", ".join(linked) + ". " if linked else "Güçlü kök veya yönlü bağımlılık bağlantısı doğrulanamadı. ")
                                   + "Bu bir inceleme kartıdır; kayıtlar belirsiz sınıfında kalır ve yeni bağımsız olay sayılmaz.")
            card["alternatives"] = [{"hypothesis": "Mevcut olayın etkisi veya bağımsız arıza",
                                     "comparison": "Tekrarlayan belirtiler var; aynı zaman aralığı nedensel bağlantı için yeterli değil.",
                                     "next_check": "Mesaj hedeflerini, bağımlılık yönünü ve eksik topoloji olasılığını operasyon ekibiyle doğrula."}]
            for alarm in rows:
                alarm["review_candidate_id"] = ident
            cards.append(card)
    return sorted(cards, key=lambda c: (-c["alarm_count"], c["start"], c["id"]))


def analyze(data_dir, external_tail_minutes=22):
    if not isinstance(external_tail_minutes, (int, float)) or not 1 <= external_tail_minutes <= 120:
        raise ValueError("Dış servis kuyruk penceresi 1–120 dakika olmalı.")
    began = time.perf_counter()
    alarms, hosts, dependencies, warnings, manifest = load_inputs(data_dir)
    graph = Graph(dependencies)
    origin, baseline, local = baseline_stats(alarms)
    episodes = find_episodes(alarms, graph, external_tail_minutes)
    decisions = []
    for a in alarms:
        target = a["message_target"]
        path = graph.path(a["service"], target) if target else None
        a["target_relation"] = "none" if not target else "self" if target == a["service"] else "direct" if path and len(path) == 2 else "transitive" if path else "unverified"
        candidates = [v for e in episodes for v in [candidate_score(a, e, graph, local)] if v]
        candidates.sort(key=lambda x: (-x["score"], x["incident_id"]))
        best = candidates[0] if candidates else None
        decision, incident, reason, codes = None, None, "", []
        if best and best["score"] >= 8:
            if len(candidates) > 1 and best["score"] - candidates[1]["score"] < 2:
                decision, reason, codes = "uncertain", "İki olay adayı yakın puan aldı; zorla birleştirme veya eleme yapılmadı.", ["competing_incidents"]
            else:
                decision, incident = "incident", best["incident_id"]
                reason, codes = " ".join(best["reasons"]), best["codes"]
        if decision is None:
            decision, reason, codes = noise_decision(a, baseline)
            if best and best["score"] >= 6:
                decision, reason, codes = "uncertain", "Olayla kısmi ilişki var; atama eşiği aşılmadı, gürültüye atılmadı.", ["weak_incident_evidence"]
        a.update(decision=decision, incident_id=incident, reason=reason, evidence_codes=codes,
                 candidate_scores=candidates[:3], concentration_ratio=baseline[a["alarm_type"]]["ratio"])
        decisions.append(a)
    assigned_ids = {a["incident_id"] for a in decisions if a["incident_id"]}
    incidents = [build_incident(e, decisions, hosts, graph) for e in episodes if e["id"] in assigned_ids]
    reviews = review_candidates(decisions, hosts, graph)
    incidents.sort(key=lambda c: (-c["priority"]["score"], c["start"], c["id"]))
    counts = Counter(a["decision"] for a in decisions)
    n = len(alarms)
    naive = len({(a["service"], int((a["_dt"] - origin).total_seconds() // 300)) for a in alarms})
    if sum(counts.values()) != n or sum(c["alarm_count"] for c in incidents) != counts["incident"]:
        raise AssertionError("Alarm kapsam muhasebesi tutarsız.")
    if len(incidents) + len(reviews) > 15:
        warnings.append("İnceleme kartları dahil 15 kart kabul sınırı aşıldı; kartlar gizlenmedi veya zorla birleştirilmedi.")
    if not incidents:
        warnings.append("Güçlü olay adayı bulunamadı; bu sonuç kabul başarısı sayılmaz.")
    summary = {"input_count": n, "processed_count": n, "incident_count": len(incidents),
               "assigned_count": counts["incident"], "noise_count": counts["noise"], "uncertain_count": counts["uncertain"],
               "coverage": 1., "accounted_count": sum(counts.values()), "card_ratio": len(incidents) / n,
               "reduction": 1 - len(incidents) / n, "naive_card_count": naive,
               "review_candidate_count": len(reviews), "total_card_count": len(incidents) + len(reviews),
               "card_limit_pass": 0 < len(incidents) + len(reviews) <= 15, "start": alarms[0]["timestamp"], "end": alarms[-1]["timestamp"],
               "service_count": len({a["service"] for a in alarms}), "host_count": len(hosts),
               "dependency_count": len(dependencies), "elapsed_ms": round((time.perf_counter() - began) * 1000, 2)}
    timeline = []
    for idx in range(len(next(iter(baseline.values()))["bins"])):
        group = [a for a in decisions if a["_bin"] == idx]
        c = Counter(a["decision"] for a in group)
        timeline.append({"time": iso(origin + timedelta(minutes=idx * 10)), "total": len(group),
                         "incident": c["incident"], "noise": c["noise"], "uncertain": c["uncertain"]})
    return {"schema_version": VERSION, "summary": summary, "incidents": incidents,
            "review_candidates": reviews, "uncertain": [public_alarm(a) for a in decisions if a["decision"] == "uncertain"],
            "settings": {"external_tail_minutes": external_tail_minutes, "assignment_threshold": 8, "competing_margin": 2,
                         "review_min_alarms": 8, "review_min_hosts": 2, "review_min_span_minutes": 5},
            "baseline": {"method": "type peak / max(median 10min, 1); full observation window, not online prediction",
                         "types": list(baseline.values()), "naive_method": "5 dakika × servis; hiçbir alarm atılmadan"},
            "quality": {"warnings": warnings, "manifest": manifest, "unique_alarm_ids": len({a['alarm_id'] for a in alarms}),
                        "target_relations": dict(Counter(a["target_relation"] for a in alarms if a["message_target"]))},
            "timeline": timeline, "alarms": [public_alarm(a) for a in decisions],
            "limitations": ["Sentetik veri; kapalı doğrulama etiketleri yok. Kök doğruluğu ve gürültü isabeti ölçülmedi.",
                            "Eşikler ve olay aileleri açık heuristiklerdir; farklı veride yeniden doğrulama gerekir.",
                            "Gürültü bir aday kararıdır. Belirsiz kayıtlar ayrı tutulur ve kaybolmaz.",
                            "Tam dosya analizi yapılır; gelecekten erken tahmin veya gerçek zaman iddiası yok.",
                            "Bağımlılık olası etkiyi gösterir; mesaj uyumsuzlukları ve eksik topoloji mümkün.",
                            "Aksiyonlar bellekte tutulur; yeniden başlatma durum geçmişini sıfırlar."]}
