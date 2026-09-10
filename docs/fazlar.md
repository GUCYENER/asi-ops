# Fazlar

Detaylı zaman çizelgesi için bkz. [plan.md](plan.md). Aşağıdaki fazlar `/scout → /straton → (/forge veya /augur) → /scribe ‖ /herald` skill zincirine karşılık gelir.

## Faz 0 — Keşif (14:30-14:45)
- **Durum:** planlandı
- **Açıklama:** Senaryo ve veri paketi açıklanır. `/scout` ile veri şeması, kısıtlar, kullanılabilir zaman hızla çıkarılır.
- **Çıktı:** SCOUT REPORT → `/straton`'a girdi

## Faz 1 — Strateji (14:45'in ilk dakikaları)
- **Durum:** planlandı
- **Açıklama:** `/straton` ile çözüm A/B değerlendirilir, MVP scope netleşir. Uzun sürmemeli — dakikalar içinde karar.
- **Çıktı:** FORGE INPUT

## Faz 2 — Geliştirme (14:45-17:30 içinde, ~165 dk'nın büyük kısmı)
- **Durum:** planlandı
- **Açıklama:** `/forge` (veri/analitik problemse önce `/augur`) ile çalışan çekirdek kurulur. Açıklanabilirlik (XAI) çıktısı bu fazda üretilmeli.
- **Çıktı:** çalışan MVP, `src/` dolu

## Faz 3 — Belgeleme (Faz 2 ile paralel, sona bırakılmaz)
- **Durum:** planlandı
- **Açıklama:** `/scribe` build boyunca AI_JURI.md, submission.json, prompts/'u günceller — 17:30'da aceleye getirilmez.
- **Çıktı:** teslime hazır dokümantasyon

## Faz 4 — Sunum Hazırlığı (17:30 sonrası, mola sırasında)
- **Durum:** planlandı
- **Açıklama:** `/herald` ile 7 dk + 3 dk soru-cevap formatında demo script'i ve jüri soru hazırlığı yapılır.
- **Çıktı:** demo script, fallback plan, X-Factor anlatımı
