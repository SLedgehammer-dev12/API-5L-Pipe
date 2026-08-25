"""
Pydantic request/response schemas for API 5L Pipe QA/QC & Design Suite.

Adds input validation so malformed requests fail fast with 422 instead of
crashing with a 500 inside the calculation engines.
"""

from typing import Optional, List
from pydantic import BaseModel, Field, field_validator, ConfigDict
from core.database import API_5L_SMYS_TABLE

KNOWN_GRADES = set(API_5L_SMYS_TABLE.keys())

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

    @field_validator("design_pressure_bar", "wall_thickness_mm")
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


class ReportRequest(BaseModel):
    model_config = ConfigDict(extra="allow")
    project_info: dict = Field(default_factory=dict)
    pipes: List[PipeInput] = Field(default_factory=list)
    lang: str = "tr"
    verification: Optional[dict] = None
