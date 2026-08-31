"""
Comprehensive Automated Test Suite for API 5L PSL2 & BOTAŞ Pipe QA/QC & Design Suite.
Evaluates 10+ BOTAŞ pipes, 10+ API 5L pipes, ASME B31.3 / B31.8 wall thickness,
stainless steel ASME B36.19M selection, and 40+ parameter factory verification.
"""

import unittest

from fastapi.testclient import TestClient

from app import app
from core.excel_exporter import ExcelExporter
from core.pipe_qaqc_engine import PipeQAQCEngine
from core.project_manager import ProjectManager
from core.verification_engine import PipeVerificationEngine
from core.wall_thickness_engine import WallThicknessEngine


class TestPipeQAQCSuite(unittest.TestCase):

    def setUp(self):
        self.client = TestClient(app)

    def test_01_nominal_pipe_size_and_actual_od_mapping(self):
        """Verifies Nominal Pipe Size (NPS) is distinct from Outside Diameter (OD mm) and correctly resolved."""
        # 1/2" NPS -> 21.3 mm OD
        res_half = PipeQAQCEngine.calculate_pipe_qc(diameter_inch='1/2"', standard_type='BOTAŞ')
        self.assertEqual(res_half['input_summary']['diameter_mm'], 21.3)
        self.assertEqual(res_half['input_summary']['diameter_inch'], '1/2"')

        # 2" NPS -> 60.3 mm OD
        res_2 = PipeQAQCEngine.calculate_pipe_qc(diameter_inch='2"', standard_type='BOTAŞ')
        self.assertEqual(res_2['input_summary']['diameter_mm'], 60.3)

        # 4" NPS -> 114.3 mm OD
        res_4 = PipeQAQCEngine.calculate_pipe_qc(diameter_inch='4"', standard_type='BOTAŞ')
        self.assertEqual(res_4['input_summary']['diameter_mm'], 114.3)

        # 48" NPS -> 1219.0 mm OD
        res_48 = PipeQAQCEngine.calculate_pipe_qc(diameter_inch='48"', standard_type='BOTAŞ')
        self.assertEqual(res_48['input_summary']['diameter_mm'], 1219.0)

    def test_02_ten_botas_pipes_preset_evaluation(self):
        """Evaluates 10 distinct BOTAŞ standard pipes from preset."""
        preset = ProjectManager.get_10_botas_pipes_preset()
        pipes = preset['pipes']
        self.assertEqual(len(pipes), 10)

        for p in pipes:
            res = PipeQAQCEngine.calculate_pipe_qc(
                diameter_inch=p['diameter_inch'],
                wall_thickness_mm=p['wall_thickness_mm'],
                material_grade=p['material_grade'],
                design_factor_str=p['design_factor_str'],
                manufacturing_process=p['manufacturing_process'],
                standard_type='BOTAŞ'
            )
            self.assertIsNotNone(res)
            self.assertGreater(res['hydrostatic_test']['hydro_test_max_bar'], 0)
            self.assertGreater(res['weights_and_safety']['weight_nominal_kg_m'], 0)

    def test_03_ten_api_5l_pipes_preset_evaluation(self):
        """Evaluates 10 distinct API 5L PSL2 pipes from preset."""
        preset = ProjectManager.get_10_api_5l_pipes_preset()
        pipes = preset['pipes']
        self.assertEqual(len(pipes), 10)

        for p in pipes:
            res = PipeQAQCEngine.calculate_pipe_qc(
                diameter_inch=p['diameter_inch'],
                wall_thickness_mm=p['wall_thickness_mm'],
                material_grade=p['material_grade'],
                design_factor_str=p['design_factor_str'],
                manufacturing_process=p['manufacturing_process'],
                standard_type='API 5L'
            )
            self.assertIsNotNone(res)
            self.assertGreater(res['hydrostatic_test']['hydro_test_max_bar'], 0)
            self.assertGreater(res['chemical_analysis']['C_max'], 0)

    def test_04_engineering_remarks_and_standard_explanations(self):
        """Verifies that engineering explanations and standard references exist for every row."""
        res = PipeQAQCEngine.calculate_pipe_qc(diameter_inch='48"', wall_thickness_mm=14.30, material_grade='X65')
        self.assertIn('explanations', res)
        exp = res['explanations']

        self.assertIn('diameter', exp)
        self.assertIn('hydro_test', exp)
        self.assertIn('residual_stress', exp)
        self.assertIn('elongation', exp)
        self.assertIn('dwtt', exp)
        self.assertIn('weld_repair', exp)

    def test_05_botas_lookup_api_endpoint(self):
        """Tests the /api/botas-lookup endpoint for automatic form filling."""
        # 48" F=0.72 Hat -> X65, 14.30 mm
        r1 = self.client.get('/api/botas-lookup?diameter_inch=48"&factor=0,72 (Hat)')
        self.assertEqual(r1.status_code, 200)
        d1 = r1.json()
        self.assertEqual(d1['material'], 'X65')
        self.assertEqual(d1['thickness'], 14.30)

        # 48" F=0.50 İstasyon 75 Bar -> 22.20 mm
        r_ist75 = self.client.get('/api/botas-lookup?diameter_inch=48"&factor=0,5 (İstasyon - 75 Bar)&pressure=75.0')
        self.assertEqual(r_ist75.status_code, 200)
        self.assertEqual(r_ist75.json()['thickness'], 22.20)

        # 48" F=0.50 İstasyon 82.5 Bar -> 23.80 mm
        r_ist825 = self.client.get('/api/botas-lookup?diameter_inch=48"&factor=0,5 (İstasyon - 82,5 Bar)&pressure=82.5')
        self.assertEqual(r_ist825.status_code, 200)
        self.assertEqual(r_ist825.json()['thickness'], 23.80)

        # 48" F=0.50 Hat -> 20.60 mm
        r_hat50 = self.client.get('/api/botas-lookup?diameter_inch=48"&factor=0,5 (Hat)')
        self.assertEqual(r_hat50.status_code, 200)
        self.assertEqual(r_hat50.json()['thickness'], 20.60)

        # 12" F=0.72 Hat -> X52, 5.20 mm
        r2 = self.client.get('/api/botas-lookup?diameter_inch=12"&factor=0,72 (Hat)')
        self.assertEqual(r2.status_code, 200)
        d2 = r2.json()
        self.assertEqual(d2['material'], 'X52')
        self.assertEqual(d2['thickness'], 5.20)

    def test_06_excel_export_with_10_botas_and_10_api5l(self):
        """Tests Excel exporter with both 10 BOTAŞ and 10 API 5L datasets."""
        p_botas = ProjectManager.get_10_botas_pipes_preset()
        calc_botas = [PipeQAQCEngine.calculate_pipe_qc(
            diameter_inch=p['diameter_inch'],
            wall_thickness_mm=p['wall_thickness_mm'],
            material_grade=p['material_grade'],
            design_factor_str=p['design_factor_str'],
            manufacturing_process=p['manufacturing_process'],
            standard_type='BOTAŞ'
        ) for p in p_botas['pipes']]

        s_botas = ExcelExporter.export_matrix_to_excel(p_botas['project_info'], calc_botas)
        self.assertGreater(len(s_botas.getvalue()), 8000)

    def test_07_check_update_endpoint_and_semver_logic(self):
        """Verifies /api/check-update endpoint and semver comparison."""
        from core.updater import is_newer_version, parse_semver
        
        self.assertEqual(parse_semver('v1.1.0'), (1, 1, 0))
        self.assertTrue(is_newer_version('1.0.3', '1.1.0'))
        self.assertFalse(is_newer_version('1.1.0', '1.1.0'))
        
        resp = self.client.get('/api/check-update')
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertIn('current_version', data)

    def test_08_backward_compatibility_project_migration(self):
        """Verifies that projects created in older versions can be cleanly loaded and evaluated."""
        old_project = {
            "project_info": {"project_name": "Eski Proje v1.0.0"},
            "pipes": [{"diameter_inch": "48\"", "wall_thickness_mm": 14.30, "material_grade": "X65"}]
        }
        pipe = old_project['pipes'][0]
        res = PipeQAQCEngine.calculate_pipe_qc(
            diameter_inch=pipe['diameter_inch'],
            wall_thickness_mm=pipe['wall_thickness_mm'],
            material_grade=pipe['material_grade']
        )
        self.assertIsNotNone(res)
        self.assertEqual(res['input_summary']['material_grade'], 'X65')
        self.assertAlmostEqual(res['hydrostatic_test']['hydro_test_max_bar'], 105.61, delta=0.5)

    def test_09_multi_standard_wall_thickness_and_stainless_selection(self):
        """Verifies wall thickness calculation across BOTAŞ, ASME B31.8, ASME B31.3 and ASME B36.19M Stainless."""
        # 1a. BOTAŞ Standard: 48" X65 F=0.72 P=75 bar (Hat Borusu)
        res_botas_hat = WallThicknessEngine.calculate_wall_thickness('48"', 'X65', design_pressure_bar=75.0, design_factor_f=0.72, location_type='Pipeline', standard_code='BOTAŞ')
        self.assertEqual(res_botas_hat['calculation_results']['t_required_asme_b31_8_mm'], 14.11)
        self.assertEqual(res_botas_hat['calculation_results']['selected_nominal_thickness_asme_b36_10_mm'], 14.27)
        self.assertEqual(res_botas_hat['calculation_results']['schedule_standard_used'], 'ASME B36.10M (Karbon Çeliği)')
        self.assertEqual(res_botas_hat['calculation_results']['botas_standard_thickness_mm'], 14.30)
        self.assertEqual(res_botas_hat['calculation_results']['botas_standard_label'], 'BOTAŞ Şartnamesi (Hat F=0.72)')

        # 1b. BOTAŞ Standard: 48" X65 F=0.50 P=75 bar (İstasyon Borusu 75 Bar - BOTAŞ Matrix standard)
        res_botas_ist_75 = WallThicknessEngine.calculate_wall_thickness('48"', 'X65', design_pressure_bar=75.0, design_factor_f=0.50, location_type='Station', standard_code='BOTAŞ')
        self.assertEqual(res_botas_ist_75['calculation_results']['t_required_asme_b31_8_mm'], 20.32)
        self.assertEqual(res_botas_ist_75['calculation_results']['selected_nominal_thickness_asme_b36_10_mm'], 20.62)
        self.assertEqual(res_botas_ist_75['calculation_results']['tolerance_percent_used'], 0.0)
        self.assertEqual(res_botas_ist_75['calculation_results']['botas_standard_thickness_mm'], 22.20)
        self.assertEqual(res_botas_ist_75['calculation_results']['botas_standard_label'], 'BOTAŞ Şartnamesi (İstasyon - 75 Bar)')

        # 1c. BOTAŞ Standard: 48" X65 F=0.50 P=82.5 bar (İstasyon Borusu 82.5 Bar)
        res_botas_ist_825 = WallThicknessEngine.calculate_wall_thickness('48"', 'X65', design_pressure_bar=82.5, design_factor_f=0.50, location_type='Station', standard_code='BOTAŞ')
        self.assertEqual(res_botas_ist_825['calculation_results']['botas_standard_thickness_mm'], 23.80)
        self.assertEqual(res_botas_ist_825['calculation_results']['botas_standard_label'], 'BOTAŞ Şartnamesi (İstasyon - 82.5 Bar)')

        # 1d. BOTAŞ Standard: 48" X65 F=0.50 P=75 bar (Hat Borusu F=0.50)
        res_botas_hat_050 = WallThicknessEngine.calculate_wall_thickness('48"', 'X65', design_pressure_bar=75.0, design_factor_f=0.50, location_type='Pipeline', standard_code='BOTAŞ')
        self.assertEqual(res_botas_hat_050['calculation_results']['botas_standard_thickness_mm'], 20.60)
        self.assertEqual(res_botas_hat_050['calculation_results']['botas_standard_label'], 'BOTAŞ Şartnamesi (Hat F=0.50)')

        # 1e. BOTAŞ Standard: 24" X65 Station 75 bar and 82.5 bar
        res_botas_24_75 = WallThicknessEngine.calculate_wall_thickness('24"', 'X65', design_pressure_bar=75.0, design_factor_f=0.50, location_type='Station', standard_code='BOTAŞ')
        self.assertEqual(res_botas_24_75['calculation_results']['botas_standard_thickness_mm'], 11.90)
        res_botas_24_825 = WallThicknessEngine.calculate_wall_thickness('24"', 'X65', design_pressure_bar=82.5, design_factor_f=0.50, location_type='Station', standard_code='BOTAŞ')
        self.assertEqual(res_botas_24_825['calculation_results']['botas_standard_thickness_mm'], 12.70)

        # 2. ASME B31.3 Process Piping: 4" SS 316 / 316L P=50 bar
        res_b313 = WallThicknessEngine.calculate_wall_thickness('4"', 'SS 316 / 316L', design_pressure_bar=50.0, standard_code='ASME B31.3')
        self.assertEqual(res_b313['calculation_results']['schedule_standard_used'], 'ASME B36.19M (Paslanmaz Çelik)')
        self.assertEqual(res_b313['calculation_results']['t_required_asme_b31_8_mm'], 2.44)
        self.assertEqual(res_b313['calculation_results']['selected_nominal_thickness_asme_b36_10_mm'], 3.05)

        # 3. ASME B31.8 Pipeline: 24" X70 F=0.60 P=80 bar with SAWH (Table 11 welded: 5<t<15 -> -10%)
        res_b318_sawh = WallThicknessEngine.calculate_wall_thickness(
            '24"', 'X70', design_pressure_bar=80.0, design_factor_f=0.60,
            standard_code='ASME B31.8 / ASME B31.4', manufacturing_process='SAWH'
        )
        self.assertGreater(res_b318_sawh['calculation_results']['t_required_asme_b31_8_mm'], 0)
        self.assertEqual(res_b318_sawh['calculation_results']['tolerance_percent_used'], 10.0)

        # 3b. ASME B31.8 SAWH with explicit 0% tolerance (Must NOT fallback to 8% or Table 11)
        res_b318_0pct = WallThicknessEngine.calculate_wall_thickness(
            '24"', 'X70', design_pressure_bar=80.0, design_factor_f=0.60,
            standard_code='ASME B31.8 / ASME B31.4', manufacturing_process='SAWH',
            manual_negative_tolerance_percent=0.0
        )
        self.assertEqual(res_b318_0pct['calculation_results']['tolerance_percent_used'], 0.0)
        self.assertFalse(res_b318_0pct['input_parameters']['apply_negative_tolerance'])

        # 4. ASME B31.8 Pipeline: 8" X46 F=0.72 P=75 bar with ERW (Table 11 welded: t<=5 -> -0.5 mm)
        res_b318_erw = WallThicknessEngine.calculate_wall_thickness(
            '8"', 'X46', design_pressure_bar=75.0, design_factor_f=0.72,
            standard_code='ASME B31.8 / ASME B31.4', manufacturing_process='ERW HFW'
        )
        # t_req = 7.5*219.1/(2*320*0.72) = 3.57 mm <= 5.0 -> -0.5 mm -> 14.02 %
        self.assertAlmostEqual(res_b318_erw['calculation_results']['tolerance_percent_used'], 14.02, delta=0.01)
        self.assertEqual(res_b318_erw['input_parameters']['material_grade'], 'X46')
        self.assertEqual(res_b318_erw['input_parameters']['smys_mpa'], 320.0)

        # 5. ASME B31.8 Pipeline: 4" Grade B with SMLS (Table 11 SMLS: t<=4 -> -0.5 mm)
        res_b318_smls = WallThicknessEngine.calculate_wall_thickness(
            '4"', 'GRADE B', design_pressure_bar=75.0, design_factor_f=0.50,
            standard_code='ASME B31.8 / ASME B31.4', manufacturing_process='SMLS'
        )
        # t_req = 7.5*114.3/(2*245*0.5) = 3.50 mm <= 4.0 -> -0.5 mm -> 14.29 %
        self.assertAlmostEqual(res_b318_smls['calculation_results']['tolerance_percent_used'], 14.29, delta=0.01)

        # 6. ASME B31.3: 24" X65 P=75 bar (610.0 mm OD) with custom 10% tolerance
        res_b313_24_custom = WallThicknessEngine.calculate_wall_thickness(
            '24"', 'X65', design_pressure_bar=75.0, standard_code='ASME B31.3',
            manual_negative_tolerance_percent=10.0
        )
        self.assertEqual(res_b313_24_custom['calculation_results']['t_required_asme_b31_8_mm'], 7.55)
        self.assertEqual(res_b313_24_custom['calculation_results']['tolerance_percent_used'], 10.0)
        self.assertEqual(res_b313_24_custom['calculation_results']['selected_nominal_thickness_asme_b36_10_mm'], 8.74)
        self.assertAlmostEqual(res_b313_24_custom['calculation_results']['negative_tolerance_min_mm'], 7.87, places=2)

        # 7. BOTAŞ with Custom Corrosion Allowance (c=2.0 mm)
        res_botas_custom = WallThicknessEngine.calculate_wall_thickness(
            '48"', 'X65', design_pressure_bar=75.0, design_factor_f=0.72,
            location_type='Pipeline', standard_code='BOTAŞ',
            corrosion_allowance_mm=2.0
        )
        self.assertEqual(res_botas_custom['calculation_results']['t_theoretical_mm'], 14.11)
        self.assertEqual(res_botas_custom['calculation_results']['corrosion_allowance_mm'], 2.0)
        self.assertEqual(res_botas_custom['calculation_results']['t_required_asme_b31_8_mm'], 16.11)
        self.assertEqual(res_botas_custom['calculation_results']['tolerance_percent_used'], 0.0)
        self.assertEqual(res_botas_custom['calculation_results']['selected_nominal_thickness_asme_b36_10_mm'], 17.48)
        self.assertEqual(res_botas_custom['calculation_results']['negative_tolerance_min_mm'], 17.48)

    def test_10_comprehensive_40_parameter_verification(self):
        """Verifies PipeVerificationEngine evaluates chemical, mechanical, dimensional, weld, and test data."""
        pipe_cfg = {
            'diameter_inch': '48"',
            'diameter_mm': 1219.0,
            'wall_thickness_mm': 14.30,
            'material_grade': 'X65',
            'manufacturing_process': 'SAWH',
            'standard_type': 'BOTAŞ'
        }
        actual_test_data = {
            'C': 0.10,
            'Mn': 1.45,
            'P': 0.012,
            'S': 0.003,
            'Nb': 0.035,
            'V': 0.030,
            'Ti': 0.020,
            'N': 0.006,
            'CE_IIW': 0.38,
            'wall_thickness_actual': 14.35,
            'diameter_end_actual': 1219.2,
            'diameter_body_actual': 1219.5,
            'ovality_end_actual': 3.2,
            'ovality_body_actual': 4.1,
            'pipe_end_peaking_actual': 1.8,
            'pipe_end_squareness_actual': 1.2,
            'yield_strength_actual': 480.0,
            'tensile_strength_actual': 560.0,
            'elongation_actual': 24.5,
            'radial_offset_actual': 0.95,
            'weld_height_inside_actual': 1.8,
            'weld_height_outside_actual': 2.1,
            'misalignment_actual': 1.1,
            'cvn_mat_actual': 85.0,
            'cvn_weld_actual': 65.0,
            'residual_stress_actual': 12.0,
            'hardness_actual': 220.0,
            'weight_actual_kg_m': 425.0,
            'hydro_test_actual_bar': 106.0
        }
        ver_res = PipeVerificationEngine.verify_pipe_test_results(pipe_cfg, actual_test_data)
        self.assertEqual(ver_res['overall_status'], 'ACCEPTED')
        self.assertGreaterEqual(ver_res['passed_count'], 20)
        self.assertEqual(ver_res['failed_count'], 0)
        # Total applicable parameter count is exposed (fixes "0 / 0 Parametre Uygun").
        self.assertGreater(ver_res['total_applicable'], 0)
        self.assertEqual(ver_res['unchecked_count'],
                         ver_res['total_applicable'] - ver_res['checks_count'])

    def test_26_verification_total_applicable(self):
        """Empty verification form -> 0 checks but a non-zero applicable parameter count."""
        from core.verification_engine import PipeVerificationEngine
        cfg = {'diameter_inch': '48"', 'diameter_mm': 1219.0, 'wall_thickness_mm': 14.3,
               'material_grade': 'X65', 'manufacturing_process': 'SAWH', 'standard_type': 'BOTAŞ'}
        # No measurement data entered -> no checks, but the total parameter count is still shown.
        ver = PipeVerificationEngine.verify_pipe_test_results(cfg, {})
        self.assertEqual(ver['checks_count'], 0)
        self.assertGreater(ver['total_applicable'], 20)
        self.assertEqual(ver['unchecked_count'], ver['total_applicable'])
        # PSL1 skips CVN / Y-T / CE -> fewer applicable parameters than the PSL2 equivalent.
        cfg_psl1 = dict(cfg, standard_type='API 5L', psl_level='PSL1')
        ver_psl1 = PipeVerificationEngine.verify_pipe_test_results(cfg_psl1, {})
        cfg_psl2 = dict(cfg, standard_type='API 5L', psl_level='PSL2', delivery_condition='M')
        ver_psl2 = PipeVerificationEngine.verify_pipe_test_results(cfg_psl2, {})
        self.assertLess(ver_psl1['total_applicable'], ver_psl2['total_applicable'])

    def test_27_tensile_dual_rows(self):
        """Welded D>=219.1 mm -> two tensile rows (strip + round bar); otherwise a single row."""
        from core.test_plan import get_test_plan
        # 48" SAWH -> dual rows
        plan = get_test_plan({'diameter_mm': 1219.0, 'wall_thickness_mm': 14.3,
                              'material_grade': 'X65', 'manufacturing_process': 'SAWH'})
        names = [t['test'] for t in plan]
        self.assertIn('Çekme Testi (Şerit)', names)
        self.assertIn('Çekme Testi (Yuvarlak Çubuk)', names)
        strip = next(t for t in plan if t['test'] == 'Çekme Testi (Şerit)')
        rnd = next(t for t in plan if t['test'] == 'Çekme Testi (Yuvarlak Çubuk)')
        self.assertEqual(strip['specimen_figure'], 'tensile_strip')
        self.assertEqual(rnd['specimen_figure'], 'tensile_round')
        # 4" ERW (D<219.1) -> single strip row
        plan4 = get_test_plan({'diameter_mm': 114.3, 'wall_thickness_mm': 6.02,
                               'material_grade': 'X42', 'manufacturing_process': 'ERW HFW'})
        names4 = [t['test'] for t in plan4]
        self.assertIn('Çekme Testi (Tensile)', names4)
        self.assertNotIn('Çekme Testi (Yuvarlak Çubuk)', names4)
        # SMLS t >= 19 mm -> mandatory 12.7 mm round bar
        plan_smls = get_test_plan({'diameter_mm': 508.0, 'wall_thickness_mm': 22.0,
                                   'material_grade': 'X65', 'manufacturing_process': 'SMLS'})
        names_smls = [t['test'] for t in plan_smls]
        self.assertIn('Çekme Testi (Yuvarlak Çubuk)', names_smls)
        self.assertNotIn('Çekme Testi (Şerit)', names_smls)

    def test_28_elongation_dual_values(self):
        """Both elongation minima are exposed when strip and round bar are both permitted."""
        res = PipeQAQCEngine.calculate_pipe_qc('48"', wall_thickness_mm=14.3, material_grade='X65',
                                               manufacturing_process='SAWH', standard_type='API 5L',
                                               psl_level='PSL2', delivery_condition='M')
        tt = res['toughness_and_tests']
        self.assertTrue(tt['tensile_dual_option'])
        # Strip (Axc=485) requires more elongation than the 6.4 mm round bar (Axc=65).
        self.assertGreater(tt['elongation_strip_percent'], tt['elongation_round_percent'])
        # Non-dual pipe: flag is False and the primary value equals the applicable one.
        res4 = PipeQAQCEngine.calculate_pipe_qc('4"', wall_thickness_mm=6.02, material_grade='X42',
                                                manufacturing_process='ERW HFW', standard_type='API 5L',
                                                psl_level='PSL2', delivery_condition='M')
        self.assertFalse(res4['toughness_and_tests']['tensile_dual_option'])

    def test_29_sawh_strip_roundtrip(self):
        """B(alpha) followed by alpha(B) returns the original angle (48\" X65 t=14.3)."""
        from core.sawh_engine import compute_helix_angle, compute_strip_width
        d, t, alpha = 1219.0, 14.3, 55.0
        B = compute_strip_width(d, alpha, t)
        self.assertAlmostEqual(compute_helix_angle(d, B, t), alpha, delta=0.01)
        # B = pi * (D - t) * cos(55)
        self.assertAlmostEqual(B, 3.141592653589793 * (d - t) * 0.573576436, delta=1.0)

    def test_30_sawh_boundaries(self):
        """Boundary conditions: alpha=0 -> pi*D_mid; B=pi*D_mid -> alpha=0; small B -> ~90 deg."""
        from core.sawh_engine import compute_helix_angle, compute_strip_width
        d, t = 1219.0, 14.3
        piD = 3.141592653589793 * (d - t)
        # alpha = 0 -> B = pi * D_mid
        self.assertAlmostEqual(compute_strip_width(d, 0.0, t), piD, delta=1e-6)
        # B = pi * D_mid -> alpha = 0
        self.assertAlmostEqual(compute_helix_angle(d, piD, t), 0.0, delta=1e-6)
        # tiny B -> alpha -> 90 deg
        self.assertAlmostEqual(compute_helix_angle(d, 1.0, t), 90.0, delta=0.05)
        # over-wide B (larger than pi*D_mid) is clamped to alpha = 0
        self.assertAlmostEqual(compute_helix_angle(d, piD * 1.5, t), 0.0, delta=1e-6)

    def test_31_sawh_practical_range(self):
        """Practical SAWH range: alpha in [30,65] -> B in [pi*D_mid*cos65, pi*D_mid*cos30]."""
        from core.sawh_engine import compute_sawh_calc
        d, t = 1219.0, 14.3
        piD = 3.141592653589793 * (d - t)
        res = compute_sawh_calc(d, t)  # default alpha = 55
        self.assertAlmostEqual(res['helix_angle_deg'], 55.0, delta=1e-6)
        self.assertTrue(res['valid'])
        self.assertAlmostEqual(res['b_min_mm'], piD * 0.422618262, delta=1.0)
        self.assertAlmostEqual(res['b_max_mm'], piD * 0.866025404, delta=1.0)
        # at the lower bound (30 deg) valid, beyond (25 deg) invalid
        self.assertTrue(compute_sawh_calc(d, t, helix_angle_deg=30.0)['valid'])
        self.assertFalse(compute_sawh_calc(d, t, helix_angle_deg=25.0)['valid'])

    def test_32_sawh_endpoint(self):
        """POST /api/sawh-strip returns strip width + helix angle + ranges."""
        r = self.client.post('/api/sawh-strip', json={'diameter_mm': 1219.0, 'wall_thickness_mm': 14.3})
        self.assertEqual(r.status_code, 200)
        data = r.json()['data']
        self.assertAlmostEqual(data['helix_angle_deg'], 55.0, delta=1e-6)
        self.assertGreater(data['strip_width_mm'], 0)
        r2 = self.client.post('/api/sawh-strip', json={'diameter_mm': 1219.0, 'wall_thickness_mm': 14.3, 'strip_width_mm': data['strip_width_mm']})
        self.assertEqual(r2.status_code, 200)
        self.assertAlmostEqual(r2.json()['data']['helix_angle_deg'], 55.0, delta=0.5)

    def test_11_unknown_diameter_nameerror_safety(self):
        """P0-1 Regression Test: Ensures unknown diameter does not raise NameError in WallThicknessEngine."""
        res_unknown = WallThicknessEngine.calculate_wall_thickness('999"', 'X65')
        self.assertIsNotNone(res_unknown)
        self.assertGreater(res_unknown['calculation_results']['selected_nominal_thickness_asme_b36_10_mm'], 0)

    def test_12_design_factor_comma_dot_parsing(self):
        """A1 Regression: comma vs dot decimal design factors must parse to the same numeric F."""
        from core.database import parse_design_factor
        self.assertEqual(parse_design_factor('0,6 (Hat)'), ('0.60_hat', 0.60))
        self.assertEqual(parse_design_factor('0.6 (Hat)'), ('0.60_hat', 0.60))
        self.assertEqual(parse_design_factor('0,5 (İst.)'), ('0.50_ist1', 0.50))
        self.assertEqual(parse_design_factor('0,5 (İst. 2)'), ('0.50_ist2', 0.50))
        self.assertEqual(parse_design_factor('0,5 (Hat)'), ('0.50_hat', 0.50))
        self.assertEqual(parse_design_factor('0,72 (Hat)'), ('0.72_hat', 0.72))
        self.assertEqual(parse_design_factor('0,4'), ('0.40_hat', 0.40))
        # End-to-end: a comma factor must yield f=0.6, not 0.72
        r = PipeQAQCEngine.calculate_pipe_qc('48"', wall_thickness_mm=17.5, design_factor_str='0,6 (Hat)', material_grade='X65')
        self.assertEqual(r['input_summary']['design_factor_num'], 0.60)

    def test_13_dual_source_cvn_and_chemistry(self):
        """CVN and chemistry must follow the standard the column was created with."""
        b = PipeQAQCEngine.calculate_pipe_qc('48"', wall_thickness_mm=14.3, material_grade='X65', standard_type='BOTAŞ')
        a = PipeQAQCEngine.calculate_pipe_qc('48"', wall_thickness_mm=14.3, material_grade='X65', standard_type='API 5L')
        # BOTAŞ CVN (from Excel) is stricter than API 5L Table 8 draft
        self.assertEqual(b['toughness_and_tests']['notch_impact_mat_j'], 60.0)
        self.assertEqual(a['toughness_and_tests']['notch_impact_mat_j'], 40.0)
        # Chemistry S limit: BOTAŞ 0.010, API 5L 0.015
        self.assertEqual(b['chemical_analysis']['S_max'], 0.01)
        self.assertEqual(a['chemical_analysis']['S_max'], 0.015)

    def test_14_barlow_constant_precision(self):
        """A2: hydrostatic test uses the correct psi->bar constant (14.5037738)."""
        r = PipeQAQCEngine.calculate_pipe_qc('48"', wall_thickness_mm=14.3, material_grade='X65')
        expected = 2.0 * 65300.0 * 14.3 / (1219.0 * 14.5037738)
        self.assertAlmostEqual(r['hydrostatic_test']['hydro_test_max_bar'], expected, delta=0.01)
        # BOTAŞ minimum test pressure rule: min = max - 2.0 bar
        self.assertAlmostEqual(r['hydrostatic_test']['hydro_test_min_bar'], expected - 2.0, delta=0.01)

    def test_15_test_plan_specimen_info(self):
        """ITP must expose sampling frequency, location, specimen dimensions, clause_ref & figure."""
        from core.test_plan import get_test_plan, VALID_FIGURES
        plan = get_test_plan({'diameter_mm': 1219.0, 'wall_thickness_mm': 14.3, 'material_grade': 'X65', 'manufacturing_process': 'SAWH'})
        names = [t['test'] for t in plan]
        self.assertIn('Çentik Darbe (CVN)', names)
        self.assertIn('DWTT (Drop Weight Tear Test)', names)
        # Every entry must carry the required fields
        for t in plan:
            self.assertTrue(t.get('frequency'))
            self.assertTrue(t.get('location'))
            self.assertTrue(t.get('specimen'))
            # clause_ref (original standard text) must be present & non-empty
            self.assertTrue(t.get('clause_ref'), f"clause_ref missing for {t['test']}")
            # specimen_figure must be None or a valid figure key
            fig = t.get('specimen_figure')
            if fig is not None:
                self.assertIn(fig, VALID_FIGURES, f"invalid specimen_figure {fig} for {t['test']}")
        # Specimen-bearing tests must have a figure; chemical/hydrostatic must not
        for t in plan:
            if t['test'] in ('Kimyasal Analiz (Heat & Product)', 'Hidrostatik Test'):
                self.assertIsNone(t['specimen_figure'])
        # API endpoint
        resp = self.client.post('/api/test-plan', json={'pipe_config': {'diameter_mm': 1219.0, 'wall_thickness_mm': 14.3, 'material_grade': 'X65', 'manufacturing_process': 'SAWH'}})
        self.assertEqual(resp.status_code, 200)
        self.assertGreaterEqual(len(resp.json()['test_plan']), 6)
        for tp in resp.json()['test_plan']:
            self.assertTrue(tp.get('clause_ref'))
            if tp.get('specimen_figure'):
                self.assertIn(tp['specimen_figure'], VALID_FIGURES)

    def test_16_wall_thickness_tolerance_api5l_vs_botas(self):
        """API 5L uses Table 11 negative tolerance; BOTAŞ keeps the Excel formula."""
        b = PipeQAQCEngine.calculate_pipe_qc('18"', wall_thickness_mm=16.66, manufacturing_process='SAWH', material_grade='X65', standard_type='BOTAŞ')
        a = PipeQAQCEngine.calculate_pipe_qc('18"', wall_thickness_mm=16.66, manufacturing_process='SAWH', material_grade='X65', standard_type='API 5L')
        # BOTAŞ: t - 0.15 = 16.51 ; API 5L welded t>=15: t - 1.5 = 15.16
        self.assertEqual(b['wall_thickness_tolerance']['min_mm'], 16.51)
        self.assertEqual(a['wall_thickness_tolerance']['min_mm'], 15.16)
        # Positive tolerance unchanged for both
        self.assertEqual(b['wall_thickness_tolerance']['max_mm'], 18.16)
        self.assertEqual(a['wall_thickness_tolerance']['max_mm'], 18.16)

    def test_17_weld_parameters_api5l_vs_botas(self):
        """API 5L weld seam values are base Table 14/16/9.13.3; BOTAŞ applies 0.75 factor."""
        b = PipeQAQCEngine.calculate_pipe_qc('18"', wall_thickness_mm=16.66, manufacturing_process='SAWH', material_grade='X65', standard_type='BOTAŞ')
        a = PipeQAQCEngine.calculate_pipe_qc('18"', wall_thickness_mm=16.66, manufacturing_process='SAWH', material_grade='X65', standard_type='API 5L')
        self.assertAlmostEqual(b['weld_and_geometry']['radial_offset_max_mm'], 1.25, delta=0.01)
        self.assertAlmostEqual(a['weld_and_geometry']['radial_offset_max_mm'], 1.67, delta=0.01)
        self.assertEqual(b['weld_and_geometry']['weld_height_inside_mm'], 2.62)
        self.assertEqual(a['weld_and_geometry']['weld_height_inside_mm'], 3.5)
        self.assertEqual(a['weld_and_geometry']['misalignment_max_mm'], 3.0)

    def test_18_api5l_diameter_ovality_table10(self):
        """API 5L Table 10 (47th Ed.) diameter & out-of-roundness with welded-pipe caps."""
        from core.database import compute_api5l_tolerances
        # 18" welded: body = ±0.0075D but max ±3.2 -> 460.2 / 453.8
        tol = compute_api5l_tolerances(457.0, 16.66, 'SAWH')
        self.assertAlmostEqual(tol['body_max'], 460.2, delta=0.01)
        self.assertAlmostEqual(tol['body_min'], 453.8, delta=0.01)
        # ovality end = 0.015D = 6.855 ; body = 0.020D = 9.14
        self.assertAlmostEqual(tol['ovality_end'], 0.015 * 457, delta=0.01)
        self.assertAlmostEqual(tol['ovality_body'], 0.020 * 457, delta=0.01)
        # 48" welded: body = ±0.005D max 4.0 -> 1223.0 / 1215.0 (NOT ±0.01D)
        tol48 = compute_api5l_tolerances(1219.0, 14.3, 'SAWH')
        self.assertAlmostEqual(tol48['body_max'], 1223.0, delta=0.01)
        self.assertAlmostEqual(tol48['body_min'], 1215.0, delta=0.01)
        # 48" SMLS: body = ±0.01D -> 1231.19 / 1206.81
        tol48s = compute_api5l_tolerances(1219.0, 14.3, 'SMLS')
        self.assertAlmostEqual(tol48s['body_max'], 1219 * 1.01, delta=0.01)
        self.assertAlmostEqual(tol48s['body_min'], 1219 * 0.99, delta=0.01)

    def test_19_hydrostatic_factor_no_smys_condition(self):
        """Table 26 (47th Ed.): 18in X65 (D<508) standard test = 0.85, capped at 20.5 MPa (205 bar)."""
        a = PipeQAQCEngine.calculate_pipe_qc('18"', wall_thickness_mm=16.66, manufacturing_process='SAWH', material_grade='X65', standard_type='API 5L')
        expected = min(a['hydrostatic_test']['hydro_test_max_bar'] * 0.85, 205.0)
        self.assertAlmostEqual(a['hydrostatic_test']['api_5l_std_test_bar'], expected, delta=0.01)
        # 4" X42 (D <= 141.3) -> 0.60 factor per Table 26
        x42 = PipeQAQCEngine.calculate_pipe_qc('4"', wall_thickness_mm=6.02, manufacturing_process='SAWH', material_grade='X42', standard_type='API 5L')
        self.assertAlmostEqual(x42['hydrostatic_test']['api_5l_std_test_bar'],
                               min(x42['hydrostatic_test']['hydro_test_max_bar'] * 0.60, 205.0), delta=0.01)

    def test_20_pydantic_input_validation(self):
        """Malformed inputs must be rejected with 422 instead of crashing (Pydantic)."""
        # Unknown material grade
        r = self.client.post('/api/calculate', json={'pipes': [{'diameter_inch': '48"', 'material_grade': 'X999'}]})
        self.assertEqual(r.status_code, 422)
        # Negative design pressure
        r2 = self.client.post('/api/calculate', json={'pipes': [{'diameter_inch': '48"', 'material_grade': 'X65', 'design_pressure_bar': -5}]})
        self.assertEqual(r2.status_code, 422)
        # Empty grade (auto-detect in BOTAŞ mode) must be accepted
        r3 = self.client.post('/api/calculate', json={'pipes': [{'diameter_inch': '6"', 'material_grade': '', 'standard_type': 'BOTAŞ'}]})
        self.assertEqual(r3.status_code, 200)
        # Valid API 5L pipe accepted
        r4 = self.client.post('/api/calculate', json={'pipes': [{'diameter_inch': '48"', 'material_grade': 'X65', 'wall_thickness_mm': 14.3, 'standard_type': 'API 5L'}]})
        self.assertEqual(r4.status_code, 200)
        # Invalid delivery condition rejected
        r5 = self.client.post('/api/calculate', json={'pipes': [{'diameter_inch': '48"', 'material_grade': 'X65', 'standard_type': 'API 5L', 'delivery_condition': 'X'}]})
        self.assertEqual(r5.status_code, 422)

    def test_21_psl1_preset_and_psl1_rules(self):
        """PSL 1 pipes: no CVN / Y-T / CE; Table 4 & 6 values; no SAW."""
        preset = ProjectManager.get_10_api_5l_psl1_pipes_preset()
        self.assertEqual(len(preset['pipes']), 10)
        for p in preset['pipes']:
            self.assertNotIn('SAWH', p['manufacturing_process'])
            res = PipeQAQCEngine.calculate_pipe_qc(
                diameter_inch=p['diameter_inch'], wall_thickness_mm=p['wall_thickness_mm'],
                material_grade=p['material_grade'], manufacturing_process=p['manufacturing_process'],
                standard_type='API 5L', psl_level='PSL1')
            # PSL 1: no CE, no Y/T max, no CVN
            self.assertIsNone(res['chemical_analysis']['CE_IIW_max'])
            self.assertEqual(res['mechanical_properties']['yield_to_tensile_ratio_max'], 0.0)
            self.assertFalse(res['toughness_and_tests']['cvn_required'])
            self.assertEqual(res['toughness_and_tests']['dwtt_test'], 'TEST YOK (PSL1)')
            # X70 welded PSL1: C 0.26, Mn 1.65 (Table 4)
        x70 = PipeQAQCEngine.calculate_pipe_qc('36"', wall_thickness_mm=17.48, material_grade='X70',
                                               manufacturing_process='SMLS', standard_type='API 5L', psl_level='PSL1')
        self.assertAlmostEqual(x70['chemical_analysis']['C_max'], 0.28, delta=0.001)  # seamless
        self.assertAlmostEqual(x70['mechanical_properties']['yield_min_mpa'], 485.0, delta=0.01)
        self.assertAlmostEqual(x70['mechanical_properties']['tensile_min_mpa'], 570.0, delta=0.01)

    def test_22_psl2_delivery_chemistry_table5(self):
        """Table 5 (47th Ed.) chemistry depends on delivery condition (R/N/Q/M)."""
        n = PipeQAQCEngine.calculate_pipe_qc('12"', wall_thickness_mm=9.53, material_grade='X52',
                                             manufacturing_process='SMLS', standard_type='API 5L',
                                             psl_level='PSL2', delivery_condition='N')
        m = PipeQAQCEngine.calculate_pipe_qc('12"', wall_thickness_mm=9.53, material_grade='X52',
                                             manufacturing_process='ERW HFW', standard_type='API 5L',
                                             psl_level='PSL2', delivery_condition='M')
        q = PipeQAQCEngine.calculate_pipe_qc('12"', wall_thickness_mm=9.53, material_grade='X52',
                                             manufacturing_process='SMLS', standard_type='API 5L',
                                             psl_level='PSL2', delivery_condition='Q')
        self.assertAlmostEqual(n['chemical_analysis']['C_max'], 0.24, delta=0.001)
        self.assertAlmostEqual(m['chemical_analysis']['C_max'], 0.22, delta=0.001)
        self.assertAlmostEqual(q['chemical_analysis']['C_max'], 0.18, delta=0.001)
        # X65 M: C 0.12, Mn 1.60, CE 0.43/0.25
        x65m = PipeQAQCEngine.calculate_pipe_qc('48"', wall_thickness_mm=14.3, material_grade='X65',
                                                manufacturing_process='SAWH', standard_type='API 5L',
                                                psl_level='PSL2', delivery_condition='M')
        self.assertAlmostEqual(x65m['chemical_analysis']['C_max'], 0.12, delta=0.001)
        self.assertAlmostEqual(x65m['chemical_analysis']['Mn_max'], 1.60, delta=0.001)
        self.assertAlmostEqual(x65m['chemical_analysis']['CE_IIW_max'], 0.43, delta=0.001)
        # Y/T ratio = 0.93 for PSL2 (Table 7)
        self.assertAlmostEqual(x65m['mechanical_properties']['yield_to_tensile_ratio_max'], 0.93, delta=0.001)

    def test_23_chemistry_as_agreed_t_gt_25(self):
        """t > 25.0 mm -> chemistry 'as agreed' (API 5L 9.2.3)."""
        res = PipeQAQCEngine.calculate_pipe_qc('48"', wall_thickness_mm=30.0, material_grade='X65',
                                               manufacturing_process='SAWH', standard_type='API 5L',
                                               psl_level='PSL2', delivery_condition='M')
        self.assertTrue(res['chemical_analysis']['as_agreed'])
        self.assertIsNone(res['chemical_analysis']['C_max'])
        # PSL2 SMLS t > 20 mm -> CE as agreed (Table 5 footnote a)
        res2 = PipeQAQCEngine.calculate_pipe_qc('24"', wall_thickness_mm=22.0, material_grade='X65',
                                                manufacturing_process='SMLS', standard_type='API 5L',
                                                psl_level='PSL2', delivery_condition='Q')
        self.assertFalse(res2['chemical_analysis']['as_agreed'])
        self.assertIsNone(res2['chemical_analysis']['CE_IIW_max'])

    def test_24_carbon_equivalent_calculation(self):
        """CE_IIW and CE_Pcm formulas (API 5L 47th Ed. Eq. 2/3)."""
        from core.database import compute_ce_iww, compute_ce_pcm
        a = {'C': 0.10, 'Si': 0.25, 'Mn': 1.45, 'Cr': 0.05, 'Mo': 0.02, 'V': 0.03,
             'Ni': 0.05, 'Cu': 0.05, 'B': 0.0003}
        # CE_Pcm = 0.10 + 0.25/30 + (1.45+0.05+0.05)/20 + 0.05/60 + 0.02/15 + 0.03/10 + 5*0.0003
        expected_pcm = (0.10 + 0.25/30 + (1.45+0.05+0.05)/20 + 0.05/60 + 0.02/15 + 0.03/10 + 5*0.0003)
        self.assertAlmostEqual(compute_ce_pcm(a), expected_pcm, delta=1e-9)
        # CE_IIW = C + Mn/6 + (Cr+Mo+V)/5 + (Ni+Cu)/15
        expected_iww = 0.10 + 1.45/6 + (0.05+0.02+0.03)/5 + (0.05+0.05)/15
        self.assertAlmostEqual(compute_ce_iww(a), expected_iww, delta=1e-9)

    def test_25_psl1_verification_skips_cvn_yt_ce(self):
        """Verification for PSL 1 must not emit CVN / Y-T / CE checks."""
        from core.verification_engine import PipeVerificationEngine
        cfg = {'diameter_inch': '48"', 'diameter_mm': 1219.0, 'wall_thickness_mm': 14.3,
               'material_grade': 'X65', 'manufacturing_process': 'SAWH', 'standard_type': 'API 5L',
               'psl_level': 'PSL1'}
        data = {'C': 0.10, 'Mn': 1.45, 'yield_strength_actual': 480.0, 'tensile_strength_actual': 560.0,
                'cvn_mat_actual': 45.0, 'cvn_weld_actual': 30.0}
        ver = PipeVerificationEngine.verify_pipe_test_results(cfg, data)
        names = [c['parameter'] for c in ver['checks']]
        self.assertNotIn('Akma/Çekme Oranı (Y/T)', names)
        self.assertNotIn('Çentik Darbe - Gövde (CVN J)', names)
        self.assertNotIn('Karbon Eşdeğeri (CE IIW)', names)

    def test_26_comprehensive_itp_specification_frequencies(self):
        """API 5L 47th Ed. Table 17/18/19/20 comprehensive inspection matrix rules."""
        from core.test_plan import get_comprehensive_itp_specification

        # 48" X65 PSL2 SAWH (Welded D >= 508 mm - API 5L)
        spec_48 = get_comprehensive_itp_specification({
            'diameter_mm': 1219.0, 'diameter_inch': '48"', 'wall_thickness_mm': 14.3,
            'material_grade': 'X65', 'manufacturing_process': 'SAWH', 'psl_level': 'PSL2'
        })
        self.assertEqual(len(spec_48), 21)
        dwtt_48 = next(s for s in spec_48 if s['test_key'] == 'dwtt')
        self.assertTrue(dwtt_48['is_mandatory'])
        self.assertIn("Table 18", dwtt_48['table_ref'])

        hydro_48 = next(s for s in spec_48 if s['test_key'] == 'hydrostatic')
        self.assertIn("10 saniye", hydro_48['standard_acceptance_criteria'])

        # 48" X65 BOTAŞ Specification (BOTAŞ 4-NGTL-0-GN-P-002-5120 R7)
        spec_botas_48 = get_comprehensive_itp_specification({
            'diameter_mm': 1219.0, 'diameter_inch': '48"', 'wall_thickness_mm': 14.3,
            'material_grade': 'X65', 'manufacturing_process': 'SAWH', 'standard_type': 'BOTAŞ'
        })
        self.assertEqual(len(spec_botas_48), 23)
        hydro_botas = next(s for s in spec_botas_48 if s['test_key'] == 'hydrostatic')
        self.assertIn("20 saniye", hydro_botas['standard_acceptance_criteria'])
        cvn_botas = next(s for s in spec_botas_48 if s['test_key'] == 'cvn_body')
        self.assertIn("-20 °C", cvn_botas['standard_acceptance_criteria'])
        self.assertIn("60 J", cvn_botas['standard_acceptance_criteria'])
        res_stress_botas = next(s for s in spec_botas_48 if s['test_key'] == 'residual_stress')
        self.assertTrue(res_stress_botas['is_mandatory'])
        self.assertIn("BOTAŞ", res_stress_botas['clause_ref'])

        # 12" X52 PSL2 SMLS (Seamless D < 508 mm)
        spec_12_smls = get_comprehensive_itp_specification({
            'diameter_mm': 323.9, 'diameter_inch': '12"', 'wall_thickness_mm': 9.53,
            'material_grade': 'X52', 'manufacturing_process': 'SMLS', 'psl_level': 'PSL2'
        })
        self.assertFalse(any(s['test_key'] == 'dwtt' for s in spec_12_smls))
        hydro_12 = next(s for s in spec_12_smls if s['test_key'] == 'hydrostatic')
        self.assertIn("5 saniye", hydro_12['standard_acceptance_criteria'])

    def test_27_unlimited_ocr_parser_fallback(self):
        """UnlimitedOCREngine parses text and produces standardized ITP dictionary items."""
        from core.unlimited_ocr_engine import UnlimitedOCREngine

        sample_text = (
            "KIMYASAL ANALIZ DOKUM: Isı başına 1 analiz, C max 0.16%, P max 0.020%\n"
            "GOVDE CEKME TESTI: Her test unitesi basina 1 set, Rt0.5 >= 450 MPa\n"
            "HIDROSTATIK TEST: Her boru 100%, Min 110 bar, 10 saniye tutma\n"
            "DWTT DENEYI: Isı başına 1 test, Ortalama sünek kırılma >= 85%"
        )
        parsed = UnlimitedOCREngine._parse_text_into_itp_rows(sample_text)
        self.assertGreaterEqual(len(parsed), 3)

        fallback = UnlimitedOCREngine._heuristic_extract_fallback("demo")
        self.assertGreaterEqual(len(fallback), 10)
        self.assertTrue(any(it['test_name'].startswith('Fabrika Hidrostatik') for it in fallback))

    def test_28_itp_audit_engine_compliance_and_discrepancies(self):
        """ITPAuditEngine audits manufacturer ITP items against API 5L 47th Ed. limits."""
        from core.itp_audit_engine import ITPAuditEngine

        pipe_cfg = {
            'diameter_mm': 1219.0, 'diameter_inch': '48"', 'wall_thickness_mm': 14.3,
            'material_grade': 'X65', 'manufacturing_process': 'SAWH', 'psl_level': 'PSL2'
        }

        # 1. Non-compliant: 5 seconds hydro holding time instead of 10s & insufficient CVN energy (27 J instead of 40 J)
        flawed_items = [
            {
                'test_name': 'Fabrika Hidrostatik Basınç Testi',
                'test_frequency': 'Her boru (%100)',
                'acceptance_criteria': 'Min 100 bar, 5 saniye tutma süresi'
            },
            {
                'test_name': 'Gövde Çentik Darbe Testi (CVN Body)',
                'test_frequency': 'Lot başına 1 set',
                'acceptance_criteria': 'Min Ort. 27 J (0 °C)'
            }
        ]
        audit_res = ITPAuditEngine.audit_itp(flawed_items, pipe_cfg)
        self.assertGreater(audit_res['kpi']['non_compliant_count'], 0)
        self.assertEqual(audit_res['kpi']['overall_verdict'], 'REJECTED')
        
        # Verify specific critical findings
        findings_msgs = [f['message'] for f in audit_res['findings']]
        self.assertTrue(any("YETERSİZ TEST SÜRESİ" in m for m in findings_msgs))
        self.assertTrue(any("YETERSİZ DARBE ENERJİSİ" in m for m in findings_msgs))

    def test_29_itp_excel_report_export(self):
        """ExcelExporter.export_itp_audit_report creates a valid Excel spreadsheet."""
        from core.excel_exporter import ExcelExporter
        from core.itp_audit_engine import ITPAuditEngine
        from core.unlimited_ocr_engine import UnlimitedOCREngine

        pipe_cfg = {
            'diameter_mm': 1219.0, 'diameter_inch': '48"', 'wall_thickness_mm': 14.3,
            'material_grade': 'X65', 'manufacturing_process': 'SAWH', 'psl_level': 'PSL2'
        }
        demo_items = UnlimitedOCREngine._heuristic_extract_fallback("demo")
        audit_res = ITPAuditEngine.audit_itp(demo_items, pipe_cfg)

        stream = ExcelExporter.export_itp_audit_report(audit_res, lang='tr')
        self.assertGreater(len(stream.getvalue()), 1000)

    def test_30_itp_fastapi_endpoints(self):
        """FastAPI endpoints for ITP upload, manual audit, reference frequencies, and export."""
        # 1. Reference Frequencies GET
        r_freq = self.client.get('/api/itp/reference-frequencies?diameter_mm=1219.0&material_grade=X65&psl_level=PSL2')
        self.assertEqual(r_freq.status_code, 200)
        self.assertGreaterEqual(len(r_freq.json()['master_specification']), 20)

        # 2. Upload & Audit POST (Demo Mode)
        r_demo = self.client.post('/api/itp/upload-and-audit', data={'use_demo': 'true'})
        self.assertEqual(r_demo.status_code, 200)
        res_data = r_demo.json()
        self.assertEqual(res_data['status'], 'success')
        self.assertIn('audit_result', res_data)

        # 3. Export Audit Report POST
        audit_res = res_data['audit_result']
        r_exp = self.client.post('/api/itp/export-audit-report', json={'audit_result': audit_res, 'lang': 'tr'})
        self.assertEqual(r_exp.status_code, 200)
        self.assertIn('application/vnd.openxmlformats-officedocument.spreadsheetml.sheet', r_exp.headers['content-type'])

    def test_31_botas_and_asme_negative_tolerance_zero_percent(self):
        """Ensures BOTAŞ does not apply double tolerance and ASME strictly respects 0% tolerance without falling back to 8%."""
        # 1. BOTAŞ Standard calculation -> tolerance must be strictly 0%
        res_botas = WallThicknessEngine.calculate_wall_thickness(
            '48"', 'X65', design_pressure_bar=75.0, design_factor_f=0.72,
            location_type='Pipeline', standard_code='BOTAŞ'
        )
        self.assertEqual(res_botas['calculation_results']['tolerance_percent_used'], 0.0)
        self.assertFalse(res_botas['input_parameters']['apply_negative_tolerance'])
        self.assertIn("BOTAŞ Şartnamesi Standart Et Kalınlığı Matrisi", res_botas['calculation_results']['tolerance_rule_description'])

        # 2. ASME B31.8 SAWH D > 20" with explicit manual_negative_tolerance_percent = 0.0
        res_asme_0 = WallThicknessEngine.calculate_wall_thickness(
            '48"', 'X65', design_pressure_bar=75.0, design_factor_f=0.72,
            standard_code='ASME B31.8 / ASME B31.4', manufacturing_process='SAWH',
            manual_negative_tolerance_percent=0.0
        )
        self.assertEqual(res_asme_0['calculation_results']['tolerance_percent_used'], 0.0)
        self.assertFalse(res_asme_0['input_parameters']['apply_negative_tolerance'])
        self.assertEqual(res_asme_0['calculation_results']['selected_nominal_thickness_asme_b36_10_mm'], 14.27)

        # 3. ASME B31.8 SAWH D > 20" with manual_negative_tolerance_percent = 8.0
        res_asme_8 = WallThicknessEngine.calculate_wall_thickness(
            '48"', 'X65', design_pressure_bar=75.0, design_factor_f=0.72,
            standard_code='ASME B31.8 / ASME B31.4', manufacturing_process='SAWH',
            manual_negative_tolerance_percent=8.0
        )
        self.assertEqual(res_asme_8['calculation_results']['tolerance_percent_used'], 8.0)
        self.assertTrue(res_asme_8['input_parameters']['apply_negative_tolerance'])
        self.assertEqual(res_asme_8['calculation_results']['selected_nominal_thickness_asme_b36_10_mm'], 15.88)

        # 4. API endpoint /api/wall-thickness with 0% tolerance
        r_api = self.client.post('/api/wall-thickness', json={
            'diameter_inch': '48"',
            'material_grade': 'X65',
            'standard_code': 'ASME B31.8 / ASME B31.4',
            'manufacturing_process': 'SAWH',
            'manual_negative_tolerance_percent': 0.0,
            'design_pressure_bar': 75.0,
            'design_factor_f': 0.72,
            'longitudinal_joint_factor_e': 1.0,
            'temperature_derating_factor_t': 1.0
        })
        self.assertEqual(r_api.status_code, 200)
        self.assertEqual(r_api.json()['data']['calculation_results']['tolerance_percent_used'], 0.0)

    def test_32_botas_itp_audit_frequencies_and_criteria(self):
        """ITPAuditEngine properly evaluates BOTAŞ-specific specifications (20s hydro, -20C CVN, residual stress)."""
        from core.itp_audit_engine import ITPAuditEngine

        botas_cfg = {
            'diameter_mm': 1219.0, 'diameter_inch': '48"', 'wall_thickness_mm': 14.3,
            'material_grade': 'X65', 'manufacturing_process': 'SAWH', 'standard_type': 'BOTAŞ'
        }

        # 1. Test with 10s hydro (Passes API 5L, but Fails BOTAŞ 20s requirement)
        itp_items = [
            {
                'test_name': 'Fabrika Hidrostatik Basınç Testi',
                'test_frequency': 'Her boru (%100)',
                'acceptance_criteria': 'Min 110 bar, 10 saniye tutma süresi'
            },
            {
                'test_name': 'Gövde Çentik Darbe Testi',
                'test_frequency': 'Lot başına 1 set',
                'acceptance_criteria': 'Min Ort. 45 J (-20 °C)'
            }
        ]
        audit_res = ITPAuditEngine.audit_itp(itp_items, botas_cfg)
        self.assertEqual(audit_res['kpi']['overall_verdict'], 'REJECTED')
        findings_msgs = [f['message'] for f in audit_res['findings']]
        self.assertTrue(any("20 SANİYE" in m for m in findings_msgs))
        self.assertTrue(any("60 J" in m for m in findings_msgs))

        # Check missing mandatory residual stress test
        self.assertTrue(any(f['issue_type'] == 'MISSING_MANDATORY_TEST' and 'Artık Stres' in f['test_name'] for f in audit_res['findings']))

    def test_33_dynamic_pipe_column_itp_audit_calculations(self):
        """Verifies that all 40+ pipe column outputs are populated with calculated targets and checked."""
        from core.test_plan import get_comprehensive_itp_specification
        from core.itp_audit_engine import ITPAuditEngine

        cfg = {
            'diameter_mm': 1219.0, 'diameter_inch': '48"', 'wall_thickness_mm': 14.30,
            'material_grade': 'X65', 'manufacturing_process': 'SAWH', 'standard_type': 'BOTAŞ',
            'psl_level': 'PSL2'
        }

        master_items = get_comprehensive_itp_specification(cfg)
        self.assertGreaterEqual(len(master_items), 22)

        # Check specific calculated targets
        keys_found = {it['test_key']: it for it in master_items}
        self.assertIn('guided_bend', keys_found)
        self.assertIn('dimensional_weight', keys_found)
        self.assertIn('weld_repair_rules', keys_found)
        self.assertIn('weld_geometry_offset_height', keys_found)
        self.assertIn('ndt_weld_seam', keys_found)

        # Mandrel & Jaw
        gb = keys_found['guided_bend']
        self.assertIn('mandrel_dia_mm', gb['calculated_targets'])
        self.assertIn('jaw_opening_mm', gb['calculated_targets'])

        # Weight
        wt = keys_found['dimensional_weight']
        self.assertAlmostEqual(wt['calculated_targets']['nominal_kg_m'], 424.87, delta=1.0)

        # Audit with insufficient hydrostatic pressure and body repair permission
        bad_items = [
            {
                'test_name': 'Fabrika Hidrostatik Basınç Testi',
                'test_frequency': 'Her boru (%100)',
                'acceptance_criteria': 'Min 80.0 bar, 20 saniye'
            },
            {
                'test_name': 'Kaynak ve Gövde Tamir Kuralları',
                'test_frequency': 'Tamir oldukça',
                'acceptance_criteria': 'Gövde tamiri serbesttir'
            }
        ]
        audit_res = ITPAuditEngine.audit_itp(bad_items, cfg)
        self.assertEqual(audit_res['kpi']['overall_verdict'], 'REJECTED')
        msgs = [f['message'] for f in audit_res['findings']]
        self.assertTrue(any("DÜŞÜK HİDROSTATİK BASINÇ" in m for m in msgs))
        self.assertTrue(any("GÖVDE TAMİRİ YASAKTIR" in m for m in msgs))

    def test_34_sample_itps_ocr_and_audit_all_clean(self):
        """Verifies that all 12 generated authentic ITP PDFs in itp_sample_library can be read and audited."""
        import os
        from core.unlimited_ocr_engine import UnlimitedOCREngine
        from core.itp_audit_engine import ITPAuditEngine

        lib_dir = os.path.join(os.path.dirname(__file__), '..', 'itp_sample_library')
        if not os.path.exists(lib_dir):
            return

        pdf_files = [f for f in os.listdir(lib_dir) if f.endswith('.pdf')]
        self.assertEqual(len(pdf_files), 12)

        botas_cfg = {
            'diameter_mm': 1219.0, 'diameter_inch': '48"', 'wall_thickness_mm': 14.30,
            'material_grade': 'X65', 'manufacturing_process': 'SAWH', 'standard_type': 'BOTAŞ',
            'psl_level': 'PSL2'
        }

        for pdf in pdf_files:
            pdf_path = os.path.join(lib_dir, pdf)
            with open(pdf_path, 'rb') as f:
                content = f.read()
            parse_res = UnlimitedOCREngine.parse_pdf_or_image(content, pdf)
            self.assertEqual(parse_res['status'], 'success')
            parsed_items = parse_res['items']
            self.assertGreater(len(parsed_items), 5)

            audit_res = ITPAuditEngine.audit_itp(parsed_items, botas_cfg)
            self.assertIn('kpi', audit_res)
            self.assertIn('compliance_score_percent', audit_res['kpi'])

    def test_35_bipartite_matcher_and_comprehensive_criteria_rules(self):
        """Verifies maximum-weight bipartite matcher and comprehensive criteria evaluation across all disciplines."""
        from core.itp_audit_engine import ITPAuditEngine

        cfg = {
            'diameter_mm': 1219.0, 'diameter_inch': '48"', 'wall_thickness_mm': 14.30,
            'material_grade': 'X65', 'manufacturing_process': 'SAWH', 'standard_type': 'BOTAŞ',
            'psl_level': 'PSL2'
        }

        # Items with multiple deliberate criteria violations:
        # - DWTT shear area only 70% (< 85%)
        # - Yield Rt0.5 420 MPa (< 450 MPa)
        # - Y/T ratio 0.95 (> 0.90)
        # - High Carbon 0.18% (> 0.12%)
        # - Body lamination only 20% scan (< 40%)
        # - Preheat omitted for t=14.3mm
        flawed_itp = [
            {
                'test_name': 'DWTT (Düşen Ağırlık Yırtılma Testi)',
                'test_frequency': 'Isı başına 1 test',
                'acceptance_criteria': 'Ortalama sünek kırılma alanı min %70 (0 °C)'
            },
            {
                'test_name': 'Gövde Çekme Testi (Body Tensile)',
                'test_frequency': 'Lot başına 1 set',
                'acceptance_criteria': 'Rt0.5 >= 420 MPa, Y/T <= 0.95'
            },
            {
                'test_name': 'Döküm Analizi (Heat Chemical)',
                'test_frequency': 'Her dökümde 1 analiz',
                'acceptance_criteria': 'C <= 0.18%, P <= 0.030%, S <= 0.015%'
            },
            {
                'test_name': 'Boru Gövdesi UT Laminasyon',
                'test_frequency': 'Boru gövde yüzeyi',
                'acceptance_criteria': 'Gövde yüzeyinin %20 si taranacak'
            },
            {
                'test_name': 'Kaynak ve Gövde Tamir Kuralları',
                'test_frequency': 'Tamir oldukça',
                'acceptance_criteria': 'Ön ısıtmasız kaynak tamiri yapılabilir, tek tamir 250 mm'
            }
        ]

        audit_res = ITPAuditEngine.audit_itp(flawed_itp, cfg)
        self.assertEqual(audit_res['kpi']['overall_verdict'], 'REJECTED')
        msgs = [f['message'] for f in audit_res['findings']]

        self.assertTrue(any("YETERSİZ DWTT SÜNEK KIRILMA" in m for m in msgs))
        self.assertTrue(any("DÜŞÜK AKMA MUKAVEMETİ" in m for m in msgs))
        self.assertTrue(any("YÜKSEK Y/T ORANI" in m for m in msgs))
        self.assertTrue(any("YÜKSEK KARBON LİMİTİ" in m for m in msgs))
        self.assertTrue(any("YETERSİZ GÖVDE TARAMA ORANI" in m for m in msgs))
        self.assertTrue(any("ÖN ISITMA ZORUNLU" in m for m in msgs))

    def test_36_upload_validation_and_fallback_warning(self):
        """Verifies file validation, MIME check, and fallback warning on empty/non-table PDF."""
        from core.unlimited_ocr_engine import UnlimitedOCREngine

        # 1. Non-table blank payload triggers warning and is_fallback: True
        blank_pdf_bytes = b"%PDF-1.4\n%EOF\n"
        parse_res = UnlimitedOCREngine.parse_pdf_or_image(blank_pdf_bytes, "empty.pdf")
        self.assertEqual(parse_res['status'], 'warning')
        self.assertTrue(parse_res['is_fallback'])
        self.assertIn("DİKKAT", parse_res['warning_message'])

        # 2. Upload endpoint rejects invalid extensions
        r_bad_ext = self.client.post(
            '/api/itp/upload-and-audit',
            files={'file': ('document.exe', b'bad content', 'application/octet-stream')}
        )
        self.assertEqual(r_bad_ext.status_code, 400)
        self.assertIn("Geçersiz dosya formatı", r_bad_ext.json()['message'])


    def test_37_granular_negative_audit_scenarios_proof(self):
        """Verifies all granular negative branches: repair > 150mm, weight +15%, weld height > 2.625mm, hardness > 300HV, residual stress > 45MPa, and NDT level."""
        from core.itp_audit_engine import ITPAuditEngine, FrequencyNormalizer, FrequencyCanonical

        # 1. FrequencyNormalizer Tests
        self.assertEqual(FrequencyNormalizer.normalize("İstisnasız her boruda (%100)"), FrequencyCanonical.EVERY_PIPE_100)
        self.assertEqual(FrequencyNormalizer.normalize("Her dökümde (per heat) 1 analiz"), FrequencyCanonical.PER_HEAT)
        self.assertEqual(FrequencyNormalizer.normalize("1 per 5 heats sample"), FrequencyCanonical.INADEQUATE_SAMPLING)
        self.assertEqual(FrequencyNormalizer.normalize("10 boruda 1 adet numune"), FrequencyCanonical.INADEQUATE_SAMPLING)
        self.assertEqual(FrequencyNormalizer.normalize("Vardiyada 2 kez ölçüm"), FrequencyCanonical.PERIODIC_SHIFT)

        botas_cfg = {
            'diameter_mm': 1219.0, 'diameter_inch': '48"', 'wall_thickness_mm': 14.30,
            'material_grade': 'X65', 'manufacturing_process': 'SAWH', 'standard_type': 'BOTAŞ',
            'psl_level': 'PSL2'
        }

        negative_items = [
            {
                'test_name': 'Kaynak ve Gövde Tamir Kuralları',
                'test_frequency': 'Tamir oldukça',
                'acceptance_criteria': 'Tek tamir boyu azami 250 mm tamir yapılabilir'
            },
            {
                'test_name': 'Boru Birim Ağırlığı ve Toleransı',
                'test_frequency': 'Her boruda (%100)',
                'acceptance_criteria': 'Birim ağırlık toleransı -%5.0 / +%15.0'
            },
            {
                'test_name': 'Kaynak Geometrisi ve Kaçıklık',
                'test_frequency': 'Her boruda',
                'acceptance_criteria': 'Kaynak dikiş yüksekliği azami 3.5 mm'
            },
            {
                'test_name': 'Sertlik Testi (Hardness)',
                'test_frequency': 'Lot başına 1 adet',
                'acceptance_criteria': 'Azami 340 HV10 sertlik'
            },
            {
                'test_name': 'Artık Stres Testi (Residual Stress)',
                'test_frequency': 'Her dökümde 1 test',
                'acceptance_criteria': 'Azami artık stres 58.0 MPa'
            },
            {
                'test_name': 'Kaynak Dikişi %100 NDT',
                'test_frequency': 'Her boruda %100',
                'acceptance_criteria': 'AUT Seviye U3 ve Class A film çekimi'
            }
        ]

        audit_res = ITPAuditEngine.audit_itp(negative_items, botas_cfg)
        self.assertEqual(audit_res['kpi']['overall_verdict'], 'REJECTED')
        msgs = [f['message'] for f in audit_res['findings']]

        self.assertTrue(any("TAMİR BOY LİMİTİ AŞILDI" in m for m in msgs))
        self.assertTrue(any("AĞIRLIK TOLERANSI AŞILDI" in m for m in msgs))
        self.assertTrue(any("KAYNAK YÜKSEKLİK LİMİTİ" in m for m in msgs))
        self.assertTrue(any("YÜKSEK SERTLİK LİMİTİ" in m for m in msgs))
        self.assertTrue(any("ARTIK GERİLME LİMİTİ AŞILDI" in m for m in msgs))
        self.assertTrue(any("YETERSİZ NDT KABUL SEVİYESİ" in m for m in msgs))


if __name__ == '__main__':
    unittest.main()




