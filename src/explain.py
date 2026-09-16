"""Aciklanabilirlik katmani — LLM anlatisi + deterministik sablon fallback.

LLM kritik yolda DEGILDIR. Anahtar yoksa, ag yoksa veya servis hata verirse
uygulama tam calismaya devam eder; sablon metni her zaman uretilir.
"""

import json
import os
import urllib.error
import urllib.request

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TIMEOUT_SEC = 20

SYSTEM_PROMPT = (
    "Sen bir SRE nobetci muhendisine yardim eden bir operasyon asistanisin. "
    "Sana bir olay kartinin hesaplanmis kanitlari verilecek. "
    "Bu kanitlari 3-4 cumlelik, sade Turkce bir anlatiya cevir. "
    "KURALLAR: Sadece verilen kanitlari kullan, yeni sayi veya servis adi uydurma. "
    "Kesinlik iddia etme; bu bir hipotezdir. Karsi olasiligi da bir cumleyle belirt. "
    "Teknik jargonu minimumda tut."
)


def load_env():
    env = {}
    path = os.path.join(ROOT_DIR, ".env")
    if os.path.isfile(path):
        with open(path, "r", encoding="utf-8") as fh:
            for line in fh:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    key, value = line.split("=", 1)
                    env[key.strip()] = value.strip()
    for key in ("AZURE_OPENAI_ENDPOINT", "AZURE_OPENAI_API_KEY", "AZURE_OPENAI_MODEL"):
        if os.environ.get(key):
            env[key] = os.environ[key]
    return env


def template_narrative(card):
    """LLM olmadan da her zaman calisan deterministik anlati."""
    parts = [
        "%s: %s." % (card["severity_label"], card["title"]),
        card["why"],
        "Onerilen ilk aksiyon: %s (%s)." % (card["suggested_action"], card["owner"]),
    ]
    if card.get("counter_hypotheses"):
        parts.append(card["counter_hypotheses"][0]["text"])
    parts.append("Bu bir hipotezdir; guven %.2f (kalibre edilmemis, kanit gucune dayali)." % card["confidence"])
    return " ".join(parts)


def build_prompt(card):
    evidence = {
        "baslik": card["title"],
        "kok_neden_hipotezi": card["root_cause_hypothesis"],
        "gerekce": card["why"],
        "sinyaller": card["signals"],
        "etkilenen_servisler": card["services"],
        "alarm_sayisi": card["alarm_count"],
        "zaman_araligi": "%s - %s" % (card["time_start"], card["time_end"]),
        "guven": card["confidence"],
        "karsi_olasilik": [c["text"] for c in card.get("counter_hypotheses", [])],
        "onerilen_aksiyon": card["suggested_action"],
    }
    return (
        "Asagidaki olay kartini nobetci muhendise anlat:\n\n"
        + json.dumps(evidence, ensure_ascii=False, indent=2)
    )


def narrate(card):
    """(metin, kaynak) dondurur. kaynak: 'llm' veya 'sablon'."""
    env = load_env()
    endpoint = env.get("AZURE_OPENAI_ENDPOINT", "")
    api_key = env.get("AZURE_OPENAI_API_KEY", "")
    model = env.get("AZURE_OPENAI_MODEL", "claude-sonnet-4-5")

    if not endpoint or not api_key:
        return template_narrative(card), "sablon"

    base = endpoint.split("/openai/")[0].rstrip("/")
    url = base + "/anthropic/v1/messages"
    body = json.dumps({
        "model": model,
        "max_tokens": 400,
        "system": SYSTEM_PROMPT,
        "messages": [{"role": "user", "content": build_prompt(card)}],
    }).encode("utf-8")

    request = urllib.request.Request(url, data=body, headers={
        "Content-Type": "application/json",
        "x-api-key": api_key,
        "anthropic-version": "2023-06-01",
    })
    try:
        with urllib.request.urlopen(request, timeout=TIMEOUT_SEC) as response:
            data = json.load(response)
        blocks = data.get("content", [])
        text = " ".join(b.get("text", "") for b in blocks if b.get("type") == "text").strip()
        if text:
            return text, "llm"
        return template_narrative(card), "sablon"
    except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError, OSError, ValueError):
        # Demo tek bir API hatasi yuzunden bozulmaz
        return template_narrative(card), "sablon"


if __name__ == "__main__":
    import sys
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    import correlator
    result = correlator.run(os.path.join(ROOT_DIR, "data", "katilimci_paketi"))
    text, source = narrate(result["events"][0])
    print("[kaynak: %s]\n%s" % (source, text))
