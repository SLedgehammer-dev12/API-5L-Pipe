"""
Excel Report Exporter using OpenPyXL.
Generates pixel-perfect, beautifully formatted Excel spreadsheets
matching the exact design and layout of the user's reference matrix report.
"""

import io
from typing import List, Dict, Any
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter

class ExcelExporter:
    @staticmethod
    def export_matrix_to_excel(
        project_info: Dict[str, Any],
        pipes_data: List[Dict[str, Any]],
        lang: str = "tr"
    ) -> io.BytesIO:
        """
        Creates an OpenPyXL workbook formatted exactly like the reference inspection matrix.
        """
        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = "Boru Kontrol ve Kabul Raporu"
        ws.views.sheetView[0].showGridLines = True

        # Styles
        font_title = Font(name="Calibri", size=14, bold=True, color="1F2937")
        font_header_dark = Font(name="Calibri", size=10, bold=True, color="000000")
        font_header_bold = Font(name="Calibri", size=9, bold=True, color="000000")
        font_regular = Font(name="Calibri", size=9, bold=False, color="111827")
        font_sub = Font(name="Calibri", size=8, italic=True, color="4B5563")

        fill_header_main = PatternFill(start_color="9CA3AF", end_color="9CA3AF", fill_type="solid")  # Dark grey
        fill_header_sub = PatternFill(start_color="D1D5DB", end_color="D1D5DB", fill_type="solid")   # Light grey
        fill_zebra = PatternFill(start_color="F9FAFB", end_color="F9FAFB", fill_type="solid")        # Very light grey
        fill_section = PatternFill(start_color="E5E7EB", end_color="E5E7EB", fill_type="solid")      # Medium grey

        thin_side = Side(border_style="thin", color="4B5563")
        border_all = Border(left=thin_side, right=thin_side, top=thin_side, bottom=thin_side)
        border_thick_bottom = Border(left=thin_side, right=thin_side, top=thin_side, bottom=Side(border_style="medium", color="111827"))

        align_center = Alignment(horizontal="center", vertical="center", wrap_text=True)
        align_left = Alignment(horizontal="left", vertical="center", wrap_text=True)
        align_right = Alignment(horizontal="right", vertical="center")
        align_vertical_center = Alignment(horizontal="center", vertical="center", text_rotation=90)

        # 1. Project Header Rows
        ws.merge_cells("A1:C1")
        ws["A1"] = f"{project_info.get('project_name', 'Boru Kalite Güvence & Kabul Raporu')}"
        ws["A1"].font = font_title
        ws["A1"].alignment = Alignment(horizontal="left", vertical="center")

        ws["A2"] = f"Proje No: {project_info.get('project_no', '')} | Revizyon: {project_info.get('revision', 'Rev 0')} ({project_info.get('revision_date', '')})"
        ws["A2"].font = font_sub
        ws["A3"] = f"Standart: {project_info.get('standard', 'API 5L PSL2 / BOTAŞ')} | Mühendis: {project_info.get('prepared_by', '')}"
        ws["A3"].font = font_sub

        start_row = 5
        num_pipes = len(pipes_data)

        # Group pipes by diameter for header merging if possible
        # Build headers
        # Row 1: ÇAP (inch)
        # Row 2: ÇAP (mm)
        # Row 3: Design Basıncı / Faktör
        # Row 4: Et Kalınlığı (mm)
        # Row 5: Üretim Yöntemi
        # Row 6: Malzeme Kalitesi
        # Row 7: SMYS (Psi)

        row_defs = [
            # (Label A-D, field_extractor, is_section_header)
            ("ÇAP (inch)", lambda p: p['input_summary']['diameter_inch']),
            ("ÇAP (mm)", lambda p: p['input_summary']['diameter_mm']),
            ("Design Basıncı", lambda p: p['input_summary']['design_factor_str']),
            ("Et Kalınlığı (mm)", lambda p: f"{p['input_summary']['wall_thickness_mm']:.2f}"),
            ("Üretim Yöntemi", lambda p: p['input_summary']['manufacturing_process']),
            ("Malzeme Kalitesi", lambda p: p['input_summary']['material_grade']),
            ("SMYS (Psi)", lambda p: p['mechanical_properties']['smys_psi']),
        ]

        # Write top parameter matrix
        current_r = start_row
        for label, extractor in row_defs:
            ws.merge_cells(start_row=current_r, start_column=1, end_row=current_r, end_column=4)
            cell_lbl = ws.cell(current_r, 1, label)
            cell_lbl.font = font_header_dark
            cell_lbl.fill = fill_header_main
            cell_lbl.alignment = align_center
            for c in range(1, 5):
                ws.cell(current_r, c).border = border_all
                ws.cell(current_r, c).fill = fill_header_main

            # Write values for each pipe
            for idx, pipe in enumerate(pipes_data):
                col_idx = 5 + idx
                val = extractor(pipe)
                c_val = ws.cell(current_r, col_idx, val)
                c_val.font = font_header_bold
                c_val.alignment = align_center
                c_val.border = border_all
                c_val.fill = fill_header_sub if current_r <= start_row + 3 else PatternFill(fill_type=None)
            current_r += 1

        # Chemical Analysis Block
        # Vertical merged block for "Kimyasal Analiz" in Cols A-D
        chem_start_r = current_r
        chem_items = [
            ("C", "Max %", lambda p: p['chemical_analysis']['C_max']),
            ("Mn", "Max %", lambda p: p['chemical_analysis']['Mn_max']),
            ("P", "Max %", lambda p: p['chemical_analysis']['P_max']),
            ("S", "Max %", lambda p: p['chemical_analysis']['S_max']),
            ("Nb", "Min%-Max%", lambda p: p['chemical_analysis']['Nb_min_max']),
            ("V", "Max %", lambda p: p['chemical_analysis']['V_max']),
            ("Ti", "Max %", lambda p: p['chemical_analysis']['Ti_max']),
            ("N", "Max %", lambda p: p['chemical_analysis']['N_max'])
        ]

        for elem, limit_type, ext in chem_items:
            # Columns A-B merged for vertical Kimyasal Analiz later
            ws.cell(current_r, 3, elem).alignment = align_center
            ws.cell(current_r, 3).font = font_header_bold
            ws.cell(current_r, 3).border = border_all
            
            ws.cell(current_r, 4, limit_type).alignment = align_center
            ws.cell(current_r, 4).font = font_regular
            ws.cell(current_r, 4).border = border_all

            for idx, pipe in enumerate(pipes_data):
                col_idx = 5 + idx
                val = ext(pipe)
                c_val = ws.cell(current_r, col_idx, val)
                c_val.font = font_regular
                c_val.alignment = align_center
                c_val.border = border_all
            current_r += 1

        chem_end_r = current_r - 1
        ws.merge_cells(start_row=chem_start_r, start_column=1, end_row=chem_end_r, end_column=2)
        c_chem = ws.cell(chem_start_r, 1, "Kimyasal Analiz")
        c_chem.font = font_header_dark
        c_chem.alignment = align_vertical_center
        c_chem.fill = fill_section
        for r in range(chem_start_r, chem_end_r + 1):
            for c in range(1, 3):
                ws.cell(r, c).border = border_all
                ws.cell(r, c).fill = fill_section

        # Wall Thickness Tolerance Block
        thk_tol_start = current_r
        # Row 1: Min
        ws.merge_cells(start_row=current_r, start_column=2, end_row=current_r, end_column=4)
        ws.cell(current_r, 2, "Et Kalınlığı: Min. (mm)").font = font_header_bold
        ws.cell(current_r, 2).alignment = align_center
        for c in range(2, 5): ws.cell(current_r, c).border = border_all
        for idx, pipe in enumerate(pipes_data):
            c_val = ws.cell(current_r, 5 + idx, pipe['wall_thickness_tolerance']['min_mm'])
            c_val.font = font_regular; c_val.alignment = align_center; c_val.border = border_all
        current_r += 1

        # Row 2: Max
        ws.merge_cells(start_row=current_r, start_column=2, end_row=current_r, end_column=4)
        ws.cell(current_r, 2, "Et Kalınlığı: Max. (mm)").font = font_header_bold
        ws.cell(current_r, 2).alignment = align_center
        for c in range(2, 5): ws.cell(current_r, c).border = border_all
        for idx, pipe in enumerate(pipes_data):
            c_val = ws.cell(current_r, 5 + idx, pipe['wall_thickness_tolerance']['max_mm'])
            c_val.font = font_regular; c_val.alignment = align_center; c_val.border = border_all
        current_r += 1

        thk_tol_end = current_r - 1
        ws.merge_cells(start_row=thk_tol_start, start_column=1, end_row=thk_tol_end, end_column=1)
        c_thk = ws.cell(thk_tol_start, 1, "Et Kalınlığı\nToleransı")
        c_thk.font = font_header_dark; c_thk.alignment = align_center; c_thk.fill = fill_section
        for r in range(thk_tol_start, thk_tol_end + 1):
            ws.cell(r, 1).border = border_all; ws.cell(r, 1).fill = fill_section

        # Remaining Inspection Rows (Full width label in Cols 1-4)
        inspection_rows = [
            ("Yield Min. (Psi-Mpa)", lambda p: f"{p['mechanical_properties']['yield_min_psi']} / {p['mechanical_properties']['yield_min_mpa']}"),
            ("Yield Max. (Psi-Mpa)", lambda p: f"{p['mechanical_properties']['yield_max_psi']} / {p['mechanical_properties']['yield_max_mpa']}"),
            ("Tensile Min  (Psi-Mpa)", lambda p: f"{p['mechanical_properties']['tensile_min_psi']} / {p['mechanical_properties']['tensile_min_mpa']}"),
            ("Tensile Max  (Psi-Mpa)", lambda p: f"{p['mechanical_properties']['tensile_max_psi']} / {p['mechanical_properties']['tensile_max_mpa']}"),
            ("Hydro Test Basıncı Max.(Bar)", lambda p: p['hydrostatic_test']['hydro_test_max_bar']),
            ("Hydro Test Basıncı Min.(Bar)", lambda p: p['hydrostatic_test']['hydro_test_min_bar']),
            ("API 5L Standart Test Pressure (Bar)", lambda p: p['hydrostatic_test']['api_5l_std_test_bar']),
            ("API 5L Alternative Test Pressure (Bar)", lambda p: p['hydrostatic_test']['api_5l_alt_test_bar']),
            ("Boru Çap Toleransı - Boru Ucu Max (mm)", lambda p: p['dimensional_tolerances']['diameter_end_max_mm']),
            ("Boru Çap Toleransı - Boru Ucu Min (mm)", lambda p: p['dimensional_tolerances']['diameter_end_min_mm']),
            ("Boru Çap Toleransı - Gövde Max (mm)", lambda p: p['dimensional_tolerances']['diameter_body_max_mm']),
            ("Boru Çap Toleransı - Gövde Min (mm)", lambda p: p['dimensional_tolerances']['diameter_body_min_mm']),
            ("Boru Çevre Toleransı - Boru Ucu Max (mm)", lambda p: p['dimensional_tolerances']['circ_end_max_mm']),
            ("Boru Çevre Toleransı - Boru Ucu Min (mm)", lambda p: p['dimensional_tolerances']['circ_end_min_mm']),
            ("Boru Çevre Toleransı - Gövde Max (mm)", lambda p: p['dimensional_tolerances']['circ_body_max_mm']),
            ("Boru Çevre Toleransı - Gövde Min (mm)", lambda p: p['dimensional_tolerances']['circ_body_min_mm']),
            ("Ovalite - Boru Ucu (mm)", lambda p: p['dimensional_tolerances']['ovality_end_mm']),
            ("Ovalite - Gövde (mm)", lambda p: p['dimensional_tolerances']['ovality_body_mm']),
            ("Minimum Uzama - Malzeme (%)", lambda p: p['toughness_and_tests']['elongation_mat_min_percent']),
            ("Minimum Uzama - Kaynak (%)", lambda p: p['toughness_and_tests']['elongation_weld_min_percent']),
            ("Radial Offset Max. (mm)", lambda p: p['weld_and_geometry']['radial_offset_max_mm']),
            ("Kaynak Yüksekliği - İç (mm)", lambda p: p['weld_and_geometry']['weld_height_inside_mm']),
            ("Kaynak Yüksekliği - Dış (mm)", lambda p: p['weld_and_geometry']['weld_height_outside_mm']),
            ("Misalignment (mm)", lambda p: p['weld_and_geometry']['misalignment_max_mm']),
            ("Çentik Darbe (J) - Malzeme", lambda p: p['toughness_and_tests']['notch_impact_mat_j']),
            ("Çentik Darbe (J) - Kaynak", lambda p: p['toughness_and_tests']['notch_impact_weld_j']),
            ("Çentik Numunesi Boyutu", lambda p: p['toughness_and_tests']['notch_specimen_size']),
            ("Akma Çekme Oranı Max.", lambda p: p['mechanical_properties']['yield_to_tensile_ratio_max']),
            ("Artık Sress Testi Max (mm)", lambda p: p['toughness_and_tests']['residual_stress_max_mm']),
            ("Yırtılma Testi (DWTT)", lambda p: p['toughness_and_tests']['dwtt_test']),
            ("Sertlik TESTİ", lambda p: p['toughness_and_tests']['hardness_test_max']),
            ("Mandrel Çapı Max (mm)", lambda p: p['toughness_and_tests']['mandrel_dia_max_mm']),
            ("Çene Açıklığı Max (mm)", lambda p: p['toughness_and_tests']['jaw_opening_max_mm']),
            ("FLATTENING - Kaynak açılma yüksekliği (mm)", lambda p: p['flattening']['weld_opening_height_mm']),
            ("FLATTENING - Malzemede çatlak yüksekliği (mm)", lambda p: p['flattening']['material_crack_height_mm']),
            ("FLATTENING - Laminasyon", lambda p: p['flattening']['lamination_rule']),
            ("Boru Ucu Kaynak Çatılaşma Max (mm)", lambda p: p['dimensional_tolerances']['pipe_end_peaking_max_mm']),
            ("Boru Ucu Diklik Max. (mm)", lambda p: p['dimensional_tolerances']['pipe_end_squareness_max_mm']),
            ("Tamir Kaynağı Uzunluğu (Tek mm)", lambda p: p['weld_and_geometry']['weld_repair_length_max_mm']),
            ("Tam. Kay. Ön Isıtma", lambda p: p['weld_and_geometry']['weld_repair_preheat']),
            ("Ağırlık Nominal (Kg/m)", lambda p: p['weights_and_safety']['weight_nominal_kg_m']),
            ("Ağırlık Min. (Kg/m)", lambda p: p['weights_and_safety']['weight_min_kg_m']),
            ("Ağırlık Max. (Kg/m)", lambda p: p['weights_and_safety']['weight_max_kg_m']),
            ("Operating pressure/ SMYS", lambda p: p['weights_and_safety']['operating_press_over_smys_percent']),
            ("841.1.2 Fracture Control and Arrest", lambda p: p['weights_and_safety']['fracture_control_asme_841_1_2']),
            ("D/t", lambda p: p['weights_and_safety']['d_over_t']),
            ("841.1.1 Steel Pipe Design Formula Alternative", lambda p: p['weights_and_safety']['design_formula_asme_841_1_1']),
            ("Alternative Design Pressure", lambda p: p['weights_and_safety']['alternative_design_pressure_bar'])
        ]

        for label, ext in inspection_rows:
            ws.merge_cells(start_row=current_r, start_column=1, end_row=current_r, end_column=4)
            c_lbl = ws.cell(current_r, 1, label)
            c_lbl.font = font_header_bold
            c_lbl.alignment = align_left
            for c in range(1, 5):
                ws.cell(current_r, c).border = border_all
                if current_r % 2 == 0:
                    ws.cell(current_r, c).fill = fill_zebra

            for idx, pipe in enumerate(pipes_data):
                col_idx = 5 + idx
                val = ext(pipe)
                c_val = ws.cell(current_r, col_idx, val)
                c_val.font = font_regular
                c_val.alignment = align_center
                c_val.border = border_all
                if current_r % 2 == 0:
                    c_val.fill = fill_zebra
            current_r += 1

        # Set column widths
        ws.column_dimensions['A'].width = 6
        ws.column_dimensions['B'].width = 8
        ws.column_dimensions['C'].width = 12
        ws.column_dimensions['D'].width = 14

        for idx in range(num_pipes):
            col_letter = get_column_letter(5 + idx)
            ws.column_dimensions[col_letter].width = 15

        # Set Remarks column width
        remarks_col_letter = get_column_letter(5 + num_pipes)
        ws.column_dimensions[remarks_col_letter].width = 32

        # Header for remarks
        cell_rem_head = ws.cell(start_row - 1, 5 + num_pipes, "Standart Referansı / Açıklama")
        cell_rem_head.font = font_header_dark
        cell_rem_head.fill = fill_header_main
        cell_rem_head.alignment = align_center
        cell_rem_head.border = border_all

        # Fill explanations in the far right column for all rows
        exp_dict = pipes_data[0].get('explanations', {}) if pipes_data else {}
        
        # Add explanations for remaining standard rows
        rem_mapping = {
            start_row: exp_dict.get('diameter', {}).get('tr', ''),
            start_row + 1: "Boru Gerçek Dış Çapı (OD mm)",
            start_row + 2: exp_dict.get('design_factor', {}).get('tr', ''),
            start_row + 3: exp_dict.get('wall_thickness', {}).get('tr', ''),
            start_row + 4: exp_dict.get('process', {}).get('tr', ''),
            start_row + 5: exp_dict.get('grade', {}).get('tr', ''),
            start_row + 6: exp_dict.get('smys', {}).get('tr', ''),
        }
        for r_idx, exp_txt in rem_mapping.items():
            c_exp = ws.cell(r_idx, 5 + num_pipes, exp_txt)
            c_exp.font = font_sub
            c_exp.fill = fill_zebra
            c_exp.alignment = align_left
            c_exp.border = border_all

        # Disclaimer & Copyright Footer in Excel
        disclaimer_row = current_r + 2
        total_cols = 5 + num_pipes
        
        # Copyright Note
        ws.merge_cells(start_row=disclaimer_row, start_column=1, end_row=disclaimer_row, end_column=total_cols)
        c_copy = ws.cell(disclaimer_row, 1, "© 2026 API 5L PSL2 & BOTAŞ Pipe QA/QC & Design Suite. Tüm Hakları Saklıdır.")
        c_copy.font = Font(name="Segoe UI", size=9, bold=True, color="334155")
        c_copy.alignment = align_left

        # Engineering Disclaimer Note
        ws.merge_cells(start_row=disclaimer_row + 1, start_column=1, end_row=disclaimer_row + 2, end_column=total_cols)
        disclaimer_text = (
            "YASAL SORUMLULUK REDDİ (ENGINEERING DISCLAIMER): Bu rapor API 5L PSL2 standardı ve BOTAŞ teknik şartnameleri "
            "doğrultusunda otomatik ön hesaplama ve kalite kontrol amacıyla üretilmiştir. Projelerde uygulanacak nihai et kalınlıkları "
            "ve kabul parametreleri, yürürlükteki yasal mevzuat ve lisanslı proje baş mühendisinin / kuruluşunun resmi onayına tabidir."
        )
        c_disc = ws.cell(disclaimer_row + 1, 1, disclaimer_text)
        c_disc.font = Font(name="Segoe UI", size=8, italic=True, color="64748B")
        c_disc.alignment = Alignment(horizontal="left", vertical="top", wrap_text=True)

        stream = io.BytesIO()
        wb.save(stream)
        stream.seek(0)
        return stream
