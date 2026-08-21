# Changelog / Sürüm Geçmişi

All notable changes to this project will be documented in this file.
This project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [1.0.3] - 2026-08-21

### 🛠️ Düzeltmeler ve İyileştirmeler (Fixed & Improved)
- **Arayüz Versiyon Senkronizasyonu:** Arayüz başlığındaki versiyon rozeti dinamik `v1.0.3` olarak güncellendi.
- **PyInstaller Binary Başlatma Düzeltmesi:** Uvicorn `app:app` string modülü yerine doğrudan ASGI nesnesiyle başlatılarak `.exe` ve `.app` paketlerinin açılış çökmesi giderildi.
- **Multiprocessing Freeze & Stdout Güvenliği:** `multiprocessing.freeze_support()` ve `DummyWriter` eklenerek Windows ve macOS GUI modunda kararlı çalışma sağlandı.
- **BOTAŞ Otomatik Doldurma:** Çap seçildiğinde tüm dizayn faktörlerindeki BOTAŞ borularının tek tıkla matrise eklenmesi tamamlandı.
- **Sağ Açıklamalar Sütunu:** Mühendislik açıklamaları ve standart referansları en sağ sütuna sabitlendi.

---

## [1.0.0] - 2026-08-21

### 🎉 İlk Kararlı Sürüm (Initial Release)
- API 5L PSL2 ve BOTAŞ şartnamelerine göre 40+ parametrenin otomatik hesaplanması.
- 3D WebGL (Three.js) ve 2D SVG boru görselleştiricisi.
- PASS / FAIL fabrika kabul test doğrulama modülü.
- ASME B31.8 & ASME B36.10 et kalınlığı tasarım aracı.
- Excel (.xlsx) profesyonel dışa aktarım ve EN 10204 3.1 rapor şablonu.
