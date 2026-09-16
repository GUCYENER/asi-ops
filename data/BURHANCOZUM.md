# S-A1 "Alarm Fırtınası" — STRATON Çözüm Alternatifleri

> AO Hackathon 2026 · Senaryo S-A1 · Teslim 17:30
> Bu dosya, STRATON Strateji Konseyi'nin ürettiği İterasyon 1 çıktısıdır — dış değerlendirme için ayrıştırılmıştır.

---

## PROBLEM ÖZETİ

- **Problem:** 3.000 alarm arasında kök-neden/türev-etki/gürültü ayrımı görünmüyor, nöbetçi mühendis doğru müdahale sırasına giremiyor.
- **Hedef kullanıcı:** Gece nöbetçisi SRE mühendisi.
- **Kullanıcının temel ihtiyacı:** En fazla 15 kartlık, gerekçeli, aksiyon alınabilir özet.
- **Kök neden:** Alarmlar zaman + servis + bağımlılık ilişkisi kurulmadan düz liste halinde geliyor.
- **Mevcut yaklaşımın problemi:** Alarm tipine bakmak yanıltıcı — tipler olaylar arasında paylaşılıyor.
- **Kritik kısıtlar:** 17:30 kesin teslim; kod repo `src/`'e yazılmalı; kaç gerçek olay olduğu bilinmiyor, küme sayısı sabit (K) olamaz.
- **Varsayımlar:** Zaman + servis bağımlılık grafiği kombinasyonu, kök neden tespiti için en güçlü sinyal — veri paketinde ayrıca `service_dependencies.csv` verilmiş olması bunu destekliyor.
- **Başarı kriteri:** ≤15 kart, düşük yanlış-birleştirme, yüksek gürültü elemesi, gerekçeli kök neden hipotezi.

**Veri:** `alarms.csv` (3.000 satır, eksiksiz), `service_dependencies.csv` (32 kayıt, yönlü bağımlılık grafiği), `host_inventory.csv` (56 host). Doğrulama verisi (gerçek kaç olay, hangi alarm hangi olaya ait) jüri tarafından değerlendirme aşamasında açılacak — şu an elimizde yok.

---

## ÇÖZÜM A — GÜVENLİ MVP: "Deterministik Korelasyon Motoru"

- **Çözüm:** Zaman penceresi + servis bağımlılık grafiği ile bağlı-bileşen (connected-components) kümeleme; her kümede bağımlılık grafiğinde en "yukarıdaki" (kök) servisin alarmı = kök neden hipotezi.
- **Kullanıcıya sağladığı değer:** ≤15 gerekçeli, aksiyon alınabilir kart; gürültü otomatik elenir.
- **AI'ın rolü:** Kümeleme/kök-neden tamamen deterministik (graf algoritması); LLM yalnızca sonucu "Sonuç: X, çünkü Y + karşı olasılık Z" cümlesine çevirir.
- **Kullanıcı akışı:** Veri toplu okunur → kümeleme çalışır → kartlar listelenir → nöbetçi aksiyon açar/kapatır (sahip + durum).
- **MVP özellikleri:**
  1. Toplu okuma + parse (alarms.csv/json)
  2. Zaman + bağımlılık grafiği kümeleme
  3. Kök-neden ranklama (grafikte en yukarıdaki düğüm + en erken zaman + en yüksek severity)
  4. LLM gerekçe katmanı (fallback: şablon cümle)
  5. Aksiyon kaydı (aç/ata/kapat, sahip + durum)
  6. Gürültü denetim görünümü (X-Factor bonus #2 — elenen alarmın neden elendiği gösterilir)
- **MVP dışı özellikler:** Gerçek zamanlı stream, geçmiş olay eşleştirme (zaman kalırsa eklenir), auth/login.
- **Gerekli veri:** alarms.csv, service_dependencies.csv, host_inventory.csv (üçü de doğrulandı, erişilebilir).
- **Kullanılabilecek teknoloji/servisler:** Python (pandas + networkx) + basit arayüz (Streamlit veya FastAPI+HTML); LLM (model seçimi ayrıca belirlenecek) opsiyonel gerekçe katmanı, yoksa şablon fallback.
- **Teknik riskler:** Düşük — algoritma tamamen deterministik, LLM çökse/erişilemese bile kart + kural-tabanlı gerekçe çalışmaya devam eder.
- **Demo senaryosu:** Uygulama başlatılır → 3.000 alarm okunur → tahmini 8-12 kart üretilir → bir karta aksiyon atanıp "kapatıldı" durumuna geçirilerek gösterilir.

**Puanlama (10 üzerinden, teknik riskte yüksek puan = düşük risk):**

| Kriter | Puan |
|---|---:|
| Problem Çözme Gücü | 8 |
| Kullanıcı Değeri | 9 |
| AI Katkısı | 7 |
| Yenilikçilik | 6 |
| 3 Saatte Yapılabilirlik | 9 |
| Teknik Risk | 9 |
| Demo Etkisi | 8 |
| Farklılaşma | 6 |
| Ölçeklenebilirlik | 7 |
| Jüri Etkisi | 8 |
| **TOPLAM** | **77** |

---

## ÇÖZÜM B — İDDİALI MVP: "ML-Destekli Çok Sinyalli Kümeleme"

- **Çözüm:** Alarm mesajı + tip + servis üzerinden embedding/özellik çıkarımı + DBSCAN (yoğunluk-tabanlı kümeleme, K sabitlenmeden) + bağımlılık grafiği füzyonu.
- **Kullanıcıya sağladığı değer:** Potansiyel olarak daha ince/gizli örüntüleri (yavaş yayılan olaylar) yakalayabilir.
- **AI'ın rolü:** Kümeleme kararının kendisi ML modelinde (DBSCAN + embedding); LLM ayrıca hipotez + karşı olasılık üretir.
- **Kullanıcı akışı:** A ile aynı kullanıcı deneyimi, arka planda daha karmaşık bir pipeline.
- **MVP özellikleri:** A'nın tüm özellikleri + embedding/DBSCAN katmanı + parametre ayarı (eps/min_samples).
- **MVP dışı özellikler:** A ile aynı.
- **Gerekli veri:** A ile aynı (alarms.csv, service_dependencies.csv, host_inventory.csv).
- **Kullanılabilecek teknoloji/servisler:** scikit-learn (DBSCAN) + embedding (TF-IDF veya sentence-embedding) + LLM.
- **Teknik riskler:** Yüksek — parametre (eps/min_samples) ayarı doğrulama verisi olmadan kör yapılıyor; kalan sürede hem doğru hem açıklanabilir hale getirmek riskli.
- **Demo senaryosu:** Aynı akış, ama sonuç kümeleri "neden böyle kümelendi" sorusuna DBSCAN'ın iç parametreleriyle cevap veriyor — A'ya göre daha az anlaşılır/açıklanabilir.

**Puanlama (10 üzerinden):**

| Kriter | Puan |
|---|---:|
| Problem Çözme Gücü | 8 |
| Kullanıcı Değeri | 8 |
| AI Katkısı | 7 |
| Yenilikçilik | 8 |
| 3 Saatte Yapılabilirlik | 4 |
| Teknik Risk | 3 |
| Demo Etkisi | 7 |
| Farklılaşma | 7 |
| Ölçeklenebilirlik | 7 |
| Jüri Etkisi | 6 |
| **TOPLAM** | **65** |

---

## STRATON'UN ÖNERİSİ (referans için)

**Önerilen: Çözüm A** — 3 gerekçe:
1. Jüri notu açık: "gerekçesiz doğru hipotezden, gerekçeli yanlış hipotez daha yüksek puan alabilir." A'nın deterministik grafiği her kararı satır satır açıklayabilir; B'nin DBSCAN'ı açıklaması zor.
2. Doğrulama verisi elimizde yok — B'nin parametrelerini "doğru" ayarladığımızı kanıtlayamayız, kör tahmin riski taşır.
3. Kalan süre (teslime ~2.5 saat) B'yi hem doğru hem UI/aksiyon takibiyle bitirmeye yetmeyebilir; A aynı temel değeri çok daha düşük riskle veriyor.

*(Bu dosya dış değerlendirme için hazırlanmıştır — nihai karar kullanıcı tarafından verilecektir.)*
