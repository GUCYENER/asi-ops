# asi-ops — AI Yapılandırma

Bu dosya, bu repoda çalışan AI ajanları (Claude Code vb.) için proje bağlamını ve kurallarını tanımlar. AI Jüri, ekibin AI'ı nasıl yönlendirdiğini değerlendirirken bu dosyayı referans alır.

## Proje Bağlamı
*[asi-ops'un ne yaptığına dair 2-3 cümlelik özet]*

## Kullanılan AI Araçları
- **SAKA** — şirketin çoklu LLM erişim platformu, bu hackathon'un birincil AI ortamı. IDE entegrasyonu ve konsol seviyesi erişim mevcut. Hangi model(ler) kullanıldıysa adı+sürümü burada ve `submission.json > ai_kullanimi.modeller`'da belirtilmeli.
- *[SAKA dışında kullanılan diğer araçlar — kısıt yok, ama kullanılan her araç burada beyan edilmeli]*

## Açıklanabilirlik (XAI) Kuralı
Çözüm bir karar üretiyorsa (sınıflandırma, öncelik sıralaması, anomali işaretleme vb.), o kararın **gerekçesini de üretmesi zorunlu** — AI Jüri'nin en çok önemsediği başlıklardan biri budur. "Sonuç: X" yetmez, "Sonuç: X, çünkü Y" gerekir.
- *[hangi modül/fonksiyon açıklanabilirlik çıktısı üretiyor — dosya yolu]*

## İnsan / AI İş Bölümü
- **İnsan kararı:** *[mimari kararlar, kapsam, öncelik sıralaması vb.]*
- **AI kararı / üretimi:** *[boilerplate kod, test yazımı, dokümantasyon taslağı vb.]*

## Kod Standartları ve Kısıtlar
- *[dil/framework tercihleri, klasör yapısı kuralları]*
- *[yapılmaması gerekenler]*

## Kritik Prompt'lara Referans
Bu projede kullanılan önemli prompt'lar [prompts/](prompts/) klasöründe saklanır.
