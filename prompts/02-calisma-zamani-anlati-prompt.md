# 02 — Çalışma Zamanı Anlatı Prompt'u (ürünün içinde)

## Amaç

Korelasyon motorunun **hesapladığı** kanıtları, nöbetçi mühendisin okuyacağı doğal dile çevirmek. LLM burada karar vermez — sadece var olan kanıtı anlatıya dönüştürür.

## Kullanılan prompt

`src/explain.py:SYSTEM_PROMPT`

```
Sen bir SRE nöbetçi mühendisine yardım eden bir operasyon asistanısın.
Sana bir olay kartının hesaplanmış kanıtları verilecek.
Bu kanıtları 3-4 cümlelik, sade Türkçe bir anlatıya çevir.

KURALLAR:
- Sadece verilen kanıtları kullan, yeni sayı veya servis adı uydurma.
- Kesinlik iddia etme; bu bir hipotezdir.
- Karşı olasılığı da bir cümleyle belirt.
- Teknik jargonu minimumda tut.
```

Kullanıcı mesajı olarak modelin gördüğü tek şey, motorun ürettiği yapılandırılmış kanıt JSON'u:

```json
{
  "baslik": "dc1/rack-A ag kesintisi",
  "kok_neden_hipotezi": "dc1/rack-A fiziksel ag alaninda kesinti (34 ag alarmi, 9 host, 9 servis)",
  "gerekce": "...",
  "sinyaller": ["network_down x12", "pkt_loss x22", ...],
  "etkilenen_servisler": [...],
  "alarm_sayisi": 396,
  "guven": 0.92,
  "karsi_olasilik": [...],
  "onerilen_aksiyon": "..."
}
```

## Neden bu tasarım

1. **Halüsinasyon yüzeyi kapatıldı.** Model ham 3.000 alarmı hiç görmüyor; yalnızca hesaplanmış özet veriliyor. Uydurabileceği bir alan bırakılmadı.
2. **"Kesinlik iddia etme" kuralı.** Doğrulama verisi kapalı; modelin "kesinlikle bu" demesi dürüstlük puanını düşürürdü.
3. **Karşı olasılık zorunlu.** Bonus gereksinimi (B1) doğrudan prompt'a gömüldü.

## Üretilen gerçek çıktı örneği

```
Saat 01:42 civarında dc1 veri merkezindeki rack-A kabinetinde ağ bağlantısı kesildi.
Sistem 34 farklı ağ alarmı gördü: bağlantı reddedildi, paket kayıpları ve ağ çökmesi gibi.
Bu kesinti 9 sunucuyu ve 14 servisi etkiledi.

Neden büyük ihtimalle bu: Tüm belirtiler aynı fiziksel kabinde toplandı ve aynı anda başladı.
Bu patern, tek bir servis sorununa değil, altlarındaki ortak ağ altyapısı sorununa işaret ediyor.

Alternatif senaryo: Order-service'teki paket kayıpları da kök neden olabilir mi?
Pek mümkün değil - çünkü ilk belirtileri ağ alarmlarından 12 saniye sonra geldi,
yani büyük ihtimalle bir kurban, tetikleyici değil.
```

## İnsan müdahalesi / fallback

LLM **kritik yolda değil.** Erişim yoksa, timeout olursa veya hata dönerse `template_narrative()` devreye girer ve aynı kanıtlardan deterministik bir metin üretir. Uygulama tam çalışmaya devam eder.

Kanıt: `src/explain.py:narrate` (try/except bloğu), `src/explain.py:template_narrative`
