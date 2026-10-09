# -*- coding: utf-8 -*-
"""
core/pdf_exporter.py
High-Grade Engineering PDF Exporter for API 5L & BOTAŞ ITP Compliance Reports.
Generates publication-quality, landscape A4 PDF reports with executive KPI dashboards,
project & pipe specifications, discrepancies, and full side-by-side audit matrices.
"""

import datetime
import io
import os
from typing import Any, Dict, List, Optional

from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, KeepTogether, HRFlowable
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

try:
    from version import __version__
except Exception:
    __version__ = "2.11.0"


class NumberedCanvas(canvas.Canvas):
    """
    Two-pass canvas to dynamically compute and print total page numbers: 'Sayfa X / Y'.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_decorations(num_pages)
            super().showPage()
        super().save()

    def draw_page_decorations(self, page_count: int):
        self.saveState()
        w, h = landscape(A4)
        
        # Header rule & title (on pages > 1)
        if self._pageNumber > 1:
            self.setStrokeColor(colors.HexColor("#CBD5E1"))
            self.setLineWidth(0.75)
            self.line(30, h - 28, w - 30, h - 28)
            
            font_to_use = getattr(PDFExporter, "_font_regular", "Helvetica")
            self.setFont(font_to_use, 8)
            self.setFillColor(colors.HexColor("#64748B"))
            header_text = getattr(PDFExporter, "_current_header_title", "API 5L 47. Baskı & BOTAŞ Şartnamesi — Kalite Güvence ve Kabul Matrisi")
            self.drawString(30, h - 24, header_text)
            self.drawRightString(w - 30, h - 24, "Boru Kalite Güvence Matrisi")

        # Footer rule & metadata
        self.setStrokeColor(colors.HexColor("#E2E8F0"))
        self.setLineWidth(0.75)
        self.line(30, 28, w - 30, 28)

        font_to_use = getattr(PDFExporter, "_font_regular", "Helvetica")
        self.setFont(font_to_use, 8)
        self.setFillColor(colors.HexColor("#64748B"))
        now_str = datetime.datetime.now().strftime("%d.%m.%Y %H:%M")
        self.drawString(30, 16, f"Rapor Üretim Tarihi: {now_str} | Sistem: API 5L QA/QC Expert System v{__version__}")
        
        page_text = f"Sayfa {self._pageNumber} / {page_count}"
        self.drawRightString(w - 30, 16, page_text)
        
        self.restoreState()


class PDFExporter:
    """
    Renders styled, executive-grade PDF reports for ITP audits.
    """

    _font_initialized = False
    _font_regular = "Helvetica"
    _font_bold = "Helvetica-Bold"

    @classmethod
    def _init_fonts(cls):
        if cls._font_initialized:
            return

        font_paths = [
            # macOS paths
            ("/System/Library/Fonts/Supplemental/Arial.ttf", "/System/Library/Fonts/Supplemental/Arial Bold.ttf"),
            ("/Library/Fonts/Arial.ttf", "/Library/Fonts/Arial Bold.ttf"),
            ("/System/Library/Fonts/Supplemental/Tahoma.ttf", "/System/Library/Fonts/Supplemental/Tahoma Bold.ttf"),
            # Linux paths
            ("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"),
            ("/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf", "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf"),
            # Windows paths
            ("C:\\Windows\\Fonts\\arial.ttf", "C:\\Windows\\Fonts\\arialbd.ttf")
        ]

        for reg_path, bold_path in font_paths:
            if os.path.exists(reg_path):
                try:
                    pdfmetrics.registerFont(TTFont("ReportFont", reg_path))
                    cls._font_regular = "ReportFont"
                    if os.path.exists(bold_path):
                        pdfmetrics.registerFont(TTFont("ReportFont-Bold", bold_path))
                        cls._font_bold = "ReportFont-Bold"
                    else:
                        cls._font_bold = "ReportFont"
                    cls._font_initialized = True
                    return
                except Exception:
                    pass

        cls._font_regular = "Helvetica"
        cls._font_bold = "Helvetica-Bold"
        cls._font_initialized = True

    @classmethod
    def export_itp_audit_pdf(cls, audit_data: Dict[str, Any], lang: str = "tr") -> io.BytesIO:
        """
        Builds and returns a PDF stream for an ITP audit report.
        """
        cls._init_fonts()
        buf = io.BytesIO()

        doc = SimpleDocTemplate(
            buf,
            pagesize=landscape(A4),
            leftMargin=30,
            rightMargin=30,
            topMargin=35,
            bottomMargin=35
        )

        styles = getSampleStyleSheet()
        f_reg = cls._font_regular
        f_bold = cls._font_bold

        title_style = ParagraphStyle(
            "DocTitle",
            parent=styles["Heading1"],
            fontName=f_bold,
            fontSize=15,
            leading=18,
            textColor=colors.HexColor("#0F172A")
        )
        section_title_style = ParagraphStyle(
            "SectionTitle",
            parent=styles["Heading2"],
            fontName=f_bold,
            fontSize=11,
            leading=14,
            textColor=colors.HexColor("#1E293B"),
            spaceAfter=4
        )
        body_style = ParagraphStyle(
            "ReportBody",
            parent=styles["Normal"],
            fontName=f_reg,
            fontSize=8,
            leading=10,
            textColor=colors.HexColor("#1E293B")
        )
        th_style = ParagraphStyle(
            "TableHeader",
            parent=styles["Normal"],
            fontName=f_bold,
            fontSize=7.5,
            leading=9,
            textColor=colors.white,
            alignment=0
        )
        cell_style = ParagraphStyle(
            "TableCell",
            parent=styles["Normal"],
            fontName=f_reg,
            fontSize=7,
            leading=8.5,
            textColor=colors.HexColor("#1E293B")
        )
        cell_bold = ParagraphStyle(
            "TableCellBold",
            parent=styles["Normal"],
            fontName=f_bold,
            fontSize=7,
            leading=8.5,
            textColor=colors.HexColor("#0F172A")
        )
        cell_calc = ParagraphStyle(
            "TableCellCalc",
            parent=styles["Normal"],
            fontName=f_bold,
            fontSize=7,
            leading=8.5,
            textColor=colors.HexColor("#312E81")
        )

        elements = []

        pipe = audit_data.get("pipe_summary", {})
        kpi = audit_data.get("kpi", {})
        rows = audit_data.get("audit_rows", [])
        findings = audit_data.get("findings", [])

        d_inch = pipe.get("diameter_inch", "48\"")
        d_mm = pipe.get("diameter_mm", 1219.0)
        t_mm = pipe.get("wall_thickness_mm", 14.30)
        grade = pipe.get("material_grade", "X65")
        process = pipe.get("manufacturing_process", "SAWH")
        psl = pipe.get("psl_level", "PSL2")

        # --- 1. Header Banner ---
        std_ed_name = str(pipe.get("standard_edition") or "API Spec 5L 47. Baskı & BOTAŞ Şartnamesi")
        banner_table_data = [
            [
                Paragraph(f"<b>{std_ed_name.upper()}</b><br/><font size=7 color='#64748B'>BORU İMALAT VE DIŞ KAPLAMA KALİTE GÜVENCE SİSTEMİ</font>", body_style),
                Paragraph("<font size=12><b>ITP UYGUNLUK VE SAPMA DENETİM RAPORU</b></font><br/><font size=7 color='#64748B'>Inspection & Test Plan (ITP) Compliance & Gap Audit Certificate</font>", ParagraphStyle("RAlign", parent=title_style, alignment=2, fontSize=12, leading=15)),
            ]
        ]
        t_banner = Table(banner_table_data, colWidths=[350, 430])
        t_banner.setStyle(TableStyle([
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
            ("TOPPADDING", (0, 0), (-1, -1), 0),
            ("LEFTPADDING", (0, 0), (-1, -1), 0),
            ("RIGHTPADDING", (0, 0), (-1, -1), 0),
        ]))
        elements.append(t_banner)
        elements.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor("#3B82F6"), spaceBefore=3, spaceAfter=8))

        # --- 2. Project, Specification & KPI Dashboard Grid ---
        score_val = kpi.get("compliance_score_percent", 100.0)
        bare_s = kpi.get("bare_pipe_score_percent")
        coat_s = kpi.get("coating_score_percent")
        verdict = kpi.get("overall_verdict", "APPROVED")
        is_pass = verdict == "APPROVED"
        verdict_text = "ONAYLANDI (APPROVED)" if is_pass else "RED / REVİZYON GEREKLİ (REJECTED)"
        verdict_color = colors.HexColor("#065F46") if is_pass else colors.HexColor("#991B1B")
        verdict_bg = colors.HexColor("#D1FAE5") if is_pass else colors.HexColor("#FEE2E2")

        cust_str = str(audit_data.get("customer") or "BOTAŞ")
        proj_str = str(audit_data.get("project_name") or "Doğalgaz Boru Hattı Projesi")
        src_file = str(audit_data.get("source_filename") or "İmalatçı ITP Dokümanı")

        scores_summary_html = f"<font color='#1E40AF'><b>Genel: %{score_val:.1f}</b></font>"
        if bare_s is not None:
            scores_summary_html += f" | <font color='#065F46'><b>Çıplak Boru: %{bare_s:.1f}</b></font>"
        if coat_s is not None:
            scores_summary_html += f" | <font color='#7C3AED'><b>3LPE Kaplama: %{coat_s:.1f}</b></font>"

        spec_box_data = [
            [
                Paragraph(f"<b>Proje / Müşteri:</b> {cust_str} — {proj_str}", body_style),
                Paragraph(f"<b>Denetim Standardı:</b> <font color='#1D4ED8'><b>{std_ed_name}</b></font>", body_style),
            ],
            [
                Paragraph(f"<b>Boru Ebat & Malzeme:</b> <b>{d_inch} ({d_mm} mm) x {t_mm} mm</b> | <b>{grade} {psl} {process}</b>", body_style),
                Paragraph(f"<b>Disiplin Puanları:</b> {scores_summary_html}", body_style),
            ],
            [
                Paragraph(f"<b>Kaynak ITP Dokümanı:</b> {src_file} ({len(rows)} Test Kalemi)", body_style),
                Paragraph(f"<b>Rapor Tarihi / No:</b> {datetime.datetime.now().strftime('%d.%m.%Y %H:%M')} | REF-ITP-{int(d_mm)}-{grade}", body_style),
            ]
        ]
        t_spec = Table(spec_box_data, colWidths=[390, 390])
        t_spec.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#F8FAFC")),
            ("BOX", (0, 0), (-1, -1), 0.75, colors.HexColor("#CBD5E1")),
            ("INNERGRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#E2E8F0")),
            ("TOPPADDING", (0, 0), (-1, -1), 4),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
            ("LEFTPADDING", (0, 0), (-1, -1), 8),
            ("RIGHTPADDING", (0, 0), (-1, -1), 8),
        ]))
        elements.append(t_spec)
        elements.append(Spacer(1, 6))

        # KPI Summary Bar
        kpi_bar_data = [
            [
                Paragraph(f"<b>GENEL DENETİM KARARI</b><br/><font size=10 color='{verdict_color.hexval()}'><b>{verdict_text}</b></font>", ParagraphStyle("K1", parent=body_style, alignment=1)),
                Paragraph(f"<b>UYUMLULUK PUANI</b><br/><font size=11 color='#1E40AF'><b>%{score_val:.1f}</b></font>", ParagraphStyle("K2", parent=body_style, alignment=1)),
                Paragraph(f"<b>TOPLAM MADDE</b><br/><font size=11 color='#0F172A'><b>{kpi.get('total_tests_audited', len(rows))}</b></font>", ParagraphStyle("K3", parent=body_style, alignment=1)),
                Paragraph(f"<b>UYUMLU TESTLER (🟢)</b><br/><font size=11 color='#065F46'><b>{kpi.get('compliant_count', 0)}</b></font>", ParagraphStyle("K4", parent=body_style, alignment=1)),
                Paragraph(f"<b>DAHA SIKI ŞARTLAR (🟡)</b><br/><font size=11 color='#92400E'><b>{kpi.get('more_stringent_count', 0)}</b></font>", ParagraphStyle("K5", parent=body_style, alignment=1)),
                Paragraph(f"<b>HATA & SAPMA (🔴)</b><br/><font size=11 color='#991B1B'><b>{kpi.get('non_compliant_count', 0)}</b></font>", ParagraphStyle("K6", parent=body_style, alignment=1)),
            ]
        ]
        t_kpi = Table(kpi_bar_data, colWidths=[160, 110, 110, 130, 140, 130])
        t_kpi.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#F1F5F9")),
            ("BACKGROUND", (0, 0), (0, 0), verdict_bg),
            ("BOX", (0, 0), (-1, -1), 1, colors.HexColor("#94A3B8")),
            ("INNERGRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E1")),
            ("TOPPADDING", (0, 0), (-1, -1), 4),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ]))
        elements.append(t_kpi)
        elements.append(Spacer(1, 8))

        # --- 3. Discrepancies & Findings Box (If any) ---
        if findings:
            elements.append(Paragraph(f"<b>Kritik Uygunsuzluklar ve Revizyon Gerektiren Maddeler ({len(findings)} Adet Bulgu)</b>", section_title_style))
            find_rows = [
                [
                    Paragraph("<b>#</b>", th_style),
                    Paragraph("<b>İlgili Muayene / Test</b>", th_style),
                    Paragraph("<b>Önem</b>", th_style),
                    Paragraph("<b>Uygunsuzluk & Sapma Açıklaması</b>", th_style),
                    Paragraph("<b>Standart / Madde</b>", th_style),
                ]
            ]
            for idx, f in enumerate(findings):
                sev_color = colors.HexColor("#991B1B") if f.get("severity") == "CRITICAL" else colors.HexColor("#B45309")
                find_rows.append([
                    Paragraph(str(idx + 1), cell_bold),
                    Paragraph(f.get("test_name", "—"), cell_bold),
                    Paragraph(f"<font color='{sev_color.hexval()}'><b>{f.get('severity', 'CRITICAL')}</b></font>", cell_style),
                    Paragraph(f.get("message", "—"), cell_style),
                    Paragraph(f.get("clause_ref", "API 5L / BOTAŞ"), cell_style),
                ])
            t_find = Table(find_rows, colWidths=[20, 160, 60, 420, 120])
            t_find.setStyle(TableStyle([
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#991B1B")),
                ("BACKGROUND", (0, 1), (-1, -1), colors.HexColor("#FFF1F2")),
                ("BOX", (0, 0), (-1, -1), 1, colors.HexColor("#FCA5A5")),
                ("INNERGRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#FECDD3")),
                ("TOPPADDING", (0, 0), (-1, -1), 3),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
                ("LEFTPADDING", (0, 0), (-1, -1), 4),
                ("RIGHTPADDING", (0, 0), (-1, -1), 4),
            ]))
            elements.append(t_find)
            elements.append(Spacer(1, 8))

        # --- 4. Complete Side-by-Side Audit Matrix Table ---
        elements.append(Paragraph("<b>Uçtan Uca Yan Yana ITP Karşılaştırma & Standart Denetim Matrisi</b>", section_title_style))

        matrix_headers = [
            Paragraph("<b>#</b>", th_style),
            Paragraph("<b>Muayene & Test Adı</b>", th_style),
            Paragraph("<b>Boru Sütunu Hedef Değer</b>", th_style),
            Paragraph("<b>İmalatçı Frekansı</b>", th_style),
            Paragraph("<b>Standart Frekansı</b>", th_style),
            Paragraph("<b>İmalatçı Kriteri</b>", th_style),
            Paragraph("<b>Standart Kriteri</b>", th_style),
            Paragraph("<b>Durum</b>", th_style),
            Paragraph("<b>Denetim Notu</b>", th_style),
        ]

        matrix_data = [matrix_headers]

        # Total usable width = 780 pt
        col_widths = [20, 100, 130, 75, 75, 110, 115, 55, 100]

        for idx, r in enumerate(rows):
            status = r.get("status", "COMPLIANT")
            if status == "COMPLIANT":
                st_html = "<font color='#065F46'><b>🟢 UYUMLU</b></font>"
            elif status == "MORE_STRINGENT":
                st_html = "<font color='#92400E'><b>🟡 DAHA SIKI</b></font>"
            else:
                st_html = "<font color='#991B1B'><b>🔴 SAPMA</b></font>"

            rem_text = r.get("audit_remarks", "")
            if not rem_text:
                rem_text = "🟢 Standart şartlarına uygundur." if status in ("COMPLIANT", "MORE_STRINGENT") else "🔴 Standart şartlarını sağlamıyor."

            matrix_data.append([
                Paragraph(str(idx + 1), cell_style),
                Paragraph(f"<b>{r.get('test_name', '—')}</b>", cell_bold),
                Paragraph(r.get("calculated_target_str", "—"), cell_calc),
                Paragraph(r.get("uploaded_frequency", "—"), cell_style),
                Paragraph(r.get("standard_frequency", "—"), cell_style),
                Paragraph(r.get("uploaded_criteria", "—"), cell_style),
                Paragraph(r.get("standard_acceptance_criteria", "—"), cell_style),
                Paragraph(st_html, cell_style),
                Paragraph(rem_text, cell_style),
            ])

        t_matrix = Table(matrix_data, colWidths=col_widths, repeatRows=1)
        
        t_matrix_style = [
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#0F172A")),
            ("BOX", (0, 0), (-1, -1), 1, colors.HexColor("#94A3B8")),
            ("INNERGRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E1")),
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("TOPPADDING", (0, 0), (-1, -1), 3),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
            ("LEFTPADDING", (0, 0), (-1, -1), 3),
            ("RIGHTPADDING", (0, 0), (-1, -1), 3),
        ]

        for r_i in range(1, len(matrix_data)):
            if r_i % 2 == 0:
                t_matrix_style.append(("BACKGROUND", (0, r_i), (-1, r_i), colors.HexColor("#F8FAFC")))

        t_matrix.setStyle(TableStyle(t_matrix_style))
        elements.append(t_matrix)
        elements.append(Spacer(1, 10))

        # --- 5. Sign-Off & Approvals Block ---
        sign_data = [
            [
                Paragraph("<b>HAZIRLAYAN (İmalatçı Kalite Kontrol)</b><br/><br/><br/>İsim: ....................................................<br/>İmza / Tarih:", body_style),
                Paragraph("<b>KONTROL EDEN (Boru QA/QC Şefi)</b><br/><br/><br/>İsim: ....................................................<br/>İmza / Tarih:", body_style),
                Paragraph("<b>ONAYLAYAN (BOTAŞ / Müşteri / TPI Temsilcisi)</b><br/><br/><br/>İsim: ....................................................<br/>İmza / Tarih:", body_style),
            ]
        ]
        t_sign = Table(sign_data, colWidths=[260, 260, 260])
        t_sign.setStyle(TableStyle([
            ("BOX", (0, 0), (-1, -1), 0.75, colors.HexColor("#94A3B8")),
            ("INNERGRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E1")),
            ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#F8FAFC")),
            ("TOPPADDING", (0, 0), (-1, -1), 6),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
            ("LEFTPADDING", (0, 0), (-1, -1), 8),
            ("RIGHTPADDING", (0, 0), (-1, -1), 8),
        ]))
        elements.append(KeepTogether([t_sign]))

        doc.build(elements, canvasmaker=NumberedCanvas)
        buf.seek(0)
        return buf

    @classmethod
    def export_matrix_pdf(
        cls,
        project_info: Dict[str, Any],
        pipes_data: List[Dict[str, Any]],
        lang: str = "tr"
    ) -> io.BytesIO:
        """
        Builds and returns a publication-grade, landscape A4 PDF report for
        the multi-pipe Quality Assurance, Mill Acceptance & Dimensional Tolerances Matrix.
        """
        cls._init_fonts()
        cls._current_header_title = (
            "API Spec 5L (47. Baskı) & BOTAŞ — Kalite Güvence ve Kabul Matrisi"
            if lang == "tr" else "API Spec 5L (47th Ed.) & BOTAŞ — QA/QC Acceptance Matrix"
        )

        buf = io.BytesIO()
        doc = SimpleDocTemplate(
            buf,
            pagesize=landscape(A4),
            leftMargin=30,
            rightMargin=30,
            topMargin=32,
            bottomMargin=32
        )

        styles = getSampleStyleSheet()
        f_reg = cls._font_regular
        f_bold = cls._font_bold

        title_style = ParagraphStyle(
            "MatrixTitle",
            parent=styles["Heading1"],
            fontName=f_bold,
            fontSize=12,
            leading=15,
            textColor=colors.HexColor("#0F172A")
        )
        subtitle_style = ParagraphStyle(
            "MatrixSubtitle",
            parent=styles["Normal"],
            fontName=f_reg,
            fontSize=7,
            leading=9,
            textColor=colors.HexColor("#64748B")
        )
        meta_label_style = ParagraphStyle(
            "MetaLabel",
            parent=styles["Normal"],
            fontName=f_bold,
            fontSize=7,
            leading=8.5,
            textColor=colors.HexColor("#334155")
        )
        meta_val_style = ParagraphStyle(
            "MetaVal",
            parent=styles["Normal"],
            fontName=f_reg,
            fontSize=7,
            leading=8.5,
            textColor=colors.HexColor("#0F172A")
        )

        th_style = ParagraphStyle(
            "MTableHeader",
            parent=styles["Normal"],
            fontName=f_bold,
            fontSize=7,
            leading=8.5,
            textColor=colors.white,
            alignment=1
        )
        th_left_style = ParagraphStyle(
            "MTableHeaderLeft",
            parent=styles["Normal"],
            fontName=f_bold,
            fontSize=7,
            leading=8.5,
            textColor=colors.white,
            alignment=0
        )
        sec_header_style = ParagraphStyle(
            "MSecHeader",
            parent=styles["Normal"],
            fontName=f_bold,
            fontSize=7.2,
            leading=8.5,
            textColor=colors.HexColor("#0F172A")
        )
        cell_param = ParagraphStyle(
            "MCellParam",
            parent=styles["Normal"],
            fontName=f_bold,
            fontSize=6.5,
            leading=7.8,
            textColor=colors.HexColor("#0F172A")
        )
        cell_unit = ParagraphStyle(
            "MCellUnit",
            parent=styles["Normal"],
            fontName=f_reg,
            fontSize=6.2,
            leading=7.5,
            textColor=colors.HexColor("#64748B"),
            alignment=1
        )
        cell_val = ParagraphStyle(
            "MCellVal",
            parent=styles["Normal"],
            fontName=f_bold,
            fontSize=6.5,
            leading=7.8,
            textColor=colors.HexColor("#1E3A8A"),
            alignment=1
        )
        cell_crit = ParagraphStyle(
            "MCellCrit",
            parent=styles["Normal"],
            fontName=f_reg,
            fontSize=6.2,
            leading=7.5,
            textColor=colors.HexColor("#334155")
        )
        body_style = ParagraphStyle(
            "MBodyStyle",
            parent=styles["Normal"],
            fontName=f_reg,
            fontSize=7,
            leading=8.5,
            textColor=colors.HexColor("#1E293B")
        )

        elements = []

        # 1. Header Banner
        p_name = str(project_info.get("project_name") or "Doğal Gaz Boru Hattı Projesi")
        p_no = str(project_info.get("project_no") or "PRJ-2026")
        p_rev = str(project_info.get("revision") or "Rev. 0")
        p_std = str(project_info.get("standard") or "BOTAŞ / API Spec 5L")
        today_str = datetime.datetime.now().strftime("%d.%m.%Y")

        banner_left = [
            Paragraph(
                "<b>API SPEC 5L (47. BASKI) &amp; BOTAŞ BORU KALİTE GÜVENCE MATRİSİ</b>" if lang == "tr"
                else "<b>API SPEC 5L (47th ED.) &amp; BOTAŞ PIPE QA/QC ACCEPTANCE MATRIX</b>",
                title_style
            ),
            Spacer(1, 2),
            Paragraph(
                "Fabrika Ön Kabul, Boyutsal Toleranslar ve Malzeme Doğrulama Denetim Belgesi" if lang == "tr"
                else "Mill Pre-Acceptance, Dimensional Tolerances &amp; Material Verification Certificate",
                subtitle_style
            )
        ]

        meta_table_data = [
            [Paragraph("<b>Proje:</b>", meta_label_style), Paragraph(p_name, meta_val_style), Paragraph("<b>Tarih:</b>", meta_label_style), Paragraph(today_str, meta_val_style)],
            [Paragraph("<b>Proje No:</b>", meta_label_style), Paragraph(p_no, meta_val_style), Paragraph("<b>Rev:</b>", meta_label_style), Paragraph(p_rev, meta_val_style)],
            [Paragraph("<b>Standart:</b>", meta_label_style), Paragraph(p_std, meta_val_style), Paragraph("<b>Durum:</b>", meta_label_style), Paragraph("<font color='#059669'><b>DENETİME HAZIR</b></font>", meta_val_style)]
        ]
        meta_table = Table(meta_table_data, colWidths=[50, 140, 38, 74])
        meta_table.setStyle(TableStyle([
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("TOPPADDING", (0, 0), (-1, -1), 1),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 1),
            ("LEFTPADDING", (0, 0), (-1, -1), 2),
            ("RIGHTPADDING", (0, 0), (-1, -1), 2),
            ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#F8FAFC")),
            ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E1")),
            ("INNERGRID", (0, 0), (-1, -1), 0.25, colors.HexColor("#E2E8F0")),
        ]))

        banner_table = Table([[banner_left, meta_table]], colWidths=[470, 312])
        banner_table.setStyle(TableStyle([
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("TOPPADDING", (0, 0), (-1, -1), 0),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
            ("LEFTPADDING", (0, 0), (-1, -1), 0),
            ("RIGHTPADDING", (0, 0), (-1, -1), 0),
        ]))
        elements.append(banner_table)
        elements.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor("#2563EB"), spaceBefore=3, spaceAfter=5))

        # 2. Multi-Pipe Matrix Table Calculation & Columns
        total_w = 782.0
        num_p = max(1, len(pipes_data))
        param_w = 175.0
        unit_w = 48.0
        col_rem_w = max(160.0, 782.0 - param_w - unit_w - (num_p * 85.0))
        pipe_w = (782.0 - param_w - unit_w - col_rem_w) / num_p
        col_widths = [param_w, unit_w] + [pipe_w] * num_p + [col_rem_w]

        # Header Row
        header_row = [
            Paragraph("<b>PARAMETRE / KONTROL ÖĞESİ</b>", th_left_style),
            Paragraph("<b>BİRİM</b>", th_style)
        ]
        for idx, p in enumerate(pipes_data):
            s = p.get("input_summary", {})
            d_in = s.get("diameter_inch", "—")
            t_val = s.get("wall_thickness_mm", 0.0)
            grd = s.get("material_grade", "—")
            fac = s.get("design_factor_str", "—")
            header_row.append(
                Paragraph(
                    f"<b>BORU #{idx+1}</b><br/><font size=5.5 color='#93C5FD'>{d_in} {grd}<br/>t={t_val:.2f}mm ({fac})</font>",
                    th_style
                )
            )
        header_row.append(Paragraph("<b>STANDART ŞARTNAME &amp; KABUL KRİTERİ</b>", th_left_style))

        matrix_rows = [header_row]
        table_style_commands = [
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#0F172A")),
            ("BOX", (0, 0), (-1, -1), 0.75, colors.HexColor("#94A3B8")),
            ("INNERGRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#E2E8F0")),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("TOPPADDING", (0, 0), (-1, -1), 2),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 2),
            ("LEFTPADDING", (0, 0), (-1, -1), 3),
            ("RIGHTPADDING", (0, 0), (-1, -1), 3),
        ]

        def add_section(sec_title):
            row_idx = len(matrix_rows)
            sec_row = [Paragraph(f"<b>{sec_title}</b>", sec_header_style)] + [""] * (num_p + 2)
            matrix_rows.append(sec_row)
            table_style_commands.extend([
                ("SPAN", (0, row_idx), (-1, row_idx)),
                ("BACKGROUND", (0, row_idx), (-1, row_idx), colors.HexColor("#E2E8F0")),
                ("TOPPADDING", (0, row_idx), (-1, row_idx), 3),
                ("BOTTOMPADDING", (0, row_idx), (-1, row_idx), 3),
            ])

        def _fmt_val(v, dec=2, prefix="", suffix=""):
            if v is None or v == "" or v == "—":
                return "—"
            try:
                val = float(v)
                return f"{prefix}{val:.{dec}f}{suffix}"
            except (ValueError, TypeError):
                return f"{prefix}{v}{suffix}"

        def _fmt_range(v_min, v_max, dec=2, unit=""):
            u_str = f" {unit}" if unit else ""
            s_min = _fmt_val(v_min, dec)
            s_max = _fmt_val(v_max, dec)
            if s_min == "—" and s_max == "—":
                return "—"
            if s_min == s_max:
                return f"{s_min}{u_str}"
            return f"[{s_min} — {s_max}]{u_str}"

        def add_param(name, unit, val_fn, crit_text):
            row_idx = len(matrix_rows)
            row = [
                Paragraph(name, cell_param),
                Paragraph(unit, cell_unit)
            ]
            for p in pipes_data:
                v_str = str(val_fn(p))
                row.append(Paragraph(v_str, cell_val))
            row.append(Paragraph(crit_text, cell_crit))
            matrix_rows.append(row)
            if row_idx % 2 == 1:
                table_style_commands.append(("BACKGROUND", (0, row_idx), (-1, row_idx), colors.HexColor("#F8FAFC")))

        # --- Section 1: GENEL BORU ÖZELLİKLERİ ---
        add_section("1. GENEL BORU ÖZELLİKLERİ VE TASARIM VERİLERİ (GENERAL SPECIFICATIONS)")
        add_param("Boru Anma Dış Çapı (OD)", "in (mm)", lambda p: f"{p.get('input_summary', {}).get('diameter_inch', '—')} ({_fmt_val(p.get('input_summary', {}).get('diameter_mm'), 1, suffix=' mm')})", "API 5L Madde 9.11.1 / BOTAŞ Çizelge 1")
        add_param("Nominal Et Kalınlığı (t)", "mm", lambda p: _fmt_val(p.get('input_summary', {}).get('wall_thickness_mm'), 2, suffix=" mm"), "API 5L Madde 9.11.2 / BOTAŞ Çizelge 1")
        add_param("Malzeme Çelik Kalitesi", "—", lambda p: str(p.get('input_summary', {}).get('material_grade', '—')), "API 5L Tablo 1 / BOTAŞ 3.1 Kimyasal Grup")
        add_param("İmalat Yöntemi / Proses", "—", lambda p: str(p.get('input_summary', {}).get('manufacturing_process', '—')), "API 5L Tablo 2 / BOTAŞ 3.2 İmalat Prosesi")
        add_param("Tasarım Faktörü (F)", "—", lambda p: str(p.get('input_summary', {}).get('design_factor_str', '—')), "ASME B31.8 Madde 841.1.1 Emniyet Faktörü")
        add_param("Tasarım Basıncı (P_des)", "bar", lambda p: _fmt_val(p.get('input_summary', {}).get('design_pressure_bar', 75.0), 1, suffix=" bar"), "Barlow Formülü / BOTAŞ İşletme Basıncı")
        add_param("Minimum Akma Dayanımı (SMYS)", "MPa", lambda p: f"{_fmt_val(p.get('mechanical_properties', {}).get('yield_min_mpa', 450), 0, suffix=' MPa')} ({_fmt_val(p.get('mechanical_properties', {}).get('smys_psi', 65300), 0, suffix=' psi')})", "API 5L Tablo 7 Belirtilen Minimum Akma")

        # --- Section 2: BOYUTSAL TOLERANSLAR ---
        add_section("2. BOYUTSAL TOLERANSLAR (DIMENSIONAL TOLERANCES — API 5L TABLO 9-14 & BOTAŞ 8.1.2)")
        add_param("Et Kalınlığı Kabul Bandı (t)", "mm", lambda p: _fmt_range(p.get('wall_thickness_tolerance', {}).get('min_mm'), p.get('wall_thickness_tolerance', {}).get('max_mm'), 2, "mm"), "API 5L Tablo 11 (BOTAŞ -%8/+%10 veya -%10/+%10)")
        add_param("Gövde Dış Çap Toleransı (OD_body)", "mm", lambda p: _fmt_range(p.get('dimensional_tolerances', {}).get('diameter_body_min_mm'), p.get('dimensional_tolerances', {}).get('diameter_body_max_mm'), 2, "mm"), "API 5L Tablo 10 (±%0.5 D / maks ±4.0 mm)")
        add_param("Boru Ucu Dış Çap Toleransı (OD_end)", "mm", lambda p: _fmt_range(p.get('dimensional_tolerances', {}).get('diameter_end_min_mm'), p.get('dimensional_tolerances', {}).get('diameter_end_max_mm'), 2, "mm"), "API 5L Tablo 10 (±1.6 mm / BOTAŞ ±1.0 mm)")
        add_param("Boru Gövdesi Ovallik Sınırı", "mm", lambda p: _fmt_val(p.get('dimensional_tolerances', {}).get('ovality_body_mm'), 2, prefix="≤ ", suffix=" mm"), "API 5L Tablo 10 (D_max - D_min ≤ %1.0 D)")
        add_param("Boru Ucu Ovallik Sınırı", "mm", lambda p: _fmt_val(p.get('dimensional_tolerances', {}).get('ovality_end_mm'), 2, prefix="≤ ", suffix=" mm"), "API 5L Tablo 10 (≤%1.0 D maks 10.0 mm / BOTAŞ 0.6% D)")
        add_param("Toplam Boy Düzlük Sapması", "mm", lambda p: "≤ 24.0 mm", "API 5L Tablo 12 (Chord ≤ %0.2 L, maks 24 mm)")
        add_param("Boru Ucu Düzlük Sapması (1.0 m)", "mm", lambda p: "≤ 3.0 mm" if "BOTAŞ" in str(p.get('input_summary', {}).get('standard_type', '')) else "≤ 4.0 mm", "API 5L Tablo 12 (≤ 4.0 mm / BOTAŞ Madde 8.1.2 ≤ 3.0 mm)")
        add_param("İç Kaynak Dikiş Fazlalığı", "mm", lambda p: _fmt_val(p.get('weld_and_geometry', {}).get('weld_height_inside_mm', 3.5), 2, prefix="≤ ", suffix=" mm"), "API 5L Tablo 13 (Tozaltı SAW iç kaynak yüksekliği)")
        add_param("Dış Kaynak Dikiş Fazlalığı", "mm", lambda p: _fmt_val(p.get('weld_and_geometry', {}).get('weld_height_outside_mm', 3.5), 2, prefix="≤ ", suffix=" mm"), "API 5L Tablo 13 (Tozaltı SAW dış kaynak yüksekliği)")
        add_param("Radyal Basamaklanma (Radial Offset)", "mm", lambda p: _fmt_val(p.get('weld_and_geometry', {}).get('radial_offset_max_mm', 1.5), 2, prefix="≤ ", suffix=" mm"), "API 5L Tablo 14 (Kenar basamaklanma maks 1.5 mm)")

        # --- Section 3: KİMYASAL BİLEŞİM & KARBON EŞDEĞERİ ---
        add_section("3. KİMYASAL BİLEŞİM & KARBON EŞDEĞERİ (API 5L TABLO 5 & BOTAŞ ÇİZELGE 2)")
        add_param("Karbon (C) Maksimum", "%", lambda p: _fmt_val(p.get('chemical_analysis', {}).get('C_max', 0.12), 2, prefix="≤ %"), "API 5L Tablo 5 / BOTAŞ Çizelge 2")
        add_param("Mangan (Mn) Maksimum", "%", lambda p: _fmt_val(p.get('chemical_analysis', {}).get('Mn_max', 1.60), 2, prefix="≤ %"), "API 5L Tablo 5 / BOTAŞ Çizelge 2")
        add_param("Fosfor (P) Maksimum", "%", lambda p: _fmt_val(p.get('chemical_analysis', {}).get('P_max', 0.020), 3, prefix="≤ %"), "API 5L Tablo 5 (maks %0.025 / BOTAŞ maks %0.020)")
        add_param("Kükürt (S) Maksimum", "%", lambda p: _fmt_val(p.get('chemical_analysis', {}).get('S_max', 0.010), 3, prefix="≤ %"), "API 5L Tablo 5 (maks %0.015 / BOTAŞ maks %0.010)")
        add_param("Niyobyum (Nb) Sınırı", "%", lambda p: str(p.get('chemical_analysis', {}).get('Nb_min_max', '—')), "BOTAŞ Çizelge 2 (min %0.015 mikroalaşım)")
        add_param("Karbon Eşdeğeri CE (IIW) Maks", "—", lambda p: _fmt_val(p.get('chemical_analysis', {}).get('CE_IIW_max', 0.43), 2, prefix="≤ "), "IIW Eşitliği: C + Mn/6 + (Cr+Mo+V)/5 + (Ni+Cu)/15")
        add_param("Karbon Eşdeğeri CE (Pcm) Maks", "—", lambda p: _fmt_val(p.get('chemical_analysis', {}).get('CE_Pcm_max', 0.25), 2, prefix="≤ "), "Ito-Bessyo Eşitliği (Düşük C için kaynaklanabilirlik)")

        # --- Section 4: MEKANİK ÖZELLİKLER & DARBE TOKLUĞU ---
        add_section("4. MEKANİK ÖZELLİKLER & DARBE TOKLUĞU (API 5L TABLO 7, 8 & BOTAŞ ÇİZELGE 3)")
        add_param("Akma Dayanımı (Rt0.5)", "MPa", lambda p: _fmt_range(p.get('mechanical_properties', {}).get('yield_min_mpa', 450), p.get('mechanical_properties', {}).get('yield_max_mpa', 600), 0, "MPa"), "API 5L Tablo 7 (PSL2 Akma Kabul Aralığı)")
        add_param("Çekme Dayanımı (Rm)", "MPa", lambda p: _fmt_range(p.get('mechanical_properties', {}).get('tensile_min_mpa', 535), p.get('mechanical_properties', {}).get('tensile_max_mpa', 760), 0, "MPa"), "API 5L Tablo 7 (PSL2 Çekme Kabul Aralığı)")
        add_param("Akma / Çekme Oranı (Rt0.5/Rm)", "—", lambda p: _fmt_val(p.get('mechanical_properties', {}).get('yield_to_tensile_ratio_max', 0.93), 2, prefix="≤ "), "API 5L Tablo 7 (maks 0.93 / BOTAŞ maks 0.90)")
        add_param("Kopma Uzaması (Af)", "%", lambda p: _fmt_val(p.get('toughness_and_tests', {}).get('elongation_mat_min_percent', 18.0), 1, prefix="≥ %"), "API 5L Madde 9.3.2 & Tablo 8 Formülü")
        add_param("Gövde Charpy V-Notch (CVN)", "J", lambda p: _fmt_val(p.get('toughness_and_tests', {}).get('notch_impact_mat_j', 60), 0, prefix="≥ ", suffix=" J"), "API 5L Tablo 8 / BOTAŞ Çizelge 4 (0°C / -20°C)")
        add_param("Kaynak Dikişi Charpy (CVN)", "J", lambda p: _fmt_val(p.get('toughness_and_tests', {}).get('notch_impact_weld_j', 40), 0, prefix="≥ ", suffix=" J"), "API 5L Tablo 8 / BOTAŞ Çizelge 4 (Kaynak ve ITAB)")
        add_param("Kalan Gerilme Halka Açıklığı (Δ)", "mm", lambda p: _fmt_val(p.get('toughness_and_tests', {}).get('residual_stress_max_mm', 1.5), 1, prefix="≤ ", suffix=" mm"), "BOTAŞ Madde 3.3.9 (150 mm halka kesme testi)")

        # --- Section 5: FABRİKA HİDROSTATİK TESTİ & TASARIM GÜVENLİĞİ ---
        add_section("5. FABRİKA HİDROSTATİK TESTİ & ASME B31.8 TASARIM EMNİYETİ")
        add_param("Fabrika Hidrostatik Test Basıncı", "bar", lambda p: _fmt_val(p.get('hydrostatic_test', {}).get('hydro_test_max_bar', 100), 1, suffix=" bar"), "API 5L 10.2.6.7 (Çeper gerilmesi %90 - %95 SMYS)")
        add_param("API 5L Standart Test Basıncı", "bar", lambda p: _fmt_val(p.get('hydrostatic_test', {}).get('api_5l_std_test_bar', 95), 1, suffix=" bar"), "API 5L Madde 10.2.6.7 Standart Test Hesabı")
        add_param("Doğrusal Çelik Kütlesi (Nominal)", "kg/m", lambda p: _fmt_val(p.get('weights_and_safety', {}).get('weight_nominal_kg_m', 425), 1, suffix=" kg/m"), "API 5L 9.11.3 (w = 0.0246615 * (D-t) * t)")
        add_param("Ağırlık Tolerans Aralığı (Tek Boru)", "kg/m", lambda p: _fmt_range(p.get('weights_and_safety', {}).get('weight_min_kg_m', 410), p.get('weights_and_safety', {}).get('weight_max_kg_m', 467), 1, "kg/m"), "API 5L Tablo 11 (-%3.5 / +%10.0)")
        add_param("Çap / Cidar Oranı (D/t)", "—", lambda p: _fmt_val(p.get('weights_and_safety', {}).get('d_over_t', 85), 1), "ASME B31.8 Section 841.1.1 Emniyet Katsayısı")
        add_param("Kırılma Yayılma Kontrol Kriteri", "—", lambda p: str(p.get('weights_and_safety', {}).get('fracture_control_asme_841_1_2', 'Normal Emniyet')), "ASME B31.8 Section 841.1.2 (Annex G Zorunlu / Normal)")

        t_matrix = Table(matrix_rows, colWidths=col_widths, repeatRows=1)
        t_matrix.setStyle(TableStyle(table_style_commands))
        elements.append(t_matrix)
        elements.append(Spacer(1, 8))

        # 3. Engineering Sign-Off Block
        sign_data = [
            [
                Paragraph("<b>HAZIRLAYAN (İmalatçı QA/QC Kontrol Mühendisi)</b><br/><br/><br/>İsim: ................................................................<br/>İmza / Tarih:", body_style),
                Paragraph("<b>İNCELEYEN (Boru QA/QC Şefi / IWE Kaynak Müh.)</b><br/><br/><br/>İsim: ................................................................<br/>İmza / Tarih:", body_style),
                Paragraph("<b>ONAYLAYAN (BOTAŞ / Müşteri / TPI Temsilcisi)</b><br/><br/><br/>İsim: ................................................................<br/>İmza / Tarih:", body_style),
            ]
        ]
        t_sign = Table(sign_data, colWidths=[260, 260, 262])
        t_sign.setStyle(TableStyle([
            ("BOX", (0, 0), (-1, -1), 0.75, colors.HexColor("#94A3B8")),
            ("INNERGRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E1")),
            ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#F8FAFC")),
            ("TOPPADDING", (0, 0), (-1, -1), 5),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
            ("LEFTPADDING", (0, 0), (-1, -1), 6),
            ("RIGHTPADDING", (0, 0), (-1, -1), 6),
        ]))
        elements.append(KeepTogether([t_sign]))

        doc.build(elements, canvasmaker=NumberedCanvas)
        buf.seek(0)
        return buf
