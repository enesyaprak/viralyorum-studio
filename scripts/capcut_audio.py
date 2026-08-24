#!/usr/bin/env python3
"""CapCut taslağındaki seslendirmeyi (TTS) yeni bir ses dosyasıyla değiştirir.

Eslina tipi akış için: şablondaki ElevenLabs TTS seslendirmesini, bizim ürettiğimiz
yeni TTS ile değiştirir. Eşleşen ses materyalinin yolunu+süresini günceller ve o sesin
track segmentlerini TEK segmente toplar [0, yeni_süre] (parça split'ini sadeleştirir).

Kullanım:
    python scripts/capcut_audio.py --draft "ESL-1" --audio audio/yeni_vo.mp3 --match ElevenLabs
"""
import argparse
import copy
import json
import os
import subprocess
import sys
import uuid
from pathlib import Path

DRAFTS = Path(os.environ["LOCALAPPDATA"]) / "CapCut Drafts"


def audio_dur_us(path):
    out = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                          "-of", "json", str(path)], capture_output=True, text=True, check=True).stdout
    return int(float(json.loads(out)["format"]["duration"]) * 1_000_000)


def cc_path(p):
    return str(Path(p).resolve()).replace("\\", "/")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--draft", required=True)
    ap.add_argument("--audio", required=True, help="Yeni ses dosyası (mp3/wav)")
    ap.add_argument("--match", default="ElevenLabs", help="Değiştirilecek ses materyalinin adında geçen ifade")
    args = ap.parse_args()

    folder = DRAFTS / args.draft
    dc_path = folder / "draft_content.json"
    if not dc_path.exists():
        sys.exit(f"HATA: taslak yok: {dc_path}")
    new_path = cc_path(args.audio)
    if not Path(args.audio).exists():
        sys.exit(f"HATA: ses dosyası yok: {args.audio}")
    new_dur = audio_dur_us(args.audio)

    dc = json.loads(dc_path.read_text(encoding="utf-8"))
    m = dc["materials"]

    # eşleşen ses materyalleri (TTS)
    matched = [a for a in m.get("audios", []) if args.match.lower() in str(a.get("name", "")).lower()]
    if not matched:
        sys.exit(f"HATA: '{args.match}' içeren ses materyali yok. Mevcut: "
                 + ", ".join(str(a.get('name'))[:20] for a in m.get('audios', [])))
    old_paths = {a.get("path") for a in matched if a.get("path")}
    matched_ids = {a["id"] for a in matched}

    # materyal yolu+süre güncelle
    for a in matched:
        a["path"] = new_path
        a["duration"] = new_dur

    # ses track'lerinde bu materyalleri kullanan segmentleri TEK segmente topla
    keep_mat = matched[0]["id"]
    for tr in dc.get("tracks", []):
        if tr.get("type") != "audio":
            continue
        segs = tr.get("segments", [])
        mine = [s for s in segs if s.get("material_id") in matched_ids]
        if not mine:
            continue
        proto = copy.deepcopy(mine[0])
        proto["id"] = str(uuid.uuid4()).upper()
        proto["material_id"] = keep_mat
        proto["source_timerange"] = {"start": 0, "duration": new_dur}
        proto["target_timerange"] = {"start": 0, "duration": new_dur}
        # bu track'ten eski TTS segmentlerini çıkar, tek yeni segment koy
        tr["segments"] = [s for s in segs if s.get("material_id") not in matched_ids] + [proto]

    # diğer JSON dosyalarında eski ses yolunu yenisiyle değiştir (meta vb.)
    dc_path.write_text(json.dumps(dc, ensure_ascii=False), encoding="utf-8")
    for jf in folder.rglob("*.json"):
        if jf.name == "draft_content.json":
            continue
        try:
            txt = jf.read_text(encoding="utf-8")
        except Exception:
            continue
        orig = txt
        for op in old_paths:
            if op:
                txt = txt.replace(op, new_path)
        if txt != orig:
            jf.write_text(txt, encoding="utf-8")

    # Ayna dosyalari guncelle (rglob path-degisiminden SONRA: dc kopyasi en guncel kalsin)
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    import capcut_sync; capcut_sync.sync(folder, quiet=True)

    print(f"[OK] Ses değiştirildi: {Path(args.audio).name} ({round(new_dur/1e6,1)}s) -> {args.draft}")
    print(f"  {len(matched)} ses materyali güncellendi, segmentler tek parçaya toplandı.")


if __name__ == "__main__":
    main()
