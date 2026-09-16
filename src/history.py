"""Benzer gecmis olay eslestirme (bonus B3).

Gecmis olay arsivi opsiyoneldir: klasor yoksa uygulama tam calisir, kartlarda
yalnizca bu bolum bos kalir.

ONEMLI: Arsiv dosyasinda `similarity_to_current` diye hazir bir alan var;
KULLANILMIYOR. Benzerlik bu modulde imzalardan hesaplanir, aksi halde skor bu
veri setine gomulu bir sabit olurdu ve baska bir arsivde anlamsiz kalirdi.
"""

import json
import os

# Motorun olay turu -> gecmis arsivdeki kok neden kategorisi
KIND_CATEGORY = {
    "network": "network",
    "storage": "database/storage",
    "memory": "application/memory",
    "external": "external_dependency",
    "batch": "batch/scheduling",
}

# Kok alarm tipi -> gecmis arsivdeki kok neden kategorisi
CATEGORY_OF = {
    "network_down": "network",
    "pkt_loss": "network",
    "conn_refused": "network",
    "disk_full": "database/storage",
    "db_write_fail": "database/storage",
    "db_conn_pool": "database/storage",
    "mem_high": "application/memory",
    "gc_pressure": "application/memory",
    "oom_risk": "application/memory",
    "thread_pool": "application/memory",
    "ext_slow": "external_dependency",
    "ext_unreach": "external_dependency",
    "batch_overlap": "batch/scheduling",
    "batch_slow": "batch/scheduling",
}

W_TYPES = 0.45      # alarm tipi imzasi ortusmesi
W_SERVICES = 0.35   # etkilenen servis kumesi ortusmesi
W_CATEGORY = 0.20   # kok neden kategorisi eslesmesi
MIN_SIMILARITY = 0.35


def jaccard(a, b):
    sa, sb = set(a), set(b)
    if not sa or not sb:
        return 0.0
    return len(sa & sb) / len(sa | sb)


def load_archive(path):
    """Gecmis olay arsivini okur. Yoksa bos liste doner (ozellik sessizce kapanir)."""
    candidate = os.path.join(path, "historical_incidents.json")
    if not os.path.isfile(candidate):
        return []
    try:
        with open(candidate, "r", encoding="utf-8") as fh:
            data = json.load(fh)
        return data if isinstance(data, list) else []
    except (ValueError, OSError):
        return []


def match_signature(kind, services, alarm_types, archive):
    """Olay turu + servis kumesi + alarm tipi imzasindan gecmis olay eslestirir.

    Benzerlik = 0.45*Jaccard(alarm tipleri) + 0.35*Jaccard(servisler) + 0.20*kategori
    """
    if not archive:
        return []

    card_types = set(alarm_types)
    card_services = set(services)
    category = KIND_CATEGORY.get(kind, "")

    scored = []
    for past in archive:
        s_types = jaccard(card_types, past.get("signature_alarm_types", []))
        s_services = jaccard(card_services, past.get("affected_services", []))
        s_category = 1.0 if category and category == past.get("root_cause_category") else 0.0
        score = W_TYPES * s_types + W_SERVICES * s_services + W_CATEGORY * s_category
        if score < MIN_SIMILARITY:
            continue
        scored.append({
            "incident_id": past.get("incident_id", ""),
            "title": past.get("title", ""),
            "date": (past.get("detected_at", "") or "")[:10],
            "similarity": round(score, 2),
            "breakdown": {
                "alarm_tipi_ortusmesi": round(s_types, 2),
                "servis_ortusmesi": round(s_services, 2),
                "kategori_eslesmesi": s_category,
            },
            "shared_alarm_types": sorted(card_types & set(past.get("signature_alarm_types", []))),
            "root_cause": past.get("root_cause_tr") or past.get("root_cause", ""),
            "resolution_action": past.get("resolution_action", ""),
            "action_owner": past.get("action_owner", ""),
            "mttr_minutes": past.get("mttr_minutes"),
            "lessons_learned": past.get("lessons_learned", ""),
        })

    scored.sort(key=lambda x: -x["similarity"])
    return scored[:2]


def match(card, archive):
    """Karta en cok benzeyen gecmis olaylari benzerlik skoruyla dondurur."""
    if not archive:
        return []

    card_types = {a["type"] for a in card["alarms"]}
    card_services = set(card["services"])
    card_category = CATEGORY_OF.get(card.get("_root_type", ""), "")

    scored = []
    for past in archive:
        s_types = jaccard(card_types, past.get("signature_alarm_types", []))
        s_services = jaccard(card_services, past.get("affected_services", []))
        s_category = 1.0 if card_category and card_category == past.get("root_cause_category") else 0.0
        score = W_TYPES * s_types + W_SERVICES * s_services + W_CATEGORY * s_category
        if score < MIN_SIMILARITY:
            continue

        shared_types = sorted(card_types & set(past.get("signature_alarm_types", [])))
        shared_services = sorted(card_services & set(past.get("affected_services", [])))
        scored.append({
            "incident_id": past.get("incident_id", ""),
            "title": past.get("title", ""),
            "date": (past.get("detected_at", "") or "")[:10],
            "similarity": round(score, 2),
            "breakdown": {
                "alarm_tipi_ortusmesi": round(s_types, 2),
                "servis_ortusmesi": round(s_services, 2),
                "kategori_eslesmesi": s_category,
            },
            "shared_alarm_types": shared_types,
            "shared_services": shared_services,
            "root_cause": past.get("root_cause_tr") or past.get("root_cause", ""),
            "resolution_action": past.get("resolution_action", ""),
            "action_owner": past.get("action_owner", ""),
            "mttr_minutes": past.get("mttr_minutes"),
            "lessons_learned": past.get("lessons_learned", ""),
        })

    scored.sort(key=lambda x: -x["similarity"])
    return scored[:2]
