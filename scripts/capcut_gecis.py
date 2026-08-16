#!/usr/bin/env python3
"""Video segmentleri arasına geçiş ekler.

İki mod:
  --from <sablon>   : o şablonun kullandığı (favori) geçişleri sırayla
  --names "Mix,Black Fade" : belirli geçişleri ada göre (tüm taslaklardan bulur)

--clear : önce mevcut geçişleri temizler (geçiş değiştirmek için).

Kullanım:
    python scripts/capcut_gecis.py --draft "X" --from "rönesanskapı-1"
    python scripts/capcut_gecis.py --draft "X" --names "Mix,Black Fade" --clear
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


def find_transitions(names):
    """Tüm taslaklardan, verilen isimlerdeki geçiş objelerini bulur."""
    found = {}
    for f in glob.glob(str(DRAFTS / "*" / "draft_content.json")):
        try:
            dc = json.loads(Path(f).read_text(encoding="utf-8"))
        except Exception:
            continue
        for tr in dc.get("materials", {}).get("transitions", []):
            if tr.get("name") in names and tr["name"] not in found:
                found[tr["name"]] = tr
        if len(found) == len(names):
            break
    return [found[n] for n in names if n in found]


def from_source(src):
    sf = json.loads((DRAFTS / src / "draft_content.json").read_text(encoding="utf-8"))
    fav, seen = [], set()
    for tr in sf["materials"].get("transitions", []):
        if tr.get("name") not in seen:
            seen.add(tr.get("name")); fav.append(tr)
    return fav


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--draft", required=True)
    ap.add_argument("--from", dest="src", help="geçişlerin alınacağı şablon")
    ap.add_argument("--names", help="belirli geçiş adları (virgülle)")
    ap.add_argument("--offset", type=int, default=0)
    ap.add_argument("--clear", action="store_true", help="önce mevcut geçişleri sil")
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

    if args.names:
        fav = find_transitions([n.strip() for n in args.names.split(",")])
    elif args.src:
        fav = from_source(args.src)
    else:
        sys.exit("HATA: --from veya --names ver.")
    if not fav:
        sys.exit("HATA: geçiş bulunamadı.")
    print("Geçişler:", [t.get("name") for t in fav])

    vtracks = [t for t in dc["tracks"] if t.get("type") == "video"]
    main_tr = max(vtracks, key=lambda t: len(t["segments"]))
    segs = sorted(main_tr["segments"], key=lambda s: s["target_timerange"]["start"])
    if len(segs) < 2:
        sys.exit("HATA: en az 2 segment gerekli.")

    if args.clear:
        old = {t["id"] for t in m.get("transitions", [])}
        m["transitions"] = []
        for s in segs:
            s["extra_material_refs"] = [r for r in s.get("extra_material_refs", []) if r not in old]
        print("Mevcut geçişler temizlendi.")

    added = 0
    for i in range(len(segs) - 1):
        proto = fav[(i + args.offset) % len(fav)]
        ntr = copy.deepcopy(proto); ntr["id"] = nid()
        m.setdefault("transitions", []).append(ntr)
        segs[i].setdefault("extra_material_refs", []).append(ntr["id"])
        added += 1

    dc_path.write_text(json.dumps(dc, ensure_ascii=False), encoding="utf-8")
    import capcut_sync; capcut_sync.sync(dc_path.parent, quiet=True)
    print(f"[OK] {added} geçiş eklendi -> {args.draft}")


if __name__ == "__main__":
    main()
