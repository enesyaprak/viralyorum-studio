#!/usr/bin/env python3
"""Footage'i YENI bir CapCut taslagina MEDYA HAVUZU olarak import eder.

Timeline'a DOKUNMAZ (0 track kalir) - Enes klipleri CapCut icinde smart clipping
ile kendi dizer/keser. Bos timeline daha dusuk riskli: CapCut timeline'i kendi
kurdugu icin disaridan yazilan segmentleri ezme sorunu olusmuyor.

Yontem: bos bir taslak (iskelet) klasoru kopyalanir, kimlik/ad/yol alanlari
yenilenir, canvas 9:16 yapilir ve klipler draft_meta_info.json'daki
draft_materials type=0 grubuna 'video' kaydi olarak yazilir.

Kullanim:
    python scripts/capcut_havuz.py --proje ahtapot-uc-kalp --ad ahtapot-uc-kalp
    python scripts/capcut_havuz.py --proje ahtapot-uc-kalp --ad test --iskelet 0816
"""
import argparse
import json
import os
import shutil
import subprocess
import sys
import time
import uuid
from pathlib import Path

KOK = Path(__file__).resolve().parent.parent
SCRIPTS = Path(__file__).resolve().parent
DRAFTS = Path(os.environ["LOCALAPPDATA"]) / "CapCut Drafts"

sys.path.insert(0, str(SCRIPTS))


def bos_iskelet_bul():
    """Timeline'i BOS (0 track, duration 0) bir taslak bul - iskelet olarak kullanilir."""
    adaylar = []
    for icerik in DRAFTS.glob("*/draft_content.json"):
        try:
            veri = json.loads(icerik.read_text(encoding="utf-8"))
        except Exception:
            continue  # sifreli ya da bozuk taslak
        if not veri.get("tracks") and not veri.get("duration"):
            adaylar.append((icerik.parent.stat().st_mtime, icerik.parent.name))
    if not adaylar:
        return None
    return max(adaylar)[1]


def capcut_uuid():
    """CapCut'in kullandigi buyuk harfli GUID bicimi."""
    return str(uuid.uuid4()).upper()


def kimlik_yenile(hedef: Path, timeline_id: str, simdi_us: int, genislik: int, yukseklik: int):
    """Iskeletten miras kalan timeline kimliklerini TEK bir kimlige esitler.

    KRITIK (2026-08-16'da acilmama sorununun sebebi): calisan bir taslakta su DORT
    deger BIREBIR AYNIDIR --
      1. kok draft_content.json > id
      2. Timelines/project.json > main_timeline_id  (ve timelines[].id)
      3. Timelines/<UUID>/ klasor adi
      4. Timelines/<UUID>/draft_content.json > id
    Bunlardan biri farkli olursa CapCut taslagi LISTELER ama ACAMAZ.
    Bu yuzden hepsine ayni 'timeline_id' yazilir.

    (Timelines/project.json'un kendi 'id' alani AYRI bir kimliktir, esitlenmez.)
    """
    zaman_dizini = hedef / "Timelines"
    proje_yolu = zaman_dizini / "project.json"
    if not proje_yolu.exists():
        return False  # eski format, Timelines yok

    proje = json.loads(proje_yolu.read_text(encoding="utf-8"))
    eski_timeline = proje.get("main_timeline_id")

    proje["id"] = capcut_uuid()  # proje kimligi timeline'dan bagimsiz
    proje["main_timeline_id"] = timeline_id
    proje["create_time"] = simdi_us
    proje["update_time"] = simdi_us
    for zaman_cizgisi in proje.get("timelines") or []:
        zaman_cizgisi["id"] = timeline_id
        zaman_cizgisi["create_time"] = simdi_us
        zaman_cizgisi["update_time"] = simdi_us
    proje_metni = json.dumps(proje, ensure_ascii=False)
    proje_yolu.write_text(proje_metni, encoding="utf-8")
    for yedek in zaman_dizini.glob("project.json.bak"):
        yedek.write_text(proje_metni, encoding="utf-8")

    # UUID klasorunu yeni kimlige tasi
    eski_klasor = zaman_dizini / eski_timeline if eski_timeline else None
    yeni_klasor = zaman_dizini / timeline_id
    if eski_klasor and eski_klasor.is_dir() and eski_klasor != yeni_klasor:
        eski_klasor.rename(yeni_klasor)

    # IC draft_content.json: kimlik + canvas (asil timeline verisi burada)
    ic_yolu = yeni_klasor / "draft_content.json"
    if ic_yolu.exists():
        ic = json.loads(ic_yolu.read_text(encoding="utf-8"))
        ic["id"] = timeline_id
        ic["canvas_config"] = {"ratio": "original", "width": genislik,
                               "height": yukseklik, "background": None}
        ic_metni = json.dumps(ic, ensure_ascii=False)
        ic_yolu.write_text(ic_metni, encoding="utf-8")
        # ic ayna dosyalar da ayni icerigi tasimali
        for ayna in ("draft_content.json.bak", "template.tmp", "template-2.tmp"):
            if (yeni_klasor / ayna).exists():
                (yeni_klasor / ayna).write_text(ic_metni, encoding="utf-8")

    return True


def ayar_dosyasi_tazele(hedef: Path, simdi_s: int):
    """draft_settings iskeletin olusturma/duzenleme zamanlarini tasiyor - sifirla."""
    ayar = hedef / "draft_settings"
    if not ayar.exists():
        return
    satirlar = []
    for satir in ayar.read_text(encoding="utf-8", errors="replace").splitlines():
        if satir.startswith("draft_create_time="):
            satir = f"draft_create_time={simdi_s}"
        elif satir.startswith("draft_last_edit_time="):
            satir = f"draft_last_edit_time={simdi_s}"
        elif satir.startswith("real_edit_seconds="):
            satir = "real_edit_seconds=0"
        elif satir.startswith("real_edit_keys="):
            satir = "real_edit_keys=0"
        satirlar.append(satir)
    ayar.write_text("\n".join(satirlar) + "\n", encoding="utf-8")


def dogrula(hedef: Path):
    """Taslagin CapCut'ta ACILABILIR olmasi icin sart olan tutarliliklari kontrol eder.

    Calisan bir taslakta kok draft_content.id, project.json main_timeline_id,
    Timelines/<UUID> klasor adi ve ic draft_content.id AYNIDIR. Biri saparsa
    CapCut taslagi listeler ama acamaz - bu sessiz hatayi burada yakaliyoruz.
    """
    sorunlar = []
    kok_id = json.loads((hedef / "draft_content.json").read_text(encoding="utf-8")).get("id")

    zaman_dizini = hedef / "Timelines"
    if not (zaman_dizini / "project.json").exists():
        return sorunlar  # eski format

    proje = json.loads((zaman_dizini / "project.json").read_text(encoding="utf-8"))
    ana_id = proje.get("main_timeline_id")
    klasorler = [p.name for p in zaman_dizini.iterdir() if p.is_dir()]

    if ana_id != kok_id:
        sorunlar.append(f"main_timeline_id ({ana_id}) != kok draft_content.id ({kok_id})")
    if len(klasorler) != 1:
        sorunlar.append(f"Timelines altinda {len(klasorler)} klasor var, 1 olmali: {klasorler}")
    elif klasorler[0] != kok_id:
        sorunlar.append(f"Timelines klasor adi ({klasorler[0]}) != kok draft_content.id ({kok_id})")
    else:
        ic_yolu = zaman_dizini / klasorler[0] / "draft_content.json"
        if ic_yolu.exists():
            ic_id = json.loads(ic_yolu.read_text(encoding="utf-8")).get("id")
            if ic_id != kok_id:
                sorunlar.append(f"ic draft_content.id ({ic_id}) != kok draft_content.id ({kok_id})")

    for zaman_cizgisi in proje.get("timelines") or []:
        if zaman_cizgisi.get("id") != kok_id:
            sorunlar.append(f"timelines[].id ({zaman_cizgisi.get('id')}) != kok draft_content.id")

    if not (hedef / "draft_cover.jpg").exists():
        sorunlar.append("draft_cover.jpg eksik (calisan taslaklarda var)")

    return sorunlar


def ffprobe_bilgi(yol: Path):
    """(genislik, yukseklik, sure_mikrosaniye) dondurur."""
    sonuc = subprocess.run(
        ["ffprobe", "-v", "error", "-select_streams", "v:0",
         "-show_entries", "stream=width,height", "-show_entries", "format=duration",
         "-of", "json", str(yol)],
        capture_output=True, text=True)
    if sonuc.returncode != 0:
        raise RuntimeError(f"ffprobe okuyamadi: {yol.name}")
    veri = json.loads(sonuc.stdout)
    akis = (veri.get("streams") or [{}])[0]
    sure = float((veri.get("format") or {}).get("duration") or 0)
    return akis.get("width"), akis.get("height"), int(sure * 1_000_000)


def medya_kaydi(yol: Path, simdi_s: int, simdi_us: int):
    genislik, yukseklik, sure_us = ffprobe_bilgi(yol)
    return {
        "ai_group_type": "",
        "create_time": simdi_s,
        "duration": sure_us,
        "enter_from": 0,
        "extra_info": yol.name,
        "file_Path": str(yol).replace("\\", "/"),
        "height": yukseklik,
        "id": str(uuid.uuid4()),
        "import_time": simdi_s,
        "import_time_ms": simdi_us,
        "item_source": 1,
        "material_color_tag": "",
        "md5": "",
        "metetype": "video",
        "roughcut_time_range": {"duration": -1, "start": -1},
        "sub_time_range": {"duration": -1, "start": -1},
        "type": 0,
        "width": genislik,
    }


def main():
    ayristirici = argparse.ArgumentParser(description="Footage'i yeni CapCut taslagina havuz olarak import et")
    ayristirici.add_argument("--proje", required=True, help="projeler/<slug>")
    ayristirici.add_argument("--ad", required=True, help="olusturulacak CapCut taslak adi")
    ayristirici.add_argument("--iskelet", help="iskelet olarak kullanilacak BOS taslak (verilmezse otomatik bulunur)")
    ayristirici.add_argument("--genislik", type=int, default=1080)
    ayristirici.add_argument("--yukseklik", type=int, default=1920)
    argumanlar = ayristirici.parse_args()

    # GUVENLIK KILIDI
    import capcut_guard
    capcut_guard.dur_capcut_acikken()

    footage = KOK / "projeler" / argumanlar.proje / "footage"
    klipler = sorted(footage.glob("*.mp4"))
    if not klipler:
        sys.exit(f"HATA: klip yok: {footage}\n      Once: python scripts/indir.py --proje {argumanlar.proje}")

    hedef = DRAFTS / argumanlar.ad
    if hedef.exists():
        sys.exit(f"HATA: '{argumanlar.ad}' taslagi ZATEN VAR: {hedef}\n"
                 f"      Ustune yazmiyorum - baska ad ver ya da CapCut'tan sil.")

    iskelet_adi = argumanlar.iskelet or bos_iskelet_bul()
    if not iskelet_adi:
        sys.exit("HATA: bos iskelet taslak bulunamadi.\n"
                 "      CapCut'ta sifirdan bos bir proje olustur, kapat, tekrar calistir.")
    iskelet = DRAFTS / iskelet_adi
    if not (iskelet / "draft_content.json").exists():
        sys.exit(f"HATA: iskelet gecersiz: {iskelet}")

    print(f"iskelet : {iskelet_adi}")
    print(f"hedef   : {argumanlar.ad}")
    print(f"klip    : {len(klipler)} adet")

    shutil.copytree(iskelet, hedef)

    # Iskelette kapak yoksa calisan bir taslaktan kopyala: bazi bos iskeletler (0820 gibi)
    # draft_cover.jpg tasimadigi icin dogrula() 'CapCut acamaz' der ve senaryo.txt uretilmez.
    # CapCut taslagi ilk kaydettiginde kendi kapagini ureterek bunu ezer - placeholder yeterli.
    hedef_kapak = hedef / "draft_cover.jpg"
    if not hedef_kapak.exists():
        kaynak_kapak = next((p for p in DRAFTS.glob("*/draft_cover.jpg")
                             if p.parent != hedef), None)
        if kaynak_kapak:
            shutil.copy2(kaynak_kapak, hedef_kapak)
            print(f"kapak   : {kaynak_kapak.parent.name}'ten kopyalandi (iskelette yoktu)")
        else:
            print("  uyari: kopyalanacak kapak bulunamadi - dogrulama basarisiz olabilir")

    simdi_s = int(time.time())
    simdi_us = int(time.time() * 1_000_000)

    # --- draft_content.json: kimlik + canvas ---
    icerik_yolu = hedef / "draft_content.json"
    icerik = json.loads(icerik_yolu.read_text(encoding="utf-8"))
    if icerik.get("tracks") or icerik.get("duration"):
        shutil.rmtree(hedef)
        sys.exit(f"HATA: '{iskelet_adi}' bos degil (track/duration var). Bos bir iskelet ver.")
    # TEK kimlik: kok draft_content.id == timeline id == UUID klasoru == ic draft_content.id
    timeline_id = capcut_uuid()
    icerik["id"] = timeline_id
    icerik["canvas_config"] = {"ratio": "original", "width": argumanlar.genislik,
                              "height": argumanlar.yukseklik, "background": None}
    icerik_yolu.write_text(json.dumps(icerik, ensure_ascii=False), encoding="utf-8")

    if kimlik_yenile(hedef, timeline_id, simdi_us, argumanlar.genislik, argumanlar.yukseklik):
        print(f"timeline kimligi (dort yerde ayni): {timeline_id}")
    ayar_dosyasi_tazele(hedef, simdi_s)

    # --- draft_meta_info.json: kimlik/ad/yol + medya havuzu ---
    meta_yolu = hedef / "draft_meta_info.json"
    meta = json.loads(meta_yolu.read_text(encoding="utf-8"))
    meta["draft_id"] = str(uuid.uuid4()).upper()
    meta["draft_name"] = argumanlar.ad
    meta["draft_fold_path"] = str(hedef).replace("\\", "/")
    meta["draft_cover"] = "draft_cover.jpg"  # calisan taslaklarda bu dosya VAR, silme
    meta["tm_draft_create"] = simdi_us
    meta["tm_draft_modified"] = simdi_us
    meta["tm_duration"] = 0

    gruplar = meta.get("draft_materials") or []
    video_grubu = next((g for g in gruplar if g.get("type") == 0), None)
    if video_grubu is None:
        video_grubu = {"type": 0, "value": []}
        gruplar.insert(0, video_grubu)
        meta["draft_materials"] = gruplar
    video_grubu["value"] = []  # iskeletten gelen artik kayitlari temizle

    toplam_bayt = 0
    for klip in klipler:
        try:
            kayit = medya_kaydi(klip, simdi_s, simdi_us)
        except RuntimeError as hata:
            print(f"  ! atlandi: {hata}")
            continue
        video_grubu["value"].append(kayit)
        toplam_bayt += klip.stat().st_size
        print(f"  + {klip.name} ({kayit['width']}x{kayit['height']}, {kayit['duration'] / 1e6:.1f}sn)")

    if not video_grubu["value"]:
        shutil.rmtree(hedef)
        sys.exit("HATA: hicbir klip okunamadi, taslak olusturulmadi.")

    meta["draft_timeline_materials_size_"] = toplam_bayt
    meta_yolu.write_text(json.dumps(meta, ensure_ascii=False), encoding="utf-8")

    # --- ayna dosyalar + degisiklik damgasi (CapCut disaridan yazimi gorsun) ---
    try:
        import capcut_sync
        capcut_sync.sync(hedef, quiet=True)
    except Exception as hata:
        print(f"  uyari: capcut_sync calismadi ({hata}) - CapCut degisikligi gormezse bu olabilir")

    # --- OTOMATIK DOGRULAMA: dort kimlik ayni mi + kapak yerinde mi ---
    sorunlar = dogrula(hedef)
    if sorunlar:
        print("\nDOGRULAMA BASARISIZ - CapCut bu taslagi ACAMAZ:")
        for sorun in sorunlar:
            print(f"  ! {sorun}")
        print(f"\nTaslak silinmedi, incelemek icin: {hedef}")
        sys.exit(1)
    print("\ndogrulama: dort kimlik ayni, kapak yerinde - OK")

    print(f"\nTAMAM: '{argumanlar.ad}' olusturuldu ({len(video_grubu['value'])} klip havuzda, timeline bos)")
    print(f"       {hedef}")
    # Senaryo metni: Enes bunu CapCut'ta auto clipping (akilli klip) outline alanina
    # yapistiriyor -> klip dizilimi, VO'ya giden metinle BIREBIR ayni metinden cikiyor.
    try:
        subprocess.run([sys.executable, str(SCRIPTS / "senaryo.py"),
                        "--proje", argumanlar.proje], check=True)
    except Exception as hata:
        print(f"  uyari: senaryo.txt uretilemedi ({hata})")

    print("\nCapCut'i ac -> taslak listesinde gorunecek -> klipler medya sekmesinde hazir.")
    print("Auto clipping (akilli klip) outline alanina senaryo.txt icerigini yapistir.")
    print("Acilista 'kurtar/recover' dialogu cikarsa REDDET.")


if __name__ == "__main__":
    main()
