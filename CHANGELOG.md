# Changelog / Sürüm Geçmişi

All notable changes to this project will be documented in this file.
This project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [1.1.0] - 2026-08-21 (Kapsamlı Ergonomi, 3D Senkronizasyon & Otomatik Güncelleyici)

### 🎉 Eklenen Özellikler (Added)
- **Açılışta Otomatik Güncelleme Denetimi:** GitHub Releases API üzerinden yeni sürümleri algılayıp doğrudan indirme bağlantıları sunan bildirim şeridi ve manuel güncelleme butonu.
- **Çoklu Boru 2D & 3D Senkronizasyonu:** Tablo sütun başlığından tıklanarak aktif boru odaklaması ve 2D/3D modelin eşzamanlı güncellenmesi.
- **2D/3D Yatay Boru Seçim Çipleri:** Görselleştirme ekranında sekmeler arası geçiş yapmadan tek tıkla borular arası gezinme.
- **3D PNG Snapshot Dışa Aktarma:** Three.js WebGL tuvalinden şeffaf arka planlı yüksek çözünürlüklü teknik PNG indirme.
- **Yönetici KPI Özet Kartları:** Matrisin en üstünde seçili borunun hidrostatik basıncı, ağırlığı, $D/t$ oranı ve kırılma emniyeti özetleri.
- **Donuk Başlıklar (Sticky Table) & Katlanabilir Akordeon:** 6 kategoriye ayrılmış katlanabilir parametre blokları ve donuk üst/sol/sağ sütunlar.
- **Canlı Parametre Arama:** Matris tablosunda anlık parametre ve standart filtreleme.
- **Telif Hakkı & Sorumluluk Reddi (Disclaimer):** Alt bilgi (Footer), Hakkında modalı, Excel çıktısı ve resmi rapor şablonuna kapsamlı yasal uyarılar.
- **Geriye Dönük Şema Göçü (Backward Compatibility):** Eski versiyonlarda kaydedilmiş `.pipeproj` dosyalarını otomatik uyarlama.

---

## [1.0.3] - 2026-08-21
- PyInstaller freeze support ve doğrudan ASGI nesnesiyle çalıştırma düzeltmesi.
- BOTAŞ otomatik doldurma entegrasyonu.
- Sağ açıklama sütunu sabitlemesi.

---

## [1.0.0] - 2026-08-21
- İlk kararlı sürüm (Initial Release).
