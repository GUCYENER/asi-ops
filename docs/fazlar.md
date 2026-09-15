# Fazlar

Detaylı zaman çizelgesi için bkz. [plan.md](plan.md). Aşağıdaki fazlar `/scout → /straton → (/forge veya /augur) → /scribe ‖ /herald` skill zincirine karşılık gelir.

## Faz 0 — Keşif (14:20-14:30)
- **Durum:** planlandı
- **Açıklama:** Senaryo ve veri paketi **mail ile** 14:20'de gelir. `/scout` ile veri şeması, kısıtlar hızla çıkarılır — ayrı bir soru penceresi yok, 14:30'da kodlama başlıyor.
- **Çıktı:** SCOUT REPORT → `/straton`'a girdi

## Faz 1 — Strateji (14:30'un ilk dakikaları)
- **Durum:** planlandı
- **Açıklama:** `/straton` ile çözüm A/B değerlendirilir, MVP scope netleşir. Uzun sürmemeli — dakikalar içinde karar.
- **Çıktı:** FORGE INPUT

## Faz 2 — Geliştirme (14:30-17:30, 180 dk'nın büyük kısmı)
- **Durum:** planlandı
- **Açıklama:** `/forge` (veri/analitik problemse önce `/augur`) ile çalışan çekirdek kurulur. Açıklanabilirlik (XAI) çıktısı bu fazda üretilmeli. 15:00-15:30 ve 17:00-17:30 ikram var — dikkat dağıtabilir, plana dahil edin.
- **Çıktı:** çalışan MVP, `src/` dolu

## Faz 3 — Belgeleme (Faz 2 ile paralel, sona bırakılmaz)
- **Durum:** planlandı
- **Açıklama:** `/scribe` build boyunca AI_JURI.md, submission.json, prompts/'u günceller — 17:30'da aceleye getirilmez.
- **Çıktı:** teslime hazır dokümantasyon

## Faz 4 — Sunum Hazırlığı (17:30 sonrası, mola sırasında)
- **Durum:** planlandı
- **Açıklama:** `/herald` ile 7 dk + 3 dk soru-cevap formatında demo script'i ve jüri soru hazırlığı yapılır.
- **Çıktı:** demo script, fallback plan, X-Factor anlatımı
