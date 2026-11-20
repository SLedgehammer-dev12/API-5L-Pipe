import io
import sys
import time
import unittest
from pathlib import Path
from unittest.mock import patch

import fitz
import openpyxl
from fastapi.testclient import TestClient
from reportlab import rl_config
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

ROOT_DIR = str(Path(__file__).resolve().parent.parent)
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

import app as app_module  # noqa: E402
from app import app  # noqa: E402
from core.excel_exporter import ExcelExporter  # noqa: E402
from core.itp_audit_engine import FrequencyCanonical, FrequencyNormalizer, ITPAuditEngine  # noqa: E402
from core.itp_criteria_parser import ITPCriteriaParser  # noqa: E402
from core.pdf_exporter import PDFExporter  # noqa: E402
from core.pipe_qaqc_engine import PipeQAQCEngine  # noqa: E402
from core.test_plan import get_comprehensive_itp_specification  # noqa: E402
from core.unlimited_ocr_engine import UnlimitedOCREngine  # noqa: E402


def _build_pdf_with_table(title_lines, table_rows) -> bytes:
    PDFExporter._init_fonts()
    font_name = PDFExporter._font_regular
    buf = io.BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=landscape(A4), leftMargin=20, rightMargin=20, topMargin=20, bottomMargin=20)
    style = ParagraphStyle("TestP", fontName=font_name, fontSize=8, leading=10)
    cell_style = ParagraphStyle("CellP", fontName=font_name, fontSize=7, leading=8.5)
    story = [Paragraph(line, style) for line in title_lines]
    if table_rows:
        story.append(Spacer(1, 8))
        wrapped = [[Paragraph(str(c), cell_style) for c in row] for row in table_rows]
        col_w = 780.0 / len(table_rows[0])
        tbl = Table(wrapped, colWidths=[col_w] * len(table_rows[0]))
        tbl.setStyle(TableStyle([
            ("GRID", (0, 0), (-1, -1), 0.5, colors.black),
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ]))
        story.append(tbl)
    doc.build(story)
    return buf.getvalue()


class TestITPPipelineStep1A(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.client = TestClient(app)

    def test_all_caps_turkish_header_pdf_extraction(self):
        pdf_bytes = _build_pdf_with_table(
            [
                "BOTAŞ DOĞAL GAZ BORU HATTI PROJESİ",
                "MUAYENE VE TEST PLANI (ITP) - 48\" X65 SAWH PSL2",
            ],
            [
                ["NO", "PROSES / FAALİYET", "KONTROL PARAMETRESİ", "NUMUNE SIKLIĞI", "ŞARTNAME / KABUL KRİTERLERİ", "İMALATÇI", "TPI", "BOTAŞ"],
                ["1", "Hammadde", "Isı Kimyasal Analizi", "Her dökümde 1 analiz", "C <= 0.12%, P <= 0.020%, S <= 0.010%, CE_IIW <= 0.40", "C", "W", "H"],
                ["2", "Fabrika Testi", "Hidrostatik Basınç Testi", "Her boruda (%100)", "Min 168.0 bar, 20 saniye tutma süresi", "C", "W", "H"],
            ],
        )
        res = UnlimitedOCREngine.parse_pdf_or_image(pdf_bytes, "ALL_CAPS_ITP.pdf")
        self.assertEqual(res["status"], "success")
        self.assertFalse(res["is_fallback"])
        self.assertEqual(len(res["items"]), 2)

        hydro = next(it for it in res["items"] if "Hidrostatik" in it["test_name"])
        self.assertEqual(hydro["reading_confidence"], "HIGH")
        self.assertIn("%100", hydro["test_frequency"])
        self.assertIn("168.0 bar", hydro["acceptance_criteria"])
        self.assertEqual(hydro["inspection_points"], {"mfg": "C", "tpi": "W", "client": "H"})

    def test_unread_cells_never_pass_as_compliant(self):
        cfg = {
            "diameter_mm": 914.4,
            "diameter_inch": '36"',
            "wall_thickness_mm": 11.1,
            "material_grade": "X65",
            "manufacturing_process": "SAWH",
            "standard_type": "BOTAŞ",
            "psl_level": "PSL2",
            "scope_mode": "COATING_ONLY",
        }
        items = [
            {
                "test_name": "Elektrik Porozite (Holiday) Testi",
                "test_frequency": "— (Tablodan Okunamadı)",
                "acceptance_criteria": "— (Tablodan Okunamadı)",
            },
            {
                "test_name": "3LPE Kaplama Kalınlığı",
                "test_frequency": "",
                "acceptance_criteria": "—",
            },
        ]
        audit = ITPAuditEngine.audit_itp(items, cfg)
        self.assertEqual(audit["kpi"]["overall_verdict"], "REJECTED")
        holiday = next(r for r in audit["audit_rows"] if r["test_key"] == "coating_holiday_test")
        thick = next(r for r in audit["audit_rows"] if r["test_key"] == "coating_thickness_3lpe")
        self.assertEqual(holiday["status"], "NON_COMPLIANT")
        self.assertEqual(holiday["issue_type"], "UNREAD_CRITERIA")
        self.assertEqual(thick["status"], "NON_COMPLIANT")
        self.assertEqual(thick["issue_type"], "UNREAD_CRITERIA")

    def test_non_compliant_frequency_not_overwritten_by_high_cvn(self):
        cfg = {
            "diameter_mm": 1219.0,
            "diameter_inch": '48"',
            "wall_thickness_mm": 14.3,
            "material_grade": "X65",
            "manufacturing_process": "SAWH",
            "standard_type": "BOTAŞ",
            "psl_level": "PSL2",
        }
        items = [
            {
                "test_name": "Gövde Çentik Darbe Testi (CVN Body)",
                "test_frequency": "1/200 boru",
                "acceptance_criteria": "Min Ort. 80 J, Min Tekil 60 J (-20 °C)",
            }
        ]
        audit = ITPAuditEngine.audit_itp(items, cfg)
        cvn = next(r for r in audit["audit_rows"] if r["test_key"] == "cvn_body")
        self.assertEqual(cvn["status"], "NON_COMPLIANT")
        self.assertEqual(cvn["issue_type"], "INADEQUATE_SAMPLING_FREQUENCY")

    def test_non_itp_gatekeeper_blocks_audit(self):
        spec_pdf = _build_pdf_with_table(
            ["ÇELİK BORU TEKNİK ŞARTNAMESİ", "Genel Hükümler ve Kapsam"],
            [],
        )
        sched_pdf = _build_pdf_with_table(
            ["DOĞALGAZ BORU HATTI TERMİN PROGRAMI", "Sevkiyat Takvimi"],
            [],
        )

        spec_res = UnlimitedOCREngine.parse_pdf_or_image(spec_pdf, "TEKNİK_ŞARTNAME.pdf")
        self.assertEqual(spec_res["document_type"], "TECHNICAL_SPECIFICATION")
        self.assertEqual(spec_res["items"], [])

        resp = self.client.post(
            "/api/itp/upload-and-audit",
            files={"file": ("TESLIM_PROGRAMI.pdf", sched_pdf, "application/pdf")},
            data={"pipe_config_json": "{}"},
        )
        self.assertEqual(resp.status_code, 200)
        body = resp.json()
        self.assertEqual(body["status"], "warning")
        self.assertEqual(body["document_type"], "DELIVERY_SCHEDULE")
        self.assertEqual(body["extracted_items"], [])
        self.assertEqual(body["audit_result"]["kpi"]["overall_verdict"], "NON_ITP_DOCUMENT")

    def test_metadata_anti_poisoning_delivery_and_variant_inch_sync(self):
        api_text = (
            "API Spec 5L 47th Edition Line Pipe ITP\n"
            "Delivery Condition: N\n"
            "Kapsam: 1 914,4 11,10 PSL2 X65\n"
            "2 914,4 12,70 PSL2 X65\n"
            "Unless otherwise specified, submerged arc helical welded (SAWH) pipes apply."
        )
        unread_items = [
            {
                "test_name": "Hydrostatic Test",
                "test_frequency": "— (Tablodan Okunamadı)",
                "acceptance_criteria": "— (Tablodan Okunamadı)",
            }
        ]
        meta = UnlimitedOCREngine.detect_itp_metadata(api_text, unread_items, "API_5L_SAWH_ITP.pdf")
        self.assertEqual(meta["detected_standard"], "API")
        self.assertEqual(meta["detected_process"], "SAWH")
        self.assertEqual(meta["detected_delivery_condition"], "N")
        self.assertEqual(meta["detected_diameter_mm"], 914.4)
        self.assertEqual(meta["detected_diameter_inch"], '36"')

    def test_upload_and_audit_adopts_detected_config_and_keeps_english_coating_rows(self):
        erw_pdf = _build_pdf_with_table(
            [
                "BOTAŞ MANİSA DOĞALGAZ BORU HATTI PROJESİ - MUAYENE VE TEST PLANI (ITP)",
                "Standart: API 5L / BOTAŞ 4-NGTL-0-GN-P-002-5120 R7",
                "Kapsam: 1 219,1 6,40 PSL2 X42M ERW",
            ],
            [
                ["No", "Faaliyet", "Parametre", "Sıklık", "Kabul Kriteri"],
                ["1", "Test", "Fabrika Hidrostatik Testi", "Her boru (%100)", "Min 145 bar, 20 saniye"],
            ],
        )
        resp_erw = self.client.post(
            "/api/itp/upload-and-audit",
            files={"file": ("BOTAS_8in_X42_ERW_ITP.pdf", erw_pdf, "application/pdf")},
            data={"pipe_config_json": "{}"},
        )
        self.assertEqual(resp_erw.status_code, 200)
        erw_json = resp_erw.json()
        eff = erw_json["effective_config"]
        self.assertEqual(eff["diameter_mm"], 219.1)
        self.assertEqual(eff["wall_thickness_mm"], 6.4)
        self.assertEqual(eff["material_grade"], "X42")
        self.assertEqual(eff["manufacturing_process"], "ERW")
        self.assertEqual(eff["standard_type"], "BOTAŞ")

        coating_pdf = _build_pdf_with_table(
            [
                "EXTERNAL 3LPE COATING INSPECTION AND TEST PLAN (ITP)",
                "Standard: DIN 30670 / ISO 21809-1 | Pipe: 42\" (1066.8 mm) x 14.3 mm X70 LSAW",
            ],
            [
                ["Item", "Inspection Activity", "Frequency", "Acceptance Criteria"],
                ["1", "Abrasive Blast Cleaning", "100% of pipes", "Sa 2.5, Rz 60-100 um"],
                ["2", "3LPE Coating Thickness", "100% of pipes", "Min 3.0 mm total thickness"],
                ["3", "High Voltage Holiday Detection", "100% of surface", "25 kV zero pinholes"],
                ["4", "Cathodic Disbondment", "1 per batch", "Max 7.0 mm radius"],
            ],
        )
        resp_coat = self.client.post(
            "/api/itp/upload-and-audit",
            files={"file": ("42in_3LPE_Coating_Only_ITP.pdf", coating_pdf, "application/pdf")},
            data={"pipe_config_json": "{}"},
        )
        self.assertEqual(resp_coat.status_code, 200)
        coat_json = resp_coat.json()
        self.assertEqual(coat_json["effective_config"]["scope_mode"], "COATING_ONLY")
        extracted_names = [it["test_name"] for it in coat_json["extracted_items"]]
        self.assertEqual(len(extracted_names), 4)
        self.assertIn("Abrasive Blast Cleaning", extracted_names)
        self.assertIn("Cathodic Disbondment", extracted_names)

        bad_cfg = self.client.post(
            "/api/itp/upload-and-audit",
            files={"file": ("test.pdf", erw_pdf, "application/pdf")},
            data={"pipe_config_json": "[]"},
        )
        self.assertEqual(bad_cfg.status_code, 400)

    def test_pdf_export_populates_target_and_standard_criteria_handles_approved_with_comments_and_escapes_xml(self):
        self.assertEqual(rl_config.trustedSchemes, [])
        self.assertEqual(rl_config.trustedHosts, [])

        audit = {
            "customer": 'ACME <script> & "Partner" <img src="/etc/passwd"/>',
            "project_name": "Pipeline <Phase 1 & 2>",
            "source_filename": "Vendor_ITP_&_Notes.pdf",
            "pipe_summary": {
                "diameter_mm": 1219.0,
                "diameter_inch": '48"',
                "wall_thickness_mm": 14.3,
                "material_grade": "X65",
                "manufacturing_process": "SAWH",
                "psl_level": "PSL2",
                "standard_edition": "API Spec 5L 47. Baskı & BOTAŞ",
            },
            "kpi": {
                "total_tests_audited": 1,
                "compliant_count": 0,
                "more_stringent_count": 1,
                "non_compliant_count": 0,
                "compliance_score_percent": 100.0,
                "bare_pipe_score_percent": 100.0,
                "coating_score_percent": None,
                "overall_verdict": "APPROVED_WITH_COMMENTS",
            },
            "findings": [
                {
                    "test_name": "CVN <Impact> & Check",
                    "severity": "INFO",
                    "message": "Energy >= 80 J & temp < -20 C <img src='http://169.254.169.254/'>",
                    "clause_ref": "BOTAŞ <3.3.5>",
                }
            ],
            "audit_rows": [
                {
                    "test_name": "Gövde Çentik Darbe & CVN",
                    "calculated_target": "TARGET_MIN_60J_AT_MINUS20C",
                    "uploaded_frequency": "1 / Lot",
                    "standard_frequency": "Lot başına 1 set",
                    "uploaded_criteria": "Min 80 J < 0°C & 100% pass",
                    "standard_criteria": "STD_CRIT_BOTAS_TABLO_3",
                    "status": "MORE_STRINGENT",
                    "audit_remarks": "Daha sıkı enerji taahhüdü <OK>",
                }
            ],
        }

        pdf_bytes = PDFExporter.export_itp_audit_pdf(audit, lang="tr").getvalue()
        with fitz.open(stream=pdf_bytes, filetype="pdf") as doc:
            full_text = " ".join(" ".join(p.get_text() for p in doc).split())

        self.assertIn("TARGET_MIN_60J_AT_MINUS20C", full_text)
        self.assertIn("STD_CRIT_BOTAS_TABLO_3", full_text)
        self.assertIn("APPROVED WITH COMMENTS", full_text)
        self.assertNotIn("REJECTED", full_text)

    def test_excel_export_neutralizes_formulas_and_strips_control_chars(self):
        audit = {
            "pipe_summary": {
                "diameter_mm": 1219.0,
                "diameter_inch": '48"',
                "wall_thickness_mm": 14.3,
                "material_grade": "X65",
                "manufacturing_process": "SAWH",
                "psl_level": "PSL2",
                "standard_edition": "API Spec 5L 47. Baskı",
            },
            "kpi": {
                "compliance_score_percent": 50.0,
                "overall_verdict": "REJECTED",
            },
            "audit_rows": [
                {
                    "test_name": "=HYPERLINK(\"http://evil.example\",\"Click\")\x00\x07",
                    "category": "+SUM(1,1)",
                    "calculated_target": "-100",
                    "ndt_method_standard": "@cmd|' /C calc'!A0",
                    "uploaded_frequency": "\t=1+1",
                    "standard_frequency": "Her boru",
                    "uploaded_criteria": "  =IMPORTXML(\"http://x\",\"//a\")",
                    "standard_criteria": "Min 100 bar",
                    "inspection_points": {},
                    "status": "NON_COMPLIANT",
                    "audit_remarks": "-Test\x0b remark",
                }
            ],
            "findings": [
                {
                    "severity": "CRITICAL",
                    "test_name": "=1+2",
                    "issue_type": "CRITERIA_VIOLATION",
                    "clause_ref": "@REF",
                    "message": "+Bad\x0c formula",
                }
            ],
        }

        xlsx_buf = ExcelExporter.export_itp_audit_report(audit, lang="tr")
        wb = openpyxl.load_workbook(xlsx_buf, data_only=False)
        for ws in wb.worksheets:
            for row in ws.iter_rows():
                for cell in row:
                    self.assertNotEqual(cell.data_type, "f")

        ws_main = wb.active
        self.assertEqual(ws_main.cell(5, 1).value, "'=HYPERLINK(\"http://evil.example\",\"Click\")")
        self.assertEqual(ws_main.cell(5, 2).value, "'+SUM(1,1)")
        self.assertEqual(ws_main.cell(5, 3).value, "'-100")
        self.assertEqual(ws_main.cell(5, 4).value, "'@cmd|' /C calc'!A0")
        self.assertEqual(ws_main.cell(5, 7).value, "'  =IMPORTXML(\"http://x\",\"//a\")")

    def test_upload_security_magic_bytes_oversized_and_export_header_sanitization(self):
        r_bad_pdf = self.client.post(
            "/api/itp/upload-and-audit",
            files={"file": ("fake.pdf", b"NOT A PDF CONTENT", "application/pdf")},
            data={"pipe_config_json": "{}"},
        )
        self.assertEqual(r_bad_pdf.status_code, 400)

        r_bad_png = self.client.post(
            "/api/itp/upload-and-audit",
            files={"file": ("fake.png", b"<html>alert(1)</html>", "image/png")},
            data={"pipe_config_json": "{}"},
        )
        self.assertEqual(r_bad_png.status_code, 400)

        with patch.object(app_module, "MAX_ITP_UPLOAD_SIZE", 256):
            r_big = self.client.post(
                "/api/itp/upload-and-audit",
                files={"file": ("big.pdf", b"%PDF-1.4\n" + b"A" * 512, "application/pdf")},
                data={"pipe_config_json": "{}"},
            )
            self.assertEqual(r_big.status_code, 413)

        malicious_audit = {
            "pipe_summary": {
                "diameter_inch": '1/2"',
                "material_grade": 'X65"; filename="evil.exe\r\nX-Evil: 1',
            },
            "kpi": {"compliance_score_percent": 100.0, "overall_verdict": "APPROVED"},
            "audit_rows": [],
            "findings": [],
        }
        for ep in ("/api/itp/export-audit-report", "/api/itp/export-audit-pdf"):
            resp = self.client.post(ep, json={"audit_result": malicious_audit, "lang": "tr"})
            self.assertEqual(resp.status_code, 200)
            cd = resp.headers["content-disposition"]
            self.assertNotIn("\r", cd)
            self.assertNotIn("\n", cd)
            self.assertNotIn(";", cd.split('filename="', 1)[1])
            self.assertNotIn("X-Evil", cd)
            self.assertEqual(cd.count("filename="), 1)
            self.assertNotIn("1/2", cd)

        r_wt0 = self.client.get("/api/itp/reference-frequencies?wall_thickness_mm=0")
        self.assertEqual(r_wt0.status_code, 400)

        r_bad_manual = self.client.post(
            "/api/itp/audit-manual",
            json={"items": "not-a-list", "pipe_config": {}},
        )
        self.assertEqual(r_bad_manual.status_code, 400)

    def test_step1c_criteria_parser_fixes_and_redos(self):
        dim_range = ITPCriteriaParser.parse_dimensional_criteria("1217.40 - 1220.60 mm")
        self.assertIsNone(dim_range["minus_mm"])
        self.assertIsNone(dim_range["plus_mm"])

        dim_asym = ITPCriteriaParser.parse_dimensional_criteria("-0.5 / +2.0 mm")
        self.assertEqual(dim_asym["minus_mm"], 0.5)
        self.assertEqual(dim_asym["plus_mm"], 2.0)

        chem = ITPCriteriaParser.parse_chemical_criteria(
            "C ≤ %0.12, P ≤ %0.15, S ≤ %0.12, N ≤ %0.10, CE_Pcm ≤ %0.22, CE_IIW ≤ %0.40"
        )
        self.assertEqual(chem["C_max"], 0.12)
        self.assertEqual(chem["P_max"], 0.15)
        self.assertEqual(chem["S_max"], 0.12)
        self.assertEqual(chem["N_max"], 0.10)
        self.assertEqual(chem["CE_Pcm_max"], 0.22)
        self.assertEqual(chem["CE_IIW_max"], 0.40)

        tens = ITPCriteriaParser.parse_tensile_criteria(
            "Rt0.5/Rm <= 0.90, Rt0.5: 450 - 570 MPa, Rm: 535 - 760 MPa, Kopma uzaması >= %19.5"
        )
        self.assertEqual(tens["ratio_max"], 0.90)
        self.assertEqual(tens["yield_min"], 450.0)
        self.assertEqual(tens["tensile_min"], 535.0)
        self.assertEqual(tens["elongation_min"], 19.5)

        hydro = ITPCriteriaParser.parse_hydrostatic_criteria("168.0 bar, 20.0 s")
        self.assertEqual(hydro["holding_time_sec"], 20.0)

        coat = ITPCriteriaParser.parse_coating_criteria(
            "FBE min 0.15 mm, Yapıştırıcı 0.20 mm, Toplam 3LPE min 3.0 mm, 5 kV/mm (25 kV)"
        )
        self.assertEqual(coat["fbe_um"], 150.0)
        self.assertEqual(coat["total_pe_mm"], 3.0)
        self.assertEqual(coat["holiday_kv"], 25.0)
        self.assertEqual(coat["holiday_kv_per_mm"], 5.0)
        self.assertIsNone(ITPCriteriaParser.parse_coating_criteria("5 kV/mm")["holiday_kv"])

        start = time.monotonic()
        ITPCriteriaParser.parse_chemical_criteria("c" + (" " * 20000) + "x")
        ITPCriteriaParser.parse_cvn_criteria("ort" + (" " * 20000) + "x")
        ITPCriteriaParser.parse_dimensional_criteria("+" + (" " * 20000) + "x")
        self.assertLess(time.monotonic() - start, 0.2)

    def test_step1c_audit_engine_matching_and_evaluation_fixes(self):
        cfg_sawh = {
            "diameter_mm": 1219.0,
            "diameter_inch": '48"',
            "wall_thickness_mm": 14.3,
            "material_grade": "X65",
            "manufacturing_process": "SAWH",
            "standard_type": "BOTAŞ",
            "psl_level": "PSL2",
        }

        audit_mis_ok = ITPAuditEngine.audit_itp(
            [{
                "test_name": "Kaynak Hiza Kaçıklığı (Weld Misalignment)",
                "test_frequency": "Vardiyada 2 kez",
                "acceptance_criteria": "Eksenel kaçıklık ≤ 2.25 mm",
            }],
            cfg_sawh,
        )
        mis_ok = next(r for r in audit_mis_ok["audit_rows"] if r["test_key"] == "weld_misalignment")
        self.assertEqual(mis_ok["status"], "COMPLIANT")

        audit_mis_bad = ITPAuditEngine.audit_itp(
            [{
                "test_name": "Kaynak Hiza Kaçıklığı (Weld Misalignment)",
                "test_frequency": "Vardiyada 2 kez",
                "acceptance_criteria": "Eksenel kaçıklık ≤ 4.0 mm",
            }],
            cfg_sawh,
        )
        mis_bad = next(r for r in audit_mis_bad["audit_rows"] if r["test_key"] == "weld_misalignment")
        self.assertEqual(mis_bad["status"], "NON_COMPLIANT")

        audit_hijack = ITPAuditEngine.audit_itp(
            [
                {"test_name": "Etiketleme %100", "test_frequency": "Her boru (%100)", "acceptance_criteria": "Okunaklı etiket"},
                {"test_name": "Gövde Çentik Darbe Testi", "test_frequency": "Lot başına 1 set", "acceptance_criteria": "-20 °C Min Ort. 60 J, Tekil 45 J"},
                {"test_name": "Kaynak ve Gövde Tamir Kuralları", "test_frequency": "Tamir oldukça", "acceptance_criteria": "Gövdeye kaynak yasak, tek tamir <= 150 mm"},
                {"test_name": "Gövde Boya Kontrolü", "test_frequency": "Her boru (%100)", "acceptance_criteria": "Üniform yüzey"},
            ],
            cfg_sawh,
        )
        matched_map = {r["test_key"]: r for r in audit_hijack["audit_rows"]}
        self.assertEqual(matched_map["ndt_weld_seam"]["issue_type"], "MISSING_MANDATORY_TEST")
        self.assertEqual(matched_map["coating_impact_resistance"]["issue_type"], "MISSING_MANDATORY_TEST")
        self.assertEqual(matched_map["coating_repair_rules"]["issue_type"], "MISSING_MANDATORY_TEST")
        self.assertEqual(matched_map["tensile_body"]["issue_type"], "MISSING_MANDATORY_TEST")
        self.assertEqual(matched_map["dimensional_diameter_body"]["issue_type"], "MISSING_MANDATORY_TEST")

        cfg_x42_botas = dict(cfg_sawh, diameter_mm=219.1, diameter_inch='8"', wall_thickness_mm=6.4, material_grade="X42", manufacturing_process="ERW")
        audit_x42_085 = ITPAuditEngine.audit_itp(
            [{"test_name": "Gövde Çekme Testi", "test_frequency": "Lot başına 2 set", "acceptance_criteria": "Y/T <= 0.85"}],
            cfg_x42_botas,
        )
        self.assertEqual(next(r for r in audit_x42_085["audit_rows"] if r["test_key"] == "tensile_body")["status"], "COMPLIANT")

        audit_x42_090 = ITPAuditEngine.audit_itp(
            [{"test_name": "Gövde Çekme Testi", "test_frequency": "Lot başına 2 set", "acceptance_criteria": "Y/T <= 0.90"}],
            cfg_x42_botas,
        )
        self.assertEqual(next(r for r in audit_x42_090["audit_rows"] if r["test_key"] == "tensile_body")["status"], "NON_COMPLIANT")

        cfg_api_x65 = dict(cfg_sawh, standard_type="API 5L")
        audit_api_x65 = ITPAuditEngine.audit_itp(
            [{"test_name": "Gövde Çekme Testi", "test_frequency": "Lot başına 1 set", "acceptance_criteria": "Y/T <= 0.93"}],
            cfg_api_x65,
        )
        self.assertEqual(next(r for r in audit_api_x65["audit_rows"] if r["test_key"] == "tensile_body")["status"], "COMPLIANT")

        audit_x65_botas = ITPAuditEngine.audit_itp(
            [{"test_name": "Gövde Çekme Testi", "test_frequency": "Lot başına 2 set", "acceptance_criteria": "Y/T <= 0.93"}],
            cfg_sawh,
        )
        self.assertEqual(next(r for r in audit_x65_botas["audit_rows"] if r["test_key"] == "tensile_body")["status"], "NON_COMPLIANT")

        audit_vis = ITPAuditEngine.audit_itp(
            [{"test_name": "Görsel Yüzey Muayenesi", "test_frequency": "Her boru (%100)", "acceptance_criteria": "EN 10163-2 Sınıf A"}],
            cfg_sawh,
        )
        self.assertEqual(next(r for r in audit_vis["audit_rows"] if r["test_key"] == "visual_surface")["status"], "NON_COMPLIANT")

        cfg_coat = dict(cfg_sawh, scope_mode="COATING_ONLY")
        audit_coat_bad_sa = ITPAuditEngine.audit_itp(
            [{"test_name": "Kumlama ve Yüzey Hazırlığı", "test_frequency": "Her boru (%100)", "acceptance_criteria": "Sa 2, Rz 60-100 µm"}],
            cfg_coat,
        )
        self.assertEqual(
            next(r for r in audit_coat_bad_sa["audit_rows"] if r["test_key"] == "coating_surface_prep_blasting")["status"],
            "NON_COMPLIANT",
        )

        audit_coat_ok = ITPAuditEngine.audit_itp(
            [
                {"test_name": "Kumlama ve Yüzey Hazırlığı", "test_frequency": "Her boru (%100)", "acceptance_criteria": "Sa 2.5, Rz 60-100 µm"},
                {"test_name": "Holiday Testi", "test_frequency": "Her boru (%100)", "acceptance_criteria": "5 kV/mm (25 kV)"},
                {"test_name": "Doküman Kontrolü EN 10204 3.1", "test_frequency": "Her lot", "acceptance_criteria": "3.1 sertifika"},
            ],
            cfg_coat,
        )
        coat_rows = {r["test_key"]: r for r in audit_coat_ok["audit_rows"]}
        self.assertEqual(coat_rows["coating_surface_prep_blasting"]["status"], "COMPLIANT")
        self.assertEqual(coat_rows["coating_holiday_test"]["status"], "COMPLIANT")
        self.assertIsNone(audit_coat_ok["kpi"]["bare_pipe_score_percent"])

        audit_rz_periodic = ITPAuditEngine.audit_itp(
            [{"test_name": "Yüzey Profili (Rz) ve Tuz Testi", "test_frequency": "4 saatte 1", "acceptance_criteria": "Rz 60-100 µm, Tuz ≤ 20 mg/m²"}],
            cfg_coat,
        )
        self.assertEqual(
            next(r for r in audit_rz_periodic["audit_rows"] if r["test_key"] == "coating_surface_prep_blasting")["status"],
            "COMPLIANT",
        )

        audit_cvn_cold = ITPAuditEngine.audit_itp(
            [{"test_name": "Gövde Çentik Darbe Testi", "test_frequency": "Lot başına 1 set", "acceptance_criteria": "-40 °C'de Min Ort. 60 J, Tekil 45 J"}],
            cfg_sawh,
        )
        self.assertEqual(
            next(r for r in audit_cvn_cold["audit_rows"] if r["test_key"] == "cvn_body")["status"],
            "MORE_STRINGENT",
        )

        audit_cvn_warm = ITPAuditEngine.audit_itp(
            [{"test_name": "Gövde Çentik Darbe Testi", "test_frequency": "Lot başına 1 set", "acceptance_criteria": "-10 °C'de Min Ort. 60 J, Tekil 45 J"}],
            cfg_sawh,
        )
        self.assertEqual(
            next(r for r in audit_cvn_warm["audit_rows"] if r["test_key"] == "cvn_body")["status"],
            "NON_COMPLIANT",
        )

        self.assertEqual(FrequencyNormalizer.normalize("1 in 50 pipes"), FrequencyCanonical.INADEQUATE_SAMPLING)
        self.assertEqual(FrequencyNormalizer.normalize("1 set per 100 pipes"), FrequencyCanonical.INADEQUATE_SAMPLING)
        self.assertEqual(FrequencyNormalizer.normalize("Hard spot 100%"), FrequencyCanonical.EVERY_PIPE_100)

        audit_hydro_heat = ITPAuditEngine.audit_itp(
            [{"test_name": "Fabrika Hidrostatik Basınç Testi", "test_frequency": "Her dökümde 1", "acceptance_criteria": "Min 168.0 bar, 20 s"}],
            cfg_sawh,
        )
        hydro_row = next(r for r in audit_hydro_heat["audit_rows"] if r["test_key"] == "hydrostatic")
        self.assertEqual(hydro_row["status"], "NON_COMPLIANT")
        self.assertEqual(hydro_row["issue_type"], "INADEQUATE_FREQUENCY")

    def test_step1c_test_plan_botas_wall_tol_and_peel_unit(self):
        cfg = {
            "diameter_mm": 1219.0,
            "diameter_inch": '48"',
            "wall_thickness_mm": 14.30,
            "material_grade": "X65",
            "manufacturing_process": "SAWH",
            "standard_type": "BOTAŞ",
            "psl_level": "PSL2",
        }
        qc = PipeQAQCEngine.calculate_pipe_qc(
            diameter_inch='48"',
            diameter_mm=1219.0,
            wall_thickness_mm=14.30,
            material_grade="X65",
            manufacturing_process="SAWH",
            standard_type="BOTAŞ",
            psl_level="PSL2",
        )
        spec = {it["test_key"]: it for it in get_comprehensive_itp_specification(cfg)}
        self.assertEqual(
            spec["dimensional_wall_thickness"]["calculated_targets"]["min_mm"],
            qc["wall_thickness_tolerance"]["min_mm"],
        )
        self.assertEqual(spec["dimensional_wall_thickness"]["calculated_targets"]["min_mm"], 14.15)
        self.assertIn("yt_max", spec["tensile_body"]["calculated_targets"])
        self.assertIn("yt_ratio_max", spec["tensile_body"]["calculated_targets"])
        self.assertIn("15 N/mm", spec["coating_peel_adhesion"]["standard_acceptance_criteria"])
        self.assertNotIn("18 N/mm", spec["coating_peel_adhesion"]["standard_acceptance_criteria"])


if __name__ == "__main__":
    unittest.main()
