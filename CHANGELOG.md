# Changelog / Sürüm Geçmişi

All notable changes to this project will be documented in this file.
This project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [1.0.0] - 2026-08-21 (İlk Kararlı Sürüm - Initial Release)

### 🎉 Eklenen Özellikler (Added)
- **Boru Kalite Güvence & Kabul Matrisi (QA/QC Matrix):**
  - API 5L PSL2 ve BOTAŞ şartnamelerine göre 40+ parametrenin otomatik hesaplanması.
  - Sınırsız sayıda boru sütunu ekleme, klonlama ve silme desteği.
  - Kesirli anma çapları (`1/2"`, `¾"`, `1¼"`, `1½"`, `2½"`, `3½"`) ve büyük çaplar (`14"` - `60"`) için NPS $\leftrightarrow$ OD (mm) tam entegrasyonu.
- **BOTAŞ / API 5L Dinamik Değerlendirme Modları:**
  - **BOTAŞ Modu:** Çap ve tasarım faktörü seçildiğinde malzeme kalitesi ve et kalınlığının BOTAŞ standart tablolarından otomatik çekilmesi ve şartname uygunluk kontrolü (`is_botas_compliant`).
  - **API 5L Modu:** Çap, malzeme ve et kalınlığının serbest seçimi ve API 5L PSL2 uluslararası formülleriyle değerlendirilmesi.
- **Satır Yanı Mühendislik Açıklamaları (Engineering Remarks):**
  - Matris tablosundaki her satırın yanında ilgili standardın maddesi (örn. *ASME B31.8 Madde 841.1.1, API 5L Madde 9.3.2, BOTAŞ Madde 4.2*) ve formül açıklaması.
- **3D İnteraktif WebGL Boru Modeli (Three.js):**
  - 360° serbest döndürme, yakınlaştırma ve dinamik kesit alma (cutaway).
  - SAWH borular için gövde boyunca gerçekçi 3D spiral kaynak dikişi, ERW borular için boyuna dikiş.
- **2D Vektörel Kesit Çizimi (SVG):**
  - Dış çap ($D$), iç çap ($d$), et kalınlığı ($t$) ve imalat tolerans bantlarının ölçekli teknik çizimi.
- **Fabrika Test Doğrulama (PASS / FAIL Analizi):**
  - Sahadan veya laboratuvardan gelen gerçek test verilerinin standart sınırlarına göre otomatik denetimi.
- **Boru Et Kalınlığı Tasarım Aracı (Bonus Module):**
  - ASME B31.8 Barlow formülü ve ASME B36.10 standart Schedule et kalınlığı seçimi.
- **Çoklu Dil Desteği:**
  - Türkçe ve İngilizce (TR / EN) anlık dinamik dil geçişi.
- **Proje, Revizyon ve Şablon Yönetimi:**
  - `.pipeproj` (JSON) proje dosyası kaydetme/yükleme.
  - 48" + 18" Referans Şablonu, 10 Çeşit BOTAŞ Şablonu ve 10 Çeşit API 5L Şablonu.
- **Raporlama & Dışa Aktarma:**
  - Excel (.xlsx) profesyonel formatlı dışa aktarma (OpenPyXL).
  - EN 10204 3.1 uyumlu resmi yazdırılabilir FAT sertifikası / PDF şablonu.
- **Çapraz Platform Başlatıcılar:**
  - Windows için `run.bat`.
  - macOS (Apple Silicon M1/M2/M3/M4 & Intel) ve Linux için `run.sh`.
