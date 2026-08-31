# Sürüm Notları / Release Notes - v1.9.0

## 🚀 API 5L PSL1/PSL2 & BOTAŞ Boru Kalite Güvence, Fabrika Kabul ve Çoklu Standart Et Kalınlığı Tasarım Yazılımı

Bu sürüm, **BOTAŞ 75 Bar ve 82.5 Bar İstasyon Borusu Et Kalınlıklarının Ayrıştırılmasını**, **Boru Et Kalınlığı Tasarım Aracı'nda Kullanıcı Tanımlı Korozyon Payı & Negatif İmalat Toleransı Esnekliğini** ve 48" istasyon borusu tavsiye düzeltmelerini içerir.

---

### 🌟 v1.9.0 ile Gelenler

1. **🏭 BOTAŞ F=0.50 İstasyon Et Kalınlığı Ayrımı (75 Bar vs 82.5 Bar):**
   - BOTAŞ standart veritabanında istasyon boruları için 75 bar (`0.50_ist_75bar`) ve 82.5 bar (`0.50_ist_82_5bar`) et kalınlıkları ayrıştırıldı.
   - Örn. 48" X65 istasyon borusu için: 75 Bar $\rightarrow$ **22.20 mm**, 82.5 Bar $\rightarrow$ **23.80 mm**.
   - Örn. 24" X65 istasyon borusu için: 75 Bar $\rightarrow$ **11.90 mm**, 82.5 Bar $\rightarrow$ **12.70 mm**.

2. **🛡️ Kullanıcı Tanımlı Korozyon Payı (*Corrosion Allowance* - c, mm):**
   - Boru Et Kalınlığı Tasarım Aracı'na korozyon payı serbest giriş kutusu ve hızlı seçim çipleri (`0 mm`, `1.0 mm`, `1.5 mm`, `3.0 mm`) eklendi.
   - Doğrudan $t_{\text{req}} = t_{\text{teorik}} + c$ hesabına bağlanarak nominal schedule seçimini etkiler.

3. **⚙️ Kullanıcı Tanımlı Negatif Tolerans (%):**
   - BOTAŞ, ASME B31.8 / B31.4 ve ASME B31.3 standartlarında negatif imalat toleransı kullanıcı tarafından doğrudan ayarlanabilir kılındı (`0%`, `8%`, `10%`, `12.5%` hazır butonlar).
   - Boş veya 0 bırakıldığında ilgili standardın fabrika toleransı (API 5L Tablo 11, BOTAŞ İstasyon %12.5) otomatik işletilir.

4. **📊 Geliştirilmiş 5 Sütunlu Sonuç Kartı:**
   - Tasarım sonuç kartında Teorik Kalınlık ($t$), Korozyon Payı ($+c$), Gereken Kalınlık ($t_{\text{req}}$), Seçilen Nominal ($t_{\text{nom}}$) ve Net Tolerans Sınırı net olarak gösterilir.

5. **🛠️ 48" İstasyon Borusu Tavsiye Düzeltmesi:**
   - 48" istasyon borusu seçiminde hat borusu değeri olan 20.60 mm yerine doğru şartname değeri olan 22.20 mm (75 bar) veya 23.80 mm (82.5 bar) getirilmesi sağlandı.

---

### 💻 İndirme Bağlantıları (v1.9.0)

- **🪟 Windows (x64):**  
  [**`API-5L-Pipe-Windows-x64-v1.9.0.exe` İndir**](https://github.com/SLedgehammer-dev12/API-5L-Pipe/releases/download/v1.9.0/API-5L-Pipe-Windows-x64-v1.9.0.exe)  
  *Tek dosyadır, kurulum gerektirmez. Doğrudan çift tıklayarak çalıştırabilirsiniz.*

- **🍏 macOS (Apple Silicon M1/M2/M3/M4 & Intel):**  
  [**`API-5L-Pipe-macOS-v1.9.0.dmg` İndir**](https://github.com/SLedgehammer-dev12/API-5L-Pipe/releases/download/v1.9.0/API-5L-Pipe-macOS-v1.9.0.dmg)  
  *Disk kalıbını açıp `API-5L-Pipe.app` uygulamasını Applications klasörüne sürükleyin.*