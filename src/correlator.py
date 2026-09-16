"""Dependency-Aware Alert Storm Correlator — cekirdek korelasyon motoru.

Sadece Python standart kutuphanesi kullanir. Harici bagimlilik yoktur.

Akis:
  1) Yukleme + normalize + yonlu bagimlilik grafigi
  2) Zamansal yogunlasma orani -> sinyal / gurultu / belirsiz tip ayrimi
  3) Kok-tipi alarmlardan olay cekirdegi (seed) kumeleme
  4) Turev alarmlarin kanit skoruyla olaylara atanmasi
  5) Kok neden secimi + karsi olasilik + guven skoru
"""

import csv
import json
import os
import re
import statistics
from collections import defaultdict
from datetime import datetime, timedelta

# --- Alarm tipi siniflandirmasi -------------------------------------------------
# Tier 1: altyapi/dis kaynakli kok nedenler (en guclu kok adayi)
# Tier 2: kaynak tukenmesi (kok de olabilir, turev de)
# Tier 3: belirti / turev etki
TIER = {
    "network_down": 1, "pkt_loss": 1, "disk_full": 1,
    "ext_unreach": 1, "ext_slow": 1, "batch_overlap": 1,
    "db_conn_pool": 2, "oom_risk": 2, "db_write_fail": 2,
    "gc_pressure": 2, "conn_refused": 2, "thread_pool": 2,
    "timeout": 3, "http_5xx": 3, "txn_fail": 3, "batch_slow": 3, "latency_high": 3,
}

# Kok tipine gore onerilen ilk aksiyon ve sorumlu rol
ACTION_BOOK = {
    "network_down": ("Etkilenen kabinin ToR switch / uplink port durumunu dogrula", "Ag Ekibi"),
    "pkt_loss": ("Kabin ici ag baglantilarinda paket kaybi olcumu yap", "Ag Ekibi"),
    "disk_full": ("Veritabani disk/tablespace kapasitesini dogrula, otomatik silme yapma", "DBA Nobetcisi"),
    "db_write_fail": ("Veritabani yazma hatalarini ve tablespace durumunu incele", "DBA Nobetcisi"),
    "db_conn_pool": ("Baglanti havuzu kullanimini ve uzun suren sorgulari incele", "DBA Nobetcisi"),
    "ext_unreach": ("Dis servis erisilebilirligini ve cikis agi kurallarini dogrula", "Entegrasyon Nobetcisi"),
    "ext_slow": ("Dis servis yanit sureleri ve hata kodlarini dogrula", "Entegrasyon Nobetcisi"),
    "batch_overlap": ("Cakisan toplu is pencerelerini ayir, zamanlamayi yeniden planla", "Batch Nobetcisi"),
    "oom_risk": ("Heap kullanimi ve GC trendini incele, restart gerekcesini dogrula", "Uygulama Nobetcisi"),
    "gc_pressure": ("GC duraklamalarini ve heap buyume egrisini incele", "Uygulama Nobetcisi"),
    "conn_refused": ("Hedef servisin ayakta olup olmadigini ve port durumunu dogrula", "Uygulama Nobetcisi"),
    "thread_pool": ("Is parcacigi havuzu doygunlugunu ve bekleyen istekleri incele", "Uygulama Nobetcisi"),
}
DEFAULT_ACTION = ("Olayin kok neden adayini dogrula ve etkilenen servisleri kontrol et", "Nobetci Muhendis")

# Mesajdan hedef servis ayristirma kaliplari
RE_TARGET_CALL = re.compile(r"^([a-z0-9][a-z0-9-]+) servisine yapilan cagri")
RE_TARGET_CONN = re.compile(r"^([a-z0-9][a-z0-9-]+) baglantisi reddedildi")
RE_TARGET_EXT = re.compile(r"Dis servis ([a-z0-9][a-z0-9-]+)")
RE_PERCENT = re.compile(r"yuzde (\d+)")

# Esikler (veriden turetilen olculere gore secildi, tek tek host/servis adi sabitlenmedi)
SIGNAL_RATIO = 4.0      # >= ise olay sinyali
NOISE_RATIO = 3.0       # <  ise arka plan gurultusu (arasi belirsiz)
SEED_GAP_SEC = 480      # cekirdek alarmlar arasi izin verilen bosluk
ATTACH_SCORE_MIN = 3.0  # turev alarmi olaya baglamak icin gereken minimum kanit skoru
MAX_CARDS = 15


def parse_ts(value):
    return datetime.strptime(value.strip(), "%Y-%m-%dT%H:%M:%S")


def load_data(data_dir):
    """alarms.csv + service_dependencies.csv + host_inventory.csv okur."""
    alarms = []
    alarms_path = os.path.join(data_dir, "alarms.csv")
    with open(alarms_path, "r", encoding="utf-8") as fh:
        for row in csv.DictReader(fh):
            row["ts"] = parse_ts(row["timestamp"])
            row["severity"] = int(row["severity"])
            row["msg_target"] = extract_target(row["message"])
            row["pct"] = extract_percent(row["message"])
            alarms.append(row)
    alarms.sort(key=lambda a: a["ts"])

    deps = []
    with open(os.path.join(data_dir, "service_dependencies.csv"), "r", encoding="utf-8") as fh:
        deps = list(csv.DictReader(fh))

    inventory = {}
    with open(os.path.join(data_dir, "host_inventory.csv"), "r", encoding="utf-8") as fh:
        for row in csv.DictReader(fh):
            inventory[row["host"]] = row

    return alarms, deps, inventory


def extract_target(message):
    """Alarm metninden hedef servis adini cikarir (varsa)."""
    for pattern in (RE_TARGET_CALL, RE_TARGET_CONN, RE_TARGET_EXT):
        match = pattern.search(message)
        if match:
            return match.group(1)
    return None


def extract_percent(message):
    match = RE_PERCENT.search(message)
    return int(match.group(1)) if match else None


def build_graph(deps):
    """kaynak_servis -> hedef_servis (kaynak, hedefe bagimlidir).

    depends_on[s]  = s'nin dogrudan bagimli oldugu servisler
    affects[s]     = s bozulursa etkilenecek servisler
    """
    depends_on = defaultdict(set)
    affects = defaultdict(set)
    crit = {}
    for dep in deps:
        src, dst = dep["kaynak_servis"], dep["hedef_servis"]
        depends_on[src].add(dst)
        affects[dst].add(src)
        crit[dst] = dep.get("kritiklik", "")
    return depends_on, affects, crit


def depth_to(depends_on, src, dst, max_depth=3):
    """src servisinden dst servisine bagimlilik zinciri derinligi (yoksa None)."""
    if src == dst:
        return 0
    frontier = {src}
    seen = {src}
    for depth in range(1, max_depth + 1):
        nxt = set()
        for node in frontier:
            for child in depends_on.get(node, ()):
                if child == dst:
                    return depth
                if child not in seen:
                    seen.add(child)
                    nxt.add(child)
        if not nxt:
            break
        frontier = nxt
    return None


def concentration_profile(alarms, bucket_minutes=10):
    """Her alarm tipi icin zamansal yogunlasma orani = tepe pencere / medyan pencere.

    Duzgun dagilmis tipler (arka plan gurultusu) 1'e yakin cikar;
    olaya bagli tipler yuksek oran verir. Esik elle ayarlanmaz, veriden turetilir.
    """
    if not alarms:
        return {}
    start = alarms[0]["ts"]
    end = alarms[-1]["ts"]
    total_buckets = int((end - start).total_seconds() // (bucket_minutes * 60)) + 1

    per_type = defaultdict(lambda: [0] * total_buckets)
    for alarm in alarms:
        idx = int((alarm["ts"] - start).total_seconds() // (bucket_minutes * 60))
        idx = min(idx, total_buckets - 1)
        per_type[alarm["alarm_type"]][idx] += 1

    profile = {}
    for atype, counts in per_type.items():
        peak = max(counts)
        median = max(statistics.median(counts), 1)
        ratio = round(peak / median, 1)
        if ratio >= SIGNAL_RATIO:
            label = "sinyal"
        elif ratio < NOISE_RATIO:
            label = "gurultu"
        else:
            label = "belirsiz"
        profile[atype] = {
            "ratio": ratio,
            "peak": peak,
            "median": median,
            "label": label,
            "total": sum(counts),
        }
    return profile


def cluster_seeds(seeds, depends_on, inventory):
    """Kok-tipi alarmlari zaman + servis/bagimlilik/lokalite yakinligiyla kumeler."""
    clusters = []
    for alarm in seeds:
        placed = False
        for cluster in clusters:
            if (alarm["ts"] - cluster["last_ts"]).total_seconds() > SEED_GAP_SEC:
                continue
            if seed_related(alarm, cluster, depends_on):
                cluster["alarms"].append(alarm)
                cluster["last_ts"] = alarm["ts"]
                cluster["services"].add(alarm["service"])
                cluster["racks"].add((alarm["veri_merkezi"], alarm["kabin"]))
                placed = True
                break
        if not placed:
            clusters.append({
                "alarms": [alarm],
                "last_ts": alarm["ts"],
                "services": {alarm["service"]},
                "racks": {(alarm["veri_merkezi"], alarm["kabin"])},
            })
    return clusters


def seed_related(alarm, cluster, depends_on):
    """Bir cekirdek alarmi mevcut kumeye ait mi: servis / bagimlilik / lokalite."""
    if alarm["service"] in cluster["services"]:
        return True
    for svc in cluster["services"]:
        if depth_to(depends_on, alarm["service"], svc, 2) is not None:
            return True
        if depth_to(depends_on, svc, alarm["service"], 2) is not None:
            return True
    if (alarm["veri_merkezi"], alarm["kabin"]) in cluster["racks"]:
        # Ayni kabin, ancak yalnizca ag tipi belirtilerde lokalite tek basina yeterli sayilir
        if alarm["alarm_type"] in ("network_down", "pkt_loss"):
            return True
    return False


def pick_root(cluster_alarms):
    """Kume icinden kok neden alarmini secer: tip onceligi > erkenlik > siddet."""
    return sorted(
        cluster_alarms,
        key=lambda a: (TIER.get(a["alarm_type"], 4), a["ts"], -a["severity"]),
    )[0]


def attach_score(alarm, event, depends_on):
    """Turev alarmin bir olaya ait olma kanit skoru."""
    score = 0.0
    reasons = []

    root_service = event["root_service"]

    if alarm["msg_target"] and alarm["msg_target"] == root_service:
        score += 5.0
        reasons.append("alarm metni dogrudan %s hedefini gosteriyor" % root_service)
    elif alarm["msg_target"] and alarm["msg_target"] in event["services"]:
        score += 2.5
        reasons.append("alarm metni olay kapsamindaki %s servisini gosteriyor" % alarm["msg_target"])

    if alarm["service"] == root_service:
        score += 3.0
        reasons.append("kok servisin kendi uzerinde")
    else:
        depth = depth_to(depends_on, alarm["service"], root_service, 3)
        if depth:
            score += 3.0 / depth
            reasons.append("%s -> %s bagimlilik zinciri (derinlik %d)" % (alarm["service"], root_service, depth))

    if (alarm["veri_merkezi"], alarm["kabin"]) in event["racks"]:
        score += 2.0
        reasons.append("olayin yogunlastigi %s/%s kabininde" % (alarm["veri_merkezi"], alarm["kabin"]))

    return score, reasons


def in_window(alarm, event, pre=120, post=600):
    start = event["start"] - timedelta(seconds=pre)
    end = event["end"] + timedelta(seconds=post)
    return start <= alarm["ts"] <= end


def build_events(alarms, deps, inventory, profile):
    depends_on, affects, crit = build_graph(deps)

    signal_types = {t for t, p in profile.items() if p["label"] == "sinyal"}
    noise_types = {t for t, p in profile.items() if p["label"] == "gurultu"}

    # 1) Cekirdek (seed) alarmlar: kok olabilecek tipler ve zamansal olarak yogunlasan tipler
    seeds = [
        a for a in alarms
        if TIER.get(a["alarm_type"], 4) <= 2 and a["alarm_type"] in signal_types
    ]
    clusters = cluster_seeds(seeds, depends_on, inventory)

    events = []
    for cluster in clusters:
        root = pick_root(cluster["alarms"])
        events.append({
            "root_alarm": root,
            "root_service": root["service"],
            "root_type": root["alarm_type"],
            "seed_alarms": cluster["alarms"],
            "alarms": list(cluster["alarms"]),
            "services": set(cluster["services"]),
            "racks": set(cluster["racks"]),
            "start": min(a["ts"] for a in cluster["alarms"]),
            "end": max(a["ts"] for a in cluster["alarms"]),
        })

    # Cok kucuk kumeleri (tek alarmlik gurultu adasi) ele
    events = [e for e in events if len(e["seed_alarms"]) >= 2]
    events.sort(key=lambda e: e["start"])

    # 2) Turev ve destekleyici alarmlari kanit skoruyla olaylara ata
    seed_ids = {a["alarm_id"] for e in events for a in e["seed_alarms"]}
    pending = [a for a in alarms if a["alarm_id"] not in seed_ids]

    # Atama ALARM seviyesinde yapilir: servis + bagimlilik + mesaj hedefi + lokalite
    # birlikte skorlanir. Zaman penceresi yalnizca aday daraltma icin kullanilir.
    # Iki gecis: ilk gecis cekirdek pencerelere gore, ikinci gecis genisleyen
    # pencerelere gore -> uzun kuyruklu cascade'lerin sonu sahipsiz kalmaz.
    last_scores = {}
    for pass_no in (1, 2):
        still_pending = []
        for alarm in pending:
            best_event, best_score, best_reasons = None, 0.0, []
            for event in events:
                if not in_window(alarm, event):
                    continue
                score, reasons = attach_score(alarm, event, depends_on)
                if score > best_score:
                    best_event, best_score, best_reasons = event, score, reasons

            if best_event and best_score >= ATTACH_SCORE_MIN:
                alarm["_link_reasons"] = best_reasons
                alarm["_link_score"] = round(best_score, 1)
                best_event["alarms"].append(alarm)
                best_event["services"].add(alarm["service"])
            else:
                last_scores[alarm["alarm_id"]] = (best_event, best_score)
                still_pending.append(alarm)

        # Pencereleri yeni atamalarla genislet, ikinci gecis bunlari kullanir
        for event in events:
            event["start"] = min(a["ts"] for a in event["alarms"])
            event["end"] = max(a["ts"] for a in event["alarms"])
        pending = still_pending

    noise = []
    unclear = []
    for alarm in pending:
        best_event, best_score = last_scores.get(alarm["alarm_id"], (None, 0.0))
        if alarm["alarm_type"] in signal_types:
            unclear.append((alarm, "olay penceresinde ancak kok servisle kanit bagi zayif (skor %.1f < %.1f)"
                            % (best_score, ATTACH_SCORE_MIN)))
        else:
            noise.append((alarm, noise_reason(alarm, profile, best_event, best_score)))

    return events, noise, unclear, depends_on, affects, crit


def noise_reason(alarm, profile, best_event, best_score):
    info = profile.get(alarm["alarm_type"], {})
    ratio = info.get("ratio", 0)
    if best_event is None:
        return ("tip zamanda duzgun dagilmis (yogunlasma %.1fx), hicbir olay penceresiyle ortusmuyor" % ratio)
    return ("olay penceresinde ancak kok servisle bagimlilik/lokalite bagi yok "
            "(kanit skoru %.1f < %.1f), tip yogunlasmasi %.1fx" % (best_score, ATTACH_SCORE_MIN, ratio))


def counter_hypothesis(event, depends_on):
    """Reddedilen en guclu alternatif kok neden ve red gerekcesi."""
    root = event["root_alarm"]
    candidates = [
        a for a in event["alarms"]
        if a["service"] != root["service"] and TIER.get(a["alarm_type"], 4) <= 2
    ]
    if not candidates:
        derivative = [a for a in event["alarms"] if TIER.get(a["alarm_type"], 4) == 3]
        if not derivative:
            return None
        alt = sorted(derivative, key=lambda a: a["ts"])[0]
        gap = (alt["ts"] - root["ts"]).total_seconds() / 60.0
        return {
            "text": ("Alternatif: kok neden %s uzerindeki %s olabilir mi? "
                     "Hayir - bu bir turev belirti tipi ve kok alarmdan %.1f dk %s geldi."
                     % (alt["service"], alt["alarm_type"], abs(gap), "sonra" if gap >= 0 else "once")),
            "confidence": 0.15,
        }
    alt = sorted(candidates, key=lambda a: (TIER.get(a["alarm_type"], 4), a["ts"]))[0]
    gap = (alt["ts"] - root["ts"]).total_seconds() / 60.0
    if gap >= 0:
        reason = ("ilk belirtisi kok alarmdan %.1f dk sonra geldi, zaman sirasi bu hipotezi zayiflatiyor" % gap)
        conf = 0.18
    else:
        reason = ("kok alarmdan %.1f dk once basladi ancak tip onceligi daha dusuk (tier %d vs %d)"
                  % (abs(gap), TIER.get(alt["alarm_type"], 4), TIER.get(root["alarm_type"], 4)))
        conf = 0.30
    return {
        "text": ("Alternatif: kok neden %s uzerindeki %s olabilir mi? Hayir - %s."
                 % (alt["service"], alt["alarm_type"], reason)),
        "confidence": conf,
    }


def confidence_of(event):
    """Kanit gucune dayali guven skoru (kalibre edilmemis, acikca belirtilir)."""
    root_tier = TIER.get(event["root_type"], 4)
    score = 0.45
    if root_tier == 1:
        score += 0.25
    elif root_tier == 2:
        score += 0.12
    seed_count = len(event["seed_alarms"])
    score += min(seed_count / 40.0, 0.15)
    if len(event["racks"]) == 1:
        score += 0.08
    if event["root_alarm"]["severity"] >= 5:
        score += 0.07
    return round(min(score, 0.95), 2)


def severity_label(event):
    max_sev = max(a["severity"] for a in event["alarms"])
    span = len(event["services"])
    if max_sev >= 5 or span >= 6:
        return "KRITIK"
    if max_sev >= 4 or span >= 3:
        return "YUKSEK"
    return "ORTA"


def why_text(event, depends_on, profile):
    """Kok neden hipotezinin deterministik gerekcesi (LLM'siz de tam calisir)."""
    root = event["root_alarm"]
    seed_types = defaultdict(int)
    for alarm in event["seed_alarms"]:
        seed_types[alarm["alarm_type"]] += 1
    seed_desc = ", ".join("%s x%d" % (t, c) for t, c in sorted(seed_types.items(), key=lambda kv: -kv[1]))

    racks = sorted("%s/%s" % r for r in event["racks"])
    derivative = [a for a in event["alarms"] if TIER.get(a["alarm_type"], 4) == 3]
    chains = set()
    for alarm in derivative:
        depth = depth_to(depends_on, alarm["service"], event["root_service"], 3)
        if depth:
            chains.add("%s -> %s" % (alarm["service"], event["root_service"]))
    msg_hits = sum(1 for a in event["alarms"] if a.get("msg_target") == event["root_service"])

    domain = network_domain(event)
    if domain:
        parts = [
            "Ag kaynakli belirtiler %s'te basladi ve tamami tek fiziksel alanda: %s."
            % (root["ts"].strftime("%H:%M:%S"), domain["domain"]),
            "%d ag alarmi (%s), %d farkli host ve %d farkli serviste goruldu - yani kok neden tek bir "
            "servis degil, bu host'larin paylastigi ag alani."
            % (domain["alarm_count"], seed_desc, domain["host_count"], domain["service_count"]),
        ]
    else:
        parts = [
            "%s ilk olarak %s'te %s uzerinde basladi (%s)."
            % (root["alarm_type"], root["ts"].strftime("%H:%M:%S"), root["host"], root["service"]),
            "Cekirdek kanit: %s." % seed_desc,
        ]
        if len(racks) == 1:
            parts.append("Tum cekirdek alarmlar tek fiziksel alanda yogunlasiyor (%s)." % racks[0])
    if msg_hits:
        parts.append("%d alarmin metni dogrudan %s hedefini gosteriyor." % (msg_hits, event["root_service"]))
    if chains:
        sample = sorted(chains)[:3]
        parts.append("Bagimlilik zinciri uzerinden turev belirtiler: %s%s."
                     % ("; ".join(sample), " ..." if len(chains) > 3 else ""))

    # Ek kanit 1: en cok reddedilen baglanti hedefi (cakilan altyapi bileseni)
    refused = defaultdict(int)
    for alarm in event["alarms"]:
        if alarm["alarm_type"] == "conn_refused" and alarm["msg_target"]:
            refused[alarm["msg_target"]] += 1
    if refused:
        target, count = max(refused.items(), key=lambda kv: kv[1])
        parts.append("Reddedilen baglantilarin en sik hedefi %s (%d kez) - bu bilesen de etkilendigi icin "
                     "etki carpan etkisiyle buyumus gorunuyor." % (target, count))

    # Ek kanit 2: monoton artan kaynak merdiveni (yavas gelisen olaylarin imzasi)
    ladder = memory_ladder(event["alarms"])
    if ladder:
        parts.append("Kaynak kullanimi %d host'ta monoton tirmandi (or. %s: %%%d -> %%%d) - "
                     "bu, ani bir sicrama degil zamana yayilan bir bozulma imzasi."
                     % (ladder["hosts"], ladder["sample_host"], ladder["first"], ladder["last"]))
    parts.append("Toplam %d alarm, %d servis, %s-%s araligi."
                 % (len(event["alarms"]), len(event["services"]),
                    event["start"].strftime("%H:%M"), event["end"].strftime("%H:%M")))
    return " ".join(parts)


def network_domain(event):
    """Ag tipi kok alarmlar tek bir fiziksel alanda yogunlasiyorsa o alani dondurur.

    Ag kesintisinde kok neden tek bir servis degil, paylasilan fiziksel ag alanidir;
    alarm hangi servisin host'unda goruldugu kok neden anlamina gelmez.
    """
    net = [a for a in event["seed_alarms"] if a["alarm_type"] in ("network_down", "pkt_loss")]
    if not net:
        return None
    racks = {(a["veri_merkezi"], a["kabin"]) for a in net}
    if len(racks) == 1 and len(net) >= 3:
        dc, rack = next(iter(racks))
        return {
            "domain": "%s/%s" % (dc, rack),
            "alarm_count": len(net),
            "host_count": len({a["host"] for a in net}),
            "service_count": len({a["service"] for a in net}),
        }
    return None


def memory_ladder(alarms, min_steps=3):
    """Host bazinda monoton artan kaynak kullanimi zinciri arar.

    Yavas gelisen olaylarin (bellek sizintisi vb.) imzasi "kac tane mem_high var"
    degil, ayni host'ta yuzdenin duzenli tirmanmasidir. Tip sayarak bakmak
    gurultudeki mem_high alarmlariyla karisir.
    """
    by_host = defaultdict(list)
    for alarm in alarms:
        if alarm["alarm_type"] in ("mem_high", "gc_pressure", "oom_risk") and alarm["pct"] is not None:
            by_host[alarm["host"]].append((alarm["ts"], alarm["pct"]))

    best = None
    hosts_with_ladder = 0
    for host, points in by_host.items():
        points.sort()
        longest, current = [], [points[0]]
        for prev, nxt in zip(points, points[1:]):
            if nxt[1] > prev[1]:
                current.append(nxt)
            else:
                if len(current) > len(longest):
                    longest = current
                current = [nxt]
        if len(current) > len(longest):
            longest = current
        if len(longest) >= min_steps:
            hosts_with_ladder += 1
            if best is None or len(longest) > best[1]:
                best = (host, len(longest), longest[0][1], longest[-1][1])

    if not best:
        return None
    return {"hosts": hosts_with_ladder, "sample_host": best[0], "steps": best[1],
            "first": best[2], "last": best[3]}


def title_of(event):
    root = event["root_alarm"]
    domain = network_domain(event)
    if domain:
        return "%s ag kesintisi" % domain["domain"]
    racks = sorted("%s/%s" % r for r in event["racks"])
    labels = {
        "disk_full": "%s disk dolmasi" % event["root_service"],
        "db_write_fail": "%s yazma hatasi" % event["root_service"],
        "db_conn_pool": "%s baglanti havuzu tukenmesi" % event["root_service"],
        "ext_unreach": "%s dis servis kesintisi" % event["root_service"],
        "ext_slow": "%s dis servis yavaslamasi" % event["root_service"],
        "batch_overlap": "Toplu is penceresi cakismasi",
        "oom_risk": "%s bellek tukenme riski" % event["root_service"],
        "gc_pressure": "%s bellek/GC baskisi" % event["root_service"],
        "thread_pool": "%s is parcacigi doygunlugu" % event["root_service"],
        "conn_refused": "%s baglanti reddi" % event["root_service"],
    }
    return labels.get(root["alarm_type"], "%s uzerinde %s" % (event["root_service"], root["alarm_type"]))


def run(data_dir):
    alarms, deps, inventory = load_data(data_dir)
    profile = concentration_profile(alarms)
    events, noise, unclear, depends_on, affects, crit = build_events(alarms, deps, inventory, profile)

    # Onceliklendirme: siddet x etkilenen servis sayisi x kok tipi onceligi
    def priority(event):
        max_sev = max(a["severity"] for a in event["alarms"])
        return (-(max_sev * 2 + len(event["services"])), TIER.get(event["root_type"], 4), event["start"])

    events.sort(key=priority)
    events = events[:MAX_CARDS]

    cards = []
    for idx, event in enumerate(events, start=1):
        root = event["root_alarm"]
        action, owner = ACTION_BOOK.get(event["root_type"], DEFAULT_ACTION)
        counter = counter_hypothesis(event, depends_on)
        domain = network_domain(event)
        if domain:
            hypothesis = ("%s fiziksel ag alaninda kesinti (%d ag alarmi, %d host, %d servis)"
                          % (domain["domain"], domain["alarm_count"],
                             domain["host_count"], domain["service_count"]))
            root_label = domain["domain"]
        else:
            hypothesis = "%s uzerinde %s (%s)" % (event["root_service"], event["root_type"], root["host"])
            root_label = event["root_service"]
        seed_types = sorted({a["alarm_type"] for a in event["seed_alarms"]})
        cards.append({
            "id": "EV-%02d" % idx,
            "rank": idx,
            "severity_label": severity_label(event),
            "title": title_of(event),
            "root_cause_hypothesis": hypothesis,
            "root_service": root_label,
            "root_alarm_id": root["alarm_id"],
            "why": why_text(event, depends_on, profile),
            "confidence": confidence_of(event),
            "counter_hypotheses": [counter] if counter else [],
            "signals": ["%s x%d" % (t, sum(1 for a in event["seed_alarms"] if a["alarm_type"] == t))
                        for t in seed_types],
            "services": sorted(event["services"]),
            "hosts": sorted({a["host"] for a in event["alarms"]}),
            "racks": sorted("%s/%s" % r for r in event["racks"]),
            "alarm_count": len(event["alarms"]),
            "time_start": event["start"].strftime("%H:%M:%S"),
            "time_end": event["end"].strftime("%H:%M:%S"),
            "suggested_action": action,
            "owner": owner,
            "status": "Acik",
            "alarm_ids": sorted(a["alarm_id"] for a in event["alarms"]),
            "alarms": [
                {
                    "alarm_id": a["alarm_id"],
                    "time": a["ts"].strftime("%H:%M:%S"),
                    "service": a["service"],
                    "host": a["host"],
                    "type": a["alarm_type"],
                    "severity": a["severity"],
                    "message": a["message"],
                    "role": "kok" if a["alarm_id"] == root["alarm_id"] else (
                        "cekirdek" if TIER.get(a["alarm_type"], 4) <= 2 else "turev"),
                    "link_reasons": a.get("_link_reasons", []),
                }
                for a in sorted(event["alarms"], key=lambda x: x["ts"])
            ],
        })

    assigned = sum(c["alarm_count"] for c in cards)
    naive_card_count = len({(a["ts"].strftime("%H:%M")[:4], a["service"]) for a in alarms})

    return {
        "events": cards,
        "noise": [
            {
                "alarm_id": a["alarm_id"],
                "time": a["ts"].strftime("%H:%M:%S"),
                "service": a["service"],
                "type": a["alarm_type"],
                "severity": a["severity"],
                "message": a["message"],
                "reason": reason,
            }
            for a, reason in sorted(noise, key=lambda x: x[0]["ts"])
        ],
        "unclear": [
            {
                "alarm_id": a["alarm_id"],
                "time": a["ts"].strftime("%H:%M:%S"),
                "service": a["service"],
                "type": a["alarm_type"],
                "severity": a["severity"],
                "message": a["message"],
                "reason": reason,
            }
            for a, reason in sorted(unclear, key=lambda x: x[0]["ts"])
        ],
        "type_profile": [
            {"type": t, **info}
            for t, info in sorted(profile.items(), key=lambda kv: -kv[1]["ratio"])
        ],
        "metrics": {
            "total_alarms": len(alarms),
            "processed_alarms": len(alarms),
            "event_count": len(cards),
            "alarms_in_events": assigned,
            "noise_count": len(noise),
            "unclear_count": len(unclear),
            "accounted": assigned + len(noise) + len(unclear),
            "reduction_ratio": round(1 - len(cards) / len(alarms), 4),
            "naive_card_count": naive_card_count,
            "time_window": "%s - %s" % (alarms[0]["ts"].strftime("%H:%M"), alarms[-1]["ts"].strftime("%H:%M")),
        },
    }


if __name__ == "__main__":
    import sys
    target = sys.argv[1] if len(sys.argv) > 1 else "data/katilimci_paketi"
    result = run(target)
    print(json.dumps(result["metrics"], indent=2, ensure_ascii=False))
    for card in result["events"]:
        print("\n[%s] %s  (%s, %d alarm, guven %.2f)"
              % (card["id"], card["title"], card["severity_label"], card["alarm_count"], card["confidence"]))
        print("   Kok : %s" % card["root_cause_hypothesis"])
        print("   Neden: %s" % card["why"])
        if card["counter_hypotheses"]:
            print("   Karsi: %s" % card["counter_hypotheses"][0]["text"])
        print("   Aksiyon: %s [%s]" % (card["suggested_action"], card["owner"]))
