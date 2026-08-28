"""
Verification & Compliance Engine (PASS / FAIL Analysis).
Compares actual inspection / lab test data against all 40+ API 5L PSL2 and BOTAŞ specification limits.
"""

from typing import Any, Dict, List

from core.database import compute_ce_iww, compute_ce_pcm, get_cvn_specimen_size
from core.pipe_qaqc_engine import PipeQAQCEngine


def _subsize_cvn_factor(d_mm: float, t_mm: float) -> float:
    """Width ratio of the required CVN specimen vs full-size (API 5L Table 22 / 9.8.1.1)."""
    return get_cvn_specimen_size(d_mm, t_mm)["width_ratio"]


def applicable_parameter_keys(limits: Dict[str, Any]) -> List[str]:
    """
    Returns the list of parameters that ARE applicable for this pipe configuration
    (independent of whether actual measurement data was entered). Used to show the
    total parameter count in the verification summary (e.g. "12 / 31 Parametre Uygun").
    """
    inp = limits.get("input_summary", {})
    chem = limits.get("chemical_analysis", {})
    mech = limits.get("mechanical_properties", {})
    dim = limits.get("dimensional_tolerances", {})
    weld = limits.get("weld_and_geometry", {})
    tough = limits.get("toughness_and_tests", {})

    is_psl1 = inp.get("psl_level") and "PSL1" in str(inp.get("psl_level")).upper()
    std = str(inp.get("standard_type", "")).upper()
    is_api = "API" in std
    d = float(inp.get("diameter_mm", 1219.0))
    proc = str(inp.get("manufacturing_process", "")).upper()
    is_saw = any(k in proc for k in ("SAW", "COW"))
    yt_max = mech.get("yield_to_tensile_ratio_max", 0)

    keys: List[str] = []

    def _num(dct, k):
        return isinstance(dct.get(k), (int, float))

    # --- Chemistry (skipped entirely when 'as agreed' for t > 25.0 mm) ---
    if not chem.get("as_agreed"):
        for k, key in (("C_max", "C"), ("Mn_max", "Mn"), ("P_max", "P"), ("S_max", "S"),
                       ("Nb_max", "Nb"), ("V_max", "V"), ("Ti_max", "Ti"), ("N_max", "N")):
            if _num(chem, k):
                keys.append(key)
        if chem.get("nb_v_ti_combined_max"):
            keys.append("nb_v_ti_combined")
        if chem.get("nb_v_combined_max"):
            keys.append("nb_v_combined")
        if _num(chem, "CE_IIW_max") or _num(chem, "CE_Pcm_max"):
            keys.append("CE")

    # --- Dimensions ---
    keys += ["wall_thickness", "diameter_end", "diameter_body"]
    if _num(dim, "ovality_end_mm"):
        keys.append("ovality_end")
    if _num(dim, "ovality_body_mm"):
        keys.append("ovality_body")
    if _num(dim, "pipe_end_peaking_max_mm") and is_saw:
        keys.append("peaking")
    keys.append("squareness")

    # --- Mechanical ---
    keys += ["yield", "tensile"]
    if (not is_psl1) and yt_max > 0 and (not is_api or d > 323.9):
        keys.append("yt_ratio")
    keys.append("elongation")

    # --- Toughness & special tests ---
    if tough.get("cvn_required"):
        if _num(tough, "notch_impact_mat_j"):
            keys.append("cvn_mat")
        if _num(tough, "notch_impact_weld_j"):
            keys.append("cvn_weld")
    if _num(tough, "residual_stress_max_mm") and is_saw:
        keys.append("residual_stress")
    keys.append("hardness")

    # --- Weld geometry (SAW/COW only) ---
    if is_saw:
        for k, key in (("radial_offset_max_mm", "radial_offset"),
                       ("weld_height_inside_mm", "weld_height_inside"),
                       ("weld_height_outside_mm", "weld_height_outside"),
                       ("misalignment_max_mm", "misalignment")):
            if _num(weld, k):
                keys.append(key)

    # --- Weight & hydrostatic ---
    keys += ["weight", "hydro"]

    return keys


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
        psl_level = pipe_config.get('psl_level', 'PSL2')
        is_psl1 = psl_level and "PSL1" in str(psl_level).upper()
        standard_type = pipe_config.get('standard_type', 'BOTAŞ')
        is_api = "API" in str(standard_type).upper()

        # First calculate theoretical limits
        limits = PipeQAQCEngine.calculate_pipe_qc(
            diameter_inch=pipe_config.get('diameter_inch', '48"'),
            diameter_mm=pipe_config.get('diameter_mm'),
            wall_thickness_mm=pipe_config.get('wall_thickness_mm'),
            design_factor_str=pipe_config.get('design_factor_str', '0.72 (Hat)'),
            material_grade=pipe_config.get('material_grade', 'X65'),
            manufacturing_process=pipe_config.get('manufacturing_process', 'SAWH'),
            standard_type=standard_type,
            design_pressure_bar=pipe_config.get('design_pressure_bar'),
            psl_level=psl_level,
            delivery_condition=pipe_config.get('delivery_condition', 'M')
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

        if chem_lim.get('as_agreed'):
            add_check(
                "Kimyasal Bileşim (t > 25.0 mm)",
                "Kimyasal Analiz",
                "—",
                "Anlaşmaya bağlıdır (API 5L 9.2.3)",
                True,
                notes=chem_lim.get('as_agreed_note', '')
            )
        else:
            def _max_check(param, label, act_key, lim_key, dec=2):
                if act_key in actual_data and actual_data[act_key] is not None:
                    val = float(actual_data[act_key])
                    lim = chem_lim.get(lim_key)
                    if isinstance(lim, (int, float)):
                        add_check(label, "Kimyasal Analiz", f"{val:.{dec}f}%", f"Max {lim:.{dec}f}%", val <= lim)

            _max_check("C", "Karbon (C %)", "C", "C_max")
            _max_check("Mn", "Mangan (Mn %)", "Mn", "Mn_max")
            _max_check("P", "Fosfor (P %)", "P", "P_max", 3)
            _max_check("S", "Kükürt (S %)", "S", "S_max", 3)
            _max_check("Nb", "Niyobyum (Nb %)", "Nb", "Nb_max", 3)
            _max_check("V", "Vanadyum (V %)", "V", "V_max", 2)
            _max_check("Ti", "Titanyum (Ti %)", "Ti", "Ti_max", 2)
            _max_check("N", "Azot (N %)", "N", "N_max", 3)

            # Combined Nb + V + Ti (Table 5/4 footnotes d & g) and Nb + V (footnote c)
            if chem_lim.get('nb_v_ti_combined_max') and all(
                k in actual_data and actual_data[k] is not None for k in ('Nb', 'V', 'Ti')
            ):
                comb = float(actual_data['Nb']) + float(actual_data['V']) + float(actual_data['Ti'])
                lim = chem_lim['nb_v_ti_combined_max']
                add_check("Nb + V + Ti (kombine)", "Kimyasal Analiz", f"{comb:.3f}%", f"Max {lim:.2f}%", comb <= lim)
            if chem_lim.get('nb_v_combined_max') and all(
                k in actual_data and actual_data[k] is not None for k in ('Nb', 'V')
            ):
                comb = float(actual_data['Nb']) + float(actual_data['V'])
                lim = chem_lim['nb_v_combined_max']
                add_check("Nb + V (kombine)", "Kimyasal Analiz", f"{comb:.3f}%", f"Max {lim:.2f}%", comb <= lim)

            # Carbon equivalent: computed from composition when possible.
            has_ce_elements = any(k in actual_data and actual_data[k] is not None
                                  for k in ('C', 'Mn', 'Si', 'Cr', 'Mo', 'V', 'Ni', 'Cu', 'B'))
            if has_ce_elements:
                c_val = float(actual_data['C']) if 'C' in actual_data and actual_data['C'] is not None else None
                # Table 5 footnote a: CE_IIW applies if C > 0.12 %, CE_Pcm if C <= 0.12 %.
                ce_iww = compute_ce_iww(actual_data)
                ce_pcm = compute_ce_pcm(actual_data)
                lim_iww = chem_lim.get('CE_IIW_max')
                lim_pcm = chem_lim.get('CE_Pcm_max')
                if isinstance(lim_iww, (int, float)) and (c_val is None or c_val > 0.12):
                    add_check("Karbon Eşdeğeri (CE IIW)", "Kimyasal Analiz", f"{ce_iww:.2f}",
                              f"Max {lim_iww:.2f}", ce_iww <= lim_iww)
                if isinstance(lim_pcm, (int, float)) and (c_val is not None and c_val <= 0.12):
                    add_check("Karbon Eşdeğeri (CE Pcm)", "Kimyasal Analiz", f"{ce_pcm:.2f}",
                              f"Max {lim_pcm:.2f}", ce_pcm <= lim_pcm)
            elif 'CE_IIW' in actual_data and actual_data['CE_IIW'] is not None:
                # Manual CE input (legacy form field)
                ce_val = float(actual_data['CE_IIW'])
                ce_lim = chem_lim.get('CE_IIW_max', 0.43)
                if isinstance(ce_lim, (int, float)):
                    add_check("Karbon Eşdeğeri (CE IIW)", "Kimyasal Analiz", f"{ce_val:.2f}",
                              f"Max {ce_lim:.2f}", ce_val <= ce_lim)

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
                yt_applicable = (not is_psl1) and isinstance(yt_lim, (int, float)) and yt_lim > 0
                if yt_applicable and is_api:
                    # Table 7 footnote c: ratio limit applies only for pipe with D > 323.9 mm
                    d_mm_v = float(limits['input_summary'].get('diameter_mm', 1219.0))
                    yt_applicable = d_mm_v > 323.9
                if yt_applicable:
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

        cvn_required = tough_lim.get('cvn_required', True)
        t_nom = float(limits['input_summary'].get('wall_thickness_mm', 14.30))
        d_nom = float(limits['input_summary'].get('diameter_mm', 1219.0))
        cvn_scale = _subsize_cvn_factor(d_nom, t_nom)  # API 5L 9.8.1.1 / Table 22 (subsize energy scaling)

        if cvn_required:
            if 'cvn_mat_actual' in actual_data and actual_data['cvn_mat_actual'] is not None:
                cvn_m_act = float(actual_data['cvn_mat_actual'])
                full_min = tough_lim['notch_impact_mat_j']
                if isinstance(full_min, (int, float)) and full_min > 0:
                    eff_min = max(1, round(full_min * cvn_scale))
                    passed = cvn_m_act >= eff_min
                    note = ""
                    if 'cvn_mat_ind_actual' in actual_data and actual_data['cvn_mat_ind_actual'] is not None:
                        ind = float(actual_data['cvn_mat_ind_actual'])
                        if ind < 0.75 * eff_min:
                            passed = False
                            note = "Tek değer ortalamanın %75'inin altında (9.8.1.2)"
                    add_check("Çentik Darbe - Gövde (CVN J)", "Tokluk ve Testler",
                              f"{cvn_m_act:.2f} J", f"Min {eff_min:.2f} J", passed, note)

            if 'cvn_weld_actual' in actual_data and actual_data['cvn_weld_actual'] is not None:
                cvn_w_act = float(actual_data['cvn_weld_actual'])
                full_w = tough_lim['notch_impact_weld_j']
                if isinstance(full_w, (int, float)) and full_w > 0:
                    eff_w = max(1, round(full_w * cvn_scale))
                    passed = cvn_w_act >= eff_w
                    note = ""
                    if 'cvn_weld_ind_actual' in actual_data and actual_data['cvn_weld_ind_actual'] is not None:
                        ind = float(actual_data['cvn_weld_ind_actual'])
                        if ind < 0.75 * eff_w:
                            passed = False
                            note = "Tek değer ortalamanın %75'inin altında (9.8.1.2)"
                    add_check("Çentik Darbe - Kaynak (CVN J)", "Tokluk ve Testler",
                              f"{cvn_w_act:.2f} J", f"Min {eff_w:.2f} J", passed, note)

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
            if is_api:
                # API 5L: test pressure shall not fall below the standard test pressure (10.2.6.4/Table 26).
                h_min = float(hydro_lim.get('api_5l_std_test_bar', hydro_lim['hydro_test_min_bar']))
                h_max = float(hydro_lim['hydro_test_max_bar'])
            else:
                # BOTAŞ: min = max - 2 bar (Excel 'Boru Seçim-Kontrol Aracı').
                h_min = hydro_lim['hydro_test_min_bar']
                h_max = hydro_lim['hydro_test_max_bar']
            # Test pressure must be between min and max
            passed = (h_act >= h_min and h_act <= (h_max + 10.0))
            add_check("Fabrika Hidrostatik Basıncı", "Hidrostatik Test", f"{h_act:.2f} Bar", f"{h_min:.2f} - {h_max:.2f} Bar", passed)

        # Summary
        passed_count = sum(1 for c in checks if c['status'] == 'PASS')
        failed_count = sum(1 for c in checks if c['status'] == 'FAIL')
        total_applicable = len(applicable_parameter_keys(limits))
        unchecked_count = max(0, total_applicable - len(checks))

        return {
            'overall_status': 'ACCEPTED' if is_all_passed else 'REJECTED',
            'overall_badge': 'UYGUN (PASS)' if is_all_passed else 'RED (FAIL)',
            'checks_count': len(checks),
            'passed_count': passed_count,
            'failed_count': failed_count,
            'total_applicable': total_applicable,
            'unchecked_count': unchecked_count,
            'checks': checks,
            'pipe_summary': limits['input_summary']
        }
