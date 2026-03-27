"""Dimension 3 endpoints: resource gaps, efficiency, optimization."""

from __future__ import annotations

import copy
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
    objective: Optional[str] = Query(None),
    budget_multiplier: Optional[float] = Query(None),
    budget: Optional[float] = Query(None),
):
    """Get optimal resource allocation results."""
    data = copy.deepcopy(_load_json(API_OUTPUT / "dim3" / "optimization.json"))
    if not (isinstance(data, dict) and isinstance(data.get("data"), dict)):
        return data

    payload = data["data"]
    target_budget = budget_multiplier if budget_multiplier is not None else budget
    normalized_budget = None
    if target_budget is not None:
        try:
            normalized_budget = float(target_budget)
        except (TypeError, ValueError):
            normalized_budget = None
    scenarios = payload.get("scenarios")
    if isinstance(scenarios, list):
        filtered = scenarios
        if objective:
            filtered = [row for row in filtered if row.get("objective") == objective]
        if normalized_budget is not None:
            filtered = [
                row for row in filtered
                if row.get("budget_multiplier") is not None and abs(float(row["budget_multiplier"]) - normalized_budget) < 1e-9
            ]
        payload["scenarios"] = filtered
        if isinstance(data.get("meta"), dict):
            data["meta"]["record_count"] = len(filtered)
            data["meta"]["query_params"] = {
                "objective": objective,
                "budget_multiplier": normalized_budget,
            }
    return data


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


@router.get("/dim3/china", response_model=APIResponse)
async def get_china_analysis():
    """Get China provincial resource gap, quadrant, and optimization analysis."""
    return _load_json(API_OUTPUT / "dim3" / "china_analysis.json")


@router.get("/dim3/china/optimization", response_model=APIResponse)
async def get_china_optimization(
    objective: Optional[str] = Query(None),
    budget_multiplier: Optional[float] = Query(None),
):
    """Get China provincial optimization scenarios."""
    data = copy.deepcopy(_load_json(API_OUTPUT / "dim3" / "china_analysis.json"))
    if not (isinstance(data, dict) and isinstance(data.get("data"), dict)):
        return data
    payload = data["data"]
    opt = payload.get("optimization", {})
    scenarios = opt.get("scenarios", [])
    if objective:
        scenarios = [s for s in scenarios if s.get("objective") == objective]
    if budget_multiplier is not None:
        scenarios = [s for s in scenarios if abs(float(s.get("budget_multiplier", 0)) - budget_multiplier) < 1e-9]
    opt["scenarios"] = scenarios
    payload["optimization"] = opt
    return data


@router.get("/dim3/equity", response_model=APIResponse)
async def get_equity():
    """Get global health equity metrics (Gini, concentration index, by-group)."""
    return _load_json(API_OUTPUT / "dim3" / "equity.json")
