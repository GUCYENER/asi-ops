# S-A1 "Alarm Fırtınası" — Bütünleşik Analiz ve Nihai Karar

> **Takım:** ASI-OPS · **Tarih:** 16 Eylül 2026 · **Aşama:** STRATON kararı tamamlandı, FORGE'a geçiliyor
> Bu belge, dört bağımsız analizin (3 ekip üyesi + Claude Code) birleştirilmiş nihai halidir.

---

## 1. Girdi Analizler

| Kaynak | Dosya | Yöntem |
|---|---|---|
| Ali Alperen Erkoç | `alperen_analiz.md` | Codex — tam veri taraması, 5 hipotez adayı, kanıt düzeyi etiketlemesi |
| Burhan Özdemirci | `BURHANCOZUM.md` | STRATON A/B, puanlama tablosu |
| Eren Eyüp Demir | `eren_eyup.md` | Master blueprint — execution/timebox/backlog/demo |
| Claude Code (kaptan oturumu) | bu oturum | pandas ile canlı profil, zamansal yoğunlaşma analizi |

**Yakınsama:** Dört analiz de bağımsız olarak **deterministik korelasyon motoru** önerdi (ML kümeleme değil), LLM'i yalnızca anlatı katmanında konumlandırdı. Bu karar tartışmasız kabul edildi.

---

## 2. Her Analizin Benzersiz Katkısı (birleşime giren)

### 2.1 Alperen — kaçırılan 5. olay + mesaj alanı sinyali

- **5. olay: session-service bellek baskısı.** ~01:35'ten itibaren %60→62→64→66→68→70→72→%74 ilerleyen `mem_high` serisi; 02:11-02:34 arası 18 `gc_pressure`; 02:38-02:52 arası 12 `oom_risk`.
  *Diğer analizlerde bu olay ya hiç yoktu ya da ödeme olayına yanlış atanmıştı.*
- **`message` alanı hedef servisi içeriyor.** 271 `timeout` kaydının mesaj hedefi incelendi: 172'si doğrudan bağımlılık, 54'ü dolaylı yol, 42'sinde yol yok, 3'ü kendi servisini gösteriyor. → Korelasyon için yapılandırılmış alanların ötesinde ek kanıt katmanı.
- **Aynı serviste eşzamanlı iki kök.** mobile-bff'te 02:35-03:05 arası 38 `timeout`: 12'si session-service hedefli (02:36-02:54), 26'sı payment-provider-gw hedefli (02:41-02:59). → **Tek servis + yakın zaman + aynı alarm tipi, aynı olay demek değildir.**
- **Üçlü karar ayrımı:** olaya bağlı / gürültü adayı / **belirsiz** — belirsiz alarmlar sessizce gürültüye atılmamalı.

### 2.2 Claude Code — objektif gürültü ölçütü

Her alarm tipi için **zamansal yoğunlaşma oranı** = tepe 10dk / medyan 10dk:

| Sinyal (≥5) | Oran | Gürültü (≤3) | Oran |
|---|---:|---|---:|
| thread_pool | 59.0 | latency_high | 2.9 |
| txn_fail | 43.0 | network_flap | 2.1 |
| conn_refused | 24.0 | log_rotate | 2.0 |
| db_conn_pool | 22.0 | backup_warn | 2.0 |
| pkt_loss | 22.0 | cpu_high | 2.0 |
| disk_full | 17.0 | disk_warn | 1.7 |
| db_write_fail | 14.0 | cert_expiry | 1.6 |
| ext_slow | 13.0 | ntp_drift | 1.5 |
| http_5xx | 12.2 | mem_high | 1.3 |
| network_down | 12.0 | | |
| ext_unreach | 11.0 | | |
| gc_pressure | 9.0 | | |
| batch_slow | 7.0 | | |
| oom_risk | 6.0 | | |
| timeout | 5.6 | | |
| batch_overlap | 4.0 | | |

**Neden değerli:** "Gürültü elemesi" resmi bir puanlama ölçütü ve bu ölçüt **elle eşik ayarlamadan, veriden türetilen tek bir sayıyla** savunulabiliyor. Eleme gerekçesi her alarm için üretilebilir.

**Uyarı:** `latency_high` (402) ve `mem_high` (240) *kısmen* olay türevi, kısmen taban gürültü. Tip bazında topluca elenmemeli — zaman penceresi yakınlığıyla ayrıştırılmalı.

### 2.3 Eren Eyüp — execution disiplini

- **Kök neden skoru:** tip önceliği × erkenlik × şiddet × downstream derinliği.
  *Kaynak tipler* (`network_down`, `disk_full`, `ext_unreach`, `batch_overlap`) > *türev tipler* (`timeout`, `http_5xx`, `thread_pool`).
- **JSON sözleşmesi** ile backend/frontend paralel çalışması.
- **Checkpoint'ler:** CP1 15:50 (uçtan uca dikey dilim) · CP2 16:40 (demo edilebilir) · 17:05 feature freeze · 17:20 push freeze · 17:25 remote doğrulama.
- **Kesme sırası** (geride kalınırsa): B3 geçmiş örüntü → zaman çizelgesi → LLM katmanı → gürültü sekmesi → karşı olasılık → Web UI (CLI'a düş). **Asla kesilmeyecek:** tüm veri işleme, ≤15 kart, kart gerekçesi, aksiyon+sahip+durum, README/AI_JURI, push.

### 2.4 Burhan — bağımsız doğrulama

Deterministik motor (A) 77, ML/DBSCAN (B) 65 puan. Kritik gerekçe: *"gerekçesiz doğru hipotezden, gerekçeli yanlış hipotez daha yüksek puan alır"* brifing notu, açıklanabilirliği doğruluğun önüne koyuyor → DBSCAN'ın "neden bu küme" sorusuna cevap verememesi diskalifiye edici zayıflık.

---

## 3. Çözülen Çelişkiler

| Çelişki | Karar | Gerekçe |
|---|---|---|
| Olay sayısı: 4 mü 5 mi? | **5 olay adayı**, ama motor sayıyı **sabitlemeyecek** | Claude'un yoğunlaşma analizi gc_pressure (9x) ve oom_risk'i (6x) sinyal olarak işaretlemişti ama ödeme penceresine yanlış atamıştı; Alperen'in ayrı session-service olayı doğru. Gerçek sayı bilinmiyor → eşik veriden türetilecek |
| stdlib mi, pandas mı? | **stdlib-only çekirdek** | Jürinin makinesinde ne kurulu olduğunu bilmiyoruz; "temiz clone + tek komut" zorunlu (Z6). pandas yalnızca yerel analizde kullanıldı, üründe kullanılmayacak |
| LLM zorunlu mu? | **Opsiyonel anlatı katmanı + şablon fallback** | Azure/Claude API erişimi doğrulandı (çalışıyor), ama kritik yola konulmayacak — demo tek bir API hatasıyla çökmeyecek |
| Gürültü elemesi ne kadar agresif? | **Muhafazakâr + üçlü ayrım** (olay / gürültü / belirsiz) | "Gürültü elemesi" ölçütü ters tepebilir; her eleme kararı gerekçesiyle loglanacak |

---

## 4. Tespit Edilen Olay Adayları (kanıtlarıyla)

> Bunlar **hipotezdir**, doğrulama verisi jüride kapalı. Motor bu listeye sabitlenmeyecek, veriden türetecek.

| # | Zaman | Kök neden hipotezi | Kanıt | Tip |
|---|---|---|---|---|
| E1 | 01:42–01:55 | **dc1/rack-A ağ kesintisi** | 12 `network_down` + 22 `pkt_loss`, **34'ünün tamamı dc1/rack-A**, 9 host. Ardından 79 `thread_pool`, 100 `http_5xx` cascade | Ani patlama |
| E2 | 02:05–02:35 | **billing-db disk dolması** | 17 `disk_full` (sev 5.0), %97-100 dolu, 28 sn sonra "tablespace genişletilemedi"; 34 `db_write_fail` → billing-service `txn_fail` → invoice-batch | Yavaş yayılan |
| E3 | 02:40–02:57 | **payment-provider-gw dış servis kesintisi** | 11 `ext_unreach` + 13 `ext_slow` (sev 5.0, HTTP 504); payment-service 34 timeout'un **tamamı** payment-provider-gw hedefli → order → mobile-bff | Ani patlama |
| E4 | 03:05–03:25 | **batch çakışması → subscriber-db conn pool** | 4 `batch_overlap` (03:05-03:06) → report/reconciliation `batch_slow` → subscriber-db 19 `db_conn_pool` → subscriber-service | Yavaş, en zor |
| E5 | 01:35–02:52 | **session-service bellek baskısı** | mem %60→74 ilerleyen seri, 18 `gc_pressure` (02:11-02:34), 12 `oom_risk` (02:38-02:52) | Çok yavaş yayılan |

**Kritik ayrım testi:** E2 ve E3 birleştirilmemeli (ikisi de payment/billing zincirine dokunuyor ama 02:35-02:40 arası sakinleşme + farklı kök tip imzası var). E3 ve E5 birleştirilmemeli (mobile-bff aynı anda ikisinden de etkileniyor).

---

## 5. Nihai Çözüm — "Dependency-Aware Alert Storm Correlator"

### Uçtan uca akış

```
INPUT          alarms.json (3.000) + service_dependencies.csv (32) + host_inventory.csv (56)
   ↓
PREPROCESS     normalize · host→servis→dc/rack · yönlü bağımlılık grafiği ·
               message'tan hedef servis + sayısal sinyal (%100, HTTP 504, p99 ms) ayrıştırma
   ↓
BASELINE       alarm tipi bazında zamansal yoğunlaşma oranı → sinyal/gürültü/belirsiz
   ↓
DETECTION      anomali pencereleri: (a) patlama = z-skor, (b) yavaş yükseliş = hareketli ort. artışı
   ↓
CORRELATION    bağımlılık yakınlığı + message-hedef eşleşmesi + host/rack/dc ortaklığı +
               zaman yakınlığı → olay ataması (ayrılma eşiği = yanlış birleştirme koruması)
   ↓
ROOT CAUSE     skor = tip önceliği × erkenlik × şiddet × downstream derinliği
   ↓
EXPLANATION    WHAT / WHY / CONFIDENCE / SIGNALS / COUNTER-HYPOTHESES
               (LLM anlatı katmanı — opsiyonel, şablon fallback'li)
   ↓
ACTION         kök tipine göre ilk aksiyon + sahip (servis kritikliğinden) + durum
   ↓
OUTPUT/UI      öncelik sıralı kart listesi → kart detayı → gürültü denetimi → aksiyon durumu
```

### Teknoloji

- **Çekirdek:** Python 3 **stdlib only** (`json`, `csv`, `datetime`, `collections`, `statistics`, `re`) — sıfır kurulum riski
- **UI:** statik HTML + vanilla JS, `http.server` ile JSON servisi + aksiyon POST
- **LLM (opsiyonel):** Azure üzerinden `claude-sonnet-4-5`, Anthropic Messages formatı — **erişim doğrulandı**
- **DB:** yok (bellek içi — brifing izin veriyor)

### X-Factor (3 katman)

1. **Karşı olasılık paneli** — her kartta reddedilen alternatif + neden reddedildiği (zaman sırası, lokalite, bağımlılık yönü)
2. **Gürültü denetim görünümü** — elenen her alarm için objektif gerekçe (yoğunlaşma oranı + olay penceresine uzaklık)
3. **Aynı serviste iki kök ayrımı** — mobile-bff'in 38 timeout'unun 12/26 olarak iki farklı olaya ayrılması. *Sıradan bir korelatör bunu tek karta koyar.*

---

## 6. Ölçütler (uydurma metrik yok)

| Metrik | Hesap | Not |
|---|---|---|
| İndirgeme oranı | kart / 3.000 | Hedef 5-12 kart |
| Kapsam | işlenen / 3.000 | %100 zorunlu (Z1) |
| Hesap verebilirlik | olay + gürültü + belirsiz = 3.000 | Kayıp/çift sayım yok |
| Gürültü oranı | elenen / 3.000 | Denetim sekmesinde sayaç |
| Baseline karşılaştırma | naif (5dk pencere + servis grubu) kaç kart üretir | Tablo olarak gösterilecek |

**Ölçemeyeceğimiz:** Kök neden isabeti — doğrulama verisi jüride kapalı. *"%X doğruluk"* iddiası edilmeyecek; "5 bağımsız olay adayı tespit ettik, her biri için gerekçe ve karşı olasılık üretiyoruz" denecek.

---

## 7. Karar

**ONAYLANDI:** Yukarıdaki bütünleşik çözüm, 4 analizin birleşimi olarak nihai kapsamdır. FORGE aşamasına geçiliyor.

**İlk iş:** JSON sözleşmesini dondurmak (backend/frontend paralelliğini açar), ardından stdlib çekirdek.
