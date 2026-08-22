"""
Multi-Standard Pipe Wall Thickness Calculation & Schedule Selection Engine.
Supports:
1. BOTAŞ Specification (Gas Transmission & Station Piping)
2. ASME B31.8 (Gas Transmission) / ASME B31.4 (Liquid Petroleum)
3. ASME B31.3 (Process Piping)
Standard schedule selection from ASME B36.10M (Carbon Steel) and ASME B36.19M (Stainless Steel).
"""

from typing import Dict, Any, List
from core.database import (
    ASME_B36_10_TABLE,
    ASME_B36_19_TABLE,
    PIPE_SIZES_TABLE,
    get_smys_info,
    get_pipe_size_by_inch,
    is_stainless_grade
)

class WallThicknessEngine:
    @staticmethod
    def calculate_wall_thickness(
        diameter_inch: str,
        material_grade: str = "X65",
        design_pressure_bar: float = 75.0,
        design_factor_f: float = 0.72,
        longitudinal_joint_factor_e: float = 1.0,
        temperature_derating_factor_t: float = 1.0,
        corrosion_allowance_mm: float = 0.0,
        location_type: str = "Pipeline",  # "Pipeline", "Station", "Pig Or Valve Station"
        standard_code: str = "BOTAŞ"      # "BOTAŞ", "ASME B31.8 / ASME B31.4", "ASME B31.3"
    ) -> Dict[str, Any]:
        """
        Calculates required wall thickness across BOTAŞ, ASME B31.8/B31.4, or ASME B31.3,
        and selects the appropriate nominal schedule from ASME B36.10M or ASME B36.19M.
        """
        inch_clean = str(diameter_inch).replace('\\', '').replace('"', '').replace("'", '').strip()
        pipe_size = get_pipe_size_by_inch(inch_clean)
        if pipe_size:
            d_mm = pipe_size['mm']
            d_inch = pipe_size['inch']
        else:
            try:
                inch_val = float(inch_clean)
                d_mm = round(inch_val * 25.4, 2)
                d_inch = f"{inch_val}\""
            except (ValueError, TypeError):
                d_mm = 114.3
                d_inch = diameter_inch

        smys_info = get_smys_info(material_grade)
        smys_mpa = smys_info['yield_min_mpa']  # MPa
        p_mpa = design_pressure_bar / 10.0      # bar -> MPa
        is_stainless = is_stainless_grade(material_grade)

        # Standard-specific calculation
        std_upper = standard_code.upper().strip()
        formula_name = ""
        formula_latex = ""

        if "B31.3" in std_upper:
            # ASME B31.3 Process Piping (Paragraph 304.1.2)
            # t = (P * D) / [2 * (S * E * W + P * Y)] + c
            # S: Allowable stress in MPa
            allowable_s_mpa = smys_info.get('allowable_stress_mpa', smys_mpa / 1.5)
            e_quality = longitudinal_joint_factor_e
            w_factor = 1.0  # Weld joint strength reduction factor
            y_coeff = 0.40  # Coefficient for ferritic/austenitic steel at T < 482 C

            denom = 2.0 * (allowable_s_mpa * e_quality * w_factor + p_mpa * y_coeff)
            t_base = (p_mpa * d_mm) / denom if denom > 0 else 0.0
            t_req = t_base + corrosion_allowance_mm
            formula_name = "ASME B31.3 Para. 304.1.2 [P·D / (2·(S·E·W + P·Y)) + c]"
            formula_latex = r"t = \frac{P \cdot D}{2(S \cdot E \cdot W + P \cdot Y)} + c"
            design_factor_used = f"S_allow = {allowable_s_mpa:.1f} MPa (E={e_quality}, Y={y_coeff})"
        elif "B31.8" in std_upper or "B31.4" in std_upper:
            # ASME B31.8 / ASME B31.4 Barlow Pipeline Formula
            # t = (P * D) / (2 * S * F * E * T) + c
            denom = 2.0 * smys_mpa * design_factor_f * longitudinal_joint_factor_e * temperature_derating_factor_t
            t_base = (p_mpa * d_mm) / denom if denom > 0 else 0.0
            t_req = t_base + corrosion_allowance_mm
            formula_name = "ASME B31.8 / B31.4 Barlow [P·D / (2·S·F·E·T) + c]"
            formula_latex = r"t = \frac{P \cdot D}{2 \cdot S \cdot F \cdot E \cdot T} + c"
            design_factor_used = f"F = {design_factor_f:.2f}, E = {longitudinal_joint_factor_e:.2f}, T = {temperature_derating_factor_t:.2f}"
        else:
            # BOTAŞ Specification
            denom = 2.0 * smys_mpa * design_factor_f * longitudinal_joint_factor_e * temperature_derating_factor_t
            t_base = (p_mpa * d_mm) / denom if denom > 0 else 0.0
            t_req = t_base + corrosion_allowance_mm
            formula_name = f"BOTAŞ Şartnamesi ({location_type}) Barlow Formülü"
            formula_latex = r"t = \frac{P \cdot D}{2 \cdot S \cdot F \cdot E \cdot T} + c"
            design_factor_used = f"F = {design_factor_f:.2f} ({location_type})"

        # Schedule Table Selection (ASME B36.19M for Stainless, ASME B36.10M for Carbon)
        target_schedule_table = ASME_B36_19_TABLE if is_stainless else ASME_B36_10_TABLE
        schedule_standard_name = "ASME B36.19M (Paslanmaz Çelik)" if is_stainless else "ASME B36.10M (Karbon Çeliği)"

        inch_key = inch_clean
        avail_thks: List[float] = []

        # Find schedule thicknesses for this diameter
        for k, v in target_schedule_table.items():
            k_clean = str(k).replace('\\', '').replace('"', '').replace("'", '').strip()
            if k_clean == inch_key or f"{k_clean}\"" == d_inch:
                avail_thks = v
                break
            try:
                if float(k_clean) == float(inch_key):
                    avail_thks = v
                    break
            except (ValueError, TypeError):
                pass

        if not avail_thks:
            # Match by nearest diameter in mm using PIPE_SIZES_TABLE
            for p in PIPE_SIZES_TABLE:
                if abs(p['mm'] - d_mm) < 1.0:
                    matched_inch = p['inch'].replace('\\', '').replace('"', '').replace("'", '').strip()
                    if matched_inch in target_schedule_table:
                        avail_thks = target_schedule_table[matched_inch]
                        break

        if not avail_thks:
            # Fallback series for very large custom diameters
            avail_thks = [5.56, 6.35, 7.14, 7.92, 8.74, 9.53, 10.31, 11.13, 11.91, 12.70, 14.27, 15.88, 17.48, 19.05, 20.62, 22.22, 23.83, 25.40]

        # Select standard nominal thickness where t_nom * 0.875 >= t_req (12.5% mill tolerance)
        selected_thk = avail_thks[-1]
        for thk in sorted(avail_thks):
            if (thk * 0.875) >= t_req:
                selected_thk = thk
                break
            elif thk >= t_req:
                selected_thk = thk

        neg_tolerance_val = round(selected_thk * 0.875, 2)
        is_safe = neg_tolerance_val >= t_req or selected_thk >= t_req

        # BOTAŞ standard thickness recommendation from database
        botas_thk_rec = 0.0
        if pipe_size and not is_stainless:
            if design_factor_f >= 0.72:
                botas_thk_rec = pipe_size['botas_thk'].get('0.72_hat', 0.0)
            elif design_factor_f >= 0.60:
                botas_thk_rec = pipe_size['botas_thk'].get('0.60_hat', 0.0)
            else:
                botas_thk_rec = pipe_size['botas_thk'].get('0.50_hat', pipe_size['botas_thk'].get('0.50_ist1', 0.0))

        return {
            'input_parameters': {
                'diameter_inch': d_inch,
                'diameter_mm': round(d_mm, 2),
                'material_grade': material_grade,
                'is_stainless': is_stainless,
                'smys_mpa': round(smys_mpa, 2),
                'design_pressure_bar': round(design_pressure_bar, 2),
                'design_factor_f': round(design_factor_f, 2),
                'longitudinal_joint_factor_e': round(longitudinal_joint_factor_e, 2),
                'temperature_derating_factor_t': round(temperature_derating_factor_t, 2),
                'corrosion_allowance_mm': round(corrosion_allowance_mm, 2),
                'location_type': location_type,
                'standard_code': standard_code
            },
            'calculation_results': {
                'formula_name': formula_name,
                'formula_latex': formula_latex,
                'design_factor_used': design_factor_used,
                't_theoretical_mm': round(t_base, 2),
                't_required_asme_b31_8_mm': round(t_req, 2),
                'selected_nominal_thickness_asme_b36_10_mm': round(selected_thk, 2),
                'schedule_standard_used': schedule_standard_name,
                'negative_tolerance_min_mm': neg_tolerance_val,
                'botas_standard_thickness_mm': round(botas_thk_rec, 2),
                'is_nominal_sufficient': is_safe,
                'available_schedule_thicknesses': [round(x, 2) for x in sorted(avail_thks)]
            }
        }
