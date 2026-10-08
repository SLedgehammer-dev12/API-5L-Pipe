# Sürüm Notları / Release Notes - v2.10.0

## 🚀 API 5L PSL1/PSL2 & BOTAŞ Boru Kalite Güvence, Et Kalınlığı Tasarım ve Akıllı ITP Denetim Süiti (v2.10.0)

Bu sürüm (**v2.10.0**), **satır bazlı Test Frekansı sütunu**, **SAWL boyuna dikiş 3D imalat simülasyonu** ve **API 5L serbest seçimde Operating Pressure girişi**ni getirir.

---

### 🌟 v2.10.0 ile Gelen Başlıca Yenilikler

1. **🧪 Test Frekansı Sütunu (Matris + Excel + Rapor):**
   - "Standart & Mühendislik Açıklamaları" sütununun sağında, en sağda sabit yeni sütun.
   - Her satırın testine karşılık gelen frekans; boru standartları farklıysa `BOTAŞ: … | API 5L PSL2: …` biçiminde birleşir. Eşleşmeyenlerde "—".
   - Ayrı "🧪 TEST FREKANSI" bölümü de korunur.

2. **📏 SAWL Boyuna Dikiş Kartı (3D Canlı Simülasyon):**
   - SAWL/LSAW seçildiğinde artık spiral kart değil, **boyuna dikiş kartı** açılır.
   - Plakanın rulolarla silindire bükülmesi, tek boyuna dikiş, iç/dış SAW torçları, kıvılcımlar, ölçü okları ve 2D açınım (plaka genişliği = π·D_mid).
   - **Düzeltme:** SAWH spiral kartı artık yalnız SAWH için açılır.

3. **⚙️ API 5L Serbest Seçimde Operating Pressure:**
   - Yeni "Çalışma Basıncı / Operating Pressure (bar)" alanı (yalnız API PSL1/PSL2 serbest seçimde).
   - Girilen basınçla **Operating pressure / SMYS** oranı hesaplanır ve hücre dolar.

4. **🧪 Deneme Koşusu:** **115/115 senaryo başarılı**; birim testleri **78/78** geçer, ruff temiz.

---

### 💻 İndirme Bağlantıları (v2.10.0)

- **🪟 Windows (x64):**  
  [**`API-5L-Pipe-Windows-x64-v2.10.0.exe` İndir**](https://github.com/SLedgehammer-dev12/API-5L-Pipe/releases/download/v2.10.0/API-5L-Pipe-Windows-x64-v2.10.0.exe)  
  *Tek dosyadır, kurulum gerektirmez. Doğrudan çift tıklayarak çalıştırabilirsiniz.*

- **🍏 macOS (Apple Silicon M1/M2/M3/M4 & Intel):**  
  [**`API-5L-Pipe-macOS-v2.10.0.dmg` İndir**](https://github.com/SLedgehammer-dev12/API-5L-Pipe/releases/download/v2.10.0/API-5L-Pipe-macOS-v2.10.0.dmg)  
  *Disk kalıbını açıp `API-5L-Pipe.app` uygulamasını Applications klasörüne sürükleyin.*

---

# Sürüm Notları / Release Notes - v2.9.5

## 🚀 API 5L PSL1/PSL2 & BOTAŞ Boru Kalite Güvence, Et Kalınlığı Tasarım ve Akıllı ITP Denetim Süiti (v2.9.5)

Bu sürüm (**v2.9.5**), **test ve ölçüm frekansı (sıklık/numune) kontrolünü** QA/QC matrisi, Fabrika Test Doğrulama motoru, resmi rapor ve Excel çıktısına ekler. Frekanslar **çap, malzeme kalitesi, PSL seviyesi, imalat yöntemi ve standarda** göre otomatik belirlenir.

---

### 🌟 v2.9.5 ile Gelen Başlıca Yenilikler

1. **🧪 QA/QC Matrisi "Test Frekansı" Bölümü:**
   - Her test için gerekli sıklık/numune sayısı matriste ayrı bölüm olarak gösterilir.
   - Çapa/prosese göre değişir: 48" X65 SAWH BOTAŞ → **Artık Stres (her döküm)** + **DWTT**; 12" X52 ERW → düzleştirme (DWTT/artık stres yok); PSL1 → CVN/DWTT yok.

2. **📋 Doğrulama Motorunda Frekans Referansları:**
   - Fabrika Test Doğrulama sekmesinde ve resmi raporda "Şartname Test Frekansları" tablosu.
   - PASS/FAIL sayıları ve parametre toplamı etkilenmez (yanlış RED üretmez).

3. **📄 Rapor & Excel:** Resmi rapor ve matris Excel çıktısına "Test Frekansı" blokları eklendi.

4. **🧪 Deneme (Trial) Koşusu:** 16 çap × kalite × proses × BOTAŞ/API PSL1/PSL2 + 10'luk presetler + kural senaryoları → **107/107 başarılı**.

---

### 💻 İndirme Bağlantıları (v2.9.5)

- **🪟 Windows (x64):**  
  [**`API-5L-Pipe-Windows-x64-v2.9.5.exe` İndir**](https://github.com/SLedgehammer-dev12/API-5L-Pipe/releases/download/v2.9.5/API-5L-Pipe-Windows-x64-v2.9.5.exe)  
  *Tek dosyadır, kurulum gerektirmez. Doğrudan çift tıklayarak çalıştırabilirsiniz.*

- **🍏 macOS (Apple Silicon M1/M2/M3/M4 & Intel):**  
  [**`API-5L-Pipe-macOS-v2.9.5.dmg` İndir**](https://github.com/SLedgehammer-dev12/API-5L-Pipe/releases/download/v2.9.5/API-5L-Pipe-macOS-v2.9.5.dmg)  
  *Disk kalıbını açıp `API-5L-Pipe.app` uygulamasını Applications klasörüne sürükleyin.*

---

# Sürüm Notları / Release Notes - v2.9.0

## 🚀 API 5L PSL1/PSL2 & BOTAŞ Boru Kalite Güvence, Et Kalınlığı Tasarım ve Akıllı ITP Denetim Süiti (v2.9.0)

Bu sürüm (**v2.9.0**), kimyasal bileşim modülünü **BOTAŞ 5120 R7 Tablo-1** ile birebir uyumlu hale getirir: **X52 ve üzeri Nb minimumu**, **CE_IIW 0.40 / CE_Pcm 0.22**, **not a/b (Nb+V+Ti)** ve **not c (C azalmasına bağlı Mn telafisi)** artık uygulanır; Tablo-1 dışı kaliteler API 5L'e göre değerlendirilir.

---

### 🌟 v2.9.0 ile Gelen Başlıca Yenilikler

1. **🧪 BOTAŞ 5120 R7 Tablo-1 Kimyasal Uyumu:**
   - **Nb:** Gr.B / X42 / X46 → yalnız max **0.050**; **X52 ve üzeri → 0.015–0.050** (minimum sütunda görünür).
   - **X80:** hatalı Nb max `0.06` kaldırıldı → **0.050**; V max **0.050**, Ti max **0.040**.
   - **CE (Madde 3.2.1):** tüm Tablo-1 kalitelerinde **CE_IIW ≤ 0.40**, **CE_Pcm ≤ 0.22**.

2. **📏 Tablo-1 Dipnotları:**
   - **Not a/b:** Gr.B için **Nb+V+Ti ≤ 0.06%**, X42 ve üzeri için **≤ 0.15%** denetlenir.
   - **Not c:** C max'tan her tam **0.01%** azalma için Mn üst sınırına **+0.05%** eklenir; tavan Gr.B–X52 **1.65%**, X56–X65 **1.75%**, X70+ **2.00%**.

3. **🔄 Tablo-1 Dışı Kaliteler → API 5L:**
   - **X90/X100/X120:** API 5L PSL2 Tablo 5 (M) — C 0.10, Mn 2.10, Ti 0.06, N 0.015, Nb+V+Ti ≤ 0.15, CE_Pcm 0.25.
   - **GRADE A:** API 5L PSL1 Tablo 4 — C 0.22, Mn 0.90, P/S 0.030, mikroalaşım ve CE yok.

4. **🏷️ Dinamik Nb Etiketi:** Seçili borularda minimum yoksa başlık **"Max %"**, varsa **"Min%-Max%"** (matris, Excel ve rapor).

5. **📐 Ovalite Yuvarlama:** Ovalite uç/gövde değerleri **yüzdelik basamağa (2 hane)** yuvarlanır (örn. `0.45225 → 0.45`).

6. **🧪 Testler:** `test_61`–`test_65` eklendi. **73/73** birim testi geçer, ruff temiz.

---

### 💻 İndirme Bağlantıları (v2.9.0)

- **🪟 Windows (x64):**  
  [**`API-5L-Pipe-Windows-x64-v2.9.0.exe` İndir**](https://github.com/SLedgehammer-dev12/API-5L-Pipe/releases/download/v2.9.0/API-5L-Pipe-Windows-x64-v2.9.0.exe)  
  *Tek dosyadır, kurulum gerektirmez. Doğrudan çift tıklayarak çalıştırabilirsiniz.*

- **🍏 macOS (Apple Silicon M1/M2/M3/M4 & Intel):**  
  [**`API-5L-Pipe-macOS-v2.9.0.dmg` İndir**](https://github.com/SLedgehammer-dev12/API-5L-Pipe/releases/download/v2.9.0/API-5L-Pipe-macOS-v2.9.0.dmg)  
  *Disk kalıbını açıp `API-5L-Pipe.app` uygulamasını Applications klasörüne sürükleyin.*

---

# Sürüm Notları / Release Notes - v2.8.3

## 🚀 API 5L PSL1/PSL2 & BOTAŞ Boru Kalite Güvence, Et Kalınlığı Tasarım ve Akıllı ITP Denetim Süiti (v2.8.3)

Bu sürüm (**v2.8.3**), **API 5L Tablo 2/3 Uyumlu Proses Seçenekleri**, **Gerçekçi Numune Çizimleri** (Charpy V-çentik, çekme şerit, yuvarlak çubuk) ve **İçi Boş (Cidarlı) Artık Stres Ring Animasyonu** ile ITP görsellerini ve proses seçimini standarda tam uyumlu hale getirir.

---

### 🌟 v2.8.3 ile Gelen Başlıca Yenilikler

1. **🧭 API 5L Tablo 2/3 Uyumlu Proses Seçenekleri:**
   - **PSL 1:** SMLS, ERW/HFW, **SAWH, SAWL, COW** (Tablo 2, PSL 1'de kaynaklı proseslere izin verir).
   - **PSL 2 – Teslim M:** ERW/HFW, SAWH, SAWL, **COW** (SMLS geçerli değil — Tablo 3).
   - **PSL 2 – N/Q/R:** SMLS + tüm kaynaklı prosesler.
   - Modal proses listesine **SAWL** ve **COW** eklendi (önceden DOM'da hiç yoktu, bu yüzden görünemiyordu); wall-thickness sekmesine COW eklendi.

2. **📐 Gerçekçi Numune Çizimleri (ortoğrafik mühendislik çizimi):**
   - **Charpy V-çentik:** gerçek V-çentik (45°, 2 mm, **r = 0,25 mm**, 8 mm ligaman), büyütülmüş kesit detayı, **40 mm örs açıklıklı darbe düzeni** ve **Çizelge 22 alt boyutları** — seçili boyut vurgulu, PSL1'de "zorunlu değil" rozeti.
   - **Çekme şerit (38,1 mm × t):** tutma bölgeleri, 50 mm mastar çizgileri, kaynaklı boruda **enine kaynak + ITAB**, dinamik **t**, boru kesitinde numune alım inset'i.
   - **Yuvarlak çubuk:** dişli uçlar + omuz yarıçapı, **Tablo 21'e göre dinamik mastar çapı** (6,4 / 8,9 / 12,7 mm), gauge ortasında enine kaynak, cidardan alım inset'i (**d ≤ t**).

3. **🪚 İçi Boş (Cidarlı) Artık Stres Ring Animasyonu:**
   - Ring artık katı disk değil: delik **geçirgen (içi boş)**, **iç cidar yüzeyi** görünür.
   - Kesme/açılma **cidardan ve 150 mm boyunca**; açılan kenarlarda **amber cidar kesit yüzeyleri** ayrılır.
   - Faz A'daki ayrılan halka parçası her iki ucunda **içi boş ring kesiti** gösterir.

4. **🛠️ Düzeltmeler:**
   - **Tablo 21 tutarlılığı:** ITP satır metni artık motorla aynı kaynağı kullanır (örn. 24" t=19,0 mm → **6,4 mm**; önceki metin 8,9 mm diyordu).
   - **BOTAŞ 3.3.9 kapsamı:** artık stres yalnız ark kaynaklı SAW (SAWH/SAWL/LSAW) ve COW için hesaplanır; ERW/HFW ve SMLS hariç. API 5L'de "TEST YOK".
   - Ring figüründeki mükerrer yorum ve iç cidar yayı geometrisi düzeltildi.

5. **🧪 Testler:**
   - `test_59_process_availability_and_residual_stress_scope` ve `test_60_round_bar_dia_table21_consistency` eklendi. **67/67 test** geçer, ruff temiz.

---

### 💻 İndirme Bağlantıları (v2.8.3)

- **🪟 Windows (x64):**  
  [**`API-5L-Pipe-Windows-x64-v2.8.3.exe` İndir**](https://github.com/SLedgehammer-dev12/API-5L-Pipe/releases/download/v2.8.3/API-5L-Pipe-Windows-x64-v2.8.3.exe)  
  *Tek dosyadır, kurulum gerektirmez. Doğrudan çift tıklayarak çalıştırabilirsiniz.*

- **🍏 macOS (Apple Silicon M1/M2/M3/M4 & Intel):**  
  [**`API-5L-Pipe-macOS-v2.8.3.dmg` İndir**](https://github.com/SLedgehammer-dev12/API-5L-Pipe/releases/download/v2.8.3/API-5L-Pipe-macOS-v2.8.3.dmg)  
  *Disk kalıbını açıp `API-5L-Pipe.app` uygulamasını Applications klasörüne sürükleyin.*

---

# Sürüm Notları / Release Notes - v2.8.2

## 🚀 API 5L PSL1/PSL2 & BOTAŞ Boru Kalite Güvence, Et Kalınlığı Tasarım ve Akıllı ITP Denetim Süiti (v2.8.2)

Bu sürüm (**v2.8.2**), **Standarta Göre Özelleşen Mühendislik Açıklamaları**, **Artık Stres Formülünde Ortalama Çap (Dₘ = D − t) Düzeltmesi** ve **OCR Et Kalınlığı Fallback Düzeltmesi** ile matrisin seçilen Değerlendirme Kriteri / Şartname'ye tam uyumlu açıklama üretmesini sağlar.

---

### 🌟 v2.8.2 ile Gelen Başlıca Yenilikler

1. **🧭 Standarta Göre Özelleşen Mühendislik Açıklamaları:**
   - Matristeki "Standart & Mühendislik Açıklamaları" sütunu artık **her borunun kendi seçimine** göre üretilir (BOTAŞ / API 5L PSL1 / API 5L PSL2).
   - **CVN/Çentik Darbe:** BOTAŞ → **Tablo 3, -20°C**; API 5L PSL2 → **Çizelge 8, 0°C**; PSL1 → zorunlu değil.
   - **Boyutsal & kaynak toleransları:** Çap toleransı, çevre toleransı, ovalite, radial offset, kaynak yüksekliği, misalignment, tepeleşme ve diklik açıklamaları; değerlerin farklılaştığı her hücrede standarta özel referans/limit metni gösterir (örn. BOTAŞ 0.75 katsayılı radial offset 1.125 mm / API 1.5 mm).
   - **Mekanik & test referansları:** Kimyasal, sertlik, DWTT, Y/T oranı, hidrostatik alt sınır, akma-çekme, tamir kaynağı, tasarım faktörü, et kalınlığı ve SMYS açıklamaları standarta göre ayrıştırıldı.
   - **Karışık standartlı projeler:** Tek açıklama sütununda `BOTAŞ: … | API 5L PSL2: …` biçiminde etiketli birleşik metin gösterilir.

2. **📐 Artık Stres Formülü — Ortalama Çap (Dₘ = D − t):**
   - BOTAŞ Madde 3.3.9 halka açılma formülü, dış çap $D$ yerine halka ortalama çapı $D_m = D - t$ ile hesaplanır.
   - $\Delta_{\text{max}} = \frac{12.566 \cdot D_m^2 \cdot 0.10 \cdot \text{SMYS}}{E \cdot t}$; 48" X65 SAWH t=14.30 mm için Δ max **286.95 mm** (önceki 293.80 mm yerine).

3. **🧪 OCR Et Kalınlığı Fallback Düzeltmesi:**
   - Yüklenen ITP'den et kalınlığı okunamadığında ASME B36.10 schedule değerleri yerine, tespit edilen çapa ait **BOTAŞ standart et kalınlıkları** aranır.

4. **🧾 Tepeleşme Açıklaması Düzeltmesi:**
   - BOTAŞ için hatalı "1.50 mm sabit" ifadesi kaldırıldı; motorun ürettiği **3.2 mm** değeriyle uyumlu hale getirildi.

5. **🧪 Testler:**
   - Yeni `test_58_standard_conditional_explanations` regresyon testi (standart bazlı açıklama + değer tutarlılığı). Toplam **65/65 test** geçer, ruff temiz.

---

### 💻 İndirme Bağlantıları (v2.8.2)

- **🪟 Windows (x64):**  
  [**`API-5L-Pipe-Windows-x64-v2.8.2.exe` İndir**](https://github.com/SLedgehammer-dev12/API-5L-Pipe/releases/download/v2.8.2/API-5L-Pipe-Windows-x64-v2.8.2.exe)  
  *Tek dosyadır, kurulum gerektirmez. Doğrudan çift tıklayarak çalıştırabilirsiniz.*

- **🍏 macOS (Apple Silicon M1/M2/M3/M4 & Intel):**  
  [**`API-5L-Pipe-macOS-v2.8.2.dmg` İndir**](https://github.com/SLedgehammer-dev12/API-5L-Pipe/releases/download/v2.8.2/API-5L-Pipe-macOS-v2.8.2.dmg)  
  *Disk kalıbını açıp `API-5L-Pipe.app` uygulamasını Applications klasörüne sürükleyin.*

---

## 🚀 API 5L PSL1/PSL2 & BOTAŞ Boru Kalite Güvence, Et Kalınlığı Tasarım ve Akıllı ITP Denetim Süiti (v2.8.0)

Bu sürüm (**v2.8.0**), **Telif Hassasiyeti Temizliği** (program çalışması için gerekli olmayan örnek ITP/şartname/Excel dokümanlarının depodan kaldırılması) ve **Artık Stres (Ring Kesme) Testi Canlı Animasyonu** ile birlikte önemli sürüm iyileştirmeleri sunmaktadır.

---

### 🌟 v2.8.0 ile Gelen Başlıca Yenilikler

1. **🪚 Artık Stres (Ring Kesme) Testi Animasyonu:**
   - 2D/3D şematik sekmesine spiral/düz dikişli ark kaynaklı (SAWH/SAWL/LSAW) borular için BOTAŞ Madde 3.3.9'a uygun canlı animasyon eklendi.
   - **150 mm halka kesimi**, **kaynak karşısından çentik** ve **halka açılması (Δ boşluğu)** adımları seçili borunun gerçek ölçüleriyle (D, t, Δ max) gösterilir.
   - ITP listesindeki "Artık Stres Testi (Residual Stress)" satırının numune çizimi doğru `residual_stress_ring` figürüyle düzeltildi (önceden yanlışlıkla `flattening` kullanılıyordu).

2. **🧹 Telif Hassasiyeti Temizliği:**
   - Programın çalışması için gerekli olmayan ve telif hakkı riski taşıyan dokümanlar GitHub deposundan kaldırıldı:
     - `itp_sample_library/` örnek ITP PDF'leri (26 doküman)
     - `5120_R7.pdf` (BOTAŞ şartname)
     - `Pipe Fittings Flange Calc *.xlsx` çalışma kitapları
     - `tests/sample_vendor_itp.pdf`
   - Bu dosyaların yeniden commit edilmemesi için `.gitignore` güncellendi.

3. **🔧 Artık Stres Formül Düzeltmesi (BOTAŞ 3.3.9):**
   - **Ortalama çap kullanımı:** Artık stres halka açılma formülü artık dış çap $D$ yerine halka ortalama çapı $D_m = D - t$ kullanıyor (BOTAŞ Şartnamesi Madde 3.3.9). Bu, Δ max hesaplamasında ~2.4% düzeltme sağlar.
   - **Formül:** $\Delta_{\text{max}} = \frac{12.566 \cdot D_m^2 \cdot 0.10 \cdot \text{SMYS}}{E \cdot t}$ burada $D_m = D - t$.

4. **🧪 Test & Lint İyileştirmeleri:**
   - Örnek ITP kütüphanesi olmadan golden master PDF testleri zarifçe atlanır; JSON bazlı golden master testleri çalışmaya devam eder.
   - `test_regression_golden.py` mükerrer fonksiyon tanımlarından (F811) temizlendi.
   - CI ruff lint kontrolü tamamen temiz.

5. **🧹 Telif Hassasiyeti Temizliği:**
   - Programın çalışması için gerekli olmayan ve telif hakkı riski taşıyan dokümanlar GitHub deposundan kaldırıldı:
     - `itp_sample_library/` örnek ITP PDF'leri (26 doküman)
     - `5120_R7.pdf` (BOTAŞ şartname)
     - `Pipe Fittings Flange Calc *.xlsx` çalışma kitapları
     - `tests/sample_vendor_itp.pdf`
   - Bu dosyaların yeniden commit edilmemesi için `.gitignore` güncellendi.

---

### 💻 İndirme Bağlantıları (v2.8.0)

- **🪟 Windows (x64):**  
  [**`API-5L-Pipe-Windows-x64-v2.8.0.exe` İndir**](https://github.com/SLedgehammer-dev12/API-5L-Pipe/releases/download/v2.8.0/API-5L-Pipe-Windows-x64-v2.8.0.exe)  
  *Tek dosyadır, kurulum gerektirmez. Doğrudan çift tıklayarak çalıştırabilirsiniz.*

- **🍏 macOS (Apple Silicon M1/M2/M3/M4 & Intel):**  
  [**`API-5L-Pipe-macOS-v2.8.0.dmg` İndir**](https://github.com/SLedgehammer-dev12/API-5L-Pipe/releases/download/v2.8.0/API-5L-Pipe-macOS-v2.8.0.dmg)  
  *Disk kalıbını açın `API-5L-Pipe.app` uygulamasını Applications klasörüne sürükleyin.*

---

### 🔧 v2.8.0 Hotfix Düzeltmeleri (Bu Sürümde Dahil)

- **OCR Engine Fallback:** ITP yükleme sırasında et kalınlığı tablo okunamazsa, ASME B36.10 schedule değerleri yerine **BOTAŞ standart et kalınlıkları** (seçilen çapa göre `botas_thk` tablosundan) aranır.
- **Artık Stres Formülü:** Dış çap $D$ yerine halka ortalama çapı $D_m = D - t$ kullanılıyor (BOTAŞ 3.3.9). Δ max değerleri ~2.4% azaldı (daha gerçekçi).
- **Formül Belgelenmesi:** Tüm ITP notları, rapor şablonları ve animasyon şemalarında formül $S = \frac{E \cdot t \cdot \Delta}{12.566 \cdot D_m^2}$ ile $D_m = D - t$ olarak güncellendi.
- **OCR Fallback:** Yüklenen ITP'den et kalınlığı okunamazsa, ASME B36.10 schedule listesi yerine o çap için **BOTAŞ standart et kalınlıkları** (`botas_thk` tablosu) aranır.

---

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