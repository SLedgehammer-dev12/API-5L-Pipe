"""
Verification & Compliance Engine (PASS / FAIL Analysis).
Compares actual inspection / lab test data against API 5L PSL2 and BOTAŞ specification limits.
"""

from typing import Dict, Any, List
from core.pipe_qaqc_engine import PipeQAQCEngine

class PipeVerificationEngine:
    @staticmethod
    def verify_pipe_test_results(
        pipe_config: Dict[str, Any],
        actual_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Performs comprehensive compliance checks on actual inspection data.
        Returns parameter-by-parameter evaluation, pass/fail status, and summary.
        """
        # First calculate theoretical limits
        limits = PipeQAQCEngine.calculate_pipe_qc(
            diameter_inch=pipe_config.get('diameter_inch', '48"'),
            diameter_mm=pipe_config.get('diameter_mm'),
            wall_thickness_mm=pipe_config.get('wall_thickness_mm'),
            design_factor_str=pipe_config.get('design_factor_str', '0.72 (Hat)'),
            material_grade=pipe_config.get('material_grade', 'X65'),
            manufacturing_process=pipe_config.get('manufacturing_process', 'SAWH'),
            standard_type=pipe_config.get('standard_type', 'BOTAŞ'),
            design_pressure_bar=pipe_config.get('design_pressure_bar')
        )

        checks: List[Dict[str, Any]] = []
        is_all_passed = True

        def add_check(param: str, category: str, actual_val: Any, limit_desc: str, passed: bool, notes: str = ""):
            nonlocal is_all_passed
            if not passed:
                is_all_passed = False
            checks.append({
                'parameter': param,
                'category': category,
                'actual_value': actual_val,
                'required_limit': limit_desc,
                'status': 'PASS' if passed else 'FAIL',
                'notes': notes
            })

        # 1. Chemical Checks
        chem_lim = limits['chemical_analysis']
        if 'C' in actual_data and actual_data['C'] is not None:
            c_val = float(actual_data['C'])
            c_lim = chem_lim['C_max']
            add_check("Karbon (C %)", "Kimyasal Analiz", f"{c_val:.3f}%", f"Max {c_lim:.2f}%", c_val <= c_lim)

        if 'Mn' in actual_data and actual_data['Mn'] is not None:
            mn_val = float(actual_data['Mn'])
            mn_lim = chem_lim['Mn_max']
            add_check("Mangan (Mn %)", "Kimyasal Analiz", f"{mn_val:.3f}%", f"Max {mn_lim:.2f}%", mn_val <= mn_lim)

        if 'P' in actual_data and actual_data['P'] is not None:
            p_val = float(actual_data['P'])
            p_lim = chem_lim['P_max']
            add_check("Fosfor (P %)", "Kimyasal Analiz", f"{p_val:.4f}%", f"Max {p_lim:.3f}%", p_val <= p_lim)

        if 'S' in actual_data and actual_data['S'] is not None:
            s_val = float(actual_data['S'])
            s_lim = chem_lim['S_max']
            add_check("Kükürt (S %)", "Kimyasal Analiz", f"{s_val:.4f}%", f"Max {s_lim:.3f}%", s_val <= s_lim)

        # 2. Wall Thickness Check
        thk_lim = limits['wall_thickness_tolerance']
        if 'wall_thickness_actual' in actual_data and actual_data['wall_thickness_actual'] is not None:
            t_act = float(actual_data['wall_thickness_actual'])
            t_min = thk_lim['min_mm']
            t_max = thk_lim['max_mm']
            passed = (t_act >= t_min and t_act <= t_max)
            add_check("Et Kalınlığı (mm)", "Boyutsal Kontrol", f"{t_act:.2f} mm", f"{t_min:.2f} - {t_max:.2f} mm", passed)

        # 3. Mechanical Checks
        mech_lim = limits['mechanical_properties']
        if 'yield_strength_actual' in actual_data and actual_data['yield_strength_actual'] is not None:
            y_act = float(actual_data['yield_strength_actual'])
            y_min = mech_lim['yield_min_mpa']
            y_max = mech_lim['yield_max_mpa']
            passed = (y_act >= y_min and (y_max == 0 or y_act <= y_max))
            limit_str = f"Min {y_min} MPa" if y_max == 0 else f"{y_min} - {y_max} MPa"
            add_check("Akma Dayanımı (Yield)", "Mekanik Testler", f"{y_act:.1f} MPa", limit_str, passed)

        if 'tensile_strength_actual' in actual_data and actual_data['tensile_strength_actual'] is not None:
            u_act = float(actual_data['tensile_strength_actual'])
            u_min = mech_lim['tensile_min_mpa']
            u_max = mech_lim['tensile_max_mpa']
            passed = (u_act >= u_min and (u_max == 0 or u_act <= u_max))
            limit_str = f"Min {u_min} MPa" if u_max == 0 else f"{u_min} - {u_max} MPa"
            add_check("Çekme Dayanımı (Tensile)", "Mekanik Testler", f"{u_act:.1f} MPa", limit_str, passed)

        if 'yield_strength_actual' in actual_data and 'tensile_strength_actual' in actual_data:
            if actual_data['yield_strength_actual'] and actual_data['tensile_strength_actual']:
                yt_ratio = float(actual_data['yield_strength_actual']) / float(actual_data['tensile_strength_actual'])
                yt_lim = mech_lim['yield_to_tensile_ratio_max']
                add_check("Akma/Çekme Oranı (Y/T)", "Mekanik Testler", f"{yt_ratio:.3f}", f"Max {yt_lim:.2f}", yt_ratio <= yt_lim)

        # 4. Elongation Check
        elong_lim = limits['toughness_and_tests']['elongation_mat_min_percent']
        if 'elongation_actual' in actual_data and actual_data['elongation_actual'] is not None:
            e_act = float(actual_data['elongation_actual'])
            add_check("Minimum Uzama (% e)", "Mekanik Testler", f"{e_act:.1f}%", f"Min {elong_lim:.2f}%", e_act >= elong_lim)

        # 5. Notch Impact (CVN) Check
        cvn_mat_lim = limits['toughness_and_tests']['notch_impact_mat_j']
        if 'cvn_mat_actual' in actual_data and actual_data['cvn_mat_actual'] is not None:
            cvn_act = float(actual_data['cvn_mat_actual'])
            add_check("Çentik Darbe Gövde (CVN)", "Tokluk Testleri", f"{cvn_act:.1f} J", f"Min {cvn_mat_lim} J", cvn_act >= cvn_mat_lim)

        cvn_weld_lim = limits['toughness_and_tests']['notch_impact_weld_j']
        if 'cvn_weld_actual' in actual_data and actual_data['cvn_weld_actual'] is not None:
            cvn_w_act = float(actual_data['cvn_weld_actual'])
            add_check("Çentik Darbe Kaynak (CVN)", "Tokluk Testleri", f"{cvn_w_act:.1f} J", f"Min {cvn_weld_lim} J", cvn_w_act >= cvn_weld_lim)

        # 6. Hydrostatic Test Check
        p_hydro_min = limits['hydrostatic_test']['hydro_test_min_bar']
        if 'hydro_test_actual_bar' in actual_data and actual_data['hydro_test_actual_bar'] is not None:
            p_act = float(actual_data['hydro_test_actual_bar'])
            add_check("Fabrika Hidrostatik Testi", "Basınç Testi", f"{p_act:.1f} bar", f"Min {p_hydro_min:.1f} bar", p_act >= p_hydro_min)

        return {
            'overall_status': 'ACCEPTED' if is_all_passed else 'REJECTED',
            'overall_badge': 'UYGUN (PASS)' if is_all_passed else 'UYGUN DEĞİL (FAIL)',
            'checks_count': len(checks),
            'passed_count': sum(1 for c in checks if c['status'] == 'PASS'),
            'failed_count': sum(1 for c in checks if c['status'] == 'FAIL'),
            'checks': checks,
            'reference_limits': limits
        }
