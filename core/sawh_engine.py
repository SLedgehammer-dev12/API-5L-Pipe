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
) -> Dict[str, Any]:
    """
    Returns strip width B and helix angle alpha (whichever is not provided is derived),
    the practical min/max ranges, the pitch and a validity status.

    If both inputs are given, helix_angle_deg is derived from strip_width_mm and the
    provided helix_angle_deg is reported as the user-entered value.
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
        "strip_width_mm": round(B, 2),
        "helix_angle_deg": round(alpha, 2),
        "pitch_mm": (round(pitch, 2) if math.isfinite(pitch) else None),
        "b_min_mm": round(b_min, 2),
        "b_max_mm": round(b_max, 2),
        "alpha_min_deg": ALPHA_MIN,
        "alpha_max_deg": ALPHA_MAX,
        "valid": valid,
        "status": status,
        "note": note,
        "formula": "B = π·D_mid·cos(α),  α = arccos(B/(π·D_mid)),  D_mid = D − t",
    }