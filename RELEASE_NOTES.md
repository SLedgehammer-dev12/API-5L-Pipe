# Sürüm Notları / Release Notes - v2.7.0

## 🚀 API 5L PSL1/PSL2 & BOTAŞ Boru Kalite Güvence, Et Kalınlığı Tasarım ve Akıllı ITP Denetim Süiti (v2.7.0)

Bu sürüm (**v2.7.0**), **Doğal Gaz Boru Hatları 3LPE Dış Polietilen Kaplama**, **İç Akış Artırıcı Epoksi Kaplama**, **Çift Katmanlı FBE/ARO**, **Ağır Etli (t > 25 mm) Mega Boru Desteği**, **Uluslararası IOGP JIP33 Kalite Dokümanları Entegrasyonu** ve **93/93 Kapsamlı Test Süiti** ile ITP denetimlerini eksiksiz kılmaktadır.

---

### 🌟 v2.7.0 ile Gelen Başlıca Yenilikler

1. **📦 Genişletilmiş Doğal Gaz Boru Hattı ITP Kütüphanesi (26 Doküman):**
   - **3LPE Dış Kaplama:** ISO 21809-1 / DIN 30670 / BOTAŞ uyumlu, 22 kritik adımlı denetim matrisi (Sa 2.5, 25 kV holiday testi, soyulma, katodik ayrılma, darbe ve batma direnci).
   - **İç Akış Artırıcı Epoksi Kaplama:** API RP 5L2 / ISO 15741 uyumlu (Rz <= 25 µm hidrolik pürüzlülük ile gaz debi artışı, hızlı gaz dekompresyon testi, MEK 50 çift silme).
   - **Çift Katmanlı FBE/ARO Kaplama:** CSA Z245.20 / NACE SP0394 uyumlu yatay sondaj (HDD) ve aşınma korumalı kaplama denetimi.
   - **56" X80 Ağır Etli Mega Boru:** API 5L PSL 2 / ISO 3183 ultra yüksek basınç (120 bar) 190.5 bar hidrostatik testli boru denetimi.
   - **IOGP JIP33 Kalite Standartları:** S-616Q, S-616 ve S-715Q normatif gözetim matrisleri sisteme entegre edildi.

2. **⚙️ Ağır Et Kalınlığı ($t > 25.0\text{ mm}$) API 5L 9.2.3 Desteği:**
   - Ağır et kalınlıklarında API 5L Madde 9.2.3 uyarınca kimyasal analizin anlaşmaya bağlı (`as_agreed`) olduğu durumlar güvenli varsayılan değerlerle desteklenerek olası `NoneType` formatlama açıkları giderildi.

3. **🧪 93/93 Kapsamlı Test Süiti (%100 PASS):**
   - 26 ITP dosyasının tamamı deterministik golden master testleriyle indekslendi, 93 testin tamamı 0 hata ile doğrulandı.

---

### 💻 İndirme Bağlantıları (v2.7.0)

- **🪟 Windows (x64):**  
  [**`API-5L-Pipe-Windows-x64-v2.7.0.exe` İndir**](https://github.com/SLedgehammer-dev12/API-5L-Pipe/releases/download/v2.7.0/API-5L-Pipe-Windows-x64-v2.7.0.exe)  
  *Tek dosyadır, kurulum gerektirmez. Doğrudan çift tıklayarak çalıştırabilirsiniz.*

- **🍏 macOS (Apple Silicon M1/M2/M3/M4 & Intel):**  
  [**`API-5L-Pipe-macOS-v2.7.0.dmg` İndir**](https://github.com/SLedgehammer-dev12/API-5L-Pipe/releases/download/v2.7.0/API-5L-Pipe-macOS-v2.7.0.dmg)  
  *Disk kalıbını açıp `API-5L-Pipe.app` uygulamasını Applications klasörüne sürükleyin.*

---

### Sürüm Özeti - v2.5.0 (2026-09-01)

---

### 🌟 v2.5.0 ile Gelen Başlıca Yenilikler

1. **📚 API Spec 5L 46. Baskı vs 47. Baskı Dinamik Seçeneği:**
   - 46. ve 47. baskılar arasındaki kritik standart madde ve çizelge farkları (Hidrostatik Çizelge 26 / Barlow formülü, ERW Normalizasyon Madde 10.2.5.3, Çekme Çizelge 7, Çentik Darbe Çizelge 8) ayrıştırıldı.
   - Denetim raporlarında ve Excel çıktılarında standart baskısı dinamik olarak referans gösterilir.

2. **📊 Hibrit Çift Skorlama Sistemi (Çıplak Boru & 3LPE Kaplama):**
   - Çıplak Boru Uyum Puanı (`bare_pipe_score_percent`) ve 3LPE Dış Kaplama Uyum Puanı (`coating_score_percent`) birbirinden bağımsız olarak hesaplanır.
   - Kombine denetimlerde %70 Çıplak Boru / %30 Kaplama ağırlıklı genel uyum skoru üretilir; tek disiplinli ITP yüklemelerinde ise diğer disiplin cezalandırılmadan izole edilir.

3. **🛡️ H/W/R/I/C Şahitlik Noktaları (Witness / Hold Matrix) Ayrıştırması:**
   - İmalatçı, Üçüncü Taraf Gözetim (TPI) ve Müşteri (BOTAŞ) şahitlik ve durdurma noktaları kabul kriterlerinden temiz şekilde ayrıştırıldı.
   - Excel ve PDF raporlarına özel şahitlik matrisi sütunu eklendi.

4. **🔍 Gelişmiş Frekans & NDT Seviyesi Reddi:**
   - `1/200 boru`, `1 per 100`, `50 boruda 1` gibi yetersiz seyrek frekanslar `INADEQUATE_SAMPLING` olarak tanınıp uygunsuzluk olarak işaretlenir.
   - NDT kaynak dikişi kabul kriterinde yetersiz kalan `U1 / U1H / U3 / U4` seviyeleri reddedilir, `ISO 10893-11 Seviye U2` zorunluluğu denetlenir.

5. **🧪 64/64 Kapsamlı Test Süiti (%100 PASS):**
   - Borusan GBB 18 sayfalık tablo matrisi, seyrek frekans reddi, NDT U1 reddi, 46. baskı eşleşmeleri ve hibrit çift skorlama dahil tüm 64 test senaryosu %100 başarıyla geçmektedir.

---

### 💻 İndirme Bağlantıları (v2.5.0)

- **🪟 Windows (x64):**  
  [**`API-5L-Pipe-Windows-x64-v2.5.0.exe` İndir**](https://github.com/SLedgehammer-dev12/API-5L-Pipe/releases/download/v2.5.0/API-5L-Pipe-Windows-x64-v2.5.0.exe)  
  *Tek dosyadır, kurulum gerektirmez. Doğrudan çift tıklayarak çalıştırabilirsiniz.*

- **🍏 macOS (Apple Silicon M1/M2/M3/M4 & Intel):**  
  [**`API-5L-Pipe-macOS-v2.5.0.dmg` İndir**](https://github.com/SLedgehammer-dev12/API-5L-Pipe/releases/download/v2.5.0/API-5L-Pipe-macOS-v2.5.0.dmg)  
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