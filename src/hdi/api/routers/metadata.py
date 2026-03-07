"""Metadata endpoints: countries, indicators."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Optional

from fastapi import APIRouter, Query

from hdi.api.schemas import APIResponse, CountryInfo, IndicatorInfo
from hdi.config import API_OUTPUT

router = APIRouter(tags=["metadata"])


def _load_json(path: Path) -> dict | list:
    if path.exists():
        with open(path) as f:
            return json.load(f)
    return {"status": "error", "message": f"Data not found: {path.name}"}


@router.get("/metadata/countries", response_model=APIResponse)
async def get_countries(
    region: Optional[str] = Query(None, description="WHO region filter"),
    income_group: Optional[str] = Query(None, description="WB income group filter"),
):
    """Get list of countries with metadata."""
    data = _load_json(API_OUTPUT / "metadata" / "countries.json")
    if isinstance(data, dict) and "data" in data:
        records = data["data"]
        if region:
            records = [r for r in records if r.get("who_region") == region]
        if income_group:
            records = [r for r in records if r.get("wb_income") == income_group]
        data["data"] = records
        data["meta"]["record_count"] = len(records)
    return data


@router.get("/metadata/indicators", response_model=APIResponse)
async def get_indicators(
    dimension: Optional[str] = Query(None, description="Dimension filter (dim1/dim2/dim3)"),
):
    """Get available indicators with descriptions."""
    data = _load_json(API_OUTPUT / "metadata" / "indicators.json")
    if isinstance(data, dict) and "data" in data and dimension:
        data["data"] = [r for r in data["data"] if r.get("dimension") == dimension]
        data["meta"]["record_count"] = len(data["data"])
    return data


@router.get("/composite/ghri", response_model=APIResponse)
async def get_ghri(
    year: Optional[int] = Query(None, description="Year filter"),
):
    """Get GHRI availability metadata."""
    data = _load_json(API_OUTPUT / "metadata" / "ghri.json")
    if isinstance(data, dict) and "data" in data and year:
        data["data"] = [r for r in data["data"] if r.get("year") == year]
        data["meta"]["record_count"] = len(data["data"])
    return data
