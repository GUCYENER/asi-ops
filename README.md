# asi-ops

> ⚠️ Bu repo şu an bir **iskelet** aşamasındadır. Aşağıdaki başlıklar hackathon başvurusundan önce doldurulmalıdır.

## Proje Adı ve Özet
**asi-ops** — *[tek cümlelik özet buraya]*

## Çözdüğümüz Problem
*[Hangi problemi, kimin için, neden çözdüğünüzü buraya yazın]*

## Çözümümüzün Nasıl Çalıştığı
*[Yüksek seviye mimari / akış açıklaması. Detay için bkz. [docs/mimari.md](docs/mimari.md)]*

## Kurulum Adımları
```bash
git clone https://github.com/GUCYENER/asi-ops.git
cd asi-ops
cp .env.example .env
# [bağımlılık kurulum komutları buraya]
```

## Çalıştırma Komutu
```bash
# [projeyi çalıştıran tek komut buraya]
```

## Kullanılan AI Araçları ve Model Sürümleri
| Araç | Model / Sürüm | Kullanım Amacı |
|------|----------------|-----------------|
| *[örn. Claude Code]* | *[örn. claude-sonnet-5]* | *[kodlama / analiz / açıklama]* |

## MCP Sunucu Listesi
- *[kullanılan MCP sunucuları buraya]*

## Entegre Edilen API'ler
- *[kullanılan üçüncü parti API'ler buraya]*

## Ekran Görüntüleri
*[bkz. [demo/](demo/) klasörü]*

## Deploy URL ve Bilinen Sınırlar
- **Deploy URL:** *[opsiyonel — deploy zorunlu değil, yerel çalışan ürün yeterli. Varsa buraya]*
- **Bilinen sınırlar:** *[neyi yapamadık, neden — bkz. [AI_JURI.md](AI_JURI.md) Bölüm 5]*

## Proje Yapısı
```
asi-ops/
├── README.md                # bu dosya
├── AI_JURI.md                # AI Jüri için yapılandırılmış özet
├── submission.json           # makine okunabilir künye
├── .env.example               # örnek ortam değişkenleri
├── CLAUDE.md                  # AI yapılandırma
├── docs/                      # plan.md, fazlar.md, mimari.md
├── prompts/                   # kullanılan kritik prompt'lar
├── demo/                      # ekran görüntüleri, video linki
└── src/                       # kaynak kod
```
