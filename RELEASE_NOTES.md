# Sürüm Notları / Release Notes - v2.0.0

## 🚀 API 5L PSL1/PSL2 & BOTAŞ Boru Kalite Güvence, Et Kalınlığı Tasarım ve Akıllı ITP Denetim Süiti (v2.0.0)

Bu ana sürüm (**v2.0.0**), **BOTAŞ Çelik Boru Şartnamesi (`4-NGTL-0-GN-P-002-5120 Rev. 7`) Tam Entegrasyonunu**, **Sekme 5: Akıllı ITP Denetim ve AI Doküman Okuma Motorunu (Unlimited-OCR & PyMuPDF)** ve **Boru Et Kalınlığı Negatif Tolerans İyileştirmelerini** sunar.

---

### 🌟 v2.0.0 ile Gelen Başlıca Yenilikler

1. **📑 BOTAŞ Çelik Boru Şartnamesi (`4-NGTL-0-GN-P-002-5120 Rev. 7`) Standart ve Test Planı Entegrasyonu:**
   - **20 Saniye Hidrostatik Test:** Fabrika hidrostatik test tutma süresi tüm boru çapları için asgari 20 saniye olarak tanımlandı (Madde 8.4.1).
   - **$-20\ ^\circ\text{C}$ Çentik Darbe (CVN) Tokluğu:** X65 için Gövde min 60 J / tekil 45 J, Kaynak min 45 J / tekil 34 J şartı getirildi (Madde 3.3.5 & Tablo-3).
   - **Artık Stres Testi (Residual Stress Ring Test):** Kaynaklı borularda (SAWH/LSAW) her dökümde (heat) zorunlu 150 mm halka testi ($S \le 0.10 \times SMYS$) kuralları eklendi (Madde 3.3.9).
   - **Gövde UT Laminasyon Muayenesi:** Gövde yüzeyinin en az %40'ını tarayacak UT (ISO 12094 B1) ve boru uçlarında min 50 mm laminasyon kontrolü zorunlu kılındı (Madde 8.8.4.4).
   - **Çap, Doğrusallık ve Sertlik:** Boru ucu ovallik (API 5L Çizelge 10'un %50'si), doğrusallık sapması ($\le \%0.10 L$), dairesellik sapması ($\le \%0.15 D$) ve sertlik ($300\text{ HV10}$, aşılması halinde o dökümdeki boruların %100'ünü test etme kuralı) eklendi.
   - **$D \ge 20"$ Borularda %100 Muayene:** $D \ge 20"$ borularda istisnasız %100 görsel ve boyutsal kontrol zorunluluğu tanımlandı (Madde 8.1.2).

2. **🤖 Sekme 5: ITP Akıllı Denetim ve Doküman Okuma Motoru (Unlimited-OCR & PyMuPDF):**
   - İmalatçı ITP dokümanlarını (dijital/taranmış PDF veya resim) 0.02 saniyede okuyabilen hibrit mimari (`PyMuPDF / fitz` + Semantik NLP Regex ayrıştırıcı).
   - Yüklenen ITP'deki test frekanslarını, sürelerini ve kabul kriterlerini API 5L 47. Baskı ve BOTAŞ 5120 R7 şartnameleriyle otomatik karşılaştırma (`ITPAuditEngine`).
   - Yetersiz test frekansı, eksik zorunlu test, kısa hidrostatik test süresi ve düşük darbe enerjisi kusurlarını kırmızı uyarılarla anlık yakalama.
   - Renk kodlu, şartname referanslı profesyonel Excel denetim raporu çıktısı (`.xlsx`).

3. **⚙️ Boru Et Kalınlığı Tasarım Aracı Negatif Tolerans Düzeltmeleri:**
   - BOTAŞ standardı için negatif toleransın 2 defa düşülmesi (çift tolerans tenzili) önlendi.
   - BOTAŞ seçildiğinde kullanıcıyı yanıltmamak adına tolerans kutusu dinamik gizlendi.
   - ASME B31.8 / B31.4 / B31.3 standartlarında kullanıcının `%0` tolerans girmesi halinde SAWH borularda otomatik %8 düşümüne kayma engellendi ve kesin 0% işletildi.

---

### 💻 İndirme Bağlantıları (v2.0.0)

- **🪟 Windows (x64):**  
  [**`API-5L-Pipe-Windows-x64-v2.0.0.exe` İndir**](https://github.com/SLedgehammer-dev12/API-5L-Pipe/releases/download/v2.0.0/API-5L-Pipe-Windows-x64-v2.0.0.exe)  
  *Tek dosyadır, kurulum gerektirmez. Doğrudan çift tıklayarak çalıştırabilirsiniz.*

- **🍏 macOS (Apple Silicon M1/M2/M3/M4 & Intel):**  
  [**`API-5L-Pipe-macOS-v2.0.0.dmg` İndir**](https://github.com/SLedgehammer-dev12/API-5L-Pipe/releases/download/v2.0.0/API-5L-Pipe-macOS-v2.0.0.dmg)  
  *Disk kalıbını açıp `API-5L-Pipe.app` uygulamasını Applications klasörüne sürükleyin.*