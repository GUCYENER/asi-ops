# Alert Storm Correlator

**3.000 alarmı, her biri kök neden hipotezi + gerekçesi + karşı olasılığı + önerilen aksiyonu taşıyan 5 olay kartına indirgeyen, bağımlılık farkında korelasyon motoru.**

> AO AI Hackathon 2026 — "Signal Sprint" · Senaryo S-A1 "Alarm Fırtınası" · Takım **ASI-OPS**

---

## Çözdüğümüz Problem

Gece 02:14. Nöbetçi mühendisin ekranında 2 saatlik pencerede 3.000 alarm akıyor. O gece birden fazla şey aynı anda ters gitmiş; bazıları birbiriyle ilişkili, bazıları tamamen bağımsız, önemli bir kısmı ise hiçbir olayla ilgisi olmayan arka plan gürültüsü.

Asıl güçlük alarm sayısı değil: **hangisinin kök neden, hangisinin türev etki, hangisinin gürültü olduğunun görünmemesi.** Bu yüzden müdahale sırası yanlış kurulur ve çözüm süresi uzar.

## Çözümümüzün Nasıl Çalıştığı

```
alarms.csv (3.000) + service_dependencies.csv (32) + host_inventory.csv (56)
   ↓  normalize · host→servis→dc/rack · yönlü bağımlılık grafiği · mesajdan hedef servis ayrıştırma
BASELINE      alarm tipi bazında zamansal yoğunlaşma oranı → sinyal / gürültü / belirsiz
   ↓
ÇEKİRDEK      kök-tipi (network_down, disk_full, ext_unreach, batch_overlap...) alarmlardan
              zaman + servis/bağımlılık/lokalite yakınlığıyla olay çekirdeği kümeleme
   ↓
ATAMA         her türev alarm ALARM SEVİYESİNDE skorlanır:
              mesaj hedefi (+5) · bağımlılık derinliği (+3/d) · aynı kabin (+2) · aynı servis (+3)
              iki geçişli — uzun kuyruklu cascade'ler sahipsiz kalmaz
   ↓
KÖK NEDEN     tip önceliği × erkenlik × şiddet → kök alarm + karşı olasılık + güven skoru
   ↓
ANLATIM       deterministik gerekçe (her zaman) + LLM doğal dil anlatısı (opsiyonel)
   ↓
ÇIKTI         öncelik sıralı olay kartları · gürültü denetim görünümü · aksiyon (sahip + durum)
```

Detaylı mimari: [docs/mimari.md](docs/mimari.md) · Karar süreci: [docs/plan.md](docs/plan.md)

## Sonuçlar (gerçek veri, ölçülmüş)

| Ölçüt | Değer |
|---|---|
| İşlenen alarm | **3.000 / 3.000** (örnekleme yok) |
| Üretilen olay kartı | **5** (üst sınır 15) |
| İndirgeme oranı | **%99,83** |
| Olaylara bağlanan alarm | 1.435 |
| Gürültü olarak elenen | 1.453 (her biri gerekçeli) |
| Belirsiz (gürültüye atılmadı) | 112 |
| **Hesap verilen toplam** | **3.000 / 3.000** — kayıp ve çift sayım yok |
| Naif yöntem karşılaştırması | 10dk pencere × servis grubu = **321 kart** |

**Ölçmediğimiz:** Kök neden isabeti. Doğrulama verisi jüride kapalı olduğu için doğruluk yüzdesi iddia etmiyoruz.

## Kurulum Adımları

Harici bağımlılık **yoktur**. Python 3.8+ dışında hiçbir şey kurmanız gerekmez.

```bash
git clone https://github.com/GUCYENER/asi-ops.git
cd asi-ops
```

Veri paketi repoda değildir (organizatör orijinal dosyaların repoya konmamasını belirtti). Katılımcı paketini şuraya yerleştirin:

```
data/katilimci_paketi/
├── alarms.csv
├── service_dependencies.csv
└── host_inventory.csv
```

## Çalıştırma Komutu

```bash
python run.py
```

Arayüz: **http://localhost:8000**

Alternatifler:

```bash
python run.py --cli                       # terminal modu (yedek demo)
python run.py --data <baska/klasor>       # farklı veri klasörü
```

## Kullanılan AI Araçları ve Model Sürümleri

| Araç | Model / Sürüm | Kullanım Amacı |
|---|---|---|
| Claude Code (SAKA) | `claude-opus-5` | Analiz, mimari kararlar, korelasyon motoru implementasyonu |
| Codex | — | Bağımsız veri analizi ve hipotez üretimi (ekip üyesi) |
| Claude (Azure/SAKA) | `claude-sonnet-4-5-20250929` | **Çalışma zamanı**: olay kartı gerekçesinin doğal dile çevrilmesi |

Çalışma zamanı LLM çağrısı **kritik yolda değildir** — erişilemezse deterministik şablon devreye girer, uygulama tam çalışmaya devam eder (`src/explain.py:template_narrative`).

## MCP Sunucu Listesi

MCP sunucusu kullanılmamıştır.

## Entegre Edilen API'ler

| API | Kullanım | Zorunlu mu |
|---|---|---|
| Azure/Anthropic Messages API (`claude-sonnet-4-5`) | Olay kartı doğal dil anlatısı | Hayır — şablon fallback mevcut |

## Kullanılan Açık Kaynak Kütüphaneler

**Yoktur.** Çekirdek ve arayüz tamamen Python standart kütüphanesi (`json`, `csv`, `datetime`, `collections`, `statistics`, `re`, `http.server`, `urllib`) ve vanilla JS/CSS ile yazılmıştır. Bu bilinçli bir karardır: jürinin makinesinde kurulum riski sıfırdır.

*(Geliştirme sırasındaki keşifsel analizde `pandas` kullanıldı, ancak üründe kullanılmamaktadır.)*

## Ekran Görüntüleri

[demo/](demo/) klasörüne bakınız.

## Deploy URL ve Bilinen Sınırlar

- **Deploy URL:** Yok — yerel çalışan ürün (organizatör deploy'u zorunlu tutmuyor).
- **Bilinen sınırlar:**
  - Kök neden isabetini ölçemiyoruz; doğrulama verisi kapalı. Ürettiğimiz 5 olay bir **hipotezdir**.
  - Eşikler (yoğunlaşma ≥4.0 sinyal, kanıt skoru ≥3.0) bu 2 saatlik pencereden türetildi; farklı ortamda yeniden kalibrasyon ister.
  - 112 alarm "belirsiz" olarak işaretlendi — bilerek gürültüye atılmadı, ayrı sekmede gösteriliyor.
  - "Benzer geçmiş olay örüntüsü" bonusu **sentetik arşivle** çalışıyor: organizatörün paketinde geçmiş olay kaydı yoktu, mekanizmayı kurup kendi ürettiğimiz 5 vakalık örnek arşivle gösteriyoruz (kartta açıkça etiketli). Gerçek ortamda kurumun kendi incident kayıtlarına bağlanır.
  - Aksiyon durumu bellek içinde tutulur (brifing kalıcı DB'yi kapsam dışı bırakıyor); sunucu yeniden başlarsa sıfırlanır.

## Proje Yapısı

```
asi-ops/
├── run.py                  # tek komutluk giriş noktası
├── src/
│   ├── correlator.py       # korelasyon motoru (çekirdek karar mantığı)
│   ├── explain.py          # LLM anlatı katmanı + şablon fallback
│   ├── server.py           # stdlib HTTP sunucusu + API
│   └── web/                # arayüz (vanilla JS/CSS)
├── data/                   # veri paketi buraya (repoya dahil değil)
├── docs/                   # plan, fazlar, mimari
├── prompts/                # kullanılan kritik prompt'lar
├── demo/                   # ekran görüntüleri
├── AI_JURI.md              # AI Jüri özeti
└── submission.json         # makine okunabilir künye
```
