---
description: 
---

# İş Akışları

## 1. Proje İlk Kurulum Akışı
Bu iş akışını projeyi sıfırdan başlatırken çağır.
Adım 1: Sanal ortam oluştur (`python -m venv venv`) ve aktive et.
Adım 2: `requirements.txt` dosyası oluştur ve içine şu paketleri yaz: flask, firebase-admin, bcrypt, python-dotenv.
Adım 3: `pip install -r requirements.txt` komutunu çalıştır.
Adım 4: `app.py`, `firebase_config.py`, `.env.example`, `.gitignore` dosyalarını oluştur.
Adım 5: `templates/`, `static/css/`, `static/js/` klasörlerini oluştur.
Adım 6: README.md taslağını oluştur ve kurulum adımlarını yaz.
Adım 7: `git init` yap ve ilk commit'i öner.

## 2. Yeni Sayfa Ekleme Akışı
Bu iş akışını her yeni sayfa (ör. ürünler, satış, raporlar) eklediğinde çağır.
Adım 1: `app.py` içine yeni route fonksiyonunu `@login_required` ile birlikte ekle.
Adım 2: `templates/` klasörü içine ilgili `.html` dosyasını oluştur ve `base.html`'den extend et.
Adım 3: Sayfaya özel CSS gerekiyorsa `static/css/` altına ayrı dosya aç.
Adım 4: Sayfaya özel JavaScript gerekiyorsa `static/js/` altına ayrı dosya aç.
Adım 5: Navbar veya menüye yeni sayfanın linkini ekle.
Adım 6: Sayfayı tarayıcıda test et ve sonucu kullanıcıya bildir.

## 3. Veritabanı Şema Doğrulama Akışı
Bu iş akışı Firestore koleksiyonlarının doğru kurgulandığını kontrol etmek içindir.
Adım 1: `firebase_config.py` üzerinden Firestore bağlantısını test et.
Adım 2: Beklenen 5 koleksiyonun (kullanicilar, kategoriler, urunler, satislar, satis_detaylari) varlığını kontrol et.
Adım 3: Eksik koleksiyon varsa başlangıç verisi (seed) ekleyerek oluştur.
Adım 4: Varsayılan admin kullanıcısının (admin / hash'lenmiş şifre) var olup olmadığını kontrol et, yoksa ekle.
Adım 5: Doğrulama sonucunu Markdown tablosu olarak kullanıcıya raporla.

## 4. Test ve Hata Ayıklama Akışı
Bu iş akışını her büyük özellikten sonra çağır.
Adım 1: Flask uygulamasını debug modda başlat (`flask run --debug`).
Adım 2: Önemli sayfaları (giriş, dashboard, ürünler, satış, raporlar) sırayla test et.
Adım 3: Konsolda hata varsa logları analiz et ve düzeltme öner.
Adım 4: Düzeltme yapıldıktan sonra ilgili sayfayı tekrar test et.
Adım 5: Test sonuçlarını ve düzeltmeleri özetleyen kısa bir Markdown raporu hazırla.

## 5. GitHub'a Teslim Akışı
Bu iş akışını proje tamamlandığında çağır.
Adım 1: `.gitignore` dosyasının `.env` ve servis hesabı JSON'unu içerdiğini doğrula.
Adım 2: README.md'nin eksiksiz olduğunu kontrol et (kurulum, kullanım, Firebase ayarı, varsayılan admin bilgisi).
Adım 3: Tüm değişikliklerin commit'lendiğinden emin ol.
Adım 4: GitHub repo oluşturma ve push komutlarını kullanıcıya göster.
Adım 5: Teslim öncesi son kontrol listesini sun (UI çalışıyor mu, login çalışıyor mu, satış stok düşürüyor mu, rapor doğru mu).