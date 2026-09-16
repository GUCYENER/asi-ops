#!/usr/bin/env python3
"""Alert Storm Correlator — tek komutluk giris noktasi.

Kullanim:
    python run.py                      # arayuzu baslatir (http://localhost:8000)
    python run.py --cli                # terminal modu (yedek demo)
    python run.py --data <klasor>      # farkli veri klasoru
"""

import os
import sys

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(BASE_DIR, "src"))

DEFAULT_DATA = os.path.join(BASE_DIR, "data", "katilimci_paketi")


def main():
    args = sys.argv[1:]
    data_dir = DEFAULT_DATA
    if "--data" in args:
        data_dir = args[args.index("--data") + 1]

    if not os.path.isdir(data_dir):
        print("HATA: veri klasoru bulunamadi: %s" % data_dir)
        print("Kullanim: python run.py --data <katilimci_paketi klasoru>")
        return 1

    if "--cli" in args:
        import correlator
        result = correlator.run(data_dir)
        metrics = result["metrics"]
        print("=" * 78)
        print("ALERT STORM CORRELATOR  |  %d alarm -> %d olay karti (%%%.2f indirgeme)"
              % (metrics["total_alarms"], metrics["event_count"], metrics["reduction_ratio"] * 100))
        print("Gurultu: %d  |  Belirsiz: %d  |  Hesap verilen: %d/%d"
              % (metrics["noise_count"], metrics["unclear_count"],
                 metrics["accounted"], metrics["total_alarms"]))
        print("=" * 78)
        for card in result["events"]:
            print("\n[%s] #%d  %s   (%s, %d alarm, guven %.2f)"
                  % (card["id"], card["rank"], card["title"], card["severity_label"],
                     card["alarm_count"], card["confidence"]))
            print("  Zaman   : %s - %s" % (card["time_start"], card["time_end"]))
            print("  Kok     : %s" % card["root_cause_hypothesis"])
            print("  Servisler: %s" % ", ".join(card["services"]))
            print("  Neden   : %s" % card["why"])
            if card["counter_hypotheses"]:
                print("  Karsi   : %s" % card["counter_hypotheses"][0]["text"])
            print("  Aksiyon : %s" % card["suggested_action"])
            print("  Sahip   : %s  |  Durum: %s" % (card["owner"], card["status"]))
        return 0

    os.environ.setdefault("PORT", "8000")
    import server
    sys.argv = [sys.argv[0], data_dir]
    server.main()
    return 0


if __name__ == "__main__":
    sys.exit(main())
