# Sürüm Notları / Release Notes - v1.7.0

## 🚀 API 5L PSL1/PSL2 & BOTAŞ Boru Kalite Güvence, Fabrika Kabul ve Çoklu Standart Et Kalınlığı Tasarım Yazılımı

Bu sürüm, **API 5L 47. baskı (Haziran 2026)** uyumunu tamamlar: **PSL1 boru seçimi**, **PSL2 teslim koşulları (R/N/Q/M)**, **otomatik karbon eşdeğeri hesabı**, **46 vs 47 baskı karşılaştırma notları** ve düzeltilmiş numune çizimleri.

---

### 🌟 v1.7.0 ile Gelen Yenilikler

1. **🧪 API 5L PSL1 Boru Seçimi:**
   - "Matrise Yeni Boru Sütunu Ekle" bölümüne **API 5L PSL1** seçeneği eklendi (BOTAŞ akışı aynen korundu).
   - PSL1 için Tablo 4 (kimyasal bileşim, seamless/welded farklı), Tablo 6 (yalnız min akma/çekme), Tablo 17/19 (ITP).
   - PSL1'de CVN / Y-T oranı / CE / DWTT **zorunlu değildir**; SAW üretimi yasaktır (Tablo 2).
   - "10 adet API 5L PSL1" ön ayar şablonu + `/api/presets/api5l-psl1-10`.

2. **📦 PSL2 Teslim Koşulu (R / N / Q / M):**
   - Boru sütunu eklerken teslim koşulu seçilir; kimyasal bileşim (Tablo 5) ve Y/T oranı (Tablo 7) teslim koşuluna göre alınır.
   - **M koşulu** yalnız kaynaklı boru (ERW/HFW, SAWH/SAWL) ve Grade B–X120 ile sınırlandırıldı (Tablo 3).
   - Kademe↔teslim koşulu çift yönlü filtrelenir (örn. X120 → yalnız M).

3. **🧮 Otomatik Karbon Eşdeğeri Hesabı:**
   - `CE_IIW` ve `CE_Pcm` formülleri (Denk. 2/3) uygulandı; doğrulama formuna Si/Cr/Mo/Ni/Cu/B alanları eklendi.
   - C > %0.12 ise CE_IIW, C ≤ %0.12 ise CE_Pcm kontrolü otomatik yapılır.
   - **t > 25.0 mm** kimyasal bileşim "anlaşmaya bağlıdır" (API 5L 9.2.3); PSL2 + SMLS + t > 20 mm CE anlaşmaya bağlı (Tablo 5 dipnot a).

4. **📘 API 5L 47. Baskı Düzeltmeleri (46. baskı ile karşılaştırma notlarıyla):**
   - **Y/T oranı:** ≤X80 için 0.93 (yalnız D > 323.9 mm, Tablo 7 dipnot c).
   - **CVN gövde:** Tablo 8'e göre çap + kademeye bağlı (27/40/54/68/81/95/108 J).
   - **CVN kaynak/ITAB:** 9.8.3.1 — HFW için 20 J (yeni), HFW dışı D<1422 & ≤X80 için 27 J.
   - **Çap toleransı (Tablo 10):** kaynaklı gövde ±3.2 mm tavanı ve ±0.005D (max 4.0) uygulandı.
   - **Hidrostatik (Tablo 26):** D≤141.3 → %60; standard test basıncı 20.5 MPa tavanı; API modunda alt sınır = standart test basıncı.
   - **Uzama:** Tablo 21'e göre yuvarlak çubuk numune alanı (Axc 130/65 mm²); SMLS t≥25 pozitif tolerans max(+3.7, +0.1t).
   - **CVN numune boyutu:** Tablo 22'ye göre çapa bağlı seçim.
   - **DWTT** yalnız kaynaklı D≥508 mm; **peaking** 9.10.5.1 (≤3.2 mm); et kalınlığı motorundaki "%8" kuralı kaldırıldı.

5. **🗂️ 46 vs 47 Baskı Karşılaştırma Notları (ⓘ):**
   - Her sonuç satırında **46. baskı orijinal değeri + 47. baskı güncel değeri + kaynak madde** bilgi ikonu ile gösterilir.
   - Gerçek 46→47 farkları (kaynak CVN HFW 20 J, düzleştirme 9.6 a)3), hidrotest kalibrasyonu 4 ay→6/12 ay, Tablo 5 M kimya) işaretlenir.

6. **🎨 Numune Çizimleri Düzeltildi:**
   - Çekme **şerit** numunesi paralel kenarlı tam cidar olarak (L0 = 50 mm, 38,1 mm genişlik, uç görünümü) yeniden çizildi.
   - Çekme **yuvarlak çubuk** numunesi tek silindirik mastar + dişli uçlar (d = 6,4/8,9/12,7 mm, L0 = 50 mm) olarak düzeltildi.
   - Referanslar 47. baskıya güncellendi (guided-bend 9.7, DWTT 9.9).

7. **🔢 Hesaplama Sonuçları 2 Ondalık:**
   - KPI kartları, MPa değerleri, çevre toleransları, operasyon basıncı/SMYS oranı ve rapor ağırlığı 2 ondalık gösterilir (PSI ve kimya limitleri korundu).

---

### 💻 İndirme Bağlantıları (v1.7.0)

- **🪟 Windows (x64):**  
  [**`API-5L-Pipe-Windows-x64-v1.7.0.exe` İndir**](https://github.com/SLedgehammer-dev12/API-5L-Pipe/releases/download/v1.7.0/API-5L-Pipe-Windows-x64-v1.7.0.exe)  
  *Tek dosyadır, kurulum gerektirmez. Doğrudan çift tıklayarak çalıştırabilirsiniz.*

- **🍏 macOS (Apple Silicon M1/M2/M3/M4 & Intel):**  
  [**`API-5L-Pipe-macOS-v1.7.0.dmg` İndir**](https://github.com/SLedgehammer-dev12/API-5L-Pipe/releases/download/v1.7.0/API-5L-Pipe-macOS-v1.7.0.dmg)  
  *Disk kalıbını açıp `API-5L-Pipe.app` uygulamasını Applications klasörüne sürükleyin.*