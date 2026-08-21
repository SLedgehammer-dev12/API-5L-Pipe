"""
Wall Thickness Calculation & ASME B36.10 Schedule Selection Engine.
Calculates required pipe wall thickness according to ASME B31.8, BOTAŞ standards,
and selects the standard nominal wall thickness with negative tolerance verification.
"""

from typing import Dict, Any, List
from core.database import (
    ASME_B36_10_TABLE,
    get_smys_info,
    get_pipe_size_by_inch,
    get_pipe_size_by_mm
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
        location_type: str = "Pipeline"  # "Pipeline", "Station", "Pig Or Valve Station"
    ) -> Dict[str, Any]:
        """
        Calculates required wall thickness and selects standard nominal thickness from ASME B36.10.
        """
        pipe_size = get_pipe_size_by_inch(diameter_inch)
        d_mm = pipe_size['mm'] if pipe_size else 114.3
        d_inch = pipe_size['inch'] if pipe_size else diameter_inch

        smys_info = get_smys_info(material_grade)
        smys_mpa = smys_info['yield_min_mpa']  # MPa
        p_mpa = design_pressure_bar / 10.0      # bar -> MPa

        # ASME B31.8 Formula: t = (P * D) / (2 * S * F * E * T)
        denom = 2.0 * smys_mpa * design_factor_f * longitudinal_joint_factor_e * temperature_derating_factor_t
        t_base = (p_mpa * d_mm) / denom if denom > 0 else 0.0

        # Location Type & Station Tolerances (ASME B31.8)
        if location_type.lower() == "pipeline":
            t_req = t_base + corrosion_allowance_mm
        else:
            # Station / Pig Station
            if d_mm < 168.3:
                # Add 12.5% mill tolerance
                t_req = (t_base + corrosion_allowance_mm) * 1.125
            else:
                t_req = t_base + corrosion_allowance_mm

        # Look up standard schedule thicknesses in ASME B36.10
        inch_key = str(diameter_inch).replace('"', '').replace("'", '').strip()
        avail_thks: List[float] = []
        
        # Exact match or normalized matching
        for k, v in ASME_B36_10_TABLE.items():
            if k == inch_key or f"{k}\"" == diameter_inch:
                avail_thks = v
                break
            try:
                if float(k) == float(inch_key):
                    avail_thks = v
                    break
            except (ValueError, TypeError):
                pass
        
        if not avail_thks:
            # Match by nearest diameter in mm
            for p in PIPE_SIZES_TABLE:
                if abs(p['mm'] - d_mm) < 1.0:
                    matched_inch = p['inch'].replace('"', '').strip()
                    if matched_inch in ASME_B36_10_TABLE:
                        avail_thks = ASME_B36_10_TABLE[matched_inch]
                        break

        if not avail_thks:
            # Fallback standard series
            avail_thks = [2.77, 3.18, 3.96, 4.78, 5.56, 6.35, 7.14, 7.92, 8.74, 9.53, 10.31, 11.13, 11.91, 12.70, 14.27, 15.88, 17.48, 19.05, 20.62, 22.22, 23.83, 25.40]

        # Select standard thickness where t_nom * 0.875 >= t_req (or closest higher)
        selected_thk = avail_thks[-1]
        for thk in sorted(avail_thks):
            # Check negative tolerance 12.5%
            if (thk * 0.875) >= t_req:
                selected_thk = thk
                break
            elif thk >= t_req:
                selected_thk = thk

        neg_tolerance_val = selected_thk * 0.875
        is_safe = neg_tolerance_val >= t_req

        # Compare with BOTAŞ standard recommendation
        botas_thk_rec = 0.0
        if pipe_size:
            if design_factor_f >= 0.72:
                botas_thk_rec = pipe_size['botas_thk']['0.72_hat']
            elif design_factor_f >= 0.60:
                botas_thk_rec = pipe_size['botas_thk']['0.60_hat']
            else:
                botas_thk_rec = pipe_size['botas_thk']['0.50_hat']

        return {
            'inputs': {
                'diameter_inch': d_inch,
                'diameter_mm': d_mm,
                'material_grade': material_grade,
                'smys_mpa': smys_mpa,
                'design_pressure_bar': design_pressure_bar,
                'design_pressure_mpa': round(p_mpa, 2),
                'design_factor_f': design_factor_f,
                'joint_factor_e': longitudinal_joint_factor_e,
                'temp_factor_t': temperature_derating_factor_t,
                'corrosion_allowance_mm': corrosion_allowance_mm,
                'location_type': location_type
            },
            'calculation_results': {
                't_theoretical_mm': round(t_base, 3),
                't_required_asme_b31_8_mm': round(t_req, 3),
                'selected_nominal_thickness_asme_b36_10_mm': round(selected_thk, 2),
                'negative_tolerance_min_mm': round(neg_tolerance_val, 3),
                'is_nominal_sufficient': is_safe,
                'botas_standard_thickness_mm': botas_thk_rec,
                'available_schedules': avail_thks
            }
        }
