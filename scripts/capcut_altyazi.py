#!/usr/bin/env python3
"""CapCut altyazılarını OKU + DÜZELT (proofread).

Akış: Enes CapCut auto-caption ile altyazıyı üretir -> bu araç metni döker ->
Claude sesle/bağlamla karşılaştırıp düzeltir (marka adı, büyük harf, yanlış kelime)
-> bu araç düzeltmeleri geri yazar. Karaoke zamanlaması korunur.

Oku:
    python scripts/capcut_altyazi.py --draft "ZEUS-cc-1" --oku --out output/zeus_alt.json
Düzelt (metinler zaman sırasıyla 1:1):
    python scripts/capcut_altyazi.py --draft "ZEUS-cc-1" --duzelt output/zeus_alt_duzelt.json
"""
import argparse
import json
import os
import re
import sys
from pathlib import Path

DRAFTS = Path(os.environ["LOCALAPPDATA"]) / "CapCut Drafts"
ROOT = Path(__file__).resolve().parent.parent


def resolve_texts(dc):
    """Text segmentlerini zaman sırasıyla -> (segment, texts_materyali) döndürür.
    Hem düz texts hem text_templates dolaylamasını çözer."""
    m = dc["materials"]
    by_id = {it["id"]: (k, it) for k, v in m.items() if isinstance(v, list)
             for it in v if isinstance(it, dict) and "id" in it}
    out = []
    for t in dc["tracks"]:
        if t.get("type") != "text":
            continue
        for s in t["segments"]:
            kind, mat = by_id.get(s["material_id"], (None, None))
            if kind == "text_templates":
                txid = mat["text_info_resources"][0]["text_material_id"]
                tx = by_id.get(txid, (None, None))[1]
            elif kind == "texts":
                tx = mat
            else:
                tx = None
            if tx:
                out.append((s, tx))
    out.sort(key=lambda x: x[0].get("target_timerange", {}).get("start", 0))
    return out


def get_text(tx):
    c = json.loads(tx["content"]) if isinstance(tx["content"], str) else tx["content"]
    return c.get("text", "")


def set_text(tx, new):
    c = json.loads(tx["content"]) if isinstance(tx["content"], str) else tx["content"]
    old = c.get("text", "")
    c["text"] = new
    if c.get("styles"):
        # ilk stilin aralığını yeni uzunluğa çek (tek stil varsay)
        c["styles"][0]["range"] = [0, len(new)]
        c["styles"] = [c["styles"][0]]
    tx["content"] = json.dumps(c, ensure_ascii=False)
    # karaoke words güncelle (ekranda doğru metin için şart)
    w = tx.get("words")
    if isinstance(w, dict) and w.get("text"):
        old_tokens = w["text"]
        old_idx = [i for i, t in enumerate(old_tokens) if t.strip()]
        new_words = new.split()
        if len(new_words) == len(old_idx):
            # kelime sayısı aynı: zamanı koru, sadece metni değiştir
            for j, idx in enumerate(old_idx):
                old_tokens[idx] = new_words[j]
            w["text"] = old_tokens
        else:
            # kelime sayısı değişti: tüm span'a eşit dağıt
            span = max(w.get("end_time") or [0]) or 1000
            n = len(new_words)
            toks, st, en = [], [], []
            for k, word in enumerate(new_words):
                a = round(k * span / n); b = round((k + 1) * span / n)
                toks.append(word); st.append(a); en.append(b)
                if k < n - 1:
                    toks.append(" "); st.append(b); en.append(b)
            w["text"], w["start_time"], w["end_time"] = toks, st, en
    return old


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--draft", required=True)
    ap.add_argument("--oku", action="store_true")
    ap.add_argument("--out", help="oku çıktısı JSON")
    ap.add_argument("--duzelt", help="düzeltme JSON'u (zaman sırasıyla metin listesi)")
    ap.add_argument("--sozluk", nargs="?", const=str(ROOT / "presets" / "altyazi_sozluk.json"),
                    help="otomatik düzeltme sözlüğü uygula (varsayılan: presets/altyazi_sozluk.json)")
    ap.add_argument("--marka", help="sözlükteki marka kuralları da uygulansın")
    args = ap.parse_args()

    # Türkçe/kısmi klasör adı çözümle (partial match)
    if not (DRAFTS / args.draft / "draft_content.json").exists():
        import glob
        key = args.draft.lower().replace(" ", "")
        for f in glob.glob(str(DRAFTS / "*" / "draft_meta_info.json")):
            folder = os.path.basename(os.path.dirname(f))
            try:
                nm = json.load(open(f, encoding="utf-8")).get("draft_name", "")
            except Exception:
                nm = ""
            if key in folder.lower().replace(" ", "") or key in nm.lower().replace(" ", ""):
                args.draft = folder
                break

    dc_path = DRAFTS / args.draft / "draft_content.json"
    if not dc_path.exists():
        sys.exit(f"HATA: taslak yok: {dc_path}")
    # GÜVENLİK KİLİDİ: yazma işleminde CapCut açıksa dur (iş kaybını önle)
    if args.duzelt or args.sozluk:
        import capcut_guard
        capcut_guard.dur_capcut_acikken()
        if (DRAFTS / args.draft / ".locked").exists():
            sys.exit(f"DUR: CapCut '{args.draft}' ile AÇIK. Önce KAPAT, sonra düzeltmeyi yaz.")
    dc = json.loads(dc_path.read_text(encoding="utf-8"))
    pairs = resolve_texts(dc)

    if args.oku:
        rows = [{"i": i, "t": round(s.get("target_timerange", {}).get("start", 0) / 1e6, 2),
                 "metin": get_text(tx)} for i, (s, tx) in enumerate(pairs)]
        if args.out:
            Path(args.out).write_text(json.dumps(rows, ensure_ascii=False, indent=1), encoding="utf-8")
            print(f"[OK] {len(rows)} altyazı yazıldı -> {args.out}")
        else:
            for r in rows:
                print(f"  [{r['i']}] {r['t']}s: {r['metin']}")
        return

    if args.sozluk:
        sz = json.loads(Path(args.sozluk).read_text(encoding="utf-8"))
        rules = list(sz.get("global", []))
        if args.marka and args.marka in sz.get("markalar", {}):
            rules = sz["markalar"][args.marka] + rules  # marka kuralları önce
        changed = 0
        for s, tx in pairs:
            old = get_text(tx)
            new = old
            for pat, rep in rules:
                new = re.sub(pat, rep, new)
            if new != old:
                set_text(tx, new)
                changed += 1
                print(f"  '{old[:35]}' -> '{new[:35]}'")
        dc_path.write_text(json.dumps(dc, ensure_ascii=False), encoding="utf-8")
        import capcut_sync; capcut_sync.sync(dc_path.parent, quiet=True)
        print(f"[OK] Sözlük uygulandı: {changed} altyazı düzeltildi. (kalan ince hatalar için --oku)")
        return

    if args.duzelt:
        new_list = json.loads(Path(args.duzelt).read_text(encoding="utf-8"))
        if len(new_list) != len(pairs):
            print(f"UYARI: {len(new_list)} düzeltme, {len(pairs)} altyazı. İlk {min(len(new_list),len(pairs))} uygulanacak.")
        changed = 0
        for i in range(min(len(new_list), len(pairs))):
            if new_list[i] is None:
                continue
            old = set_text(pairs[i][1], new_list[i])
            if old != new_list[i]:
                changed += 1
        dc_path.write_text(json.dumps(dc, ensure_ascii=False), encoding="utf-8")
        import capcut_sync; capcut_sync.sync(dc_path.parent, quiet=True)
        print(f"[OK] {changed} altyazı düzeltildi -> {args.draft}")
        return

    sys.exit("--oku veya --duzelt ver.")


if __name__ == "__main__":
    main()
