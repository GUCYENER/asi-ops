# Canlı demo — 7 dakika sunum + 3 dakika soru-cevap

Resmi format: 7 dakika anlatım, ayrı 3 dakika soru-cevap, sıra kura ile. Sunumun omurgası çalışan yerel arayüz. Ek slayt gerekmiyor. Konuşmacı görev dağılımını ekip belirleyecek; isim varsayılmadı.

## 1. Yedi dakikalık akış

| Süre | Ekran / aksiyon | Söylenecek ana nokta |
|---|---|---|
| 00:00–00:30 | Operasyon masası; sayaçlar | “3.000 alarmın tamamını işledik. 5 olay ve 3 düşük kanıtlı inceleme kartı var. Her kaydın kararı izlenebilir.” |
| 00:30–01:30 | Ağ kartı | “401 alarm, 9 doğrudan kök host'u, 14 servis. Aynı fiziksel alan ve sonraki belirtiler ortak ağ hipotezini destekliyor.” Kanıt listesi ve DNS notunu göster. |
| 01:30–02:20 | Bellek kartı → ayrıntı → bellek öncülleri | “Üç host'ta %60'tan %74'e yükselen 24 öncül. Rastgele düşük ölçümler zincire girmiyor; GC/OOM daha sonra geliyor. Kesin memory leak demiyoruz.” |
| 02:20–03:30 | Dış ödeme kartı; sonra Tüm alarmlar → mobile-bff ara | “24 kaynak alarmı ve 79 provider hedefli timeout tek kartta. Aynı servisteki 12 session timeout'u farklı kartta; pencere tek başına atamıyor.” Bir kaydın hedef/yol gerekçesini aç. |
| 03:30–04:20 | İnceleme adayları → charging-service | “Topolojiyle doğrulanmayan çağrı yönünü uydurmadık. 44 kayıt inceleme kartında ama hâlâ belirsiz. Bu ek kartları doğrulanmış bağımsız olay diye saymıyoruz.” |
| 04:20–05:20 | Ağ kartı → aksiyona geç | Sorumluyu gerçek demo rolüne göre düzenle; “İncelemeye al” seç; “Rack uplink kontrolü için ağ ekibine devredildi” notunu kaydet. Geçmişi göster. Çözüm demosunda bunun senaryo kaydı olduğunu açıkça söyle. |
| 05:20–06:10 | Yöntem ve ölçüm | “1.015 + 1.664 + 321 = 3.000. Gürültü silinmiyor. 578 naif grup ile kart sayısını kıyaslıyoruz; gizli etiketler olmadığı için doğruluk yüzdesi vermiyoruz.” |
| 06:10–06:40 | Kanıt özeti veya AI anlatı düğmesi | Anahtar yoksa şablon olduğunu açıkça göster: “Çekirdek dış API'ye bağlı değil. Opsiyonel model bu kanıtları kısa anlatıya çevirir, korelasyonu değiştiremez.” |
| 06:40–07:00 | Raporu indir; operasyon masasına dön | “Her hipotezden kanıta, kanıttan sorumlu ve ilk aksiyona gidiyoruz. Belirsizliği görünür tutuyoruz.” |

**İlk kesilecek:** 06:10 AI/şablon anlatısı. **İkinci kesilecek:** yoğunlaşma tablosundaki detaylar. Korunacak üç an: 9 host'lu ağ kanıtı, 12/26 ayrımı, aksiyon kaydı.

Sunumda örnek görseldeki 527 alarm, %94 güven veya DNS %18 değerlerini kullanmayın; uygulamada ölçülmediler. Kanıt düzeyi olasılık değildir. “8 gerçek olay bulduk” demeyin: **5 hipotez + 3 inceleme kartı**.

## 2. Üç dakikalık soru-cevap

| Soru | Kısa cevap | Kanıt |
|---|---|---|
| Neden beş olay? | Beş güçlü aile bu veride tetiklendi; sayı sabit değil. 16 bağımsız örnekte 16 kart kalır ve sınır hatası görünür. | `tests/test_engine.py` |
| Ek kartlar recall artırdı mı? | Bunu ölçemiyoruz. 84 belirsiz kaydı inceleme için topluyor; doğrulanmış bağımsız olay saymıyoruz. | `review_candidates`, rapor muhasebesi |
| Pencereler çakışınca ne oluyor? | Her alarmı hedef, yol, tip, konum ve zamanla puanlıyoruz. Yakın iki aday varsa belirsiz bırakıyoruz. | 12/26 ve E3 103 kayıt testleri |
| AI gerekli mi? | Korelasyon için dış model gerekmiyor. AI geliştirmede analiz/kod/test üretti; çalışma zamanında isteğe bağlı kanıt anlatısı var. | `CLAUDE.md`, `src/narrative.py` |
| Neden %94 güven yazmadınız? | Etiketler kapalı, olasılık kalibrasyonu yok. Açık kanıt düzeyi ve somut sinyaller daha savunulabilir. | Kart, `AI_JURI.md` |
| DNS kesin kök mü? | Hayır. Hedef ağ alarmı ve 7 bağlantı reddi var; yalnız 3 yol doğrulanıyor. DNS işlev ölçümü yok. | `dependency_evidence` |
| Gerçek üretimde ne gerekir? | Farklı veriyle eşik doğrulama, kalıcı aksiyon kaydı, kimlik doğrulama, akış işleme ve işletim ölçümleri. | Bilinen sınırlar |
| Çözüldü düğmesi ne yapıyor? | Operatörün notlu durum kaydını tutuyor; gerçek cihaz veya uygulamaya müdahale etmiyor. | `src/server.py` |

## 3. X-Factor cümlesi

“Aynı serviste aynı anda görünen iki kökün etkisini mesaj hedefi ve yönlü bağımlılıkla ayırıyor; ayıramadığımız kayıtları gerekçesiyle belirsiz bırakıyoruz.”

## 4. Yedek plan

- İnternet/API yoksa: çekirdek ve arayüz çalışır; şablon açıklaması kullanılır.
- Tarayıcı sorunu: `demo/operasyon-masasi.png` ve diğer gerçek ekran görüntülerini açın.
- HTTP sunucusu sorunu: `python3 app.py --export outputs/report.json`; JSON'da `summary`, `incidents`, `review_candidates`, `uncertain` gösterin.
- Port doluysa: `python3 app.py --port 8002` ve http://127.0.0.1:8002.
- Sunucuyu yeniden başlatmadan önce güncel aksiyon geçmişini dışa aktarın; bellek sıfırlanır.

## 5. Sahne kontrol listesi

- [x] Yerel uygulama ve test akışları çalışıyor.
- [x] Ekran görüntüleri ve CLI yedeği hazır.
- [ ] Konuşmacılar ve görev dağılımı kesinleşti.
- [ ] Gerçek ekran paylaşımı / projeksiyon test edildi.
- [ ] En az bir kez yüksek sesle, süre tutarak 7 dakika prova yapıldı.
- [ ] Kura nedeniyle uygulama, ekran ve yedekler her an hazır tutuluyor.
- [ ] Sunum öncesi demo aksiyon durumları gözden geçirildi.

Bu belge hazırlanmıştır; ekibin sesli prova yaptığı iddia edilmez.
