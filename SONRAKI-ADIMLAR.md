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

## Durum: kurgu + VO tamam, altyazı bekliyor

Enes 7 klibi timeline'a dizdi (33.3 sn). Anlatım **clickbait/anlatı stiline göre
yeniden yazıldı** (`presets/senaryo-stili.md` — referans: "Tüy Hırsızı Kuşlar"
shorts'u, transkripti `output/referans_tuy-hirsizi_tr.json`). VO 33.1 sn, taslağa
enjekte edildi (audio track, volume 1.0), kurguyla oranı 0.99. Kelime zamanlı
transkript güncel: `output/ahtapot-uc-kalp_vo_tr.json`.

**Senaryo kuralı bundan sonra:** her plan.json anlatımı `presets/senaryo-stili.md`
formülüne göre yazılır — kanca (izleyiciye hitap + absürt tehdit/vaat) → kurulum →
iç ses (hayvana replik) → "ama" ile tersine dönüş → kısa kapanış. Konu asla başta
anons edilmez.

## Yapılacaklar

### 1. Enes: altyazı stilini bir kere kur  ← ŞU AN BURADA

Kanalın karaoke altyazı stilini taşıyan taslak yok, klonlanacak kaynak lazım.
Karar: **stili Enes kuracak** (reklam taslaklarından klonlanmayacak — kanal kimliği).

CapCut'ta `ahtapot-uc-kalp` taslağını aç → tek bir metin ekle, fontu/rengi/konturu/
animasyonu kanalın istediği gibi ayarla → **tepsiden TAM kapat**.
Sonra `preset.json > seslendirme.style_from` = `ahtapot-uc-kalp` yapılır ve
altyazı bu stille üretilir:

```bash
python scripts/capcut_captions.py --draft ahtapot-uc-kalp --transcript output/ahtapot-uc-kalp_vo_tr.json
```

Stil bir kere kurulduktan sonra sonraki tüm videolar bu taslaktan klonlar.

### 2. Enes: kontrol + export

Export daima elde.

**Müzik / efekt / geçiş / hook text hâlâ atlanıyor** — `preset.json`'daki o bloklar
boş. İlk video çıktıktan sonra o videonun kendisi şablon kaynağı olur.

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
