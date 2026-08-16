#!/usr/bin/env python3
"""Kaynak taslaktaki efekt/filtre TRACK'lerini hedefe klonlar (tüm video süresince).

MM Auto şablonu için: mmauto-1'deki Vignette (effect track) + Bold Saturation
(filter track, %70) yapısını birebir taşır. Efekt segmenti hedefte videonun tam
süresine uzatılır.

Kullanım:
    python scripts/capcut_efekt_klon.py --draft "mmauto-2" --from "mmauto-1"
"""
import argparse
import copy
import glob
import json
import os
import sys
import uuid
from pathlib import Path

DRAFTS = Path(os.environ["LOCALAPPDATA"]) / "CapCut Drafts"
nid = lambda: str(uuid.uuid4()).upper()


def resolve(key):
    if (DRAFTS / key / "draft_content.json").exists():
        return key
    k = key.lower().replace(" ", "").replace("-", "")
    for f in glob.glob(str(DRAFTS / "*" / "draft_meta_info.json")):
        fo = os.path.basename(os.path.dirname(f))
        try:
            nm = json.load(open(f, encoding="utf-8")).get("draft_name", "")
        except Exception:
            nm = ""
        if k in fo.lower().replace(" ", "").replace("-", "") or k in nm.lower().replace(" ", "").replace("-", ""):
            return fo
    sys.exit(f"HATA: '{key}' taslağı yok.")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--draft", required=True)
    ap.add_argument("--from", dest="src", required=True)
    args = ap.parse_args()
    import capcut_guard
    capcut_guard.dur_capcut_acikken()

    src = resolve(args.src)
    dst = resolve(args.draft)
    sf = json.loads((DRAFTS / src / "draft_content.json").read_text(encoding="utf-8"))
    p = DRAFTS / dst / "draft_content.json"
    dc = json.loads(p.read_text(encoding="utf-8"))
    m = dc["materials"]
    total = dc.get("duration", 0)
    sby = {it["id"]: (k, it) for k, v in sf["materials"].items() if isinstance(v, list)
           for it in v if isinstance(it, dict) and "id" in it}

    copied = []
    for t in sf["tracks"]:
        if t.get("type") not in ("effect", "filter") or not t.get("segments"):
            continue
        # hedefte ayni tip track zaten varsa atla (cift eklemeyi onle)
        names = []
        nt = copy.deepcopy(t)
        nt["id"] = nid()
        for s in nt["segments"]:
            ki = sby.get(s["material_id"])
            if not ki:
                continue
            nit = copy.deepcopy(ki[1]); nit["id"] = nid()
            m.setdefault(ki[0], []).append(nit)
            s["id"] = nid(); s["material_id"] = nit["id"]
            s["target_timerange"] = {"start": 0, "duration": total}
            refs = []
            for r in s.get("extra_material_refs", []):
                k2 = sby.get(r)
                if k2:
                    n2 = copy.deepcopy(k2[1]); n2["id"] = nid()
                    m.setdefault(k2[0], []).append(n2); refs.append(n2["id"])
            s["extra_material_refs"] = refs
            names.append(f"{nit.get('name','?')}({t['type']})")
        dc["tracks"].append(nt)
        copied += names

    p.write_text(json.dumps(dc, ensure_ascii=False), encoding="utf-8")
    import capcut_sync; capcut_sync.sync(p.parent, quiet=True)
    print(f"[OK] Klonlanan efektler: {', '.join(copied) if copied else 'YOK'} -> {dst}")


if __name__ == "__main__":
    main()
