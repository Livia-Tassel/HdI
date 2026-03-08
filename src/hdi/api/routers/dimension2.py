"""Dimension 2 endpoints: PAF, Shapley, scenarios, interventions."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Optional

from fastapi import APIRouter, Query

from hdi.api.schemas import APIResponse
from hdi.config import API_OUTPUT

router = APIRouter(tags=["dimension2"])


def _load_json(path: Path) -> dict | list:
    if path.exists():
        with open(path) as f:
            return json.load(f)
    return {"status": "error", "message": f"Data not found: {path.name}"}


@router.get("/dim2/paf", response_model=APIResponse)
async def get_paf(
    country: Optional[str] = Query(None),
    disease: Optional[str] = Query(None),
    risk_factor: Optional[str] = Query(None),
):
    """Get risk-attributable death contribution results."""
    data = _load_json(API_OUTPUT / "dim2" / "paf.json")
    if isinstance(data, dict) and "data" in data:
        records = data["data"]
        if country:
            records = [r for r in records if r.get("iso3") == country]
        if disease:
            records = [r for r in records if r.get("cause_name") == disease]
        if risk_factor:
            records = [r for r in records if r.get("risk_factor") == risk_factor]
        data["data"] = records
        data["meta"]["record_count"] = len(records)
        data["meta"]["method"] = "attributable_share"
    return data


@router.get("/dim2/shapley", response_model=APIResponse)
async def get_shapley(
    country: str = Query("global"),
    disease: Optional[str] = Query(None),
):
    """Get a fair-share proxy of observed risk contributions."""
    data = _load_json(API_OUTPUT / "dim2" / f"shapley_{country}.json")
    if isinstance(data, dict):
        meta = data.setdefault("meta", {})
        if disease:
            meta["supports_disease_filter"] = False
            meta["ignored_filters"] = ["disease"]
            meta["query_params"] = {"country": country, "disease": disease}
        else:
            meta["supports_disease_filter"] = False
    return data


@router.get("/dim2/sankey", response_model=APIResponse)
async def get_sankey():
    """Get risk-to-region Sankey data built from attributable death flows."""
    return _load_json(API_OUTPUT / "dim2" / "sankey.json")


@router.get("/dim2/scenarios", response_model=APIResponse)
async def get_scenarios(
    scenario: Optional[str] = Query(None, description="A|B|C|D"),
    country: Optional[str] = Query(None),
):
    """Get policy scenario simulation projections."""
    data = _load_json(API_OUTPUT / "dim2" / "scenarios.json")
    if isinstance(data, dict) and "data" in data:
        records = data["data"]
        if isinstance(records, dict):
            if scenario:
                records = {k: v for k, v in records.items() if scenario in k}
            if country:
                records = {k: v for k, v in records.items() if v.get("country") == country}
            data["data"] = records
    return data


@router.get("/dim2/dose_response", response_model=APIResponse)
async def get_dose_response(
    risk_factor: str = Query("air_pollution"),
    disease: str = Query("all_causes"),
):
    """Compatibility endpoint retained for legacy frontend expectations."""
    return {
        "status": "success",
        "meta": {"available": False, "risk_factor": risk_factor, "disease": disease},
        "data": [],
    }
