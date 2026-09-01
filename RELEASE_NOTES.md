# Sürüm Notları / Release Notes - v2.3.0

## 🚀 API 5L PSL1/PSL2 & BOTAŞ Boru Kalite Güvence, Et Kalınlığı Tasarım ve Akıllı ITP Denetim Süiti (v2.3.0)

Bu majör-minör sürüm (**v2.3.0**), **ITP Standart ve Kapsam Otomatik Algılama Motoru (`detect_itp_metadata`)**, **Kullanıcı Etkileşimli Manuel Müdahale / Şartname Değiştirme Kartı** ve **Resmi Yatay A4 PDF Denetim ve Sapma Raporu Üreteci (`PDFExporter`)** modüllerini sunar.

---

### 🌟 v2.3.0 ile Gelen Başlıca Yenilikler

1. **📄 Resmi PDF ITP Denetim ve Sapma Belgesi Üreteci (`PDFExporter`):**
   - **Yatay A4 (Landscape) Mimarisi:** Çok sütunlu teknik tabloların ve tolerans limitlerinin taşmadan, yüksek okunabilirlikle sunulması.
   - **Dinamik İki Geçişli Sayfalama (`NumberedCanvas`):** Otomatik `Sayfa X / Y` numaralandırması ve kurumsal üst/alt bilgi (header/footer) şeritleri.
   - **Yerel Türkçe Karakter Desteği:** `ç, ğ, ı, ö, ş, ü, Ç, Ğ, İ, Ö, Ş, Ü` glifleri sıfır bozulma ile basılır.
   - **Rapor Bölümleri:** Proje & Boru Künyesi, Yönetici KPI Skor Kartı, Varsa Kritik Uygunsuzluklar Tablosu, Uçtan Uca Yan Yana Karşılaştırma Matrisi ve 3'lü Resmi İmza/Onay Bloğu.
   - **Tek Tıkla İndirme:** Arayüzdeki kırmızı **`[ PDF Denetim Raporu İndir ]`** butonuyla anında çıktı alma.

2. **🧠 Akıllı Standart & Kapsam Otomatik Algılama Motoru:**
   - **Standart Tespiti:** Yüklenen ITP PDF dokümanında geçen BOTAŞ (`4-NGTL-0-GN-P-002-5120`, `5410`, `5140`), API Spec 5L (46th/47th), ISO 3183 ve DIN 30670 referanslarını tarayarak geçerli standardı otomatik belirler.
   - **Kapsam İzolasyonu (Scope Mode):**
     - `Sadece 3LPE Dış Kaplama` *(Örn: Tosçelik `TOS-ITP-ŞRK-002`)*: Sadece kaplama testlerini denetler, çıplak boru mekanik testlerinin eksik olduğu yanıltıcı hataları engeller.
     - `Sadece Çıplak Boru İmalatı` *(Örn: `TOS-ITP-ŞRK-001`)*: Sadece çelik boru imalat maddelerini denetler.
     - `Bütünsel (İmalat + Kaplama)` *(Örn: Borusan `GBB-ITP-ERW-BOT-2620`)*: Hem boru imalatını hem dış kaplamayı birlikte denetler.
   - **Boru Ebat & Malzeme Tespiti:** Çap ($D$), et kalınlığı ($t$), çelik kalitesi (X42/X65), PSL ve imalat prosesini otomatik ayıklar.

3. **🎛️ Kullanıcı Etkileşimli Standart Eşleme ve Hızlı Yeniden Denetim Kartı:**
   - Yüklenen doküman sonrası açılan modern kart üzerinden:
     - Standart Değerlendirmesi: `BOTAŞ (5120 R7 + 5410 R1)`, `API Spec 5L 47. Baskı (PSL2)`, `API PSL1`, `ASME / ISO`.
     - Denetim Kapsamı: `Bütünsel`, `Sadece 3LPE Kaplama`, `Sadece Çıplak Boru`.
     - **"Yeniden Denetle"** butonuyla 1 saniyede tüm matrisi ve KPI skorunu seçilen yeni şartnameye göre yenileme.
     - **"+ Dokümandaki Boruyu Projeye Ekle"** butonuyla algılanan boruyu projeye kaydetme.
     - BOTAŞ negatif et payı (%0), CVN -20°C, 25 kV Holiday ve sıfır martenzit ek şartları bilgilendirme uyarısı.

4. **🧪 57/57 Genişletilmiş Test Süiti (%100 PASS):**
   - PDF raporlama, Türkçe karakter glifleri, metadata tolerans dayanıklılığı ve proje durum yaşam döngüsü testleri eklendi.

---

### 💻 İndirme Bağlantıları (v2.3.0)

- **🪟 Windows (x64):**  
  [**`API-5L-Pipe-Windows-x64-v2.3.0.exe` İndir**](https://github.com/SLedgehammer-dev12/API-5L-Pipe/releases/download/v2.3.0/API-5L-Pipe-Windows-x64-v2.3.0.exe)  
  *Tek dosyadır, kurulum gerektirmez. Doğrudan çift tıklayarak çalıştırabilirsiniz.*

- **🍏 macOS (Apple Silicon M1/M2/M3/M4 & Intel):**  
  [**`API-5L-Pipe-macOS-v2.3.0.dmg` İndir**](https://github.com/SLedgehammer-dev12/API-5L-Pipe/releases/download/v2.3.0/API-5L-Pipe-macOS-v2.3.0.dmg)  
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