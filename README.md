# asi-ops

## Proje Adı ve Özet

**ASI-OPS — Alarmdan karara.** Alarm fırtınasını kanıtları incelenebilen olay hipotezlerine ve sorumlusu belirlenmiş ilk aksiyonlara dönüştüren yerel operasyon masası.

## Çözdüğümüz Problem

S-A1 paketindeki 3.000 alarm aynı anda birden fazla soruna işaret ediyor. Yalnız zaman veya servis bazında gruplama, oturum ve ödeme sorunlarını aynı karta karıştırabilir. Operatörün bağlantıyı, belirsizliği ve ilk aksiyonu birlikte görebilmesi gerekir.

## Çözümümüzün Nasıl Çalıştığı

1. Bütün kayıtları, envanteri ve yönlü bağımlılıkları doğrular.
2. Kök alarm imzalarını ve host bazında artan bellek serilerini bulur.
3. Her alarmı zaman, servis, mesaj hedefi, grafik yolu ve fiziksel hata alanıyla puanlar.
4. Olay / gürültü adayı / belirsiz kararını gerekçesiyle saklar.
5. Belirsizlerdeki tekrarlayan kümeleri düşük kanıtlı inceleme kartlarında gösterir.
6. Düzenlenebilir sorumlu rolü, durum, not geçmişi ve JSON dışa aktarımı sunar.

Katılımcı verisinde **5 olay + 3 inceleme kartı**; **1.015 olaya bağlı + 1.664 gürültü adayı + 321 belirsiz = 3.000 alarm**. İnceleme kartlarındaki 84 kayıt belirsiz toplamının içindedir. Bunlar doğruluk/recall ölçümü değildir. Detay: [geliştirme raporu](docs/gelistirme_raporu.md), [mimari](docs/mimari.md).

## Alarmları Nasıl Sınıflandırıyoruz — Yöntemin Tamamı

Hiçbir alarm silinmez. Her kayıt **olaya bağlı / gürültü adayı / belirsiz** üçlüsünden birine, **gerekçesiyle birlikte** yazılır. Toplam her zaman 3.000'e eşittir.

### İş Kuralının Özeti

**Gürültü ayrımı:** Her alarm tipinin zaman içindeki dağılımına bakılır. Sürekli ve düzenli aralıklarla gelen alarmlar rutin sistem bildirimidir; ani ve yoğun şekilde artan alarmlar gerçek bir olayın işaretidir.

**Olay ataması:** Bir alarmın bir olaya bağlanabilmesi için kanıt hem yeterince güçlü olmalı hem de en yakın alternatiften belirgin şekilde ayrışmalı. İki olasılık birbirine yakınsa kayıt kesin bir kararla eşleştirilmez, belirsiz olarak işaretlenir.

Aşağıda bunun tam teknik karşılığı var.

### 1. Normalizasyon ve doğrulama

Her alarm okunurken şunlar çıkarılır:

- **Envanter birleştirmesi:** `host` alanından servis, veri merkezi, kabin ve iş kritikliği türetilir.
- **Mesaj hedefi:** "charging-service servisine yapilan cagri zaman asimina ugradi" gibi metinlerden **hedef servis adı** ayrıştırılır. Bu, en güçlü korelasyon kanıtlarından biridir.
- **Sayısal sinyal:** "yuzde 100 dolu", "503 ms", "HTTP 504" gibi değerler ayrı alanlara alınır; farklı büyüklükler birbirine karıştırılmaz.
- **Bağımlılık grafiği:** `kaynak_servis -> hedef_servis` yönlü okunur; *kaynak, hedefe bağımlıdır*. Etki ters yönde aranır.

### 2. Alarm tiplerinin rol ayrımı

| Rol | Tipler | Anlamı |
|---|---|---|
| **Kök imzası (güçlü)** | `network_down`, `pkt_loss` · `disk_full` · `gc_pressure`, `oom_risk` · `ext_unreach`, `ext_slow` · `batch_overlap` | Olayı **başlatabilecek** tipler |
| **Belirti (türev)** | `timeout`, `http_5xx`, `thread_pool`, `txn_fail`, `db_write_fail`, `db_conn_pool`, `batch_slow` | Kök nedenin **sonucu** olabilecek tipler |
| **Yaygın** | `mem_high`, `cpu_high`, `latency_high`, `network_flap`, `disk_warn` | Hem olayda hem arka planda görülür; tek başına kanıt sayılmaz |
| **Bakım** | `cert_expiry`, `backup_warn`, `ntp_drift`, `log_rotate` | Rutin işlerden doğar, olayla ilgisi genelde yoktur |

Her olay ailesinin ayrıca kendi **uyumlu belirti listesi** vardır; uyumsuz tip o olaya bağlanamaz.

### 3. Olay çekirdeklerinin bulunması

Kök imzası taşıyan alarmlar aileye göre kümelenir:

- **Ağ:** aynı (veri merkezi, kabin) içindeki `network_down` / `pkt_loss` — en az **3** güçlü sinyal
- **Depolama / Bellek / Dış servis / Batch:** servis bazında — en az **2** güçlü sinyal
- Güçlü sinyaller arası boşluk en çok **10 dakika** (bellekte 30 dakika)
- Tek başına kalan güçlü sinyal olay açmaz, **belirsiz** olur

**Yavaş gelişen bellek olayı özel ele alınır.** GC/OOM alarmından geriye doğru **75 dakika** içinde, aynı host'ta yüzdenin **monoton arttığı** zincir aranır: en az **4 ölçüm**, en az **10 dakika** süre, en az **6 puan** artış, adımlar 30 sn – 8 dk arası. Tipik adımın **2,5 katından** büyük sıçrama zinciri böler; aradaki rastgele düşük ölçümler öncül sayılmaz. *Bu, sabit "5 dakikalık pencere" yaklaşımının kaçıracağı olaydır.*

**Batch olayı** ayrı bir mekanizmadır: scheduler'a bağımlı **en az iki iş** aynı dönemde yavaşlıyorsa, ortak bağımlılıkları kaynak baskısı adayı olur.

### 4. Her alarmın kanıt puanı — asıl karar burada

Zaman penceresi **karar vermez, yalnızca aday daraltır.** Her alarm, her aday olaya karşı ayrı ayrı puanlanır:

| Kanıt | Puan |
|---|---:|
| Mesaj hedefi grafikte doğrulanıyor | **+6** |
| Alarm kök servisin kendi üzerinde | +4 |
| Yönlü bağımlılık yolu yakınlığı | +2 … +4,4 |
| Ağ olayında aynı fiziksel alan (dc + kabin) | +5 |
| Batch'te ortak kaynak veya iş | +3 |
| Aileye özgü hata belirtisi | +2 |
| Kök sinyal dönemiyle çakışma | +1 |
| Temel puan | +3 |
| Mesaj hedefi olayla ilgisiz | **−3** |
| Yaygın tip, yerel tekrar yoksa | −1 |

**Atama kuralı:** en iyi puan **8 veya üstü** olmalı *ve* ikinci adayla fark **en az 2** olmalı. Puanlar birbirine yakınsa kayıt zorla atanmaz, **belirsiz** kalır. Kısmi destek (**6 ve üstü**) alan kayıt gürültüye de düşürülmez.

> Bu kural X-Factor'ümüzün temelidir: `mobile-bff` üzerindeki eşzamanlı `timeout` alarmları mesaj hedefine göre farklı köklere ayrılır — 12'si oturum, 26'sı dış ödeme olayına.

### 5. Gürültü kararı — liste değil, ölçüm

Her alarm tipi için **zamansal yoğunlaşma** hesaplanır:

```text
yoğunlaşma = tepe 10 dk dilimi / medyan 10 dk dilimi
```

Arka plan gürültüsü sürekli çalışan süreçlerden doğar, zamana düzgün yayılır, oran 1'e yaklaşır. Gerçek olaylar patlama yapar, oran yükselir. Ölçülen değerler: `thread_pool` 59x, `txn_fail` 43x, `disk_full` 17x — buna karşılık `mem_high` 1,3x, `ntp_drift` 1,5x, `cert_expiry` 1,6x.

**Ama düşük oran tek başına eleme sebebi değildir.** Gürültü kararı için şunlar birlikte aranır: bakım/yaygın tip **ve** düşük yoğunlaşma **ve** kök/trend/yerel olay bağlamının bulunmaması. Eleme gerekçesi her alarm için ayrı yazılır ve denetim ekranında görünür.

### 6. Belirsiz kayıtlar ve inceleme kartları

Atanamayan ama gürültü de sayılamayan kayıtlar **belirsiz** kalır. İçlerinde tekrar eden kümeler varsa **düşük kanıtlı inceleme kartı** açılır: aynı servis, aynı belirsizlik gerekçesi, aralarında en çok 5 dakika boşluk, en az 8 alarm / 2 host / 5 dakika süre.

Bu kartlar **yeni bağımsız olay iddiası değildir**; kayıtlar belirsiz sayacında kalır, ikinci kez sayılmaz.

### 7. Kök neden seçimi ve karşı olasılık

Küme içinde kök adayı **tip önceliği × erkenlik × şiddet × bağımlı derinliği** ile sıralanır. Bu bir **kanıt sıralama** ölçüsüdür; olasılık veya doğruluk değildir.

Ağ olaylarında kök **tek bir servis değil, paylaşılan fiziksel alan** olarak raporlanır: 34 ağ alarmının tamamı tek kabinde, 9 farklı host ve 9 farklı serviste görülüyorsa sorun o host'ların paylaştığı ağdadır.

Her kart ayrıca **reddedilen en güçlü alternatifi** ve neden reddedildiğini (zaman sırası, lokalite, bağımlılık yönü) gösterir.

### 8. Benzer geçmiş olaylar

Kartın imzası geçmiş olay arşiviyle karşılaştırılır:

```text
benzerlik = 0,45 x Jaccard(alarm tipleri) + 0,35 x Jaccard(servisler) + 0,20 x kategori eşleşmesi
```

Arşivde hazır bir `similarity_to_current` alanı bulunmasına rağmen **kullanılmamıştır**; kullanılsaydı skor bu veri setine gömülü bir sabit olur, başka bir arşivde anlamsız kalırdı. Arşiv sentetiktir ve arayüzde bu şekilde etiketlenmiştir.

### 9. AI'nın rolü ve rolü olmayan yer

**Sınıflandırmanın hiçbir adımında LLM kullanılmaz.** Gerekçesi:

- **Determinizm:** aynı veri her çalıştırmada aynı sonucu verir; operasyon kararında bu zorunludur
- **Denetlenebilirlik:** her kararın arkasında bir sayı vardır, model kanaati değil
- **Hız:** 3.000 alarm yaklaşık 160 ms'de işlenir
- **Erişim:** çekirdek çevrimdışı çalışır, API anahtarı gerektirmez

LLM yalnızca **hesaplanmış kanıtı** okunur bir anlatıya çevirir; yeni kök, sayı veya servis üretmesi promptla yasaklanır ve döndürdüğü kanıt kimlikleri doğrulanır. Erişim yoksa deterministik şablon devreye girer ve uygulama tam çalışır.

## Kurulum Adımları

Python **3.9 veya üstü** yeterli. Paket kurulumu, Node, veritabanı veya API anahtarı gerekmez.

```bash
git clone https://github.com/GUCYENER/asi-ops.git
cd asi-ops
```

Katılımcı paketini `data/katilimci_paketi/` altına yerleştirin (orijinal dosyalar repoya konmadı). Farklı bir konum kullanacaksanız `--data-dir` ile gösterin. `alarms.json` **veya** `alarms.csv`, `host_inventory.csv`, `service_dependencies.csv` gerekir. İkisi de varsa JSON seçilir; ikisi birlikte sayılmaz.

`.env` bu çalışma alanında boş anahtarlarla hazır. Başka makinede isteğe bağlı olarak `.env.example` dosyasını `.env` olarak kopyalayın. Çekirdek için zorunlu değildir.

## Çalıştırma Komutu

```bash
python run.py
```

Tarayıcı: **http://127.0.0.1:8000**. (Eşdeğeri: `python app.py --data-dir data/katilimci_paketi`) Port doluysa `--port 8002` ekleyin. Varsayılan veri konumu proje klasörünün kardeşi `katilimci_paketi` dizinidir.

Sunucusuz yedek çıktı:

```bash
python app.py --data-dir data/katilimci_paketi --export outputs/report.json
```

Testler:

```bash
python -m pytest tests -q
```

Sentetik örnekler, gerçek veri regresyonları, JSON/CSV eşdeğerliği, zaman/kimlik/servis değişiklikleri, HTTP uçları, aksiyonlar ve LLM fallback'i kapsanır. Katılımcı paketi yoksa ona bağlı testler açıkça atlanır. Test sonuçları: [doğrulama](docs/dogrulama.md).

## Kullanılan AI Araçları ve Model Sürümleri

| Araç | Model / Sürüm | Kullanım Amacı |
|---|---|---|
| Codex | GPT-6; daha ayrıntılı build kimliği sağlanmadı | Analiz, kod, test ve dokümantasyon üretimi |
| Claude Code | `claude-opus-5` | Bütünleşik analiz, B3 geçmiş olay eşleştirme, entegrasyon ve doğrulama |
| Azure Anthropic Messages | `claude-sonnet-4-5-20250929` | Kanıtların kısa anlatısı; **canlı erişim doğrulandı**, kanıt kimlikleri şema kontrolünden geçiyor |

Kararları LLM vermez. Eğitilmiş ML modeli veya ölçülmüş doğruluk iddiası yok. İnsan kapsamı ve bütünleşik analizi onayladı; kod ve sonuçlar incelemeye açık.

## MCP Sunucu Listesi

Ürün çalışma zamanında MCP sunucusu kullanmaz. Geliştirmede yerel dosya/komut araçları ve resmi API dokümanı araması kullanıldı; harici ekip hesabına erişilmedi.

## Entegre Edilen API'ler

- Yerel HTTP JSON API: [sözleşme](docs/sozlesme.md).
- Azure Anthropic Messages: `.env` içine `AZURE_ANTHROPIC_ENDPOINT`, `AZURE_ANTHROPIC_API_KEY` yazıp `LLM_ENABLED=true` yapılır. İstek yalnız "AI ile kısa özet" düğmesiyle gider. Sekiz saniye timeout, kanıt kimliği doğrulaması ve hata halinde şablon geri dönüşü var. **Bu kurulumda canlı çağrı doğrulandı.**
- Entegrasyon biçimi [Microsoft'un resmi Claude/Foundry belgesine](https://learn.microsoft.com/en-us/azure/foundry/foundry-models/how-to/use-foundry-models-claude) dayanır. Canlı sağlayıcı çağrısı bu kurulumda test edildi ve çalışıyor.

## Ekran Görüntüleri

Hepsi çalışan uygulamadan, `tests/capture-screens.mjs` ile otomatik alınmıştır (Chrome DevTools Protocol; ek paket kurulumu gerekmez).

![Operasyon masası](demo/operasyon-masasi.png)

| Görüntü | Ne gösteriyor |
|---|---|
| [operasyon-masasi.png](demo/operasyon-masasi.png) | Özet sayaçlar, alarm yoğunluğu, öncelikli olay listesi |
| [zaman-cizelgesi.png](demo/zaman-cizelgesi.png) | Olayların zamanda iç içe geçtiği çizelge |
| [olay-karti.png](demo/olay-karti.png) | Kanıt özeti, AI anlatısı, renk kodlu bölümler, aksiyon |
| [benzer-gecmis-olaylar.png](demo/benzer-gecmis-olaylar.png) | Geçmiş olay eşleştirmesi ve benzerlik kırılımı |
| [yontem-ve-olcum.png](demo/yontem-ve-olcum.png) | Yoğunlaşma profili ve ölçümler |
| [alarm-izlenebilirligi.png](demo/alarm-izlenebilirligi.png) | 3.000 alarmın filtrelenebilir denetim ekranı |
| [mobil.png](demo/mobil.png) | Mobil görünüm |

## Deploy URL ve Bilinen Sınırlar

- **Deploy URL:** Yok; yerel `127.0.0.1` uygulaması (organizatör deploy'u zorunlu tutmuyor).
- Altın etiketler kapalı; kök doğruluğu ve gürültü isabeti bilinmiyor. Eşikler açık heuristiklerdir.
- İnceleme kartları yeni bağımsız olay kanıtı değildir; kayıtlar belirsiz kalır.
- Aksiyonlar bellekte tutulur. Yeniden başlatmadan önce raporu indirin; dışa aktarımı geri yükleme özelliği yok.
- Tam dosya analizi; gerçek zaman, erken tahmin ve otomatik düzeltme yok.
- Yerel demo sunucusu; kullanıcı doğrulaması veya üretim dağıtımı kapsamda değil.
- Ham katılımcı verileri projeye kopyalanmadı. `outputs/`, `data/` ve `.env` Git dışında tutulur.

## Proje Yapısı

```text
asi-ops/
├── run.py                   # tek komutluk giris
├── app.py                   # CLI, .env, sunucu / JSON çıktı
├── src/engine.py            # korelasyon, kanıt, inceleme adayları
├── src/server.py            # API ve aksiyon geçmişi
├── src/narrative.py         # opsiyonel anlatı / fallback
├── src/history.py           # benzer geçmiş olay eşleştirme (B3)
├── static/                  # HTML + CSS + vanilla JS
├── tests/                   # unittest + tarayıcı kontrolü
├── README.md / AI_JURI.md / submission.json / CLAUDE.md
├── docs/                    # sözleşme, mimari, plan, sonuçlar
├── prompts/                 # kritik yönlendirmeler
├── demo/                    # ekran görüntüleri ve demo akışı
├── outputs/                 # yerel JSON; Git dışında
├── .env.example             # anahtarsız şablon
├── codex_analiz.md           # ilk analiz; korunmuştur
└── BUTUNLESIK_ANALIZ.md      # kapsam kararı + uygulama eki
```
