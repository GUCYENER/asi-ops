# Prompts

Bu klasör, geliştirme sürecinde kullanılan kritik prompt'ları içerir. AI Jüri'nin birinci odağı "AI stratejiniz ve iş akışınız" olduğu için, burası puan getiren en önemli klasörlerden biridir.

## Kullanım
Her önemli/kritik prompt için ayrı bir `.md` dosyası ekleyin, örn:

```
prompts/
├── 01-mimari-tasarim.md
├── 02-api-endpoint-ureteci.md
└── 03-test-yazimi.md
```

Her dosyada şunları belirtin:
- **Amaç:** Bu prompt hangi işi yapmak için kullanıldı
- **Prompt:** Kullanılan tam prompt metni
- **Sonuç:** Hangi kod/dosya üretildi (dosya yoluna referans verin)
- **İnsan müdahalesi:** AI çıktısı üzerinde hangi değişiklikler insan tarafından yapıldı
