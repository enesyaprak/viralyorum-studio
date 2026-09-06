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

### AKTİF VİDEO: `deve-horguc`  ← ŞU AN BURADA (2026-08-23)

"Devenin hörgücünde su yok" — MİT YIKMA formatı (kanalda ilk). Hörgüç yağ deposu,
oval alyuvarlar, 10 dk'da 100 litre, insan %15 su kaybında ölür / deve %30'a dayanır.
36 sn, 466 karakter, **14 klip havuzda**, senaryo.txt hazır.
**Kaldı:** Enes outline'ı yapıştırıp dizer (timeline ~36 sn) → tepsiden kapat →
`python scripts/uret.py --proje deve-horguc --draft deve-horguc`.

### EXPORT BEKLİYOR (5 video, hepsi üretildi)

| Proje | Süre | Not |
|---|---|---|
| `bal-arisi-isi-topu` | 21 sn | Altyazı 6-7'de replik tırnakları garip karakter uyarısı verdi |
| `acimasiz-anneler` | 47 sn | 5 hayvan listesi, tartışma CTA'sı (`plan.json > cta`) |
| `canli-silahlar` | 47.9 sn | En temiz koşu: oran 0.98, 0 şüpheli altyazı, 18 geçiş |
| `inek-arkadaslik` | 34.5 sn | Metin dizimden SONRA güçlendirildi → kesme noktaları eski outline'a göre |
| `ucan-yilan` | 36.1 sn | Sadece 3 geçiş; havuzda 14 klipten 7'si kullanılmamış, istenirse yeniden dizilip bedava tekrar koşulabilir |

**Tekrarlayan tırnak sorunu:** ElevenLabs transkripti düz tırnağı kıvrık tırnağa
(" ") çeviriyor, altyazıda çirkin duruyor (bal-arısı, acımasız-anneler, inek).
Kalıcı çözüm: altyazıya giderken tırnakları düzleştiren bir adım — Enes onayı bekliyor.

### BİTTİ: `guguk-yuva-paraziti`  (Enes elle bitirdi, 2026-08-21)

Klip+havuz+senaryo+üretim tamam; Enes CapCut'ta kendi bitirip kapattı. Dönme.
Senaryo 26-30 banda inecek şekilde kısaltılmıştı (513→448 karakter). Başlık clickbait,
etiketler optimize (plan.json). `ahtapot-uc-kalp` gibi referans olarak durabilir.

**Tekrarlayan süre sorunu:** hem guguk (24.9 uzun VO) hem bal arısı (21 kısa) auto
clipping timeline'ı hedef banttan (26-30) saptı. Enes'in dizerken hedef süreyi
tutturması ya da senaryo.txt'ye hedef sn notu düşmek düşünülebilir.

#### Yeni bir video açarken — GÜNCEL AKIŞ (2026-08-23 akşamı, Enes kararı)

**Sıra değişti: VO ARTIK ÖNCE GİRİYOR.** Eskiden Enes dizerdi, sonra VO basılırdı; bu
yüzden bütün gün "VO 33 sn / timeline 36 sn" sürtünmesi yaşandı. Artık VO referans,
kurgu ona göre yapılıyor.

```bash
python scripts/yeni.py <slug> --sure 35
# plan.json: konu + senaryo (senaryo-stili.md 6-parca formulu)
# hedef karakter = kurgu saniyesi x karakter_hiz (15.1)
# havuz bol tut: klip sayisi ~ video saniyesi / 3
python scripts/klip_ekle.py --proje <slug> --klasor ~/Downloads/<konu>   # ENES'IN KLIPLERI
python scripts/indir.py --proje <slug>                                   # TELIFSIZ DESTEK
python scripts/capcut_havuz.py --proje <slug> --ad <slug>
python scripts/uret.py --proje <slug> --draft <slug> --sablon    # VO + ALTYAZI
```

#### HIBRIT KLIP AKISI (2026-09-04, Enes karari)

Klipler artik **iki kaynaktan** geliyor ve ikisi de ayni havuza akiyor:

| Bacak | Komut | Lisans | Rol |
|---|---|---|---|
| Enes bulur | `klip_ekle.py` | ispatli DEGIL | konunun **kahraman** goruntusu (Instagram vb.) |
| Claude bulur | `indir.py` | Pexels/Pixabay/Commons - ispatli | **destek/dolgu** planlar |

```bash
python scripts/klip_ekle.py --proje bal-porsugu --klasor ~/Downloads/honeybadger
# -> footage/ig_01.mp4 ...  + onizleme/ig_01.jpg (KONTAK SAYFASI)
# Claude onizleme/*.jpg'lere BAKAR, senaryoyu eldeki goruntuye gore yazar
python scripts/klip_ekle.py --proje bal-porsugu --ad 1=leopar-kacar,2=kobra-avi
```

**Neden kontak sayfasi:** bal-porsugu'nda ilk metin goruntu gorulmeden yazilmisti;
icinde goruntusu OLMAYAN sahneler vardi ("deri icinde donup isirma", "zehirden bayilma"),
elimizdeki en guclu uc goruntu (leopar kacisi / bal petegi / kobra avi) ise metinde hic
gecmiyordu. Kontak sayfalarina bakildiktan sonra metin bastan yazildi ve hook artik en
sert klibe oturuyor. **Kural: senaryo, klipler gorulduKTEN sonra yazilir.**

**Telif kaydi ayrisik tutuluyor:** `klip_ekle.py` kendi kliplerini `"kaynak": "elle"` ve
`"lisans": "ISPATLI DEGIL"` diye isliyor. Boylece `kaynaklar.json` hangi klibin lisansi
kanitli, hangisinin degil ayirt edilebiliyor - Pexels/Commons kayitlarinin degeri bozulmuyor.
Claude Instagram indirici YAZMIYOR/otomatiklestirmiyor; klipleri Enes getiriyor.

**Diger notlar:**
- Yatay ve 3 sn'den kisa klipler uyari veriyor (9:16 kirpma / hizli kesmede yetersiz).
- Ayni dosya iki kere alinmaz (`orijinal_ad` ile eslesme); tekrar icin `--zorla`.
- mp4 disi (webm/mov) otomatik H.264 mp4'e cevriliyor - CapCut uyumu.
- Meta'nin **"AI" etiketi** tasiyan klipler cikiyor (bal-porsugu ig_aslan-surusu). Script bunu
  tespit EDEMEZ - kontak sayfasinda kosede rozet gorunuyorsa o klibi kullanma.

#### CTA artik VIDEOYA OZEL (2026-09-04, Enes karari)

Sabit *"Siradaki hangi hayvan olsun?"* KALDIRILDI — yorum getirmiyordu (Enes: *"sıradaki
hayvan ne olsun nerden bilsin adam"*). Artik her videonun CTA'si `plan.json > "cta"`
alaninda, konuya bagli **ikili/tartismali soru** olarak yaziliyor:

```json
"cta": "Bal porsuğu mu kazanır, sırtlan mı? Yorumlara yaz."
```

- `senaryo.py` ve `uret.py` ikisi de `plan > cta`'yi oncelikli okuyor (kod zaten destekliyordu);
  eksik olan `yeni.py`'nin bu alani iskelete koymamasiydi — eklendi, rehber notuyla birlikte.
- `preset.json > kapanis_cagri` artik sadece **yedek**: plan'da `cta` bossa devreye girer.
- Kural detayi: `presets/senaryo-stili.md` > kapanis cagrisi maddesi. Ozet: cevabi videoda
  VERILMEMIS bir soru sor, yoksa tekrar olur.

```bash
```

Sonra **Enes**: CapCut'ta açar → **auto clipping** (outline'a senaryo.txt) ile dizer →
timeline'ı VO süresine kırpar → tepsiden kapatır.

```bash
python scripts/uret.py --proje <slug> --draft <slug> --atla vo,altyazi   # muzik+logo+gecis
```

Sonra Enes: kontrol + export.

**Doğrulandı (deve-horguc, 2026-08-23):** auto clipping önden konan VO'yu ve altyazıyı
SİLMİYOR — ikisi de sağ kaldı. Yani şablon akışı auto clipping ile uyumlu.

**Bilinmesi gerekenler:**
- `--sablon` modunda VO **uydurulmaz** (`vo_uydur` kapalı) — VO ham temposunda kalır,
  Enes kurguyu ona göre keser. `capcut_muzik.py` boş timeline'da sesi 0 uzunlukta
  ekliyordu, düzeltildi (timeline boşsa sesin kendi süresi + taslak süresi VO'ya eşitlenir).
- Auto clipping klipleri doğal uzunlukta dizdiği için timeline VO'dan uzun çıkıyor
  (deve: 46.9 sn / VO 33.2) — **Enes kuyruğu kırpıyor**, altyazılar VO'ya bağlı olduğu
  için otomatik hizalanıyor.
- **Enes altyazıları compound yapıyor ve sticker ekliyor** (görüntü değişince yazılar
  kayıp bozuluyormuş). Bu yüzden ikinci geçişte rapor `0 altyazi` der — NORMAL, panik yok;
  ikinci geçiş zaten `--atla vo,altyazi` ile altyazıya dokunmuyor.

---

## Klip kaynaklari

| Kaynak | Ne icin | Lisans | Atif |
|---|---|---|---|
| **Pexels** / **Pixabay** (MCP) | Hayvanin KENDISI, estetik/stok cekim, yuksek cozunurluk, dikey | ticari serbest | gerekmez |
| **Wikimedia Commons** (`scripts/ara_commons.py`) | Hayvanin YAPTIGI SEY - davranis kaydi | CC0 / CC-BY / CC-BY-SA | **CC-BY'de ZORUNLU** |

**Neden Commons eklendi (2026-08-23):** Pexels/Pixabay stok odakli; hayvani bulursun ama
davranisini bulamazsin. Uc konuda duvara toslandi: biyolüminesans (0 gercek klip, sadece AI),
ucan yilan suzulme (0), guguk yuva parazitligi (0). Commons'a bilim insanlari/belgeselciler
yukluyor - ornek: `Common cuckoo (Cuculus canorus) and host.webm` (1280x720, 87 sn, CC BY 3.0)
tam da guguk videosunda bulamadigimiz kare.

```bash
python scripts/ara_commons.py "Cuculus canorus" --limit 20
python scripts/ara_commons.py "bioluminescence" --json   # plan.json'a yapistirmak icin
```

Secilen klip plan.json'a `"kaynak": "commons"` ile yazilir. `indir.py`:
- webm/ogv/mkv indirir ve **otomatik H.264 mp4'e cevirir** (CapCut webm'i duzgun almiyor)
- CC-BY kliplerde is bitince **atif blogu basar** - o metni video aciklamasina yapistir

**Sinirlari:** cozunurluk dusuk olabiliyor (320x240 - 1280x720 tipik), cogu yatay,
bazi sonuclar laboratuvar/mikroskop kaydi. Yani ana govde yine Pexels/Pixabay; Commons
"baska turlu bulunamayan tek kare" icin.

**Instagram/TikTok'tan klip CEKILMEZ** (2026-08-23 Enes sordu, gerekce): telifli icerik,
ticari kullanim lisansi yok, Content ID/strike riski var ve platform ToS'u yasakliyor.
Kanalin telif disiplini `kaynaklar.json` uzerine kurulu - bozulmayacak.

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
