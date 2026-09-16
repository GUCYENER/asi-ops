#!/usr/bin/env python3
"""Run: python3 app.py --data-dir ../katilimci_paketi"""
from pathlib import Path
import argparse
import json
import os
import sys

from src.engine import analyze
from src.server import make_server

ROOT = Path(__file__).resolve().parent


def load_env(path):
    if not path.exists():
        return
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        key, sep, value = line.partition("=")
        if sep and key.strip().replace("_", "").isalnum():
            os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))


def main():
    load_env(ROOT / ".env")
    parser = argparse.ArgumentParser(description="ASI-OPS · Alarm Fırtınası")
    parser.add_argument("--data-dir", type=Path, default=os.getenv("DATA_DIR") or ROOT.parent / "katilimci_paketi")
    parser.add_argument("--port", type=int, default=int(os.getenv("PORT", "8000")))
    parser.add_argument("--external-tail-minutes", type=float, default=float(os.getenv("EXTERNAL_TAIL_MINUTES", "22")))
    parser.add_argument("--export", type=Path, help="JSON raporunu yaz ve çık; sunucu gerekmez.")
    args = parser.parse_args()
    try:
        report = analyze(args.data_dir, external_tail_minutes=args.external_tail_minutes)
        summary = report["summary"]
        print(f"{summary['input_count']} alarm → {summary['incident_count']} olay adayı | "
              f"{summary['noise_count']} gürültü adayı | {summary['uncertain_count']} belirsiz | {summary['elapsed_ms']} ms")
        if args.export:
            args.export.parent.mkdir(parents=True, exist_ok=True)
            args.export.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
            print("Rapor yazıldı: " + str(args.export))
            return 0
        server = make_server(report, port=args.port)
        print(f"Operasyon masası: http://127.0.0.1:{server.server_port}", flush=True)
        print("Aksiyonlar bellekte tutulur; JSON dışa aktarımıyla kaydedebilirsiniz.", flush=True)
        try:
            server.serve_forever()
        except KeyboardInterrupt:
            pass
        finally:
            server.server_close()
        return 0
    except (ValueError, OSError) as exc:
        print("Başlatılamadı: " + str(exc), file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
