#!/usr/bin/env python3
"""draft_content.json editini CapCut'ın okuduğu AYNA dosyalara yazar.

Bazı (yeni format) CapCut projelerinde asıl okunan dosya template.json'dır;
scriptler sadece draft_content.json'ı editler → CapCut açılışta editi görmez,
kendi eski template.json'ını geri yükler ('olmamış'/ezilme sorunu). Bu modül
editi template.json (+ template-2.tmp + .bak) dosyalarına da yazar ve
draft_meta_info'daki tm_draft_modified'ı şimdiye çeker.

Artık tüm editleme araçları (capcut_muzik/altyazi/vurgu/gecis/... ) yazdıktan
sonra OTOMATİK sync(draft) çağırıyor — ayrı adım gerekmez. Elle de çalışır:
    python scripts/capcut_sync.py --draft "istikbal-banaz-7"
"""
import argparse
import json
import os
import shutil
import sys
import time
from pathlib import Path

DRAFTS = Path(os.environ["LOCALAPPDATA"]) / "CapCut Drafts"
# template.json'ın sahip olmadığı (draft_content'e özel) üst-seviye anahtarlar
TPL_HARIC = {"time_marks", "cover", "group_container", "mutable_config", "retouch_cover"}


def sync(draft, quiet=False):
    """draft_content.json'ı ayna dosyalara yazar + meta damgasını günceller.

    draft: klasör adı (örn 'istikbal-banaz-7') veya tam yol.
    Sessizce başarısız olur (edit'i bozmamak için) — sadece koruma katmanı.
    """
    folder = Path(draft) if os.path.isabs(str(draft)) else DRAFTS / draft
    dc_path = folder / "draft_content.json"
    if not dc_path.exists():
        return []
    try:
        dc = json.loads(dc_path.read_text(encoding="utf-8"))
    except Exception:
        return []

    synced = []
    tpl_path = folder / "template.json"
    if tpl_path.exists():
        try:
            tpl = {k: v for k, v in dc.items() if k not in TPL_HARIC}
            tpl_path.write_text(json.dumps(tpl, ensure_ascii=False), encoding="utf-8")
            synced.append("template.json")
        except Exception:
            pass
    # Timelines/<UUID>/draft_content.json - YENI FORMAT PROJELERDE CAPCUT'IN OKUDUGU DOSYA.
    # 2026-08-20'ye kadar yazilmiyordu: scriptler kok draft_content.json'i editliyor, CapCut
    # ise nested kopyayi okuyup ESKI hali gosteriyor ve kapanista o eski hali her yere yazip
    # editi siliyordu (agaclarin-agi + karinca-koprusu'nda VO/altyazi/muzik/logo/gecis ucdu).
    # Iki dosyanin id'si, klasor adi ve main_timeline_id ayni; icerik birebir ayna.
    for ic in (folder / 'Timelines').glob('*/draft_content.json'):
        try:
            shutil.copyfile(dc_path, ic)
            synced.append(f'Timelines/{ic.parent.name[:8]}')
        except Exception:
            pass

    for mirror in ("template-2.tmp", "draft_content.json.bak"):
        if (folder / mirror).exists():
            try:
                shutil.copyfile(dc_path, folder / mirror)
                synced.append(mirror)
            except Exception:
                pass

    mi_path = folder / "draft_meta_info.json"
    if mi_path.exists():
        try:
            mi = json.loads(mi_path.read_text(encoding="utf-8"))
            mi["tm_draft_modified"] = int(time.time() * 1_000_000)
            mi_path.write_text(json.dumps(mi, ensure_ascii=False), encoding="utf-8")
            synced.append("meta")
        except Exception:
            pass

    if not quiet:
        print(f"[OK] Senkron: {', '.join(synced) if synced else 'ayna yok'} -> {os.path.basename(str(folder))}")
    return synced


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--draft", required=True)
    args = ap.parse_args()
    if not (DRAFTS / args.draft / "draft_content.json").exists() and not os.path.isabs(args.draft):
        sys.exit(f"HATA: '{args.draft}' taslağı yok.")
    sync(args.draft)


if __name__ == "__main__":
    main()
