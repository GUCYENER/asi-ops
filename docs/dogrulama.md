# Doğrulama — 16 Eylül 2026

## Ortam ve sonuç

Python 3.9.6, Node 24.19.0, yerel Google Chrome headless. Ürünün çalışması yalnız Python gerektirir; Node/Chrome tarayıcı doğrulamasında kullanıldı.

```text
python3 -m unittest discover -s tests -v
Ran 30 tests in 0.960s
OK
```

## Kapsanan riskler

| Risk | Test |
|---|---|
| Kayıp/çift kayıt ve gözlem sonu | 3.000 benzersiz karar; son kayıt 03:30:20 |
| Tarih, isim veya ID'ye ezber | +400 gün, değişen alarm ID'leri, bütün servislerin yeniden adlandırılması |
| Girdi sırasına bağımlılık | Karıştırılmış dosyada aynı kararlar |
| Alternatif veri biçimi | JSON/CSV aynı kararlar |
| İç içe olaylar | Mobile timeout 12/26 ayrımı |
| Zincirin parçalanması | 24 kaynak + 79 timeout tek dış servis kartında |
| Geç kritik kuyruk | 7 severity=5 kaydın aynı ödeme kartında korunması |
| Hatalı grafik yönü | Yönlü yol, döngü ve doğrulanmamış DNS hedefleri |
| Aynı kabin adı | Farklı veri merkezlerinde ayrı olaylar |
| Yavaş bellek / rastgele ölçüm | Düşük severity trendi, uç sıçrama, üç host'ta 24 öncül |
| Sayıyı 15'e zorlamak | 16 bağımsız olay saklanır, kabul sınırı başarısız |
| İzole güçlü / bilinmeyen tip | Belirsiz kalır, gürültüye atılmaz |
| Bozuk veri | Yinelenen ID, yanlış zaman/şiddet/host/etiket reddedilir |
| uncertain[] ve inceleme kartı | Alt küme eşitliği, çift sayım yok, 5+3 kart |
| Sahip çıkarımı | Aynı kritiklikte farklı kök aileleri farklı rol üretir |
| Jüri kartı sayıları | 401 alarm, 9 doğrudan / 26 toplam host, 14 servis; kanıt ID'leri gerçek |
| Aksiyon | Açık → incelemede → çözüldü → yeniden açık; not zorunluluğu; sürüm çakışması |
| API | Rapor, filtre, dışa aktarım, statik dosyalar, geçersiz istekler |
| Yerel erişim | Yabancı Host/Origin reddi, `.env` ve kaynak dosyaların HTTP'den kapalı olması |
| Opsiyonel model | Kapalıyken istek yok; timeout fallback; sahte kanıt ID reddi; geçerli yanıt cache |

Gerçek veri regresyonları etiket doğruluğu testi değildir. Beklenen gözlenebilir ilişkilerin korunmasını denetler. Sentetik testler olay sayısı ve isimlerden bağımsız davranışı kontrol eder.

## Gerçek tarayıcı kontrolü

`tests/browser-check.mjs` ayrı 8001 test sunucusunda çalıştırıldı; ana 8000 demosunun aksiyonları değiştirilmedi. Sonuç: başarılı, JavaScript/CSP hata listesi boş.

- Masaüstü 1440×1100: 5 olay + 3 inceleme kartı; 9 doğrudan host; ayrıntı başlangıçta kapalı.
- Mobil 390×844: yatay taşma yok.
- Gürültü sayfalama, servis arama ve alarm gerekçe açma.
- Yöntem/ölçüm ekranı.
- İnceleme kartının 44 belirsiz kaydına filtreli geçiş; sınıflar korunuyor.
- Sorumlu ve notla incelemeye alma, çözüm kaydı, geçmiş görüntüleme.
- Model kapalıyken kanıtlı şablon özeti.
- Dört ekran görüntüsü `demo/` altında; masaüstü ve mobil görüntüleri ayrıca görsel olarak incelendi.

Tekrar çalıştırma (isteğe bağlı): ayrı bir terminalde `python3 app.py --port 8001`; ayrı geçici Chrome profiliyle `--headless=new --remote-debugging-port=9222` açın; sonra `node tests/browser-check.mjs`. Test sunucusunun aksiyonları değişir. Testi yeniden çalıştırmadan önce 8001 sunucusunu yeniden başlatın.

## Yapılmamış kontroller

- Canlı Azure anahtarı/endpoint doğrulaması yapılmadı; kullanıcı dolduracak.
- Üretim yük testi, gerçek zamanlı akış ve gerçek arıza giderme yok.
- Gizli jüri etiketleriyle doğruluk/recall testi yapılamadı.
- Gerçek ekip sesli provası, sahne ekran paylaşımı ve GitHub uzaktaki son commit doğrulaması yapılmadı.
