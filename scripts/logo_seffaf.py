#!/usr/bin/env python3
"""Logonun arka planını şeffaf yapar (beyaz/düz renk zemin için).

Köşelerden zemin rengini tespit eder, o renge yakın pikselleri saydamlaştırır.
Kenarlarda yumuşak geçiş bırakır. Çıktı: alfa kanallı PNG.

Kullanım:
    python scripts/logo_seffaf.py --in "input/zeus logo.jpg" --out "input/zeus_logo_seffaf.png"
    python scripts/logo_seffaf.py --in logo.jpg --out logo.png --tol 40
"""
import argparse
from collections import Counter
from pathlib import Path
from PIL import Image


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--in", dest="src", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--tol", type=int, default=36, help="renk toleransı (yüksek = daha çok siler)")
    args = ap.parse_args()

    img = Image.open(args.src).convert("RGBA")
    px = img.load()
    w, h = img.size

    # köşelerden zemin rengini tahmin et
    corners = [px[0, 0], px[w - 1, 0], px[0, h - 1], px[w - 1, h - 1]]
    bg = Counter([c[:3] for c in corners]).most_common(1)[0][0]

    tol = args.tol
    soft = tol + 24  # yumuşak geçiş bandı
    cleared = 0
    for y in range(h):
        for x in range(w):
            r, g, b, a = px[x, y]
            d = abs(r - bg[0]) + abs(g - bg[1]) + abs(b - bg[2])
            if d <= tol:
                px[x, y] = (r, g, b, 0); cleared += 1
            elif d <= soft:
                # bant içinde kademeli saydamlık (kenar yumuşatma)
                na = int(a * (d - tol) / (soft - tol))
                px[x, y] = (r, g, b, na)

    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    img.save(out)
    pct = round(100 * cleared / (w * h))
    print(f"[OK] Şeffaf logo: {out} | zemin rengi {bg} | %{pct} silindi")
    if pct < 5:
        print("  UYARI: çok az silindi — zemin beyaz/düz değilse --tol artır ya da CapCut remove-bg gerekir.")


if __name__ == "__main__":
    main()
