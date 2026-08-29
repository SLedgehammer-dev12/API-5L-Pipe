# Sürüm Notları / Release Notes - v1.8.0

## 🚀 API 5L PSL1/PSL2 & BOTAŞ Boru Kalite Güvence, Fabrika Kabul ve Çoklu Standart Et Kalınlığı Tasarım Yazılımı

Bu sürüm, **SAWH Spiral Bant Genişliği & Büküm Açısı** hesaplama aracını (canlı 2D diyagram + 3D model entegrasyonu + sarım animasyonu) ekler ve **uygulama ikonu** ile **sürümlü çalıştırma dosyası adlarını** içerir.

---

### 🌟 v1.8.0 ile Gelenler

1. **🧮 SAWH Spiral Bant Genişliği & Büküm Açısı (yeni):**
   - 2D/3D Şematik sekmesine tam genişlik kart eklendi (yalnız SAWH/SAWL borular için görünür).
   - Formül: `B = π·D_mid·cos(α)`, `α = arccos(B/(π·D_mid))`, `D_mid = D − t`.
   - Sınır koşulları: `α=0° → B=π·D_mid` (boyuna); `α→90° → B→0` (çevresel); pratik aralık `α∈[30°,65°]`.
   - **Canvas 2D canlı diyagram:** açılmış yüzey (bir tur) + α açısı + açılmış şerit bandı; rulolar bant genişliği değişince anlık güncellenir.
   - **3D model entegrasyonu:** seçili borunun spiral kaynak dikişinin adımı/eğimi hesaplanan α'ya göre canlı güncellenir.
   - **SVG sarım animasyonu:** şeridin boruya sarılışı.
   - Backend: `core/sawh_engine.py` + `POST /api/sawh-strip`.

2. **🎨 Uygulama İkonu:**
   - Boru/hat mühendisliğine uygun **3D boru + "API"** ikonu (`tools/make_icon.py` ile üretilen `.ico`/`.icns`).
   - Windows `.exe` ve macOS `.app` ikonlarına bağlandı.

3. **🏷️ Sürümlü Çalıştırma Dosyası Adları (tüm yollar):**
   - `API-5L-Pipe-Windows-x64-v1.8.0.exe`, `API-5L-Pipe-macOS-v1.8.0.dmg`, macOS `.app` → `API-5L-Pipe-v1.8.0.app`.
   - `API-5L-Pipe.spec` ve workflow macOS adları da versiyonlandı.

4. **🔐 (önceki sürümden) Windows SSL & doğrulama parametre sayısı & çekme numunesi çift-tip düzeltmeleri** dahildir.

---

### 💻 İndirme Bağlantıları (v1.8.0)

- **🪟 Windows (x64):**  
  [**`API-5L-Pipe-Windows-x64-v1.8.0.exe` İndir**](https://github.com/SLedgehammer-dev12/API-5L-Pipe/releases/download/v1.8.0/API-5L-Pipe-Windows-x64-v1.8.0.exe)  
  *Tek dosyadır, kurulum gerektirmez. Doğrudan çift tıklayarak çalıştırabilirsiniz.*

- **🍏 macOS (Apple Silicon M1/M2/M3/M4 & Intel):**  
  [**`API-5L-Pipe-macOS-v1.8.0.dmg` İndir**](https://github.com/SLedgehammer-dev12/API-5L-Pipe/releases/download/v1.8.0/API-5L-Pipe-macOS-v1.8.0.dmg)  
  *Disk kalıbını açıp `API-5L-Pipe.app` uygulamasını Applications klasörüne sürükleyin.*