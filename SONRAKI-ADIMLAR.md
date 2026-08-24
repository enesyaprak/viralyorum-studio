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
| **Geçişler** | `Left → Down → Pull In II → Pull & Reveal`, kesme fazlaysa baştan döner | Enes kurdu, `ahtapot-uc-kalp` (2026-08-16) |
| **VO seviyesi** | volume 1.63 (arkaplan sesinin üstünde net dursun) | Enes ayarladı (2026-08-16) |
| **Altyazı stili** | `ahtapot-uc-kalp` taslağından klonlanır (CapCut şablonu 跟读手写黄), 2-3 kelimelik karaoke | Enes kurdu (2026-08-16) |
| **Senaryo** | `presets/senaryo-stili.md` **6-parça formülü** (kanca→netleştirme→iç ses→rehook→tersine dönüş/payoff→kapanış), netlik-merak dengesi, sonunda sabit soru CTA'sı | "Tüy Hırsızı Kuşlar" ref. + uzman revizyonu (2026-08-21) |
| **Hedef süre** | 26-30 sn (~335-390 karakter, CTA dahil — `karakter_hiz` 12.9). Liste/çok-konulu videoda bant aşılabilir (acimasiz-anneler 45 sn) | Enes kararı (2026-08-21); karakter bütçesi 2026-08-23'te 1.05x VO'ya göre kalibre edildi |
| **Açılış karesi** | aydınlık/yüksek kontrast, özne ilk karede tanınır — karanlık açılış yasak | YouTube analizi sonrası Enes kararı (2026-08-19) |
| **VO hızı** | ElevenLabs `speed 1.05`, ek ffmpeg hızlandırma KAPALI (`vo_hizlandirma 1.0`); uydurma üst sınırı x1.10 (`vo_uydur_ust`) | Enes: "hızlı, insanlar algılayamıyor" (2026-08-22) — eski 1.20×1.15 profili iptal |
| **senaryo.txt** | `capcut_havuz.py` her projede otomatik üretir — Enes CapCut auto clipping (akıllı klip) **outline** alanına bunu yapıştırıyor | Enes'in iş akışı (2026-08-16) |

Logo ve müzik dosyaları `Downloads`'tan repoya alındı — Downloads temizlenirse
üretim kırılmasın diye. Logonun zemini `logo_seffaf.py` ile şeffaflaştırıldı
(CapCut'taki jpg sürümü beyaz kare gösteriyordu).

**`ahtapot-uc-kalp` referans taslaktır — silme.** Logo yerleşimi, altyazı stili ve
geçiş prototipleri oradan klonlanıyor. Silinirse şablon kaybolur.

Marka zinciri boş bir taslak kopyası üzerinde uçtan uca test edildi (2026-08-16):
logo doğru ölçek/konumla (0.145 / x 0.0 / y 0.827) tam video boyunca, arkaplan sesi
0.24 seviyede 1.87. sn'den, 6 geçiş doğru sırayla eklendi.

## Yapılacaklar

### AKTİF VİDEO: `acimasiz-anneler`  ← ŞU AN BURADA (2026-08-23)

"Doğanın en vicdansız 5 annesi" — panda / guguk / kara kartal / hamster / fok.
**Liste formatı**, 45 sn hedef, 604 karakter (~47 sn VO). Klipler indi, havuz kuruldu
(**17 benzersiz klip** — hızlı kesme için bilerek bol), `senaryo.txt` hazır.
`plan.json > cta` ile videoya özel tartışma CTA'sı kullanılıyor.
**Kaldı:** Enes outline'ı yapıştırıp dizer (timeline ~47 sn olmalı) → tepsiden kapat →
`python scripts/uret.py --proje acimasiz-anneler --draft acimasiz-anneler`.
Bu video, 2026-08-23 pipeline revizyonunun (TTS önbelleği, x1.10 tempo kilidi,
otomatik sync, CTA override) ilk tam testi.

### EXPORT BEKLİYOR: `bal-arisi-isi-topu` (2026-08-21)

Japon bal arısı / ısı topu savunması. Uçtan uca üretildi, **export bekliyor**.
7 sahne, 21 sn. `uret.py` çalıştı: VO+altyazı+müzik+logo+4 geçiş bası, **VO kurguya
tam oturdu** (x1.167 atempo, kırpılma yok). Timeline 21 sn hedef 26-30'un altında
ama Enes "böyle bırak, export et" dedi.
**Kaldı:** Enes CapCut'ta kontrol + export. Not: altyazı 6-7'de replik tırnakları
(`'iğnemiz bu zırhı delmez'`) garip-karakter uyarısı verdi — CapCut'ta kontrol,
çirkinse elle sil.

Bu, **yeni güçlendirilmiş 6-parça formülle** (rehook + net payoff, bkz.
`senaryo-stili.md` 2026-08-21 revizyonu) üretilen İLK video.

### BİTTİ: `guguk-yuva-paraziti`  (Enes elle bitirdi, 2026-08-21)

Klip+havuz+senaryo+üretim tamam; Enes CapCut'ta kendi bitirip kapattı. Dönme.
Senaryo 26-30 banda inecek şekilde kısaltılmıştı (513→448 karakter). Başlık clickbait,
etiketler optimize (plan.json). `ahtapot-uc-kalp` gibi referans olarak durabilir.

**Tekrarlayan süre sorunu:** hem guguk (24.9 uzun VO) hem bal arısı (21 kısa) auto
clipping timeline'ı hedef banttan (26-30) saptı. Enes'in dizerken hedef süreyi
tutturması ya da senaryo.txt'ye hedef sn notu düşmek düşünülebilir.

#### Yeni bir video açarken (guguk bittikten sonra)

```bash
python scripts/yeni.py <slug>
```

1. `plan.json`: konu + `presets/senaryo-stili.md` formülüyle anlatım.
   Hedef karakter = **kurgu saniyesi × `karakter_hiz` (12.9)**; CTA otomatik ekleniyor,
   onu da paya kat (`plan.json > cta` ile videoya özel CTA yazılabilir).
   **Havuz bol tut: klip sayısı ≈ video saniyesi ÷ 3** (hızlı kesme kuralı, 2026-08-23)
2. Claude MCP ile klip seçer (4K, gerçek çekim, AI üretimi eleniyor) → `indir.py`
3. `capcut_havuz.py` → havuz + `projeler/<slug>/senaryo.txt` çıkar →
   Enes CapCut'ta **auto clipping outline'a senaryo.txt'yi yapıştırıp** dizer →
   tepsiden tam kapatır
4. `uret.py`: TTS → VO → altyazı → **arkaplan sesi + logo + geçişler otomatik**
5. Enes: kontrol + export

Enes'in elle yapması gereken tek şey: **dizme ve export**.

---

## Bilinmesi gereken tuzaklar

- **CapCut'ın OKUDUĞU dosya `Timelines/<UUID>/draft_content.json`.** Kök
  `draft_content.json`'ı editleyip bu dosyayı güncellemezsen CapCut projeyi ESKİ
  haliyle açar ve kapanışta o eski hali bütün dosyalara yazıp editi siler — hiçbir
  uyarı, hiçbir "kurtar" dialogu çıkmadan. `agaclarin-agi` ve `karinca-koprusu`'nda
  VO+altyazı+müzik+logo+geçiş bu yüzden iki kez uçtu. `capcut_sync` 2026-08-20'den
  beri bu dosyayı da yazıyor (Enes onayı); iki dosyanın `id`'si ve klasör adı aynı
  olduğu için içerik birebir kopyalanabiliyor.
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
- **`senaryo.txt` ile VO metni BİREBİR aynı olmalı.** Enes klipleri CapCut auto
  clipping'e senaryo metnini vererek dizdiriyor; VO da aynı `plan.json` anlatımından
  üretiliyor. `plan.json` değişirse `senaryo.py` yeniden çalıştırılmalı, yoksa kurgu
  ile ses kayar.
- **Altyazıları compound clip'e alırsan script onları GÖREMEZ.** Enes altyazılar
  kliplere yapışıp kaymasın diye hepsini compound clip yapıyor; compound'un içeriği
  `draft_content.json`'da görünmüyor. `uret.py` artık bunu tanıyıp ikinci set altyazı
  basmıyor (2026-08-18'de basmıştı, ekranda çift altyazı oldu). Altyazıyı yeniden
  ürettirmek istersen önce CapCut'ta compound'u çöz.
- **`capcut_havuz.py` var olan taslak adının üstüne yazmaz.** Yeniden kurmak
  gerekirse önce `%LOCALAPPDATA%\CapCut Drafts\<ad>` klasörünü kaldır.
  (2026-08-16'da eski 1 kliplik taslak yedeklenip kaldırıldı, yenisi kuruldu.)
- **İskelet cover'sızsa `capcut_havuz.py` artık otomatik kopyalıyor** (2026-08-21).
  `0820` iskeletinde `draft_cover.jpg` yoktu → `dogrula()` "CapCut açamaz" deyip
  `sys.exit` ile çıkıyor ve senaryo.txt üretilmiyordu (guguk'ta yaşandı; o sefer
  cover elle kopyalanıp senaryo.py elle çalıştırıldı). Fallback eklendi: `copytree`
  sonrası cover yoksa `DRAFTS`'taki çalışan bir taslaktan kopyalanıyor. Bal arısında
  sorunsuz çalıştı ("kapak: 0418 (1)'ten kopyalandi").
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
Kod/preset/kural **değişikliklerinde** onay almadan uygulama (2026-08-19 kararı) —
**ama rutin YÜRÜTMEDE Enes'i meşgul etme**: klip seçimi, `indir.py`, `capcut_havuz.py`
+ `senaryo.py` doğrudan yapılır, sonuç raporlanır.

**"CapCut kapalı mı?" diye SORMA** (2026-08-23 Enes kararı): yeni video hazırlarken
CapCut zaten kapalı; ayrıca `capcut_havuz.py` ve `uret.py` içinde
`capcut_guard.dur_capcut_acikken()` kilidi var — açıksa script kendisi duruyor.
İstisna: **`uret.py`**, Enes'in elle dizdiği timeline'ın üstüne yazdığı için
"dizdim, kapattım" haberi beklenir.

Enes kontrolü CapCut'ta dizerken yapıyor (2026-08-16 kararı).
