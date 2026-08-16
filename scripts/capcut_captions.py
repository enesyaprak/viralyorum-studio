#!/usr/bin/env python3
"""CapCut taslağına Scribe transkriptinden karaoke altyazı enjekte eder.

Kopyala-mutasyon: taslaktaki MEVCUT bir caption elementini (text_template + texts +
animation) prototip alır, Scribe kelime-zaman verisinden N caption üretir, ID'leri
tutarlı bağlar, eski caption'ları temizler. Senin tam CapCut altyazı stilin korunur.

Zincir: segment.material_id->text_template ; segment.extra_material_refs->animation ;
        text_template.text_info_resources[0].text_material_id->texts (metin+words).

Kullanım:
    python scripts/capcut_captions.py --draft "OTO-cap-1" --transcript output/ronesans_FULL_transkript.json
"""
import argparse
import copy
import json
import os
import sys
import uuid
from pathlib import Path

DRAFTS = Path(os.environ["LOCALAPPDATA"]) / "CapCut Drafts"


def nid():
    return str(uuid.uuid4()).upper()


def chunk_words(words, max_words, pause):
    chunks, cur = [], []
    for i, w in enumerate(words):
        cur.append(w)
        raw = w.get("raw", w["text"])
        last = raw.rstrip().endswith((".", "!", "?", ":"))
        gap = (i + 1 < len(words)) and (words[i + 1]["start"] - w["end"] > pause)
        if len(cur) >= max_words or last or gap or i == len(words) - 1:
            chunks.append(cur)
            cur = []
    return chunks


def load_words(transcript):
    data = json.loads(Path(transcript).read_text(encoding="utf-8"))
    out = []
    for w in data.get("words", []):
        if w.get("type") != "word":
            continue
        t = w["text"].strip()
        if not any(c.isalnum() for c in t):
            continue
        out.append({"text": t, "raw": w["text"], "start": w["start"], "end": w["end"]})
    return out


def build_word_tokens(chunk):
    """CapCut words yapısı: ['kel',' ','kel'] + start/end (ms, chunk başına göreli)."""
    base = chunk[0]["start"]
    toks, starts, ends = [], [], []
    for i, w in enumerate(chunk):
        ws = round((w["start"] - base) * 1000)
        we = round((w["end"] - base) * 1000)
        toks.append(w["text"]); starts.append(ws); ends.append(we)
        if i < len(chunk) - 1:
            toks.append(" "); starts.append(we); ends.append(we)
    return toks, starts, ends


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--draft", required=True, help="CapCut Drafts içindeki HEDEF taslak (klon)")
    ap.add_argument("--transcript", required=True, help="transcribe.py çıktı JSON")
    ap.add_argument("--max-words", type=int, default=3)
    ap.add_argument("--pause", type=float, default=0.45)
    ap.add_argument("--style-from", help="Caption stilini başka bir taslaktan al (hedefte caption yoksa)")
    args = ap.parse_args()

    folder = DRAFTS / args.draft
    dc_path = folder / "draft_content.json"
    if not dc_path.exists():
        sys.exit(f"HATA: taslak yok: {dc_path}")

    dc = json.loads(dc_path.read_text(encoding="utf-8"))
    m = dc["materials"]
    by_id = {}
    for k, v in m.items():
        if isinstance(v, list):
            for it in v:
                if isinstance(it, dict) and "id" in it:
                    by_id[it["id"]] = (k, it)

    # prototip caption elementi: hedefte caption varsa oradan, yoksa --style-from'dan
    ttrack = next((t for t in dc["tracks"] if t.get("type") == "text" and t.get("segments")), None)
    old_seg_tt, old_tx, old_anim = set(), set(), set()

    if ttrack:
        proto_dc, proto_by = dc, by_id
        proto_seg = copy.deepcopy(ttrack["segments"][0])
        # hedefteki eski caption id'lerini topla (silinecek)
        old_seg_tt = {s["material_id"] for s in ttrack["segments"]}
        for s in ttrack["segments"]:
            tt = by_id.get(s["material_id"])
            if tt and tt[0] == "text_templates":
                old_tx.add(tt[1]["text_info_resources"][0]["text_material_id"])
            for r in s.get("extra_material_refs", []):
                if by_id.get(r, ("",))[0] == "material_animations":
                    old_anim.add(r)
    else:
        if not args.style_from:
            sys.exit("HATA: hedefte caption yok. --style-from \"<sablon>\" ile stil kaynağı ver.")
        sf = json.loads((DRAFTS / args.style_from / "draft_content.json").read_text(encoding="utf-8"))
        proto_by = {}
        for k, v in sf["materials"].items():
            if isinstance(v, list):
                for it in v:
                    if isinstance(it, dict) and "id" in it:
                        proto_by[it["id"]] = (k, it)
        st = next((t for t in sf["tracks"] if t.get("type") == "text" and t.get("segments")), None)
        if not st:
            sys.exit(f"HATA: '{args.style_from}' içinde caption yok.")
        proto_seg = copy.deepcopy(st["segments"][0])
        # hedefe yeni text track ekle
        ttrack = {"type": "text", "attribute": 0, "flag": 0, "id": nid(), "segments": [],
                  "is_default_name": True, "name": ""}
        dc["tracks"].append(ttrack)

    by_id = proto_by  # prototip materyalleri buradan çözülecek
    proto_tt = copy.deepcopy(by_id[proto_seg["material_id"]][1])
    anim_ref = next((r for r in proto_seg["extra_material_refs"]
                     if by_id.get(r, ("",))[0] == "material_animations"), None)
    proto_anim = copy.deepcopy(by_id[anim_ref][1]) if anim_ref else None
    proto_txid = proto_tt["text_info_resources"][0]["text_material_id"]
    proto_text = copy.deepcopy(by_id[proto_txid][1])

    # transkript -> chunk
    words = load_words(args.transcript)
    chunks = chunk_words(words, args.max_words, args.pause)
    if not chunks:
        sys.exit("HATA: transkriptte kelime yok.")

    new_texts, new_tts, new_anims, new_segs = [], [], [], []
    base_render = proto_seg.get("render_index", 14001)
    for i, ch in enumerate(chunks):
        toks, starts, ends = build_word_tokens(ch)
        phrase = "".join(toks)
        start_us = int(ch[0]["start"] * 1_000_000)
        dur_us = int((ch[-1]["end"] - ch[0]["start"]) * 1_000_000) or 50000

        # texts (metin + words)
        nt = copy.deepcopy(proto_text); nt["id"] = nid()
        content = json.loads(nt["content"]) if isinstance(nt["content"], str) else nt["content"]
        content["text"] = phrase
        if content.get("styles"):
            content["styles"] = [content["styles"][0]]
            content["styles"][0]["range"] = [0, len(phrase)]
        nt["content"] = json.dumps(content, ensure_ascii=False)
        nt["words"] = {"text": toks, "start_time": starts, "end_time": ends}
        new_texts.append(nt)

        # animation (varsa)
        ref_anim = None
        if proto_anim:
            na = copy.deepcopy(proto_anim); na["id"] = nid()
            new_anims.append(na); ref_anim = na["id"]

        # text_template (texts'e bağla)
        ntt = copy.deepcopy(proto_tt); ntt["id"] = nid()
        ntt["text_info_resources"][0]["text_material_id"] = nt["id"]
        ntt["text_info_resources"][0]["id"] = nid()
        new_tts.append(ntt)

        # segment
        ns = copy.deepcopy(proto_seg); ns["id"] = nid()
        ns["material_id"] = ntt["id"]
        ns["extra_material_refs"] = [ref_anim] if ref_anim else []
        ns["target_timerange"] = {"start": start_us, "duration": dur_us}
        ns["render_index"] = base_render + i
        new_segs.append(ns)

    # eskileri çıkar, yenileri ekle (hedefte ilgili liste boş/yoksa güvenli)
    m["texts"] = [t for t in m.get("texts", []) if t["id"] not in old_tx] + new_texts
    m["text_templates"] = [t for t in m.get("text_templates", []) if t["id"] not in old_seg_tt] + new_tts
    m["material_animations"] = [a for a in m.get("material_animations", []) if a["id"] not in old_anim] + new_anims
    ttrack["segments"] = new_segs

    dc_path.write_text(json.dumps(dc, ensure_ascii=False), encoding="utf-8")
    print(f"[OK] {len(chunks)} caption enjekte edildi -> {args.draft}")
    print("Örnek ilk 3:", [" ".join(w["text"] for w in c) for c in chunks[:3]])


if __name__ == "__main__":
    main()
