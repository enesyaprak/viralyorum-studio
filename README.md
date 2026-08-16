# viralyorum-studio

`viralyorumyt` kanalı için **anlatım shorts** üretim hattı.
Format: ElevenLabs anlatım + stok görüntü + karaoke altyazı + müzik.

Telif temiz (YPP'ye uygun). Kanalın en çok izlenen videosu (AI balina, ~600k) bu formattaydı.

Repo **tam bağımsız** — CapCut motoru (`capcut_*.py`) bluemedya-video-editor'dan kopyalandı,
çalışmak için o repoya ihtiyaç duymaz.

---

## Katmanlar

| # | Katman | Nasıl | Kim |
|---|---|---|---|
| 1 | Senaryo → `plan.json` | hook + sahne anlatımları + İngilizce arama terimleri | Claude |
| 2 | Klip arama/seçim | **Pexels + Pixabay MCP** — adaylar görülür, seçilir | Claude |
| 3 | İndirme + lisans kaydı | `indir.py` | otomatik |
| 4 | VO (TTS) | `tts.py` → ElevenLabs | otomatik |
| 5 | Dizme / kesme | CapCut smart clipping | **Enes** |
| 6 | Altyazı | `transcribe.py` (Scribe) → karaoke | otomatik |
| 7 | Müzik / efekt / geçiş / hook text | `uret.py` zinciri | otomatik |
| 8 | Export | — | **Enes** |

4, 6 ve 7 tek komutta: `uret.py`.

---

## Kurulum (bir kere)

**1. API anahtarları** — `.env.example` → `.env` kopyala, doldur:
- Pexels: https://www.pexels.com/api/ (ücretsiz)
- Pixabay: https://pixabay.com/api/docs/ (ücretsiz)
- ElevenLabs: bluemedya `.env`'den kopyalanabilir

MCP server'ları `.mcp.json`'da `${PEXELS_API_KEY}` şeklinde okuduğu için bunları
**ortam değişkeni** olarak da tanımla:

```bash
setx PEXELS_API_KEY "buraya_anahtar"
```

**2. MCP server'ları** — `.mcp.json` hazır, ikisi de test edildi (initialize + tools/list).

- **pexels** → `uvx --with "mcp<2" pexels-mcp-server` — 8 tool (`videos_search`, `video_get`, ...)
- **pixabay** → `npx.cmd -y pixabay-mcp@latest` — 2 tool (`search_pixabay_videos`, `search_pixabay_images`)

İki tuzak, ikisi de çözüldü ve config'e gömüldü:

- **`mcp<2` pin zorunlu.** `pexels-mcp-server` 0.0.4 düşük seviye `@server.list_tools()`
  API'sini kullanıyor; bağımlılık çözümü serbest bırakılırsa `mcp` 2.0.0 geliyor ve
  `AttributeError: 'Server' object has no attribute 'list_tools'` ile ölüyor.
  Pin **komutun içinde** olmalı — `uvx` her çağrıda geçici ortam kurduğu için
  `uv tool install --with` ile yapılan pin `.mcp.json`'a yansımıyor.
- **`uvx` PATH'te değildi.** `pip install uv` onu
  `%APPDATA%\Python\Python314\Scripts\` altına koyuyor. O dizin kullanıcı PATH'ine
  eklendi (2026-08-16), config artık sade `"command": "uvx"` kullanıyor.
  Ekleme `[Environment]::SetEnvironmentVariable` ile yapıldı — `setx` kullanılmamalı,
  PATH 1724 karakter ve `setx` 1024'ü aşanı kırpıyor.
  Değişiklik öncesi yedek: `PATH-yedek-20260816.txt`.

**3. `preset.json`** — boş alanları doldur (voice ID, hangi CapCut taslağından
müzik/efekt/geçiş/text stili klonlanacak). **Boş alan = o adım atlanır**, uydurma yapılmaz.

---

## Bir video üretme akışı

```bash
python scripts/yeni.py ahtapot-uc-kalp
```

`projeler/<slug>/plan.json` açılır → konu, hook, sahne anlatımları ve her sahne için
**İngilizce** arama terimleri doldurulur (Claude yazar).

Sonra Claude MCP ile klipleri arar, adayları değerlendirir, seçtiklerini sahnelerin
`klipler` alanına yazar. Ardından:

```bash
python scripts/indir.py --proje ahtapot-uc-kalp
```

Klipler `projeler/<slug>/footage/` altına iner. Her klibin kaynağı ve lisansı
`kaynaklar.json`'a yazılır — **telif kanıtı, sakla**.

Sonra klipler yeni bir CapCut taslağına medya havuzu olarak import edilir:

```bash
python scripts/capcut_havuz.py --proje ahtapot-uc-kalp --ad ahtapot-uc-kalp
```

Boş bir taslağı iskelet alıp (otomatik bulur) yeni taslak üretir: canvas 1080x1920,
**timeline boş**, klipler medya sekmesinde hazır. Timeline'a dokunulmaz — CapCut'ın
timeline'ı kendi kurması, dışarıdan yazılan segmentlerin ezilmesi riskini ortadan kaldırıyor.
Var olan bir taslak adının üstüne yazmaz, hata verip durur.

Sonra Enes:
1. CapCut'ı açar, taslak listesinden yeni projeyi açar
2. Klipleri smart clipping ile dizer/keser
3. **CapCut'ı tepsiden TAM kapatır**

```bash
python scripts/uret.py --proje ahtapot-uc-kalp --draft "ahtapot"
```

TTS → VO enjekte → Scribe transcribe → karaoke altyazı → müzik → efekt → geçiş →
hook text → sözlük düzeltmesi → şüpheli altyazı raporu.

Sonra CapCut'ı aç, rapordaki şüpheli satırlara bak, export et.
Açılışta "kurtar/recover" dialogu çıkarsa **reddet**.

---

## Kritik kurallar (bluemedya'da acıyla öğrenildi)

- **CapCut açıkken script çalıştırma.** Auto-save diske yazılan editleri eziyor.
  `capcut_guard` bunu yakalayıp durduruyor ama pencereyi kapatmak yetmez —
  **tepsiden tam kapat**.
- **Template'ten proje başlatma.** Template projelerin `draft_content.json`'ı şifreli
  (base64 blob), scriptler okuyamıyor. Sıfırdan kes.
- **VO süresi ≈ video süresi.** `uret.py` oranı ölçüp uyarıyor. VO kısaysa
  `plan.json` anlatımlarını uzat (~15 karakter/saniye).
- **Export daima elde.** Otomatikleştirilmiyor.
- Text `y` değeri **pozitif = yukarı**. 0.45 = orta-üst, Meta kırpma payı bırakır.

---

## Klip seçim kuralları

- **En yüksek çözünürlüğü indir (4K).** Enes'in kararı. Pexels aynı klibi 360p'den
  4K'ya kadar veriyor; mevcut olan en yükseği alınır — kesme/zoom/reframe payı kalsın diye.
  Boyut bilgisi (karar değil, sadece bilgi): 7 sn'lik klip 4K'da ~52 MB, 1080x1920'de ~17 MB.
- **Dikey (portrait) tercih et.** Pexels'te `orientation=portrait` filtresi var.
  Yatay klip 9:16'ya kırpılınca kadrajın yarısı gidiyor.
- Sahne süresinden **uzun** klip seç; kesme payı kalsın.

---

## Notlar

- Arama terimleri **İngilizce** olmalı; stok arşivler İngilizce etiketli.
  Her sahneye 2-3 yedek terim yaz.
- **SSL notu:** bu makinede Python'un varsayılan CA bundle'ı tanımsız
  (`ssl.get_default_verify_paths().cafile == None`) ve `api.pexels.com`
  "certificate has expired" veriyor. `indir.py` bunu `certifi` bundle'ıyla çözüyor
  (`ssl_baglami()`). OS seviyesinde sorun yok — sadece Python'u etkiliyor.
- `presets/altyazi_sozluk.json` şeması bluemedya ile aynı (`global` + `markalar`)
  ki kopyalanan `capcut_altyazi.py` değişmeden çalışsın. Bu repoda `markalar` =
  **konu grubu** (deniz, genel_biyoloji...). Her videoda Scribe'ın bozduğu terim
  buraya eklenir.
- AI video üretimi şimdilik **yok** (karar). Bağlı MCP hesabı free plan / 10 kredi.
- Ek Python bağımlılığı yok — stdlib + ffmpeg + CapCut.
