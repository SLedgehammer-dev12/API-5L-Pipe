# API 5L PSL2 & BOTAŞ Pipe QA/QC & Wall Thickness Design Suite
### Boru Kalite Güvence, Fabrika Kabul (FAT) ve Et Kalınlığı Tasarım Yazılımı

[![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.110%2B-009688.svg)](https://fastapi.tiangolo.com)
[![Three.js](https://img.shields.io/badge/Three.js-r128-black.svg)](https://threejs.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20macOS%20(Apple%20Silicon%20%26%20Intel)%20%7C%20Linux-lightgrey.svg)]()

---

## 📖 Genel Bakış / Overview

**API 5L PSL2 & BOTAŞ Boru Kalite Güvence ve Tasarım Yazılımı**, doğal gaz ve petrol boru hatlarında kullanılan çelik hat borularının **API 5L PSL2 standardı** ve **BOTAŞ teknik şartnamelerine** göre fabrika test ve kabul parametrelerini otomatik olarak denetleyen, karşılaştıran ve raporlayan modern bir mühendislik platformudur.

Hem **Windows** ortamında hem de **Apple Silicon (M1/M2/M3/M4) / Intel macOS** ve Linux işletim sistemlerinde tek tıkla çalıştırılabilir.

---

## ✨ Temel Özellikler / Key Features

- 📊 **Boru Kalite Güvence & Kabul Matrisi:**
  - Sınırsız boru sütunu ekleme, klonlama ve karşılaştırma.
  - 40'tan fazla parametrenin eşzamanlı hesabı: Barlow formülü hidrostatik basınç, artık gerilme halka testi ($\Delta$), minimum uzama ($e = 1940 \frac{A^{0.2}}{U^{0.9}}$), radyal kaçıklık, kaynak yüksekliği, misalignment, DWTT ($D \ge 508\text{ mm}$), mandrel çapı/çene açıklığı, ağırlıklar, $D/t$ ve ASME B31.8 841.1.2 kırılma kontrolü (API 5L Annex G).
- 🏷️ **Satır Yanı Mühendislik Açıklamaları (Engineering Remarks):**
  - Matris tablosundaki her satırın yanında standardın ilgili maddesi ve formül açıklaması.
- ⚙️ **BOTAŞ / API 5L Dinamik Değerlendirme Modları:**
  - **BOTAŞ Modu:** Çap ve faktör seçildiğinde malzeme kalitesi ve et kalınlığı BOTAŞ şartname tablolarından otomatik çekilir ve BOTAŞ et kalınlığı şartına uygunluk denetlenir.
  - **API 5L Modu:** Çap, malzeme ve et kalınlığı serbestçe seçilebilir ve uluslararası API 5L PSL2 / ASME B31.8 standartlarına göre hesaplanır.
- 🎮 **3D İnteraktif WebGL & 2D Şematik Model:**
  - Three.js tabanlı 360° serbest döndürülebilen, yakınlaştırılabilen 3D boru gövdesi ve SAWH borular için gövde boyunca dönen **3D Helisel/Spiral Kaynak Dikişi** (ERW için boyuna dikiş).
  - SVG tabanlı 2D teknik enkesit ve tolerans bantları.
- 🛡️ **Fabrika Test Doğrulama (PASS / FAIL Analizi):**
  - Sahadan veya laboratuvardan gelen gerçek ölçüm değerlerinin tek tıkla standart sınırlarına göre denetimi ve kabul/ret rozetleri üretimi.
- 📐 **Boru Et Kalınlığı Tasarım Aracı (Bonus Module):**
  - ASME B31.8 Barlow formülü ve ASME B36.10 standart Schedule serisi seçimi.
- 🌍 **Çoklu Dil Desteği (TR / EN):**
  - Türkçe ve İngilizce anlık dinamik dil geçişi.
- 📁 **Proje & Revizyon Yönetimi:**
  - `.pipeproj` (JSON) proje dosyası kaydetme/yükleme.
  - 48" + 18" Referans Şablonu, 10 Çeşit BOTAŞ Şablonu ve 10 Çeşit API 5L Şablonu.
- 📑 **Raporlama:**
  - Excel (.xlsx) profesyonel formatlı dışa aktarım (OpenPyXL).
  - Resmi EN 10204 3.1 uyumlu yazdırılabilir kabul raporu / PDF.

---

## 🚀 Kurulum ve Çalıştırma / Installation & Usage

### 🪟 Windows:
1. Projeyi indirin / klonlayın.
2. `run.bat` dosyasına çift tıklayın (gerekli paketleri otomatik kurar ve tarayıcınızı açar).

### 🍏 macOS (Apple Silicon M1/M2/M3/M4 & Intel) / 🐧 Linux:
Terminali açın ve projenin bulunduğu dizinde çalıştırın:
```bash
./run.sh
# veya
python3 run.py
```

Tarayıcınızda otomatik olarak **`http://127.0.0.1:8000`** adresi açılacaktır.

---

## 🧪 Otomatik Testleri Çalıştırma / Running Tests

Uygulama 10 BOTAŞ ve 10 API 5L borusunu, sınır şartlarını ve formülleri kapsayan otomatik bir test paketine sahiptir:

```bash
python3 -m unittest tests/test_pipe_suite.py -v
```

---

## 📁 Proje Dizin Yapısı / Project Structure

```
API 5L Pipe/
├── run.bat                     # Windows tek tıkla başlatıcı
├── run.sh                      # macOS / Linux başlatıcı
├── run.py                      # Platform bağımsız Python başlatıcı
├── version.py                  # Versiyon bilgisi (v1.0.0)
├── app.py                      # FastAPI ana uygulaması
├── requirements.txt            # Python bağımlılıkları
├── core/
│   ├── database.py             # API 5L, BOTAŞ, ASME B36.10 standart matrisleri
│   ├── pipe_qaqc_engine.py     # Boru QA/QC ve kabul kriterleri motoru
│   ├── verification_engine.py  # Gerçek test verileri PASS / FAIL motoru
│   ├── wall_thickness_engine.py# ASME B31.8 & BOTAŞ Et Kalınlığı Tasarım Motoru
│   ├── excel_exporter.py       # Excel (.xlsx) rapor üretici
│   ├── i18n.py                 # TR / EN çoklu dil motoru
│   └── project_manager.py      # Proje kaydetme, şablonlar ve revizyon yöneticisi
├── static/
│   ├── css/style.css           # Tasarım stilleri
│   ├── js/
│   │   ├── app.js              # Ana frontend mantığı
│   │   ├── i18n.js             # Çoklu dil istemcisi
│   │   ├── pipe_visualizer_2d.js # 2D SVG enkesit
│   │   ├── pipe_visualizer_3d.js # 3D Three.js WebGL boru & spiral kaynak modeli
│   │   └── project_storage.js  # JSON proje dosyası saklama
├── templates/
│   ├── index.html              # Ana dashboard arayüzü
│   └── report_template.html    # Resmi yazdırılabilir FAT sertifikası
└── tests/
    └── test_pipe_suite.py      # 10 BOTAŞ + 10 API 5L kapsamlı test paketi
```

---

## 📄 Lisans / License

Bu proje [MIT Lisansı](LICENSE) altında lisanslanmıştır.
