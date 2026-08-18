#!/usr/bin/env python3
"""plan.json anlatimlarini duz metne cikarir.

Enes bu metni CapCut'ta **auto clipping (akilli klip) outline** alanina yapistiriyor;
CapCut klipleri metne gore diziyor. Bu yuzden metin, VO'ya giden metinle BIREBIR ayni
olmali - klip dizilimi ile seslendirme kaymasin.

Cikti: projeler/<slug>/senaryo.txt  (tek paragraf, sahne numarasi/etiket yok)

Kullanim:
    python scripts/senaryo.py --proje olumsuz-denizanasi
    python scripts/senaryo.py --proje olumsuz-denizanasi --sahneli   # sahne sahne, panoya bakmak icin
"""
import argparse
import json
import sys
from pathlib import Path

KOK = Path(__file__).resolve().parent.parent
PRESET = KOK / "preset.json"


def preset_oku():
    try:
        return json.loads(PRESET.read_text(encoding="utf-8")).get("seslendirme", {})
    except Exception:
        return {}


def kapanis_cagri():
    """Her senaryonun sonuna eklenen sabit CTA (preset.json'dan)."""
    return (preset_oku().get("kapanis_cagri") or "").strip()


def main():
    ap = argparse.ArgumentParser(description="plan.json -> senaryo.txt (CapCut auto clipping outline)")
    ap.add_argument("--proje", required=True, help="projeler/<slug>")
    ap.add_argument("--sahneli", action="store_true", help="sahne numaralariyla yazdir (dosyaya degil, ekrana)")
    a = ap.parse_args()

    plan_yolu = KOK / "projeler" / a.proje / "plan.json"
    if not plan_yolu.exists():
        sys.exit(f"HATA: plan bulunamadi: {plan_yolu}")
    plan = json.loads(plan_yolu.read_text(encoding="utf-8"))

    anlatimlar = [(s.get("no"), (s.get("anlatim") or "").strip())
                  for s in plan.get("sahneler", []) if (s.get("anlatim") or "").strip()]
    if not anlatimlar:
        sys.exit("HATA: plan.json'da anlatim yok.")

    metin = " ".join(m for _, m in anlatimlar)
    cagri = kapanis_cagri()
    if cagri and not metin.rstrip().endswith(cagri):
        metin = f"{metin} {cagri}"
    hiz = preset_oku().get("karakter_hiz") or 16.5
    hedef = plan_yolu.parent / "senaryo.txt"
    hedef.write_text(metin + "\n", encoding="utf-8")

    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    if a.sahneli:
        for no, m in anlatimlar:
            print(f"{no}. {m}")
        print()
    print(metin)
    print(f"\n[OK] {hedef}  ({len(metin)} karakter, tahmini VO ~{len(metin)/hiz:.0f} sn)")
    print("     CapCut > auto clipping (akilli klip) > outline alanina bu metni yapistir.")


if __name__ == "__main__":
    main()
