"""Dimension 3 endpoints: resource gaps, efficiency, optimization."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Optional

from fastapi import APIRouter, Query

from hdi.api.schemas import APIResponse
from hdi.config import API_OUTPUT

router = APIRouter(tags=["dimension3"])


def _load_json(path: Path) -> dict | list:
    if path.exists():
        with open(path) as f:
            return json.load(f)
    return {"status": "error", "message": f"Data not found: {path.name}"}


@router.get("/dim3/resource_gap", response_model=APIResponse)
async def get_resource_gap(
    year: Optional[int] = Query(None),
):
    """Get needs-based resource allocation gaps."""
    data = _load_json(API_OUTPUT / "dim3" / "resource_gap.json")
    if isinstance(data, dict) and "data" in data and year:
        records = data["data"]
        if isinstance(records, list):
            records = [r for r in records if r.get("year") == year]
            data["data"] = records
            data["meta"]["record_count"] = len(records)
    return data


@router.get("/dim3/efficiency", response_model=APIResponse)
async def get_efficiency(
    year: Optional[int] = Query(None),
    quadrant: Optional[str] = Query(None),
):
    """Get input-output efficiency scores and quadrant classification."""
    data = _load_json(API_OUTPUT / "dim3" / "efficiency.json")
    if isinstance(data, dict) and "data" in data:
        records = data["data"]
        if isinstance(records, list):
            if year:
                records = [r for r in records if r.get("year") == year]
            if quadrant:
                records = [r for r in records if r.get("quadrant") == quadrant]
            data["data"] = records
            data["meta"]["record_count"] = len(records)
    return data


@router.get("/dim3/optimization", response_model=APIResponse)
async def get_optimization(
    objective: str = Query("maximize_need_weighted_health_output"),
    budget: Optional[float] = Query(None),
):
    """Get optimal resource allocation results."""
    return _load_json(API_OUTPUT / "dim3" / "optimization.json")


@router.get("/dim3/malmquist", response_model=APIResponse)
async def get_malmquist(
    country: Optional[str] = Query(None),
):
    """Compatibility endpoint retained for legacy frontend expectations."""
    return {
        "status": "success",
        "meta": {"available": False, "country": country},
        "data": [],
    }
