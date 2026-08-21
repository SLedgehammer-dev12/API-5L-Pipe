"""
API 5L PSL2 & BOTAŞ Pipe QA/QC & Factory Acceptance Test (FAT) Calculation Engine.
Calculates all dimensional, mechanical, chemical, destructive/non-destructive tests,
safety factors and attaches engineering remarks / standard references for every parameter.
"""

import math
from typing import Dict, Any, Optional
from core.database import (
    API_5L_SMYS_TABLE,
    CHEMICAL_COMPOSITION_RULES,
    get_smys_info,
    get_chemical_rules,
    get_pipe_size_by_inch,
    get_pipe_size_by_mm,
    PIPE_SIZES_TABLE
)

# Standard references and engineering explanations for every matrix row
STANDARD_EXPLANATIONS = {
    'diameter': {
        'tr': 'API 5L Madde 9.11.3 / BOTAŞ Çizelge 4 (Boru Anma Çapı ve Dış Çap OD)',
        'en': 'API 5L Cl. 9.11.3 / BOTAŞ Table 4 (Nominal Pipe Size & Outside Diameter OD)'
    },
    'design_factor': {
        'tr': 'ASME B31.8 Çizelge 841.1.6-1 / BOTAŞ Şartnamesi (Tasarım Faktörü F)',
        'en': 'ASME B31.8 Table 841.1.6-1 / BOTAŞ Spec (Design Factor F)'
    },
    'wall_thickness': {
        'tr': 'ASME B31.8 Madde 841.1.1 / BOTAŞ Standart Et Kalınlığı Matrisi',
        'en': 'ASME B31.8 Cl. 841.1.1 / BOTAŞ Standard Thickness Matrix'
    },
    'process': {
        'tr': 'API 5L Madde 6.1 (SAWH: Helisel Tozaltı, ERW: Yüksek Frekans Direnç, SMLS: Dikişsiz)',
        'en': 'API 5L Cl. 6.1 (SAWH: Spiral Submerged Arc, ERW: Electric Resistance, SMLS: Seamless)'
    },
    'grade': {
        'tr': 'API 5L PSL2 / ISO 3183 Çelik Mukavemet Sınıfı',
        'en': 'API 5L PSL2 / ISO 3183 Steel Strength Grade'
    },
    'smys': {
        'tr': 'API 5L Çizelge 7 (Belirtilmiş Minimum Akma Mukavemeti - SMYS)',
        'en': 'API 5L Table 7 (Specified Minimum Yield Strength - SMYS)'
    },
    'chemical': {
        'tr': 'API 5L Çizelge 5 (PSL2 Kimyasal Bileşim Ürün Analizi Limitleri)',
        'en': 'API 5L Table 5 (PSL2 Chemical Composition Product Analysis Limits)'
    },
    'wall_thickness_tol': {
        'tr': 'API 5L Çizelge 9 / BOTAŞ Şartnamesi (İmalat Et Kalınlığı Toleransı)',
        'en': 'API 5L Table 9 / BOTAŞ Spec (Manufacturing Wall Thickness Tolerances)'
    },
    'yield_tensile': {
        'tr': 'API 5L Çizelge 7 (Mekanik Çekme ve Akma Dayanım Aralıkları)',
        'en': 'API 5L Table 7 (Mechanical Tensile & Yield Strength Limits)'
    },
    'hydro_test': {
        'tr': 'ASME B31.8 & API 5L Madde 9.3 (Barlow Formülü: P = 2*S*t / D)',
        'en': 'ASME B31.8 & API 5L Cl. 9.3 (Barlow Formula: P = 2*S*t / D)'
    },
    'api_std_test': {
        'tr': 'API 5L Madde 9.3.1 (Standart Fabrika Hidrostatik Deney Basıncı Katsayıları)',
        'en': 'API 5L Cl. 9.3.1 (Standard Mill Hydrostatic Test Pressure Factors)'
    },
    'diameter_tol': {
        'tr': 'API 5L Çizelge 10 / BOTAŞ Çizelge 4 (Boru Ucu ve Gövde Çap Toleransları)',
        'en': 'API 5L Table 10 / BOTAŞ Table 4 (Pipe End & Body Diameter Tolerances)'
    },
    'circumference_tol': {
        'tr': 'BOTAŞ Şartnamesi (Çap Toleransı x Pi / Çevre Ölçüm Bandı)',
        'en': 'BOTAŞ Spec (Diameter Tolerance x Pi / Circumferential Tape Measurement)'
    },
    'ovality': {
        'tr': 'API 5L Madde 9.11.3.3 / BOTAŞ Şartnamesi (Boru Ucu ve Gövde Ovalite Sınırları)',
        'en': 'API 5L Cl. 9.11.3.3 / BOTAŞ Spec (Pipe End & Body Out-of-Roundness Limits)'
    },
    'elongation': {
        'tr': 'API 5L Madde 9.3.2 Formülü: e = 1940 * A^0.2 / U^0.9 (Minimum Uzama %)',
        'en': 'API 5L Cl. 9.3.2 Formula: e = 1940 * A^0.2 / U^0.9 (Min. Elongation %)'
    },
    'radial_offset': {
        'tr': 'API 5L Çizelge E.1 / BOTAŞ Şartnamesi (Kaynak Radyal Kaçıklık Sınırı)',
        'en': 'API 5L Table E.1 / BOTAŞ Spec (Weld Radial Offset Limits)'
    },
    'weld_height': {
        'tr': 'API 5L Çizelge 16 / BOTAŞ (İç ve Dış Kaynak Dikiş Fazlalığı/Takviyesi)',
        'en': 'API 5L Table 16 / BOTAŞ (Inside & Outside Weld Reinforcement Height)'
    },
    'misalignment': {
        'tr': 'API 5L Ek E / BOTAŞ Şartnamesi (Kaynak Hiza Kaçıklığı Max. mm)',
        'en': 'API 5L Annex E / BOTAŞ Spec (Weld Seam Misalignment Max. mm)'
    },
    'cvn': {
        'tr': 'API 5L Çizelge 8 / BOTAŞ (Gövde ve Kaynak Çentik Darbe Tokluğu - CVN 0°C)',
        'en': 'API 5L Table 8 / BOTAŞ (Body & Weld Charpy V-Notch Toughness - CVN 0°C)'
    },
    'yt_ratio': {
        'tr': 'API 5L Çizelge 7 (Maksimum Akma/Çekme Oranı Sınırı)',
        'en': 'API 5L Table 7 (Maximum Yield-to-Tensile Ratio Limit)'
    },
    'residual_stress': {
        'tr': 'BOTAŞ Şartnamesi Madde 4.2: Delta = 12.566*D^2*Yield*0.1 / (E*t) (Artık Gerilme Halka Açılması)',
        'en': 'BOTAŞ Spec Cl. 4.2: Delta = 12.566*D^2*Yield*0.1 / (E*t) (Residual Stress Ring Test)'
    },
    'dwtt': {
        'tr': 'API 5L Madde 9.8.5 (D >= 508 mm / 20" gaz hatlarında DWTT Yırtılma Testi zorunludur)',
        'en': 'API 5L Cl. 9.8.5 (DWTT Drop Weight Tear Test mandatory for gas lines D >= 508 mm / 20")'
    },
    'hardness': {
        'tr': 'API 5L Çizelge 8 (Maksimum Sertlik Sınırı: 300 HV10 / 250 HV)',
        'en': 'API 5L Table 8 (Maximum Hardness Limit: 300 HV10 / 250 HV)'
    },
    'mandrel_jaw': {
        'tr': 'API 5L Madde 9.10.2 / BOTAŞ (Kılavuzlu Bükme Testi Mandrel Çapı ve Çene Açıklığı)',
        'en': 'API 5L Cl. 9.10.2 / BOTAŞ (Guided-Bend Test Mandrel Diameter & Jaw Opening)'
    },
    'flattening': {
        'tr': 'API 5L Madde 9.10.1 (ERW Borularda Düzleştirme/Yassıltma Testi Kriterleri)',
        'en': 'API 5L Cl. 9.10.1 (Flattening Test Criteria for ERW Line Pipe)'
    },
    'peaking': {
        'tr': 'API 5L Madde 9.11.3.4 (Boru Ucu Kaynak Çatılaşma / Tepeleşme Toleransı: D * 0.0015 mm)',
        'en': 'API 5L Cl. 9.11.3.4 (Pipe End Weld Peaking Tolerance: D * 0.0015 mm)'
    },
    'squareness': {
        'tr': 'API 5L Madde 9.11.3.5 (Boru Ucu Diklikten Sapma Toleransı: Max 1.6 mm)',
        'en': 'API 5L Cl. 9.11.3.5 (Pipe End Out-of-Squareness Tolerance: Max 1.6 mm)'
    },
    'weld_repair': {
        'tr': 'API 5L Ek C / BOTAŞ (Tek Tamir Kaynağı Max 150 mm ve >X52 & t>10mm için 100°C Ön Isıtma)',
        'en': 'API 5L Annex C / BOTAŞ (Single Repair Weld Max 150 mm & 100°C Preheat for >X52 & t>10mm)'
    },
    'weight': {
        'tr': 'API 5L Madde 9.11.2 (W = 0.02466 * t * (D - t) kg/m; Min -%3.5, Max +%10)',
        'en': 'API 5L Cl. 9.11.2 (W = 0.02466 * t * (D - t) kg/m; Min -3.5%, Max +10%)'
    },
    'fracture_control': {
        'tr': 'ASME B31.8 Madde 841.1.2 & API 5L Annex G (D > 14" ve Gerilme > %40 SMYS için Kırılma Kontrolü)',
        'en': 'ASME B31.8 Cl. 841.1.2 & API 5L Annex G (Fracture Control for D > 14" & Stress > 40% SMYS)'
    },
    'thick_wall_alt': {
        'tr': 'ASME B31.8 Madde 841.1.1 (D/t < 30 Kalın Etli Boru Alternatif Basınç Tasarım Formülü)',
        'en': 'ASME B31.8 Cl. 841.1.1 (D/t < 30 Thick Wall Pipe Alternative Design Pressure Formula)'
    }
}

class PipeQAQCEngine:
    @staticmethod
    def calculate_pipe_qc(
        diameter_inch: str,
        diameter_mm: Optional[float] = None,
        wall_thickness_mm: Optional[float] = None,
        design_factor_str: str = "0.72 (Hat)",
        material_grade: Optional[str] = None,
        manufacturing_process: str = "SAWH",
        standard_type: str = "BOTAŞ",
        design_pressure_bar: Optional[float] = None
    ) -> Dict[str, Any]:
        """
        Executes complete QA/QC inspection and design calculation for a single pipe configuration.
        Dynamically applies BOTAŞ specification tables or API 5L PSL2 rules.
        """
        # 1. Resolve Nominal Diameter (NPS) and Actual Outside Diameter (OD mm)
        pipe_size = get_pipe_size_by_inch(diameter_inch)
        if pipe_size:
            d_mm = float(pipe_size['mm'])
            d_inch = diameter_inch if (diameter_inch and str(diameter_inch).strip()) else pipe_size['inch']
        elif diameter_mm:
            pipe_size = get_pipe_size_by_mm(diameter_mm)
            d_mm = float(diameter_mm)
            d_inch = diameter_inch if (diameter_inch and str(diameter_inch).strip()) else (pipe_size['inch'] if pipe_size else f"{round(d_mm / 25.4, 1)}\"")
        else:
            d_inch = "48\""
            d_mm = 1219.0
            pipe_size = get_pipe_size_by_inch(d_inch)

        # 2. BOTAŞ vs API 5L Logic for Default Material and Wall Thickness
        std_upper = standard_type.upper().strip()
        is_botas_mode = ("BOTAŞ" in std_upper or "BOTAS" in std_upper)

        # Map design factor key for BOTAŞ table lookup
        factor_key = "0.72_hat"
        if "0.6" in design_factor_str:
            factor_key = "0.60_hat"
        elif "0.5" in design_factor_str and ("ist1" in design_factor_str.lower() or "ist. 1" in design_factor_str.lower()):
            factor_key = "0.50_ist1"
        elif "0.5" in design_factor_str and ("ist2" in design_factor_str.lower() or "ist. 2" in design_factor_str.lower()):
            factor_key = "0.50_ist2"
        elif "0.5" in design_factor_str and ("ist" in design_factor_str.lower() or "İst" in design_factor_str):
            factor_key = "0.50_ist1"
        elif "0.5" in design_factor_str:
            factor_key = "0.50_hat"

        # Determine Material Grade
        if is_botas_mode and (not material_grade or material_grade.strip() == ""):
            # Pick from BOTAŞ standard table
            grade_clean = pipe_size['default_material'] if pipe_size else "X65"
        elif material_grade:
            grade_clean = material_grade.upper().strip()
        else:
            grade_clean = pipe_size['default_material'] if (pipe_size and is_botas_mode) else "X65"

        # Determine Wall Thickness (t)
        t = wall_thickness_mm
        is_auto_botas_thickness = False
        if (t is None or t <= 0) and is_botas_mode and pipe_size:
            botas_thk_val = pipe_size['botas_thk'].get(factor_key, 0.0)
            if botas_thk_val > 0:
                t = botas_thk_val
                is_auto_botas_thickness = True
            else:
                # Fallback to standard station thickness if hat is None for small diameters
                t = pipe_size['botas_thk'].get('0.50_ist1', 14.30)
        
        if t is None or t <= 0:
            t = 14.30

        # Check BOTAŞ compliance of selected thickness
        botas_req_thk = pipe_size['botas_thk'].get(factor_key, 0.0) if pipe_size else 0.0
        botas_thickness_status = "UYGUN"
        if is_botas_mode and botas_req_thk > 0:
            if t < (botas_req_thk - 0.01):
                botas_thickness_status = f"BOTAŞ Şartından Düşük (Gereken: {botas_req_thk} mm)"

        # Parse numeric design factor
        f_factor = 0.72
        if "0.6" in design_factor_str:
            f_factor = 0.60
        elif "0.5" in design_factor_str:
            f_factor = 0.50
        elif "0.4" in design_factor_str:
            f_factor = 0.40
        elif "0.8" in design_factor_str:
            f_factor = 0.80

        # 3. Material & SMYS Properties
        smys_info = get_smys_info(grade_clean)
        smys_psi = smys_info['smys_psi']
        yield_min_mpa = smys_info['yield_min_mpa']
        yield_max_psi = smys_info['yield_max_psi']
        yield_max_mpa = smys_info['yield_max_mpa']
        tensile_min_psi = smys_info['tensile_min_psi']
        tensile_min_mpa = smys_info['tensile_min_mpa']
        tensile_max_psi = smys_info['tensile_max_psi']
        tensile_max_mpa = smys_info['tensile_max_mpa']
        yt_max = smys_info['yield_tensile_max']
        cvn_mat = smys_info['cvn_material_j']
        cvn_weld = smys_info['cvn_weld_j']
        strain_val = smys_info['strain_value']

        # 4. Chemical Composition Rules
        chem_rules = get_chemical_rules(grade_clean)

        # 5. Wall Thickness Tolerances (API 5L Table 9 & BOTAŞ)
        if t < 8.71:
            t_min = round(t - 0.04, 2)
        elif t < 12.71:
            t_min = round(t - 0.10, 2)
        else:
            t_min = round(t - 0.15, 2)

        proc_upper = manufacturing_process.upper()
        if "SMLS" in proc_upper:
            if t < 4.01:
                t_max = round(t + 0.6, 2)
            elif t < 25.0:
                t_max = round(t * 1.15, 2)
            else:
                t_max = round(t + 3.7, 2)
        else:
            if t < 5.01:
                t_max = round(t + 0.5, 2)
            elif t < 15.0:
                t_max = round(t * 1.10, 2)
            else:
                t_max = round(t + 1.5, 2)

        # 6. Hydrostatic Test Pressures (Barlow Formula)
        p_hydro_max = (2.0 * smys_psi * t) / (d_mm * 14.50733)
        p_hydro_min = p_hydro_max - 2.0 if p_hydro_max > 0 else 0.0

        # API 5L Standard Test Pressure Factors
        if grade_clean == "GRADE B":
            api_std_factor = 0.60
        elif d_mm < 219.2:
            api_std_factor = 0.75
        elif d_mm < 508.0 and smys_psi < 65000:
            api_std_factor = 0.85
        else:
            api_std_factor = 0.90
        
        api_std_test_press = p_hydro_max * api_std_factor

        # 7. Diameter & Circumference Tolerances (Table 10 & BOTAŞ Table 4)
        if is_botas_mode and pipe_size:
            d_end_max = pipe_size['diameter_tol_botas']['end_max']
            d_end_min = pipe_size['diameter_tol_botas']['end_min']
            d_body_max = pipe_size['diameter_tol_botas']['body_max']
            d_body_min = pipe_size['diameter_tol_botas']['body_min']
        elif pipe_size:
            d_end_max = pipe_size['diameter_tol_asme']['end_max']
            d_end_min = pipe_size['diameter_tol_asme']['end_min']
            d_body_max = pipe_size['diameter_tol_asme']['body_max']
            d_body_min = pipe_size['diameter_tol_asme']['body_min']
        else:
            d_end_max = d_mm + 1.6
            d_end_min = d_mm - 1.6
            d_body_max = d_mm + 4.0
            d_body_min = d_mm - 4.0

        circ_end_max = round(d_end_max * math.pi, 1)
        circ_end_min = round(d_end_min * math.pi, 1)
        circ_body_max = round(d_body_max * math.pi, 1)
        circ_body_min = round(d_body_min * math.pi, 1)

        ovality_end = pipe_size['ovality']['end'] if pipe_size else "Anlaşmaya bağlıdır."
        ovality_body = pipe_size['ovality']['body'] if pipe_size else "18.3"

        # 8. Minimum Elongation (% e)
        # API 5L: e = 1940 * A^0.2 / U^0.9
        a_cross = round(t * 38.0, -1) if (t * 38.0) < 485.0 else 485.0
        u_val = tensile_min_mpa if tensile_min_mpa > 0 else 535.0
        elongation_mat = 1940.0 * (math.pow(a_cross, 0.2)) / (math.pow(u_val, 0.9))
        elongation_weld = 10.0

        # 9. Radial Offset, Weld Height, Misalignment
        if "SAWH" in proc_upper:
            if t < 15.01:
                radial_offset = 1.5 * 0.75
            elif t < 25.01:
                radial_offset = 0.1 * 0.75 * t
            else:
                radial_offset = 2.5 * 0.75

            weld_h_inside = 3.5 * 0.75
            weld_h_outside = 4.5 * 0.75 if t > 13.0 else 3.5 * 0.75
            misalignment = 4.0 * 0.75 if t > 20.0 else 3.0 * 0.75
            weld_peaking = round(d_mm * 0.0015, 4)
            weld_repair_single = min(d_mm * 0.2, 150.0)
        else:
            radial_offset = "Değer Yok"
            weld_h_inside = "Değer Yok"
            weld_h_outside = "Değer Yok"
            misalignment = "DEĞER YOK"
            weld_peaking = "Bu Ölçü Yok"
            weld_repair_single = "Değer Yok"

        pipe_end_squareness = 1.6

        # 10. Residual Stress Test Max (mm) (BOTAŞ Cl. 4.2)
        if "SAWH" in proc_upper:
            stress_coeff = yield_min_mpa if yield_min_mpa > 0 else 450.0
            residual_stress_max = (12.566 * math.pow(d_mm, 2) * stress_coeff * 0.1) / (200000.0 * t)
        else:
            residual_stress_max = "TEST YOK"

        # 11. DWTT (Drop Weight Tear Test - API 5L Cl. 9.8.5)
        dwtt = "Var" if d_mm >= 508.0 else "TEST YOK"

        # 12. Hardness & Bending (Mandrel & Jaw Opening)
        hardness_test = "300 HV"
        if "SAWH" in proc_upper and strain_val > 0:
            denom = ((strain_val * d_mm / t) - (2.0 * strain_val) - 1.0)
            if denom > 0:
                mandrel_dia = (1.15 * (d_mm - 2.0 * t) / denom) - t
            else:
                mandrel_dia = 200.0
            jaw_opening = mandrel_dia + 3.2 + (2.0 * t)
        else:
            mandrel_dia = "TEST YOK"
            jaw_opening = "TEST YOK"

        # 13. Flattening Test (ERW Pipes)
        if "ERW" in proc_upper or "HFW" in proc_upper:
            weld_open_h = d_mm * 0.66 if (smys_psi > 56600 and t > 12.69) else d_mm * 0.50
            mat_crack_h = d_mm * 0.33 if (d_mm / t > 10.0) else "Soruştur"
            lamination = "Düzleştirme testinde karşı duvarlar değdiğinde Laminasyon ve Yanık bulunmayacaktır"
        else:
            weld_open_h = "TEST YOK"
            mat_crack_h = "TEST YOK"
            lamination = "TEST YOK"

        # 14. Weld Repair Preheat
        if smys_psi > 52000 and t > 10.0:
            repair_preheat = "100 C Ön Isıtma"
        else:
            repair_preheat = "Ön Isıtma Yok"

        # 15. Pipe Weights (kg/m)
        weight_nom = t * 0.02466 * (d_mm - t)
        weight_min = weight_nom * 0.965
        weight_max = weight_nom * 1.10

        # 16. Operating Pressure / SMYS & Fracture Control
        p_oper = design_pressure_bar if (design_pressure_bar and design_pressure_bar > 0) else (75.0 if f_factor >= 0.72 else (82.5 if f_factor >= 0.60 else 100.0))
        oper_press_ratio = (p_oper / p_hydro_max) if p_hydro_max > 0 else 0.0

        # ASME B31.8 841.1.2 Fracture Control & Arrest (OD > 14" / 355.6 mm)
        d_inch_num = round(d_mm / 25.4, 3)
        if d_inch_num > 14.0:
            if oper_press_ratio > 0.40:
                fracture_control = "Brittle Fracture Control, API 5L Annex G ye Bakınız"
            else:
                fracture_control = "API 5L Annex G işlemine gerek yok"
        else:
            if oper_press_ratio > 0.80:
                fracture_control = "Brittle Fracture Control, API 5L Annex G ye Bakınız"
            else:
                fracture_control = "API 5L Annex G işlemine gerek yok"

        # 17. D/t Ratio and Alternative Design Pressure
        d_over_t = d_mm / t
        if d_over_t < 30.0:
            design_formula_alt = "Alternatif Basınç Dizayn Hesabı Kullanılabilir"
            alt_design_press = (2.0 * smys_psi * t / ((d_mm - t) * 14.50733)) * f_factor
        else:
            design_formula_alt = "Normal Basınç Dizayn Hesabı"
            alt_design_press = "Hesaplamaya Gerek Yok"

        return {
            'input_summary': {
                'diameter_inch': d_inch,
                'diameter_mm': d_mm,
                'design_factor_str': design_factor_str,
                'design_factor_num': f_factor,
                'wall_thickness_mm': t,
                'manufacturing_process': manufacturing_process,
                'material_grade': grade_clean,
                'standard_type': standard_type,
                'design_pressure_bar': p_oper,
                'botas_thickness_status': botas_thickness_status
            },
            'chemical_analysis': {
                'C_max': chem_rules['C_max'],
                'Mn_max': chem_rules['Mn_max'],
                'P_max': chem_rules['P_max'],
                'S_max': chem_rules['S_max'],
                'Nb_min_max': f"{chem_rules['Nb_min']:.3f}-{chem_rules['Nb_max']:.3f}" if chem_rules['Nb_min'] > 0 else f"{chem_rules['Nb_max']:.2f}",
                'Nb_label': "Min%-Max%" if chem_rules['Nb_min'] > 0 else "Max %",
                'V_max': chem_rules['V_max'],
                'Ti_max': chem_rules['Ti_max'],
                'N_max': chem_rules['N_max'],
                'CE_IIW_max': chem_rules.get('CE_IIW_max', 0.43),
                'CE_Pcm_max': chem_rules.get('CE_Pcm_max', 0.25)
            },
            'wall_thickness_tolerance': {
                'nominal_mm': t,
                'min_mm': t_min,
                'max_mm': t_max
            },
            'mechanical_properties': {
                'smys_psi': smys_psi,
                'yield_min_psi': smys_psi,
                'yield_min_mpa': yield_min_mpa,
                'yield_max_psi': yield_max_psi,
                'yield_max_mpa': yield_max_mpa,
                'tensile_min_psi': tensile_min_psi,
                'tensile_min_mpa': tensile_min_mpa,
                'tensile_max_psi': tensile_max_psi,
                'tensile_max_mpa': tensile_max_mpa,
                'yield_to_tensile_ratio_max': yt_max
            },
            'hydrostatic_test': {
                'hydro_test_max_bar': round(p_hydro_max, 2),
                'hydro_test_min_bar': round(p_hydro_min, 2),
                'api_5l_std_test_bar': round(api_std_test_press, 2),
                'api_5l_alt_test_bar': round(alt_design_press, 2) if isinstance(alt_design_press, (int, float)) else "Hesaplamaya Gerek Yok"
            },
            'dimensional_tolerances': {
                'diameter_end_max_mm': round(d_end_max, 1),
                'diameter_end_min_mm': round(d_end_min, 1),
                'diameter_body_max_mm': round(d_body_max, 1),
                'diameter_body_min_mm': round(d_body_min, 1),
                'circ_end_max_mm': circ_end_max,
                'circ_end_min_mm': circ_end_min,
                'circ_body_max_mm': circ_body_max,
                'circ_body_min_mm': circ_body_min,
                'ovality_end_mm': ovality_end,
                'ovality_body_mm': ovality_body,
                'pipe_end_peaking_max_mm': weld_peaking,
                'pipe_end_squareness_max_mm': pipe_end_squareness
            },
            'weld_and_geometry': {
                'radial_offset_max_mm': round(radial_offset, 2) if isinstance(radial_offset, (int, float)) else radial_offset,
                'weld_height_inside_mm': round(weld_h_inside, 1) if isinstance(weld_h_inside, (int, float)) else weld_h_inside,
                'weld_height_outside_mm': round(weld_h_outside, 1) if isinstance(weld_h_outside, (int, float)) else weld_h_outside,
                'misalignment_max_mm': round(misalignment, 1) if isinstance(misalignment, (int, float)) else misalignment,
                'weld_repair_length_max_mm': round(weld_repair_single, 1) if isinstance(weld_repair_single, (int, float)) else weld_repair_single,
                'weld_repair_preheat': repair_preheat
            },
            'toughness_and_tests': {
                'elongation_mat_min_percent': round(elongation_mat, 2),
                'elongation_weld_min_percent': elongation_weld,
                'notch_impact_mat_j': cvn_mat,
                'notch_impact_weld_j': cvn_weld,
                'notch_specimen_size': "Tablo 22 ye göre düzenle",
                'residual_stress_max_mm': round(residual_stress_max, 1) if isinstance(residual_stress_max, (int, float)) else residual_stress_max,
                'dwtt_test': dwtt,
                'hardness_test_max': hardness_test,
                'mandrel_dia_max_mm': round(mandrel_dia, 1) if isinstance(mandrel_dia, (int, float)) else mandrel_dia,
                'jaw_opening_max_mm': round(jaw_opening, 1) if isinstance(jaw_opening, (int, float)) else jaw_opening
            },
            'flattening': {
                'weld_opening_height_mm': weld_open_h,
                'material_crack_height_mm': mat_crack_h,
                'lamination_rule': lamination
            },
            'weights_and_safety': {
                'weight_nominal_kg_m': round(weight_nom, 1),
                'weight_min_kg_m': round(weight_min, 1),
                'weight_max_kg_m': round(weight_max, 1),
                'operating_press_over_smys_percent': f"{round(oper_press_ratio * 100.0, 1)}%",
                'operating_press_over_smys_val': oper_press_ratio,
                'fracture_control_asme_841_1_2': fracture_control,
                'd_over_t': round(d_over_t, 1),
                'design_formula_asme_841_1_1': design_formula_alt,
                'alternative_design_pressure_bar': round(alt_design_press, 2) if isinstance(alt_design_press, (int, float)) else alt_design_press
            },
            'explanations': STANDARD_EXPLANATIONS
        }
