# Sürüm Notları / Release Notes - v1.7.1

## 🚀 API 5L PSL1/PSL2 & BOTAŞ Boru Kalite Güvence, Fabrika Kabul ve Çoklu Standart Et Kalınlığı Tasarım Yazılımı

Bu sürüm, **Windows güncelleme kontrolü SSL hatasını**, **doğrulama parametre sayısı gösterimini** ve **çekme numunesi çift-tip seçimini** düzeltir.

---

### 🛠️ v1.7.1 ile Gelen Düzeltmeler

1. **🔐 Windows Güncelleme Kontrolü SSL Hatası (truststore):**
   - Kurumsal güvenlik duvarı/proxy veya antivirüs web korumasının kendi kendinden imzalı CA'sıyla TLS'i kesmesi nedeniyle oluşan `CERTIFICATE_VERIFY_FAILED (self-signed certificate in certificate chain)` hatası çözüldü.
   - Program artık **`truststore`** ile işletim sistemi güven deposunu (Windows sertifika deposu) certifi köklerine ekler → kurumsal CA güvenilir olur (TLS doğrulaması kapatılmaz).
   - SSL hatasında ayrıntılı teşhis logu (proxy durumu / certifi paketi / truststore) ve net Türkçe mesaj eklendi.
   - Build'lere `--hidden-import truststore` eklendi; `.exe` bu sürümle yeniden derlenir.

2. **📊 Doğrulama "0 / 0 Parametre Uygun" Sorunu:**
   - Doğrulama motoru artık boru konfigürasyonuna göre **toplam uygulanabilir parametre sayısını** (`total_applicable`) ve **bekleyen parametre** sayısını döndürür.
   - Arayüz ve raporda **"X / N Parametre Uygun"** gösterilir (örn. "6 / 27 Parametre Uygun") + "Kontrol edilen • Uygun • Red • Bekleyen" özeti.
   - Form boşsa "Lütfen ölçüm verisi girin" uyarısı çıkar.

3. **🧪 Çekme Numunesi Çift-Tip Seçimi:**
   - Kaynaklı D ≥ 219,1 mm borularda (iki tip serbest, API 5L 10.2.3.2.3) ITP **iki ayrı satır** üretir: **"Çekme Testi (Şerit)"** ve **"Çekme Testi (Yuvarlak Çubuk)"** — ikisinin de numune şekli gösterilir.
   - Uzama satırında her iki tip için ayrı minimum uzama (Af) değeri görüntülenir.
   - SMLS boyuna testte **t ≥ 19 mm** için 12,7 mm yuvarlak çubuk zorunludur (10.2.3.2.5).

4. **🖼️ Kılavuzlu Bükme Şekli:**
   - Numune çizimi artık API 5L standardının gerçek **Şekil 8 (numune parçaları)** ve **Şekil 9 (test aparatları)** görsellerini içerir.

---

### 💻 İndirme Bağlantıları (v1.7.1)

- **🪟 Windows (x64):**  
  [**`API-5L-Pipe-Windows-x64-v1.7.1.exe` İndir**](https://github.com/SLedgehammer-dev12/API-5L-Pipe/releases/download/v1.7.1/API-5L-Pipe-Windows-x64-v1.7.1.exe)  
  *Tek dosyadır, kurulum gerektirmez. Doğrudan çift tıklayarak çalıştırabilirsiniz.*

- **🍏 macOS (Apple Silicon M1/M2/M3/M4 & Intel):**  
  [**`API-5L-Pipe-macOS-v1.7.1.dmg` İndir**](https://github.com/SLedgehammer-dev12/API-5L-Pipe/releases/download/v1.7.1/API-5L-Pipe-macOS-v1.7.1.dmg)  
  *Disk kalıbını açıp `API-5L-Pipe.app` uygulamasını Applications klasörüne sürükleyin.*