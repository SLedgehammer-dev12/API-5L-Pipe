# Sürüm Notları / Release Notes - v2.4.0

## 🚀 API 5L PSL1/PSL2 & BOTAŞ Boru Kalite Güvence, Et Kalınlığı Tasarım ve Akıllı ITP Denetim Süiti (v2.4.0)

Bu sürüm (**v2.4.0**), **Çift Dilli (İngilizce & Türkçe) Genişletilmiş Sanayi Terminolojisi Sözlüğü (`Bilingual Industrial Thesaurus`)**, **Çevrimdışı Sayısal Kriter ve Varlık Ayrıştırıcı Motoru (`ITPCriteriaParser`)** ve **Disambiguation / Anti-Affinity Test Eşleştirme Filtreleri** ile ITP denetim doğruluğunu %100 seviyesine çıkarmaktadır.

---

### 🌟 v2.4.0 ile Gelen Başlıca Yenilikler

1. **🌐 Çift Dilli (TR & EN) Kapsamlı Sanayi Anahtar Kelime Dağarcığı (`TEST_MATCHER_KEYWORDS`):**
   - Uluslararası şartnamelerde (API 5L, ISO 3183, ASTM A370/A751/E436, DIN 30670, Shell DEP, Saudi Aramco, TOTAL, DNV) ve yerel şartnamelerde (BOTAŞ, Borusan, Tosçelik, Erciyas, Emek, Umran) kullanılan 100'den fazla İngilizce ve Türkçe terim, kısaltma ve test ismi eşleştiriciye eklendi.
   - Çekme ($R_{t0.5}, R_m, A\%$), Çentik Darbe (Charpy V-Notch, FL+2, FL+5), DWTT, NDT (AUT, PAUT, RT, UT, MPI), Boyutsal Ölçümler ve 3LPE Kaplama terminolojisi tam kapsam altına alındı.

2. **🧮 Çevrimdışı Sayısal Değer & Kriter Ayrıştırıcı Motoru (`ITPCriteriaParser`):**
   - Harici internet veya LLM bağımlılığı olmadan %100 yerel ve deterministik çalışan fiziksel birim ve operatör ayrıştırıcı motoru yazıldı.
   - Çoklu karakterli karşılaştırma operatörleri (`<=`, `>=`, `:=`, `≤`, `≥`, `%`) ve farklı notasyon formatlarındaki metinlerden akma, çekme, Y/T oranı, darbe enerjisi, sünek kırılma yüzdesi, hidrostatik basınç/süre, kaplama kalınlığı ve toleransları hatasız ayıklar.

3. **🎯 Karışmayı Önleyici Ayrıştırma ve Negatif Ağırlıklandırma (Disambiguation / Anti-Affinity):**
   - Çekme testleri ile Çentik Darbe (Charpy/CVN) testlerinin metin benzerliklerinden dolayı birbirine karışması engellendi.
   - Dış Çap ölçümleri ile Ovalite kontrollerinin boru ucu/gövde bazında doğru test maddesine eşleşmesi garanti altına alındı.

4. **🧪 59/59 Kapsamlı Test Süiti (%100 PASS):**
   - `test_51` (İngilizce & Hibrit ITP Eşleştirme) ve `test_52` (Sayısal Kriter Ayrıştırma) testleri ile tüm test senaryoları doğrulandı.

---

### 💻 İndirme Bağlantıları (v2.4.0)

- **🪟 Windows (x64):**  
  [**`API-5L-Pipe-Windows-x64-v2.4.0.exe` İndir**](https://github.com/SLedgehammer-dev12/API-5L-Pipe/releases/download/v2.4.0/API-5L-Pipe-Windows-x64-v2.4.0.exe)  
  *Tek dosyadır, kurulum gerektirmez. Doğrudan çift tıklayarak çalıştırabilirsiniz.*

- **🍏 macOS (Apple Silicon M1/M2/M3/M4 & Intel):**  
  [**`API-5L-Pipe-macOS-v2.4.0.dmg` İndir**](https://github.com/SLedgehammer-dev12/API-5L-Pipe/releases/download/v2.4.0/API-5L-Pipe-macOS-v2.4.0.dmg)  
  *Disk kalıbını açıp `API-5L-Pipe.app` uygulamasını Applications klasörüne sürükleyin.*

---

1. **📏 Tüm Boru Boyut Ölçüleri ve Toleranslarının ITP Denetimine Eklenmesi:**
   - **Boru Ucu & Gövde Dış Çap Toleransları:** $d_{\text{end\_min}} - d_{\text{end\_max}}\text{ mm}$ ve $d_{\text{body\_min}} - d_{\text{body\_max}}\text{ mm}$ tolerans kontrolleri.
   - **Boru Ucu & Gövde Çevre Toleransları:** $\pi \cdot D_{\text{end}}$ ve $\pi \cdot D_{\text{body}}$ Pi-Mezura çevre kontrolleri.
   - **Boru Ucu & Gövde Ovalite Toleransları:** $D_{\text{max}} - D_{\text{min}} \le \text{ovality\_end}\text{ mm}$ (BOTAŞ $\le 3.05\text{ mm}$) ve gövde ovalite kontrolleri.
   - **Et Kalınlığı & Birim Ağırlık:** Ultrasonik cidar kalınlığı ($t_{\text{min}} - t_{\text{max}}\text{ mm}$) ve kantar tartım ($-\%3.5 / +\%10.0$) denetimleri.
   - **Doğrusallık, Kaynak Ağzı & Diklik:** Toplam doğrusallık ($\le \%0.10 L$), alın kaynak ağzı açısı ($30^\circ (+5^\circ/-0^\circ)$), kök yüzeyi ($1.6 \pm 0.8\text{ mm}$) ve diklik sapması ($\le 1.6\text{ mm}$).
   - **Kaynak Dikiş Geometrisi:** Tepeleşme ($\le \text{peaking\_max}\text{ mm}$), sac kenarları radyal basamaklanma ($\le \text{radial\_offset}\text{ mm}$) ve iç/dış paso kaynak yüksekliği limitleri.

2. **🎥 Canlı 3D/2.5D Helisel Sarım & Kaynak Sahnesi (`SawhSimulationEngine`):**
   - Rulo çelik sac şeridin $\alpha$ helis açısıyla girişini, şekillendirme kafesini ve borunun 3D silindirik dönüş/ilerleyişini 60 FPS akıcılıkla simüle eder.
   - Altın tonlu helisel spiral kaynak dikişi ve çift taraflı tozaltı ark kaynağı (Dış OD SAW + İç ID SAW torçları) plazma arkı ve uçuşan fiziksel kıvılcım efektleriyle canlandırıldı.

3. **📐 2D Geometrik Açınım & Trigonometri Düzlemi:**
   - 1 tam turun açılmış dikdörtgen yüzeyi ($w = \pi \cdot D_{\text{mid}}$, $h = P$) ve açılmış şerit paralelkenarı ($B = \pi \cdot D_{\text{mid}} \cdot \cos\alpha$) net mühendislik blueprint görünümünde sunuldu.

4. **🎛️ Ergonomik Kontroller & Telemetri:**
   - `🎥 3D İmalat`, `📐 2D Açınım` ve `◫ İkili Görünüm (Split View)` mod geçişleri.
   - Oynat/Durdur, Başa Sar, $0.5\text{x} / 1.0\text{x} / 2.0\text{x}$ hız ayarları.
   - Tozaltı Arkı, Ölçülendirme Okları, Şekillendirme Ruloları ve Röntgen (X-Ray Wireframe) katman anahtarları.
   - `Min B` ($65^\circ$), `Nominal` ($55^\circ$), `Max B` ($30^\circ$) tek tıkla şerit genişliği ön ayarları.
   - Retina / 4K ekranlar için `devicePixelRatio` keskin çizim entegrasyonu.

---

### 💻 İndirme Bağlantıları (v2.2.0)

- **🪟 Windows (x64):**  
  [**`API-5L-Pipe-Windows-x64-v2.2.0.exe` İndir**](https://github.com/SLedgehammer-dev12/API-5L-Pipe/releases/download/v2.2.0/API-5L-Pipe-Windows-x64-v2.2.0.exe)  
  *Tek dosyadır, kurulum gerektirmez. Doğrudan çift tıklayarak çalıştırabilirsiniz.*

- **🍏 macOS (Apple Silicon M1/M2/M3/M4 & Intel):**  
  [**`API-5L-Pipe-macOS-v2.2.0.dmg` İndir**](https://github.com/SLedgehammer-dev12/API-5L-Pipe/releases/download/v2.2.0/API-5L-Pipe-macOS-v2.2.0.dmg)  
  *Disk kalıbını açıp `API-5L-Pipe.app` uygulamasını Applications klasörüne sürükleyin.*

---

## Önceki Sürümler / Previous Versions

### Sürüm Özeti - v2.1.1 (2026-09-01)
- SAWH Helisel Sarım & Çift Taraflı Tozaltı Kaynağı (SAW) Canlı 3D/2D İnteraktif Simülasyon Motoru (`SawhSimulationEngine`).

### Sürüm Özeti - v2.1.0 (2026-08-31)
- Çok Sütunlu Gerçek Tablo Ekstraksiyonu (PyMuPDF 1.23+ `find_tables()`).
- Maksimum Ağırlıklı İki Kümeli Eşleştirici (Maximum-Weight Bipartite Matcher).
- 24 Disiplin İçin Sayısal Kriter & Tolerans Denetimi (DWTT, Çekme, Kimya, NDT, Tamir).
- Kapsamlı Kod Sağlığı ve Güvenilirlik Refaktörü (C1-C18, F1-F13, B1-B6).