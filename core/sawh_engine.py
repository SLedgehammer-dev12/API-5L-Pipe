"""
SAWH (Spiral Submerged-Arc Welded) Pipe — Strip Width & Helix Angle Engine.

Geometric relation for the spiral-formed strip (developed-surface model):

    B = pi * D_mid * cos(alpha)         D_mid = D - t
    alpha = arccos( B / (pi * D_mid) )

where B is the strip (coil) width, D the outside diameter, t the wall thickness,
D_mid the mean diameter and alpha the helix angle between the spiral weld seam
and the pipe axis (longitudinal direction).

Boundary / practical checks:
    alpha = 0 deg   -> B = pi * D_mid  (longitudinal / LSAW limit)     [validated]
    alpha -> 90 deg -> B -> 0          (circumferential-weld limit)     [validated]
    practical SAWH range: alpha in [30, 65] deg -> B in [pi*D_mid*cos65, pi*D_mid*cos30]

If neither the strip width nor the helix angle is provided, the default helix
angle (55 deg) is used.
"""

import math
from typing import Any, Dict, Optional

ALPHA_MIN = 30.0   # practical lower bound (deg)
ALPHA_MAX = 65.0   # practical upper bound (deg)
DEFAULT_HELIX_ANGLE = 55.0


def mean_diameter(d_mm: float, t_mm: float) -> float:
    """D_mid = D - t (mean diameter). Validates physical pipe geometry."""
    d = float(d_mm)
    t = float(t_mm) if t_mm is not None else 0.0
    if d <= 0:
        raise ValueError("Boru dış çapı (D) sıfırdan büyük pozitif bir değer olmalıdır.")
    if t >= d and t > 0:
        raise ValueError(f"Et kalınlığı (t={t:.2f} mm) boru dış çapına (D={d:.2f} mm) eşit veya büyük olamaz.")
    return max(0.001, d - t)


def compute_strip_width(d_mm: float, helix_angle_deg: float, t_mm: float = 0.0) -> float:
    """B = pi * D_mid * cos(alpha), in mm."""
    dm = mean_diameter(d_mm, t_mm)
    return math.pi * dm * math.cos(math.radians(float(helix_angle_deg)))


def compute_helix_angle(d_mm: float, strip_width_mm: float, t_mm: float = 0.0) -> float:
    """alpha = arccos(B / (pi * D_mid)), in degrees; ratio clamped to [0, 1]."""
    dm = mean_diameter(d_mm, t_mm)
    denom = math.pi * dm
    if denom <= 0:
        return 0.0
    ratio = max(0.0, min(1.0, float(strip_width_mm) / denom))
    return math.degrees(math.acos(ratio))


def compute_pitch(d_mm: float, helix_angle_deg: float, t_mm: float = 0.0) -> float:
    """Axial advance (pitch) per full turn: P = pi * D_mid * cot(alpha)."""
    dm = mean_diameter(d_mm, t_mm)
    alpha = math.radians(float(helix_angle_deg))
    if math.isclose(alpha, 0.0):
        return math.inf
    return math.pi * dm * (math.cos(alpha) / math.sin(alpha))


def compute_sawh_calc(
    d_mm: float,
    t_mm: float = 0.0,
    strip_width_mm: Optional[float] = None,
    helix_angle_deg: Optional[float] = None,
    edge_milling_allowance_mm: float = 15.0,
    coil_length_m: float = 800.0,
    pipe_length_m: float = 12.0,
    min_skelp_end_distance_mm: float = 300.0,
) -> Dict[str, Any]:
    """
    Returns strip width B and helix angle alpha (whichever is not provided is derived),
    the practical min/max ranges, the pitch and a validity status.

    Includes manufacturing & procurement extensions:
      - edge_milling_allowance_mm: allowance for dual-sided edge milling/slitting
      - strip_width_gross_mm: gross coil order width
      - strip_length_per_meter_pipe: strip consumption in meters per meter of pipe (1 / sin(alpha))
      - seam_stress_reduction_factor: sigma_w / sigma_h = 1 - 0.5 * cos^2(alpha)
      - weight_nominal_kg_m: theoretical pipe nominal weight (API 5L formula)
      - API 5L 8.10 Skelp End Weld (bobin uç kaynağı) safety margin (>= 300 mm from pipe ends)
    """
    d = float(d_mm)
    t = float(t_mm if t_mm is not None else 0.0)
    dm = mean_diameter(d, t)

    if strip_width_mm is None and helix_angle_deg is None:
        helix_angle_deg = DEFAULT_HELIX_ANGLE

    if helix_angle_deg is not None:
        alpha = float(helix_angle_deg)
        B = compute_strip_width(d, alpha, t)
    else:
        B = float(strip_width_mm)
        alpha = compute_helix_angle(d, B, t)

    b_min = compute_strip_width(d, ALPHA_MAX, t)   # pi*D_mid*cos65
    b_max = compute_strip_width(d, ALPHA_MIN, t)   # pi*D_mid*cos30
    pitch = compute_pitch(d, alpha, t)

    # Manufacturing & procurement calculations
    milling = float(edge_milling_allowance_mm) if edge_milling_allowance_mm is not None else 15.0
    b_gross = B + milling

    rad = math.radians(alpha)
    sin_a = math.sin(rad)
    cos_a = math.cos(rad)

    # Strip length per meter of pipe (1 / sin(alpha))
    strip_len_per_m = (1.0 / sin_a) if sin_a > 1e-6 else math.nan
    weld_len_per_m = strip_len_per_m

    # Theoretical pipe weight (API 5L formula: (D - t) * t * 0.0246615)
    weight_nom = (d - t) * t * 0.0246615 if d > t else 0.0

    # Normal stress ratio on helical seam vs hoop stress:
    # sigma_w / sigma_h = sin^2(alpha) + 0.5 * cos^2(alpha) = 1 - 0.5 * cos^2(alpha)
    stress_factor = 1.0 - 0.5 * (cos_a ** 2)
    stress_reduction_pct = (1.0 - stress_factor) * 100.0

    # Skelp End Weld (Bobin Uç Kaynağı) Analysis — API 5L 8.10
    coil_len = float(coil_length_m) if coil_length_m and coil_length_m > 0 else 800.0
    pipe_len = float(pipe_length_m) if pipe_length_m and pipe_length_m > 0 else 12.0
    min_dist_req = float(min_skelp_end_distance_mm) if min_skelp_end_distance_mm is not None else 300.0

    total_pipe_len_coil = coil_len * sin_a if sin_a > 1e-6 else 0.0
    pipes_per_coil = int(total_pipe_len_coil // pipe_len) if pipe_len > 0 else 0
    skelp_pos_in_pipe = total_pipe_len_coil % pipe_len if pipe_len > 0 else 0.0

    dist_to_near_end_m = min(skelp_pos_in_pipe, pipe_len - skelp_pos_in_pipe) if pipe_len > 0 else 0.0
    dist_to_near_end_mm = dist_to_near_end_m * 1000.0
    skelp_axial_span_mm = 0.5 * math.pi * dm * math.sin(2 * rad)

    skelp_end_weld_safe = dist_to_near_end_mm >= min_dist_req
    skelp_end_weld_status = "PASS" if skelp_end_weld_safe else "REJECT_OR_CROP"
    skelp_end_weld_note = (
        f"API 5L 8.10 UYGUN: Bobin uç kaynağı en yakın boru alnından {dist_to_near_end_mm:.1f} mm uzakta (min {min_dist_req:.0f} mm kuralı sağlandı)."
        if skelp_end_weld_safe
        else f"API 5L 8.10 UYARI: Bobin uç kaynağı boru alnına {dist_to_near_end_mm:.1f} mm mesafede (< {min_dist_req:.0f} mm)! Kesim/kırpma boy düzeltmesi gerekir."
    )

    valid = (ALPHA_MIN <= alpha <= ALPHA_MAX) and (b_min - 1e-9 <= B <= b_max + 1e-9)
    if valid:
        status = "valid"
        note = "Helis açısı pratik SAWH aralığında (α ∈ [30°, 65°])."
    elif alpha < ALPHA_MIN or alpha > ALPHA_MAX:
        status = "out_of_range"
        note = "Helis açısı pratik SAWH aralığının dışında (α ∈ [30°, 65°] önerilir)."
    else:
        status = "out_of_range"
        note = "Bant genişliği pratik aralığın dışında."

    return {
        "d_mm": round(d, 2),
        "t_mm": round(t, 2),
        "d_mid_mm": round(dm, 2),
        "d_in_mm": round(max(0.0, d - 2 * t), 2),
        "perimeter_mid_mm": round(math.pi * dm, 2),
        "strip_width_mm": round(B, 2),
        "edge_milling_allowance_mm": round(milling, 2),
        "strip_width_gross_mm": round(b_gross, 2),
        "helix_angle_deg": round(alpha, 2),
        "pitch_mm": (round(pitch, 2) if math.isfinite(pitch) else None),
        "b_min_mm": round(b_min, 2),
        "b_max_mm": round(b_max, 2),
        "alpha_min_deg": ALPHA_MIN,
        "alpha_max_deg": ALPHA_MAX,
        "strip_length_per_meter_pipe": round(strip_len_per_m, 4) if math.isfinite(strip_len_per_m) else None,
        "weld_length_per_meter_pipe": round(weld_len_per_m, 4) if math.isfinite(weld_len_per_m) else None,
        "weight_nominal_kg_m": round(weight_nom, 2),
        "seam_stress_factor": round(stress_factor, 4),
        "seam_stress_reduction_percent": round(stress_reduction_pct, 2),
        "coil_length_m": round(coil_len, 1),
        "pipe_length_m": round(pipe_len, 2),
        "total_pipe_length_per_coil_m": round(total_pipe_len_coil, 2),
        "pipes_per_coil_count": pipes_per_coil,
        "skelp_weld_position_in_pipe_m": round(skelp_pos_in_pipe, 3),
        "skelp_weld_distance_to_nearest_end_mm": round(dist_to_near_end_mm, 1),
        "skelp_weld_axial_span_mm": round(skelp_axial_span_mm, 1),
        "min_skelp_end_distance_mm": round(min_dist_req, 1),
        "skelp_weld_safe": skelp_end_weld_safe,
        "skelp_weld_status": skelp_end_weld_status,
        "skelp_weld_note": skelp_end_weld_note,
        "valid": valid,
        "status": status,
        "note": note,
        "formula": "B = π·D_mid·cos(α),  α = arccos(B/(π·D_mid)),  D_mid = D − t,  P = π·D_mid·cot(α)",
    }