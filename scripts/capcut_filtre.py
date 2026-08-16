#!/usr/bin/env python3
"""Video kliplerine bir filtre efekti ekler (kaynak taslaktan klonlayarak).

CapCut filtresi = materials.effects içinde type:filter obje; her video segmentinin
extra_material_refs'ine referans eklenir. Varsayılan: 'Bold Saturation' (bymdoor'dan).

Kullanım:
    python scripts/capcut_filtre.py --draft "istikbal-banaz-5"
    python scripts/capcut_filtre.py --draft "X" --from "bymdoor" --name "Bold Saturation"
"""
import argparse
import copy
import json
import os
import sys
import uuid
from pathlib import Path

DRAFTS = Path(os.environ["LOCALAPPDATA"]) / "CapCut Drafts"
nid = lambda: str(uuid.uuid4()).upper()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--draft", required=True)
    ap.add_argument("--from", dest="src", default="bymdoor", help="filtrenin alınacağı taslak")
    ap.add_argument("--name", default="Bold Saturation", help="filtre adı")
    args = ap.parse_args()
    import capcut_guard
    capcut_guard.dur_capcut_acikken()

    sf = json.loads((DRAFTS / args.src / "draft_content.json").read_text(encoding="utf-8"))
    proto = next((e for e in sf["materials"].get("effects", [])
                  if e.get("type") == "filter" and args.name.lower() in str(e.get("name", "")).lower()), None)
    if not proto:
        sys.exit(f"HATA: '{args.name}' filtresi '{args.src}' içinde yok.")

    dc_path = DRAFTS / args.draft / "draft_content.json"
    dc = json.loads(dc_path.read_text(encoding="utf-8"))
    m = dc["materials"]

    added = 0
    for t in dc["tracks"]:
        if t.get("type") != "video":
            continue
        for s in t["segments"]:
            # zaten bu filtre varsa atla
            if any(r for r in s.get("extra_material_refs", [])
                   if any(e["id"] == r and args.name.lower() in str(e.get("name", "")).lower()
                          for e in m.get("effects", []))):
                continue
            nf = copy.deepcopy(proto); nf["id"] = nid()
            m.setdefault("effects", []).append(nf)
            s.setdefault("extra_material_refs", []).append(nf["id"])
            added += 1

    dc_path.write_text(json.dumps(dc, ensure_ascii=False), encoding="utf-8")
    import capcut_sync; capcut_sync.sync(dc_path.parent, quiet=True)
    print(f"[OK] '{args.name}' filtresi {added} klibe eklendi -> {args.draft}")


if __name__ == "__main__":
    main()
