"""Dimension 1 endpoints: spatiotemporal analysis, trends, forecasts."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Optional

from fastapi import APIRouter, Query

from hdi.api.schemas import APIResponse
from hdi.config import API_OUTPUT

router = APIRouter(tags=["dimension1"])


def _load_json(path: Path) -> dict | list:
    if path.exists():
        with open(path) as f:
            return json.load(f)
    return {"status": "error", "message": f"Data not found: {path.name}"}


@router.get("/dim1/spatiotemporal", response_model=APIResponse)
async def get_spatiotemporal(
    disease_group: Optional[str] = Query(None),
    year: Optional[int] = Query(None),
    metric: str = Query("daly_rate"),
):
    """Get spatiotemporal disease burden data (GeoJSON)."""
    filename = f"spatiotemporal_{metric}_{year}.json" if year else "spatiotemporal_latest.json"
    return _load_json(API_OUTPUT / "dim1" / filename)


@router.get("/dim1/trends", response_model=APIResponse)
async def get_trends(
    country: Optional[str] = Query(None),
    disease_group: Optional[str] = Query(None),
):
    """Get trend analysis results (Mann-Kendall, joinpoints)."""
    data = _load_json(API_OUTPUT / "dim1" / "trends.json")
    if isinstance(data, dict) and "data" in data:
        records = data["data"]
        if country:
            records = [r for r in records if r.get("iso3") == country]
        if disease_group:
            records = [r for r in records if r.get("disease_group") == disease_group]
        data["data"] = records
        data["meta"]["record_count"] = len(records)
    return data


@router.get("/dim1/forecasts", response_model=APIResponse)
async def get_forecasts(
    country: Optional[str] = Query(None),
    indicator: Optional[str] = Query(None),
    horizon: int = Query(7),
):
    """Get time series forecasts with confidence intervals."""
    data = _load_json(API_OUTPUT / "dim1" / "forecasts.json")
    if isinstance(data, dict) and "data" in data:
        records = data["data"]
        if country:
            records = [r for r in records if r.get("country") == country]
        if indicator:
            records = [r for r in records if r.get("indicator") == indicator]
        data["data"] = records
        data["meta"]["record_count"] = len(records)
    return data


@router.get("/dim1/lisa", response_model=APIResponse)
async def get_lisa(
    variable: str = Query("daly_rate"),
    year: Optional[int] = Query(None),
):
    """Get LISA cluster analysis results."""
    return _load_json(API_OUTPUT / "dim1" / f"lisa_{variable}.json")
