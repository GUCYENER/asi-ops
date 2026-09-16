# JSON sözleşmesi — sürüm 1.1

Onaylanan kapsam: `BUTUNLESIK_ANALIZ.md`. Çekirdek deterministiktir; LLM yalnızca isteğe bağlı anlatı üretir.

## Uçlar

- `GET /api/report`: `schema_version`, `summary`, `incidents[]`, **`uncertain[]`**, `review_candidates[]`, `settings`, `baseline`, `quality`, `timeline`, `limitations`.
- `GET /api/alarms?decision=incident|noise|uncertain&incident_id=...&q=...&offset=0&limit=50`: filtrelenmiş alarm kayıtları ve toplamı. `incident_id`, olay veya inceleme kartının kimliği olabilir. Limit üst sınırı 200.
- `GET /api/export`: bütün olaylar, aksiyonlar ve alarm→karar eşlemesi (JSON).
- `POST /api/incidents/{id}/action`: `owner`, `status`, `note`, `version`; sürüm çakışması 409.
- `POST /api/incidents/{id}/narrative`: isteğe bağlı, doğrulanan LLM anlatısı veya şablon geri dönüşü.

## Olay kartı

`id`, `title`, `kind`, `root` (scope/service/location/hypothesis/score/factors), `start`, `end`, `alarm_count`, `services` (gözlenen), `potential_services` (grafik), `priority`, `confidence` (kanıt düzeyi), `evidence`, `explanation`, `alternatives`, `action`, `timeline`.

`action`: `owner` (atanmış sorumlu rolü; kişi bilgisi değildir), `owner_kind`, `status` (`open`, `investigating`, `resolved`), `recommendation`, `history`, `version`.

## Alarm kararı

Özgün alanlar + `decision`, `incident_id` veya null, `reason`, `evidence_codes`, `candidate_scores`, `message_target`, `target_relation`, `concentration_ratio`.

Her kimlik tek birincil karara sahiptir. `assigned_count + noise_count + uncertain_count = input_count`. Gürültü etiketleri adaydır; gerçek doğruluk bilinmiyor. Kart sayısı zorla sınırlandırılmaz; olay + inceleme kartı toplamı 15'i aşarsa kabul kontrolü başarısız gösterilir.

## Açık belirsizlik sözleşmesi

- `uncertain[]`: belirsiz karar verilmiş alarm kayıtlarının tamamı, boşsa `[]`. Tam rapordaki `alarms[]` dizisinin belirsiz alt kümesinin erişim görünümüdür; iki dizi toplanarak sayılmaz.
- `review_candidates[]`: belirsizlerden türeyen düşük kanıtlı inceleme kartları. `card_type=review`, `confidence.level=düşük`, `root.score=null`, `review_alarm_ids[]`, `linked_incident_ids[]`, `message_targets` içerir.
- İnceleme kartına alınan kayıt **belirsiz sınıfında kalır**; yeni bağımsız olay veya olaya atanmış kayıt sayılmaz. Alarm kaydında `review_candidate_id` bulunur.
- `summary.total_card_count = incident_count + review_candidate_count`. Kabul sınırı toplam kart üzerinden denetlenir.
- `incidents[]`, önceki dış taslaklardaki `events[]` alanının uygulamadaki karşılığıdır. Gürültü API filtresinden ve tam rapordaki `alarms[]` kararlarından okunur.
- Olay kartında `direct_hosts[]` yalnız kök imzası bulunan host'ları, `hosts[]` ilişkili alarm bulunan bütün host'ları gösterir. İki sayı birbirinin yerine kullanılmaz.
- `evidence_checks[]` hesaplanan kısa kanıt listesi; `memory_trend[]` tüm host/yüzde öncülleri; `dependency_evidence[]` hedef bağlantıları ve doğrulanamayan yolları içerir.
- `settings.external_tail_minutes` varsayılan 22; son dış servis kök sinyalinden itibaren aday kuyruğu. `--external-tail-minutes` veya `EXTERNAL_TAIL_MINUTES` ile değişir; olayın bitişi son atanmış alarmdan gelir.

## Alarm seviyesinde atama

Zaman penceresi yalnızca aday daraltır. Her kayıt için servis, uyumlu alarm ailesi, yönlü bağımlılık, mesaj hedefi, fiziksel konum ve yerel tekrar birlikte puanlanır. Yakın puanlı iki aday varsa kayıt belirsiz kalır. Farklı alarm tipleri ortak köke bağlanabilir; aynı tipte olmak tek başına ortak olay anlamına gelmez.

Aksiyonlar her iki kart türünde de geçerlidir. `open → investigating → resolved`, yeniden açma `resolved → open`; çözüm kaydı için not zorunlu. Eski sürümle güncelleme 409 döndürür.

## Uygulama notları

- Gözlem penceresi dosyadan türetilir; olay sayısı, servis adları, alarm kimlikleri ve tarihler sabitlenmez.
- Yoğunlaşma: eşit 10 dakikalık dilimlerde `tepe / max(medyan, 1)`. Sıfır medyan düzeltmesi görünürdür.
- Düşük yoğunlaşma tek başına gürültü kararı değildir; olay bağlamı, yerel sıklık ve trend kontrol edilir.
- Kritikliği yüksek servis, gerçek insan sahibinin kim olduğunu söylemez; başlangıçta düzenlenebilir nöbetçi rolü atanır.
- Eylem çözülmesi manuel durum kaydıdır; veri clear/recovery içermediğinden fiziksel arıza çözümü doğrulanmış sayılmaz.
- Altın etiketler yok; kesin kök doğruluğu veya gürültü precision değeri raporlanmaz.
- Bütünleşik belgede yazan API erişimi bu oturumda henüz doğrulanmadı; çekirdek API olmadan çalışır.
