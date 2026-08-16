"""Ortak güvenlik kontrolü: CapCut uygulaması çalışıyorsa düzenlemeyi durdur.

CapCut açıkken (uygulama olarak) diske yazılan değişiklikleri auto-save eziyor.
.locked dosyası her zaman olmuyor; bu yüzden DOĞRUDAN CapCut.exe sürecine bakarız.
"""
import subprocess
import sys


def capcut_calisiyor_mu():
    try:
        out = subprocess.run(["tasklist", "/FI", "IMAGENAME eq CapCut.exe", "/NH"],
                             capture_output=True, text=True, timeout=10).stdout
        return "CapCut.exe" in out
    except Exception:
        return False  # kontrol edilemezse engelleme


def dur_capcut_acikken():
    if capcut_calisiyor_mu():
        sys.exit("DUR: CapCut UYGULAMASI açık (çalışıyor). Düzenlemem ezilir. "
                 "Önce CapCut'ı TAMAMEN KAPAT (sistem tepsisi dahil), sonra tekrar çalıştır.")
