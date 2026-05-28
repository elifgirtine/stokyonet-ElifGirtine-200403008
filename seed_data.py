"""
Firestore Başlangıç Verisi (Seed) Scripti
-----------------------------------------
Koleksiyonlara varsayılan verileri ekler.
Mevcut veriler tekrar eklenmez (idempotent).

Kullanım:
    source venv/bin/activate
    python seed_data.py
"""

import bcrypt
from google.cloud.firestore import SERVER_TIMESTAMP
from firebase_config import get_db

# ─────────────────────────────────────────────
# Yardımcı Fonksiyonlar
# ─────────────────────────────────────────────

def ekle_yoksa(koleksiyon_ref, filtre_alan, filtre_deger, veri):
    """
    Koleksiyonda aynı alana sahip doküman yoksa ekler.
    İdempotent çalışır: mevcut kayıt varsa ekleme yapmaz.

    Returns:
        tuple: (bool eklendi_mi, str doc_id)
    """
    mevcut = list(koleksiyon_ref.where(filtre_alan, "==", filtre_deger).limit(1).get())
    if mevcut:
        return False, mevcut[0].id
    ref = koleksiyon_ref.add(veri)
    return True, ref[1].id


def rapor_satiri(koleksiyon, eklenen, atlanan, toplam):
    """Raporlama için tek satır formatı."""
    return {
        "koleksiyon": koleksiyon,
        "eklenen": eklenen,
        "atlanan": atlanan,
        "toplam": toplam
    }


# ─────────────────────────────────────────────
# Seed Fonksiyonları
# ─────────────────────────────────────────────

def seed_kullanicilar(db):
    """Admin kullanıcısını kullanicilar koleksiyonuna ekler."""
    koleksiyon = db.collection("kullanicilar")
    eklenen = 0
    atlanan = 0

    # Şifre bcrypt ile hashlenir
    sifre_hash = bcrypt.hashpw(
        "Admin123!".encode("utf-8"),
        bcrypt.gensalt()
    ).decode("utf-8")

    basarili, doc_id = ekle_yoksa(
        koleksiyon,
        "kullanici_adi", "admin",
        {
            "kullanici_adi": "admin",
            "sifre_hash": sifre_hash,
            "ad_soyad": "Sistem Yöneticisi",
            "rol": "admin",
            "aktif": True,
            "olusturulma_tarihi": SERVER_TIMESTAMP
        }
    )

    if basarili:
        eklenen += 1
        print(f"  ✔ Admin kullanıcısı eklendi (id: {doc_id})")
    else:
        atlanan += 1
        print(f"  • Admin kullanıcısı zaten mevcut, atlandı.")

    toplam = list(koleksiyon.get())
    return rapor_satiri("kullanicilar", eklenen, atlanan, len(toplam))


def seed_kategoriler(db):
    """5 örnek kategoriyi kategoriler koleksiyonuna ekler."""
    koleksiyon = db.collection("kategoriler")
    eklenen = 0
    atlanan = 0

    kategoriler = [
        "İçecekler",
        "Atıştırmalıklar",
        "Temizlik Ürünleri",
        "Kırtasiye",
        "Kişisel Bakım",
    ]

    for kat_adi in kategoriler:
        basarili, doc_id = ekle_yoksa(
            koleksiyon,
            "ad", kat_adi,
            {
                "ad": kat_adi,
                "aktif": True,
                "olusturulma_tarihi": SERVER_TIMESTAMP
            }
        )
        if basarili:
            eklenen += 1
            print(f"  ✔ Kategori eklendi: {kat_adi}")
        else:
            atlanan += 1
            print(f"  • Kategori zaten mevcut, atlandı: {kat_adi}")

    toplam = list(koleksiyon.get())
    return rapor_satiri("kategoriler", eklenen, atlanan, len(toplam))


def seed_urunler(db):
    """8 örnek ürünü kategori ID'leriyle eşleştirerek urunler koleksiyonuna ekler."""
    koleksiyon = db.collection("urunler")
    kategoriler_ref = db.collection("kategoriler")
    eklenen = 0
    atlanan = 0

    # Kategori adına göre ID haritası oluştur
    kat_docs = list(kategoriler_ref.get())
    kat_map = {d.to_dict().get("ad", ""): d.id for d in kat_docs}

    # Ürün tanımları — kategori adı daha sonra ID'ye çevrilecek
    urun_listesi = [
        {
            "ad": "Su 0.5L",
            "kategori_adi": "İçecekler",
            "alis_fiyati": 5.00,
            "satis_fiyati": 8.00,
            "stok_miktari": 50,
            "kritik_stok_seviyesi": 10,
        },
        {
            "ad": "Kola 1L",
            "kategori_adi": "İçecekler",
            "alis_fiyati": 18.00,
            "satis_fiyati": 30.00,
            "stok_miktari": 25,
            "kritik_stok_seviyesi": 5,
        },
        {
            "ad": "Cips Büyük",
            "kategori_adi": "Atıştırmalıklar",
            "alis_fiyati": 22.00,
            "satis_fiyati": 35.00,
            "stok_miktari": 30,
            "kritik_stok_seviyesi": 8,
        },
        {
            "ad": "Çikolata Bar",
            "kategori_adi": "Atıştırmalıklar",
            "alis_fiyati": 8.00,
            "satis_fiyati": 15.00,
            "stok_miktari": 3,
            "kritik_stok_seviyesi": 10,
        },
        {
            "ad": "Çamaşır Suyu",
            "kategori_adi": "Temizlik Ürünleri",
            "alis_fiyati": 35.00,
            "satis_fiyati": 55.00,
            "stok_miktari": 12,
            "kritik_stok_seviyesi": 5,
        },
        {
            "ad": "Defter A4",
            "kategori_adi": "Kırtasiye",
            "alis_fiyati": 20.00,
            "satis_fiyati": 35.00,
            "stok_miktari": 40,
            "kritik_stok_seviyesi": 10,
        },
        {
            "ad": "Tükenmez Kalem",
            "kategori_adi": "Kırtasiye",
            "alis_fiyati": 4.00,
            "satis_fiyati": 8.00,
            "stok_miktari": 2,
            "kritik_stok_seviyesi": 15,
        },
        {
            "ad": "Diş Macunu",
            "kategori_adi": "Kişisel Bakım",
            "alis_fiyati": 25.00,
            "satis_fiyati": 40.00,
            "stok_miktari": 18,
            "kritik_stok_seviyesi": 5,
        },
    ]

    for urun in urun_listesi:
        kategori_id = kat_map.get(urun["kategori_adi"], "")
        if not kategori_id:
            print(f"  ✘ Kategori bulunamadı, atlandı: {urun['kategori_adi']}")
            atlanan += 1
            continue

        basarili, doc_id = ekle_yoksa(
            koleksiyon,
            "ad", urun["ad"],
            {
                "ad": urun["ad"],
                "kategori_id": kategori_id,
                "alis_fiyati": round(urun["alis_fiyati"], 2),
                "satis_fiyati": round(urun["satis_fiyati"], 2),
                "stok_miktari": urun["stok_miktari"],
                "kritik_stok_seviyesi": urun["kritik_stok_seviyesi"],
                "aktif": True,
                "olusturulma_tarihi": SERVER_TIMESTAMP
            }
        )

        if basarili:
            eklenen += 1
            stok_uyari = " ⚠ KRİTİK STOK" if urun["stok_miktari"] <= urun["kritik_stok_seviyesi"] else ""
            print(f"  ✔ Ürün eklendi: {urun['ad']}{stok_uyari}")
        else:
            atlanan += 1
            print(f"  • Ürün zaten mevcut, atlandı: {urun['ad']}")

    toplam = list(koleksiyon.get())
    return rapor_satiri("urunler", eklenen, atlanan, len(toplam))


# ─────────────────────────────────────────────
# Ana Akış
# ─────────────────────────────────────────────

def main():
    """Seed scriptinin ana giriş noktası."""
    print("\n" + "═" * 55)
    print("  FIRESTORE SEED BAŞLIYOR")
    print("═" * 55)

    try:
        db = get_db()
        print("  Firebase bağlantısı: ✔\n")
    except RuntimeError as e:
        print(f"  ✘ Firebase bağlantısı kurulamadı: {e}")
        return

    sonuclar = []

    print("▶ kullanicilar")
    sonuclar.append(seed_kullanicilar(db))

    print("\n▶ kategoriler")
    sonuclar.append(seed_kategoriler(db))

    print("\n▶ urunler")
    sonuclar.append(seed_urunler(db))

    # ─── Özet Tablo ───────────────────────────────────────────
    print("\n" + "═" * 55)
    print("  SEED ÖZET RAPORU")
    print("═" * 55)
    print(f"  {'Koleksiyon':<22} {'Eklenen':>7} {'Atlanan':>8} {'Toplam':>7}")
    print("  " + "─" * 48)
    for r in sonuclar:
        print(
            f"  {r['koleksiyon']:<22} "
            f"{r['eklenen']:>7} "
            f"{r['atlanan']:>8} "
            f"{r['toplam']:>7}"
        )
    print("═" * 55)
    print("  Seed işlemi tamamlandı.\n")


if __name__ == "__main__":
    main()
