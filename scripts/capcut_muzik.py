#!/usr/bin/env python3
"""Taslağa arka plan müziği ekler (kaynak şablondaki müzik elementini kopyalayarak).

Video süresince uzanan bir müzik track'i ekler, sesi arka plan seviyesine düşürür.

Kullanım:
    python scripts/capcut_muzik.py --draft "0623" --from "eslina kids-1" --match "Happy Upbeat" --volume 0.22
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
    ap.add_argument("--from", dest="src", required=True, help="müziğin alınacağı şablon")
    ap.add_argument("--match", default="", help="müzik materyali adı (boşsa ilk 'music')")
    ap.add_argument("--volume", type=float, default=0.22, help="ses seviyesi (müzik 0.22, voiceover 1.0)")
    ap.add_argument("--audio", help="harici ses dosyası (verilirse müzik yerine bu eklenir; voiceover için)")
    args = ap.parse_args()
    if not (DRAFTS / args.draft / "draft_content.json").exists():
        import glob as _g
        _k = args.draft.lower().replace(" ", "")
        for _f in _g.glob(str(DRAFTS / "*" / "draft_meta_info.json")):
            _fo = os.path.basename(os.path.dirname(_f))
            try:
                _nm = json.load(open(_f, encoding="utf-8")).get("draft_name", "")
            except Exception:
                _nm = ""
            if _k in _fo.lower().replace(" ", "") or _k in _nm.lower().replace(" ", ""):
                args.draft = _fo
                break
    import capcut_guard
    capcut_guard.dur_capcut_acikken()

    dc_path = DRAFTS / args.draft / "draft_content.json"
    dc = json.loads(dc_path.read_text(encoding="utf-8"))
    m = dc["materials"]
    total = dc.get("duration", 0)

    sf = json.loads((DRAFTS / args.src / "draft_content.json").read_text(encoding="utf-8"))
    sm = sf["materials"]
    sby = {it["id"]: (k, it) for k, v in sm.items() if isinstance(v, list)
           for it in v if isinstance(it, dict) and "id" in it}
    mus = None
    for a in sm.get("audios", []):
        if a.get("type") == "music" and (not args.match or args.match.lower() in str(a.get("name", "")).lower()):
            mus = a; break
    if not mus:
        sys.exit(f"HATA: '{args.src}' içinde müzik yok ('{args.match}').")
    if not os.path.exists(mus.get("path", "")):
        sys.exit(f"HATA: müzik dosyası yok: {mus.get('path')}")
    mseg = next((s for t in sf["tracks"] if t["type"] == "audio"
                 for s in t["segments"] if s["material_id"] == mus["id"]), None)

    nm = copy.deepcopy(mus); nm["id"] = nid()
    # harici ses dosyası verildiyse (voiceover): yolu+süreyi onunla değiştir
    if args.audio:
        import subprocess
        if not os.path.exists(args.audio):
            sys.exit(f"HATA: ses dosyası yok: {args.audio}")
        out = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                              "-of", "json", args.audio], capture_output=True, text=True, check=True).stdout
        nm["duration"] = int(float(json.loads(out)["format"]["duration"]) * 1_000_000)
        nm["path"] = str(Path(args.audio).resolve()).replace("\\", "/")
        nm["name"] = Path(args.audio).stem
        nm["type"] = "extract_music"
    m.setdefault("audios", []).append(nm)
    src_dur = min(nm.get("duration", total), total) if nm.get("duration") else total

    ns = copy.deepcopy(mseg) if mseg else {"extra_material_refs": []}
    ns["id"] = nid(); ns["material_id"] = nm["id"]
    ns["source_timerange"] = {"start": 0, "duration": src_dur}
    ns["target_timerange"] = {"start": 0, "duration": src_dur}
    ns["volume"] = args.volume
    ns["last_nonzero_volume"] = args.volume
    ns["common_keyframes"] = []  # kaynaktan taşınan volume keyframe'lerini temizle (seviyeyi kullanıcı ayarlar)
    ns["keyframe_refs"] = []
    refs = []
    for r in ns.get("extra_material_refs", []):
        ki = sby.get(r)
        if not ki:
            continue
        nit = copy.deepcopy(ki[1]); nit["id"] = nid()
        m.setdefault(ki[0], []).append(nit); refs.append(nit["id"])
    ns["extra_material_refs"] = refs

    dc["tracks"].append({"type": "audio", "attribute": 0, "flag": 0, "id": nid(),
                         "segments": [ns], "is_default_name": True, "name": ""})
    dc_path.write_text(json.dumps(dc, ensure_ascii=False), encoding="utf-8")
    import capcut_sync; capcut_sync.sync(dc_path.parent, quiet=True)
    print(f"[OK] {'Seslendirme' if args.audio else 'Müzik'} eklendi: {nm.get('name','')[:25]} (vol {args.volume}) -> {args.draft}")


if __name__ == "__main__":
    main()
