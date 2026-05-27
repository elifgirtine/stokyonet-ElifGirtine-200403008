---
name: firestore-crud
description: Kullanıcı Firestore üzerinde bir koleksiyona veri ekleme, okuma, güncelleme veya silme (CRUD) işlemi yapacak Python kodu istediğinde bu yeteneği kullan. Örneğin "ürün ekleme fonksiyonu yaz", "kategorileri listele", "ürünü güncelle", "kullanıcıyı sil" gibi isteklerde devreye gir.
---

# Amaç
Firebase Firestore üzerinde standart, güvenli ve tekrar kullanılabilir CRUD fonksiyonları üretmek.

# Talimatlar
1. Her CRUD fonksiyonunu `try/except` bloğu içine al; `except Exception as e` ile genel hatayı yakala ve `flash()` ile kullanıcıya anlamlı Türkçe mesaj göster.
2. CREATE işlemlerinde otomatik olarak `olusturulma_tarihi` alanı ekle (`firestore.SERVER_TIMESTAMP` kullan).
3. UPDATE işlemlerinde otomatik olarak `guncelleme_tarihi` alanı ekle.
4. READ işlemlerinde dokümanın `.id` değerini de sonuçla birlikte döndür (Firestore default'ta vermez).
5. DELETE işlemleri öncesi kullanıcıdan onay alınması gerekiyorsa, frontend'de confirmation modal kullanılmasını öner.
6. Tüm fonksiyonlara docstring ekle: parametre, dönüş değeri ve örnek kullanım.
7. Şu standart yapıyı kullan:

```python
def urun_ekle(urun_data: dict) -> str:
    """
    Firestore'a yeni ürün ekler.
    
    Args:
        urun_data: {ad, kategori_id, alis_fiyati, satis_fiyati, stok_miktari, kritik_stok_seviyesi}
    
    Returns:
        Oluşturulan dokümanın id'si.
    """
    try:
        urun_data['olusturulma_tarihi'] = firestore.SERVER_TIMESTAMP
        doc_ref = db.collection('urunler').add(urun_data)
        return doc_ref[1].id
    except Exception as e:
        raise Exception(f"Ürün eklenemedi: {str(e)}")
```

8. Kritik: Stok güncelleyen UPDATE işlemleri için ayrı bir skill (satis-transaction) kullanılması gerektiğini hatırlat.