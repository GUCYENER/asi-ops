# AI Jüri Özeti

> Her iddia için çalışan kod veya doğrulama dosyası belirtilmiştir. Altın etiketlere erişim yoktur.

## 1. AI Stratejimiz ve İş Akışı

İnsan bütünleşik analizi ve geliştirme kapsamını onayladı; iç içe olaylar, kuyruk alarmları, belirsizlik, sorumlu rolleri ve jüri ekranı hakkında düzeltmeler sağladı. Dört ekip üyesi aynı veriyi birbirinden habersiz analiz etti (Codex/GPT-6 ve Claude Code/claude-opus-5); dördü de bağımsız olarak deterministik korelasyon motoru önerdi. Codex motoru, arayüzü, testleri ve belgeleri üretti; Claude Code bütünleşik analizi, benzer geçmiş olay eşleştirmesini ve entegrasyonu üretti. Korelasyon deterministiktir; opsiyonel model yalnız kanıt özeti üretir. **Canlı model erişimi doğrulandı** (claude-sonnet-4-5-20250929, kanıt kimliği şema kontrolünden geçiyor).

Kanıt: [prompts/](prompts/), [CLAUDE.md](CLAUDE.md), [docs/plan.md](docs/plan.md), [BUTUNLESIK_ANALIZ.md](BUTUNLESIK_ANALIZ.md).

## 2. Problemi Nasıl Çözdük

3.000 alarmın tamamı işlendi. Yönlü bağımlılık, mesaj hedefi, fiziksel alan, kök imzası ve host bazlı bellek trendi kullanıldı. Her karar gerekçeli: 1.015 olaya bağlı, 1.664 gürültü adayı, 321 belirsiz. 5 olay ve 3 düşük kanıtlı inceleme kartı var. İnceleme kartları 84 belirsiz kaydı görünür kılar; bu kayıtlar ikinci kez sayılmaz.

30 test ve gerçek tarayıcı akışı geçti. Naif 5 dakika × servis gruplaması 578 grup üretir; bu kart sayısı kıyasıdır, etiket doğruluğu kıyası değildir.

Kanıt: [engine.py](src/engine.py), [mimari](docs/mimari.md), [doğrulama](docs/dogrulama.md), [ekran görüntüsü](demo/operasyon-masasi.png).

## 3. X-Factor

**Aynı serviste ve aynı zaman aralığında görünen timeout'ları, mesaj hedefi ve bağımlılık yolu üzerinden farklı köklere ayırıyoruz.** Mobile-bff'in 38 timeout'u 12 oturum / 26 dış ödeme olarak ayrılıyor; 24 kaynak + 79 provider hedefli timeout aynı ödeme kartında kalıyor. Hedefi olmayan yarışan belirtiler zorla atanmak yerine belirsiz bırakılıyor. Her kart, kendi kanıtını ve doğrulanması gereken alternatifini gösteriyor.

**Benzer geçmiş olaylar (B3).** Her kart, imza benzerliğiyle eşleşen geçmiş olayı ve o zaman işe yarayan çözümü gösterir. Benzerlik bu uygulamada hesaplanır: `0.45×Jaccard(alarm tipleri) + 0.35×Jaccard(servisler) + 0.20×kategori`. Arşivdeki hazır `similarity_to_current` alanı **bilinçli kullanılmadı**; kullanılsaydı skor bu veri setine gömülü bir sabit olurdu. 5/5 kart doğru vakayla eşleşti (%62–87) ve hesap kırılımı kartta görünür. Arşiv sentetiktir, kartta "örnek arşiv · sentetik" olarak etiketlidir.

Kanıt: `src/history.py::match_signature`, `src/engine.py::candidate_score`, `src/engine.py::review_candidates`, `tests/test_engine.py::test_concurrent_mobile_timeouts_follow_message_target`, `tests/test_engine.py::test_external_root_and_79_targeted_timeouts_share_one_card`.

## 4. Çalıştırma

Python 3.9+; harici paket veya API anahtarı zorunlu değil. Katılımcı verisi repo dışında tutulur.

```bash
python run.py
```

http://127.0.0.1:8000 adresinde olay kartları, kanıt, sorumlu/durum ve denetim ekranı açılır. Sunucusuz çıktı: `python3 app.py --export outputs/report.json`.

## 5. Bilinen Sınırlar

Gizli etiketler nedeniyle kök doğruluğu, gürültü precision ve recall ölçülmedi. Eşikler heuristik; kanıt düzeyi olasılık değil. İnceleme kartlarının bağımsız olay olduğu bilinmiyor. Tam dosya analizi yapılır. Aksiyonlar bellekte; gerçek altyapıya müdahale yok. Opsiyonel LLM metninde semantik doğruluk garanti edilmez, anahtar yokken yalnız şablon çalışır. Senkron/asenkron yollar aynı ağırlıkta. Geçmiş olay arşivi sentetiktir (kendi ürettiğimiz 5 vaka); gerçek ortamda kurumun incident kayıtlarına bağlanır. Üretim dağıtımı kapsam dışı.

Kanıt: [geliştirme raporu](docs/gelistirme_raporu.md), [sözleşme](docs/sozlesme.md), `src/narrative.py`, `src/server.py`.
