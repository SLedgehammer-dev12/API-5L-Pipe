"""
Project & Revision Management Module.
Handles project metadata, revisions, presets for 10 BOTAŞ and 10 API 5L pipes, and JSON serialization.
"""

from typing import Dict, Any, List
import json

class ProjectManager:
    @staticmethod
    def get_reference_preset_48_18() -> Dict[str, Any]:
        """
        Returns the exact reference project shown in the user's screenshot:
        - 48\" SAWH X65 with 5 wall thicknesses: 14.30, 17.50, 20.60, 22.20, 23.80 mm
        - 18\" SAWH X65 with wall thickness 16.66 mm
        """
        return {
            'project_info': {
                'project_name': 'Doğal Gaz Boru Hattı Fabrika Kabul ve Kalite Güvence Projesi',
                'project_no': 'PRJ-2026-API5L-001',
                'line_name': 'Ana İletim Hattı & İstasyon Bağlantıları',
                'client': 'BOTAŞ Boru Hatları ile Petrol Taşıma A.Ş.',
                'contractor': 'Boru İmalat ve Denetim San. A.Ş.',
                'prepared_by': 'Boru Tasarım & Kalite Mühendisi',
                'checked_by': 'Kalite Kontrol Şefi',
                'approved_by': 'Baş Denetçi / Proje Müdürü',
                'revision': 'Rev. 0',
                'revision_date': '2026-08-21',
                'standard': 'BOTAŞ Şartnamesi',
                'language': 'tr'
            },
            'pipes': [
                {'id': 'pipe_1', 'diameter_inch': '48"', 'diameter_mm': 1219.0, 'design_factor_str': '0,72 (Hat)', 'wall_thickness_mm': 14.30, 'manufacturing_process': 'SAWH', 'material_grade': 'X65', 'standard_type': 'BOTAŞ', 'design_pressure_bar': 75.0},
                {'id': 'pipe_2', 'diameter_inch': '48"', 'diameter_mm': 1219.0, 'design_factor_str': '0,6 (Hat)', 'wall_thickness_mm': 17.50, 'manufacturing_process': 'SAWH', 'material_grade': 'X65', 'standard_type': 'BOTAŞ', 'design_pressure_bar': 75.0},
                {'id': 'pipe_3', 'diameter_inch': '48"', 'diameter_mm': 1219.0, 'design_factor_str': '0,5 (Hat)', 'wall_thickness_mm': 20.60, 'manufacturing_process': 'SAWH', 'material_grade': 'X65', 'standard_type': 'BOTAŞ', 'design_pressure_bar': 75.0},
                {'id': 'pipe_4', 'diameter_inch': '48"', 'diameter_mm': 1219.0, 'design_factor_str': '0,5 (İst.)', 'wall_thickness_mm': 22.20, 'manufacturing_process': 'SAWH', 'material_grade': 'X65', 'standard_type': 'BOTAŞ', 'design_pressure_bar': 75.0},
                {'id': 'pipe_5', 'diameter_inch': '48"', 'diameter_mm': 1219.0, 'design_factor_str': '0,5 (İst.)', 'wall_thickness_mm': 23.80, 'manufacturing_process': 'SAWH', 'material_grade': 'X65', 'standard_type': 'BOTAŞ', 'design_pressure_bar': 75.0},
                {'id': 'pipe_6', 'diameter_inch': '18"', 'diameter_mm': 457.0, 'design_factor_str': '0,72', 'wall_thickness_mm': 16.66, 'manufacturing_process': 'SAWH', 'material_grade': 'X65', 'standard_type': 'BOTAŞ', 'design_pressure_bar': 75.0}
            ]
        }

    @staticmethod
    def get_10_botas_pipes_preset() -> Dict[str, Any]:
        """
        Preset containing 10 distinct BOTAŞ standard pipes.
        Material grade and wall thickness are automatically matched to BOTAŞ specification tables.
        """
        return {
            'project_info': {
                'project_name': 'BOTAŞ Doğal Gaz İletim ve İstasyon Boruları Fabrika Kabul Matrisi (10 Çeşit)',
                'project_no': 'BOTAS-FAT-10PIPES-2026',
                'line_name': 'BOTAŞ Standart İletim ve İstasyon Şebekesi',
                'client': 'BOTAŞ Boru Hatları ile Petrol Taşıma A.Ş.',
                'contractor': 'Boru İmalat A.Ş.',
                'prepared_by': 'BOTAŞ Hat Tasarım Mühendisi',
                'checked_by': 'BOTAŞ Baş Kontrolör',
                'approved_by': 'BOTAŞ Kalite Güvence Müdürü',
                'revision': 'Rev. 0',
                'revision_date': '2026-08-21',
                'standard': 'BOTAŞ Şartnamesi',
                'language': 'tr'
            },
            'pipes': [
                {'id': 'botas_1', 'diameter_inch': '1/2"', 'diameter_mm': 21.3, 'design_factor_str': '0,5 (İst.)', 'wall_thickness_mm': 3.70, 'manufacturing_process': 'SMLS', 'material_grade': 'GRADE B', 'standard_type': 'BOTAŞ', 'design_pressure_bar': 75.0},
                {'id': 'botas_2', 'diameter_inch': '2"', 'diameter_mm': 60.3, 'design_factor_str': '0,5 (İst.)', 'wall_thickness_mm': 5.50, 'manufacturing_process': 'SMLS', 'material_grade': 'GRADE B', 'standard_type': 'BOTAŞ', 'design_pressure_bar': 75.0},
                {'id': 'botas_3', 'diameter_inch': '4"', 'diameter_mm': 114.3, 'design_factor_str': '0,5 (İst.)', 'wall_thickness_mm': 6.00, 'manufacturing_process': 'ERW HFW', 'material_grade': 'GRADE B', 'standard_type': 'BOTAŞ', 'design_pressure_bar': 75.0},
                {'id': 'botas_4', 'diameter_inch': '6"', 'diameter_mm': 168.3, 'design_factor_str': '0,72 (Hat)', 'wall_thickness_mm': 5.20, 'manufacturing_process': 'ERW HFW', 'material_grade': 'X42', 'standard_type': 'BOTAŞ', 'design_pressure_bar': 75.0},
                {'id': 'botas_5', 'diameter_inch': '8"', 'diameter_mm': 219.1, 'design_factor_str': '0,72 (Hat)', 'wall_thickness_mm': 5.20, 'manufacturing_process': 'ERW HFW', 'material_grade': 'X42', 'standard_type': 'BOTAŞ', 'design_pressure_bar': 75.0},
                {'id': 'botas_6', 'diameter_inch': '12"', 'diameter_mm': 323.9, 'design_factor_str': '0,72 (Hat)', 'wall_thickness_mm': 5.20, 'manufacturing_process': 'ERW HFW', 'material_grade': 'X52', 'standard_type': 'BOTAŞ', 'design_pressure_bar': 75.0},
                {'id': 'botas_7', 'diameter_inch': '16"', 'diameter_mm': 406.4, 'design_factor_str': '0,6 (Hat)', 'wall_thickness_mm': 6.40, 'manufacturing_process': 'SAWH', 'material_grade': 'X60', 'standard_type': 'BOTAŞ', 'design_pressure_bar': 75.0},
                {'id': 'botas_8', 'diameter_inch': '24"', 'diameter_mm': 610.0, 'design_factor_str': '0,72 (Hat)', 'wall_thickness_mm': 7.10, 'manufacturing_process': 'SAWH', 'material_grade': 'X65', 'standard_type': 'BOTAŞ', 'design_pressure_bar': 75.0},
                {'id': 'botas_9', 'diameter_inch': '36"', 'diameter_mm': 914.0, 'design_factor_str': '0,72 (Hat)', 'wall_thickness_mm': 11.10, 'manufacturing_process': 'SAWH', 'material_grade': 'X65', 'standard_type': 'BOTAŞ', 'design_pressure_bar': 75.0},
                {'id': 'botas_10', 'diameter_inch': '48"', 'diameter_mm': 1219.0, 'design_factor_str': '0,72 (Hat)', 'wall_thickness_mm': 14.30, 'manufacturing_process': 'SAWH', 'material_grade': 'X65', 'standard_type': 'BOTAŞ', 'design_pressure_bar': 75.0}
            ]
        }

    @staticmethod
    def get_10_api_5l_pipes_preset() -> Dict[str, Any]:
        """
        Preset containing 10 distinct API 5L PSL2 pipes with user-selected sizes, schedules and grades (Grade B to X80).
        """
        return {
            'project_info': {
                'project_name': 'API 5L PSL2 & ASME B31.8 Uluslararası Boru Hattı Kalite Kabul Matrisi (10 Çeşit)',
                'project_no': 'API5L-PSL2-10PIPES-2026',
                'line_name': 'Yüksek Basınçlı Doğal Gaz ve Petrol Boru Hatları',
                'client': 'Uluslararası Boru Hattı İşletmesi',
                'contractor': 'Global Pipe Manufacturing Ltd.',
                'prepared_by': 'Kıdemli Boru Mühendisi',
                'checked_by': 'QA/QC Koordinatörü',
                'approved_by': 'Bağımsız Denetçi (Third Party TPI)',
                'revision': 'Rev. 0',
                'revision_date': '2026-08-21',
                'standard': 'API 5L PSL2',
                'language': 'tr'
            },
            'pipes': [
                {'id': 'api_1', 'diameter_inch': '2"', 'diameter_mm': 60.3, 'design_factor_str': '0.72 (Hat)', 'wall_thickness_mm': 3.91, 'manufacturing_process': 'SMLS', 'material_grade': 'GRADE B', 'standard_type': 'API 5L', 'design_pressure_bar': 100.0},
                {'id': 'api_2', 'diameter_inch': '4"', 'diameter_mm': 114.3, 'design_factor_str': '0.72 (Hat)', 'wall_thickness_mm': 4.78, 'manufacturing_process': 'ERW HFW', 'material_grade': 'X42', 'standard_type': 'API 5L', 'design_pressure_bar': 100.0},
                {'id': 'api_3', 'diameter_inch': '6"', 'diameter_mm': 168.3, 'design_factor_str': '0.72 (Hat)', 'wall_thickness_mm': 7.11, 'manufacturing_process': 'ERW HFW', 'material_grade': 'X52', 'standard_type': 'API 5L', 'design_pressure_bar': 100.0},
                {'id': 'api_4', 'diameter_inch': '8"', 'diameter_mm': 219.1, 'design_factor_str': '0.60 (Hat)', 'wall_thickness_mm': 8.18, 'manufacturing_process': 'ERW HFW', 'material_grade': 'X56', 'standard_type': 'API 5L', 'design_pressure_bar': 100.0},
                {'id': 'api_5', 'diameter_inch': '12"', 'diameter_mm': 323.9, 'design_factor_str': '0.72 (Hat)', 'wall_thickness_mm': 9.53, 'manufacturing_process': 'ERW HFW', 'material_grade': 'X60', 'standard_type': 'API 5L', 'design_pressure_bar': 100.0},
                {'id': 'api_6', 'diameter_inch': '18"', 'diameter_mm': 457.0, 'design_factor_str': '0.72 (Hat)', 'wall_thickness_mm': 16.66, 'manufacturing_process': 'SAWH', 'material_grade': 'X65', 'standard_type': 'API 5L', 'design_pressure_bar': 100.0},
                {'id': 'api_7', 'diameter_inch': '24"', 'diameter_mm': 610.0, 'design_factor_str': '0.72 (Hat)', 'wall_thickness_mm': 12.70, 'manufacturing_process': 'SAWH', 'material_grade': 'X65', 'standard_type': 'API 5L', 'design_pressure_bar': 100.0},
                {'id': 'api_8', 'diameter_inch': '30"', 'diameter_mm': 762.0, 'design_factor_str': '0.72 (Hat)', 'wall_thickness_mm': 14.27, 'manufacturing_process': 'SAWH', 'material_grade': 'X70', 'standard_type': 'API 5L', 'design_pressure_bar': 100.0},
                {'id': 'api_9', 'diameter_inch': '36"', 'diameter_mm': 914.0, 'design_factor_str': '0.72 (Hat)', 'wall_thickness_mm': 15.88, 'manufacturing_process': 'SAWH', 'material_grade': 'X70', 'standard_type': 'API 5L', 'design_pressure_bar': 100.0},
                {'id': 'api_10', 'diameter_inch': '48"', 'diameter_mm': 1219.0, 'design_factor_str': '0.72 (Hat)', 'wall_thickness_mm': 18.00, 'manufacturing_process': 'SAWH', 'material_grade': 'X80', 'standard_type': 'API 5L', 'design_pressure_bar': 100.0}
            ]
        }
