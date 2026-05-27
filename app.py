"""
Küçük İşletme Stok ve Gelir Yönetimi Sistemi
Ana Flask uygulama dosyası.
"""

import os
from functools import wraps
from flask import Flask, render_template, redirect, url_for, request, session, flash
from dotenv import load_dotenv

# Ortam değişkenlerini yükle
load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "degistir-bunu-production-da")


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
    """Kullanıcı giriş sayfası. POST ile kullanıcı doğrulama yapar."""
    if "kullanici_id" in session:
        return redirect(url_for("dashboard"))

    if request.method == "POST":
        kullanici_adi = request.form.get("kullanici_adi", "").strip()
        sifre = request.form.get("sifre", "")

        if not kullanici_adi or not sifre:
            flash("Kullanıcı adı ve şifre boş bırakılamaz.", "danger")
            return render_template("giris.html")

        # TODO: Firebase'den kullanıcı doğrulama eklenecek
        # Şimdilik geliştirme amaçlı geçici giriş
        flash("Firebase bağlantısı henüz yapılandırılmadı.", "warning")
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
    """Ana kontrol paneli — özet istatistikleri gösterir."""
    return render_template("dashboard.html")


@app.route("/urunler")
@login_required
def urunler():
    """Ürün listesi sayfası."""
    return render_template("urunler.html")


@app.route("/kategoriler")
@login_required
def kategoriler():
    """Kategori yönetimi sayfası."""
    return render_template("kategoriler.html")


@app.route("/satis")
@login_required
def satis():
    """Satış işlemi sayfası."""
    return render_template("satis.html")


@app.route("/raporlar")
@login_required
def raporlar():
    """Gelir/gider ve stok raporları sayfası."""
    return render_template("raporlar.html")


# ─────────────────────────────────────────────
# Uygulama Başlatma
# ─────────────────────────────────────────────

if __name__ == "__main__":
    debug_mod = os.getenv("FLASK_DEBUG", "True").lower() in ("true", "1", "yes")
    app.run(debug=debug_mod, host="0.0.0.0", port=5000)
