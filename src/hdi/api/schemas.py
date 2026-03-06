"""Pydantic response models for API type safety."""

from __future__ import annotations

from typing import Any, Optional

from pydantic import BaseModel, Field


# ── Envelope ─────────────────────────────────────────────────────────────────

class APIResponse(BaseModel):
    status: str = "success"
    meta: dict[str, Any] = Field(default_factory=dict)
    data: Any = None


class ErrorResponse(BaseModel):
    status: str = "error"
    message: str
    detail: Optional[str] = None


# ── Metadata ─────────────────────────────────────────────────────────────────

class CountryInfo(BaseModel):
    iso3: str
    name: str
    who_region: Optional[str] = None
    wb_income: Optional[str] = None


class IndicatorInfo(BaseModel):
    code: str
    name: str
    description: Optional[str] = None
    dimension: Optional[str] = None
    unit: Optional[str] = None


# ── Dimension 1: Spatiotemporal ──────────────────────────────────────────────

class SpatiotemporalFeature(BaseModel):
    iso3: str
    name: Optional[str] = None
    value: Optional[float] = None
    year: int
    geometry: Optional[dict] = None  # GeoJSON geometry


class TrendPoint(BaseModel):
    year: int
    value: float
    trend_direction: Optional[str] = None
    p_value: Optional[float] = None


class ForecastPoint(BaseModel):
    year: int
    predicted: float
    ci_lower: float
    ci_upper: float


class LISACluster(BaseModel):
    iso3: str
    local_i: float
    p_value: float
    cluster: str  # HH, HL, LH, LL, Not Significant


# ── Dimension 2: Risk Attribution ────────────────────────────────────────────

class PAFDecomposition(BaseModel):
    iso3: str
    year: int
    risk_factor: str
    disease: Optional[str] = None
    paf: float
    attributable_burden: Optional[float] = None


class ShapleyValue(BaseModel):
    risk_factor: str
    shapley_value: float
    shapley_pct: float


class ScenarioTrajectory(BaseModel):
    scenario: str
    country: str
    year: int
    total_daly: float
    cvd_daly: Optional[float] = None
    resp_daly: Optional[float] = None
    cancer_daly: Optional[float] = None
    ci_lower: Optional[float] = None
    ci_upper: Optional[float] = None


# ── Dimension 3: Resource Allocation ─────────────────────────────────────────

class ResourceGap(BaseModel):
    iso3: str
    year: int
    actual_expenditure: Optional[float] = None
    theoretical_need: Optional[float] = None
    gap: Optional[float] = None
    gap_grade: str  # A through E


class EfficiencyScore(BaseModel):
    iso3: str
    year: int
    efficiency: float
    quadrant: str
    input_index: Optional[float] = None
    output_index: Optional[float] = None


class OptimalAllocation(BaseModel):
    iso3: str
    current: float
    optimal: float
    change: float
    change_pct: float


# ── Composite: GHRI ──────────────────────────────────────────────────────────

class GHRIScore(BaseModel):
    iso3: str
    year: Optional[int] = None
    ghri: float
    ghri_rank: int
    disease_burden: Optional[float] = None
    risk_factor_control: Optional[float] = None
    health_system_capacity: Optional[float] = None
    socioeconomic_foundation: Optional[float] = None
    resilience_equity: Optional[float] = None
    rank_lo: Optional[int] = None
    rank_hi: Optional[int] = None
