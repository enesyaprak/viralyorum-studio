# Sonraki adımlar — ilk videoyu bitirme

Bu dosya, `viralyorum-studio` klasöründe açılan **yeni** Claude Code oturumu için devir notudur.
Hedef: `ahtapot-uc-kalp` videosunu uçtan uca bitirmek. Stok üretimi ondan sonra.

## Şu an hazır olanlar

| Parça | Durum |
|---|---|
| MCP (`pexels`, `pixabay`) | `.mcp.json` hazır, ikisi de test edildi. **Bu klasörde açılan oturumda yüklenir.** |
| API anahtarları | `.env` + kalıcı ortam değişkeni (`PEXELS_API_KEY`, `PIXABAY_API_KEY`, `ELEVENLABS_API_KEY`) |
| Ses | Doga (`IuRRIAcbQK5AQk1XevPj`), yüksek enerji profili — `preset.json` içinde |
| CapCut taslağı | `ahtapot-uc-kalp` oluşturuldu, **açıldığı doğrulandı**, 1 klip havuzda |
| Plan | `projeler/ahtapot-uc-kalp/plan.json` — 7 sahne, anlatım ve arama terimleri dolu |

## Yapılacaklar

### 1. Kalan 6 sahnenin kliplerini seç (MCP)

Sahne 1'in klibi seçili ve indirilmiş. Sahne 2-7 boş.

`videos_search` (pexels) ve `search_pixabay_videos` (pixabay) ile her sahnenin
`ara[]` terimlerini ara. Seçilen klipleri sahnenin `klipler[]` alanına şu şemayla yaz:

```json
{"kaynak":"pexels","id":"1234","url":"https://...mp4","genislik":2160,
 "yukseklik":3840,"sure":12,"sahibi":"Ad Soyad","sayfa":"https://www.pexels.com/video/..."}
```

Pexels'te dosya URL'lerini almak için `video_get` (id ile) gerekiyor — `videos_search`
sonucu tek başına yetmeyebilir.

**Seçim kuralları:**
- **En yüksek çözünürlüğü al (4K).** Enes'in kararı — kesme/zoom payı için.
- Dikey (portrait) tercih et; yatay 9:16'ya kırpılınca kadrajın yarısı gidiyor.
- Sahne süresinden uzun klip seç.

### 2. İndir

```bash
python scripts/indir.py --proje ahtapot-uc-kalp
```

`kaynaklar.json`'a lisans kaydı yazılır — telif kanıtı, saklanır.

### 3. Taslağı yeniden kur

Taslakta şu an sadece 1 klip var. 7 klip inince taslağı yenilemek gerekiyor:

```bash
python scripts/capcut_havuz.py --proje ahtapot-uc-kalp --ad ahtapot-uc-kalp
```

Var olan adın üstüne **yazmaz** — önce CapCut'tan sil ya da klasörü kaldır.
**CapCut kapalı olmalı** (script zaten kontrol edip duruyor).

### 4. Enes: CapCut'ta dizer

Klipleri smart clipping ile dizer/keser, sonra **CapCut'ı tepsiden TAM kapatır**.

### 5. Üret

```bash
python scripts/uret.py --proje ahtapot-uc-kalp --draft ahtapot-uc-kalp
```

TTS → VO enjekte → Scribe transcribe → karaoke altyazı → sözlük düzeltmesi →
şüpheli altyazı raporu.

**Şablon olmadığı için müzik / efekt / geçiş / hook text adımları atlanacak**
(`preset.json`'daki o bloklar boş). İlk video çıktıktan sonra o videonun kendisi
şablon kaynağı olur ve bloklar doldurulur.

### 6. Enes: kontrol + export

Export daima elde.

---

## Bilinmesi gereken tuzaklar

- **CapCut açıkken hiçbir script çalıştırma.** Auto-save diske yazılanı eziyor.
  Pencereyi kapatmak yetmez, tepsiden tam kapat.
- **CapCut taslak kimliği:** kök `draft_content.json > id`, `Timelines/project.json >
  main_timeline_id`, `Timelines/<UUID>/` klasör adı ve iç `draft_content.json > id`
  **dördü de aynı olmak zorunda**. Sapması taslağın açılmamasına yol açıyor (sessizce).
  `capcut_havuz.py > dogrula()` bunu üretimden sonra kontrol ediyor.
- **SSL:** bu makinede Python'un varsayılan CA bundle'ı tanımsız; `api.pexels.com`
  ve ElevenLabs çağrıları `certifi` bağlamı gerektiriyor. `indir.py`, `tts.py`,
  `transcribe.py` içinde çözülü.
- **`uvx` PATH'e eklendi** (2026-08-16). Yedek: `PATH-yedek-20260816.txt`.
- **computer-use ile CapCut denetlenemiyor:** izin sistemi `...\CapCut\Apps\capcut.exe`
  kaydediyor, süreç `...\Apps\9.2.0.3931\CapCut.exe` yolundan çalışıyor → pencere
  maskeleniyor. CapCut doğrulaması Enes'te.

## Rol kuralı

Enes solution architect ve teknik/teknoloji kararlarını o veriyor.
**Plan kurmadan önce sor, onay almadan inşaya geçme.** Bu parametre seçimlerini de
kapsıyor (çözünürlük, ses ayarı vb.) — ölçümü sun, kararı Enes versin.
