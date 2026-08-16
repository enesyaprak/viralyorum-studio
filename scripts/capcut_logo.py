#!/usr/bin/env python3
"""CapCut taslağından logo/foto katmanını kaldırır (veya değiştirir).

Şablonda logo genelde 'photo' tipi bir materyal (materials.videos içinde). Bu aracı
'logo yok' istenen markalar için kullan: foto materyalini ve segmentini siler.

Kullanım:
    python scripts/capcut_logo.py --draft "ERCAN-cc-1" --remove
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


def img_dims(path):
    out = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0",
                          "-show_entries", "stream=width,height", "-of", "json", str(path)],
                         capture_output=True, text=True, check=True).stdout
    st = json.loads(out)["streams"][0]
    return st["width"], st["height"]


def add_logo_from(dc, m, image, template):
    """Kaynak şablondaki logo (photo) elementini kopyalayıp bu taslağa ekler."""
    sf = json.loads((DRAFTS / template / "draft_content.json").read_text(encoding="utf-8"))
    sby = {it["id"]: (k, it) for k, v in sf["materials"].items() if isinstance(v, list)
           for it in v if isinstance(it, dict) and "id" in it}
    # KULLANILAN logo: sablonda birden fazla photo materyali olabilir (import edilip
    # silinmis gorseller materyalde kaliyor) -> timeline'da SEGMENTI olani sec.
    kullanilan = {s["material_id"] for t in sf["tracks"] if t["type"] == "video"
                  for s in t["segments"]}
    photo = next((v for v in sf["materials"]["videos"]
                  if v.get("type") == "photo" and v["id"] in kullanilan), None)
    if not photo:
        sys.exit(f"HATA: '{template}' icinde timeline'da kullanilan logo (photo) yok.")
    pseg = next((s for t in sf["tracks"] if t["type"] == "video"
                 for s in t["segments"] if s["material_id"] == photo["id"]), None)
    if not pseg:
        sys.exit("HATA: kaynak logo segmenti bulunamadı.")
    nid = lambda: str(uuid.uuid4()).upper()
    w, h = img_dims(image)
    np_ = copy.deepcopy(photo); np_["id"] = nid()
    np_["path"] = str(Path(image).resolve()).replace("\\", "/")
    np_["width"], np_["height"] = w, h
    m.setdefault("videos", []).append(np_)
    ns = copy.deepcopy(pseg); ns["id"] = nid(); ns["material_id"] = np_["id"]
    # segmentin extra ref materyallerini de kopyala (canvas vb.)
    new_refs = []
    for r in ns.get("extra_material_refs", []):
        kind_it = sby.get(r)
        if not kind_it:
            continue
        kind, it = kind_it
        nit = copy.deepcopy(it); nit["id"] = nid()
        m.setdefault(kind, []).append(nit)
        new_refs.append(nit["id"])
    ns["extra_material_refs"] = new_refs
    # logo videonun TAMAMI boyunca dursun (sablonun suresi farkli olabilir)
    hedef_sure = dc.get("duration") or ns["target_timerange"]["duration"]
    ns["source_timerange"] = {"start": 0, "duration": hedef_sure}
    ns["target_timerange"] = {"start": 0, "duration": hedef_sure}
    # flag 2 = overlay (ust katman) track; ana video track'inin uzerinde dursun
    dc["tracks"].append({"type": "video", "attribute": 0, "flag": 2, "id": nid(),
                         "segments": [ns], "is_default_name": True, "name": ""})


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--draft", required=True)
    ap.add_argument("--remove", action="store_true", help="foto/logo katmanını kaldır")
    ap.add_argument("--replace", help="logoyu bu görselle değiştir (yol)")
    ap.add_argument("--add", help="logo yoksa bu görseli ekle (yol)")
    ap.add_argument("--from", dest="src", help="--add için logo elementinin alınacağı şablon")
    args = ap.parse_args()

    dc_path = DRAFTS / args.draft / "draft_content.json"
    if not dc_path.exists():
        sys.exit(f"HATA: taslak yok: {dc_path}")
    dc = json.loads(dc_path.read_text(encoding="utf-8"))
    m = dc["materials"]

    if args.add:
        if not args.src:
            sys.exit("HATA: --add için --from \"<sablon>\" gerekli.")
        if not Path(args.add).exists():
            sys.exit(f"HATA: görsel yok: {args.add}")
        add_logo_from(dc, m, args.add, args.src)
        dc_path.write_text(json.dumps(dc, ensure_ascii=False), encoding="utf-8")
        print(f"[OK] Logo eklendi: {Path(args.add).name} (kaynak: {args.src})")
        return

    photo_ids = {v["id"] for v in m.get("videos", []) if v.get("type") == "photo"}
    if not photo_ids:
        print("Foto/logo materyali bulunamadı (zaten yok).")
        return
    print(f"Foto/logo materyali: {len(photo_ids)} adet")

    if args.replace:
        import subprocess
        img = Path(args.replace)
        if not img.exists():
            sys.exit(f"HATA: görsel yok: {img}")
        out = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0",
                              "-show_entries", "stream=width,height", "-of", "json", str(img)],
                             capture_output=True, text=True, check=True).stdout
        st = json.loads(out)["streams"][0]
        npath = str(img.resolve()).replace("\\", "/")
        for v in m["videos"]:
            if v["id"] in photo_ids:
                v["path"], v["width"], v["height"] = npath, st["width"], st["height"]
        dc_path.write_text(json.dumps(dc, ensure_ascii=False), encoding="utf-8")
        print(f"[OK] Logo değiştirildi -> {img.name} ({st['width']}x{st['height']})")
        return

    if not args.remove:
        print("(--remove / --replace verilmedi, değişiklik yapılmadı)")
        return

    # foto segmentlerini tüm track'lerden çıkar; boşalan track'i de sil
    new_tracks = []
    removed_seg = 0
    for tr in dc.get("tracks", []):
        segs = tr.get("segments", [])
        kept = [s for s in segs if s.get("material_id") not in photo_ids]
        removed_seg += len(segs) - len(kept)
        tr["segments"] = kept
        if kept or tr.get("type") not in ("video",):
            new_tracks.append(tr)
        # boşalan video track'i atla (logo kendi track'indeyse)
    dc["tracks"] = new_tracks

    # foto materyallerini sil
    m["videos"] = [v for v in m.get("videos", []) if v["id"] not in photo_ids]

    dc_path.write_text(json.dumps(dc, ensure_ascii=False), encoding="utf-8")
    print(f"[OK] Logo kaldırıldı: {removed_seg} segment, {len(photo_ids)} foto materyali silindi.")


if __name__ == "__main__":
    main()
