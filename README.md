# API 5L PSL2 & BOTAŞ Pipe QA/QC & Wall Thickness Design Suite
### Boru Kalite Güvence, Fabrika Kabul (FAT) ve Et Kalınlığı Tasarım Yazılımı

[![Build and Release Multi-Platform Packages](https://github.com/SLedgehammer-dev12/API-5L-Pipe/actions/workflows/build_and_release.yml/badge.svg)](https://github.com/SLedgehammer-dev12/API-5L-Pipe/actions/workflows/build_and_release.yml)
[![GitHub release (latest by date)](https://img.shields.io/github/v/release/SLedgehammer-dev12/API-5L-Pipe)](https://github.com/SLedgehammer-dev12/API-5L-Pipe/releases/latest)
[![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.110%2B-009688.svg)](https://fastapi.tiangolo.com)
[![Three.js](https://img.shields.io/badge/Three.js-r128-black.svg)](https://threejs.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

---

## 📖 Genel Bakış / Overview

**API 5L PSL2 & BOTAŞ Boru Kalite Güvence ve Tasarım Yazılımı**, doğal gaz ve petrol iletim şebekelerinde kullanılan çelik boruların **API 5L PSL2 standardı** ve **BOTAŞ teknik şartnamelerine** göre fabrika kabul ve kalite güvence (QA/QC) denetimlerini gerçekleştiren, boyut ve kaynak toleranslarını denetleyen ve mühendislik raporları üreten kapsamlı bir platformdur.

---

## ✨ Temel Özellikler / Key Features

- 📊 **Boru Kalite Güvence & Kabul Matrisi:**
  - 40'tan fazla parametrenin eşzamanlı hesabı (Hidrostatik basınç, artık gerilme halka testi $\Delta$, minimum uzama $e = 1940 \frac{A^{0.2}}{U^{0.9}}$, radyal kaçıklık, kaynak yüksekliği, misalignment, DWTT yırtılma, mandrel çapı/çene açıklığı, ağırlıklar, $D/t$ ve ASME B31.8 841.1.2 kırılma kontrolü).
  - **Açıklamalar Sütunu (Her Zaman En Sağda):** Her satırın yanında ilgili standardın maddesi (örn. *ASME B31.8 Madde 841.1.1, API 5L Madde 9.3.2, BOTAŞ Madde 4.2*) ve formül açıklaması.
- ⚡ **BOTAŞ Otomatik Doldurma (Auto-Populate All Design Factors):**
  - BOTAŞ Şartnamesi seçildiğinde kullanıcı **SADECE ÇAP** seçer; o çapa ait tüm dizayn faktörlerindeki borular ($F=0.72\text{ Hat}$, $F=0.60\text{ Hat}$, $F=0.50\text{ Hat}$, $F=0.50\text{ İstasyon 1/2}$) tek tıkla matrise ayrı sütunlar olarak eklenir.
- ⚙️ **API 5L Serbest Seçim Modu:**
  - Kullanıcı çap, et kalınlığı, malzeme kalitesi ve imalat yöntemini serbestçe seçer ve uluslararası API 5L PSL2 standartlarına göre hesaplar.
- 🎮 **3D İnteraktif WebGL & 2D Şematik Model:**
  - Three.js tabanlı 360° serbest döndürülebilen, yakınlaştırılabilen 3D boru gövdesi ve SAWH borular için gövde boyunca dönen **3D Helisel/Spiral Kaynak Dikişi** (ERW için boyuna dikiş).
  - SVG tabanlı 2D teknik enkesit ve tolerans bantları.
- 🛡️ **Fabrika Test Doğrulama (PASS / FAIL Analizi):**
  - Sahadan gelen gerçek ölçüm değerlerinin tek tıkla standart sınırlarına göre denetimi ve kabul/ret rozetleri.
- 📐 **Boru Et Kalınlığı Tasarım Aracı (ASME B31.8 & ASME B36.10):**
  - Barlow formülü ve standart Schedule serisi seçimi.
- 📑 **Raporlama:**
  - Excel (.xlsx) profesyonel formatlı dışa aktarım (OpenPyXL).
  - Resmi EN 10204 3.1 uyumlu yazdırılabilir kabul raporu / PDF.

---

## 📦 İndirme ve Kurulum / Download & Installation

### 1. Hazır Paketler (Releases)
Son kararlı sürümleri [GitHub Releases](https://github.com/SLedgehammer-dev12/API-5L-Pipe/releases/latest) sayfasından indirebilirsiniz:
- **🪟 Windows:** `API-5L-Pipe-Windows-x64.exe` (Tek dosya, kurulumsuz çalışır)
- **🍏 macOS:** `API-5L-Pipe-macOS.dmg` (Apple Silicon M1/M2/M3/M4 ve Intel uyumlu)

### 2. Kaynak Koddan Çalıştırma

#### 🪟 Windows:
```cmd
run.bat
```

#### 🍏 macOS / 🐧 Linux:
```bash
./run.sh
# veya
python3 run.py
```
Tarayıcınızda otomatik olarak **`http://127.0.0.1:8000`** adresi açılacaktır.

---

## 🧪 Otomatik Testler / Running Unit Tests

```bash
python3 -m unittest tests/test_pipe_suite.py -v
```

---

## 📄 Lisans / License

Bu proje [MIT Lisansı](LICENSE) altında lisanslanmıştır.
