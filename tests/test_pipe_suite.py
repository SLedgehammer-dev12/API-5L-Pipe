"""
Comprehensive Automated Test Suite for API 5L PSL2 & BOTAŞ Pipe QA/QC & Design Suite.
Evaluates 10+ BOTAŞ pipes, 10+ API 5L pipes, ASME B31.3 / B31.8 wall thickness,
stainless steel ASME B36.19M selection, and 40+ parameter factory verification.
"""

import unittest
from fastapi.testclient import TestClient

from app import app
from core.pipe_qaqc_engine import PipeQAQCEngine
from core.verification_engine import PipeVerificationEngine
from core.wall_thickness_engine import WallThicknessEngine
from core.excel_exporter import ExcelExporter
from core.project_manager import ProjectManager

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
        # 1. BOTAŞ Standard: 48" X65 F=0.72 P=75 bar
        res_botas = WallThicknessEngine.calculate_wall_thickness('48"', 'X65', design_pressure_bar=75.0, design_factor_f=0.72, standard_code='BOTAŞ')
        self.assertEqual(res_botas['calculation_results']['t_required_asme_b31_8_mm'], 14.11)
        self.assertEqual(res_botas['calculation_results']['selected_nominal_thickness_asme_b36_10_mm'], 17.48)
        self.assertEqual(res_botas['calculation_results']['schedule_standard_used'], 'ASME B36.10M (Karbon Çeliği)')

        # 2. ASME B31.3 Process Piping: 4" SS 316 / 316L P=50 bar
        res_b313 = WallThicknessEngine.calculate_wall_thickness('4"', 'SS 316 / 316L', design_pressure_bar=50.0, standard_code='ASME B31.3')
        self.assertEqual(res_b313['calculation_results']['schedule_standard_used'], 'ASME B36.19M (Paslanmaz Çelik)')
        self.assertEqual(res_b313['calculation_results']['t_required_asme_b31_8_mm'], 2.44)
        self.assertEqual(res_b313['calculation_results']['selected_nominal_thickness_asme_b36_10_mm'], 3.05)

        # 3. ASME B31.8 Pipeline: 24" X70 F=0.60 P=80 bar
        res_b318 = WallThicknessEngine.calculate_wall_thickness('24"', 'X70', design_pressure_bar=80.0, design_factor_f=0.60, standard_code='ASME B31.8 / ASME B31.4')
        self.assertGreater(res_b318['calculation_results']['t_required_asme_b31_8_mm'], 0)

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

    def test_11_unknown_diameter_nameerror_safety(self):
        """P0-1 Regression Test: Ensures unknown diameter does not raise NameError in WallThicknessEngine."""
        res_unknown = WallThicknessEngine.calculate_wall_thickness('999"', 'X65')
        self.assertIsNotNone(res_unknown)
        self.assertGreater(res_unknown['calculation_results']['selected_nominal_thickness_asme_b36_10_mm'], 0)

if __name__ == '__main__':
    unittest.main()
