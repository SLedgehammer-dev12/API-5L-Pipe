"""
Inspection & Test Plan (ITP) Generator — API 5L 46th Edition / ISO 3183.

Provides, per pipe configuration, the required test sampling information:
    - frequency (quantity per lot/heat)
    - sampling location
    - specimen dimensions / type

References:
    Table 18 — Inspection frequency for PSL 2 pipe
    Table 20 — Number, orientation and location of test pieces (PSL 2)
    Table 21 — Round bar test piece diameter vs pipe dimensions (transverse tensile)
    Table 22 — Required impact test piece size vs pipe dimensions (CVN)
    Figures 5/6 — Sample and test piece orientation and locations
"""

from typing import Any, Dict, List


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


def get_test_plan(pipe_config: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Returns the API 5L PSL2 inspection & test plan for the given pipe configuration.

    pipe_config keys: diameter_mm, wall_thickness_mm, material_grade,
                      manufacturing_process, standard_type.
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
            "frequency": "Isı başına 1 ısı analizi; ısı başına 2 ürün analizi",
            "location": "Döküm / ürün (sondaj talaşı)",
            "specimen": "Spektrometrik / ıslak analiz",
            "note": "C, Mn, P, S, V, Nb, Ti, N + CE raporlanır",
        },
        {
            "test": "Çekme Testi (Tensile)",
            "clause": "API 5L 9.3 / Table 20",
            "frequency": "Test ünitesi (lot) başına 1 set",
            "location": "Gövde - enine" if not is_smls else "Gövde - boyuna",
            "specimen": _tensile_specimen(d_mm, t_mm),
            "note": "Rt0.5 (yield), Rm (tensile) ve uzama raporlanır",
        },
        {
            "test": "Çentik Darbe (CVN)",
            "clause": "API 5L 9.4 / Table 20 & 22",
            "frequency": "Lot başına 1 set = 3 numune (gövde/kaynak/ITAB)",
            "location": "Gövde (enine) + kaynak merkez hattı + ITAB",
            "specimen": _cvn_specimen_size(t_mm),
            "note": "0 °C test sıcaklığı (aksi sipariş edilmedikçe)",
        },
        {
            "test": "Hidrostatik Test",
            "clause": "API 5L 9.3.1 / 10.2.6",
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
            "frequency": "Lot başına 1 set (kök + kapak)",
            "location": "Kaynak dikişi",
            "specimen": "Tam cidar şerit (kök & kapak bükme)",
            "note": "ISO 5173 / ASTM A370 uyarınca",
        })
        if "ERW" in process or "HFW" in process:
            plan.append({
                "test": "Düzleştirme (Flattening)",
                "clause": "API 5L 9.6",
                "frequency": "Lot başına 1 set",
                "location": "Boru ucu halkası",
                "specimen": "Tam kesit halka numune",
                "note": "ISO 8492 / ASTM A370 uyarınca",
            })

    if is_welded and d_mm >= 508.0:
        plan.append({
            "test": "DWTT (Drop Weight Tear Test)",
            "clause": "API 5L 9.8",
            "frequency": "Isı / lot başına",
            "location": "Gövde - enine",
            "specimen": "Tam cidar (press-notch)",
            "note": "D >= 508 mm kaynaklı hat borusu için zorunlu",
        })

    plan.append({
        "test": "Sertlik Testi",
        "clause": "API 5L 9.9 / Table 20",
        "frequency": "Lot başına",
        "location": "Kaynak dikişi / gövde",
        "specimen": "HV10 / HV5 izi",
        "note": "ISO 6507-1 / ASTM A370 uyarınca",
    })

    return plan
