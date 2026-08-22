# Changelog / Sürüm Geçmişi

All notable changes to this project will be documented in this file.
This project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [1.2.0] - 2026-08-22 (Çoklu Standart Et Kalınlığı, Paslanmaz Çelik, 40+ Parametre & Tablo Ergonomisi)

### 🎉 Eklenen Özellikler (Added)
- **Çoklu Standart Et Kalınlığı Hesaplama:** BOTAŞ (Hat/İstasyon + %12.5 Mill Tol.), ASME B31.8 / B31.4 ve ASME B31.3 Proses Borulaması kriterleri desteği.
- **Paslanmaz ve Dubleks Malzemeler:** SS 304/304L, SS 316/316L, SS 321, Duplex 2205, Super Duplex 2507 kaliteleri ve ASME B36.19M paslanmaz schedule tablosu.
- **40+ Parametreli Kapsamlı Kabul & Doğrulama Motoru:** Kimyasal, boyutsal, mekanik, kaynak, tokluk ve ağırlık/hidro testlerinin standartlara göre tam otomatik değerlendirilmesi.
- **Tablo Okunabilirlik ve Crosshair Odaklanması:** Seçili sütun kontrast iyileştirmesi, fareyle gezinilen satır ile aktif sütunun kesiştiği hücreye anlık aydınlatma.
- **Klavye Yön Tuşları ile Sütun Gezintisi:** Sol/Sağ ok tuşları ve araç çubuğu butonları ile sütunlar arasında hızlı geçiş.
- **Bilingual (TR/EN) Excel Çıktısı:** 40+ parametre ve açıklama satırının Türkçe ve İngilizce standart referanslarıyla doldurulması.
- **2 Ondalık Basamak Yuvarlama Standardı:** Arayüz ve raporlamalarda tüm değerlerin 2 basamağa yuvarlanması.

### 🛠️ Düzeltmeler (Fixed)
- P0-1: Bilinmeyen boru çaplarında oluşan NameError güvenli hale getirildi.
- P1-1: İşletme basıncı eşleşmesinde tasarım faktörüne bağlı dinamik varsayılan atama ve kullanıcı değer önceliği düzeltildi.
- P1-5: İstasyon borularında mill toleransının nominal schedule seçiminde standartlaştırılması.

---

## [1.1.0] - 2026-08-21 (Kapsamlı Ergonomi, 3D Senkronizasyon & Otomatik Güncelleyici)
- Açılışta GitHub Releases üzerinden otomatik güncelleme denetimi.
- Çoklu boru 2D & 3D senkronizasyonu ve 3D PNG snapshot alma.
- Yönetici KPI özet performans kartları.
- Donuk başlıklar ve katlanabilir akordeon parametre matrisi.
- Telif Hakkı & Sorumluluk Reddi (Disclaimer) entegrasyonu.

---

## [1.0.3] - 2026-08-21
- PyInstaller freeze support ve doğrudan ASGI nesnesiyle çalıştırma düzeltmesi.
- BOTAŞ otomatik doldurma entegrasyonu.

---

## [1.0.0] - 2026-08-21
- İlk kararlı sürüm (Initial Release).
