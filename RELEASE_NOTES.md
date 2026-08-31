# Sürüm Notları / Release Notes - v2.1.1

## 🚀 API 5L PSL1/PSL2 & BOTAŞ Boru Kalite Güvence, Et Kalınlığı Tasarım ve Akıllı ITP Denetim Süiti (v2.1.1 Hotfix)

Bu ara sürüm (**v2.1.1**), **SAWH Helisel Büküm & Tozaltı Kaynağı (SAW) Canlı 3D/2D İnteraktif Simülasyon Motorunu (`SawhSimulationEngine`)** ve ergonomik imalat kontrollerini sunar.

---

### 🌟 v2.1.1 ile Gelen Başlıca Yenilikler

1. **🎥 Canlı 3D/2.5D Helisel Sarım & Kaynak Sahnesi (`static/js/app.js`):**
   - Rulo çelik sac şeridin $\alpha$ helis açısıyla girişini, şekillendirme kafesini ve borunun 3D silindirik dönüş/ilerleyişini 60 FPS akıcılıkla simüle eder.
   - Altın tonlu helisel spiral kaynak dikişi ve çift taraflı tozaltı ark kaynağı (Dış OD SAW + İç ID SAW torçları) plazma arkı ve uçuşan fiziksel kıvılcım efektleriyle canlandırıldı.

2. **📐 2D Geometrik Açınım & Trigonometri Düzlemi:**
   - 1 tam turun açılmış dikdörtgen yüzeyi ($w = \pi \cdot D_{\text{mid}}$, $h = P$) ve açılmış şerit paralelkenarı ($B = \pi \cdot D_{\text{mid}} \cdot \cos\alpha$) net mühendislik blueprint görünümünde sunuldu.

3. **🎛️ Ergonomik Kontroller & Telemetri:**
   - `🎥 3D İmalat`, `📐 2D Açınım` ve `◫ İkili Görünüm (Split View)` mod geçişleri.
   - Oynat/Durdur, Başa Sar, $0.5\text{x} / 1.0\text{x} / 2.0\text{x}$ hız ayarları.
   - Tozaltı Arkı, Ölçülendirme Okları, Şekillendirme Ruloları ve Röntgen (X-Ray Wireframe) katman anahtarları.
   - `Min B` ($65^\circ$), `Nominal` ($55^\circ$), `Max B` ($30^\circ$) tek tıkla şerit genişliği ön ayarları.
   - Retina / 4K ekranlar için `devicePixelRatio` keskin çizim entegrasyonu.

---

### 💻 İndirme Bağlantıları (v2.1.1)

- **🪟 Windows (x64):**  
  [**`API-5L-Pipe-Windows-x64-v2.1.1.exe` İndir**](https://github.com/SLedgehammer-dev12/API-5L-Pipe/releases/download/v2.1.1/API-5L-Pipe-Windows-x64-v2.1.1.exe)  
  *Tek dosyadır, kurulum gerektirmez. Doğrudan çift tıklayarak çalıştırabilirsiniz.*

- **🍏 macOS (Apple Silicon M1/M2/M3/M4 & Intel):**  
  [**`API-5L-Pipe-macOS-v2.1.1.dmg` İndir**](https://github.com/SLedgehammer-dev12/API-5L-Pipe/releases/download/v2.1.1/API-5L-Pipe-macOS-v2.1.1.dmg)  
  *Disk kalıbını açıp `API-5L-Pipe.app` uygulamasını Applications klasörüne sürükleyin.*

---

## Önceki Sürümler / Previous Versions

### Sürüm Özeti - v2.1.0 (2026-08-31)
- Çok Sütunlu Gerçek Tablo Ekstraksiyonu (PyMuPDF 1.23+ `find_tables()`)
- Maksimum Ağırlıklı İki Kümeli Eşleştirici (Maximum-Weight Bipartite Matcher)
- 24 Disiplin İçin Sayısal Kriter & Tolerans Denetimi (DWTT, Çekme, Kimya, NDT, Tamir)
- Kapsamlı Kod Sağlığı ve Güvenilirlik Refaktörü (C1-C18, F1-F13, B1-B6)