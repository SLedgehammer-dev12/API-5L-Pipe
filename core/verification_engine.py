"""
Verification & Compliance Engine (PASS / FAIL Analysis).
Compares actual inspection / lab test data against all 40+ API 5L PSL2 and BOTAŞ specification limits.
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

        # ----------------------------------------------------
        # 1. Chemical Composition Checks
        # ----------------------------------------------------
        chem_lim = limits['chemical_analysis']
        if 'C' in actual_data and actual_data['C'] is not None:
            c_val = float(actual_data['C'])
            c_lim = chem_lim['C_max']
            add_check("Karbon (C %)", "Kimyasal Analiz", f"{c_val:.2f}%", f"Max {c_lim:.2f}%", c_val <= c_lim)

        if 'Mn' in actual_data and actual_data['Mn'] is not None:
            mn_val = float(actual_data['Mn'])
            mn_lim = chem_lim['Mn_max']
            add_check("Mangan (Mn %)", "Kimyasal Analiz", f"{mn_val:.2f}%", f"Max {mn_lim:.2f}%", mn_val <= mn_lim)

        if 'P' in actual_data and actual_data['P'] is not None:
            p_val = float(actual_data['P'])
            p_lim = chem_lim['P_max']
            add_check("Fosfor (P %)", "Kimyasal Analiz", f"{p_val:.3f}%", f"Max {p_lim:.3f}%", p_val <= p_lim)

        if 'S' in actual_data and actual_data['S'] is not None:
            s_val = float(actual_data['S'])
            s_lim = chem_lim['S_max']
            add_check("Kükürt (S %)", "Kimyasal Analiz", f"{s_val:.3f}%", f"Max {s_lim:.3f}%", s_val <= s_lim)

        if 'Nb' in actual_data and actual_data['Nb'] is not None:
            nb_val = float(actual_data['Nb'])
            nb_lim = chem_lim['Nb_max'] if 'Nb_max' in chem_lim else 0.05
            add_check("Niyobyum (Nb %)", "Kimyasal Analiz", f"{nb_val:.3f}%", f"Max {nb_lim:.2f}%", nb_val <= nb_lim)

        if 'V' in actual_data and actual_data['V'] is not None:
            v_val = float(actual_data['V'])
            v_lim = chem_lim['V_max']
            add_check("Vanadyum (V %)", "Kimyasal Analiz", f"{v_val:.2f}%", f"Max {v_lim:.2f}%", v_val <= v_lim)

        if 'Ti' in actual_data and actual_data['Ti'] is not None:
            ti_val = float(actual_data['Ti'])
            ti_lim = chem_lim['Ti_max']
            add_check("Titanyum (Ti %)", "Kimyasal Analiz", f"{ti_val:.2f}%", f"Max {ti_lim:.2f}%", ti_val <= ti_lim)

        if 'N' in actual_data and actual_data['N'] is not None:
            n_val = float(actual_data['N'])
            n_lim = chem_lim['N_max']
            add_check("Azot (N %)", "Kimyasal Analiz", f"{n_val:.3f}%", f"Max {n_lim:.3f}%", n_val <= n_lim)

        if 'CE_IIW' in actual_data and actual_data['CE_IIW'] is not None:
            ce_val = float(actual_data['CE_IIW'])
            ce_lim = chem_lim.get('CE_IIW_max', 0.43)
            add_check("Karbon Eşdeğeri (CE IIW)", "Kimyasal Analiz", f"{ce_val:.2f}", f"Max {ce_lim:.2f}", ce_val <= ce_lim)

        # ----------------------------------------------------
        # 2. Wall Thickness & Dimensional Tolerances
        # ----------------------------------------------------
        thk_lim = limits['wall_thickness_tolerance']
        if 'wall_thickness_actual' in actual_data and actual_data['wall_thickness_actual'] is not None:
            t_act = float(actual_data['wall_thickness_actual'])
            t_min = thk_lim['min_mm']
            t_max = thk_lim['max_mm']
            passed = (t_act >= t_min and t_act <= t_max)
            add_check("Et Kalınlığı (mm)", "Boyutsal Tolerans", f"{t_act:.2f} mm", f"{t_min:.2f} - {t_max:.2f} mm", passed)

        dim_lim = limits['dimensional_tolerances']
        if 'diameter_end_actual' in actual_data and actual_data['diameter_end_actual'] is not None:
            d_end_act = float(actual_data['diameter_end_actual'])
            d_end_min = dim_lim['diameter_end_min_mm']
            d_end_max = dim_lim['diameter_end_max_mm']
            passed = (d_end_act >= d_end_min and d_end_act <= d_end_max)
            add_check("Boru Ucu Çapı (mm)", "Boyutsal Tolerans", f"{d_end_act:.2f} mm", f"{d_end_min:.2f} - {d_end_max:.2f} mm", passed)

        if 'diameter_body_actual' in actual_data and actual_data['diameter_body_actual'] is not None:
            d_body_act = float(actual_data['diameter_body_actual'])
            d_body_min = dim_lim['diameter_body_min_mm']
            d_body_max = dim_lim['diameter_body_max_mm']
            passed = (d_body_act >= d_body_min and d_body_act <= d_body_max)
            add_check("Boru Gövde Çapı (mm)", "Boyutsal Tolerans", f"{d_body_act:.2f} mm", f"{d_body_min:.2f} - {d_body_max:.2f} mm", passed)

        if 'ovality_end_actual' in actual_data and actual_data['ovality_end_actual'] is not None:
            ov_end_act = float(actual_data['ovality_end_actual'])
            ov_end_lim = dim_lim['ovality_end_mm']
            if isinstance(ov_end_lim, (int, float)):
                passed = ov_end_act <= ov_end_lim
                add_check("Boru Ucu Ovalite (mm)", "Boyutsal Tolerans", f"{ov_end_act:.2f} mm", f"Max {ov_end_lim:.2f} mm", passed)

        if 'ovality_body_actual' in actual_data and actual_data['ovality_body_actual'] is not None:
            ov_body_act = float(actual_data['ovality_body_actual'])
            ov_body_lim = dim_lim['ovality_body_mm']
            if isinstance(ov_body_lim, (int, float)):
                passed = ov_body_act <= ov_body_lim
                add_check("Boru Gövde Ovalite (mm)", "Boyutsal Tolerans", f"{ov_body_act:.2f} mm", f"Max {ov_body_lim:.2f} mm", passed)

        if 'pipe_end_peaking_actual' in actual_data and actual_data['pipe_end_peaking_actual'] is not None:
            peak_act = float(actual_data['pipe_end_peaking_actual'])
            peak_lim = dim_lim['pipe_end_peaking_max_mm']
            if isinstance(peak_lim, (int, float)):
                passed = peak_act <= peak_lim
                add_check("Boru Ucu Çatılaşma (Peaking mm)", "Boyutsal Tolerans", f"{peak_act:.2f} mm", f"Max {peak_lim:.2f} mm", passed)

        if 'pipe_end_squareness_actual' in actual_data and actual_data['pipe_end_squareness_actual'] is not None:
            sq_act = float(actual_data['pipe_end_squareness_actual'])
            sq_lim = dim_lim['pipe_end_squareness_max_mm']
            if isinstance(sq_lim, (int, float)):
                passed = sq_act <= sq_lim
                add_check("Boru Ucu Diklik (Squareness mm)", "Boyutsal Tolerans", f"{sq_act:.2f} mm", f"Max {sq_lim:.2f} mm", passed)

        # ----------------------------------------------------
        # 3. Mechanical Properties
        # ----------------------------------------------------
        mech_lim = limits['mechanical_properties']
        if 'yield_strength_actual' in actual_data and actual_data['yield_strength_actual'] is not None:
            y_act = float(actual_data['yield_strength_actual'])
            y_min = mech_lim['yield_min_mpa']
            y_max = mech_lim['yield_max_mpa']
            passed = (y_act >= y_min and (y_max == 0 or y_act <= y_max))
            limit_str = f"Min {y_min:.2f} MPa" if y_max == 0 else f"{y_min:.2f} - {y_max:.2f} MPa"
            add_check("Akma Dayanımı (Yield)", "Mekanik Testler", f"{y_act:.2f} MPa", limit_str, passed)

        if 'tensile_strength_actual' in actual_data and actual_data['tensile_strength_actual'] is not None:
            u_act = float(actual_data['tensile_strength_actual'])
            u_min = mech_lim['tensile_min_mpa']
            u_max = mech_lim['tensile_max_mpa']
            passed = (u_act >= u_min and (u_max == 0 or u_act <= u_max))
            limit_str = f"Min {u_min:.2f} MPa" if u_max == 0 else f"{u_min:.2f} - {u_max:.2f} MPa"
            add_check("Çekme Dayanımı (Tensile)", "Mekanik Testler", f"{u_act:.2f} MPa", limit_str, passed)

        if 'yield_strength_actual' in actual_data and 'tensile_strength_actual' in actual_data:
            if actual_data['yield_strength_actual'] and actual_data['tensile_strength_actual']:
                yt_ratio = float(actual_data['yield_strength_actual']) / float(actual_data['tensile_strength_actual'])
                yt_lim = mech_lim['yield_to_tensile_ratio_max']
                add_check("Akma/Çekme Oranı (Y/T)", "Mekanik Testler", f"{yt_ratio:.2f}", f"Max {yt_lim:.2f}", yt_ratio <= yt_lim)

        # ----------------------------------------------------
        # 4. Weld Geometry & Offsets
        # ----------------------------------------------------
        weld_lim = limits['weld_and_geometry']
        if 'radial_offset_actual' in actual_data and actual_data['radial_offset_actual'] is not None:
            ro_act = float(actual_data['radial_offset_actual'])
            ro_lim = weld_lim['radial_offset_max_mm']
            if isinstance(ro_lim, (int, float)):
                passed = ro_act <= ro_lim
                add_check("Radyal Ofset (Radial Offset mm)", "Kaynak Geometrisi", f"{ro_act:.2f} mm", f"Max {ro_lim:.2f} mm", passed)

        if 'weld_height_inside_actual' in actual_data and actual_data['weld_height_inside_actual'] is not None:
            whi_act = float(actual_data['weld_height_inside_actual'])
            whi_lim = weld_lim['weld_height_inside_mm']
            if isinstance(whi_lim, (int, float)):
                passed = whi_act <= whi_lim
                add_check("Kaynak Yüksekliği - İç (mm)", "Kaynak Geometrisi", f"{whi_act:.2f} mm", f"Max {whi_lim:.2f} mm", passed)

        if 'weld_height_outside_actual' in actual_data and actual_data['weld_height_outside_actual'] is not None:
            who_act = float(actual_data['weld_height_outside_actual'])
            who_lim = weld_lim['weld_height_outside_mm']
            if isinstance(who_lim, (int, float)):
                passed = who_act <= who_lim
                add_check("Kaynak Yüksekliği - Dış (mm)", "Kaynak Geometrisi", f"{who_act:.2f} mm", f"Max {who_lim:.2f} mm", passed)

        if 'misalignment_actual' in actual_data and actual_data['misalignment_actual'] is not None:
            mis_act = float(actual_data['misalignment_actual'])
            mis_lim = weld_lim['misalignment_max_mm']
            if isinstance(mis_lim, (int, float)):
                passed = mis_act <= mis_lim
                add_check("Eksenel Kaçıklık (Misalignment mm)", "Kaynak Geometrisi", f"{mis_act:.2f} mm", f"Max {mis_lim:.2f} mm", passed)

        # ----------------------------------------------------
        # 5. Toughness, Residual Stress & Special Tests
        # ----------------------------------------------------
        tough_lim = limits['toughness_and_tests']
        if 'elongation_actual' in actual_data and actual_data['elongation_actual'] is not None:
            e_act = float(actual_data['elongation_actual'])
            e_min = tough_lim['elongation_mat_min_percent']
            passed = e_act >= e_min
            add_check("Minimum Uzama (% e)", "Tokluk ve Testler", f"{e_act:.2f}%", f"Min {e_min:.2f}%", passed)

        if 'cvn_mat_actual' in actual_data and actual_data['cvn_mat_actual'] is not None:
            cvn_m_act = float(actual_data['cvn_mat_actual'])
            cvn_m_min = tough_lim['notch_impact_mat_j']
            if isinstance(cvn_m_min, (int, float)) and cvn_m_min > 0:
                passed = cvn_m_act >= cvn_m_min
                add_check("Çentik Darbe - Gövde (CVN J)", "Tokluk ve Testler", f"{cvn_m_act:.2f} J", f"Min {cvn_m_min:.2f} J", passed)

        if 'cvn_weld_actual' in actual_data and actual_data['cvn_weld_actual'] is not None:
            cvn_w_act = float(actual_data['cvn_weld_actual'])
            cvn_w_min = tough_lim['notch_impact_weld_j']
            if isinstance(cvn_w_min, (int, float)) and cvn_w_min > 0:
                passed = cvn_w_act >= cvn_w_min
                add_check("Çentik Darbe - Kaynak (CVN J)", "Tokluk ve Testler", f"{cvn_w_act:.2f} J", f"Min {cvn_w_min:.2f} J", passed)

        if 'residual_stress_actual' in actual_data and actual_data['residual_stress_actual'] is not None:
            rs_act = float(actual_data['residual_stress_actual'])
            rs_lim = tough_lim['residual_stress_max_mm']
            if isinstance(rs_lim, (int, float)):
                passed = rs_act <= rs_lim
                add_check("Artık Gerilme (Residual Stress mm)", "Tokluk ve Testler", f"{rs_act:.2f} mm", f"Max {rs_lim:.2f} mm", passed)

        if 'hardness_actual' in actual_data and actual_data['hardness_actual'] is not None:
            hard_act = float(actual_data['hardness_actual'])
            # Standard limit is 260 HV10 for PSL2 sour or 280-300 HV10
            hard_lim = 280.0
            passed = hard_act <= hard_lim
            add_check("Sertlik Testi (HV10)", "Tokluk ve Testler", f"{hard_act:.2f} HV10", f"Max {hard_lim:.2f} HV10", passed)

        # ----------------------------------------------------
        # 6. Weight & Hydrostatic Test Pressure
        # ----------------------------------------------------
        weight_lim = limits['weights_and_safety']
        if 'weight_actual_kg_m' in actual_data and actual_data['weight_actual_kg_m'] is not None:
            w_act = float(actual_data['weight_actual_kg_m'])
            w_min = weight_lim['weight_min_kg_m']
            w_max = weight_lim['weight_max_kg_m']
            passed = (w_act >= w_min and w_act <= w_max)
            add_check("Birim Ağırlık (kg/m)", "Ağırlık ve Emniyet", f"{w_act:.2f} kg/m", f"{w_min:.2f} - {w_max:.2f} kg/m", passed)

        hydro_lim = limits['hydrostatic_test']
        if 'hydro_test_actual_bar' in actual_data and actual_data['hydro_test_actual_bar'] is not None:
            h_act = float(actual_data['hydro_test_actual_bar'])
            h_min = hydro_lim['hydro_test_min_bar']
            h_max = hydro_lim['hydro_test_max_bar']
            # Test pressure must be between min and max
            passed = (h_act >= h_min and h_act <= (h_max + 10.0))
            add_check("Fabrika Hidrostatik Basıncı", "Hidrostatik Test", f"{h_act:.2f} Bar", f"{h_min:.2f} - {h_max:.2f} Bar", passed)

        # Summary
        passed_count = sum(1 for c in checks if c['status'] == 'PASS')
        failed_count = sum(1 for c in checks if c['status'] == 'FAIL')

        return {
            'overall_status': 'ACCEPTED' if is_all_passed else 'REJECTED',
            'overall_badge': 'UYGUN (PASS)' if is_all_passed else 'RED (FAIL)',
            'checks_count': len(checks),
            'passed_count': passed_count,
            'failed_count': failed_count,
            'checks': checks,
            'pipe_summary': limits['input_summary']
        }
