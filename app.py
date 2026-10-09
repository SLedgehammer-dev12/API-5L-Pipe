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
from core.pdf_exporter import PDFExporter
from core.pipe_qaqc_engine import PipeQAQCEngine
from core.project_manager import ProjectManager
from core.schemas import (
    CalculateRequest,
    ExportRequest,
    ExportVerificationRequest,
    ExportWallThicknessRequest,
    ExportSawhRequest,
    ExportSawlRequest,
    ExportHydroRequest,
    ExportErwRequest,
    ExportBevelRequest,
    ExportStraightnessRequest,
    ExportDeratingRequest,
    PipeInput,
    ReportRequest,
    SawhStripRequest,
    SawlCalcRequest,
    HydroCalcRequest,
    ErwCalcRequest,
    BevelCalcRequest,
    StraightnessCalcRequest,
    DeratingCalcRequest,
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
                operating_pressure_bar=pd.get("operating_pressure_bar"),
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

@app.post("/api/export-matrix-pdf")
async def export_matrix_pdf_endpoint(data: ExportRequest = Body(...)):
    """
    Generates and streams publication-grade Landscape A4 PDF report
    for the multi-pipe QA/QC Factory Acceptance & Dimensional Tolerances Matrix.
    """
    import re
    project_info = data.project_info or {}
    lang = data.lang or "tr"
    pipes_calculated = _calculate_pipes(data.pipes)

    pdf_stream = PDFExporter.export_matrix_pdf(project_info, pipes_calculated, lang=lang)

    raw_no = str(project_info.get("project_no", "API5L")).strip()
    safe_no = re.sub(r"[^a-zA-Z0-9_\-\.]", "_", raw_no)
    filename = f"Boru_Kalite_Guvence_Kabul_Matrisi_{safe_no}.pdf" if lang == "tr" else f"Pipe_QA_QC_Acceptance_Matrix_{safe_no}.pdf"

    return StreamingResponse(
        pdf_stream,
        media_type="application/pdf",
        headers={"Content-Disposition": f'inline; filename="{filename}"'}
    )

@app.post("/api/export-verification-excel")
async def export_verification_excel(data: ExportVerificationRequest = Body(...)):
    """
    Generates and streams formatted Excel report for MTC inspection verification results.
    """
    import re
    project_info = data.project_info or {}
    verification_data = data.verification or {}
    lang = data.lang or "tr"

    excel_file = ExcelExporter.export_verification_report(project_info, verification_data, lang=lang)

    raw_no = str(project_info.get('project_no', 'API5L')).strip()
    safe_no = re.sub(r'[^a-zA-Z0-9_\-\.]', '_', raw_no) if raw_no else 'API5L'
    filename = f"MTC_Dogrulama_{safe_no}.xlsx"
    headers = {
        'Content-Disposition': f'attachment; filename="{filename}"'
    }
    return StreamingResponse(
        excel_file,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers=headers
    )

@app.post("/api/export-wall-thickness-excel")
async def export_wall_thickness_excel(data: ExportWallThicknessRequest = Body(...)):
    """
    Generates and streams formatted Excel engineering calculation sheet for pipe wall thickness.
    """
    import re
    project_info = data.project_info or {}
    calculation_data = data.calculation_data or {}
    lang = data.lang or "tr"

    excel_file = ExcelExporter.export_wall_thickness_report(calculation_data, project_info, lang=lang)

    raw_no = str(project_info.get('project_no', 'CALC')).strip()
    safe_no = re.sub(r'[^a-zA-Z0-9_\-\.]', '_', raw_no) if raw_no else 'CALC'
    raw_dia = str(calculation_data.get('input_parameters', {}).get('diameter_inch', '48in')).replace('"', '').replace("'", "").strip()
    safe_dia = re.sub(r'[^a-zA-Z0-9_\-\.]', '', raw_dia) if raw_dia else '48in'
    if not safe_dia.endswith('in') and not safe_dia.endswith('mm'):
        safe_dia = f"{safe_dia}in"
    filename = f"Et_Kalinligi_Hesabi_{safe_no}_{safe_dia}.xlsx"
    headers = {
        'Content-Disposition': f'attachment; filename="{filename}"'
    }
    return StreamingResponse(
        excel_file,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers=headers
    )

@app.post("/api/export-sawh-excel")
async def export_sawh_excel(data: ExportSawhRequest = Body(...)):
    """
    Generates and streams formatted Excel engineering calculation sheet for SAWH spiral geometry and coil strip procurement.
    """
    import re
    from core.sawh_engine import compute_sawh_calc

    project_info = data.project_info or {}
    sawh_data = data.sawh_data or {}
    pipe_info = data.pipe_info or {}
    lang = data.lang or "tr"

    # Ensure all enriched manufacturing metrics are populated
    d_v = float(sawh_data.get("d_mm") or pipe_info.get("diameter_mm") or 1219.0)
    t_v = float(sawh_data.get("t_mm") or pipe_info.get("wall_thickness_mm") or 14.30)
    b_v = float(sawh_data["strip_width_mm"]) if sawh_data.get("strip_width_mm") else None
    a_v = float(sawh_data["helix_angle_deg"]) if (sawh_data.get("helix_angle_deg") and not b_v) else None
    milling_v = float(sawh_data.get("edge_milling_allowance_mm", 15.0) or 15.0)
    coil_len_v = float(sawh_data.get("coil_length_m", 800.0) or 800.0)
    pipe_len_v = float(sawh_data.get("pipe_length_m", 12.0) or 12.0)
    min_skelp_dist_v = float(sawh_data.get("min_skelp_end_distance_mm", 300.0) or 300.0)

    # Re-compute to guarantee consistency of all metrics
    computed = compute_sawh_calc(
        d_mm=d_v,
        t_mm=t_v,
        strip_width_mm=b_v,
        helix_angle_deg=a_v,
        edge_milling_allowance_mm=milling_v,
        coil_length_m=coil_len_v,
        pipe_length_m=pipe_len_v,
        min_skelp_end_distance_mm=min_skelp_dist_v,
    )
    # Merge existing metadata while using computed math
    final_sawh_data = {**sawh_data, **computed}

    excel_file = ExcelExporter.export_sawh_geometry_report(
        final_sawh_data,
        project_info,
        pipe_info=pipe_info,
        lang=lang
    )

    raw_no = str(project_info.get('project_no', 'SAWH')).strip()
    safe_no = re.sub(r'[^a-zA-Z0-9_\-\.]', '_', raw_no) if raw_no else 'SAWH'
    raw_dia = str(pipe_info.get('diameter_inch', f"{d_v:.0f}mm")).replace('"', '').replace("'", "").strip()
    safe_dia = re.sub(r'[^a-zA-Z0-9_\-\.]', '', raw_dia) if raw_dia else '48in'
    if not safe_dia.endswith('in') and not safe_dia.endswith('mm'):
        safe_dia = f"{safe_dia}in"
    filename = f"SAWH_Spiral_Geometri_{safe_no}_{safe_dia}.xlsx"
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
        edge_milling_allowance_mm=float(data.edge_milling_allowance_mm if data.edge_milling_allowance_mm is not None else 15.0),
        coil_length_m=float(data.coil_length_m if data.coil_length_m is not None else 800.0),
        pipe_length_m=float(data.pipe_length_m if data.pipe_length_m is not None else 12.0),
        min_skelp_end_distance_mm=float(data.min_skelp_end_distance_mm if data.min_skelp_end_distance_mm is not None else 300.0),
    )
    return JSONResponse(content={"status": "success", "data": res})

@app.post("/api/export-sawl-excel")
async def export_sawl_excel(data: ExportSawlRequest = Body(...)):
    """
    Generates and streams formatted Excel engineering calculation sheet for SAWL longitudinal pipe JCOE geometry,
    heavy plate procurement, and API 5L 8.9 mechanical expansion.
    """
    import re
    from core.sawl_engine import compute_sawl_calc

    project_info = data.project_info or {}
    sawl_data = data.sawl_data or {}
    pipe_info = data.pipe_info or {}
    lang = data.lang or "tr"

    d_v = float(sawl_data.get("d_mm") or pipe_info.get("diameter_mm") or 1219.0)
    t_v = float(sawl_data.get("t_mm") or pipe_info.get("wall_thickness_mm") or 14.30)
    l_v = float(sawl_data.get("pipe_length_m") or 12.0)
    milling_v = float(sawl_data.get("edge_milling_allowance_mm", 30.0) or 30.0)
    er_v = float(sawl_data.get("expansion_ratio_pct", 1.0) or 1.0)

    computed = compute_sawl_calc(
        d_mm=d_v,
        t_mm=t_v,
        pipe_length_m=l_v,
        edge_milling_allowance_mm=milling_v,
        expansion_ratio_pct=er_v,
    )
    final_sawl_data = {**sawl_data, **computed}

    excel_file = ExcelExporter.export_sawl_geometry_report(
        final_sawl_data,
        project_info,
        pipe_info=pipe_info,
        lang=lang
    )

    raw_no = str(project_info.get('project_no', 'SAWL')).strip()
    safe_no = re.sub(r'[^a-zA-Z0-9_\-\.]', '_', raw_no) if raw_no else 'SAWL'
    raw_dia = str(pipe_info.get('diameter_inch', f"{d_v:.0f}mm")).replace('"', '').replace("'", "").strip()
    safe_dia = re.sub(r'[^a-zA-Z0-9_\-\.]', '', raw_dia) if raw_dia else '48in'
    if not safe_dia.endswith('in') and not safe_dia.endswith('mm'):
        safe_dia = f"{safe_dia}in"
    filename = f"SAWL_Boyuna_Geometri_{safe_no}_{safe_dia}.xlsx"
    headers = {
        'Content-Disposition': f'attachment; filename="{filename}"'
    }
    return StreamingResponse(
        excel_file,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers=headers
    )

@app.post("/api/sawl-calc")
async def api_sawl_calc(data: SawlCalcRequest = Body(...)):
    """
    SAWL longitudinal pipe JCOE plate sizing and mechanical expansion calculation.
    """
    from core.sawl_engine import compute_sawl_calc

    d_mm = data.diameter_mm
    if d_mm is None and data.diameter_inch:
        from core.database import get_pipe_size_by_inch
        ps = get_pipe_size_by_inch(data.diameter_inch)
        d_mm = ps['mm'] if ps else 1219.0
    elif d_mm is None:
        d_mm = 1219.0

    res = compute_sawl_calc(
        float(d_mm),
        float(data.wall_thickness_mm or 14.30),
        pipe_length_m=float(data.pipe_length_m or 12.0),
        edge_milling_allowance_mm=float(data.edge_milling_allowance_mm if data.edge_milling_allowance_mm is not None else 30.0),
        expansion_ratio_pct=float(data.expansion_ratio_pct if data.expansion_ratio_pct is not None else 1.0),
    )
    return JSONResponse(content={"status": "success", "data": res})

@app.post("/api/export-hydro-excel")
async def export_hydro_excel(data: ExportHydroRequest = Body(...)):
    """
    Generates and streams formatted Excel engineering calculation sheet for API 5L PSL2 & BOTAŞ
    Mill Hydrostatic Test Pressure, Water Volume, and Inspection Acceptance.
    """
    import re
    from core.hydrostatic_engine import compute_hydrostatic_calc

    project_info = data.project_info or {}
    hydro_data = data.hydro_data or {}
    pipe_info = data.pipe_info or {}
    lang = data.lang or "tr"

    d_v = float(hydro_data.get("d_mm") or pipe_info.get("diameter_mm") or 1219.0)
    t_v = float(hydro_data.get("t_mm") or pipe_info.get("wall_thickness_mm") or 14.30)
    smys_v = float(hydro_data.get("smys_mpa") or 450.0)
    l_v = float(hydro_data.get("pipe_length_m") or 12.0)
    is_botas_v = bool(hydro_data.get("is_botas", True))
    cap_v = float(hydro_data.get("press_cap_bar", 250.0) or 250.0)

    computed = compute_hydrostatic_calc(
        d_mm=d_v,
        t_mm=t_v,
        smys_mpa=smys_v,
        pipe_length_m=l_v,
        is_botas=is_botas_v,
        press_cap_bar=cap_v,
    )
    final_hydro_data = {**hydro_data, **computed}

    excel_file = ExcelExporter.export_hydrostatic_test_report(
        final_hydro_data,
        project_info,
        pipe_info=pipe_info,
        lang=lang
    )

    raw_no = str(project_info.get('project_no', 'HYDRO')).strip()
    safe_no = re.sub(r'[^a-zA-Z0-9_\-\.]', '_', raw_no) if raw_no else 'HYDRO'
    raw_dia = str(pipe_info.get('diameter_inch', f"{d_v:.0f}mm")).replace('"', '').replace("'", "").strip()
    safe_dia = re.sub(r'[^a-zA-Z0-9_\-\.]', '', raw_dia) if raw_dia else '48in'
    if not safe_dia.endswith('in') and not safe_dia.endswith('mm'):
        safe_dia = f"{safe_dia}in"
    filename = f"Hidrostatik_Test_Foyu_{safe_no}_{safe_dia}.xlsx"
    headers = {
        'Content-Disposition': f'attachment; filename="{filename}"'
    }
    return StreamingResponse(
        excel_file,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers=headers
    )

@app.post("/api/hydro-calc")
async def api_hydro_calc(data: HydroCalcRequest = Body(...)):
    """
    API 5L / BOTAŞ hydrostatic test pressure, water volume, and elastic expansion calculation.
    """
    from core.hydrostatic_engine import compute_hydrostatic_calc

    d_mm = data.diameter_mm
    if d_mm is None and data.diameter_inch:
        from core.database import get_pipe_size_by_inch
        ps = get_pipe_size_by_inch(data.diameter_inch)
        d_mm = ps['mm'] if ps else 1219.0
    elif d_mm is None:
        d_mm = 1219.0

    res = compute_hydrostatic_calc(
        float(d_mm),
        float(data.wall_thickness_mm or 14.30),
        smys_mpa=float(data.smys_mpa or 450.0),
        pipe_length_m=float(data.pipe_length_m or 12.0),
        is_botas=bool(data.is_botas),
        press_cap_bar=float(data.press_cap_bar or 250.0),
    )
    return JSONResponse(content={"status": "success", "data": res})


@app.post("/api/export-erw-excel")
async def export_erw_excel_endpoint(data: ExportErwRequest = Body(...)):
    """
    Exports official ERW/HFW Pipe Manufacturing Geometry, Skelp Sizing,
    Flash Trimming Tolerances, and API 5L Clause 10.2.4.3 Flattening Test Report to Excel.
    """
    import re
    from core.erw_engine import ErwEngine

    project_info = data.project_info or {}
    erw_data = data.erw_data or {}
    pipe_info = data.pipe_info or {}
    lang = data.lang or "tr"

    d_val = float(pipe_info.get('diameter_mm') or erw_data.get('diameter_mm') or 323.9)
    t_val = float(pipe_info.get('wall_thickness_mm') or erw_data.get('wall_thickness_mm') or 9.53)
    grade_val = str(pipe_info.get('material_grade') or erw_data.get('material_grade') or 'X52')
    psl_val = str(pipe_info.get('psl_level') or erw_data.get('psl_level') or 'PSL2')
    len_val = float(pipe_info.get('pipe_length_m') or erw_data.get('pipe_length_m') or 12.0)

    computed = ErwEngine.calculate_erw_geometry(
        diameter_mm=d_val,
        wall_thickness_mm=t_val,
        material_grade=grade_val,
        psl_level=psl_val,
        pipe_length_m=len_val
    )
    final_erw_data = {**erw_data, **computed}

    excel_file = ExcelExporter.export_erw_geometry_report(
        project_info,
        final_erw_data,
        pipe_info=pipe_info,
        lang=lang
    )

    raw_no = str(project_info.get('project_no', 'ERW')).strip()
    safe_no = re.sub(r'[^a-zA-Z0-9_\-\.]', '_', raw_no) if raw_no else 'ERW'
    raw_dia = str(pipe_info.get('diameter_inch', f"{d_val:.0f}mm")).replace('"', '').replace("'", "").strip()
    safe_dia = re.sub(r'[^a-zA-Z0-9_\-\.]', '', raw_dia) if raw_dia else '12in'
    if not safe_dia.endswith('in') and not safe_dia.endswith('mm'):
        safe_dia = f"{safe_dia}in"
    filename = f"ERW_Imalat_Yassiltma_Foyu_{safe_no}_{safe_dia}.xlsx"
    headers = {
        'Content-Disposition': f'attachment; filename="{filename}"'
    }
    return StreamingResponse(
        excel_file,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers=headers
    )


@app.post("/api/erw-calc")
async def api_erw_calc(data: ErwCalcRequest = Body(...)):
    """
    ERW / HFW skelp sizing, flash trimming, and API 5L Clause 10.2.4.3 flattening test heights.
    """
    from core.erw_engine import ErwEngine

    d_mm = data.diameter_mm
    if d_mm is None and data.diameter_inch:
        from core.database import get_pipe_size_by_inch
        ps = get_pipe_size_by_inch(data.diameter_inch)
        d_mm = ps['mm'] if ps else 323.9
    elif d_mm is None:
        d_mm = 323.9

    res = ErwEngine.calculate_erw_geometry(
        diameter_mm=float(d_mm),
        wall_thickness_mm=float(data.wall_thickness_mm or 9.53),
        material_grade=str(data.material_grade or "X52"),
        psl_level=str(data.psl_level or "PSL2"),
        pipe_length_m=float(data.pipe_length_m or 12.0)
    )
    return JSONResponse(content={"status": "success", "data": res})


@app.post("/api/bevel-calc")
async def api_bevel_calc(data: BevelCalcRequest = Body(...)):
    """
    Calculates pipe end machining dimensions, bevel groove volume, tolerances,
    out-of-squareness limits, end ovality thresholds, and verifies compliance.
    """
    from core.bevel_engine import BevelEngine

    d_mm = data.diameter_mm
    if d_mm is None and data.diameter_inch:
        from core.database import get_pipe_size_by_inch
        ps = get_pipe_size_by_inch(data.diameter_inch)
        d_mm = ps['mm'] if ps else 1219.0
    elif d_mm is None:
        d_mm = 1219.0

    res = BevelEngine.calculate_bevel_geometry(
        diameter_mm=float(d_mm),
        wall_thickness_mm=float(data.wall_thickness_mm or 14.30),
        material_grade=str(data.material_grade or "X65"),
        standard_code=str(data.standard_code or "BOTAŞ"),
        end_type=str(data.end_type or "BEVEL"),
        bevel_angle_actual=data.bevel_angle_actual,
        root_face_actual=data.root_face_actual,
        out_of_squareness_actual=data.out_of_squareness_actual,
        end_diameter_min_actual=data.end_diameter_min_actual,
        end_diameter_max_actual=data.end_diameter_max_actual,
        pipe_length_m=float(data.pipe_length_m or 12.0)
    )
    return JSONResponse(content={"status": "success", "data": res})


@app.post("/api/export-bevel-excel")
async def export_bevel_excel_endpoint(data: ExportBevelRequest = Body(...)):
    """
    Exports official Pipe End Geometry, Bevel Preparation, Root Face,
    Out-of-Squareness, and End Ovality Inspection Report to Excel.
    """
    import re
    from core.bevel_engine import BevelEngine

    project_info = data.project_info or {}
    bevel_data = data.bevel_data or {}
    pipe_info = data.pipe_info or {}
    lang = data.lang or "tr"

    d_val = float(pipe_info.get('diameter_mm') or bevel_data.get('diameter_mm') or 1219.0)
    t_val = float(pipe_info.get('wall_thickness_mm') or bevel_data.get('wall_thickness_mm') or 14.30)
    grade_val = str(pipe_info.get('material_grade') or bevel_data.get('material_grade') or 'X65')
    std_val = str(pipe_info.get('standard_type') or bevel_data.get('standard_code') or 'BOTAŞ')
    end_val = str(pipe_info.get('end_type') or bevel_data.get('end_type') or 'BEVEL')

    computed = BevelEngine.calculate_bevel_geometry(
        diameter_mm=d_val,
        wall_thickness_mm=t_val,
        material_grade=grade_val,
        standard_code=std_val,
        end_type=end_val,
        bevel_angle_actual=bevel_data.get('bevel_angle_actual'),
        root_face_actual=bevel_data.get('root_face_actual'),
        out_of_squareness_actual=bevel_data.get('out_of_squareness_actual'),
        end_diameter_min_actual=bevel_data.get('end_diameter_min_actual'),
        end_diameter_max_actual=bevel_data.get('end_diameter_max_actual'),
        pipe_length_m=float(bevel_data.get('pipe_length_m') or 12.0)
    )
    final_bevel_data = {**bevel_data, **computed}

    excel_file = ExcelExporter.export_bevel_geometry_report(
        project_info,
        final_bevel_data,
        pipe_info=pipe_info,
        lang=lang
    )

    raw_no = str(project_info.get('project_no', 'BEVEL')).strip()
    safe_no = re.sub(r'[^a-zA-Z0-9_\-\.]', '_', raw_no) if raw_no else 'BEVEL'
    raw_dia = str(pipe_info.get('diameter_inch', f"{d_val:.0f}mm")).replace('"', '').replace("'", "").strip()
    safe_dia = re.sub(r'[^a-zA-Z0-9_\-\.]', '', raw_dia) if raw_dia else '48in'
    if not safe_dia.endswith('in') and not safe_dia.endswith('mm'):
        safe_dia = f"{safe_dia}in"
    filename = f"Boru_Uc_Kaynak_Agzi_Foyu_{safe_no}_{safe_dia}.xlsx"
    headers = {
        'Content-Disposition': f'attachment; filename="{filename}"'
    }
    return StreamingResponse(
        excel_file,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers=headers
    )


@app.post("/api/straightness-calc")
async def api_straightness_calc(data: StraightnessCalcRequest = Body(...)):
    """
    Calculates pipe straightness, full-length sweep/camber, and end straightness deviations
    per API Spec 5L Clause 9.11.3 & Table 12 and BOTAŞ Clauses 5.5, 8.1.2.4.
    """
    from core.straightness_engine import StraightnessEngine

    d_mm = data.diameter_mm
    if d_mm is None and data.diameter_inch:
        from core.database import get_pipe_size_by_inch
        ps = get_pipe_size_by_inch(data.diameter_inch)
        d_mm = ps['mm'] if ps else 1219.0
    elif d_mm is None:
        d_mm = 1219.0

    res = StraightnessEngine.calculate_straightness(
        diameter_mm=float(d_mm),
        wall_thickness_mm=float(data.wall_thickness_mm or 14.30),
        pipe_length_m=float(data.pipe_length_m or 12.0),
        standard_code=str(data.standard_code or "BOTAŞ"),
        material_grade=str(data.material_grade or "X65"),
        manufacturing_process=str(data.manufacturing_process or "SAWH"),
        total_straightness_actual_mm=data.total_straightness_actual_mm,
        end_straightness_left_actual_mm=data.end_straightness_left_actual_mm,
        end_straightness_right_actual_mm=data.end_straightness_right_actual_mm,
    )
    return JSONResponse(content={"status": "success", "data": res})


@app.post("/api/export-straightness-excel")
async def export_straightness_excel_endpoint(data: ExportStraightnessRequest = Body(...)):
    """
    Exports official Pipe Straightness, Full-Length Sweep / Camber, and End Straightness
    Inspection Report to Excel.
    """
    import re
    from core.straightness_engine import StraightnessEngine

    project_info = data.project_info or {}
    straightness_data = data.straightness_data or {}
    pipe_info = data.pipe_info or {}
    lang = data.lang or "tr"

    d_val = float(pipe_info.get('diameter_mm') or straightness_data.get('diameter_mm') or 1219.0)
    t_val = float(pipe_info.get('wall_thickness_mm') or straightness_data.get('wall_thickness_mm') or 14.30)
    l_val = float(pipe_info.get('pipe_length_m') or straightness_data.get('pipe_length_m') or 12.0)
    grade_val = str(pipe_info.get('material_grade') or straightness_data.get('material_grade') or 'X65')
    proc_val = str(pipe_info.get('manufacturing_process') or straightness_data.get('manufacturing_process') or 'SAWH')
    std_val = str(pipe_info.get('standard_type') or straightness_data.get('standard_code') or 'BOTAŞ')

    computed = StraightnessEngine.calculate_straightness(
        diameter_mm=d_val,
        wall_thickness_mm=t_val,
        pipe_length_m=l_val,
        standard_code=std_val,
        material_grade=grade_val,
        manufacturing_process=proc_val,
        total_straightness_actual_mm=straightness_data.get('total_straightness_actual_mm'),
        end_straightness_left_actual_mm=straightness_data.get('end_straightness_left_actual_mm'),
        end_straightness_right_actual_mm=straightness_data.get('end_straightness_right_actual_mm'),
    )
    final_straightness_data = {**straightness_data, **computed}

    excel_file = ExcelExporter.export_straightness_report(
        project_info,
        final_straightness_data,
        pipe_info=pipe_info,
        lang=lang
    )

    raw_no = str(project_info.get('project_no', 'STR')).strip()
    safe_no = re.sub(r'[^a-zA-Z0-9_\-\.]', '_', raw_no) if raw_no else 'STR'
    raw_dia = str(pipe_info.get('diameter_inch', f"{d_val:.0f}mm")).replace('"', '').replace("'", "").strip()
    safe_dia = re.sub(r'[^a-zA-Z0-9_\-\.]', '', raw_dia) if raw_dia else '48in'
    if not safe_dia.endswith('in') and not safe_dia.endswith('mm'):
        safe_dia = f"{safe_dia}in"
    filename = f"Boru_Duzluk_Sapma_Foyu_{safe_no}_{safe_dia}.xlsx"
    headers = {
        'Content-Disposition': f'attachment; filename="{filename}"'
    }
    return StreamingResponse(
        excel_file,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers=headers
    )


@app.post("/api/derating-calc")
async def api_derating_calc(data: DeratingCalcRequest = Body(...)):
    """
    Calculates wall thickness underflow (minus tolerance), Barlow design pressure derating,
    and hydrostatic hoop stress jump per API Spec 5L Table 11 & ASME B31.8 Section 841.1.
    """
    from core.derating_engine import DeratingEngine

    d_mm = data.diameter_mm
    if d_mm is None and data.diameter_inch:
        from core.database import get_pipe_size_by_inch
        ps = get_pipe_size_by_inch(data.diameter_inch)
        d_mm = ps['mm'] if ps else 1219.0
    elif d_mm is None:
        d_mm = 1219.0

    res = DeratingEngine.calculate_derating(
        diameter_mm=float(d_mm),
        wall_thickness_mm=float(data.wall_thickness_mm or 14.30),
        material_grade=str(data.material_grade or "X65"),
        manufacturing_process=str(data.manufacturing_process or "SAWH"),
        standard_code=str(data.standard_code or "BOTAŞ"),
        design_factor_f=float(data.design_factor_f if data.design_factor_f is not None else 0.72),
        corrosion_allowance_mm=float(data.corrosion_allowance_mm if data.corrosion_allowance_mm is not None else 0.0),
        smys_mpa=data.smys_mpa,
        design_pressure_bar=data.design_pressure_bar,
        hydro_test_pressure_bar=data.hydro_test_pressure_bar,
        pipe_length_m=float(data.pipe_length_m or 12.0),
        actual_measured_thickness_mm=data.actual_measured_thickness_mm,
    )
    return JSONResponse(content={"status": "success", "data": res})


@app.post("/api/export-derating-excel")
async def export_derating_excel_endpoint(data: ExportDeratingRequest = Body(...)):
    """
    Exports official Wall Thickness Underflow (Minus Tolerance), Barlow Design Pressure
    Derating, and Hydrostatic Hoop Stress Verification Report to Excel.
    """
    import re
    from core.derating_engine import DeratingEngine

    project_info = data.project_info or {}
    derating_data = data.derating_data or {}
    pipe_info = data.pipe_info or {}
    lang = data.lang or "tr"

    d_val = float(pipe_info.get('diameter_mm') or derating_data.get('diameter_mm') or 1219.0)
    t_val = float(pipe_info.get('wall_thickness_mm') or derating_data.get('wall_thickness_mm') or 14.30)
    grade_val = str(pipe_info.get('material_grade') or derating_data.get('material_grade') or 'X65')
    proc_val = str(pipe_info.get('manufacturing_process') or derating_data.get('manufacturing_process') or 'SAWH')
    std_val = str(pipe_info.get('standard_type') or derating_data.get('standard_code') or 'BOTAŞ')
    l_val = float(pipe_info.get('pipe_length_m') or derating_data.get('pipe_length_m') or 12.0)
    f_val = float(derating_data.get('design_factor_f') if derating_data.get('design_factor_f') is not None else 0.72)
    ca_val = float(derating_data.get('corrosion_allowance_mm') if derating_data.get('corrosion_allowance_mm') is not None else 0.0)

    computed = DeratingEngine.calculate_derating(
        diameter_mm=d_val,
        wall_thickness_mm=t_val,
        material_grade=grade_val,
        manufacturing_process=proc_val,
        standard_code=std_val,
        design_factor_f=f_val,
        corrosion_allowance_mm=ca_val,
        smys_mpa=derating_data.get('smys_mpa'),
        design_pressure_bar=derating_data.get('design_pressure_bar'),
        hydro_test_pressure_bar=derating_data.get('hydro_test_pressure_bar'),
        pipe_length_m=l_val,
        actual_measured_thickness_mm=derating_data.get('actual_measured_thickness_mm'),
    )
    final_derating_data = {**derating_data, **computed}

    excel_file = ExcelExporter.export_derating_report(
        project_info,
        final_derating_data,
        pipe_info=pipe_info,
        lang=lang
    )

    raw_no = str(project_info.get('project_no', 'DERATING')).strip()
    safe_no = re.sub(r'[^a-zA-Z0-9_\-\.]', '_', raw_no) if raw_no else 'DERATING'
    raw_dia = str(pipe_info.get('diameter_inch', f"{d_val:.0f}mm")).replace('"', '').replace("'", "").strip()
    safe_dia = re.sub(r'[^a-zA-Z0-9_\-\.]', '', raw_dia) if raw_dia else '48in'
    if not safe_dia.endswith('in') and not safe_dia.endswith('mm'):
        safe_dia = f"{safe_dia}in"
    filename = f"Et_Kalinligi_Indirgeme_Foyu_{safe_no}_{safe_dia}.xlsx"
    headers = {
        'Content-Disposition': f'attachment; filename="{filename}"'
    }
    return StreamingResponse(
        excel_file,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers=headers
    )


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
        demo_meta = UnlimitedOCREngine.detect_itp_metadata("", extracted, "Demo_BOTAŞ_ITP.pdf")
        audit_res = ITPAuditEngine.audit_itp(extracted, pipe_config)
        return JSONResponse(content={
            "status": "success",
            "is_fallback": False,
            "source": "Demo ITP Sample Data",
            "extracted_items": extracted,
            "detected_metadata": demo_meta,
            "effective_config": pipe_config,
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
    detected_meta = parse_result.get("detected_metadata", {})

    # If pipe_config has unset/default values, enrich with detected metadata
    effective_config = dict(pipe_config)
    for k, det_k in (
        ("standard_type", "detected_standard"),
        ("scope_mode", "detected_scope_mode"),
        ("material_grade", "detected_grade"),
        ("manufacturing_process", "detected_process"),
        ("psl_level", "detected_psl"),
        ("diameter_mm", "detected_diameter_mm"),
        ("diameter_inch", "detected_diameter_inch"),
        ("wall_thickness_mm", "detected_wall_thickness_mm"),
        ("delivery_condition", "detected_delivery_condition"),
    ):
        if det_k in detected_meta and (k not in pipe_config or pipe_config.get(k) in (None, "", "auto", "default")):
            effective_config[k] = detected_meta[det_k]

    # Handle coating-only scope: filter items to coating-related tests only
    scope_mode = effective_config.get("scope_mode", detected_meta.get("detected_scope_mode", "BARE_PIPE_ONLY"))
    if scope_mode == "COATING_ONLY":
        # Filter items to only coating-related tests
        coating_keywords = ("kaplama", "kumlama", "holiday", "peel", "soyulma", "darbe", "indentation", "katodik", "cutback", "cut back", "fbe", "3lpe", "hdpe", "boyasız", "yama")
        extracted_items = [it for it in extracted_items if any(kw in (it.get("test_name") or "").lower() for kw in coating_keywords)]
        # Also add detected coating items from metadata
        effective_config["scope_mode"] = "COATING_ONLY"

    # Multi-variant detection: same diameter with several wall thicknesses (e.g. 914.4×11.10/12.70/15.90/17.50)
    scope_variants = detected_meta.get("scope_variants", []) if isinstance(detected_meta, dict) else []
    variant_audits: list = []
    if scope_variants and len(scope_variants) > 1:
        # Use detected scope table to audit each pipe geometry separately
        for var in scope_variants:
            var_cfg = dict(effective_config)
            var_cfg["diameter_mm"] = var.get("diameter_mm", effective_config.get("diameter_mm"))
            var_cfg["diameter_inch"] = var.get("diameter_inch", effective_config.get("diameter_inch"))
            var_cfg["wall_thickness_mm"] = var.get("wall_thickness_mm", effective_config.get("wall_thickness_mm"))
            var_cfg["material_grade"] = var.get("material_grade", effective_config.get("material_grade"))
            var_audit = ITPAuditEngine.audit_itp(extracted_items, var_cfg)
            variant_audits.append({"pipe_config": var_cfg, "audit_result": var_audit})
        # Primary audit remains first variant for backward compat
        audit_res = variant_audits[0]["audit_result"] if variant_audits else ITPAuditEngine.audit_itp(extracted_items, effective_config)
    else:
        audit_res = ITPAuditEngine.audit_itp(extracted_items, effective_config)

    # Persist in current project state if available
    try:
        current_proj = ProjectManager.get_current_project()
        if current_proj:
            current_proj["latest_itp_audit"] = {
                "source": filename,
                "engine": parse_result.get("engine", "Unlimited-OCR"),
                "detected_metadata": detected_meta,
                "effective_config": effective_config,
                "audit_result": audit_res,
                "variant_audits": variant_audits
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
        "detected_metadata": detected_meta,
        "effective_config": effective_config,
        "audit_result": audit_res,
        "variant_audits": variant_audits,
        "scope_variants": scope_variants
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

@app.post("/api/itp/export-audit-pdf")
async def export_itp_audit_pdf(data: Dict[str, Any] = Body(...)):
    """
    Generates and downloads publication-grade PDF audit discrepancy & compliance certificate.
    """
    audit_data = data.get("audit_result", {})
    lang = data.get("lang", "tr")
    pdf_stream = PDFExporter.export_itp_audit_pdf(audit_data, lang)

    pipe = audit_data.get("pipe_summary", {})
    d_inch = str(pipe.get("diameter_inch", "48in")).replace('"', '').replace("'", "").strip()
    grade = pipe.get("material_grade", "X65")
    filename = f"ITP_Audit_Report_{d_inch}_{grade}_API5L_BOTAS.pdf"

    return StreamingResponse(
        pdf_stream,
        media_type="application/pdf",
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

