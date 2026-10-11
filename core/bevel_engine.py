"""
Pipe End Geometry, Bevel Preparation, Root Face, Out-of-Squareness,
and End Ovality Calculation & Verification Engine.

Conforms to:
- API Spec 5L (46th & 47th Editions) Clause 9.12.5 (Pipe Ends), Table 10 & 11
- BOTAŞ Petroleum Pipeline Corporation Specification Clauses 3.3.8, 5.5, 8.1.2.4
- ASME B31.8 Figure I-4 & API 5L 9.12.5.5 (Internal Counterbore & Taper Transitions)
"""

import math
from typing import Any, Dict, Optional


class BevelEngine:
    @staticmethod
    def calculate_bevel_geometry(
        diameter_mm: float,
        wall_thickness_mm: float,
        material_grade: str = "X65",
        standard_code: str = "BOTAŞ",
        end_type: str = "BEVEL",
        bevel_angle_actual: Optional[float] = None,
        root_face_actual: Optional[float] = None,
        out_of_squareness_actual: Optional[float] = None,
        end_diameter_min_actual: Optional[float] = None,
        end_diameter_max_actual: Optional[float] = None,
        pipe_length_m: float = 12.0
    ) -> Dict[str, Any]:
        """
        Calculates pipe end machining dimensions, bevel groove volume, tolerances,
        out-of-squareness limits, end ovality thresholds, and verifies compliance.
        """
        try:
            D = float(diameter_mm)
            t = float(wall_thickness_mm)
            L = float(pipe_length_m)
        except (TypeError, ValueError):
            raise ValueError("Bevel inputs D, t and L must be numeric.")
        if not D > 0.0:
            raise ValueError("diameter_mm must be > 0.")
        if not t > 0.0:
            raise ValueError("wall_thickness_mm must be > 0.")
        if not L > 0.0:
            raise ValueError("pipe_length_m must be > 0.")
        grade = str(material_grade or "X65").upper().strip()
        std = str(standard_code or "BOTAŞ").upper().strip()
        is_botas = "BOTAŞ" in std or "BOTAS" in std

        # ---------------------------------------------------------------------
        # 1. Bevel Angle & Root Face (API 5L 9.12.5.2 & BOTAŞ 3.3.8)
        # ---------------------------------------------------------------------
        # Standard plain-end bevel:
        # Angle nominal = 30°, tolerance +5° / -0° (acceptable range: 30.0° to 35.0°)
        # For special customer specs, 35° +0°/-5° is sometimes allowed.
        bevel_angle_nom = 30.0
        bevel_angle_min = 30.0
        bevel_angle_max = 35.0

        # Root face (landing c):
        # Nominal = 1.6 mm, tolerance ± 0.8 mm (acceptable range: 0.80 mm to 2.40 mm)
        root_face_nom = 1.60
        root_face_min = 0.80
        root_face_max = 2.40

        # Bevel depth & chamfer width
        bevel_depth_nom = max(0.0, t - root_face_nom)
        rad30 = math.radians(bevel_angle_nom)
        axial_cut_width_nom = bevel_depth_nom * math.tan(rad30)
        chamfer_face_length_nom = bevel_depth_nom / math.cos(rad30) if math.cos(rad30) > 0 else bevel_depth_nom

        # Single pipe end half-groove cross-sectional area (mm^2)
        groove_half_area_mm2 = 0.5 * bevel_depth_nom * axial_cut_width_nom
        total_v_groove_area_mm2 = 2.0 * groove_half_area_mm2  # When two pipes abut
        included_groove_angle_deg = 2.0 * bevel_angle_nom  # 60°

        # ---------------------------------------------------------------------
        # 2. Out-of-Squareness (API 5L 9.12.5.1 / 9.12.5.2 & BOTAŞ 5.5)
        # ---------------------------------------------------------------------
        # Pipe ends shall be cut square with the axis within e <= 1.6 mm
        squareness_max_limit_mm = 1.60

        # ---------------------------------------------------------------------
        # 3. End Diameter & Out-of-Roundness / Ovality (API 5L Table 10 & BOTAŞ 8.1.2.4)
        # ---------------------------------------------------------------------
        # Tolerances applied within 100 mm of pipe ends
        if D <= 60.3:
            end_dia_tol_pos = 1.60
            end_dia_tol_neg = -1.60
            ovality_max_mm = 0.015 * D
        elif D <= 610.0:
            end_dia_tol_pos = 1.60
            end_dia_tol_neg = -1.60
            ovality_max_mm = min(4.0, 0.010 * D)
        else:
            # D > 610 mm (24")
            if is_botas:
                end_dia_tol_pos = 1.60
                end_dia_tol_neg = -1.60
                ovality_max_mm = 3.00 if (D / t <= 75.0) else 3.50
            else:
                end_dia_tol_pos = 2.00
                end_dia_tol_neg = -2.00
                ovality_max_mm = 3.00 if (D / t <= 75.0) else 4.00

        end_dia_min_allowed = D + end_dia_tol_neg
        end_dia_max_allowed = D + end_dia_tol_pos

        # ---------------------------------------------------------------------
        # 4. Internal Taper Boring / Counterbore (API 5L 9.12.5.5 & ASME B31.8 Fig I-4)
        # ---------------------------------------------------------------------
        # Max transition taper angle 1:4 (approx 14.04° slope)
        max_counterbore_taper_slope = "1:4 (14.0°)"
        counterbore_max_angle_deg = 14.04
        counterbore_note = (
            "Farklı et kalınlığı veya iç çap geçişlerinde, iç talaş kaldırma (counterbore) "
            "pah açısı en fazla 1:4 (14°) eğimle işlenmeli, gerilme yığılması önlenmelidir."
        )

        # ---------------------------------------------------------------------
        # 5. Verification Checks (Actual vs Limits)
        # ---------------------------------------------------------------------
        checks = []
        overall_pass = True

        # Check A: Bevel Angle
        ba_stat = "NOT_EVALUATED"
        ba_val = bevel_angle_actual
        if ba_val is not None:
            if bevel_angle_min <= ba_val <= bevel_angle_max:
                ba_stat = "PASS"
            else:
                ba_stat = "FAIL"
                overall_pass = False
        checks.append({
            "parameter": "Alın Kaynak Ağzı Açısı (Bevel Angle)",
            "nominal": bevel_angle_nom,
            "min_allowed": bevel_angle_min,
            "max_allowed": bevel_angle_max,
            "actual": ba_val,
            "unit": "derece (°)",
            "status": ba_stat,
            "criteria": f"{bevel_angle_min:.1f}° — {bevel_angle_max:.1f}° (+5°/-0°)",
            "clause": "BOTAŞ 3.3.8 / API 5L 9.12.5.2"
        })

        # Check B: Root Face
        rf_stat = "NOT_EVALUATED"
        rf_val = root_face_actual
        if rf_val is not None:
            if root_face_min <= rf_val <= root_face_max:
                rf_stat = "PASS"
            else:
                rf_stat = "FAIL"
                overall_pass = False
        checks.append({
            "parameter": "Kök Yüzeyi / Küt Burun (Root Face Landing)",
            "nominal": root_face_nom,
            "min_allowed": root_face_min,
            "max_allowed": root_face_max,
            "actual": rf_val,
            "unit": "mm",
            "status": rf_stat,
            "criteria": f"{root_face_nom:.1f} ± 0.8 mm ({root_face_min:.2f} - {root_face_max:.2f} mm)",
            "clause": "BOTAŞ 3.3.8 / API 5L 9.12.5.2"
        })

        # Check C: Out-of-Squareness
        sq_stat = "NOT_EVALUATED"
        sq_val = out_of_squareness_actual
        if sq_val is not None:
            if sq_val <= squareness_max_limit_mm:
                sq_stat = "PASS"
            else:
                sq_stat = "FAIL"
                overall_pass = False
        checks.append({
            "parameter": "Boru Ucu Diklikten Sapma (Out-of-Squareness)",
            "nominal": 0.00,
            "min_allowed": 0.00,
            "max_allowed": squareness_max_limit_mm,
            "actual": sq_val,
            "unit": "mm",
            "status": sq_stat,
            "criteria": f"≤ {squareness_max_limit_mm:.2f} mm",
            "clause": "BOTAŞ 5.5 / API 5L 9.12.5.1"
        })

        # Check D: End Diameter & Ovality
        ov_stat = "NOT_EVALUATED"
        measured_ovality_mm = None
        if end_diameter_min_actual is not None and end_diameter_max_actual is not None:
            measured_ovality_mm = round(abs(end_diameter_max_actual - end_diameter_min_actual), 2)
            d_min_ok = (end_dia_min_allowed <= end_diameter_min_actual <= end_dia_max_allowed)
            d_max_ok = (end_dia_min_allowed <= end_diameter_max_actual <= end_dia_max_allowed)
            ov_ok = (measured_ovality_mm <= ovality_max_mm)
            if d_min_ok and d_max_ok and ov_ok:
                ov_stat = "PASS"
            else:
                ov_stat = "FAIL"
                overall_pass = False

        checks.append({
            "parameter": "Boru Ucu Dairesellikten Sapma / Ovalite (End Out-of-Roundness)",
            "nominal": 0.00,
            "min_allowed": 0.00,
            "max_allowed": ovality_max_mm,
            "actual": measured_ovality_mm,
            "unit": "mm",
            "status": ov_stat,
            "criteria": f"≤ {ovality_max_mm:.2f} mm (Çap aralığı: {end_dia_min_allowed:.1f} - {end_dia_max_allowed:.1f} mm)",
            "clause": "BOTAŞ 8.1.2.4 / API 5L Tablo 10"
        })

        # Status text
        has_fail = any(c["status"] == "FAIL" for c in checks)
        has_evaluated = any(c["status"] in ("PASS", "FAIL") for c in checks)
        if has_fail:
            verdict = "REJECTED (RED)"
            verdict_class = "text-rose-600 bg-rose-50"
        elif has_evaluated:
            verdict = "APPROVED (UYGUN / KABUL)"
            verdict_class = "text-emerald-600 bg-emerald-50"
        else:
            verdict = "NOMINAL (DENETİME HAZIR)"
            verdict_class = "text-indigo-600 bg-indigo-50"

        return {
            "diameter_mm": round(D, 2),
            "wall_thickness_mm": round(t, 2),
            "material_grade": grade,
            "standard_code": std,
            "end_type": end_type,
            "pipe_length_m": round(L, 2),
            # Geometric Bevel Parameters
            "bevel_angle_deg": round(bevel_angle_nom, 1),
            "bevel_angle_min_deg": round(bevel_angle_min, 1),
            "bevel_angle_max_deg": round(bevel_angle_max, 1),
            "root_face_mm": round(root_face_nom, 2),
            "root_face_min_mm": round(root_face_min, 2),
            "root_face_max_mm": round(root_face_max, 2),
            "bevel_depth_mm": round(bevel_depth_nom, 2),
            "axial_cut_width_mm": round(axial_cut_width_nom, 2),
            "chamfer_face_length_mm": round(chamfer_face_length_nom, 2),
            "included_groove_angle_deg": round(included_groove_angle_deg, 1),
            "groove_half_area_mm2": round(groove_half_area_mm2, 2),
            "total_v_groove_area_mm2": round(total_v_groove_area_mm2, 2),
            # Squareness
            "squareness_max_limit_mm": squareness_max_limit_mm,
            # End Diameter & Ovality Limits
            "end_dia_tol_pos_mm": end_dia_tol_pos,
            "end_dia_tol_neg_mm": end_dia_tol_neg,
            "end_dia_min_allowed_mm": round(end_dia_min_allowed, 2),
            "end_dia_max_allowed_mm": round(end_dia_max_allowed, 2),
            "end_ovality_max_limit_mm": round(ovality_max_mm, 2),
            # Counterbore / Taper
            "counterbore_max_taper_slope": max_counterbore_taper_slope,
            "counterbore_max_angle_deg": counterbore_max_angle_deg,
            "counterbore_note": counterbore_note,
            # Actual values passed in
            "bevel_angle_actual": ba_val,
            "root_face_actual": rf_val,
            "out_of_squareness_actual": sq_val,
            "end_diameter_min_actual": end_diameter_min_actual,
            "end_diameter_max_actual": end_diameter_max_actual,
            "end_ovality_actual": measured_ovality_mm,
            # Checks & Overall Evaluation
            "checks": checks,
            "verdict": verdict,
            "verdict_class": verdict_class,
            "is_compliant": (not has_fail)
        }
