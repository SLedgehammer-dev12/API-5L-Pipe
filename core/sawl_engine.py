"""
SAWL (Submerged Arc Welded Longitudinal) Pipe Manufacturing & Plate Procurement Engine.
Implements API 5L Clause 8.9 / Annex E (Mechanical Expansion), JCOE / UOE cold forming geometry,
heavy steel plate order sizing, edge planing allowances, and forming force estimations.
"""

import math
from typing import Dict, Any, Optional

# API 5L Clause 8.9 / Table E.1 standard mechanical expansion ratio range (%)
DEFAULT_EXPANSION_RATIO = 1.0     # Nominal %1.0 expansion
MIN_EXPANSION_RATIO = 0.8         # Minimum %0.8 permanent plastic expansion
MAX_EXPANSION_RATIO = 1.5         # Maximum %1.5 permanent plastic expansion

# Edge milling / planing allowance for double-sided weld bevel machining (mm)
DEFAULT_EDGE_MILLING_ALLOWANCE_MM = 30.0  # 15.0 mm each longitudinal side


def mean_diameter(outer_d_mm: float, wall_t_mm: float) -> float:
    """Mean / neutral bending diameter D_mid = D - t (mm)."""
    return max(0.0, float(outer_d_mm) - float(wall_t_mm))


def compute_net_plate_width(outer_d_mm: float, wall_t_mm: float) -> float:
    """Net developed plate width W_net = pi * D_mid (mm)."""
    dm = mean_diameter(outer_d_mm, wall_t_mm)
    return math.pi * dm


def compute_sawl_calc(
    d_mm: float,
    t_mm: float,
    pipe_length_m: float = 12.0,
    edge_milling_allowance_mm: float = DEFAULT_EDGE_MILLING_ALLOWANCE_MM,
    expansion_ratio_pct: float = DEFAULT_EXPANSION_RATIO,
    steel_density_kg_m3: float = 7850.0,
) -> Dict[str, Any]:
    """
    Computes comprehensive SAWL pipe forming geometry, heavy steel plate sizing,
    mechanical expansion calibration according to API 5L Clause 8.9 & Annex E,
    and longitudinal double submerged arc welding (DSAW) joint volume.
    """
    d = float(d_mm)
    t = float(t_mm if t_mm is not None else 0.0)
    dm = mean_diameter(d, t)
    din = max(0.0, d - 2.0 * t)
    pipe_len = float(pipe_length_m if pipe_length_m and pipe_length_m > 0 else 12.0)
    milling = float(edge_milling_allowance_mm if edge_milling_allowance_mm is not None else DEFAULT_EDGE_MILLING_ALLOWANCE_MM)
    er_pct = float(expansion_ratio_pct if expansion_ratio_pct is not None else DEFAULT_EXPANSION_RATIO)
    rho = float(steel_density_kg_m3 if steel_density_kg_m3 and steel_density_kg_m3 > 0 else 7850.0)

    # 1. Developed Plate Dimensions
    w_net = math.pi * dm
    w_gross = w_net + milling
    plate_len = pipe_len  # Typically equal to pipe finished length + minor end crop

    # 2. Weights & Procurement
    # Net plate volume: (W_net / 1000) * L * (t / 1000)
    vol_net_m3 = (w_net / 1000.0) * pipe_len * (t / 1000.0)
    weight_net_kg = vol_net_m3 * rho
    vol_gross_m3 = (w_gross / 1000.0) * pipe_len * (t / 1000.0)
    weight_gross_kg = vol_gross_m3 * rho
    milling_scrap_kg = max(0.0, weight_gross_kg - weight_net_kg)
    milling_scrap_pct = (milling_scrap_kg / weight_gross_kg * 100.0) if weight_gross_kg > 0 else 0.0

    # Theoretical finished pipe nominal weight (API 5L Table 9: (D - t) * t * 0.0246615 * L)
    weight_nom_kg_m = (d - t) * t * 0.0246615 if d > t else 0.0
    weight_nom_pipe_kg = weight_nom_kg_m * pipe_len

    # 3. API 5L Clause 8.9 & Annex E Mechanical Expansion Analysis
    # ER = (D_final - D_as_formed) / D_as_formed * 100
    # => D_as_formed = D_final / (1 + ER / 100)
    er_factor = 1.0 + (er_pct / 100.0)
    d_as_formed = d / er_factor if er_factor > 0 else d
    delta_d_mm = d - d_as_formed
    delta_perimeter_mm = math.pi * delta_d_mm

    er_valid = MIN_EXPANSION_RATIO <= er_pct <= MAX_EXPANSION_RATIO
    if er_valid:
        expansion_status = "PASS"
        expansion_note = (
            f"API 5L 8.9 UYGUN: Mekanik genleşme oranı %{er_pct:.2f} standart aralıkta "
            f"([%{MIN_EXPANSION_RATIO:.1f}, %{MAX_EXPANSION_RATIO:.1f}]). Kalıntı gerilmeler sönümlenir, yuvarlaklık sağlanır."
        )
    elif er_pct < MIN_EXPANSION_RATIO:
        expansion_status = "LOW_EXPANSION"
        expansion_note = (
            f"UYARI: Mekanik genleşme oranı %{er_pct:.2f} düşük (< %{MIN_EXPANSION_RATIO:.1f}). "
            "Kalıntı gerilme sönümleme yetersiz kalabilir veya boru ovalliği tolerans dışına çıkabilir."
        )
    else:
        expansion_status = "HIGH_EXPANSION"
        expansion_note = (
            f"UYARI: Mekanik genleşme oranı %{er_pct:.2f} aşırı yüksek (> %{MAX_EXPANSION_RATIO:.1f}). "
            "Aşırı pekleşme (work hardening) sonucu malzeme sünekliği (çentik darbe tokluğu) düşebilir."
        )

    # 4. JCOE Forming Process Parameters
    # Step 1: J-forming: Edge crimping with radius ~ D/2, crimping width approx. 200-350 mm
    crimp_radius_mm = dm / 2.0
    # Step 2: C-forming: Multi-step punch along first half of plate width
    c_steps_count = max(8, int(math.ceil(w_net / 180.0)))
    # Step 3: O-forming: Multi-step punch along second half to complete open cylinder
    o_steps_count = c_steps_count
    # Forming seam gap before continuous tack welding (typically 0 - 1.5 mm)
    seam_gap_target_mm = 0.8

    # 5. Longitudinal Seam Welding Details
    # DSAW: 1 inside (ID) pass + 1 outside (OD) pass, 0.0 degree angle with pipe axis
    weld_length_total_m = pipe_len
    # Double-V or X-bevel groove volume approximation (approx 0.5 * t * 12 mm per meter)
    weld_deposit_kg_m = (t * 0.18) if t > 0 else 1.5  # empirical DSAW deposited wire weight
    weld_wire_total_kg = weld_deposit_kg_m * pipe_len

    return {
        "d_mm": round(d, 2),
        "t_mm": round(t, 2),
        "d_mid_mm": round(dm, 2),
        "d_in_mm": round(din, 2),
        "pipe_length_m": round(pipe_len, 2),
        "plate_width_net_mm": round(w_net, 2),
        "edge_milling_allowance_mm": round(milling, 2),
        "plate_width_gross_mm": round(w_gross, 2),
        "plate_length_m": round(plate_len, 2),
        "plate_weight_net_kg": round(weight_net_kg, 2),
        "plate_weight_gross_kg": round(weight_gross_kg, 2),
        "milling_scrap_kg": round(milling_scrap_kg, 2),
        "milling_scrap_percent": round(milling_scrap_pct, 2),
        "weight_nominal_kg_m": round(weight_nom_kg_m, 2),
        "weight_nominal_pipe_kg": round(weight_nom_pipe_kg, 2),
        # Mechanical Expansion (Expander)
        "expansion_ratio_pct": round(er_pct, 2),
        "d_as_formed_mm": round(d_as_formed, 2),
        "delta_d_mm": round(delta_d_mm, 2),
        "delta_perimeter_mm": round(delta_perimeter_mm, 2),
        "expansion_ratio_min_pct": MIN_EXPANSION_RATIO,
        "expansion_ratio_max_pct": MAX_EXPANSION_RATIO,
        "expansion_valid": er_valid,
        "expansion_status": expansion_status,
        "expansion_note": expansion_note,
        # JCOE Process
        "forming_method": "JCOE (J-büküm, C-büküm, O-presi, Sürekli Punto, Çift Tozaltı Kaynak, Mekanik Genişletme)",
        "crimp_radius_mm": round(crimp_radius_mm, 1),
        "c_steps_count": c_steps_count,
        "o_steps_count": o_steps_count,
        "seam_gap_target_mm": seam_gap_target_mm,
        "weld_length_total_m": round(weld_length_total_m, 2),
        "weld_wire_total_kg": round(weld_wire_total_kg, 2),
        "formula": "W_net = π·D_mid,  W_brüt = W_net + Freze_Payı,  ER = (D_son − D_ham)/D_ham · 100",
    }
