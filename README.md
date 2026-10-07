# Compressor-line beam dump — sadeleştirilmiş FLUKA geometrisi

Bu sürüm, `kaba_cizim.zip` içindeki STL'den çıkarılan ölçülerle hazırlanmış **zırhsız başlangıç geometrisidir**. FLUKA taşıma hesabı yapılmadı; doz, optimum kurşun kalınlığı veya izin verilebilir akım sonucu içermez.

## Açılış

1. `model/beam_dump_baseline.flair` dosyasını Flair'de açın.
2. Alternatif olarak `model/beam_dump_baseline.inp` dosyasını açın ve projeyi kaydedin.
3. Geometry bölümünde dump merkezine `(X,Y,Z)=(0,140,0)` cm konumunda bakın. Y düşey, Z demet yönüdür. Kaynak `(0,140,-1)` cm'dedir.
4. Tüm düzeneğin görünümü için yaklaşık `X=-45…45`, `Y=0…155`, `Z=-110…35` cm aralığını kullanın. Dış black-hole küresini seçip bütün görüntüyü buna sığdırmayın.
5. Z–Y yan kesit ve Z–X yatay kesit için `docs/geometry_sections.png`, dump ayrıntısı için `docs/dump_section.png` karşılaştırma görselleridir. Kesit, düzlemin dışında kalan ayakları göstermeyebilir.

Flair'de geometri hata kontrolü ve kısa bir FLUKA deneme koşusu, üretim hesabından önce yapılmalıdır. Buradaki kontrol, Flair'in giriş okuyucusu ve bağımsız hacim örneklemesidir; grafik arayüz veya FLUKA executable çalıştırması değildir.

## Modelde olanlar

| Parça / ayar | Tanım |
|---|---|
| Dump | Oksijensiz bakır için başlangıç yaklaşımı: FLUKA `COPPER` |
| Ana bakır gövde | Çap 110 mm, uzunluk 130 mm; dış kanatçıklar kaldırıldı |
| Konik oyuk | Ağız çapı 60 mm, düz dip çapı 5 mm, derinlik 40 mm |
| Dip arkasındaki bakır | Eksen üzerinde 90 mm |
| Bakır giriş dudağı | 4 mm uzunluk; iç/dış çap 70/82 mm |
| Masa, taşıyıcılar, hat | Kullanıcının istediği başlangıç yaklaşımı: `IRON` |
| Profiller | STL sınırları korunmuş, köşeleri düzleştirilmiş içi boş profiller |
| Boru | Kademeli eşeksenli silindirler, flanşlar, vakum içi ve T bağlantısı |
| Kaynak | 20 MeV monoenerjetik elektron, +Z; dipten 10 mm önce vakumda |
| Demet çapı | Bilinmediği için ilk sürümde ideal noktasal/paralel demet |
| Kurşun | Başlangıçta yok; JSON'daki `lead_panels` boş |
| Çevre | Hava; gerçek bina zemini, duvarlar ve elektronik malzemeleri modellenmedi |

Ana masa tablasının üstü Y=123.1 cm; demet yüksekliği Y=140 cm'dir. İkisinin arasındaki 16.9 cm fark korunmuştur. Skorlama hacmi her iki yüksekliği de kapsar.

## Sadeleştirmeler ve sınırlar

- Vida dişleri, cıvatalar, küçük delikler, pahlar, kanatçıklar, körük olukları, bazı küçük destek ve ayak parçaları çıkarıldı veya düzgün hacimlerle temsil edildi.
- Kanatçık boşlukları bakırla doldurulmadı: 130 mm kanatçık dış çapı yerine 110 mm çekirdek çapı kullanıldı. Bunun doz üzerindeki etkisinin her yönde emniyetli olduğu varsayılmamalı; son zırh çalışmasında geometri duyarlılığı kontrol edilmeli.
- Kare profillerin et kalınlığı 5 mm alındı; yuvarlatılmış iç/dış köşeler düzleştirildi. Boru geçişleri ve flanşlar STL'deki radyal/eksenel seviyelerden sadeleştirildi; valf iç ayrıntıları ve küçük fittingler tam CAD kopyası değildir.
- Kaynak ve koni geometrisi STL'den ölçüldü; elektroniklerin kesin azimut bölgesi bu dosyada etiketlenmedi. 600 mm uzaklık, doz haritasında ilgili tarafın seçilmesi için referanstır; bütün halka için bir kabul şartı konmadı.
- Kaynak yalnızca dump'a ulaşmış elektronları temsil eder. Üst akıştaki gerçek demet kayıpları bu modelde üretilmez.
- `IRON`, paslanmaz çelik veya gerçek yapı alaşımının tam karşılığı değildir; bölge malzemeleri ayrı değiştirilebilir.

## Düzenleme

Flair'de `DUMP` ve `CULIP` bakır; `PIPE..`, `PORT..`, `STR..`, `SUP..`, `ADJ..`, `FOOT..`, `BASE..` demir bölgeleridir. Sonunda `V0`/`V1` bulunan bölgeler ilgili parçanın vakum veya hava iç hacmidir. Malzeme atamaları `ASSIGNMA` kartlarındadır.

Geometriyi yeniden üretmek için yalnız Python standart kütüphanesi yeterli:

```bash
python tools/build_geometry.py
```

Bu komut `.inp` ve `.geometry.json` dosyalarını günceller. Teslim edilen `.flair` dosyası bu ilk sürümün kopyasıdır; yeniden üretimden sonra yeni `.inp` dosyasını Flair'de açıp kaydedin veya aşağıdaki dönüştürücüyü kullanın.

```bash
python tools/export_flair.py --flair-root /path/to/flair
python tools/check_geometry.py
python tools/preview_geometry.py
```

Son iki komut için `numpy` ve önizleme için ayrıca `matplotlib` gerekir. STL yeniden ayrıştırılmaz; ölçüler `model/geometry_mm.json` içinde tutulur.

İleride kurşun panel eklemek için `lead_panels` içine dönüştürülmüş fiziksel koordinatlarla, **mm biriminde** `min_mm`, `max_mm`, `note` alanlarını içeren kutular eklenebilir. Mevcut parçalar panelden çıkarılır; fiziksel olarak uygun montaj, boşluk ve taşıma yükü ayrıca kontrol edilmelidir. Bu mekanizma zırh optimizasyonu yapmaz.

## İlk koşu ve skorlama

`START=10000` yalnızca kısa başlangıç kontrolü içindir. Dosyada `PRECISIO`, kullanılan malzemeler için `PHOTONUC/ELECTNUC` ve 2 cm hücreli üç boyutlu `DOSE-EQ`, `PHOTON`, `NEUTRON` USRBIN ağları bulunur. Bunlar doz sonuçları değildir. Nötron katkısını atlayarak yalnız foton hesabıyla kurşun kalınlığı seçilmemelidir.

`DOSE-EQ` sonucu pSv/primary'dir. 1 µA ortalama elektron akımı için:

```text
Elektron/s = 1e-6 / 1.602176634e-19 = 6.241509074e12
mSv/h = USRBIN[pSv/primary] × 2.2469432668e7
Imax[µA] = 10 / D_at_1uA[mSv/h]
```

Son formül ancak seçilen elektronik bölgesindeki en yüksek doz hızı ve belirsizliği güvenilir biçimde elde edildikten sonra, sabit geometri ve demet koşulları için kullanılabilir. Sıfır skor “sonsuz izin verilebilir akım” anlamına gelmez. 1 µA demet gücü 20 W'tır; soğutma/ısıl akım sınırı bu geometri çalışmasının dışındadır.

Kullanıcının 10 mSv/h hedefi korunmuştur. **Sv insan radyasyon korunması büyüklüğüdür; tek başına elektronik dayanımını göstermez.** Elektroniklerin gerçek hasar değerlendirmesi için uygun malzemede soğurulan doz (örn. Gy(Si)) ve ilgili parçacık fluensleri ayrıca ele alınmalıdır.

Artık aktivasyon, ışınlama/soğuma süreleri ve sonraki aşamanın fizik ayarları belirlenmediği için bu sürümde yoktur. Nihai zırh hesabında oda saçılması, istatistik, kesme enerjileri, ağ yakınsaması, malzeme doğrulaması ve gerçek elektronik bölgesi değerlendirilmelidir.

## Doğrulama kayıtları

- `docs/geometry_check.json`: dışa yazılmış INP üzerinde 332480 noktalık bağımsız geometri örneklemesi; kaynak/eksen kontrolleri.
- `docs/flair_parser_check.json`: CERN Flair 3.4-5.4 okuyucusuyla kart kontrolü.
- `docs/cad_measurements.json`: kaynak STL kimliği, koordinat dönüşümü ve temel ölçüler.

Bu kontroller FLUKA taşıma koşusu veya doz doğrulaması yerine geçmez.

## Kullanılan resmi dokümantasyon

- [FLUKA BEAM](https://flukafiles.web.cern.ch/manual/chapters/description_input/description_options/beam.html)
- [FLUKA BEAMPOS](https://flukafiles.web.cern.ch/manual/chapters/description_input/description_options/beampos.html)
- [FLUKA USRBIN](https://flukafiles.web.cern.ch/manual/chapters/description_input/description_options/usrbin.html)
- [FLUKA PHOTONUC](https://flukafiles.web.cern.ch/manual/chapters/description_input/description_options/photonuc.html)
- [CERN Flair](https://flair.cern/download.html)
