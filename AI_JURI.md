# AI Jüri Özeti

> Her iddia için çalışan kod veya doğrulama dosyası belirtilmiştir. Altın etiketlere erişim yoktur.

## 1. AI Stratejimiz ve İş Akışı

İnsan bütünleşik analizi ve geliştirme kapsamını onayladı; iç içe olaylar, kuyruk alarmları, belirsizlik, sorumlu rolleri ve jüri ekranı hakkında düzeltmeler sağladı. Codex/GPT-6 veri analizi, kod, test ve belgeleri üretti. Ayrı alt ajan kullanılmadı. Korelasyon deterministiktir; opsiyonel model yalnız kanıt özeti üretir. Canlı model erişimi bu çalışma sırasında denenmedi.

Kanıt: [prompts/](prompts/), [CLAUDE.md](CLAUDE.md), [docs/plan.md](docs/plan.md), [BUTUNLESIK_ANALIZ.md](BUTUNLESIK_ANALIZ.md).

## 2. Problemi Nasıl Çözdük

3.000 alarmın tamamı işlendi. Yönlü bağımlılık, mesaj hedefi, fiziksel alan, kök imzası ve host bazlı bellek trendi kullanıldı. Her karar gerekçeli: 1.015 olaya bağlı, 1.664 gürültü adayı, 321 belirsiz. 5 olay ve 3 düşük kanıtlı inceleme kartı var. İnceleme kartları 84 belirsiz kaydı görünür kılar; bu kayıtlar ikinci kez sayılmaz.

30 test ve gerçek tarayıcı akışı geçti. Naif 5 dakika × servis gruplaması 578 grup üretir; bu kart sayısı kıyasıdır, etiket doğruluğu kıyası değildir.

Kanıt: [engine.py](src/engine.py), [mimari](docs/mimari.md), [doğrulama](docs/dogrulama.md), [ekran görüntüsü](demo/operasyon-masasi.png).

## 3. X-Factor

**Aynı serviste ve aynı zaman aralığında görünen timeout'ları, mesaj hedefi ve bağımlılık yolu üzerinden farklı köklere ayırıyoruz.** Mobile-bff'in 38 timeout'u 12 oturum / 26 dış ödeme olarak ayrılıyor; 24 kaynak + 79 provider hedefli timeout aynı ödeme kartında kalıyor. Hedefi olmayan yarışan belirtiler zorla atanmak yerine belirsiz bırakılıyor. Her kart, kendi kanıtını ve doğrulanması gereken alternatifini gösteriyor.

Kanıt: `src/engine.py::candidate_score`, `src/engine.py::review_candidates`, `tests/test_engine.py::test_concurrent_mobile_timeouts_follow_message_target`, `tests/test_engine.py::test_external_root_and_79_targeted_timeouts_share_one_card`.

## 4. Çalıştırma

Python 3.9+; harici paket veya API anahtarı zorunlu değil. Katılımcı verisi repo dışında tutulur.

```bash
python3 app.py --data-dir ../katilimci_paketi
```

http://127.0.0.1:8000 adresinde olay kartları, kanıt, sorumlu/durum ve denetim ekranı açılır. Sunucusuz çıktı: `python3 app.py --export outputs/report.json`.

## 5. Bilinen Sınırlar

Gizli etiketler nedeniyle kök doğruluğu, gürültü precision ve recall ölçülmedi. Eşikler heuristik; kanıt düzeyi olasılık değil. İnceleme kartlarının bağımsız olay olduğu bilinmiyor. Tam dosya analizi yapılır. Aksiyonlar bellekte; gerçek altyapıya müdahale yok. Opsiyonel LLM metninde semantik doğruluk garanti edilmez, anahtar yokken yalnız şablon çalışır. Senkron/asenkron yollar aynı ağırlıkta. Geçmiş olay verisi ve üretim dağıtımı kapsam dışı.

Kanıt: [geliştirme raporu](docs/gelistirme_raporu.md), [sözleşme](docs/sozlesme.md), `src/narrative.py`, `src/server.py`.
