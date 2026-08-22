# Sürüm Notları / Release Notes - v1.2.0

## 🚀 API 5L PSL2 & BOTAŞ Boru Kalite Güvence, Fabrika Kabul ve Çoklu Standart Et Kalınlığı Tasarım Yazılımı

Bu sürüm, boru mühendisliği standartlarına tam uyumluluk sağlayan **Çoklu Standart Et Kalınlığı Hesaplama Motoru (BOTAŞ, ASME B31.8/B31.4, ASME B31.3)**, **Paslanmaz ve Dubleks Çelik Malzeme Kütüphanesi & ASME B36.19M Schedule Matrisi**, **40+ Parametreli Kapsamlı Fabrika Kabul & Doğrulama Motoru**, **İki Dilli (TR/EN) Excel Dışa Aktarma**, **2 Ondalık Hassasiyet Standardı** ve **Gelişmiş Tablo Ergonomisi & Crosshair (Kesişim) Odaklanması** geliştirmelerini içermektedir.

---

### 🌟 v1.2.0 ile Gelen Önemli Yenilikler ve İyileştirmeler

1. **📐 Çoklu Standart Et Kalınlığı & Schedule Seçim Motoru:**
   - **BOTAŞ Şartnamesi:** Hat ve İstasyon boruları ayrımı, korozyon payı ($c$) ve %12.5 fabrika et kalınlığı eksi toleransı ($t_{\text{nom}} \times 0.875 \ge t_{\text{req}}$) entegrasyonu.
   - **ASME B31.8 / ASME B31.4 (Gaz & Sıvı İletim Hatları):** $t = \frac{P \cdot D}{2 \cdot S \cdot F \cdot E \cdot T} + c$ formülasyonu ve ASME B36.10M / B36.19M nominal schedule eşleştirmesi.
   - **ASME B31.3 (Proses Borulaması):** $t = \frac{P \cdot D}{2(S \cdot E \cdot W + P \cdot Y)} + c$ formülasyonu ($W=1.0$, $Y=0.40$).
   - Bilinmeyen çaplar için güvenli fallback mekanizması (P0-1 NameError güvenliği).

2. **🧪 Paslanmaz ve Dubleks Çelik Malzeme Kütüphanesi:**
   - Standart malzeme listesine **SS 304 / 304L**, **SS 316 / 316L**, **SS 321**, **Duplex 2205** ve **Super Duplex 2507** kaliteleri eklendi.
   - Paslanmaz çelikler seçildiğinde otomatik olarak **ASME B36.19M** standardındaki paslanmaz schedule değerleri (5S, 10S, 40S, 80S) devreye girer.

3. **🔍 40+ Parametreli Kapsamlı Doğrulama ve Kabul Motoru:**
   - Doğrulama modülü 10 parametreden 40+ parametreye genişletildi:
     - 🧪 **Kimyasal Bileşim:** C, Mn, P, S, Nb, V, Ti, N, CE_IIW, CE_Pcm vb.
     - 📐 **Boyut & Toleranslar:** Dış Çap, Et Kalınlığı Min/Max, Çevre, Ovalite, Diklik, Çatılaşma.
     - 💥 **Mekanik Değerler:** Yield Min/Max, Tensile Min/Max, Y/T Oranı, Uzama.
     - 🔬 **Kaynak & Geometri:** Radial Offset, Misalignment, Kaynak Dikişi Yüksekliği (İç/Dış).
     - 🛡️ **Tokluk & Testler:** CVN Çentik Darbe, DWTT Yırtılma, Artık Gerilme, Sertlik, Flattening, Tamir Kaynağı.
     - ⚖️ **Ağırlık & Hidrostatik:** Nominal Birim Ağırlık, $D/t$ Oranı, Fabrika Hidrostatik Test Basıncı.

4. **🎨 Matris Tablosunda Yüksek Okunabilirlik ve Ergonomik Geliştirmeler:**
   - **Kontrast İyileştirmesi:** Seçili sütun başlıkları ve gövde hücrelerindeki renk çakışmaları giderildi; kristal netliğinde okunabilir tipografi sağlandı.
   - **Crosshair (Kesişim) Odaklanması:** Fareyle satırlar üzerinde gezinirken seçili sütun ile kesişen hücre aydınlatılarak 40+ parametre arasında göz yorulması engellendi.
   - **Yapışkan Üst Sütun Seçim Satırı:** Tablonun tepesinde sabitlenen boru seçim rozetleri (`★ SEÇİLİ BORU`).
   - **Hızlı Sütun Gezgini:** Tablo araç çubuğuna `◀ Önceki` ve `Sonraki ▶` butonları ve klavye yön tuşları ($\leftarrow$ / $\rightarrow$) ile borular arası anında geçiş desteği.

5. **📊 İki Dilli (TR / EN) Excel Raporlayıcı & 2 Decimal Yuvarlama:**
   - Excel dışa aktarımında 40+ satırın tamamı seçilen dile göre Türkçe veya İngilizce standart maddeleriyle doldurulur.
   - Tüm mühendislik hesaplama sonuçları ve toleranslar standart olarak 2 ondalık basamağa (`.toFixed(2)`) yuvarlanarak sunulur.

---

### 💻 İndirme Bağlantıları (v1.2.0)

- **🪟 Windows (x64):**  
  [**`API-5L-Pipe-Windows-x64.exe` İndir**](https://github.com/SLedgehammer-dev12/API-5L-Pipe/releases/download/v1.2.0/API-5L-Pipe-Windows-x64.exe)  
  *Tek dosyadır, kurulum gerektirmez. Doğrudan çift tıklayarak çalıştırabilirsiniz.*

- **🍏 macOS (Apple Silicon M1/M2/M3/M4 & Intel):**  
  [**`API-5L-Pipe-macOS.dmg` İndir**](https://github.com/SLedgehammer-dev12/API-5L-Pipe/releases/download/v1.2.0/API-5L-Pipe-macOS.dmg)  
  *Disk kalıbını açıp `API-5L-Pipe.app` uygulamasını Applications klasörüne sürükleyin.*
