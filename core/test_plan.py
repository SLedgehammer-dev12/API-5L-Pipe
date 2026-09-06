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

import math
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


def get_comprehensive_itp_specification(pipe_config: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
    """
    Returns the comprehensive Master Inspection & Test Plan (ITP) matrix for API 5L 47th Edition and BOTAŞ specifications.
    Dynamically integrates all calculated values (40+ parameters) from PipeQAQCEngine:
      - Hydrostatic test pressure (Barlow formula) & duration (20s BOTAŞ / 10s API)
      - Tensile properties (Rt0.5 min/max, Rm min/max, calculated Af elongation % from Axc, Y/T ratio)
      - CVN impact energy & temperature (-20°C BOTAŞ / 0°C API)
      - DWTT drop weight shear area (>= 85%)
      - Guided-bend mandrel diameter (Ag) & jaw opening (Bg)
      - Residual stress ring test limit (0.10 x SMYS MPa & delta mm)
      - Unit weight per meter (W kg/m) and single/carload tolerances (-3.5%/+10%)
      - Complete dimensional tolerances (diameter body/ends, ovality, thickness min/max mm, straightness, bevel, squareness)
      - Weld seam geometry (reinforcement height, radial offset, misalignment, peaking)
      - NDT examination standards (ISO 10893-11/6/8/9, Level U2, Class B)
      - Weld repair conditions (max 150 mm length, 300 mm end ban, 100°C preheat, post-repair RT & re-hydro)
      - Quality certification (EN 10204 3.1/3.2, marking, Sa 2.5 surface preparation)
    """
    from core.pipe_qaqc_engine import PipeQAQCEngine

    cfg = pipe_config or {}
    d_mm = float(cfg.get("diameter_mm") or 1219.0)
    d_inch = cfg.get("diameter_inch", '48"')
    t_mm = float(cfg.get("wall_thickness_mm") or 14.30)
    grade = (cfg.get("material_grade") or "X65").upper()
    process = (cfg.get("manufacturing_process") or "SAWH").upper()
    std_type = (cfg.get("standard_type") or cfg.get("standard_code") or "API").upper()
    is_botas = "BOTAŞ" in std_type or "BOTAS" in std_type
    psl_level = (cfg.get("psl_level") or "PSL2").upper()
    delivery_condition = cfg.get("delivery_condition", "M")

    is_smls = "SMLS" in process or "SEAMLESS" in process or "DIKISSIZ" in process
    is_welded = not is_smls
    is_saw = is_welded and any(p in process for p in ("SAW", "SAWH", "LSAW", "COW"))
    is_psl1 = "PSL1" in psl_level
    freq_tbl = "Çizelge 17 (Table 17)" if is_psl1 else "Çizelge 18 (Table 18)"
    piece_tbl = "Çizelge 19 (Table 19)" if is_psl1 else "Çizelge 20 (Table 20)"

    # Compute full QA/QC parameters dynamically from PipeQAQCEngine
    qc = PipeQAQCEngine.calculate_pipe_qc(
        diameter_inch=d_inch,
        diameter_mm=d_mm,
        wall_thickness_mm=t_mm,
        design_factor_str=cfg.get("design_factor_str", "0.72 (Hat)"),
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
    weld = qc.get("weld_and_geometry", {})
    wall_tol = qc.get("wall_thickness_tolerance", {})
    weights = qc.get("weights_and_safety", {})

    # Chemical limits
    c_max = chem.get("C_max")
    if c_max is None:
        c_max = 0.12 if is_botas else 0.16
    p_max = chem.get("P_max")
    if p_max is None:
        p_max = 0.025 if is_botas else 0.020
    s_max = chem.get("S_max")
    if s_max is None:
        s_max = 0.010 if is_botas else 0.010
    ce_iiw_max = 0.40 if is_botas else chem.get("CE_IIW_max")
    ce_pcm_max = 0.22 if is_botas else chem.get("CE_Pcm_max")
    ce_str = f", CE_IIW ≤ {ce_iiw_max:.2f}" if ce_iiw_max else (f", CE_Pcm ≤ {ce_pcm_max:.2f}" if ce_pcm_max else "")
    
    if is_botas:
        chem_crit = f"C ≤ {c_max:.2f}%, P ≤ {p_max:.3f}%, S ≤ {s_max:.3f}%, N ≤ 0.009%{ce_str} (BOTAŞ Madde 3.2 & Tablo 1)"
    elif chem.get("as_agreed"):
        chem_crit = f"t > 25.0 mm: Kimyasal bileşim anlaşmaya bağlıdır (API 5L 9.2.3). Tipik: C ≤ {c_max:.2f}%, P ≤ {p_max:.3f}%, S ≤ {s_max:.3f}%{ce_str}"
    else:
        chem_crit = f"C ≤ {c_max:.2f}%, P ≤ {p_max:.3f}%, S ≤ {s_max:.3f}%{ce_str} (API 5L Çizelge 5)"

    # Tensile limits
    rt05_min = mech.get("yield_min_mpa", 450.0)
    rt05_max = mech.get("yield_max_mpa")
    rm_min = mech.get("tensile_min_mpa", 535.0)
    rm_max = mech.get("tensile_max_mpa", 760.0)
    af_min = cvn.get("elongation_mat_min_percent", 19.5)
    yt_max = 0.90 if (is_botas and grade in ("X60", "X65", "X70")) else mech.get("yield_to_tensile_ratio_max", 0.93)
    rt_str = f"Rt0.5: {rt05_min:.1f}" + (f" - {rt05_max:.1f} MPa" if rt05_max else " MPa min")
    rm_str = f"Rm: {rm_min:.1f}" + (f" - {rm_max:.1f} MPa" if rm_max else " MPa min")
    yt_str = f", Y/T ≤ {yt_max:.2f}" if yt_max else ""
    tensile_crit = f"{rt_str}, {rm_str}, Af ≥ {af_min:.1f}%{yt_str}"

    # CVN limits
    cvn_temp = -20 if is_botas else 0
    if is_psl1:
        cvn_body_avg = 0.0
        cvn_body_min = 0.0
        cvn_crit = "PSL 1'de Çentik Darbe (CVN) zorunlu değildir."
    elif is_botas:
        cvn_body_avg = cvn.get("notch_impact_mat_j", 60.0)
        cvn_body_min = round(cvn_body_avg * 0.75, 1)
        cvn_crit = f"Gövde (-20 °C): Min Ort. {cvn_body_avg:.0f} J, Min Tek {cvn_body_min:.0f} J (BOTAŞ Tablo 3)"
    else:
        cvn_body_avg = cvn.get("notch_impact_mat_j", 41.0)
        cvn_body_min = round(cvn_body_avg * 0.75, 1)
        cvn_crit = f"Gövde (0 °C): Min Ort. {cvn_body_avg:.0f} J, Min Tek {cvn_body_min:.0f} J (API 5L Çizelge 8)"

    # Hydrostatic limits
    hydro_p = hydro.get("hydro_test_max_bar", 100.0)
    min_acceptable_p = round(hydro_p - 2.0, 1) if is_botas else round(float(hydro.get("api_5l_std_test_bar", hydro_p * 0.90)), 1)
    if is_botas:
        hydro_time = 20
        hydro_crit = f"Min Test Basıncı: {hydro_p:.1f} bar (SMYS %100, +0/-2 bar), Min Tutma Süresi: 20 saniye (BOTAŞ Madde 8.4)"
    else:
        hydro_time = 10 if (is_welded and d_mm > 457.0) else 5
        hydro_crit = f"Min Test Basıncı: {hydro_p:.1f} bar, Min Tutma Süresi: {hydro_time} saniye (API 5L 10.2.6.2 & Tablo 26)"

    # Guided Bend Mandrel & Jaw Opening
    mandrel_dia = cvn.get("mandrel_dia_max_mm", 200.0)
    if not isinstance(mandrel_dia, (int, float)):
        mandrel_dia = 200.0
    jaw_opening = cvn.get("jaw_opening_max_mm", mandrel_dia + 3.2 + (2.0 * t_mm))
    if not isinstance(jaw_opening, (int, float)):
        jaw_opening = mandrel_dia + 3.2 + (2.0 * t_mm)

    # Unit Weight
    weight_nom = weights.get("weight_nominal_kg_m", 0.0246615 * t_mm * (d_mm - t_mm))
    weight_min = weights.get("weight_min_kg_m", round(weight_nom * (1.0 - 0.035), 2))
    weight_max = weights.get("weight_max_kg_m", round(weight_nom * (1.0 + 0.10), 2))

    # Dimensional & Circumference tolerances
    d_body_min = dim.get("diameter_body_min_mm", d_mm - 4.0)
    d_body_max = dim.get("diameter_body_max_mm", d_mm + 4.0)
    d_end_min = dim.get("diameter_end_min_mm", d_mm - 1.6)
    d_end_max = dim.get("diameter_end_max_mm", d_mm + 1.6)
    dia_body_tol = round((d_body_max - d_body_min) / 2.0, 1)

    circ_end_min = dim.get("circ_end_min_mm", round(d_end_min * math.pi, 2)) if isinstance(dim.get("circ_end_min_mm"), (int, float)) else round(d_end_min * math.pi, 2)
    circ_end_max = dim.get("circ_end_max_mm", round(d_end_max * math.pi, 2)) if isinstance(dim.get("circ_end_max_mm"), (int, float)) else round(d_end_max * math.pi, 2)
    circ_body_min = dim.get("circ_body_min_mm", round(d_body_min * math.pi, 2)) if isinstance(dim.get("circ_body_min_mm"), (int, float)) else round(d_body_min * math.pi, 2)
    circ_body_max = dim.get("circ_body_max_mm", round(d_body_max * math.pi, 2)) if isinstance(dim.get("circ_body_max_mm"), (int, float)) else round(d_body_max * math.pi, 2)

    ovality_end = dim.get("ovality_end_mm", 3.05 if is_botas else 6.10)
    if not isinstance(ovality_end, (int, float)):
        ovality_end = 3.05 if is_botas else 6.10

    ovality_body = dim.get("ovality_body_mm", 6.10 if is_botas else 18.30)
    if not isinstance(ovality_body, (int, float)):
        ovality_body = 6.10 if is_botas else 18.30

    if is_botas:
        t_neg_pct = 8.0
        t_pos_pct = 15.0 if t_mm < 15.0 else 10.0
        t_min = round(t_mm * (1.0 - t_neg_pct / 100.0), 2)
        t_max = round(t_mm * (1.0 + t_pos_pct / 100.0), 2)
    else:
        t_min = wall_tol.get("min_mm", round(t_mm * 0.90, 2))
        t_max = wall_tol.get("max_mm", round(t_mm * 1.10, 2))
        t_neg_pct = round(((t_mm - t_min) / t_mm) * 100.0, 1)
        t_pos_pct = round(((t_max - t_mm) / t_mm) * 100.0, 1)

    straightness_pct = 0.10 if is_botas else 0.20
    squareness_max = dim.get("pipe_end_squareness_max_mm", 1.6)

    # Weld geometry
    weld_h_val = weld.get("weld_height_inside_mm")
    weld_h_max = weld_h_val if isinstance(weld_h_val, (int, float)) else (2.625 if is_botas else 3.50)

    rad_val = weld.get("radial_offset_max_mm")
    radial_offset = rad_val if isinstance(rad_val, (int, float)) else (1.125 if is_botas else (1.50 if t_mm <= 15.0 else round(0.10 * t_mm, 2)))

    peak_val = dim.get("pipe_end_peaking_max_mm")
    peaking_max = peak_val if isinstance(peak_val, (int, float)) else (1.50 if is_botas else round(d_mm * 0.0015, 2))

    mis_val = weld.get("misalignment_max_mm")
    misalignment_max = mis_val if isinstance(mis_val, (int, float)) else (2.25 if is_botas else 3.0)

    # Residual Stress
    residual_stress_max_mpa = round(0.10 * rt05_min, 1)
    delta_max = round(cvn.get("residual_stress_max_mm", 3.5), 2) if isinstance(cvn.get("residual_stress_max_mm"), (int, float)) else 3.5

    master_list: List[Dict[str, Any]] = [
        # 1. Chemical Heat Analysis
        {
            "test_key": "chemical_heat",
            "category": "Kimyasal Analiz",
            "test_name": "Isı Analizi (Heat Analysis)",
            "standard_frequency": "Hammadde: ebat bazında her döküm (per heat)" if is_botas else "Isı (Döküm) başına 1 analiz",
            "standard_frequency_en": "One analysis per heat of steel (raw material)",
            "standard_acceptance_criteria": chem_crit,
            "clause_ref": "BOTAŞ Şartnamesi Madde 3.2.2.4 & Tablo 1" if is_botas else "API 5L Madde 9.2 & 10.2.1",
            "table_ref": "BOTAŞ Tablo 1" if is_botas else f"{freq_tbl} / Çizelge 4-5",
            "ndt_method_standard": "ASTM A751 / ISO 14284 (OES / XRF Spektrometre)",
            "ndt_acceptance_level": "API 5L Çizelge 5 / BOTAŞ Tablo 1 Limitleri",
            "calculated_target_str": f"C ≤ {c_max:.2f}%, P ≤ {p_max:.3f}%, S ≤ {s_max:.3f}%{ce_str}",
            "calculated_targets": {"C_max": c_max, "P_max": p_max, "S_max": s_max, "CE_IIW_max": ce_iiw_max, "CE_Pcm_max": ce_pcm_max, "N_max": 0.009 if is_botas else None},
            "is_mandatory": True,
        },
        # 2. Chemical Product Analysis
        {
            "test_key": "chemical_product",
            "category": "Kimyasal Analiz",
            "test_name": "Ürün Analizi (Product Analysis)",
            "standard_frequency": "Boru: ebat bazında her lot (per test unit)" if is_botas else "Isı başına 2 analiz (farklı borulardan)",
            "standard_frequency_en": "Once per lot of finished pipe" if is_botas else "Two analyses per heat of steel (taken from separate lengths)",
            "standard_acceptance_criteria": chem_crit,
            "clause_ref": "BOTAŞ Şartnamesi Madde 3.2.2.4 & Tablo 1" if is_botas else "API 5L Madde 9.2 & 10.2.1",
            "table_ref": "BOTAŞ Tablo 1" if is_botas else f"{freq_tbl} / Çizelge 4-5",
            "ndt_method_standard": "ISO 14284 / ASTM A751",
            "ndt_acceptance_level": "API 5L Çizelge 5 / BOTAŞ Tablo 1 Limitleri",
            "calculated_target_str": f"C ≤ {c_max:.2f}%, P ≤ {p_max:.3f}%, S ≤ {s_max:.3f}%{ce_str}",
            "calculated_targets": {"C_max": c_max, "P_max": p_max, "S_max": s_max, "CE_IIW_max": ce_iiw_max, "CE_Pcm_max": ce_pcm_max, "N_max": 0.009 if is_botas else None},
            "is_mandatory": True,
        },
        # 3. Pipe Body Tensile Test
        {
            "test_key": "tensile_body",
            "category": "Tahribatlı Mekanik",
            "test_name": "Gövde Çekme Testi (Pipe Body Tensile)",
            "standard_frequency": "Test ünitesi (lot) başına 2 set numune (1. set test, 2. set 5 yıl saklanır)" if is_botas else "Test ünitesi (lot / max 100 boru) başına 1 set",
            "standard_frequency_en": "Two sets per test unit (1st tested, 2nd retained for 5 years)" if is_botas else "Once per test unit of pipe with same cold-expansion ratio",
            "standard_acceptance_criteria": tensile_crit,
            "clause_ref": "BOTAŞ Şartnamesi Madde 3.3.1.4 & 3.3.2" if is_botas else "API 5L Madde 9.3 & 10.2.3",
            "table_ref": "BOTAŞ Tablo 2" if is_botas else f"{freq_tbl} / {piece_tbl} / Çizelge 6-7",
            "ndt_method_standard": "ISO 6892-1 / ASTM A370 (Gövde Enine / Boyuna Numune)",
            "ndt_acceptance_level": f"Rt0.5 ≥ {rt05_min:.1f} MPa, Rm ≥ {rm_min:.1f} MPa, Af ≥ %{af_min:.1f}",
            "calculated_target_str": f"Rt0.5: {rt05_min:.1f} - {rt05_max or 760.0:.1f} MPa, Rm: {rm_min:.1f} - {rm_max or 760.0:.1f} MPa, Af ≥ %{af_min:.1f}{yt_str}",
            "calculated_targets": {"yield_min_mpa": rt05_min, "yield_max_mpa": rt05_max, "tensile_min_mpa": rm_min, "tensile_max_mpa": rm_max, "elongation_min_pct": af_min, "yt_max": yt_max},
            "is_mandatory": True,
        },
    ]

    # 4. Weld Seam Tensile Test (Welded)
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
            "ndt_method_standard": "ISO 6892-1 / ASTM A370 (Enine Kaynak Numunesi)",
            "ndt_acceptance_level": f"Rm ≥ {rm_min:.1f} MPa",
            "calculated_target_str": f"Rm ≥ {rm_min:.1f} MPa (Gövde Asgari Dayanımı)" + (", Kopma Uzaması ≥ %10" if is_botas else ""),
            "calculated_targets": {"tensile_min_mpa": rm_min, "weld_elongation_min_pct": 10.0 if is_botas else None},
            "is_mandatory": True,
        })

    # 5. CVN Body Impact
    master_list.append({
        "test_key": "cvn_body",
        "category": "Tahribatlı Mekanik",
        "test_name": "Gövde Çentik Darbe Testi (CVN Body Impact)",
        "standard_frequency": "Test ünitesi (lot) başına 1 set (3 numune) (-20 °C'de test)" if is_botas else ("PSL 2: Test ünitesi (lot) başına 1 set (3 numune); PSL 1: İsteğe bağlı" if not is_psl1 else "PSL 1: Zorunlu değil"),
        "standard_frequency_en": "Once per test unit of pipe (1 set = 3 specimens at -20 °C)" if is_botas else ("Once per test unit of pipe (1 set = 3 specimens)" if not is_psl1 else "Not mandatory for PSL 1"),
        "standard_acceptance_criteria": cvn_crit,
        "clause_ref": "BOTAŞ Şartnamesi Madde 3.3.5 & Tablo 3" if is_botas else "API 5L Madde 9.8 & 10.2.4.2",
        "table_ref": "BOTAŞ Tablo 3" if is_botas else f"{freq_tbl} / {piece_tbl} / Çizelge 8 & 22",
        "ndt_method_standard": f"ISO 148-1 / ASTM A370 (Charpy V-Çentik {cvn_temp} °C)",
        "ndt_acceptance_level": f"Min Ortalama: {cvn_body_avg:.0f} J, Min Tekil: {cvn_body_min:.0f} J",
        "calculated_target_str": f"Test Sıcaklığı: {cvn_temp} °C | Min Ortalama: {cvn_body_avg:.0f} J, Min Münferit: {cvn_body_min:.0f} J",
        "calculated_targets": {"temp_c": cvn_temp, "avg_j": cvn_body_avg, "min_j": cvn_body_min},
        "is_mandatory": not is_psl1,
    })

    # 6. CVN Weld & HAZ Impact
    if is_welded and not is_psl1:
        cvn_weld_avg = cvn.get("notch_impact_weld_j", 36.0 if is_botas else 27.0)
        cvn_weld_min = round(cvn_weld_avg * 0.75, 1)
        temp_str = "-20 °C" if is_botas else "0 °C"
        master_list.append({
            "test_key": "cvn_weld_haz",
            "category": "Tahribatlı Mekanik",
            "test_name": "Kaynak & ITAB Çentik Darbe (CVN Weld & HAZ)",
            "standard_frequency": f"Test ünitesi başına 1 set kaynak + 1 set ITAB (3+3 numune) ({temp_str} test)",
            "standard_frequency_en": f"Once per test unit: 1 set weld seam + 1 set HAZ at {temp_str}",
            "standard_acceptance_criteria": f"Kaynak & ITAB ({temp_str}): Min Ort. {cvn_weld_avg:.0f} J, Min Tek {cvn_weld_min:.0f} J" + (" (BOTAŞ Tablo 3)" if is_botas else ""),
            "clause_ref": "BOTAŞ Şartnamesi Madde 3.3.5 & Tablo 3" if is_botas else "API 5L Madde 9.8.3 & 10.2.4.3",
            "table_ref": "BOTAŞ Tablo 3" if is_botas else f"{freq_tbl} / {piece_tbl}",
            "ndt_method_standard": f"ISO 148-1 / ASTM A370 (Kaynak Ekseni ve Füzyon Hattı {temp_str})",
            "ndt_acceptance_level": f"Min Ortalama: {cvn_weld_avg:.0f} J, Min Tekil: {cvn_weld_min:.0f} J",
            "calculated_target_str": f"Test Sıcaklığı: {temp_str} | Min Ortalama: {cvn_weld_avg:.0f} J, Min Münferit: {cvn_weld_min:.0f} J",
            "calculated_targets": {"temp_c": cvn_temp, "avg_j": cvn_weld_avg, "min_j": cvn_weld_min},
            "is_mandatory": True,
        })

    # 7. DWTT (Drop Weight Tear Test)
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
            "ndt_method_standard": "API RP 5L3 / ASTM E436 (Düşen Ağırlık Yırtılma Testi)",
            "ndt_acceptance_level": "Ortalama Sünek Alan ≥ %85, Tekil ≥ %60",
            "calculated_target_str": "Test Sıcaklığı: 0 °C | Ortalama Sünek Kırılma Alanı ≥ %85, Tekil Numune ≥ %60",
            "calculated_targets": {"temp_c": 0, "avg_shear_pct": 85.0, "min_shear_pct": 60.0},
            "is_mandatory": True,
        })

    # 8. Guided Bend (Welded SAW / COW only - Not applicable to ERW/HFW)
    if is_welded and not ("ERW" in process or "HFW" in process):
        master_list.append({
            "test_key": "guided_bend",
            "category": "Tahribatlı Mekanik",
            "test_name": "Kılavuzlu Bükme Testi (Guided-Bend)",
            "standard_frequency": "Test ünitesi (lot) başına 1 set (1 kök + 1 kapak veya 2 yan bükme)",
            "standard_frequency_en": "Once per test unit (1 root + 1 face or 2 side bend specimens)",
            "standard_acceptance_criteria": f"Mandrel Ag: {mandrel_dia:.1f} mm, Çene Bg: {jaw_opening:.1f} mm; 180° bükmede kaynak/ITAB'da > 3.2 mm çatlak oluşmayacak",
            "clause_ref": "BOTAŞ Madde 3.1.6 & 3.3.4 / API 5L 9.7 & 10.2.4.6",
            "table_ref": f"{freq_tbl} / {piece_tbl} / Çizelge 15",
            "ndt_method_standard": "ISO 5173 / ASTM A370 / API 5L Madde 10.2.4.6",
            "ndt_acceptance_level": "180° bükme sonrası kusur/çatlak boyutu ≤ 3.2 mm",
            "calculated_target_str": f"Mandrel Çapı Ag: {mandrel_dia:.1f} mm, Çene Açıklığı Bg: {jaw_opening:.1f} mm | Maks Kusur ≤ 3.2 mm",
            "calculated_targets": {"mandrel_dia_mm": mandrel_dia, "jaw_opening_mm": jaw_opening, "max_crack_mm": 3.2},
            "is_mandatory": True,
        })

    # 9. Hardness Testing
    hardness_max = 250.0 if "SOUR" in std_type or "ANNEX H" in std_type else 300.0
    master_list.append({
        "test_key": "hardness",
        "category": "Tahribatlı Mekanik",
        "test_name": "Sertlik Testi (Hardness Testing)",
        "standard_frequency": "Test ünitesi (lot) başına 1 makro enine kesit",
        "standard_frequency_en": "Once per test unit",
        "standard_acceptance_criteria": f"Maksimum {hardness_max:.0f} HV10 (Aşılması durumunda o dökümdeki boruların %100'ü test edilir)" if is_botas else f"Maksimum ≤ {hardness_max:.0f} HV10 (Gövde, ITAB, Kaynak)",
        "clause_ref": "BOTAŞ Şartnamesi Madde 3.3.7" if is_botas else "API 5L Madde 10.2.4.8 & 9.10.6",
        "table_ref": "BOTAŞ Madde 3.3.7" if is_botas else f"{freq_tbl} / {piece_tbl}",
        "ndt_method_standard": "ISO 6507-1 / ASTM E384 / ASTM E92 (HV10 Taraması)",
        "ndt_acceptance_level": f"Azami Sertlik ≤ {hardness_max:.0f} HV10",
        "calculated_target_str": f"Maksimum {hardness_max:.0f} HV10 (Gövde, ITAB ve Kaynak Dikişi)",
        "calculated_targets": {"max_hv10": hardness_max},
        "is_mandatory": not is_psl1,
    })

    # 10. Residual Stress Test (BOTAŞ Mandatory for welded SAWH / LSAW only - Not applicable to ERW/HFW)
    if is_botas and (is_saw or "SAW" in process or "SAWH" in process or "LSAW" in process or "COW" in process):
        master_list.append({
            "test_key": "residual_stress",
            "category": "Tahribatlı Mekanik",
            "test_name": "Artık Stres Testi (Residual Stress Ring Test)",
            "standard_frequency": "Her çap ve et kalınlığı için ve ÇAP/ET KALINLIĞI DEĞİŞMESE DAHİ HER DÖKÜM (HEAT) İÇİN 1 halka",
            "standard_frequency_en": "Once per heat even if diameter and wall thickness do not change (150 mm ring)",
            "standard_acceptance_criteria": f"Artık stres S ≤ {residual_stress_max_mpa:.1f} MPa (0.10 × SMYS), Halka açılma Δ ≤ {delta_max:.2f} mm (BOTAŞ Madde 3.3.9)",
            "clause_ref": "BOTAŞ Şartnamesi Madde 3.3.9",
            "table_ref": "BOTAŞ 4-NGTL-0-GN-P-002-5120 R7",
            "ndt_method_standard": "BOTAŞ Şartnamesi Madde 3.3.9 (150 mm Halka Kesme Metodu)",
            "ndt_acceptance_level": f"S ≤ {residual_stress_max_mpa:.1f} MPa (0.10 x SMYS)",
            "calculated_target_str": f"Azami Artık Gerilme S ≤ {residual_stress_max_mpa:.1f} MPa | Halka Açılması Δ ≤ {delta_max:.2f} mm",
            "calculated_targets": {"max_stress_mpa": residual_stress_max_mpa, "max_delta_mm": delta_max},
            "is_mandatory": True,
        })

    # 11. Flattening (ERW/HFW)
    if "ERW" in process or "HFW" in process:
        master_list.append({
            "test_key": "flattening",
            "category": "Tahribatlı Mekanik",
            "test_name": "Düzleştirme Testi (Flattening)",
            "standard_frequency": "Her rulo (bobin) başı ve sonu (Şekil 6) ve/veya lot başına",
            "standard_frequency_en": "At crop ends of each coil / per test unit",
            "standard_acceptance_criteria": "Kaynak açılması: %67 D mesafeye kadar açılma yok; %33 D çatlak yok; Yüzeyler değene kadar füzyon kusuru yok",
            "clause_ref": "API 5L Madde 9.6 & 10.2.4.5",
            "table_ref": f"{freq_tbl} / {piece_tbl}",
            "ndt_method_standard": "ISO 8492 / ASTM A370",
            "ndt_acceptance_level": "API 5L Madde 9.6 Kademeli Sıkıştırma Kriterleri",
            "calculated_target_str": "Adım 1: Kaynak 90°'de %67 D (açılma yok) | Adım 2: %33 D (çatlak yok)",
            "calculated_targets": {"step1_distance_pct": 67.0, "step2_distance_pct": 33.0},
            "is_mandatory": True,
        })

    # 12. Hydrostatic Test
    master_list.append({
        "test_key": "hydrostatic",
        "category": "Basınç & Mukavemet",
        "test_name": "Fabrika Hidrostatik Basınç Testi",
        "standard_frequency": "Her boru (%100 tüm borular)",
        "standard_frequency_en": "Each pipe (100% of all pipes)",
        "standard_acceptance_criteria": hydro_crit,
        "clause_ref": "BOTAŞ Şartnamesi Madde 8.4.1 & 8.4.2" if is_botas else "API 5L Madde 9.4 & 10.2.6",
        "table_ref": "BOTAŞ Madde 8.4" if is_botas else f"{freq_tbl} / Çizelge 26",
        "ndt_method_standard": "API 5L Madde 10.2.6 / BOTAŞ Madde 8.4 (Kalibreli Basınç Test Cihazı)",
        "ndt_acceptance_level": f"Test Basıncı ≥ {hydro_p:.1f} bar, Sızdırma / Deformasyon Yok",
        "calculated_target_str": f"Min Test Basıncı: {hydro_p:.1f} bar | Min Tutma Süresi: {hydro_time} saniye",
        "calculated_targets": {"nominal_pressure_bar": hydro_p, "min_pressure_bar": min_acceptable_p, "min_holding_time_sec": hydro_time},
        "is_mandatory": True,
    })

    # 13. NDT of Weld Seam
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
            "ndt_method_standard": "ISO 10893-11 (Otomatik UT) + ISO 10893-6 / ISO 10893-7 (Radyografi / DDA)",
            "ndt_acceptance_level": "AUT Seviye U2 / U2H (N5 Çentik, Ø1.6-3.2 mm Delik) + RT Sınıf B (API 5L Çizelge E.5/E.6)",
            "calculated_target_str": "Tam boy %100 On-line AUT + Uçlarda (min 200 mm) ve şüpheli/tamir yerlerinde %100 RT (Sınıf B)",
            "calculated_targets": {"extent_pct": 100.0, "aut_level": "U2", "rt_class": "Class B"},
            "is_mandatory": True,
        })

    # 14. Pipe Body UT Lamination (BOTAŞ Mandatory min 40% scan)
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
            "ndt_method_standard": "ISO 10893-8 / ISO 10893-9 / ISO 12094",
            "ndt_acceptance_level": "ISO 12094 Sınıf B1 (Tekil Laminasyon Alanı ≤ 100 mm²)",
            "calculated_target_str": "Boru Gövde Yüzeyinin EN AZ %40'ı taranacaktır | Max Laminasyon Alanı ≤ 100 mm²",
            "calculated_targets": {"scan_coverage_pct": 40.0, "max_flaw_area_mm2": 100.0},
            "is_mandatory": True,
        })

    # 15. NDT of Pipe Ends
    end_band_width = 50 if is_botas else 100
    master_list.append({
        "test_key": "ndt_pipe_ends",
        "category": "Tahribatsız Muayene (NDT)",
        "test_name": "Boru Uçları Laminasyon Kontrolü (UT Laminar Testing)",
        "standard_frequency": f"Her boru (%100) uç kısımlarında en az {end_band_width} mm genişlikte bölge",
        "standard_frequency_en": f"100% of pipe ends of each pipe (min {end_band_width} mm band)",
        "standard_acceptance_criteria": f"Boru uçlarında en az {end_band_width} mm bant boyunca laminasyon kusuru bulunmayacaktır (Kusur boyutu > 6.0 mm veya > 100 mm² yasaktır)",
        "clause_ref": "BOTAŞ Şartnamesi Madde 8.8.4.4.2" if is_botas else "API 5L Ek E.8",
        "table_ref": "BOTAŞ Madde 8.8.4.4.2" if is_botas else f"{freq_tbl} / Ek E.8",
        "ndt_method_standard": "ISO 10893-8 / API 5L Ek E.8 (360° Ultrasonik Uç Taraması)",
        "ndt_acceptance_level": "Kusur Boyutu ≤ 6.0 mm, Kusur Alanı ≤ 100 mm²",
        "calculated_target_str": f"Boru uçlarında en az {end_band_width} mm çevre bandı boyunca %100 UT (Kusur ≤ 6.0 mm)",
        "calculated_targets": {"end_band_width_mm": end_band_width, "max_flaw_dim_mm": 6.0},
        "is_mandatory": True,
    })

    # 16. NDT of Seamless Body
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
            "ndt_method_standard": "ISO 10893-10 (Ultrasonik) / ISO 10893-1 / ISO 10893-3 (MFL)",
            "ndt_acceptance_level": "Seviye U2 / N5 (Referans Çentik %5 t)",
            "calculated_target_str": "%100 Tam boy ve 360° çevre hacimsel tahribatsız muayene (Seviye U2 / N5)",
            "calculated_targets": {"extent_pct": 100.0, "acceptance_level": "U2/N5"},
            "is_mandatory": not is_psl1,
        })

    # 17. Magnetic Particle Testing of Bevels & Repairs
    master_list.append({
        "test_key": "ndt_bevel_mt",
        "category": "Tahribatsız Muayene (NDT)",
        "test_name": "Kaynak Ağzı ve Tamir Yüzeyi Manyetik Parçacık (MT)",
        "standard_frequency": "Her boru (%100) alın kaynak ağızları ve tüm tamir bölgeleri",
        "standard_frequency_en": "100% of pipe bevels and all repair cavities",
        "standard_acceptance_criteria": "Kaynak ağızlarında ve tamir yüzeyinde çatlak, katmer veya lineer kusur bulunmayacaktır",
        "clause_ref": "API 5L Ek E.6 / BOTAŞ Madde 8.8.4",
        "table_ref": "ISO 10893-5 / ASTM E709",
        "ndt_method_standard": "ISO 10893-5 / ASTM E709 (Manyetik Parçacık - MT)",
        "ndt_acceptance_level": "Sıfır Çatlak / Sıfır Lineer Kusur",
        "calculated_target_str": "Boru uç kaynak ağızları ve tamir yüzeyleri %100 MT ile kontrol edilir; çatlak kesinlikle yasaktır",
        "calculated_targets": {"crack_allowed": False},
        "is_mandatory": True,
    })

    # 18. Weld & Body Repair Rules
    if is_welded:
        master_list.append({
            "test_key": "weld_repair_rules",
            "category": "Kaynak ve Onarım Şartları",
            "test_name": "Kaynak ve Gövde Tamir Kuralları (Repair Conditions)",
            "standard_frequency": "Oluşan her tamir işleminde istisnasız uygulanır",
            "standard_frequency_en": "Applied to each repair operation",
            "standard_acceptance_criteria": "Gövdeye kaynak tamiri YASAK; Tek tamir boyu ≤ 150 mm; Uçta 300 mm tamir yasağı; Re-repair YASAK; >X52 ve t>10mm için ≥ 100°C ön ısıtma; Tamir sonrası %100 RT+MT ve %100 RE-HYDRO (BOTAŞ Madde 9.1 & Ek C)",
            "clause_ref": "BOTAŞ Şartnamesi Madde 9.1 & Ek C / API 5L Ek C",
            "table_ref": "API 5L Annex C / BOTAŞ Madde 9",
            "ndt_method_standard": "Onaylı Tamir WPS/PQR + Tamir Sonrası %100 RT & MT + Re-Hydro",
            "ndt_acceptance_level": "Max Tamir Boyu: 150 mm, Uç Yasağı: 300 mm, İkinci Tamir Yasak",
            "calculated_target_str": "Gövde kaynağı YASAK; Tek tamir boyu ≤ 150 mm; Uçta 300 mm tamir yasağı; Re-repair YASAK; Tamir sonrası %100 RT+MT ve %100 RE-HYDRO",
            "calculated_targets": {"max_single_repair_length_mm": 150, "end_repair_ban_distance_mm": 300, "min_preheat_c": 100, "re_repair_allowed": False, "post_repair_rehydro_mandatory": True},
            "is_mandatory": True,
        })

    # 19. Weld Geometry & Peaking (if welded)
    if is_welded and not ("ERW" in process or "HFW" in process):
        master_list.append({
            "test_key": "weld_geometry_offset_height",
            "category": "Boyutsal & Geometri",
            "test_name": "Kaynak Dikiş Yüksekliği (Weld Reinforcement Height - Inside & Outside)",
            "standard_frequency": "Her kaynaklı boruda %100 dikiş boyunca mastar ve optik ölçüm ile",
            "standard_frequency_en": "100% of pipes along full weld seam",
            "standard_acceptance_criteria": f"İç/Dış Kaynak Yüksekliği: 0.50 mm - {weld_h_max:.2f} mm | Eksenel Kaçıklık ≤ {misalignment_max:.2f} mm (BOTAŞ Çizelge 4)",
            "clause_ref": "BOTAŞ Madde 8.8.4 & Çizelge 4 / API 5L Madde 9.13 & Çizelge 16",
            "table_ref": "BOTAŞ Çizelge 4 / API 5L Çizelge 16",
            "ndt_method_standard": "Kaynak Dikiş Yüksekliği Mastarları / Lazer Profilometre",
            "ndt_acceptance_level": f"İç/Dış Yükseklik ≤ {weld_h_max:.2f} mm, Kaçıklık ≤ {misalignment_max:.2f} mm",
            "calculated_target_str": f"İç/Dış Kaynak Yüksekliği ≤ {weld_h_max:.2f} mm | Eksenel Kaçıklık ≤ {misalignment_max:.2f} mm",
            "calculated_targets": {"max_weld_height_mm": weld_h_max, "min_weld_height_mm": 0.50, "max_misalignment_mm": misalignment_max},
            "is_mandatory": True,
        })
        master_list.append({
            "test_key": "weld_radial_offset",
            "category": "Boyutsal & Geometri",
            "test_name": "Sac Kenarları Radyal Kaçıklık / Basamaklanma (Radial Offset)",
            "standard_frequency": "Her kaynaklı boruda %100 dikiş boyunca",
            "standard_frequency_en": "100% of welded pipes along weld seam",
            "standard_acceptance_criteria": f"Radyal Kaçıklık ≤ {radial_offset:.2f} mm (BOTAŞ: {radial_offset:.2f} mm / API 5L Çizelge 14)",
            "clause_ref": "BOTAŞ Şartnamesi Madde 8.8.4" if is_botas else "API 5L Madde 9.13.1 & Çizelge 14",
            "table_ref": "BOTAŞ Madde 8.8.4 / API 5L Çizelge 14",
            "ndt_method_standard": "Basamak / Kaçıklık Derinlik Mastarı",
            "ndt_acceptance_level": f"Radyal Kaçıklık ≤ {radial_offset:.2f} mm",
            "calculated_target_str": f"Radyal Kaçıklık ≤ {radial_offset:.2f} mm",
            "calculated_targets": {"max_radial_offset_mm": radial_offset},
            "is_mandatory": True,
        })
        master_list.append({
            "test_key": "dimensional_peaking_offset",
            "category": "Boyutsal & Geometri",
            "test_name": "Boru Ucu Tepeleşme / Çıkıntı (Pipe End Peaking)",
            "standard_frequency": "Her kaynaklı borunun her iki ucunda (%100)",
            "standard_frequency_en": "100% of pipe ends for welded pipes",
            "standard_acceptance_criteria": f"Boru Ucu Tepeleşme (Peaking) ≤ {peaking_max:.2f} mm (BOTAŞ Çizelge 4 / API 5L Çizelge 16)",
            "clause_ref": "BOTAŞ Şartnamesi Madde 5.1 & Çizelge 4" if is_botas else "API 5L Madde 9.13.2 & Çizelge 16",
            "table_ref": "BOTAŞ Çizelge 4 / API 5L Çizelge 16",
            "ndt_method_standard": "200 mm Kavisli Tepeleşme Mastarı (Peaking Template)",
            "ndt_acceptance_level": f"Tepeleşme ≤ {peaking_max:.2f} mm",
            "calculated_target_str": f"Tepeleşme (Peaking) ≤ {peaking_max:.2f} mm",
            "calculated_targets": {"max_peaking_mm": peaking_max},
            "is_mandatory": True,
        })

    # 20. Diameter - Pipe Ends
    master_list.append({
        "test_key": "dimensional_diameter_ends",
        "category": "Boyutsal & Geometri",
        "test_name": "Boru Ucu Dış Çap Toleransı (Diameter Tolerance - Pipe Ends)",
        "standard_frequency": "Her borunun her iki ucunda (%100)" if is_botas else "Vardiyada en az 4 saatte bir ve soğuk genişletilen her boruda",
        "standard_frequency_en": "100% of pipe ends",
        "standard_acceptance_criteria": f"Uç Çapı Kabul Aralığı: {d_end_min:.2f} mm - {d_end_max:.2f} mm ({'+' if d_end_max>=d_mm else ''}{d_end_max-d_mm:.2f} / {d_end_min-d_mm:.2f} mm)",
        "clause_ref": "BOTAŞ Şartnamesi Madde 5.1 & 8.1.2.4" if is_botas else "API 5L Madde 9.11.1 & Çizelge 10",
        "table_ref": "BOTAŞ Madde 5.1" if is_botas else f"{freq_tbl} / Çizelge 10",
        "ndt_method_standard": "Pi-Mezura (Pi-Tape) / Kumpas / Lazer Çapölçer",
        "ndt_acceptance_level": f"Uç Çapı: {d_end_min:.2f} mm - {d_end_max:.2f} mm",
        "calculated_target_str": f"Uç Çapı: {d_end_min:.2f} mm - {d_end_max:.2f} mm (Nominal {d_mm:.1f} mm)",
        "calculated_targets": {"d_end_min_mm": d_end_min, "d_end_max_mm": d_end_max, "nominal_od_mm": d_mm},
        "is_mandatory": True,
    })

    # 21. Diameter - Pipe Body
    master_list.append({
        "test_key": "dimensional_diameter_body",
        "category": "Boyutsal & Geometri",
        "test_name": "Boru Gövdesi Dış Çap Toleransı (Diameter Tolerance - Pipe Body)",
        "standard_frequency": "D ≥ 20\" borularda istisnasız %100 tüm borular; D < 20\" borularda vardiya başı / periyodik" if is_botas else "Vardiya başına en az her 4 saatte bir ve her parti boruda",
        "standard_frequency_en": "100% of pipes for D >= 20\"" if is_botas else "At least once per 4 hours per operating shift",
        "standard_acceptance_criteria": f"Gövde Çapı Kabul Aralığı: {d_body_min:.2f} mm - {d_body_max:.2f} mm ({'+' if d_body_max>=d_mm else ''}{d_body_max-d_mm:.2f} / {d_body_min-d_mm:.2f} mm)",
        "clause_ref": "BOTAŞ Şartnamesi Madde 5.1 & 8.1.2.4" if is_botas else "API 5L Madde 9.11.1 & Çizelge 10",
        "table_ref": "BOTAŞ Madde 5.1" if is_botas else f"{freq_tbl} / Çizelge 10",
        "ndt_method_standard": "Pi-Mezura (Pi-Tape) / Optik Çap Ölçer",
        "ndt_acceptance_level": f"Gövde Çapı: {d_body_min:.2f} mm - {d_body_max:.2f} mm (±{dia_body_tol:.1f} mm)",
        "calculated_target_str": f"Gövde Çapı: {d_body_min:.2f} mm - {d_body_max:.2f} mm (Nominal {d_mm:.1f} mm)",
        "calculated_targets": {"d_body_min_mm": d_body_min, "d_body_max_mm": d_body_max, "nominal_od_mm": d_mm},
        "is_mandatory": True,
    })

    # 22. Circumference - Pipe Ends
    master_list.append({
        "test_key": "dimensional_circumference_ends",
        "category": "Boyutsal & Geometri",
        "test_name": "Boru Çevre Toleransı - Boru Ucu (Circumference Tolerance - Pipe Ends)",
        "standard_frequency": "Her borunun her iki ucunda (%100)",
        "standard_frequency_en": "100% of pipe ends",
        "standard_acceptance_criteria": f"Boru Ucu Çevre Kabul Aralığı: {circ_end_min:.1f} mm - {circ_end_max:.1f} mm (π·D_end)",
        "clause_ref": "BOTAŞ Şartnamesi Madde 5.1 / API 5L Madde 9.11.1",
        "table_ref": "BOTAŞ Madde 5.1 / API 5L Çizelge 10",
        "ndt_method_standard": "Kalibreli Pi-Mezura (Pi-Tape)",
        "ndt_acceptance_level": f"Uç Çevresi: {circ_end_min:.1f} mm - {circ_end_max:.1f} mm",
        "calculated_target_str": f"Uç Çevresi: {circ_end_min:.1f} mm - {circ_end_max:.1f} mm",
        "calculated_targets": {"circ_end_min_mm": circ_end_min, "circ_end_max_mm": circ_end_max, "nominal_circ_mm": round(math.pi * d_mm, 2)},
        "is_mandatory": True,
    })

    # 23. Circumference - Pipe Body
    master_list.append({
        "test_key": "dimensional_circumference_body",
        "category": "Boyutsal & Geometri",
        "test_name": "Boru Çevre Toleransı - Gövde (Circumference Tolerance - Pipe Body)",
        "standard_frequency": "D ≥ 20\" borularda %100 tüm borular; D < 20\" borularda vardiya başı / periyodik",
        "standard_frequency_en": "100% of pipes for D >= 20\"",
        "standard_acceptance_criteria": f"Boru Gövdesi Çevre Kabul Aralığı: {circ_body_min:.1f} mm - {circ_body_max:.1f} mm (π·D_body)",
        "clause_ref": "BOTAŞ Şartnamesi Madde 5.1 / API 5L Madde 9.11.1",
        "table_ref": "BOTAŞ Madde 5.1 / API 5L Çizelge 10",
        "ndt_method_standard": "Kalibreli Pi-Mezura (Pi-Tape)",
        "ndt_acceptance_level": f"Gövde Çevresi: {circ_body_min:.1f} mm - {circ_body_max:.1f} mm",
        "calculated_target_str": f"Gövde Çevresi: {circ_body_min:.1f} mm - {circ_body_max:.1f} mm",
        "calculated_targets": {"circ_body_min_mm": circ_body_min, "circ_body_max_mm": circ_body_max, "nominal_circ_mm": round(math.pi * d_mm, 2)},
        "is_mandatory": True,
    })

    # 24. Ovality - Pipe Ends
    master_list.append({
        "test_key": "dimensional_ovality_ends",
        "category": "Boyutsal & Geometri",
        "test_name": "Ovalite - Boru Ucu (Out-of-Roundness - Pipe Ends)",
        "standard_frequency": "Her borunun her iki ucunda (%100)" if is_botas else "Vardiyada en az her 4 saatte bir ve soğuk genişletilen her boruda",
        "standard_frequency_en": "100% of pipe ends",
        "standard_acceptance_criteria": f"Boru Ucu Azami Ovalite: ≤ {ovality_end:.2f} mm (D_max - D_min ≤ {ovality_end:.2f} mm)",
        "clause_ref": "BOTAŞ Şartnamesi Madde 5.1" if is_botas else "API 5L Madde 9.11.1 & Çizelge 10",
        "table_ref": "BOTAŞ Madde 5.1" if is_botas else f"{freq_tbl} / Çizelge 10",
        "ndt_method_standard": "İç/Dış Çap Kumpası / Dairesellik Mastarı / Lazer Profiler",
        "ndt_acceptance_level": f"Uç Ovalitesi ≤ {ovality_end:.2f} mm",
        "calculated_target_str": f"Uç Ovalitesi ≤ {ovality_end:.2f} mm",
        "calculated_targets": {"ovality_end_max_mm": ovality_end},
        "is_mandatory": True,
    })

    # 25. Ovality - Pipe Body
    master_list.append({
        "test_key": "dimensional_ovality_body",
        "category": "Boyutsal & Geometri",
        "test_name": "Ovalite - Boru Gövdesi (Out-of-Roundness - Pipe Body)",
        "standard_frequency": "D ≥ 20\" borularda %100 tüm borular; D < 20\" borularda vardiya başı / periyodik",
        "standard_frequency_en": "100% of pipes for D >= 20\"",
        "standard_acceptance_criteria": f"Boru Gövdesi Azami Ovalite: ≤ {ovality_body:.2f} mm (D_max - D_min ≤ {ovality_body:.2f} mm)" if isinstance(ovality_body, (int, float)) else f"Gövde Ovalitesi: {ovality_body}",
        "clause_ref": "BOTAŞ Şartnamesi Madde 5.1" if is_botas else "API 5L Madde 9.11.1 & Çizelge 10",
        "table_ref": "BOTAŞ Madde 5.1" if is_botas else f"{freq_tbl} / Çizelge 10",
        "ndt_method_standard": "Dairesellik Mastarı / Çap Kumpası",
        "ndt_acceptance_level": f"Gövde Ovalitesi ≤ {ovality_body:.2f} mm" if isinstance(ovality_body, (int, float)) else str(ovality_body),
        "calculated_target_str": f"Gövde Ovalitesi ≤ {ovality_body:.2f} mm" if isinstance(ovality_body, (int, float)) else str(ovality_body),
        "calculated_targets": {"ovality_body_max_mm": ovality_body if isinstance(ovality_body, (int, float)) else 15.0},
        "is_mandatory": True,
    })

    # 26. Wall Thickness
    master_list.append({
        "test_key": "dimensional_wall_thickness",
        "category": "Boyutsal & Geometri",
        "test_name": "Et Kalınlığı Ölçümü ve Toleransı (Wall Thickness Verification)",
        "standard_frequency": "Her boru (%100) uçlardan ve gövdeden ultrasonik/mikrometre ile",
        "standard_frequency_en": "Each pipe (100%)",
        "standard_acceptance_criteria": f"Nominal: {t_mm:.2f} mm | Kabul Edilen Aralık: {t_min:.2f} mm - {t_max:.2f} mm (-%{t_neg_pct:.1f} / +%{t_pos_pct:.1f})",
        "clause_ref": "BOTAŞ Şartnamesi Madde 5.2 (Tablo 4)" if is_botas else "API 5L Madde 9.11.2 & 10.2.8.2",
        "table_ref": "BOTAŞ Tablo 4" if is_botas else f"{freq_tbl} / Çizelge 11",
        "ndt_method_standard": "Ultrasonik Et Kalınlığı Ölçer / Mikrometre",
        "ndt_acceptance_level": f"t_min = {t_min:.2f} mm, t_max = {t_max:.2f} mm",
        "calculated_target_str": f"Nominal: {t_mm:.2f} mm | Kabul Aralığı: {t_min:.2f} mm - {t_max:.2f} mm (-%{t_neg_pct:.1f} / +%{t_pos_pct:.1f})",
        "calculated_targets": {"nominal_mm": t_mm, "min_mm": t_min, "max_mm": t_max, "neg_tol_pct": t_neg_pct, "pos_tol_pct": t_pos_pct},
        "is_mandatory": True,
    })

    # 27. Unit Weight Verification
    master_list.append({
        "test_key": "dimensional_weight",
        "category": "Boyutsal & Geometri",
        "test_name": "Boru Birim Ağırlığı ve Toleransı (Weight per Meter & Tolerance)",
        "standard_frequency": "Her boruda (%100 münferit kantar tartımı)",
        "standard_frequency_en": "Each pipe (100% weighing or per lot)",
        "standard_acceptance_criteria": f"Teorik Ağırlık: {weight_nom:.2f} kg/m | Münferit Boru Sınırı: {weight_min:.2f} kg/m - {weight_max:.2f} kg/m (-%3.5 / +%10.0)",
        "clause_ref": "API 5L Madde 9.11.2 & 10.2.8.7 / BOTAŞ",
        "table_ref": f"{freq_tbl} / Madde 9.11.2",
        "ndt_method_standard": "Kalibreli Yük Hücresi / Endüstriyel Kantar",
        "ndt_acceptance_level": f"W = {weight_nom:.2f} kg/m (-%3.5 / +%10.0)",
        "calculated_target_str": f"Teorik: {weight_nom:.2f} kg/m | Münferit Boru: {weight_min:.2f} - {weight_max:.2f} kg/m (-%3.5 / +%10.0)",
        "calculated_targets": {"nominal_kg_m": weight_nom, "min_kg_m": weight_min, "max_kg_m": weight_max, "neg_tol_pct": 3.5, "pos_tol_pct": 10.0},
        "is_mandatory": True,
    })

    # 28. Straightness
    master_list.append({
        "test_key": "dimensional_straightness",
        "category": "Boyutsal & Geometri",
        "test_name": "Boru Toplam Doğrusallığı (Straightness Deviation)",
        "standard_frequency": "Her boru (%100)",
        "standard_frequency_en": "Each pipe (100%)",
        "standard_acceptance_criteria": f"Toplam boy boyunca doğrusallıktan sapma ≤ %{straightness_pct:.2f} L (Uç 1.5 m bölgede sapma ≤ 3.2 mm)",
        "clause_ref": "BOTAŞ Şartnamesi Madde 5.4" if is_botas else "API 5L Madde 9.11.3.4 & Çizelge 12",
        "table_ref": "BOTAŞ Madde 5.4" if is_botas else f"{freq_tbl} / Çizelge 12",
        "ndt_method_standard": "Gergi Teli (Piano Wire) / Lazer Doğrusallık Mastarı",
        "ndt_acceptance_level": f"Doğrusallık ≤ %{straightness_pct:.2f} L",
        "calculated_target_str": f"Doğrusallık ≤ %{straightness_pct:.2f} L",
        "calculated_targets": {"straightness_max_pct": straightness_pct},
        "is_mandatory": True,
    })

    # 29. Bevel Angle & Root Face
    master_list.append({
        "test_key": "dimensional_bevel_ends",
        "category": "Boyutsal & Geometri",
        "test_name": "Alın Kaynak Ağzı Açısı ve Kök Yüzeyi (Bevel Angle & Root Face)",
        "standard_frequency": "Her borunun her iki ucunda (%100)",
        "standard_frequency_en": "Each pipe ends (100%)",
        "standard_acceptance_criteria": "Kaynak Ağzı Açısı: 30° (+5° / -0°) (veya 35°), Kök Yüzeyi (Root Face): 1.6 ± 0.8 mm",
        "clause_ref": "BOTAŞ Şartnamesi Madde 7.2" if is_botas else "API 5L Madde 9.12.5.4",
        "table_ref": "BOTAŞ Madde 7.2 / API 5L Madde 9.12",
        "ndt_method_standard": "Kaynak Ağzı ve Kök Yüzeyi Mastarı (Bridge Cam Gauge)",
        "ndt_acceptance_level": "Açı 30° (+5°/-0°), Kök 1.6 ± 0.8 mm",
        "calculated_target_str": "Ağız Açısı: 30° (+5°/-0°), Kök Yüzeyi: 1.6 ± 0.8 mm",
        "calculated_targets": {"bevel_angle_deg": 30.0, "root_face_mm": 1.6, "root_face_tol_mm": 0.8},
        "is_mandatory": True,
    })

    # 30. Squareness
    master_list.append({
        "test_key": "dimensional_squareness_ends",
        "category": "Boyutsal & Geometri",
        "test_name": "Boru Ucu Diklikten Sapma (Pipe End Squareness)",
        "standard_frequency": "Her borunun her iki ucunda (%100)",
        "standard_frequency_en": "Each pipe ends (100%)",
        "standard_acceptance_criteria": f"Boru ucu diklikten sapma ≤ {squareness_max:.2f} mm",
        "clause_ref": "BOTAŞ Şartnamesi Madde 5.5" if is_botas else "API 5L Madde 9.12.5.3",
        "table_ref": "BOTAŞ Madde 5.5 / API 5L Madde 9.12",
        "ndt_method_standard": "Hassas Gönye ve Sentil / Lazer Diklik Mastarı",
        "ndt_acceptance_level": f"Diklikten Sapma ≤ {squareness_max:.2f} mm",
        "calculated_target_str": f"Diklikten Sapma ≤ {squareness_max:.2f} mm",
        "calculated_targets": {"max_squareness_mm": squareness_max},
        "is_mandatory": True,
    })

    # 24. Visual Surface Inspection
    master_list.append({
        "test_key": "visual_surface",
        "category": "Boyutsal & Görsel",
        "test_name": "Görsel Yüzey ve Kusur Muayenesi (Visual Inspection)",
        "standard_frequency": "D ≥ 20\" borularda istisnasız %100 boru kaynağı (iç/dış) ve %100 gövde (iç/dış) görsel muayenesi" if is_botas else "Her boru (%100 iç ve dış yüzey)",
        "standard_frequency_en": "100% internal and external surface of each pipe",
        "standard_acceptance_criteria": "EN 10163-2 Sınıf B Altsınıf 3 (Keskin köşeli hata kabul edilmez, gövde/kaynak çatlak yok, derinlik ≤ %12.5 t)",
        "clause_ref": "BOTAŞ Şartnamesi Madde 3.1.5, 8.1.2.1, 8.1.2.2 & 9.1" if is_botas else "API 5L Madde 9.10.1 & 10.2.7",
        "table_ref": "BOTAŞ Madde 8.1.2" if is_botas else freq_tbl,
        "ndt_method_standard": "EN 10163-2 Sınıf B / API 5L Madde 10.2.7 (Doğrudan Görsel Muayene VT)",
        "ndt_acceptance_level": "Sıfır Çatlak / Katmer / Kabuk; Kusur Derinliği ≤ %12.5 t",
        "calculated_target_str": "D ≥ 20\" borularda %100 iç/dış görsel kontrol; çatlak, katmer, kabuk kesinlikle yasaktır (Kusur ≤ %12.5 t)",
        "calculated_targets": {"extent_pct": 100.0, "max_imperfection_pct_t": 12.5},
        "is_mandatory": True,
    })

    # 25. Residual Magnetism
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

    # 26. ERW Specific Process Checks
    if "ERW" in process or "HFW" in process:
        master_list.append({
            "test_key": "erw_metallographic_seam",
            "category": "Metalografi & Yapı",
            "test_name": "Metalografik İnceleme & Mikro Yapı (ERW Seam Metallography)",
            "standard_frequency": "Üretim başlangıcında, her döküm değişiminde ve ayar değişikliğinde",
            "standard_frequency_en": "Start of production, each heat change and machine setup",
            "standard_acceptance_criteria": "Martenzit yapısı kesinlikle olmayacak, tam normalizasyon sağlanacak; EN 10163-2 Sınıf B alt sınıf 3 yüzey kalitesi",
            "clause_ref": "API 5L Madde 10.2.5.3 & EN 10163-2 Sınıf B",
            "table_ref": "API 5L Madde 10.2.5",
            "ndt_method_standard": "Optik Mikroskop / Metalografi Numunesi Dağlama",
            "ndt_acceptance_level": "Sıfır Martenzit, Homojen Ferrit-Perlit Yapı",
            "calculated_target_str": "Martenzit yapısı yasaktır; tam normalizasyon tavlaması uygulanacaktır",
            "calculated_targets": {"martensite_allowed": False},
            "is_mandatory": True,
        })
        master_list.append({
            "test_key": "erw_flash_trim_weld",
            "category": "Boyutsal & Geometri",
            "test_name": "İç ve Dış Çapak Alma & Geometri (Flash Trim & Groove)",
            "standard_frequency": "Her boruda (%100 tam boy)",
            "standard_frequency_en": "100% of pipes along full weld seam",
            "standard_acceptance_criteria": "İç çapak yüksekliği ≤ 1.1 mm; Oyuk derinliği ≤ 0.04 mm; Ofset ≤ 1.1 mm; Çapak sonrası kalan et kalınlığı ≥ t_min",
            "clause_ref": "API 5L 46th/47th Ver. Madde 9.13.2",
            "table_ref": "API 5L Madde 9.13.2",
            "ndt_method_standard": "İç Çapak Derinlik Mastarı / Ultrasonik Cidar Ölçer",
            "ndt_acceptance_level": "İç Çapak ≤ 1.1 mm, Oyuk ≤ 0.04 mm",
            "calculated_target_str": "İç çapak max 1.1 mm | Oyuk derinliği max 0.04 mm | Kalan et kalınlığı ≥ t_min",
            "calculated_targets": {"max_flash_trim_mm": 1.1, "max_groove_depth_mm": 0.04},
            "is_mandatory": True,
        })

    # 27. 3LPE / HDPE External Coating Disciplinary Requirements (DIN 30670 / BOTAŞ 5410 R1 / EN 21809-1)
    master_list.append({
        "test_key": "coating_surface_prep_blasting",
        "category": "Dış Kaplama (3LPE / HDPE)",
        "test_name": "Yüzey Hazırlığı, Kumlama ve Temizlik (Surface Preparation & Blasting)",
        "standard_frequency": "Her boru (%100 Sa 2.5 görsel) | Pürüzlülük/Toz/Tuz: 4 saatte 1",
        "standard_frequency_en": "Each pipe (100% Sa 2.5) | Rz/Dust/Salt every 4 hours",
        "standard_acceptance_criteria": "Temizlik: Min Sa 2½ (ISO 8501-1); Pürüzlülük: Rz 60-100 µm; Çiğ noktası +3 °C üzerinde; Toz Sınıfı ≤ 2; Tuz ≤ 20 mg/m² (2 µg/cm²)",
        "clause_ref": "BOTAŞ 4-NGTL-0-GN-P-002-5410 R1 Madde 5.5 / DIN 30670 / EN 21809-1",
        "table_ref": "BOTAŞ 5410 R1 / DIN 30670",
        "ndt_method_standard": "ISO 8501-1 (Görsel Karşılaştırma) + Yüzey Profilometresi (Rz) + Bresle Tuz Kiti",
        "ndt_acceptance_level": "Sa 2.5, Rz 60-100 µm, Toz ≤ Sınıf 2, Tuz ≤ 20 mg/m²",
        "calculated_target_str": "Min Sa 2.5 | Rz: 60 - 100 µm | Sıcaklık ≥ Çiğ Noktası + 3 °C | Tuz ≤ 20 mg/m²",
        "calculated_targets": {"min_sa_level": 2.5, "min_rz_um": 60, "max_rz_um": 100, "max_salt_mg_m2": 20.0},
        "is_mandatory": True,
    })
    master_list.append({
        "test_key": "coating_thickness_3lpe",
        "category": "Dış Kaplama (3LPE / HDPE)",
        "test_name": "3LPE / HDPE Kaplama Kalınlığı (Coating Thickness - FBE/Adhesive/PE)",
        "standard_frequency": "Her boruda (%100 boru boyunca en az 12 nokta + kaynak kepi üzeri 4 nokta)",
        "standard_frequency_en": "100% of pipes (at least 12 readings on body + 4 on weld seam)",
        "standard_acceptance_criteria": "FBE Astar ≥ 120 µm; Yapıştırıcı ≥ 120 µm; Toplam 3LPE/HDPE ≥ 3.0 mm (3000 µm) (Kaynak kepi üzeri min kalınlıktan max %10 düşük olabilir)",
        "clause_ref": "BOTAŞ 5410 R1 Madde 5.8 / DIN 30670 Tip S-v (Yükseltilmiş Kalınlık)",
        "table_ref": "BOTAŞ 5410 R1 Tablo 5 / DIN 30670",
        "ndt_method_standard": "Manyetik/Elektromanyetik Kaplama Kalınlık Ölçer (ISO 2808)",
        "ndt_acceptance_level": "Toplam PE ≥ 3.0 mm (3000 µm), FBE ≥ 120 µm, Yapıştırıcı ≥ 120 µm",
        "calculated_target_str": "Toplam 3LPE ≥ 3.0 mm (3000 µm) | FBE ≥ 120 µm | Yapıştırıcı ≥ 120 µm",
        "calculated_targets": {"min_total_pe_mm": 3.0, "min_fbe_um": 120, "min_adhesive_um": 120},
        "is_mandatory": True,
    })
    master_list.append({
        "test_key": "coating_holiday_test",
        "category": "Dış Kaplama (3LPE / HDPE)",
        "test_name": "Elektrik Porozite / Süreksizlik Testi (Holiday Detection 25 kV)",
        "standard_frequency": "Her boru (%100 tam yüzey taraması)",
        "standard_frequency_en": "100% of pipe coated surface",
        "standard_acceptance_criteria": "Test Gerilimi: 25.000 Volt (25 kV); Sıfır Kıvılcım / Hatasız (%100 kusursuz yalıtım)",
        "clause_ref": "BOTAŞ 5410 R1 Madde 7.4.3 / DIN 30670 / EN 21809-1",
        "table_ref": "BOTAŞ 5410 R1 Madde 7.4.3",
        "ndt_method_standard": "Yüksek Gerilimli Holiday Dedektörü (25 kV Yaylı Elektrot)",
        "ndt_acceptance_level": "25 kV Gerilimde Sıfır Delik / Sıfır Kıvılcım",
        "calculated_target_str": "25 kV Yüksek Gerilim ile %100 Yüzey Taraması; kıvılcım/gözenek kesinlikle yasaktır",
        "calculated_targets": {"voltage_kv": 25.0, "defects_allowed": 0},
        "is_mandatory": True,
    })
    master_list.append({
        "test_key": "coating_peel_adhesion",
        "category": "Dış Kaplama (3LPE / HDPE)",
        "test_name": "Soyulma Mukavemeti / Yapışma Testi (Peel Adhesion Test)",
        "standard_frequency": "İlk boru ve her PE partisinde / her vardiya (3 adet numune)",
        "standard_frequency_en": "First pipe and each PE batch / shift (3 specimens)",
        "standard_acceptance_criteria": "(23 ± 2) °C'de ≥ 150 N/cm (veya ≥ 18 N/mm); (50 ± 2) °C'de ≥ 15 N/cm; Test hızı: 10 mm/dakika",
        "clause_ref": "BOTAŞ 5410 R1 Madde 7.4.4 & Ek D / DIN 30670 / EN 21809-1",
        "table_ref": "BOTAŞ 5410 R1 Ek D",
        "ndt_method_standard": "Soyulma Test Cihazı (DIN 30670 / EN ISO 21809-1 Ek D)",
        "ndt_acceptance_level": "23 °C ≥ 150 N/cm, 50 °C ≥ 15 N/cm",
        "calculated_target_str": "23 °C'de Min 150 N/cm | 50 °C'de Min 15 N/cm",
        "calculated_targets": {"min_peel_23c_n_cm": 150.0, "min_peel_50c_n_cm": 15.0},
        "is_mandatory": True,
    })
    master_list.append({
        "test_key": "coating_impact_resistance",
        "category": "Dış Kaplama (3LPE / HDPE)",
        "test_name": "Kaplama Darbe Direnci Testi (Impact Resistance Test)",
        "standard_frequency": "Her vardiya ve et kalınlığı değişiminde (20 darbe)",
        "standard_frequency_en": "Each shift and wall thickness change (20 impacts)",
        "standard_acceptance_criteria": "Darbe Direnci ≥ 5 J/mm (23 ± 2 °C); 2.5 kg ağırlık 1 m'den düşürülecek; darbe sonrası 25 kV holiday testinde delinme/kıvılcım olmayacak",
        "clause_ref": "BOTAŞ 5410 R1 Madde 7.4.5 / DIN 30670 / EN 21809-1",
        "table_ref": "BOTAŞ 5410 R1 Madde 7.4.5",
        "ndt_method_standard": "Düşen Ağırlıklı Darbe Cihazı (25 mm Yarımküre Uç) + 25 kV Holiday",
        "ndt_acceptance_level": "Darbe Direnci ≥ 5 J/mm, 25 kV Holiday Delinme Yok",
        "calculated_target_str": "Darbe Direnci ≥ 5.0 J/mm (2.5 kg ağırlık / 1 m düşüş) | 25 kV Holiday Hatasız",
        "calculated_targets": {"min_impact_j_mm": 5.0},
        "is_mandatory": True,
    })
    master_list.append({
        "test_key": "coating_indentation",
        "category": "Dış Kaplama (3LPE / HDPE)",
        "test_name": "Delici Uca Batma / Girinti Direnci (Indentation Test)",
        "standard_frequency": "Her PE partisinde (1 / Batch)",
        "standard_frequency_en": "1 per PE batch",
        "standard_acceptance_criteria": "Batma Derinliği: (23 ± 2) °C'de Azami 0.20 mm; (50 ± 2) °C'de Azami 0.30 mm",
        "clause_ref": "BOTAŞ 5410 R1 Ek I / DIN 30670 / EN 21809-1",
        "table_ref": "BOTAŞ 5410 R1 Ek I",
        "ndt_method_standard": "Penetrasyon / İndentasyon Test Düzeneği (ISO 21809-1 Ek E)",
        "ndt_acceptance_level": "23 °C ≤ 0.20 mm, 50 °C ≤ 0.30 mm",
        "calculated_target_str": "Batma Derinliği: 23 °C'de ≤ 0.20 mm | 50 °C'de ≤ 0.30 mm",
        "calculated_targets": {"max_indentation_23c_mm": 0.20, "max_indentation_50c_mm": 0.30},
        "is_mandatory": True,
    })
    master_list.append({
        "test_key": "coating_cathodic_disbondment",
        "category": "Dış Kaplama (3LPE / HDPE)",
        "test_name": "Katodik Soyulma Testi (Cathodic Disbondment - CD Test)",
        "standard_frequency": "Sipariş başına / her ebatta 1 set",
        "standard_frequency_en": "1 set per order / pipe size",
        "standard_acceptance_criteria": "20 °C (28 Gün - 1.5 V): Max 7.0 mm soyulma yarıçapı | 65 °C (24 Saat - 3.5 V): Max 7.0 mm soyulma yarıçapı",
        "clause_ref": "BOTAŞ 5410 R1 Madde 7.4.6 / ISO 21809-1 Ek H",
        "table_ref": "ISO 21809-1 Ek H",
        "ndt_method_standard": "Katodik Koruma Test Hücresi (Potansiyostat / Platin Elektrot)",
        "ndt_acceptance_level": "CD Yarıçapı ≤ 7.0 mm",
        "calculated_target_str": "20 °C 28 Gün CD ≤ 7.0 mm | 65 °C 24 Saat CD ≤ 7.0 mm",
        "calculated_targets": {"max_cd_radius_mm": 7.0},
        "is_mandatory": True,
    })
    master_list.append({
        "test_key": "coating_cutback_bevel",
        "category": "Dış Kaplama (3LPE / HDPE)",
        "test_name": "Kaplamasız Uç Bölgesi ve Pah Açısı (Cutback Distance & Bevel)",
        "standard_frequency": "Her borunun her iki ucunda (%100)",
        "standard_frequency_en": "100% of pipe ends",
        "standard_acceptance_criteria": "Cutback mesafesi: 80 - 100 mm; Kaplamasız boyasız bölüm: 45 - 55 mm; PE Pah Açısı: 20° - 30° (veya 30° - 50°); Korozyona karşı geçici şeffaf vernik koruması ve koruyucu uç tapası",
        "clause_ref": "BOTAŞ 5410 R1 Madde 10 & 5140 R1 / DIN 30670",
        "table_ref": "BOTAŞ 5410 R1 Madde 10",
        "ndt_method_standard": "Kumpas / Mastar / Görsel Muayene",
        "ndt_acceptance_level": "Cutback 80-100 mm, Boyasız 45-55 mm, Açı 20°-30°",
        "calculated_target_str": "Cutback: 80 - 100 mm | Boyasız Bölüm: 45 - 55 mm | PE Açısı: 20° - 30° | Geçici Vernik & Tapa",
        "calculated_targets": {"min_cutback_mm": 80, "max_cutback_mm": 100, "min_bare_mm": 45, "max_bare_mm": 55},
        "is_mandatory": True,
    })
    master_list.append({
        "test_key": "coating_repair_rules",
        "category": "Dış Kaplama (3LPE / HDPE)",
        "test_name": "Kaplama Kusur Tamir Kuralları (Coating Repair Limitations)",
        "standard_frequency": "Uygulanan her kaplama tamirinde istisnasız uygulanır",
        "standard_frequency_en": "Applied to every coating repair",
        "standard_acceptance_criteria": "Bir boruda azami 3 tamir; Tek tamir alanı max 25 cm²; Toplam tamir alanı max 200 cm²; Astar boyaya inen hasarlarda ısıyla büzüşen yama ile min 50 mm sağlam kaplama üzerine bindirme; Tamir sonrası %100 25 kV holiday kontrolü",
        "clause_ref": "BOTAŞ 5410 R1 Madde 9 / DIN 30670",
        "table_ref": "BOTAŞ 5410 R1 Madde 9",
        "ndt_method_standard": "Onaylı Kaplama Tamir Kiti + 25 kV Holiday Dedektörü",
        "ndt_acceptance_level": "Max 3 Tamir / Boru, Tek Tamir ≤ 25 cm², Toplam ≤ 200 cm²",
        "calculated_target_str": "Boru Başına Max 3 Tamir | Tek Tamir ≤ 25 cm² | Toplam ≤ 200 cm² | Yama Bindirme ≥ 50 mm",
        "calculated_targets": {"max_repairs_per_pipe": 3, "max_single_repair_area_cm2": 25.0, "max_total_repair_area_cm2": 200.0, "min_patch_overlap_mm": 50.0},
        "is_mandatory": True,
    })
    master_list.append({
        "test_key": "personnel_qualification_ndt",
        "category": "Kalite & Sertifikasyon",
        "test_name": "NDT Personel Yetkinliği ve Sertifikasyonu (Personnel Qualification)",
        "standard_frequency": "Proje başlangıcında ve denetim süresince geçerli sertifikalar",
        "standard_frequency_en": "Valid certificates throughout the project",
        "standard_acceptance_criteria": "NDT Süpervizörü / Seviye 3: EN ISO 9712 Level 3; NDT Operatörleri: EN ISO 9712 / EN ISO 11484 Level 1 veya Level 2",
        "clause_ref": "BOTAŞ Şartnamesi Madde 8.8.1 / EN ISO 9712 / EN ISO 11484",
        "table_ref": "EN ISO 9712 / EN ISO 11484",
        "ndt_method_standard": "Personel Kalifikasyon Dosyası & Sertifika Kontrolü",
        "ndt_acceptance_level": "Geçerli Level 2 / Level 3 Sertifikaları",
        "calculated_target_str": "NDT Seviye 3: EN ISO 9712 Level 3 | Operatörler: EN ISO 9712 / 11484 Level 1/2",
        "is_mandatory": True,
    })

    edition = str(cfg.get("standard_edition") or cfg.get("edition") or "47th").lower()
    for it in master_list:
        is_coat = it.get("test_key", "").startswith("coating_") or "Kaplama" in it.get("category", "")
        it["is_coating"] = is_coat

        if "46" in edition and not is_botas:
            tkey = it.get("test_key", "")
            if tkey == "hydrostatic":
                it["clause_ref"] = "API 5L 46. Baskı Madde 10.2.6 & Tablo 26"
                it["table_ref"] = "API 5L 46. Baskı Tablo 26"
            elif tkey == "erw_metallographic_seam":
                it["clause_ref"] = "API 5L 46. Baskı Madde 10.2.5.3 Normalizasyon"
                it["table_ref"] = "API 5L 46. Baskı Madde 10.2.5.3"
            elif tkey == "tensile_body":
                it["clause_ref"] = "API 5L 46. Baskı Madde 9.3 & Tablo 7"
                it["table_ref"] = "API 5L 46. Baskı Tablo 7 / Çizelge 6"
            elif tkey == "cvn_body":
                it["clause_ref"] = "API 5L 46. Baskı Madde 9.8 & Tablo 8"
                it["table_ref"] = "API 5L 46. Baskı Tablo 8"
            elif tkey == "chemical_heat":
                it["clause_ref"] = "API 5L 46. Baskı Madde 9.2 & Tablo 4/5"
                it["table_ref"] = "API 5L 46. Baskı Tablo 4/5"

    # Scope Mode Isolation (Discipline Filter)
    scope_mode = str(cfg.get("scope_mode") or "COMBINED").upper()
    if scope_mode == "COATING_ONLY":
        master_list = [
            it for it in master_list
            if it.get("is_coating", False)
        ]
    elif scope_mode == "BARE_PIPE_ONLY":
        master_list = [
            it for it in master_list
            if not it.get("is_coating", False)
        ]

    return master_list