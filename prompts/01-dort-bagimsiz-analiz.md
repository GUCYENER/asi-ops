# 01 — Dört Bağımsız Analiz Stratejisi

## Amaç

Senaryo açıldığında (14:20) tek bir AI oturumuna güvenmek yerine, ekibin 4 üyesinin **birbirinden habersiz** aynı veriyi analiz etmesi. Amaç: tek bir modelin kör noktasına takılmamak ve yakınsama varsa kararı güçlendirmek.

## Kullanılan prompt kalıbı (her üye kendi aracında)

```
MODE: ANALYSIS_ONLY
STRICT RULE — NO IMPLEMENTATION

Bu aşamada sadece ANALİZ yap. Kod yazma, dosya değiştirme, commit atma.

~/katilimci_paketi içindeki resmi hackathon materyallerinin tamamını read-only incele.

1. Case'i uçtan uca açıkla: gerçek problem, hedef kullanıcı, input, beklenen output,
   zorunlu requirement'lar, opsiyonel alanlar, kapsam dışı, jüri neyi değerlendirecek
2. Dataset'i read-only profille: şema, row count, missing, duplicate, leakage riski,
   class imbalance, timestamp alanları
3. Her kritik bilgiyi FACT / INFERENCE / ASSUMPTION / UNKNOWN olarak etiketle
4. En az 2 gerçekçi çözüm alternatifi üret (A güvenli / B iddialı), puanla, gerekçeli öner
5. Kaynakta olmayan requirement UYDURMA

Sonunda implementation'a geçme, benden açık komut bekle.
```

## Neden bu kalıp

- **`ANALYSIS_ONLY` kilidi:** İlk 15 dakikada kod yazmaya başlamak, yanlış mimariyi hızlıca inşa etmek demektir. Kilit, analizin bitmesini zorunlu kıldı.
- **FACT/INFERENCE/ASSUMPTION/UNKNOWN etiketlemesi:** Hangi bilginin doğrulanmış, hangisinin yorum olduğunu ayırdı. Bu ayrım daha sonra AI_JURI.md'deki "kanıtsız iddia yok" disiplinine dönüştü.
- **"Kaynakta olmayan requirement uydurma":** Modellerin eksik bilgiyi doldurma eğilimini bastırdı.

## Sonuç

| Üye | Çıktı | Diğerlerinde olmayan katkı |
|---|---|---|
| Ali Alperen Erkoç (Codex) | [data/alperen_analiz.md](../data/alperen_analiz.md) | 5. olayı (session-service bellek) yakaladı; `message` alanının hedef servisi içerdiğini buldu |
| Eren Eyüp Demir | [data/eren_eyup.md](../data/eren_eyup.md) | Execution blueprint, kök neden skorlama formülü, checkpoint disiplini |
| Burhan Özdemirci | [data/BURHANCOZUM.md](../data/BURHANCOZUM.md) | Bağımsız A/B doğrulaması, kabul testi önerisi |
| Kaptan oturumu (Claude Code) | [data/BUTUNLESIK_ANALIZ.md](../data/BUTUNLESIK_ANALIZ.md) | Zamansal yoğunlaşma oranıyla objektif gürültü ayrımı |

**Dördü de bağımsız olarak "deterministik korelasyon motoru, ML kümeleme değil" dedi.** Bu yakınsama, kararı tek bir analizden çok daha güvenilir kıldı.

## İnsan müdahalesi

Kaptan, dört analizi çakıştırıp çelişkileri çözdü:
- **Olay sayısı 4 mü 5 mi?** → Alperen'in 5. olayı doğru; kaptan oturumunun `gc_pressure`/`oom_risk` sinyallerini yanlış pencereye atadığı tespit edildi.
- **pandas mı stdlib mi?** → Jürinin makinesi bilinmiyor, stdlib-only seçildi.
