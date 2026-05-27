/**
 * main.js — StokYönet Global JavaScript
 * Sidebar toggle ve genel UI davranışları.
 */

document.addEventListener("DOMContentLoaded", () => {

    // ── Sidebar Mobil Toggle ──
    const sidebar = document.getElementById("sidebar");
    const toggleBtn = document.getElementById("sidebar-toggle");

    if (sidebar && toggleBtn) {
        toggleBtn.addEventListener("click", () => {
            sidebar.classList.toggle("open");
        });

        // Sidebar dışına tıklanınca kapat
        document.addEventListener("click", (e) => {
            if (
                sidebar.classList.contains("open") &&
                !sidebar.contains(e.target) &&
                e.target !== toggleBtn
            ) {
                sidebar.classList.remove("open");
            }
        });
    }

    // ── Flash Mesajlarını Otomatik Kapat (5 sn) ──
    const flashMessages = document.querySelectorAll(".flash");
    flashMessages.forEach((flash) => {
        setTimeout(() => {
            flash.style.transition = "opacity 0.4s ease";
            flash.style.opacity = "0";
            setTimeout(() => flash.remove(), 400);
        }, 5000);
    });

});
