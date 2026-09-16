# Mimari — Alert Storm Correlator

## Genel Bakış

Tek süreçli, harici bağımlılığı olmayan bir Python uygulaması. Üç veri dosyasını toplu okur, korelasyon motorundan geçirir, sonucu bellek içinde tutar ve stdlib HTTP sunucusuyla hem JSON API hem statik arayüz sunar.

**Neden monolith ve stdlib-only:** Jürinin makinesinde hangi paketlerin kurulu olduğunu bilmiyoruz ve "temiz clone + tek komut" zorunlu. Her harici bağımlılık, demoyu kaybetme riskidir. `pandas` geliştirme sırasındaki keşifsel analizde kullanıldı; üründe kullanılmıyor.

## Bileşenler

| Bileşen | Dosya | Sorumluluk |
|---|---|---|
| Korelasyon motoru | `src/correlator.py` | Tüm karar mantığı: yükleme, profil, kümeleme, atama, kök neden, gerekçe |
| Açıklama katmanı | `src/explain.py` | LLM doğal dil anlatısı + deterministik şablon fallback |
| HTTP sunucusu | `src/server.py` | JSON API, statik dosya servisi, aksiyon durumu (bellek içi) |
| Arayüz | `src/web/` | Olay kartları, gürültü denetimi, belirsiz sekmesi, metrikler |
| Giriş noktası | `run.py` | Tek komut; `--cli` yedek modu |

## Veri Akışı

```
data/katilimci_paketi/*.csv
        │
        ▼
load_data()          alarm kayıtları + yönlü bağımlılık grafiği + host envanteri
        │             mesajdan hedef servis ve yüzde değeri ayrıştırılır
        ▼
concentration_profile()   her alarm tipi için tepe/medyan oranı
        │                 → sinyal (≥4.0) / belirsiz / gürültü (<3.0)
        ▼
cluster_seeds()      kök-tipi alarmlar zaman + servis/bağımlılık/lokalite ile kümelenir
        │
        ▼
build_events()       türev alarmlar ALARM SEVİYESİNDE kanıt skoruyla atanır (iki geçiş)
        │
        ▼
pick_root() + counter_hypothesis() + why_text()
        │
        ▼
run() → {events[], noise[], unclear[], type_profile[], metrics{}}
        │
        ├──► server.py  ──► /api/data, /api/explain/<id>, POST /api/actions/<id>
        └──► run.py --cli ──► terminal tablosu
```

## Kritik Tasarım Kararları

### 1. Zaman penceresi karar vermez, yalnızca aday daraltır

İlk tasarımda olaylar zaman penceresiyle tanımlanıp içindeki alarmlar o olaya atanıyordu. Ekip review'unda bunun kırılgan olduğu tespit edildi: olaylar zamanda iç içe geçiyor (session-service olayı 01:35–03:01 arası diğer üç olayın üstünden geçiyor).

**Karar:** Atama alarm seviyesinde yapılır. Her alarm, her aday olaya karşı ayrı ayrı skorlanır:

| Kanıt | Puan |
|---|---:|
| Alarm mesajı doğrudan kök servisi hedef gösteriyor | +5.0 |
| Alarm kök servisin kendi üzerinde | +3.0 |
| Bağımlılık zinciri var (derinlik d) | +3.0 / d |
| Olayın yoğunlaştığı kabinde | +2.0 |

Eşik: 3.0. Altında kalan sinyal tipleri "belirsiz", gürültü tipleri gerekçesiyle "gürültü" olur.

### 2. İki geçişli atama

Cascade'ler uzun kuyrukludur; ödeme zinciri olayının son alarmları çekirdek penceresinin 15 dakika sonrasında geliyordu. Tek geçişte bu 7 kritik alarmın 5'i sahipsiz kalıyordu.

**Karar:** İlk geçişten sonra olay pencereleri atanan alarmlarla genişletilir, ikinci geçiş bu genişlemiş pencerelerle çalışır. Sonuç: 2/7 → 7/7.

### 3. Gürültü ayrımı sabit listeyle değil, ölçümle

"cert_expiry gürültüdür" gibi elle liste yazmak veriye aşırı uyum (overfit) olurdu ve jüri "genel mi?" diye sorduğunda savunulamazdı.

**Karar:** Her tip için zamansal yoğunlaşma oranı hesaplanır. Gürültü zamana düzgün dağılır, olay sinyalleri yoğunlaşır. Eşik veriden türetilir, host/servis adı koda yazılmaz.

### 4. Ağ olaylarında kök neden servis değil, fiziksel alan

`network_down` alarmı hangi servisin host'unda görüldüyse o servis kök sanılabilir. Ama 34 ağ alarmının tamamı tek kabinde (dc1/rack-A), 9 farklı host ve 9 farklı serviste.

**Karar:** Ağ tipi kök alarmlar tek bir kabinde yoğunlaşıyorsa kök neden o **paylaşılan fiziksel ağ alanı** olarak raporlanır (`network_domain()`).

### 5. LLM kritik yolda değil

**Karar:** Karar üretimi tamamen deterministik. LLM yalnızca hesaplanmış kanıtları doğal dile çevirir ve yeni bilgi üretmesi promptla yasaklanır. Erişilemezse `template_narrative()` devreye girer; uygulama tam çalışır.

## Kapsam Dışı Bırakılanlar

- Gerçek zamanlı akış işleme (brifing toplu okumayı yeterli sayıyor)
- Kalıcı veritabanı (bellek içi kabul ediliyor)
- Kullanıcı yönetimi / yetkilendirme
- Benzer geçmiş olay eşleştirme (veri paketinde geçmiş arşiv yok)
