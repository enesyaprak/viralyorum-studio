#!/usr/bin/env python3
"""Geçiş noktalarına whoosh (Buon) ses efekti yerleştirir.

Hedef taslaktaki geçişleri (geçiş referansı olan video segmentlerinin sonu) bulur,
kaynak şablondaki whoosh ses elementini kopyalayıp her geçişe bir whoosh koyar.

Kullanım:
    python scripts/capcut_whoosh.py --draft "RONESANS2-cc-1" --from "zeus-1"
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
    ap.add_argument("--from", dest="src", required=True, help="whoosh elementinin alınacağı şablon")
    ap.add_argument("--match", default="Buon", help="whoosh ses materyali adı")
    ap.add_argument("--lead", type=float, default=0.3, help="whoosh geçişten kaç sn önce başlasın")
    args = ap.parse_args()

    dc_path = DRAFTS / args.draft / "draft_content.json"
    dc = json.loads(dc_path.read_text(encoding="utf-8"))
    m = dc["materials"]

    # hedefteki geçiş noktaları (geçiş ref'i olan video segmentin sonu)
    tr_ids = {t["id"] for t in m.get("transitions", [])}
    points = []
    for t in dc["tracks"]:
        if t.get("type") == "video":
            for s in t["segments"]:
                if any(r in tr_ids for r in s.get("extra_material_refs", [])):
                    points.append(s["target_timerange"]["start"] + s["target_timerange"]["duration"])
    points = sorted(set(points))
    if not points:
        sys.exit("HATA: geçiş bulunamadı.")
    print(f"Geçiş noktaları: {[round(p/1e6,2) for p in points]}")

    # kaynak whoosh elementi
    sf = json.loads((DRAFTS / args.src / "draft_content.json").read_text(encoding="utf-8"))
    sm = sf["materials"]
    sby = {it["id"]: (k, it) for k, v in sm.items() if isinstance(v, list)
           for it in v if isinstance(it, dict) and "id" in it}
    wmat = next((a for a in sm["audios"] if args.match.lower() in str(a.get("name", "")).lower()), None)
    if not wmat:
        sys.exit(f"HATA: '{args.src}' içinde '{args.match}' ses materyali yok.")
    if not os.path.exists(wmat.get("path", "")):
        sys.exit(f"HATA: whoosh dosyası yok: {wmat.get('path')}")
    wseg = next((s for t in sf["tracks"] if t["type"] == "audio"
                 for s in t["segments"] if s["material_id"] == wmat["id"]), None)
    if not wseg:
        sys.exit("HATA: kaynak whoosh segmenti yok.")
    wdur = wseg["source_timerange"]["duration"]

    # whoosh materyalini hedefe ekle (bir kez)
    new_mat = copy.deepcopy(wmat); new_mat["id"] = nid()
    m.setdefault("audios", []).append(new_mat)

    # her geçişe whoosh segmenti
    new_segs = []
    lead_us = int(args.lead * 1e6)
    for p in points:
        ns = copy.deepcopy(wseg); ns["id"] = nid(); ns["material_id"] = new_mat["id"]
        start = max(0, p - lead_us)
        ns["source_timerange"] = {"start": 0, "duration": wdur}
        ns["target_timerange"] = {"start": start, "duration": wdur}
        # extra ref materyallerini kopyala (speed, beats, sound_channel_mapping vb.)
        refs = []
        for r in ns.get("extra_material_refs", []):
            ki = sby.get(r)
            if not ki:
                continue
            nit = copy.deepcopy(ki[1]); nit["id"] = nid()
            m.setdefault(ki[0], []).append(nit)
            refs.append(nit["id"])
        ns["extra_material_refs"] = refs
        new_segs.append(ns)

    dc["tracks"].append({"type": "audio", "attribute": 0, "flag": 0, "id": nid(),
                         "segments": new_segs, "is_default_name": True, "name": ""})
    dc_path.write_text(json.dumps(dc, ensure_ascii=False), encoding="utf-8")
    import capcut_sync; capcut_sync.sync(dc_path.parent, quiet=True)
    print(f"[OK] {len(new_segs)} whoosh sesi eklendi -> {args.draft}")


if __name__ == "__main__":
    main()
