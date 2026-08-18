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
  ("Daha fazla belgesel için beğen ve abone ol."). Elle yazma — `senaryo.py` ve
  `uret.py` ikisi de preset'ten ekliyor, metinler birebir aynı kalsın diye.
- Uzunluk: hedef karakter = **kurgu saniyesi × `preset.json > karakter_hiz`**
  (2026-08-16 itibarıyla 16.5; VO hızlandırıldı, eskiden ~14.4'tü).
  25 sn'lik kurgu ≈ 410 karakter, CTA dahil.

## Tutundurma kuralları (odak süresi yok)

Enes'in duruşu (2026-08-16): *"millet odak süresi yok, çok kalamıyorlar — kaliteli
bile olsa."* Kalite tek başına izletmiyor; ritim izletiyor. Somut karşılığı:

- **Sessiz açılış yok.** VO videonun 0. saniyesinde başlar. İlk kelime kancanın kendisi
  olmalı; "bakın şimdi", "biliyor muydunuz" gibi ısınma cümlesi yasak.
- **Ölü kuyruk yok.** VO bitince video da bitsin — sonda 1 sn'den uzun sessiz kare kalmasın.
  (`uret.py` VO/video oranını yazdırıyor; 0.95-1.00 bandı hedef.)
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
