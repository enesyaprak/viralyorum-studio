#!/usr/bin/env python3
"""Supheli altyazi dedektoru.

Scribe (STT) guven skoru vermiyor; supheyi metnin KENDISINDEN sezgisel yakalariz.
Amac: yanlis-pozitif olsa da Enes'in bakmasi gereken KISA bir liste uretmek.

viralyorum'da VO'yu biz uretiyoruz (ElevenLabs TTS), o yuzden ASR hatasi az —
ama bilimsel/tur adlari (solungac, sefalopod, biyolüminesans) hala bozulabiliyor.

bluemedya bir_video.py'deki dedektorden turetildi; marka kavrami yerine
sozluk terimleri (presets/altyazi_sozluk.json > terimler) kullanilir.
"""
import json
import re
import unicodedata
from pathlib import Path

KOK = Path(__file__).resolve().parent.parent
SOZLUK = KOK / "presets" / "altyazi_sozluk.json"

TR = "abcçdefgğhıijklmnoöprsştuüvyzABCÇDEFGĞHIİJKLMNOÖPRSŞTUÜVYZ"


def tr_lower(s):
    """Turkce-duyarli kucult + birlesen aksan isaretlerini temizle (İ->i sorununu cozer)."""
    s = s.replace("İ", "i").replace("I", "ı")
    s = s.lower()
    return "".join(c for c in unicodedata.normalize("NFC", s)
                   if not unicodedata.combining(c))


def _yakin(a, b):
    """a ve b birbirine 1 duzenleme mesafesinde mi (basit Levenshtein <= 1)."""
    if abs(len(a) - len(b)) > 1:
        return False
    if a == b:
        return False
    if len(a) == len(b):
        return sum(x != y for x, y in zip(a, b)) == 1
    kisa, uzun = (a, b) if len(a) < len(b) else (b, a)
    farklar = i = j = 0
    while i < len(kisa) and j < len(uzun):
        if kisa[i] == uzun[j]:
            i += 1
            j += 1
        else:
            farklar += 1
            j += 1
            if farklar > 1:
                return False
    return True


def supheli_nedenleri(metin, terimler=()):
    m = metin.strip()
    low = tr_lower(m)
    nedenler = []

    # 1) Rakam iceren satir — ASR/TTS en cok burada yaniliyor (yas, agirlik, derinlik)
    if re.search(r"\d", m):
        nedenler.append("rakam var (sayi/birim kontrol)")

    # 2) Turkce olmayan karakter (ASR copu)
    yabanci = [c for c in m if not (c in TR or c.isdigit() or c in " .,!?'’-%₺&:/()")]
    if yabanci:
        nedenler.append(f"garip karakter: {''.join(dict.fromkeys(yabanci))[:6]}")

    # 3) Bitisik tekrar eden kelime ("ve ve", "bu bu")
    kelimeler = re.findall(r"\w+", low, re.UNICODE)
    for a, b in zip(kelimeler, kelimeler[1:]):
        if a == b and len(a) > 1:
            nedenler.append(f"tekrar: '{a} {a}'")
            break

    # 4) Tek harflik anlamsiz token ('o' gecerli tek-harf TR kelimesi, haric)
    #    Rakamlar haric tutulur: tek haneli sayi normaldir ("3 bin metre") ve
    #    zaten 1. kuralda isaretleniyor - iki kere flag'lemek gurultu yapiyordu.
    if kelimeler and any(len(k) == 1 and k != "o" and not k.isdigit() for k in kelimeler):
        nedenler.append("tek harflik token")

    # 5) Sozluk terimine BENZEYEN ama tam eslesmeyen kelime (yanlis yazilmis terim?)
    for terim in terimler:
        t = tr_lower(terim)
        if t and t not in low:
            for k in kelimeler:
                if len(k) >= 4 and _yakin(k, t):
                    nedenler.append(f"'{terim}' yanlis olabilir: '{k}'")
                    break

    return nedenler


def sozluk_terimleri():
    """Sozlukteki duzeltme HEDEFLERINDEN (dogru yazimlardan) terim listesi cikar."""
    terimler = set()
    try:
        sozluk = json.loads(SOZLUK.read_text(encoding="utf-8"))
    except Exception:
        return []
    # Sema bluemedya ile AYNI ("global" + "markalar") ki kopyalanan
    # capcut_altyazi.py --sozluk hic degistirilmeden calissin.
    # Bu repoda "markalar" = konu grubu (deniz, kus, bocek...).
    kurallar = list(sozluk.get("global", []))
    for kural_listesi in sozluk.get("markalar", {}).values():
        kurallar += kural_listesi
    for _, dogru in kurallar:
        for kelime in re.findall(r"[A-Za-zÇĞİÖŞÜçğıöşü]{4,}", dogru):
            terimler.add(kelime)
    return sorted(terimler)


def rapor(satirlar, terimler=None):
    """satirlar: [{'metin': ...}, ...] -> supheli olanlarin (index, metin, nedenler) listesi."""
    if terimler is None:
        terimler = sozluk_terimleri()
    bulgular = []
    for sira, satir in enumerate(satirlar):
        metin = satir if isinstance(satir, str) else (satir.get("metin") or satir.get("text") or "")
        nedenler = supheli_nedenleri(metin, terimler)
        if nedenler:
            bulgular.append((sira, metin, nedenler))
    return bulgular
