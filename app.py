"""
Küçük İşletme Stok ve Gelir Yönetimi Sistemi
Ana Flask uygulama dosyası.
"""

import os
from datetime import datetime, timezone
from functools import wraps

import bcrypt
from flask import Flask, render_template, redirect, url_for, request, session, flash
from dotenv import load_dotenv

from firebase_config import get_db

# Ortam değişkenlerini yükle
load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "degistir-bunu-production-da")


# ─────────────────────────────────────────────
# Yardımcı Fonksiyonlar
# ─────────────────────────────────────────────

# Kategori adına göre emoji seçme tablosu (case-insensitive anahtar kelime eşleşmesi)
# Kural sırası önemli: daha özel kurallar önce gelir
_EMOJI_KURALLARI = [
    # ── İçecekler (önce özel, sonra genel) ──────────────────────────
    (["kahve", "coffee", "neskafe", "espresso", "latte"],                           "☕"),
    (["çay", "bitki çay", "bitki çayı", "yeşil çay"],                              "🍵"),
    (["su", "içecek", "içecekler", "kola", "meyve suyu",
      "ayran", "soda", "gazoz", "limonata", "maden suyu"],                         "🥤"),
    # ── Yiyecek / Atıştırmalık ───────────────────────────────────────
    (["atıştırmalık", "cips", "bisküvi", "bisküvü", "kraker",
      "çerez", "kuruyemiş", "fındık", "fıstık"],                                   "🍿"),
    (["çikolata", "şeker", "gofret", "tatlı", "şekerleme",
      "karamel", "bonbon", "draje"],                                                "🍫"),
    (["gıda", "market", "yemek", "bakliyat", "tahıl",
      "makarna", "pirinç", "un", "bulgur", "gıda & içecek",
      "erzak", "kumanya"],                                                          "🍞"),
    (["meyve", "sebze", "salata", "organik"],                                      "🥦"),
    (["süt", "peynir", "yoğurt", "tereyağ", "süt ürün",
      "kefir", "ayran süt"],                                                       "🥛"),
    (["et", "tavuk", "balık", "şarküteri", "sucuk",
      "salam", "jambon", "hindi"],                                                  "🥩"),
    (["fırın", "ekmek", "pasta", "unlu", "poğaça",
      "simit", "börek", "kurabiye"],                                                "🥐"),
    # ── Temizlik ─────────────────────────────────────────────────────
    (["temizlik", "deterjan", "sabun", "çamaşır", "bulaşık",
      "dezenfektan", "çamaşır suyu", "kir", "yüzey"],                             "🧹"),
    # ── Kırtasiye / Ofis ─────────────────────────────────────────────
    (["kırtasiye", "kalem", "defter", "kağıt", "dosya",
      "zımba", "makas", "silgi", "cetvel", "ofis malzeme",
      "tükenmez"],                                                                  "📝"),
    # ── Kişisel Bakım / Kozmetik ─────────────────────────────────────
    (["kişisel bakım", "kozmetik", "parfüm", "makyaj",
      "ruj", "deodorant", "oje", "fondöten", "serum",
      "krem", "losyon", "şampuan", "duş jeli"],                                   "💄"),
    # ── Bakım (genel — kozmetik'ten sonra gelsin) ─────────────────────
    (["bakım", "hijyen", "cilt", "saç", "diş macunu",
      "ağız bakım"],                                                                "🧴"),
    # ── Tekstil / Giyim ──────────────────────────────────────────────
    (["tekstil", "giyim", "kıyafet", "elbise", "tişört",
      "pantolon", "gömlek", "mont", "ceket", "etek",
      "çorap", "iç çamaşır", "pijama"],                                           "👕"),
    # ── Ayakkabı / Çanta ─────────────────────────────────────────────
    (["ayakkabı", "bot", "sandalet", "terlik", "spor ayak"],                      "👟"),
    (["çanta", "valiz", "sırt çantası", "el çantası", "cüzdan"],                  "👜"),
    # ── Takı / Aksesuar (kıyafet aksesuarı) ──────────────────────────
    (["takı", "kolye", "bilezik", "küpe", "yüzük",
      "saat", "gümüş", "altın", "mücevher"],                                      "💍"),
    (["aksesuar", "şapka", "kemer", "fular", "atkı",
      "gözlük", "güneş gözlüğü", "kravat"],                                       "🕶️"),
    # ── Mobilya / Ev Dekorasyonu ──────────────────────────────────────
    (["mobilya", "koltuk", "kanepe", "sandalye", "masa",
      "dolap", "yatak", "raf", "sehpa", "konsol"],                                "🛋️"),
    (["dekorasyon", "dekor", "heykel", "tablo", "çerçeve",
      "vazo", "halı", "perde", "yastık", "nevresim",
      "ev aksesuarı", "ev dekor"],                                                 "🏡"),
    # ── Mutfak / Züccaciye ────────────────────────────────────────────
    (["züccaciye", "mutfak", "tencere", "tava", "bıçak",
      "tabak", "bardak", "çatal", "kaşık", "fırın tepsisi",
      "ev gereç", "mutfak araç"],                                                  "🍳"),
    # ── Elektronik / Teknoloji ────────────────────────────────────────
    (["elektronik", "kablo", "telefon", "bilgisayar",
      "tablet", "kulaklık", "şarj", "adaptör", "hoparlör",
      "televizyon", "tv", "monitör"],                                              "💻"),
    (["fotoğraf", "kamera", "lens", "tripod"],                                     "📷"),
    # ── Araç-Gereç / Hırdavat ────────────────────────────────────────
    (["hırdavat", "alet", "tornavida", "anahtar", "çekiç",
      "vida", "alet kutusu", "elektrik malzeme", "boya malzeme",
      "yapı malzeme", "inşaat"],                                                   "🔧"),
    (["bahçe alet", "kürek", "sulama", "bahçe hortum"],                           "⛏️"),
    # ── Araç / Oto Aksesuar ───────────────────────────────────────────
    (["oto", "otomobil", "araç", "araba", "motor",
      "yağ", "filtre", "lastik", "oto aksesuar"],                                  "🚗"),
    # ── Spor / Outdoor ────────────────────────────────────────────────
    (["spor", "fitness", "antrenman", "egzersiz",
      "dumbbell", "halter", "yoga", "kamp", "outdoor",
      "bisiklet", "koşu"],                                                         "⚽"),
    # ── Sağlık / Eczane ──────────────────────────────────────────────
    (["sağlık", "ilaç", "vitamin", "eczane", "takviye",
      "mineral", "omega", "probiyotik"],                                           "💊"),
    # ── Bebek / Çocuk ────────────────────────────────────────────────
    (["bebek", "mama", "bez", "emzik", "mama sandalye"],                          "🍼"),
    (["çocuk", "oyuncak", "oyun", "lego", "puzzle",
      "peluş", "yapboz"],                                                          "🎮"),
    # ── Kitap / Kültür ────────────────────────────────────────────────
    (["kitap", "dergi", "gazete", "roman", "ansiklopedi",
      "atlas", "sözlük"],                                                          "📚"),
    # ── Bahçe / Bitkiler ──────────────────────────────────────────────
    (["bahçe", "çiçek", "bitki", "saksı", "toprak",
      "gübre", "tohum"],                                                            "🌱"),
    # ── Evcil Hayvan ──────────────────────────────────────────────────
    (["evcil", "kedi", "köpek", "hayvan", "petshop",
      "mama evcil", "pet", "kuş", "akvaryum"],                                    "🐾"),
    # ── Kıymetli Evrak / Ofis Ekipman ────────────────────────────────
    (["yazıcı", "mürekkep", "toner", "tarayıcı", "bilgisayar sarf"],              "🖨️"),
    # ── Aydınlatma / Elektrik ────────────────────────────────────────
    (["aydınlatma", "lamba", "ampul", "led", "elektrik"],                         "💡"),
    # ── Temizlik Ekipman / Süpürge ────────────────────────────────────
    (["süpürge", "paspas", "faraş", "temizlik ekipman"],                          "🧺"),
    # ── Kamp / Outdoor ───────────────────────────────────────────────
    (["kamp", "çadır", "uyku tulumu", "trekking"],                                "⛺"),
    # ── Varsayılan ────────────────────────────────────────────────────
    (["diğer", "genel", "karma", "çeşitli"],                                      "📦"),
]

# Kategori kartları için deterministik renk paleti
_KAT_RENKLERI = [
    "#2C5F2D",  # koyu yeşil — marka
    "#028090",  # turkuaz
    "#1C7293",  # teal
    "#6D2E46",  # berry
    "#E89F47",  # turuncu/hardal
    "#2F3C7E",  # lacivert
    "#97BC62",  # moss yeşili
    "#B85042",  # terracotta
    "#84B59F",  # sage
    "#F96167",  # mercan
]


def emoji_sec(kategori_adi: str) -> str:
    """
    Kategori adına göre uygun emoji döndürür.
    Case-insensitive keyword eşleştirmesi yapar; hiçbiri uymuyorsa 📦 döner.
    Türkçe büyük harf normalizasyonu uygulanır (İ→i, I→ı).

    Args:
        kategori_adi: Kategori adı (herhangi bir büyük/küçük harf karışımı).

    Returns:
        Tek emoji karakter string'i.
    """
    # Python'da "İçecekler".lower() → "i̇çecekler" (birleşik nokta) verir;
    # Önce Türkçe büyük harfleri elle çevir, sonra standart lower() uygula.
    ad_kucuk = (
        kategori_adi
        .replace("İ", "i")   # U+0130 → i (noktalı büyük I)
        .replace("I", "ı")   # U+0049 → ı (Türkçe büyük I → küçük ı)
        .lower()
    )
    for anahtar_kelimeler, emoji in _EMOJI_KURALLARI:
        if any(anahtar in ad_kucuk for anahtar in anahtar_kelimeler):
            return emoji
    return "📦"  # Varsayılan


def renk_sec(kategori_id: str) -> str:
    """
    Kategori id'sinden deterministik renk seçer.
    Aynı id her zaman aynı rengi verir; liste sırasından bağımsızdır.

    Args:
        kategori_id: Firestore doküman id'si.

    Returns:
        Hex renk kodu string'i.
    """
    # id'nin tüm karakterlerinin ASCII değerlerini topla → modulo renk sayısı
    indeks = sum(ord(c) for c in kategori_id) % len(_KAT_RENKLERI)
    return _KAT_RENKLERI[indeks]


# ─────────────────────────────────────────────
# Yardımcı Decorator'lar
# ─────────────────────────────────────────────

def login_required(f):
    """Oturum açmamış kullanıcıları giriş sayfasına yönlendiren decorator."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "kullanici_id" not in session:
            flash("Bu sayfaya erişmek için giriş yapmanız gerekiyor.", "warning")
            return redirect(url_for("giris"))
        return f(*args, **kwargs)
    return decorated_function


# ─────────────────────────────────────────────
# Auth Route'ları
# ─────────────────────────────────────────────

@app.route("/")
def anasayfa():
    """Kök URL'yi dashboard'a yönlendirir; giriş yapılmamışsa login'e."""
    if "kullanici_id" in session:
        return redirect(url_for("dashboard"))
    return redirect(url_for("giris"))


@app.route("/giris", methods=["GET", "POST"])
def giris():
    """Kullanıcı giriş sayfası. POST ile Firestore üzerinden kullanıcı doğrulama yapar."""
    if "kullanici_id" in session:
        return redirect(url_for("dashboard"))

    if request.method == "POST":
        kullanici_adi = request.form.get("kullanici_adi", "").strip()
        sifre = request.form.get("sifre", "")

        # Temel doğrulama: boş alan kontrolü
        if not kullanici_adi or not sifre:
            flash("Kullanıcı adı ve şifre boş bırakılamaz.", "danger")
            return render_template("giris.html")

        try:
            db = get_db()

            # Firestore'dan kullanıcıyı sorgula
            kullanicilar_ref = db.collection("kullanicilar")
            sonuclar = kullanicilar_ref.where("kullanici_adi", "==", kullanici_adi).limit(1).get()

            if not sonuclar:
                flash("Kullanıcı adı veya şifre hatalı.", "danger")
                return render_template("giris.html")

            kullanici_doc = sonuclar[0]
            kullanici = kullanici_doc.to_dict()

            # bcrypt ile şifre doğrulama
            sifre_eslesdi = bcrypt.checkpw(
                sifre.encode("utf-8"),
                kullanici["sifre_hash"].encode("utf-8")
            )

            if not sifre_eslesdi:
                flash("Kullanıcı adı veya şifre hatalı.", "danger")
                return render_template("giris.html")

            # Oturum bilgilerini kaydet
            session["kullanici_id"] = kullanici_doc.id
            session["kullanici_adi"] = kullanici.get("kullanici_adi", "")
            session["ad_soyad"] = kullanici.get("ad_soyad", "")

            flash(f"Hoş geldiniz, {session['ad_soyad'] or session['kullanici_adi']}!", "success")
            return redirect(url_for("dashboard"))

        except Exception:
            flash("Giriş sırasında bir hata oluştu. Lütfen tekrar deneyin.", "danger")
            return render_template("giris.html")

    return render_template("giris.html")


@app.route("/cikis")
def cikis():
    """Kullanıcı oturumunu sonlandırır ve giriş sayfasına yönlendirir."""
    session.clear()
    flash("Başarıyla çıkış yapıldı.", "success")
    return redirect(url_for("giris"))


# ─────────────────────────────────────────────
# Korumalı Sayfalar
# ─────────────────────────────────────────────

@app.route("/dashboard")
@login_required
def dashboard():
    """Ana kontrol paneli — Firestore'dan özet istatistikleri çekip gösterir."""
    try:
        db = get_db()

        # ── Toplam aktif ürün sayısı ──
        urun_docs = list(db.collection("urunler").where("aktif", "==", True).get())
        toplam_urun = len(urun_docs)

        # ── Kritik stokta olan ürünler ──
        # skill kuralı: stok_miktari <= kritik_stok_seviyesi olan ürünler
        kritik_urunler = []
        for doc in urun_docs:
            u = doc.to_dict()
            stok = u.get("stok_miktari", 0)
            kritik = u.get("kritik_stok_seviyesi", 0)
            if stok <= kritik:
                kritik_urunler.append({
                    "ad": u.get("ad", ""),
                    "stok": stok,
                    "kritik": kritik
                })
        kritik_stok_sayisi = len(kritik_urunler)

        # ── Bugünkü satış adedi ve tutarı ──
        simdi_local = datetime.now().astimezone()
        bugun_baslangic = simdi_local.replace(
            hour=0, minute=0, second=0, microsecond=0
        )
        bugunki_satislar = list(
            db.collection("satislar")
            .where("tarih", ">=", bugun_baslangic)
            .get()
        )
        bugunku_satis_adedi = len(bugunki_satislar)
        bugunku_satis_tutari = round(
            sum(s.to_dict().get("toplam_tutar", 0.0) for s in bugunki_satislar), 2
        )

        # ── Bu ayki toplam gelir (ayın 1'inden itibaren) ──
        bu_ay_baslangic = simdi_local.replace(
            day=1, hour=0, minute=0, second=0, microsecond=0
        )
        aylik_satislar = list(
            db.collection("satislar")
            .where("tarih", ">=", bu_ay_baslangic)
            .get()
        )
        aylik_gelir = round(
            sum(s.to_dict().get("toplam_tutar", 0.0) for s in aylik_satislar), 2
        )

    except Exception:
        flash("Dashboard verileri yüklenirken bir hata oluştu.", "danger")
        toplam_urun = 0
        kritik_stok_sayisi = 0
        kritik_urunler = []
        bugunku_satis_adedi = 0
        bugunku_satis_tutari = 0.0
        aylik_gelir = 0.0

    return render_template(
        "dashboard.html",
        toplam_urun=toplam_urun,
        kritik_stok_sayisi=kritik_stok_sayisi,
        kritik_urunler=kritik_urunler,
        bugunku_satis_adedi=bugunku_satis_adedi,
        bugunku_satis_tutari=bugunku_satis_tutari,
        aylik_gelir=aylik_gelir,
    )


@app.route("/urunler")
@login_required
def urunler():
    """
    Ürün listesi sayfası.
    Tüm aktif ürünleri Firestore'dan çeker, kritik olanları üste alır.
    Kategori adlarını id'den çözerek her ürüne ekler.
    """
    try:
        db = get_db()

        # Kategori haritası: {id -> ad}
        kat_docs = list(db.collection("kategoriler").get())
        kat_map = {d.id: d.to_dict().get("ad", "") for d in kat_docs}
        kategoriler_listesi = [{"id": d.id, "ad": d.to_dict().get("ad", "")} for d in kat_docs]
        kategoriler_listesi = sorted(kategoriler_listesi, key=lambda x: x["ad"])

        # Aktif ürünleri çek
        urun_docs = list(db.collection("urunler").where("aktif", "==", True).get())
        urun_listesi = []
        for doc in urun_docs:
            u = doc.to_dict()
            stok = u.get("stok_miktari", 0)
            kritik = u.get("kritik_stok_seviyesi", 0)
            alis = round(float(u.get("alis_fiyati", 0)), 2)
            satis_f = round(float(u.get("satis_fiyati", 0)), 2)
            kar_marji = round(((satis_f - alis) / alis) * 100, 1) if alis > 0 else 0.0

            # Stok durumu hesapla
            if stok == 0:
                stok_durum = "tukendi"
            elif stok <= kritik:
                stok_durum = "kritik"
            else:
                stok_durum = "normal"

            urun_listesi.append({
                "id": doc.id,
                "ad": u.get("ad", ""),
                "kategori_id": u.get("kategori_id", ""),
                "kategori_ad": kat_map.get(u.get("kategori_id", ""), "—"),
                "alis_fiyati": alis,
                "satis_fiyati": satis_f,
                "kar_marji": kar_marji,
                "stok_miktari": stok,
                "kritik_stok_seviyesi": kritik,
                "stok_durum": stok_durum,
            })

        # Kritik ve tükenmiş ürünler üste gelsin
        durum_sirasi = {"tukendi": 0, "kritik": 1, "normal": 2}
        urun_listesi.sort(key=lambda x: durum_sirasi.get(x["stok_durum"], 3))

    except Exception:
        flash("Ürünler yüklenirken bir hata oluştu.", "danger")
        urun_listesi = []
        kategoriler_listesi = []

    return render_template("urunler.html", urunler=urun_listesi, kategoriler=kategoriler_listesi)


@app.route("/urunler/ekle", methods=["GET", "POST"])
@login_required
def urun_ekle():
    """
    Yeni ürün ekleme sayfası.
    GET: Boş formu göster.
    POST: Form verilerini validate edip Firestore'a ekle.
    """
    try:
        db = get_db()
        kat_docs = list(db.collection("kategoriler").get())
        kategoriler_listesi = [{"id": d.id, "ad": d.to_dict().get("ad", "")} for d in kat_docs]
        kategoriler_listesi = sorted(kategoriler_listesi, key=lambda x: x["ad"])
    except Exception:
        flash("Kategoriler yüklenirken hata oluştu.", "danger")
        kategoriler_listesi = []

    if request.method == "POST":
        ad = request.form.get("ad", "").strip()
        kategori_id = request.form.get("kategori_id", "").strip()
        alis_fiyati_str = request.form.get("alis_fiyati", "").strip()
        satis_fiyati_str = request.form.get("satis_fiyati", "").strip()
        stok_miktari_str = request.form.get("stok_miktari", "").strip()
        kritik_stok_str = request.form.get("kritik_stok_seviyesi", "5").strip()

        # Validasyon
        hatalar = []
        if not ad:
            hatalar.append("Ürün adı boş bırakılamaz.")
        if not kategori_id:
            hatalar.append("Kategori seçilmesi zorunludur.")

        try:
            alis_fiyati = float(alis_fiyati_str)
            if alis_fiyati < 0.01:
                hatalar.append("Alış fiyatı 0 veya negatif olamaz (minimum 0.01).")
        except ValueError:
            hatalar.append("Alış fiyatı geçerli bir sayı olmalıdır.")
            alis_fiyati = 0.0

        try:
            satis_fiyati = float(satis_fiyati_str)
            if satis_fiyati < alis_fiyati:
                hatalar.append("Satış fiyatı, alış fiyatından düşük olamaz.")
            elif satis_fiyati <= 0:
                hatalar.append("Satış fiyatı 0'dan büyük olmalıdır.")
        except ValueError:
            hatalar.append("Satış fiyatı geçerli bir sayı olmalıdır.")
            satis_fiyati = 0.0

        try:
            stok_miktari = int(stok_miktari_str)
            if stok_miktari < 0:
                hatalar.append("Stok miktarı negatif olamaz.")
        except ValueError:
            hatalar.append("Stok miktarı tam sayı olmalıdır.")
            stok_miktari = 0

        try:
            kritik_stok = int(kritik_stok_str)
            if kritik_stok < 1:
                hatalar.append("Kritik stok seviyesi minimum 1 olmalıdır.")
        except ValueError:
            hatalar.append("Kritik stok seviyesi tam sayı olmalıdır.")
            kritik_stok = 5

        if hatalar:
            for h in hatalar:
                flash(h, "danger")
            form_data = request.form
            return render_template("urun_form.html", mod="yeni",
                                   kategoriler=kategoriler_listesi, form_data=form_data)

        # Firestore'a kaydet (skill kuralı: olusturulma_tarihi ekle)
        try:
            from google.cloud.firestore import SERVER_TIMESTAMP
            db.collection("urunler").add({
                "ad": ad,
                "kategori_id": kategori_id,
                "alis_fiyati": round(alis_fiyati, 2),
                "satis_fiyati": round(satis_fiyati, 2),
                "stok_miktari": stok_miktari,
                "kritik_stok_seviyesi": kritik_stok,
                "aktif": True,
                "olusturulma_tarihi": SERVER_TIMESTAMP,
            })
            flash(f"'{ad}' ürünü başarıyla eklendi.", "success")
            return redirect(url_for("urunler"))
        except Exception:
            flash("Ürün kaydedilirken bir hata oluştu. Lütfen tekrar deneyin.", "danger")
            return render_template("urun_form.html", mod="yeni",
                                   kategoriler=kategoriler_listesi, form_data=request.form)

    return render_template("urun_form.html", mod="yeni",
                           kategoriler=kategoriler_listesi, form_data={})


@app.route("/urunler/duzenle/<urun_id>", methods=["GET", "POST"])
@login_required
def urun_duzenle(urun_id):
    """
    Mevcut ürünü düzenleme sayfası.
    GET: Mevcut ürün verileriyle formu göster.
    POST: Validate edip Firestore'da güncelle.

    Args:
        urun_id: Düzenlenecek ürünün Firestore doküman id'si.
    """
    try:
        db = get_db()
        urun_ref = db.collection("urunler").document(urun_id)
        urun_doc = urun_ref.get()

        if not urun_doc.exists:
            flash("Ürün bulunamadı.", "danger")
            return redirect(url_for("urunler"))

        urun = urun_doc.to_dict()
        urun["id"] = urun_doc.id

        kat_docs = list(db.collection("kategoriler").get())
        kategoriler = [{"id": d.id, "ad": d.to_dict().get("ad", "")} for d in kat_docs if d.to_dict().get("aktif", True)]
        kategoriler_listesi = sorted(kategoriler, key=lambda x: x["ad"])

    except Exception:
        flash("Ürün bilgileri yüklenirken hata oluştu.", "danger")
        return redirect(url_for("urunler"))

    if request.method == "POST":
        ad = request.form.get("ad", "").strip()
        kategori_id = request.form.get("kategori_id", "").strip()
        alis_fiyati_str = request.form.get("alis_fiyati", "").strip()
        satis_fiyati_str = request.form.get("satis_fiyati", "").strip()
        stok_miktari_str = request.form.get("stok_miktari", "").strip()
        kritik_stok_str = request.form.get("kritik_stok_seviyesi", "5").strip()

        # Validasyon
        hatalar = []
        if not ad:
            hatalar.append("Ürün adı boş bırakılamaz.")
        if not kategori_id:
            hatalar.append("Kategori seçilmesi zorunludur.")

        try:
            alis_fiyati = float(alis_fiyati_str)
            if alis_fiyati < 0.01:
                hatalar.append("Alış fiyatı 0 veya negatif olamaz (minimum 0.01).")
        except ValueError:
            hatalar.append("Alış fiyatı geçerli bir sayı olmalıdır.")
            alis_fiyati = 0.0

        try:
            satis_fiyati = float(satis_fiyati_str)
            if satis_fiyati < alis_fiyati:
                hatalar.append("Satış fiyatı, alış fiyatından düşük olamaz.")
            elif satis_fiyati <= 0:
                hatalar.append("Satış fiyatı 0'dan büyük olmalıdır.")
        except ValueError:
            hatalar.append("Satış fiyatı geçerli bir sayı olmalıdır.")
            satis_fiyati = 0.0

        try:
            stok_miktari = int(stok_miktari_str)
            if stok_miktari < 0:
                hatalar.append("Stok miktarı negatif olamaz.")
        except ValueError:
            hatalar.append("Stok miktarı tam sayı olmalıdır.")
            stok_miktari = 0

        try:
            kritik_stok = int(kritik_stok_str)
            if kritik_stok < 1:
                hatalar.append("Kritik stok seviyesi minimum 1 olmalıdır.")
        except ValueError:
            hatalar.append("Kritik stok seviyesi tam sayı olmalıdır.")
            kritik_stok = 5

        if hatalar:
            for h in hatalar:
                flash(h, "danger")
            return render_template("urun_form.html", mod="duzenle", urun=urun,
                                   kategoriler=kategoriler_listesi, form_data=request.form)

        # Firestore'da güncelle (skill kuralı: guncelleme_tarihi ekle)
        try:
            from google.cloud.firestore import SERVER_TIMESTAMP
            urun_ref.update({
                "ad": ad,
                "kategori_id": kategori_id,
                "alis_fiyati": round(alis_fiyati, 2),
                "satis_fiyati": round(satis_fiyati, 2),
                "stok_miktari": stok_miktari,
                "kritik_stok_seviyesi": kritik_stok,
                "guncelleme_tarihi": SERVER_TIMESTAMP,
            })
            flash(f"'{ad}' ürünü başarıyla güncellendi.", "success")
            return redirect(url_for("urunler"))
        except Exception:
            flash("Ürün güncellenirken bir hata oluştu.", "danger")
            return render_template("urun_form.html", mod="duzenle", urun=urun,
                                   kategoriler=kategoriler_listesi, form_data=request.form)

    # GET: mevcut değerlerle formu göster
    return render_template("urun_form.html", mod="duzenle", urun=urun,
                           kategoriler=kategoriler_listesi, form_data=urun)


@app.route("/urunler/sil/<urun_id>", methods=["POST"])
@login_required
def urun_sil(urun_id):
    """
    Ürünü soft-delete ile pasife alır (aktif=False).
    Dokümanı silmez; satış geçmişi bozulmaz.

    Args:
        urun_id: Silinecek ürünün Firestore doküman id'si.
    """
    try:
        db = get_db()
        from google.cloud.firestore import SERVER_TIMESTAMP
        urun_ref = db.collection("urunler").document(urun_id)
        urun_doc = urun_ref.get()

        if not urun_doc.exists:
            flash("Ürün bulunamadı.", "danger")
            return redirect(url_for("urunler"))

        urun_adi = urun_doc.to_dict().get("ad", "Ürün")
        urun_ref.update({
            "aktif": False,
            "guncelleme_tarihi": SERVER_TIMESTAMP,
        })
        flash(f"'{urun_adi}' ürünü silindi.", "success")
    except Exception:
        flash("Ürün silinirken bir hata oluştu.", "danger")

    return redirect(url_for("urunler"))


@app.route("/kategoriler")
@login_required
def kategoriler():
    """
    Kategori listesi sayfası.
    Firestore'dan aktif kategorileri çeker; her kategorideki aktif ürün sayısını hesaplar.
    Oluşturulma tarihine göre yeniden eskiye sıralar.
    """
    try:
        db = get_db()
        # Tüm dokümanları çek; aktif filtresi template'de uygulanıyor
        kat_docs = list(db.collection("kategoriler").get())
        urun_docs = list(db.collection("urunler").where("aktif", "==", True).get())

        # Kategori başına aktif ürün sayısını say
        urun_sayisi_map = {}
        for doc in urun_docs:
            kid = doc.to_dict().get("kategori_id", "")
            urun_sayisi_map[kid] = urun_sayisi_map.get(kid, 0) + 1

        kat_listesi = []
        for doc in kat_docs:
            k = doc.to_dict()
            if not k.get("aktif", True):
                continue  # Pasif kategorileri atla
            ad = k.get("ad", "")
            # Kayıtlı emoji varsa kullan; yoksa addan dinamik seç
            emoji = k.get("emoji") or emoji_sec(ad)
            # Renk: id'den deterministik hesapla — sıra değişse bile aynı kalır
            renk = renk_sec(doc.id)
            kat_listesi.append({
                "id": doc.id,
                "ad": ad,
                "emoji": emoji,
                "renk": renk,
                "aktif": True,
                "urun_sayisi": urun_sayisi_map.get(doc.id, 0),
                "olusturulma_tarihi": k.get("olusturulma_tarihi"),
            })

        # Alfabetik sırala
        kat_listesi.sort(key=lambda x: x["ad"])

    except Exception:
        flash("Kategoriler yüklenirken bir hata oluştu.", "danger")
        kat_listesi = []

    return render_template("kategoriler.html", kategoriler=kat_listesi)


@app.route("/kategoriler/ekle", methods=["GET", "POST"])
@login_required
def kategori_ekle():
    """
    Yeni kategori ekleme sayfası.
    GET: Boş formu göster.
    POST: Validate et, case-insensitive isim kontrolü yap, Firestore'a ekle.
    """
    from google.cloud.firestore import SERVER_TIMESTAMP

    if request.method == "POST":
        ad = request.form.get("ad", "").strip()

        if not ad:
            flash("Kategori adı boş bırakılamaz.", "danger")
            return render_template("kategori_form.html", mod="yeni", form_data=request.form)

        try:
            db = get_db()
            # Case-insensitive isim kontrolü: tüm aktif kategorileri çek, Python'da karşılaştır
            mevcut_docs = list(db.collection("kategoriler").where("aktif", "==", True).get())
            isimler = [d.to_dict().get("ad", "").lower() for d in mevcut_docs]
            if ad.lower() in isimler:
                flash(f"'{ad}' adında bir kategori zaten var.", "warning")
                return render_template("kategori_form.html", mod="yeni", form_data=request.form)

            db.collection("kategoriler").add({
                "ad": ad,
                "emoji": emoji_sec(ad),  # Addan keyword eşleşmesiyle seçilir
                "aktif": True,
                "olusturulma_tarihi": SERVER_TIMESTAMP,
            })
            flash(f"'{ad}' kategorisi başarıyla eklendi.", "success")
            return redirect(url_for("kategoriler"))
        except Exception:
            flash("Kategori eklenirken bir hata oluştu.", "danger")
            return render_template("kategori_form.html", mod="yeni", form_data=request.form)

    return render_template("kategori_form.html", mod="yeni", form_data={})


@app.route("/kategoriler/duzenle/<kat_id>", methods=["GET", "POST"])
@login_required
def kategori_duzenle(kat_id):
    """
    Mevcut kategoriyi düzenleme sayfası.
    GET: Mevcut adıyla formu göster.
    POST: Validate et, case-insensitive çakışma kontrolü yap, Firestore'da güncelle.
    Not: kategori id değişmez — bağlı ürünlerin kategori_id'si korunur.

    Args:
        kat_id: Düzenlenecek kategorinin Firestore doküman id'si.
    """
    from google.cloud.firestore import SERVER_TIMESTAMP
    try:
        db = get_db()
        kat_ref = db.collection("kategoriler").document(kat_id)
        kat_doc = kat_ref.get()

        if not kat_doc.exists:
            flash("Kategori bulunamadı.", "danger")
            return redirect(url_for("kategoriler"))

        kategori = kat_doc.to_dict()
        kategori["id"] = kat_doc.id

    except Exception:
        flash("Kategori bilgileri yüklenirken hata oluştu.", "danger")
        return redirect(url_for("kategoriler"))

    if request.method == "POST":
        yeni_ad = request.form.get("ad", "").strip()

        if not yeni_ad:
            flash("Kategori adı boş bırakılamaz.", "danger")
            return render_template("kategori_form.html", mod="duzenle",
                                   kategori=kategori, form_data=request.form)

        try:
            # Case-insensitive çakışma kontrolü (kendi id'si hariç)
            mevcut_docs = list(db.collection("kategoriler").where("aktif", "==", True).get())
            for d in mevcut_docs:
                if d.id != kat_id and d.to_dict().get("ad", "").lower() == yeni_ad.lower():
                    flash(f"'{yeni_ad}' adında başka bir kategori zaten var.", "warning")
                    return render_template("kategori_form.html", mod="duzenle",
                                           kategori=kategori, form_data=request.form)

            kat_ref.update({
                "ad": yeni_ad,
                "emoji": emoji_sec(yeni_ad),
                "guncelleme_tarihi": SERVER_TIMESTAMP,
            })
            flash(f"Kategori adı '{yeni_ad}' olarak güncellendi.", "success")
            return redirect(url_for("kategoriler"))
        except Exception:
            flash("Kategori güncellenirken bir hata oluştu.", "danger")
            return render_template("kategori_form.html", mod="duzenle",
                                   kategori=kategori, form_data=request.form)

    return render_template("kategori_form.html", mod="duzenle",
                           kategori=kategori, form_data=kategori)


@app.route("/kategoriler/sil/<kat_id>", methods=["POST"])
@login_required
def kategori_sil(kat_id):
    """
    Kategoriye bağlı aktif ürün yoksa soft-delete yapar (aktif=False).
    Bağlı ürün varsa tam sayıyı mesajla birlikte gösterip silmeyi engeller.

    Args:
        kat_id: Silinecek kategorinin Firestore doküman id'si.
    """
    from google.cloud.firestore import SERVER_TIMESTAMP
    try:
        db = get_db()
        kat_ref = db.collection("kategoriler").document(kat_id)
        kat_doc = kat_ref.get()

        if not kat_doc.exists:
            flash("Kategori bulunamadı.", "danger")
            return redirect(url_for("kategoriler"))

        kat_adi = kat_doc.to_dict().get("ad", "Kategori")

        # Bu kategorideki tüm aktif ürünleri say
        bagli_urunler = list(
            db.collection("urunler")
            .where("kategori_id", "==", kat_id)
            .where("aktif", "==", True)
            .get()
        )
        if bagli_urunler:
            sayi = len(bagli_urunler)
            flash(
                f"Bu kategoride {sayi} aktif ürün var. "
                "Önce ürünleri başka kategoriye taşı veya sil.",
                "warning"
            )
            return redirect(url_for("kategoriler"))

        kat_ref.update({"aktif": False, "guncelleme_tarihi": SERVER_TIMESTAMP})
        flash(f"'{kat_adi}' kategorisi silindi.", "success")
    except Exception:
        flash("Kategori silinirken bir hata oluştu.", "danger")

    return redirect(url_for("kategoriler"))


# ─────────────────────────────────────────────
# Satış Route'ları
# ─────────────────────────────────────────────

@app.route("/satis")
@login_required
def satis():
    """
    Satış işlemi sayfası.
    Aktif ve stoğu > 0 olan ürünleri, kategori adıyla birlikte listeler.
    Kategori pill filtresi için tüm aktif kategorileri de gönderir.
    """
    try:
        db = get_db()

        # Aktif kategorileri çek (filtre dropdown için)
        kat_docs = list(db.collection("kategoriler").where("aktif", "==", True).get())
        kategori_map = {d.id: d.to_dict().get("ad", "") for d in kat_docs}
        kategoriler = sorted(
            [{"id": d.id, "ad": d.to_dict().get("ad", "")} for d in kat_docs],
            key=lambda x: x["ad"]
        )

        # Aktif ve stoklu ürünleri çek
        urun_docs = list(db.collection("urunler").where("aktif", "==", True).get())
        urun_listesi = []
        for doc in urun_docs:
            u = doc.to_dict()
            stok = u.get("stok_miktari", 0)
            if stok <= 0:
                continue  # Tükenenler satışa sunulmaz
            kid = u.get("kategori_id", "")
            urun_listesi.append({
                "id": doc.id,
                "ad": u.get("ad", ""),
                "kategori_id": kid,
                "kategori_adi": kategori_map.get(kid, "Genel"),
                "satis_fiyati": round(float(u.get("satis_fiyati", 0)), 2),
                "alis_fiyati": round(float(u.get("alis_fiyati", 0)), 2),
                "stok_miktari": stok,
                "kritik_stok": stok <= u.get("kritik_stok_seviyesi", 5),
            })
        urun_listesi.sort(key=lambda x: x["ad"])

    except Exception:
        flash("Ürünler yüklenirken hata oluştu.", "danger")
        urun_listesi = []
        kategoriler = []

    return render_template("satis.html", urunler=urun_listesi, kategoriler=kategoriler)


@app.route("/satis/tamamla", methods=["POST"])
@login_required
def satis_tamamla():
    """
    Sepeti JSON olarak alır, Firestore transaction ile atomik kaydeder.
    satis-transaction skill kuralı: 1-OKU, 2-KONTROL, 3-YAZ sırası korunur.
    Returns: JSON {success, satis_id, toplam_tutar, toplam_kar, mesaj} veya {success, error}
    """
    from google.cloud import firestore as fs
    from google.cloud.firestore import SERVER_TIMESTAMP
    from flask import jsonify

    # JSON body parse
    try:
        data = request.get_json(force=True) or {}
        sepet = data.get("sepet", [])
    except Exception:
        return jsonify({"success": False, "error": "Geçersiz istek formatı."}), 400

    if not sepet:
        return jsonify({"success": False, "error": "Sepet boş. En az bir ürün ekleyin."}), 400

    # Adet validasyonu
    for item in sepet:
        try:
            item["adet"] = int(item["adet"])
            if item["adet"] <= 0:
                raise ValueError()
        except (ValueError, KeyError):
            return jsonify({"success": False, "error": "Ürün adetleri geçersiz."}), 400

    db = get_db()
    kullanici_id = session.get("kullanici_id", "")
    kullanici_adi = session.get("kullanici_adi", "")

    # Kategori adlarını transaction dışında çek
    try:
        kat_docs = list(db.collection("kategoriler").get())
        kategori_map = {d.id: d.to_dict().get("ad", "") for d in kat_docs}
    except Exception:
        kategori_map = {}

    @fs.transactional
    def satis_yap(transaction, sepet, kullanici_id, kullanici_adi):
        """
        Sepetteki ürünleri atomik olarak satışa dönüştürür.
        satis-transaction skill: ADIM 1-OKU → ADIM 2-KONTROL → ADIM 3-YAZ

        Args:
            transaction: Firestore transaction nesnesi.
            sepet: [{'urun_id': str, 'adet': int}, ...]
            kullanici_id: Oturumdaki kullanıcı id'si.
            kullanici_adi: Oturumdaki kullanıcı adı.
        """
        # ADIM 1 — Tüm ürünleri transaction içinde OKU
        urun_refs = [
            db.collection("urunler").document(item["urun_id"])
            for item in sepet
        ]
        urun_snaps = [ref.get(transaction=transaction) for ref in urun_refs]

        # ADIM 2 — Her ürün için KONTROL (aktiflik + stok yeterliliği)
        for i, snap in enumerate(urun_snaps):
            if not snap.exists:
                raise ValueError(f"Bir ürün bulunamadı (id: {sepet[i]['urun_id']}).")
            u = snap.to_dict()
            if not u.get("aktif", True):
                raise ValueError(f"'{u.get('ad', '?')}' ürünü artık aktif değil.")
            mevcut = u.get("stok_miktari", 0)
            istenen = sepet[i]["adet"]
            if mevcut < istenen:
                raise ValueError(
                    f"'{u.get('ad', '?')}' için yetersiz stok! "
                    f"Mevcut: {mevcut}, İstenen: {istenen}"
                )

        # ADIM 3a — Toplam tutar ve kâr hesapla
        toplam_tutar = 0.0
        toplam_kar   = 0.0
        toplam_adet  = 0
        detaylar     = []
        for i, item in enumerate(sepet):
            u          = urun_snaps[i].to_dict()
            satis_fyt  = round(float(u.get("satis_fiyati", 0)), 2)
            alis_fyt   = round(float(u.get("alis_fiyati",  0)), 2)
            adet       = item["adet"]
            ara_toplam = round(satis_fyt * adet, 2)
            kar        = round((satis_fyt - alis_fyt) * adet, 2)
            kid        = u.get("kategori_id", "")
            toplam_tutar += ara_toplam
            toplam_kar   += kar
            toplam_adet  += adet
            detaylar.append({
                "urun_id":            item["urun_id"],
                "urun_adi":           u.get("ad", ""),
                "kategori_id":        kid,
                "kategori_adi":       kategori_map.get(kid, ""),
                "adet":               adet,
                "birim_alis_fiyati":  alis_fyt,
                "birim_satis_fiyati": satis_fyt,
                "toplam_tutar":       ara_toplam,
                "kar_tutari":         kar,
            })

        toplam_tutar = round(toplam_tutar, 2)
        toplam_kar   = round(toplam_kar, 2)

        # ADIM 3b — "satislar" ana kaydını YAZ
        satis_ref = db.collection("satislar").document()
        transaction.set(satis_ref, {
            "kullanici_id":  kullanici_id,
            "kullanici_adi": kullanici_adi,
            "toplam_tutar":  toplam_tutar,
            "toplam_kar":    toplam_kar,
            "urun_sayisi":   len(sepet),
            "toplam_adet":   toplam_adet,
            "tarih":         SERVER_TIMESTAMP,
            "aktif":         True,
        })

        # ADIM 3c — "satis_detaylari" satırlarını YAZ
        for detay in detaylar:
            detay["satis_id"] = satis_ref.id
            detay["tarih"]    = SERVER_TIMESTAMP
            detay_ref = db.collection("satis_detaylari").document()
            transaction.set(detay_ref, detay)

        # ADIM 3d — Stokları DÜŞÜR
        for i, ref in enumerate(urun_refs):
            yeni_stok = urun_snaps[i].to_dict()["stok_miktari"] - sepet[i]["adet"]
            transaction.update(ref, {
                "stok_miktari":      yeni_stok,
                "guncelleme_tarihi": SERVER_TIMESTAMP,
            })

        return satis_ref.id, toplam_tutar, toplam_kar

    try:
        transaction = db.transaction()
        satis_id, toplam, kar = satis_yap(
            transaction, sepet, kullanici_id, kullanici_adi
        )
        from flask import jsonify as _jsonify
        return _jsonify({
            "success":      True,
            "satis_id":     satis_id,
            "toplam_tutar": toplam,
            "toplam_kar":   kar,
            "mesaj":        "Satış başarıyla tamamlandı.",
        })
    except ValueError as e:
        from flask import jsonify as _jsonify
        return _jsonify({"success": False, "error": str(e)}), 409
    except Exception as e:
        from flask import jsonify as _jsonify
        return _jsonify({"success": False, "error": f"Beklenmedik bir hata: {str(e)}"}), 500
@login_required
def satis():
    """
    Satış işlemi sayfası.
    Aktif ve stoğu > 0 olan ürünleri, kategori adıyla birlikte listeler.
    Kategori pill filtresi için tüm aktif kategorileri de gönderir.
    """
    try:
        db = get_db()

        # Aktif kategorileri çek (filtre dropdown için)
        kat_docs = list(db.collection("kategoriler").where("aktif", "==", True).get())
        kategori_map = {d.id: d.to_dict().get("ad", "") for d in kat_docs}
        kategoriler = sorted(
            [{"id": d.id, "ad": d.to_dict().get("ad", "")} for d in kat_docs],
            key=lambda x: x["ad"]
        )

        # Aktif ve stoklu ürünleri çek
        urun_docs = list(db.collection("urunler").where("aktif", "==", True).get())
        urun_listesi = []
        for doc in urun_docs:
            u = doc.to_dict()
            stok = u.get("stok_miktari", 0)
            if stok <= 0:
                continue  # Tükenenler satışa sunulmaz
            kat_id = u.get("kategori_id", "")
            urun_listesi.append({
                "id": doc.id,
                "ad": u.get("ad", ""),
                "kategori_id": kat_id,
                "kategori_adi": kategori_map.get(kat_id, "Genel"),
                "satis_fiyati": round(float(u.get("satis_fiyati", 0)), 2),
                "alis_fiyati": round(float(u.get("alis_fiyati", 0)), 2),
                "stok_miktari": stok,
                "kritik_stok": stok <= u.get("kritik_stok_seviyesi", 5),
            })
        urun_listesi.sort(key=lambda x: x["ad"])

    except Exception:
        flash("Ürünler yüklenirken hata oluştu.", "danger")
        urun_listesi = []
        kategoriler = []


    return render_template("satis.html", urunler=urun_listesi, kategoriler=kategoriler)



# ─────────────────────────────────────────────
# Raporlar Route'u
# ─────────────────────────────────────────────

@app.route("/raporlar")
@login_required
def raporlar():
    """
    Raporlar sayfası.
    rapor-uretici skill kurallarına göre son 30 günlük istatistikler, 
    en çok satan ürünler, kategori bazlı satışlar ve grafik hesaplanır.
    """
    from datetime import timedelta, datetime, timezone
    from collections import defaultdict
    import calendar

    try:
        db = get_db()
        simdi_local = datetime.now().astimezone()
        otuz_gun_once = simdi_local - timedelta(days=30)
        
        # Bu ayın başı
        bu_ay_basi = simdi_local.replace(day=1, hour=0, minute=0, second=0, microsecond=0)

        # ── Son 30 günlük satışlar (Ana Sorgu) ──
        satis_docs = list(
            db.collection("satislar")
            .where("tarih", ">=", otuz_gun_once)
            .get()
        )
        
        # Temel Metrikler (30 Gün)
        toplam_satis_tutari = 0.0
        toplam_kar = 0.0
        satis_adedi = len(satis_docs)
        
        # Bu ay metrikleri
        bu_ay_satis = 0.0
        bu_ay_kar = 0.0
        
        gunluk_map = defaultdict(float)

        for doc in satis_docs:
            d = doc.to_dict()
            tutar = d.get("toplam_tutar", 0.0)
            kar = d.get("toplam_kar", 0.0)
            tarih = d.get("tarih")
            
            toplam_satis_tutari += tutar
            toplam_kar += kar
            
            if tarih:
                # Firestore'dan gelen tarihi yerel saate çevir
                tarih_local = tarih.astimezone()
                
                # Günlük harita için
                gun_str = tarih_local.strftime("%Y-%m-%d")
                gunluk_map[gun_str] += tutar
                
                # Bu ay hesaplaması
                if tarih_local >= bu_ay_basi:
                    bu_ay_satis += tutar
                    bu_ay_kar += kar
                    
        ortalama_satis_tutari = round(toplam_satis_tutari / satis_adedi, 2) if satis_adedi > 0 else 0.0
        
        toplam_satis_tutari = round(toplam_satis_tutari, 2)
        toplam_kar = round(toplam_kar, 2)
        bu_ay_satis = round(bu_ay_satis, 2)
        bu_ay_kar = round(bu_ay_kar, 2)
        
        # En yüksek satış günü (Son 30 gün)
        en_yuksek_satis_gunu = "Yok"
        if gunluk_map:
            max_gun = max(gunluk_map.items(), key=lambda x: x[1])
            dt_max = datetime.strptime(max_gun[0], "%Y-%m-%d")
            aylar = ["Oca", "Şub", "Mar", "Nis", "May", "Haz", "Tem", "Ağu", "Eyl", "Eki", "Kas", "Ara"]
            en_yuksek_satis_gunu = f"{dt_max.day} {aylar[dt_max.month-1]}"

        # ── Satis ID listesi ──
        satis_id_listesi = [d.id for d in satis_docs]

        # ── Günlük satış grafiği (son 14 gün, eksik günler 0) ──
        aylar = ["Oca", "Şub", "Mar", "Nis", "May", "Haz", "Tem", "Ağu", "Eyl", "Eki", "Kas", "Ara"]
        gunluk_satis_grafigi = []
        for i in range(13, -1, -1):
            gun_dt = simdi_local - timedelta(days=i)
            gun_key = gun_dt.strftime("%Y-%m-%d")
            tutar = round(gunluk_map.get(gun_key, 0.0), 2)
            etiket = f"{gun_dt.day} {aylar[gun_dt.month-1]}"
            gunluk_satis_grafigi.append({
                "tarih": etiket,
                "tutar": tutar,
            })
            
        print("DEBUG GRAFİK VERİSİ:", gunluk_satis_grafigi)

        # ── Satis Detaylari ──
        en_cok_satan = []
        kategori_bazli = []
        
        if satis_id_listesi:
            detay_docs = list(
                db.collection("satis_detaylari")
                .where("tarih", ">=", otuz_gun_once)
                .get()
            )
            
            urun_map = defaultdict(lambda: {"adet": 0, "tutar": 0.0, "kar": 0.0, "ad": ""})
            kat_map = defaultdict(lambda: {"adet": 0, "tutar": 0.0, "ad": ""})
            
            for d in detay_docs:
                det = d.to_dict()
                if det.get("satis_id") in satis_id_listesi:
                    # Ürün bazlı
                    uid = det.get("urun_id", "")
                    urun_map[uid]["adet"] += det.get("adet", 0)
                    urun_map[uid]["tutar"] += det.get("toplam_tutar", det.get("ara_toplam", 0.0))
                    urun_map[uid]["kar"] += det.get("kar_tutari", 0.0)
                    urun_map[uid]["ad"] = det.get("urun_adi", det.get("urun_ad", uid))
                    
                    # Kategori bazlı
                    kid = det.get("kategori_id", "")
                    kad = det.get("kategori_adi", "Genel")
                    if not kid: 
                        kid = "Genel"
                    kat_map[kid]["adet"] += det.get("adet", 0)
                    kat_map[kid]["tutar"] += det.get("toplam_tutar", det.get("ara_toplam", 0.0))
                    kat_map[kid]["ad"] = kad
            
            en_cok_satan = sorted(
                [{"ad": v["ad"], "adet": v["adet"], "tutar": round(v["tutar"], 2), "kar": round(v["kar"], 2)}
                 for v in urun_map.values()],
                key=lambda x: x["adet"], reverse=True
            )[:5]
            
            kategori_bazli = sorted(
                [{"ad": v["ad"], "adet": v["adet"], "tutar": round(v["tutar"], 2)}
                 for v in kat_map.values()],
                key=lambda x: x["tutar"], reverse=True
            )

    except Exception as e:
        flash(f"Raporlar yüklenirken bir hata oluştu.", "danger")
        toplam_satis_tutari = 0.0
        toplam_kar = 0.0
        satis_adedi = 0
        ortalama_satis_tutari = 0.0
        bu_ay_satis = 0.0
        bu_ay_kar = 0.0
        en_yuksek_satis_gunu = "Yok"
        en_cok_satan = []
        kategori_bazli = []
        gunluk_satis_grafigi = []

    return render_template(
        "raporlar.html",
        toplam_satis_tutari=toplam_satis_tutari,
        toplam_kar=toplam_kar,
        satis_adedi=satis_adedi,
        ortalama_satis_tutari=ortalama_satis_tutari,
        bu_ay_satis=bu_ay_satis,
        bu_ay_kar=bu_ay_kar,
        en_yuksek_satis_gunu=en_yuksek_satis_gunu,
        en_cok_satan=en_cok_satan,
        kategori_bazli=kategori_bazli,
        gunluk_satis_grafigi=gunluk_satis_grafigi,
    )


# ─────────────────────────────────────────────
# Hata Yönetimi
# ─────────────────────────────────────────────
@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

# ─────────────────────────────────────────────
# Uygulama Başlatma
# ─────────────────────────────────────────────

if __name__ == "__main__":
    debug_mod = os.getenv("FLASK_DEBUG", "True").lower() in ("true", "1", "yes")
    app.run(debug=debug_mod, host="0.0.0.0", port=5001)

