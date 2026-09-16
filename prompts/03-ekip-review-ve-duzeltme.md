# 03 — Ekip Review'u ve Bulunan Gerçek Bug

## Amaç

Bütünleşik analiz dokümanı yazıldıktan sonra ekip üyelerine **eleştirel review** yaptırmak. Amaç: "hepimiz aynı fikirdeyiz" rahatlığına kapılmamak.

## Kullanılan yaklaşım

Bütünleşik analiz ([data/BUTUNLESIK_ANALIZ.md](../data/BUTUNLESIK_ANALIZ.md)) ekip üyelerine verildi ve şu soruyla review istendi:

```
Bu bütünleşik analizde İKİSİNİN DE (veya hepimizin) kaçırdığı ne var?
P0 (şimdi düzeltilmeli) / P1 (değerli) olarak önceliklendir.
```

## Gelen bulgular ve her birinin akıbeti

| # | Bulgu (Eren D.) | Durum | Kanıt |
|---|---|---|---|
| P0-1 | "Anomali penceresi bul → içindekileri ata" mantığı kırılır; olaylar zamanda iç içe geçiyor. Atama alarm seviyesinde olmalı | **Zaten böyleydi** — `attach_score()` alarm seviyesinde çalışıyor, pencere yalnızca aday daraltıyor | `src/correlator.py:attach_score` |
| P0-2 | E3'ün kuyruğu 03:01'e kadar sürüyor; 7 kritik alarm sahipsiz kalıyor | **GERÇEK BUG — düzeltildi.** Pencere çekirdekten hesaplandığı için cascade kuyruğu dışarıda kalıyordu. İki geçişli atamaya çevrildi: **2/7 → 7/7** | `src/correlator.py:build_events` |
| P0-3 | JSON sözleşmesinde `uncertain[]` yok | **Zaten vardı** — `unclear[]` olarak mevcut, ayrı UI sekmesi de var | `src/correlator.py:run` |
| P0-4 | Aksiyon sahibi servis kritikliğinden çıkarılamaz; kök alarm tipinden türetilmeli | **Zaten böyleydi** — `ACTION_BOOK` alarm tipi → (aksiyon, sahip) eşlemesi | `src/correlator.py:ACTION_BOOK` |
| P1-5 | `mem_high` merdiveni: tip sayarak değil, host bazında monoton artış aranmalı | **Eklendi** — `memory_ladder()` fonksiyonu, gerekçe metnine giriyor | `src/correlator.py:memory_ladder` |
| P1-6 | `conn_refused` hedefleri kullanılmayan güçlü kanıt (dns-resolver 7 kez) | **Eklendi** — gerekçeye "etki çarpan etkisiyle büyümüş" cümlesi olarak giriyor | `src/correlator.py:why_text` |

## Burhan'ın kabul testi

```
E3'e ait alarmlar (payment-provider-gw kaynaklı, 3 farklı servise yayılan)
tek bir karta mı düşüyor, yoksa yanlışlıkla 2-3 karta mı bölünüyor?
Bölünüyorsa zincirleme eşiği çok sıkı demektir.
```

**Sonuç: tek kartta (EV-04).** 223 alarm, 4 servis (payment-provider-gw, payment-service, order-service, mobile-bff) — bağımlılık zinciri boyunca yayılan tüm cascade tek kartta toplandı, bölünmedi.

## Değeri

Bu review, **saatler harcanacak bir hatayı 15 dakikada yakaladı.** P0-2 düzeltilmeseydi 7 kritik ödeme alarmı "belirsiz" kovasında kalacak ve demo sırasında jüri "bu kritik alarmlar neden hiçbir olaya bağlı değil?" diye soracaktı.

## İnsan müdahalesi

Kaptan, her bulguyu **koda karşı doğruladı** — "zaten yapılmış" olanları kabul etmeyip kod referansıyla teyit etti, gerçek bug'ı (P0-2) ölçüm yaparak kanıtladı (2/7 → 7/7).
