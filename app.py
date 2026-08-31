import json
import logging
import os
import sys
from typing import Any, Dict, Optional

from fastapi import Body, FastAPI, File, Form, Request, UploadFile
from fastapi.responses import HTMLResponse, JSONResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from core.database import API_5L_SMYS_TABLE, PIPE_SIZES_TABLE, normalize_design_factor
from core.excel_exporter import ExcelExporter
from core.i18n import TRANSLATIONS, get_text
from core.itp_audit_engine import ITPAuditEngine
from core.pipe_qaqc_engine import PipeQAQCEngine
from core.project_manager import ProjectManager
from core.schemas import (
    CalculateRequest,
    ExportRequest,
    PipeInput,
    ReportRequest,
    SawhStripRequest,
    VerificationRequest,
    WallThicknessRequest,
)
from core.test_plan import get_comprehensive_itp_specification, get_test_plan as compute_test_plan
from core.unlimited_ocr_engine import UnlimitedOCREngine
from core.verification_engine import PipeVerificationEngine
from core.wall_thickness_engine import WallThicknessEngine
from version import __version__

logger = logging.getLogger(__name__)

# Resolve base directory (compatible with PyInstaller one-file and normal runtime)
BASE_DIR = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
STATIC_DIR = os.path.join(BASE_DIR, "static")
TEMPLATES_DIR = os.path.join(BASE_DIR, "templates")

app = FastAPI(
    title="API 5L PSL2 & BOTAŞ Pipe QA/QC & Acceptance Suite",
    description="Full-Scope Quality Assurance, Testing Verification and Wall Thickness Calculation Engine",
    version=__version__
)

# Ensure static and template directories exist
os.makedirs(os.path.join(STATIC_DIR, "css"), exist_ok=True)
os.makedirs(os.path.join(STATIC_DIR, "js"), exist_ok=True)
os.makedirs(os.path.join(STATIC_DIR, "img"), exist_ok=True)
os.makedirs(TEMPLATES_DIR, exist_ok=True)

app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")
templates = Jinja2Templates(directory=TEMPLATES_DIR)


def _fmt_number(v, dec=2):
    """Jinja template filter to format floats safely."""
    if v is None or v == "":
        return "—"
    if isinstance(v, (int, float)):
        return f"{v:.{int(dec)}f}"
    return str(v)


templates.env.filters['fmt'] = _fmt_number

def _calculate_pipes(pipes) -> list:
    """Runs the QA/QC engine over a list of PipeInput models or dicts with per-pipe error isolation."""
    results = []
    for p in pipes:
        try:
            pd = p.model_dump() if isinstance(p, PipeInput) else p
            res = PipeQAQCEngine.calculate_pipe_qc(
                diameter_inch=pd.get("diameter_inch", "48\""),
                diameter_mm=pd.get("diameter_mm"),
                wall_thickness_mm=pd.get("wall_thickness_mm"),
                design_factor_str=pd.get("design_factor_str", "0.72 (Hat)"),
                material_grade=pd.get("material_grade", "X65"),
                manufacturing_process=pd.get("manufacturing_process", "SAWH"),
                standard_type=pd.get("standard_type", "BOTAŞ"),
                design_pressure_bar=pd.get("design_pressure_bar", 75.0),
                psl_level=pd.get("psl_level", "PSL2"),
                delivery_condition=pd.get("delivery_condition", "M")
            )
            res['id'] = pd.get('id', '')
            results.append(res)
        except Exception as e_pipe:
            logger.error(f"Error calculating pipe {p}: {e_pipe}")
            p_id = getattr(p, 'id', '') if hasattr(p, 'id') else (p.get('id', '') if isinstance(p, dict) else '')
            results.append({
                'id': p_id,
                'error': str(e_pipe),
                'input_summary': {'error': True, 'message': str(e_pipe)}
            })
    return results

@app.get("/", response_class=HTMLResponse)
async def index_page(request: Request):
    """Renders the main interactive engineering dashboard."""
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={
            "app_version": __version__,
            "translations": TRANSLATIONS,
            "grades": list(API_5L_SMYS_TABLE.keys()),
            "diameters": PIPE_SIZES_TABLE
        }
    )

@app.get("/api/check-update")
async def check_update_endpoint():
    """
    Checks GitHub Releases for application updates and returns download links.
    """
    from core.updater import check_for_updates
    update_info = await check_for_updates()
    return JSONResponse(content=update_info)

@app.post("/api/calculate")
async def calculate_matrix(data: CalculateRequest = Body(...)):
    """
    Calculates full QA/QC acceptance matrix for a list of pipes.
    """
    results = _calculate_pipes(data.pipes)
    return JSONResponse(content={"status": "success", "data": results})

@app.post("/api/verify")
async def verify_pipe(data: VerificationRequest = Body(...)):
    """
    Verifies actual inspection test data against API 5L and BOTAŞ specifications (PASS/FAIL).
    """
    result = PipeVerificationEngine.verify_pipe_test_results(data.pipe_config, data.actual_data)
    return JSONResponse(content={"status": "success", "verification": result})

@app.post("/api/wall-thickness")
async def calculate_wall_thickness(data: WallThicknessRequest = Body(...)):
    """
    Calculates required pipe wall thickness across BOTAŞ, ASME B31.8/B31.4, or ASME B31.3
    and selects standard nominal thickness from ASME B36.10M or ASME B36.19M.
    """
    res = WallThicknessEngine.calculate_wall_thickness(
        diameter_inch=data.diameter_inch,
        material_grade=data.material_grade,
        design_pressure_bar=float(data.design_pressure_bar),
        design_factor_f=float(data.design_factor_f),
        longitudinal_joint_factor_e=float(data.longitudinal_joint_factor_e),
        temperature_derating_factor_t=float(data.temperature_derating_factor_t),
        corrosion_allowance_mm=float(data.corrosion_allowance_mm),
        location_type=data.location_type,
        standard_code=data.standard_code,
        manufacturing_process=data.manufacturing_process,
        apply_negative_tolerance=data.apply_negative_tolerance,
        manual_negative_tolerance_percent=data.manual_negative_tolerance_percent,
        psl_level=data.psl_level
    )
    return JSONResponse(content={"status": "success", "data": res})

@app.get("/api/presets/reference")
async def get_reference_preset():
    """Returns the reference preset (48\" SAWH X65 with 5 wall thicknesses + 18\" SAWH X65)."""
    return JSONResponse(content=ProjectManager.get_reference_preset_48_18())

@app.get("/api/presets/botas-10")
async def get_botas_10_preset():
    """Returns preset with 10 distinct BOTAŞ standard pipes."""
    return JSONResponse(content=ProjectManager.get_10_botas_pipes_preset())

@app.get("/api/presets/api5l-10")
async def get_api5l_10_preset():
    """Returns preset with 10 distinct API 5L PSL2 pipes."""
    return JSONResponse(content=ProjectManager.get_10_api_5l_pipes_preset())

@app.get("/api/presets/api5l-psl1-10")
async def get_api5l_psl1_10_preset():
    """Returns preset with 10 distinct API 5L PSL1 pipes."""
    return JSONResponse(content=ProjectManager.get_10_api_5l_psl1_pipes_preset())

@app.get("/api/botas-lookup")
async def lookup_botas_specs(diameter_inch: str, factor: str = "0.72 (Hat)", pressure: float = 75.0):
    """
    Returns BOTAŞ standard material and wall thickness for a given diameter, factor and pressure.
    """
    pipe_size = None
    for p in PIPE_SIZES_TABLE:
        clean1 = p['inch'].replace('\"', '').replace("'", '').strip()
        clean2 = diameter_inch.replace('\"', '').replace("'", '').strip()
        if clean1 == clean2 or p['inch'] == diameter_inch:
            pipe_size = p
            break

    if not pipe_size:
        return JSONResponse(
            status_code=404,
            content={"status": "not_found", "message": f"Boru çapı '{diameter_inch}' standart BOTAŞ tablosunda bulunamadı."}
        )

    factor_key = normalize_design_factor(factor)
    if factor_key in ("0.50_ist1", "0.50_ist2", "0.50_ist_75bar", "0.50_ist_82_5bar"):
        if float(pressure) > 75.0 or "ist2" in str(factor).lower() or "82" in str(factor):
            factor_key = "0.50_ist2"
        else:
            factor_key = "0.50_ist1"

    botas_thk = pipe_size['botas_thk'].get(factor_key, 0.0)
    if botas_thk == 0.0:
        botas_thk = pipe_size['botas_thk'].get('0.50_ist1', 14.30)

    return JSONResponse(content={
        "status": "success",
        "diameter_inch": pipe_size['inch'],
        "diameter_mm": pipe_size['mm'],
        "material": pipe_size['default_material'],
        "thickness": botas_thk,
        "available_thicknesses": pipe_size['botas_thk']
    })

@app.get("/api/botas-all-factors")
async def get_botas_all_factors(diameter_inch: str):
    """
    Returns all standard BOTAŞ pipe configurations for all available design factors for a given diameter.
    """
    from core.database import get_botas_all_factors_for_diameter
    pipes = get_botas_all_factors_for_diameter(diameter_inch)
    return JSONResponse(content={
        "status": "success",
        "diameter_inch": diameter_inch,
        "count": len(pipes),
        "pipes": pipes
    })

@app.post("/api/export-excel")
async def export_excel(data: ExportRequest = Body(...)):
    """
    Generates and streams formatted Excel spreadsheet.
    """
    import re
    project_info = data.project_info
    lang = data.lang

    pipes_calculated = _calculate_pipes(data.pipes)
    excel_file = ExcelExporter.export_matrix_to_excel(project_info, pipes_calculated, lang=lang)
    
    raw_no = str(project_info.get('project_no', 'API5L')).strip()
    safe_no = re.sub(r'[^a-zA-Z0-9_\-\.]', '_', raw_no)
    filename = f"Boru_Kabul_Raporu_{safe_no}.xlsx"
    headers = {
        'Content-Disposition': f'attachment; filename="{filename}"'
    }
    return StreamingResponse(
        excel_file,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers=headers
    )

@app.post("/api/sawh-strip")
async def sawh_strip(data: SawhStripRequest = Body(...)):
    """
    SAWH spiral strip width & helix angle calculation.
    """
    from core.sawh_engine import compute_sawh_calc

    d_mm = data.diameter_mm
    if d_mm is None and data.diameter_inch:
        from core.database import get_pipe_size_by_inch
        ps = get_pipe_size_by_inch(data.diameter_inch)
        d_mm = ps['mm'] if ps else 1219.0
    elif d_mm is None:
        d_mm = 1219.0

    res = compute_sawh_calc(
        float(d_mm),
        float(data.wall_thickness_mm or 0.0),
        strip_width_mm=float(data.strip_width_mm) if data.strip_width_mm is not None else None,
        helix_angle_deg=float(data.helix_angle_deg) if data.helix_angle_deg is not None else None,
    )
    return JSONResponse(content={"status": "success", "data": res})

@app.post("/api/test-plan")
async def api_get_test_plan(data: Dict[str, Any] = Body(...)):
    """
    Returns the API 5L PSL2 inspection & test plan (sampling frequency,
    location and specimen dimensions) for a given pipe configuration.
    """
    pipe_config = data.get("pipe_config", data)
    plan = compute_test_plan(pipe_config, psl_level=pipe_config.get("psl_level", "PSL2"))
    return JSONResponse(content={"status": "success", "test_plan": plan})

@app.post("/api/report-view", response_class=HTMLResponse)
async def generate_html_report(request: Request, data: ReportRequest = Body(...)):
    """
    Renders printable official inspection certificate / FAT report.
    """
    project_info = data.project_info
    lang = data.lang
    verification = data.verification

    pipes_calculated = _calculate_pipes(data.pipes)

    # API 5L inspection & test plan for the first pipe (sampling info)
    from core.test_plan import get_test_plan
    test_plan = []
    if data.pipes:
        pd0 = data.pipes[0].model_dump()
        test_plan = get_test_plan(pd0, psl_level=pd0.get("psl_level", "PSL2"))

    return templates.TemplateResponse(
        request=request,
        name="report_template.html",
        context={
            "project": project_info,
            "pipes": pipes_calculated,
            "lang": lang,
            "verification": verification,
            "test_plan": test_plan,
            "app_version": __version__,
            "t": lambda key: get_text(key, lang)
        }
    )

MAX_ITP_UPLOAD_SIZE = 25 * 1024 * 1024  # 25 MB max limit (DoS protection)
ALLOWED_ITP_EXTENSIONS = (".pdf", ".png", ".jpg", ".jpeg")

@app.post("/api/itp/upload-and-audit")
async def upload_and_audit_itp(
    file: Optional[UploadFile] = File(None),
    pipe_config_json: str = Form("{}"),
    use_demo: bool = Form(False)
):
    """
    Uploads an ITP document (PDF / image), validates size & MIME type,
    runs Unlimited-OCR parsing, and audits against API 5L 47th Ed. / BOTAŞ master specification.
    """
    try:
        pipe_config = json.loads(pipe_config_json) if pipe_config_json else {}
    except Exception:
        pipe_config = {}

    if not pipe_config:
        pipe_config = {
            "diameter_mm": 1219.0,
            "diameter_inch": '48"',
            "wall_thickness_mm": 14.30,
            "material_grade": "X65",
            "manufacturing_process": "SAWH",
            "psl_level": "PSL2",
            "standard_type": "API"
        }

    if use_demo or file is None:
        extracted = UnlimitedOCREngine._heuristic_extract_fallback("demo")
        audit_res = ITPAuditEngine.audit_itp(extracted, pipe_config)
        return JSONResponse(content={
            "status": "success",
            "is_fallback": False,
            "source": "Demo ITP Sample Data",
            "extracted_items": extracted,
            "audit_result": audit_res
        })

    filename = file.filename or "itp_doc.pdf"
    if not any(filename.lower().endswith(ext) for ext in ALLOWED_ITP_EXTENSIONS):
        return JSONResponse(
            status_code=400,
            content={"status": "error", "message": "Geçersiz dosya formatı. Yalnızca PDF veya görsel (.png, .jpg) yükleyebilirsiniz."}
        )

    content_bytes = await file.read()
    if len(content_bytes) > MAX_ITP_UPLOAD_SIZE:
        return JSONResponse(
            status_code=400,
            content={"status": "error", "message": f"Dosya boyutu çok büyük (Max: {MAX_ITP_UPLOAD_SIZE // (1024*1024)} MB)."}
        )

    parse_result = UnlimitedOCREngine.parse_pdf_or_image(content_bytes, filename)
    extracted_items = parse_result.get("items", [])
    audit_res = ITPAuditEngine.audit_itp(extracted_items, pipe_config)

    # Persist in current project state if available
    try:
        current_proj = ProjectManager.get_current_project()
        if current_proj:
            current_proj["latest_itp_audit"] = {
                "source": filename,
                "engine": parse_result.get("engine", "Unlimited-OCR"),
                "audit_result": audit_res
            }
    except Exception as e:
        logger.debug(f"Project state save debug: {e}")

    return JSONResponse(content={
        "status": parse_result.get("status", "success"),
        "is_fallback": parse_result.get("is_fallback", False),
        "warning_message": parse_result.get("warning_message"),
        "source": filename,
        "engine": parse_result.get("engine", "Unlimited-OCR"),
        "extracted_items": extracted_items,
        "audit_result": audit_res
    })

@app.post("/api/itp/audit-manual")
async def audit_itp_manual(data: Dict[str, Any] = Body(...)):
    """
    Audits manually provided or edited ITP rows against the selected pipe configuration.
    """
    items = data.get("items", [])
    pipe_config = data.get("pipe_config", {})
    audit_res = ITPAuditEngine.audit_itp(items, pipe_config)
    return JSONResponse(content={"status": "success", "audit_result": audit_res})

@app.post("/api/itp/export-audit-report")
async def export_itp_audit_report(data: Dict[str, Any] = Body(...)):
    """
    Generates and downloads styled Excel audit discrepancy report.
    """
    audit_data = data.get("audit_result", {})
    lang = data.get("lang", "tr")
    excel_stream = ExcelExporter.export_itp_audit_report(audit_data, lang)

    pipe = audit_data.get("pipe_summary", {})
    d_inch = str(pipe.get("diameter_inch", "48in")).replace('"', '').replace("'", "").strip()
    grade = pipe.get("material_grade", "X65")
    filename = f"ITP_Audit_Report_{d_inch}_{grade}_API5L_47th.xlsx"

    return StreamingResponse(
        excel_stream,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'}
    )

@app.get("/api/itp/reference-frequencies")
async def get_reference_frequencies(
    diameter_mm: float = 1219.0,
    wall_thickness_mm: float = 14.30,
    material_grade: str = "X65",
    manufacturing_process: str = "SAWH",
    psl_level: str = "PSL2",
    standard_type: str = "API"
):
    """
    Returns official API 5L 47th Edition (Tables 17, 18, 19, 20) & BOTAŞ master test frequencies.
    """
    pipe_config = {
        "diameter_mm": diameter_mm,
        "wall_thickness_mm": wall_thickness_mm,
        "material_grade": material_grade,
        "manufacturing_process": manufacturing_process,
        "psl_level": psl_level,
        "standard_type": standard_type
    }
    master_spec = get_comprehensive_itp_specification(pipe_config)
    return JSONResponse(content={"status": "success", "master_specification": master_spec})

