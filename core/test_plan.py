"""
Inspection & Test Plan (ITP) Generator — API 5L 47th Edition / ISO 3183.

Provides, per pipe configuration, the required test sampling information:
    - frequency (quantity per lot/heat)
    - sampling location
    - specimen dimensions / type
    - clause reference (original API 5L text) for each test
    - specimen figure key (for schematic drawings)

References (47th Ed.):
    Table 17 — Inspection frequency for PSL 1 pipe
    Table 18 — Inspection frequency for PSL 2 pipe
    Table 19 — Number, orientation and location of test pieces (PSL 1)
    Table 20 — Number, orientation and location of test pieces (PSL 2)
    Table 21 — Round bar test piece diameter vs pipe dimensions (transverse tensile)
    Table 22 — Required impact test piece size vs pipe dimensions (CVN)
    Figures 5/6 — Sample and test piece orientation and locations
"""

from typing import Any, Dict, List, Optional

# Original clause text (API 5L 47th Edition / ISO 3183) for each test.
# Keyed by the test name; rendered verbatim in the info modal / expandable row.
CLAUSE_REFERENCES: Dict[str, str] = {
    "Kimyasal Analiz (Heat & Product)": (
        "API Spec 5L 47th Ed., Madde 9.2 & Çizelge 17/18 (Denetim Sıklığı):\n"
        "• Isı analizi (Heat analysis): 'One analysis per heat of steel.'\n"
        "• Ürün analizi (Product analysis): 'Two analyses per heat of steel (taken from separate product items).'\n"
        "• PSL 1 kimyasal bileşim limitleri Çizelge 4'te, PSL 2 limitleri Çizelge 5'te (t ≤ 25,0 mm) verilir.\n"
        "• t > 25,0 mm için kimyasal bileşim anlaşmaya bağlıdır (9.2.3)."
    ),
    "Çekme Testi (Tensile)": (
        "API Spec 5L 47th Ed., Madde 9.3 & Çizelge 19/20 (Test Parçası Sayısı/Yönü/Yeri):\n"
        "• Gövde çekme testi, PSL 2 için 'Once per test unit of pipe with the same cold-expansion ratio' yapılır.\n"
        "• Yön: Kaynaklı boruda gövde ENİNE (enine şerit veya Tablo 21'e göre yuvarlak çubuk), "
        "SMLS boruda BOYUNA.\n"
        "• D ≥ 219,1 mm kaynaklı borularda yuvarlak çubuk numune çapı Çizelge 21'e göre belirlenir.\n"
        "• Rt0.5 (akma), Rm (çekme) ve uzama raporlanır."
    ),
    "Çentik Darbe (CVN)": (
        "API Spec 5L 47th Ed., Madde 9.8 & Çizelge 20 & 22:\n"
        "• PSL 2 gövde + kaynaklı boruda kaynak ve ITAB/HTZ için Charpy V-notch deneyi "
        "'Once per test unit of pipe with the same cold-expansion ratio' yapılır.\n"
        "• Numune boyutu (tam boy 10×10×55 mm veya alt boyut 7,5 / 6,67 / 5 mm) "
        "boru boyutlarına ve et kalınlığına göre Çizelge 22'den belirlenir.\n"
        "• Test sıcaklığı: aksi sipariş edilmedikçe 0 °C; ortalama ve tek-minimum değerler "
        "Çizelge 8'e göre raporlanır. Alt boyut numunede enerji 9.8.1.1'e göre ölçeklenir; "
        "tek değer ortalamanın %75'inden az olamaz (9.8.1.2).\n"
        "• PSL 1'de CVN ZORUNLU DEĞİLDİR."
    ),
    "Hidrostatik Test": (
        "API Spec 5L 47th Ed., Madde 9.4 & 10.2.6:\n"
        "• Her boru hidrostatik deneye tabi tutulur.\n"
        "• Stabilizasyon süresi: 'All sizes of seamless (SMLS) pipe and welded pipe with "
        "D ≤ 457 mm (18.000 in) shall have a stabilization time of not less than 5 seconds. "
        "Welded pipe with D > 457 mm (18.000 in) shall have a stabilization time of "
        "not less than 10 seconds.'\n"
        "• Deney basıncı 10.2.6.4 ve Tablo 26'ya göre (standart veya alternatif) uygulanır.\n"
        "• Basınç ölçer kalibrasyonu (10.2.6.1): mekanik max 6 ay, elektronik max 12 ay."
    ),
    "Kılavuzlu Bükme (Guided Bend)": (
        "API Spec 5L 47th Ed., Madde 9.7 & Çizelge 19/20:\n"
        "• Kaynaklı borularda kaynak dikişi için kılavuzlu bükme (guided-bend) deneyi yapılır.\n"
        "• Test parçası: tam cidar şerit; kök bükme (root bend) ve kapak bükme (cap bend) numuneleri.\n"
        "• Deney ISO 5173 / ASTM A370 uyarınca yapılır; çatlaklar 9.7.1'e göre sınırlandırılmıştır."
    ),
    "Düzleştirme (Flattening)": (
        "API Spec 5L 47th Ed., Madde 9.6:\n"
        "• EW/HFW/LW borular için düzleştirme (flattening) deneyi yapılır.\n"
        "• Numune: tam kesit halka (ring); iki plaka arasında sıkıştırılır.\n"
        "• Kaynağın açılması: X60+ ve t ≥ 12,7 mm için %66, diğerleri için %50 (9.6 a) 1)).\n"
        "• D/t > 10 için %33'e kadar kaynak dışı çatlak yok (9.6 a) 2)).\n"
        "• Karşı duvarlar değene kadar kaynakta füzyon eksikliği / eksik nüfuziyet / laminasyon yok (9.6 a) 3)).\n"
        "• Deney ISO 8492 / ASTM A370 uyarınca yapılır."
    ),
    "Bükme (Bend)": (
        "API Spec 5L 47th Ed., Madde 9.5 & Çizelge 19:\n"
        "• PSL 1'de CW/LFW/HFW borularda D ≤ 60,3 mm (2.375 in) için tam kesit bükme deneyi yapılır.\n"
        "• Test parçası uygun uzunlukta, 90° bükülür (mandrel çapı 12D'den büyük olmayacak).\n"
        "• Deney ISO 8491 / ASTM A370 uyarınca yapılır."
    ),
    "DWTT (Drop Weight Tear Test)": (
        "API Spec 5L 47th Ed., Madde 9.9 & Çizelge 20:\n"
        "• D ≥ 508 mm kaynaklı (HFW/SAW) hat borularında DWTT zorunludur.\n"
        "• Numune: tam cidar, press-notch (presle çentiklenmiş) plaka; gövdeden ENİNE alınır.\n"
        "• Her testte (iki numune) ortalama sünek kırılma alanı ≥ %85 (9.9).\n"
        "• PSL 1'de DWTT zorunlu değildir."
    ),
    "Sertlik Testi": (
        "API Spec 5L 47th Ed., Madde 10.2.4.8 & 9.10.6 & Çizelge 20:\n"
        "• PSL 2'de gövde / kaynak / ITAB sertlik deneyi sipariş koşullarına göre yapılır "
        "(örn. Ek H/J/N'de 300 HV10 / 250 HV).\n"
        "• PSL 1'de sertlik yalnız sert nokta (hard spot) tespitinde yapılır: 50 mm'den büyük "
        "sert nokta 35 HRC / 345 HV10 / 327 HBW üzerindeyse defekt sayılır (9.10.6).\n"
        "• Deney ISO 6506/6507/6508 veya ASTM A370 uyarınca yapılır."
    ),
}

# Specimen figure keys for schematic drawings (frontend renders SVG per key).
# Chemical & hydrostatic have no specimen drawing (None).
SPECIMEN_FIGURES: Dict[str, Optional[str]] = {
    "Kimyasal Analiz (Heat & Product)": None,
    "Çekme Testi (Tensile)": None,          # set dynamically below (strip vs round)
    "Çentik Darbe (CVN)": "charpy",
    "Hidrostatik Test": None,
    "Kılavuzlu Bükme (Guided Bend)": "guided_bend",
    "Düzleştirme (Flattening)": "flattening",
    "DWTT (Drop Weight Tear Test)": "dwtt",
    "Sertlik Testi": "hardness",
}

VALID_FIGURES = {
    "sampling_location", "charpy", "tensile_strip", "tensile_round",
    "guided_bend", "flattening", "dwtt", "hardness",
}


def _cvn_specimen_size(diameter_mm: float, wall_thickness_mm: float) -> str:
    """Required CVN specimen size from D and t (API 5L Table 22)."""
    from core.database import get_cvn_specimen_size
    return get_cvn_specimen_size(diameter_mm, wall_thickness_mm)["label"]


def _tensile_specimen(diameter_mm: float, wall_thickness_mm: float, manufacturing_process: str = "SAWH") -> str:
    """Tensile test piece per Table 20/21 (round bar for welded pipe D >= 219.1 mm)."""
    proc = (manufacturing_process or "").upper()
    is_smls = "SMLS" in proc or "SEAMLESS" in proc
    if not is_smls and diameter_mm >= 219.1:
        dia = "12.7 mm" if wall_thickness_mm >= 24.0 else ("8.9 mm" if wall_thickness_mm >= 17.5 else "6.4 mm")
        return f"Yuvarlak çubuk (çap {dia}, Table 21)"
    if is_smls:
        return "Tam kesit / şerit (boyuna)"
    return "Şerit 38.1 mm genişlik x tam cidar"


def _tensile_figure(diameter_mm: float, manufacturing_process: str = "SAWH") -> str:
    """Selects tensile specimen drawing (round bar vs strip)."""
    proc = (manufacturing_process or "").upper()
    is_smls = "SMLS" in proc or "SEAMLESS" in proc
    if not is_smls and diameter_mm >= 219.1:
        return "tensile_round"
    return "tensile_strip"


def _tensile_rows(d_mm: float, t_mm: float, process: str, is_smls: bool, tbl: str) -> List[Dict[str, Any]]:
    """
    Tensile test row(s) per API 5L 10.2.3.2 / Table 19/20:
    - Welded pipe D >= 219.1 mm: transverse test; BOTH strip and round bar are
      permitted (10.2.3.2.3) -> two separate rows.
    - SMLS longitudinal with t >= 19.0 mm: 12.7 mm round bar is mandatory (10.2.3.2.5).
    - Otherwise: strip / full-section (longitudinal or transverse) -> one row.
    """
    proc = (process or "").upper()
    tbl_t = "Table 19" if tbl == "Table 17" else "Table 20"

    if not is_smls and d_mm >= 219.1:
        return [
            {
                "test": "Çekme Testi (Şerit)",
                "clause": f"API 5L 9.3 / {tbl_t}",
                "clause_ref": CLAUSE_REFERENCES["Çekme Testi (Tensile)"],
                "specimen_figure": "tensile_strip",
                "frequency": "Test ünitesi (lot) başına 1 set",
                "location": "Gövde - enine (düzleştirilmiş numune)",
                "specimen": "Şerit 38,1 mm x t (tam cidar)",
                "note": "10.2.3.2.3 — üretici seçimine bağlı",
            },
            {
                "test": "Çekme Testi (Yuvarlak Çubuk)",
                "clause": f"API 5L 9.3 / {tbl_t}",
                "clause_ref": CLAUSE_REFERENCES["Çekme Testi (Tensile)"],
                "specimen_figure": "tensile_round",
                "frequency": "Test ünitesi (lot) başına 1 set",
                "location": "Gövde - enine (düzleştirilmemiş numune)",
                "specimen": "Yuvarlak çubuk, çap Tablo 21'e göre (6,4/8,9/12,7 mm)",
                "note": "10.2.3.2.3 / Tablo 21 — üretici seçimine bağlı",
            },
        ]

    if is_smls and t_mm >= 19.0:
        return [
            {
                "test": "Çekme Testi (Yuvarlak Çubuk)",
                "clause": f"API 5L 9.3 / {tbl_t}",
                "clause_ref": CLAUSE_REFERENCES["Çekme Testi (Tensile)"],
                "specimen_figure": "tensile_round",
                "frequency": "Test ünitesi (lot) başına 1 set",
                "location": "Gövde - boyuna",
                "specimen": "Yuvarlak çubuk, çap 12,7 mm",
                "note": "10.2.3.2.5 — boyuna testte t >= 19,0 mm için 12,7 mm zorunlu",
            },
        ]

    return [
        {
            "test": "Çekme Testi (Tensile)",
            "clause": f"API 5L 9.3 / {tbl_t}",
            "clause_ref": CLAUSE_REFERENCES["Çekme Testi (Tensile)"],
            "specimen_figure": _tensile_figure(d_mm, proc),
            "frequency": "Test ünitesi (lot) başına 1 set",
            "location": "Gövde - boyuna" if is_smls else ("Gövde - enine" if d_mm >= 219.1 else "Gövde - boyuna"),
            "specimen": _tensile_specimen(d_mm, t_mm, proc),
            "note": "Rt0.5 (yield), Rm (tensile) ve uzama raporlanır",
        },
    ]


def get_test_plan(pipe_config: Dict[str, Any], psl_level: str = "PSL2") -> List[Dict[str, Any]]:
    """
    Returns the API 5L inspection & test plan for the given pipe configuration.

    PSL 1 uses Table 17 (frequency) & Table 19 (test pieces); CVN / DWTT / hardness
    rows are omitted. PSL 2 uses Table 18 & Table 20.

    pipe_config keys: diameter_mm, wall_thickness_mm, material_grade,
                      manufacturing_process, standard_type, psl_level.
    Each entry includes 'clause_ref' (original standard text) and 'specimen_figure'.
    """
    d_mm = float(pipe_config.get("diameter_mm") or 1219.0)
    t_mm = float(pipe_config.get("wall_thickness_mm") or 14.30)
    process = (pipe_config.get("manufacturing_process") or "SAWH").upper()
    is_welded = any(k in process for k in ("SAW", "ERW", "HFW", "LSAW", "COW"))
    is_smls = "SMLS" in process
    is_psl1 = psl_level and "PSL1" in str(psl_level).upper()
    tbl = "Table 17" if is_psl1 else "Table 18"

    std_str = str(pipe_config.get("standard_type") or pipe_config.get("standard_code") or "").upper()
    is_botas = "BOTAŞ" in std_str or "BOTAS" in std_str

    if is_botas:
        # BOTAŞ 4-NGTL-0-GN-P-002-5120 R7 Test Plan
        plan: List[Dict[str, Any]] = [
            {
                "test": "Kimyasal Analiz (Heat & Product)",
                "clause": "BOTAŞ Madde 3.2.2.4 / API 5L 9.2",
                "clause_ref": "BOTAŞ Şartnamesi Madde 3.2.2.4: Hammadde için ebat bazında her döküm (per heat); Boru ürün analizi için ebat bazında her lot (per test unit) için yapılır.",
                "specimen_figure": None,
                "frequency": "Hammadde: her döküm; Boru: her lot",
                "location": "Döküm / boru (sondaj talaşı / spektrometre)",
                "specimen": "Spektrometrik / ıslak analiz",
                "note": "C, Mn, P (≤0.025%), S (≤0.010%), N (≤0.009%), V, Nb, Ti, Cu, Ni, Cr, Mo + CE_IIW (≤0.40) veya CE_Pcm (≤0.22)",
            },
        ]
        plan += _tensile_rows(d_mm, t_mm, process, is_smls, tbl)
        # Update tensile note with BOTAŞ Y/T & 2-set sample rule
        if plan and len(plan) > 1:
            plan[1]["frequency"] = "Lot başına 2 set numune (1. set test, 2. set 5 yıl İdare için saklanır)"
            plan[1]["note"] = "Rt0.5, Rm, Af ≥ %10 (kaynaklı); Y/T Oranı: X65 ≤ 0.90 (soğuk genişletilmemiş) / ≤ 0.93 (genişletilmiş)"

        plan.append({
            "test": "Hidrostatik Test",
            "clause": "BOTAŞ Madde 8.4.1 & 8.4.2 / API 5L 9.4",
            "clause_ref": "BOTAŞ Şartnamesi Madde 8.4.1: Test basıncı uygulaması tüm boru boyutları için 20 SANİYEDEN DAHA AZ OLMAYACAKTIR. Madde 8.4.2: Basınç SMYS %100 (+0 / -2 bar).",
            "specimen_figure": None,
            "frequency": "Her boru (%100)",
            "location": "Boru tam boyu",
            "specimen": "—",
            "note": "Min Tutma Süresi: EN AZ 20 SANİYE; Test Basıncı: SMYS %100 (+0 / -2 bar)",
        })

        plan.append({
            "test": "Çentik Darbe (CVN)",
            "clause": "BOTAŞ Madde 3.3.5 & Tablo 3",
            "clause_ref": "BOTAŞ Şartnamesi Madde 3.3.5: Aksi belirtilmedikçe testler -20 °C'de yapılır. Tablo-3 kabul enerjileri geçerlidir.",
            "specimen_figure": "charpy",
            "frequency": "Lot başına 1 set = 3 numune (gövde + kaynak + ITAB)",
            "location": "Gövde (enine) + kaynak merkez hattı + ITAB",
            "specimen": _cvn_specimen_size(d_mm, t_mm),
            "note": "-20 °C test sıcaklığı; X65 Gövde min 60 J, Kaynak min 45 J (Tablo 3)",
        })

        if is_welded:
            plan.append({
                "test": "Kılavuzlu Bükme (Guided Bend)",
                "clause": "BOTAŞ Madde 3.3.4 / API 5L 9.7",
                "clause_ref": "BOTAŞ Şartnamesi Madde 3.3.4 & API 5L Madde 9.7: Kaynak dikişi için kılavuzlu bükme.",
                "specimen_figure": "guided_bend",
                "frequency": "Lot başına 1 set (kök + kapak)",
                "location": "Kaynak dikişi",
                "specimen": "Tam cidar şerit (kök & kapak bükme)",
                "note": "ISO 5173 / ASTM A370 uyarınca",
            })
            plan.append({
                "test": "Artık Stres Testi (Residual Stress)",
                "clause": "BOTAŞ Madde 3.3.9",
                "clause_ref": "BOTAŞ Şartnamesi Madde 3.3.9: Spiral veya düz dikişli ark kaynaklı borularda boru gövdesi şekillendirilirken kalan artık stres kontrol edilir. Her çap ve et kalınlığı için ve ÇAP VE ET KALINLIĞI DEĞİŞMESE DAHİ HER DÖKÜM (HEAT) İÇİN tekrarlanır. Kabul: S ≤ %10 SMYS.",
                "specimen_figure": "flattening",
                "frequency": "Her döküm (heat) başına 1 halka",
                "location": "Boru ucu (150 mm halka)",
                "specimen": "150 mm genişlikte halka, kaynak karşısından kesilir",
                "note": "S = (E·t·C) / (12.566·D²) ≤ %10 SMYS",
            })
            if d_mm >= 508.0:
                plan.append({
                    "test": "DWTT (Drop Weight Tear Test)",
                    "clause": "BOTAŞ Madde 3.3.6 / API 5L 9.9",
                    "clause_ref": "BOTAŞ Şartnamesi Madde 3.3.6: Test 0 °C'de yapılır. Bir set numunenin (2 adet) herhangi birinin yırtılma alanı %60'tan daha düşük olamaz; ortalama ≥ %85.",
                    "specimen_figure": "dwtt",
                    "frequency": "Isı / lot başına (2 numune)",
                    "location": "Gövde - enine",
                    "specimen": "Tam cidar (chevron / press-notch)",
                    "note": "0 °C test sıcaklığı; Ortalama ≥ %85, münferit numuneler ≥ %60",
                })
            plan.append({
                "test": "Boru Gövdesi UT Laminasyon Muayenesi",
                "clause": "BOTAŞ Madde 8.8.4.4.1",
                "clause_ref": "BOTAŞ Şartnamesi Madde 8.8.4.4.1: Rulo/sac tamamı ISO 12094 Sınıf B1. Boru formu verildikten sonra gövde yüzeyinin EN AZ %40'INI TARAYACAK ŞEKİLDE UT laminasyon muayenesi yapılır.",
                "specimen_figure": None,
                "frequency": "Boru gövde yüzeyinin en az %40'ı",
                "location": "Boru gövdesi tam yüzeyi",
                "specimen": "—",
                "note": "ISO 12094 Sınıf B1 kabul kriterleri",
            })

        plan.append({
            "test": "Sertlik Testi",
            "clause": "BOTAŞ Madde 3.3.7",
            "clause_ref": "BOTAŞ Şartnamesi Madde 3.3.7: Alınan sertlik testi değerlerinin hiçbiri 300 HV10 değerini geçmeyecektir. Bu değeri geçmesi halinde o döküme ait boruların TAMAMI (%100) sertlik testine tabi tutulur.",
            "specimen_figure": "hardness",
            "frequency": "Lot başına",
            "location": "Kaynak dikişi / gövde / ITAB",
            "specimen": "HV10 izi",
            "note": "Maksimum 300 HV10 (Aşılırsa dökümdeki tüm borular %100 test edilir)",
        })

    elif is_psl1:
        # PSL 1: no CVN, no DWTT, no hardness row. Flattening for EW/HFW; bend for D <= 60.3 mm.
        plan: List[Dict[str, Any]] = [
            {
                "test": "Kimyasal Analiz (Heat & Product)",
                "clause": f"API 5L 9.2 / {tbl}",
                "clause_ref": CLAUSE_REFERENCES["Kimyasal Analiz (Heat & Product)"],
                "specimen_figure": None,
                "frequency": "Isı başına 1 ısı analizi; ısı başına 2 ürün analizi",
                "location": "Döküm / ürün (sondaj talaşı)",
                "specimen": "Spektrometrik / ıslak analiz",
                "note": "C, Mn, P, S, V, Nb, Ti",
            },
        ]
        plan += _tensile_rows(d_mm, t_mm, process, is_smls, tbl)
        plan.append({
            "test": "Hidrostatik Test",
            "clause": "API 5L 9.4 / 10.2.6",
            "clause_ref": CLAUSE_REFERENCES["Hidrostatik Test"],
            "specimen_figure": None,
            "frequency": "Her boru",
            "location": "Boru tam boyu",
            "specimen": "—",
            "note": "Stabilizasyon: 5 s (D<=457 mm) / 10 s (D>457 mm)",
        })
        if is_welded:
            if "ERW" in process or "HFW" in process:
                plan.append({
                    "test": "Düzleştirme (Flattening)",
                    "clause": "API 5L 9.6",
                    "clause_ref": CLAUSE_REFERENCES["Düzleştirme (Flattening)"],
                    "specimen_figure": "flattening",
                    "frequency": "Şekil 6'ya göre (bobin uçları)",
                    "location": "Boru ucu halkası",
                    "specimen": "Tam kesit halka numune",
                    "note": "ISO 8492 / ASTM A370 uyarınca",
                })
            if d_mm <= 60.3:
                plan.append({
                    "test": "Bükme (Bend)",
                    "clause": "API 5L 9.5 / Table 19",
                    "clause_ref": CLAUSE_REFERENCES["Bükme (Bend)"],
                    "specimen_figure": "guided_bend",
                    "frequency": "Test ünitesi başına (≤25/50 ton)",
                    "location": "Gövde ve kaynak (D ≤ 60.3 mm)",
                    "specimen": "Tam kesit, 90° bükme",
                    "note": "ISO 8491 / ASTM A370 uyarınca; mandrel ≤ 12D",
                })
        plan.append({
            "test": "Sertlik Testi",
            "clause": "API 5L 9.10.6 / Table 17",
            "clause_ref": CLAUSE_REFERENCES["Sertlik Testi"],
            "specimen_figure": "hardness",
            "frequency": "50 mm'den büyük sert noktada",
            "location": "Sert nokta bölgesi",
            "specimen": "HV10 / HRC / HBW",
            "note": "Yalnız sert nokta kontrolü (9.10.6)",
        })
    else:
        # Standard API 5L PSL 2
        plan: List[Dict[str, Any]] = [
            {
                "test": "Kimyasal Analiz (Heat & Product)",
                "clause": f"API 5L 9.2 / {tbl}",
                "clause_ref": CLAUSE_REFERENCES["Kimyasal Analiz (Heat & Product)"],
                "specimen_figure": None,
                "frequency": "Isı başına 1 ısı analizi; ısı başına 2 ürün analizi",
                "location": "Döküm / ürün (sondaj talaşı)",
                "specimen": "Spektrometrik / ıslak analiz",
                "note": "C, Mn, P, S, V, Nb, Ti + CE raporlanır",
            },
        ]
        plan += _tensile_rows(d_mm, t_mm, process, is_smls, tbl)
        plan.append({
            "test": "Hidrostatik Test",
            "clause": "API 5L 9.4 / 10.2.6",
            "clause_ref": CLAUSE_REFERENCES["Hidrostatik Test"],
            "specimen_figure": None,
            "frequency": "Her boru",
            "location": "Boru tam boyu",
            "specimen": "—",
            "note": "Stabilizasyon: 5 s (D<=457 mm) / 10 s (D>457 mm)",
        })
        plan.append({
            "test": "Çentik Darbe (CVN)",
            "clause": "API 5L 9.8 / Table 20 & 22",
            "clause_ref": CLAUSE_REFERENCES["Çentik Darbe (CVN)"],
            "specimen_figure": "charpy",
            "frequency": "Lot başına 1 set = 3 numune (gövde/kaynak/ITAB)",
            "location": "Gövde (enine) + kaynak merkez hattı + ITAB",
            "specimen": _cvn_specimen_size(d_mm, t_mm),
            "note": "0 °C test sıcaklığı (aksi sipariş edilmedikçe)",
        })
        if is_welded:
            plan.append({
                "test": "Kılavuzlu Bükme (Guided Bend)",
                "clause": "API 5L 9.7 / Table 20",
                "clause_ref": CLAUSE_REFERENCES["Kılavuzlu Bükme (Guided Bend)"],
                "specimen_figure": "guided_bend",
                "frequency": "Lot başına 1 set (kök + kapak)",
                "location": "Kaynak dikişi",
                "specimen": "Tam cidar şerit (kök & kapak bükme)",
                "note": "ISO 5173 / ASTM A370 uyarınca",
            })
            if "ERW" in process or "HFW" in process:
                plan.append({
                    "test": "Düzleştirme (Flattening)",
                    "clause": "API 5L 9.6",
                    "clause_ref": CLAUSE_REFERENCES["Düzleştirme (Flattening)"],
                    "specimen_figure": "flattening",
                    "frequency": "Lot başına 1 set",
                    "location": "Boru ucu halkası",
                    "specimen": "Tam kesit halka numune",
                    "note": "ISO 8492 / ASTM A370 uyarınca",
                })
        if is_welded and d_mm >= 508.0:
            plan.append({
                "test": "DWTT (Drop Weight Tear Test)",
                "clause": "API 5L 9.9 / Table 20",
                "clause_ref": CLAUSE_REFERENCES["DWTT (Drop Weight Tear Test)"],
                "specimen_figure": "dwtt",
                "frequency": "Isı / lot başına",
                "location": "Gövde - enine",
                "specimen": "Tam cidar (press-notch)",
                "note": "D >= 508 mm kaynaklı hat borusu için zorunlu",
            })
        plan.append({
            "test": "Sertlik Testi",
            "clause": "API 5L 10.2.4.8 / Table 20",
            "clause_ref": CLAUSE_REFERENCES["Sertlik Testi"],
            "specimen_figure": "hardness",
            "frequency": "Lot başına",
            "location": "Kaynak dikişi / gövde",
            "specimen": "HV10 / HV5 izi",
            "note": "ISO 6507-1 / ASTM A370 uyarınca",
        })

    # Attach a sampling-location figure for the first entry that has any specimen.
    for entry in plan:
        if entry.get("specimen_figure"):
            entry["sampling_figure"] = "sampling_location"
            break

    return plan


def get_comprehensive_itp_specification(pipe_config: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Returns the comprehensive API 5L 47th Edition (Table 17/18 & 19/20) + BOTAŞ
    Inspection & Test Plan specification for auditing incoming manufacturer ITPs.

    Each item contains:
      - test_key: Unique identifier
      - category: Inspection discipline
      - test_name: Full Turkish/English name
      - standard_frequency: API 5L / BOTAŞ mandated sampling frequency (Turkish)
      - standard_frequency_en: Mandatory sampling frequency (English)
      - standard_acceptance_criteria: Explicit threshold values/rules
      - clause_ref: Standard clause
      - table_ref: Standard table (Table 17/18/19/20/etc.)
      - is_mandatory: Whether mandatory for this specific pipe configuration
    """
    from core.pipe_qaqc_engine import PipeQAQCEngine

    d_mm = float(pipe_config.get("diameter_mm") or 1219.0)
    d_inch = str(pipe_config.get("diameter_inch") or '48"')
    t_mm = float(pipe_config.get("wall_thickness_mm") or 14.30)
    grade = str(pipe_config.get("material_grade") or "X65").upper()
    process = str(pipe_config.get("manufacturing_process") or "SAWH").upper()
    psl_level = str(pipe_config.get("psl_level") or "PSL2").upper()
    delivery_condition = str(pipe_config.get("delivery_condition") or "M").upper()
    std_type = str(pipe_config.get("standard_type") or pipe_config.get("standard_code") or "API").upper()
    is_botas = "BOTAŞ" in std_type or "BOTAS" in std_type

    is_smls = "SMLS" in process
    is_welded = any(k in process for k in ("SAW", "ERW", "HFW", "LSAW", "COW"))
    is_psl1 = "PSL1" in psl_level
    freq_tbl = "Çizelge 17 (Table 17)" if is_psl1 else "Çizelge 18 (Table 18)"
    piece_tbl = "Çizelge 19 (Table 19)" if is_psl1 else "Çizelge 20 (Table 20)"

    qc = PipeQAQCEngine.calculate_pipe_qc(
        diameter_inch=d_inch,
        wall_thickness_mm=t_mm,
        design_factor_str=pipe_config.get("design_factor_str", "0.72 (Hat)"),
        material_grade=grade,
        manufacturing_process=process,
        standard_type="BOTAŞ" if is_botas else std_type,
        psl_level=psl_level,
        delivery_condition=delivery_condition
    )

    chem = qc.get("chemical_analysis", {})
    mech = qc.get("mechanical_properties", {})
    cvn = qc.get("toughness_and_tests", {})
    hydro = qc.get("hydrostatic_test", {})
    dim = qc.get("dimensional_tolerances", {})

    # Chemical acceptance string
    c_max = chem.get("C_max", 0.12 if is_botas else 0.16)
    p_max = 0.025 if is_botas else chem.get("P_max", 0.020)
    s_max = 0.010 if is_botas else chem.get("S_max", 0.010)
    ce_iiw_max = 0.40 if is_botas else chem.get("CE_IIW_max")
    ce_pcm_max = 0.22 if is_botas else chem.get("CE_Pcm_max")
    ce_str = f", CE_IIW ≤ {ce_iiw_max:.2f}" if ce_iiw_max else (f", CE_Pcm ≤ {ce_pcm_max:.2f}" if ce_pcm_max else "")
    
    if is_botas:
        chem_crit = f"C ≤ {c_max:.2f}%, P ≤ {p_max:.3f}%, S ≤ {s_max:.3f}%, N ≤ 0.009%{ce_str} (BOTAŞ Madde 3.2 & Tablo 1)"
    else:
        chem_crit = f"C ≤ {c_max:.2f}%, P ≤ {p_max:.3f}%, S ≤ {s_max:.3f}%{ce_str} (API 5L Çizelge 5)"

    # Tensile criteria
    rt05_min = mech.get("yield_strength_min_mpa", 450.0)
    rt05_max = mech.get("yield_strength_max_mpa")
    rm_min = mech.get("tensile_strength_min_mpa", 535.0)
    rm_max = mech.get("tensile_strength_max_mpa", 760.0)
    af_min = mech.get("elongation_min_percent", 19.5)
    yt_max = 0.90 if (is_botas and grade in ("X60", "X65")) else mech.get("yt_ratio_max")
    rt_str = f"Rt0.5: {rt05_min:.1f}" + (f" - {rt05_max:.1f} MPa" if rt05_max else " MPa min")
    rm_str = f"Rm: {rm_min:.1f}" + (f" - {rm_max:.1f} MPa" if rm_max else " MPa min")
    yt_str = f", Y/T ≤ {yt_max:.2f}" if yt_max else ""
    tensile_crit = f"{rt_str}, {rm_str}, Af ≥ {af_min:.1f}%{yt_str}"

    # CVN criteria
    if is_psl1:
        cvn_crit = "PSL 1'de Çentik Darbe (CVN) zorunlu değildir."
    elif is_botas:
        cvn_body_avg = cvn.get("notch_impact_mat_j", 60.0)
        cvn_body_min = round(cvn_body_avg * 0.75, 1)
        cvn_crit = f"Gövde (-20 °C): Min Ort. {cvn_body_avg:.0f} J, Min Tek {cvn_body_min:.0f} J (BOTAŞ Tablo 3)"
    else:
        cvn_body_avg = cvn.get("notch_impact_mat_j", 41.0)
        cvn_body_min = round(cvn_body_avg * 0.75, 1)
        cvn_crit = f"Gövde (0 °C): Min Ort. {cvn_body_avg:.0f} J, Min Tek {cvn_body_min:.0f} J (API 5L Çizelge 8)"

    # Hydrostatic criteria & time
    hydro_p = hydro.get("hydro_test_max_bar", 100.0)
    if is_botas:
        hydro_time = 20
        hydro_crit = f"Min Test Basıncı: {hydro_p:.1f} bar (SMYS %100, +0/-2 bar), Min Tutma Süresi: 20 saniye (BOTAŞ Madde 8.4)"
    else:
        hydro_time = 10 if (is_welded and d_mm > 457.0) else 5
        hydro_crit = f"Min Test Basıncı: {hydro_p:.1f} bar, Min Tutma Süresi: {hydro_time} saniye (API 5L 10.2.6.2 & Tablo 26)"

    master_list: List[Dict[str, Any]] = [
        {
            "test_key": "chemical_heat",
            "category": "Kimyasal Analiz",
            "test_name": "Isı Analizi (Heat Analysis)",
            "standard_frequency": "Hammadde: ebat bazında her döküm (per heat)" if is_botas else "Isı (Döküm) başına 1 analiz",
            "standard_frequency_en": "One analysis per heat of steel (raw material)",
            "standard_acceptance_criteria": chem_crit,
            "clause_ref": "BOTAŞ Şartnamesi Madde 3.2.2.4 & Tablo 1" if is_botas else "API 5L Madde 9.2 & 10.2.1",
            "table_ref": "BOTAŞ Tablo 1" if is_botas else f"{freq_tbl} / Çizelge 4-5",
            "is_mandatory": True,
        },
        {
            "test_key": "chemical_product",
            "category": "Kimyasal Analiz",
            "test_name": "Ürün Analizi (Product Analysis)",
            "standard_frequency": "Boru: ebat bazında her lot (per test unit)" if is_botas else "Isı başına 2 analiz (farklı borulardan)",
            "standard_frequency_en": "Once per lot of finished pipe" if is_botas else "Two analyses per heat of steel (taken from separate lengths)",
            "standard_acceptance_criteria": chem_crit,
            "clause_ref": "BOTAŞ Şartnamesi Madde 3.2.2.4 & Tablo 1" if is_botas else "API 5L Madde 9.2 & 10.2.1",
            "table_ref": "BOTAŞ Tablo 1" if is_botas else f"{freq_tbl} / Çizelge 4-5",
            "is_mandatory": True,
        },
        {
            "test_key": "tensile_body",
            "category": "Tahribatlı Mekanik",
            "test_name": "Gövde Çekme Testi (Pipe Body Tensile)",
            "standard_frequency": "Test ünitesi (lot) başına 2 set numune (1. set test, 2. set 5 yıl saklanır)" if is_botas else "Test ünitesi (lot / max 100 boru) başına 1 set",
            "standard_frequency_en": "Two sets per test unit (1st tested, 2nd retained for 5 years)" if is_botas else "Once per test unit of pipe with same cold-expansion ratio",
            "standard_acceptance_criteria": tensile_crit,
            "clause_ref": "BOTAŞ Şartnamesi Madde 3.3.1.4 & 3.3.2" if is_botas else "API 5L Madde 9.3 & 10.2.3",
            "table_ref": "BOTAŞ Tablo 2" if is_botas else f"{freq_tbl} / {piece_tbl} / Çizelge 6-7",
            "is_mandatory": True,
        },
    ]

    if is_welded:
        master_list.append({
            "test_key": "tensile_weld",
            "category": "Tahribatlı Mekanik",
            "test_name": "Kaynak Çekme Testi (Weld Tensile)",
            "standard_frequency": "Test ünitesi (lot) başına 1 test",
            "standard_frequency_en": "Once per test unit of pipe",
            "standard_acceptance_criteria": f"Rm ≥ {rm_min:.1f} MPa" + (", Min uzama ≥ %10 (BOTAŞ Madde 3.3.2.3)" if is_botas else " (Ana metal asgari çekme dayanımını karşılamalıdır)"),
            "clause_ref": "BOTAŞ Şartnamesi Madde 3.3.2.3" if is_botas else "API 5L Madde 9.3.2 & 10.2.3.3",
            "table_ref": "BOTAŞ Madde 3.3.2.3" if is_botas else f"{freq_tbl} / {piece_tbl}",
            "is_mandatory": True,
        })

    # CVN Impact
    master_list.append({
        "test_key": "cvn_body",
        "category": "Tahribatlı Mekanik",
        "test_name": "Gövde Çentik Darbe Testi (CVN Body Impact)",
        "standard_frequency": "Test ünitesi (lot) başına 1 set (3 numune) (-20 °C'de test)" if is_botas else ("PSL 2: Test ünitesi (lot) başına 1 set (3 numune); PSL 1: İsteğe bağlı" if not is_psl1 else "PSL 1: Zorunlu değil"),
        "standard_frequency_en": "Once per test unit of pipe (1 set = 3 specimens at -20 °C)" if is_botas else ("Once per test unit of pipe (1 set = 3 specimens)" if not is_psl1 else "Not mandatory for PSL 1"),
        "standard_acceptance_criteria": cvn_crit,
        "clause_ref": "BOTAŞ Şartnamesi Madde 3.3.5 & Tablo 3" if is_botas else "API 5L Madde 9.8 & 10.2.4.2",
        "table_ref": "BOTAŞ Tablo 3" if is_botas else f"{freq_tbl} / {piece_tbl} / Çizelge 8 & 22",
        "is_mandatory": not is_psl1,
    })

    if is_welded and not is_psl1:
        w_avg = 45.0 if (is_botas and grade in ("X60", "X65", "X70")) else cvn.get('weld_avg_j', 27.0)
        w_min = round(w_avg * 0.75, 1)
        temp_str = "-20 °C" if is_botas else "0 °C"
        master_list.append({
            "test_key": "cvn_weld_haz",
            "category": "Tahribatlı Mekanik",
            "test_name": "Kaynak & ITAB Çentik Darbe (CVN Weld & HAZ)",
            "standard_frequency": f"Test ünitesi başına 1 set kaynak + 1 set ITAB (3+3 numune) ({temp_str} test)",
            "standard_frequency_en": f"Once per test unit: 1 set weld seam + 1 set HAZ at {temp_str}",
            "standard_acceptance_criteria": f"Kaynak & ITAB ({temp_str}): Min Ort. {w_avg:.0f} J, Min Tek {w_min:.0f} J" + (" (BOTAŞ Tablo 3)" if is_botas else ""),
            "clause_ref": "BOTAŞ Şartnamesi Madde 3.3.5 & Tablo 3" if is_botas else "API 5L Madde 9.8.3 & 10.2.4.3",
            "table_ref": "BOTAŞ Tablo 3" if is_botas else f"{freq_tbl} / {piece_tbl}",
            "is_mandatory": True,
        })

    # DWTT
    if is_welded and d_mm >= 508.0 and not is_psl1:
        dwtt_crit = "Ortalama sünek kırılma alanı ≥ %85 ve hiçbir münferit numune < %60 olamaz (0 °C / BOTAŞ Madde 3.3.6.4)" if is_botas else "Her test için ortalama sünek kırılma alanı ≥ %85 (0 °C)"
        master_list.append({
            "test_key": "dwtt",
            "category": "Tahribatlı Mekanik",
            "test_name": "DWTT (Düşen Ağırlık Yırtılma Testi)",
            "standard_frequency": "Isı / test ünitesi başına 1 test (2 numune) (0 °C test)",
            "standard_frequency_en": "Once per test unit (2 specimens per test at 0 °C)",
            "standard_acceptance_criteria": dwtt_crit,
            "clause_ref": "BOTAŞ Şartnamesi Madde 3.3.6.4" if is_botas else "API 5L Madde 9.9 & 10.2.4.4",
            "table_ref": "BOTAŞ Madde 3.3.6" if is_botas else f"{freq_tbl} / {piece_tbl}",
            "is_mandatory": True,
        })

    # Guided Bend (Welded)
    if is_welded:
        master_list.append({
            "test_key": "guided_bend",
            "category": "Tahribatlı Mekanik",
            "test_name": "Kılavuzlu Bükme Testi (Guided-Bend)",
            "standard_frequency": "Test ünitesi (lot) başına 1 set (1 kök + 1 kapak veya 2 yan bükme)",
            "standard_frequency_en": "Once per test unit (1 root + 1 face or 2 side bend specimens)",
            "standard_acceptance_criteria": "Kök ve kapak bükmede kaynak/ITAB'da > 3.2 mm çatlak/kusur oluşmayacak",
            "clause_ref": "BOTAŞ Madde 3.3.4 / API 5L 9.7",
            "table_ref": f"{freq_tbl} / {piece_tbl}",
            "is_mandatory": True,
        })

    # Hardness Test
    master_list.append({
        "test_key": "hardness",
        "category": "Tahribatlı Mekanik",
        "test_name": "Sertlik Testi (Hardness Testing)",
        "standard_frequency": "Test ünitesi (lot) başına",
        "standard_frequency_en": "Once per test unit",
        "standard_acceptance_criteria": "Maksimum 300 HV10 (Aşılması durumunda o dökümdeki boruların %100'ü test edilir)" if is_botas else "PSL 2 Sipariş koşulu / Ek H-J-N: ≤ 300 HV10 (Ek N: ≤ 250 HV10)",
        "clause_ref": "BOTAŞ Şartnamesi Madde 3.3.7" if is_botas else "API 5L Madde 10.2.4.8 & 9.10.6",
        "table_ref": "BOTAŞ Madde 3.3.7" if is_botas else f"{freq_tbl} / {piece_tbl}",
        "is_mandatory": True,
    })

    # Residual Stress Test (BOTAŞ Mandatory for welded SAWH / LSAW)
    if is_welded and is_botas:
        master_list.append({
            "test_key": "residual_stress",
            "category": "Tahribatlı Mekanik",
            "test_name": "Artık Stres Testi (Residual Stress Ring Test)",
            "standard_frequency": "Her çap ve et kalınlığı için ve ÇAP/ET KALINLIĞI DEĞİŞMESE DAHİ HER DÖKÜM (HEAT) İÇİN 1 halka",
            "standard_frequency_en": "Once per heat even if diameter and wall thickness do not change (150 mm ring)",
            "standard_acceptance_criteria": "Artık stres S = (E·t·C) / (12.566·D²) ≤ 0.10 × SMYS (BOTAŞ Madde 3.3.9.3)",
            "clause_ref": "BOTAŞ Şartnamesi Madde 3.3.9",
            "table_ref": "BOTAŞ 4-NGTL-0-GN-P-002-5120 R7",
            "is_mandatory": True,
        })

    # Flattening (ERW/HFW)
    if "ERW" in process or "HFW" in process:
        master_list.append({
            "test_key": "flattening",
            "category": "Tahribatlı Mekanik",
            "test_name": "Düzleştirme Testi (Flattening)",
            "standard_frequency": "Her rulo (bobin) başı ve sonu (Şekil 6) ve/veya lot başına",
            "standard_frequency_en": "At crop ends of each coil / per test unit",
            "standard_acceptance_criteria": "Kaynak açılması: %50/%66 mesafeye kadar açılma yok; Karşı yüzeyler değene kadar füzyon hatası/laminasyon yok",
            "clause_ref": "API 5L Madde 9.6 & 10.2.4.5",
            "table_ref": f"{freq_tbl} / {piece_tbl}",
            "is_mandatory": True,
        })

    # Hydrostatic Test
    master_list.append({
        "test_key": "hydrostatic",
        "category": "Basınç & Mukavemet",
        "test_name": "Fabrika Hidrostatik Basınç Testi",
        "standard_frequency": "Her boru (%100 tüm borular)",
        "standard_frequency_en": "Each pipe (100% of all pipes)",
        "standard_acceptance_criteria": hydro_crit,
        "clause_ref": "BOTAŞ Şartnamesi Madde 8.4.1 & 8.4.2" if is_botas else "API 5L Madde 9.4 & 10.2.6",
        "table_ref": "BOTAŞ Madde 8.4" if is_botas else f"{freq_tbl} / Çizelge 26",
        "is_mandatory": True,
    })

    # NDT of Weld Seam
    if is_welded:
        master_list.append({
            "test_key": "ndt_weld_seam",
            "category": "Tahribatsız Muayene (NDT)",
            "test_name": "Kaynak Dikişi %100 Tahribatsız Muayene (UT / RT)",
            "standard_frequency": "Her kaynaklı boru tam boy dikişi (%100)",
            "standard_frequency_en": "100% of weld seam of each pipe",
            "standard_acceptance_criteria": "Kaynaktan hemen sonra On-line UT + Hidro/tamir/ısıl işlem sonrası Off-line Radyolojik Muayene (BOTAŞ Madde 8.8.4.2)" if is_botas else "Ek E (Annex E) kabul seviyelerine uygun (Kabul edilemez çatlak, füzyon noksanlığı, gözenek yok)",
            "clause_ref": "BOTAŞ Şartnamesi Madde 8.8.4.2 & 8.8.4.3" if is_botas else "API 5L Madde 9.13 & Ek E (Annex E)",
            "table_ref": "BOTAŞ Madde 8.8.4" if is_botas else f"{freq_tbl} / Ek E",
            "is_mandatory": True,
        })

    # Pipe Body UT Lamination (BOTAŞ Mandatory min 40% scan)
    if is_botas:
        master_list.append({
            "test_key": "ndt_pipe_body_lamination",
            "category": "Tahribatsız Muayene (NDT)",
            "test_name": "Boru Gövdesi UT Laminasyon Muayenesi (Body Laminar Testing)",
            "standard_frequency": "Boru formu verildikten sonra boru gövde yüzeyinin EN AZ %40'INI TARAYACAK ŞEKİLDE",
            "standard_frequency_en": "Scanning at least 40% of the pipe body surface after forming",
            "standard_acceptance_criteria": "ISO 12094 Sınıf B1 kabul kriterleri (Rulo/sac tamamı B1)",
            "clause_ref": "BOTAŞ Şartnamesi Madde 8.8.4.4.1",
            "table_ref": "ISO 12094 B1 / BOTAŞ",
            "is_mandatory": True,
        })

    # NDT of Pipe Ends
    master_list.append({
        "test_key": "ndt_pipe_ends",
        "category": "Tahribatsız Muayene (NDT)",
        "test_name": "Boru Uçları Laminasyon Kontrolü (UT Laminar Testing)",
        "standard_frequency": "Her boru (%100) uç kısımlarında en az 50 mm genişlikte bölge" if is_botas else "Her boru (%100) uç kısımları (min 100 mm çevre boyunca)",
        "standard_frequency_en": "100% of pipe ends of each pipe (min 50 mm band)" if is_botas else "100% of pipe ends of each pipe (min 100 mm band)",
        "standard_acceptance_criteria": "Boru uçlarında en az 50 mm bant boyunca %100 laminasyon kontrolü (Madde 8.8.4.4.2)" if is_botas else "Ek E.8 gereği > 6.0 mm veya > 100 mm² laminasyon hatası bulunmayacaktır",
        "clause_ref": "BOTAŞ Şartnamesi Madde 8.8.4.4.2" if is_botas else "API 5L Ek E.8",
        "table_ref": "BOTAŞ Madde 8.8.4.4.2" if is_botas else f"{freq_tbl} / Ek E.8",
        "is_mandatory": True,
    })

    # NDT of Seamless Body
    if is_smls:
        master_list.append({
            "test_key": "ndt_smls_body",
            "category": "Tahribatsız Muayene (NDT)",
            "test_name": "Dikişsiz Boru Gövde NDT (UT / Flux Leakage)",
            "standard_frequency": "PSL 2: Her boru (%100 tam boy); PSL 1: Sipariş şartına göre",
            "standard_frequency_en": "100% of each pipe full body (PSL 2)",
            "standard_acceptance_criteria": "Ek E uyarınca boyuna ve enine kusurlar için N5/L2 seviyesi",
            "clause_ref": "API 5L Madde 9.13 & Ek E.3",
            "table_ref": f"{freq_tbl} / Ek E",
            "is_mandatory": not is_psl1,
        })

    # Dimensional - Diameter & Out of Roundness
    dia_tol = dim.get("diameter_pipe_body_tol_mm", "±0.5% (Max ±4.0 mm)")
    ovality_tol = dim.get("out_of_roundness_body_max_mm", "≤ 15.0 mm")
    master_list.append({
        "test_key": "dimensional_diameter_ovality",
        "category": "Boyutsal & Görsel",
        "test_name": "Dış Çap ve Ovallik Kontrolü (Diameter & Ovality)",
        "standard_frequency": "D ≥ 20\" borularda %100 tüm borular (Madde 8.1.2.4); D < 20\" borularda vardiya başı / soğuk genişletme" if is_botas else "Vardiya başına en az her 4 saatte bir ve soğuk genişletilen borularda her boru (%100)",
        "standard_frequency_en": "100% of pipes for D >= 20\"" if is_botas else "At least once per 4 hours per operating shift / each pipe for cold-expanded",
        "standard_acceptance_criteria": f"Gövde Çap Toleransı: {dia_tol}, Boru Ucu Ovallik Toleransı: API 5L Çizelge 10 değerlerinin %50'si (BOTAŞ Madde 5.1)" if is_botas else f"Gövde Çap Toleransı: {dia_tol}, Maksimum Ovallik: {ovality_tol} (Tablo 10)",
        "clause_ref": "BOTAŞ Şartnamesi Madde 5.1 & 8.1.2.4" if is_botas else "API 5L Madde 9.11 & 10.2.8.1",
        "table_ref": "BOTAŞ Madde 5.1" if is_botas else f"{freq_tbl} / Çizelge 10",
        "is_mandatory": True,
    })

    # Dimensional - Wall Thickness
    master_list.append({
        "test_key": "dimensional_wall_thickness",
        "category": "Boyutsal & Görsel",
        "test_name": "Et Kalınlığı Ölçümü (Wall Thickness Verification)",
        "standard_frequency": "Her boru (%100) uçlardan ve gövdeden ultrasonik/kumpas ile",
        "standard_frequency_en": "Each pipe (100%)",
        "standard_acceptance_criteria": "Sac/plaka eksi toleransı: t ≤ 8.7 mm: -0.04 mm; 9.5-12.7 mm: -0.10 mm; ≥14.3 mm: -0.15 mm (BOTAŞ Tablo 4)" if is_botas else "Tolerans: -%8.0 / -%10.0 / -%12.5 (API 5L Tablo 11)",
        "clause_ref": "BOTAŞ Şartnamesi Madde 5.2 (Tablo 4)" if is_botas else "API 5L Madde 9.11.2 & 10.2.8.2",
        "table_ref": "BOTAŞ Tablo 4" if is_botas else f"{freq_tbl} / Çizelge 11",
        "is_mandatory": True,
    })

    # Dimensional - Length & Straightness & Bevel
    master_list.append({
        "test_key": "dimensional_length_straightness_bevel",
        "category": "Boyutsal & Görsel",
        "test_name": "Doğrusallık, Boy ve Alın Kaynak Ağzı (Straightness, Length & Bevel)",
        "standard_frequency": "Her boru (%100)",
        "standard_frequency_en": "Each pipe (100%)",
        "standard_acceptance_criteria": "Doğrusallıktan sapma ≤ %0.10 L (≤ 0.001 x L); Kaynak bitiş noktası dairesellik sapması ≤ %0.15 x D (R/2 mastar ile); Boy: 8-14.5m (ort. min 12m) (BOTAŞ Madde 5.4, 5.5 & 7.2)" if is_botas else "Sapma ≤ %0.20 L (Uçlarda ≤ 3.2 mm / 1.5 m); Kaynak ağzı: 30° (+5°/-0°), Kök yüzeyi: 1.6 ± 0.8 mm (9.11.3)",
        "clause_ref": "BOTAŞ Şartnamesi Madde 5.4, 5.5 & 7.2" if is_botas else "API 5L Madde 9.11.3 & 10.2.8.3 / 10.2.8.4",
        "table_ref": "BOTAŞ Madde 5.4, 5.5" if is_botas else f"{freq_tbl} / Çizelge 12",
        "is_mandatory": True,
    })

    # Visual Inspection
    master_list.append({
        "test_key": "visual_surface",
        "category": "Boyutsal & Görsel",
        "test_name": "Görsel Yüzey ve Kusur Muayenesi (Visual Inspection)",
        "standard_frequency": "D ≥ 20\" borularda istisnasız %100 boru kaynağı (iç/dış) ve %100 gövde (iç/dış) görsel muayenesi" if is_botas else "Her boru (%100 iç ve dış yüzey)",
        "standard_frequency_en": "100% internal and external surface of each pipe",
        "standard_acceptance_criteria": "EN 10163-2 Sınıf B Altsınıf 3 (Keskin köşeli hata kabul edilmez, gövde/kaynak çatlak yok)" if is_botas else "Çatlak, katmer, kabuk, derin çizik (> %12.5 t) ve yüzey defekti bulunmayacaktır (Madde 9.10.1)",
        "clause_ref": "BOTAŞ Şartnamesi Madde 3.1.5, 8.1.2.1, 8.1.2.2 & 9.1" if is_botas else "API 5L Madde 9.10.1 & 10.2.7",
        "table_ref": "BOTAŞ Madde 8.1.2" if is_botas else freq_tbl,
        "is_mandatory": True,
    })

    # Residual Magnetism
    master_list.append({
        "test_key": "residual_magnetism",
        "category": "Özel Denetim",
        "test_name": "Kalıntı Manyetizma Ölçümü (Residual Magnetism)",
        "standard_frequency": "Vardiyada EN AZ İKİ DEFA ölçülerek kayıt altına alınır" if is_botas else "Vardiyada her 4 saatte bir ve sevkiyat öncesi her boru uçlarından",
        "standard_frequency_en": "At least twice per shift" if is_botas else "At least once per 4 hours and prior to dispatch",
        "standard_acceptance_criteria": "Ortalama ≤ 3.0 mT (30 Gauss), hiçbir münferit nokta > 3.5 mT (35 Gauss) olmayacaktır (Madde 8.1.1 / 9.14)",
        "clause_ref": "BOTAŞ Şartnamesi Madde 8.1.1" if is_botas else "API 5L Madde 9.14 & 10.2.10",
        "table_ref": "BOTAŞ Madde 8.1.1" if is_botas else freq_tbl,
        "is_mandatory": True,
    })

    return master_list