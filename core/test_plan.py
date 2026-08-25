"""
Inspection & Test Plan (ITP) Generator — API 5L 46th Edition / ISO 3183.

Provides, per pipe configuration, the required test sampling information:
    - frequency (quantity per lot/heat)
    - sampling location
    - specimen dimensions / type
    - clause reference (original API 5L text) for each test
    - specimen figure key (for schematic drawings)

References:
    Table 18 — Inspection frequency for PSL 2 pipe
    Table 20 — Number, orientation and location of test pieces (PSL 2)
    Table 21 — Round bar test piece diameter vs pipe dimensions (transverse tensile)
    Table 22 — Required impact test piece size vs pipe dimensions (CVN)
    Figures 5/6 — Sample and test piece orientation and locations
"""

from typing import Any, Dict, List, Optional

# Original clause text (API 5L 46th Edition / ISO 3183) for each test.
# Keyed by the test name; rendered verbatim in the info modal / expandable row.
CLAUSE_REFERENCES: Dict[str, str] = {
    "Kimyasal Analiz (Heat & Product)": (
        "API Spec 5L 46th Ed., Madde 9.1 & Çizelge 18 (PSL 2 Denetim Sıklığı):\n"
        "• Isı analizi (Heat analysis): 'One analysis per heat of steel.'\n"
        "• Ürün analizi (Product analysis): 'Two analyses per heat of steel (taken from separate product items).'\n"
        "• PSL 2 kimyasal bileşim limitleri Çizelge 5'te (t ≤ 25,0 mm) verilir; "
        "C, Mn, P, S, V, Nb, Ti, N ve karbon eşdeğeri (CE IIW / CE Pcm) raporlanır."
    ),
    "Çekme Testi (Tensile)": (
        "API Spec 5L 46th Ed., Madde 9.3 & Çizelge 20 (Test Parçası Sayısı/Yönü/Yeri):\n"
        "• Gövde çekme testi, PSL 2 için 'Once per test unit of pipe with the same cold-expansion ratio' yapılır.\n"
        "• Yön: Kaynaklı boruda gövde ENİNE (enine şerit veya Table 21'e göre yuvarlak çubuk), "
        "SMLS boruda BOYUNA.\n"
        "• D ≥ 610 mm kaynaklı borularda yuvarlak çubuk numune çapı Çizelge 21'e göre "
        "(örn. 8,9 mm / 12,7 mm); daha küçük çaplarda 38,1 mm genişlikte şerit numune.\n"
        "• Rt0.5 (akma), Rm (çekme) ve uzama raporlanır."
    ),
    "Çentik Darbe (CVN)": (
        "API Spec 5L 46th Ed., Madde 9.4 & Çizelge 20 & 22:\n"
        "• PSL 2 gövde + kaynaklı boruda kaynak ve ITAB için Charpy V-notch deneyi "
        "'Once per test unit of pipe with the same cold-expansion ratio' yapılır.\n"
        "• Numune boyutu (tam boy 10×10×55 mm veya alt boyut 7,5 / 6,67 / 5 mm) "
        "boru boyutlarına ve et kalınlığına göre Çizelge 22'den belirlenir.\n"
        "• Test sıcaklığı: aksi sipariş edilmedikçe 0 °C; ortalama ve tek-minimum değerler "
        "Çizelge 8'e göre raporlanır."
    ),
    "Hidrostatik Test": (
        "API Spec 5L 46th Ed., Madde 9.3.1 & 10.2.6:\n"
        "• Her boru hidrostatik deneye tabi tutulur.\n"
        "• Stabilizasyon süresi: 'All sizes of seamless (SMLS) pipe and welded pipe with "
        "D ≤ 457 mm (18.000 in) shall have a stabilization time of not less than 5 seconds. "
        "Welded pipe with D > 457 mm (18.000 in) shall have a stabilization time of "
        "not less than 10 seconds.'\n"
        "• Deney basıncı standart veya alternatif test basıncına göre uygulanır (Clause 9.3.1)."
    ),
    "Kılavuzlu Bükme (Guided Bend)": (
        "API Spec 5L 46th Ed., Madde 9.5 & Çizelge 20:\n"
        "• Kaynaklı borularda kaynak dikişi için kılavuzlu bükme (guided-bend) deneyi yapılır.\n"
        "• Test parçası: tam cidar şerit; kök bükme (root bend) ve kapak bükme (cap bend) numuneleri.\n"
        "• Deney ISO 5173 / ASTM A370 uyarınca yapılır; numunede çatlak olmamalı, "
        "kaynak dikişi çatlamamalıdır."
    ),
    "Düzleştirme (Flattening)": (
        "API Spec 5L 46th Ed., Madde 9.6:\n"
        "• EW/HFW borular için düzleştirme (flattening) deneyi yapılır.\n"
        "• Numune: tam kesit halka (ring); iki plaka arasında sıkıştırılır.\n"
        "• 'The distance between the two plates shall be such that no cracking of the weld "
        "shall occur until the specified distance has been reached.'\n"
        "• Deney ISO 8492 / ASTM A370 uyarınca yapılır."
    ),
    "DWTT (Drop Weight Tear Test)": (
        "API Spec 5L 46th Ed., Madde 9.8:\n"
        "• D ≥ 508 mm kaynaklı hat borularında (gaz hatları) DWTT zorunludur.\n"
        "• Numune: tam cidar, press-notch (presle çentiklenmiş) plaka; gövdeden ENİNE alınır.\n"
        "• Kırılma yüzeyindeki sünek alan oranı Çizelge 8 / sipariş koşullarına göre değerlendirilir."
    ),
    "Sertlik Testi": (
        "API Spec 5L 46th Ed., Madde 9.9 & Çizelge 20:\n"
        "• Gövde / kaynak / ITAB sertlik deneyi lot başına yapılır.\n"
        "• Deney ISO 6506 (Brinell), ISO 6507 (Vickers), ISO 6508 (Rockwell) veya "
        "ASTM A370 uyarınca yapılır.\n"
        "• PSL 2 sınır değerleri siparişe göre (örn. 300 HV10 / 250 HV) uygulanır."
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


def _cvn_specimen_size(wall_thickness_mm: float) -> str:
    """Approximate required CVN specimen size from wall thickness (API 5L Table 22)."""
    t = wall_thickness_mm
    if t >= 11.0:
        return "Tam boy 10 x 10 x 55 mm"
    if t >= 8.0:
        return "3/4 boy 7.5 x 10 x 55 mm"
    if t >= 6.0:
        return "2/3 boy 6.67 x 10 x 55 mm"
    return "1/2 boy 5 x 10 x 55 mm"


def _tensile_specimen(diameter_mm: float, wall_thickness_mm: float) -> str:
    """Tensile test piece per Table 20/21."""
    if diameter_mm >= 610.0:
        dia = "12.7 mm" if wall_thickness_mm >= 20.0 else "8.9 mm"
        return f"Yuvarlak çubuk (çap {dia}, Table 21)"
    return "Şerit 38.1 mm genişlik x tam cidar"


def _tensile_figure(diameter_mm: float) -> str:
    """Selects tensile specimen drawing (round bar vs strip)."""
    if diameter_mm >= 610.0:
        return "tensile_round"
    return "tensile_strip"


def get_test_plan(pipe_config: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Returns the API 5L PSL2 inspection & test plan for the given pipe configuration.

    pipe_config keys: diameter_mm, wall_thickness_mm, material_grade,
                      manufacturing_process, standard_type.
    Each entry includes 'clause_ref' (original standard text) and 'specimen_figure'.
    """
    d_mm = float(pipe_config.get("diameter_mm") or 1219.0)
    t_mm = float(pipe_config.get("wall_thickness_mm") or 14.30)
    process = (pipe_config.get("manufacturing_process") or "SAWH").upper()
    is_welded = any(k in process for k in ("SAW", "ERW", "HFW", "LSAW", "COW"))
    is_smls = "SMLS" in process

    plan: List[Dict[str, Any]] = [
        {
            "test": "Kimyasal Analiz (Heat & Product)",
            "clause": "API 5L 9.1 / Table 18",
            "clause_ref": CLAUSE_REFERENCES["Kimyasal Analiz (Heat & Product)"],
            "specimen_figure": None,
            "frequency": "Isı başına 1 ısı analizi; ısı başına 2 ürün analizi",
            "location": "Döküm / ürün (sondaj talaşı)",
            "specimen": "Spektrometrik / ıslak analiz",
            "note": "C, Mn, P, S, V, Nb, Ti, N + CE raporlanır",
        },
        {
            "test": "Çekme Testi (Tensile)",
            "clause": "API 5L 9.3 / Table 20",
            "clause_ref": CLAUSE_REFERENCES["Çekme Testi (Tensile)"],
            "specimen_figure": _tensile_figure(d_mm),
            "frequency": "Test ünitesi (lot) başına 1 set",
            "location": "Gövde - enine" if not is_smls else "Gövde - boyuna",
            "specimen": _tensile_specimen(d_mm, t_mm),
            "note": "Rt0.5 (yield), Rm (tensile) ve uzama raporlanır",
        },
        {
            "test": "Çentik Darbe (CVN)",
            "clause": "API 5L 9.4 / Table 20 & 22",
            "clause_ref": CLAUSE_REFERENCES["Çentik Darbe (CVN)"],
            "specimen_figure": "charpy",
            "frequency": "Lot başına 1 set = 3 numune (gövde/kaynak/ITAB)",
            "location": "Gövde (enine) + kaynak merkez hattı + ITAB",
            "specimen": _cvn_specimen_size(t_mm),
            "note": "0 °C test sıcaklığı (aksi sipariş edilmedikçe)",
        },
        {
            "test": "Hidrostatik Test",
            "clause": "API 5L 9.3.1 / 10.2.6",
            "clause_ref": CLAUSE_REFERENCES["Hidrostatik Test"],
            "specimen_figure": None,
            "frequency": "Her boru",
            "location": "Boru tam boyu",
            "specimen": "—",
            "note": "Stabilizasyon: 5 s (D<=457 mm) / 10 s (D>457 mm)",
        },
    ]

    if is_welded:
        plan.append({
            "test": "Kılavuzlu Bükme (Guided Bend)",
            "clause": "API 5L 9.5 / Table 20",
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
            "clause": "API 5L 9.8",
            "clause_ref": CLAUSE_REFERENCES["DWTT (Drop Weight Tear Test)"],
            "specimen_figure": "dwtt",
            "frequency": "Isı / lot başına",
            "location": "Gövde - enine",
            "specimen": "Tam cidar (press-notch)",
            "note": "D >= 508 mm kaynaklı hat borusu için zorunlu",
        })

    plan.append({
        "test": "Sertlik Testi",
        "clause": "API 5L 9.9 / Table 20",
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