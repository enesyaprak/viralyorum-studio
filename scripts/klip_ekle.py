#!/usr/bin/env python3
"""HIBRIT AKIS: Enes'in disaridan getirdigi klipleri projeye alir.

Pipeline'in klip kaynagi artik iki bacakli (2026-09-04, Enes karari):
  1) indir.py      -> Pexels/Pixabay/Commons; lisansi ISPATLI, kaynaklar.json'a yazilir
  2) klip_ekle.py  -> Enes'in kendi bulup indirdigi klipler (bu script)

Bu script ne yapar:
  - klasordeki videolari footage/'a kopyalar (mp4 disi olanlari H.264 mp4'e cevirir)
  - ffprobe ile cozunurluk/sure/fps cikarir; yatay ve cok kisa klipleri UYARIR
  - HER KLIP ICIN KONTAK SAYFASI uretir (onizleme/*.jpg). Hibrit akisin asil kazanci
    bu adim: Claude kontak sayfalarina bakip senaryoyu ELDEKI GORUNTUYE gore yazar.
    Boylece goruntusu olmayan cumle yazilmiyor, en guclu goruntu metinde mutlaka geciyor.
  - kaynaklar.json'a "kaynak": "elle" olarak isler ve lisansi ISPATLI DEGIL diye
    ayrica isaretler - telif kaydinin durustlugu bozulmasin diye.

Kullanim:
    python scripts/klip_ekle.py --proje bal-porsugu --klasor ~/Downloads/honeybadger
    python scripts/klip_ekle.py --proje bal-porsugu --ad 1=leopar-kacar,2=kobra-avi
    python scripts/klip_ekle.py --proje bal-porsugu --klasor <yol> --zorla
"""
import argparse
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path

# Instagram/TikTok dosya adlarinda emoji ve aksanli harf oluyor; Windows konsolu
# cp1254 oldugu icin print() cokuyordu (2026-09-04). errors=replace: ad bozuk gorunse
# bile calisma DURMAZ - dosya zaten ig_NN.mp4 olarak yeniden adlandiriliyor.
for _akis in (sys.stdout, sys.stderr):
    try:
        _akis.reconfigure(encoding="utf-8", errors="replace")
    except (AttributeError, ValueError):
        pass

KOK = Path(__file__).resolve().parent.parent
PROJELER = KOK / "projeler"
VIDEO_UZANTI = {".mp4", ".mov", ".webm", ".mkv", ".avi", ".m4v", ".ogv"}
CEVRILECEK = VIDEO_UZANTI - {".mp4"}
LISANS = "ISPATLI DEGIL - Enes sagladi (harici kaynak, lisans kaydi yok)"


def sluglastir(metin):
    metin = (metin or "").lower()
    for a, b in (("ı", "i"), ("ğ", "g"), ("ü", "u"),
                 ("ş", "s"), ("ö", "o"), ("ç", "c")):
        metin = metin.replace(a, b)
    return re.sub(r"[^a-z0-9]+", "-", metin).strip("-")[:40]


def probe(yol):
    sonuc = subprocess.run(
        ["ffprobe", "-v", "error", "-select_streams", "v:0",
         "-show_entries", "stream=width,height,duration,r_frame_rate",
         "-of", "json", str(yol)], capture_output=True, text=True)
    if sonuc.returncode != 0:
        return None
    akislar = json.loads(sonuc.stdout).get("streams") or [{}]
    akis = akislar[0]
    fps = akis.get("r_frame_rate") or "0/1"
    pay, _, payda = fps.partition("/")
    try:
        fps_degeri = round(float(pay) / float(payda or 1), 1)
    except (ValueError, ZeroDivisionError):
        fps_degeri = None
    return {"genislik": akis.get("width"), "yukseklik": akis.get("height"),
            "sure": round(float(akis.get("duration") or 0), 1), "fps": fps_degeri}


def mp4e_cevir(kaynak, hedef):
    sonuc = subprocess.run(
        ["ffmpeg", "-y", "-v", "error", "-i", str(kaynak),
         "-c:v", "libx264", "-preset", "veryfast", "-crf", "20",
         "-pix_fmt", "yuv420p", "-c:a", "aac", str(hedef)],
        capture_output=True, text=True)
    tamam = sonuc.returncode == 0 and hedef.exists()
    return tamam, sonuc.stderr.strip()[:160]


def kontak_sayfasi(video, hedef, sure, kare=12):
    """4x3 kontak sayfasi - klibin icinde ne oldugu tek bakista gorulsun."""
    aralik = max(0.5, (sure or 10.0) / kare)
    sonuc = subprocess.run(
        ["ffmpeg", "-y", "-v", "error", "-i", str(video),
         "-vf", "fps=1/%.3f,scale=320:-1,tile=4x3" % aralik,
         "-frames:v", "1", str(hedef)], capture_output=True, text=True)
    return sonuc.returncode == 0 and hedef.exists()


def sonraki_numara(kayitlar):
    numaralar = [0]
    for k in kayitlar:
        eslesme = re.match(r"ig_(\d+)", str(k.get("dosya") or ""))
        if eslesme:
            numaralar.append(int(eslesme.group(1)))
    return max(numaralar) + 1


def yeniden_adlandir(footage, onizleme, ifade, kayit_yolu):
    # kaynaklar.json TELIF KANITI - dosya adi degisince kayit da degismeli,
    # yoksa kayit diskteki dosyaya isaret etmiyor (2026-09-04).
    kayitlar = json.loads(kayit_yolu.read_text(encoding="utf-8")) if kayit_yolu.exists() else []
    kayit_indeksi = {str(k.get("dosya")): k for k in kayitlar}
    degisti = False

    for parca in ifade.split(","):
        no, _, yeni_ad = parca.partition("=")
        try:
            numara = int(no.strip())
        except ValueError:
            print("  ! '%s' cozulemedi, bicim: 1=leopar-kacar" % parca)
            continue
        adaylar = sorted(footage.glob("ig_%02d*.mp4" % numara))
        if not adaylar:
            print("  ! ig_%02d*.mp4 yok, atlandi" % numara)
            continue
        eski = adaylar[0]
        hedef = footage / ("ig_%02d_%s.mp4" % (numara, sluglastir(yeni_ad)))
        if hedef == eski:
            continue
        eski.rename(hedef)
        onz = onizleme / (eski.stem + ".jpg")
        if onz.exists():
            onz.rename(onizleme / (hedef.stem + ".jpg"))
        kayit = kayit_indeksi.get(eski.name)
        if kayit:
            kayit["dosya"] = hedef.name
            kayit["id"] = hedef.stem
            kayit_indeksi[hedef.name] = kayit_indeksi.pop(eski.name)
            degisti = True
        print("  = %s -> %s" % (eski.name, hedef.name))

    if degisti:
        kayit_yolu.write_text(json.dumps(kayitlar, ensure_ascii=False, indent=2),
                              encoding="utf-8")
        print("  i kaynaklar.json guncellendi (dosya adlari eslesiyor)")


def main():
    a = argparse.ArgumentParser(description="Disaridan gelen klipleri projeye al (hibrit akis)")
    a.add_argument("--proje", required=True, help="projeler/<slug>")
    a.add_argument("--klasor", help="kaynak klasor (varsayilan: ~/Downloads/<proje>)")
    a.add_argument("--ad", help="inceleme sonrasi adlandirma: 1=leopar-kacar,2=kobra-avi")
    a.add_argument("--zorla", action="store_true", help="zaten alinmis dosyalari tekrar al")
    arg = a.parse_args()

    proje = PROJELER / arg.proje
    if not (proje / "plan.json").exists():
        sys.exit("HATA: proje yok: %s\n      Once: python scripts/yeni.py %s" % (proje, arg.proje))

    footage = proje / "footage"
    onizleme = proje / "onizleme"
    footage.mkdir(parents=True, exist_ok=True)

    if arg.ad:
        onizleme.mkdir(parents=True, exist_ok=True)
        yeniden_adlandir(footage, onizleme, arg.ad, proje / "kaynaklar.json")
        return

    kaynak_klasor = (Path(arg.klasor).expanduser() if arg.klasor
                     else Path.home() / "Downloads" / arg.proje)
    if not kaynak_klasor.is_dir():
        sys.exit("HATA: klasor yok: %s" % kaynak_klasor)

    dosyalar = sorted(d for d in kaynak_klasor.iterdir()
                      if d.is_file() and d.suffix.lower() in VIDEO_UZANTI)
    if not dosyalar:
        sys.exit("HATA: %s icinde video yok (%s)" % (kaynak_klasor, ", ".join(sorted(VIDEO_UZANTI))))

    onizleme.mkdir(parents=True, exist_ok=True)
    kayit_yolu = proje / "kaynaklar.json"
    kayitlar = json.loads(kayit_yolu.read_text(encoding="utf-8")) if kayit_yolu.exists() else []
    alinmis = {k.get("orijinal_ad") for k in kayitlar if k.get("kaynak") == "elle"}
    numara = sonraki_numara(kayitlar)

    print("proje: %s | kaynak: %s | %d video" % (arg.proje, kaynak_klasor, len(dosyalar)))
    alinan = atlanan = hatali = 0
    uyarilar = []

    for dosya in dosyalar:
        if dosya.name in alinmis and not arg.zorla:
            print("  = %s zaten alinmis" % dosya.name[:50])
            atlanan += 1
            continue

        ad = "ig_%02d" % numara
        hedef = footage / (ad + ".mp4")
        if dosya.suffix.lower() in CEVRILECEK:
            tamam, hata = mp4e_cevir(dosya, hedef)
            if not tamam:
                print("  ! %s: mp4'e cevrilemedi (%s)" % (dosya.name[:40], hata))
                hatali += 1
                continue
            print("  i %s -> mp4 cevrildi (CapCut uyumu)" % dosya.suffix)
        else:
            shutil.copyfile(dosya, hedef)

        bilgi = probe(hedef) or {}
        kontak_sayfasi(hedef, onizleme / (ad + ".jpg"), bilgi.get("sure"))

        g, y, sn = bilgi.get("genislik"), bilgi.get("yukseklik"), bilgi.get("sure")
        if g and y and g >= y:
            uyarilar.append("%s.mp4 YATAY (%sx%s) - 9:16'da kenarlar kirpilacak" % (ad, g, y))
        if sn and sn < 3:
            uyarilar.append("%s.mp4 cok kisa (%s sn) - hizli kesmede tek plan bile zor" % (ad, sn))

        kayit = {"kaynak": "elle", "id": ad, "dosya": ad + ".mp4",
                 "orijinal_ad": dosya.name, "lisans": LISANS}
        kayit.update(bilgi)
        kayitlar.append(kayit)
        print("  + %s.mp4  %sx%s  %s sn  <- %s" % (ad, g, y, sn, dosya.name[:45]))
        alinan += 1
        numara += 1

    kayit_yolu.write_text(json.dumps(kayitlar, ensure_ascii=False, indent=2), encoding="utf-8")

    if uyarilar:
        print("\n=== UYARI ===")
        for u in uyarilar:
            print("  ! %s" % u)

    print("\nalinan %d | zaten vardi %d | hata %d" % (alinan, atlanan, hatali))
    print("kontak sayfalari: %s" % onizleme)
    print("SONRAKI: Claude onizleme/*.jpg dosyalarina BAKAR ve senaryoyu eldeki")
    print("         goruntuye gore yazar; sonra: --ad 1=leopar-kacar,2=kobra-avi")
    print("\nNOT: bu klipler kaynaklar.json'a 'elle' olarak islendi, lisanslari ISPATLI DEGIL.")
    print("     Pexels/Pixabay/Commons klipleri ayri duruyor - telif kaydi karismiyor.")
    if hatali:
        sys.exit(1)


if __name__ == "__main__":
    main()
