"""
Pydantic request/response schemas for API 5L Pipe QA/QC & Design Suite.

Adds input validation so malformed requests fail fast with 422 instead of
crashing with a 500 inside the calculation engines.
"""

from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator

from core.database import API_5L_PSL1_SMYS_TABLE, API_5L_SMYS_TABLE

KNOWN_GRADES = set(API_5L_SMYS_TABLE.keys()) | set(API_5L_PSL1_SMYS_TABLE.keys())
KNOWN_DELIVERIES = {"R", "N", "Q", "M"}

# Manufacturing processes recognized by the engine (case-insensitive match).
KNOWN_PROCESSES = {
    "SAWH", "SAWL", "ERW", "HFW", "ERW HFW", "LSAW", "SMLS",
    "COW", "COWL", "COWH", "EW", "LW",
}


class PipeInput(BaseModel):
    """A single pipe column in the acceptance matrix."""

    model_config = ConfigDict(extra="allow")

    id: Optional[str] = ""
    diameter_inch: str = "48\""
    diameter_mm: Optional[float] = None
    wall_thickness_mm: Optional[float] = None
    design_factor_str: str = "0.72 (Hat)"
    material_grade: Optional[str] = "X65"
    manufacturing_process: str = "SAWH"
    standard_type: str = "BOTAŞ"
    design_pressure_bar: Optional[float] = None
    operating_pressure_bar: Optional[float] = None
    psl_level: Optional[str] = "PSL2"
    delivery_condition: Optional[str] = "M"

    @field_validator("psl_level")
    @classmethod
    def _check_psl(cls, v):
        if v is None or str(v).strip() == "":
            return v
        s = str(v).upper().strip()
        if s not in ("PSL1", "PSL2"):
            raise ValueError("psl_level must be 'PSL1' or 'PSL2'")
        return s

    @field_validator("delivery_condition")
    @classmethod
    def _check_delivery(cls, v):
        if v is None or str(v).strip() == "":
            return v
        s = str(v).upper().strip()
        if s not in KNOWN_DELIVERIES:
            raise ValueError(f"delivery_condition must be one of {sorted(KNOWN_DELIVERIES)}")
        return s

    @field_validator("material_grade")
    @classmethod
    def _check_grade(cls, v):
        if v is None or str(v).strip() == "":
            return v  # allowed: engine auto-picks default in BOTAŞ mode
        g = str(v).upper().strip()
        if g not in KNOWN_GRADES:
            raise ValueError(
                f"Unknown material grade '{v}'. Known grades: {sorted(KNOWN_GRADES)}"
            )
        return g

    @field_validator("design_pressure_bar", "operating_pressure_bar", "wall_thickness_mm")
    @classmethod
    def _check_non_negative(cls, v):
        if v is not None and v < 0:
            raise ValueError("pressure and thickness must be >= 0")
        return v

    @field_validator("manufacturing_process")
    @classmethod
    def _check_process(cls, v):
        if v is None or str(v).strip() == "":
            return v
        p = str(v).strip()
        # Allow free-form process strings; normalize spacing only.
        return p


class CalculateRequest(BaseModel):
    model_config = ConfigDict(extra="allow")
    pipes: List[PipeInput] = Field(default_factory=list)
    standard_type: str = "BOTAŞ"


class ProjectInfoInput(BaseModel):
    model_config = ConfigDict(extra="allow")
    project_name: str = ""
    project_no: str = ""
    standard: str = "BOTAŞ Şartnamesi"
    language: str = "tr"


class ExportRequest(BaseModel):
    model_config = ConfigDict(extra="allow")
    project_info: dict = Field(default_factory=dict)
    pipes: List[PipeInput] = Field(default_factory=list)
    lang: str = "tr"


class ExportVerificationRequest(BaseModel):
    model_config = ConfigDict(extra="allow")
    project_info: dict = Field(default_factory=dict)
    verification: dict = Field(default_factory=dict)
    lang: str = "tr"


class ExportWallThicknessRequest(BaseModel):
    model_config = ConfigDict(extra="allow")
    project_info: dict = Field(default_factory=dict)
    calculation_data: dict = Field(default_factory=dict)
    lang: str = "tr"


class ExportSawhRequest(BaseModel):
    model_config = ConfigDict(extra="allow")
    project_info: dict = Field(default_factory=dict)
    sawh_data: dict = Field(default_factory=dict)
    pipe_info: Optional[dict] = Field(default_factory=dict)
    lang: str = "tr"


class ExportSawlRequest(BaseModel):
    model_config = ConfigDict(extra="allow")
    project_info: dict = Field(default_factory=dict)
    sawl_data: dict = Field(default_factory=dict)
    pipe_info: Optional[dict] = Field(default_factory=dict)
    lang: str = "tr"


class ExportHydroRequest(BaseModel):
    model_config = ConfigDict(extra="allow")
    project_info: dict = Field(default_factory=dict)
    hydro_data: dict = Field(default_factory=dict)
    pipe_info: Optional[dict] = Field(default_factory=dict)
    lang: str = "tr"


class ExportErwRequest(BaseModel):
    model_config = ConfigDict(extra="allow")
    project_info: dict = Field(default_factory=dict)
    erw_data: dict = Field(default_factory=dict)
    pipe_info: Optional[dict] = Field(default_factory=dict)
    lang: str = "tr"


class ExportBevelRequest(BaseModel):
    model_config = ConfigDict(extra="allow")
    project_info: dict = Field(default_factory=dict)
    bevel_data: dict = Field(default_factory=dict)
    pipe_info: Optional[dict] = Field(default_factory=dict)
    lang: str = "tr"


class ExportStraightnessRequest(BaseModel):
    model_config = ConfigDict(extra="allow")
    project_info: dict = Field(default_factory=dict)
    straightness_data: dict = Field(default_factory=dict)
    pipe_info: Optional[dict] = Field(default_factory=dict)
    lang: str = "tr"


class ExportDeratingRequest(BaseModel):
    model_config = ConfigDict(extra="allow")
    project_info: dict = Field(default_factory=dict)
    derating_data: dict = Field(default_factory=dict)
    pipe_info: Optional[dict] = Field(default_factory=dict)
    lang: str = "tr"


class ReportRequest(BaseModel):
    model_config = ConfigDict(extra="allow")
    project_info: dict = Field(default_factory=dict)
    pipes: List[PipeInput] = Field(default_factory=list)
    lang: str = "tr"
    verification: Optional[dict] = None


class VerificationRequest(BaseModel):
    model_config = ConfigDict(extra="allow")
    pipe_config: dict = Field(default_factory=dict)
    actual_data: dict = Field(default_factory=dict)


class WallThicknessRequest(BaseModel):
    model_config = ConfigDict(extra="allow")
    diameter_inch: str = '4"'
    material_grade: str = "X65"
    design_pressure_bar: float = 75.0
    design_factor_f: float = 0.72
    longitudinal_joint_factor_e: float = 1.0
    temperature_derating_factor_t: float = 1.0
    corrosion_allowance_mm: float = 0.0
    location_type: str = "Pipeline"
    standard_code: str = "BOTAŞ"
    manufacturing_process: str = "SAWH"
    apply_negative_tolerance: bool = True
    manual_negative_tolerance_percent: Optional[float] = None
    psl_level: str = "PSL2"


class ITPManualAuditRequest(BaseModel):
    model_config = ConfigDict(extra="allow")
    pipe_config: dict = Field(default_factory=dict)
    uploaded_items: List[dict] = Field(default_factory=list)


class TestPlanRequest(BaseModel):
    model_config = ConfigDict(extra="allow")
    diameter_inch: str = '48"'
    diameter_mm: Optional[float] = None
    wall_thickness_mm: Optional[float] = 14.30
    material_grade: str = "X65"
    manufacturing_process: str = "SAWH"
    standard_type: str = "BOTAŞ"
    psl_level: str = "PSL2"
    design_factor_str: str = "0.72 (Hat)"
    design_pressure_bar: float = 75.0
    delivery_condition: str = "M"


class SawhStripRequest(BaseModel):
    model_config = ConfigDict(extra="allow")
    diameter_mm: Optional[float] = None
    diameter_inch: Optional[str] = None
    strip_width_mm: Optional[float] = None
    helix_angle_deg: Optional[float] = None
    wall_thickness_mm: Optional[float] = 0.0
    edge_milling_allowance_mm: Optional[float] = 15.0
    coil_length_m: Optional[float] = 800.0
    pipe_length_m: Optional[float] = 12.0
    min_skelp_end_distance_mm: Optional[float] = 300.0


class SawlCalcRequest(BaseModel):
    model_config = ConfigDict(extra="allow")
    diameter_mm: Optional[float] = None
    diameter_inch: Optional[str] = None
    wall_thickness_mm: Optional[float] = 14.30
    pipe_length_m: Optional[float] = 12.0
    edge_milling_allowance_mm: Optional[float] = 30.0
    expansion_ratio_pct: Optional[float] = 1.0


class HydroCalcRequest(BaseModel):
    model_config = ConfigDict(extra="allow")
    diameter_mm: Optional[float] = None
    diameter_inch: Optional[str] = None
    wall_thickness_mm: Optional[float] = 14.30
    smys_mpa: Optional[float] = 450.0
    pipe_length_m: Optional[float] = 12.0
    is_botas: bool = True
    press_cap_bar: Optional[float] = 250.0


class ErwCalcRequest(BaseModel):
    model_config = ConfigDict(extra="allow")
    diameter_mm: Optional[float] = None
    diameter_inch: Optional[str] = None
    wall_thickness_mm: Optional[float] = 9.53
    material_grade: Optional[str] = "X52"
    psl_level: Optional[str] = "PSL2"
    pipe_length_m: Optional[float] = 12.0


class BevelCalcRequest(BaseModel):
    model_config = ConfigDict(extra="allow")
    diameter_mm: Optional[float] = None
    diameter_inch: Optional[str] = None
    wall_thickness_mm: Optional[float] = 14.30
    material_grade: Optional[str] = "X65"
    standard_code: Optional[str] = "BOTAŞ"
    end_type: Optional[str] = "BEVEL"
    bevel_angle_actual: Optional[float] = None
    root_face_actual: Optional[float] = None
    out_of_squareness_actual: Optional[float] = None
    end_diameter_min_actual: Optional[float] = None
    end_diameter_max_actual: Optional[float] = None
    pipe_length_m: Optional[float] = 12.0


class StraightnessCalcRequest(BaseModel):
    model_config = ConfigDict(extra="allow")
    diameter_mm: Optional[float] = None
    diameter_inch: Optional[str] = None
    wall_thickness_mm: Optional[float] = 14.30
    pipe_length_m: Optional[float] = 12.0
    material_grade: Optional[str] = "X65"
    manufacturing_process: Optional[str] = "SAWH"
    standard_code: Optional[str] = "BOTAŞ"
    total_straightness_actual_mm: Optional[float] = None
    end_straightness_left_actual_mm: Optional[float] = None
    end_straightness_right_actual_mm: Optional[float] = None


class DeratingCalcRequest(BaseModel):
    model_config = ConfigDict(extra="allow")
    diameter_mm: Optional[float] = None
    diameter_inch: Optional[str] = None
    wall_thickness_mm: Optional[float] = 14.30
    material_grade: Optional[str] = "X65"
    manufacturing_process: Optional[str] = "SAWH"
    standard_code: Optional[str] = "BOTAŞ"
    design_factor_f: Optional[float] = 0.72
    corrosion_allowance_mm: Optional[float] = 0.0
    smys_mpa: Optional[float] = None
    design_pressure_bar: Optional[float] = None
    hydro_test_pressure_bar: Optional[float] = None
    pipe_length_m: Optional[float] = 12.0
    actual_measured_thickness_mm: Optional[float] = None


