#!/usr/bin/env python3
"""ElevenLabs Scribe — video/ses dosyasından kelime-zaman damgalı altyazı verisi çıkarır.

Kullanım:
    python scripts/transcribe.py input/video.mp4 --out texts.json
    python scripts/transcribe.py audio/clip.mp3 --out texts.json --lang tur

Çıktı JSON: tam metin + her kelimenin start/end saniyesi (karaoke altyazı için).
Anahtar repo kökündeki .env'den okunur.
"""
import argparse
import json
import mimetypes
import os
import subprocess
import sys
import tempfile
import urllib.request

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
import urllib.error
import uuid
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
VIDEO_EXT = {".mp4", ".mov", ".mkv", ".avi", ".webm"}


def ssl_baglami():
    """Bu makinede Python'un varsayilan CA bundle'i tanimsiz (cafile=None) ->
    bazi hostlarda 'certificate has expired' veriyor. certifi varsa onu kullan."""
    import ssl
    try:
        import certifi
        return ssl.create_default_context(cafile=certifi.where())
    except ImportError:
        return ssl.create_default_context()


BAGLAM = ssl_baglami()


def load_env():
    env_path = ROOT / ".env"
    if not env_path.exists():
        sys.exit("HATA: .env bulunamadi.")
    for line in env_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, _, v = line.partition("=")
        os.environ.setdefault(k.strip(), v.strip())


def extract_audio(video_path: Path) -> Path:
    """Videodan mono 16kHz mp3 ses çıkarır (Scribe için yeterli ve küçük)."""
    tmp = Path(tempfile.gettempdir()) / f"scribe_{uuid.uuid4().hex}.mp3"
    subprocess.run([
        "ffmpeg", "-hide_banner", "-loglevel", "error", "-y",
        "-i", str(video_path), "-vn", "-ac", "1", "-ar", "16000",
        "-c:a", "libmp3lame", "-q:a", "5", str(tmp)
    ], check=True)
    return tmp


def build_multipart(fields: dict, file_field: str, file_path: Path):
    """multipart/form-data gövdesini elle kurar (requests bağımlılığı olmadan)."""
    boundary = "----bluemedya" + uuid.uuid4().hex
    nl = b"\r\n"
    body = bytearray()
    for name, value in fields.items():
        body += b"--" + boundary.encode() + nl
        body += f'Content-Disposition: form-data; name="{name}"'.encode() + nl + nl
        body += str(value).encode() + nl
    mime = mimetypes.guess_type(file_path.name)[0] or "application/octet-stream"
    body += b"--" + boundary.encode() + nl
    body += f'Content-Disposition: form-data; name="{file_field}"; filename="{file_path.name}"'.encode() + nl
    body += f"Content-Type: {mime}".encode() + nl + nl
    body += file_path.read_bytes() + nl
    body += b"--" + boundary.encode() + b"--" + nl
    return bytes(body), boundary


def main():
    load_env()
    ap = argparse.ArgumentParser()
    ap.add_argument("input", help="Video veya ses dosyasi")
    ap.add_argument("--out", required=True, help="Cikti JSON yolu")
    ap.add_argument("--lang", default="tur", help="Dil kodu (varsayilan tur)")
    ap.add_argument("--model", default=os.environ.get("ELEVENLABS_STT_MODEL", "scribe_v1"))
    args = ap.parse_args()

    api_key = os.environ.get("ELEVENLABS_API_KEY")
    if not api_key:
        sys.exit("HATA: ELEVENLABS_API_KEY .env'de yok.")

    src = Path(args.input)
    if not src.exists():
        sys.exit(f"HATA: bulunamadi: {src}")

    tmp_audio = None
    if src.suffix.lower() in VIDEO_EXT:
        print("Videodan ses cikariliyor...")
        tmp_audio = extract_audio(src)
        audio_path = tmp_audio
    else:
        audio_path = src

    fields = {
        "model_id": args.model,
        "language_code": args.lang,
        "timestamps_granularity": "word",
        "diarize": "false",
    }
    body, boundary = build_multipart(fields, "file", audio_path)

    req = urllib.request.Request(
        "https://api.elevenlabs.io/v1/speech-to-text",
        data=body, method="POST", headers={
            "xi-api-key": api_key,
            "Content-Type": f"multipart/form-data; boundary={boundary}",
        })

    try:
        with urllib.request.urlopen(req, context=BAGLAM) as resp:
            data = json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        sys.exit(f"API HATASI {e.code}: {e.read().decode('utf-8','ignore')}")
    finally:
        if tmp_audio and tmp_audio.exists():
            tmp_audio.unlink()

    words = [w for w in data.get("words", []) if w.get("type") == "word"]
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"[OK] Transkript yazildi: {out}")
    print(f"Tam metin: {data.get('text','')[:200]}")
    print(f"Kelime sayisi: {len(words)}")
    if words:
        print("Ilk 8 kelime (zaman damgali):")
        for w in words[:8]:
            print(f"  {w['start']:.2f}-{w['end']:.2f}s  {w['text']}")


if __name__ == "__main__":
    main()
