# Sürüm Notları / Release Notes - v1.6.1

## 🚀 API 5L PSL2 & BOTAŞ Boru Kalite Güvence, Fabrika Kabul ve Çoklu Standart Et Kalınlığı Tasarım Yazılımı

Bu sürüm, **Windows otomatik güncelleme sorununu** giderir ve indirme dosyalarının adlarına **sürüm numarasını** ekleyerek farklı sürümlerin karışmasını önler.

---

### 🛠️ v1.6.1 Düzeltmeleri

1. **🪟 Windows Otomatik Güncelleme Düzeltmesi:**
   - Windows tek-dosya (`--onefile`) build'inde `httpx`'in çalışma-zamanı bağımlılıkları (`anyio` backend, `httpcore`, `certifi` CA sertifika paketi) toplanmıyordu. Bu yüzden GitHub API isteği sessizce başarısız oluyor ve yeni sürüm görünmüyordu.
   - Build artık `--collect-all httpx anyio httpcore certifi` ile bu bağımlılıkları tam olarak paketliyor.

2. **🔍 Güncelleme Denetimi Teşhisi:**
   - Güncelleme kontrolü sırasında oluşan hatalar artık sessizce yutulmuyor; `logging.error` ile loglanıyor ve hata detayı kullanıcıya gösteriliyor.

3. **🏷️ Versiyonlu İndirme Dosyaları:**
   - `API-5L-Pipe-Windows-x64.exe` → **`API-5L-Pipe-Windows-x64-v1.6.1.exe`**
   - `API-5L-Pipe-macOS.dmg` → **`API-5L-Pipe-macOS-v1.6.1.dmg`**
   - Farklı sürümlerin indirme dosyaları artık aynı isme sahip olmayacağı için karışıklık giderildi.

4. **🛡️ Sağlamlık İyileştirmeleri:**
   - Pydantic girdi doğrulaması (bilinmeyen kalite / negatif değerler 422 ile reddedilir).
   - Kullanıcı girdili alanlarda XSS koruması (HTML-escape).
   - CI'a `ruff` lint eklendi.

---

### 💻 İndirme Bağlantıları (v1.6.1)

- **🪟 Windows (x64):**  
  [**`API-5L-Pipe-Windows-x64-v1.6.1.exe` İndir**](https://github.com/SLedgehammer-dev12/API-5L-Pipe/releases/download/v1.6.1/API-5L-Pipe-Windows-x64-v1.6.1.exe)  
  *Tek dosyadır, kurulum gerektirmez. Doğrudan çift tıklayarak çalıştırabilirsiniz.*

- **🍏 macOS (Apple Silicon M1/M2/M3/M4 & Intel):**  
  [**`API-5L-Pipe-macOS-v1.6.1.dmg` İndir**](https://github.com/SLedgehammer-dev12/API-5L-Pipe/releases/download/v1.6.1/API-5L-Pipe-macOS-v1.6.1.dmg)  
  *Disk kalıbını açıp `API-5L-Pipe.app` uygulamasını Applications klasörüne sürükleyin.*