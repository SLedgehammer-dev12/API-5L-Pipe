"""
Excel Exporter for API 5L PSL2 & BOTAŞ Pipe QA/QC Suite.
Generates fully formatted, colored, print-ready .xlsx workbooks matching exact engineering layout.
"""

import io
from typing import Dict, Any, List
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
        Exports the entire multi-pipe QA/QC inspection matrix to an Excel workbook.
        Populates all 40+ row standard remarks in Turkish or English.
        """
        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = "Boru Kontrol ve Kabul Matrisi"
        ws.views.sheetView[0].showGridLines = True

        # Styles
        font_title = Font(name="Arial", size=14, bold=True, color="1E3A8A")
        font_subtitle = Font(name="Arial", size=9, italic=True, color="475569")
        font_header_dark = Font(name="Arial", size=9, bold=True, color="0F172A")
        font_header_bold = Font(name="Arial", size=9, bold=True, color="000000")
        font_regular = Font(name="Arial", size=9, bold=False, color="000000")
        font_sub = Font(name="Arial", size=8, italic=True, color="475569")

        # Fills
        fill_header_main = PatternFill(start_color="9CA3AF", end_color="9CA3AF", fill_type="solid")
        fill_header_sub = PatternFill(start_color="D1D5DB", end_color="D1D5DB", fill_type="solid")
        fill_section = PatternFill(start_color="E5E7EB", end_color="E5E7EB", fill_type="solid")
        fill_zebra = PatternFill(start_color="F8FAFC", end_color="F8FAFC", fill_type="solid")
        fill_disclaimer = PatternFill(start_color="FEF3C7", end_color="FEF3C7", fill_type="solid")

        # Borders
        border_thin = Side(border_style="thin", color="94A3B8")
        border_all = Border(left=border_thin, right=border_thin, top=border_thin, bottom=border_thin)

        # Alignments
        align_center = Alignment(horizontal="center", vertical="center", wrap_text=True)
        align_left = Alignment(horizontal="left", vertical="center", wrap_text=True)

        # 1. Project Title & Metadata Header
        ws.merge_cells("A1:G1")
        title_text = "API 5L PSL2 & BOTAŞ BORU KALİTE GÜVENCE VE KABUL MATRİSİ" if lang == "tr" else "API 5L PSL2 & BOTAŞ PIPE QA/QC ACCEPTANCE MATRIX"
        cell_t = ws.cell(1, 1, title_text)
        cell_t.font = font_title
        cell_t.alignment = align_left

        ws.merge_cells("A2:G2")
        p_name = project_info.get('project_name', 'Boru Hattı Projesi')
        p_no = project_info.get('project_no', 'PRJ-2026')
        p_rev = project_info.get('revision', 'Rev. 0')
        sub_text = f"Proje: {p_name} | No: {p_no} | Revizyon: {p_rev} | Standart: {project_info.get('standard', 'BOTAŞ Şartnamesi')}"
        cell_s = ws.cell(2, 1, sub_text)
        cell_s.font = font_subtitle
        cell_s.alignment = align_left

        start_row = 5
        num_pipes = len(pipes_data)
        exp_dict = pipes_data[0].get('explanations', {}) if pipes_data else {}

        def get_exp(key: str, fallback: str = "") -> str:
            val = exp_dict.get(key, {})
            if isinstance(val, dict):
                return val.get(lang, val.get('tr', fallback))
            return fallback

        # Matrix Row Definitions
        # Top Header Rows
        header_rows = [
            ("ÇAP (inch)", lambda p: str(p['input_summary']['diameter_inch']), get_exp('diameter')),
            ("ÇAP (mm)", lambda p: f"{p['input_summary']['diameter_mm']:.2f}", "Boru Gerçek Dış Çapı (OD mm)" if lang == "tr" else "Actual Outside Diameter (OD mm)"),
            ("Design Basıncı", lambda p: str(p['input_summary']['design_factor_str']), get_exp('design_factor')),
            ("Et Kalınlığı (mm)", lambda p: f"{p['input_summary']['wall_thickness_mm']:.2f}", get_exp('wall_thickness')),
            ("Üretim Yöntemi", lambda p: str(p['input_summary']['manufacturing_process']), get_exp('process')),
            ("Malzeme Kalitesi", lambda p: str(p['input_summary']['material_grade']), get_exp('grade')),
            ("SMYS (Psi)", lambda p: f"{p['mechanical_properties']['smys_psi']:.2f}", get_exp('smys')),
        ]

        current_r = start_row
        row_remarks_map = {}

        for label, extractor, remark in header_rows:
            ws.merge_cells(start_row=current_r, start_column=1, end_row=current_r, end_column=4)
            cell_lbl = ws.cell(current_r, 1, label)
            cell_lbl.font = font_header_dark
            cell_lbl.fill = fill_header_main
            cell_lbl.alignment = align_center
            for c in range(1, 5):
                ws.cell(current_r, c).border = border_all
                ws.cell(current_r, c).fill = fill_header_main

            for idx, pipe in enumerate(pipes_data):
                col_idx = 5 + idx
                val = extractor(pipe)
                c_val = ws.cell(current_r, col_idx, val)
                c_val.font = font_header_bold
                c_val.alignment = align_center
                c_val.border = border_all
                c_val.fill = fill_header_sub if current_r <= start_row + 3 else PatternFill(fill_type=None)

            row_remarks_map[current_r] = remark
            current_r += 1

        # 2. Chemical Analysis Block (C, Mn, P, S, Nb, V, Ti, N)
        chem_start_r = current_r
        chem_items = [
            ("C", "Max %", lambda p: f"{p['chemical_analysis']['C_max']:.2f}"),
            ("Mn", "Max %", lambda p: f"{p['chemical_analysis']['Mn_max']:.2f}"),
            ("P", "Max %", lambda p: f"{p['chemical_analysis']['P_max']:.3f}"),
            ("S", "Max %", lambda p: f"{p['chemical_analysis']['S_max']:.3f}"),
            ("Nb", "Min%-Max%", lambda p: str(p['chemical_analysis']['Nb_min_max'])),
            ("V", "Max %", lambda p: f"{p['chemical_analysis']['V_max']:.2f}"),
            ("Ti", "Max %", lambda p: f"{p['chemical_analysis']['Ti_max']:.2f}"),
            ("N", "Max %", lambda p: f"{p['chemical_analysis']['N_max']:.3f}")
        ]

        for elem, limit_type, ext in chem_items:
            c_elem = ws.cell(current_r, 2, elem)
            c_elem.font = font_header_dark
            c_elem.alignment = align_center
            c_elem.fill = fill_section

            ws.merge_cells(start_row=current_r, start_column=3, end_row=current_r, end_column=4)
            c_type = ws.cell(current_r, 3, limit_type)
            c_type.font = font_header_dark
            c_type.alignment = align_center
            c_type.fill = fill_section

            for c in range(2, 5):
                ws.cell(current_r, c).border = border_all
                ws.cell(current_r, c).fill = fill_section

            for idx, pipe in enumerate(pipes_data):
                col_idx = 5 + idx
                val = ext(pipe)
                c_val = ws.cell(current_r, col_idx, val)
                c_val.font = font_regular
                c_val.alignment = align_center
                c_val.border = border_all

            row_remarks_map[current_r] = get_exp('chemical', 'API 5L Tablo 5 / BOTAŞ Çizelge 2 Kimyasal Sınırları')
            current_r += 1

        chem_end_r = current_r - 1
        ws.merge_cells(start_row=chem_start_r, start_column=1, end_row=chem_end_r, end_column=1)
        c_chem = ws.cell(chem_start_r, 1, "Kimyasal Analiz" if lang == "tr" else "Chemical Analysis")
        c_chem.font = font_header_dark
        c_chem.alignment = align_center
        c_chem.fill = fill_section
        for r in range(chem_start_r, chem_end_r + 1):
            ws.cell(r, 1).border = border_all
            ws.cell(r, 1).fill = fill_section

        # 3. Wall Thickness Tolerances
        thk_tol_start = current_r
        thk_tol_items = [
            ("Min. (mm)", lambda p: f"{p['wall_thickness_tolerance']['min_mm']:.2f}"),
            ("Max. (mm)", lambda p: f"{p['wall_thickness_tolerance']['max_mm']:.2f}")
        ]

        for lbl, ext in thk_tol_items:
            ws.merge_cells(start_row=current_r, start_column=2, end_row=current_r, end_column=4)
            c_lbl = ws.cell(current_r, 2, lbl)
            c_lbl.font = font_header_dark
            c_lbl.alignment = align_center
            c_lbl.fill = fill_section
            for c in range(2, 5):
                ws.cell(current_r, c).border = border_all
                ws.cell(current_r, c).fill = fill_section

            for idx, pipe in enumerate(pipes_data):
                col_idx = 5 + idx
                val = ext(pipe)
                c_val = ws.cell(current_r, col_idx, val)
                c_val.font = font_regular
                c_val.alignment = align_center
                c_val.border = border_all

            row_remarks_map[current_r] = get_exp('wall_thickness_tol', 'API 5L Tablo 11 / BOTAŞ Çizelge 5 Et Kalınlığı Toleransı')
            current_r += 1

        thk_tol_end = current_r - 1
        ws.merge_cells(start_row=thk_tol_start, start_column=1, end_row=thk_tol_end, end_column=1)
        c_thk = ws.cell(thk_tol_start, 1, "Et Kalınlığı\nToleransı" if lang == "tr" else "Wall Thickness\nTolerance")
        c_thk.font = font_header_dark
        c_thk.alignment = align_center
        c_thk.fill = fill_section
        for r in range(thk_tol_start, thk_tol_end + 1):
            ws.cell(r, 1).border = border_all
            ws.cell(r, 1).fill = fill_section

        def _fmt(v, decimals=2, suffix=""):
            if v is None:
                return ""
            if isinstance(v, (int, float)):
                return f"{v:.{decimals}f}{suffix}"
            return f"{v}{suffix}" if suffix and not str(v).endswith(suffix) else str(v)

        # 4. Remaining Inspection Rows (Full width label in Cols 1-4)
        inspection_rows = [
            ("Boru Çap Toleransı - Boru Ucu Max (mm)", lambda p: _fmt(p['dimensional_tolerances']['diameter_end_max_mm']), get_exp('diameter_tol')),
            ("Boru Çap Toleransı - Boru Ucu Min (mm)", lambda p: _fmt(p['dimensional_tolerances']['diameter_end_min_mm']), get_exp('diameter_tol')),
            ("Boru Çap Toleransı - Boru Gövdesi Max (mm)", lambda p: _fmt(p['dimensional_tolerances']['diameter_body_max_mm']), get_exp('diameter_tol')),
            ("Boru Çap Toleransı - Boru Gövdesi Min (mm)", lambda p: _fmt(p['dimensional_tolerances']['diameter_body_min_mm']), get_exp('diameter_tol')),
            ("Boru Çevre Toleransı - Boru Ucu Max (mm)", lambda p: str(p['dimensional_tolerances']['circ_end_max_mm']), get_exp('circumference_tol')),
            ("Boru Çevre Toleransı - Boru Ucu Min (mm)", lambda p: str(p['dimensional_tolerances']['circ_end_min_mm']), get_exp('circumference_tol')),
            ("Boru Çevre Toleransı - Boru Gövdesi Max (mm)", lambda p: str(p['dimensional_tolerances']['circ_body_max_mm']), get_exp('circumference_tol')),
            ("Boru Çevre Toleransı - Boru Gövdesi Min (mm)", lambda p: str(p['dimensional_tolerances']['circ_body_min_mm']), get_exp('circumference_tol')),
            ("Ovalite - Boru Ucu (mm)", lambda p: str(p['dimensional_tolerances']['ovality_end_mm']), get_exp('ovality')),
            ("Ovalite - Boru Gövdesi (mm)", lambda p: str(p['dimensional_tolerances']['ovality_body_mm']), get_exp('ovality')),
            ("Yield Min. (Psi-Mpa)", lambda p: f"{_fmt(p['mechanical_properties']['yield_min_psi'])} / {_fmt(p['mechanical_properties']['yield_min_mpa'])}", get_exp('yield_tensile')),
            ("Yield Max. (Psi-Mpa)", lambda p: f"{_fmt(p['mechanical_properties']['yield_max_psi'])} / {_fmt(p['mechanical_properties']['yield_max_mpa'])}", get_exp('yield_tensile')),
            ("Tensile Min (Psi-Mpa)", lambda p: f"{_fmt(p['mechanical_properties']['tensile_min_psi'])} / {_fmt(p['mechanical_properties']['tensile_min_mpa'])}", get_exp('yield_tensile')),
            ("Tensile Max (Psi-Mpa)", lambda p: f"{_fmt(p['mechanical_properties']['tensile_max_psi'])} / {_fmt(p['mechanical_properties']['tensile_max_mpa'])}", get_exp('yield_tensile')),
            ("Akma / Çekme Oranı Max. (Y/T)", lambda p: _fmt(p['mechanical_properties']['yield_to_tensile_ratio_max']), get_exp('yt_ratio')),
            ("Hydro Test Basıncı Max. (Bar)", lambda p: _fmt(p['hydrostatic_test']['hydro_test_max_bar']), get_exp('hydro_test')),
            ("Hydro Test Basıncı Min. (Bar)", lambda p: _fmt(p['hydrostatic_test']['hydro_test_min_bar']), "P_max - 2.0 Bar (Fabrika Test Alt Sınırı)"),
            ("API 5L Standart Test Pressure (Bar)", lambda p: _fmt(p['hydrostatic_test']['api_5l_std_test_bar']), get_exp('api_std_test')),
            ("Minimum Uzama (% e) - Malzeme", lambda p: _fmt(p['toughness_and_tests']['elongation_mat_min_percent'], suffix="%"), get_exp('elongation')),
            ("Minimum Uzama (% e) - Kaynak", lambda p: _fmt(p['toughness_and_tests']['elongation_weld_min_percent'], suffix="%"), "Kaynak Dikişi Min. %10 Uzama"),
            ("Çentik Darbe (J) - Malzeme", lambda p: _fmt(p['toughness_and_tests']['notch_impact_mat_j'], suffix=" J"), get_exp('cvn')),
            ("Çentik Darbe (J) - Kaynak", lambda p: _fmt(p['toughness_and_tests']['notch_impact_weld_j'], suffix=" J"), get_exp('cvn')),
            ("Radial Offset Max. (mm)", lambda p: _fmt(p['weld_and_geometry']['radial_offset_max_mm']), get_exp('radial_offset')),
            ("Kaynak Yüksekliği - İç / Dış (mm)", lambda p: f"{_fmt(p['weld_and_geometry']['weld_height_inside_mm'])} / {_fmt(p['weld_and_geometry']['weld_height_outside_mm'])}", get_exp('weld_height')),
            ("Misalignment (mm)", lambda p: _fmt(p['weld_and_geometry']['misalignment_max_mm']), get_exp('misalignment')),
            ("Artık Gerilme Testi Max (mm)", lambda p: _fmt(p['toughness_and_tests']['residual_stress_max_mm']), get_exp('residual_stress')),
            ("Yırtılma Testi (DWTT)", lambda p: str(p['toughness_and_tests']['dwtt_test']), get_exp('dwtt')),
            ("Sertlik TESTİ", lambda p: str(p['toughness_and_tests']['hardness_test_max']), get_exp('hardness')),
            ("Mandrel Çapı / Çene Açıklığı (mm)", lambda p: f"{_fmt(p['toughness_and_tests']['mandrel_dia_max_mm'])} / {_fmt(p['toughness_and_tests']['jaw_opening_max_mm'])}", get_exp('mandrel_jaw')),
            ("FLATTENING - Kaynak / Çatlak", lambda p: f"{_fmt(p['flattening']['weld_opening_height_mm'])} / {_fmt(p['flattening']['material_crack_height_mm'])}", get_exp('flattening')),
            ("Ağırlık Nominal (Kg/m)", lambda p: f"{_fmt(p['weights_and_safety']['weight_nominal_kg_m'])} ({_fmt(p['weights_and_safety']['weight_min_kg_m'])} - {_fmt(p['weights_and_safety']['weight_max_kg_m'])})", get_exp('weight')),
            ("Operating pressure / SMYS", lambda p: str(p['weights_and_safety']['operating_press_over_smys_percent']), "İşletme Gerilmesi / SMYS Oranı"),
            ("841.1.2 Fracture Control and Arrest", lambda p: str(p['weights_and_safety']['fracture_control_asme_841_1_2']), get_exp('fracture_control')),
            ("D/t & Alternatif Basınç Dizayn", lambda p: f"D/t={_fmt(p['weights_and_safety']['d_over_t'])} ({_fmt(p['weights_and_safety']['design_formula_asme_841_1_1'])})", get_exp('thick_wall_alt')),
        ]

        for lbl, ext, remark in inspection_rows:
            ws.merge_cells(start_row=current_r, start_column=1, end_row=current_r, end_column=4)
            c_lbl = ws.cell(current_r, 1, lbl)
            c_lbl.font = font_header_dark
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

            row_remarks_map[current_r] = remark
            current_r += 1

        # Set column widths
        ws.column_dimensions['A'].width = 6
        ws.column_dimensions['B'].width = 8
        ws.column_dimensions['C'].width = 14
        ws.column_dimensions['D'].width = 16

        for idx in range(num_pipes):
            col_letter = get_column_letter(5 + idx)
            ws.column_dimensions[col_letter].width = 18

        # Set Remarks column width & fill remarks for ALL 40+ rows
        remarks_col_idx = 5 + num_pipes
        remarks_col_letter = get_column_letter(remarks_col_idx)
        ws.column_dimensions[remarks_col_letter].width = 40

        cell_rem_head = ws.cell(start_row - 1, remarks_col_idx, "Standart Referansı & Açıklama" if lang == "tr" else "Standard Reference & Remarks")
        cell_rem_head.font = font_header_dark
        cell_rem_head.fill = fill_header_main
        cell_rem_head.alignment = align_center
        cell_rem_head.border = border_all

        for r_idx, rem_text in row_remarks_map.items():
            c_exp = ws.cell(r_idx, remarks_col_idx, rem_text)
            c_exp.font = font_sub
            c_exp.fill = fill_zebra
            c_exp.alignment = align_left
            c_exp.border = border_all

        # Disclaimer & Copyright Footer in Excel
        disclaimer_row = current_r + 2
        total_cols = remarks_col_idx

        # Copyright Note
        ws.merge_cells(start_row=disclaimer_row, start_column=1, end_row=disclaimer_row, end_column=total_cols)
        c_copy = ws.cell(disclaimer_row, 1, "© 2026 API 5L PSL2 & BOTAŞ Pipe QA/QC & Design Suite. Tüm Hakları Saklıdır.")
        c_copy.font = font_header_bold
        c_copy.alignment = align_left

        # Engineering Disclaimer Note
        ws.merge_cells(start_row=disclaimer_row + 1, start_column=1, end_row=disclaimer_row + 2, end_column=total_cols)
        disclaimer_text = (
            "Yasal Uyarı / Disclaimer: Bu hesaplama ve kalite güvence tablosu mühendislik ön tasarımı ve fabrika kabul denetimleri amacıyla üretilmiştir. "
            "Projelerdeki nihai imalat ve satın alma kararlarında yürürlükteki resmi standartlar ve lisanslı baş mühendisin onayı esastır."
            if lang == "tr" else
            "Disclaimer: This calculation and QA/QC matrix is generated for engineering pre-design and factory acceptance inspection purposes. "
            "Official standards and licensed chief engineer approvals govern final manufacturing and procurement decisions."
        )
        c_disc = ws.cell(disclaimer_row + 1, 1, disclaimer_text)
        c_disc.font = font_sub
        c_disc.fill = fill_disclaimer
        c_disc.alignment = align_left

        output = io.BytesIO()
        wb.save(output)
        output.seek(0)
        return output
