# 📦 StokYönet — Küçük İşletme Stok ve Gelir Yönetimi

Küçük işletmeler için geliştirilmiş, Flask + Firebase Firestore tabanlı stok ve gelir yönetim sistemi.

---

## 🚀 Hızlı Başlangıç

### Gereksinimler
- Python 3.9+
- Firebase servis hesabı JSON dosyası

### Kurulum (Tek Komut)
```bash
python kurulum.py
```

Kurulum scripti tüm adımları otomatik halleder.
Sadece Firebase JSON dosyanızın yolunu girmeniz yeterli.

### Uygulamayı Başlat
```bash
python app.py
```

Tarayıcıda açın: http://localhost:5001

**Varsayılan Giriş:** admin / Admin123!

---

## 🚀 Özellikler

- 🔐 Güvenli kullanıcı girişi (bcrypt ile şifre hashleme)
- 📦 Ürün ekleme, düzenleme, silme ve stok takibi
- 🗂️ Kategori yönetimi
- 💳 Atomik satış işlemi (Firestore transaction)
- ⚠️ Kritik stok uyarıları
- 📊 Gelir/gider raporları (son 30 gün)
- 📱 Mobil uyumlu (responsive) arayüz

---

## 🛠️ Kurulum

### 1. Depoyu Klonlayın
```bash
git clone https://github.com/KULLANICI_ADI/stok-takip.git
cd stok-takip
```

### 2. Sanal Ortam Oluşturun ve Aktive Edin
```bash
python -m venv venv

# macOS / Linux
source venv/bin/activate

# Windows
venv\Scripts\activate
```

### 3. Bağımlılıkları Yükleyin
```bash
pip install -r requirements.txt
```

### 4. Firebase Servis Hesabı Ayarı

1. [Firebase Console](https://console.firebase.google.com/) → Proje Ayarları → Hizmet Hesapları
2. **"Yeni özel anahtar oluştur"** butonuna tıklayın
3. İndirilen JSON dosyasını proje kök dizinine `serviceAccountKey.json` adıyla kaydedin
4. Bu dosyanın `.gitignore`'da bulunduğunu doğrulayın

### 5. Ortam Değişkenlerini Yapılandırın
```bash
cp .env.example .env
```

`.env` dosyasını açın ve aşağıdaki değerleri doldurun:

```env
SECRET_KEY=guclu-rastgele-bir-anahtar
FLASK_ENV=development
FLASK_DEBUG=True
FIREBASE_SERVICE_ACCOUNT_PATH=serviceAccountKey.json
```

> ⚠️ `.env` dosyasını **asla** GitHub'a yüklemeyin!

### 6. Uygulamayı Başlatın
```bash
python app.py
```

Tarayıcınızda `http://localhost:5000` adresini açın.

---

## 🗄️ Firebase Firestore Koleksiyonları

| Koleksiyon        | Açıklama                          |
|-------------------|-----------------------------------|
| `kullanicilar`    | Sistem kullanıcıları              |
| `kategoriler`     | Ürün kategorileri                 |
| `urunler`         | Ürünler ve stok bilgileri         |
| `satislar`        | Satış kayıtları (başlık)          |
| `satis_detaylari` | Satış satır kalemleri             |

---

## 👤 Varsayılan Admin Kullanıcısı

İlk kurulumda Firestore'a manuel olarak veya seed scripti ile ekleyin:

| Alan           | Değer                       |
|----------------|-----------------------------|
| kullanici_adi  | `admin`                     |
| sifre          | bcrypt ile hashlenmiş değer |
| rol            | `admin`                     |

---

## 📁 Proje Yapısı

```
stok-takip/
├── app.py                  # Ana Flask uygulaması
├── firebase_config.py      # Firebase bağlantı yapılandırması
├── requirements.txt        # Python bağımlılıkları
├── .env                    # Ortam değişkenleri (GitHub'a yükleme!)
├── .env.example            # Ortam değişkenleri şablonu
├── .gitignore
├── templates/
│   ├── base.html           # Temel şablon
│   ├── giris.html          # Giriş sayfası
│   ├── dashboard.html      # Ana kontrol paneli
│   ├── urunler.html        # Ürün yönetimi
│   ├── kategoriler.html    # Kategori yönetimi
│   ├── satis.html          # Satış işlemi
│   └── raporlar.html       # Raporlar
└── static/
    ├── css/
    │   └── main.css        # Ana stil dosyası
    └── js/
        ├── main.js         # Global JavaScript
        └── giris.js        # Giriş sayfası JavaScript
```

---

## 🔒 Güvenlik Notları

- Şifreler `bcrypt` ile hashlenir, düz metin saklanmaz
- Firebase kimlik bilgileri `.env` ve `serviceAccountKey.json` üzerinden okunur
- Tüm korumalı route'lar `@login_required` decorator'ı ile güvence altına alınmıştır
- Tüm Firestore yazma işlemleri `try/except` bloğu içindedir

---

## 📦 Kullanılan Teknolojiler

| Teknoloji         | Versiyon    | Amaç                         |
|-------------------|-------------|------------------------------|
| Python            | 3.10+       | Backend dili                 |
| Flask             | 3.0+        | Web framework                |
| Firebase Admin    | 6.5+        | Firestore bağlantısı         |
| bcrypt            | 4.1+        | Şifre hashleme               |
| python-dotenv     | —           | Ortam değişkeni yönetimi     |

---

## 🤝 Katkı

Pull request'ler memnuniyetle karşılanır. Büyük değişiklikler için önce bir issue açın.

---

## 📄 Lisans

MIT
