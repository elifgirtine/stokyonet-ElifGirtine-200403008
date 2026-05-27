---
trigger: always_on
---

# Küçük İşletme Stok ve Gelir Yönetimi - Proje Kuralları

## Teknoloji Yığını (Asla Değiştirme)
- **Backend:** Python 3.10+ ile Flask kullan. Django, FastAPI veya başka framework ÖNERME.
- **Frontend:** HTML5, Vanilla CSS, Vanilla JavaScript. React, Vue, Tailwind, Bootstrap KULLANMA.
- **Template:** Jinja2 (Flask'in dahili motoru).
- **Veritabanı:** Google Firebase Firestore. SQLite, MySQL, PostgreSQL ASLA önerme.
- **Auth:** Şifreleri her zaman `bcrypt` ile hashle. Açık metin şifre kabul etme.

## Dosya/Klasör Yapısı
- Ana uygulama dosyası: `app.py`
- Firebase yapılandırması: `firebase_config.py`
- Şablonlar: `templates/` klasörü
- Statik dosyalar (CSS, JS, img): `static/` klasörü
- Ortam değişkenleri: `.env` (asla GitHub'a yükleme, `.gitignore`'a ekle)

## Kodlama Standartları
- Değişken ve fonksiyon isimleri `snake_case` (Python standardı).
- HTML id/class isimleri `kebab-case` kullan.
- Her Flask route fonksiyonunun başına ne işe yaradığını anlatan docstring yaz.
- Her yeni fonksiyona açıklama yorumu ekle.

## Güvenlik Kuralları (ZORUNLU)
- Firebase API anahtarlarını ve servis hesabı JSON'unu ASLA koda gömme. `.env` veya ayrı bir dosyadan oku.
- Her korumalı route'a `@login_required` decoratorı uygula.
- Kullanıcı girişlerini her zaman validasyondan geçir (boş alan, sayısal kontrol vb.).
- Şifreleri, token'ları ve hassas veriyi ASLA `console.log` veya `print` ile loglama.
- SQL injection gibi NoSQL injection'a karşı kullanıcı girdilerini doğrudan Firestore sorgusuna basma; önce temizle.

## Veritabanı Kuralları
- Firestore koleksiyon isimleri Türkçe ve çoğul olarak şu şekilde olmalı: `kullanicilar`, `kategoriler`, `urunler`, `satislar`, `satis_detaylari`.
- Para birimi her zaman Türk Lirası (₺). Tutarları `float` değil, ondalık hassasiyet için 2 basamağa yuvarlayarak göster.
- Stok güncelleyen TÜM işlemleri (özellikle satışları) Firestore `transaction` içinde yap. Yarım kalan satış stoğu bozmasın.

## UI/UX Kuralları
- Ana renk paleti: 
  - Birincil/Marka: `#2C5F2D` (koyu yeşil — güven)
  - Gelir/Pozitif: `#2ECC71` (yeşil)
  - Gider/Kritik stok uyarısı: `#E74C3C` (kırmızı)
  - Nötr arka plan: `#F5F5F5`
- Kritik stok seviyesinin altındaki ürünleri listede kırmızı arka planla veya kırmızı bir badge ile işaretle.
- Tüm formlar HTML5 validation (`required`, `type="number"` vb.) ile temel kontrolden geçsin.
- Tüm sayfalar mobil uyumlu (responsive) olsun; basit medya sorgularıyla.

## Hata Yönetimi
- Tüm Firestore çağrılarını `try/except` bloğu içine al.
- Hata mesajları kullanıcıya Flask `flash()` ile gösterilsin; teknik hata stack trace'i kullanıcıya gösterme.
- Yetersiz stok, hatalı şifre, eksik form alanı gibi durumlar için anlamlı Türkçe mesajlar yaz.

## GitHub ve Belgeleme
- Her önemli özellik tamamlandığında anlamlı bir commit mesajı öner (örn. "feat: satış transaction mantığı eklendi").
- README.md dosyasında kurulum adımları, gerekli paketler ve Firebase bağlantı talimatı bulunsun.
- `.gitignore` içinde mutlaka: `.env`, `__pycache__/`, `*.json` (servis hesabı anahtarı), `venv/`.