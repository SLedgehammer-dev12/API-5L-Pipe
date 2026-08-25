# Sürüm Notları / Release Notes - v1.6.2

## 🚀 API 5L PSL2 & BOTAŞ Boru Kalite Güvence, Fabrika Kabul ve Çoklu Standart Et Kalınlığı Tasarım Yazılımı

Bu sürüm, **API 5L Test & Muayene Planını (ITP)** zenginleştirir: boru seçici, standart madde metinleri (tam orijinal) ve numune çizimleri.

---

### 🌟 v1.6.2 ile Gelen Yenilikler

1. **🔀 ITP Boru Seçici (Chips):**
   - Fabrika Test Doğrulama sekmesindeki ITP kartına, 3D/2D'dekiyle aynı yatay boru çipleri eklendi.
   - Çipe tıklayınca boru seçimi **global `selectedPipeIndex` ile senkron** çalışır — matris, KPI kartları ve 3D/2D model de aynı boruya geçer.

2. **📖 Standart Madde Metni (ℹ️ + tıkla-genişle):**
   - ITP tablosundaki **Madde** hücresindeki bilgi ikonu, ilgili API 5L 46th Ed. maddesinin **tam orijinal metnini** modal ile gösterir.
   - Test satırına tıklanınca madde metni satır altında **inline** açılır.

3. **🖼️ Numune Çizimleri (ℹ️):**
   - **Numune Boyutu** hücresindeki bilgi ikonu, API 5L Şekil 4/5/6 ve standart numune şekillerine çok yakın **SVG şematik çizimleri** gösterir: Charpy (10×10×55 + alt boyutlar), çekme şerit/yuvarlak çubuk, kılavuzlu bükme, düzleştirme, DWTT, sertlik izleri ve numune alım yerleri.

4. **⚙️ Backend:** `test_plan.py` her teste `clause_ref` (orijinal standart metni) ve `specimen_figure` (çizim anahtarı) alanlarını ekledi.

---

### 💻 İndirme Bağlantıları (v1.6.2)

- **🪟 Windows (x64):**  
  [**`API-5L-Pipe-Windows-x64-v1.6.2.exe` İndir**](https://github.com/SLedgehammer-dev12/API-5L-Pipe/releases/download/v1.6.2/API-5L-Pipe-Windows-x64-v1.6.2.exe)  
  *Tek dosyadır, kurulum gerektirmez. Doğrudan çift tıklayarak çalıştırabilirsiniz.*

- **🍏 macOS (Apple Silicon M1/M2/M3/M4 & Intel):**  
  [**`API-5L-Pipe-macOS-v1.6.2.dmg` İndir**](https://github.com/SLedgehammer-dev12/API-5L-Pipe/releases/download/v1.6.2/API-5L-Pipe-macOS-v1.6.2.dmg)  
  *Disk kalıbını açıp `API-5L-Pipe.app` uygulamasını Applications klasörüne sürükleyin.*