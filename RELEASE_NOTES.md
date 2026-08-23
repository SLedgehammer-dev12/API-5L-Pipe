# Sürüm Notları / Release Notes - v1.4.0

## 🚀 API 5L PSL2 & BOTAŞ Boru Kalite Güvence, Fabrika Kabul ve Çoklu Standart Et Kalınlığı Tasarım Yazılımı

Bu sürüm, **Boru Üretim Yöntemine Bağlı API 5L Tablo 11 Negatif Tolerans Otomasyonu (SMLS, ERW, SAWH, SAWL)**, **ASME B31.3 El ile Negatif Tolerans Girişi**, **Paslanmaz Çelik Opsiyonel Tolerans Yönetimi**, **API 5L X46 Malzeme Kalitesi Entegrasyonu** ve arayüz dinamik güncellemelerini içermektedir.

---

### 🌟 v1.4.0 ile Gelen Önemli Yenilikler ve İyileştirmeler

1. **🏭 Boru Üretim Yöntemine Göre API 5L Tablo 11 Negatif Tolerans Otomasyonu:**
   - **ASME B31.8 / ASME B31.4 + API 5L Borusu Seçildiğinde:**
     - Kullanıcı arayüzden **Boru Üretim Yöntemini (SMLS, ERW/HFW, SAWH, SAWL)** ve **PSL Seviyesini (PSL 1 / PSL 2)** seçer.
     - **API Spec 5L Tablo 11** standart kuralları otomatik işletilir:
       - **Dikişsiz (SMLS):** **`-%12.5`**
       - **Boyuna Kaynaklı (ERW / HFW):** **`-%10.0`**
       - **Tozaltı Kaynaklı (SAWH / SAWL - $D > 20''$ / $24'' - 60''$):** **`-%8.0`**
       - **Tozaltı Kaynaklı (SAWH / SAWL - $D \le 20''$):** **`-%10.0`**
     - ASME B36.10M nominal schedule seçiminde bu tolerans payı düşülerek $t_{\text{nom}} \times (1 - \text{tol}) \ge t_{\text{req}}$ emniyet denetimi yapılır.

2. **⚙️ ASME B31.3 (Proses Borulaması) El İle Negatif Tolerans Girişi:**
   - ASME B31.3 seçildiğinde negatif tolerans **varsayılan olarak zorunlu/aktiftir**.
   - Kullanıcı dilediği **negatif tolerans oranını (%)** (varsayılan: `%12.5`, istenirse `%10.0`, `%15.0` vb.) serbestçe belirleyebilir.

3. **🧪 Paslanmaz ve Dubleks Çelikler İçin Opsiyonel Tolerans:**
   - ASME B31.8 / B31.4 altında paslanmaz çelik (SS 304, SS 316, Duplex 2205, Super Duplex 2507) seçildiğinde negatif tolerans **opsiyonel (checkbox)** olarak sunulur; kullanıcı işaretlerse girdiği % oranını düşer, işaretlemezse doğrudan nominal schedule seçilir.

4. **🏷️ API 5L X46 Malzeme Kalitesi Eklendi:**
   - Tasarım aracındaki malzeme kalitesi listesine **`X46 (L320 - SMYS: 46400 psi / 320 MPa)`** kalitesi eklenmiştir.

5. **📊 Dinamik Bilgi Rozeti ve Şeffaf Sonuç Gösterimi:**
   - Form üzerinde parametreler değiştikçe hangi API 5L Tablo 11 kuralının işletileceği canlı olarak gösterilir.
   - Sonuç kartında uygulanan tolerans kuralı ve minimum et kalınlığı sınırı şeffaf şekilde raporlanır.

---

### 💻 İndirme Bağlantıları (v1.4.0)

- **🪟 Windows (x64):**  
  [**`API-5L-Pipe-Windows-x64.exe` İndir**](https://github.com/SLedgehammer-dev12/API-5L-Pipe/releases/download/v1.4.0/API-5L-Pipe-Windows-x64.exe)  
  *Tek dosyadır, kurulum gerektirmez. Doğrudan çift tıklayarak çalıştırabilirsiniz.*

- **🍏 macOS (Apple Silicon M1/M2/M3/M4 & Intel):**  
  [**`API-5L-Pipe-macOS.dmg` İndir**](https://github.com/SLedgehammer-dev12/API-5L-Pipe/releases/download/v1.4.0/API-5L-Pipe-macOS.dmg)  
  *Disk kalıbını açıp `API-5L-Pipe.app` uygulamasını Applications klasörüne sürükleyin.*

