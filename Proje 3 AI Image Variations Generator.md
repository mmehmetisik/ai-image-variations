# Proje 2: AI Image Variations Generator

## Proje Özeti
Bu proje, mevcut bir görselden yeni ve farklı varyasyonlar üreten bir AI destekli görsel dönüştürme aracıdır. Hugging Face API kullanarak Stable Diffusion'ın image-to-image yeteneklerinden faydalanır. Bu proje AI Image Studio serisinin ikinci parçasıdır.

## Projenin Amacı
Kullanıcılar ellerindeki görselleri farklı yorumlamalara dönüştürebilecekler. Bir fotoğrafı farklı sanat stillerine çevirebilecek, aynı kompozisyonun farklı varyasyonlarını üretebilecek veya bir taslak çizimden gerçekçi görsel elde edebilecekler. Bu proje image-to-image teknolojisini ve görsel yükleme işlemlerini öğretir.

## Kullanılacak Teknolojiler

### Ana Teknolojiler
- **Python 3.9+**: Programlama dili
- **Streamlit**: Web arayüzü framework'ü
- **Hugging Face Inference API**: Görsel dönüştürme motoru (img2img)
- **Pillow (PIL)**: Görsel işleme ve preprocessing
- **requests**: HTTP istekleri için
- **python-dotenv**: Çevre değişkenleri yönetimi
- **NumPy**: Görsel array işlemleri (opsiyonel)
- **Git**: Versiyon kontrol sistemi

### Kullanılacak AI Modelleri
- **Stable Diffusion 2.1 img2img**: Ana görsel dönüştürme modeli
- **Stable Diffusion XL img2img**: Yüksek kaliteli dönüşüm (opsiyonel)

### Öğrenilecek Kavramlar
- Image-to-image pipeline ve teknolojisi
- Strength parametresi (orijinale ne kadar sadık kalınsın)
- Görsel yükleme ve file handling
- Image preprocessing ve normalization
- RGB/RGBA format dönüşümleri
- Prompt blending (görsel + metin)
- Multi-image comparison UI

## Temel Özellikler

### 1. Görsel Yükleme Sistemi
- PNG, JPG, JPEG formatlarını destekler
- Maksimum dosya boyutu kontrolü (örn: 5MB)
- Otomatik görsel önizleme
- Yüklenen görselin boyut ve format kontrolü
- RGB formatına otomatik dönüşüm

### 2. Transformation Strength (Dönüşüm Gücü)
- **0.3-0.5**: Orijinale çok benzer, minimal değişiklik
- **0.5-0.7**: Dengeli dönüşüm (önerilen)
- **0.7-0.9**: Yaratıcı ve farklı sonuçlar
- Slider ile kullanıcı kontrolü

### 3. Prompt Girişi (Opsiyonel)
Kullanıcı görseli yönlendirmek için prompt ekleyebilir:
- Boş bırakılırsa: Sadece varyasyon üretir
- Prompt girilirse: Görsel o yönde dönüştürülür
- Örnek: "oil painting style" → Yağlıboya stili
- Örnek: "winter scene" → Yaz manzarasını kışa çevirir

### 4. Stil Dönüşümleri
Hazır stil şablonları:
- **Artistic Styles**: Oil painting, watercolor, sketch, digital art
- **Photo Styles**: Vintage, black and white, HDR, film grain
- **Fantasy Styles**: Anime, cartoon, comic book
- Her stil için optimize edilmiş prompt + strength kombinasyonu

### 5. Çoklu Varyasyon Üretimi
- Aynı görselden 2-4 farklı varyasyon
- Her varyasyon farklı seed ile üretilir
- Yan yana karşılaştırma görünümü
- En beğenileni seçme özelliği

### 6. Görsel Karşılaştırma
- Orijinal vs Üretilen görünümü
- Slider ile önce/sonra karşılaştırması
- Zoom ve detay inceleme
- Metadata bilgisi (hangi parametreler kullanıldı)

### 7. Toplu İşlem
- Birden fazla görseli sıraya koyma
- Aynı stil/parametreleri toplu uygulama
- Batch processing için progress bar
- Tamamlanan görselleri galeri olarak görüntüleme

## Proje Dosya Yapısı

```
ai-image-variations/
│
├── .env                    # API anahtarları (GIT'E EKLENMEYEN)
├── .gitignore             # Git ignore dosyası
├── requirements.txt       # Python bağımlılıkları
├── README.md             # Proje dokümantasyonu
│
├── app.py                # Ana Streamlit uygulaması
│
├── config/
│   ├── settings.py       # Yapılandırma ayarları
│   └── style_presets.py  # Stil şablonları ve strength değerleri
│
├── utils/
│   ├── hf_api_handler.py # Hugging Face img2img API çağrıları
│   ├── image_loader.py   # Görsel yükleme ve preprocessing
│   ├── image_processor.py # Görsel işleme fonksiyonları
│   └── comparison_ui.py  # Karşılaştırma arayüzü
│
├── input_images/         # Yüklenen görseller (GIT'E EKLENMEYEN)
├── output_images/        # Üretilen görseller (GIT'E EKLENMEYEN)
│
└── assets/
    ├── style.css         # Özel CSS stilleri
    └── sample_images/    # Örnek görseller ve demo için
```

## Geliştirme Adımları

### Faz 1: Görsel Yükleme Sistemi (2 gün)
- Streamlit file uploader entegrasyonu
- Dosya formatı ve boyut kontrolü
- Görsel önizleme sistemi
- RGB format dönüşümü
- Error handling (corrupt files, wrong format)

### Faz 2: Temel img2img İşlemi (2-3 gün)
- Hugging Face img2img API entegrasyonu
- Strength parametresi kontrolü
- Base64 encoding/decoding
- İlk başarılı dönüşümü gerçekleştirme
- Rate limit ve timeout yönetimi

### Faz 3: Prompt ve Stil Sistemi (2 gün)
- Opsiyonel prompt girişi
- Stil şablonları oluşturma
- Prompt + strength kombinasyonları
- Stil önizleme örnekleri
- Negatif prompt desteği

### Faz 4: Çoklu Varyasyon (2 gün)
- Farklı seed'lerle çoklu üretim
- Paralel işlem yönetimi
- Progress tracking
- Karşılaştırma grid görünümü
- Seçim ve favorileme

### Faz 5: Karşılaştırma UI (1-2 gün)
- Önce/sonra görünümü
- Slider karşılaştırma widget'ı
- Zoom ve pan fonksiyonları
- Metadata gösterimi
- İndirme seçenekleri

### Faz 6: Toplu İşlem (1-2 gün)
- Batch upload sistemi
- Queue yönetimi
- Toplu parametre uygulama
- Batch progress bar
- Toplu indirme (ZIP)

### Faz 7: Dokümantasyon (1 gün)
- README.md yazma
- Örnek kullanım senaryoları
- Before/after görselleri ekleme
- GitHub'a push etme

## Öğrenme Çıktıları

Bu projeyi tamamladığında şunları öğrenmiş olacaksın:
- Image-to-image pipeline'ları ve nasıl çalıştıkları
- Strength parametresinin etkisi ve optimizasyonu
- Streamlit file upload ve görsel işleme
- PIL/Pillow ile ileri seviye görsel manipülasyonu
- Base64 encoding ile görsel aktarımı
- Batch processing ve queue yönetimi
- Before/after karşılaştırma UI tasarımı
- Multiple model endpoint kullanımı

## API Kullanım ve Maliyet

Hugging Face img2img API kullanımı:
- **Ücretsiz tier**: Günlük sınırlı kullanım
- **Pro tier**: Aylık $9, daha yüksek limit
- Her dönüşüm yaklaşık 5-15 saniye sürüyor
- Strength değeri düşük olursa daha hızlı

**Test aşamasında dikkat edilecekler**:
- Orta strength değerleriyle başla (0.5-0.7)
- Küçük boyutlu görseller kullan (512x512)
- Toplu işlemde dikkatli ol (rate limit)

## Başarı Kriterleri

Proje başarılı sayılabilir çünkü:
- Görsel yükleme sorunsuz çalışıyor
- img2img dönüşümleri beklendiği gibi
- Farklı strength değerleri doğru sonuç veriyor
- Karşılaştırma UI kullanıcı dostu
- Çoklu varyasyonlar başarıyla üretiliyor
- Hata durumları iyi yönetiliyor
- Kod temiz ve modüler
- GitHub repo profesyonel görünüyor

## Proje 1'den Farklar ve Gelişmeler

Bu proje ilk projeden şu yönlerle farklılaşıyor:
- Kullanıcıdan görsel input alıyor (file handling)
- Image preprocessing gerektiriyor
- Strength parametresi yeni bir konsept
- Önce/sonra karşılaştırması sunuyor
- Input ve output görselleri aynı anda yönetiyor

## LinkedIn İçin Sunum Noktaları

Bu projeyi LinkedIn'de paylaşırken vurgulayabileceğin noktalar:
- "Image-to-image AI ile görsel dönüştürme aracı geliştirdim"
- "Stable Diffusion img2img pipeline'ını kullanarak varyasyon üretimi"
- "Kullanıcı dosya yükleme ve görsel preprocessing özellikleri ekledim"
- "Before/after karşılaştırma UI'ı ile kullanıcı deneyimini zenginleştirdim"
- "Batch processing ile birden fazla görseli aynı anda işleyebildim"
- "Strength parametresi optimizasyonu ile farklı dönüşüm seviyeleri sundum"

## Potansiyel İyileştirmeler (V2 için)

İlerleyen zamanlarda eklenebilecek özellikler:
- Birden fazla modeli karşılaştırma (SD 2.1 vs SDXL)
- Gelişmiş preprocessing (auto-enhance, denoise)
- Style transfer modelleri entegrasyonu
- Video frame-by-frame dönüşümü
- Görsel geçmişi ve versiyonlama
- A/B testing farklı parametrelerle
- Social sharing özellikleri