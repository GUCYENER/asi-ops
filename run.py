#!/usr/bin/env python3
"""Alert Storm Correlator — tek komutluk giris noktasi.

    python run.py                    # operasyon masasini baslatir
    python run.py --data-dir <yol>   # farkli veri klasoru
"""
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

if __name__ == "__main__":
    if not any(a.startswith("--data-dir") for a in sys.argv[1:]):
        sys.argv += ["--data-dir", str(ROOT / "data" / "katilimci_paketi")]
    from app import main
    sys.exit(main())
