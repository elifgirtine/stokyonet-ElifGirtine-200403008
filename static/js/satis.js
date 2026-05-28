/**
 * satis.js — Satış Sayfası Vanilla JS
 * Sepet yönetimi, filtreleme, arama ve satış tamamlama.
 * Hiçbir framework kullanılmaz; rules.md standartlarına uygun.
 */

"use strict";

// ── Durum ────────────────────────────────────────────────────────────────────
/**
 * Sepet dizisi. Her eleman:
 * { urun_id, urun_adi, kategori_id, satis_fiyati, alis_fiyati, stok, adet }
 */
let sepet = [];

/** Aktif kategori filtresi (boş = tümü) */
let aktifKategori = "";

/** Aktif arama metni */
let aramaMetni = "";

/**
 * Sunucudan gelen tüm ürün verisi — ID lookup için kullanılır.
 * onclick attribute'unda JSON geçmek çift-tırnak sorununa yol açtığından
 * veriyi buradan okuyoruz.
 */
let URUNLER_DATA = [];

// ── Sayfa Yüklenince ─────────────────────────────────────────────────────────
document.addEventListener("DOMContentLoaded", () => {
    // Ürün verisini script tag'inden parse et
    const dataEl = document.getElementById("urunler-data");
    if (dataEl) {
        try {
            URUNLER_DATA = JSON.parse(dataEl.textContent);
        } catch (e) {
            console.error("Ürün verisi parse edilemedi:", e);
        }
    }
    sepetiCiz();
});

// ── Sepete Ekleme ─────────────────────────────────────────────────────────────
/**
 * Ürünü sepete ekler; zaten varsa adedini artırır.
 * Stok limitini aşmaya izin vermez.
 * Ürün verisi URUNLER_DATA'dan lookup yapılır (HTML attribute çift-tırnak sorunu önlenir).
 *
 * @param {string} urunId - Firestore doküman id'si
 */
function urunEkle(urunId) {
    // Ürün verisini sunucudan gelen listeden bul
    const urun = URUNLER_DATA.find(u => u.id === urunId);
    if (!urun) {
        console.error("Ürün bulunamadı:", urunId);
        return;
    }

    const mevcutIndex = sepet.findIndex(s => s.urun_id === urunId);

    if (mevcutIndex !== -1) {
        const mevcut = sepet[mevcutIndex];
        if (mevcut.adet >= mevcut.stok) {
            alert(`⚠️ "${mevcut.urun_adi}" için maksimum stok adedi: ${mevcut.stok}`);
            return;
        }
        sepet[mevcutIndex].adet += 1;
    } else {
        sepet.push({
            urun_id:      urun.id,
            urun_adi:     urun.ad,
            kategori_id:  urun.kategori_id,
            satis_fiyati: urun.satis_fiyati,
            alis_fiyati:  urun.alis_fiyati,
            stok:         urun.stok_miktari,
            adet:         1,
        });
    }

    sepetiCiz();

    // Kısa görsel geri bildirim — buton rengi kısa süre değişir
    const btn = document.getElementById(`btn-ekle-${urunId}`);
    if (btn) {
        btn.textContent = "✓ Eklendi";
        btn.style.background = "#2ECC71";
        setTimeout(() => {
            btn.textContent = "+ Sepete Ekle";
            btn.style.background = "";
        }, 800);
    }
}

// ── Adet Güncelleme ───────────────────────────────────────────────────────────
/**
 * Sepetteki bir ürünün adetini günceller.
 * yeniAdet 0 ise satırı siler.
 * Stoktan fazla adet girilirse uyarı verir ve düzeltir.
 *
 * @param {string} urunId   - Ürün id'si
 * @param {number} delta    - +1 veya -1
 */
function adetGuncelle(urunId, delta) {
    const index = sepet.findIndex(s => s.urun_id === urunId);
    if (index === -1) return;

    const item = sepet[index];
    const yeniAdet = item.adet + delta;

    if (yeniAdet <= 0) {
        urunSil(urunId);
        return;
    }

    if (yeniAdet > item.stok) {
        alert(`⚠️ "${item.urun_adi}" için maksimum stok: ${item.stok} adet`);
        return;
    }

    sepet[index].adet = yeniAdet;
    sepetiCiz();
}

// ── Ürün Silme ────────────────────────────────────────────────────────────────
/**
 * Ürünü sepetten tamamen çıkarır.
 *
 * @param {string} urunId - Ürün id'si
 */
function urunSil(urunId) {
    sepet = sepet.filter(s => s.urun_id !== urunId);
    sepetiCiz();
}

// ── Sepet Temizleme ───────────────────────────────────────────────────────────
/**
 * Confirm sonrası tüm sepeti temizler.
 */
function sepetTemizle() {
    if (!confirm("Sepeti temizlemek istediğinize emin misiniz?")) return;
    sepet = [];
    sepetiCiz();
}

// ── Toplam Hesaplama ──────────────────────────────────────────────────────────
/**
 * Sepet toplamlarını hesaplar.
 *
 * @returns {{ toplam_tutar, toplam_kar, urun_sayisi, toplam_adet }}
 */
function toplamHesapla() {
    let toplam_tutar = 0;
    let toplam_kar   = 0;
    let toplam_adet  = 0;

    for (const item of sepet) {
        toplam_tutar += item.satis_fiyati * item.adet;
        toplam_kar   += (item.satis_fiyati - item.alis_fiyati) * item.adet;
        toplam_adet  += item.adet;
    }

    return {
        toplam_tutar: Math.round(toplam_tutar * 100) / 100,
        toplam_kar:   Math.round(toplam_kar   * 100) / 100,
        urun_sayisi:  sepet.length,
        toplam_adet,
    };
}

// ── Sepeti Çiz ────────────────────────────────────────────────────────────────
/**
 * Sağ paneli (sepet) yeniden render eder; toplamları günceller.
 */
function sepetiCiz() {
    const icerikEl    = document.getElementById("sepet-icerik");
    const bosEl       = document.getElementById("sepet-bos");
    const ozetEl      = document.getElementById("ozet-bar");
    const ozetKucukEl = document.getElementById("sepet-ozet-kucuk");
    const btnTamamla  = document.getElementById("btn-tamamla");

    if (!icerikEl) return;

    if (sepet.length === 0) {
        icerikEl.innerHTML   = "";
        bosEl.style.display  = "block";
        ozetEl.style.display = "none";
        if (ozetKucukEl) ozetKucukEl.textContent = "Boş";
        if (btnTamamla)  btnTamamla.disabled = true;
        return;
    }

    bosEl.style.display  = "none";
    ozetEl.style.display = "block";

    // Sepet satırları
    let html = "";
    for (const item of sepet) {
        const araTop = (item.satis_fiyati * item.adet).toFixed(2).replace(".", ",");
        const birim  = item.satis_fiyati.toFixed(2).replace(".", ",");

        html += `
        <div class="sepet-item" id="sepet-item-${item.urun_id}">
            <div class="sepet-item-ust">
                <p class="sepet-item-ad">${htmlKac(item.urun_adi)}</p>
                <button class="btn-sil-item"
                        onclick="urunSil('${item.urun_id}')"
                        aria-label="${htmlKac(item.urun_adi)} ürününü sil">🗑</button>
            </div>
            <p class="sepet-item-fiyat-kucuk">₺${birim} / adet</p>
            <div class="sepet-item-alt">
                <div class="adet-kontrol">
                    <button class="adet-btn"
                            onclick="adetGuncelle('${item.urun_id}', -1)"
                            aria-label="Azalt">−</button>
                    <span class="adet-gosterge">${item.adet}</span>
                    <button class="adet-btn"
                            onclick="adetGuncelle('${item.urun_id}', 1)"
                            aria-label="Artır">+</button>
                </div>
                <span class="sepet-item-ara-toplam">₺${araTop}</span>
            </div>
        </div>`;
    }
    icerikEl.innerHTML = html;

    // Toplamlar
    const { toplam_tutar, toplam_kar, urun_sayisi, toplam_adet } = toplamHesapla();

    document.getElementById("ozet-urun-sayisi").textContent    = urun_sayisi;
    document.getElementById("ozet-toplam-adet").textContent    = toplam_adet;
    document.getElementById("ozet-toplam-tutar").textContent   = "₺" + toplam_tutar.toFixed(2).replace(".", ",");
    document.getElementById("ozet-kar").textContent            = "₺" + toplam_kar.toFixed(2).replace(".", ",");

    if (ozetKucukEl) {
        ozetKucukEl.textContent = `${urun_sayisi} ürün, ${toplam_adet} adet`;
    }

    if (btnTamamla) btnTamamla.disabled = false;
}

// ── Kategori Filtreleme ───────────────────────────────────────────────────────
/**
 * Ürün kartlarını kategori id'sine göre göster/gizle.
 *
 * @param {string} kategoriId - Boş string = tümünü göster
 */
function kategoriyeFiltrele(kategoriId) {
    aktifKategori = kategoriId;

    // Pill butonlarını güncelle
    document.querySelectorAll(".kategori-pill").forEach(pill => {
        const pid = pill.getAttribute("data-kategori-id");
        pill.classList.toggle("active", pid === kategoriId);
    });

    kartlarıFiltrele();
}

// ── Ürün Arama ────────────────────────────────────────────────────────────────
/**
 * Ürün adına göre (data-ad attribute) kartları göster/gizle.
 *
 * @param {string} metin - Aranan metin
 */
function urunAra(metin) {
    aramaMetni = metin.toLowerCase()
        .replace("i\u0307", "i")  // Türkçe İ normalizasyonu
        .replace("I", "ı");
    kartlarıFiltrele();
}

/**
 * Hem kategori hem arama filtresini birlikte uygular.
 */
function kartlarıFiltrele() {
    const kartlar = document.querySelectorAll(".urun-card");
    let gorinenSayi = 0;

    kartlar.forEach(kart => {
        const kartKat  = kart.getAttribute("data-kategori") || "";
        const kartAd   = kart.getAttribute("data-ad") || "";

        const katEsles = aktifKategori === "" || kartKat === aktifKategori;
        const adEsles  = aramaMetni === "" || kartAd.includes(aramaMetni);

        if (katEsles && adEsles) {
            kart.classList.remove("gizli");
            gorinenSayi++;
        } else {
            kart.classList.add("gizli");
        }
    });

    // Sonuç yok mesajı
    const noResults = document.getElementById("no-results");
    if (noResults) noResults.style.display = gorinenSayi === 0 ? "block" : "none";

    // Sayaç
    const sayac = document.getElementById("urun-sayac");
    if (sayac) sayac.textContent = `${gorinenSayi} ürün mevcut`;
}

// ── Satışı Tamamla ────────────────────────────────────────────────────────────
/**
 * Sepeti JSON olarak /satis/tamamla endpoint'ine POST eder.
 * Başarılı olursa modal açar, hata olursa alert gösterir.
 * satis-transaction skill: transaction server-side çalışır.
 */
async function satisiTamamla() {
    if (sepet.length === 0) {
        alert("Sepet boş! Lütfen ürün ekleyin.");
        return;
    }

    const btnTamamla = document.getElementById("btn-tamamla");
    if (!btnTamamla) return;

    // Loading state
    btnTamamla.disabled    = true;
    btnTamamla.textContent = "⏳ Satış işleniyor...";

    const payload = {
        sepet: sepet.map(s => ({
            urun_id: s.urun_id,
            adet:    s.adet,
        }))
    };

    try {
        const response = await fetch("/satis/tamamla", {
            method:  "POST",
            headers: { "Content-Type": "application/json" },
            body:    JSON.stringify(payload),
        });

        const data = await response.json();

        if (data.success) {
            // Başarı modalını göster
            const tutar = parseFloat(data.toplam_tutar).toFixed(2).replace(".", ",");
            const kar   = parseFloat(data.toplam_kar).toFixed(2).replace(".", ",");

            document.getElementById("modal-tutar").textContent = `₺${tutar}`;
            document.getElementById("modal-kar").textContent   = `₺${kar}`;

            document.getElementById("basari-modal").style.display = "flex";
        } else {
            // Hata: sepeti koruyarak kullanıcıya mesaj ver
            alert(`❌ Hata: ${data.error}`);
            btnTamamla.disabled    = false;
            btnTamamla.textContent = "✓ SATIŞI TAMAMLA";
        }

    } catch (err) {
        alert("❌ Bağlantı hatası oluştu. Lütfen tekrar deneyin.");
        btnTamamla.disabled    = false;
        btnTamamla.textContent = "✓ SATIŞI TAMAMLA";
    }
}

// ── Yeni Satış ───────────────────────────────────────────────────────────────
/**
 * Modal'ı kapatır, sepeti sıfırlar ve sayfayı yeniler.
 */
function yeniSatis() {
    document.getElementById("basari-modal").style.display = "none";
    sepet = [];
    sepetiCiz();
    // Stok verileri değişmiş olabileceğinden sayfayı yenile
    window.location.reload();
}

// ── Yardımcı: HTML Escape ─────────────────────────────────────────────────────
/**
 * XSS koruması için özel HTML karakterlerini kaçırır.
 *
 * @param {string} str - Ham string
 * @returns {string} Güvenli string
 */
function htmlKac(str) {
    const div = document.createElement("div");
    div.appendChild(document.createTextNode(String(str)));
    return div.innerHTML;
}

// ── Modal dışına tıklayınca kapat ────────────────────────────────────────────
document.addEventListener("click", (e) => {
    const modal = document.getElementById("basari-modal");
    if (modal && e.target === modal) {
        yeniSatis();
    }
});
