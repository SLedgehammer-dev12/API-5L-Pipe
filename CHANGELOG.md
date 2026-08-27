# Changelog / Sürüm Geçmişi

All notable changes to this project will be documented in this file.
This project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.7.0] - 2026-08-28 (API 5L 47. Baskı Uyumu: PSL1 Seçimi, PSL2 Teslim Koşulları, CE Hesabı, Baskı Karşılaştırma Notları)

### 🎉 Eklenen Özellikler (Added)
- **API 5L PSL1 Boru Seçimi:** "Matrise Yeni Boru Sütunu Ekle" bölümüne API 5L PSL1 seçeneği (BOTAŞ aynen korundu); Tablo 4/6 kimyasal + mekanik, Tablo 17/19 ITP; PSL1'de CVN/Y-T/CE/DWTT zorunlu değil, SAW yasak; "10 adet PSL1" ön ayar şablonu.
- **PSL2 Teslim Koşulu (R/N/Q/M):** Kimyasal bileşim (Tablo 5) ve Y/T oranı (Tablo 7) teslim koşuluna göre seçilir; M koşulu yalnız kaynaklı boru + Grade B–X120 (Tablo 3); kademe↔teslim çift yönlü filtre.
- **Otomatik Karbon Eşdeğeri Hesabı:** CE_IIW (Denk. 3) ve CE_Pcm (Denk. 2) formülleri; formda Si/Cr/Mo/Ni/Cu/B alanları; C>%0.12 ise CE_IIW, aksi halde CE_Pcm kontrolü.
- **t > 25.0 mm Kimya Kuralı (9.2.3):** Kimyasal bileşim "anlaşmaya bağlıdır"; PSL2 + SMLS + t > 20 mm CE anlaşmaya bağlı (Tablo 5 dipnot a).
- **46 vs 47 Baskı Karşılaştırma Notları (ⓘ):** Her satırda 46. orijinal + 47. güncel değer + kaynak madde; gerçek 46→47 farkları işaretlenir.
- **Çekme Numune Çizimleri Düzeltildi:** Şerit (paralel kenarlı tam cidar, L0=50 mm, 38,1 mm) ve yuvarlak çubuk (tek silindirik mastar, d=6,4/8,9/12,7 mm) SVG'leri yeniden çizildi; referanslar 47. baskı (guided-bend 9.7, DWTT 9.9).
- **Hesaplama Sonuçları 2 Ondalık:** KPI, MPa, çevre toleransları, oper/SMYS oranı, rapor ağırlığı.

### 🛠️ Düzeltmeler (Fixed)
- **API 5L 47. Baskı Tablo Değerleri:** Y/T 0.93 (D>323.9, dipnot c); CVN gövde çap+kademeye bağlı (Tablo 8); CVN kaynak 9.8.3.1 (HFW 20 J); çap toleransı ±3.2 tavanı ve ±0.005D max 4.0 (Tablo 10); hidrostatik D≤141.3→%60 ve 20.5 MPa tavanı (Tablo 26); API modunda hidro min = standart test basıncı; uzama yuvarlak çubuk Axc (Tablo 21); SMLS t≥25 +max(3.7,0.1t); CVN numune boyutu Tablo 22'ye göre; DWTT yalnız kaynaklı D≥508; peaking 9.10.5.1 (≤3.2 mm); et kalınlığı motorunda "%8" kuralı kaldırıldı.
- **ITP/rapor/Excel:** PSL1 satırları; None güvenli kimya gösterimi; CE satırları; madde referansları 47. baskı.

---

## [1.6.2] - 2026-08-25 (API 5L ITP Geliştirmesi: Boru Seçici, Standart Madde Metni & Numune Çizimleri)

### 🎉 Eklenen Özellikler (Added)
- **ITP Boru Seçici (Chips):** API 5L Test & Muayene Planı kartına, 3D/2D seçiciyle aynı yatay boru çipleri eklendi — global `selectedPipeIndex` ile senkron (matris/KPI/3D de güncellenir).
- **Tıkla-Genişle Satırlar:** ITP tablosunda test satırına tıklanınca altında standart madde metni + numune çizimi inline açılır.
- **Standart Madde Referansı (ℹ️):** "Madde" sütunundaki bilgi ikonu, ilgili API 5L 46th Ed. maddesinin **tam orijinal metnini** modal ile gösterir.
- **Numune Çizimleri (ℹ️):** "Numune Boyutu" sütunundaki bilgi ikonu, API 5L Şekil 4/5/6 ve standart numune şekillerine çok yakın **SVG şematik çizimleri** (Charpy, çekme şerit/yuvarlak, kılavuzlu bükme, düzleştirme, DWTT, sertlik, numune alım yerleri) modal ile gösterir.
- **Backend:** `test_plan.py` her teste `clause_ref` (orijinal standart metni) ve `specimen_figure` (çizim anahtarı) alanlarını ekledi.

---

## [1.6.1] - 2026-08-25 (Windows Auto-Updater Düzeltmesi & Versiyonlu İndirme Dosyaları)

### 🛠️ Düzeltmeler (Fixed)
- **Windows Otomatik Güncelleme Sorunu:** Windows `--onefile` build'inde `httpx`'in çalışma-zamanı bağımlılıkları (`anyio` backend, `httpcore`, `certifi` CA paketi) toplanmıyordu; bu yüzden GitHub API isteği sessizce başarısız oluyor ve güncelleme banner'ı gösterilmiyordu. Build'e `--collect-all httpx anyio httpcore certifi` eklendi.
- **Updater teşhisi:** `check_for_updates()` artık hataları `logging.error` ile logluyor ve hata detayını yanıtta döndürüyor (sessiz "offline" kaldırıldı).
- **Versiyonlu indirme dosyaları:** `.exe`/`.dmg` dosya adlarına sürüm eklendi — `API-5L-Pipe-Windows-x64-v1.6.1.exe`, `API-5L-Pipe-macOS-v1.6.1.dmg` (farklı sürümlerde aynı isim karmaşası giderildi).
- `build_macos_dmg.sh`'deki hardcoded `VERSION="1.0.0"` düzeltildi; sürüm artık `version.py`'den okunuyor.

### 🛡️ Sağlamlık İyileştirmeleri (Robustness)
- **Pydantic girdi doğrulaması:** Bilinmeyen kalite / negatif basınç 422 ile reddediliyor (500 yerine).
- **XSS koruması:** Kullanıcı girdili alanlar HTML-escape ediliyor.
- **CI lint:** `ruff check` hem Windows hem macOS build job'larına eklendi.

---

## [1.6.0] - 2026-08-24 (API 5L PSL2 ↔ BOTAŞ Tam Ayrımı: Et Kalınlığı, Kaynak Parametreleri, Çap/Ovalite)

### 🎉 Eklenen Özellikler (Added)
- **API 5L ↔ BOTAŞ Tolerans Ayrımı:** Boru sütunu hangi standarda göre oluşturulduysa o standardın toleransları uygulanır.
- **Et Kalınlığı Negatif Toleransı:** API 5L Table 11 (kaynaklı −0.5/−0.1t/−1.5; SMLS −0.5/−0.125t/−3.0) ile BOTAŞ (−0.04/−0.10/−0.15) ayrıştırıldı.
- **Kaynak Parametreleri (SAW):** Radial offset (Table 14), kaynak yüksekliği (Table 16), misalignment (9.13.3) API 5L'de katsayısız; BOTAŞ'ta ×0.75 faktörlü.
- **Çap Toleransı & Ovalite:** API 5L Table 10 değerleri dinamik olarak hesaplanıyor (`compute_api5l_tolerances`); BOTAŞ Excel değerlerini koruyor.
- **Kimyasal Bileşim Boşlukları:** GRADE A, X70–X120 kaliteleri API 5L Table 5 PSL2 değerleriyle dolduruldu.

### 🛠️ Düzeltmeler (Fixed)
- **Hidrostatik test faktörü:** `SMYS<65000` koşulu kaldırıldı (Excel formülüyle uyumlu; 18" X65 artık 0.85 faktör).
- **Excel güncellendi:** Kimya formüllerindeki `"hata"` düzeltildi; std test basıncı formül referans hatası (E→J) giderildi; `Pipe Fittings Flange Calc 2026.08.24.xlsx` olarak kaydedildi.

---

## [1.5.0] - 2026-08-24 (EN 10204 3.1 Raporu, API 5L ITP, Çift Kaynak CVN/Kimya & Kritik Hesap Düzeltmeleri)

### 🎉 Eklenen Özellikler (Added)
- **EN 10204 3.1 Uyumlu Resmi Kabul Raporu:** Doğrulama (PASS/FAIL) sonucunun rapora entegre edilmesi — rapor artık *limit + gerçek ölçüm değeri + UYGUN/RED* kararını birlikte gösterir. "Resmi Rapor / PDF" butonu ile tek tıkla yazdırılabilir sertifika üretimi.
- **EN 10204 3.1 İzlenebilirlik Alanları:** Isı/Döküm No, Sertifika No, Miktar, Sipariş No ve Muayene Kuruluşu alanları (Proje sekmesi + rapor + proje şeması).
- **API 5L Test & Muayene Planı (ITP):** Seçili boruya göre numune adedi/sıklığı, alınma yeri ve boyutu (Table 18/20/21/22, Şekil 5/6) dinamik olarak üretilir; doğrulama sekmesinde kart ve raporda özet blok olarak gösterilir.
- **Çift Kaynak CVN & Kimyasal Limitler:** BOTAŞ (Excel `Boru SMYS Tablosu`) ve API 5L (Table 5/8) setlerinin `standard_type` seçimine göre ayrıştırılması.
- **3D Koyu/Açık Tema Geçişi:** 3D boru modelinde yüksek kontrastlı teknik çizim görünümü için tema butonu.

### 🛠️ Düzeltmeler (Fixed)
- **Ondalık ayraç (virgül/nokta) tasarım faktörü hatası:** `0,6 (Hat)` gibi virgüllü faktörler artık doğru `F=0.60` olarak işleniyor (önceki davranış: yanlışlıkla 0.72).
- **psi→bar sabiti:** `14.50733` → `14.5037738` (doğru birim dönüşümü).
- **Birim ağırlık sabiti:** `0.02466` → `0.0246615` (API 5L 9.11.2).
- **"API 5L Alternative Test Pressure"** kavram ayrıştırması (tasarım basıncı ile karıştırılmaması; 9.3.1.1 "anlaşmaya bağlı").
- CVN numune boyutu placeholder'ının gerçek Table 22 hesabıyla değiştirilmesi.
- Rapor şablonunda sürüm hardcode'u (`v2.0`) ve "Artık Sress" yazım hatası giderildi.

---

## [1.4.0] - 2026-08-24 (API 5L Tablo 11 Negatif Tolerans Otomasyonu, ASME B31.3 Özel Tolerans & X46)

### 🎉 Eklenen Özellikler (Added)
- **Boru Üretim Yöntemine Bağlı API 5L Tablo 11 Negatif Tolerans Otomasyonu:** SMLS (-%12.5), ERW/HFW (-%10.0), SAWH/SAWL ($D > 20''$ için -%8.0, $D \le 20''$ için -%10.0) imalat toleranslarının ASME B31.8 / B31.4 hesaplamalarında otomatik uygulanması.
- **ASME B31.3 El ile Negatif Tolerans Girişi:** Kullanıcının proses borulaması için negatif tolerans oranını (%) el ile dilediği gibi girebilmesi (Varsayılan %12.5).
- **Paslanmaz Çelik Opsiyonel Toleransı:** ASME B31.8 / B31.4 altında paslanmaz ve dubleks borular için negatif toleransın opsiyonel checkbox ile yönetilmesi.
- **API 5L X46 Kalite Entegrasyonu:** Malzeme listesine `X46 (L320 - SMYS: 46400 psi / 320 MPa)` kalitesinin eklenmesi.
- **Dinamik Canlı Tolerans Bilgisi:** Arayüzde form elemanları değiştikçe işletilecek API 5L Tablo 11 kuralının ve minimum et kalınlığı sınırının canlı raporlanması.

---

## [1.3.0] - 2026-08-23 (Geri Bildirim & İletişim Modülü, ASME B31.3 Düzeltmesi)

### 🎉 Eklenen Özellikler (Added)
- **Kullanıcı Geri Bildirim & İletişim Modülü:** `omer.erbas@botas.gov.tr` doğrudan mailto, panoya kopyalama ve GitHub Issues entegrasyonu.
- **Otomatik Tanı Raporlama:** Seçili boru parametreleri, işletim sistemi ve sürüm bilgisinin tek tıkla hata raporuna eklenmesi.
- **Dinamik Çap Listesi:** Et kalınlığı hesaplama aracında tüm 35 standart çapın dinamik yüklenmesi.

### 🛠️ Düzeltmeler (Fixed)
- Form seçim listelerindeki kaçış karakterleri giderilerek 24" ve diğer çapların ASME B31.3 hesaplamalarında doğru işletilmesi sağlandı.

---

## [1.2.0] - 2026-08-22 (Çoklu Standart Et Kalınlığı, Paslanmaz Çelik, 40+ Parametre & Tablo Ergonomisi)

### 🎉 Eklenen Özellikler (Added)
- **Çoklu Standart Et Kalınlığı Hesaplama:** BOTAŞ (Hat/İstasyon + %12.5 Mill Tol.), ASME B31.8 / B31.4 ve ASME B31.3 Proses Borulaması kriterleri desteği.
- **Paslanmaz ve Dubleks Malzemeler:** SS 304/304L, SS 316/316L, SS 321, Duplex 2205, Super Duplex 2507 kaliteleri ve ASME B36.19M paslanmaz schedule tablosu.
- **40+ Parametreli Kapsamlı Kabul & Doğrulama Motoru:** Kimyasal, boyutsal, mekanik, kaynak, tokluk ve ağırlık/hidro testlerinin standartlara göre tam otomatik değerlendirilmesi.
- **Tablo Okunabilirlik ve Crosshair Odaklanması:** Seçili sütun kontrast iyileştirmesi, fareyle gezinilen satır ile aktif sütunun kesiştiği hücreye anlık aydınlatma.
- **Klavye Yön Tuşları ile Sütun Gezintisi:** Sol/Sağ ok tuşları ve araç çubuğu butonları ile sütunlar arasında hızlı geçiş.
- **Bilingual (TR/EN) Excel Çıktısı:** 40+ parametre ve açıklama satırının Türkçe ve İngilizce standart referanslarıyla doldurulması.
- **2 Ondalık Basamak Yuvarlama Standardı:** Arayüz ve raporlamalarda tüm değerlerin 2 basamağa yuvarlanması.

### 🛠️ Düzeltmeler (Fixed)
- P0-1: Bilinmeyen boru çaplarında oluşan NameError güvenli hale getirildi.
- P1-1: İşletme basıncı eşleşmesinde tasarım faktörüne bağlı dinamik varsayılan atama ve kullanıcı değer önceliği düzeltildi.
- P1-5: İstasyon borularında mill toleransının nominal schedule seçiminde standartlaştırılması.

---

## [1.1.0] - 2026-08-21 (Kapsamlı Ergonomi, 3D Senkronizasyon & Otomatik Güncelleyici)
- Açılışta GitHub Releases üzerinden otomatik güncelleme denetimi.
- Çoklu boru 2D & 3D senkronizasyonu ve 3D PNG snapshot alma.
- Yönetici KPI özet performans kartları.
- Donuk başlıklar ve katlanabilir akordeon parametre matrisi.
- Telif Hakkı & Sorumluluk Reddi (Disclaimer) entegrasyonu.

---

## [1.0.3] - 2026-08-21
- PyInstaller freeze support ve doğrudan ASGI nesnesiyle çalıştırma düzeltmesi.
- BOTAŞ otomatik doldurma entegrasyonu.

---

## [1.0.0] - 2026-08-21
- İlk kararlı sürüm (Initial Release).
