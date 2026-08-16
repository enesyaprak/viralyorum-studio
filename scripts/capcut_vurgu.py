#!/usr/bin/env python3
"""Vurgu/callout metni ekler — verilen metinleri, bir text elementinin stilinde basar.

Prototip kaynağı:
  --from self (varsayılan)  : hedef taslağın kendi text elementi (en uyumlu)
  --from "<sablon>"         : başka taslaktan (favori efekt/stil taşımak için)
  --proto-contains "X"      : prototip text'i içeriğine göre seç (ör. 'Default text')

Vurgu JSON: [{"text":"...","start":sec,"dur":sec}, ...]
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


def resolve_draft(s):
    if (DRAFTS / s / "draft_content.json").exists():
        return s
    key = s.lower().replace(" ", "")
    for f in glob.glob(str(DRAFTS / "*" / "draft_meta_info.json")):
        folder = os.path.basename(os.path.dirname(f))
        try:
            name = json.load(open(f, encoding="utf-8")).get("draft_name", "")
        except Exception:
            name = ""
        if key in folder.lower().replace(" ", "") or key in name.lower().replace(" ", ""):
            return folder
    sys.exit(f"HATA: '{s}' taslağı bulunamadı.")


def index(materials):
    return {it["id"]: (k, it) for k, v in materials.items() if isinstance(v, list)
            for it in v if isinstance(it, dict) and "id" in it}


def seg_text(s, sby, sm):
    kd = sby.get(s["material_id"], (None, None))
    if kd[0] == "text_templates":
        tx = sby.get(kd[1]["text_info_resources"][0]["text_material_id"], (None, None))[1]
    elif kd[0] == "texts":
        tx = kd[1]
    else:
        return ""
    if not tx:
        return ""
    c = json.loads(tx["content"]) if isinstance(tx["content"], str) else tx["content"]
    return c.get("text", "")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--draft", required=True)
    ap.add_argument("--vurgu", required=True)
    ap.add_argument("--from", dest="src", default="self", help="prototip kaynağı (self / şablon adı)")
    ap.add_argument("--proto-contains", help="prototip text'i içeriğine göre seç")
    ap.add_argument("--size", type=int, default=20)
    ap.add_argument("--y", type=float, default=None, help="dikey konum (verilmezse proto korunur)")
    ap.add_argument("--keep-size", action="store_true")
    args = ap.parse_args()

    items = json.loads(Path(args.vurgu).read_text(encoding="utf-8"))
    import capcut_guard
    capcut_guard.dur_capcut_acikken()
    args.draft = resolve_draft(args.draft)
    dc_path = DRAFTS / args.draft / "draft_content.json"
    dc = json.loads(dc_path.read_text(encoding="utf-8"))
    m = dc["materials"]

    # kaynak (prototip) taslağı
    if args.src and args.src != "self":
        sf = json.loads((DRAFTS / resolve_draft(args.src) / "draft_content.json").read_text(encoding="utf-8"))
    else:
        sf = dc
    sm = sf["materials"]
    sby = index(sm)

    # prototip segment seç
    pseg = None
    proto_track = None
    for t in sf["tracks"]:
        if t.get("type") != "text" or not t.get("segments"):
            continue
        for s in t["segments"]:
            if not args.proto_contains or args.proto_contains.lower() in seg_text(s, sby, sm).lower():
                pseg, proto_track = s, t
                break
        if pseg:
            break
    if not pseg:
        sys.exit("HATA: prototip text bulunamadı (kaynakta text olmalı).")

    is_tpl = sby.get(pseg["material_id"], (None,))[0] == "text_templates"
    proto_tt = copy.deepcopy(sby[pseg["material_id"]][1]) if is_tpl else None
    anim_ref = next((r for r in pseg.get("extra_material_refs", [])
                     if sby.get(r, ("",))[0] == "material_animations"), None)
    proto_anim = copy.deepcopy(sby[anim_ref][1]) if anim_ref else None
    if is_tpl:
        proto_text = copy.deepcopy(sby[proto_tt["text_info_resources"][0]["text_material_id"]][1])
    else:
        proto_text = copy.deepcopy(sby[pseg["material_id"]][1])

    new_segs = []
    base_render = (pseg.get("render_index", 15000) or 15000) + 800
    for i, it in enumerate(items):
        phrase = it["text"]
        start = int(it["start"] * 1e6)
        dur = int(it.get("dur", 2.0) * 1e6)

        nt = copy.deepcopy(proto_text); nt["id"] = nid()
        c = json.loads(nt["content"]) if isinstance(nt["content"], str) else nt["content"]
        c["text"] = phrase
        if c.get("styles"):
            c["styles"] = [c["styles"][0]]
            c["styles"][0]["range"] = [0, len(phrase)]
            if not (args.keep_size or args.proto_contains):
                c["styles"][0]["size"] = args.size
        nt["content"] = json.dumps(c, ensure_ascii=False)
        nt["words"] = {"text": [phrase], "start_time": [0], "end_time": [dur // 1000]}
        m["texts"].append(nt)

        ref_anim = None
        if proto_anim:
            na = copy.deepcopy(proto_anim); na["id"] = nid()
            m.setdefault("material_animations", []).append(na); ref_anim = na["id"]

        ns = copy.deepcopy(pseg); ns["id"] = nid()
        if is_tpl:
            ntt = copy.deepcopy(proto_tt); ntt["id"] = nid()
            ntt["text_info_resources"][0]["text_material_id"] = nt["id"]
            ntt["text_info_resources"][0]["id"] = nid()
            m.setdefault("text_templates", []).append(ntt)
            ns["material_id"] = ntt["id"]
        else:
            ns["material_id"] = nt["id"]
        ns["extra_material_refs"] = [ref_anim] if ref_anim else []
        ns["target_timerange"] = {"start": start, "duration": dur}
        if args.y is not None:
            ns.setdefault("clip", {})["transform"] = {"x": 0.0, "y": args.y}
        ns["render_index"] = base_render + i
        new_segs.append(ns)

    # placeholder kaldır (sadece aynı taslakta --proto-contains ile)
    if args.proto_contains and proto_track is not None and sf is dc:
        proto_track["segments"] = [s for s in proto_track["segments"] if s["id"] != pseg["id"]]

    dc["tracks"].append({"type": "text", "attribute": 0, "flag": 0, "id": nid(),
                         "segments": new_segs, "is_default_name": True, "name": ""})
    dc_path.write_text(json.dumps(dc, ensure_ascii=False), encoding="utf-8")
    import capcut_sync; capcut_sync.sync(dc_path.parent, quiet=True)
    print(f"[OK] {len(new_segs)} metin eklendi ({'template' if is_tpl else 'duz'}, kaynak={args.src}) -> {args.draft}")


if __name__ == "__main__":
    main()
