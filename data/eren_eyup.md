ocs/ altındaki 3 dosyayı da taradım (plan.md, fazlar.md, mimari.md). Yerel zip hâlâ 10 Eylül sürümü — remote main (dün 13:53, 24d6319) daha güncel ve kural olarak onu alıyorum. mimari.md tamamen boş şablon, yarın doldurulacak.

Geçerli kurallar (remote plan.md + fazlar.md, birleşik)
Saat	Ne olur	Bizim aksiyon
14:20	Senaryo + veri seti mail ile gelir	Maili aç, case metnini bana yapıştır
14:30	Kodlama başlar — ayrı soru penceresi YOK	14:30'da yazmaya başlamış olmalıyız
14:30–17:30	180 dk net geliştirme	/scout → /straton → /forge (+/augur)
15:00–15:30 / 17:00–17:30	Kurabiye / pizza	Dikkat dağıtıcı, masada nöbetçi kalsın
17:30	HARD STOP — GitHub repo linki olarak teslim, sonraki commit sayılmaz	17:20 push freeze, 17:25 remote doğrulama
17:30–17:45	Ara + sunum son gözden geçirme	/scribe → /herald son kontrol, repoya dokunma
17:45–20:30	Sunumlar, 10 dk/takım (7 dk + 3 dk), sıra kura	Geç gruba düşersek uygulama açık bekler
20:30	Sonuçlar (15.000 / 10.000 / 5.000 ₺)	—

Değişmeyen puan kuralları: kanıtsız iddia puanlanmaz (her iddia dosya:satır), AI stratejisi + prompts/ birinci odak, karar üreten her çıktı gerekçesini de üretmeli (XAI), AI Jüri kodu okur ama uygulamayı çalıştırmaz → demo/ ekran görüntüsü şart, deploy zorunlu değil, dürüst "bilinen sınırlar" puan kazandırır. Resmi araçlar Claude (SAKA) + Codex; başka araç kullanırsak beyan zorunlu.

Case geldiğinde ilk 10 dakikada ne yapacağım
Case'i kendi cümlelerimle özetleyip resmi requirement listesi çıkarırım
Veri teşhisi: şema, boyut, hedef alan, kalite/leakage/PII riski
Belirsizlikler + yazılı varsayımlar (mentöre sorulacaklar ayrı işaretli)
Ölçülebilir başarı kriteri
2 çözüm (A güvenli / B iddialı) + puan tablosu + gerekçeli önerim
Kaptan seçer → FORGE INPUT + JSON çıktı sözleşmesi ({karar, gerekce, guven_skoru, sinyaller}) dondurulur
4 kişiye dakika bazlı workstream ataması + checkpoint saatleri (CP1 15:40 uçtan uca, CP2 16:40 demo edilebilir, 17:05 feature freeze)
Şimdi benden istediğim 3 şey (case gelmeden)
Case metnini birebir yapıştır (özetleme, kes-yapıştır)
Veri: dosya yolu + kolon adları/örnek satır. ⚠️ Şirket verisinin dış LLM'e gitmesi konusunda mentörden izin çıktı mı? Çıkmadıysa bana ham satır değil sadece şema ver, ben ona göre çalışırım
Repo durumu: ~/asi-ops clone'u ve push yetkisi tamam mı? (Dünkü NO-GO blocker'ıydı — teslim buna bağlı)

Hazırım, case'i bekliyorum.

MODE: LARGE
DELIVERY: ANALYSIS_ONLY
PRIORITY: QUALITY

STRICT EXECUTION RULE:

DO NOT IMPLEMENT ANYTHING.

- Kod yazma.
- Dosya oluşturma veya değiştirme.
- Repository değiştirme.
- Notebook oluşturma.
- Script çalıştırarak solution üretme.
- Model train etme.
- Commit / push yapma.
- Dependency kurma.
- Uygulama geliştirme.

Read-only analysis only.

Bu aşamanın amacı:
Gerçek hackathon case'ini uçtan uca anlamak,
en güçlü çözüm stratejisini belirlemek
ve ekibin uygulayacağı eksiksiz execution blueprint'ini hazırlamaktır.

MODE: LARGE
DELIVERY: ANALYSIS_ONLY
PRIORITY: QUALITY

MISSION:
SIGNAL SPRINT — AO AI HACKATHON 2026
CASE ANALYSIS & WINNING SOLUTION BLUEPRINT

OFFICIAL PARTICIPANT PACKAGE:

~/Downloads/katilimci_paketi

Bu klasör hackathon için bize verilen resmi pakettir.

==================================================
STRICT RULE — NO IMPLEMENTATION
==================================================

Bu aşamada sadece ANALİZ ve PLANLAMA yap.

KESİNLİKLE:

- kod yazma
- dosya değiştirme
- repository değiştirme
- notebook oluşturma
- model train etme
- dependency yükleme
- uygulama geliştirme
- commit/push yapma

YAPMA.

Repository ve dosyalar üzerinde READ-ONLY inceleme yap.

Ben implementation'a geçmek için daha sonra ayrıca açık komut vereceğim.

==================================================
1 — FULL PACKAGE DISCOVERY
==================================================

Önce ~/Downloads/katilimci_paketi içindeki HER ŞEYİ incele.

Inventory çıkar:

- case / senaryo
- README
- MD
- PDF
- CSV
- XLSX
- JSON
- dataset
- rules
- scoring
- submission requirements
- examples
- templates
- architecture veya teknik dokümanlar

Dosyalar birbirine referans veriyorsa takip et.

Case metnini TAMAMINI oku.

Resmi participant package bu aşamadaki PRIMARY SOURCE OF TRUTH olsun.

Önceki hackathon hazırlıklarımızla çelişen yeni resmi bilgi varsa
yeni resmi paket kazanır.

Kaynakta olmayan requirement uydurma.

Her kritik bilgiyi:

FACT
INFERENCE
ASSUMPTION
UNKNOWN

olarak ayır.

==================================================
2 — CASE DECONSTRUCTION
==================================================

Case'i bana uçtan uca açıkla:

- Gerçek problem nedir?
- Kim için çözülüyor?
- Business / operational problem nedir?
- Input nedir?
- Beklenen output nedir?
- Dataset ne içeriyor?
- Zorunlu requirement'lar neler?
- Optional alanlar neler?
- Yasaklar / constraints neler?
- Teslim edilmesi gerekenler neler?
- Jüri neyi değerlendirecek?
- Puanlama sistemi varsa nedir?
- Başarı nasıl ölçülecek?

Case'in tek cümlelik özünü ayrıca yaz.

==================================================
3 — DATASET ANALYSIS PLAN
==================================================

Dataset varsa dosyaları READ-ONLY incele.

Belirle:

- dosya sayısı
- formatlar
- schema
- kolonlar
- data types
- row counts
- labels / target
- missing values açısından olası sorunlar
- duplicates
- PII / confidential data riski
- class imbalance
- leakage riski
- timestamp / identifier alanları
- data quality problemleri
- train/test ayrımı açısından riskler

Dataset'i çözmek için hangi analizlerin yapılması gerektiğini
öncelik sırasıyla çıkar.

Henüz bu analizleri implementation seviyesinde çalıştırma.

==================================================
4 — SUCCESS / WIN CONDITIONS
==================================================

Resmi kurallara göre:

MUST HAVE
SHOULD HAVE
NICE TO HAVE

şeklinde ayır.

Sonra:

"Bu hackathon'da güçlü sonuç almak için gerçekte neyi iyi yapmamız gerekiyor?"

sorusunu cevapla.

Özellikle:

- problem çözme
- AI kullanımı
- explainability
- innovation
- business value
- technical correctness
- metrics
- demo
- documentation
- presentation

alanlarının önemini değerlendir.

Resmi olmayan çıkarımları açıkça işaretle.

==================================================
5 — AI SOFTWARE COMPANY ANALYSIS
==================================================

Mevcut capability'leri doğrula.

Bu LARGE analizde sadece gerçekten faydalı olanları kullan:

Superpowers
→ brainstorming / structured reasoning / planning

gstack
→ problem framing / engineering / product / presentation perspective

Agent Teams
→ yalnız bağımsız analysis workstream'leri faydalıysa

Hackathon-specific skills mevcutsa:
- scout
- straton
- forge
- augur
- oracle
- scribe
- herald

Case'e göre specialist kullan.

Ancak henüz implementation yok.

Frontend/backend/database/security gibi specialist'leri
yalnız case gerçekten gerektiriyorsa analiz amacıyla çağır.

Gereksiz agent kullanma.

==================================================
6 — PARALLEL ANALYSIS WORKSTREAMS
==================================================

Gerekirse problemi şu tür workstream'lere böl:

A — Requirements / Rules Analyst
B — Data / AI Analyst
C — Architecture / Engineering Analyst
D — UX / Demo Analyst
E — Jury / Presentation Strategist

Case'e uygun olmayan stream'i kullanma.

Her workstream'in bulgularını sonunda birleştir.

Çelişki varsa çöz.

==================================================
7 — RESEARCH QUESTIONS
==================================================

Case veri/AI ağırlıklıysa güçlü research question'lar üret.

Her biri için:

- neden önemli?
- hangi datayla cevaplanır?
- hangi yöntem gerekir?
- hangi metric gerekir?
- hangi visualization gerekir?
- jüri açısından değeri nedir?

Sonra:

HIGH VALUE
MEDIUM VALUE
LOW VALUE

olarak sınıflandır.

==================================================
8 — SOLUTION OPTIONS
==================================================

Case için en az 3 gerçekçi çözüm yaklaşımı üret:

A — SAFE / FAST
B — BALANCED
C — AMBITIOUS

Her biri için:

- yaklaşım
- architecture
- AI yöntemi
- avantaj
- dezavantaj
- implementation complexity
- süre riski
- data riski
- explainability
- demo value
- jury impact
- failure modes

değerlendir.

==================================================
9 — BEST SOLUTION
==================================================

Sonra TEK bir ana çözüm seç.

Açıkça:

"Biz hackathon'da bunu yapmalıyız."

de.

Nedenlerini belirt.

Çözümü uçtan uca tasarla:

INPUT / DATA
↓
PREPROCESSING
↓
ANALYSIS / AI
↓
DECISION
↓
EXPLANATION
↓
METRIC
↓
OUTPUT / UI
↓
DEMO
↓
BUSINESS IMPACT

Ama hiçbirini implement etme.

==================================================
10 — TECHNICAL BLUEPRINT
==================================================

Seçilen çözüm için teknik tasarım çıkar.

Belirle:

- teknoloji stack'i
- Python / JS vb.
- hangi kütüphaneler
- AI/ML yaklaşımı
- backend gerekiyor mu?
- UI gerekiyor mu?
- database gerekiyor mu?
- API gerekiyor mu?
- LLM gerekiyor mu?
- local mi?
- external dependency var mı?
- fallback nasıl olacak?

Mümkün olan EN BASİT ve en güvenilir yapıyı tercih et.

Overengineering yapma.

==================================================
11 — AI / ML STRATEGY
==================================================

AI/ML gerekiyorsa alternatifleri karşılaştır.

Örneğin case'e göre:

- rules/statistics baseline
- classification
- regression
- anomaly detection
- clustering
- LLM
- hybrid approach

değerlendir.

Her model/yöntem için:

- neden?
- metric?
- data requirement?
- explainability?
- süre?
- failure risk?

belirt.

En güçlü kombinasyonu seç.

==================================================
12 — EXPLAINABILITY / X-FACTOR
==================================================

Çözüm bir karar üretiyorsa:

WHAT
WHY
CONFIDENCE
SUPPORTING SIGNALS

çıktısını nasıl vereceğimizi tasarla.

Case'e özel X-Factor öner.

X-Factor:

- gerçek problemle ilişkili
- birkaç dakikada anlatılabilir
- kanıtlanabilir
- demo'da görünür

olsun.

==================================================
13 — METRIC STRATEGY
==================================================

Hangi metric'leri kullanacağımızı belirle.

BASELINE vs OUR SOLUTION yaklaşımını tasarla.

Uydurma metric üretme.

Her metric için:

- neyi ölçüyor?
- neden önemli?
- nasıl hesaplanacak?
- jüriye nasıl gösterilecek?

belirt.

==================================================
14 — IMPLEMENTATION BACKLOG
==================================================

KOD YAZMADAN implementation backlog çıkar.

P0 — zorunlu
P1 — değerli
P2 — zaman kalırsa

olarak ayır.

Her task için:

- task
- owner/skill
- dependency
- expected output
- done criteria
- estimated effort / order

belirt.

==================================================
15 — TEAM / AGENT ROUTING
==================================================

İnsan ekibini ve AI agent'larını case'e göre böl.

Her kişi/agent için:

- görev
- input
- output
- dependency
- merge point

belirt.

Agent Teams kullanılacaksa neden kullanıldığını açıkla.

Gereksiz paralellik yapma.

==================================================
16 — TIMEBOX PLAN
==================================================

Mevcut hackathon deadline'ına göre kalan zamanı kullan.

Gerçek saate göre planı ölçekle.

Bana:

- ilk 15 dakika
- ilk çalışan vertical slice hedefi
- MVP checkpoint
- feature freeze
- documentation freeze
- push freeze
- submission

zamanlarını ver.

Ayrıca:

IF BEHIND SCHEDULE

durumunda hangi özelliklerin hangi sırayla kesileceğini yaz.

==================================================
17 — TEST / VALIDATION PLAN
==================================================

Implementation sonrasında yapılacak kontrolleri şimdiden tanımla.

Case'e göre:

- data validation
- unit
- integration
- model validation
- UI smoke
- API
- edge cases
- fallback
- reproducibility

belirle.

Her test için acceptance criteria yaz.

==================================================
18 — DEMO BLUEPRINT
==================================================

Demo'yu adım adım tasarla.

Şunları belirt:

- hangi input
- hangi aksiyon
- hangi output
- wow moment nerede?
- XAI nerede?
- metric nerede?
- business value nerede?

Demo 2–4 dakikada güçlü şekilde anlatılabilsin.

Fallback demo planını da ver.

==================================================
19 — PRESENTATION BLUEPRINT
==================================================

Final jüri sunumu için slide-by-slide veya bölüm-bölüm narrative oluştur.

Örneğin:

Problem
Why it matters
Dataset / insight
Solution
Architecture
AI
Demo
Metric
X-Factor
Limitations / next step

Ancak resmi süre ve case'e göre optimize et.

Her bölümde jüriye söyleyeceğimiz ana cümleyi yaz.

==================================================
20 — RED TEAM
==================================================

Seçtiğin çözümü eleştir.

Ara:

- requirement kaçırılmış mı?
- overengineering var mı?
- data leakage riski?
- yanlış metric?
- model gereksiz mi?
- LLM gerçekten gerekli mi?
- demo riski?
- zaman riski?
- dependency riski?
- güvenlik/gizlilik riski?
- jüriye teknik ama değersiz bir çözüm sunma riski?

Sonra solution blueprint'i iyileştir.

==================================================
FINAL OUTPUT
==================================================

BU AŞAMADA KOD YAZMA.

Bana tek bir HACKATHON MASTER BLUEPRINT ver:

Executive Summary
Case'in sade Türkçe açıklaması
Official requirements
Dataset analysis
Constraints
Scoring / win conditions
En önemli riskler
Research questions
Solution alternatives
Selected best solution
Neden bu çözüm
Architecture
AI/ML strategy
Explainability / X-Factor
Metrics
UI / output design
Team & agent routing
Implementation backlog
Step-by-step execution plan
Time plan
Test / validation plan
Demo blueprint
Presentation blueprint
Failure / fallback plan
Submission checklist
İlk yapacağımız 10 işlem

Son bölümde ayrıca:

DO NOT IMPLEMENT YET

yaz ve benden açık implementation komutu bekle.

ŞİMDİ BAŞLA:

~/Downloads/katilimci_paketi

klasöründeki resmi hackathon materyallerinin tamamını read-only incele.

Ran 2 commands

Paket okundu. Şimdi resmi maili ve veriyi read-only profilliyorum (sadece istatistik, çözüm kodu değil).

Ran 3 commands

Veri temiz ve tutarlı. Olay yapısını görmek için son bir profil turu atıyorum, ardından blueprint'i veriyorum.

Ran 3 commands
HACKATHON MASTER BLUEPRINT — S-A1 "Alarm Fırtınası"

Kaynak: ~/Downloads/katilimci_paketi (brifing + veri sözlüğü + resmi mail + 4 veri dosyası). Hepsi read-only okundu ve profillendi. Hiçbir şey yazılmadı, kurulmadı, commit edilmedi.

1 — EXECUTIVE SUMMARY

3.000 alarmlık 2 saatlik penceredeki veriyi profilledim. Veri kusursuz temiz (eksik değer yok, duplicate yok, host/servis referansları %100 tutarlı) — yani zaman veri temizliğine değil, korelasyon mantığına harcanmalı.

Profil sonucunda 4 gerçek olay ve geniş bir arka plan gürültüsü katmanı net biçimde ayrıştı (kanıtlar §4'te). Kazanan çözüm karmaşık ML değil: bağımlılık grafiği + zaman penceresi + şiddet tabanlı deterministik korelasyon motoru, üstünde LLM'in sadece anlatı katmanı olarak durduğu bir mimari. Sebep: puanlama "kök neden isabeti + yanlış birleştirme + gürültü elemesi" ölçüyor ve brifing açıkça "gerekçeli yanlış hipotez, gerekçesiz doğru hipotezden yüksek puan alır" diyor. Yani açıklama kalitesi tahmin doğruluğundan daha çok puan getiriyor.

Ayrıca kritik bir kolaylık: veri tamamen sentetik → dış LLM'e veri gönderme kısıtı (dünkü Q1 blocker'ı) bu case için geçersiz. Claude'u özgürce kullanabiliriz.

Tek cümlelik öz: 3.000 alarmı, her biri kök neden hipotezi + gerekçesi + karşı olasılığı + önerilen aksiyonu taşıyan ≤15 olay kartına indirgeyen ve elenen gürültüyü denetlenebilir kılan bir korelasyon motoru.

2 — CASE'İN SADE TÜRKÇE AÇIKLAMASI

Gece 02:14, nöbetçi mühendis 2 saatlik pencerede 3.000 alarm görüyor. O gece birden fazla bağımsız arıza aynı anda yaşanmış; alarmların çoğu ise hiçbir olayla ilgisi olmayan rutin gürültü. Mühendisin problemi alarm sayısı değil, neden-sonuç ilişkisinin görünmez olması: hangisi kök neden, hangisi türev etki, hangisi gürültü ayırt edilemiyor, müdahale sırası yanlış kuruluyor, çözüm süresi uzuyor.

Bizden istenen: bu seli birkaç okunabilir karara indirgemek ve indirgemenin gerekçesini göstermek.

Kim için: NOC / nöbetçi operasyon mühendisi (7 dakikası var)
Input: 3.000 alarm + 32 bağımlılık kaydı + 56 sunucu envanteri
Output: ≤15 olay kartı (kök neden hipotezi, etkilenen servisler, alarm sayısı, zaman aralığı, önerilen ilk aksiyon + sahip + durum) + gürültü denetim görünümü
Gerçek olay sayısı bize söylenmiyor — veriden çıkarılacak; çözüm sayıyı bilmeden çalışmalı
Doğrulama verisi (ground truth) jüride kapalı — bizim skorumuzu onlar hesaplayacak
3 — RESMİ GEREKSİNİMLER

ZORUNLU (FACT)

#	Gereksinim	Kabul kriteri
Z1	Alarm akışının tamamı işlenmeli; kısmi veri = eksik	3.000/3.000 kayıt okunuyor
Z2	Alarmlar anlamlı gruplara indirgenip her grup için tek olay kartı	≤15 kart
Z3	Her kartta: kök neden hipotezi, etkilenen servis listesi, alarm sayısı, zaman aralığı	Ekranda görünür
Z4	Her kart için önerilen ilk aksiyon + sahip + durum kayıt altında	Kartta alan mevcut
Z5	(Opsiyonel) Aksiyonun açılıp kapanana kadar izlenebilmesi demoda gösterilmeli	Demoda 1 aksiyon durumu değiştirilir
Z6	Uygulama veri paketiyle sıfırdan ayağa kalkıp sonuç üretmeli	Temiz clone + tek komut
Z7	Kök neden hipotezleri gerekçesiyle birlikte ekranda	Her kartta "neden" metni
Z8	Demoda canlı çalışmalı (terminal/masaüstü/web serbest)	Sahnede çalışıyor
Z9	Repo public, değerlendirme 17:30'daki son commit üzerinden	Push 17:30'dan önce
Z10	Repo içeriği: README.md (kurulum, kullanılan AI araçları, MCP listesi, ekran görüntüleri), docs/ (plan, fazlar, mimari), .env.example, AI yapılandırma dosyaları (CLAUDE.md vb.)	Dosyalar dolu
Z11	Kullanılan her açık kaynak kütüphane README'de belirtilmeli	Bağımlılık listesi
Z12	Örnekleme yaparsak demoda belirtmek zorunlu	(Yapmayacağız)

BONUS / X-FACTOR (FACT)

B1: Kök neden hipotezinin neden bu olduğunu doğal dille açıklamak ve karşı olasılıkları belirtmek
B2: Gürültü olarak elenen alarmların neden elendiğini gösteren denetim görünümü
B3: Benzer geçmiş olay örüntülerini yakalayıp kartın üzerine iliştirmek

KAPSAM DIŞI (FACT) — vakit harcamayın

Gerçek zamanlı akış altyapısı (batch okuma yeterli)
Kullanıcı yönetimi / login / yetkilendirme
Kalıcı veritabanı (bellek içi saklama kabul)

UNKNOWN

Puan ağırlıkları (4 ölçüt listelenmiş, ağırlık verilmemiş)
Gerçek olay sayısı ve ground truth eşleşmesi
AI Jüri otomatik taraması var mı (dünkü çelişki sürüyor)
Sunum sırası (kura)
4 — DATASET ANALİZİ (profilleme sonuçları — FACT)

Dosyalar: alarms.json (3.000 kayıt, 1.0 MB) · alarms.csv (aynı içerik, tags 3 kolona açık) · service_dependencies.csv (32 kayıt) · host_inventory.csv (56 sunucu) · VERI_SOZLUGU.md · SENARYO_BRIFINGI.md

Veri kalitesi — beklenmedik derecede temiz:

Kontrol	Sonuç
Satır / benzersiz alarm_id	3.000 / 3.000
Eksik veya boş alan	0
Şema tutarlılığı	Tüm kayıtlar aynı 9 alan
Zaman aralığı	2026-09-10 01:30:20 → 03:30:20, tam 120 dk, 121 dakikanın hepsi dolu
Aynı (ts,host,servis,tip) tekrarı	1 adet (ihmal edilebilir)
alarms.host ⊄ envanter	0 — referans bütünlüğü tam
Alarm servis ↔ envanter servis çelişkisi	0
Servis sayısı / host / tip	27 / 56 / 25 (sözlükte 26 tip listeli, network_down dahil hepsi mevcut; 1 tip veride hiç geçmiyor)
ortam	Tümü prod → ayırt edici değil, kullanma
Şiddet dağılımı	1:614, 2:709, 3:800, 4:629, 5:248
Kaynak sistem	5 sistem dengeli (559–645) → ayırt edici değil
Mesaj şablonu	48 farklı şablon (sayılar değişken) → regex ile sinyal çıkarılabilir

PII / gizlilik: YOK. Veri sözlüğü açıkça "tüm veriler sentetiktir, hiçbir kurumsal sisteme erişim gerektirmez" diyor → repoya commit edilebilir, LLM'e gönderilebilir. (Yine de data/ klasörünü README'de kaynağıyla belirtin.)

Sınıf dengesizliği / leakage: Etiket yok, train/test yok → ML supervised eğitim mümkün değil. Bu unsupervised/kural tabanlı bir problem. Leakage riski yok; overfitting riski var (veriye elle uydurulan sabit kurallar).

Zaman profili — dakika bazlı alarm yoğunluğu

Taban gürültü ~12-20 alarm/dk. İki belirgin patlama + iki yavaş yayılan olay:

01:45 ██████████████████ 79   ← E1 zirvesi
01:47 ███████████████ 69
02:08 ███████ 28            ← E2 yavaş yükseliş
02:18 ████████ 36
02:42 ███████████ 47         ← E3 zirvesi
02:45 ███████████ 47
03:12 ██████ 29              ← E4 yavaş
Bulunan 4 olay (kanıtlarıyla — INFERENCE, ama veri kanıtı güçlü)
#	Zaman	Kök neden hipotezi	Kanıt	Tip
E1	01:42–01:55	dc1 / rack-A ağ kesintisi (ToR switch / uplink)	12 network_down alarmının tamamı dc1+rack-A, 7 farklı servis/host'ta 01:42:13–01:45:04 arası. Burst'te rack-A 329 alarm (rack-B 156, rack-C 160). Türev: api-gateway/subscriber-service/mobile-bff/order-service timeout+http_5xx+thread_pool, report-batch pkt_loss %77	Ani patlama
E2	02:05–02:35	billing-db disk dolması → yazma hatası	02:05:06'dan itibaren ao-034/035/036-billing disk_full sev5, %97-100 dolu, hemen ardından db_write_fail "tablespace genişletilemedi". Türev: billing-service db_conn_pool+txn_fail+http_5xx, invoice-batch db_write_fail, payment/charging latency_high	Yavaş yayılan
E3	02:40–02:57	payment-provider-gw dış servis kesintisi	02:40:28'den itibaren 24 ext_unreach/ext_slow alarmının tamamı sev5, HTTP 504. Türev bağımlılık zincirini birebir izliyor: payment-service txn_fail(28)+timeout(31) → order-service txn_fail(24) → mobile-bff http_5xx(27). sev5 zirvesi 02:40-02:50 bucket'ında (86+44)	Ani patlama
E4	03:05–03:25	Batch penceresi çakışması → subscriber-db bağlantı havuzu tükenmesi	03:05-03:06 batch_overlap ×4 (batch-scheduler) → report-batch + reconciliation-batch db_conn_pool/batch_slow → subscriber-db db_conn_pool (03:09-03:23, zirve 6) → subscriber-service latency_high	Yavaş yayılan, en zor yakalanan

Gürültü katmanı (INFERENCE): Zaman içinde düzgün dağılmış (cv<1.0) tipler → mem_high(240), cert_expiry(220), cpu_high(230), ntp_drift(193), disk_warn(189), log_rotate(196), backup_warn(177) ≈ 1.445 alarm. Ayrıca latency_high(402) ve network_flap(202) kısmen taban gürültü, kısmen olay türevi — bunları körü körüne elemek hata olur, zaman penceresi + olay yakınlığıyla ayrıştırılmalı.

⚠️ Tuzak (brifing uyarısı doğrulandı): "Alarm tipleri olaylar arasında paylaşılır." latency_high hem E1, E2, E3'te hem taban gürültüde var. Sadece tipe bakan çözüm yanılır.

5 — KISITLAR
Kısıt	Etki
17:30 hard stop, değerlendirme son commit üzerinden	17:20 push freeze
Demo canlı çalışmalı	Sıfır dış bağımlılık hedefi
Tüm veri işlenmeli	Örnekleme yok
≤15 kart	Kart sayısı bir tasarım parametresi, üst sınır
Ortamımız: Python 3.9.6, pandas/streamlit/numpy KURULU DEĞİL, Node yok	Stdlib-öncelikli tasarım (§12)
Ground truth kapalı	Kendi doğruluğumuzu ölçemeyiz → iç tutarlılık metrikleri kullanacağız
6 — SCORING / WIN CONDITIONS

Resmi ölçütler (FACT, ağırlık verilmemiş):

Ölçüt	Ne bakılacak	Bizim kaldıracımız
İndirgeme oranı	Kart sayısı / toplam alarm	3.000 → ~8-12 kart (%99,6 indirgeme)
Kök neden isabeti	Gerçek köklerden kaçını yakaladık	4 olayı da yakalayan tasarım
Yanlış birleştirme	İlgisiz iki olayı tek karta koyduk mu	E2 ile E3 kritik ayrım (ikisi de ödeme zinciri!)
Gürültü elemesi	Elenenlerin gerçekten gürültü olma oranı	Muhafazakâr eleme + denetim görünümü

MUST HAVE

3.000 alarmın tamamı işleniyor, ≤15 kart üretiliyor
Kartta: kök neden hipotezi + gerekçe + etkilenen servisler + alarm sayısı + zaman aralığı
Önerilen ilk aksiyon + sahip + durum alanı
Temiz clone'dan tek komutla çalışıyor, canlı demo
README (AI araçları, MCP listesi, kütüphaneler, ekran görüntüleri) + docs/ + .env.example + CLAUDE.md

SHOULD HAVE

Aksiyon durum değişimi demoda canlı (Z5 — "çözümünüze güç katar")
Karşı olasılıklar (B1) + gürültü denetim görünümü (B2)
Baseline vs bizim çözüm metrik karşılaştırması

NICE TO HAVE

Benzer geçmiş örüntü eşleştirme (B3)
LLM ile doğal dil anlatı katmanı
Zaman çizelgesi görselleştirmesi

Gerçekte neyi iyi yapmalıyız (önem sırası — INFERENCE, brifing sinyallerine dayalı):

Explainability — "gerekçeli yanlış > gerekçesiz doğru" açıkça yazılmış. En yüksek getirili alan.
Yanlış birleştirme kontrolü — ayrı bir ölçüt, kolay kaybedilir
Gürültü elemesi + denetimi — hem ölçüt hem bonus
Demo — canlı çalışma zorunlu, 7 dk sahne
Teknik doğruluk — tüm veri işleniyor
AI kullanımı — repo kuralı, AI Jüri odağı
Business value — "7 dakikası var" çerçevesi
Innovation — X-Factor alanı
Metrics — ölçülebilir indirgeme
UI cilası — en düşük öncelik
7 — EN ÖNEMLİ RİSKLER
#	Risk	Etki	Önlem
R1	E2 ve E3'ü tek karta birleştirmek (ikisi de payment/order/billing zincirine dokunuyor)	"Yanlış birleştirme" puanı	Zaman boşluğu kontrolü (02:35→02:40 arası sakinleşme) + farklı kök tip imzası
R2	E4'ü (yavaş batch olayı) kaçırmak	"Kök neden isabeti"	Yalnız patlama tespiti değil, oran artışı (baseline'a göre) tespiti de
R3	Gürültüyü fazla agresif elemek	"Gürültü elemesi" ölçütü ters teper	Sadece zamanda düzgün dağılmış + olay penceresi dışındaki düşük şiddetlileri ele; her eleme kararı loglansın
R4	Kuralları bu veriye elle uydurmak (overfit)	Jüri "genel mi?" diye sorar	Parametreleri veriden türet (baseline oran, z-skor), sabit host/servis adı yazma
R5	Ortam: pandas/streamlit yok, Python 3.9, eski SSL	Kurulum tıkanırsa saat kaybı	Stdlib-only çekirdek (§12), UI kurulum riski çekirdeği bloklamaz
R6	LLM'i kritik yola koymak	Demo çöker	LLM sadece süsleme katmanı, deterministik şablon fallback
R7	Zaman: UI'ya fazla yatırım	MVP yetişmez	CP1'e (15:50) kadar UI yok, JSON + terminal çıktısı
R8	Repo/push yetkisi (dünkü blocker)	Teslim edilemez	Şimdi doğrulanmalı
8 — RESEARCH QUESTIONS
#	Soru	Neden önemli	Veri	Yöntem	Metrik	Değer
Q1	Kaç bağımsız olay var?	Kart sayısını belirler	alarms + zaman	Dakika bazlı yoğunluk + z-skor + boşluk analizi	Tespit edilen olay sayısı	HIGH
Q2	Bir olayın kökü hangi alarm?	Ana ölçüt	alarms + deps + inventory	En erken + en yüksek şiddet + bağımlılık grafiğinde en alt (downstream) düğüm	Kök isabeti	HIGH
Q3	Hangi alarm gürültü?	Ayrı ölçüt + bonus	alarms	Zaman düzgünlüğü (cv) + şiddet + olay penceresine uzaklık	Elenen alarm oranı	HIGH
Q4	İki olay gerçekten ayrı mı?	Yanlış birleştirme ölçütü	alarms + deps	Zaman boşluğu + servis kümesi örtüşmesi + kök tipi farkı	Ayrım doğruluğu	HIGH
Q5	Etki bağımlılık grafiğinde nasıl yayılıyor?	Gerekçenin omurgası	deps	Yönlü graf üzerinde geri yayılım (hedef bozulursa kaynak etkilenir)	Zincir uzunluğu	HIGH
Q6	Rack/DC lokalitesi sinyal veriyor mu?	E1'in kökü tam bu	tags + inventory	Olay içi rack/dc yoğunlaşma oranı	Konsantrasyon %	MEDIUM
Q7	Yavaş yayılan olay nasıl yakalanır?	E4	zaman serisi	Hareketli ortalama + kümülatif artış	Tespit gecikmesi	MEDIUM
Q8	Mesaj metninden ek sinyal (%100 dolu, HTTP 504) çıkar mı?	Gerekçeyi zenginleştirir	message	Regex ile sayı çıkarımı	—	MEDIUM
Q9	Kaynak sistem (OBM/Zabbix...) ayırt edici mi?	—	source_system	Dağılım testi	—	LOW (dengeli, bilgi yok)
Q10	ortam alanı kullanılır mı?	—	tags	—	—	LOW (hepsi prod)
9 — ÇÖZÜM ALTERNATİFLERİ
A — SAFE / FAST: Zaman penceresi + servis kümeleme
Yaklaşım: 5 dk'lık kayan pencerede alarm yoğunluğu eşiği aşınca olay aç; aynı pencerede alarmları servise göre grupla; en erken/en şiddetli alarm = kök.
Mimari: Tek Python script → JSON → terminal tablosu
Artı: 45 dk'da biter, sıfır risk · Eksi: Bağımlılık grafiğini kullanmaz, gerekçe zayıf, E4'ü kaçırır, "yanlış birleştirme" riski yüksek
Explainability: Zayıf · Demo değeri: Düşük · Jüri etkisi: Orta-düşük
B — BALANCED: Bağımlılık farkında korelasyon motoru + gerekçeli kart + hafif UI ⭐
Yaklaşım: (1) Baseline gürültü profili çıkar → (2) anomali pencereleri tespit et (patlama + yavaş artış) → (3) her pencerede alarmları bağımlılık grafiği + host/rack/dc + zaman yakınlığıyla olaylara ata → (4) kökü seçim kuralıyla belirle (en erken ∧ en şiddetli ∧ grafikte en downstream) → (5) gerekçe + karşı olasılık + güven skoru üret → (6) aksiyon önerisi (kök tipine göre) + sahip + durum → (7) kalanları gürültü olarak, eleme sebebiyle işaretle
Mimari: Stdlib Python çekirdek → JSON → basit web UI (kart listesi + detay + gürültü denetimi + aksiyon durumu)
Artı: Tüm zorunlu maddeleri + 2 bonusu karşılar, gerekçe güçlü, deterministik, demo güvenli · Eksi: Kural ayarı zaman ister
Explainability: Çok güçlü · Demo değeri: Yüksek · Jüri etkisi: Yüksek · Karmaşıklık: Orta · Süre riski: Düşük-orta
C — AMBITIOUS: B + graf kümeleme/ML + LLM ajan
Yaklaşım: B'nin üstüne alarm benzerlik grafı + community detection (Louvain), embedding tabanlı örüntü eşleştirme, LLM ajanına kök neden muhakemesi
Artı: Wow potansiyeli, B3 bonusu · Eksi: networkx/sklearn kurulumu (ortam riski), açıklanabilirlik düşer, "neden bu küme?" sorusuna cevap zorlaşır, LLM demo riski, 3 saate sığmaz
Failure modes: Kümeleme E2/E3'ü birleştirir, LLM tutarsız hipotez üretir, demo yavaşlar
10 & 11 — SEÇİLEN ÇÖZÜM VE NEDENİ
➡️ B'yi yapıyoruz: "Dependency-Aware Alert Storm Correlator"

Neden B:

Puanlama doğrudan B'yi ödüllendiriyor. Dört resmi ölçütün üçü (kök isabeti, yanlış birleştirme, gürültü elemesi) bağımlılık + zaman + şiddet mantığıyla çözülür; C'nin ML katmanı bu üçünde ölçülebilir kazanç getirmez ama açıklanabilirliği düşürür — ki brifing açıkça gerekçeyi ödüllendiriyor.
Veri zaten temiz ve etiketsiz. Supervised ML yapılamaz; unsupervised kümeleme ise "neden bu küme" sorusuna cevap veremez. Kural tabanlı sistem her kararın gerekçesini kodun kendisinden üretir.
Ortam riski sıfıra iner. Stdlib ile çalışır; pandas/streamlit kurulumu tıkanırsa çekirdek etkilenmez.
X-Factor alanı B'de. "Karşı olasılıklar" ve "gürültü denetim görünümü" bonusları, ML değil muhakeme şeffaflığı istiyor.
A yetersiz: bağımlılık grafiğini kullanmadan gerekçe üretilemez ve E4 kaçar.
Uçtan uca akış
INPUT           alarms.json (3.000) + service_dependencies.csv (32) + host_inventory.csv (56)
   ↓
PREPROCESSING   normalize · host→servis→dc/rack eşleme · bağımlılık grafiği (yönlü) ·
                mesajdan sayısal sinyal çıkarımı (%100 dolu, HTTP 504, p99 ms)
   ↓
BASELINE        her (alarm_type) için dakika bazlı taban oran + zaman düzgünlüğü (cv)
   ↓
DETECTION       anomali pencereleri: (a) patlama = z-skor eşiği, (b) yavaş yayılma = hareketli
                ortalama artışı; pencereler boşlukla ayrılır
   ↓
CORRELATION     pencere içi alarmlar → olaylara ata: bağımlılık yakınlığı + host/rack/dc ortaklığı
                + zaman yakınlığı + tip uyumu skoru (ayrılma eşiği ile yanlış birleştirme koruması)
   ↓
ROOT CAUSE      kök adayı skoru = erkenlik × şiddet × downstream derinliği × tip önceliği
                (network_down/disk_full/ext_unreach gibi "kaynak" tipler > timeout/5xx "türev" tipler)
   ↓
EXPLANATION     WHAT / WHY / CONFIDENCE / SUPPORTING SIGNALS / COUNTER-HYPOTHESES
   ↓
ACTION          kök tipine göre önerilen ilk aksiyon + sahip (servis kritikliğinden) + durum
   ↓
METRIC          indirgeme oranı · kapsanan alarm % · gürültü % · baseline karşılaştırması
   ↓
OUTPUT/UI       olay kartı listesi (öncelik sıralı) → kart detayı → gürültü denetim sekmesi →
                aksiyon durumu değiştirme
   ↓
DEMO            3.000 satır → 8-12 kart → tek kartın gerekçesi → aksiyon aç/kapat → gürültü denetimi
   ↓
IMPACT          "7 dakikada okunabilir 8 karar" — müdahale sırası doğru kurulur
12 — TEKNİK BLUEPRINT
Karar	Seçim	Gerekçe
Dil	Python 3 (stdlib öncelikli)	Kurulu, ekipte bilinen, veri işleme doğal
Kütüphane (çekirdek)	json, csv, datetime, collections, statistics, re — sıfır dış bağımlılık	Kurulum riski yok, demo garantili
Kütüphane (opsiyonel)	pandas/matplotlib sadece grafiğe zaman kalırsa	README'de beyan
UI	Statik HTML + vanilla JS, backend http.server (stdlib) ile JSON servisi + aksiyon POST'u	Sıfır bağımlılık, canlı demo, aksiyon durumu bellek içi (brifing kabul ediyor)
UI alternatifi (paralel, timeboxed)	Streamlit — 10 dk kurulum timebox, başarısızsa bırak	Hız avantajı, ama çekirdeği bloklamaz
Backend/API	Küçük: /api/events, /api/noise, POST /api/actions/<id>	Z4/Z5 için yeterli
Database	Yok — bellek içi (brifing açıkça izin veriyor)	Kapsam dışı
LLM	Opsiyonel anlatı katmanı: kart gerekçesini doğal dile çevirir; yapılandırılmış JSON ister; deterministik şablon fallback	AI kullanımı beyanı + X-Factor, ama kritik yolda değil
Dış bağımlılık	Yok (LLM hariç, o da opsiyonel)	Demo riski sıfır
Çalıştırma	python3 -m src.main veya python3 src/app.py → tarayıcı localhost	Tek komut (Z6)

Overengineering yasakları: microservice yok, DB yok, auth yok, Docker yok, React yok, gerçek zamanlı akış yok, model eğitimi yok.

13 — AI/ML STRATEJİSİ
Yaklaşım	Neden / Neden değil	Metrik	Açıklanabilirlik	Süre	Risk
Kural + istatistik baseline ✅	Etiketsiz veri, açıklanabilirlik ödüllü. Çekirdek bu	İndirgeme, kapsam	Çok yüksek	Düşük	Düşük
Bağımlılık grafiği yayılımı ✅	32 kayıtlık graf = kök neden gerekçesinin omurgası	Zincir doğruluğu	Yüksek	Düşük	Düşük
Zaman serisi anomali (z-skor / hareketli ort.) ✅	Patlama + yavaş yayılma tespiti	Tespit sayısı	Yüksek	Düşük	Düşük
LLM (anlatı + karşı olasılık) ✅ opsiyonel	Doğal dil gerekçe = B1 bonusu, AI kullanım kanıtı	—	Orta (yapılandırılmış çıktı + kanıt bağlama)	Orta	Fallback ile düşük
Kümeleme (DBSCAN/Louvain) ❌	"Neden bu küme" cevaplanamaz, E2/E3 birleşme riski	—	Düşük	Orta	Yüksek
Supervised sınıflandırma ❌	Etiket yok	—	—	—	Uygulanamaz
Derin öğrenme ❌	3.000 satır, 3 saat, açıklanamaz	—	—	—	Uygulanamaz

Seçilen kombinasyon: İstatistiksel baseline + zaman anomali tespiti + graf tabanlı kök neden skorlaması + (opsiyonel) LLM anlatı katmanı.

14 — EXPLAINABILITY / X-FACTOR

Her kart şu dört alanı üretir:

WHAT        "dc1/rack-A ağ kesintisi — 7 servis etkilendi, 654 alarm, 01:42–01:55"
WHY         "01:42:13'te 12 network_down alarmı başladı; hepsi dc1/rack-A'da, 7 farklı host'ta.
             Aynı pencerede rack-A'dan 329 alarm geldi (rack-B 156, rack-C 160).
             Ardından bu host'lara bağımlı api-gateway, subscriber-service, mobile-bff
             servislerinde timeout ve http_5xx başladı (bağımlılık grafiği: 4 zincir)."
CONFIDENCE  0.87 — yüksek (tek rack'te yoğunlaşma + kaynak-tip alarmın türevlerden önce gelmesi)
SIGNALS     network_down×12 (sev5) · rack-A yoğunlaşma %51 · 4 bağımlılık zinciri · 13 dk pencere
COUNTER     "Alternatif: subscriber-db kaynaklı olabilir (aynı pencerede 36 alarm) — ancak
             ilk db alarmı 01:44:52, ağ alarmlarından 2,5 dk sonra. Zaman sırası bu hipotezi
             zayıflatıyor (güven 0.11)."

X-Factor önerimiz (3 katman, hepsi kanıtlanabilir ve demoda görünür):

"Karşı olasılık" paneli — her kartta reddedilen alternatif hipotez + neden reddedildiği (zaman sırası, lokalite, bağımlılık yönü). Sıradan bir korelatör bunu yapmaz. Brifing bunu açıkça istiyor.
Gürültü denetim görünümü — elenen her alarm için eleme sebebi ("cert_expiry, 120 dakikaya düzgün dağılmış, cv=0.72, hiçbir olay penceresiyle zamansal örtüşmüyor"). Jüri "gürültü elemesi" ölçütünü doğrudan burada görür.
Müdahale sırası — kartlar sadece listelenmez, iş kritikliği × etkilenen servis sayısı × şiddetle sıralanır: "Önce şuna bak" = mühendisin 7 dakikası.
15 — METRİKLER
Metrik	Ne ölçer	Nasıl hesaplanır	Jüriye nasıl gösterilir
İndirgeme oranı	Resmi ölçüt 1	kart sayısı / 3.000	Başlıkta rozet: "3.000 → 9 kart (%99,7)"
Kapsam	Tüm veri işlendi mi (Z1)	işlenen / toplam = 3.000/3.000	"3.000/3.000 alarm işlendi"
Olay kapsaması	Kartlara atanan alarm oranı	olaya atanan / toplam	Kart + gürültü = %100
Gürültü oranı	Resmi ölçüt 4	elenen / toplam (~%45-50 bekleniyor)	Denetim sekmesinde sayaç
Ayrım güvenliği	Resmi ölçüt 3 (yanlış birleştirme)	Kart içi zaman yayılımı + servis kümesi tutarlılığı; birleştirme eşiğine yakın çiftler ayrı raporlanır	"Birleştirilmeyen sınır vakalar: 2"
Baseline karşılaştırma	Değer kanıtı	Naif yöntem (5 dk pencere + servis bazlı gruplama) kaç kart üretiyor?	Tablo: Naif 180+ kart / Bizim 9 kart
Mühendis okuma süresi	İş değeri	3.000 satır ≈ okunamaz vs 9 kart ≈ ~2 dk	Sunumda tek cümle

⚠️ Uydurma metrik yasak: Kök neden isabetini ölçemeyiz (ground truth kapalı). "%X doğruluk" demeyeceğiz; "4 bağımsız olay tespit ettik, her biri için gerekçe üretiyoruz" diyeceğiz.

16 — UI / ÇIKTI TASARIMI

Tek sayfa, üç bölüm:

┌──────────────────────────────────────────────────────────────┐
│ ALERT STORM CORRELATOR   3.000 alarm → 9 olay kartı (%99,7 ↓)│
│ [Olay Kartları] [Gürültü Denetimi (1.412)] [Metrikler]       │
├──────────────────────────────────────────────────────────────┤
│ #1 🔴 KRİTİK  dc1/rack-A ağ kesintisi           654 alarm    │
│    01:42–01:55 · 7 servis · güven 0.87                       │
│    ▸ Kök: network_down (ao-003-api + 6 host, tümü rack-A)    │
│    ▸ Aksiyon: rack-A ToR switch/uplink kontrolü              │
│      Sahip: [Ağ Ekibi ▾]  Durum: [Açık ▾] → [Devam ▾]        │
│    [Gerekçeyi göster] [Karşı olasılıklar] [Alarmları listele]│
├──────────────────────────────────────────────────────────────┤
│ #2 🔴 KRİTİK  billing-db disk dolması           412 alarm ... │
│ #3 🟠 YÜKSEK  payment-provider-gw kesintisi     528 alarm ... │
│ #4 🟡 ORTA    batch çakışması → subscriber-db   ... │
└──────────────────────────────────────────────────────────────┘

Terminal fallback: Aynı kartları renkli tablo olarak basan CLI (--cli bayrağı). UI yetişmezse demo bununla yapılır.

17 — EKİP & AGENT ROUTING
Kişi	Görev	Input	Output	Bağımlılık	Merge
Kaptan (H. Eren Güçyener)	Kapsam, saat, karar, freeze yetkisi	Bu blueprint	Kararlar, zaman uyarıları	—	Sürekli
Backend & AI (Burhan Özdemirci)	Çekirdek korelasyon motoru + kök neden + gerekçe	alarms/deps/inventory	events.json (sözleşmeli)	Sözleşme	CP1 15:50, CP2 16:40
Frontend/UI (Ali Alperen Erkoç)	Kart UI + gürültü sekmesi + aksiyon durumu	Mock events.json	Çalışan arayüz	Sadece sözleşme	CP2 16:40
Entegrasyon & Belgeleme (Eren Eyüp Demir)	Çalıştırma akışı, README/AI_JURI/submission.json/docs, prompts/, screenshot, push	Commit'ler, kararlar	Teslim dokümanı	Sürekli	17:15

JSON sözleşmesi (15:00'te dondurulacak, herkes buna göre paralel çalışır):

{"events":[{"id","rank","severity_label","title","root_cause_hypothesis","why","confidence",
"counter_hypotheses":[{"text","confidence"}],"signals":[],"services":[],"hosts":[],
"alarm_count","time_start","time_end","suggested_action","owner","status","alarm_ids":[]}],
"noise":[{"alarm_id","reason"}],
"metrics":{"total_alarms","event_count","reduction_ratio","noise_count","coverage"}}

Agent kullanımı (minimum, gerekçeli):

python-pro → korelasyon motoru tasarım desteği (Backend ile, tek agent)
ui-designer veya frontend-developer → yalnızca kart UI'ı için, 1 agent
systematic-debugging → takılan bug olursa
Agent Teams kullanmıyoruz: 4 kişilik insan ekip zaten paralel, koordinasyon maliyeti 3 saatte kazançtan büyük
comprehensive-review → 17:00'de hafif, sadece kritik bulgular
/scribe mantığı → Entegrasyon kişisinde sürekli
18 — IMPLEMENTATION BACKLOG
P	#	Task	Sahip	Bağımlılık	Çıktı	Done kriteri
P0	1	Repo clone + push testi + data/ yerleşimi	Entegrasyon	—	Çalışan repo	push --dry-run OK
P0	2	JSON sözleşmesini dondur	Kaptan	—	Sözleşme	Herkes onayladı
P0	3	Veri yükleme + normalize + graf kurma	Backend	2	load.py	3.000 kayıt yüklü, referanslar bağlı
P0	4	Baseline + anomali penceresi tespiti	Backend	3	Pencere listesi	≥4 pencere, saatler beklenenle uyumlu
P0	5	Olay atama + yanlış birleştirme koruması	Backend	4	Olay grupları	≤15 kart, E2/E3 ayrı
P0	6	Kök neden skorlama + WHY metni	Backend	5	Kart alanları	Her kartta gerekçe
P0	7	Aksiyon önerisi + sahip + durum alanı	Backend	6	Kart tamam	Z4 karşılanıyor
P0	8	Gürültü etiketleme + eleme sebebi	Backend	4	noise[]	Her elenen alarmda sebep
P0	9	Kart listesi + detay UI	Frontend	2 (mock)	Çalışan sayfa	Kartlar görünüyor
P0	10	Aksiyon durumu değiştirme (canlı)	Frontend	9	Etkileşim	Durum Açık→Devam→Kapalı
P0	11	Tek komutla çalıştırma + README kurulum	Entegrasyon	3-10	README.md	Temiz clone'da çalışıyor
P0	12	AI_JURI.md + submission.json + docs/ + prompts/	Entegrasyon	Sürekli	Teslim dosyaları	Placeholder yok
P1	13	Karşı olasılık üretimi (B1)	Backend	6	counter_hypotheses	En az 1 alternatif/kart
P1	14	Gürültü denetim sekmesi (B2)	Frontend	8,9	Sekme	Sebepler filtrelenebilir
P1	15	Metrik paneli + baseline karşılaştırma	Backend+Frontend	5	Rozet + tablo	Sayılar gerçek
P1	16	Ekran görüntüleri demo/	Entegrasyon	9	3-5 PNG	X-Factor ilk karede
P1	17	LLM anlatı katmanı + fallback	Backend & AI	6	Doğal dil metin	LLM kapalıyken de çalışıyor
P2	18	Benzer geçmiş örüntü (B3)	Backend	5	Kart eki	Zaman kalırsa
P2	19	Zaman çizelgesi görseli	Frontend	9	Grafik	Zaman kalırsa
P2	20	Terminal CLI modu (yedek demo)	Backend	6	--cli	Fallback hazır
19 — ADIM ADIM EXECUTION PLAN
Sözleşme + iskelet (herkes aynı anda başlar, kimse kimseyi beklemez)
Backend: yükleme → baseline → pencere → atama → kök → gerekçe → gürültü (sırayla, her adım sonunda events.json yeniden üretilir)
Frontend: mock events.json ile UI'ı kurar, sözleşme değişmediği için entegrasyon anlık olur
Entegrasyon: ilk andan itibaren README + AI_JURI + prompts/ + docs/mimari.md doldurur
CP1'de (15:50) uçtan uca: veri → kartlar → ekranda görünüyor (çirkin olabilir)
CP2'de (16:40) gerekçe + karşı olasılık + gürültü sekmesi + aksiyon durumu tamam
Feature freeze 17:05 — sadece bug fix, screenshot, doküman
17:20 push freeze, 17:25 remote doğrulama
17:30–17:45 sözlü prova (repoya dokunulmaz)
20 — ZAMAN PLANI (kalan süreye göre)
Saat	Hedef	Çıktı
Şimdi–15:00	Repo/push doğrulama · sözleşme dondurma · rol teyidi · ortam (python3 stdlib yeterli)	İlk commit
15:00–15:50	Backend: yükleme→pencere→atama→kart · Frontend: mock UI · Doküman başlar	CP1: uçtan uca çalışan dikey dilim (15:50)
15:50–16:40	Kök neden skoru + WHY + gürültü sebebi + aksiyon durumu + entegrasyon	CP2: demo edilebilir MVP (16:40)
16:40–17:05	Karşı olasılık, metrik paneli, gürültü sekmesi, screenshot, LLM katmanı (varsa)	Feature freeze 17:05
17:05–17:20	README/AI_JURI/submission.json/docs, temiz clone testi	Doküman freeze 17:20
17:20	PUSH FREEZE	Son commit
17:25	git log origin/main -1 doğrulama	Teslim teyidi
17:30	HARD STOP	—
17:30–17:45	Ara + sesli prova	Demo hazır

⚠️ 15:00-15:30 kurabiye, 17:00-17:30 pizza — masada nöbetçi kalır, ikram sırayla alınır.

IF BEHIND SCHEDULE — kesme sırası:

B3 geçmiş örüntü → kes
Zaman çizelgesi görseli → kes
LLM anlatı katmanı → deterministik şablona düş
Gürültü denetim sekmesi → gürültü sebebini kart altında göster (veri yine üretilsin)
Karşı olasılık → tek cümlelik sabit alternatif
Web UI → terminal CLI moduna düş (demo canlı çalışır, kabul kriteri karşılanır)
ASLA kesilmeyecek: tüm veriyi işleme, ≤15 kart, kart gerekçesi, aksiyon+sahip+durum, README/AI_JURI, push
21 — TEST / VALIDATION PLAN
Test	Acceptance criteria
Veri bütünlüğü	len(alarms)==3000, benzersiz id 3000, hiçbir kayıt drop edilmiyor
Kapsam	Kartlardaki alarm sayısı + gürültü sayısı = 3.000 (kayıp yok, çift sayım yok)
Kart sınırı	len(events) <= 15 (hedef 8-12)
Kart bütünlüğü	Her kartta 4 zorunlu alan + aksiyon + sahip + durum dolu
Ayrım testi	E2 (billing-db) ve E3 (payment-gw) ayrı kartlarda; hiçbir kart 30 dk'dan uzun yayılmıyor (E4 hariç, bilinçli)
Determinizm	Aynı girdi 2 kez → aynı çıktı (LLM kapalıyken byte-aynı)
Sıfırdan ayağa kalkma	Temiz clone + python3 ... → 30 sn içinde sonuç
UI smoke	Kart açılıyor, gerekçe görünüyor, gürültü sekmesi doluyor
Aksiyon akışı	Durum Açık→Devam→Kapalı değişiyor ve ekranda kalıcı
Edge case	Boş pencere, tek alarmlık olay, tüm alarmlar gürültü senaryosunda çökmüyor
Fallback	LLM kapalı/erişimsizken uygulama tam çalışıyor
Reproducibility	README'deki komut birebir çalışıyor (3. kişi denemeli)
22 — DEMO BLUEPRINT (2,5–3 dk, 7 dk sahnenin içinde)
Süre	Ekranda	Söylenen
0:00–0:20	Ham alarms.json / terminal akışı	"Saat 02:14. Nöbetçi mühendisin ekranı bu: 3.000 satır, 2 saat."
0:20–0:35	Tek komut çalışır, kartlar belirir	"Tek komut. 3.000 alarm → 9 karar." ⭐ WOW ANI
0:35–1:20	Kart #1 detayı açılır	"En kritik olay: dc1 rack-A ağ kesintisi. Neden böyle diyoruz: 12 network_down alarmı, hepsi tek rack'te, türev timeout'lardan 2 dakika önce." ⭐ XAI
1:20–1:45	Karşı olasılık paneli	"Alternatif hipotez de üretiyoruz: subscriber-db olabilir miydi? Hayır, çünkü ilk db alarmı 2,5 dk sonra geldi." ⭐ X-FACTOR
1:45–2:05	Aksiyon: sahip ata, durum değiştir	"Aksiyonu açıyorum, Ağ Ekibine atıyorum, durumu Devam'a çekiyorum — izlenebilir." (Z5)
2:05–2:25	Gürültü denetim sekmesi	"1.400 alarmı eledik ve neden elediğimizi gösteriyoruz: cert_expiry 2 saate düzgün dağılmış, hiçbir olayla örtüşmüyor." ⭐ BONUS
2:25–2:45	Metrik paneli	"3.000/3.000 işlendi. %99,7 indirgeme. Naif yöntem 180 kart üretirdi, biz 9."

Fallback demo: (1) UI çökerse --cli terminal modu, (2) o da olmazsa demo/ ekran görüntüleri sırayla + kod dosya:satır gösterimi. Uygulama sahneye çıkmadan önce zaten ayakta bekler (kura anlık).

23 — SUNUM BLUEPRINT (7 dk + 3 dk Q&A)
#	Bölüm	Söylenecek ana cümle	Süre
1	Problem	"Gece 02:14'te sorun alarm sayısı değil; hangisinin neden, hangisinin sonuç olduğunun görünmemesi."	0:40
2	Neden önemli	"Yanlış müdahale sırası, çözüm süresini doğrudan uzatıyor. Mühendisin 7 dakikası var."	0:30
3	Veri içgörüsü	"Veriye baktık: 25 alarm tipinin 7'si 2 saate düzgün dağılmış taban gürültü. Gerçek olaylar zamanda yoğunlaşıyor ve bağımlılık zinciri boyunca yayılıyor."	0:40
4	Çözüm	"Bağımlılık farkında bir korelasyon motoru: 3.000 alarmı gerekçeli 9 olay kartına indiriyor."	0:30
5	Nasıl çalışıyor	"Baseline → anomali penceresi → bağımlılık + lokalite ile gruplama → kök neden skoru → gerekçe."	0:50
6	Demo	(canlı)	2:30
7	Metrik	"3.000/3.000 işlendi, %99,7 indirgeme, naif yöntem 180 kart üretiyor."	0:30
8	AI kullanımımız	"Kararı kural motoru veriyor, AI anlatıyı üretiyor. Hangi kararı insan verdi, hangisini AI — repoda prompts/ altında kayıtlı."	0:30
9	X-Factor	"Sadece 'ne' değil, 'neden bu, neden şu değil'i de söylüyoruz. Karşı olasılık üreten tek çözüm biziz."	0:30
10	Sınırlar + sonraki adım	"Ground truth kapalı olduğu için isabeti biz ölçemedik. Eşikler bu pencereden türetildi, farklı ortamda kalibrasyon ister."	0:30

Q&A hazırlığı: "AI gerçekten gerekli miydi?" → "Karar için değil, açıklama için. Kural motoru deterministik ve savunulabilir; AI onu mühendisin okuyacağı dile çeviriyor." · "Kaç olay olduğunu nereden biliyorsunuz?" → "Bilmiyoruz; sabit sayı yok, eşik veriden türetiliyor." · "Ölçeklenir mi?" → "Tek geçişli, O(n log n); 3.000 alarm saniyeler içinde."

24 — FAILURE / FALLBACK PLAN
Senaryo	Plan B
Push çalışmıyor	Yetkili diğer üyeden push; 17:10'a kadar çözülmezse kaptan GitHub web arayüzünden yükler
UI yetişmiyor	--cli terminal modu (kabul kriterleri yine karşılanır)
LLM/SAKA yok	Deterministik şablon gerekçe; AI kullanımı promptlarla belgelenir
Kural motoru 15 karttan fazla üretiyor	Eşiği sıkılaştır + en düşük öncelikli kartları "diğer" kartında topla
E2/E3 birleşiyor	Zaman boşluğu eşiğini düşür, kök tipi imzasını zorunlu kıl
pandas/streamlit kurulmuyor	Zaten stdlib planı; kurulum denemesini bırak
Demo çöküyor	demo/ screenshot'ları + önceden üretilmiş events.json
16:40'ta MVP yok	Kart üretimi + terminal çıktısı + gerekçe; UI ve bonuslar kesilir
17:05'te bug var	15 dk kuralı: çözülmezse o yolu kapat, "bilinen sınırlar"a yaz
25 — SUBMISSION CHECKLIST (17:05–17:20)
 3.000/3.000 alarm işleniyor, ≤15 kart üretiliyor
 Her kartta: kök neden hipotezi + gerekçe + etkilenen servisler + alarm sayısı + zaman aralığı
 Her kartta: önerilen ilk aksiyon + sahip + durum
 En az bir aksiyon demoda açılıp durumu değiştirilebiliyor (opsiyonel ama değerli)
 Temiz clone + tek komut → 30 sn içinde sonuç (3. kişi test etti)
 README.md: kurulum, çalıştırma komutu, kullanılan AI araçları + model sürümleri, MCP listesi, kullanılan açık kaynak kütüphaneler, ekran görüntüleri, bilinen sınırlar
 docs/: plan.md, fazlar.md, mimari.md (şu an boş — doldurulacak)
 .env.example güncel · CLAUDE.md dolu
 AI_JURI.md: 5 bölüm, her iddiada dosya:satır kanıtı
 submission.json: geçerli JSON, x_factor + olctugumuz_metrikler + demo_akisi dolu
 prompts/: kritik promptlar (amaç/prompt/sonuç/insan müdahalesi)
 demo/: 3-5 ekran görüntüsü, X-Factor ilk karelerde
 Repo public, secret yok, .env commit edilmemiş
 17:20 push freeze · 17:25 git log origin/main -1 doğrulandı
26 — İLK YAPACAĞIMIZ 10 İŞLEM
Repo clone + push yetkisi doğrula (push --dry-run) — dünkü açık blocker, her şeyden önce
Veri paketini repodaki data/ altına koy (sentetik veri, commit edilebilir)
JSON sözleşmesini dondur (§17) — Backend ve Frontend'i birbirinden ayırır
Rol teyidi + 17:20 push freeze sahibi ilan et + alarmları kur (15:50 / 16:40 / 17:05 / 17:20)
Backend: veri yükleme + bağımlılık grafiği + host/rack eşlemesi
Frontend: mock events.json ile kart listesi iskeleti
Entegrasyon: docs/mimari.md + CLAUDE.md + prompts/01-*.md ilk doldurma, ilk commit + push
Backend: baseline gürültü profili + anomali pencere tespiti
Backend: olay atama + kök neden skorlama → ilk gerçek events.json
15:50 CP1 kontrolü: veri → kartlar → ekranda görünüyor mu? Görünmüyorsa kesme listesine geçs