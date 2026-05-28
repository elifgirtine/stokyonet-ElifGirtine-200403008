/**
 * urunler.js — Ürün Yönetimi Sayfası JavaScript
 * Arama filtresi, kategori filtresi ve silme onayı.
 */

document.addEventListener("DOMContentLoaded", () => {

    const aramaInput    = document.getElementById("arama-input");
    const kategoriFiltre = document.getElementById("kategori-filtre");
    const tabloBody     = document.querySelector("#urun-tablosu tbody");
    const noResults     = document.getElementById("no-results");

    // ── Filtreleme ana fonksiyonu ──────────────────────────────────
    function filtrele() {
        if (!tabloBody) return;

        const aramaMetni   = (aramaInput?.value || "").toLowerCase().trim();
        const seciliKat    = kategoriFiltre?.value || "";
        const satirlar     = tabloBody.querySelectorAll("tr.urun-satiri");
        let gorunenSayi    = 0;

        satirlar.forEach((satir) => {
            const urunAdi    = (satir.dataset.ad || "").toLowerCase();
            const urunKat    = satir.dataset.kategori || "";

            const aramaEslesti = !aramaMetni || urunAdi.includes(aramaMetni);
            const katEslesti   = !seciliKat  || urunKat === seciliKat;

            if (aramaEslesti && katEslesti) {
                satir.style.display = "";
                gorunenSayi++;
            } else {
                satir.style.display = "none";
            }
        });

        // Hiç sonuç yoksa mesaj göster
        if (noResults) {
            noResults.style.display = gorunenSayi === 0 ? "block" : "none";
        }
    }

    // ── Event Listener'lar ────────────────────────────────────────
    if (aramaInput) {
        aramaInput.addEventListener("input", filtrele);
    }

    if (kategoriFiltre) {
        kategoriFiltre.addEventListener("change", filtrele);
    }

    // ── Silme Onayı ───────────────────────────────────────────────
    // HTML'de onsubmit="return silinsinMi(this, 'Ürün Adı')" ile çağrılır
    window.silinsinMi = function (form, urunAdi) {
        return confirm(`"${urunAdi}" ürününü silmek istediğinize emin misiniz?\n\nBu işlem geri alınamaz.`);
    };

});
