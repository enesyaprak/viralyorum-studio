#!/usr/bin/env python3
"""Transkript JSON -> karaoke ASS altyazi.

Scribe (transcribe.py) ciktisindaki kelime-zaman damgalarini alir, Bluemedya
tarzi karaoke altyazi (.ass) uretir: kelime kelime, aktif kelime SARI, digerleri
beyaz + siyah kontur, alt-orta.

Kullanim:
    python scripts/captions.py output/ronesans_FULL_transkript.json --out output/ronesans.ass
    # sonra ffmpeg ile yakma:
    # ffmpeg -i video.mp4 -vf "subtitles=output/ronesans.ass" out.mp4
"""
import argparse
import json
from pathlib import Path


def cs(t: float) -> str:
    """Saniye -> ASS zaman formati H:MM:SS.cc"""
    h = int(t // 3600)
    m = int((t % 3600) // 60)
    s = int(t % 60)
    c = int(round((t - int(t)) * 100))
    if c == 100:
        c = 0
        s += 1
    return f"{h}:{m:02d}:{s:02d}.{c:02d}"


def chunk_words(words, max_words, pause):
    """Kelimeleri kisa gruplara boler: max kelime, uzun duraklama veya cumle sonu."""
    chunks, cur = [], []
    for i, w in enumerate(words):
        cur.append(w)
        last = w.get("raw", w["text"]).rstrip().endswith((".", "!", "?", ":"))
        gap_next = (i + 1 < len(words)) and (words[i + 1]["start"] - w["end"] > pause)
        if len(cur) >= max_words or last or gap_next or i == len(words) - 1:
            chunks.append(cur)
            cur = []
    return chunks


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("json", help="transcribe.py cikti JSON")
    ap.add_argument("--out", required=True, help="cikti .ass")
    ap.add_argument("--res", default="1080x1920", help="video cozunurlugu WxH")
    ap.add_argument("--font", default="Arial", help="font ailesi (Roboto kuruluysa: Roboto)")
    ap.add_argument("--fontsize", type=int, default=78)
    ap.add_argument("--max-words", type=int, default=3)
    ap.add_argument("--pause", type=float, default=0.45)
    ap.add_argument("--marginv", type=int, default=240, help="alttan bosluk (logo icin)")
    ap.add_argument("--highlight", default="&H0000FFFF&", help="ASS BGR sari varsayilan")
    args = ap.parse_args()

    W, H = (int(x) for x in args.res.lower().split("x"))
    data = json.loads(Path(args.json).read_text(encoding="utf-8"))
    def clean(t: str) -> str:
        return t.strip().strip(",.;:!?“”\"'()").strip()

    words = []
    for w in data.get("words", []):
        if w.get("type") != "word":
            continue
        t = clean(w["text"])
        if not any(ch.isalnum() for ch in t):  # salt noktalama token'lari at
            continue
        w = dict(w)
        w["raw"] = w["text"]
        w["text"] = t
        words.append(w)
    if not words:
        raise SystemExit("HATA: JSON'da kelime yok.")

    WHITE = "&H00FFFFFF&"
    head = f"""[Script Info]
ScriptType: v4.00+
PlayResX: {W}
PlayResY: {H}
WrapStyle: 2
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, OutlineColour, BackColour, Bold, Italic, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Karaoke,{args.font},{args.fontsize},{WHITE},&H00000000&,&H64000000&,-1,0,1,4,1,2,60,60,{args.marginv},1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, Effect, Text
"""

    lines = []
    chunks = chunk_words(words, args.max_words, args.pause)
    for chunk in chunks:
        for i, w in enumerate(chunk):
            start = w["start"]
            end = chunk[i + 1]["start"] if i + 1 < len(chunk) else w["end"]
            if end <= start:
                end = start + 0.05
            parts = []
            for j, cw in enumerate(chunk):
                txt = cw["text"].strip()
                if j == i:
                    parts.append(f"{{\\c{args.highlight}}}{txt}{{\\c{WHITE}}}")
                else:
                    parts.append(txt)
            text = " ".join(parts)
            lines.append(f"Dialogue: 0,{cs(start)},{cs(end)},Karaoke,,0,0,,{text}")

    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(head + "\n".join(lines) + "\n", encoding="utf-8")
    print(f"[OK] ASS yazildi: {out}  ({len(chunks)} grup, {len(lines)} olay)")


if __name__ == "__main__":
    main()
