# AO S-A1 Historical Incident Demo Data

Bu paket, S-A1 Alarm Firtinasi hackathon uygulamasindaki **Historical / Similar Incidents**
ekrani icin uretilmis sentetik demo verisidir.

## Icerik
- `historical_incidents.json` / `.csv`: 5 gecmis olay kartinin ozet bilgileri
- `historical_alarms_all.csv`: tum gecmis alarm kayitlari tek dosyada (`incident_id` ek kolonu ile)
- Her `HIST-.../` klasorunde:
  - `alarms.csv`: orijinal yarismadaki alarms.csv ile ayni kolon yapisi
  - `alarms.json`: orijinal yarismadaki alarms.json ile ayni alan yapisi
  - `incident.json`: root cause, resolution, MTTR, similarity, owner ve signature bilgileri
- `host_inventory.csv`, `service_dependencies.csv`, `VERI_SOZLUGU.md`: mevcut paketle ayni referans dosyalari

## Onerilen UI
Current incident kartinda:
- Similar Historical Incident
- Similarity %
- Previous Root Cause
- Previous Resolution
- MTTR
- Matching Signals
- "View Timeline" / "Compare Evidence"

## Not
Tum historical kayitlar demo amacli sentetiktir. Gercek bir kurumsal olay kaydi degildir.
