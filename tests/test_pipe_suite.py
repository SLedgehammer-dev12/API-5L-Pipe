"""
Comprehensive Automated Test Suite for API 5L PSL2 & BOTAŞ Pipe QA/QC & Design Suite.
Evaluates 10+ BOTAŞ pipes and 10+ API 5L pipes, verifying formulas, nominal diameter mappings,
engineering explanations, and specification compliance.
"""

import unittest
from fastapi.testclient import TestClient

from app import app
from core.pipe_qaqc_engine import PipeQAQCEngine, STANDARD_EXPLANATIONS
from core.verification_engine import PipeVerificationEngine
from core.wall_thickness_engine import WallThicknessEngine
from core.excel_exporter import ExcelExporter
from core.project_manager import ProjectManager
from core.database import API_5L_SMYS_TABLE, PIPE_SIZES_TABLE

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
        """
        Evaluates 10 distinct BOTAŞ standard pipes from preset:
        1/2", 2", 4", 6", 8", 12", 16", 24", 36", 48"
        Verifies material grades and wall thicknesses match BOTAŞ tables and formulas.
        """
        botas_preset = ProjectManager.get_10_botas_pipes_preset()
        self.assertEqual(len(botas_preset['pipes']), 10)

        for p in botas_preset['pipes']:
            res = PipeQAQCEngine.calculate_pipe_qc(
                diameter_inch=p['diameter_inch'],
                diameter_mm=p['diameter_mm'],
                wall_thickness_mm=p['wall_thickness_mm'],
                design_factor_str=p['design_factor_str'],
                material_grade=p['material_grade'],
                manufacturing_process=p['manufacturing_process'],
                standard_type='BOTAŞ'
            )

            # Check BOTAŞ compliance
            self.assertEqual(res['input_summary']['botas_thickness_status'], 'UYGUN')
            
            # Check basic physics and pressure rules
            self.assertGreater(res['hydrostatic_test']['hydro_test_max_bar'], 0)
            self.assertGreater(res['hydrostatic_test']['hydro_test_min_bar'], 0)
            self.assertGreater(res['toughness_and_tests']['elongation_mat_min_percent'], 15.0)

            # Check DWTT rule
            if res['input_summary']['diameter_mm'] >= 508.0:
                self.assertEqual(res['toughness_and_tests']['dwtt_test'], 'Var')
            else:
                self.assertEqual(res['toughness_and_tests']['dwtt_test'], 'TEST YOK')

            # Check residual stress on SAWH pipes
            if 'SAWH' in res['input_summary']['manufacturing_process']:
                self.assertIsInstance(res['toughness_and_tests']['residual_stress_max_mm'], float)
                self.assertGreater(res['toughness_and_tests']['residual_stress_max_mm'], 0)

    def test_03_ten_api_5l_pipes_preset_evaluation(self):
        """
        Evaluates 10 distinct API 5L PSL2 pipes from preset:
        2" Gr.B, 4" X42, 6" X52, 8" X56, 12" X60, 18" X65, 24" X65, 30" X70, 36" X70, 48" X80.
        Verifies API 5L formulas, standard test factors and mechanical limits.
        """
        api_preset = ProjectManager.get_10_api_5l_pipes_preset()
        self.assertEqual(len(api_preset['pipes']), 10)

        for p in api_preset['pipes']:
            res = PipeQAQCEngine.calculate_pipe_qc(
                diameter_inch=p['diameter_inch'],
                diameter_mm=p['diameter_mm'],
                wall_thickness_mm=p['wall_thickness_mm'],
                design_factor_str=p['design_factor_str'],
                material_grade=p['material_grade'],
                manufacturing_process=p['manufacturing_process'],
                standard_type='API 5L'
            )

            # Check SMYS matches Grade
            self.assertIn(p['material_grade'], API_5L_SMYS_TABLE)
            self.assertEqual(res['mechanical_properties']['smys_psi'], API_5L_SMYS_TABLE[p['material_grade']]['smys_psi'])

            # Verify API standard test pressure factor
            p_max = res['hydrostatic_test']['hydro_test_max_bar']
            p_std = res['hydrostatic_test']['api_5l_std_test_bar']
            self.assertLessEqual(p_std, p_max)

    def test_04_engineering_remarks_and_standard_explanations(self):
        """Verifies that engineering explanations and standard references exist for every row."""
        res = PipeQAQCEngine.calculate_pipe_qc(diameter_inch='48"', wall_thickness_mm=14.30, material_grade='X65')
        self.assertIn('explanations', res)
        exp = res['explanations']

        # Key required standard references
        self.assertIn('diameter', exp)
        self.assertIn('hydro_test', exp)
        self.assertIn('residual_stress', exp)
        self.assertIn('elongation', exp)
        self.assertIn('dwtt', exp)
        self.assertIn('weld_repair', exp)

        # Check Turkish and English text presence
        self.assertIn('tr', exp['hydro_test'])
        self.assertIn('en', exp['hydro_test'])
        self.assertIn('Barlow', exp['hydro_test']['tr'])

    def test_05_botas_lookup_api_endpoint(self):
        """Tests the /api/botas-lookup endpoint for automatic form filling."""
        # Test 1: 48" F=0.72 Hat -> X65, 14.30 mm
        r1 = self.client.get('/api/botas-lookup?diameter_inch=48"&factor=0,72 (Hat)')
        self.assertEqual(r1.status_code, 200)
        d1 = r1.json()
        self.assertEqual(d1['material'], 'X65')
        self.assertEqual(d1['thickness'], 14.30)

        # Test 2: 12" F=0.72 Hat -> X52, 5.20 mm
        r2 = self.client.get('/api/botas-lookup?diameter_inch=12"&factor=0,72 (Hat)')
        self.assertEqual(r2.status_code, 200)
        d2 = r2.json()
        self.assertEqual(d2['material'], 'X52')
        self.assertEqual(d2['thickness'], 5.20)

        # Test 3: 4" F=0.50 İst. -> GRADE B, 6.00 mm
        r3 = self.client.get('/api/botas-lookup?diameter_inch=4"&factor=0,5 (İst.)')
        self.assertEqual(r3.status_code, 200)
        d3 = r3.json()
        self.assertEqual(d3['material'], 'GRADE B')
        self.assertEqual(d3['thickness'], 6.00)

    def test_06_excel_export_with_10_botas_and_10_api5l(self):
        """Tests Excel exporter with both 10 BOTAŞ and 10 API 5L datasets."""
        # 1. BOTAŞ 10 Pipes Excel Export
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

        # 2. API 5L 10 Pipes Excel Export
        p_api = ProjectManager.get_10_api_5l_pipes_preset()
        calc_api = [PipeQAQCEngine.calculate_pipe_qc(
            diameter_inch=p['diameter_inch'],
            wall_thickness_mm=p['wall_thickness_mm'],
            material_grade=p['material_grade'],
            design_factor_str=p['design_factor_str'],
            manufacturing_process=p['manufacturing_process'],
            standard_type='API 5L'
        ) for p in p_api['pipes']]

        s_api = ExcelExporter.export_matrix_to_excel(p_api['project_info'], calc_api)
        self.assertGreater(len(s_api.getvalue()), 8000)

    def test_07_check_update_endpoint_and_semver_logic(self):
        """Verifies /api/check-update endpoint and semver comparison."""
        from core.updater import is_newer_version, parse_semver
        
        # Test semver parser
        self.assertEqual(parse_semver('v1.0.3'), (1, 0, 3))
        self.assertEqual(parse_semver('2.1.0-beta'), (2, 1, 0))
        
        # Test newer version comparator
        self.assertTrue(is_newer_version('1.0.3', '1.0.4'))
        self.assertTrue(is_newer_version('1.0.3', '1.1.0'))
        self.assertTrue(is_newer_version('1.0.3', '2.0.0'))
        self.assertFalse(is_newer_version('1.0.3', '1.0.3'))
        self.assertFalse(is_newer_version('1.0.3', '1.0.2'))
        
        # Test API endpoint
        resp = self.client.get('/api/check-update')
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertIn('current_version', data)
        self.assertIn('latest_version', data)
        self.assertIn('update_available', data)
        self.assertIn('download_assets', data)

    def test_08_backward_compatibility_project_migration(self):
        """Verifies that projects created in older versions (v1.0.0, v1.0.1) can be cleanly loaded and evaluated."""
        # Simulated raw project from v1.0.0 with missing fields
        old_project = {
            "project_info": {
                "project_name": "Eski Proje v1.0.0",
                "revision": "Rev. A"
            },
            "pipes": [
                {
                    "diameter_inch": "48\"",
                    "wall_thickness_mm": 14.30,
                    "material_grade": "X65"
                    # missing standard_type, design_pressure_bar, manufacturing_process, id
                }
            ]
        }

        # Calculate using the QA/QC Engine with fallback defaults
        pipe = old_project['pipes'][0]
        res = PipeQAQCEngine.calculate_pipe_qc(
            diameter_inch=pipe.get('diameter_inch', '48"'),
            wall_thickness_mm=pipe.get('wall_thickness_mm', 14.30),
            material_grade=pipe.get('material_grade', 'X65'),
            design_factor_str=pipe.get('design_factor_str', '0,72 (Hat)'),
            manufacturing_process=pipe.get('manufacturing_process', 'SAWH'),
            standard_type=pipe.get('standard_type', 'BOTAŞ')
        )
        self.assertIsNotNone(res)
        self.assertEqual(res['input_summary']['material_grade'], 'X65')
        self.assertEqual(res['input_summary']['wall_thickness_mm'], 14.30)
        self.assertAlmostEqual(res['hydrostatic_test']['hydro_test_max_bar'], 105.61, delta=0.5)

if __name__ == '__main__':
    unittest.main()
