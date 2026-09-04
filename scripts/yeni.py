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
    ayristirici.add_argument("--sure", type=int, default=28,
                             help="hedef toplam sure sn (varsayilan 28; marka bandi 26-30)")
    argumanlar = ayristirici.parse_args()

    proje = PROJELER / argumanlar.slug
    plan_yolu = proje / "plan.json"
    if plan_yolu.exists():
        sys.exit(f"zaten var: {plan_yolu}")

    # karakter butcesi preset'ten (VO hizi degisince otomatik dogru kalir)
    try:
        hiz = json.loads((KOK / "preset.json").read_text(encoding="utf-8"))["seslendirme"]["karakter_hiz"]
    except Exception:
        hiz = 12.9
    hedef_karakter = round(argumanlar.sure * hiz)

    sahne_suresi = max(4, round(argumanlar.sure / argumanlar.sahne))
    plan = {
        "slug": argumanlar.slug,
        "baslik": "",
        "hook": "",
        "cta": "",
        "_cta_not": "ZORUNLU. Videoya OZEL, tartismali/ikili soru yaz - izleyici yorum "
                    "yazacak somut bir sey bulsun. Ornek: Bal porsugu mu kazanir, sirtlan mi? "
                    "Yorumlara yaz. Bos birakilirsa preset > kapanis_cagri (sabit siradaki "
                    "hangi hayvan cumlesi) kullanilir - o cumle yorum GETIRMIYOR, izleyicinin "
                    "kafasinda hayvan listesi yok (Enes karari 2026-09-04).",
        "hedef_sure": argumanlar.sure,
        "etiketler": ["#shorts", "#hayvanlar", "#doğa", "#ilginçbilgiler"],
        "_not": "ara[] terimleri INGILIZCE (MCP aramasi icin). klipler[] MCP ile secildikten "
                "sonra doldurulur, sonra: python scripts/indir.py --proje <slug>. "
                f"Toplam anlatim hedefi ~{hedef_karakter} karakter (CTA dahil; "
                f"{argumanlar.sure} sn x karakter_hiz {hiz}). Etiketlere konuya ozel 1-2 tag ekle.",
        "text": [],
        "sahneler": [
            {"no": i, "sure": sahne_suresi, "anlatim": "", "ara": [], "klipler": []}
            for i in range(1, argumanlar.sahne + 1)
        ],
        "_stil": "presets/senaryo-stili.md 6-parca formulu (kanca -> netlestirme -> ic ses -> "
                 "rehook -> tersine donus/payoff -> kapanis). Her cumle somut, belirsiz fiil yok.",
    }

    (proje / "footage").mkdir(parents=True, exist_ok=True)
    plan_yolu.write_text(json.dumps(plan, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"olusturuldu: {plan_yolu}")
    print("Sonraki: plan.json'daki anlatim + ara terimlerini doldur,")
    print("         MCP ile klipleri sec, sonra: python scripts/indir.py --proje " + argumanlar.slug)


if __name__ == "__main__":
    main()
