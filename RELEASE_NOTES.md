# Sürüm Notları / Release Notes - v1.0.3

## 🚀 API 5L PSL2 & BOTAŞ Boru Kalite Güvence, Fabrika Kabul ve Et Kalınlığı Tasarım Yazılımı

Bu sürüm, kullanıcı arayüzü versiyon senkronizasyonunu, **BOTAŞ tüm dizayn faktörlerine göre otomatik boru matrisi doldurma motorunu**, **sağ tarafa sabitlenmiş mühendislik açıklamalarını** ve **Windows (.exe) ile macOS (.dmg) bağımsız çalıştırılabilir paketlerinin** tam uyumluluğunu içermektedir.

---

### 🌟 Öne Çıkan Özellikler ve Yenilikler (What's New)

1. **⚡ BOTAŞ Çapa Göre Otomatik Doldurma (Auto-Populate All Design Factors):**
   - Kullanıcı boru eklerken **BOTAŞ Şartnamesi** seçtiğinde yalnızca boru çapını (örn. 48", 24", 8" vb.) belirler.
   - Sistem, BOTAŞ şartname tablosundan ilgili çapa ait tüm dizayn faktörlerindeki boruları ($F=0.72\text{ Hat}$, $F=0.60\text{ Hat}$, $F=0.50\text{ Hat}$, $F=0.50\text{ İstasyon 1}$, $F=0.50\text{ İstasyon 2}$) otomatik tespit eder ve **tek tıkla aynı anda matrise ayrı sütunlar olarak ekler**.

2. **🏷️ Sabit Sağ Açıklamalar Sütunu (Engineering Remarks):**
   - Matris tablosunun ve Excel çıktısının en sağ sütununda her parametrenin standarda dayalı kuralı, ASME B31.8 / API 5L / BOTAŞ şartname maddesi ve formülü açıklanmıştır.

3. **🛠️ PyInstaller ve Çapraz Platform Çalıştırma İyileştirmeleri:**
   - `multiprocessing.freeze_support()` ve doğrudan ASGI uygulama nesnesi (`from app import app`) entegre edildi.
   - Uvicorn'un string modül arama hatası ve GUI pencereli modundaki `sys.stdout` None çökmesi tamamen giderildi.
   - Otomatik boş port tespit edici (`find_available_port`) eklendi.

4. **🎮 3D WebGL (Three.js) & 2D SVG Modeli:**
   - 360° döndürülebilir 3D boru gövdesi ve SAWH borular için helisel/spiral kaynak dikişi, ERW için boyuna kaynak.
   - 2D vektörel kesit ve imalat tolerans bantları.

5. **🛡️ Fabrika Test Doğrulama (PASS / FAIL Analizi):**
   - Sahadan/laboratuvardan gelen gerçek ölçüm değerlerinin otomatik uygunluk denetimi.

6. **📑 Raporlama & Dışa Aktarma:**
   - Excel (.xlsx) profesyonel formatlı dışa aktarım (OpenPyXL).
   - Resmi EN 10204 3.1 uyumlu yazdırılabilir kabul raporu / PDF.

---

### 📦 İndirme ve Kurulum / Download & Installation

- **🪟 Windows (x64):**  
  [**`API-5L-Pipe-Windows-x64.exe`**](https://github.com/SLedgehammer-dev12/API-5L-Pipe/releases/download/v1.0.3/API-5L-Pipe-Windows-x64.exe)  
  *Tek dosyadır, kurulum gerektirmez. Çift tıklayarak doğrudan çalıştırabilirsiniz.*

- **🍏 macOS (Apple Silicon M1/M2/M3/M4 & Intel):**  
  [**`API-5L-Pipe-macOS.dmg`**](https://github.com/SLedgehammer-dev12/API-5L-Pipe/releases/download/v1.0.3/API-5L-Pipe-macOS.dmg)  
  *Disk kalıbını açıp `API-5L-Pipe.app` uygulamasını Applications klasörüne sürükleyin.*
