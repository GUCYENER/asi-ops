# AI Jüri Özeti

> Takım **ASI-OPS** · Senaryo S-A1 "Alarm Fırtınası" · Proje: **Alert Storm Correlator**
> Her başlığın altında kanıt olarak dosya yolu verilmiştir.

---

## 1. AI Stratejimiz ve İş Akışı

**Dört bağımsız analiz → tek bütünleşik karar.** Kod yazmadan önce ekibin 4 üyesi aynı veriyi **birbirinden habersiz** analiz etti, sonra bulgular çakıştırıldı. Dördü de bağımsız olarak "deterministik korelasyon motoru, ML kümeleme değil" sonucuna vardı — bu yakınsama kararı güçlendirdi.

Her analizin diğerlerinde olmayan bir katkısı vardı ve hepsi birleşime girdi:

| Kaynak | Benzersiz katkı | Kanıt |
|---|---|---|
| Codex (Ali Alperen Erkoç) | 5. olayı (session-service bellek baskısı) yakaladı — diğer üç analiz kaçırmıştı. Ayrıca `message` alanının hedef servisi içerdiğini tespit etti | [data/alperen_analiz.md](data/alperen_analiz.md) |
| Claude Code (kaptan oturumu) | Zamansal yoğunlaşma oranı ile **objektif** sinyal/gürültü ayrımı | [data/BUTUNLESIK_ANALIZ.md](data/BUTUNLESIK_ANALIZ.md) §2.2 |
| Eren Eyüp Demir | Execution blueprint, kök neden skorlama formülü, checkpoint/kesme disiplini | [data/eren_eyup.md](data/eren_eyup.md) |
| Burhan Özdemirci | Bağımsız STRATON A/B doğrulaması + kabul testi önerisi | [data/BURHANCOZUM.md](data/BURHANCOZUM.md) |

**Hangi kararı insan verdi:**
- Çözüm seçimi (deterministik motor vs ML) — kaptan, STRATON puanlama tablosuna bakarak
- stdlib-only kısıtı — jürinin makinesinde kurulum riskini sıfırlamak için bilinçli insan kararı
- Bonus B3'ün (geçmiş örüntü) kapsam dışı bırakılması — veri yok, uydurmamak için

**Hangi kararı AI verdi / üretti:**
- Korelasyon motorunun implementasyonu, kanıt skorlama fonksiyonları, arayüz
- Alarm tipi yoğunlaşma profilinin hesaplanması ve eşiklerin veriden türetilmesi
- Çalışma zamanında olay kartı gerekçesinin doğal dile çevrilmesi

**Ekip geri bildirimi koda yansıdı:** Bütünleşik doküman ekip tarafından review edildi; çıkan P0 bulgusu (uzun kuyruklu cascade'lerin sonundaki alarmların sahipsiz kalması) doğrulandı ve düzeltildi — 02:58-03:01 arasındaki 7 kritik ödeme alarmının **2/7'si atanıyordu, 7/7'ye çıktı**.

Kanıt: [prompts/](prompts/), [CLAUDE.md](CLAUDE.md), [docs/plan.md](docs/plan.md), commit geçmişi

---

## 2. Problemi Nasıl Çözdük

**Yaklaşım:** Üç katmanlı kanıt birleştirme — hiçbir katman tek başına karar vermiyor.

1. **Objektif gürültü ayrımı.** Her alarm tipi için *zamansal yoğunlaşma oranı* = tepe 10dk / medyan 10dk. Arka plan gürültüsü zamana düzgün dağılır (`mem_high` 1.3x, `ntp_drift` 1.5x, `cert_expiry` 1.6x); olay sinyalleri yoğunlaşır (`thread_pool` 59x, `txn_fail` 43x, `disk_full` 17x). Eşik elle ayarlanmadı, veriden türetildi.
   Kanıt: `src/correlator.py:concentration_profile`

2. **Çekirdekten kümeleme.** Kök olabilecek tipler (ağ kesintisi, disk dolması, dış servis erişilemezliği, batch çakışması) çekirdek kabul edilir; zaman + bağımlılık + lokalite yakınlığıyla kümelenir.
   Kanıt: `src/correlator.py:cluster_seeds`

3. **Alarm seviyesinde atama.** Türev alarmlar pencereye göre değil, **her alarm için ayrı kanıt skoruyla** atanır: mesaj hedefi (+5), bağımlılık zinciri derinliği (+3/derinlik), aynı kabin (+2), aynı servis (+3). Zaman penceresi yalnızca aday daraltır. İki geçişlidir, böylece uzun kuyruklu cascade'ler sahipsiz kalmaz.
   Kanıt: `src/correlator.py:attach_score`, `src/correlator.py:build_events`

**Ürettiğimiz çıktı:** 5 olay kartı — her birinde kök neden hipotezi, gerekçesi, karşı olasılığı, etkilenen servisler, alarm sayısı, zaman aralığı, önerilen ilk aksiyon + sahip + durum.

**Ölçtüğümüz sonuç (gerçek sayılar):**

| Ölçüt | Değer |
|---|---|
| İşlenen alarm | 3.000 / 3.000 |
| Olay kartı | 5 (sınır 15) |
| İndirgeme | %99,83 |
| Gürültü elenen | 1.453 (her biri gerekçeli) |
| Belirsiz | 112 (gürültüye atılmadı) |
| Hesap verilen | **3.000 / 3.000** |
| Naif yöntem | 321 kart üretirdi |

Kanıt: [src/](src/), [docs/mimari.md](docs/mimari.md), [demo/](demo/)

---

## 3. X-Factor

**Aynı servisin aynı tipteki alarmlarını farklı olaylara ayırabiliyoruz — ve nedenini gösteriyoruz.**

`mobile-bff` servisinin `timeout` alarmları tek bir olaya ait değil. Motorumuz bunları mesaj hedefi ve bağımlılık zincirine bakarak **üç ayrı olaya** dağıttı:

| Olay | Kök neden | mobile-bff timeout sayısı |
|---|---|---:|
| EV-01 | dc1/rack-A ağ kesintisi | 15 |
| EV-03 | session-service bellek/GC baskısı | 23 |
| EV-04 | payment-provider-gw dış servis kesintisi | 18 |

Sıradan bir korelatör "aynı servis + yakın zaman + aynı alarm tipi" der ve bu 56 alarmı tek karta koyar — nöbetçi mühendisi tek bir yanlış müdahaleye yönlendirir. Biz üç farklı ekibe üç farklı aksiyon üretiyoruz.

**İkinci katman — karşı olasılık.** Her kartta reddedilen en güçlü alternatif hipotez ve *neden reddedildiği* yazıyor:
> "Alternatif: kök neden order-service üzerindeki pkt_loss olabilir mi? Hayır — ilk belirtisi kök alarmdan 0.2 dk sonra geldi, zaman sırası bu hipotezi zayıflatıyor."

**Üçüncü katman — gürültü denetimi.** Elenen 1.453 alarmın her biri için objektif gerekçe: *"tip zamanda düzgün dağılmış (yoğunlaşma 1.3x), hiçbir olay penceresiyle örtüşmüyor."*

Kanıt:
- `src/correlator.py:attach_score` — mesaj hedefi + bağımlılık skorlaması
- `src/correlator.py:counter_hypothesis`
- `src/correlator.py:noise_reason`

---

## 4. Çalıştırma

```bash
python run.py
```

Tek komut, harici bağımlılık yok (yalnızca Python standart kütüphanesi). `http://localhost:8000` adresinde olay kartları, gürültü denetim sekmesi, belirsiz alarmlar ve metrik paneli açılır.

Yedek: `python run.py --cli` — aynı kartları terminale basar.

Veri paketi `data/katilimci_paketi/` altına yerleştirilmelidir (orijinal dosyalar repoya konmadı).

---

## 5. Bilinen Sınırlar

- **Kök neden isabetini ölçemiyoruz.** Doğrulama verisi jüride kapalı. Ürettiğimiz 5 olay bir hipotezdir; "%X doğruluk" iddia etmiyoruz.
- **Eşikler bu pencereden türetildi.** Yoğunlaşma ≥4.0 ve kanıt skoru ≥3.0 eşikleri bu 2 saatlik veriden çıktı; farklı bir ortamda yeniden kalibrasyon ister.
- **112 alarm belirsiz kaldı.** Olay penceresinde görüldüler ama kök servisle kanıt bağları zayıftı. Bunları gürültüye atmak indirgeme oranını güzelleştirirdi; dürüst olmayı tercih edip ayrı bir sekmede gösteriyoruz.
- **Geçmiş örüntü bonusu (B3) yapılmadı.** Veri paketinde geçmiş olay arşivi yok. Sahte bir "benzer geçmiş olay" üretmek yerine kapsam dışı bıraktık.
- **Olay sayısı 5.** Jüri daha fazla olay tanımlamış olabilir; belirsiz kovasındaki alarmlar bu yüzden ayrı tutuldu ve denetlenebilir durumda.
- **Aksiyon durumu bellek içinde.** Brifing kalıcı veritabanını kapsam dışı bıraktığı için sunucu yeniden başlarsa durumlar sıfırlanır.
