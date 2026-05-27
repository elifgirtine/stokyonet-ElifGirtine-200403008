/**
 * giris.js — Giriş sayfası JavaScript
 * Şifre göster/gizle ve form doğrulama davranışları.
 */

document.addEventListener("DOMContentLoaded", () => {

    // ── Şifre Göster / Gizle ──
    const toggleBtn = document.getElementById("toggle-sifre");
    const sifreInput = document.getElementById("sifre");

    if (toggleBtn && sifreInput) {
        toggleBtn.addEventListener("click", () => {
            const isPassword = sifreInput.type === "password";
            sifreInput.type = isPassword ? "text" : "password";
            toggleBtn.textContent = isPassword ? "🙈" : "👁️";
        });
    }

    // ── Giriş Butonu Yükleniyor Durumu ──
    const form = document.getElementById("giris-formu");
    const girisBtn = document.getElementById("giris-btn");

    if (form && girisBtn) {
        form.addEventListener("submit", (e) => {
            // HTML5 validasyon başarısızsa devam etme
            if (!form.checkValidity()) return;

            girisBtn.disabled = true;
            girisBtn.textContent = "Giriş yapılıyor…";
            girisBtn.style.opacity = "0.8";
        });
    }

});
