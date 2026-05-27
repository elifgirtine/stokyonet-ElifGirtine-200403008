---
name: satis-transaction
description: Kullanıcı satış işlemi, sepet onayı, satış kaydetme veya stok düşürme ile ilgili bir kod istediğinde bu yeteneği kullan. Örneğin "satışı kaydet", "sepeti onayla", "satış endpointi yaz" gibi isteklerde devreye gir. Bu yetenek satışın atomik olmasını garanti eder.
---

# Amaç
Satış işlemini Firestore transaction içinde yaparak veri tutarlılığını sağlamak. Yetersiz stok kontrolü, satış kaydı oluşturma, satış detaylarını yazma ve ürün stoklarını düşürme işlemlerini tek bir atomik birim halinde gerçekleştirmek.

# Talimatlar
1. Her satış işlemi `@firestore.transactional` decoratorı ile sarmalı.
2. Transaction içinde önce TÜM ürünlerin mevcut stoğunu OKU.
3. Sonra TÜM ürünlerin yeterli stoğu olup olmadığını KONTROL ET. Yetersizse `ValueError` fırlat ve mesajda hangi ürünün eksik olduğunu belirt.
4. Yeterli stok varsa şu sırayla yaz:
   - `satislar` koleksiyonuna toplam tutar, kullanıcı, tarih ile ana kayıt oluştur.
   - `satis_detaylari` koleksiyonuna her ürün için satır (urun_id, adet, birim_fiyat, satis_id) ekle.
   - `urunler` koleksiyonunda her ürünün `stok_miktari` alanını düşür.
5. Kâr hesabı: `(satis_fiyati - alis_fiyati) * adet` formülünü kullan; bu bilgiyi `satis_detaylari`'na `kar_tutari` olarak ekle.
6. Tarih alanı her zaman `firestore.SERVER_TIMESTAMP` olsun (sunucu saatine güvenmek için).
7. Frontend'e dönerken satış başarılıysa satış id'sini ve toplam tutarı dön; başarısızsa anlamlı Türkçe hata mesajı dön.
8. Şu iskeleti kullan:

```python
@firestore.transactional
def satis_yap(transaction, sepet: list, kullanici_id: str):
    """
    Sepetteki ürünleri atomik olarak satışa dönüştürür.
    sepet = [{'urun_id': 'xxx', 'adet': 2}, ...]
    """
    # 1) Tüm ürünleri OKU
    urun_refs = [db.collection('urunler').document(item['urun_id']) for item in sepet]
    urun_snapshots = [ref.get(transaction=transaction) for ref in urun_refs]
    
    # 2) Stok kontrol
    for i, snap in enumerate(urun_snapshots):
        if snap.to_dict()['stok_miktari'] < sepet[i]['adet']:
            raise ValueError(f"'{snap.to_dict()['ad']}' için yetersiz stok!")
    
    # 3) Toplam hesapla, satışı yaz, detayları yaz, stokları düş
    # ... (devamını yaz)
```

9. Bu fonksiyonu çağıran route mutlaka `try/except ValueError` ile sarmalanmalı ve kullanıcıya `flash()` ile uyarı vermeli.