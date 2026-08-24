"""
Main FastAPI Web Application for API 5L PSL2 & BOTAŞ Pipe QA/QC & Design Suite.
"""

from fastapi import FastAPI, Request, Body
from fastapi.responses import HTMLResponse, StreamingResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import os
import sys
from typing import Dict, Any

from core.pipe_qaqc_engine import PipeQAQCEngine
from core.verification_engine import PipeVerificationEngine
from core.wall_thickness_engine import WallThicknessEngine
from core.project_manager import ProjectManager
from core.excel_exporter import ExcelExporter
from core.database import API_5L_SMYS_TABLE, PIPE_SIZES_TABLE, normalize_design_factor
from core.i18n import TRANSLATIONS, get_text
from version import __version__, __app_name__

# Resolve base directory (compatible with PyInstaller one-file and normal runtime)
BASE_DIR = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
STATIC_DIR = os.path.join(BASE_DIR, "static")
TEMPLATES_DIR = os.path.join(BASE_DIR, "templates")

app = FastAPI(
    title=__app_name__,
    description="Professional Engineering Software for Pipe QA/QC, Factory Acceptance Testing and Wall Thickness Design",
    version=__version__
)

# Ensure static and template directories exist
os.makedirs(os.path.join(STATIC_DIR, "css"), exist_ok=True)
os.makedirs(os.path.join(STATIC_DIR, "js"), exist_ok=True)
os.makedirs(os.path.join(STATIC_DIR, "img"), exist_ok=True)
os.makedirs(TEMPLATES_DIR, exist_ok=True)

app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")
templates = Jinja2Templates(directory=TEMPLATES_DIR)

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
async def calculate_matrix(data: Dict[str, Any] = Body(...)):
    """
    Calculates full QA/QC acceptance matrix for a list of pipes.
    """
    pipes = data.get("pipes", [])
    standard_type = data.get("standard_type", "BOTAŞ")
    results = []

    for p in pipes:
        res = PipeQAQCEngine.calculate_pipe_qc(
            diameter_inch=p.get("diameter_inch", "48\""),
            diameter_mm=p.get("diameter_mm"),
            wall_thickness_mm=p.get("wall_thickness_mm"),
            design_factor_str=p.get("design_factor_str", "0.72 (Hat)"),
            material_grade=p.get("material_grade", "X65"),
            manufacturing_process=p.get("manufacturing_process", "SAWH"),
            standard_type=p.get("standard_type", standard_type),
            design_pressure_bar=p.get("design_pressure_bar", 75.0)
        )
        # Preserve client pipe ID
        res['id'] = p.get('id', '')
        results.append(res)

    return JSONResponse(content={"status": "success", "data": results})

@app.post("/api/verify")
async def verify_pipe(data: Dict[str, Any] = Body(...)):
    """
    Verifies actual inspection test data against API 5L and BOTAŞ specifications (PASS/FAIL).
    """
    pipe_config = data.get("pipe_config", {})
    actual_data = data.get("actual_data", {})
    
    result = PipeVerificationEngine.verify_pipe_test_results(pipe_config, actual_data)
    return JSONResponse(content={"status": "success", "verification": result})

@app.post("/api/wall-thickness")
async def calculate_wall_thickness(data: Dict[str, Any] = Body(...)):
    """
    Calculates required pipe wall thickness across BOTAŞ, ASME B31.8/B31.4, or ASME B31.3
    and selects standard nominal thickness from ASME B36.10M or ASME B36.19M.
    """
    res = WallThicknessEngine.calculate_wall_thickness(
        diameter_inch=data.get("diameter_inch", "4\""),
        material_grade=data.get("material_grade", "X65"),
        design_pressure_bar=float(data.get("design_pressure_bar", 75.0)),
        design_factor_f=float(data.get("design_factor_f", 0.72)),
        longitudinal_joint_factor_e=float(data.get("longitudinal_joint_factor_e", 1.0)),
        temperature_derating_factor_t=float(data.get("temperature_derating_factor_t", 1.0)),
        corrosion_allowance_mm=float(data.get("corrosion_allowance_mm", 0.0)),
        location_type=data.get("location_type", "Pipeline"),
        standard_code=data.get("standard_code", "BOTAŞ"),
        manufacturing_process=data.get("manufacturing_process", "SAWH"),
        apply_negative_tolerance=bool(data.get("apply_negative_tolerance", True)),
        manual_negative_tolerance_percent=float(data.get("manual_negative_tolerance_percent", 12.5)),
        psl_level=data.get("psl_level", "PSL2")
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

@app.get("/api/botas-lookup")
async def lookup_botas_specs(diameter_inch: str, factor: str = "0.72 (Hat)"):
    """
    Returns BOTAŞ standard material and wall thickness for a given diameter and factor.
    """
    pipe_size = None
    for p in PIPE_SIZES_TABLE:
        clean1 = p['inch'].replace('\"', '').replace("'", '').strip()
        clean2 = diameter_inch.replace('\"', '').replace("'", '').strip()
        if clean1 == clean2 or p['inch'] == diameter_inch:
            pipe_size = p
            break

    if not pipe_size:
        return JSONResponse(content={"status": "not_found", "material": "X65", "thickness": 14.30})

    factor_key = normalize_design_factor(factor)

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
async def export_excel(data: Dict[str, Any] = Body(...)):
    """
    Generates and streams formatted Excel spreadsheet.
    """
    project_info = data.get("project_info", {})
    pipes_input = data.get("pipes", [])
    lang = data.get("lang", "tr")

    # Calculate results
    pipes_calculated = []
    for p in pipes_input:
        res = PipeQAQCEngine.calculate_pipe_qc(
            diameter_inch=p.get("diameter_inch", "48\""),
            diameter_mm=p.get("diameter_mm"),
            wall_thickness_mm=p.get("wall_thickness_mm"),
            design_factor_str=p.get("design_factor_str", "0.72 (Hat)"),
            material_grade=p.get("material_grade", "X65"),
            manufacturing_process=p.get("manufacturing_process", "SAWH"),
            standard_type=p.get("standard_type", "BOTAŞ"),
            design_pressure_bar=p.get("design_pressure_bar", 75.0)
        )
        pipes_calculated.append(res)

    excel_file = ExcelExporter.export_matrix_to_excel(project_info, pipes_calculated, lang=lang)
    
    filename = f"Boru_Kabul_Raporu_{project_info.get('project_no', 'API5L')}.xlsx"
    headers = {
        'Content-Disposition': f'attachment; filename="{filename}"'
    }
    return StreamingResponse(
        excel_file,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers=headers
    )

@app.post("/api/test-plan")
async def get_test_plan(data: Dict[str, Any] = Body(...)):
    """
    Returns the API 5L PSL2 inspection & test plan (sampling frequency,
    location and specimen dimensions) for a given pipe configuration.
    """
    from core.test_plan import get_test_plan
    pipe_config = data.get("pipe_config", {})
    plan = get_test_plan(pipe_config)
    return JSONResponse(content={"status": "success", "test_plan": plan})

@app.post("/api/report-view", response_class=HTMLResponse)
async def generate_html_report(request: Request, data: Dict[str, Any] = Body(...)):
    """
    Renders printable official inspection certificate / FAT report.
    """
    project_info = data.get("project_info", {})
    pipes_input = data.get("pipes", [])
    lang = data.get("lang", "tr")
    verification = data.get("verification", None)

    pipes_calculated = []
    for p in pipes_input:
        res = PipeQAQCEngine.calculate_pipe_qc(
            diameter_inch=p.get("diameter_inch", "48\""),
            diameter_mm=p.get("diameter_mm"),
            wall_thickness_mm=p.get("wall_thickness_mm"),
            design_factor_str=p.get("design_factor_str", "0.72 (Hat)"),
            material_grade=p.get("material_grade", "X65"),
            manufacturing_process=p.get("manufacturing_process", "SAWH"),
            standard_type=p.get("standard_type", "BOTAŞ"),
            design_pressure_bar=p.get("design_pressure_bar", 75.0)
        )
        pipes_calculated.append(res)

    # API 5L inspection & test plan for the first pipe (sampling info)
    from core.test_plan import get_test_plan
    test_plan = []
    if pipes_input:
        test_plan = get_test_plan(pipes_input[0])

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
