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
    year: Optional[int] = Query(None),
    metric: str = Query("life_expectancy"),
):
    """Get latest cross-country snapshot for a selected metric."""
    if year:
        filename = f"spatiotemporal_{metric}_{year}.json"
    elif metric == "life_expectancy":
        filename = "spatiotemporal_latest.json"
    else:
        candidates = sorted((API_OUTPUT / "dim1").glob(f"spatiotemporal_{metric}_*.json"))
        filename = candidates[-1].name if candidates else "spatiotemporal_latest.json"
    return _load_json(API_OUTPUT / "dim1" / filename)


@router.get("/dim1/trends", response_model=APIResponse)
async def get_trends(
    country: Optional[str] = Query(None),
    disease_group: Optional[str] = Query(None),
):
    """Get cause-group trend records by country and year."""
    data = _load_json(API_OUTPUT / "dim1" / "trends.json")
    if isinstance(data, dict) and "data" in data:
        records = data["data"]
        if country:
            records = [r for r in records if r.get("iso3") == country]
        if disease_group:
            records = [r for r in records if r.get("cause_group") == disease_group]
        data["data"] = records
        data["meta"]["record_count"] = len(records)
    return data


@router.get("/dim1/forecasts", response_model=APIResponse)
async def get_forecasts(
    country: Optional[str] = Query(None),
    indicator: Optional[str] = Query(None),
):
    """Get country-level forecasting outputs."""
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
    variable: str = Query("life_expectancy"),
    year: Optional[int] = Query(None),
):
    """Compatibility endpoint retained for legacy frontend expectations."""
    return {
        "status": "success",
        "meta": {"available": False, "variable": variable, "year": year},
        "data": [],
    }
