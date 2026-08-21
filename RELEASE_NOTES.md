# Sürüm Notları / Release Notes - v1.1.0

## 🚀 API 5L PSL2 & BOTAŞ Boru Kalite Güvence, Fabrika Kabul ve Et Kalınlığı Tasarım Yazılımı

Bu sürüm, kullanıcı deneyimini ve ergonomisini artıran **çoklu boru 2D/3D senkronizasyonunu**, **Yönetici KPI özet kartlarını**, **katlanabilir akordeon parametre matrisini**, **canlı parametre arama motorunu**, **3D yüksek çözünürlüklü PNG teknik çizim çıktısını**, **otomatik açılış güncelleme denetleyicisini** ve **Telif Hakkı & Yasal Sorumluluk Reddi (Disclaimer)** entegrasyonlarını içermektedir.

---

### 🌟 v1.1.0 ile Gelen Önemli Yenilikler

1. **🔄 Açılışta Otomatik Güncelleme Denetimi (Auto-Updater):**
   - Program açıldığında arka planda GitHub Releases API üzerinden yeni sürümleri sorgular.
   - Yeni sürüm çıktığında Windows (`.exe`) ve macOS (`.dmg`) için doğrudan indirme bağlantıları içeren şık bir bildirim şeridi açılır.
   - "Hakkında" penceresinde istenildiği zaman manuel güncelleme denetimi yapılabilir.

2. **🎯 Çoklu Boru 2D & 3D Görsel Senkronizasyonu:**
   - Tablodaki herhangi bir boru sütununa tıklandığında, o sütun parlama efektiyle aktif seçilir; 2D kesit ve 3D WebGL modeli anında o borunun gerçek geometrisine ($D$, $t$, kaynak türü) güncellenir.
   - 2D/3D sekmesinde yer alan yatay **Boru Seçim Çipleri (Chips Carousel)** ile sekmeler arası geçiş yapmadan tek tıkla borular arası odaklama sağlanır.
   - **📷 3D Görüntüyü Kaydet (PNG Snapshot):** 3D model ekranından tek tıkla teknik raporlar ve sunumlar için şeffaf arka planlı yüksek çözünürlüklü PNG resmi indirilebilir.

3. **📊 Yönetici KPI Özet Performans Kartları:**
   - Matrisin en üstünde seçili boruya ait 4 kritik mühendislik kartı yer alır:
     - 💧 *Maks. Fabrika Hidrostatik Basıncı ($P_{\max}$)*
     - ⚖️ *Nominal Birim Boru Ağırlığı ($\text{kg/m}$)*
     - 📐 *D/t Oranı & ASME B31.8 841.1.1 Tasarım Formülü*
     - 🛡️ *ASME 841.1.2 Kırılma Emniyeti (API 5L Annex G Durumu)*

4. **📑 Donuk Başlıklar (Sticky Table) & Katlanabilir Akordeon Matrisi:**
   - Aşağı kaydırırken boru başlıkları (`sticky top`), sağa kaydırırken parametre adları (`sticky left`) ve açıklamalar (`sticky right`) donuk kalır.
   - 40+ satır 6 mantıksal mühendislik grubuna ayrıldı; kullanıcı dilediği bloğu tek tıkla daraltıp genişletebilir.
   - **Canlı Parametre Arama Çubuğu:** Tablo üzerinde anlık parametre süzme imkanı.

5. **⚡ BOTAŞ Çapa Göre Otomatik Doldurma:**
   - BOTAŞ Şartnamesi seçildiğinde kullanıcı yalnızca çap seçer; ilgili çapa ait tüm dizayn faktörlerindeki borular ($F=0.72\text{ Hat}$, $F=0.60\text{ Hat}$, $F=0.50\text{ Hat}$, $F=0.50\text{ İstasyon 1/2}$) tek tıkla matrise ayrı sütunlar olarak eklenir.

6. **⚖️ Telif Hakkı (Copyright) & Yasal Sorumluluk Reddi (Disclaimer):**
   - Alt bilgi (Footer), Hakkında modalı, Excel çalışma kitabı dipnotu ve resmi EN 10204 3.1 rapor şablonuna kapsamlı yasal sorumluluk ve telif bildirimleri entegre edildi.

7. **📦 Geriye Dönük Şema Uyumluluğu:**
   - Eski versiyonlarda (`v1.0.0`, `v1.0.1`, `v1.0.2`) kaydedilmiş `.pipeproj` dosyaları yüklendiğinde otomatik göç ettirilerek veri kaybı olmadan açılır.

---

### 💻 İndirme Bağlantıları (v1.1.0)

- **🪟 Windows (x64):**  
  [**`API-5L-Pipe-Windows-x64.exe` İndir**](https://github.com/SLedgehammer-dev12/API-5L-Pipe/releases/download/v1.1.0/API-5L-Pipe-Windows-x64.exe)  
  *Tek dosyadır, kurulum gerektirmez. Doğrudan çift tıklayarak çalıştırabilirsiniz.*

- **🍏 macOS (Apple Silicon M1/M2/M3/M4 & Intel):**  
  [**`API-5L-Pipe-macOS.dmg` İndir**](https://github.com/SLedgehammer-dev12/API-5L-Pipe/releases/download/v1.1.0/API-5L-Pipe-macOS.dmg)  
  *Disk kalıbını açıp `API-5L-Pipe.app` uygulamasını Applications klasörüne sürükleyin.*
