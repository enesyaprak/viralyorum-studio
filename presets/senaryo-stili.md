# Anlatım shorts senaryo stili

Kaynak: "Tüy Hırsızı Kuşlar" (Tüyler Diken Diken) — 25 sn, ~500 karakter.
Referans transkript: `output/referans_tuy-hirsizi_tr.json`.
Enes'in hedeflediği ton bu (2026-08-16).

## Formül

| # | Parça | Süre | Kural |
|---|---|---|---|
| 1 | **Kanca** | 0-3 sn | İzleyiciye **doğrudan hitap** + absürt tehdit/vaat. Konu ANONS EDİLMEZ. |
| 2 | **Kurulum** | 3-10 sn | Olayı kur, ama sebebi henüz verme. |
| 3 | **İç ses** | 10-15 sn | Hayvana/nesneye **replik ver** — mizah buradan gelir. |
| 4 | **Tersine dönüş** | 15-22 sn | "Ama..." ile ironiyi patlat. Beklenti kırılır. |
| 5 | **Kapanış** | 22-25 sn | Tek cümlelik toparlama. Ders verme, sadece bırak. |

## Referansın satır satır analizi

- **Kanca:** "Kel kalmak istemiyorsanız bu kuşlardan uzak durun."
  → 2. tekil/çoğul hitap + saçma ama merak açan tehdit. "Kuşlar tüy çalıyor" DEMİYOR.
- **İç ses:** "yumuşacık tüyler varken neden çalı çırpı toplayalım diyor"
  → Kuşa replik veriyor. Bilgi + mizah aynı cümlede.
- **Tersine dönüş:** "Ama normalde aynı kuşlar ... parazitlerden temizlediği için masum
  hayvanlar yaklaşmalarına izin veriyor ve tüylerinden oluyor."
  → Güven ilişkisinin istismarı. "Tüylerinden oluyor" kelime oyunu.
- **Kapanış:** "Böylece kuşlar da yuvalarını hızlıca bitirip dinlenebiliyor."
  → Kısa, nötr, ahlak dersi yok.

## Yazım kuralları

- **Şimdiki zaman** (`-yor`), konuşma dili. Yazılı/ansiklopedik cümle yok.
- Cümleler kısa; bir cümlede bir fikir.
- **İkinci tekil hitap** en az bir kere ("istemiyorsan", "sanma ki", "dur").
- Rakam ve zıtlık kancayı güçlendirir ("üç kalbi var", "biri duruyor").
- Sayı/terim yığmayın — bir videoda en fazla 2 sayısal bilgi.
- **Konuyu asla başta özetleme.** Merak boşluğu kapanırsa video biter.
- **Kapanış çağrısı zorunlu:** her senaryo `preset.json > kapanis_cagri` ile bitiyor
  ("Sıradaki hangi hayvan olsun? Yorumlara yaz."). Elle yazma — `senaryo.py` ve
  `uret.py` ikisi de preset'ten ekliyor, metinler birebir aynı kalsın diye.
  2026-08-19'da abone çağrısı yerine SORU kondu: ilk iki videoda sıfır yorum geldi,
  izleyiciye yazacak somut bir şey verilmiyordu (Enes kararı).
- Uzunluk: **hedef bant 26-30 sn → ~435-500 karakter** (CTA dahil).
  Formül: hedef karakter = kurgu saniyesi × `preset.json > karakter_hiz` (16.7).
  **Bant geçmişi:** 25-33 → 20-24 (2026-08-19, YouTube analizi: ortalama izlenme
  14-17 sn'de kalıyordu, Shorts'ta en güçlü sinyal tamamlanma oranı) → **26-30**
  (2026-08-21, Enes: "video uzasın sıkıntı yok"). Son değişiklik 2026-08-19'daki
  veriye dayalı kısaltmayı geri alıyor; tamamlanma oranını sonraki YouTube
  analizinde ayrıca kontrol et.

## Tutundurma kuralları (odak süresi yok)

Enes'in duruşu (2026-08-16): *"millet odak süresi yok, çok kalamıyorlar — kaliteli
bile olsa."* Kalite tek başına izletmiyor; ritim izletiyor. Somut karşılığı:

- **Sessiz açılış yok.** VO videonun 0. saniyesinde başlar. İlk kelime kancanın kendisi
  olmalı; "bakın şimdi", "biliyor muydunuz" gibi ısınma cümlesi yasak.
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
- **Görsel 4 saniyeden uzun sabit kalmasın.** Kesme ya da geçiş gelsin; havuzdaki
  klipler bunun için sahne süresinden uzun seçiliyor.
- **Merak zinciri kapanmasın.** Her cümle bir sonrakini borçlandırmalı; cevabı verdiğin
  anda yeni soru aç. Kapanış cümlesi hariç.

## Kancada işe yarayan kalıplar

- "X olmak istemiyorsan Y'den uzak dur."
- "Bunu bilseydin bir daha Y yapmazdın."
- "Şu an Y yapıyorsun ve X bunu izliyor."
- "Bir X'in olsaydı ölürdün. Bu hayvanın üç tane var."
