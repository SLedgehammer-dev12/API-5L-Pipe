# Sürüm Notları / Release Notes - v2.1.0

## 🚀 API 5L PSL1/PSL2 & BOTAŞ Boru Kalite Güvence, Et Kalınlığı Tasarım ve Akıllı ITP Denetim Süiti (v2.1.0)

Bu sürüm (**v2.1.0**), **Çok Sütunlu Gerçek Tablo Ekstraksiyonunu (PyMuPDF 1.23+ `find_tables()`)**, **Maksimum Ağırlıklı İki Kümeli Eşleştiriciyi (Maximum-Weight Bipartite Matcher)**, **Tüm 24 Disiplin İçin Kapsamlı Sayısal Kriter Denetimini** ve **Kapsamlı Kod Sağlığı / Güvenilirlik Refaktörünü (C1-C18, F1-F13, B1-B6)** sunar.

---

### 🌟 v2.1.0 ile Gelen Başlıca Yenilikler

1. **📑 Çok Sütunlu Gerçek Tablo Ekstraksiyonu & Sütun İzolasyonu (`core/unlimited_ocr_engine.py`):**
   - PyMuPDF 1.23+ `page.find_tables()` entegrasyonu ile karmaşık, çok sütunlu ITP tabloları hücre düzeyinde ayrıştırılır.
   - Sütun başlıkları (`Aktivite`, `Frekans`, `Konum`, `Standart`, `Kabul Kriteri`, `Madde`) dinamik olarak sınıflandırılır.
   - Vektörsüz/taranmış resim PDF'leri için rasterize `pytesseract` OCR katmanı ve `UNLIMITED_OCR_API_URL` uzak yapay zeka servisi desteği sağlandı.

2. **🎯 Maksimum Ağırlıklı İki Kümeli Eşleştirici (Maximum-Weight Bipartite Matcher) (`core/itp_audit_engine.py`):**
   - Sıra-bağımlı greedy algoritma kaldırılarak küresel optimum iki kümeli eşleştirme kuruldu.
   - Disiplin ağırlıkları, kelime uzunluğu skorlaması ve SMLS vs Kaynaklı boru anti-affinity kuralları ile yanlış eşleşmeler %100 önlendi.

3. **🧪 Tüm 24 Disiplin İçin Sayısal Kriter & Tolerans Denetimi:**
   - **DWTT:** Ortalama sünek kırılma alanı $\ge \%85$ ve BOTAŞ için münferit $<\%60$ olmama şartı.
   - **Çekme (Tensile Body & Weld):** $R_{t0.5}, R_m, A_f$ ve azami $Y/T$ oranı ($0.90 / 0.93$).
   - **Kimyasal Analiz:** $C, P, S, N$ ve $CE_{\text{IIW}} / CE_{\text{Pcm}}$ tavanları.
   - **Kaynak Tamir & Ön Isıtma:** Gövde tamir yasağı, tek tamir boyu $\le 150\text{ mm}$, $t > 10\text{ mm}$ için $\ge 100\ ^\circ\text{C}$ ön ısıtma şartı.
   - **Birim Ağırlık & Geometri:** Münferit boru ağırlık toleransı ($-\%3.5 / +\%10.0$) ve kaynak yüksekliği ($\le 2.625\text{ mm}$ BOTAŞ / $\le 3.5\text{ mm}$ API).

4. **🛡️ Kapsamlı Kod Sağlığı ve Güvenilirlik Refaktörü (C1-C18, F1-F13, B1-B6):**
   - Grade A mekanik özellikleri ve ovalite tipleri normalize edildi.
   - `get_pipe_size_by_mm` içine mesafe güvenlik eşiği konuldu.
   - Doğrulama motorunda boş veride yanıltıcı `ACCEPTED` kararı verilmesi engellendi (`NO_DATA` yapıldı).
   - 56" ve 60" gibi büyük çaplar için nominal schedule listesi $50.80\text{ mm}$'ye genişletildi.
   - API uç noktaları Pydantic şema modelleri ile korundu; dışa aktarılan dosya adları sanitize edildi.
   - Tarayıcı `LocalStorage` kalıcılığı ile ITP denetim sonuçları sayfa yenilemelerinde korunur hale getirildi.

---

### 💻 İndirme Bağlantıları (v2.1.0)

- **🪟 Windows (x64):**  
  [**`API-5L-Pipe-Windows-x64-v2.1.0.exe` İndir**](https://github.com/SLedgehammer-dev12/API-5L-Pipe/releases/download/v2.1.0/API-5L-Pipe-Windows-x64-v2.1.0.exe)  
  *Tek dosyadır, kurulum gerektirmez. Doğrudan çift tıklayarak çalıştırabilirsiniz.*

- **🍏 macOS (Apple Silicon M1/M2/M3/M4 & Intel):**  
  [**`API-5L-Pipe-macOS-v2.1.0.dmg` İndir**](https://github.com/SLedgehammer-dev12/API-5L-Pipe/releases/download/v2.1.0/API-5L-Pipe-macOS-v2.1.0.dmg)  
  *Disk kalıbını açıp `API-5L-Pipe.app` uygulamasını Applications klasörüne sürükleyin.*