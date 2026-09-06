#!/usr/bin/env python3
"""Wikimedia Commons'ta CC lisansli VIDEO arar (Pexels/Pixabay'in bulamadigi
DAVRANIS goruntuleri icin).

NEDEN VAR: Pexels ve Pixabay stok/estetik odakli - hayvanin kendisini bulursun ama
YAPTIGI SEYI bulamazsin. Bu oturumda uc kez duvara toslandi: biyolüminesans (0 gercek),
ucan yilan suzulme (0), guguk yuva parazitligi (0). Commons'a ise bilim insanlari ve
belgeselciler yukluyor; tur bazli davranis kaydi cikma ihtimali cok daha yuksek.
Lisans CC-BY / CC0 -> ticari kullanim serbest, ATIF ZORUNLU (CC0 haric).

Kullanim:
    python scripts/ara_commons.py "flying snake"
    python scripts/ara_commons.py "cuckoo nest parasitism" --limit 30
    python scripts/ara_commons.py "bioluminescence" --json      # makine icin

Cikti: baslik, cozunurluk, sure, LISANS, sahibi ve DOGRUDAN dosya URL'i.
Secilen klip plan.json'a "kaynak": "commons" olarak yazilir; indir.py webm/ogv ise
otomatik mp4'e cevirir (CapCut webm'i duzgun almiyor).
"""
import argparse
import json
import re
import ssl
import sys
import urllib.parse
import urllib.request

API = "https://commons.wikimedia.org/w/api.php"
# Wikimedia UA politikasi: kim oldugunu ve iletisim/proje adresini belirt (yoksa 403).
UA = "viralyorum-studio/1.0 (https://github.com/enesyaprak/viralyorum-studio)"

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")


def baglam():
    try:
        import certifi
        return ssl.create_default_context(cafile=certifi.where())
    except ImportError:
        return ssl.create_default_context()


BAGLAM = baglam()


def etiket_temizle(html):
    """extmetadata alanlari HTML donuyor (<a href=..>Ad</a>) - duz metne indir."""
    if not html:
        return ""
    metin = re.sub(r"<[^>]+>", "", str(html))
    return " ".join(metin.split()).strip()


def ara(sorgu, limit):
    parametreler = {
        "action": "query", "format": "json", "formatversion": "2",
        "generator": "search",
        "gsrsearch": f"{sorgu} filetype:video",
        "gsrnamespace": "6",          # 6 = File: ad alani
        "gsrlimit": str(limit),
        "prop": "imageinfo",
        "iiprop": "url|size|mime|extmetadata",
        "iiextmetadatafilter": "Artist|LicenseShortName|LicenseUrl|UsageTerms|Credit",
    }
    url = f"{API}?{urllib.parse.urlencode(parametreler)}"
    istek = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(istek, timeout=60, context=BAGLAM) as cevap:
        veri = json.loads(cevap.read().decode("utf-8"))
    return veri.get("query", {}).get("pages", []) or []


def kayit_cikar(sayfa):
    bilgi = (sayfa.get("imageinfo") or [{}])[0]
    ust = bilgi.get("extmetadata") or {}
    def al(anahtar):
        return etiket_temizle((ust.get(anahtar) or {}).get("value", ""))
    baslik = sayfa.get("title", "").replace("File:", "")
    return {
        "kaynak": "commons",
        "id": re.sub(r"[^A-Za-z0-9]+", "", baslik.rsplit(".", 1)[0])[:28] or "commons",
        "dosya": baslik,
        "url": bilgi.get("url", ""),
        "genislik": bilgi.get("width") or 0,
        "yukseklik": bilgi.get("height") or 0,
        "sure": round(bilgi.get("duration") or 0),
        "sahibi": al("Artist") or "bilinmiyor",
        "lisans": al("LicenseShortName") or al("UsageTerms") or "bilinmiyor",
        "lisans_url": al("LicenseUrl"),
        "sayfa": bilgi.get("descriptionurl", ""),
        "tur": bilgi.get("mime", ""),
    }


def main():
    ayristirici = argparse.ArgumentParser(description="Wikimedia Commons CC lisansli video arama")
    ayristirici.add_argument("sorgu", help="arama terimi (INGILIZCE daha iyi sonuc verir)")
    ayristirici.add_argument("--limit", type=int, default=20)
    ayristirici.add_argument("--json", action="store_true", help="plan.json'a yapistirilabilir cikti")
    argumanlar = ayristirici.parse_args()

    try:
        sayfalar = ara(argumanlar.sorgu, argumanlar.limit)
    except Exception as hata:
        sys.exit(f"HATA: Commons aramasi basarisiz -> {hata}")

    kayitlar = [kayit_cikar(s) for s in sayfalar]
    kayitlar = [k for k in kayitlar if k["url"]]
    if not kayitlar:
        print(f"'{argumanlar.sorgu}' icin video bulunamadi. "
              "Ipucu: tur adini Ingilizce/Latince dene (ornek: 'Chrysopelea', 'Cuculus canorus').")
        return

    if argumanlar.json:
        print(json.dumps(kayitlar, ensure_ascii=False, indent=2))
        return

    print(f"{len(kayitlar)} video — '{argumanlar.sorgu}'\n")
    for k in kayitlar:
        olcu = f"{k['genislik']}x{k['yukseklik']}" if k["genislik"] else "?"
        sure = f"{k['sure']}sn" if k["sure"] else "?"
        print(f"  {k['dosya'][:60]}")
        print(f"    {olcu} | {sure} | {k['tur']} | LISANS: {k['lisans']}")
        print(f"    sahibi: {k['sahibi'][:70]}")
        print(f"    url   : {k['url']}")
        print()
    print("NOT: CC-BY lisanslarda ATIF ZORUNLU - video aciklamasina 'sahibi / lisans' yaz.")
    print("     Secilen klibi plan.json'a \"kaynak\": \"commons\" ile ekle, sonra indir.py.")


if __name__ == "__main__":
    main()
