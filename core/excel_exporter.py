"""
Excel Exporter for API 5L PSL2 & BOTAŞ Pipe QA/QC Suite.
Generates fully formatted, colored, print-ready .xlsx workbooks matching exact engineering layout.
"""

import io
import math
from datetime import datetime
from typing import Any, Dict, List, Optional

import openpyxl
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
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

        num_pipes = len(pipes_data)
        max_col = max(7, 2 + num_pipes)
        last_col_letter = get_column_letter(max_col)

        # 1. Project Title & Metadata Header
        ws.merge_cells(f"A1:{last_col_letter}1")
        title_text = "API 5L PSL2 & BOTAŞ BORU KALİTE GÜVENCE VE KABUL MATRİSİ" if lang == "tr" else "API 5L PSL2 & BOTAŞ PIPE QA/QC ACCEPTANCE MATRIX"
        cell_t = ws.cell(1, 1, title_text)
        cell_t.font = font_title
        cell_t.alignment = align_left

        ws.merge_cells(f"A2:{last_col_letter}2")
        p_name = project_info.get('project_name', 'Boru Hattı Projesi')
        p_no = project_info.get('project_no', 'PRJ-2026')
        p_rev = project_info.get('revision', 'Rev. 0')
        sub_text = f"Proje: {p_name} | No: {p_no} | Revizyon: {p_rev} | Standart: {project_info.get('standard', 'BOTAŞ Şartnamesi')}"
        cell_s = ws.cell(2, 1, sub_text)
        cell_s.font = font_subtitle
        cell_s.alignment = align_left

        start_row = 5
        num_pipes = len(pipes_data)

        def _std_tag(pipe: dict) -> str:
            s = str(((pipe.get('input_summary') or {}).get('standard_type', ''))).upper()
            psl = str(((pipe.get('input_summary') or {}).get('psl_level', ''))).upper()
            if 'BOTAŞ' in s or 'BOTAS' in s:
                return 'BOTAŞ'
            if 'PSL1' in psl:
                return 'API 5L PSL1'
            return 'API 5L PSL2'

        def get_exp(key: str, fallback: str = "") -> str:
            # Per-pipe explanations: combine distinct texts across columns so the
            # shared remarks column stays correct for mixed-standard projects.
            seen = []
            for pipe in pipes_data:
                val = (pipe.get('explanations', {}) or {}).get(key, {})
                t = val.get(lang, val.get('tr', '')) if isinstance(val, dict) else ''
                if t and t not in [x[1] for x in seen]:
                    seen.append((_std_tag(pipe), t))
            if not seen:
                return fallback
            if len(seen) == 1:
                return seen[0][1]
            return " | ".join(f"{tag}: {t}" for tag, t in seen)

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

        # 2. Chemical Analysis Block (C, Mn, P, S, Nb, V, Ti, N, CE IIW, CE Pcm)
        def _fmt(v, dec):
            if v is None or v == "":
                return "—"
            if isinstance(v, (int, float)):
                return f"{v:.{dec}f}"
            return str(v)

        chem_start_r = current_r
        nb_has_min = any(
            (p['chemical_analysis'].get('Nb_min') or 0) > 0 for p in pipes_data
        )
        nb_label = "Min%-Max%" if nb_has_min else "Max %"
        chem_items = [
            ("C", "Max %", lambda p: _fmt(p['chemical_analysis'].get('C_max'), 2)),
            ("Mn", "Max %", lambda p: _fmt(p['chemical_analysis'].get('Mn_max'), 2)),
            ("P", "Max %", lambda p: _fmt(p['chemical_analysis'].get('P_max'), 3)),
            ("S", "Max %", lambda p: _fmt(p['chemical_analysis'].get('S_max'), 3)),
            ("Nb", nb_label, lambda p: str(p['chemical_analysis'].get('Nb_min_max')) if p['chemical_analysis'].get('Nb_min_max') else "—"),
            ("V", "Max %", lambda p: _fmt(p['chemical_analysis'].get('V_max'), 2)),
            ("Ti", "Max %", lambda p: _fmt(p['chemical_analysis'].get('Ti_max'), 2)),
            ("N", "Max %", lambda p: _fmt(p['chemical_analysis'].get('N_max'), 3)),
            ("CE (IIW)", "Max", lambda p: _fmt(p['chemical_analysis'].get('CE_IIW_max'), 2)),
            ("CE (Pcm)", "Max", lambda p: _fmt(p['chemical_analysis'].get('CE_Pcm_max'), 2))
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
        # Each row also carries a row_frequency key so the far-right
        # "Test Frekansı" column can be filled from each pipe's row_frequency map.
        inspection_rows = [
            ("Boru Çap Toleransı - Boru Ucu Max (mm)", lambda p: _fmt(p['dimensional_tolerances']['diameter_end_max_mm']), get_exp('diameter_tol'), "diameter_oor"),
            ("Boru Çap Toleransı - Boru Ucu Min (mm)", lambda p: _fmt(p['dimensional_tolerances']['diameter_end_min_mm']), get_exp('diameter_tol'), "diameter_oor"),
            ("Boru Çap Toleransı - Boru Gövdesi Max (mm)", lambda p: _fmt(p['dimensional_tolerances']['diameter_body_max_mm']), get_exp('diameter_tol'), "diameter_oor"),
            ("Boru Çap Toleransı - Boru Gövdesi Min (mm)", lambda p: _fmt(p['dimensional_tolerances']['diameter_body_min_mm']), get_exp('diameter_tol'), "diameter_oor"),
            ("Boru Çevre Toleransı - Boru Ucu Max (mm)", lambda p: str(p['dimensional_tolerances']['circ_end_max_mm']), get_exp('circumference_tol'), "diameter_oor"),
            ("Boru Çevre Toleransı - Boru Ucu Min (mm)", lambda p: str(p['dimensional_tolerances']['circ_end_min_mm']), get_exp('circumference_tol'), "diameter_oor"),
            ("Boru Çevre Toleransı - Boru Gövdesi Max (mm)", lambda p: str(p['dimensional_tolerances']['circ_body_max_mm']), get_exp('circumference_tol'), "diameter_oor"),
            ("Boru Çevre Toleransı - Boru Gövdesi Min (mm)", lambda p: str(p['dimensional_tolerances']['circ_body_min_mm']), get_exp('circumference_tol'), "diameter_oor"),
            ("Ovalite - Boru Ucu (mm)", lambda p: str(p['dimensional_tolerances']['ovality_end_mm']), get_exp('ovality'), "diameter_oor"),
            ("Ovalite - Boru Gövdesi (mm)", lambda p: str(p['dimensional_tolerances']['ovality_body_mm']), get_exp('ovality'), "diameter_oor"),
            ("Yield Min. (Psi-Mpa)", lambda p: f"{_fmt(p['mechanical_properties']['yield_min_psi'])} / {_fmt(p['mechanical_properties']['yield_min_mpa'])}", get_exp('yield_tensile'), "tensile"),
            ("Yield Max. (Psi-Mpa)", lambda p: f"{_fmt(p['mechanical_properties']['yield_max_psi'])} / {_fmt(p['mechanical_properties']['yield_max_mpa'])}", get_exp('yield_tensile'), "tensile"),
            ("Tensile Min (Psi-Mpa)", lambda p: f"{_fmt(p['mechanical_properties']['tensile_min_psi'])} / {_fmt(p['mechanical_properties']['tensile_min_mpa'])}", get_exp('yield_tensile'), "tensile"),
            ("Tensile Max (Psi-Mpa)", lambda p: f"{_fmt(p['mechanical_properties']['tensile_max_psi'])} / {_fmt(p['mechanical_properties']['tensile_max_mpa'])}", get_exp('yield_tensile'), "tensile"),
            ("Akma / Çekme Oranı Max. (Y/T)", lambda p: _fmt(p['mechanical_properties']['yield_to_tensile_ratio_max']), get_exp('yt_ratio'), "tensile"),
            ("Hydro Test Basıncı Max. (Bar)", lambda p: _fmt(p['hydrostatic_test']['hydro_test_max_bar']), get_exp('hydro_test'), "hydro"),
            ("Hydro Test Basıncı Min. (Bar)", lambda p: _fmt(p['hydrostatic_test']['hydro_test_min_bar']), "P_max - 2.0 Bar (Fabrika Test Alt Sınırı)", "hydro"),
            ("API 5L Standart Test Pressure (Bar)", lambda p: _fmt(p['hydrostatic_test']['api_5l_std_test_bar']), get_exp('api_std_test'), "hydro"),
            ("Minimum Uzama (% e) - Malzeme", lambda p: _fmt(p['toughness_and_tests']['elongation_mat_min_percent'], suffix="%"), get_exp('elongation'), "tensile"),
            ("Minimum Uzama (% e) - Kaynak", lambda p: _fmt(p['toughness_and_tests']['elongation_weld_min_percent'], suffix="%"), "Kaynak Dikişi Min. %10 Uzama", "tensile"),
            ("Çentik Darbe (J) - Malzeme", lambda p: _fmt(p['toughness_and_tests']['notch_impact_mat_j'], suffix=" J"), get_exp('cvn'), "cvn"),
            ("Çentik Darbe (J) - Kaynak", lambda p: _fmt(p['toughness_and_tests']['notch_impact_weld_j'], suffix=" J"), get_exp('cvn'), "cvn"),
            ("Radial Offset Max. (mm)", lambda p: _fmt(p['weld_and_geometry']['radial_offset_max_mm']), get_exp('radial_offset'), "radial_offset"),
            ("Kaynak Yüksekliği - İç / Dış (mm)", lambda p: f"{_fmt(p['weld_and_geometry']['weld_height_inside_mm'])} / {_fmt(p['weld_and_geometry']['weld_height_outside_mm'])}", get_exp('weld_height'), "weld_height"),
            ("Misalignment (mm)", lambda p: _fmt(p['weld_and_geometry']['misalignment_max_mm']), get_exp('misalignment'), "misalignment"),
            ("Boru Ucu Kaynak Çatılaşma Max(mm)", lambda p: _fmt(p['dimensional_tolerances']['pipe_end_peaking_max_mm']), get_exp('peaking'), "peaking"),
            ("Boru Ucu Diklik Max. (mm)", lambda p: _fmt(p['dimensional_tolerances']['pipe_end_squareness_max_mm']), get_exp('squareness'), "squareness"),
            ("Artık Gerilme Testi Max (mm)", lambda p: _fmt(p['toughness_and_tests']['residual_stress_max_mm']), get_exp('residual_stress'), "residual_stress"),
            ("Yırtılma Testi (DWTT)", lambda p: str(p['toughness_and_tests']['dwtt_test']), get_exp('dwtt'), "dwtt"),
            ("Sertlik TESTİ", lambda p: str(p['toughness_and_tests']['hardness_test_max']), get_exp('hardness'), "hardness"),
            ("Mandrel Çapı / Çene Açıklığı (mm)", lambda p: f"{_fmt(p['toughness_and_tests']['mandrel_dia_max_mm'])} / {_fmt(p['toughness_and_tests']['jaw_opening_max_mm'])}", get_exp('mandrel_jaw'), "bend"),
            ("FLATTENING - Kaynak / Çatlak", lambda p: f"{_fmt(p['flattening']['weld_opening_height_mm'])} / {_fmt(p['flattening']['material_crack_height_mm'])}", get_exp('flattening'), "flattening"),
            ("Ağırlık Nominal (Kg/m)", lambda p: f"{_fmt(p['weights_and_safety']['weight_nominal_kg_m'])} ({_fmt(p['weights_and_safety']['weight_min_kg_m'])} - {_fmt(p['weights_and_safety']['weight_max_kg_m'])})", get_exp('weight'), "weight"),
            ("Operating pressure / SMYS", lambda p: str(p['weights_and_safety']['operating_press_over_smys_percent']), "İşletme Gerilmesi / SMYS Oranı", None),
            ("841.1.2 Fracture Control and Arrest", lambda p: str(p['weights_and_safety']['fracture_control_asme_841_1_2']), get_exp('fracture_control'), None),
            ("D/t & Alternatif Basınç Dizayn", lambda p: f"D/t={_fmt(p['weights_and_safety']['d_over_t'])} ({_fmt(p['weights_and_safety']['design_formula_asme_841_1_1'])})", get_exp('thick_wall_alt'), None),
        ]

        def _agg_freq(freq_key):
            if not freq_key:
                return "—"
            seen = []
            for p in pipes_data:
                v = (p.get('row_frequency') or {}).get(freq_key)
                if v and v not in seen:
                    seen.append(v)
            return " | ".join(seen) if seen else "—"

        remarks_col_idx = 5 + num_pipes
        freq_col_idx = remarks_col_idx + 1

        for lbl, ext, remark, freq_key in inspection_rows:
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

            c_freq = ws.cell(current_r, freq_col_idx, _agg_freq(freq_key))
            c_freq.font = font_regular
            c_freq.alignment = align_center
            c_freq.border = border_all
            if current_r % 2 == 0:
                c_freq.fill = fill_zebra

            row_remarks_map[current_r] = remark
            current_r += 1

        # 5. Test / Inspection Frequency Block (diameter + grade + PSL + process driven)
        freq_test_names = []
        for pipe in pipes_data:
            for f in (pipe.get('test_frequency') or []):
                if f.get('test') and f['test'] not in freq_test_names:
                    freq_test_names.append(f['test'])
        if freq_test_names:
            current_r += 1
            ws.merge_cells(start_row=current_r, start_column=1, end_row=current_r, end_column=freq_col_idx)
            c_sec = ws.cell(current_r, 1, "TEST FREKANSI (Sıklık / Numune Sayısı)")
            c_sec.font = font_header_dark
            c_sec.fill = fill_header_main
            c_sec.alignment = align_left
            current_r += 1
            for test_name in freq_test_names:
                ws.merge_cells(start_row=current_r, start_column=1, end_row=current_r, end_column=4)
                c_lbl = ws.cell(current_r, 1, test_name)
                c_lbl.font = font_header_dark
                c_lbl.alignment = align_left
                for c in range(1, 5):
                    ws.cell(current_r, c).border = border_all
                    if current_r % 2 == 0:
                        ws.cell(current_r, c).fill = fill_zebra
                for idx, pipe in enumerate(pipes_data):
                    entry = next((f for f in (pipe.get('test_frequency') or [])
                                  if f.get('test') == test_name), None)
                    val = entry.get('frequency') if entry else "—"
                    c_val = ws.cell(current_r, 5 + idx, val)
                    c_val.font = font_regular
                    c_val.alignment = align_center
                    c_val.border = border_all
                    if current_r % 2 == 0:
                        c_val.fill = fill_zebra
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

        # Test frequency column (far right) width & header
        freq_col_letter = get_column_letter(freq_col_idx)
        ws.column_dimensions[freq_col_letter].width = 30
        cell_freq_head = ws.cell(start_row - 1, freq_col_idx, "Test Frekansı / Sıklık & Numune" if lang == "tr" else "Test Frequency / Sampling")
        cell_freq_head.font = font_header_dark
        cell_freq_head.fill = fill_header_main
        cell_freq_head.alignment = align_center
        cell_freq_head.border = border_all

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

    @staticmethod
    def export_itp_audit_report(
        audit_data: Dict[str, Any],
        lang: str = "tr"
    ) -> io.BytesIO:
        """
        Exports the ITP comparison and audit findings to a styled Excel report.
        """
        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = "ITP Denetim ve Sapma Raporu"
        ws.views.sheetView[0].showGridLines = True

        font_title = Font(name="Arial", size=13, bold=True, color="1E3A8A")
        font_header = Font(name="Arial", size=9, bold=True, color="FFFFFF")
        font_bold = Font(name="Arial", size=9, bold=True)
        font_regular = Font(name="Arial", size=9)
        font_small = Font(name="Arial", size=8, italic=True, color="475569")

        fill_header = PatternFill(start_color="1E3A8A", end_color="1E3A8A", fill_type="solid")
        fill_pass = PatternFill(start_color="DCFCE7", end_color="DCFCE7", fill_type="solid")
        fill_warn = PatternFill(start_color="FEF9C3", end_color="FEF9C3", fill_type="solid")
        fill_fail = PatternFill(start_color="FEE2E2", end_color="FEE2E2", fill_type="solid")
        fill_zebra = PatternFill(start_color="F8FAFC", end_color="F8FAFC", fill_type="solid")

        border_thin = Side(border_style="thin", color="CBD5E1")
        border_all = Border(left=border_thin, right=border_thin, top=border_thin, bottom=border_thin)

        align_left = Alignment(horizontal="left", vertical="center", wrap_text=True)
        align_center = Alignment(horizontal="center", vertical="center", wrap_text=True)

        pipe = audit_data.get("pipe_summary", {})
        kpi = audit_data.get("kpi", {})

        std_ed_title = pipe.get("standard_edition", "API Spec 5L 47. Baskı")
        # Header Title
        ws.merge_cells("A1:J1")
        ws.cell(1, 1, f"{std_ed_title} - ITP AKILLI DENETİM VE SAPMA RAPORU").font = font_title
        ws.cell(1, 1).alignment = align_left

        # Pipe Metadata Box
        ws.merge_cells("A2:J2")
        d_inch_str = pipe.get("diameter_inch", "48in")
        d_mm_str = pipe.get("diameter_mm", "1219")
        wt_mm_str = pipe.get("wall_thickness_mm", "14.3")
        grade_str = pipe.get("material_grade", "X65")
        psl_str = pipe.get("psl_level", "PSL2")
        process_str = pipe.get("manufacturing_process", "SAWH")
        score_val = kpi.get("compliance_score_percent", 0.0)
        bare_s = kpi.get("bare_pipe_score_percent")
        coat_s = kpi.get("coating_score_percent")
        verdict_str = kpi.get("overall_verdict", "N/A")

        scores_summary = f"Genel Uyum: %{score_val}"
        if bare_s is not None:
            scores_summary += f" | Çıplak Boru: %{bare_s}"
        if coat_s is not None:
            scores_summary += f" | 3LPE Kaplama: %{coat_s}"

        meta_str = (
            f"Boru Özellikleri: {d_inch_str} ({d_mm_str} mm) x {wt_mm_str} mm | "
            f"Kalite: {grade_str} {psl_str} | Üretim: {process_str} | "
            f"{scores_summary} ({verdict_str})"
        )
        ws.cell(2, 1, meta_str).font = font_small
        ws.cell(2, 1).alignment = align_left

        # Table Column Headers
        headers = [
            "Muayene / Test Adı",
            "Kategori / Disiplin",
            "Boru Sütunu Hesaplanan Hedef Değer",
            "NDT Metot Standardı",
            "İmalatçı ITP Frekansı",
            "API 5L / BOTAŞ Şartname Frekansı",
            "İmalatçı ITP Kabul Kriteri",
            "Standart Kabul Kriteri (Limit Değer)",
            "Şahitlik Noktaları (C/W/H)",
            "Denetim Durumu & Bulgular",
        ]
        
        ws.row_dimensions[4].height = 28
        for col_idx, text in enumerate(headers, 1):
            c = ws.cell(4, col_idx, text)
            c.font = font_header
            c.fill = fill_header
            c.alignment = align_center
            c.border = border_all

        # Populate Rows
        current_r = 5
        for row in audit_data.get("audit_rows", []):
            ws.row_dimensions[current_r].height = 36
            status = row.get("status", "COMPLIANT")
            ip = row.get("inspection_points", {})
            ip_str = f"Üretici: {ip.get('mfg', 'C')} | TPI: {ip.get('tpi', 'W')} | İdare: {ip.get('client', 'W')}" if isinstance(ip, dict) and ip else "C / W / H"
            
            c_name = ws.cell(current_r, 1, row.get("test_name", "—"))
            c_cat = ws.cell(current_r, 2, row.get("category", "—"))
            c_target = ws.cell(current_r, 3, row.get("calculated_target", "—"))
            c_ndt = ws.cell(current_r, 4, row.get("ndt_method_standard", "—"))
            c_up_f = ws.cell(current_r, 5, row.get("uploaded_frequency", "—"))
            c_st_f = ws.cell(current_r, 6, row.get("standard_frequency", "—"))
            c_up_c = ws.cell(current_r, 7, row.get("uploaded_criteria", "—"))
            c_st_c = ws.cell(current_r, 8, row.get("standard_criteria", "—"))
            c_ip = ws.cell(current_r, 9, ip_str)
            c_rem = ws.cell(current_r, 10, row.get("audit_remarks", "—"))

            status_fill = fill_pass if status == "COMPLIANT" else (fill_warn if status == "MORE_STRINGENT" else fill_fail)

            for cell in (c_name, c_cat, c_target, c_ndt, c_up_f, c_st_f, c_up_c, c_st_c, c_ip, c_rem):
                cell.font = font_regular
                cell.border = border_all
                cell.alignment = align_left

            c_target.font = font_bold
            c_ip.alignment = align_center
            c_rem.fill = status_fill
            c_rem.font = font_bold if status != "COMPLIANT" else font_regular
            c_name.fill = fill_zebra if current_r % 2 == 0 else PatternFill(fill_type=None)

            current_r += 1

        # Column Widths & Freeze Panes & Auto Filter
        widths = [26, 16, 28, 22, 22, 26, 26, 30, 24, 45]
        for idx, w in enumerate(widths, 1):
            ws.column_dimensions[get_column_letter(idx)].width = w

        ws.freeze_panes = "A5"
        if current_r > 5:
            ws.auto_filter.ref = f"A4:J{current_r - 1}"

        # Sheet 2: Findings & Non-Compliances
        findings = audit_data.get("findings", [])
        if findings:
            ws_f = wb.create_sheet(title="Bulgular ve Sapmalar")
            ws_f.views.sheetView[0].showGridLines = True
            ws_f.merge_cells("A1:E1")
            ws_f.cell(1, 1, "ITP DENETİMİ SAPMA VE UYARILAR LİSTESİ").font = font_title
            ws_f.cell(1, 1).alignment = align_left

            f_headers = ["Önem Seviyesi", "Madde / Test Adı", "Kusur Türü", "Şartname / Madde Ref.", "Denetçi Açıklaması"]
            ws_f.row_dimensions[3].height = 26
            for col_idx, text in enumerate(f_headers, 1):
                c = ws_f.cell(3, col_idx, text)
                c.font = font_header
                c.fill = fill_header
                c.alignment = align_center
                c.border = border_all

            f_row = 4
            for find in findings:
                ws_f.row_dimensions[f_row].height = 30
                sev = find.get("severity", "INFO")
                sev_fill = fill_fail if sev == "CRITICAL" else fill_warn

                c_sev = ws_f.cell(f_row, 1, sev)
                c_tname = ws_f.cell(f_row, 2, find.get("test_name", "—"))
                c_type = ws_f.cell(f_row, 3, find.get("issue_type", "—"))
                c_clause = ws_f.cell(f_row, 4, find.get("clause_ref", "—"))
                c_msg = ws_f.cell(f_row, 5, find.get("message", "—"))

                for cell in (c_sev, c_tname, c_type, c_clause, c_msg):
                    cell.font = font_regular
                    cell.border = border_all
                    cell.alignment = align_left

                c_sev.fill = sev_fill
                c_sev.font = font_bold
                c_sev.alignment = align_center
                f_row += 1

            f_widths = [16, 26, 22, 24, 60]
            for idx, w in enumerate(f_widths, 1):
                ws_f.column_dimensions[get_column_letter(idx)].width = w

            ws_f.freeze_panes = "A4"
            ws_f.auto_filter.ref = f"A3:E{f_row - 1}"

        output = io.BytesIO()
        wb.save(output)
        output.seek(0)
        return output

    @staticmethod
    def export_verification_report(
        project_info: Dict[str, Any],
        verification_data: Dict[str, Any],
        lang: str = "tr"
    ) -> io.BytesIO:
        """
        Exports the actual inspection verification results (PASS/FAIL) to a styled Excel workbook.
        """
        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = "MTC Doğrulama ve Kabul" if lang == "tr" else "MTC Verification"
        ws.views.sheetView[0].showGridLines = True

        # Fonts
        font_title = Font(name="Arial", size=13, bold=True, color="1E3A8A")
        font_sub = Font(name="Arial", size=9, bold=True, color="0F172A")
        font_info = Font(name="Arial", size=9, color="334155")
        font_header = Font(name="Arial", size=9, bold=True, color="FFFFFF")
        font_regular = Font(name="Arial", size=9, color="000000")
        font_mono = Font(name="Consolas", size=9, color="000000")
        font_bold = Font(name="Arial", size=9, bold=True, color="000000")
        font_badge_pass = Font(name="Arial", size=10, bold=True, color="065F46")
        font_badge_fail = Font(name="Arial", size=10, bold=True, color="991B1B")

        # Fills
        fill_header = PatternFill(start_color="1E3A8A", end_color="1E3A8A", fill_type="solid")
        fill_sub_header = PatternFill(start_color="475569", end_color="475569", fill_type="solid")
        fill_pass = PatternFill(start_color="D1FAE5", end_color="D1FAE5", fill_type="solid")
        fill_fail = PatternFill(start_color="FEE2E2", end_color="FEE2E2", fill_type="solid")
        fill_zebra = PatternFill(start_color="F8FAFC", end_color="F8FAFC", fill_type="solid")
        fill_badge_pass = PatternFill(start_color="A7F3D0", end_color="A7F3D0", fill_type="solid")
        fill_badge_fail = PatternFill(start_color="FECACA", end_color="FECACA", fill_type="solid")

        border_thin = Side(border_style="thin", color="CBD5E1")
        border_all = Border(left=border_thin, right=border_thin, top=border_thin, bottom=border_thin)

        align_center = Alignment(horizontal="center", vertical="center", wrap_text=True)
        align_left = Alignment(horizontal="left", vertical="center", wrap_text=True)

        # Row 1: Title
        ws.row_dimensions[1].height = 25
        title_text = "BORU MALZEME TEST SERTİFİKASI (MTC) DOĞRULAMA VE FABRİKA KABUL RAPORU" if lang == "tr" else "PIPE MATERIAL TEST CERTIFICATE (MTC) VERIFICATION & ACCEPTANCE REPORT"
        ws.merge_cells("A1:F1")
        ws.cell(1, 1, title_text).font = font_title
        ws.cell(1, 1).alignment = align_left

        # Row 2-3: Metadata
        p_name = project_info.get("project_name", "API 5L Boru Hattı Projesi")
        p_no = project_info.get("project_no", "API-5L")
        p_client = project_info.get("client", "BOTAŞ / İdare")
        p_mfg = project_info.get("contractor", "Boru İmalatçısı")
        p_std = project_info.get("standard", "API 5L PSL2 & BOTAŞ")
        p_date = project_info.get("revision_date", "2026-10-09")
        p_heat = project_info.get("heat_number", "—")
        p_cert = project_info.get("certificate_number", "—")

        pipe_summary = verification_data.get("pipe_summary", {})
        d_str = pipe_summary.get("diameter_inch", '48"')
        d_mm = pipe_summary.get("diameter_mm", 1219.0)
        t_mm = float(pipe_summary.get("wall_thickness_mm", 14.30) or 14.30)
        grade = pipe_summary.get("material_grade", "X65")
        proc = pipe_summary.get("manufacturing_process", "SAWH")
        psl = pipe_summary.get("psl_level", "PSL2")

        meta_line1 = f"Proje: {p_name} ({p_no}) | Standart: {p_std} | Tarih: {p_date} | İşveren: {p_client} | Üretici: {p_mfg}"
        meta_line2 = f"Denetlenen Boru: {d_str} ({d_mm} mm) x {t_mm:.2f} mm | Kalite: {grade} ({psl}) | Yöntem: {proc} | Isı/Döküm: {p_heat} | Sertifika No: {p_cert}"

        ws.row_dimensions[2].height = 18
        ws.merge_cells("A2:F2")
        ws.cell(2, 1, meta_line1).font = font_info
        ws.cell(2, 1).alignment = align_left

        ws.row_dimensions[3].height = 18
        ws.merge_cells("A3:F3")
        ws.cell(3, 1, meta_line2).font = font_info
        ws.cell(3, 1).alignment = align_left

        # Row 5: Verdict & Summary Badge
        overall_status = verification_data.get("overall_status", "ACCEPTED")
        is_accepted = overall_status == "ACCEPTED"
        badge_text = f"GENEL FABRİKA KABUL KARARI: {verification_data.get('overall_badge', 'UYGUN (PASS)')}"
        count_text = f"{verification_data.get('passed_count', 0)} / {verification_data.get('total_applicable', 0)} Parametre Uygun (Kontrol: {verification_data.get('checks_count', 0)}, Red: {verification_data.get('failed_count', 0)})"

        ws.row_dimensions[5].height = 26
        ws.merge_cells("A5:D5")
        c_badge = ws.cell(5, 1, f"  {badge_text}")
        c_badge.font = font_badge_pass if is_accepted else font_badge_fail
        c_badge.fill = fill_badge_pass if is_accepted else fill_badge_fail
        c_badge.alignment = align_left

        ws.merge_cells("E5:F5")
        c_count = ws.cell(5, 5, count_text)
        c_count.font = font_bold
        c_count.fill = fill_badge_pass if is_accepted else fill_badge_fail
        c_count.alignment = align_center

        # Row 7: Checks Table Header
        headers = [
            "Kategori / Disiplin" if lang == "tr" else "Category",
            "Denetlenen Parametre" if lang == "tr" else "Parameter",
            "Ölçülen Test Değeri" if lang == "tr" else "Actual Value",
            "Şartname Kabul Limiti" if lang == "tr" else "Required Limit",
            "Kabul Durumu" if lang == "tr" else "Status",
            "Standart Referansı / Denetim Notu" if lang == "tr" else "Notes / Standard Ref"
        ]
        ws.row_dimensions[7].height = 26
        for col_idx, text in enumerate(headers, 1):
            c = ws.cell(7, col_idx, text)
            c.font = font_header
            c.fill = fill_header
            c.alignment = align_center
            c.border = border_all

        # Checks Table Rows
        row_idx = 8
        for chk in verification_data.get("checks", []):
            ws.row_dimensions[row_idx].height = 22
            passed = chk.get("status") == "PASS"

            c_cat = ws.cell(row_idx, 1, chk.get("category", "—"))
            c_param = ws.cell(row_idx, 2, chk.get("parameter", "—"))
            c_act = ws.cell(row_idx, 3, str(chk.get("actual_value", "—")))
            c_req = ws.cell(row_idx, 4, str(chk.get("required_limit", "—")))
            c_status = ws.cell(row_idx, 5, "UYGUN (PASS)" if passed else "RED (FAIL)")
            c_notes = ws.cell(row_idx, 6, chk.get("notes", ""))

            for cell in (c_cat, c_param, c_act, c_req, c_status, c_notes):
                cell.font = font_regular
                cell.border = border_all
                cell.alignment = align_left

            c_param.font = font_bold
            c_act.font = font_mono
            c_act.alignment = align_center
            c_req.font = font_mono
            c_req.alignment = align_center
            c_status.alignment = align_center
            c_status.font = font_badge_pass if passed else font_badge_fail
            c_status.fill = fill_pass if passed else fill_fail

            if row_idx % 2 == 1:
                c_cat.fill = fill_zebra
                c_notes.fill = fill_zebra

            row_idx += 1

        # Ramberg-Osgood Strain-Based Design & Work Hardening Analysis
        ro = verification_data.get("ramberg_osgood")
        if ro:
            row_idx += 1
            ws.row_dimensions[row_idx].height = 24
            ws.merge_cells(f"A{row_idx}:F{row_idx}")
            title_ro = "GERİNİM BAZLI TASARIM & RAMBERG-OSGOOD PEKLEŞME MODELİ (API 5L EK N / BOTAŞ / DNV-ST-F101)" if lang == "tr" else "STRAIN-BASED DESIGN & RAMBERG-OSGOOD WORK HARDENING (API 5L ANNEX N / BOTAŞ)"
            ws.cell(row_idx, 1, title_ro).font = font_sub
            ws.cell(row_idx, 1).alignment = align_left
            row_idx += 1

            ro_headers = [
                "Gerinim Parametresi" if lang == "tr" else "Strain Parameter",
                "Formül / Denklem" if lang == "tr" else "Formula / Equation",
                "Hesaplanan Değer" if lang == "tr" else "Calculated Value",
                "Şartname Kriteri / Hedef" if lang == "tr" else "Spec Criteria / Target",
                "Değerlendirme" if lang == "tr" else "Status",
                "Açıklama / Mühendislik Notu" if lang == "tr" else "Engineering Notes"
            ]
            ws.row_dimensions[row_idx].height = 24
            for col_idx, text in enumerate(ro_headers, 1):
                c = ws.cell(row_idx, col_idx, text)
                c.font = font_header
                c.fill = fill_sub_header
                c.alignment = align_center
                c.border = border_all
            row_idx += 1

            ro_rows = [
                (
                    "Pekleşme Üssü (n)",
                    "ε = σ/E + 0.002·(σ/Rt0.5)ⁿ",
                    f"{ro.get('n_exponent', '—')}",
                    "10.0 - 30.0 (API 5L / DNV)",
                    "UYGUN" if (10.0 <= float(ro.get('n_exponent', 0) or 0) <= 35.0) else "KONTROL",
                    "Plastik deformasyonu homojen dağıtma ve boyun vermeye direnç üssü."
                ),
                (
                    "Homojen Uzama (Agt %)",
                    "Agt = (Rm/E + 1/n) · 100",
                    f"%{ro.get('uniform_strain_pct', '—')}",
                    "Min %5.0 (Annex N)",
                    "UYGUN" if float(ro.get('uniform_strain_pct', 0) or 0) >= 5.0 else "STANDART",
                    "Boyun verme (necking) öncesi ulaşılan maksimum üniform plastik gerinim."
                ),
                (
                    "Pekleşme Marjı (ΔR)",
                    "ΔR = Rm - Rt0.5",
                    f"{ro.get('hardening_margin_mpa', '—')} MPa",
                    "Min 80.0 MPa (Tavsiye)",
                    "UYGUN" if float(ro.get('hardening_margin_mpa', 0) or 0) >= 80.0 else "STANDART",
                    "Sünek kırılma rezervi ve plastik enerji sönümleme güvencesi."
                ),
                (
                    "Akma/Çekme Oranı (Y/T)",
                    "Y/T = Rt0.5 / Rm",
                    f"{ro.get('yt_ratio', '—')}",
                    "Max 0.93 (PSL2 / BOTAŞ)",
                    "UYGUN" if float(ro.get('yt_ratio', 1.0) or 1.0) <= 0.93 else "RED",
                    "Boru hattının plastik deformasyon rezervi göstergesi."
                ),
                (
                    "Rezilyans Modülü (Ur)",
                    "Ur = Rt0.5² / (2·E)",
                    f"{ro.get('resilience_modulus_mpa', '—')} MJ/m³",
                    "— (Referans)",
                    "BİLGİ",
                    "Elastik geri yaylanma ve enerji depolama kapasitesi."
                ),
                (
                    "Tokluk Modülü (Ut)",
                    "Ut ≈ [(Rt0.5 + 2Rm)/3] · εf",
                    f"{ro.get('toughness_modulus_mpa', '—')} MJ/m³",
                    "Yüksek Tokluk",
                    "UYGUN",
                    "Kopmaya kadar yutulabilen toplam plastik deformasyon enerjisi."
                ),
            ]

            for r_data in ro_rows:
                ws.row_dimensions[row_idx].height = 20
                c1 = ws.cell(row_idx, 1, r_data[0])
                c2 = ws.cell(row_idx, 2, r_data[1])
                c3 = ws.cell(row_idx, 3, r_data[2])
                c4 = ws.cell(row_idx, 4, r_data[3])
                c5 = ws.cell(row_idx, 5, r_data[4])
                c6 = ws.cell(row_idx, 6, r_data[5])

                for cell in (c1, c2, c3, c4, c5, c6):
                    cell.font = font_regular
                    cell.border = border_all
                    cell.alignment = align_left

                c1.font = font_bold
                c2.font = font_mono
                c3.font = font_mono
                c3.alignment = align_center
                c4.font = font_mono
                c4.alignment = align_center
                c5.alignment = align_center

                is_ok = r_data[4] in ("UYGUN", "BİLGİ")
                c5.font = font_badge_pass if is_ok else font_badge_fail
                c5.fill = fill_pass if is_ok else fill_fail

                if row_idx % 2 == 1:
                    c1.fill = fill_zebra
                    c6.fill = fill_zebra

                row_idx += 1

        # Test Frequency References Table
        freqs = verification_data.get("frequency_references", [])
        if freqs:
            row_idx += 1
            ws.row_dimensions[row_idx].height = 22
            ws.merge_cells(f"A{row_idx}:F{row_idx}")
            ws.cell(row_idx, 1, "ŞARTNAME TEST VE NUMUNE FREKANSLARI (API 5L & BOTAŞ)").font = font_sub
            row_idx += 1

            f_headers = ["Test Adı", "Standart Maddesi", "Gerekli Frekans / Sıklık"]
            ws.row_dimensions[row_idx].height = 24
            for col_idx, text in enumerate(f_headers, 1):
                c = ws.cell(row_idx, col_idx, text)
                c.font = font_header
                c.fill = fill_sub_header
                c.alignment = align_center
                c.border = border_all
            ws.merge_cells(f"C{row_idx}:F{row_idx}")
            row_idx += 1

            for f in freqs:
                ws.row_dimensions[row_idx].height = 20
                c_t = ws.cell(row_idx, 1, f.get("test", "—"))
                c_c = ws.cell(row_idx, 2, f.get("clause", "—"))
                c_fq = ws.cell(row_idx, 3, f.get("frequency", "—"))
                ws.merge_cells(f"C{row_idx}:F{row_idx}")

                for cell in (c_t, c_c, c_fq):
                    cell.font = font_regular
                    cell.border = border_all
                    cell.alignment = align_left
                c_t.font = font_bold
                row_idx += 1

        # Signatures
        row_idx += 2
        ws.row_dimensions[row_idx].height = 20
        ws.cell(row_idx, 1, "HAZIRLAYAN (Kalite Mühendisi)").font = font_bold
        ws.cell(row_idx, 3, "KONTROL EDEN (QA/QC Şefi)").font = font_bold
        ws.cell(row_idx, 5, "ONAYLAYAN (Baş Denetçi / TPI)").font = font_bold

        row_idx += 1
        ws.row_dimensions[row_idx].height = 30
        for col in (1, 3, 5):
            c = ws.cell(row_idx, col, "İmza / Kaşe: ______________")
            c.font = font_info
            c.alignment = align_left

        # Widths
        widths = [26, 32, 22, 28, 18, 48]
        for idx, w in enumerate(widths, 1):
            ws.column_dimensions[get_column_letter(idx)].width = w

        ws.freeze_panes = "A8"
        checks_len = len(verification_data.get("checks", []))
        if checks_len > 0:
            ws.auto_filter.ref = f"A7:F{7 + checks_len}"

        output = io.BytesIO()
        wb.save(output)
        output.seek(0)
        return output

    @staticmethod
    def export_wall_thickness_report(
        calculation_data: Dict[str, Any],
        project_info: Optional[Dict[str, Any]] = None,
        lang: str = "tr"
    ) -> io.BytesIO:
        """
        Exports the multi-standard pipe wall thickness calculation sheet to a styled Excel workbook.
        """
        if project_info is None:
            project_info = {}

        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = "Et Kalınlığı Hesabı" if lang == "tr" else "Wall Thickness Calc"
        ws.views.sheetView[0].showGridLines = True

        # Fonts
        font_title = Font(name="Arial", size=13, bold=True, color="1E3A8A")
        font_sec = Font(name="Arial", size=10, bold=True, color="1E3A8A")
        font_info = Font(name="Arial", size=9, color="334155")
        font_header = Font(name="Arial", size=9, bold=True, color="FFFFFF")
        font_regular = Font(name="Arial", size=9, color="000000")
        font_mono = Font(name="Consolas", size=9, color="000000")
        font_bold = Font(name="Arial", size=9, bold=True, color="000000")
        font_badge_pass = Font(name="Arial", size=10, bold=True, color="065F46")
        font_badge_fail = Font(name="Arial", size=10, bold=True, color="991B1B")

        # Fills
        fill_header = PatternFill(start_color="1E3A8A", end_color="1E3A8A", fill_type="solid")
        fill_sec = PatternFill(start_color="F1F5F9", end_color="F1F5F9", fill_type="solid")
        fill_pass = PatternFill(start_color="D1FAE5", end_color="D1FAE5", fill_type="solid")
        fill_fail = PatternFill(start_color="FEE2E2", end_color="FEE2E2", fill_type="solid")
        fill_zebra = PatternFill(start_color="F8FAFC", end_color="F8FAFC", fill_type="solid")
        fill_highlight = PatternFill(start_color="E0F2FE", end_color="E0F2FE", fill_type="solid")

        border_thin = Side(border_style="thin", color="CBD5E1")
        border_all = Border(left=border_thin, right=border_thin, top=border_thin, bottom=border_thin)

        align_center = Alignment(horizontal="center", vertical="center", wrap_text=True)
        align_left = Alignment(horizontal="left", vertical="center", wrap_text=True)

        inp = calculation_data.get("input_parameters", {})
        res = calculation_data.get("calculation_results", {})

        # Row 1: Title
        ws.row_dimensions[1].height = 25
        title_text = "BORU HATTI & BASINÇLI BORULAMA ET KALINLIĞI MÜHENDİSLİK HESAP FÖYÜ" if lang == "tr" else "PIPE WALL THICKNESS CALCULATION & SCHEDULE SELECTION SHEET"
        ws.merge_cells("A1:E1")
        ws.cell(1, 1, title_text).font = font_title
        ws.cell(1, 1).alignment = align_left

        # Row 2: Metadata
        p_name = project_info.get("project_name", "Boru Hattı Projesi")
        p_no = project_info.get("project_no", "PRJ-CALC")
        p_client = project_info.get("client", "BOTAŞ / İdare")
        p_date = project_info.get("revision_date", "2026-10-09")
        std_code = inp.get("standard_code", "BOTAŞ / ASME B31.8")
        meta_str = f"Proje: {p_name} ({p_no}) | Standart/Kod: {std_code} | Müşteri: {p_client} | Tarih: {p_date}"

        ws.row_dimensions[2].height = 18
        ws.merge_cells("A2:E2")
        ws.cell(2, 1, meta_str).font = font_info
        ws.cell(2, 1).alignment = align_left

        # Row 4: Status Verdict
        is_safe = res.get("is_nominal_sufficient", True)
        badge_text = "GENEL DEĞERLENDİRME: SEÇİLEN NOMİNAL ET KALINLIĞI UYGUN VE GÜVENLİ (PASS)" if is_safe else "GENEL DEĞERLENDİRME: SEÇİLEN ET KALINLIĞI YETERSİZ (FAIL)"
        ws.row_dimensions[4].height = 24
        ws.merge_cells("A4:E4")
        c_badge = ws.cell(4, 1, f"  {badge_text}")
        c_badge.font = font_badge_pass if is_safe else font_badge_fail
        c_badge.fill = fill_pass if is_safe else fill_fail
        c_badge.alignment = align_left

        def write_section_header(row_num, text):
            ws.row_dimensions[row_num].height = 22
            ws.merge_cells(f"A{row_num}:E{row_num}")
            c = ws.cell(row_num, 1, f"  {text}")
            c.font = font_sec
            c.fill = fill_sec
            c.alignment = align_left
            for col in range(1, 6):
                ws.cell(row_num, col).border = border_all

        def write_table_header(row_num, col_titles):
            ws.row_dimensions[row_num].height = 22
            for col_idx, t in enumerate(col_titles, 1):
                c = ws.cell(row_num, col_idx, t)
                c.font = font_header
                c.fill = fill_header
                c.alignment = align_center
                c.border = border_all

        r_curr = 6
        write_section_header(r_curr, "1. GİRDİ VE TASARIM PARAMETRELERİ")
        r_curr += 1

        headers_in = ["Parametre Açıklaması", "Sembol", "Tasarım Değeri", "Birim", "Şartname / Açıklama"]
        write_table_header(r_curr, headers_in)
        r_curr += 1

        d_inch_val = inp.get('diameter_inch', '48"')
        d_mm_val = inp.get('diameter_mm', 1219.0)
        p_bar_val = float(inp.get('design_pressure_bar', 75.0) or 75.0)

        input_rows = [
            ("Nominal Boru Dış Çapı", "D", f"{d_inch_val} ({d_mm_val} mm)", "in / mm", "Dış Çap (OD)"),
            ("Malzeme Kalitesi / Seviye", "Grade", f"{inp.get('material_grade', 'X65')} ({inp.get('psl_level', 'PSL2')})", "—", "API Spec 5L / BOTAŞ"),
            ("Minimum Akma Dayanımı (SMYS)", "S (SMYS)", f"{float(inp.get('smys_mpa', 450.0) or 450.0):.1f}", "MPa", "Belirtilen Minimum Akma Sınırı"),
            ("Tasarım Basıncı", "P", f"{p_bar_val:.2f}", "Bar (g)", f"({(p_bar_val/10.0):.2f} MPa)"),
            ("Tasarım Faktörü", "F", f"{float(inp.get('design_factor_f', 0.72) or 0.72):.2f}", "—", f"Konum: {inp.get('location_type', 'Pipeline')}"),
            ("Boyuna Kaynak Faktörü", "E", f"{float(inp.get('longitudinal_joint_factor_e', 1.0) or 1.0):.2f}", "—", f"Yöntem: {inp.get('manufacturing_process', 'SAWH')}"),
            ("Sıcaklık Düşürme Faktörü", "T", f"{float(inp.get('temperature_derating_factor_t', 1.0) or 1.0):.2f}", "—", "T <= 121 °C için 1.00"),
            ("Korozyon Payı", "c", f"{float(inp.get('corrosion_allowance_mm', 0.0) or 0.0):.2f}", "mm", "İç / Dış Korozyon Eklemesi"),
            ("İmalat Negatif Tolerans Kuralı", "Tol", f"-%{float(inp.get('tolerance_percent_used', 0.0) or 0.0):.2f}", "%", inp.get("tolerance_rule_description", "Standart"))
        ]

        for p_desc, p_sym, p_val, p_unit, p_rem in input_rows:
            ws.row_dimensions[r_curr].height = 20
            c1 = ws.cell(r_curr, 1, p_desc)
            c2 = ws.cell(r_curr, 2, p_sym)
            c3 = ws.cell(r_curr, 3, p_val)
            c4 = ws.cell(r_curr, 4, p_unit)
            c5 = ws.cell(r_curr, 5, p_rem)

            for cell in (c1, c2, c3, c4, c5):
                cell.font = font_regular
                cell.border = border_all
                cell.alignment = align_left

            c2.alignment = align_center
            c2.font = font_bold
            c3.alignment = align_center
            c3.font = font_mono
            c4.alignment = align_center
            if r_curr % 2 == 1:
                for cell in (c1, c2, c3, c4, c5):
                    cell.fill = fill_zebra
            r_curr += 1

        r_curr += 1
        write_section_header(r_curr, "2. HESAPLAMA YÖNTEMİ VE FORMÜL ANALİZİ")
        r_curr += 1

        headers_method = ["Hesap Adımı", "Uygulanan Formül", "Değer Özeti", "Birim", "Referans Standart"]
        write_table_header(r_curr, headers_method)
        r_curr += 1

        calc_name = res.get("formula_name", "Barlow Formülü")
        f_latex = res.get("formula_latex", r"t = (P · D) / (2 · S · F · E · T) + c")

        ws.row_dimensions[r_curr].height = 22
        c_m1 = ws.cell(r_curr, 1, "Standart Basınç Formülü")
        c_m2 = ws.cell(r_curr, 2, calc_name)
        c_m3 = ws.cell(r_curr, 3, f_latex)
        c_m4 = ws.cell(r_curr, 4, "—")
        c_m5 = ws.cell(r_curr, 5, inp.get("standard_code", "ASME / BOTAŞ"))
        for cell in (c_m1, c_m2, c_m3, c_m4, c_m5):
            cell.font = font_regular
            cell.border = border_all
        c_m2.font = font_bold
        c_m3.font = font_mono
        c_m4.alignment = align_center
        r_curr += 1

        r_curr += 1
        write_section_header(r_curr, "3. HESAP SONUÇLARI VE NOMİNAL ET KALINLIĞI SEÇİMİ")
        r_curr += 1

        headers_res = ["Sonuç Parametresi", "Sembol", "Hesaplanan Değer", "Birim", "Değerlendirme / Durum"]
        write_table_header(r_curr, headers_res)
        r_curr += 1

        t_base = float(res.get("t_theoretical_mm", 0.0) or 0.0)
        c_val = float(res.get("corrosion_allowance_mm", 0.0) or 0.0)
        t_req = float(res.get("t_required_asme_b31_8_mm", 0.0) or 0.0)
        t_nom = float(res.get("selected_nominal_thickness_asme_b36_10_mm", 0.0) or 0.0)
        t_eff = float(res.get("negative_tolerance_min_mm", 0.0) or 0.0)
        botas_rec = float(res.get("botas_standard_thickness_mm", 0.0) or 0.0)

        result_rows = [
            ("Teorik Gereken Et Kalınlığı (Basınç)", "t_base", f"{t_base:.2f}", "mm", "İç basınca karşı gereken minimum net kalınlık"),
            ("Korozyon Payı İlavesi", "+ c", f"+{c_val:.2f}", "mm", "Tasarım korozyon payı eklemesi"),
            ("Toplam Gerekli Tasarım Kalınlığı", "t_req", f"{t_req:.2f}", "mm", "t_base + c"),
            ("Seçilen Standart Nominal Et Kalınlığı", "t_nom", f"{t_nom:.2f}", "mm", f"Standart: {res.get('schedule_standard_used', 'ASME B36.10M')}"),
            ("Negatif İmalat Toleransı Sonrası Min. Kalınlık", "t_eff (min)", f"{t_eff:.2f}", "mm", f"Kural: {res.get('tolerance_rule_description', '—')}"),
            ("Emniyet Değerlendirmesi (t_eff >= t_req)", "Emniyet", f"{'UYGUN (GÜVENLİ)' if is_safe else 'YETERSİZ'}", "—", f"Emniyet Payı: +{max(0.0, t_eff - t_req):.2f} mm")
        ]

        if botas_rec > 0:
            result_rows.append((
                "BOTAŞ Şartnamesi Standart Et Kalınlığı",
                "t_BOTAŞ",
                f"{botas_rec:.2f}",
                "mm",
                res.get("botas_standard_label", "BOTAŞ Şartname Matrisi")
            ))

        for r_desc, r_sym, r_val, r_unit, r_rem in result_rows:
            ws.row_dimensions[r_curr].height = 20
            c1 = ws.cell(r_curr, 1, r_desc)
            c2 = ws.cell(r_curr, 2, r_sym)
            c3 = ws.cell(r_curr, 3, r_val)
            c4 = ws.cell(r_curr, 4, r_unit)
            c5 = ws.cell(r_curr, 5, r_rem)

            for cell in (c1, c2, c3, c4, c5):
                cell.font = font_regular
                cell.border = border_all
                cell.alignment = align_left

            c2.alignment = align_center
            c2.font = font_bold
            c3.alignment = align_center
            c3.font = font_mono
            c4.alignment = align_center

            if r_sym == "t_nom":
                c1.font = font_bold
                c3.font = Font(name="Arial", size=10, bold=True, color="1E3A8A")
                for cell in (c1, c2, c3, c4, c5):
                    cell.fill = fill_highlight

            if r_sym == "Emniyet":
                c3.font = font_badge_pass if is_safe else font_badge_fail
                c3.fill = fill_pass if is_safe else fill_fail

            r_curr += 1

        # Section 4: Available schedule series
        avail_thks = res.get("available_schedule_thicknesses", [])
        if avail_thks:
            r_curr += 1
            write_section_header(r_curr, f"4. İNCELENEN ÇAP İÇİN STANDART SCHEDULE KALINLIK SERİSİ ({res.get('schedule_standard_used', 'ASME')})")
            r_curr += 1
            thk_strs = [f"{float(x):.2f} mm" for x in avail_thks]
            series_str = " | ".join(thk_strs)
            ws.row_dimensions[r_curr].height = 22
            ws.merge_cells(f"A{r_curr}:E{r_curr}")
            c_ser = ws.cell(r_curr, 1, f"  Standart Seri: {series_str}")
            c_ser.font = font_mono
            c_ser.alignment = align_left
            for col in range(1, 6):
                ws.cell(r_curr, col).border = border_all
            r_curr += 1

        # Signatures
        r_curr += 2
        ws.row_dimensions[r_curr].height = 20
        ws.cell(r_curr, 1, "HAZIRLAYAN (Tasarım Mühendisi)").font = font_bold
        ws.cell(r_curr, 3, "KONTROL EDEN (Borulama Şefi)").font = font_bold
        ws.cell(r_curr, 5, "ONAYLAYAN (Baş Mühendis / İdare)").font = font_bold

        r_curr += 1
        ws.row_dimensions[r_curr].height = 30
        for col in (1, 3, 5):
            c = ws.cell(r_curr, col, "İmza / Tarih: ______________")
            c.font = font_info
            c.alignment = align_left

        # Widths
        widths = [36, 16, 26, 14, 46]
        for idx, w in enumerate(widths, 1):
            ws.column_dimensions[get_column_letter(idx)].width = w

        ws.freeze_panes = "A7"

        output = io.BytesIO()
        wb.save(output)
        output.seek(0)
        return output

    @staticmethod
    def export_sawh_geometry_report(
        sawh_data: Dict[str, Any],
        project_info: Optional[Dict[str, Any]] = None,
        pipe_info: Optional[Dict[str, Any]] = None,
        lang: str = "tr"
    ) -> io.BytesIO:
        """
        Exports official SAWH (Spiral Submerged-Arc Welded) Pipe Forming Geometry,
        Coil Strip Width Procurement & Forming Stand Engineering Calculation Sheet
        to a styled corporate Excel workbook.
        """
        if project_info is None:
            project_info = {}
        if pipe_info is None:
            pipe_info = {}

        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = "SAWH İmalat Geometrisi" if lang == "tr" else "SAWH Forming Geometry"
        ws.views.sheetView[0].showGridLines = True

        # Typography
        font_title = Font(name="Arial", size=13, bold=True, color="0F172A")
        font_sec = Font(name="Arial", size=10, bold=True, color="1E3A8A")
        font_info = Font(name="Arial", size=9, color="334155")
        font_header = Font(name="Arial", size=9, bold=True, color="FFFFFF")
        font_regular = Font(name="Arial", size=9, color="000000")
        font_mono = Font(name="Consolas", size=9, color="000000")
        font_mono_bold = Font(name="Consolas", size=9, bold=True, color="000000")
        font_bold = Font(name="Arial", size=9, bold=True, color="000000")
        font_badge_pass = Font(name="Arial", size=10, bold=True, color="065F46")
        font_badge_warn = Font(name="Arial", size=10, bold=True, color="92400E")
        font_badge_fail = Font(name="Arial", size=10, bold=True, color="991B1B")

        # Color Fills
        fill_header = PatternFill(start_color="1E3A8A", end_color="1E3A8A", fill_type="solid")
        fill_sec = PatternFill(start_color="F1F5F9", end_color="F1F5F9", fill_type="solid")
        fill_pass = PatternFill(start_color="D1FAE5", end_color="D1FAE5", fill_type="solid")
        fill_warn = PatternFill(start_color="FEF3C7", end_color="FEF3C7", fill_type="solid")
        fill_fail = PatternFill(start_color="FEE2E2", end_color="FEE2E2", fill_type="solid")
        fill_zebra = PatternFill(start_color="F8FAFC", end_color="F8FAFC", fill_type="solid")
        fill_highlight = PatternFill(start_color="E0F2FE", end_color="E0F2FE", fill_type="solid")

        # Borders
        border_thin = Side(border_style="thin", color="CBD5E1")
        border_all = Border(left=border_thin, right=border_thin, top=border_thin, bottom=border_thin)

        # Alignments
        align_center = Alignment(horizontal="center", vertical="center", wrap_text=True)
        align_left = Alignment(horizontal="left", vertical="center", wrap_text=True)
        align_right = Alignment(horizontal="right", vertical="center", wrap_text=True)

        # -------------------------------------------------------------
        # Row 1: Document Title Header
        # -------------------------------------------------------------
        ws.row_dimensions[1].height = 26
        title_text = (
            "SAWH SPİRAL İMALAT GEOMETRİSİ VE RULO SAC (BANT) HESAP FÖYÜ"
            if lang == "tr"
            else "SAWH SPIRAL FORMING GEOMETRY & COIL STRIP SPECIFICATION SHEET"
        )
        ws.merge_cells("A1:E1")
        ws.cell(1, 1, title_text).font = font_title
        ws.cell(1, 1).alignment = align_left

        # Row 2: Subtitle & Standards
        p_name = project_info.get("project_name", "Doğal Gaz / Petrol Boru Hattı Projesi")
        p_no = project_info.get("project_no", "PRJ-SAWH-2026")
        p_client = project_info.get("client", "BOTAŞ / İdare")
        p_date = project_info.get("revision_date", "2026-10-09")
        std_type = pipe_info.get("standard_type", "BOTAŞ / API 5L")
        grade = pipe_info.get("material_grade", "X65")
        d_inch = pipe_info.get("diameter_inch", '48"')

        meta_str = f"Proje: {p_name} ({p_no}) | Standart: {std_type} | Çelik Kalitesi: {grade} ({d_inch}) | Müşteri: {p_client} | Tarih: {p_date}"
        ws.row_dimensions[2].height = 18
        ws.merge_cells("A2:E2")
        ws.cell(2, 1, meta_str).font = font_info
        ws.cell(2, 1).alignment = align_left

        # Row 4: Status Verdict Banner
        ws.row_dimensions[4].height = 28
        is_valid = sawh_data.get("valid", True)
        alpha_val = float(sawh_data.get("helix_angle_deg", 45.0) or 45.0)

        if is_valid:
            status_text = (
                f"GENEL İMALAT UYGUNLUK KARARI: UYGUN (PASS) — Helis Açısı (α = {alpha_val:.1f}°) ve Sac Genişliği Standart SAWH Sınırları İçinde [30°, 65°]"
                if lang == "tr"
                else f"OVERALL MANUFACTURING VERDICT: ACCEPTED (PASS) — Helix Angle (α = {alpha_val:.1f}°) within SAWH standard range [30°, 65°]"
            )
            v_font = font_badge_pass
            v_fill = fill_pass
        else:
            status_text = (
                f"GENEL İMALAT UYGUNLUK KARARI: ÖZEL TASARIM (UYARI) — Helis Açısı (α = {alpha_val:.1f}°) Önerilen [30°, 65°] Aralığının Dışında"
                if lang == "tr"
                else f"OVERALL MANUFACTURING VERDICT: OUT OF RANGE (WARNING) — Helix Angle (α = {alpha_val:.1f}°) outside standard limits [30°, 65°]"
            )
            v_font = font_badge_warn
            v_fill = fill_warn

        ws.merge_cells("A4:E4")
        c_verdict = ws.cell(4, 1, f"  {status_text}")
        c_verdict.font = v_font
        c_verdict.fill = v_fill
        c_verdict.alignment = align_left
        for col in range(1, 6):
            ws.cell(4, col).border = border_all

        # Helper writer closures
        def write_section_header(row_num: int, text: str):
            ws.row_dimensions[row_num].height = 20
            ws.merge_cells(f"A{row_num}:E{row_num}")
            cell = ws.cell(row_num, 1, f"  {text}")
            cell.font = font_sec
            cell.fill = fill_sec
            cell.alignment = align_left
            for c_idx in range(1, 6):
                ws.cell(row_num, c_idx).border = border_all

        def write_table_header(row_num: int, col_titles: list):
            ws.row_dimensions[row_num].height = 22
            for idx, title in enumerate(col_titles, 1):
                cell = ws.cell(row_num, idx, title)
                cell.font = font_header
                cell.fill = fill_header
                cell.alignment = align_center if idx in (2, 3, 4) else align_left
                cell.border = border_all

        # Data extraction
        d_val = float(sawh_data.get("d_mm", 1219.0) or 1219.0)
        t_val = float(sawh_data.get("t_mm", 14.30) or 14.30)
        dm_val = float(sawh_data.get("d_mid_mm", d_val - t_val) or (d_val - t_val))
        din_val = float(sawh_data.get("d_in_mm", d_val - 2 * t_val) or (d_val - 2 * t_val))
        pid_val = float(sawh_data.get("perimeter_mid_mm", math.pi * dm_val) or (math.pi * dm_val))
        b_val = float(sawh_data.get("strip_width_mm", 2000.0) or 2000.0)
        milling_val = float(sawh_data.get("edge_milling_allowance_mm", 15.0) or 15.0)
        bgross_val = float(sawh_data.get("strip_width_gross_mm", b_val + milling_val) or (b_val + milling_val))
        pitch_val = sawh_data.get("pitch_mm")
        bmin_val = float(sawh_data.get("b_min_mm", 0.0) or 0.0)
        bmax_val = float(sawh_data.get("b_max_mm", 0.0) or 0.0)
        strip_len_val = sawh_data.get("strip_length_per_meter_pipe")
        weld_len_val = sawh_data.get("weld_length_per_meter_pipe")
        weight_nom_val = float(sawh_data.get("weight_nominal_kg_m", 0.0) or 0.0)
        stress_factor_val = float(sawh_data.get("seam_stress_factor", 0.85) or 0.85)
        stress_reduct_val = float(sawh_data.get("seam_stress_reduction_percent", 15.0) or 15.0)

        # -------------------------------------------------------------
        # Section 1: Pipe Geometry
        # -------------------------------------------------------------
        r_curr = 6
        write_section_header(r_curr, "1. BORU TEMEL GEOMETRİSİ & NÖTR EKSEN (PIPE NOMINAL GEOMETRY)")
        r_curr += 1

        headers_s1 = ["Parametre Açıklaması", "Değer", "Birim", "Şartname / Sınır", "Mühendislik Formülü & Teknik Not"]
        write_table_header(r_curr, headers_s1)
        r_curr += 1

        sec1_rows = [
            ("Boru Dış Çapı (Nominal OD - D)", f"{d_val:.2f}", "mm", f"{d_inch} (API 5L)", "Boru nominal dış çapı"),
            ("Nominal Et Kalınlığı (t)", f"{t_val:.2f}", "mm", "Standart / Sipariş", "Nominal cidar et kalınlığı"),
            ("Orta Lif / Nötr Eksen Çapı (D_mid)", f"{dm_val:.2f}", "mm", "Hesaplanan", "D_mid = D − t (Büküm nötr lif ekseni)"),
            ("Boru İç Çapı (Nominal ID - D_in)", f"{din_val:.2f}", "mm", "Hesaplanan", "D_in = D − 2t (Akış kesit iç çapı)"),
            ("Orta Lif Çevre Açınımı (π · D_mid)", f"{pid_val:.2f}", "mm", "Hesaplanan", "C_mid = π · D_mid (Açınmış sac plaka boyu)"),
            ("Boru Birim Ağırlığı (Teorik W_nom)", f"{weight_nom_val:.2f}", "kg/m", "API 5L Tablo 9", "W = (D − t) · t · 0.0246615 kg/m"),
        ]

        for i, (param, val, unit, req, notes) in enumerate(sec1_rows):
            ws.row_dimensions[r_curr].height = 20
            c_fill = fill_zebra if i % 2 == 1 else None

            c1 = ws.cell(r_curr, 1, param); c1.font = font_bold; c1.alignment = align_left
            c2 = ws.cell(r_curr, 2, val); c2.font = font_mono_bold; c2.alignment = align_center
            c3 = ws.cell(r_curr, 3, unit); c3.font = font_regular; c3.alignment = align_center
            c4 = ws.cell(r_curr, 4, req); c4.font = font_info; c4.alignment = align_center
            c5 = ws.cell(r_curr, 5, notes); c5.font = font_info; c5.alignment = align_left

            for col in range(1, 6):
                cell = ws.cell(r_curr, col)
                cell.border = border_all
                if c_fill: cell.fill = c_fill
            r_curr += 1

        # -------------------------------------------------------------
        # Section 2: Forming Stand Geometry
        # -------------------------------------------------------------
        r_curr += 1
        write_section_header(r_curr, "2. SPİRAL ŞEKİLLENDİRME & HELİS AÇISI (FORMING STAND GEOMETRY)")
        r_curr += 1
        write_table_header(r_curr, headers_s1)
        r_curr += 1

        sec2_rows = [
            ("Şekillendirme / Helis Açısı (α)", f"{alpha_val:.2f}", "derece (°)", "30.0° – 65.0°", "α = arccos(B / (π · D_mid))"),
            ("Spiral Hatve / Adım (Pitch - P)", f"{pitch_val:.1f}" if pitch_val else "—", "mm", "Hesaplanan", "P = π · D_mid · cot(α) (1 turda eksenel ilerleme)"),
            ("Standart Pratik Açı Sınırları", "30.0° – 65.0°", "derece (°)", "Önerilen Aralık", "Optimum 40°–55° (Spiral gerilme dağılım dengesi)"),
            ("Şekillendirme Uygunluk Durumu", "UYGUN" if is_valid else "ARALIK DIŞI", "—", "API 5L / İmalat", "Helis açısı pratik şekillendirme sınırları kontrolü"),
        ]

        for i, (param, val, unit, req, notes) in enumerate(sec2_rows):
            ws.row_dimensions[r_curr].height = 20
            c_fill = fill_zebra if i % 2 == 1 else None

            c1 = ws.cell(r_curr, 1, param); c1.font = font_bold; c1.alignment = align_left
            c2 = ws.cell(r_curr, 2, val); c2.font = font_mono_bold; c2.alignment = align_center
            if param.startswith("Şekillendirme Uygunluk"):
                c2.fill = fill_pass if is_valid else fill_warn
                c2.font = font_badge_pass if is_valid else font_badge_warn

            c3 = ws.cell(r_curr, 3, unit); c3.font = font_regular; c3.alignment = align_center
            c4 = ws.cell(r_curr, 4, req); c4.font = font_info; c4.alignment = align_center
            c5 = ws.cell(r_curr, 5, notes); c5.font = font_info; c5.alignment = align_left

            for col in range(1, 6):
                cell = ws.cell(r_curr, col)
                cell.border = border_all
                if c_fill and not cell.fill.start_color.rgb: cell.fill = c_fill
            r_curr += 1

        # -------------------------------------------------------------
        # Section 3: Coil Strip Procurement Dimensions
        # -------------------------------------------------------------
        r_curr += 1
        write_section_header(r_curr, "3. RULO SAC (BANT) TEDARİK VE SİPARİŞ BOYUTLARI (COIL STRIP PROCUREMENT)")
        r_curr += 1
        write_table_header(r_curr, headers_s1)
        r_curr += 1

        sec3_rows = [
            ("Net Şerit Genişliği (B_net)", f"{b_val:.2f}", "mm", "Teorik Net", "B = π · D_mid · cos(α) (Boru gövdesini oluşturan net en)"),
            ("Kenar Frezeleme / Tıraşlama Payı", f"{milling_val:.2f}", "mm", "İmalat Payı", "Kaynak ağzı frezesi için iki kenardan talaş payı (2 x 7.5 mm)"),
            ("Sipariş Brüt Bant Genişliği (B_brüt)", f"{bgross_val:.2f}", "mm", "HRC Sipariş", "B_brüt = B_net + Freze Payı (Çelikhaneye sipariş genişliği)"),
            ("İzin Verilen Min. Bant Genişliği (B_min)", f"{bmin_val:.2f}", "mm", "α = 65° İle", "B_min = π · D_mid · cos(65°) (Üst açı sınırı için min sac)"),
            ("İzin Verilen Maks. Bant Genişliği (B_max)", f"{bmax_val:.2f}", "mm", "α = 30° İle", "B_max = π · D_mid · cos(30°) (Alt açı sınırı için max sac)"),
            ("1 m Boru İçin Sac Sarfiyat Metrajı (L_şerit)", f"{strip_len_val:.4f}" if strip_len_val else "—", "m / m boru", "Hesaplanan", "L_şerit = 1 / sin(α) (1 m boru için tüketilen rulo boyu)"),
            ("1 m Boru Başına Kaynak Dikiş Uzunluğu", f"{weld_len_val:.4f}" if weld_len_val else "—", "m / m boru", "Hesaplanan", "L_kaynak = 1 / sin(α) (Toplam spiral dikiş uzunluğu)"),
        ]

        for i, (param, val, unit, req, notes) in enumerate(sec3_rows):
            ws.row_dimensions[r_curr].height = 20
            c_fill = fill_highlight if "Sipariş Brüt Bant" in param else (fill_zebra if i % 2 == 1 else None)

            c1 = ws.cell(r_curr, 1, param); c1.font = font_bold; c1.alignment = align_left
            c2 = ws.cell(r_curr, 2, val); c2.font = font_mono_bold; c2.alignment = align_center
            c3 = ws.cell(r_curr, 3, unit); c3.font = font_regular; c3.alignment = align_center
            c4 = ws.cell(r_curr, 4, req); c4.font = font_info; c4.alignment = align_center
            c5 = ws.cell(r_curr, 5, notes); c5.font = font_info; c5.alignment = align_left

            for col in range(1, 6):
                cell = ws.cell(r_curr, col)
                cell.border = border_all
                if c_fill: cell.fill = c_fill
            r_curr += 1

        # -------------------------------------------------------------
        # Section 4: Helical Seam Stress Advantage
        # -------------------------------------------------------------
        r_curr += 1
        write_section_header(r_curr, "4. SPİRAL KAYNAK DİKİŞİ ASAL GERİLME ANALİZİ (STRESS REDUCTION ADVANTAGE)")
        r_curr += 1
        write_table_header(r_curr, headers_s1)
        r_curr += 1

        sec4_rows = [
            ("Çevresel Asal Gerilme (Hoop Stress - σ_h)", "1.0000 · σ_h", "MPa", "Referans %100", "σ_h = (P · D) / (2t) (İç basınçtan oluşan teğetsel gerilme)"),
            ("Spiral Dikiş Normal Gerilme Çarpanı", f"{stress_factor_val:.4f}", "—", f"σ_w / σ_h = {stress_factor_val:.4f}", "σ_w = σ_h · (1 − 0.5·cos²α) = σ_h · (sin²α + 0.5·cos²α)"),
            ("Dikişteki Asal Gerilme İndirgemesi", f"% {stress_reduct_val:.1f}", "oran (%)", "Güvenlik Kazancı", "Düz dikişli (ERW/LSAW) boruya kıyasla dikişe binen yük azalması"),
        ]

        for i, (param, val, unit, req, notes) in enumerate(sec4_rows):
            ws.row_dimensions[r_curr].height = 20
            c_fill = fill_pass if "Gerilme İndirgemesi" in param else (fill_zebra if i % 2 == 1 else None)

            c1 = ws.cell(r_curr, 1, param); c1.font = font_bold; c1.alignment = align_left
            c2 = ws.cell(r_curr, 2, val); c2.font = font_mono_bold; c2.alignment = align_center
            c3 = ws.cell(r_curr, 3, unit); c3.font = font_regular; c3.alignment = align_center
            c4 = ws.cell(r_curr, 4, req); c4.font = font_info; c4.alignment = align_center
            c5 = ws.cell(r_curr, 5, notes); c5.font = font_info; c5.alignment = align_left

            for col in range(1, 6):
                cell = ws.cell(r_curr, col)
                cell.border = border_all
                if c_fill: cell.fill = c_fill
            r_curr += 1

        # -------------------------------------------------------------
        # Section 5: Skelp End Weld Analysis & Safety Clearance (API 5L 8.10)
        # -------------------------------------------------------------
        coil_len_val = float(sawh_data.get("coil_length_m", 800.0) or 800.0)
        pipe_len_val = float(sawh_data.get("pipe_length_m", 12.0) or 12.0)
        total_pipe_len_val = float(sawh_data.get("total_pipe_length_per_coil_m", 0.0) or 0.0)
        pipes_count_val = int(sawh_data.get("pipes_per_coil_count", 0) or 0)
        skelp_pos_val = float(sawh_data.get("skelp_weld_position_in_pipe_m", 0.0) or 0.0)
        skelp_dist_mm_val = float(sawh_data.get("skelp_weld_distance_to_nearest_end_mm", 0.0) or 0.0)
        skelp_axial_span_val = float(sawh_data.get("skelp_weld_axial_span_mm", 0.0) or 0.0)
        min_skelp_dist_val = float(sawh_data.get("min_skelp_end_distance_mm", 300.0) or 300.0)
        skelp_safe = bool(sawh_data.get("skelp_weld_safe", True))
        skelp_status = str(sawh_data.get("skelp_weld_status", "PASS"))
        skelp_note = str(sawh_data.get("skelp_weld_note", ""))

        r_curr += 1
        write_section_header(r_curr, "5. BOBİN UÇ KAYNAĞI VE BORU UCUNA MESAFE KONTROLÜ (API 5L 8.10 SKELP END WELD)")
        r_curr += 1
        write_table_header(r_curr, headers_s1)
        r_curr += 1

        sec5_rows = [
            ("Rulo Bobin Uzunluğu (L_bobin)", f"{coil_len_val:.1f}", "m", "HRC Bobin Boyu", "Tedarik edilen sıcak haddelenmiş rulo sac uzunluğu"),
            ("Hedef Boru Üretim Kesim Boyu (L_boru)", f"{pipe_len_val:.2f}", "m", "Nominal Boru Boyu", "Otomatik uç kesme testeresi hedef boyu (örn. 12.00 m)"),
            ("1 Bobinden Üretilen Boru Adedi", f"{pipes_count_val} adet ({total_pipe_len_val:.1f} m)", "adet", "Hesaplanan", "L_toplam = L_bobin · sin(α) üzerinden net boru verimi"),
            ("Uç Kaynağı Konumu (Geçiş Borusunda)", f"{skelp_pos_val:.3f}", "m", "Boru Başına Göre", "Ek dikişinin geçiş borusu gövdesi üzerindeki eksenel mesafesi"),
            ("En Yakın Boru Alnına Olan Mesafe (d_min)", f"{skelp_dist_mm_val:.1f}", "mm", f"≥ {min_skelp_dist_val:.0f}.0 mm (API 5L 8.10)", "Boru ucu kaynak ağzına (pahına) olan en yakın eksenel emniyet mesafesi"),
            ("Eksenel Helis İntikal Boyu (ΔL)", f"{skelp_axial_span_val:.1f}", "mm", "Geometrik İntikal", "ΔL = 0.5 · π · D_mid · sin(2α) (Bant eninin boru eksenindeki iz düşümü)"),
            ("API 5L Madde 8.10 Emniyet Kararı", "UYGUN (PASS)" if skelp_safe else "UYARI / KIRPMA", "—", "Min 300 mm Kuralı", skelp_note),
        ]

        for i, (param, val, unit, req, notes) in enumerate(sec5_rows):
            ws.row_dimensions[r_curr].height = 20
            c_fill = (fill_pass if skelp_safe else fill_fail) if "Emniyet Kararı" in param else (fill_zebra if i % 2 == 1 else None)

            c1 = ws.cell(r_curr, 1, param); c1.font = font_bold; c1.alignment = align_left
            c2 = ws.cell(r_curr, 2, val); c2.font = font_mono_bold; c2.alignment = align_center
            if "Emniyet Kararı" in param:
                c2.fill = fill_pass if skelp_safe else fill_fail
                c2.font = font_badge_pass if skelp_safe else font_badge_fail

            c3 = ws.cell(r_curr, 3, unit); c3.font = font_regular; c3.alignment = align_center
            c4 = ws.cell(r_curr, 4, req); c4.font = font_info; c4.alignment = align_center
            c5 = ws.cell(r_curr, 5, notes); c5.font = font_info; c5.alignment = align_left

            for col in range(1, 6):
                cell = ws.cell(r_curr, col)
                cell.border = border_all
                if c_fill and not cell.fill.start_color.rgb: cell.fill = c_fill
            r_curr += 1

        # -------------------------------------------------------------
        # Section 6: Standard Provisions & Rules
        # -------------------------------------------------------------
        r_curr += 1
        write_section_header(r_curr, "6. STANDART ŞARTNAME HÜKÜMLERİ VE İMALAT KURALLARI (API 5L / BOTAŞ PROVISIONS)")
        r_curr += 1

        prov_rows = [
            ("API 5L Madde 8.10 (Bobin Uç Kaynağı - Skelp End Weld):", "Bobin/rulo uç birleştirme kaynağı, boru uçlarından (alından) en az 300 mm uzakta konumlandırılmalıdır. Uç kaynakları en az 50 bobinde bir çekme, CVN ve bükme testlerine tabi tutulur."),
            ("API 5L Madde 9.7 & 10.2.4.6 (Kılavuzlu Bükme Testi):", "Spiral kaynak dikişinden alınan kök ve kapak bükme numunelerinde 180° büküm sonrasında kaynak veya füzyon hattında 3.2 mm'yi aşan çatlak/kusur bulunamaz."),
            ("API 5L Tablo 18 / BOTAŞ Madde 3.3 (Kaynak Çekme Dayanımı):", "Spiral kaynak dikişi enine çekme testinde belirlenen çekme dayanımı, boru gövde malzemesi için şart koşulan minimum çekme dayanımından (SMTS) düşük olamaz."),
            ("API 5L Tablo 18 / BOTAŞ Madde 8.8 (Kaynak Geometrisi & NDT):", "Kaynak dikişi radyal ofset (kayma) sınırı max 1.50 mm; iç/dış paso takviye yüksekliği max 3.50 mm (t ≤ 15 mm için); on-line UT + off-line RT muayenesi %100 zorunludur."),
        ]

        for p_title, p_desc in prov_rows:
            ws.row_dimensions[r_curr].height = 24
            ws.cell(r_curr, 1, p_title).font = font_bold
            ws.cell(r_curr, 1).alignment = align_left
            ws.cell(r_curr, 1).border = border_all

            ws.merge_cells(f"B{r_curr}:E{r_curr}")
            c_desc = ws.cell(r_curr, 2, f"  {p_desc}")
            c_desc.font = font_info
            c_desc.alignment = align_left
            for col in range(2, 6):
                ws.cell(r_curr, col).border = border_all
            r_curr += 1

        # -------------------------------------------------------------
        # Section 7: Engineering Sign-off
        # -------------------------------------------------------------
        r_curr += 2
        ws.row_dimensions[r_curr].height = 20
        ws.cell(r_curr, 1, "HAZIRLAYAN (İmalat Mühendisi)").font = font_bold
        ws.cell(r_curr, 3, "KONTROL EDEN (Kalite Güvence / Kaynak Şefi)").font = font_bold
        ws.cell(r_curr, 5, "ONAYLAYAN (Fabrika Müdürü / İdare Temsilcisi)").font = font_bold

        r_curr += 1
        ws.row_dimensions[r_curr].height = 32
        for col in (1, 3, 5):
            c = ws.cell(r_curr, col, "İmza / Kaşe / Tarih: ____________________")
            c.font = font_info
            c.alignment = align_left

        # Column widths
        widths = [42, 18, 14, 24, 52]
        for idx, w in enumerate(widths, 1):
            ws.column_dimensions[get_column_letter(idx)].width = w

        ws.freeze_panes = "A6"

        output = io.BytesIO()
        wb.save(output)
        output.seek(0)
        return output

    @staticmethod
    def export_sawl_geometry_report(
        sawl_data: Dict[str, Any],
        project_info: Optional[Dict[str, Any]] = None,
        pipe_info: Optional[Dict[str, Any]] = None,
        lang: str = "tr"
    ) -> io.BytesIO:
        """
        Exports official SAWL (Submerged-Arc Welded Longitudinal) Pipe JCOE Forming Geometry,
        Heavy Steel Plate Procurement Sizing & Mechanical Expander Calibration Sheet
        to a styled corporate Excel workbook.
        """
        if project_info is None:
            project_info = {}
        if pipe_info is None:
            pipe_info = {}

        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = "SAWL İmalat Geometrisi" if lang == "tr" else "SAWL Forming Geometry"
        ws.views.sheetView[0].showGridLines = True

        # Typography
        font_title = Font(name="Arial", size=13, bold=True, color="0F172A")
        font_sec = Font(name="Arial", size=10, bold=True, color="312E81")
        font_info = Font(name="Arial", size=9, color="334155")
        font_header = Font(name="Arial", size=9, bold=True, color="FFFFFF")
        font_regular = Font(name="Arial", size=9, color="000000")
        font_mono_bold = Font(name="Consolas", size=9, bold=True, color="000000")
        font_bold = Font(name="Arial", size=9, bold=True, color="000000")
        font_badge_pass = Font(name="Arial", size=10, bold=True, color="065F46")
        font_badge_warn = Font(name="Arial", size=10, bold=True, color="92400E")

        # Color Fills
        fill_header = PatternFill(start_color="312E81", end_color="312E81", fill_type="solid")
        fill_sec = PatternFill(start_color="EEF2FF", end_color="EEF2FF", fill_type="solid")
        fill_pass = PatternFill(start_color="D1FAE5", end_color="D1FAE5", fill_type="solid")
        fill_warn = PatternFill(start_color="FEF3C7", end_color="FEF3C7", fill_type="solid")
        fill_zebra = PatternFill(start_color="F8FAFC", end_color="F8FAFC", fill_type="solid")
        fill_highlight = PatternFill(start_color="E0E7FF", end_color="E0E7FF", fill_type="solid")

        # Borders
        border_thin = Side(border_style="thin", color="CBD5E1")
        border_all = Border(left=border_thin, right=border_thin, top=border_thin, bottom=border_thin)

        # Alignments
        align_center = Alignment(horizontal="center", vertical="center", wrap_text=True)
        align_left = Alignment(horizontal="left", vertical="center", wrap_text=True)

        # -------------------------------------------------------------
        # Row 1: Document Title Header
        # -------------------------------------------------------------
        ws.row_dimensions[1].height = 26
        title_text = (
            "SAWL BOYUNA KAYNAKLI BORU İMALAT GEOMETRİSİ, PLAKA TEDARİK VE JCOE HESAP FÖYÜ"
            if lang == "tr"
            else "SAWL LONGITUDINAL PIPE JCOE FORMING & PLATE SPECIFICATION SHEET"
        )
        ws.merge_cells("A1:E1")
        ws.cell(1, 1, title_text).font = font_title
        ws.cell(1, 1).alignment = align_left

        # Row 2: Subtitle & Project Metadata
        p_name = project_info.get("project_name", "Doğal Gaz / Petrol Boru Hattı Projesi")
        p_no = project_info.get("project_no", "PRJ-SAWL-2026")
        p_client = project_info.get("client", "BOTAŞ / İdare")
        p_date = project_info.get("revision_date", "2026-10-09")
        std_type = pipe_info.get("standard_type", "BOTAŞ / API 5L")
        grade = pipe_info.get("material_grade", "X65")
        d_inch = pipe_info.get("diameter_inch", '48"')

        meta_str = f"Proje: {p_name} ({p_no}) | Standart: {std_type} | Çelik Kalitesi: {grade} ({d_inch}) | Müşteri: {p_client} | Tarih: {p_date}"
        ws.row_dimensions[2].height = 18
        ws.merge_cells("A2:E2")
        ws.cell(2, 1, meta_str).font = font_info
        ws.cell(2, 1).alignment = align_left

        # Row 4: Status Verdict Banner
        ws.row_dimensions[4].height = 28
        er_valid = sawl_data.get("expansion_valid", True)
        er_pct = float(sawl_data.get("expansion_ratio_pct", 1.0) or 1.0)

        if er_valid:
            status_text = (
                f"GENEL İMALAT UYGUNLUK KARARI: UYGUN (PASS) — JCOE Şekillendirme ve Mekanik Genişletme Oranı (%ER = %{er_pct:.2f}) API 5L 8.9 Sınırları İçinde [%0.8, %1.5]"
                if lang == "tr"
                else f"OVERALL MANUFACTURING VERDICT: ACCEPTED (PASS) — Mechanical Expansion Ratio (%ER = %{er_pct:.2f}) within API 5L 8.9 range [%0.8, %1.5]"
            )
            v_font = font_badge_pass
            v_fill = fill_pass
        else:
            status_text = (
                f"GENEL İMALAT UYGUNLUK KARARI: UYARI — Mekanik Genişletme Oranı (%ER = %{er_pct:.2f}) API 5L 8.9 Sınırları Dışında"
                if lang == "tr"
                else f"OVERALL MANUFACTURING VERDICT: WARNING — Mechanical Expansion Ratio (%ER = %{er_pct:.2f}) outside API 5L limits"
            )
            v_font = font_badge_warn
            v_fill = fill_warn

        ws.merge_cells("A4:E4")
        c_verdict = ws.cell(4, 1, f"  {status_text}")
        c_verdict.font = v_font
        c_verdict.fill = v_fill
        c_verdict.alignment = align_left
        for col in range(1, 6):
            ws.cell(4, col).border = border_all

        # Helper closures
        def write_section_header(row_num: int, text: str):
            ws.row_dimensions[row_num].height = 20
            ws.merge_cells(f"A{row_num}:E{row_num}")
            cell = ws.cell(row_num, 1, f"  {text}")
            cell.font = font_sec
            cell.fill = fill_sec
            cell.alignment = align_left
            for c_idx in range(1, 6):
                ws.cell(row_num, c_idx).border = border_all

        def write_table_header(row_num: int, col_titles: list):
            ws.row_dimensions[row_num].height = 22
            for idx, title in enumerate(col_titles, 1):
                cell = ws.cell(row_num, idx, title)
                cell.font = font_header
                cell.fill = fill_header
                cell.alignment = align_center if idx in (2, 3, 4) else align_left
                cell.border = border_all

        # Data extraction
        d_val = float(sawl_data.get("d_mm", 1219.0) or 1219.0)
        t_val = float(sawl_data.get("t_mm", 14.30) or 14.30)
        dm_val = float(sawl_data.get("d_mid_mm", d_val - t_val) or (d_val - t_val))
        din_val = float(sawl_data.get("d_in_mm", d_val - 2 * t_val) or (d_val - 2 * t_val))
        pipe_len_val = float(sawl_data.get("pipe_length_m", 12.0) or 12.0)
        wnet_val = float(sawl_data.get("plate_width_net_mm", math.pi * dm_val) or (math.pi * dm_val))
        milling_val = float(sawl_data.get("edge_milling_allowance_mm", 30.0) or 30.0)
        wgross_val = float(sawl_data.get("plate_width_gross_mm", wnet_val + milling_val) or (wnet_val + milling_val))
        plate_len_val = float(sawl_data.get("plate_length_m", pipe_len_val) or pipe_len_val)
        mnet_val = float(sawl_data.get("plate_weight_net_kg", 0.0) or 0.0)
        mgross_val = float(sawl_data.get("plate_weight_gross_kg", 0.0) or 0.0)
        scrap_kg_val = float(sawl_data.get("milling_scrap_kg", 0.0) or 0.0)
        scrap_pct_val = float(sawl_data.get("milling_scrap_percent", 0.0) or 0.0)
        weight_nom_m = float(sawl_data.get("weight_nominal_kg_m", 0.0) or 0.0)
        weight_nom_pipe = float(sawl_data.get("weight_nominal_pipe_kg", 0.0) or 0.0)

        # Expander data
        dasformed_val = float(sawl_data.get("d_as_formed_mm", 0.0) or 0.0)
        deltad_val = float(sawl_data.get("delta_d_mm", 0.0) or 0.0)
        deltac_val = float(sawl_data.get("delta_perimeter_mm", 0.0) or 0.0)
        er_note = str(sawl_data.get("expansion_note", ""))

        # JCOE data
        crimp_r_val = float(sawl_data.get("crimp_radius_mm", dm_val / 2.0) or (dm_val / 2.0))
        c_steps = int(sawl_data.get("c_steps_count", 22) or 22)
        o_steps = int(sawl_data.get("o_steps_count", 22) or 22)
        seam_gap = float(sawl_data.get("seam_gap_target_mm", 0.8) or 0.8)
        weld_wire_kg = float(sawl_data.get("weld_wire_total_kg", 0.0) or 0.0)

        headers_common = ["Parametre Açıklaması", "Değer", "Birim", "Şartname / Sınır", "Mühendislik Formülü & Teknik Not"]

        # -------------------------------------------------------------
        # Section 1: Pipe Nominal Geometry
        # -------------------------------------------------------------
        r_curr = 6
        write_section_header(r_curr, "1. BORU TEMEL GEOMETRİSİ & NÖTR EKSEN (PIPE NOMINAL GEOMETRY)")
        r_curr += 1
        write_table_header(r_curr, headers_common)
        r_curr += 1

        sec1_rows = [
            ("Boru Dış Çapı (Nominal OD - D)", f"{d_val:.2f}", "mm", f"{d_inch} (API 5L)", "Boru nominal dış çapı"),
            ("Nominal Et Kalınlığı (t)", f"{t_val:.2f}", "mm", "Standart / Sipariş", "Nominal cidar et kalınlığı"),
            ("Orta Lif / Büküm Eksen Çapı (D_mid)", f"{dm_val:.2f}", "mm", "Hesaplanan", "D_mid = D − t (Nötr lif büküm ekseni)"),
            ("Boru İç Çapı (Nominal ID - D_in)", f"{din_val:.2f}", "mm", "Hesaplanan", "D_in = D − 2t (Akış kesit iç çapı)"),
            ("Boru Üretim Boyu (L_boru)", f"{pipe_len_val:.2f}", "m", "Nominal Boy", "Bitmiş boru boyu (örn. 12.00 m)"),
            ("Birim Ağırlık (Teorik W_nom)", f"{weight_nom_m:.2f}", "kg/m", "API 5L Tablo 9", "W = (D − t) · t · 0.0246615 kg/m"),
            ("Boru Başına Nominal Ağırlık", f"{weight_nom_pipe:.1f}", "kg / boru", "Hesaplanan", "Tek bir bitmiş borunun teorik kütlesi"),
        ]

        for i, (param, val, unit, req, notes) in enumerate(sec1_rows):
            ws.row_dimensions[r_curr].height = 20
            c_fill = fill_zebra if i % 2 == 1 else None
            c1 = ws.cell(r_curr, 1, param); c1.font = font_bold; c1.alignment = align_left
            c2 = ws.cell(r_curr, 2, val); c2.font = font_mono_bold; c2.alignment = align_center
            c3 = ws.cell(r_curr, 3, unit); c3.font = font_regular; c3.alignment = align_center
            c4 = ws.cell(r_curr, 4, req); c4.font = font_info; c4.alignment = align_center
            c5 = ws.cell(r_curr, 5, notes); c5.font = font_info; c5.alignment = align_left
            for col in range(1, 6):
                cell = ws.cell(r_curr, col); cell.border = border_all
                if c_fill: cell.fill = c_fill
            r_curr += 1

        # -------------------------------------------------------------
        # Section 2: Plate Procurement Sizing
        # -------------------------------------------------------------
        r_curr += 1
        write_section_header(r_curr, "2. ÇELİK PLAKA TEDARİK VE SİPARİŞ ÖLÇÜLERİ (HEAVY STEEL PLATE PROCUREMENT)")
        r_curr += 1
        write_table_header(r_curr, headers_common)
        r_curr += 1

        sec2_rows = [
            ("Net Plaka Genişliği (W_net)", f"{wnet_val:.2f}", "mm", "Açınım Çevresi", "W_net = π · D_mid (Boru silindirini ve çevresini oluşturan en)"),
            ("Kenar Freze / Planya Payı", f"{milling_val:.2f}", "mm", "İmalat Payı", "Kaynak ağzı açma için iki kenardan talaş payı (2 x 15 mm)"),
            ("Sipariş Brüt Plaka Genişliği (W_brüt)", f"{wgross_val:.2f}", "mm", "Plaka Sipariş", "W_brüt = W_net + Freze Payı (Haddehaneye sipariş eni)"),
            ("Plaka Sipariş Boyu (L_plaka)", f"{plate_len_val:.2f}", "m", "Nominal Boy", "L_plaka = L_boru (Tek boru için tam plaka boyu)"),
            ("Boyuna Kaynak Dikiş Uzunluğu (L_kaynak)", f"{pipe_len_val:.2f}", "m", "Boru Boyu", "L_kaynak = L_boru (Kaynak dikişi boru ekseni boyunca uzanır; plaka eni W_net ile aynı değildir)"),
            ("Brüt Plaka Ağırlığı (M_brüt)", f"{mgross_val:.1f}", "kg / plaka", "Sipariş Tonajı", "M_brüt = W_brüt · L · t · ρ · 10⁻⁶ (ρ = 7850 kg/m³)"),
            ("Net Plaka Ağırlığı (M_net)", f"{mnet_val:.1f}", "kg / plaka", "Boru Gövdesi", "M_net = W_net · L · t · ρ · 10⁻⁶"),
            ("Kenar Talaş / Freze Firesi", f"{scrap_kg_val:.1f} kg (%{scrap_pct_val:.2f})", "kg / fire", "Talaş Firesi", "Frezeleme işleminde çıkan kenar hurda miktarı"),
        ]

        for i, (param, val, unit, req, notes) in enumerate(sec2_rows):
            ws.row_dimensions[r_curr].height = 20
            c_fill = fill_highlight if "Sipariş Brüt Plaka" in param else (fill_zebra if i % 2 == 1 else None)
            c1 = ws.cell(r_curr, 1, param); c1.font = font_bold; c1.alignment = align_left
            c2 = ws.cell(r_curr, 2, val); c2.font = font_mono_bold; c2.alignment = align_center
            c3 = ws.cell(r_curr, 3, unit); c3.font = font_regular; c3.alignment = align_center
            c4 = ws.cell(r_curr, 4, req); c4.font = font_info; c4.alignment = align_center
            c5 = ws.cell(r_curr, 5, notes); c5.font = font_info; c5.alignment = align_left
            for col in range(1, 6):
                cell = ws.cell(r_curr, col); cell.border = border_all
                if c_fill: cell.fill = c_fill
            r_curr += 1

        # -------------------------------------------------------------
        # Section 3: JCOE Cold Forming Process
        # -------------------------------------------------------------
        r_curr += 1
        write_section_header(r_curr, "3. JCOE SOĞUK ŞEKİLLENDİRME ADIMLARI (JCOE COLD FORMING PROCESS)")
        r_curr += 1
        write_table_header(r_curr, headers_common)
        r_curr += 1

        sec3_rows = [
            ("Soğuk Şekillendirme Yöntemi", "JCOE Presleme", "—", "Proses Tipi", "J-büküm, C-büküm, O-presi, Sürekli Punto, Çift Tozaltı Kaynak"),
            ("Kenar Kıvırma (J-Büküm) Radyüsü", f"{crimp_r_val:.1f}", "mm", "R ≈ D_mid / 2", "Plaka boyuna kenarlarının ilk radyusa bükülmesi"),
            ("C-Presi Kademeli Basma Adımı", f"{c_steps}", "adım (vuruş)", "Kademeli Pres", "Plakanın ilk yarısının 'C' formuna getirilmesi"),
            ("O-Presi Kapanma Basma Adımı", f"{o_steps}", "adım (vuruş)", "Kademeli Pres", "Plakanın ikinci yarısının basılarak açık 'O' silindirine dönüştürülmesi"),
            ("Kaynak Ağzı Boşluğu (Tack Gap)", f"{seam_gap:.1f}", "mm", "0.0 – 1.5 mm", "Sürekli CO2/MIG punto kaynağı öncesi dikiş aralığı"),
            ("Boyuna Dikiş Tipi (DSAW)", "Tek Boyuna Dikiş", "—", "API 5L SAWL", "1 Paso İç (ID) + 1 Paso Dış (OD) çok telli tozaltı ark kaynağı"),
            ("Tahmini Kaynak Teli Sarfiyatı", f"{weld_wire_kg:.1f}", "kg / boru", "Sarf Malzeme", "Çift paso SAW kaynak dikişi tel ve toz tüketimi"),
        ]

        for i, (param, val, unit, req, notes) in enumerate(sec3_rows):
            ws.row_dimensions[r_curr].height = 20
            c_fill = fill_zebra if i % 2 == 1 else None
            c1 = ws.cell(r_curr, 1, param); c1.font = font_bold; c1.alignment = align_left
            c2 = ws.cell(r_curr, 2, val); c2.font = font_mono_bold; c2.alignment = align_center
            c3 = ws.cell(r_curr, 3, unit); c3.font = font_regular; c3.alignment = align_center
            c4 = ws.cell(r_curr, 4, req); c4.font = font_info; c4.alignment = align_center
            c5 = ws.cell(r_curr, 5, notes); c5.font = font_info; c5.alignment = align_left
            for col in range(1, 6):
                cell = ws.cell(r_curr, col); cell.border = border_all
                if c_fill: cell.fill = c_fill
            r_curr += 1

        # -------------------------------------------------------------
        # Section 4: Mechanical Expansion (API 5L 8.9 & Annex E)
        # -------------------------------------------------------------
        r_curr += 1
        write_section_header(r_curr, "4. MEKANİK GENİŞLETİCİ (EXPANDER) VE KALINTI GERİLME ANALİZİ (API 5L 8.9 & EK E)")
        r_curr += 1
        write_table_header(r_curr, headers_common)
        r_curr += 1

        sec4_rows = [
            ("Mekanik Genişletme Oranı (%ER)", f"%{er_pct:.2f}", "oran (%)", "%0.8 – %1.5", "ER = (D_son − D_ham) / D_ham · 100 (API 5L Madde 8.9 & Tablo E.1)"),
            ("Şekillendirme Sonrası Ham Çap (D_ham)", f"{dasformed_val:.2f}", "mm", "Genişletme Öncesi", "D_ham = D / (1 + ER / 100) (O-presi ve kaynak sonrası ham çap)"),
            ("Radyal Kalıcı Plastik Genleşme (ΔD)", f"{deltad_val:.2f}", "mm", "Expander Strok", "ΔD = D_son − D_ham (Mekanik takozların radyal açılma miktarı)"),
            ("Çevresel Plastik Uzama (ΔC)", f"{deltac_val:.2f}", "mm", "Çevresel Açılma", "ΔC = π · ΔD (Plastik akma bölgesinde çevre artışı)"),
            ("Kalıntı Gerilme Sönümleme Etkisi", "%60 – %80 Azalma", "—", "Gerilme Giderme", "Büküm ve kaynak artık gerilmelerini homojenize eder"),
            ("Yuvarlaklık & Ovallik Kalibrasyonu", "Ovallik ≤ %0.5 D", "—", "API 5L 10.2.8", "Tüm boru boyu boyunca kusursuz dairesellik ve uç pabuç uyumu"),
            ("API 5L 8.9 Expander Uygunluk Kararı", "UYGUN (PASS)" if er_valid else "UYARI", "—", "%0.8 – %1.5 Sınırı", er_note),
        ]

        for i, (param, val, unit, req, notes) in enumerate(sec4_rows):
            ws.row_dimensions[r_curr].height = 20
            c_fill = (fill_pass if er_valid else fill_warn) if "Uygunluk Kararı" in param else (fill_zebra if i % 2 == 1 else None)
            c1 = ws.cell(r_curr, 1, param); c1.font = font_bold; c1.alignment = align_left
            c2 = ws.cell(r_curr, 2, val); c2.font = font_mono_bold; c2.alignment = align_center
            if "Uygunluk Kararı" in param:
                c2.fill = fill_pass if er_valid else fill_warn
                c2.font = font_badge_pass if er_valid else font_badge_warn
            c3 = ws.cell(r_curr, 3, unit); c3.font = font_regular; c3.alignment = align_center
            c4 = ws.cell(r_curr, 4, req); c4.font = font_info; c4.alignment = align_center
            c5 = ws.cell(r_curr, 5, notes); c5.font = font_info; c5.alignment = align_left
            for col in range(1, 6):
                cell = ws.cell(r_curr, col); cell.border = border_all
                if c_fill and not cell.fill.start_color.rgb: cell.fill = c_fill
            r_curr += 1

        # -------------------------------------------------------------
        # Section 5: Standard Provisions & Rules
        # -------------------------------------------------------------
        r_curr += 1
        write_section_header(r_curr, "5. STANDART ŞARTNAME HÜKÜMLERİ VE İMALAT KURALLARI (API 5L / BOTAŞ PROVISIONS)")
        r_curr += 1

        prov_rows = [
            ("API 5L Madde 8.9 & Ek E (Mekanik Genişletme Zorunluluğu):", "SAWL borularda kaynak sonrası mekanik genişletme (cold expansion) zorunludur. Genişletme oranı %0.8 ile %1.5 arasında tutulmalı; kalibratör takoz izleri boru iç yüzeyinde derin iz bırakmamalıdır."),
            ("API 5L Madde 9.7 & 10.2.4.6 (Kılavuzlu Bükme Testi):", "Boyuna kaynak dikişinden alınan kök ve kapak enine bükme numunelerinde 180° büküm sonrasında kaynak veya füzyon hattında 3.2 mm'yi aşan çatlak veya kusur bulunamaz."),
            ("API 5L Tablo 18 / BOTAŞ Madde 3.3 (Kaynak Çekme Dayanımı):", "Boyuna kaynak dikişi enine çekme testinde belirlenen çekme dayanımı, boru gövdesi için şart koşulan minimum çekme dayanımından (SMTS) düşük olamaz."),
            ("API 5L Tablo 18 / BOTAŞ Madde 8.8 (Kaynak Geometrisi & NDT):", "Boyuna dikişte radyal ofset max 1.50 mm; kaynak takviye yüksekliği max 3.50 mm; %100 otomatik ultrasonik (AUT) ve boru uçlarında %100 radyografik (RT) kontrol zorunludur."),
        ]

        for p_title, p_desc in prov_rows:
            ws.row_dimensions[r_curr].height = 24
            ws.cell(r_curr, 1, p_title).font = font_bold
            ws.cell(r_curr, 1).alignment = align_left
            ws.cell(r_curr, 1).border = border_all

            ws.merge_cells(f"B{r_curr}:E{r_curr}")
            c_desc = ws.cell(r_curr, 2, f"  {p_desc}")
            c_desc.font = font_info
            c_desc.alignment = align_left
            for col in range(2, 6):
                ws.cell(r_curr, col).border = border_all
            r_curr += 1

        # -------------------------------------------------------------
        # Section 6: Engineering Sign-off
        # -------------------------------------------------------------
        r_curr += 2
        ws.row_dimensions[r_curr].height = 20
        ws.cell(r_curr, 1, "HAZIRLAYAN (İmalat Mühendisi)").font = font_bold
        ws.cell(r_curr, 3, "KONTROL EDEN (Kalite Güvence / Kaynak Şefi)").font = font_bold
        ws.cell(r_curr, 5, "ONAYLAYAN (Fabrika Müdürü / İdare Temsilcisi)").font = font_bold

        r_curr += 1
        ws.row_dimensions[r_curr].height = 32
        for col in (1, 3, 5):
            c = ws.cell(r_curr, col, "İmza / Kaşe / Tarih: ____________________")
            c.font = font_info
            c.alignment = align_left

        # Column widths
        widths = [42, 18, 14, 24, 52]
        for idx, w in enumerate(widths, 1):
            ws.column_dimensions[get_column_letter(idx)].width = w

        ws.freeze_panes = "A6"

        output = io.BytesIO()
        wb.save(output)
        output.seek(0)
        return output

    @staticmethod
    def export_hydrostatic_test_report(
        hydro_data: Dict[str, Any],
        project_info: Optional[Dict[str, Any]] = None,
        pipe_info: Optional[Dict[str, Any]] = None,
        lang: str = "tr"
    ) -> io.BytesIO:
        """
        Exports official API 5L PSL2 & BOTAŞ Mill Hydrostatic Pressure Test Report,
        Water Volume, Fill Tonnage, and Pressure-Time Inspection Sheet to Excel.
        """
        if project_info is None:
            project_info = {}
        if pipe_info is None:
            pipe_info = {}

        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = "Hidrostatik Test Föyü" if lang == "tr" else "Hydrostatic Test Sheet"
        ws.views.sheetView[0].showGridLines = True

        # Typography
        font_title = Font(name="Arial", size=13, bold=True, color="0F172A")
        font_sec = Font(name="Arial", size=10, bold=True, color="0369A1")
        font_info = Font(name="Arial", size=9, color="334155")
        font_header = Font(name="Arial", size=9, bold=True, color="FFFFFF")
        font_regular = Font(name="Arial", size=9, color="000000")
        font_mono_bold = Font(name="Consolas", size=9, bold=True, color="000000")
        font_bold = Font(name="Arial", size=9, bold=True, color="000000")
        font_badge_pass = Font(name="Arial", size=10, bold=True, color="065F46")
        font_badge_warn = Font(name="Arial", size=10, bold=True, color="92400E")

        # Color Fills
        fill_header = PatternFill(start_color="0284C7", end_color="0284C7", fill_type="solid")
        fill_sec = PatternFill(start_color="F0F9FF", end_color="F0F9FF", fill_type="solid")
        fill_pass = PatternFill(start_color="D1FAE5", end_color="D1FAE5", fill_type="solid")
        fill_warn = PatternFill(start_color="FEF3C7", end_color="FEF3C7", fill_type="solid")
        fill_zebra = PatternFill(start_color="F8FAFC", end_color="F8FAFC", fill_type="solid")
        fill_highlight = PatternFill(start_color="E0F2FE", end_color="E0F2FE", fill_type="solid")

        # Borders
        border_thin = Side(border_style="thin", color="CBD5E1")
        border_all = Border(left=border_thin, right=border_thin, top=border_thin, bottom=border_thin)

        # Alignments
        align_center = Alignment(horizontal="center", vertical="center", wrap_text=True)
        align_left = Alignment(horizontal="left", vertical="center", wrap_text=True)

        # Row 1: Document Title Header
        ws.row_dimensions[1].height = 26
        title_text = (
            "FABRİKA HİDROSTATİK BASINÇ TESTİ KABUL VE SU HACMİ HESAP FÖYÜ"
            if lang == "tr"
            else "MILL HYDROSTATIC PRESSURE ACCEPTANCE & WATER VOLUME SPECIFICATION SHEET"
        )
        ws.merge_cells("A1:E1")
        ws.cell(1, 1, title_text).font = font_title
        ws.cell(1, 1).alignment = align_left

        # Row 2: Subtitle & Project Metadata
        p_name = project_info.get("project_name", "Doğal Gaz / Petrol Boru Hattı Projesi")
        p_no = project_info.get("project_no", "PRJ-HYDRO-2026")
        p_client = project_info.get("client", "BOTAŞ / İdare")
        p_date = project_info.get("revision_date", "2026-10-09")
        std_type = pipe_info.get("standard_type", "BOTAŞ / API 5L")
        grade = pipe_info.get("material_grade", "X65")
        d_inch = pipe_info.get("diameter_inch", '48"')

        meta_str = f"Proje: {p_name} ({p_no}) | Standart: {std_type} | Çelik Kalitesi: {grade} ({d_inch}) | Müşteri: {p_client} | Tarih: {p_date}"
        ws.row_dimensions[2].height = 18
        ws.merge_cells("A2:E2")
        ws.cell(2, 1, meta_str).font = font_info
        ws.cell(2, 1).alignment = align_left

        # Row 4: Status Verdict Banner
        ws.row_dimensions[4].height = 28
        target_p = float(hydro_data.get("target_test_pressure_bar", 100.0) or 100.0)
        hoop_ratio = float(hydro_data.get("hoop_stress_ratio_percent", 100.0) or 100.0)
        status_code = str(hydro_data.get("test_status", "PASS"))
        hold_time = int(hydro_data.get("holding_time_sec", 20) or 20)

        if status_code == "PASS":
            status_text = (
                f"HİDROSTATİK TEST KABUL KARARI: UYGUN (PASS) — Test Basıncı ({target_p:.1f} bar), SMYS'in %{hoop_ratio:.1f}'ine Ulaşır, Min. {hold_time} sn Tutma Süresiyle Sızdırmazlık Onaylıdır"
                if lang == "tr"
                else f"HYDROSTATIC ACCEPTANCE VERDICT: PASS — Test Pressure ({target_p:.1f} bar) reaches %{hoop_ratio:.1f} of SMYS with {hold_time}s holding time"
            )
            v_font = font_badge_pass
            v_fill = fill_pass
        else:
            status_text = (
                f"HİDROSTATİK TEST KABUL KARARI: PRES SINIRI (UYARI) — Test Basıncı Pres Tezgah Kapasitesi Nedeniyle Sınırlandırılmıştır"
                if lang == "tr"
                else f"HYDROSTATIC ACCEPTANCE VERDICT: WARNING — Pressure limited by bench capacity"
            )
            v_font = font_badge_warn
            v_fill = fill_warn

        ws.merge_cells("A4:E4")
        c_verdict = ws.cell(4, 1, f"  {status_text}")
        c_verdict.font = v_font
        c_verdict.fill = v_fill
        c_verdict.alignment = align_left
        for col in range(1, 6):
            ws.cell(4, col).border = border_all

        # Helper closures
        def write_section_header(row_num: int, text: str):
            ws.row_dimensions[row_num].height = 20
            ws.merge_cells(f"A{row_num}:E{row_num}")
            cell = ws.cell(row_num, 1, f"  {text}")
            cell.font = font_sec
            cell.fill = fill_sec
            cell.alignment = align_left
            for c_idx in range(1, 6):
                ws.cell(row_num, c_idx).border = border_all

        def write_table_header(row_num: int, col_titles: list):
            ws.row_dimensions[row_num].height = 22
            for idx, title in enumerate(col_titles, 1):
                cell = ws.cell(row_num, idx, title)
                cell.font = font_header
                cell.fill = fill_header
                cell.alignment = align_center if idx in (2, 3, 4) else align_left
                cell.border = border_all

        # Data extraction
        d_val = float(hydro_data.get("d_mm", 1219.0) or 1219.0)
        t_val = float(hydro_data.get("t_mm", 14.30) or 14.30)
        din_val = float(hydro_data.get("d_in_mm", d_val - 2 * t_val) or (d_val - 2 * t_val))
        pipe_len_val = float(hydro_data.get("pipe_length_m", 12.0) or 12.0)
        smys_val = float(hydro_data.get("smys_mpa", 450.0) or 450.0)

        p_botas = float(hydro_data.get("p_botas_100_smys_bar", 0.0) or 0.0)
        p_api95 = float(hydro_data.get("p_api_95_smys_bar", 0.0) or 0.0)
        min_p = float(hydro_data.get("min_acceptable_pressure_bar", target_p - 2.0) or (target_p - 2.0))
        sigma_h = float(hydro_data.get("sigma_hoop_mpa", 0.0) or 0.0)

        v_liters = float(hydro_data.get("water_volume_liters", 0.0) or 0.0)
        m_water_tons = float(hydro_data.get("water_mass_tons", 0.0) or 0.0)
        m_pipe_dry = float(hydro_data.get("pipe_dry_mass_tons", 0.0) or 0.0)
        m_flooded = float(hydro_data.get("pipe_flooded_mass_tons", 0.0) or 0.0)

        d_vol_liters = float(hydro_data.get("additional_water_liters", 0.0) or 0.0)
        d_vol_pct = float(hydro_data.get("volumetric_expansion_percent", 0.0) or 0.0)
        d_circ_mm = float(hydro_data.get("circumferential_expansion_mm", 0.0) or 0.0)

        t_fill = int(hydro_data.get("fill_time_sec", 15) or 15)
        t_press = int(hydro_data.get("pressurize_time_sec", 10) or 10)
        t_total = int(hydro_data.get("total_test_cycle_sec", 51) or 51)

        headers_common = ["Parametre Açıklaması", "Değer", "Birim", "Şartname / Sınır", "Mühendislik Formülü & Teknik Not"]

        # -------------------------------------------------------------
        # Section 1: Pipe & Material Properties
        # -------------------------------------------------------------
        r_curr = 6
        write_section_header(r_curr, "1. BORU TEMEL GEOMETRİSİ & MALZEME DAYANIMI (PIPE & MATERIAL PROPERTIES)")
        r_curr += 1
        write_table_header(r_curr, headers_common)
        r_curr += 1

        sec1_rows = [
            ("Boru Dış Çapı (Nominal OD - D)", f"{d_val:.2f}", "mm", f"{d_inch} (API 5L)", "Boru nominal dış çapı"),
            ("Nominal Et Kalınlığı (t)", f"{t_val:.2f}", "mm", "Standart / Sipariş", "Nominal cidar et kalınlığı"),
            ("Boru İç Çapı (Akış Çapı - D_in)", f"{din_val:.2f}", "mm", "Hesaplanan", "D_in = D − 2t (Su dolum silindir çapı)"),
            ("Boru Test Boyu (L_boru)", f"{pipe_len_val:.2f}", "m", "Nominal Boy", "Tek boru boyu"),
            ("Minimum Akma Dayanımı (SMYS)", f"{smys_val:.1f}", "MPa", f"{grade} Kalite", "Malzeme şartname akma mukavemeti"),
            ("Kuru Boru Boş Ağırlığı", f"{m_pipe_dry * 1000.0:.1f}", "kg (ton: " f"{m_pipe_dry:.3f})", "API 5L Formülü", "W = (D − t) · t · 0.0246615 · L"),
        ]

        for i, (param, val, unit, req, notes) in enumerate(sec1_rows):
            ws.row_dimensions[r_curr].height = 20
            c_fill = fill_zebra if i % 2 == 1 else None
            c1 = ws.cell(r_curr, 1, param); c1.font = font_bold; c1.alignment = align_left
            c2 = ws.cell(r_curr, 2, val); c2.font = font_mono_bold; c2.alignment = align_center
            c3 = ws.cell(r_curr, 3, unit); c3.font = font_regular; c3.alignment = align_center
            c4 = ws.cell(r_curr, 4, req); c4.font = font_info; c4.alignment = align_center
            c5 = ws.cell(r_curr, 5, notes); c5.font = font_info; c5.alignment = align_left
            for col in range(1, 6):
                cell = ws.cell(r_curr, col); cell.border = border_all
                if c_fill: cell.fill = c_fill
            r_curr += 1

        # -------------------------------------------------------------
        # Section 2: Test Pressures & Stresses
        # -------------------------------------------------------------
        r_curr += 1
        write_section_header(r_curr, "2. HİDROSTATİK TEST BASINÇLARI VE ÇEVRESEL GERİLME (TEST PRESSURES & HOOP STRESS)")
        r_curr += 1
        write_table_header(r_curr, headers_common)
        r_curr += 1

        sec2_rows = [
            ("BOTAŞ Test Basıncı (%100 SMYS)", f"{p_botas:.1f}", "bar", "BOTAŞ Madde 8.4", "P = (2 · 1.00·SMYS · t) / D · 10 (Tam akma sınırında test)"),
            ("API 5L Standart Basıncı (%95 SMYS)", f"{p_api95:.1f}", "bar", "API 5L Tablo 26", "P = (2 · 0.95·SMYS · t) / D · 10 (PSL2 standart kabul basıncı)"),
            ("Hedef Fabrika Test Basıncı (P_test)", f"{target_p:.1f}", "bar", "Şartname Hedefi", "Fabrika basınçlandırma istasyonu hedef set değeri"),
            ("Kabul Edilebilir Alt Limit (P_min)", f"{min_p:.1f}", "bar", "P_hedef − 2.0 bar", "BOTAŞ gösterge basınç toleransı (+0 / -2.0 bar)"),
            ("Test Basıncında Teğetsel Gerilme (σ_h)", f"{sigma_h:.1f}", "MPa", f"% {hoop_ratio:.1f} SMYS", "σ_h = (P_test · D) / (20 · t)"),
            ("Pres Tezgahı Sızdırmazlık Kapasitesi", "250.0", "bar", "Mekanik Limit", "Hidrostatik test pres kafa contalama sınırı"),
        ]

        for i, (param, val, unit, req, notes) in enumerate(sec2_rows):
            ws.row_dimensions[r_curr].height = 20
            c_fill = fill_highlight if "Hedef Fabrika Test" in param else (fill_zebra if i % 2 == 1 else None)
            c1 = ws.cell(r_curr, 1, param); c1.font = font_bold; c1.alignment = align_left
            c2 = ws.cell(r_curr, 2, val); c2.font = font_mono_bold; c2.alignment = align_center
            c3 = ws.cell(r_curr, 3, unit); c3.font = font_regular; c3.alignment = align_center
            c4 = ws.cell(r_curr, 4, req); c4.font = font_info; c4.alignment = align_center
            c5 = ws.cell(r_curr, 5, notes); c5.font = font_info; c5.alignment = align_left
            for col in range(1, 6):
                cell = ws.cell(r_curr, col); cell.border = border_all
                if c_fill: cell.fill = c_fill
            r_curr += 1

        # -------------------------------------------------------------
        # Section 3: Water Volume & Tonage
        # -------------------------------------------------------------
        r_curr += 1
        write_section_header(r_curr, "3. TEST SUYU DOLUM HACMİ VE TONAJI (WATER VOLUME & FLOODED TONNAGE)")
        r_curr += 1
        write_table_header(r_curr, headers_common)
        r_curr += 1

        sec3_rows = [
            ("Tek Boru Su Dolum Hacmi (V_0)", f"{v_liters:.1f}", "litre (m³: " f"{v_liters / 1000.0:.3f})", "Net İç Hacim", "V_0 = π/4 · D_in² · L"),
            ("Doldurulan Test Suyu Ağırlığı", f"{m_water_tons:.3f}", "ton / boru", "ρ = 1000 kg/m³", "M_su = V_0 · ρ"),
            ("Su Dolu Boru Toplam Kütlesi", f"{m_flooded:.3f}", "ton / boru", "Toplam Yük", "M_toplam = M_kuru + M_su (Test sehpası taşıma yükü)"),
            ("100 Boruluk Parti Su İhtiyacı", f"{m_water_tons * 100.0:.1f}", "m³ (ton)", "Parti Dolumu", "Geri dönüşümlü su arıtma ve depolama havuz kapasitesi"),
        ]

        for i, (param, val, unit, req, notes) in enumerate(sec3_rows):
            ws.row_dimensions[r_curr].height = 20
            c_fill = fill_zebra if i % 2 == 1 else None
            c1 = ws.cell(r_curr, 1, param); c1.font = font_bold; c1.alignment = align_left
            c2 = ws.cell(r_curr, 2, val); c2.font = font_mono_bold; c2.alignment = align_center
            c3 = ws.cell(r_curr, 3, unit); c3.font = font_regular; c3.alignment = align_center
            c4 = ws.cell(r_curr, 4, req); c4.font = font_info; c4.alignment = align_center
            c5 = ws.cell(r_curr, 5, notes); c5.font = font_info; c5.alignment = align_left
            for col in range(1, 6):
                cell = ws.cell(r_curr, col); cell.border = border_all
                if c_fill: cell.fill = c_fill
            r_curr += 1

        # -------------------------------------------------------------
        # Section 4: Elastic Expansion & Additional Water
        # -------------------------------------------------------------
        r_curr += 1
        write_section_header(r_curr, "4. BASINÇ ALTINDA ELASTİK GENLEŞME VE İLAVE BASMA SUYU (ELASTIC EXPANSION)")
        r_curr += 1
        write_table_header(r_curr, headers_common)
        r_curr += 1

        sec4_rows = [
            ("Basınç Altında Çevresel Esneme (ΔC)", f"{d_circ_mm:.2f}", "mm", "Elastik Esneme", "Test basıncında boru çevresinde oluşan elastik genleşme"),
            ("Boru Cidar ve Su Hacimsel Esneme Oranı", f"% {d_vol_pct:.3f}", "hacim oranı", "dV / V_0", "Çelik cidar elastik açılması + suyun sıkışabilirlik payı"),
            ("Basılması Gereken İlave Su Miktarı", f"{d_vol_liters:.2f}", "litre / boru", "İntensifier Hacmi", "Hedef basınca ulaşmak için yüksek basınç pompasınca basılan su"),
        ]

        for i, (param, val, unit, req, notes) in enumerate(sec4_rows):
            ws.row_dimensions[r_curr].height = 20
            c_fill = fill_zebra if i % 2 == 1 else None
            c1 = ws.cell(r_curr, 1, param); c1.font = font_bold; c1.alignment = align_left
            c2 = ws.cell(r_curr, 2, val); c2.font = font_mono_bold; c2.alignment = align_center
            c3 = ws.cell(r_curr, 3, unit); c3.font = font_regular; c3.alignment = align_center
            c4 = ws.cell(r_curr, 4, req); c4.font = font_info; c4.alignment = align_center
            c5 = ws.cell(r_curr, 5, notes); c5.font = font_info; c5.alignment = align_left
            for col in range(1, 6):
                cell = ws.cell(r_curr, col); cell.border = border_all
                if c_fill: cell.fill = c_fill
            r_curr += 1

        # -------------------------------------------------------------
        # Section 5: Inspection Cycle & Holding Time
        # -------------------------------------------------------------
        r_curr += 1
        write_section_header(r_curr, "5. TEST ÇEVRİMİ VE TUTMA SÜRELERİ (TEST CYCLE & HOLDING TIME)")
        r_curr += 1
        write_table_header(r_curr, headers_common)
        r_curr += 1

        sec5_rows = [
            ("Standart Min. Tutma Süresi", f"{hold_time}", "saniye (sn)", "BOTAŞ: 20 sn / API: 10 sn", "Hedef basınçta bekleme ve sızdırmazlık gözetim süresi"),
            ("Alçak Basınç Ön Dolum Süresi", f"{t_fill}", "saniye (sn)", "Hızlı Dolum", "Ön dolum pompası su basma süresi (~150 L/sn)"),
            ("Yüksek Basınçlandırma Süresi", f"{t_press}", "saniye (sn)", "Basınçlandırma", "Pistonlu intensifier ile hedef basınca çıkış"),
            ("Basınç Boşaltma ve Tahliye Süresi", "6", "saniye (sn)", "Boşaltma", "Basınç tahliye vanası açılma ve su geri kazanımı"),
            ("Toplam Tek Boru Test Çevrim Süresi", f"{t_total}", "saniye / boru", "Çevrim Zamanı", f"1 boru için toplam istasyon süresi (~{t_total} sn)"),
            ("İstasyon Saatlik Kapasitesi", f"{int(3600 / t_total)}", "boru / saat", "Nominal Kapasite", "Tek hidrostatik test presi teorik hat hızı"),
        ]

        for i, (param, val, unit, req, notes) in enumerate(sec5_rows):
            ws.row_dimensions[r_curr].height = 20
            c_fill = fill_zebra if i % 2 == 1 else None
            c1 = ws.cell(r_curr, 1, param); c1.font = font_bold; c1.alignment = align_left
            c2 = ws.cell(r_curr, 2, val); c2.font = font_mono_bold; c2.alignment = align_center
            c3 = ws.cell(r_curr, 3, unit); c3.font = font_regular; c3.alignment = align_center
            c4 = ws.cell(r_curr, 4, req); c4.font = font_info; c4.alignment = align_center
            c5 = ws.cell(r_curr, 5, notes); c5.font = font_info; c5.alignment = align_left
            for col in range(1, 6):
                cell = ws.cell(r_curr, col); cell.border = border_all
                if c_fill: cell.fill = c_fill
            r_curr += 1

        # -------------------------------------------------------------
        # Section 6: Standard Provisions & Rules
        # -------------------------------------------------------------
        r_curr += 1
        write_section_header(r_curr, "6. STANDART ŞARTNAME HÜKÜMLERİ VE KABUL KRİTERLERİ (API 5L / BOTAŞ PROVISIONS)")
        r_curr += 1

        prov_rows = [
            ("API 5L Madde 10.2.6.2 (Hidrostatik Test Süresi):", "Her bir boru gövdesi fabrikada hidrostatik basınç testine tabi tutulmalıdır. Kaynaklı borularda (D > 457 mm) tutma süresi en az 10 saniye olmalıdır."),
            ("BOTAŞ Madde 8.4 (Test Basıncı ve 20 Saniye Kuralı):", "Test basıncı boru et kalınlığı ve SMYS'in %100'ü esas alınarak hesaplanır. Test süresi istisnasız en az 20 saniye olmalı ve her boru için grafik yazıcı (chart recorder) çıktısı alınmalıdır."),
            ("API 5L Madde 10.2.6.3 (Sızdırmazlık Kabul Kriteri):", "Test basıncında tutma süresi boyunca boru gövdesinde, kaynak dikişlerinde veya bağlantı yerlerinde terleme, sızdırma, çatlak veya kalıcı plastik bozulma kesinlikle kabul edilemez."),
            ("BOTAŞ Madde 8.4 (Gösterge Doğrulaması):", "Basınç manometreleri ve transducerlar her vardiya başında kalibre edilmeli; test basıncı toleransı +0 / -2.0 bar aralığında tutulmalıdır."),
        ]

        for p_title, p_desc in prov_rows:
            ws.row_dimensions[r_curr].height = 24
            ws.cell(r_curr, 1, p_title).font = font_bold
            ws.cell(r_curr, 1).alignment = align_left
            ws.cell(r_curr, 1).border = border_all

            ws.merge_cells(f"B{r_curr}:E{r_curr}")
            c_desc = ws.cell(r_curr, 2, f"  {p_desc}")
            c_desc.font = font_info
            c_desc.alignment = align_left
            for col in range(2, 6):
                ws.cell(r_curr, col).border = border_all
            r_curr += 1

        # -------------------------------------------------------------
        # Section 7: Engineering Sign-off
        # -------------------------------------------------------------
        r_curr += 2
        ws.row_dimensions[r_curr].height = 20
        ws.cell(r_curr, 1, "HAZIRLAYAN (Hidrostatik Test Operatörü)").font = font_bold
        ws.cell(r_curr, 3, "KONTROL EDEN (Kalite Kontrol / NDT Şefi)").font = font_bold
        ws.cell(r_curr, 5, "ONAYLAYAN (TPI / İdare Şantiye Temsilcisi)").font = font_bold

        r_curr += 1
        ws.row_dimensions[r_curr].height = 32
        for col in (1, 3, 5):
            c = ws.cell(r_curr, col, "İmza / Kaşe / Tarih: ____________________")
            c.font = font_info
            c.alignment = align_left

        # Column widths
        widths = [42, 18, 14, 24, 52]
        for idx, w in enumerate(widths, 1):
            ws.column_dimensions[get_column_letter(idx)].width = w

        ws.freeze_panes = "A6"

        output = io.BytesIO()
        wb.save(output)
        output.seek(0)
        return output

    @staticmethod
    def export_erw_geometry_report(
        project_info: Dict[str, Any],
        erw_data: Dict[str, Any],
        pipe_info: Optional[Dict[str, Any]] = None,
        lang: str = "tr"
    ) -> io.BytesIO:
        """
        Exports official ERW/HFW Pipe Manufacturing Geometry, Skelp Sizing,
        Flash Trimming Tolerances, and API 5L Clause 10.2.4.3 Flattening Test Report to Excel.
        """
        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = "ERW İmalat & Yassıltma" if lang == "tr" else "ERW Sizing & Flattening"
        ws.views.sheetView[0].showGridLines = True

        # Fonts
        font_title = Font(name="Arial", size=13, bold=True, color="1E3A8A")
        font_sec_hdr = Font(name="Arial", size=10, bold=True, color="FFFFFF")
        font_tbl_hdr = Font(name="Arial", size=9, bold=True, color="FFFFFF")
        font_bold = Font(name="Arial", size=9, bold=True, color="0F172A")
        font_regular = Font(name="Arial", size=9, color="1E293B")
        font_mono = Font(name="Consolas", size=9, color="0F172A")
        font_mono_bold = Font(name="Consolas", size=9, bold=True, color="0F172A")
        font_info = Font(name="Arial", size=8.5, color="475569")
        font_badge_pass = Font(name="Arial", size=9, bold=True, color="065F46")

        # Fills
        fill_sec_hdr = PatternFill(start_color="1E3A8A", end_color="1E3A8A", fill_type="solid")
        fill_tbl_hdr = PatternFill(start_color="334155", end_color="334155", fill_type="solid")
        fill_zebra = PatternFill(start_color="F8FAFC", end_color="F8FAFC", fill_type="solid")
        fill_highlight = PatternFill(start_color="EFF6FF", end_color="EFF6FF", fill_type="solid")
        fill_badge_pass = PatternFill(start_color="D1FAE5", end_color="D1FAE5", fill_type="solid")

        # Borders
        border_thin = Side(border_style="thin", color="CBD5E1")
        border_all = Border(left=border_thin, right=border_thin, top=border_thin, bottom=border_thin)

        # Alignments
        align_left = Alignment(horizontal="left", vertical="center")
        align_center = Alignment(horizontal="center", vertical="center")

        def write_section_header(row_idx: int, title_text: str):
            ws.row_dimensions[row_idx].height = 24
            ws.merge_cells(f"A{row_idx}:E{row_idx}")
            c = ws.cell(row_idx, 1, f"  {title_text}")
            c.font = font_sec_hdr
            c.fill = fill_sec_hdr
            c.alignment = align_left

        def write_table_header(row_idx: int, col_headers: List[str]):
            ws.row_dimensions[row_idx].height = 22
            for c_i, h in enumerate(col_headers, 1):
                c = ws.cell(row_idx, c_i, h)
                c.font = font_tbl_hdr
                c.fill = fill_tbl_hdr
                c.alignment = align_center
                c.border = border_all

        # Row 1: Main Title
        ws.row_dimensions[1].height = 28
        title_text = (
            "API 5L / BOTAŞ ERW & HFW BORU İMALAT GEOMETRİSİ, ŞERİT SAC VE YASSILTMA TESTİ ONAY FÖYÜ"
            if lang == "tr" else
            "API 5L / BOTAŞ ERW & HFW PIPE MANUFACTURING GEOMETRY, SKELP SIZING & FLATTENING TEST SHEET"
        )
        ws.merge_cells("A1:E1")
        ws.cell(1, 1, title_text).font = font_title
        ws.cell(1, 1).alignment = align_left

        # Metadata
        p_name = project_info.get("project_name", "Doğal Gaz / Petrol İletim Hattı Projesi")
        p_no = project_info.get("project_no", "API-5L-ERW-2026")
        p_client = project_info.get("client", "BOTAŞ / İdare")
        p_mfg = project_info.get("contractor", "ERW Boru İmalatçısı")
        p_std = project_info.get("standard", "API Spec 5L (47. Baskı) PSL2 & BOTAŞ")
        p_date = project_info.get("revision_date", "2026-10-09")

        meta1 = f"Proje: {p_name} ({p_no}) | Standart: {p_std} | Tarih: {p_date}"
        meta2 = f"İşveren: {p_client} | İmalatçı Firma: {p_mfg} | Üretim Tipi: ERW / HFW (Yüksek Frekans İndüksiyon Kaynaklı)"

        ws.row_dimensions[2].height = 18
        ws.merge_cells("A2:E2")
        ws.cell(2, 1, meta1).font = font_info
        ws.cell(2, 1).alignment = align_left

        ws.row_dimensions[3].height = 18
        ws.merge_cells("A3:E3")
        ws.cell(3, 1, meta2).font = font_info
        ws.cell(3, 1).alignment = align_left

        headers_common = ["Teknik Parametre / Kontrol Maddesi", "Hesaplanan / Nominal Değer", "Birim", "Şartname Sınırı / Kriter", "Açıklama / Standart Dayanağı"]

        r_curr = 5

        # -------------------------------------------------------------
        # Section 1: Pipe Specifications
        # -------------------------------------------------------------
        write_section_header(r_curr, "1. BORU VE İMALAT TEMEL PARAMETRELERİ (PIPE BASE PARAMETERS)")
        r_curr += 1
        write_table_header(r_curr, headers_common)
        r_curr += 1

        d_mm = erw_data.get("diameter_mm", 323.9)
        t_mm = erw_data.get("wall_thickness_mm", 9.53)
        grade = erw_data.get("material_grade", "X52")
        psl = erw_data.get("psl_level", "PSL2")
        L_m = erw_data.get("pipe_length_m", 12.0)
        m_pipe = erw_data.get("pipe_mass_kg_m", 73.87)
        m_total = erw_data.get("pipe_total_mass_kg", 886.4)

        sec1_rows = [
            ("Boru Dış Çapı (D)", f"{d_mm:.2f}", "mm", "Nominal Ebat", "Boru dış çapı (OD)"),
            ("Boru Et Kalınlığı (t)", f"{t_mm:.2f}", "mm", "API 5L Tablo 11", "Nominal cidar et kalınlığı"),
            ("Çelik Malzeme Kalitesi (Grade)", grade, "—", f"API 5L {psl}", "Hat borusu çelik sınıfı"),
            ("Standart Boru İmalat Boyu (L)", f"{L_m:.2f}", "metre", "8.0 - 14.5 m", "Tek boru üretim boyu"),
            ("Birim Boru Ağırlığı (M_boru)", f"{m_pipe:.2f}", "kg/m", "0.02466 · t · (D-t)", "API 5L nominal çelik kütlesi"),
            ("1 Boy Boru Toplam Ağırlığı", f"{m_total:.1f}", "kg / boru", "Kantar Tartım", "12 metrelik net boru gövde ağırlığı"),
        ]

        for i, (param, val, unit, req, notes) in enumerate(sec1_rows):
            ws.row_dimensions[r_curr].height = 20
            c_fill = fill_zebra if i % 2 == 1 else None
            c1 = ws.cell(r_curr, 1, param); c1.font = font_bold; c1.alignment = align_left
            c2 = ws.cell(r_curr, 2, val); c2.font = font_mono_bold; c2.alignment = align_center
            c3 = ws.cell(r_curr, 3, unit); c3.font = font_regular; c3.alignment = align_center
            c4 = ws.cell(r_curr, 4, req); c4.font = font_info; c4.alignment = align_center
            c5 = ws.cell(r_curr, 5, notes); c5.font = font_info; c5.alignment = align_left
            for col in range(1, 6):
                cell = ws.cell(r_curr, col); cell.border = border_all
                if c_fill: cell.fill = c_fill
            r_curr += 1

        # -------------------------------------------------------------
        # Section 2: Skelp Sizing & Upset Allowance
        # -------------------------------------------------------------
        r_curr += 1
        write_section_header(r_curr, "2. ERW / HFW ŞERİT SAC (SKELP) SİPARİŞ GENİŞLİĞİ VE YIĞMA HESABI (SKELP SIZING)")
        r_curr += 1
        write_table_header(r_curr, headers_common)
        r_curr += 1

        c_mid = erw_data.get("circumference_mid_mm", 987.6)
        d_mid = erw_data.get("mean_diameter_mm", 314.37)
        delta_upset = erw_data.get("upset_allowance_mm", 12.87)
        w_skelp = erw_data.get("skelp_width_net_mm", 1000.49)
        w_gross = erw_data.get("skelp_width_gross_mm", 1015.49)
        m_skelp = erw_data.get("skelp_mass_kg_m", 74.83)
        loss_kg = erw_data.get("upset_loss_kg_m", 0.96)
        loss_pct = erw_data.get("upset_loss_percent", 1.28)

        sec2_rows = [
            ("Orta Eksen Çapı (D_mid)", f"{d_mid:.2f}", "mm", "D − t", "Nötr lif çapı"),
            ("Teorik Boru Çevresi (C_mid)", f"{c_mid:.2f}", "mm", "π · D_mid", "Silindirik şekillendirilmiş nötr çevre boyu"),
            ("Kaynak Yığması Payı (ΔW_upset)", f"{delta_upset:.2f}", "mm", "1.35 · t (1.2t - 1.5t)", "Yüksek frekans sıkma rulolarında eriyip taşan çapak payı"),
            ("Net Şerit Sac Genişliği (W_skelp)", f"{w_skelp:.2f}", "mm", "C_mid + ΔW_upset", "Rulo sac sipariş genişliği"),
            ("Brüt Sac Genişliği (W_gross)", f"{w_gross:.2f}", "mm", "W_skelp + 15 mm", "Kenar frezeleme / dilme payı dahil bobin genişliği"),
            ("Şerit Sac Birim Ağırlığı", f"{m_skelp:.2f}", "kg/m", "7850 · W_skelp · t", "Giriş rulo sac birim metre ağırlığı"),
            ("Kaynak Çapağı / Yığma Kaybı", f"{loss_kg:.2f} ({loss_pct:.2f}%)", "kg/m (%)", "Traşlanan Çapak", "Eriyik çapağı olarak traşlanan hurda kütle"),
        ]

        for i, (param, val, unit, req, notes) in enumerate(sec2_rows):
            ws.row_dimensions[r_curr].height = 20
            c_fill = fill_highlight if "Net Şerit Sac" in param else (fill_zebra if i % 2 == 1 else None)
            c1 = ws.cell(r_curr, 1, param); c1.font = font_bold; c1.alignment = align_left
            c2 = ws.cell(r_curr, 2, val); c2.font = font_mono_bold; c2.alignment = align_center
            c3 = ws.cell(r_curr, 3, unit); c3.font = font_regular; c3.alignment = align_center
            c4 = ws.cell(r_curr, 4, req); c4.font = font_info; c4.alignment = align_center
            c5 = ws.cell(r_curr, 5, notes); c5.font = font_info; c5.alignment = align_left
            for col in range(1, 6):
                cell = ws.cell(r_curr, col); cell.border = border_all
                if c_fill: cell.fill = c_fill
            r_curr += 1

        # -------------------------------------------------------------
        # Section 3: Flash Trimming Tolerances (API 5L Table 16)
        # -------------------------------------------------------------
        r_curr += 1
        write_section_header(r_curr, "3. KAYNAK ÇAPAĞI (FLASH TRIMMING) TOLERANSLARI (API 5L TABLO 16 & MADDE 9.11.3.2)")
        r_curr += 1
        write_table_header(r_curr, headers_common)
        r_curr += 1

        sec3_rows = [
            ("Dış Kaynak Çapağı Yüksekliği (h_out)", "≤ 0.00", "mm", "Tam Hemzemin", "Dış yüzey traşlama bıçağı ile boru profiline sıfırlanmalıdır"),
            ("Dış Yüzey Oyuk / Traş Çukuru İzni", "≤ 0.15", "mm", "API 5L 9.11.3.2", "Traşlama derinliği et kalınlığı minimumunu ihlal etmemelidir"),
            ("İç Kaynak Çapağı Yüksekliği (h_in)", f"≤ {erw_data.get('flash_inside_max_mm', 0.38):.2f}", "mm", "API 5L Tablo 16", "İç traşlama malafası ile kesilmiş dikiş kalıntı yüksekliği"),
            ("İç Çapak Sürekliliği & Çapak Pulu", "Sürekli / Temiz", "Görsel", "Kusursuz Kesim", "İç traşlama pürüzsüz olmalı, keskin çapak pulu içermemelidir"),
        ]

        for i, (param, val, unit, req, notes) in enumerate(sec3_rows):
            ws.row_dimensions[r_curr].height = 20
            c_fill = fill_zebra if i % 2 == 1 else None
            c1 = ws.cell(r_curr, 1, param); c1.font = font_bold; c1.alignment = align_left
            c2 = ws.cell(r_curr, 2, val); c2.font = font_mono_bold; c2.alignment = align_center
            c3 = ws.cell(r_curr, 3, unit); c3.font = font_regular; c3.alignment = align_center
            c4 = ws.cell(r_curr, 4, req); c4.font = font_info; c4.alignment = align_center
            c5 = ws.cell(r_curr, 5, notes); c5.font = font_info; c5.alignment = align_left
            for col in range(1, 6):
                cell = ws.cell(r_curr, col); cell.border = border_all
                if c_fill: cell.fill = c_fill
            r_curr += 1

        # -------------------------------------------------------------
        # Section 4: Flattening Test (API 5L Clause 10.2.4.3 & BOTAŞ 3.3.3)
        # -------------------------------------------------------------
        r_curr += 1
        write_section_header(r_curr, "4. YASSILTMA TESTİ (FLATTENING TEST) PLAKA MESAFELERİ (API 5L 10.2.4.3 & BOTAŞ 3.3.3)")
        r_curr += 1
        write_table_header(r_curr, headers_common)
        r_curr += 1

        h_weld = erw_data.get("flattening_h_mm", 102.56)
        h_duct = erw_data.get("flattening_ductility_h_mm", 106.89)
        h_sound = erw_data.get("flattening_soundness_h_mm", 19.06)
        e_val = erw_data.get("deformation_factor_e", 0.07)
        len_spec = erw_data.get("flattening_specimen_len_mm", 60.0)

        sec4_rows = [
            ("Deformasyon Faktörü (e)", f"{e_val:.3f}", "katsayı", f"API 5L {grade}", "Çelik akma ve süneklik derecesine bağlı formül faktörü"),
            ("Halka Numune Boyu (L_numune)", f"{len_spec:.1f}", "mm", "≥ 50.0 mm", "API 5L 10.2.4.3 uyarınca test halka kesim genişliği"),
            ("Aşama 1: Kaynak Açılma Limiti (H)", f"{h_weld:.2f}", "mm", "H = (1+e)·t / (e + t/D)", "Kaynak dikişi 90° (saat 9/3) konumunda, H mesafesine kadar 0 çatlak"),
            ("Aşama 2: Boru Gövde Sünekliği (H_duct)", f"{h_duct:.2f}", "mm", "0.33 · D", "Plakalar 0.33D'ye inene kadar gövdede (saat 12/6) çatlama olmamalıdır"),
            ("Aşama 3: Tam Ezilme & Katmer (H_sound)", f"{h_sound:.2f}", "mm", "2 · t (İç cidar temas)", "Plakalar birbirine değene kadar gövdede laminasyon/katmer olmamalıdır"),
            ("Test Hızı ve Pres Açısı", "Soğuk Pres", "≤ 25 mm/dk", "Paralel Plakalar", "Hidrostatik veya mekanik ezme presi"),
        ]

        for i, (param, val, unit, req, notes) in enumerate(sec4_rows):
            ws.row_dimensions[r_curr].height = 20
            c_fill = fill_highlight if "Kaynak Açılma" in param else (fill_zebra if i % 2 == 1 else None)
            c1 = ws.cell(r_curr, 1, param); c1.font = font_bold; c1.alignment = align_left
            c2 = ws.cell(r_curr, 2, val); c2.font = font_mono_bold; c2.alignment = align_center
            c3 = ws.cell(r_curr, 3, unit); c3.font = font_regular; c3.alignment = align_center
            c4 = ws.cell(r_curr, 4, req); c4.font = font_info; c4.alignment = align_center
            c5 = ws.cell(r_curr, 5, notes); c5.font = font_info; c5.alignment = align_left
            for col in range(1, 6):
                cell = ws.cell(r_curr, col); cell.border = border_all
                if c_fill: cell.fill = c_fill
            r_curr += 1

        # -------------------------------------------------------------
        # Section 5: Seam Normalizing Heat Treatment (API 5L 10.2.5.3)
        # -------------------------------------------------------------
        r_curr += 1
        write_section_header(r_curr, "5. ON-LINE DİKİŞ NORMALİZASYON ISIL İŞLEMİ (API 5L 10.2.5.3 & BOTAŞ 3.2.1)")
        r_curr += 1
        write_table_header(r_curr, headers_common)
        r_curr += 1

        sec5_rows = [
            ("Kaynak Dikişi Isıl İşlem Tipi", "Tam Normalizasyon", "Yöntem", "PSL2 Zorunlu", "On-line yüksek frekanslı indüksiyon bobinleri ile dikiş tavlama"),
            ("Minimum Tavlama Sıcaklığı", "≥ 720.0", "°C", "API 5L 10.2.5.3", "Şartname izin verilen alt sıcaklık sınırı"),
            ("Nominal Östenitleme Sıcaklığı", "900.0 - 950.0", "°C", "Ac3 Üzeri", "Dikişteki sert beyaz döküm yapıyı giderip ince ferrit-perlit fazı oluşturma"),
            ("Soğutma Koşulu", "Sakin Havada", "Ortam", "Air Cool", "Martenzit oluşumunu önlemek için kontrollü hava soğutma"),
            ("Dikiş Sertlik Sınırı (HV10)", "≤ 250 (Ekşi) / ≤ 300", "HV10", "BOTAŞ 3.3.7", "Normalizasyon sonrası kaynak dikişi ve ITAB sertlik sınırı"),
        ]

        for i, (param, val, unit, req, notes) in enumerate(sec5_rows):
            ws.row_dimensions[r_curr].height = 20
            c_fill = fill_zebra if i % 2 == 1 else None
            c1 = ws.cell(r_curr, 1, param); c1.font = font_bold; c1.alignment = align_left
            c2 = ws.cell(r_curr, 2, val); c2.font = font_mono_bold; c2.alignment = align_center
            c3 = ws.cell(r_curr, 3, unit); c3.font = font_regular; c3.alignment = align_center
            c4 = ws.cell(r_curr, 4, req); c4.font = font_info; c4.alignment = align_center
            c5 = ws.cell(r_curr, 5, notes); c5.font = font_info; c5.alignment = align_left
            for col in range(1, 6):
                cell = ws.cell(r_curr, col); cell.border = border_all
                if c_fill: cell.fill = c_fill
            r_curr += 1

        # -------------------------------------------------------------
        # Section 6: Signatures
        # -------------------------------------------------------------
        r_curr += 2
        ws.row_dimensions[r_curr].height = 20
        ws.cell(r_curr, 1, "HAZIRLAYAN (Üretim & Kalite Müh.)").font = font_bold
        ws.cell(r_curr, 3, "KONTROL EDEN (QA/QC Şefi)").font = font_bold
        ws.cell(r_curr, 5, "ONAYLAYAN (Baş Denetçi / TPI / İdare)").font = font_bold

        r_curr += 1
        ws.row_dimensions[r_curr].height = 32
        for col in (1, 3, 5):
            c = ws.cell(r_curr, col, "İmza / Kaşe / Tarih: ____________________")
            c.font = font_info
            c.alignment = align_left

        # Column widths
        widths = [42, 20, 14, 28, 52]
        for idx, w in enumerate(widths, 1):
            ws.column_dimensions[get_column_letter(idx)].width = w

        ws.freeze_panes = "A5"

        output = io.BytesIO()
        wb.save(output)
        output.seek(0)
        return output

    @classmethod
    def export_bevel_geometry_report(
        cls,
        project_info: Dict[str, Any],
        bevel_data: Dict[str, Any],
        pipe_info: Optional[Dict[str, Any]] = None,
        lang: str = "tr"
    ) -> io.BytesIO:
        """
        Exports official Pipe End Geometry, Bevel Preparation, Root Face,
        Out-of-Squareness, and End Ovality Inspection Report to corporate Excel.
        Conforms to API Spec 5L Clause 9.12.5 and BOTAŞ Specification Clause 3.3.8 & 5.5.
        """
        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = "Kaynak Ağzı & Uç Geometrisi"
        ws.views.sheetView[0].showGridLines = True

        p_info = project_info or {}
        p_extra = pipe_info or {}

        # Colors & Fonts
        navy_dark = "1E3A8A"
        teal_hdr = "0F766E"
        blue_hdr = "1D4ED8"
        slate_hdr = "334155"
        zebra_bg = "F8FAFC"
        pass_green = "059669"
        fail_red = "DC2626"

        font_title = Font(name="Calibri", size=15, bold=True, color="FFFFFF")
        font_sub = Font(name="Calibri", size=9.5, italic=True, color="CBD5E1")
        font_sec = Font(name="Calibri", size=11, bold=True, color="FFFFFF")
        font_tbl_hdr = Font(name="Calibri", size=10, bold=True, color="FFFFFF")
        font_bold = Font(name="Calibri", size=10, bold=True, color="0F172A")
        font_regular = Font(name="Calibri", size=9.5, color="1E293B")
        font_mono_bold = Font(name="Consolas", size=10, bold=True, color="0F172A")
        font_info = Font(name="Calibri", size=9, color="475569")
        font_pass = Font(name="Calibri", size=10, bold=True, color="047857")
        font_fail = Font(name="Calibri", size=10, bold=True, color="B91C1C")

        fill_title = PatternFill(start_color=navy_dark, end_color=navy_dark, fill_type="solid")
        fill_sec = PatternFill(start_color=teal_hdr, end_color=teal_hdr, fill_type="solid")
        fill_tbl_hdr = PatternFill(start_color=slate_hdr, end_color=slate_hdr, fill_type="solid")
        fill_zebra = PatternFill(start_color=zebra_bg, end_color=zebra_bg, fill_type="solid")
        fill_pass = PatternFill(start_color="ECFDF5", end_color="ECFDF5", fill_type="solid")
        fill_fail = PatternFill(start_color="FEF2F2", end_color="FEF2F2", fill_type="solid")

        border_thin = Side(border_style="thin", color="CBD5E1")
        border_all = Border(left=border_thin, right=border_thin, top=border_thin, bottom=border_thin)

        align_center = Alignment(horizontal="center", vertical="center")
        align_left = Alignment(horizontal="left", vertical="center")
        align_right = Alignment(horizontal="right", vertical="center")

        d_mm = float(p_extra.get("diameter_mm") or bevel_data.get("diameter_mm") or 1219.0)
        t_mm = float(p_extra.get("wall_thickness_mm") or bevel_data.get("wall_thickness_mm") or 14.30)
        grade = str(p_extra.get("material_grade") or bevel_data.get("material_grade") or "X65")
        std = str(p_extra.get("standard_type") or bevel_data.get("standard_code") or "BOTAŞ")
        d_inch = str(p_extra.get("diameter_inch") or f'{d_mm/25.4:.1f}"')

        # Row 1: Title Banner
        ws.merge_cells("A1:E1")
        c_title = ws.cell(1, 1, "API 5L / BOTAŞ BORU UÇ GEOMETRİSİ, ALIN KAYNAK AĞZI VE OVALİTE ONAY FORMU")
        c_title.font = font_title
        c_title.fill = fill_title
        c_title.alignment = align_center
        ws.row_dimensions[1].height = 36

        # Row 2: Subtitle
        ws.merge_cells("A2:E2")
        p_name = p_info.get("project_name", "Doğalgaz / Petrol Boru Hattı Projesi")
        p_no = p_info.get("project_no", "PRJ-BEVEL-2026")
        rev_date = p_info.get("revision_date", "2026-10-09")
        sub_text = f"Proje: {p_name} ({p_no}) | Standart: {std} / API 5L 9.12.5 | Boru: {d_inch} ({d_mm} mm) t={t_mm} mm {grade} | Tarih: {rev_date}"
        c_sub = ws.cell(2, 1, sub_text)
        c_sub.font = font_sub
        c_sub.fill = fill_title
        c_sub.alignment = align_center
        ws.row_dimensions[2].height = 20

        # Row 3: Client & Contractor
        ws.merge_cells("A3:E3")
        client = p_info.get("client", "BOTAŞ A.Ş.")
        contr = p_info.get("contractor", "Boru Üretim Tesisi & Kalite Kontrol Müdürlüğü")
        verdict_str = bevel_data.get("verdict", "APPROVED (UYGUN / KABUL)")
        c_sub2 = ws.cell(3, 1, f"İşveren: {client} | Üretici: {contr} | Genel Karar: {verdict_str}")
        c_sub2.font = font_sub
        c_sub2.fill = fill_title
        c_sub2.alignment = align_center
        ws.row_dimensions[3].height = 20

        r_curr = 5
        headers_common = [
            "Teknik Parametre / Kontrol Maddesi",
            "Nominal / Ölçülen Değer",
            "Birim",
            "Şartname Toleransı / Kriter",
            "Ölçüm Yöntemi / Standart Maddesi"
        ]

        def write_sec_hdr(row_idx: int, title: str):
            ws.merge_cells(f"A{row_idx}:E{row_idx}")
            c = ws.cell(row_idx, 1, title)
            c.font = font_sec
            c.fill = fill_sec
            c.alignment = align_left
            ws.row_dimensions[row_idx].height = 24

        def write_tbl_hdr(row_idx: int, cols: list):
            ws.row_dimensions[row_idx].height = 22
            for idx, h_text in enumerate(cols, 1):
                c = ws.cell(row_idx, idx, h_text)
                c.font = font_tbl_hdr
                c.fill = fill_tbl_hdr
                c.alignment = align_center
                c.border = border_all

        # -------------------------------------------------------------
        # Section 1: Pipe Base Parameters
        # -------------------------------------------------------------
        write_sec_hdr(r_curr, "1. BORU VE İMALAT TEMEL BİLGİLERİ (PIPE BASE DATA)")
        r_curr += 1
        write_tbl_hdr(r_curr, headers_common)
        r_curr += 1

        sec1_rows = [
            ("Boru Dış Çapı (OD)", f"{d_mm:.2f} ({d_inch})", "mm", "Nominal Ebat", "Kumpas / Pi-Mezura"),
            ("Nominal Et Kalınlığı (t)", f"{t_mm:.2f}", "mm", "API 5L Tablo 11", "Ultrasonik Cidar Ölçümü"),
            ("Çelik Malzeme Kalitesi (Grade)", grade, "—", f"API 5L / {std}", "MTR Doğrulama"),
            ("Boru Uç Tipi (End Preparation)", bevel_data.get("end_type", "BEVEL"), "—", "Alın Kaynak Ağızlı (Plain End Bevel)", "API 5L Madde 9.12.5.2"),
            ("Uygulanan Standart", std, "—", "API 5L PSL2 & BOTAŞ 3.3.8", "Satın Alma Şartnamesi"),
        ]

        for i, (param, val, unit, req, notes) in enumerate(sec1_rows):
            ws.row_dimensions[r_curr].height = 20
            c_fill = fill_zebra if i % 2 == 1 else None
            c1 = ws.cell(r_curr, 1, param); c1.font = font_bold; c1.alignment = align_left
            c2 = ws.cell(r_curr, 2, val); c2.font = font_mono_bold; c2.alignment = align_center
            c3 = ws.cell(r_curr, 3, unit); c3.font = font_regular; c3.alignment = align_center
            c4 = ws.cell(r_curr, 4, req); c4.font = font_info; c4.alignment = align_center
            c5 = ws.cell(r_curr, 5, notes); c5.font = font_info; c5.alignment = align_left
            for col in range(1, 6):
                cell = ws.cell(r_curr, col); cell.border = border_all
                if c_fill: cell.fill = c_fill
            r_curr += 1

        # -------------------------------------------------------------
        # Section 2: Bevel Angle & Root Face Details
        # -------------------------------------------------------------
        r_curr += 1
        write_sec_hdr(r_curr, "2. ALIN KAYNAK AĞZI & KÖK YÜZEYİ DETAYLARI (BEVEL ANGLE & ROOT FACE)")
        r_curr += 1
        write_tbl_hdr(r_curr, headers_common)
        r_curr += 1

        theta_nom = bevel_data.get("bevel_angle_deg", 30.0)
        theta_act = bevel_data.get("bevel_angle_actual")
        theta_disp = f"{theta_act:.1f}° (Ölçülen)" if theta_act is not None else f"{theta_nom:.1f}° (Nominal)"
        c_nom = bevel_data.get("root_face_mm", 1.60)
        c_act = bevel_data.get("root_face_actual")
        c_disp = f"{c_act:.2f} mm (Ölçülen)" if c_act is not None else f"{c_nom:.2f} mm (Nominal)"

        h_bev = bevel_data.get("bevel_depth_mm", t_mm - 1.6)
        x_bev = bevel_data.get("axial_cut_width_mm", 7.33)
        w_bev = bevel_data.get("chamfer_face_length_mm", 14.67)
        inc_ang = bevel_data.get("included_groove_angle_deg", 60.0)
        half_area = bevel_data.get("groove_half_area_mm2", 46.5)
        full_area = bevel_data.get("total_v_groove_area_mm2", 93.0)

        sec2_rows = [
            ("Kaynak Ağzı Açısı (θ)", theta_disp, "derece (°)", "30° (+5° / -0°) [30.0° - 35.0°]", "Bridge Cam Gauge / Açı Mastarı"),
            ("Kök Yüzeyi / Küt Burun (c)", c_disp, "mm", "1.60 ± 0.80 mm [0.80 - 2.40 mm]", "Kumpas / Sentil / Kök Mastarı"),
            ("Ağız İşleme Derinliği (h_bevel)", f"{h_bev:.2f}", "mm", "h = t − c", "Dış yüzeyden kök yüzeyine düşey derinlik"),
            ("Eksenel Açılma Genişliği (X_bevel)", f"{x_bev:.2f}", "mm", "X = h · tan(θ)", "Boru ucu boyunca eksenel talaş genişliği"),
            ("Kaynak Ağzı Pah Boyu (W_bevel)", f"{w_bev:.2f}", "mm", "W = h / cos(θ)", "İşlenmiş eğimli alın yüzey boyu"),
            ("Alın Kaynağı V-Ağız Toplam Açısı", f"{inc_ang:.1f}°", "derece (°)", "2 · θ = 60° (+10° / -0°)", "İki boru ucu birleşiminde V tepe açısı"),
            ("Yarım V-Oluk Kesit Alanı (Tek Boru)", f"{half_area:.2f}", "mm²", "0.5 · h · X", "Tek boru ucu kaynak dolgu geometrisi"),
            ("Alın Kaynağı Tam V-Oluk Alanı (İki Boru)", f"{full_area:.2f}", "mm²", "h · X (V oluk)", "Kaynak teli sarfiyat hesap alanı"),
        ]

        for i, (param, val, unit, req, notes) in enumerate(sec2_rows):
            ws.row_dimensions[r_curr].height = 20
            c_fill = fill_zebra if i % 2 == 1 else None
            c1 = ws.cell(r_curr, 1, param); c1.font = font_bold; c1.alignment = align_left
            c2 = ws.cell(r_curr, 2, val); c2.font = font_mono_bold; c2.alignment = align_center
            c3 = ws.cell(r_curr, 3, unit); c3.font = font_regular; c3.alignment = align_center
            c4 = ws.cell(r_curr, 4, req); c4.font = font_info; c4.alignment = align_center
            c5 = ws.cell(r_curr, 5, notes); c5.font = font_info; c5.alignment = align_left
            for col in range(1, 6):
                cell = ws.cell(r_curr, col); cell.border = border_all
                if c_fill: cell.fill = c_fill
            r_curr += 1

        # -------------------------------------------------------------
        # Section 3: Out-of-Squareness
        # -------------------------------------------------------------
        r_curr += 1
        write_sec_hdr(r_curr, "3. BORU UCU DİKLİKTEN SAPMA KONTROLÜ (OUT-OF-SQUARENESS)")
        r_curr += 1
        write_tbl_hdr(r_curr, headers_common)
        r_curr += 1

        sq_act = bevel_data.get("out_of_squareness_actual")
        sq_disp = f"{sq_act:.2f} mm" if sq_act is not None else "≤ 1.60 mm (Sınır Limit)"
        sq_stat = "PASS" if (sq_act is not None and sq_act <= 1.60) else ("FAIL" if sq_act is not None else "UYGUN (LİMİTTE)")

        sec3_rows = [
            ("Boru Ucu Diklikten Sapma (e)", sq_disp, "mm", "≤ 1.60 mm (Maksimum)", "BOTAŞ Madde 5.5 / API 5L 9.12.5.1"),
            ("Ölçüm Cihazı & Sentil Yöntemi", "Hassas Çelik Gönye (Square)", "—", "Boru gövdesine 90° yaslanarak", "Uç açıklığı sentil ile ölçülür"),
            ("Diklik Uygunluk Durumu", sq_stat, "—", "e ≤ 1.60 mm ise PASS", "Saha alın kaynağında kök hizalaması için kritik"),
        ]

        for i, (param, val, unit, req, notes) in enumerate(sec3_rows):
            ws.row_dimensions[r_curr].height = 20
            c_fill = fill_zebra if i % 2 == 1 else None
            c1 = ws.cell(r_curr, 1, param); c1.font = font_bold; c1.alignment = align_left
            c2 = ws.cell(r_curr, 2, val); c2.font = font_mono_bold; c2.alignment = align_center
            if "PASS" in val: c2.font = font_pass; c2.fill = fill_pass
            elif "FAIL" in val: c2.font = font_fail; c2.fill = fill_fail
            c3 = ws.cell(r_curr, 3, unit); c3.font = font_regular; c3.alignment = align_center
            c4 = ws.cell(r_curr, 4, req); c4.font = font_info; c4.alignment = align_center
            c5 = ws.cell(r_curr, 5, notes); c5.font = font_info; c5.alignment = align_left
            for col in range(1, 6):
                cell = ws.cell(r_curr, col); cell.border = border_all
                if c_fill and cell.fill == PatternFill(): cell.fill = c_fill
            r_curr += 1

        # -------------------------------------------------------------
        # Section 4: End Diameter & Out-of-Roundness / Ovality
        # -------------------------------------------------------------
        r_curr += 1
        write_sec_hdr(r_curr, "4. BORU UCU ÇAP & DAİRESELLİKTEN SAPMA / OVALİTE (END DIAMETER & OVALITY)")
        r_curr += 1
        write_tbl_hdr(r_curr, headers_common)
        r_curr += 1

        d_min_all = bevel_data.get("end_dia_min_allowed_mm", d_mm - 1.6)
        d_max_all = bevel_data.get("end_dia_max_allowed_mm", d_mm + 1.6)
        ov_max = bevel_data.get("end_ovality_max_limit_mm", 3.0)
        ov_act = bevel_data.get("end_ovality_actual")
        ov_disp = f"{ov_act:.2f} mm" if ov_act is not None else f"≤ {ov_max:.2f} mm"

        sec4_rows = [
            ("Uç Çap Tolerans Aralığı (100 mm içinde)", f"{d_min_all:.2f} - {d_max_all:.2f}", "mm", "API 5L Tablo 10 / BOTAŞ", "Uçtan 100 mm mesafe içinde geçerlidir"),
            ("Maksimum İzin Verilen Ovalite Limiti", f"≤ {ov_max:.2f}", "mm", "BOTAŞ 8.1.2.4: max 3.0 mm (D/t≤75)", "D_max − D_min (Uç dairesellik sapması)"),
            ("Ölçülen Boru Ucu Ovalitesi (ΔD_end)", ov_disp, "mm", f"≤ {ov_max:.2f} mm", "Lazer Profil / Çok Noktalı Çapölçer"),
            ("Boru Uç Çap & Ovalite Kararı", "✓ UYGUN (PASS)" if (ov_act is None or ov_act <= ov_max) else "✗ RED (FAIL)", "—", "Şartname Sınırında", "API 5L Madde 10.2.8.1"),
        ]

        for i, (param, val, unit, req, notes) in enumerate(sec4_rows):
            ws.row_dimensions[r_curr].height = 20
            c_fill = fill_zebra if i % 2 == 1 else None
            c1 = ws.cell(r_curr, 1, param); c1.font = font_bold; c1.alignment = align_left
            c2 = ws.cell(r_curr, 2, val); c2.font = font_mono_bold; c2.alignment = align_center
            if "UYGUN" in val: c2.font = font_pass; c2.fill = fill_pass
            elif "RED" in val: c2.font = font_fail; c2.fill = fill_fail
            c3 = ws.cell(r_curr, 3, unit); c3.font = font_regular; c3.alignment = align_center
            c4 = ws.cell(r_curr, 4, req); c4.font = font_info; c4.alignment = align_center
            c5 = ws.cell(r_curr, 5, notes); c5.font = font_info; c5.alignment = align_left
            for col in range(1, 6):
                cell = ws.cell(r_curr, col); cell.border = border_all
                if c_fill and cell.fill == PatternFill(): cell.fill = c_fill
            r_curr += 1

        # -------------------------------------------------------------
        # Section 5: Internal Counterbore & Taper Transitions
        # -------------------------------------------------------------
        r_curr += 1
        write_sec_hdr(r_curr, "5. İÇ TALAŞ KALDIRMA & ET GEÇİŞİ (COUNTERBORE / TAPER BORING)")
        r_curr += 1
        write_tbl_hdr(r_curr, headers_common)
        r_curr += 1

        sec5_rows = [
            ("Maksimum İç Talaş Eğimi", "1:4 (14.0°)", "oran", "ASME B31.8 Şekil I-4", "Farklı et kalınlığı iç cidar geçişi"),
            ("Taper Geçiş Mesafesi (L_taper)", "L ≥ 4 · Δt_iç", "mm", "API 5L 9.12.5.5", "Kademesiz pürüzsüz geçiş konisi"),
            ("İç Çapak ve Çapak Taşlama", "Hemzemin / Düzgün", "—", "Oyuksuz", "İç kaynak başlangıç/bitiş traşı"),
        ]

        for i, (param, val, unit, req, notes) in enumerate(sec5_rows):
            ws.row_dimensions[r_curr].height = 20
            c_fill = fill_zebra if i % 2 == 1 else None
            c1 = ws.cell(r_curr, 1, param); c1.font = font_bold; c1.alignment = align_left
            c2 = ws.cell(r_curr, 2, val); c2.font = font_mono_bold; c2.alignment = align_center
            c3 = ws.cell(r_curr, 3, unit); c3.font = font_regular; c3.alignment = align_center
            c4 = ws.cell(r_curr, 4, req); c4.font = font_info; c4.alignment = align_center
            c5 = ws.cell(r_curr, 5, notes); c5.font = font_info; c5.alignment = align_left
            for col in range(1, 6):
                cell = ws.cell(r_curr, col); cell.border = border_all
                if c_fill: cell.fill = c_fill
            r_curr += 1

        # -------------------------------------------------------------
        # Section 6: Engineering Approval Block
        # -------------------------------------------------------------
        r_curr += 2
        ws.merge_cells(f"A{r_curr}:B{r_curr}")
        c = ws.cell(r_curr, 1, "HAZIRLAYAN (Boru Üretim & Kaynak Müh.)")
        c.font = font_bold; c.alignment = align_left

        ws.merge_cells(f"C{r_curr}:D{r_curr}")
        c = ws.cell(r_curr, 3, "KONTROL EDEN (QA/QC Şefi)")
        c.font = font_bold; c.alignment = align_left

        c = ws.cell(r_curr, 5, "ONAYLAYAN (Baş Denetçi / TPI / İdare)")
        c.font = font_bold; c.alignment = align_left
        ws.row_dimensions[r_curr].height = 20

        r_curr += 1
        ws.row_dimensions[r_curr].height = 32
        for col in (1, 3, 5):
            c = ws.cell(r_curr, col, "İmza / Kaşe / Tarih: ____________________")
            c.font = font_info
            c.alignment = align_left

        # Column widths
        widths = [44, 22, 14, 30, 48]
        for idx, w in enumerate(widths, 1):
            ws.column_dimensions[get_column_letter(idx)].width = w

        ws.freeze_panes = "A5"

        output = io.BytesIO()
        wb.save(output)
        output.seek(0)
        return output

    @classmethod
    def export_straightness_report(
        cls,
        project_info: Dict[str, Any],
        straightness_data: Dict[str, Any],
        pipe_info: Optional[Dict[str, Any]] = None,
        lang: str = "tr"
    ) -> io.BytesIO:
        """
        Exports official Pipe Straightness, Full-Length Sweep / Camber, and End Straightness
        Inspection Report to corporate Excel.
        Conforms to API Spec 5L Clause 9.11.3, Table 12 & BOTAŞ Clauses 5.5, 8.1.2.4.
        """
        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = "Düzlük & Sapma Raporu"
        ws.views.sheetView[0].showGridLines = True

        p_info = project_info or {}
        p_extra = pipe_info or {}

        # Colors & Fonts
        navy_dark = "1E3A8A"
        teal_hdr = "0F766E"
        blue_hdr = "1D4ED8"
        slate_hdr = "334155"
        zebra_bg = "F8FAFC"
        pass_green = "059669"
        fail_red = "DC2626"

        font_title = Font(name="Calibri", size=15, bold=True, color="FFFFFF")
        font_sub = Font(name="Calibri", size=9.5, italic=True, color="CBD5E1")
        font_sec = Font(name="Calibri", size=11, bold=True, color="FFFFFF")
        font_tbl_hdr = Font(name="Calibri", size=10, bold=True, color="FFFFFF")
        font_bold = Font(name="Calibri", size=10, bold=True, color="0F172A")
        font_regular = Font(name="Calibri", size=9.5, color="1E293B")
        font_mono_bold = Font(name="Consolas", size=10, bold=True, color="0F172A")
        font_info = Font(name="Calibri", size=9, color="475569")
        font_pass = Font(name="Calibri", size=10, bold=True, color="047857")
        font_fail = Font(name="Calibri", size=10, bold=True, color="B91C1C")

        fill_title = PatternFill(start_color=navy_dark, end_color=navy_dark, fill_type="solid")
        fill_sec = PatternFill(start_color=teal_hdr, end_color=teal_hdr, fill_type="solid")
        fill_tbl_hdr = PatternFill(start_color=slate_hdr, end_color=slate_hdr, fill_type="solid")
        fill_zebra = PatternFill(start_color=zebra_bg, end_color=zebra_bg, fill_type="solid")
        fill_pass = PatternFill(start_color="ECFDF5", end_color="ECFDF5", fill_type="solid")
        fill_fail = PatternFill(start_color="FEF2F2", end_color="FEF2F2", fill_type="solid")

        border_thin = Side(border_style="thin", color="CBD5E1")
        border_all = Border(left=border_thin, right=border_thin, top=border_thin, bottom=border_thin)

        align_center = Alignment(horizontal="center", vertical="center")
        align_left = Alignment(horizontal="left", vertical="center")
        align_right = Alignment(horizontal="right", vertical="center")

        # -------------------------------------------------------------
        # Header Block
        # -------------------------------------------------------------
        ws.merge_cells("A1:E1")
        ws.row_dimensions[1].height = 28
        c = ws.cell(1, 1, "API SPEC 5L & BOTAŞ BORU DÜZLÜK VE UÇ SAPMASI DOĞRULAMA RAPORU")
        c.font = font_title; c.fill = fill_title; c.alignment = align_center

        ws.merge_cells("A2:E2")
        ws.row_dimensions[2].height = 20
        c = ws.cell(2, 1, "API Spec 5L 47. Baskı Madde 9.11.3 & BOTAŞ Şartnamesi Madde 5.5, 8.1.2.4 — Tam Boy Sehim & Uç Sapması Muayene Raporu")
        c.font = font_sub; c.fill = fill_title; c.alignment = align_center

        ws.row_dimensions[3].height = 10

        r_curr = 4

        # -------------------------------------------------------------
        # Section 1: Proje & Boru Genel Bilgileri
        # -------------------------------------------------------------
        ws.merge_cells(f"A{r_curr}:E{r_curr}")
        ws.row_dimensions[r_curr].height = 22
        c = ws.cell(r_curr, 1, "1. PROJE VE BORU TANIMLAMA BİLGİLERİ")
        c.font = font_sec; c.fill = fill_sec; c.alignment = align_left
        r_curr += 1

        d_mm = straightness_data.get("diameter_mm") or p_extra.get("diameter_mm") or 1219.0
        t_mm = straightness_data.get("wall_thickness_mm") or p_extra.get("wall_thickness_mm") or 14.30
        l_m = straightness_data.get("pipe_length_m") or p_extra.get("pipe_length_m") or 12.0
        grade = straightness_data.get("material_grade") or p_extra.get("material_grade") or "X65"
        proc = straightness_data.get("manufacturing_process") or p_extra.get("manufacturing_process") or "SAWH"
        std = straightness_data.get("standard_code") or "BOTAŞ"
        is_botas = straightness_data.get("is_botas", True)

        info_rows = [
            ("Proje Adı", p_info.get("project_name") or "API 5L / BOTAŞ Boru Hattı İletim Hattı Projesi",
             "Rapor Tarihi", datetime.now().strftime("%d.%m.%Y %H:%M")),
            ("Boru Çapı (D)", f"{d_mm:.1f} mm ({p_extra.get('diameter_inch') or '48\"'})",
             "Et Kalınlığı (t)", f"{t_mm:.2f} mm"),
            ("Boru Boyu (L)", f"{l_m:.2f} m ({l_m*1000:.0f} mm)",
             "Çelik Kalitesi & Tip", f"{grade} ({proc})"),
            ("Standart / Şartname", f"{std} (API Spec 5L 47th Ed. / ISO 3183)",
             "Denetim Yöntemi", "Lazer Kolimatör / Çelik Piyano Teli & 1.0 m Hassas Çelik Mastar"),
        ]

        for r_data in info_rows:
            ws.row_dimensions[r_curr].height = 20
            c = ws.cell(r_curr, 1, r_data[0]); c.font = font_bold; c.fill = fill_zebra; c.border = border_all
            c = ws.cell(r_curr, 2, r_data[1]); c.font = font_regular; c.border = border_all
            c = ws.cell(r_curr, 3, r_data[2]); c.font = font_bold; c.fill = fill_zebra; c.border = border_all
            ws.merge_cells(f"D{r_curr}:E{r_curr}")
            c = ws.cell(r_curr, 4, r_data[3]); c.font = font_regular; c.border = border_all
            ws.cell(r_curr, 5).border = border_all
            r_curr += 1

        r_curr += 1

        # -------------------------------------------------------------
        # Section 2: Düzlük Kabul Kriterleri & Tolerans Limitleri
        # -------------------------------------------------------------
        ws.merge_cells(f"A{r_curr}:E{r_curr}")
        ws.row_dimensions[r_curr].height = 22
        c = ws.cell(r_curr, 1, "2. DÜZLÜK KABUL KRİTERLERİ VE STANDART LİMİTLERİ")
        c.font = font_sec; c.fill = fill_sec; c.alignment = align_left
        r_curr += 1

        total_limit_mm = straightness_data.get("total_straightness_max_limit_mm", 18.0)
        total_ratio_pct = straightness_data.get("total_straightness_ratio_pct", 0.15)
        end_limit_mm = straightness_data.get("end_straightness_max_limit_mm", 3.0)
        end_chord_m = straightness_data.get("end_chord_length_m", 1.0)

        param_rows = [
            ("Tam Boy Maksimum Düzlük Sapması Oranı", f"%{total_ratio_pct:.2f} × L",
             "BOTAŞ 5.5 / 8.1.2.4 (API 5L Tablo 12: %0.20 × L)"),
            ("Tam Boy İzin Verilen Maksimum Sehim (f_max)", f"≤ {total_limit_mm:.2f} mm",
             f"L = {l_m:.1f} m boyundaki borunun tüm ekseni boyunca izin verilen en büyük sapma"),
            ("Boru Ucu Mastar Ölçüm Aralığı (Chord)", f"{end_chord_m:.2f} m ({end_chord_m*1000:.0f} mm)",
             "Her iki boru ucundan içeriye doğru referans çelik mastar boyu"),
            ("Uç Düzlüğü İzin Verilen Maksimum Sapma (f_end)", f"≤ {end_limit_mm:.2f} mm",
             "BOTAŞ 8.1.2.4 (≤ 3.00 mm) / API 5L 9.11.3.2 (≤ 4.00 mm)"),
        ]

        for p_label, p_val, p_desc in param_rows:
            ws.row_dimensions[r_curr].height = 20
            ws.merge_cells(f"A{r_curr}:B{r_curr}")
            c = ws.cell(r_curr, 1, p_label); c.font = font_bold; c.border = border_all
            ws.cell(r_curr, 2).border = border_all
            c = ws.cell(r_curr, 3, p_val); c.font = font_mono_bold; c.alignment = align_center; c.border = border_all
            ws.merge_cells(f"D{r_curr}:E{r_curr}")
            c = ws.cell(r_curr, 4, p_desc); c.font = font_info; c.border = border_all
            ws.cell(r_curr, 5).border = border_all
            r_curr += 1

        r_curr += 1

        # -------------------------------------------------------------
        # Section 3: QA/QC Doğrulama & Denetim Sonuçları Tablosu
        # -------------------------------------------------------------
        ws.merge_cells(f"A{r_curr}:E{r_curr}")
        ws.row_dimensions[r_curr].height = 22
        c = ws.cell(r_curr, 1, "3. DÜZLÜK VE UÇ SAPMASI DOĞRULAMA (INSPECTION CHECKS)")
        c.font = font_sec; c.fill = fill_sec; c.alignment = align_left
        r_curr += 1

        tbl_headers = ["Denetim Parametresi", "Nominal / Hedef", "İzin Verilen Limit", "Ölçülen Değer", "Durum & Standart"]
        ws.row_dimensions[r_curr].height = 24
        for idx, h_text in enumerate(tbl_headers, 1):
            c = ws.cell(r_curr, idx, h_text)
            c.font = font_tbl_hdr; c.fill = fill_tbl_hdr; c.alignment = align_center; c.border = border_all
        r_curr += 1

        checks = straightness_data.get("checks", [])
        for chk in checks:
            ws.row_dimensions[r_curr].height = 22
            p_name = chk.get("parameter", "")
            nom_str = "0,00 mm"
            crit_str = chk.get("criteria", "")
            act_val = chk.get("actual")
            act_str = f"{act_val:.2f} mm" if act_val is not None else "Ölçüm Bekleniyor"
            status = chk.get("status", "NOT_EVALUATED")
            clause = chk.get("clause", "")

            c = ws.cell(r_curr, 1, p_name); c.font = font_bold; c.border = border_all
            c = ws.cell(r_curr, 2, nom_str); c.font = font_regular; c.alignment = align_center; c.border = border_all
            c = ws.cell(r_curr, 3, crit_str); c.font = font_mono_bold; c.alignment = align_center; c.border = border_all
            c = ws.cell(r_curr, 4, act_str); c.font = font_mono_bold; c.alignment = align_center; c.border = border_all

            c = ws.cell(r_curr, 5, f"{status} — {clause}")
            if status == "PASS":
                c.font = font_pass; c.fill = fill_pass
            elif status == "FAIL":
                c.font = font_fail; c.fill = fill_fail
            else:
                c.font = font_regular; c.fill = fill_zebra
            c.alignment = align_left; c.border = border_all
            r_curr += 1

        r_curr += 1

        # -------------------------------------------------------------
        # Section 4: Boyuna İstasyon Sehim Koordinatları Tablosu
        # -------------------------------------------------------------
        ws.merge_cells(f"A{r_curr}:E{r_curr}")
        ws.row_dimensions[r_curr].height = 22
        c = ws.cell(r_curr, 1, "4. BOYUNA LAZER / TEL ÖLÇÜM İSTASYONLARI VE SEHİM PROFİLİ")
        c.font = font_sec; c.fill = fill_sec; c.alignment = align_left
        r_curr += 1

        st_headers = ["İstasyon Tanımı", "Eksenel Konum x (m)", "Maks. İzin Verilen Sehim (mm)", "Ölçülen / Model Değeri (mm)", "Denetim Notu"]
        ws.row_dimensions[r_curr].height = 22
        for idx, h_text in enumerate(st_headers, 1):
            c = ws.cell(r_curr, idx, h_text)
            c.font = font_tbl_hdr; c.fill = PatternFill(start_color=blue_hdr, end_color=blue_hdr, fill_type="solid")
            c.alignment = align_center; c.border = border_all
        r_curr += 1

        stations = straightness_data.get("stations", [])
        for st in stations:
            ws.row_dimensions[r_curr].height = 20
            s_name = st.get("station", "")
            s_x = st.get("x_m", 0.0)
            s_lim = st.get("allowed_envelope_mm", 0.0)
            s_sim = st.get("simulated_deviation_mm", 0.0)
            s_type = st.get("location_type", "")

            if "end" in s_type:
                note = "Boru ucu referans sıfır noktası"
            elif "chord" in s_type:
                note = f"Uç mastar bölgesi (Limit: ≤ {end_limit_mm:.2f} mm)"
            elif "midspan" in s_type:
                note = f"Tepe sehim noktası (L/2) — Kritik Değer (Limit: ≤ {total_limit_mm:.2f} mm)"
            else:
                note = "Ara gövde lazer okuma noktası"

            c = ws.cell(r_curr, 1, s_name); c.font = font_bold; c.border = border_all
            c = ws.cell(r_curr, 2, f"{s_x:.2f} m"); c.font = font_mono_bold; c.alignment = align_center; c.border = border_all
            c = ws.cell(r_curr, 3, f"≤ {s_lim:.2f} mm"); c.font = font_regular; c.alignment = align_center; c.border = border_all
            c = ws.cell(r_curr, 4, f"{s_sim:.2f} mm"); c.font = font_mono_bold; c.alignment = align_center; c.border = border_all
            c = ws.cell(r_curr, 5, note); c.font = font_info; c.border = border_all
            r_curr += 1

        r_curr += 1

        # -------------------------------------------------------------
        # Section 5: Nihai Değerlendirme & Karar Bloğu
        # -------------------------------------------------------------
        ws.merge_cells(f"A{r_curr}:E{r_curr}")
        ws.row_dimensions[r_curr].height = 22
        c = ws.cell(r_curr, 1, "5. NİHAİ KALİTE GÜVENCE DEĞERLENDİRMESİ")
        c.font = font_sec; c.fill = fill_sec; c.alignment = align_left
        r_curr += 1

        verdict = straightness_data.get("verdict", "NOMINAL (DENETİME HAZIR)")
        is_compliant = straightness_data.get("is_compliant", True)

        ws.merge_cells(f"A{r_curr}:B{r_curr}")
        c = ws.cell(r_curr, 1, "NİHAİ UYGUNLUK KARARI"); c.font = font_bold; c.border = border_all
        ws.cell(r_curr, 2).border = border_all

        ws.merge_cells(f"C{r_curr}:E{r_curr}")
        c = ws.cell(r_curr, 3, verdict)
        if is_compliant and "UYGUN" in verdict:
            c.font = Font(name="Calibri", size=13, bold=True, color="047857")
            c.fill = fill_pass
        elif not is_compliant:
            c.font = Font(name="Calibri", size=13, bold=True, color="B91C1C")
            c.fill = fill_fail
        else:
            c.font = Font(name="Calibri", size=13, bold=True, color="1D4ED8")
            c.fill = fill_zebra
        c.alignment = align_center; c.border = border_all
        ws.cell(r_curr, 4).border = border_all
        ws.cell(r_curr, 5).border = border_all
        ws.row_dimensions[r_curr].height = 30
        r_curr += 1

        # Methodology Explanation Row
        methodology = straightness_data.get("methodology_note", "")
        ws.merge_cells(f"A{r_curr}:E{r_curr}")
        ws.row_dimensions[r_curr].height = 40
        c = ws.cell(r_curr, 1, methodology)
        c.font = font_info; c.alignment = Alignment(horizontal="left", vertical="center", wrap_text=True)
        c.border = border_all
        for col_idx in range(2, 6):
            ws.cell(r_curr, col_idx).border = border_all
        r_curr += 2

        # -------------------------------------------------------------
        # Section 6: Onay ve İmza Bloğu
        # -------------------------------------------------------------
        ws.merge_cells(f"A{r_curr}:E{r_curr}")
        ws.row_dimensions[r_curr].height = 20
        c = ws.cell(r_curr, 1, "6. MÜHENDİSLİK KONTROL VE ONAY İMZALARI")
        c.font = font_sec; c.fill = fill_sec; c.alignment = align_left
        r_curr += 1

        ws.row_dimensions[r_curr].height = 24
        c = ws.cell(r_curr, 1, "HAZIRLAYAN (Boyutsal Kontrol Denetçisi)")
        c.font = font_bold; c.alignment = align_left

        c = ws.cell(r_curr, 3, "KONTROL EDEN (QA/QC Şefi)")
        c.font = font_bold; c.alignment = align_left

        c = ws.cell(r_curr, 5, "ONAYLAYAN (Baş Denetçi / TPI / İdare)")
        c.font = font_bold; c.alignment = align_left
        r_curr += 1

        ws.row_dimensions[r_curr].height = 32
        for col in (1, 3, 5):
            c = ws.cell(r_curr, col, "İmza / Kaşe / Tarih: ____________________")
            c.font = font_info
            c.alignment = align_left

        # Column widths
        widths = [44, 24, 26, 26, 44]
        for idx, w in enumerate(widths, 1):
            ws.column_dimensions[get_column_letter(idx)].width = w

        ws.freeze_panes = "A5"

        output = io.BytesIO()
        wb.save(output)
        output.seek(0)
        return output

    @classmethod
    def export_derating_report(
        cls,
        project_info: Dict[str, Any],
        derating_data: Dict[str, Any],
        pipe_info: Optional[Dict[str, Any]] = None,
        lang: str = "tr"
    ) -> io.BytesIO:
        """
        Exports official Wall Thickness Underflow (Minus Tolerance), Barlow Design Pressure
        Derating, and Hydrostatic Hoop Stress Verification Report to corporate Excel.
        Conforms to API Spec 5L Table 11 & ASME B31.8 Section 841.1.
        """
        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = "Et Kalınlığı İndirgeme Raporu"
        ws.views.sheetView[0].showGridLines = True

        p_info = project_info or {}
        p_extra = pipe_info or {}

        # Colors & Fonts
        navy_dark = "1E3A8A"
        teal_hdr = "0F766E"
        blue_hdr = "1D4ED8"
        slate_hdr = "334155"
        amber_hdr = "B45309"
        zebra_bg = "F8FAFC"
        pass_green = "059669"
        fail_red = "DC2626"

        font_title = Font(name="Calibri", size=14, bold=True, color="FFFFFF")
        font_sub = Font(name="Calibri", size=9.5, italic=True, color="CBD5E1")
        font_sec = Font(name="Calibri", size=11, bold=True, color="FFFFFF")
        font_tbl_hdr = Font(name="Calibri", size=10, bold=True, color="FFFFFF")
        font_bold = Font(name="Calibri", size=10, bold=True, color="0F172A")
        font_regular = Font(name="Calibri", size=9.5, color="1E293B")
        font_mono_bold = Font(name="Consolas", size=10, bold=True, color="0F172A")
        font_info = Font(name="Calibri", size=9, color="475569")
        font_pass = Font(name="Calibri", size=10, bold=True, color="047857")
        font_fail = Font(name="Calibri", size=10, bold=True, color="B91C1C")

        fill_title = PatternFill(start_color=navy_dark, end_color=navy_dark, fill_type="solid")
        fill_sec = PatternFill(start_color=teal_hdr, end_color=teal_hdr, fill_type="solid")
        fill_tbl_hdr = PatternFill(start_color=slate_hdr, end_color=slate_hdr, fill_type="solid")
        fill_zebra = PatternFill(start_color=zebra_bg, end_color=zebra_bg, fill_type="solid")
        fill_pass = PatternFill(start_color="ECFDF5", end_color="ECFDF5", fill_type="solid")
        fill_fail = PatternFill(start_color="FEF2F2", end_color="FEF2F2", fill_type="solid")

        border_thin = Side(border_style="thin", color="CBD5E1")
        border_all = Border(left=border_thin, right=border_thin, top=border_thin, bottom=border_thin)

        align_center = Alignment(horizontal="center", vertical="center")
        align_left = Alignment(horizontal="left", vertical="center")
        align_right = Alignment(horizontal="right", vertical="center")

        # -------------------------------------------------------------
        # Header Block
        # -------------------------------------------------------------
        ws.merge_cells("A1:E1")
        ws.row_dimensions[1].height = 28
        c = ws.cell(1, 1, "API SPEC 5L & ASME B31.8 ET KALINLIĞI TOLERANS ALTI & BASINÇ İNDİRGEME RAPORU")
        c.font = font_title; c.fill = fill_title; c.alignment = align_center

        ws.merge_cells("A2:E2")
        ws.row_dimensions[2].height = 20
        c = ws.cell(2, 1, "API Spec 5L Çizelge 11 & ASME B31.8 Madde 841.1 — Eksi Tolerans, Barlow Basınç Kaybı & Hidro Gerilme Sıçraması")
        c.font = font_sub; c.fill = fill_title; c.alignment = align_center

        ws.row_dimensions[3].height = 10
        r_curr = 4

        # -------------------------------------------------------------
        # Section 1: Proje ve Boru Genel Bilgileri
        # -------------------------------------------------------------
        ws.merge_cells(f"A{r_curr}:E{r_curr}")
        ws.row_dimensions[r_curr].height = 22
        c = ws.cell(r_curr, 1, "1. PROJE VE BORU TANIMLAMA BİLGİLERİ")
        c.font = font_sec; c.fill = fill_sec; c.alignment = align_left
        r_curr += 1

        d_mm = derating_data.get("diameter_mm") or p_extra.get("diameter_mm") or 1219.0
        t_mm = derating_data.get("wall_thickness_mm") or p_extra.get("wall_thickness_mm") or 14.30
        l_m = derating_data.get("pipe_length_m") or p_extra.get("pipe_length_m") or 12.0
        grade = derating_data.get("material_grade") or p_extra.get("material_grade") or "X65"
        proc = derating_data.get("manufacturing_process") or p_extra.get("manufacturing_process") or "SAWH"
        std = derating_data.get("standard_code") or "BOTAŞ"
        smys = derating_data.get("smys_mpa", 450.0)
        f_fact = derating_data.get("design_factor_f", 0.72)
        ca = derating_data.get("corrosion_allowance_mm", 0.0)

        info_rows = [
            ("Proje Adı", p_info.get("project_name") or "API 5L / BOTAŞ Boru Hattı İletim Projesi",
             "Rapor Tarihi", datetime.now().strftime("%d.%m.%Y %H:%M")),
            ("Boru Çapı (D)", f"{d_mm:.1f} mm ({p_extra.get('diameter_inch') or '48\"'})",
             "Nominal Et Kalınlığı (t)", f"{t_mm:.2f} mm"),
            ("Çelik Kalitesi & SMYS", f"{grade} (SMYS = {smys:.0f} MPa)",
             "İmalat Yöntemi & Standart", f"{proc} ({std})"),
            ("Tasarım Faktörü (F)", f"{f_fact:.2f} (ASME B31.8 Sınıf 1)",
             "Korozyon Payı (CA)", f"{ca:.2f} mm"),
        ]

        for r_data in info_rows:
            ws.row_dimensions[r_curr].height = 20
            c = ws.cell(r_curr, 1, r_data[0]); c.font = font_bold; c.fill = fill_zebra; c.border = border_all
            c = ws.cell(r_curr, 2, r_data[1]); c.font = font_regular; c.border = border_all
            c = ws.cell(r_curr, 3, r_data[2]); c.font = font_bold; c.fill = fill_zebra; c.border = border_all
            ws.merge_cells(f"D{r_curr}:E{r_curr}")
            c = ws.cell(r_curr, 4, r_data[3]); c.font = font_regular; c.border = border_all
            ws.cell(r_curr, 5).border = border_all
            r_curr += 1

        r_curr += 1

        # -------------------------------------------------------------
        # Section 2: Et Kalınlığı İmalat Toleransları
        # -------------------------------------------------------------
        ws.merge_cells(f"A{r_curr}:E{r_curr}")
        ws.row_dimensions[r_curr].height = 22
        c = ws.cell(r_curr, 1, "2. ET KALINLIĞI İMALAT TOLERANSLARI (API 5L ÇİZELGE 11 & BOTAŞ)")
        c.font = font_sec; c.fill = fill_sec; c.alignment = align_left
        r_curr += 1

        tol_pos_pct = derating_data.get("tol_pos_pct", 10.0)
        tol_neg_pct = derating_data.get("tol_neg_pct", -10.0)
        tol_pos_mm = derating_data.get("tol_pos_mm", 1.43)
        tol_neg_mm = derating_data.get("tol_neg_mm", -1.43)
        t_min = derating_data.get("t_min_allowed_mm", 12.87)
        t_max = derating_data.get("t_max_allowed_mm", 15.73)

        tol_rows = [
            ("Artı Tolerans (+)", f"+%{tol_pos_pct:.1f} (+{tol_pos_mm:.2f} mm)", f"Maksimum izin verilen cidar: t_max = {t_max:.2f} mm"),
            ("Eksi Tolerans (-) [KRİTİK]", f"%{tol_neg_pct:.1f} ({tol_neg_mm:.2f} mm)", f"Minimum izin verilen cidar: t_min = {t_min:.2f} mm"),
            ("İzin Verilen Tolerans Bandı", f"[{t_min:.2f} mm — {t_max:.2f} mm]", "API 5L Tablo 11 & BOTAŞ 8.1.2.4 fabrika kabul bandı"),
        ]

        for t_label, t_val, t_desc in tol_rows:
            ws.row_dimensions[r_curr].height = 20
            ws.merge_cells(f"A{r_curr}:B{r_curr}")
            c = ws.cell(r_curr, 1, t_label); c.font = font_bold; c.border = border_all
            ws.cell(r_curr, 2).border = border_all
            c = ws.cell(r_curr, 3, t_val); c.font = font_mono_bold; c.alignment = align_center; c.border = border_all
            ws.merge_cells(f"D{r_curr}:E{r_curr}")
            c = ws.cell(r_curr, 4, t_desc); c.font = font_info; c.border = border_all
            ws.cell(r_curr, 5).border = border_all
            r_curr += 1

        r_curr += 1

        # -------------------------------------------------------------
        # Section 3: Barlow Basınç Kapasitesi Karşılaştırma & Derating
        # -------------------------------------------------------------
        ws.merge_cells(f"A{r_curr}:E{r_curr}")
        ws.row_dimensions[r_curr].height = 22
        c = ws.cell(r_curr, 1, "3. BARLOW TASARIM BASINCI VE GÜVENLİK MARJI İNDİRGEMESİ (DERATING)")
        c.font = font_sec; c.fill = fill_sec; c.alignment = align_left
        r_curr += 1

        ws.row_dimensions[r_curr].height = 24
        tbl_headers = ["Performans Parametresi", "Nominal Kalınlık (t_nom)", "Alt Sınır (t_min)", "Fark / Değişim (Δ)", "Mühendislik Yorumu"]
        for idx, h_text in enumerate(tbl_headers, 1):
            c = ws.cell(r_curr, idx, h_text)
            c.font = font_tbl_hdr; c.fill = fill_tbl_hdr; c.alignment = align_center; c.border = border_all
        r_curr += 1

        p_nom = derating_data.get("p_des_nom_bar", 76.0)
        p_min = derating_data.get("p_des_min_bar", 68.4)
        dp = derating_data.get("delta_p_des_bar", 7.6)
        dp_pct = derating_data.get("derating_loss_pct", 10.0)

        sig_op_nom = derating_data.get("sigma_op_nom_mpa", 324.0)
        sig_op_min = derating_data.get("sigma_op_min_mpa", 360.0)
        util_nom = derating_data.get("hoop_util_nom_pct", 72.0)
        util_min = derating_data.get("hoop_util_min_pct", 80.0)

        comp_rows = [
            ("Efektif Taşıyıcı Cidar (t - CA)", f"{t_mm - ca:.2f} mm", f"{t_min - ca:.2f} mm", f"-{t_mm - t_min:.2f} mm", "Haddelenmiş net et kalınlığı"),
            ("Barlow Tasarım Basıncı (P_des)", f"{p_nom:.2f} bar", f"{p_min:.2f} bar", f"-{dp:.2f} bar (-%{dp_pct:.1f})", "Maksimum güvenli hat işletme basıncı"),
            ("İşletme Çeper Gerilmesi (σ_h)", f"{sig_op_nom:.1f} MPa", f"{sig_op_min:.1f} MPa", f"+{sig_op_min - sig_op_nom:.1f} MPa", "P_nom basıncında çeper gerilme artışı"),
            ("Gerilme / SMYS Kullanım Oranı", f"%{util_nom:.1f} SMYS", f"%{util_min:.1f} SMYS", f"+%{util_min - util_nom:.1f} SMYS", "Emniyet marjı daralması"),
        ]

        for p_name, v_nom, v_min, v_diff, v_comm in comp_rows:
            ws.row_dimensions[r_curr].height = 22
            c = ws.cell(r_curr, 1, p_name); c.font = font_bold; c.border = border_all
            c = ws.cell(r_curr, 2, v_nom); c.font = font_mono_bold; c.alignment = align_center; c.border = border_all
            c = ws.cell(r_curr, 3, v_min); c.font = font_mono_bold; c.alignment = align_center; c.border = border_all
            c = ws.cell(r_curr, 4, v_diff); c.font = Font(name="Consolas", size=10, bold=True, color="B91C1C"); c.alignment = align_center; c.border = border_all
            c = ws.cell(r_curr, 5, v_comm); c.font = font_info; c.border = border_all
            r_curr += 1

        r_curr += 1

        # -------------------------------------------------------------
        # Section 4: Fabrika Hidrostatik Test Gerilme Sıçraması
        # -------------------------------------------------------------
        ws.merge_cells(f"A{r_curr}:E{r_curr}")
        ws.row_dimensions[r_curr].height = 22
        c = ws.cell(r_curr, 1, "4. FABRİKA HİDROSTATİK TEST GERİLME SIÇRAMASI (API 5L 10.2.6.7)")
        c.font = font_sec; c.fill = fill_sec; c.alignment = align_left
        r_curr += 1

        p_hydro = derating_data.get("hydro_test_pressure_bar", 100.0)
        h_nom_pct = derating_data.get("hydro_smys_nom_pct", 95.0)
        h_min_pct = derating_data.get("hydro_smys_min_pct", 105.6)
        h_jump = derating_data.get("hydro_stress_jump_pct", 10.6)
        is_crit = derating_data.get("is_hydro_stress_critical", False)

        hydro_rows = [
            ("Uygulanan Test Basıncı (P_hydro)", f"{p_hydro:.1f} bar", "Fabrika presi hidrostatik test basıncı"),
            ("Nominal Cidar Test Gerilmesi", f"%{h_nom_pct:.1f} SMYS", "Hedef fabrika gerilme düzeyi (≤ %95 SMYS)"),
            ("Alt Sınırda (t_min) Gerçekleşen Gerilme", f"%{h_min_pct:.1f} SMYS", "Plastik deformasyon eşiği kontrolü (≤ %100 SMYS)"),
            ("Gerilme Sıçraması (Stress Jump)", f"+%{h_jump:.1f} SMYS", "Eksi tolerans nedeniyle çeperdeki ilave gerilme yığılması"),
        ]

        for h_label, h_val, h_desc in hydro_rows:
            ws.row_dimensions[r_curr].height = 20
            ws.merge_cells(f"A{r_curr}:B{r_curr}")
            c = ws.cell(r_curr, 1, h_label); c.font = font_bold; c.border = border_all
            ws.cell(r_curr, 2).border = border_all
            c = ws.cell(r_curr, 3, h_val)
            if "Alt Sınırda" in h_label and is_crit:
                c.font = font_fail; c.fill = fill_fail
            else:
                c.font = font_mono_bold
            c.alignment = align_center; c.border = border_all
            ws.merge_cells(f"D{r_curr}:E{r_curr}")
            c = ws.cell(r_curr, 4, h_desc); c.font = font_info; c.border = border_all
            ws.cell(r_curr, 5).border = border_all
            r_curr += 1

        r_curr += 1

        # -------------------------------------------------------------
        # Section 5: Çelik Kütlesi ve Ağırlık Varyansı
        # -------------------------------------------------------------
        ws.merge_cells(f"A{r_curr}:E{r_curr}")
        ws.row_dimensions[r_curr].height = 22
        c = ws.cell(r_curr, 1, "5. ÇELİK KÜTLESİ VE AĞIRLIK DEĞİŞİMİ (API 5L 9.11.3 FORMÜLÜ)")
        c.font = font_sec; c.fill = fill_sec; c.alignment = align_left
        r_curr += 1

        m_nom_m = derating_data.get("mass_nom_kg_m", 425.0)
        m_min_m = derating_data.get("mass_min_kg_m", 383.0)
        m_nom_p = derating_data.get("mass_nom_pipe_kg", 5100.0)
        m_min_p = derating_data.get("mass_min_pipe_kg", 4600.0)
        m_loss = derating_data.get("mass_loss_per_pipe_kg", 500.0)
        m_var_pct = derating_data.get("mass_variance_pct", -9.8)

        mass_rows = [
            ("Birim Metre Kütlesi (kg/m)", f"Nominal: {m_nom_m:.2f} kg/m", f"Alt Sınır: {m_min_m:.2f} kg/m", f"Varyans: %{m_var_pct:.1f}"),
            (f"Tek Boru Kütlesi (L = {l_m:.1f} m)", f"Nominal: {m_nom_p:.1f} kg", f"Alt Sınır: {m_min_p:.1f} kg", f"Fark: -{m_loss:.1f} kg / boru"),
        ]

        for m_label, m_v1, m_v2, m_v3 in mass_rows:
            ws.row_dimensions[r_curr].height = 20
            ws.merge_cells(f"A{r_curr}:B{r_curr}")
            c = ws.cell(r_curr, 1, m_label); c.font = font_bold; c.border = border_all
            ws.cell(r_curr, 2).border = border_all
            c = ws.cell(r_curr, 3, m_v1); c.font = font_mono_bold; c.alignment = align_center; c.border = border_all
            c = ws.cell(r_curr, 4, m_v2); c.font = font_mono_bold; c.alignment = align_center; c.border = border_all
            c = ws.cell(r_curr, 5, m_v3); c.font = font_bold; c.alignment = align_center; c.border = border_all
            r_curr += 1

        r_curr += 1

        # -------------------------------------------------------------
        # Section 6: Nihai Değerlendirme & Karar Bloğu
        # -------------------------------------------------------------
        ws.merge_cells(f"A{r_curr}:E{r_curr}")
        ws.row_dimensions[r_curr].height = 22
        c = ws.cell(r_curr, 1, "6. NİHAİ KALİTE GÜVENCE VE EMNİYET KARARI")
        c.font = font_sec; c.fill = fill_sec; c.alignment = align_left
        r_curr += 1

        verdict = derating_data.get("verdict", "NOMINAL (DENETİME HAZIR)")
        is_compliant = derating_data.get("is_compliant", True)

        ws.merge_cells(f"A{r_curr}:B{r_curr}")
        c = ws.cell(r_curr, 1, "NİHAİ UYGUNLUK KARARI"); c.font = font_bold; c.border = border_all
        ws.cell(r_curr, 2).border = border_all

        ws.merge_cells(f"C{r_curr}:E{r_curr}")
        c = ws.cell(r_curr, 3, verdict)
        if is_compliant and "UYGUN" in verdict:
            c.font = Font(name="Calibri", size=13, bold=True, color="047857")
            c.fill = fill_pass
        elif not is_compliant:
            c.font = Font(name="Calibri", size=13, bold=True, color="B91C1C")
            c.fill = fill_fail
        else:
            c.font = Font(name="Calibri", size=13, bold=True, color="1D4ED8")
            c.fill = fill_zebra
        c.alignment = align_center; c.border = border_all
        ws.cell(r_curr, 4).border = border_all
        ws.cell(r_curr, 5).border = border_all
        ws.row_dimensions[r_curr].height = 30
        r_curr += 1

        # Methodology Explanation
        methodology = derating_data.get("methodology_note", "")
        ws.merge_cells(f"A{r_curr}:E{r_curr}")
        ws.row_dimensions[r_curr].height = 42
        c = ws.cell(r_curr, 1, methodology)
        c.font = font_info; c.alignment = Alignment(horizontal="left", vertical="center", wrap_text=True)
        c.border = border_all
        for col_idx in range(2, 6):
            ws.cell(r_curr, col_idx).border = border_all
        r_curr += 2

        # -------------------------------------------------------------
        # Section 7: Onay ve İmza Bloğu
        # -------------------------------------------------------------
        ws.merge_cells(f"A{r_curr}:E{r_curr}")
        ws.row_dimensions[r_curr].height = 20
        c = ws.cell(r_curr, 1, "7. MÜHENDİSLİK KONTROL VE ONAY İMZALARI")
        c.font = font_sec; c.fill = fill_sec; c.alignment = align_left
        r_curr += 1

        ws.row_dimensions[r_curr].height = 24
        c = ws.cell(r_curr, 1, "HAZIRLAYAN (Boru Tasarım Mühendisi)")
        c.font = font_bold; c.alignment = align_left

        c = ws.cell(r_curr, 3, "KONTROL EDEN (QA/QC Şefi)")
        c.font = font_bold; c.alignment = align_left

        c = ws.cell(r_curr, 5, "ONAYLAYAN (Baş Denetçi / TPI / İdare)")
        c.font = font_bold; c.alignment = align_left
        r_curr += 1

        ws.row_dimensions[r_curr].height = 32
        for col in (1, 3, 5):
            c = ws.cell(r_curr, col, "İmza / Kaşe / Tarih: ____________________")
            c.font = font_info
            c.alignment = align_left

        # Column widths
        widths = [42, 25, 25, 26, 44]
        for idx, w in enumerate(widths, 1):
            ws.column_dimensions[get_column_letter(idx)].width = w

        ws.freeze_panes = "A5"

        output = io.BytesIO()
        wb.save(output)
        output.seek(0)
        return output





