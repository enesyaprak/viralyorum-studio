#!/usr/bin/env python3
"""ElevenLabs TTS — metinden Türkçe seslendirme (mp3) üretir.

Kullanım:
    python scripts/tts.py --text "Merhaba dünya" --out audio/test.mp3
    python scripts/tts.py --text-file copy.txt --out audio/vo.mp3 --voice <voice_id>

Anahtar repo kökündeki .env dosyasından okunur (ELEVENLABS_API_KEY).
Hiçbir zaman koda gömülmez.
"""
import argparse
import json
import os
import ssl
import sys
import urllib.request
import urllib.error
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def ssl_baglami():
    """Bu makinede Python'un varsayilan CA bundle'i tanimsiz (cafile=None) ->
    bazi hostlarda 'certificate has expired' veriyor. certifi varsa onu kullan."""
    try:
        import certifi
        return ssl.create_default_context(cafile=certifi.where())
    except ImportError:
        return ssl.create_default_context()


BAGLAM = ssl_baglami()


def load_env():
    """Basit .env okuyucu — repo kökündeki .env dosyasını ortam değişkenlerine yükler."""
    env_path = ROOT / ".env"
    if not env_path.exists():
        sys.exit("HATA: .env bulunamadı. .env.example'ı .env olarak kopyalayıp anahtarı doldur.")
    for line in env_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, val = line.partition("=")
        os.environ.setdefault(key.strip(), val.strip())


def main():
    load_env()
    ap = argparse.ArgumentParser()
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--text", help="Seslendirilecek metin")
    g.add_argument("--text-file", help="Metni içeren dosya")
    ap.add_argument("--out", required=True, help="Çıktı mp3 yolu")
    ap.add_argument("--voice", default=os.environ.get("ELEVENLABS_VOICE_ID"),
                    help="ElevenLabs voice_id (varsayılan .env)")
    ap.add_argument("--model", default=os.environ.get("ELEVENLABS_TTS_MODEL", "eleven_multilingual_v2"))
    # Ses ayarlari — verilmezse sesin KENDI varsayilani kullanilir (uydurma yok).
    ap.add_argument("--stability", type=float,
                    help="0-1. Dusuk = daha canli/degisken, yuksek = daha duz. Doga varsayilani 0.5")
    ap.add_argument("--similarity", type=float, help="0-1. Doga varsayilani 0.75")
    ap.add_argument("--style", type=float,
                    help="0-1. Yuksek = daha abartili/hareketli anlatim. Doga varsayilani 0.0")
    ap.add_argument("--speed", type=float,
                    help="0.7-1.2. >1 = daha hizli. Doga varsayilani 1.0")
    ap.add_argument("--speaker-boost", dest="speaker_boost", action="store_true",
                    help="Sesi one cikar (netlik/varlik)")
    args = ap.parse_args()

    api_key = os.environ.get("ELEVENLABS_API_KEY")
    if not api_key:
        sys.exit("HATA: ELEVENLABS_API_KEY .env'de tanımlı değil.")
    if not args.voice:
        sys.exit("HATA: voice_id yok. --voice ver veya .env'e ELEVENLABS_VOICE_ID ekle.")

    text = args.text if args.text else Path(args.text_file).read_text(encoding="utf-8")
    text = text.strip()
    print(f"Metin: {len(text)} karakter (~{len(text)} kredi)")

    url = (f"https://api.elevenlabs.io/v1/text-to-speech/{args.voice}"
           f"?output_format=mp3_44100_128")
    govde = {"text": text, "model_id": args.model}

    # Sadece VERILEN ayarlari gonder; hicbiri yoksa voice_settings hic gonderilmez
    # ve ElevenLabs sesin kendi varsayilanini kullanir.
    ayarlar = {}
    if args.stability is not None:
        ayarlar["stability"] = args.stability
    if args.similarity is not None:
        ayarlar["similarity_boost"] = args.similarity
    if args.style is not None:
        ayarlar["style"] = args.style
    if args.speed is not None:
        ayarlar["speed"] = args.speed
    if args.speaker_boost:
        ayarlar["use_speaker_boost"] = True
    if ayarlar:
        govde["voice_settings"] = ayarlar
        print(f"Ses ayarlari: {ayarlar}")

    payload = json.dumps(govde).encode("utf-8")
    req = urllib.request.Request(url, data=payload, method="POST", headers={
        "xi-api-key": api_key,
        "Content-Type": "application/json",
        "Accept": "audio/mpeg",
    })

    try:
        with urllib.request.urlopen(req, context=BAGLAM) as resp:
            audio = resp.read()
    except urllib.error.HTTPError as e:
        sys.exit(f"API HATASI {e.code}: {e.read().decode('utf-8', 'ignore')}")

    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_bytes(audio)
    print(f"[OK] Seslendirme yazildi: {out} ({len(audio)//1024} KB)")


if __name__ == "__main__":
    main()
