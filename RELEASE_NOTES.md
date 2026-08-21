# Release Notes - v1.0.0

## API 5L PSL2 & BOTAŞ Boru Kalite Güvence, Fabrika Kabul ve Et Kalınlığı Tasarım Yazılımı

Bu sürüm, API 5L PSL2 ve BOTAŞ doğal gaz boru hatları şartnamelerine tam uyumlu olarak geliştirilen **Boru Kalite Güvence ve Tasarım Yazılımı**'nın ilk kararlı sürümüdür (v1.0.0).

---

### 🌟 Öne Çıkan Özellikler

1. **Boru Kalite Güvence & Kabul Matrisi (QA/QC Matrix):**
   - 40'tan fazla parametrenin eşzamanlı denetimi.
   - Sınırsız sayıda boru sütunu ekleme, klonlama ve karşılaştırma.
   - Her satırın yanında standardın ilgili maddesi ve formül açıklaması (Engineering Remarks).

2. **Dinamik Şartname Seçimi:**
   - **BOTAŞ Modu:** Çap ve faktör seçildiğinde malzeme kalitesi ve et kalınlığı BOTAŞ şartname tablolarından otomatik çekilir ve BOTAŞ et kalınlığı şartına uygunluk denetlenir.
   - **API 5L Modu:** Çap, malzeme ve et kalınlığı serbestçe seçilebilir ve uluslararası API 5L PSL2 / ASME B31.8 standartlarına göre hesaplanır.

3. **3D WebGL & 2D Görselleştirme:**
   - Three.js tabanlı 360° interaktif 3D boru gövdesi ve SAWH borular için gövde boyunca dönen 3D helisel/spiral kaynak dikişi (ERW için boyuna kaynak).
   - SVG tabanlı 2D teknik enkesit ve tolerans bantları.

4. **Gerçek Test Verileri Doğrulama (PASS / FAIL):**
   - Sahadan/laboratuvardan gelen gerçek ölçüm değerlerinin tek tıkla standart sınırlarına göre denetimi ve kabul/ret rozetleri üretimi.

5. **ASME B31.8 Et Kalınlığı Tasarım Aracı:**
   - Barlow formülü ve ASME B36.10 standart Schedule serisi seçimi.

6. **Raporlama ve Dışa Aktarma:**
   - Excel (.xlsx) profesyonel formatlı dışa aktarım.
   - Resmi EN 10204 3.1 uyumlu yazdırılabilir kabul raporu.

---

### 💻 Kurulum ve Çalıştırma

#### Windows:
`run.bat` dosyasına çift tıklayın veya komut satırından çalıştırın:
```cmd
run.bat
```

#### macOS (Apple Silicon M1/M2/M3/M4 & Intel) / Linux:
Terminalden çalıştırın:
```bash
./run.sh
# veya
python3 run.py
```

Tarayıcınızda otomatik olarak `http://127.0.0.1:8000` adresi açılacaktır.
