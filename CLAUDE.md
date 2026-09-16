# asi-ops — AI Yapılandırma

## Proje Bağlamı

S-A1 Alarm Fırtınası. 3.000 alarmı kayıpsız işle; en fazla 15 olay/inceleme kartında açıklanabilir hipotez ve ilk aksiyon sun. Kullanıcının `BUTUNLESIK_ANALIZ.md` kararı ve sonraki önerileri güncel kapsamdır.

## Kullanılan AI Araçları

- Bu geliştirme: Codex / GPT-6; daha ayrıntılı sürüm bilgisi sağlanmadı.
- Çalışma zamanında LLM zorunlu değil. Opsiyonel Azure Anthropic Messages model adı `.env` içinde; varsayılan `claude-sonnet-4-5`.
- Canlı Azure erişimi bu oturumda doğrulanmadı. Önceki belgelerdeki “erişim doğrulandı” ifadesini bu uygulamanın test sonucu diye kullanma.

## Açıklanabilirlik (XAI) Kuralı

`src/engine.py::candidate_score` gerçek sinyal katkılarını, `noise_decision` eleme gerekçesini, `build_incident` kanıt ve alternatifleri üretir. Dekoratif veya uydurma gerekçe ekleme. Kök hipotezini kanıtlanmış arıza; destek skorunu olasılık olarak sunma. `review_candidates` kayıtları belirsiz bırakır.

## İnsan / AI İş Bölümü

- **İnsan:** problem, kapsam, bütünleşik karar; P0/P1 düzeltmeleri; jüri ekranı; son operasyon ve teslim kararı.
- **AI:** analiz, deterministik motor, API/arayıüz, test, dokümantasyon ve demo taslağı.

## Kod Standartları ve Kısıtlar

- Python 3.9+ stdlib; vanilla JS. Harici çalışma zamanı paketi ekleme.
- Bütün yeni çalışma bu klasörde. İlk analiz, katılımcı verisi ve kardeş `asi-ops/` repo korunur.
- Zaman pencereyi daraltır; atama alarm seviyesinde yapılır. Servis/ID/tarih/olay sayısını tespit kurallarına sabitleme.
- `.env`, ham veri ve tam JSON dışa aktarımı yayınlama. Örnek ayarlar anahtarsız olsun.
- İnsan sorumlu rolünü değiştirebilir; kritiklikten kişi uydurma.
- Yeniden başlatma aksiyonları sıfırlar; kullanıcı aksiyonları varsa önce dışa aktar.
- Geliştirme yönergeleri kökteki `AGENTS.md` ve `hackathon-skills/` altında; güncel kullanıcı talimatı önceliklidir.

## Kritik Prompt'lara Referans

[prompts/](prompts/) altında kullanıcı yönlendirmeleri ve opsiyonel model prompt'u kayıtlıdır. [Devam notu](docs/devam_notu.md) çalışan durum ve açık işleri özetler.
