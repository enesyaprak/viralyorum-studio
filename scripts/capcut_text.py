#!/usr/bin/env python3
"""CapCut taslağındaki düz başlık/yazıları yeni metinlerle değiştirir.

Eslina tipi akış için: şablondaki 4 başlığı (MİNİK BEYLER İÇİN... vb.) müşterinin
verdiği yeni metinlerle değiştirir. Stil korunur; sadece metin + stil aralığı güncellenir.
Metinler, text segmentlerine zaman sırasına göre 1:1 eşlenir.

Yeni metin dosyası: JSON dizisi (her eleman bir başlık; \\n satır içi kullanılabilir).
    ["YENİ BAŞLIK 1\\nİKİNCİ SATIR", "YENİ BAŞLIK 2\\n\\nAlt başlık", ...]

Kullanım:
    python scripts/capcut_text.py --draft "ESL-1" --headlines input/esl1_basliklar.json
"""
import argparse
import json
import os
import sys
from pathlib import Path

DRAFTS = Path(os.environ["LOCALAPPDATA"]) / "CapCut Drafts"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--draft", required=True)
    ap.add_argument("--headlines", required=True, help="JSON dizisi: yeni başlık metinleri")
    args = ap.parse_args()

    folder = DRAFTS / args.draft
    dc_path = folder / "draft_content.json"
    if not dc_path.exists():
        sys.exit(f"HATA: taslak yok: {dc_path}")

    new_texts = json.loads(Path(args.headlines).read_text(encoding="utf-8"))
    if not isinstance(new_texts, list):
        sys.exit("HATA: --headlines bir JSON string dizisi olmalı.")

    dc = json.loads(dc_path.read_text(encoding="utf-8"))
    m = dc["materials"]
    texts_by_id = {t["id"]: t for t in m.get("texts", [])}

    # text track segmentleri, zaman sırasına göre
    ttrack = next((t for t in dc["tracks"] if t.get("type") == "text"), None)
    if not ttrack:
        sys.exit("HATA: text track yok.")
    segs = sorted(ttrack["segments"], key=lambda s: s.get("target_timerange", {}).get("start", 0))

    n = min(len(new_texts), len(segs))
    if len(new_texts) != len(segs):
        print(f"UYARI: {len(new_texts)} yeni metin, {len(segs)} başlık segmenti. İlk {n} eşlenecek.")

    changed = 0
    for i in range(n):
        seg = segs[i]
        tx = texts_by_id.get(seg["material_id"])
        if not tx:
            print(f"  atlandı (segment {i}: texts bulunamadı)")
            continue
        content = json.loads(tx["content"]) if isinstance(tx["content"], str) else tx["content"]
        new = new_texts[i]
        content["text"] = new
        if content.get("styles"):
            content["styles"][0]["range"] = [0, len(new)]
            content["styles"] = [content["styles"][0]]
        tx["content"] = json.dumps(content, ensure_ascii=False)
        changed += 1
        print(f"  [{i}] -> {new[:40]!r}")

    dc_path.write_text(json.dumps(dc, ensure_ascii=False), encoding="utf-8")
    print(f"[OK] {changed} başlık değiştirildi -> {args.draft}")


if __name__ == "__main__":
    main()
