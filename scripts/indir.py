#!/usr/bin/env python3
"""plan.json'da SECILMIS klipleri indirir + lisans kaydi tutar.

Arama/secim isi MCP'de yapilir (pexels + pixabay MCP server'lari): Claude adaylari
gorup secer ve sechigi klipleri plan.json'daki sahnelerin 'klipler' alanina yazar.
Bu script sadece indirme + kaynak kaydi yapar - arama YAPMAZ.

plan.json sahne semasi:
  {
    "no": 1,
    "klipler": [
      {"kaynak": "pexels", "id": "1234", "url": "https://.../file.mp4",
       "sahibi": "Ad Soyad", "sayfa": "https://www.pexels.com/video/...",
       "genislik": 1080, "yukseklik": 1920, "sure": 12}
    ]
  }

Kullanim:
    python scripts/indir.py --proje ahtapot-uc-kalp
    python scripts/indir.py --proje ahtapot-uc-kalp --zorla
"""
import argparse
import json
import re
import ssl
import sys
import urllib.request
from pathlib import Path

KOK = Path(__file__).resolve().parent.parent
PROJELER = KOK / "projeler"
UA = "viralyorum-studio/1.0"


def ssl_baglami():
    """Bu makinede Python'un varsayilan CA bundle'i tanimsiz (ssl cafile=None) ->
    api.pexels.com 'certificate has expired' veriyor (OS seviyesinde sorun yok).
    certifi kuruluysa onun bundle'ini kullan, degilse varsayilana dus."""
    try:
        import certifi
        return ssl.create_default_context(cafile=certifi.where())
    except ImportError:
        return ssl.create_default_context()


BAGLAM = ssl_baglami()

LISANSLAR = {
    "pexels": "Pexels License (ticari kullanim serbest, atif gerekmez)",
    "pixabay": "Pixabay Content License (ticari kullanim serbest, atif gerekmez)",
}


def sluglastir(metin):
    metin = (metin or "").lower()
    for a, b in (("ı", "i"), ("ğ", "g"), ("ü", "u"), ("ş", "s"), ("ö", "o"), ("ç", "c")):
        metin = metin.replace(a, b)
    return re.sub(r"[^a-z0-9]+", "-", metin).strip("-")[:40]


def indir(url, hedef: Path):
    hedef.parent.mkdir(parents=True, exist_ok=True)
    gecici = hedef.with_suffix(hedef.suffix + ".indiriliyor")
    istek = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(istek, timeout=180, context=BAGLAM) as cevap, open(gecici, "wb") as cikti:
        while True:
            parca = cevap.read(1 << 16)
            if not parca:
                break
            cikti.write(parca)
    gecici.replace(hedef)  # yarim dosya birakma
    return hedef.stat().st_size


def main():
    ayristirici = argparse.ArgumentParser(description="Secilmis klipleri indir + lisans kaydi")
    ayristirici.add_argument("--proje", required=True, help="projeler/<slug>")
    ayristirici.add_argument("--zorla", action="store_true", help="var olan dosyalari yeniden indir")
    argumanlar = ayristirici.parse_args()

    proje = PROJELER / argumanlar.proje
    plan_yolu = proje / "plan.json"
    if not plan_yolu.exists():
        sys.exit(f"HATA: plan bulunamadi: {plan_yolu}")

    plan = json.loads(plan_yolu.read_text(encoding="utf-8"))
    footage = proje / "footage"
    kayit_yolu = proje / "kaynaklar.json"
    kayitlar = json.loads(kayit_yolu.read_text(encoding="utf-8")) if kayit_yolu.exists() else []
    kayitli = {f"{k['kaynak']}:{k['id']}" for k in kayitlar}

    sahneler = plan.get("sahneler", [])
    secili_toplam = sum(len(s.get("klipler") or []) for s in sahneler)
    if not secili_toplam:
        sys.exit("HATA: plan.json'da secilmis klip yok.\n"
                 "      Once MCP ile klip arayip secimleri sahnelerin 'klipler' alanina yaz.")

    print(f"proje: {argumanlar.proje} | {len(sahneler)} sahne | {secili_toplam} secili klip")
    inen = atlanan = hatali = 0

    for sahne in sahneler:
        no = sahne.get("no")
        for klip in sahne.get("klipler") or []:
            kaynak, kimlik_no, url = klip.get("kaynak"), str(klip.get("id")), klip.get("url")
            if not (kaynak and kimlik_no and url):
                print(f"  ! sahne {no}: eksik klip kaydi (kaynak/id/url), atlandi")
                hatali += 1
                continue

            ad = f"{no:02d}_{kaynak}{kimlik_no}.mp4"
            hedef = footage / ad
            kimlik = f"{kaynak}:{kimlik_no}"

            if hedef.exists() and not argumanlar.zorla:
                print(f"  = sahne {no}: {ad} zaten var")
                atlanan += 1
                if kimlik not in kayitli:
                    kayitlar.append({**klip, "dosya": ad, "sahne": no,
                                     "lisans": klip.get("lisans") or LISANSLAR.get(kaynak, "bilinmiyor")})
                    kayitli.add(kimlik)
                continue

            # Pixabay MCP sadece _medium (720p) URL veriyor; ayni CDN'de cogu videonun
            # _large (1080p+) kopyasi da var - once onu dene, 404'te medium'a dus (2026-08-23).
            adaylar = [url]
            if kaynak == "pixabay" and "_medium.mp4" in url:
                adaylar.insert(0, url.replace("_medium.mp4", "_large.mp4"))
            boyut, inen_url, son_hata = None, url, None
            for aday in adaylar:
                try:
                    boyut = indir(aday, hedef)
                    inen_url = aday
                    if aday != url:
                        print(f"  i sahne {no}: pixabay _large (1080p+) bulundu, medium yerine o indirildi")
                    break
                except Exception as hata:
                    son_hata = hata
            if boyut is None:
                print(f"  ! sahne {no}: {kimlik} indirilemedi -> {son_hata}")
                hatali += 1
                continue
            klip = {**klip, "indirilen_url": inen_url}  # lisans kaydinda gercek dosya izi

            print(f"  + sahne {no}: {ad} ({boyut / 1e6:.1f} MB, "
                  f"{klip.get('genislik')}x{klip.get('yukseklik')})")
            inen += 1
            if kimlik in kayitli:
                kayitlar = [k for k in kayitlar if f"{k['kaynak']}:{k['id']}" != kimlik]
            kayitlar.append({**klip, "dosya": ad, "sahne": no,
                             "lisans": klip.get("lisans") or LISANSLAR.get(kaynak, "bilinmiyor")})
            kayitli.add(kimlik)

    kayit_yolu.write_text(json.dumps(kayitlar, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"\ninen {inen} | zaten vardi {atlanan} | hata {hatali}")
    print(f"lisans kaydi: {kayit_yolu}  (telif kaniti - SAKLA)")
    print(f"CapCut'a surukle: {footage}")
    if hatali:
        sys.exit(1)


if __name__ == "__main__":
    main()
