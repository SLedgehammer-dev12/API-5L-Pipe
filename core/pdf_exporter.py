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
from typing import Any, Dict

from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, KeepTogether, HRFlowable
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont


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
            self.drawString(30, h - 24, "API 5L 47. Baskı & BOTAŞ Şartnamesi — ITP Uygunluk ve Sapma Denetim Raporu")
            self.drawRightString(w - 30, h - 24, "Boru Kalite Güvence Matrisi")

        # Footer rule & metadata
        self.setStrokeColor(colors.HexColor("#E2E8F0"))
        self.setLineWidth(0.75)
        self.line(30, 28, w - 30, 28)

        font_to_use = getattr(PDFExporter, "_font_regular", "Helvetica")
        self.setFont(font_to_use, 8)
        self.setFillColor(colors.HexColor("#64748B"))
        now_str = datetime.datetime.now().strftime("%d.%m.%Y %H:%M")
        self.drawString(30, 16, f"Rapor Üretim Tarihi: {now_str} | Sistem: API 5L QA/QC Expert System v2.3.0")
        
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
        std_type = pipe.get("standard_type", "BOTAŞ")
        scope_mode = pipe.get("scope_mode", "COMBINED")

        # --- 1. Header Banner ---
        banner_table_data = [
            [
                Paragraph("<b>API 5L 47. BASKI & BOTAŞ ŞARTNAMESİ</b><br/><font size=7 color='#64748B'>BORU İMALAT VE DIŞ KAPLAMA KALİTE GÜVENCE SİSTEMİ</font>", body_style),
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
        verdict = kpi.get("overall_verdict", "APPROVED")
        is_pass = verdict == "APPROVED"
        verdict_text = "ONAYLANDI (APPROVED)" if is_pass else "RED / REVİZYON GEREKLİ (REJECTED)"
        verdict_color = colors.HexColor("#065F46") if is_pass else colors.HexColor("#991B1B")
        verdict_bg = colors.HexColor("#D1FAE5") if is_pass else colors.HexColor("#FEE2E2")

        cust_str = str(audit_data.get("customer") or "BOTAŞ")
        proj_str = str(audit_data.get("project_name") or "Doğalgaz Boru Hattı Projesi")
        src_file = str(audit_data.get("source_filename") or "İmalatçı ITP Dokümanı")

        spec_box_data = [
            [
                Paragraph(f"<b>Proje / Müşteri:</b> {cust_str} — {proj_str}", body_style),
                Paragraph(f"<b>Denetim Standardı:</b> <font color='#1D4ED8'><b>{std_type} (5120 R7 + 5410 R1) & API 5L 47th</b></font>", body_style),
            ],
            [
                Paragraph(f"<b>Boru Ebat & Malzeme:</b> <b>{d_inch} ({d_mm} mm) x {t_mm} mm</b> | <b>{grade} {psl} {process}</b>", body_style),
                Paragraph(f"<b>Denetim Kapsamı:</b> <b>{scope_mode}</b>", body_style),
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
