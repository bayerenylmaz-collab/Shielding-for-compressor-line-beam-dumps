# Doz grafikleri ve değerlendirme tanımı
Güncelleme: 2026-10-08. Kullanıcının onayladığı grafik istekleri.

## Güncel kapsam
- 20 MeV kolime elektron; referans ortalama akım 1 µA.
- Bakır dump, demir taşıyıcılar, 10 × 10 × 5 cm kurşun bloklar.
- Otomatik optimizasyon veya parametre taraması YAPILMAYACAK. Zırh, koşuların ardından elle adım adım değiştirilecek.
- Değerlendirme dump konisinin sivri ucundan 400 mm itibarıyla başlar.
- Kullanıcının dump'a bakışına göre sol-ileri yaklaşık 45° bölge: en fazla 10 mSv/h.
- Aynı bakışta sağ-ileri, ayna simetriğindeki bölge: en fazla 100 mSv/h.
- Elektronikler masa tablasının biraz üzerinde. Mevcut karşılaştırma kesiti Y=124–126 cm; bunu tüm elektronik hacminin doğrulanması olarak sunma.
- Modelde sivri uç (X,Y,Z)=(0,140,0) cm; demet +Z. Son sayısal değerlendirme +Z tarafındaki X=±Z doğrultularında yapıldı. Kullanıcının sol/sağ tarifini ±X işaretleriyle kesin eşleştiren etiketli bir üstten görünüş henüz onaylanmadı: eşleştirmeyi varsayma; sonuçlarda koordinatları açıkça göster.

## İstenen çıktı 1: Doz dağılımı
FLUKA/Flair görsellerinin yanında Python/Matplotlib ile:
- 1 µA için mSv/h cinsinden masa üstüne yakın X–Z kesiti.
- Sivri uçtan gerçek üç boyutlu 400, 500, 600, 700 mm uzaklık konturları.
- 400 mm'den itibaren iki ilgili çapraz yöndeki doz–uzaklık profilleri.
- 10 ve 100 mSv/h referans çizgileri; istatistiksel hata çubukları veya bantları.
- Zırhsız, v1, v2 karşılaştırmalarında aynı kesit, koordinatlar, birimler ve renk ölçeği.
- Tam derinlik projeksiyon ortalamasını yerel doz olarak kullanma.
- Kesit içindeki 400 mm dairenin yatay yarıçapı sqrt(40^2-(Y-140)^2) cm'dir; yatay mesafe ile üç boyutlu uzaklığı karıştırma.

## İstenen çıktı 2: Doz–akım
- Akım ekseni 1–100 µA; doz ekseni mSv/h.
- 400, 500, 600, 700 mm için ayrı eğriler; iki hedef yönü ayrı panellerde göster.
- Sabit geometri ve kaynak dağılımında D(I)=D(1 µA) × I/(1 µA).
- Bu akım taraması yeni transport koşuları değil, mevcut sonucun doğrusal normalizasyonudur.
- Mutlak istatistiksel hata da aynı katsayıyla ölçeklenir; bağıl hata değişmez.
- Yeterli istatistik olmadan maksimum izin verilen akımı kesin sonuç diye sunma.
- Akım ölçeklemesi dump'ın termal kapasitesini veya gerçek işletme uygunluğunu doğrulamaz.

## Veri ve normalizasyon
- Birleştirilmiş _21.bnn: DOSE-EQ; _22.bnn: foton akısı; _23.bnn: nötron akısı.
- Başlık, skor türü, birincil sayısı ve çevrim sayısını dosya içinden kontrol et.
- 1 µA = 6.241509074e12 elektron/s.
- DOSE-EQ pSv/primary → 1 µA'da mSv/h: 2.2469432668e7 ile çarp.
- Foton/nötron akı skoruna doz dönüşüm çarpanını uygulama.
- Flair Data.Usrbin.readArray(0), Fortran sıralaması (nx,ny,nz).
- BNN ham istatistik dizisi bağıl kesirdir; yüzde için 100 ile çarp. DAT hata sütunu zaten yüzde olabilir.
- Düşük istatistikte sıfır nötron skoru, sıfır fiziksel katkı kanıtı değildir.
- Mevcut ağ 2 cm: hedef koordinatın hücre sınırlarını, merkezini ve gerçek uzaklığını bildir. Tam 400 mm nokta değeri gibi sunma.
- Hücreleri birleştirirken kovaryans bilinmeden bağımsızlık varsayımıyla hata küçültme.
- Kullanıcı v2 bittikten sonra istatistiği artırmayı veya uygun varyans azaltma kartlarını değerlendirmeyi istiyor; henüz bu kartlar değiştirilmedi.

## Mevcut denemeler
- v1: 16 blok, 5 cm duvar kalınlığı, 20 cm yükseklik; +Z tarafı ve iki yanda U; üst ve giriş açık.
- v2: 36 blok, 10 cm duvar kalınlığı, 20 cm yükseklik; aynı U düzeni.
- 2026-10-08 itibarıyla v2 kullanıcıda koşuyor; yeni zırh değişikliği için sonucu bekle.
- v1 sonuçları 5 milyon birincil / 5 çevrim. Y=125 cm, X=±27 cm, Z=27 cm hücre merkezlerinde (~410 mm): -X 620.68 mSv/h (%46.58), +X 118.42 mSv/h (%9.56), 1 µA için. Bunlar bölge maksimumu veya kesin uygunluk sonucu değildir.

## Teslim
Grafikleri PNG ve tercihen PDF; sayısal değerleri CSV olarak sun. Her çıktıda koşu adı, akım, kesit, mesafe tanımı ve belirsizlik yer alsın.
Bu belge istek kaydıdır; grafik üretim otomasyonu henüz eklenmiş değildir.
