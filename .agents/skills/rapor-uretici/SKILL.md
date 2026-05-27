---
name: rapor-uretici
description: Kullanıcı raporlama, son 30 günlük gelir, kâr/zarar, en çok satan ürünler, dashboard istatistikleri veya istatistiksel özet ile ilgili kod istediğinde bu yeteneği kullan. Örneğin "30 günlük rapor çıkar", "dashboard verilerini hesapla", "en çok satan 5 ürünü bul" gibi isteklerde devreye gir.
---

# Amaç
Firestore satış verilerini analiz ederek dashboard ve raporlar sayfası için anlamlı, hesaplanmış istatistikler üretmek.

# Talimatlar
1. Tarih filtreleme için her zaman `datetime.now() - timedelta(days=30)` kullan ve Firestore `.where('tarih', '>=', otuz_gun_once)` ile sorgula.
2. Standart rapor çıktısı şu JSON yapısında olmalı:
```python
{
    "toplam_satis_tutari": 0.0,
    "toplam_kar": 0.0,
    "satis_adedi": 0,
    "en_cok_satan_urunler": [{"ad": "...", "adet": N, "tutar": 0.0}, ...],
    "kritik_stoktaki_urunler": [{"ad": "...", "stok": N, "kritik": N}, ...],
    "gunluk_satis_grafigi": [{"tarih": "2026-05-01", "tutar": 0.0}, ...]
}
```
3. Tüm para tutarlarını 2 ondalık basamağa yuvarla (`round(x, 2)`).
4. En çok satan ürünleri bulurken `satis_detaylari` koleksiyonunu tara, `urun_id` bazında `adet` topla ve büyükten küçüğe sırala.
5. Kritik stok için: `urunler` koleksiyonunda `stok_miktari <= kritik_stok_seviyesi` olan ürünleri bul.
6. Hiç veri yoksa 0 veya boş liste dön; ASLA `None` dönme (frontend bozulur).
7. Grafik için günlük gruplama yaparken eksik günleri 0 ile doldur (frontend grafiği boşluksuz çiziyor olsun).
8. Rapor fonksiyonu hesaplama yoğun olduğu için sonucu istersen Flask session'a 5 dakika cache'leyebilirsin; ama bunu yapmadan önce kullanıcıya öner.
9. Tüm dönüş değerlerinin tipi Python'da net olsun: `float` parasal, `int` sayım, `str` metin, `list` koleksiyon.