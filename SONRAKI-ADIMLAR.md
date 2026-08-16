# Sonraki adımlar — ilk videoyu bitirme

Hedef: `ahtapot-uc-kalp` videosunu uçtan uca bitirmek. Stok üretimi ondan sonra.

## Şu an hazır olanlar

| Parça | Durum |
|---|---|
| MCP (`pexels`, `pixabay`) | `.mcp.json` hazır, ikisi de test edildi |
| API anahtarları | `.env` + kalıcı ortam değişkeni (`PEXELS_API_KEY`, `PIXABAY_API_KEY`, `ELEVENLABS_API_KEY`) |
| Ses | Doga (`IuRRIAcbQK5AQk1XevPj`), yüksek enerji profili — `preset.json` içinde |
| Plan | `projeler/ahtapot-uc-kalp/plan.json` — 7 sahne, **7 klip seçili** |
| Footage | 7 klibin hepsi indi (`footage/`), lisans kaydı `kaynaklar.json`'da |
| CapCut taslağı | `ahtapot-uc-kalp` **yeniden kuruldu** (2026-08-16), 7 klip havuzda, timeline boş, dört kimlik doğrulandı |

### Seçilen klipler (hepsi Pexels, hepsi gerçek çekim — AI üretimi yok)

| Sahne | id | Çözünürlük | Süre | Sahibi | İçerik |
|---|---|---|---|---|---|
| 1 | 35819970 | 2160x3840 | 7 sn | JUN HO LEE | mercan resifi |
| 2 | 11334970 | 3840x2160 | 32 sn | Magda Ehlers | ahtapot yakın plan, koyu mavi |
| 3 | 17841948 | 3840x2160 | 12 sn | Adrien JACTA | ahtapot yüzerken |
| 4 | 15623348 | 3840x2160 | 22 sn | Jozef Papp | ahtapot kayalık tabanda yürürken |
| 5 | 34268912 | 2160x3840 | 17 sn | Pramod Giri | derin mavide denizanası ("mavi kan") |
| 6 | 33422094 | 2160x3840 | 13 sn | JUN HO LEE | karanlık derin mavi mağara |
| 7 | 17836505 | 2160x3840 | 17 sn | Entdecker Fuchs | ahtapot portresi (kapanış) |

2, 3, 4 yatay 4K — 9:16'ya kırpılınca 1215x2160 kalıyor, yine de 1080x1920 hedefinin
üstünde. Dikey gerçek ahtapot görüntüsü stokta neredeyse yok; dikey olanların hepsi
AI üretimiydi ve elendi.

## Durum: video export'a hazır

Enes 7 klibi timeline'a dizdi (33.3 sn). Anlatım **clickbait/anlatı stiline göre
yeniden yazıldı** (`presets/senaryo-stili.md` — referans: "Tüy Hırsızı Kuşlar"
shorts'u, transkripti `output/referans_tuy-hirsizi_tr.json`). VO 33.1 sn, taslağa
enjekte edildi (audio track, volume 1.0), kurguyla oranı 0.99. Kelime zamanlı
transkript güncel: `output/ahtapot-uc-kalp_vo_tr.json`.

**Senaryo kuralı bundan sonra:** her plan.json anlatımı `presets/senaryo-stili.md`
formülüne göre yazılır — kanca (izleyiciye hitap + absürt tehdit/vaat) → kurulum →
iç ses (hayvana replik) → "ama" ile tersine dönüş → kısa kapanış. Konu asla başta
anons edilmez.

## Her videoda sabit (marka şablonu)

Bunlar `preset.json`'da tanımlı ve `uret.py` her videoda **otomatik** uyguluyor.
Enes'in tekrar elle eklemesi gerekmiyor.

| Öğe | Ayar | Kaynak |
|---|---|---|
| **Logo** | `presets/marka/viralyorum-logo.png`, ölçek 0.145, x 0.0 / y 0.827 (üst-orta), video boyunca, overlay track | Enes'in `ahtapot-uc-kalp` yerleşimi (2026-08-16) |
| **Arkaplan sesi** | `presets/muzik/good-starts-jingle-punks.mp3`, volume 0.24, dosyanın 1.87. sn'sinden başlar | Enes seçti (2026-08-16) |
| **Geçişler** | Girişte `Unfold`, sonra `Camera Left → Camera Down → Camera Right → Camera Up` sırayla | Enes'in kararı (2026-08-16) |
| **Altyazı stili** | `ahtapot-uc-kalp` taslağından klonlanır (CapCut şablonu 跟读手写黄), 2-3 kelimelik karaoke | Enes kurdu (2026-08-16) |
| **Senaryo** | `presets/senaryo-stili.md` formülü | "Tüy Hırsızı Kuşlar" referansı |

Logo ve müzik dosyaları `Downloads`'tan repoya alındı — Downloads temizlenirse
üretim kırılmasın diye. Logonun zemini `logo_seffaf.py` ile şeffaflaştırıldı
(CapCut'taki jpg sürümü beyaz kare gösteriyordu).

**Geçişler için tek seferlik ön koşul:** `capcut_gecis.py` geçiş prototipini
diskteki taslaklardan buluyor. `Camera Right` mevcut, ama **`Unfold`, `Camera Left`,
`Camera Down`, `Camera Up` bu makinede hiç kullanılmamış** — Enes bunları CapCut'ta
bir kere uygulayınca prototipleri diske yazılıyor ve sonrasında her video otomatik alıyor.

## Yapılacaklar

### 1. Enes: kontrol + export  ← ŞU AN BURADA

Video hazır: 7 klip (33.3 sn) + VO (33.1 sn) + 31 karaoke altyazı.
CapCut'ı aç, altyazıları gözden geçir, export al. Export daima elde.

**Müzik / efekt / geçiş / hook text hâlâ atlanıyor** — `preset.json`'daki o bloklar
boş. Bu video export edilince kendisi şablon kaynağı olur; o bloklar
`ahtapot-uc-kalp` taslağını gösterecek şekilde doldurulur.

### 2. Sonraki video

`python scripts/yeni.py <slug>` → plan.json'u `presets/senaryo-stili.md` formülüne
göre yaz → MCP ile klip seç → `indir.py` → `capcut_havuz.py` → Enes dizer →
`uret.py`. Altyazı stili artık `preset.json > style_from = ahtapot-uc-kalp`
üzerinden otomatik klonlanıyor, Enes'in tekrar stil kurmasına gerek yok.

---

## Bilinmesi gereken tuzaklar

- **CapCut açıkken hiçbir script çalıştırma.** Auto-save diske yazılanı eziyor.
  Pencereyi kapatmak yetmez, tepsiden tam kapat.
- **CapCut taslak kimliği:** kök `draft_content.json > id`, `Timelines/project.json >
  main_timeline_id`, `Timelines/<UUID>/` klasör adı ve iç `draft_content.json > id`
  **dördü de aynı olmak zorunda**. `capcut_havuz.py > dogrula()` bunu kontrol ediyor.
- **`capcut_audio.py` var olan ses materyalini DEĞİŞTİRİR, sıfırdan eklemez.**
  Şablonsuz ilk videoda taslakta hiç ses materyali olmadığı için hata veriyordu.
  `uret.py` artık bu durumda `capcut_muzik.py --audio` ile ses elementini
  `preset.json > seslendirme.vo_proto` taslağından klonlayıp VO'yu yeni bir audio
  track olarak ekliyor. **VO, timeline süresine kırpılıyor** (`min(vo, video)`) —
  yani VO videodan uzunsa sonu kesilir; oran 1.0'ın altında olmalı.
- **`capcut_havuz.py` var olan taslak adının üstüne yazmaz.** Yeniden kurmak
  gerekirse önce `%LOCALAPPDATA%\CapCut Drafts\<ad>` klasörünü kaldır.
  (2026-08-16'da eski 1 kliplik taslak yedeklenip kaldırıldı, yenisi kuruldu.)
- **SSL:** bu makinede Python'un varsayılan CA bundle'ı tanımsız; `api.pexels.com`
  ve ElevenLabs çağrıları `certifi` bağlamı gerektiriyor. `indir.py`, `tts.py`,
  `transcribe.py` içinde çözülü.
- **`api.pexels.com` Cloudflare 1010 veriyor** eğer istek `Python-urllib/x.y`
  User-Agent'ı ile giderse. Tarayıcı UA'sı gerekiyor. (CDN tarafı — `videos.pexels.com`,
  `indir.py`'nin kendi UA'sıyla sorunsuz çalışıyor.)
- **`uvx` PATH'e eklendi** (2026-08-16). Yedek: `PATH-yedek-20260816.txt`.
- **computer-use ile CapCut denetlenemiyor:** izin sistemi `...\CapCut\Apps\capcut.exe`
  kaydediyor, süreç `...\Apps\9.2.0.3931\CapCut.exe` yolundan çalışıyor → pencere
  maskeleniyor. CapCut doğrulaması Enes'te.

## Rol kuralı

Enes solution architect ve teknik/teknoloji kararlarını o veriyor.
Plan kurmadan önce sor, onay almadan inşaya geçme — **ama rutin yürütmede
(klip seçimi, indirme, havuz kurma) Enes'i meşgul etme**, seçimi yap, sonucu raporla.
Enes kontrolü CapCut'ta dizerken yapıyor (2026-08-16 kararı).
