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

    plan: List[Dict[str, Any]] = [
        {
            "test": "Kimyasal Analiz (Heat & Product)",
            "clause": f"API 5L 9.2 / {tbl}",
            "clause_ref": CLAUSE_REFERENCES["Kimyasal Analiz (Heat & Product)"],
            "specimen_figure": None,
            "frequency": "Isı başına 1 ısı analizi; ısı başına 2 ürün analizi",
            "location": "Döküm / ürün (sondaj talaşı)",
            "specimen": "Spektrometrik / ıslak analiz",
            "note": "C, Mn, P, S, V, Nb, Ti" + ("" if is_psl1 else " + CE raporlanır"),
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

    if is_psl1:
        # PSL 1: no CVN, no DWTT, no hardness row. Flattening for EW/HFW; bend for D <= 60.3 mm.
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
        # Hard spots (PSL 1)
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