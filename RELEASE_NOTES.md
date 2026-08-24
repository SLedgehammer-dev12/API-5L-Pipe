# Sürüm Notları / Release Notes - v1.5.0

## 🚀 API 5L PSL2 & BOTAŞ Boru Kalite Güvence, Fabrika Kabul ve Çoklu Standart Et Kalınlığı Tasarım Yazılımı

Bu sürüm, **EN 10204 3.1 uyumlu resmi kabul raporunu**, **API 5L Test & Muayene Planını (ITP)**, **çift kaynak CVN/kimyasal limitlerini**, **3D koyu/açık tema geçişini** ve bir dizi **kritik hesaplama düzeltmesini** içermektedir.

---

### 🌟 v1.5.0 ile Gelen Önemli Yenilikler ve İyileştirmeler

1. **📑 EN 10204 3.1 Uyumlu Resmi Kabul Raporu:**
   - Doğrulama (PASS/FAIL) sonuçları artık rapora entegre edilir: rapor **limit + gerçek ölçüm değeri + UYGUN/RED** kararını birlikte gösterir.
   - Doğrulama sekmesindeki **"Resmi Rapor / PDF"** butonu ile tek tıkla yazdırılabilir sertifika üretilir.
   - **Isı/Döküm No, Sertifika No, Miktar, Sipariş No ve Muayene Kuruluşu** alanları eklendi (Proje sekmesi → rapor → proje dosyası).

2. **🔬 API 5L Test & Muayene Planı (ITP):**
   - Seçili boruya göre **numune adedi/sıklığı**, **alınma yeri** ve **boyutu** (API 5L Table 18/20/21/22, Şekil 5/6) otomatik üretilir.
   - Doğrulama sekmesinde özel ITP kartı ve raporda özet blok olarak gösterilir.

3. **⚖️ Çift Kaynak CVN & Kimyasal Limitler:**
   - Boru sütunu **BOTAŞ** ile oluşturulduysa Excel `Boru SMYS Tablosu` değerleri, **API 5L** ile oluşturulduysa API 5L Table 5/8 değerleri uygulanır.

4. **🎨 3D Koyu/Açık Tema Geçişi:**
   - 3D boru modelinde matrise uyumlu **yüksek kontrastlı teknik çizim** görünümü için tema butonu (☀️/🌙).

### 🛠️ Kritik Düzeltmeler (Fixed)

- **Ondalık ayraç hatası:** `0,6 (Hat)` gibi virgüllü tasarım faktörleri artık doğru `F=0.60` olarak işleniyor (önceki davranışta yanlışlıkla `0.72` uygulanıyordu).
- **psi→bar sabiti:** `14.50733` → `14.5037738` (doğru birim dönüşümü).
- **Birim ağırlık sabiti:** `0.02466` → `0.0246615` (API 5L 9.11.2).
- **"API 5L Alternative Test Pressure"** kavram ayrıştırması (API 5L 9.3.1.1).
- CVN numune boyutu placeholder'ının gerçek Table 22 hesabıyla değiştirilmesi.
- Rapor şablonunda sürüm hardcode'u ve "Artık Sress" yazım hatası giderildi.

---

### 💻 İndirme Bağlantıları (v1.5.0)

- **🪟 Windows (x64):**  
  [**`API-5L-Pipe-Windows-x64.exe` İndir**](https://github.com/SLedgehammer-dev12/API-5L-Pipe/releases/download/v1.5.0/API-5L-Pipe-Windows-x64.exe)  
  *Tek dosyadır, kurulum gerektirmez. Doğrudan çift tıklayarak çalıştırabilirsiniz.*

- **🍏 macOS (Apple Silicon M1/M2/M3/M4 & Intel):**  
  [**`API-5L-Pipe-macOS.dmg` İndir**](https://github.com/SLedgehammer-dev12/API-5L-Pipe/releases/download/v1.5.0/API-5L-Pipe-macOS.dmg)  
  *Disk kalıbını açıp `API-5L-Pipe.app` uygulamasını Applications klasörüne sürükleyin.*
