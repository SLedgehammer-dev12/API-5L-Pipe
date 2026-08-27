"""
Multi-Standard Pipe Wall Thickness Calculation & Schedule Selection Engine.
Supports:
1. BOTAŞ Specification (Gas Transmission & Station Piping)
2. ASME B31.8 (Gas Transmission) / ASME B31.4 (Liquid Petroleum)
3. ASME B31.3 (Process Piping)
Standard schedule selection from ASME B36.10M (Carbon Steel) and ASME B36.19M (Stainless Steel).
"""

from typing import Any, Dict, List

from core.database import (
    ASME_B36_10_TABLE,
    ASME_B36_19_TABLE,
    PIPE_SIZES_TABLE,
    get_pipe_size_by_inch,
    get_smys_info,
    is_stainless_grade,
)


class WallThicknessEngine:
    @staticmethod
    def get_api_5l_wall_negative_tolerance(
        diameter_mm: float,
        wall_thickness_mm: float = 10.0,
        manufacturing_process: str = "SAWH"
    ) -> Dict[str, Any]:
        """
        Computes API Spec 5L (47th Edition) Table 11 negative wall thickness tolerance.

        Table 11 (absolute tolerances, converted to % of t here for schedule selection):
        - SMLS (Seamless):
          * t <= 4.0 mm:   -0.5 mm
          * 4.0 < t < 25 mm: -0.125t
          * t >= 25 mm:    -3.0 or -0.1t (whichever is greater)
        - Welded (ERW/HFW/SAW/COW):
          * t <= 5.0 mm:   -0.5 mm
          * 5.0 < t < 15 mm: -0.1t
          * t >= 15 mm:    -1.5 mm
        """
        proc_upper = str(manufacturing_process).upper().strip()
        t = float(wall_thickness_mm or 10.0)

        if "SMLS" in proc_upper or "SEAMLESS" in proc_upper or "DIKISSIZ" in proc_upper:
            if t <= 4.0:
                tol_mm = 0.5
            elif t < 25.0:
                tol_mm = 0.125 * t
            else:
                tol_mm = max(3.0, 0.1 * t)
            desc = "API 5L Tablo 11: Dikişsiz (SMLS) Negatif İmalat Toleransı"
        else:  # welded pipe (ERW / HFW / SAWH / SAWL)
            if t <= 5.0:
                tol_mm = 0.5
            elif t < 15.0:
                tol_mm = 0.10 * t
            else:
                tol_mm = 1.5
            desc = "API 5L Tablo 11: Kaynaklı Boru (ERW/HFW/SAW) Negatif İmalat Toleransı"

        return {
            'tolerance_percent': round(tol_mm / t * 100.0, 2) if t > 0 else 0.0,
            'tolerance_mm': round(tol_mm, 3),
            'rule_description': f"{desc} (-{tol_mm:.2f} mm)",
            'standard_ref': "API Spec 5L (47th Ed.) Table 11"
        }

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
        standard_code: str = "BOTAŞ",     # "BOTAŞ", "ASME B31.8 / ASME B31.4", "ASME B31.3"
        manufacturing_process: str = "SAWH",  # "SMLS", "ERW HFW", "SAWH", "SAWL"
        apply_negative_tolerance: bool = True,
        manual_negative_tolerance_percent: float = 12.5,
        psl_level: str = "PSL2"           # "PSL1", "PSL2"
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
        tolerance_percent_used = 0.0
        tolerance_rule_description = ""
        effective_apply_tolerance = False

        if "B31.3" in std_upper:
            # ASME B31.3 Process Piping (Paragraph 304.1.2)
            # t = (P * D) / [2 * (S * E * W + P * Y)] + c
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
            
            # ASME B31.3: Mill tolerance is active and user-customizable
            effective_apply_tolerance = True
            tolerance_percent_used = float(manual_negative_tolerance_percent) if manual_negative_tolerance_percent > 0 else 12.5
            tolerance_rule_description = f"ASME B31.3 Para. 304.1.2 Negatif İmalat Toleransı: -%{tolerance_percent_used:.1f}"

        elif "B31.8" in std_upper or "B31.4" in std_upper:
            # ASME B31.8 / ASME B31.4 Barlow Pipeline Formula
            # t = (P * D) / (2 * S * F * E * T) + c
            denom = 2.0 * smys_mpa * design_factor_f * longitudinal_joint_factor_e * temperature_derating_factor_t
            t_base = (p_mpa * d_mm) / denom if denom > 0 else 0.0
            t_req = t_base + corrosion_allowance_mm
            formula_name = "ASME B31.8 / B31.4 Barlow [P·D / (2·S·F·E·T) + c]"
            formula_latex = r"t = \frac{P \cdot D}{2 \cdot S \cdot F \cdot E \cdot T} + c"
            design_factor_used = f"F = {design_factor_f:.2f}, E = {longitudinal_joint_factor_e:.2f}, T = {temperature_derating_factor_t:.2f}"
            
            if is_stainless:
                # Non-API 5L (Stainless/Duplex): tolerance is optional
                if apply_negative_tolerance:
                    effective_apply_tolerance = True
                    tolerance_percent_used = float(manual_negative_tolerance_percent) if manual_negative_tolerance_percent > 0 else 12.5
                    tolerance_rule_description = f"Paslanmaz Çelik Negatif İmalat Toleransı: -%{tolerance_percent_used:.1f}"
                else:
                    effective_apply_tolerance = False
                    tolerance_percent_used = 0.0
                    tolerance_rule_description = "Negatif Tolerans Uygulanmadı (Nominal Schedule Doğrudan Seçildi)"
            else:
                # API 5L Carbon Steel: API 5L Table 11 rules by manufacturing process
                tol_info = WallThicknessEngine.get_api_5l_wall_negative_tolerance(d_mm, t_req, manufacturing_process)
                tolerance_percent_used = tol_info['tolerance_percent']
                tolerance_rule_description = tol_info['rule_description']
                effective_apply_tolerance = True

        else:
            # BOTAŞ Specification
            denom = 2.0 * smys_mpa * design_factor_f * longitudinal_joint_factor_e * temperature_derating_factor_t
            t_base = (p_mpa * d_mm) / denom if denom > 0 else 0.0
            t_req = t_base + corrosion_allowance_mm
            formula_name = f"BOTAŞ Şartnamesi ({location_type}) Barlow Formülü"
            formula_latex = r"t = \frac{P \cdot D}{2 \cdot S \cdot F \cdot E \cdot T} + c"
            design_factor_used = f"F = {design_factor_f:.2f} ({location_type})"
            
            if "station" in location_type.lower() or "istasyon" in location_type.lower() or "pig" in location_type.lower():
                effective_apply_tolerance = True
                tolerance_percent_used = 12.5
                tolerance_rule_description = "BOTAŞ İstasyon Şartnamesi Emniyet Payı: -%12.5"
            else:
                effective_apply_tolerance = False
                tolerance_percent_used = 0.0
                tolerance_rule_description = "BOTAŞ Hat Borusu Standart Şartname Değeri"

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

        # Select standard nominal thickness based on effective tolerance check
        selected_thk = avail_thks[-1]
        for thk in sorted(avail_thks):
            if effective_apply_tolerance and tolerance_percent_used > 0:
                eff_thk = thk * (1.0 - (tolerance_percent_used / 100.0))
                if eff_thk >= t_req:
                    selected_thk = thk
                    break
            else:
                if thk >= t_req:
                    selected_thk = thk
                    break

        if effective_apply_tolerance and tolerance_percent_used > 0:
            neg_tolerance_val = round(selected_thk * (1.0 - (tolerance_percent_used / 100.0)), 2)
            is_safe = neg_tolerance_val >= t_req or selected_thk >= t_req
        else:
            neg_tolerance_val = selected_thk
            is_safe = selected_thk >= t_req

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
                'standard_code': standard_code,
                'manufacturing_process': manufacturing_process,
                'psl_level': psl_level,
                'apply_negative_tolerance': effective_apply_tolerance,
                'tolerance_percent_used': tolerance_percent_used
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
                'tolerance_percent_used': tolerance_percent_used,
                'tolerance_rule_description': tolerance_rule_description,
                'botas_standard_thickness_mm': round(botas_thk_rec, 2),
                'is_nominal_sufficient': is_safe,
                'available_schedule_thicknesses': [round(x, 2) for x in sorted(avail_thks)]
            }
        }
