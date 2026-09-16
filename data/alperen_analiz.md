# S-A1 Alarm Fırtınası — Codex ayrıntılı analiz ve çözüm seçenekleri

**Tarih:** 16 Eylül 2026 · **Aşama:** SCOUT + STRATON, çözüm seçimi öncesi.

**Çalışma sınırı:** Kullanıcının talimatıyla yalnızca analiz ve öneri hazırlanmıştır. Uygulama, model, gruplama motoru veya arayüz geliştirilmemiştir. CSV/JSON dosyaları salt okunur olarak taranmış; sayımlar, çapraz kontroller ve örüntü incelemeleri yapılmıştır. Bu rapordaki öneriler uygulanmış veya başarıları ölçülmüş değildir.

## 1. Yönetici özeti: aslında hangi sorunu çözmeliyiz?

**Nöbetçi mühendis, 3.000 alarmın içinden hangi bağımsız olaylara, hangi sırayla, hangi ilk aksiyonla müdahale edeceğini anlayabilmeli.** Her önerinin hangi kayıtlara ve ilişkilere dayandığı görülebilmeli.

Bu görevin dört ayrı kararı var:

1. **İlişkilendirme:** Hangi alarmlar aynı olayın belirtileri?
2. **Kök neden hipotezi:** Bu belirtileri en iyi açıklayan kaynak veya mekanizma hangisi?
3. **Gürültü ayrımı:** Hangi alarmlar mevcut olaylara ilişkin aksiyon gerektirmiyor; neden?
4. **Operasyonel takip:** İlk ne yapılacak, kimin sorumluluğunda, hangi durumda?

Az sayıda kart üretmek tek başına yeterli değil. Bütün alarmları tek karta koymak indirgeme oranını iyileştirir; bağımsız olayları birleştirdiği için çözümü başarısız kılar.

**Önerim: A — kanıta dayalı, zaman + servis bağımlılığı + fiziksel konum + belirti uyumunu birlikte kullanan açıklanabilir korelasyon çözümü.** Öncelik, kısa bir olay kuyruğu ve her karta bağlı gerekçeli aksiyon kaydıdır. Doğal dil açıklaması çekirdeğin hesapladığı kanıtlardan üretilebilir; dış LLM zorunlu değildir.

**Önemli bulgu:** Veride en az beş ayrı incelenmeye değer örüntü adayı görüldü. Bunlar doğrulanmış olay etiketleri değildir; gerçek olay sayısı bilinmiyor. Çözüm beş olaya veya belirli alarm kimliklerine sabitlenmemeli.

## 2. Kaynaklar ve kanıt düzeyleri

| Kod | Kaynak | Bu raporda kullanım |
|---|---|---|
| K1 | [SENARYO_BRIFINGI.md](../katilimci_paketi/SENARYO_BRIFINGI.md) | Problem, zorunlular, kabul kriterleri, değerlendirme ve teslim |
| K2 | [VERI_SOZLUGU.md](../katilimci_paketi/VERI_SOZLUGU.md) | Alan anlamları, bağımlılık yönü, sentetik veri ve gizli doğrulama |
| K3 | `katilimci_paketi/Signal Sprint – Senaryo Açıldı _ S-A1 Alarm Fırtınası.eml` | MIME içindeki düz metin okundu; ek teslim kuralları ve canlı demo beklentisi |
| V1 | [alarms.csv](../katilimci_paketi/alarms.csv) | 3.000 kaydın tamamında salt okunur inceleme |
| V2 | [alarms.json](../katilimci_paketi/alarms.json) | CSV ile içerik eşitliği kontrolü |
| V3 | [host_inventory.csv](../katilimci_paketi/host_inventory.csv) | Host, servis, veri merkezi, kabin ve iş kritikliği |
| V4 | [service_dependencies.csv](../katilimci_paketi/service_dependencies.csv) | Servisler arası yönlü ilişkiler |
| P1 | [Yerel etkinlik planı](../asi-ops/docs/plan.md) | Takım bilgileri ve ön hazırlık bağlamı |

- **Doğrulanmış gözlem:** Dosyada doğrudan görülen veya bütün kayıtlar üzerinde sayılan bilgi.
- **Hipotez:** Gözlemleri açıklayan, fakat gizli doğrulamayla teyit edilmemiş yorum.
- **Tasarım önerisi:** Seçimden sonra uygulanabilecek yöntem; bu aşamada çalışan çözüm değildir.
- **[DOĞRULANAMADI]:** Paket veya mevcut oturumla cevaplanamayan konu.

K3 dosyası klasörde Unicode birleşik karakterlerle adlandırılmıştır; tabloda okunabilir adı kullanılmıştır. Rapor hazırlanırken dış servise veri gönderilmedi; yerel paketin içeriği yeterliydi.

## 3. SCOUT — kuralların doğru yorumu

### 3.1 Zorunlu ve opsiyonel işleri ayıralım

| İstek | Statü | Tasarımda karşılığı | Kanıt |
|---|---|---|---|
| Alarm akışının tamamını işlemek | Zorunlu | 3.000 kimliğin tamamı izlenebilir bir karara bağlanmalı | K1, satır 31–32 |
| Anlamlı gruplar, her gruba bir olay kartı | Zorunlu | Kartlar olay düzeyinde; salt servis/alarm tipi listesi yetersiz | K1, satır 33–34 |
| Kök hipotezi, etkilenen servisler, alarm sayısı, zaman aralığı | Zorunlu | Her kartta eksiksiz alanlar ve kaynak kayıtlar | K1, satır 35–36 |
| İlk aksiyon, sahip ve durum kaydı | Zorunlu | Açıklama metninden ayrı, kayıtlı aksiyon nesnesi | K1, satır 37–38 |
| Aksiyonu açılıştan kapanışa izlemek | Opsiyonel | Basit durum geçişi ve geçmişi iyi bir demo katkısı | K1, satır 39–40 |
| En fazla 15 olay kartı | Kabul kriteri | Gürültü silerek veya ilgisiz olayları zorla birleştirerek sağlanmamalı | K1, satır 62 |
| Ekranda gerekçeli kök hipotezi | Kabul kriteri | Gerekçe temel kapsamda olmalı | K1, satır 64 |
| Doğal dil açıklaması ve karşı olasılıklar | Bonus | Birincil hipotez, alternatif ve ayırıcı kontrol | K1, satır 44–45 |
| Gürültü eleme gerekçelerinin denetimi | Bonus | Alarm bazında karar, kanıt ve gerekçe | K1, satır 46–47 |
| Benzer geçmiş olaylar | Bonus | Gerçek geçmiş arşivi yok; geçmiş vaka uydurulmamalı | K1, satır 48 |

**İki kritik nüans:**

- Aksiyonun sahibini ve durumunu tutmak zorunlu; kapanışa kadar yaşam döngüsü göstermek opsiyonel.
- Açıklama bonus sanılıp sona bırakılamaz: gerekçeli kök hipotezi kabul kriterinde de yer alıyor.

### 3.2 Gerekmeyen altyapılar

- Dosyayı toplu okumak yeterli; canlı veri toplama veya akış altyapısı gerekmiyor.
- Kullanıcı yönetimi, giriş ekranı ve yetkilendirme beklenmiyor.
- Kalıcı veritabanı zorunlu değil; bellek içi kayıt kabul ediliyor.
- Web arayüzü zorunlu değil; terminal de kabul ediliyor. **Canlı çalışan demo zorunlu.**
- Açık kaynak kütüphaneler kullanılabilir; kullanılanlar README'de belirtilmeli.
- Paket sentetik; gerçek şirket sistemine erişim gerekmiyor.

### 3.3 Teslim ve takvim

- Kesin sınır **16 Eylül 2026, 17:30**; değerlendirme bu saate kadarki son commit üzerinden.
- Repo adresi başvuruda alınmış; K1/K3'e göre ayrıca bağlantı göndermek gerekmiyor.
- Repo public olmalı; K3, private repo durumunu diskalifiye nedeni olarak belirtiyor.
- README: kurulum, AI araçları, MCP listesi, ekran görüntüleri.
- `docs/`: plan, fazlar, mimari; `.env.example` ve kullanılan AI yapılandırma dosyası.
- K3 son kontrol listesi ayrıca `AI_JURI.md` ve geçerli `submission.json` istiyor.
- Sunum **7 dakika + 3 dakika soru-cevap**; sıra anlık kura, canlı ürün öncelikli.
- K3 başlığı 14:30 başlangıcı diyor; öneri tablosu 14:45'ten başlıyor. Öneri tablosu zorunlu takvim değil.
- Analiz sırasında saat 14:33 sonrasıydı. Uygulama bütçesi çözüm seçimi anında kalan süreyle hesaplanmalı.

**Veri yayını hakkında K3 notu:** “orijinal dosyaları repoya değiştirilmemiş hâliyle koymayın; veri paketini repoya eklemenize gerek yoktur.” Bu ifade README'de dış veri konumuyla çalışmayı tarif etmeyi gerektiriyor. Yerel dosyaları koru; ham paketi otomatik public repoya ekleme. Dönüştürülmüş verinin yayımlanması veya jüri veri yolu gerekiyorsa mentöre netleştirilmeli.

**Çalışma klasörü / teslim repo ayrımı:** Kullanıcı `sonuc codex/` altında çalışılmasını istedi. Kayıtlı repo, mevcut iskelette `asi-ops` olarak görünüyor. İleride uygulama yapılırsa sonuçların kayıtlı repoya aktarımı ayrıca planlanmalı; yalnızca yerel sonuç klasöründe durması teslim sayılmaz. Bu analiz aşamasında aktarım yapılmadı.

## 4. Verinin tamamında doğrulanan durum

### 4.1 Yapısal kalite

| Kontrol | Sonuç | Anlamı |
|---|---:|---|
| CSV alarm sayısı | 3.000 | Beklenen hacim mevcut |
| JSON alarm sayısı | 3.000 | Aynı akışın ikinci biçimi |
| Düzleştirilmiş JSON–CSV eşitliği | Tam eşit, aynı sıra | İkisini birleştirip 6.000 kayıt oluşturmamalıyız |
| Benzersiz alarm kimliği | 3.000 | Kimlik çakışması yok |
| Kimlik hariç tamamen aynı kayıt | 0 | Birebir tekrar silme tek başına indirgeme sağlamaz |
| Servis / sunucu | 27 / 56 | Envanterle uyumlu |
| Bağımlılık kaydı | 32 | 25 senkron, 7 asenkron |
| Boş hücre | 0 | İncelenen CSV alanlarında |
| 1–5 dışında severity | 0 | Geçerli ölçek |
| Envanterde bulunmayan alarm host'u | 0 | Birleştirme anahtarı kullanılabilir |
| Servis/konum/ortam envanter uyuşmazlığı | 0 | Host üzerinden zenginleştirme tutarlı |
| Zaman sırası | Artan | Yine de alarm_id zaman anahtarı sayılmamalı |
| Gerçek ilk / son kayıt | 01:30:20 / 03:30:20 | 10 Eylül 2026; zaman farkı tam iki saat |
| Ortam | 3.000 kayıt `prod` | Bu pakette ayırt edici özellik değil |

### 4.2 Küçük ama işlevsel veri sözlüğü farkları

- Sözlük penceresi 01:30–03:30; **03:30:00'dan sonra sekiz kayıt** var. Katı pencere filtresiyle düşürülmemeli.
- Sözlükte 26 alarm tipi tanımlanmış; dosyada **25 tip** gözlendi. `queue_backlog` hiç görülmedi.
- Timestamp alanında saat dilimi eki yok. Veri saatini keyfî olarak UTC'ye çevirmemeliyiz.
- Sözlükte timestamp örneği Kasım tarihli; gerçek kayıtlar ve gözlem açıklaması **10 Eylül** tarihli.
- Senaryodaki 02:14 anlatımı hikâye bağlamıdır; analiz başlangıcı veya otomatik olay sınırı değildir.

### 4.3 Dağılımlar

| Şiddet | Alarm sayısı | Pay |
|---|---:|---:|
| 1 — bilgi | 614 | %20,47 |
| 2 — uyarı | 709 | %23,63 |
| 3 — küçük | 800 | %26,67 |
| 4 — büyük | 629 | %20,97 |
| 5 — kritik | 248 | %8,27 |

- Şiddet 1–2 toplam **1.323 kayıt, %44,10**. Bunların hepsini gürültü saymak yanlış bir başlangıç olur.
- Veri merkezleri: dc1 **1.539**, dc2 **1.461** kayıt.
- Kaynaklar: OBM **604**, Prometheus **559**, Zabbix **607**, AppDynamics **585**, SyslogNG **645**.
- En yoğun beş dakikalık aralık: **01:45:00–01:49:59, 352 alarm**.
- `latency_high`: **402**, `timeout`: **271**, `mem_high`: **240**, `cpu_high`: **230** kayıt.
- `latency_high` ve `network_flap`, **27 servisin tamamında** görülüyor. Tek tip eşitliği olay eşitliği değil.
- Kaynak çeşitliliği destekleyici kanıt olabilir; beş izleme sistemi beş bağımsız arıza anlamına gelmez.

## 5. Problem yapısı: birden fazla ilişki türü gerekiyor

### 5.1 Bağımlılık yönü kritik

V4'te `kaynak_servis → hedef_servis`, **kaynağın hedefe bağımlı olduğunu** ifade ediyor.

Örnek:

```text
Bağımlılık: payment-service → payment-provider-gw
Olası arıza etkisi: payment-provider-gw ⇒ payment-service ⇒ order-service ⇒ mobile-bff
```

Ok yönü ters okunursa son kullanıcıya yakın ve çok alarm üreten servis yanlışlıkla kök seçilebilir. Yukarıdaki etki yolu **olasılıktır**; her serviste gözlenen alarm ve zaman uyumuyla doğrulanmalıdır.

### 5.2 Grafikte bağlı olmak yeterli değil

- Yönler yok sayıldığında **26 servis tek bağlantılı bileşende**, yalnızca `ntp-service` ayrı kalıyor.
- Tüm bağlantılı servisleri tek olay saymak, bağımsız arızaları birleştirir.
- Tek hedefe ulaşan servislerin tüm alarmlarını köke bağlamak da aynı hatayı üretir.
- Envanterdeki iş kritikliği müdahale önceliğine yardım eder; nedensellik kanıtı değildir.
- Bağımlılık dosyasında host düzeyinde çağrı eşleşmesi yok. Hangi host'un hangi host'a bağlandığı uydurulmamalı.

### 5.3 Fiziksel ilişki ayrı bir kanıt katmanı

- Ağ belirtileri aynı **veri merkezi + kabin** içinde, farklı servislerde görülebiliyor.
- `rack-A` tek başına anahtar olamaz; dc1/rack-A ile dc2/rack-A farklı alanlardır.
- Ortak kabin varsayımı her olay için kullanılmamalı: disk, oturum ve dış ödeme belirtileri birden fazla konuma yayılıyor.
- Envanterde switch/router cihazı bulunmuyor. Hipotez “dc1/rack-A ortak ağ sorunu” olabilir; cihaz adı uydurulmamalı.

### 5.4 Kaynak tüketimi, arıza yayılımından farklı

- Bir hedef bozulduğunda bağımlı servislerin etkilenmesi tek mekanizma değil.
- Çakışan batch işleri, bağlı oldukları veritabanında kaynak baskısı yaratabilir.
- Bu durumda batch → veritabanı yönündeki **yük oluşturma** hipotezi ile veritabanı ⇒ istemci **etki yayılımı** ayrılmalı.
- Tek yönlü grafikte ters erişilebilirlik bütün senaryoyu açıklamaya yetmez.

### 5.5 Alarm metni değerli, fakat tek başına otorite değil

271 `timeout` kaydının mesajında geçen hedef servis incelendi:

| Mesaj hedefinin mevcut grafiğe ilişkisi | Kayıt |
|---|---:|
| Doğrudan bağımlılık | 172 |
| Dolaylı bağımlılık yolu | 54 |
| Yönlü bağımlılık yolu bulunamıyor | 42 |
| Kaydın kendi servisini hedef gösteriyor | 3 |

- Örnek: `ALM-00071`, auth-service üzerinde charging-service timeout'u bildiriyor; V4'te bu yönde yol yok.
- Bu kayıtlar otomatik silinmemeli. Ortak altyapı, eksik topoloji veya sentetik metin tutarsızlığı alternatifleri korunmalı.
- Doğrudan/dolaylı doğrulanan metin ilişkisi güçlü destek; diğer metin ilişkileri daha zayıf kanıt olarak işaretlenmeli.
- `HTTP 504`, `503 ms`, `%35` ve `26 gün` farklı büyüklüklerdir; genel sayı ayrıştırması bunları karıştırmamalı.

## 6. Olay adayları — gözlemler ve sınanacak hipotezler

**Bu bölüm nihai gruplama veya gizli etiket rekonstrüksiyonu değildir.** Aşağıdaki sayılar belirtilen alarm tiplerinin sayılarıdır; kartlara atanmış toplam alarm sayıları değildir. Liste olası örüntüleri anlamak içindir; gerçek olay sayısını belirlemez.

### H1 — dc1 / rack-A ortak ağ problemi

**Gözlem:**

- `network_down`: **12 kayıt**, 01:42:13–01:45:04.
- `pkt_loss`: **22 kayıt**, 01:42:24–01:45:03.
- Bu **34 kaydın tamamı dc1/rack-A**, toplam **dokuz farklı host** üzerinde.
- 01:42–01:46 aralığında `network_flap` de dahil edilince 60 kayıt var; 58'i dc1/rack-A, ikisi dc1/rack-C.
- Ardından 01:45:13–01:54:11 arasında **79 thread_pool** alarmı, on serviste görülüyor.

**Hipotez:** Ortak fiziksel ağ alanındaki bozulma, servis belirtilerine ve istek birikmesine yol açmış olabilir.

**Alternatif:** Aynı yerde bağımsız host arızaları; uygulama doygunluğu; izleme kaynağının ortak hatası.

**Ayırıcı kanıt:** Birçok serviste aynı konumda ağ sinyallerinin erken görünmesi. Bunun bütün sonraki 79 alarmın aynı olaya ait olduğunu kanıtlamadığı özellikle korunmalı.

**Örnek kanıt:** `ALM-00006`, CSV satır 188; `ALM-00290`, satır 322.

**İlk aksiyon önerisi:** Ağ nöbetçisinin dc1/rack-A bağlantı/port durumunu doğrulaması; etkilenen host listesini kanıttan alması.

### H2 — billing-db depolama / tablespace problemi

**Gözlem:**

- 02:05:06–02:09:59 arasında billing-db üzerinde **17 disk_full** kaydı; üç host, birden fazla konum.
- İlk disk alarmından 28 saniye sonra aynı host'ta tablespace genişletilememe mesajı var.
- Toplam **34 db_write_fail**: billing-db 7, billing-service 20, invoice-batch 7.
- billing-service ve invoice-batch, V4'te billing-db'ye doğrudan bağımlı.
- payment-service üzerinde 02:05–02:35 aralığındaki **13 timeout'un tamamı billing-service** hedefini belirtiyor.

**Hipotez:** billing-db kapasite sorunu, yazma hataları ve bağımlı işlem zincirinde başarısızlık doğuruyor olabilir.

**Alternatif:** Bağımsız bağlantı havuzu problemi; uygulama tarafında işlem/yazma kilidi.

**Ayırıcı kanıt:** Disk doluluk ve tablespace mesajı, salt timeout'a göre köke daha yakın işaretler.

**Örnek kanıt:** `ALM-00467`, satır 984; `ALM-00468`, satır 995.

**İlk aksiyon önerisi:** DBA nöbetçisinin disk/tablespace kapasitesini ve yazma hatalarını doğrulaması; otomatik veri silme önerilmemeli.

### H3 — session-service üzerinde zamana yayılan bellek baskısı

**Gözlem:**

- Üç session-service host'unda yaklaşık 01:35'te %60 bellek mesajları başlıyor.
- Bu seride %62, %64, %66, %68, %70, %72 ve yaklaşık 02:07'de %74 değerleri görülüyor.
- 02:11:26–02:34:06 aralığında **18 gc_pressure** kaydı var.
- 02:38:47–02:52:02 aralığında **12 oom_risk** kaydı var.
- Araya düşük ve tutarsız bellek değerleri de giriyor; bütün mem_high kayıtları tek temiz trend değil.

**Hipotez:** Uzun sürede gelişen bellek baskısı, GC ve OOM riskine dönüşüyor olabilir. “Kesin memory leak” demek için veri yetersiz.

**Alternatif:** Artan trafik, kapasite yetersizliği, ortak uygulama davranışı; aynı serviste ilgisiz arka plan uyarıları.

**Ayırıcı kanıt:** Aynı servis/host ailesinde birden fazla evre ve zamansal süreklilik. Beş dakikalık katı pencereler tek örüntüyü parçalayabilir.

**Örnek kanıt:** `ALM-00737`, satır 78; `ALM-00744`, satır 1018; `ALM-00727`, satır 1149; `ALM-00769`, satır 1805.

**İlk aksiyon önerisi:** Uygulama/JVM nöbetçisinin heap ve GC trendini incelemesi; restart gerekçesi ve etkisi ayrıca doğrulanmalı.

### H4 — dış ödeme sağlayıcısına erişim / yavaşlık

**Gözlem:**

- payment-provider-gw üzerinde **11 ext_unreach + 13 ext_slow**, 02:40:28–02:43:45 aralığında.
- Üç gateway host'unda ve farklı konumlarda görülüyor.
- payment-service → payment-provider-gw doğrudan bağımlılığı var.
- payment-service üzerinde 02:40–03:05 aralığındaki **34 timeout'un tamamı payment-provider-gw** hedefini belirtiyor.
- payment-service, order-service ve mobile-bff üzerinde ilgili zamanlarda işlem/hata belirtileri var.

**Hipotez:** Dış ödeme erişim problemi, ödeme ve sipariş zincirini etkiliyor olabilir.

**Alternatif:** Kurumun dış ağ çıkışı, gateway konfigürasyonu veya bağlantı kapasitesi; sağlayıcının kendisi kesin suçlanamaz.

**Örnek kanıt:** `ALM-00858`, satır 1837; `ALM-00909`, satır 1896.

**İlk aksiyon önerisi:** Ödeme entegrasyon nöbetçisinin erişilebilirlik ve hata kodlarını doğrulaması; sağlayıcı/çıkış ağı ayrımını kontrol etmesi.

### H5 — batch çakışması ve ortak veritabanı baskısı

**Gözlem:**

- batch-scheduler üzerinde **4 batch_overlap**, 03:05:28–03:06:50.
- reconciliation-batch ve report-batch üzerinde **12 batch_slow**, 03:08:58–03:24:23.
- Her iki batch servisi scheduler'a ve subscriber-db'ye bağımlı.
- subscriber-db üzerinde **19 db_conn_pool**, 03:09:19–03:27:14.
- subscriber-service üzerinde **17 db_conn_pool**, 03:09:20–03:28:40.
- report-batch'te ilk havuz belirtisi 03:07:18; subscriber-db alarmından önce.

**Hipotez:** Çakışan işler ortak veritabanı kaynaklarını tüketiyor, çevrim içi abone işlemlerini etkiliyor olabilir.

**Alternatif:** Veritabanındaki bağımsız kapasite sorunu batch işlerini yavaşlatıyor; scheduler alarmı eşzamanlı ama ayrı olabilir.

**Ayırıcı kanıt:** Batch çakışmasının erken görünmesi, iki işin aynı kaynağa bağımlılığı ve ardından kaynak belirtileri. Alarm üretim gecikmesi nedeniyle zaman sırası kesin nedensellik sağlamaz.

**Örnek kanıt:** `ALM-01107`, satır 2524; `ALM-01128`, satır 2552; `ALM-01145`, satır 2584.

**İlk aksiyon önerisi:** Batch nöbetçisi ve DBA'nın çakışan işlerle ortak havuz/CPU kullanımını birlikte doğrulaması.

## 7. En güçlü ayrıştırma örneği: aynı serviste eşzamanlı iki neden

mobile-bff üzerinde 02:35–03:05 aralığında **38 timeout** var:

| Mesaj hedefi | Sayı | Gözlenen aralık | Grafikteki destek |
|---|---:|---|---|
| session-service | 12 | 02:36:01–02:54:59 | Doğrudan bağımlılık |
| payment-provider-gw | 26 | 02:41:13–02:59:22 | mobile-bff → order-service → payment-service → payment-provider-gw |

**Çıkarım:** Aynı servis + yakın zaman + aynı alarm tipi, aynı olayı belirlemek için yeterli değil. Metin hedefi, bağımlılık yolu ve kök belirtileri birlikte değerlendirildiğinde iki ayrı açıklama mümkün oluyor.

Bu, önerilen çözümün en güçlü demo adayıdır: nöbetçiye aynı mobile-bff alarm selinin neden iki farklı müdahale gerektirebileceğini göstermek. Henüz bu 38 alarm için nihai atama yapılmadı; tablo betimsel incelemedir.

## 8. Gürültü, tekrar ve belirsizlik birbirinden ayrılmalı

### 8.1 Basit filtrelerin somut tehlikesi

- `severity <= 2` filtresi, session-service bellek örüntüsünün erken uyarılarını kaybettirebilir.
- `mem_high`, `network_flap`, `latency_high` tiplerini topluca elemek hem olay hem arka plan sinyallerini birlikte siler.
- `severity >= 4` filtresi, önemli görünen arka plan uyarılarını gereksiz olaylara çevirebilir.
- Örnek: `ALM-01499`, şiddet 4 fakat sertifika için **26 gün** kaldığını söylüyor; mevcut kesintinin kökü olduğu gösterilmemiş.
- Toplam **13 cert_expiry** alarmı şiddet 4. Bunların etiketleri görülmeden “kesin gürültü” denemez.
- `ALM-02267`, şiddet 4 ama %35 bellek mesajı taşıyor. Severity ile mesajdaki büyüklük ayrı kanıtlar.

### 8.2 Önerilen karar ayrımı

| Karar | Anlamı | Kayıt tutulmalı mı? |
|---|---|---|
| Olaya bağlı alarm | Birincil olay hipotezine yeterli destek var | Evet; olay, rol, kanıt, alarm kimliği |
| Gürültü adayı | Mevcut olay için aksiyon desteği zayıf | Evet; eleme gerekçesi ve gözlem |
| Belirsiz alarm | Birden fazla aday veya yetersiz kanıt var | Evet; alternatifler ve neden karar verilemediği |
| Aynı belirtiyi tekrarlayan alarm | Ayrı kök değil, olay içi tekrar olabilir | Evet; toplam alarm sayısında korunmalı |

- Belirsiz alarmlar sessizce gürültüye çevrilmemeli.
- Denetim görünümünde ham alarm geri bulunabilmeli; yanlış eleme incelenebilmeli.
- Gürültü ve belirsiz kayıtların olay kartı limitine nasıl dahil edileceği organizatöre sorulabilir.
- Bu belirsizlik çözülene kadar raporda tüm kategori sayıları ayrı, görünür ve toplanabilir tutulmalı.

## 9. Başarıyı nasıl ölçeceğiz?

### 9.1 Şimdi bilinenler ve henüz bilinmeyenler

- Giriş sayısı, alanlar, bağımlılıklar ve gözlenen örüntüler doğrulandı.
- Nihai kart sayısı, alarm atamaları, gürültü sayısı ve kök isabeti **henüz üretilmedi/ölçülmedi**.
- Gerçek olay üyelikleri ve kökler jüriye açılacak. Şu anda F1, doğruluk veya kök isabet yüzdesi verilemez.
- Kendi seçtiğimiz beş hipotezi doğru etiket kabul edip başarı ölçmek döngüsel değerlendirme olur.

### 9.2 Geliştirme sonrası ölçülmesi önerilenler

| Kontrol | Tanım | Başarı koşulu / yorum |
|---|---|---|
| İşleme kapsamı | Okunan benzersiz alarm / 3.000 | %100 |
| Hesap verebilirlik | Olaya bağlı + gürültü adayı + belirsiz benzersiz alarm | Tam 3.000; kayıp kayıt yok |
| Kart oranı | Olay kartı sayısı / 3.000 | 15 kartta %0,5; küçük olması tek başına yeterli değil |
| Karar ekranı indirgemesi | 1 − kart sayısı / 3.000 | 15 kartta %99,5; doğruluk veya gürültü oranı değildir |
| Kart alan tamlığı | Zorunlu alanları dolu kartların oranı | %100 |
| Kanıt izlenebilirliği | Hipotez/aksiyon gerekçesinden ham alarmı açabilme | Her kartta |
| Yanlış birleştirme riski | Bağımsız kök işaretlerinin gerekçesiz aynı karta girmesi | İncelenecek; gerçek oran etiket bekler |
| Gürültü eleme kalitesi | Elenenlerin gerçekten gürültü olması | Yerelde kesin ölçülemez; jüri etiketi gerekir |
| Yeniden üretilebilirlik | Aynı dosya ve ayarda aynı temel atamalar | Özellikle demo için gerekli |
| Çalışma süresi | Dosya okumadan kartlara kadar süre | Ölçülüp raporlanmalı; henüz hedef performans iddiası yok |

Her alarmın sayımlarda **tek birincil kararı** olması önerilir. İkincil hipotezler referans olarak tutulabilir; alarmı iki kez saymamalı. Gürültü/belirsiz görünümü 15 kart şartını görünmez biçimde aşmak için kullanılmamalı.

### 9.3 Etiketsiz durumda yararlı tutarlılık kontrolleri

- Aynı dosyayı yeniden okuyunca kapsam ve temel kararlar değişiyor mu?
- Satır sırasını değiştirmek sonucu etkiliyor mu? Zaman üzerinden işlem yapılmalı.
- CSV ve JSON aynı sonucu veriyor mu?
- Kök iddiasına aykırı zaman, konum veya metin kanıtı görünür mü?
- Kısa pencere yavaş gelişen bellek örüntüsünü parçalıyor mu?
- Büyük pencere eşzamanlı oturum/ödeme olaylarını birleştiriyor mu?
- Bilinmeyen alarm tipi veya eksik alan gelince kayıt kayboluyor mu?
- Bu kontroller dayanıklılık ölçer; gerçek kök doğruluğunun yerine geçmez.

## 10. Çözümün açıklaması ne içermeli?

Kart, yalnızca bir özet cümlesi değil aşağıdaki sorulara cevap vermeli:

1. **Ne oldu?** Gözlenen belirti ailesi ve kapsam.
2. **Nereden başlamalıyız?** Kök kaynak/mekanizma hipotezi; host, servis, konum veya dış bağımlılık olabilir.
3. **Neden bu hipotez?** Alarm kimlikleri, zaman sırası, bağımlılık yolu, konum ve belirti uyumu.
4. **Neden diğer hipotez değil?** En güçlü alternatif ve zayıflatan/eksik kanıt.
5. **Hangi servisler gerçekten belirti verdi?** Gözlenen etki listesi.
6. **Başka kimler etkilenebilir?** Grafikten çıkarılan potansiyel etki; gözlenenlerden ayrı.
7. **İlk ne yapılmalı?** Doğrulama veya müdahale önerisi; amaç ve dayanak.
8. **Kimde, hangi durumda?** Aksiyon sahibi/rolü, durum ve varsa güncelleme zamanı.

**Örnek açıklama biçimi — öneri, üretilmiş olay kartı değildir:**

> billing-db depolama sorunu öne çıkıyor: ALM-00467 %100 disk doluluğu bildiriyor; 28 saniye sonra aynı host'ta ALM-00468 tablespace genişletilememe hatası var. Bağımlı servislerde yazma/havuz belirtileri görülüyor. Bağımsız havuz sorunu alternatif; önce disk ve tablespace kapasitesi doğrulanmalı.

- Güven derecesi, açıklanabilir kanıt yeterliliği şeklinde sunulabilir: yüksek/orta/düşük.
- Kalibrasyon yokken “%97 doğru” gibi olasılıklar verilmemeli.
- Bir alarmın son görülme zamanı, arızanın çözüldüğü anlamına gelmez; clear/recovery alanı bulunmuyor.
- Aksiyonun kapatılması da altta yatan olayın otomatik doğrulanmış çözümü sayılmamalı.
- Envanterde ekip/sahip alanı yok. “DBA nöbetçisi” gibi rol önerisi verilebilir; gerçek kişi ataması kullanıcıdan gelmeli.

## 11. STRATON — çözüm seçenekleri ve öneri

### Problem tanımı

- Hedef kullanıcı: aynı anda birden fazla olayı yöneten nöbetçi operasyon mühendisi.
- İhtiyaç: kısa olay kuyruğu, gerekçeli kök hipotezi ve sorumluluğu kayıtlı ilk aksiyon.
- Temel güçlük: zaman, servis, belirti ve konum ilişkileri tek başına yeterli değil.
- Kısıtlar: bütün veri, en fazla 15 kart, canlı demo, 17:30 teslim.
- Başarı: bağımsız olayları koruyarak açıklanabilir ve izlenebilir kararlar üretmek.

### A — Kanıta dayalı olay korelasyonu ve aksiyon kuyruğu

- **Çekirdek:** Açık kurallar, çoklu zaman ölçeği, bağımlılık ve konum kanıtlarını birlikte değerlendirir.
- **Akış:** Dosya → aday belirtiler → hipotez karşılaştırma → olay kartı → sahip/durumlu aksiyon.
- **Kapsam:** Kartlar, alarm ayrıntısı, kanıt/alternatifler, gürültü denetimi ve aksiyon kaydı.
- **Yavaş olaylar:** Bellek→GC→OOM gibi evreleri, ani patlamalardan farklı süreklilikle değerlendirir.
- **Birleştirme sınırı:** Ortak servis veya tek ara alarm, bağımsız kökleri birleştirmeye yetmez.
- **AI rolü:** Geliştirme/analizde AI; çalışırken kanıtlı açıklama için LLM isteğe bağlı.
- **Açıklama akışı:** Hesaplanan kanıt → şablon/opsiyonel LLM → kısa gerekçe → mühendis kararı.
- **Veri:** Üç içerik kaynağı; alarmlar, envanter ve bağımlılıklar.
- **Teknoloji yönü:** Yerel dosya işleme, basit tek uygulama, bellek içi aksiyon kaydı.
- **Dış servis:** Zorunlu değil; çevrim dışı çalışabilen çekirdek önerilir.
- **Risk:** Aşırı özel kurallar veya tek zaman penceresi, görülmeyen örüntüleri kaçırabilir.
- **Önlem:** Alarm kimliği/saat/olay sayısına sabitleme yapmamak; belirsizliği göstermek.
- **Demo:** Aynı mobile-bff üzerindeki oturum ve ödeme belirtilerini gerekçeli ayırmak.
- **Kapsam dışı:** Canlı entegrasyon, otomatik müdahale, gerçek geçmiş arşivi, model eğitimi.

### B — LLM destekli hipotez hakemliği

- **Çekirdek:** A'nın veri ve kanıt katmanı, yapılandırılmış LLM hipotez karşılaştırmasıyla genişler.
- **Akış:** Aday gruplar → kanıt özetleri → LLM karşılaştırması → doğrulama → kart/aksiyon.
- **AI rolü:** Belirsiz kökleri karşılaştırır; alternatif açıklama ve ayırıcı kontrol önerir.
- **AI girdisi:** Sınırlı kanıt özeti, geçerli alarm kimlikleri, bağımlılıklar ve aday hipotezler.
- **AI çıktısı:** Yapılandırılmış hipotez, kanıt referansları, alternatif ve ilk kontrol önerisi.
- **Kullanıcı değeri:** Karmaşık açıklamaları daha okunabilir hâle getirmek; belirsizliğin görünürlüğünü artırmak.
- **Ek kapsam:** Servis erişimi, çıktı doğrulama, zaman aşımı, önbellek ve deterministik yedek yol.
- **Risk:** Uydurma ilişki, tutarsız kartlar, gecikme, kota ve entegrasyon maliyeti.
- **Sınır:** LLM tüm 3.000 alarmı tek istemle gruplamamalı; çekirdek kararların hesabı korunmalı.
- **Demo:** Aynı kanıta iki hipotez, karşı kanıt ve seçilen ilk doğrulama aksiyonu.
- **Kapsam dışı:** Serbest otonom ajan, müdahale komutu çalıştırma, doğrulanmamış otomatik kapanış.

### Konsey karşılaştırması

Puanlar 1–5 ölçeğinde stratejik değerlendirmedir; resmi jüri ağırlığı veya ölçülmüş başarı değildir. Teknik riskte yüksek puan düşük risktir.

| Kriter | A | B |
|---|---:|---:|
| Problem çözme gücü | 5 | 4 |
| Kullanıcı değeri | 5 | 5 |
| AI katkısı | 3 | 5 |
| Yenilikçilik | 3 | 4 |
| Kalan sürede yapılabilirlik | 5 | 3 |
| Teknik risk | 4 | 2 |
| Demo etkisi | 4 | 5 |
| Farklılaşma | 4 | 4 |
| Ölçeklenebilirlik | 3 | 3 |
| Jüri etkisi | 5 | 4 |
| **Toplam** | **41** | **39** |

### Öneri: A

1. Zorunlu gereksinimleri ve değerlendirme ölçütlerini doğrudan karşılayacak en sade kapsamı sunuyor.
2. Paket, açıklanabilir korelasyon için yeterli yapılandırılmış kanıt içeriyor.
3. Dış servis riskini azaltarak doğrulama, aksiyon kaydı ve canlı demoya zaman bırakıyor.

**Seçim bekleniyor.** Önceki Data Dynamo provasında seçilen A, bu senaryonun otomatik onayı değildir.

## 12. Yöntem seçiminde kaçınılması gereken kısa yollar

| Kısa yol | Bu pakette neden tehlikeli? | Daha savunulabilir yaklaşım |
|---|---|---|
| Sadece beş dakikalık zaman dilimleri | Uzun bellek örüntüsünü böler; eşzamanlı olayları karıştırır | Kaynağa ve belirti evrelerine bağlı zaman sürekliliği |
| Servis başına tek olay | mobile-bff iki farklı kökten etkilenebilir | Aynı serviste farklı kök adaylarını koru |
| Grafikte bağlantılı olanları birleştir | 26 servis tek bileşende | Her ilişkiyi zaman ve belirti kanıtıyla destekle |
| Sadece aynı alarm tipi | latency_high/network_flap tüm servislerde | Tip + kaynak + zaman + ilişki birlikte |
| En erken / en yüksek severity köktür | Erken sertifika uyarısı, düşük şiddetli bellek öncülleri var | Kök yakınlığı ve kanıt kapsamı birlikte |
| Çok alarm üreten servisi kök seç | Uç servis yalnızca birçok etkinin buluşma noktası olabilir | Kaynak ve etki ayrımı |
| Bütün düşük şiddetlileri sil | %44,1 kayıt ve önemli öncüller kaybolabilir | Bağlama dayalı, kayıtlı eleme |
| Mesaj benzerliğiyle tek başına kümele | Ortak mesaj şablonları farklı olaylarda tekrar ediyor | Metin yardımcı kanıt; yapılandırılmış alanlarla doğrula |
| Bütün grafiği LLM'e ver, cevabı kabul et | Atıf uydurma, tutarsızlık ve kontrolsüz gecikme | Sınırlı kanıt, doğrulanabilir referans ve yedek yol |
| Zorla beş veya on beş grup üret | Gerçek olay sayısı saklı; limit doğruluk ölçüsü değil | Örüntüden aday sayısı çıkar, bağımsız kökleri koru |
| Alarm_id aralıklarından olay türet | Sentetik üretim sırasına aşırı uyum riski | Kimliği yalnızca izlenebilirlik anahtarı kullan |

## 13. Açıklığa kavuşturulması gereken sorular

### Mentöre sorulabilecek, kapsamı etkileyen sorular

1. Gürültü ve belirsiz alarm denetim listeleri 15 olay kartı sınırına dahil mi?
2. Kapalı değerlendirme için alarm→olay eşlemesi beklenen bir dosya/JSON şeması var mı?
3. Bir alarm birden fazla olayla ilişkiliyse birincil üyelik mi, çoklu üyelik mi bekleniyor?
4. “Kök neden” değerlendirmesi servis, host, fiziksel alan veya arıza mekanizması düzeylerinden hangilerini kabul ediyor?
5. Jüri uygulamaya veri paketini hangi yerel dosya yolu/biçimiyle verecek?
6. K3'teki ham veri paylaşım cümlesinin dönüştürülmüş veri ve ekran görüntüsü için kapsamı nedir?

Bu soruların cevapları olmadan da problem analizi tamamlanabilir. Uygulamada açık varsayım tutulmalı; gizli doğrulama verisi veya gerçek olay sayısı talep edilmemeli.

### Takım / teknoloji durumu

| Başlık | Durum | Karara etkisi |
|---|---|---|
| Takım adı / kaptan | Yerel planda ASI-OPS / Hüseyin Eren Güçyener | Teslim belgelerinde mevcut bilgi kullanılabilir |
| Diğer üyeler / yetkinlikler | [DOĞRULANAMADI] | Arayüz ve entegrasyon kapsamı buna göre küçültülebilir |
| SAKA/LLM API erişimi, kota, model | [DOĞRULANAMADI], çağrı yapılmadı | B için kritik; A çekirdeği için zorunlu değil |
| Zorunlu çalışma zamanı AI kullanımı | K1/K3'te açık bir zorunluluk görülmedi | AI geliştirme iş bölümü dürüstçe belgelenmeli |
| Runtime ve UI bağımlılıkları | Bu analizde kurulum/çalıştırma testi yapılmadı | Teknoloji seçimi uygulama aşamasında doğrulanmalı |
| Tarihsel olay arşivi | Pakette yok | Geçmiş olay bonusuna gerçek kanıt olmadan girilmemeli |
| Jüri metrik formülleri / ağırlıkları | [DOĞRULANAMADI] | Tahminî ağırlıklar resmi puanlama diye sunulmamalı |
| Gizli doğrulama etiketleri | Katılımcı paketinde yok; jüriye açılacak | Yerelde gerçek isabet yüzdesi iddia edilmemeli |

## 14. Kapsamı koruyan seçim ilkeleri

- İlk hedef: tam veri kapsamı, mantıklı kartlar, gerekçeli hipotezler, kayıtlı sahip/durumlu aksiyon.
- İlk bonus: denetlenebilir gürültü elemesi ve güçlü alternatif hipotez açıklaması.
- Zaman kalırsa: aksiyon durum değişikliği ve kısa geçmişi.
- Gerçek geçmiş veri yokken geçmiş olay eşleştirmesi bonusu kapsam dışı tutulmalı.
- Öncelik sırası tahmini gelir kaybı veya uydurma SLA ile değil, gözlenen etki ve verilen iş kritikliğiyle açıklanmalı.
- Asenkron bağımlılık gecikmeli etki yaratabilir; senkronla aynı zaman şartına zorlanmamalı.
- Ortak bağımlılığı olan iki kök, tek paylaşılan belirti yüzünden birleştirilmemeli.
- Kullanıcıya riskin en çok nerede olduğunu göster: yavaş bellek örüntüsü, ağın geniş yayılımı, batch kaynak baskısı.
- Gerçek olay sayısı, gürültü miktarı, nihai kart sayısı ve isabet **uygulama/etiket olmadan bilinmiyor**.

## 15. Veri incelemesinin izi

Tam CSV üzerinde yapılan kontroller: kayıt sayımı, kimlik tekilliği, boş alanlar, şiddet alanı, JSON eşitliği, envanter birleştirmeleri, zaman sırası, tip/kaynak/servis/konum sayımları, bağımlılık erişilebilirliği ve mesaj hedeflerinin karşılaştırılması. Hipotezler için ilgili kayıtlar zaman ve servis/alarm tipi kırılımlarında okundu.

Kaynak dosya SHA-256 özetleri:

| Dosya | SHA-256 |
|---|---|
| alarms.csv | `a7f35c74cd9dd15f8ec44bf7e0f706815a2eefcb8d44b05797c600358f72f743` |
| alarms.json | `85a2daac0fd14e2fb267cf6f787e11c068a27fcfeb749ff2ef43201fd5dc2960` |
| host_inventory.csv | `af0f4a50ee4adbeb860daf47048e251c73cd9c3bf9ab957909c6e242cce692b2` |
| service_dependencies.csv | `b9baaa56fe4ebf8421538aead630713b7041fdc2b557aaba24543b6e70a47303` |

CSV satır numaraları başlık satırı dahil verilmiştir. Alarm kimlikleri kanıtı bulmak içindir; gruplama etiketi olarak kullanılmadı. Yukarıdaki beş aday için olay üyeliği hesaplanmadı ve nihai kart üretilmedi.

## 16. Durma noktası

**Detaylı problem/veri analizi tamamlandı. Öneri A; çözüm seçimi kullanıcıya ait.**

Bu aşamada yalnızca bu Markdown raporu yazıldı. FORGE uygulamasına, model eğitimine, arayüz geliştirmeye, kaynak dosyaları değiştirmeye veya GitHub teslimine geçilmedi. Sonraki adım, kullanıcının kapsam seçimi ve devam yönlendirmesidir.
