# Sürüm Notları / Release Notes - v1.3.0

## 🚀 API 5L PSL2 & BOTAŞ Boru Kalite Güvence, Fabrika Kabul ve Çoklu Standart Et Kalınlığı Tasarım Yazılımı

Bu sürüm, **Kullanıcı Geri Bildirimi, Hata / Öneri Bildirimi & Geliştirici İletişim Modülü (omer.erbas@botas.gov.tr)**, **Boru Çapı Seçim ve Kaçış Karakteri Çözümleme Düzeltmesi (ASME B31.3 & Çoklu Standart Hesaplamaları)**, **Dinamik Veritabanı Çap Senkronizasyonu (35 Standart Çap)** ve sistem kararlılık iyileştirmelerini içermektedir.

---

### 🌟 v1.3.0 ile Gelen Önemli Yenilikler ve İyileştirmeler

1. **💬 Kullanıcı Geri Bildirimi & Geliştirici İletişim Modülü:**
   - **Hedef E-posta:** Doğrudan `omer.erbas@botas.gov.tr` (Geliştirici: Ömer ERBAŞ - BOTAŞ) adresine yönlendirilen entegre iletişim kanalı.
   - **3 Bildirim Kategorisi:**
     - 🐛 *Hata / Hesaplama Uyuşmazlığı (Bug Report)*
     - 💡 *Yeni Özellik / Standart Önerisi (Feature Request)*
     - 💬 *Genel Soru / Danışma (General Inquiry)*
   - **Otomatik Tanı ve Sistem Raporu:** Matriste o an seçili borunun parametreleri (çap, et kalınlığı, çelik kalitesi, basınç, faktör), uygulama sürümü (`v1.3.0`) ve işletim sistemi bilgisi tek tıkla e-postaya veya tanı raporuna eklenir.
   - **3 Farklı Gönderim Yöntemi:**
     - 📩 *E-posta İstemcisiyle Gönder (`mailto:`)*: Outlook, Apple Mail veya varsayılan istemciyi konu ve gövdesi hazır açar.
     - 📋 *Panoya Kopyala*: Tanı raporunu panoya kopyalar.
     - 🐙 *GitHub Issues*: Açık kaynak hata kaydı açma desteği.
   - **Arayüz Entegrasyonu:** Üst menü (Navbar) `Geri Bildirim` butonu, alt bilgi (Footer) hızlı linkleri ve `Hakkında` penceresinde geliştirici kartı.

2. **🛠️ Boru Çapı Seçim Listesi ve Kaçış Karakteri Düzeltmesi:**
   - Form seçim kutusundaki kaçış karakteri ayrıştırılarak 24 inç ve diğer çapların ASME B31.3 hesaplamalarında doğru nominal çapla ($610.0\text{ mm}$) çalışması sağlandı.
   - Et kalınlığı tasarım aracındaki çap seçim listesi veritabanındaki 35 standart çapın tamamını listeleyen dinamik Jinja döngüsüne bağlandı.

3. **📊 Doğrulanan Hesaplama Sonuçları:**
   - 24 inç ($610.0\text{ mm}$) X65 borusu için $75\text{ bar}$ basınçta ASME B31.3 teorik kalınlık $t_{\text{req}} = 7.55\text{ mm}$ ve nominal schedule $8.74\text{ mm}$ olarak %100 doğrulandı.

---

### 💻 İndirme Bağlantıları (v1.3.0)

- **🪟 Windows (x64):**  
  [**`API-5L-Pipe-Windows-x64.exe` İndir**](https://github.com/SLedgehammer-dev12/API-5L-Pipe/releases/download/v1.3.0/API-5L-Pipe-Windows-x64.exe)  
  *Tek dosyadır, kurulum gerektirmez. Doğrudan çift tıklayarak çalıştırabilirsiniz.*

- **🍏 macOS (Apple Silicon M1/M2/M3/M4 & Intel):**  
  [**`API-5L-Pipe-macOS.dmg` İndir**](https://github.com/SLedgehammer-dev12/API-5L-Pipe/releases/download/v1.3.0/API-5L-Pipe-macOS.dmg)  
  *Disk kalıbını açıp `API-5L-Pipe.app` uygulamasını Applications klasörüne sürükleyin.*
