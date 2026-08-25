# Sürüm Notları / Release Notes - v1.6.0

## 🚀 API 5L PSL2 & BOTAŞ Boru Kalite Güvence, Fabrika Kabul ve Çoklu Standart Et Kalınlığı Tasarım Yazılımı

Bu sürüm, **API 5L PSL2 ↔ BOTAŞ tolerans ayrımının tamamlanmasını** — et kalınlığı, kaynak parametreleri (radial offset, kaynak yüksekliği, misalignment), çap toleransı ve ovalite — ve kimyasal bileşim boşluklarının doldurulmasını içermektedir. Artık boru sütunu hangi standarda göre oluşturulduysa o standardın (API 5L PSL2 veya BOTAŞ) değerleri uygulanır.

---

### 🌟 v1.6.0 ile Gelen Önemli Yenilikler

1. **📐 Et Kalınlığı Negatif Toleransı Ayrımı:**
   - **API 5L Table 11:** Kaynaklı boru −0.5 / −0.1·t / −1.5 mm; SMLS −0.5 / −0.125·t / −3.0 mm.
   - **BOTAŞ:** Excel formülü (−0.04 / −0.10 / −0.15 mm) korunur.

2. **🔩 Kaynak Parametreleri Ayrımı (SAW borular):**
   - **Radial offset:** API 5L Table 14 (1.5 / 0.1·t / 2.5 mm); BOTAŞ ×0.75.
   - **Kaynak yüksekliği:** API 5L Table 16 (iç 3.5; dış 3.5–4.5 mm); BOTAŞ ×0.75.
   - **Misalignment:** API 5L 9.13.3 (3/4 mm); BOTAŞ ×0.75.

3. **⚪ Çap Toleransı & Ovalite Ayrımı:**
   - **API 5L Table 10** değerleri (çap gövde ±0.75%·D / uç ±0.5%·D; ovalite gövde 2%·D / uç 1.5%·D) dinamik hesaplanır.
   - **BOTAŞ** Excel değerlerini korur.

4. **🧪 Kimyasal Bileşim Boşlukları Dolduruldu:**
   - GRADE A, X70, X80, X90, X100, X120 kaliteleri için C/Mn limitleri API 5L Table 5 PSL2 değerleriyle tamamlandı (Excel'de `"hata"` dönen hücreler giderildi).

5. **📊 Excel Güncellemesi:**
   - `Pipe Fittings Flange Calc 2026.08.24.xlsx` yeni versiyon olarak kaydedildi; kimya formülleri ve hidrostatik std test basıncı formül referans hatası düzeltildi.

### 🛠️ Düzeltmeler (Fixed)

- **Hidrostatik test faktörü:** `SMYS<65000` koşulu kaldırıldı (Excel formülüyle birebir uyumlu).

---

### 💻 İndirme Bağlantıları (v1.6.0)

- **🪟 Windows (x64):**  
  [**`API-5L-Pipe-Windows-x64.exe` İndir**](https://github.com/SLedgehammer-dev12/API-5L-Pipe/releases/download/v1.6.0/API-5L-Pipe-Windows-x64.exe)  
  *Tek dosyadır, kurulum gerektirmez. Doğrudan çift tıklayarak çalıştırabilirsiniz.*

- **🍏 macOS (Apple Silicon M1/M2/M3/M4 & Intel):**  
  [**`API-5L-Pipe-macOS.dmg` İndir**](https://github.com/SLedgehammer-dev12/API-5L-Pipe/releases/download/v1.6.0/API-5L-Pipe-macOS.dmg)  
  *Disk kalıbını açıp `API-5L-Pipe.app` uygulamasını Applications klasörüne sürükleyin.*
