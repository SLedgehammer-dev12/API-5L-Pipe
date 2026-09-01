# What's New in API 5L Pipe QA/QC & Wall Thickness Suite (v2.3.0)
## Yenilikler ve Sürüm Özeti - v2.3.0 (2026-09-01)

---

### 🇹🇷 Türkçe Özet (v2.3.0)

API 5L Pipe QA/QC Suite **v2.3.0** sürümü ile birlikte **Resmi Yatay A4 PDF ITP Denetim Raporu Üreteci (`PDFExporter`)**, **Akıllı Standart & Kapsam Otomatik Algılama Motoru (`detect_itp_metadata`)** ve **Kullanıcı Etkileşimli Manuel Müdahale / Şartname Değiştirme Kartı** entegre edilmiştir:

#### 1. 📄 Resmi PDF ITP Denetim ve Sapma Raporu (`PDFExporter`)
- Yatay A4 formatında çok sayfalı, Türkçe karakter destekli, iki geçişli sayfalama (`NumberedCanvas` - Sayfa X / Y) mimarisi.
- Proje künyesi, yönetici KPI dashboard kartları, kritik bulgular tablosu, uçtan uca yan yana karşılaştırma matrisi ve 3'lü resmi imza/onay bloğu.
- Arayüzden tek tıkla `[ PDF Denetim Raporu İndir ]` butonuyla tarayıcıya anında indirme.

#### 2. 🧠 Akıllı Standart & Kapsam Otomatik Algılama
- Dokümandaki BOTAŞ, API 5L, ISO 3183 ve DIN 30670 referanslarını otomatik tarayarak standardı belirleme.
- `Sadece 3LPE Dış Kaplama` (Tosçelik formatı), `Sadece Çıplak Boru` ve `Bütünsel` disiplin izolasyonu.
- Çap ($D$), et kalınlığı ($t$), çelik kalitesi (X42/X65), PSL ve prosesi otomatik ayıklama.

#### 3. 🎛️ Etkileşimli Manuel Müdahale & Hızlı Yeniden Denetim Kartı
- Standart (BOTAŞ vs API 5L PSL2 vs PSL1) ve Kapsam (Bütünsel vs Kaplama vs Çıplak Boru) seçimi ve tek tıkla anında yeniden denetleme.
- Dokümandaki boruyu projeye ekleme ve BOTAŞ ek sıkılıkları bilgilendirme kartı.

---

#### 1. 📏 Tüm Boru Boyut Ölçüleri ve Toleranslarının ITP Denetimine Eklenmesi
- **Boru Ucu & Gövde Dış Çap Toleransları:** $d_{\text{end\_min}} - d_{\text{end\_max}}\text{ mm}$ ve $d_{\text{body\_min}} - d_{\text{body\_max}}\text{ mm}$ tolerans kontrolleri.
- **Boru Ucu & Gövde Çevre Toleransları:** $\pi \cdot D_{\text{end}}$ ve $\pi \cdot D_{\text{body}}$ Pi-Mezura çevre kontrolleri.
- **Boru Ucu & Gövde Ovalite Toleransları:** $D_{\text{max}} - D_{\text{min}} \le \text{ovality\_end}\text{ mm}$ (BOTAŞ $\le 3.05\text{ mm}$) ve gövde ovalite kontrolleri.
- **Et Kalınlığı & Birim Ağırlık:** Ultrasonik cidar kalınlığı ($t_{\text{min}} - t_{\text{max}}\text{ mm}$) ve kantar tartım ($-\%3.5 / +\%10.0$) denetimleri.
- **Doğrusallık, Kaynak Ağzı & Diklik:** Toplam doğrusallık ($\le \%0.10 L$), alın kaynak ağzı açısı ($30^\circ (+5^\circ/-0^\circ)$), kök yüzeyi ($1.6 \pm 0.8\text{ mm}$) ve diklik sapması ($\le 1.6\text{ mm}$).
- **Kaynak Dikiş Geometrisi:** Tepeleşme ($\le \text{peaking\_max}\text{ mm}$), sac kenarları radyal basamaklanma ($\le \text{radial\_offset}\text{ mm}$) ve iç/dış paso kaynak yüksekliği limitleri.

#### 2. 🎥 3D/2.5D İzometrik Canlı İmalat & Sarım Sahnesi (`SawhSimulationEngine`)
- Rulo çelik sac şerit beslemesi, şekillendirme kafesi ve silindirik boru dönüş/ilerleyişi 60 FPS akıcılıkta canlandırıldı.
- Altın tonlu helisel spiral kaynak dikişi ve çift taraflı tozaltı ark kaynağı (Dış OD SAW + İç ID SAW torçları), plazma arkı ve uçuşan fiziksel kıvılcım efektleriyle simüle edildi.

#### 3. 📐 2D Geometrik Açınım & Trigonometri Düzlemi
- 1 tam turun açılmış dikdörtgen yüzeyi ($w = \pi \cdot D_{\text{mid}}$, $h = P$) ve açılmış şerit paralelkenarı ($B = \pi \cdot D_{\text{mid}} \cdot \cos\alpha$) blueprint görünümünde sunuldu.

#### 4. 🎛️ Ergonomik Kontroller & Telemetri
- `3D İmalat`, `2D Açınım` ve `İkili Görünüm (Split View)` modları.
- Oynat/Durdur, Başa Sar, $0.5\text{x} / 1.0\text{x} / 2.0\text{x}$ hız ayarları.
- Tozaltı Arkı, Ölçülendirme Okları, Şekillendirme Ruloları ve Röntgen (X-Ray Wireframe) katman anahtarları.
- `Min B` ($65^\circ$), `Nominal` ($55^\circ$), `Max B` ($30^\circ$) tek tıkla şerit genişliği ön ayarları.

---

## Önceki Sürümler / Previous Versions

### Sürüm Özeti - v2.1.1 (2026-09-01)
- SAWH Helisel Sarım & Çift Taraflı Tozaltı Kaynağı (SAW) Canlı 3D/2D İnteraktif Simülasyon Motoru (`SawhSimulationEngine`).

### Sürüm Özeti - v2.1.0 (2026-08-31)

#### 1. 📑 Çok Sütunlu Tablo Ekstraksiyonu & Sütun İzolasyonu
- PyMuPDF `find_tables()` ile tablo hücreleri ayrıştırılır; komşu kolon karışmaları önlenir.
- Rasterize `pytesseract` OCR desteği ve `UNLIMITED_OCR_API_URL` uzak sunucu entegrasyonu sağlandı.

#### 2. 🎯 Maksimum Ağırlıklı Bipartite Eşleştirici
- Sıra-bağımlı greedy döngü yerine global optimal bipartite matcher kuruldu.
- SMLS vs Kaynaklı boru anti-affinity kuralları ile yanlış eşleşmeler %100 engellendi.

#### 3. 🧪 24 Disiplin İçin Sayısal Kriter & Tolerans Denetimi
- DWTT ($\ge \%85$ ort., $<\%60$ tekil), Çekme ($R_{t0.5}, R_m, A_f, Y/T$), Kimya ($C, P, S, N, CE$), %100 NDT, tamir boyu $\le 150\text{ mm}$ ve $\ge 100\ ^\circ\text{C}$ ön ısıtma denetlendi.

#### 4. 🛡️ Kod Sağlığı ve Güvenilirlik Refaktörü (C1-C18, F1-F13, B1-B6)
- Grade A değerleri, boş veride `NO_DATA` kararı, büyük çap schedule listesi, Pydantic şema doğrulamaları ve tarayıcı LocalStorage kalıcılığı sağlandı.

---

## Önceki Sürümler / Previous Versions

### Sürüm Özeti - v2.0.0 (2026-08-31)

#### 1. 📑 BOTAŞ Çelik Boru Şartnamesi (`5120 Rev. 7`) Standart & Test Planı Entegrasyonu
- **20 Saniye Hidrostatik Test:** Fabrika hidrostatik test tutma süresi tüm boru çapları için asgari 20 saniye olarak tanımlandı (Madde 8.4.1).
- **$-20\ ^\circ\text{C}$ Çentik Darbe (CVN) Tokluğu:** X65 için Gövde min 60 J / tekil 45 J, Kaynak min 45 J / tekil 34 J şartı getirildi (Madde 3.3.5 & Tablo-3).
- **Artık Stres Testi (Residual Stress Ring Test):** Kaynaklı borularda her dökümde (heat) zorunlu 150 mm halka kesme testi ($S \le 0.10 \times SMYS$) tanımlandı (Madde 3.3.9).
- **Gövde UT Laminasyon Muayenesi:** Gövde yüzeyinin en az %40'ını tarayacak UT (ISO 12094 B1) ve boru uçlarında min 50 mm laminasyon kontrolü zorunlu kılındı (Madde 8.8.4.4).
- **Çap, Doğrusallık ve Sertlik:** Boru ucu ovallik (%50 API 5L), doğrusallık sapması ($\le \%0.10 L$), dairesellik sapması ($\le \%0.15 D$) ve sertlik ($300\text{ HV10}$, aşarsa %100 test) kuralları eklendi.

#### 2. 🤖 Sekme 5: ITP Akıllı Denetim & Doküman Okuma Motoru (Unlimited-OCR & PyMuPDF)
- İmalatçı ITP dokümanlarını (PDF veya resim) 0.02 saniyede okuyabilen hibrit mimari (`PyMuPDF` + Semantik Regex ayrıştırıcı).
- Yüklenen ITP'deki test frekanslarını ve kabul kriterlerini API 5L 47. Baskı ve BOTAŞ 5120 R7 şartnameleriyle otomatik karşılaştırma (`ITPAuditEngine`).
- Yetersiz test frekansı, eksik zorunlu test ve süre/kriter kusurlarını anlık kırmızı uyarılarla yakalama.
- Renk kodlu profesyonel Excel denetim raporu çıktısı (`.xlsx`).

#### 3. ⚙️ Boru Et Kalınlığı Negatif Tolerans İyileştirmeleri
- BOTAŞ standardı için negatif toleransın 2 defa düşülmesi önlendi ve tolerans kutusu BOTAŞ seçildiğinde gizlendi.
- ASME B31.8 / B31.4 / B31.3 standartlarında kullanıcının `%0` girmesi durumunda sistemin bunu kesin bir 0% kabul etmesi sağlandı.

---

## Önceki Sürümler / Previous Versions

### Sürüm Özeti - v1.9.0 (2026-08-31)
- BOTAŞ F=0.50 İstasyon Et Kalınlığı Ayrımı (75 Bar vs 82.5 Bar)
- Kullanıcı Tanımlı Korozyon Payı (*Corrosion Allowance* - c, mm)
- Kullanıcı Tanımlı Negatif Tolerans (%) ve 5 Sütunlu Sonuç Kartı

---

## Önceki Sürümler / Previous Versions

### 🇹🇷 Türkçe Özet

API 5L Pipe QA/QC Suite **v1.4.0** sürümü ile birlikte boru üretim yöntemine göre dinamik API 5L Tablo 11 tolerans otomasyonu ve X46 malzeme kalitesi eklenmiştir:

#### 1. 🏭 Boru Üretim Yöntemine Bağlı API 5L Tablo 11 Tolerans Otomasyonu
- **ASME B31.8 / ASME B31.4 + API 5L:** İmalat yöntemine (SMLS, ERW/HFW, SAWH, SAWL) göre:
  - **SMLS:** -%12.5
  - **ERW / HFW:** -%10.0
  - **SAWH / SAWL ($D > 20''$):** -%8.0
  - **SAWH / SAWL ($D \le 20''$):** -%10.0
- ASME B36.10M nominal schedule seçiminde bu tolerans payı düşülerek $t_{\text{nom}} \times (1 - \text{tol}) \ge t_{\text{req}}$ şartı denetlenir.

#### 2. ⚙️ ASME B31.3 El ile Negatif Tolerans Girişi
- Proses borulaması için negatif tolerans zorunlu olup kullanıcı dilediği tolerans oranını (%) el ile serbestçe girebilir (Varsayılan: %12.5).

#### 3. 🧪 Paslanmaz Çelik Opsiyonel Tolerans Yönetimi
- ASME B31.8 / B31.4 altında paslanmaz çelikler için negatif tolerans opsiyonel checkbox ile yönetilebilir.

#### 4. 🏷️ API 5L X46 Malzeme Kalitesi Eklendi
- Tasarım aracına **API 5L X46 (L320 - SMYS: 46400 psi / 320 MPa)** kalitesi eklendi.

---

## Önceki Sürümler / Previous Versions

### Sürüm Özeti - v1.3.0 (2026-08-23)

#### 1. 💬 Kullanıcı Geri Bildirim, Hata / Öneri & İletişim Modülü
- **Geliştirici İletişimi:** Doğrudan `omer.erbas@botas.gov.tr` (Ömer ERBAŞ - BOTAŞ) adresine yönlendirilen entegre geri bildirim sistemi.
- **Otomatik Tanı ve Sistem Raporu:** Matriste o an seçili borunun özellikleri (çap, et kalınlığı, çelik kalitesi, basınç), işletim sistemi ve sürüm bilgisi tek tıkla e-postaya veya tanı raporuna eklenir.
- **3 İletişim Yöntemi:** Varsayılan e-posta istemcisi (`mailto:`), panoya kopyalama ve GitHub Issues desteği.

#### 2. 🛠️ Boru Çapı ve Çoklu Standart Hesaplama Düzeltmeleri
- Et kalınlığı formundaki kaçış karakterleri temizlenerek 24" ($610.0\text{ mm}$) ve diğer çapların ASME B31.3 hesaplamalarında doğru işletilmesi sağlandı.
- Et kalınlığı aracındaki çap seçim kutusu veritabanındaki 35 standart çapın tamamını listeleyecek şekilde dinamikleştirildi.

---

## Önceki Sürümler / Previous Versions

### Sürüm Özeti - v1.2.0 (2026-08-22)

#### 1. 📐 Çoklu Standart Et Kalınlığı & Schedule Seçim Motoru
- **BOTAŞ Şartnamesi:** Hat ve İstasyon boruları ayrımı, korozyon payı ($c$) ve %12.5 fabrika et kalınlığı toleransı ($t_{\text{nom}} \times 0.875 \ge t_{\text{req}}$) entegre edildi.
- **ASME B31.8 / ASME B31.4:** $t = \frac{P \cdot D}{2 \cdot S \cdot F \cdot E \cdot T} + c$ formülasyonu ve ASME B36.10M / B36.19M nominal schedule eşleştirmesi.
- **ASME B31.3 (Proses Borulaması):** $t = \frac{P \cdot D}{2(S \cdot E \cdot W + P \cdot Y)} + c$ formülasyonu ($W=1.0$, $Y=0.40$).
- Bilinmeyen boru çaplarında oluşabilecek NameError hatalarına karşı güvenli fallback mimarisi.

#### 2. 🧪 Paslanmaz ve Dubleks Çelik Malzeme Kütüphanesi & ASME B36.19M
- Standart malzeme listesine **SS 304 / 304L**, **SS 316 / 316L**, **SS 321**, **Duplex 2205** ve **Super Duplex 2507** kaliteleri eklendi.
- Paslanmaz çelikler seçildiğinde otomatik olarak **ASME B36.19M** standardındaki paslanmaz schedule değerleri (5S, 10S, 40S, 80S) devreye girer.

#### 3. 🔍 40+ Parametreli Kapsamlı Fabrika Kabul & Doğrulama Motoru
- Doğrulama modülü 10 parametreden 40+ parametreye genişletildi:
  - 🧪 **Kimyasal Analiz:** C, Mn, P, S, Nb, V, Ti, N, Karbon Eşdeğerleri (CE_IIW, CE_Pcm).
  - 📐 **Boyut ve Toleranslar:** Dış Çap, Et Kalınlığı Min/Max, Çevre, Ovalite, Diklik, Çatılaşma.
  - 💥 **Mekanik Değerler:** Yield Min/Max, Tensile Min/Max, Y/T Oranı, Uzama.
  - 🔬 **Kaynak Geometrisi:** Radial Offset, Misalignment, Kaynak Dikişi Yüksekliği (İç/Dış).
  - 🛡️ **Tokluk ve Testler:** CVN Çentik Darbe, DWTT Yırtılma, Artık Gerilme, Sertlik, Flattening, Tamir Kaynağı.
  - ⚖️ **Ağırlık ve Hidrostatik:** Nominal Birim Ağırlık, $D/t$ Oranı, Fabrika Hidrostatik Test Basıncı.

#### 4. 🎨 Matris Tablosunda Yüksek Okunabilirlik ve Crosshair Odaklanması
- **Kontrast ve Renk Çakışması Giderildi:** Seçili sütun başlıkları ve hücrelerindeki renk çakışmaları tamamen çözülerek yüksek kontrastlı okunabilirlik sağlandı.
- **Crosshair (Kesişim) Odaklanması:** Fareyle satırlar üzerinde gezinirken seçili sütun ile kesişen hücre aydınlatılarak göz yorulması engellendi.
- **Yapışkan Üst Sütun Seçim Satırı:** Tablonun tepesinde sabitlenen boru seçim rozetleri (`★ SEÇİLİ BORU`).
- **Hızlı Sütun Gezgini:** Tablo araç çubuğuna `◀ Önceki` ve `Sonraki ▶` butonları ve klavye yön tuşları ($\leftarrow$ / $\rightarrow$) ile borular arası anında geçiş desteği.

#### 5. 📊 İki Dilli (TR / EN) Excel Raporu & 2 Ondalık Basamak Standardı
- Excel dışa aktarımında 40+ satırın tamamı seçilen dile göre Türkçe veya İngilizce standart maddeleriyle doldurulur.
- Tüm mühendislik hesaplama sonuçları ve toleranslar standart olarak 2 ondalık basamağa (`.toFixed(2)`) yuvarlanarak sunulur.

---

### 🇬🇧 English Summary

API 5L Pipe QA/QC Suite **v1.2.0** introduces comprehensive pipeline engineering upgrades, full multi-standard wall thickness calculations, expanded material grades, 40+ parameter verification, and ergonomic table navigation:

#### 1. 📐 Multi-Standard Wall Thickness & Schedule Selection Engine
- **BOTAŞ Specification:** Line Pipe vs. Station Pipe criteria, corrosion allowance ($c$), and %12.5 mill undertolerance ($t_{\text{nom}} \times 0.875 \ge t_{\text{req}}$).
- **ASME B31.8 / ASME B31.4 (Gas & Liquid Transmission):** Full $t = \frac{P \cdot D}{2 \cdot S \cdot F \cdot E \cdot T} + c$ calculation with nominal schedule selection.
- **ASME B31.3 (Process Piping):** $t = \frac{P \cdot D}{2(S \cdot E \cdot W + P \cdot Y)} + c$ formulation ($W=1.0$, $Y=0.40$).
- Safe fallback architecture preventing NameError on custom/non-standard diameters.

#### 2. 🧪 Stainless Steel & Duplex Material Library & ASME B36.19M Schedules
- Added **SS 304 / 304L**, **SS 316 / 316L**, **SS 321**, **Duplex 2205**, and **Super Duplex 2507** material grades.
- Automatic switching to **ASME B36.19M** schedules (5S, 10S, 40S, 80S) for stainless steels.

#### 3. 🔍 40+ Parameter Quality Acceptance & Verification Engine
- Complete verification across 6 inspection categories:
  - 🧪 **Chemical Analysis:** C, Mn, P, S, Nb, V, Ti, N, Carbon Equivalents (CE_IIW, CE_Pcm).
  - 📐 **Dimensional Tolerances:** Diameter End/Body, Wall Thickness Min/Max, Circumference, Ovality, Squareness, Peaking.
  - 💥 **Mechanical Properties:** Yield Min/Max, Tensile Min/Max, Y/T Ratio, Elongation.
  - 🔬 **Weld & Geometry:** Radial Offset, Misalignment, Weld Seam Height (Inside/Outside).
  - 🛡️ **Toughness & Tests:** CVN Impact Energy, DWTT Fracture Appearance, Residual Stress, Hardness, Flattening, Weld Repair.
  - ⚖️ **Weights & Hydrostatic:** Nominal Weight, $D/t$ Ratio, Hydrostatic Mill Test Pressure.

#### 4. 🎨 Enhanced Matrix Ergonomics & Crosshair Highlighting
- **High-Contrast Readability:** Eliminated overlapping color styles in active headers and body cells.
- **Crosshair Focus Highlight:** Live intersection spotlight when hovering rows over the active column.
- **Sticky Top Selection Row:** Pinned column selection badges (`★ SEÇİLİ BORU`).
- **Quick Column Navigation:** Toolbar buttons (`◀ Prev`, `Next ▶`) and keyboard arrow key ($\leftarrow$ / $\rightarrow$) shortcuts.

#### 5. 📊 Bilingual (TR/EN) Excel Exporter & 2-Decimal Precision
- Full Turkish and English engineering remarks across all 40+ rows.
- Standardized 2-decimal rounding (`.toFixed(2)`) across UI and Excel reports.

---

### 📦 Downloads / İndirme

- **Windows x64 (.exe):** [Download API-5L-Pipe-Windows-x64.exe](https://github.com/SLedgehammer-dev12/API-5L-Pipe/releases/download/v1.2.0/API-5L-Pipe-Windows-x64.exe)
- **macOS (.dmg):** [Download API-5L-Pipe-macOS.dmg](https://github.com/SLedgehammer-dev12/API-5L-Pipe/releases/download/v1.2.0/API-5L-Pipe-macOS.dmg)
