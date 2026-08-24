# Anlatım shorts senaryo stili

Kaynak: "Tüy Hırsızı Kuşlar" (Tüyler Diken Diken) — 25 sn, ~500 karakter.
Referans transkript: `output/referans_tuy-hirsizi_tr.json`.
Enes'in hedeflediği ton bu (2026-08-16).

**2026-08-21 revizyonu (Enes talebi):** eski metinler merak boşluğu uğruna fazla
belirsiz kalıp izleyiciyi kaybediyordu ("izleyici bu metni anlamaz"). Faceless
shorts uzman kaynaklarından (retention/hook araştırması) üç eksik parça eklendi:
**rehook**, **netlik-merak dengesi**, **net payoff**. Detay aşağıda.

## Formül (6 parça)

| # | Parça | Süre | Kural |
|---|---|---|---|
| 1 | **Kanca** | 0-3 sn | İzleyiciye **doğrudan hitap** + somut/absürt tehdit-vaat. Konu ANONS EDİLMEZ ama **belirsizlik ≠ kafa karışıklığı** — tek bir net görüntü kur. |
| 2 | **Netleştirme** | 3-8 sn | Hook'un açtığı soruyu **kısmen** cevapla: özneyi tanıt, sahneyi anlaşılır kıl. İzleyici *neye baktığını* bilsin; merakı "sırada ne var"a taşı. |
| 3 | **İç ses + kurulum** | 8-14 sn | Hayvana/nesneye **replik ver** — mizah + bilgi aynı cümlede. Sebebi henüz tam verme. |
| 4 | **Rehook** | 14-17 sn | "Ama asıl olay şu" / "İşte tam burada" — orta düşüşü kes, **en vurucu bilgiyi vaat et**. Faceless shorts'ta orta bölüm en çok düşüşün olduğu yer. |
| 5 | **Tersine dönüş + payoff** | 17-25 sn | "Ama..." ile ironiyi patlat **ve asıl şoku NET teslim et**. İzleyici "vaov" demeli, "ne oldu ya?" değil. Hook'ta açılan soru burada kapanır. |
| 6 | **Kapanış + CTA** | 25-28 sn | Tek cümle toparlama (ders verme), sonra sabit soru CTA. |

Not: rehook eklenince yapı 5'ten 6 parçaya çıktı; süre bandı 26-30 sn buna uygun.

## Netlik vs merak dengesi (YENİ — en önemli kural)

Uzman özeti: *"güçlü retention merakla DEĞİL, netlik + merakı birlikte yönetmekle
gelir."* Faceless içerikte yüz yok — izleyici mesaja, yapıya, tona tutunur. Metin
belirsizse tutunacak dal kalmaz ve kayar.

- **İzleyici HER cümle sonunda neye baktığını anlamalı.** Merak "sırada ne var?"
  olmalı; "şu an ne izliyorum?" ASLA. İkincisi kafa karışıklığıdır, merak değil.
- **Gizem kelimesi / belirsiz zamir yasak.** "İşini bitiriyor", "oradan giriyor",
  "o şeyi yapıyor" gibi somut olmayan fiiller izleyiciyi düşürür. Somut fiil kullan:
  ne yaptığını AÇIKÇA söyle.
- **Hook body ile eşleşmeli.** Kanca neyi vaat ettiyse gövde onu vermeli;
  uyumsuzluk 3 saniye eşiğini geçse bile tamamlanma oranını ve güveni öldürür.
- **Payoff videonun EN NET cümlesidir.** Asıl bilgiyi burada dolaysız söyle —
  "narrative completion". Tatminsiz biten video paylaşılmaz.

### Somut örnek: guguk videosu (netlik hatası, gelecek için ders)
Yayınlandı, değiştirmiyoruz — ama tipik hatayı gösteriyor:
- Kanca "Bu kuş o boşlukta **işini bitiriyor**" → "işini bitirmek" belirsiz, izleyici
  ne olduğunu anlamıyor. Daha iyisi: somut eylemi ima et ("o boşlukta yumurtasını
  bırakıyor" kadar açık olmasa da yönü belli).
- Kapanış "Guguk tam **oradan giriyor**" → payoff bulanık. İzleyici "nereden, neye?"
  diye kalıyor. Payoff net olmalıydı: guguk'un içgüdüyü nasıl sömürdüğünü açıkça söyle.

## Referansın satır satır analizi

- **Kanca:** "Kel kalmak istemiyorsanız bu kuşlardan uzak durun."
  → 2. tekil/çoğul hitap + saçma ama merak açan tehdit. "Kuşlar tüy çalıyor" DEMİYOR
  ama izleyici "hangi kuş, neden kel?" diye NET bir soru soruyor (belirsiz değil).
- **İç ses:** "yumuşacık tüyler varken neden çalı çırpı toplayalım diyor"
  → Kuşa replik veriyor. Bilgi + mizah aynı cümlede.
- **Tersine dönüş/payoff:** "Ama normalde aynı kuşlar ... parazitlerden temizlediği
  için masum hayvanlar yaklaşmalarına izin veriyor ve tüylerinden oluyor."
  → Güven ilişkisinin istismarı NET anlatılıyor. "Tüylerinden oluyor" kelime oyunu.
- **Kapanış:** "Böylece kuşlar da yuvalarını hızlıca bitirip dinlenebiliyor."
  → Kısa, nötr, ahlak dersi yok.

## Yazım kuralları

- **Şimdiki zaman** (`-yor`), konuşma dili. Yazılı/ansiklopedik cümle yok.
- Cümleler kısa; bir cümlede bir fikir.
- **İkinci tekil hitap** en az bir kere ("istemiyorsan", "sanma ki", "dur").
- Rakam ve zıtlık kancayı güçlendirir ("üç kalbi var", "biri duruyor"). Somut sayı
  inandırıcılık katar — ama bir videoda **en fazla 2 sayısal bilgi**.
- **Konuyu asla başta özetleme** ama **her cümleyi anlaşılır tut** (bkz. netlik kuralı).
- **Kapanış çağrısı zorunlu:** her senaryo `preset.json > kapanis_cagri` ile bitiyor
  ("Sıradaki hangi hayvan olsun? Yorumlara yaz."). Elle yazma — `senaryo.py` ve
  `uret.py` ikisi de preset'ten ekliyor, metinler birebir aynı kalsın diye.
  2026-08-19'da abone çağrısı yerine SORU kondu: ilk iki videoda sıfır yorum geldi,
  izleyiciye yazacak somut bir şey verilmiyordu (Enes kararı).
- Uzunluk: **hedef bant 26-30 sn → ~335-390 karakter** (CTA dahil).
  Formül: hedef karakter = kurgu saniyesi × `preset.json > karakter_hiz` (**12.9**,
  2026-08-23'te 1.05x yavaş VO profiline göre kalibre edildi — eski 16.7/435-500
  değerleriyle yazılan senaryo artık UZUN çıkar, bu sayıları kullan).
  **Bant geçmişi:** 25-33 → 20-24 (2026-08-19, YouTube analizi: ortalama izlenme
  14-17 sn'de kalıyordu, Shorts'ta en güçlü sinyal tamamlanma oranı) → **26-30**
  (2026-08-21, Enes: "video uzasın sıkıntı yok"). Tamamlanma oranını sonraki YouTube
  analizinde ayrıca kontrol et.

## Tutundurma kuralları (odak süresi yok)

Enes'in duruşu (2026-08-16): *"millet odak süresi yok, çok kalamıyorlar — kaliteli
bile olsa."* Kalite tek başına izletmiyor; ritim izletiyor. Somut karşılığı:

- **Sessiz açılış yok.** VO videonun 0. saniyesinde başlar. İlk kelime kancanın kendisi
  olmalı; "bakın şimdi", "biliyor muydunuz" gibi ısınma cümlesi yasak. Uzman verisi:
  ilk 2-2.5 sn'de gelen kanca %19 daha fazla izleyici tutuyor.
- **Açılış karesi aydınlık olacak.** İlk klip yüksek kontrast olmalı ve özne ilk karede
  tanınmalı; karanlık/siyah açılış yasak (klip seçiminde süzgeç). 2026-08-19 kararı:
  aydınlık mercan açılışlı ahtapot videosu %57,5 izlemeye devam verdi, siyah zeminli
  denizanası açılışı %43,6'da kaldı — akışta siyah kare "yüklenmemiş video" gibi
  görünüp parmağı hızlandırıyor olabilir. İki videoluk veri, kesin değil ama ucuz önlem.
- **Ölü kuyruk yok.** `uret.py` VO'yu ffmpeg atempo ile kurgu süresine otomatik oturtuyor
  (`preset > vo_uydur`), video bitiminden 0.3 sn önce susuyor. Metni saniyesine kadar
  ayarlamaya çalışma — `stability 0.30` yüzünden aynı metin her üretimde 18-21
  karakter/sn arasında okunuyor. Uzunluk yine de ±%20 içinde tutulmalı; ötesinde
  atempo sesi bozar ve script uyarı verip dokunmaz.
- **Her cümle yeni bilgi taşır.** Tekrar, özet, "yani şöyle ki" bağlacı yok. Bir cümle
  kesildiğinde anlam bozulmuyorsa o cümle fazladır.
- **HIZLI KESME: görsel 2-3 saniyeden uzun sabit kalmasın** (2026-08-23 Enes kararı:
  *"izleyici 2-3 saniyeden sonra sıkılıyor"*; eski kural 4 sn'ydi). Pratik karşılığı:
  **havuz bilerek bol tutulur** — sahne başına 1 değil **2-3 klip** seçilir, böylece
  CapCut auto clipping aynı görüntüye dönmek zorunda kalmaz. Kaba ölçü: video saniyesi
  ÷ 3 ≈ havuzdaki klip sayısı (45 sn → ~15-18 klip). Klip seçerken tek "kahraman"
  görüntü yerine aynı konunun farklı açılarını topla.
- **Merak zinciri kapanmasın (rehook'a kadar).** Her cümle bir sonrakini borçlandırmalı;
  cevabı verdiğin anda yeni soru aç. Merak zinciri payoff'ta (parça 5) kapanır —
  orada NET kapat, açık bırakma.

## Kancada işe yarayan kalıplar

Kanal tonuna (hayvan + iç ses + ironi) uyarlanmış. Uzman "copy-paste" kalıplarından
türetilmiş; hepsi **somut merak** açar, belirsizlik değil:

- **Tehdit/uzak dur:** "X olmak istemiyorsan Y'den uzak dur."
- **Yalanı boz:** "Y hakkında sana yıllardır yalan söylendi."
- **Şu an sen:** "Şu an Y yapıyorsun ve X seni izliyor."
- **Kıyas-şok:** "Bir X'in olsaydı ölürdün. Bu hayvanın üç tane var."
- **Zıt gerçek:** "Herkes X sanıyor. Gerçek çok daha kötü."
- **Gerçek zamanlı:** "İzle, bu hayvan on saniyede ne yapıyor."
- **Paradoks:** "Ne kadar az X yaparsa, o kadar çok Y kazanıyor."

Kalıbı seçtikten sonra **parça 2'de mutlaka netleştir** — kanca ne kadar cesur olursa
netleştirme o kadar önemli, yoksa merak kafa karışıklığına döner.
