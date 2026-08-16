#!/usr/bin/env python3
"""Video segmentlerine MANUEL keyframe zoom (easing-in punch) ekler.

Animations sekmesine (In/Out/Combo preset) DOKUNMAZ. Bunun yerine her segmente
scale (X+Y) keyframe'i koyar: başta %100, sonda %amount -> yavaşça yakınlaşan ufak
vurgu zoom'u. Varsa eski 'Zoom' preset animasyonlarını da temizler.

Kullanım:
    python scripts/capcut_zoom.py --draft "zeus 4" --amount 1.08
"""
import argparse
import json
import os
import sys
import uuid
from pathlib import Path

DRAFTS = Path(os.environ["LOCALAPPDATA"]) / "CapCut Drafts"
nid = lambda: str(uuid.uuid4()).upper()


def kf(time_us, val):
    return {"curveType": "Line", "graphID": "", "id": nid(),
            "left_control": {"x": 0.0, "y": 0.0}, "right_control": {"x": 0.0, "y": 0.0},
            "string_value": "", "time_offset": int(time_us), "values": [val]}


def scale_group(dur_us, amount, prop):
    return {"id": nid(), "keyframe_list": [kf(0, 1.0), kf(dur_us, amount)],
            "material_id": "", "property_type": prop}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--draft", required=True)
    ap.add_argument("--amount", type=float, default=1.08, help="bitis zoom orani (1.08 = yuzde 8, ufak vurgu)")
    ap.add_argument("--segments", help="sadece bu klip indeksleri (zaman sirasi, virgulle: '0,3'). Bossa hepsi.")
    ap.add_argument("--clear", action="store_true", help="once mevcut scale keyframe'lerini temizle")
    args = ap.parse_args()
    hedef = None if not args.segments else {int(x) for x in args.segments.split(",") if x.strip() != ""}

    dc_path = DRAFTS / args.draft / "draft_content.json"
    dc = json.loads(dc_path.read_text(encoding="utf-8"))
    m = dc["materials"]
    by_id = {it["id"]: (k, it) for k, v in m.items() if isinstance(v, list)
             for it in v if isinstance(it, dict) and "id" in it}

    vtracks = [t for t in dc["tracks"] if t.get("type") == "video"]
    main_tr = max(vtracks, key=lambda t: len(t["segments"]))

    segs = sorted(main_tr["segments"], key=lambda s: s["target_timerange"]["start"])
    added = 0
    for i, s in enumerate(segs):
        ck = s.setdefault("common_keyframes", [])
        if args.clear:  # eski scale keyframe gruplarini sil (yeniden hedefleme icin)
            ck[:] = [g for g in ck if g.get("property_type") not in ("KFTypeScaleX", "KFTypeScaleY")]
        if hedef is not None and i not in hedef:
            continue
        # eski preset zoom animasyonlarını temizle (Animations sekmesi)
        for r in s.get("extra_material_refs", []):
            ki = by_id.get(r)
            if ki and ki[0] == "material_animations":
                ki[1]["animations"] = [a for a in ki[1].get("animations", [])
                                       if "zoom" not in str(a.get("name", "")).lower()]
        # mevcut scale keyframe'i varsa atla
        if any(g.get("property_type") in ("KFTypeScaleX", "KFTypeScaleY") for g in ck):
            continue
        dur = s["target_timerange"]["duration"]
        ck.append(scale_group(dur, args.amount, "KFTypeScaleX"))
        ck.append(scale_group(dur, args.amount, "KFTypeScaleY"))
        added += 1

    dc_path.write_text(json.dumps(dc, ensure_ascii=False), encoding="utf-8")
    import capcut_sync; capcut_sync.sync(dc_path.parent, quiet=True)
    print(f"[OK] Keyframe zoom (%{round((args.amount-1)*100)}) {added} segmente eklendi -> {args.draft}")


if __name__ == "__main__":
    main()
