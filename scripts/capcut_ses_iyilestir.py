#!/usr/bin/env python3
"""Video segmentlerine reduce noise (gürültü azaltma) + enhance voice ekler.

Konuşma video kliplerinin içinde olduğu için (talking-head) işlemler video
segmentlerine uygulanır. Reduce noise realtime (sağlam); enhance voice CapCut'ın
render'ı gerekebilir (tutmazsa CapCut'ta tek tık).

Kullanım:
    python scripts/capcut_ses_iyilestir.py --draft "zeus 8"
"""
import argparse
import glob
import json
import os
import sys
import uuid
from pathlib import Path

DRAFTS = Path(os.environ["LOCALAPPDATA"]) / "CapCut Drafts"
CAPCUT = Path(os.environ["LOCALAPPDATA"]) / "CapCut"
nid = lambda: str(uuid.uuid4()).upper()


def denoise_model():
    cands = sorted(glob.glob(str(CAPCUT / "Apps" / "*" / "Resources" / "audiosami" /
                                 "unet_denoise_44k_music_model_v1.0.model")))
    if not cands:
        sys.exit("HATA: denoise modeli bulunamadı.")
    return str(Path(cands[-1])).replace("\\", "/")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--draft", required=True)
    ap.add_argument("--rate", type=float, default=0.85, help="gürültü azaltma oranı")
    ap.add_argument("--no-voice", action="store_true", help="sadece denoise, voice enhance ekleme")
    args = ap.parse_args()

    dc_path = DRAFTS / args.draft / "draft_content.json"
    dc = json.loads(dc_path.read_text(encoding="utf-8"))
    m = dc["materials"]
    model = denoise_model()

    n = 0
    for t in dc["tracks"]:
        if t.get("type") != "video":
            continue
        for s in t["segments"]:
            refs = s.setdefault("extra_material_refs", [])
            # reduce noise
            dn = {"denoise_mode": 1.0, "denoise_rate": args.rate, "id": nid(),
                  "is_denoise": True, "path": model, "sami_name": "denoise_v2",
                  "sami_type": 2, "sami_version": "1.0", "type": "realtime_denoise"}
            m.setdefault("realtime_denoises", []).append(dn)
            refs.append(dn["id"])
            # enhance voice
            if not args.no_voice:
                dur = s.get("source_timerange", {}).get("duration", 0)
                vb = {"ambient_sound_level": 25, "enable": True, "id": nid(),
                      "production_path": "", "time_range": {"start": 0, "duration": dur},
                      "type": "vocal_beautify", "voice_change_mode": None}
                m.setdefault("vocal_beautifys", []).append(vb)
                refs.append(vb["id"])
            n += 1

    dc_path.write_text(json.dumps(dc, ensure_ascii=False), encoding="utf-8")
    import capcut_sync; capcut_sync.sync(dc_path.parent, quiet=True)
    print(f"[OK] {n} segmente reduce noise" + ("" if args.no_voice else " + enhance voice") + f" -> {args.draft}")


if __name__ == "__main__":
    main()
