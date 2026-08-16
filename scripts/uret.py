#!/usr/bin/env python3
"""TEK KOMUT — viralyorum anlatim shorts: plan.json'dan sonrasini uctan uca kurar.

Tek yaratici adim plan.json'daki anlatim metni. Gerisi mekanik:
TTS -> VO enjekte -> VO'yu transcribe et -> karaoke altyazi -> muzik -> efekt
-> gecis -> hook text -> sozluk duzeltmesi -> supheli altyazi raporu.

Kullanim:
    python scripts/uret.py --proje ahtapot-uc-kalp --draft "ahtapot"
    python scripts/uret.py --proje ahtapot-uc-kalp --draft "ahtapot" --atla muzik,efekt

On kosul: Enes CapCut'ta projeyi kurmus (footage dizilmis) ve CapCut'i TAM KAPATMIS olmali.
Config preset.json'dan gelir; EKSIK alan o adimi ATLAR (uydurmaz).

bluemedya seslendirme.py'den turetildi; marka/brands.json yerine proje/preset.json kullanir.
"""
import argparse
import glob
import json
import os
import subprocess
import sys
from pathlib import Path

KOK = Path(__file__).resolve().parent.parent
SCRIPTS = Path(__file__).resolve().parent
DRAFTS = Path(os.environ["LOCALAPPDATA"]) / "CapCut Drafts"
PRESET = KOK / "preset.json"
SOZLUK = KOK / "presets" / "altyazi_sozluk.json"
CIKTI = KOK / "output"
PY = sys.executable

sys.path.insert(0, str(SCRIPTS))
import supheli  # noqa: E402


def draft_bul(ad):
    """Kismi ada gore CapCut taslagini bul (CapCut klasor adini degistirebiliyor)."""
    if (DRAFTS / ad / "draft_content.json").exists():
        return ad
    anahtar = ad.lower().replace(" ", "")
    for meta in glob.glob(str(DRAFTS / "*" / "draft_meta_info.json")):
        klasor = os.path.basename(os.path.dirname(meta))
        try:
            isim = json.load(open(meta, encoding="utf-8")).get("draft_name", "")
        except Exception:
            isim = ""
        if anahtar in klasor.lower().replace(" ", "") or anahtar in isim.lower().replace(" ", ""):
            return klasor
    sys.exit(f"HATA: '{ad}' taslagi bulunamadi.")


def ffprobe_sure(yol):
    try:
        sonuc = subprocess.run(
            ["ffprobe", "-v", "quiet", "-show_entries", "format=duration", "-of", "csv=p=0", str(yol)],
            capture_output=True, text=True)
        return float(sonuc.stdout.strip())
    except Exception:
        return None


def draft_video_suresi(draft):
    try:
        icerik = json.loads((DRAFTS / draft / "draft_content.json").read_text(encoding="utf-8"))
        return icerik.get("duration", 0) / 1e6  # mikrosaniye -> saniye
    except Exception:
        return None


def calistir(arac, argumanlar, etiket):
    print(f"\n--- {etiket} ---")
    sonuc = subprocess.run([PY, str(SCRIPTS / arac)] + [str(x) for x in argumanlar])
    if sonuc.returncode != 0:
        print(f"  UYARI: '{etiket}' hata verdi (devam ediliyor).")
        return False
    return True


def logo_var_mi(draft, dosya_adi):
    """Taslakta bu logo zaten duruyor mu (tekrar uretimde ikinci kez eklenmesin)."""
    try:
        dc = json.loads((DRAFTS / draft / "draft_content.json").read_text(encoding="utf-8"))
    except Exception:
        return False
    return any(v.get("type") == "photo" and dosya_adi.lower() in str(v.get("path", "")).lower()
               for v in dc.get("materials", {}).get("videos", []))


def plan_oku(slug):
    plan_yolu = KOK / "projeler" / slug / "plan.json"
    if not plan_yolu.exists():
        sys.exit(f"HATA: plan bulunamadi: {plan_yolu}")
    plan = json.loads(plan_yolu.read_text(encoding="utf-8"))

    anlatimlar = [s.get("anlatim", "").strip() for s in plan.get("sahneler", [])]
    vo_metni = " ".join(a for a in anlatimlar if a)
    if not vo_metni:
        sys.exit("HATA: plan.json sahnelerinde 'anlatim' metni yok.")

    text_satirlari = plan.get("text") or ([plan["hook"]] if plan.get("hook") else [])
    return plan, vo_metni, text_satirlari


def main():
    ayristirici = argparse.ArgumentParser(description="viralyorum anlatim shorts uretim zinciri")
    ayristirici.add_argument("--proje", required=True, help="projeler/<slug>")
    ayristirici.add_argument("--draft", required=True, help="CapCut taslak adi (kismi eslesme yeterli)")
    ayristirici.add_argument("--atla", default="", help="atlanacak: vo,altyazi,muzik,efekt,gecis,text,sozluk")
    argumanlar = ayristirici.parse_args()

    if not PRESET.exists():
        sys.exit(f"HATA: preset bulunamadi: {PRESET}")
    yapilandirma = json.loads(PRESET.read_text(encoding="utf-8")).get("seslendirme", {})
    if not yapilandirma:
        sys.exit("HATA: preset.json icinde 'seslendirme' blogu yok.")

    plan, vo_metni, text_satirlari = plan_oku(argumanlar.proje)
    draft = draft_bul(argumanlar.draft)
    CIKTI.mkdir(exist_ok=True)

    # GUVENLIK KILIDI — CapCut acikken diske yazilan editleri auto-save eziyor
    import capcut_guard
    capcut_guard.dur_capcut_acikken()
    if (DRAFTS / draft / ".locked").exists():
        sys.exit(f"DUR: CapCut '{draft}' ile ACIK. Once tepsiden TAM KAPAT, sonra tekrar calistir.")

    atla = {x.strip() for x in argumanlar.atla.split(",") if x.strip()}
    print(f"=== VIRALYORUM: {plan.get('slug', argumanlar.proje)} | taslak: {draft} ===")

    vo_mp3 = CIKTI / f"{draft}_vo.mp3"
    tr_json = CIKTI / f"{draft}_vo_tr.json"

    # 1) TTS
    if "vo" not in atla:
        ses = yapilandirma.get("voice")
        if not ses:
            sys.exit("HATA: preset.json > seslendirme.voice (ElevenLabs voice ID) bos.")
        vo_txt = CIKTI / f"{draft}_vo.txt"
        vo_txt.write_text(vo_metni, encoding="utf-8")

        tts_arg = ["--text-file", vo_txt, "--out", vo_mp3, "--voice", ses]
        # Ses ayarlari preset'ten; TANIMSIZ olan gonderilmez -> sesin varsayilani gecerli
        ayarlar = yapilandirma.get("ses_ayarlari") or {}
        for anahtar, bayrak in (("stability", "--stability"), ("similarity", "--similarity"),
                                ("style", "--style"), ("speed", "--speed")):
            if ayarlar.get(anahtar) is not None:
                tts_arg += [bayrak, str(ayarlar[anahtar])]
        if ayarlar.get("speaker_boost"):
            tts_arg.append("--speaker-boost")

        if not calistir("tts.py", tts_arg, "TTS (VO uret)"):
            sys.exit("DUR: TTS basarisiz (ElevenLabs anahtari/kredisi?).")

        # KURAL: VO suresi ~ video suresi (VO videonun tamami boyunca sursun)
        vo_sure, video_sure = ffprobe_sure(vo_mp3), draft_video_suresi(draft)
        if vo_sure and video_sure:
            oran = vo_sure / video_sure
            print(f"  VO {vo_sure:.1f}s / video {video_sure:.1f}s (oran {oran:.2f})")
            if oran < 0.85:
                print(f"  ! VO KISA — plan.json anlatimlarini uzat, ~{video_sure * 15:.0f} karakter hedefle.")
            elif oran > 1.1:
                print("  ! VO UZUN — anlatimi kisalt, videoya tasiyor.")

        if not calistir("capcut_audio.py",
                        ["--draft", draft, "--audio", vo_mp3,
                         "--match", yapilandirma.get("vo_match", "ElevenLabs")], "VO enjekte"):
            # capcut_audio.py var olan bir ses materyalini DEGISTIRIR. Sifirdan kurulan
            # taslakta (sablonsuz ilk video) degistirecek materyal yok -> ses elementini
            # bir prototip taslaktan klonlayip VO'yu YENI audio track olarak ekle.
            proto = yapilandirma.get("vo_proto")
            if proto:
                calistir("capcut_muzik.py",
                         ["--draft", draft, "--from", proto,
                          "--volume", "1.0", "--audio", vo_mp3], "VO enjekte (prototipten klon)")
            else:
                print("  ! VO enjekte edilemedi: taslakta ses materyali yok ve "
                      "preset.json > seslendirme.vo_proto bos.")

    # 2) ALTYAZI (VO'yu transcribe et -> karaoke)
    if "altyazi" not in atla:
        calistir("transcribe.py", [vo_mp3, "--out", tr_json], "VO transcribe (kelime zamani)")
        altyazi_arg = ["--draft", draft, "--transcript", tr_json]
        if yapilandirma.get("style_from"):
            altyazi_arg += ["--style-from", yapilandirma["style_from"]]
        calistir("capcut_captions.py", altyazi_arg, "Karaoke altyazi")

    # 3) MUZIK (arkaplan sesi — her videoda ayni)
    if "muzik" not in atla and yapilandirma.get("muzik", {}).get("from"):
        muzik = yapilandirma["muzik"]
        muzik_arg = ["--draft", draft, "--from", muzik["from"],
                     "--match", muzik.get("match", ""),
                     "--volume", str(muzik.get("volume", 0.18))]
        if muzik.get("dosya"):
            dosya = KOK / muzik["dosya"]
            if not dosya.exists():
                sys.exit(f"HATA: arkaplan sesi bulunamadi: {dosya}")
            muzik_arg += ["--audio", str(dosya), "--varsa-atla",
                          "--kaynak-baslangic", str(muzik.get("kaynak_baslangic", 0))]
        calistir("capcut_muzik.py", muzik_arg, "Arkaplan sesi")

    # 3b) LOGO (kanal logosu — her videoda ayni yer/olcek)
    if "logo" not in atla and yapilandirma.get("logo", {}).get("dosya"):
        logo = yapilandirma["logo"]
        gorsel = KOK / logo["dosya"]
        if not gorsel.exists():
            sys.exit(f"HATA: logo bulunamadi: {gorsel}")
        if logo_var_mi(draft, gorsel.name):
            print("\n--- Logo ---\n  [=] logo taslakta zaten var, atlandi.")
        elif logo.get("from"):
            calistir("capcut_logo.py",
                     ["--draft", draft, "--add", str(gorsel), "--from", logo["from"]], "Logo")
        else:
            print("\n--- Logo ---\n  ! preset.json > seslendirme.logo.from bos, logo eklenemedi.")

    # 4) EFEKT (vignette + filtre track klonu)
    if "efekt" not in atla and yapilandirma.get("efekt", {}).get("from"):
        calistir("capcut_efekt_klon.py",
                 ["--draft", draft, "--from", yapilandirma["efekt"]["from"]], "Efekt/filtre klon")

    # 5) GECIS
    if "gecis" not in atla and yapilandirma.get("gecis"):
        gecis = yapilandirma["gecis"]
        gecis_arg = ["--draft", draft]
        if gecis.get("names"):
            gecis_arg += ["--names", gecis["names"]]
        if gecis.get("from"):
            gecis_arg += ["--from", gecis["from"]]
        if len(gecis_arg) > 2:
            calistir("capcut_gecis.py", gecis_arg, "Gecis")

    # 6) HOOK / VURGU TEXT
    if "text" not in atla and text_satirlari and yapilandirma.get("text_from"):
        text_arg_ortak = ["--from", yapilandirma["text_from"],
                          "--y", str(yapilandirma.get("text_y", 0.45))]
        if yapilandirma.get("text_proto"):
            text_arg_ortak += ["--proto-contains", yapilandirma["text_proto"]]
        for satir in text_satirlari:
            calistir("capcut_vurgu.py",
                     ["--draft", draft, "--vurgu", satir] + text_arg_ortak,
                     f"Text: {satir[:30]}")

    # 7) SOZLUK DUZELTMESI (kesin hatalar, sessiz)
    if "sozluk" not in atla and SOZLUK.exists():
        calistir("capcut_altyazi.py", ["--draft", draft, "--sozluk", str(SOZLUK)],
                 "Altyazi sozluk duzeltmesi")

    # 8) SUPHELI ALTYAZI RAPORU
    alt_json = CIKTI / f"{draft}_alt.json"
    subprocess.run([PY, str(SCRIPTS / "capcut_altyazi.py"), "--draft", draft,
                    "--oku", "--out", str(alt_json)], stdout=subprocess.DEVNULL)
    satirlar = json.loads(alt_json.read_text(encoding="utf-8")) if alt_json.exists() else []
    terimler = supheli.sozluk_terimleri()
    bulgular = [(s["i"], s["t"], s["metin"], supheli.supheli_nedenleri(s["metin"], terimler))
                for s in satirlar]
    bulgular = [b for b in bulgular if b[3]]

    print(f"\n=== TAMAM: {len(satirlar)} altyazi, {len(bulgular)} supheli ===")
    for sira, zaman, metin, nedenler in bulgular:
        print(f"  [{sira}] {zaman}s: \"{metin}\" -> {'; '.join(nedenler)}")
    print("\nExport haric hazir. CapCut'i AC, kontrol et, export al.")
    print("(Acilista 'kurtar/recover' dialogu cikarsa REDDET.)")


if __name__ == "__main__":
    main()
