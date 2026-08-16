#!/usr/bin/env python3
"""Yeni video projesi iskeleti olusturur.

    python scripts/yeni.py balina-kalbi
    python scripts/yeni.py balina-kalbi --sahne 8
"""
import argparse
import json
import sys
from pathlib import Path

KOK = Path(__file__).resolve().parent.parent
PROJELER = KOK / "projeler"


def main():
    ayristirici = argparse.ArgumentParser(description="Yeni proje iskeleti")
    ayristirici.add_argument("slug", help="proje klasor adi, ornek: balina-kalbi")
    ayristirici.add_argument("--sahne", type=int, default=7, help="sahne sayisi (varsayilan 7)")
    ayristirici.add_argument("--sure", type=int, default=42, help="hedef toplam sure (sn)")
    argumanlar = ayristirici.parse_args()

    proje = PROJELER / argumanlar.slug
    plan_yolu = proje / "plan.json"
    if plan_yolu.exists():
        sys.exit(f"zaten var: {plan_yolu}")

    sahne_suresi = max(4, round(argumanlar.sure / argumanlar.sahne))
    plan = {
        "slug": argumanlar.slug,
        "baslik": "",
        "hook": "",
        "hedef_sure": argumanlar.sure,
        "etiketler": ["#hayvanlar", "#ilginçbilgiler", "#shorts"],
        "_not": "ara[] terimleri INGILIZCE (MCP aramasi icin). klipler[] MCP ile secildikten "
                "sonra doldurulur, sonra: python scripts/indir.py --proje <slug>",
        "text": [],
        "sahneler": [
            {"no": i, "sure": sahne_suresi, "anlatim": "", "ara": [], "klipler": []}
            for i in range(1, argumanlar.sahne + 1)
        ],
    }

    (proje / "footage").mkdir(parents=True, exist_ok=True)
    plan_yolu.write_text(json.dumps(plan, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"olusturuldu: {plan_yolu}")
    print("Sonraki: plan.json'daki anlatim + ara terimlerini doldur,")
    print("         MCP ile klipleri sec, sonra: python scripts/indir.py --proje " + argumanlar.slug)


if __name__ == "__main__":
    main()
