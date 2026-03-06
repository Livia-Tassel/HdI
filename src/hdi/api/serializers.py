"""Result-to-JSON transformers for static API output generation."""

from __future__ import annotations

import json
import logging
from pathlib import Path

import pandas as pd

from hdi.config import API_OUTPUT

logger = logging.getLogger(__name__)


def _ensure_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def _write_json(data: dict | list, path: Path) -> None:
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2, default=str)
    logger.info("Wrote: %s", path)


def wrap_response(data, query_params: dict | None = None, version: str = "2025-03-05") -> dict:
    """Wrap data in the standard API response envelope."""
    record_count = len(data) if isinstance(data, list) else 1
    return {
        "status": "success",
        "meta": {
            "query_params": query_params or {},
            "data_version": version,
            "record_count": record_count,
        },
        "data": data,
    }


def df_to_records(df: pd.DataFrame) -> list[dict]:
    """Convert DataFrame to list of dicts, handling NaN."""
    return json.loads(df.to_json(orient="records", date_format="iso"))


# ── Metadata exports ─────────────────────────────────────────────────────────

def export_metadata_countries(panel: pd.DataFrame) -> None:
    """Export country list with metadata."""
    _ensure_dir(API_OUTPUT / "metadata")
    agg_spec = {
        "who_region": "first",
        "wb_income": "first",
    }
    name_col = next(
        (col for col in ("country", "country_name", "name") if col in panel.columns),
        None,
    )
    if name_col:
        agg_spec[name_col] = "first"

    countries = panel.groupby("iso3").agg(agg_spec).reset_index()
    if name_col and name_col != "name":
        countries = countries.rename(columns={name_col: "name"})
    if "name" not in countries.columns:
        countries["name"] = countries["iso3"]

    data = df_to_records(countries)
    _write_json(wrap_response(data), API_OUTPUT / "metadata" / "countries.json")


def export_metadata_indicators(indicator_list: list[dict]) -> None:
    """Export available indicator descriptions."""
    _ensure_dir(API_OUTPUT / "metadata")
    _write_json(wrap_response(indicator_list), API_OUTPUT / "metadata" / "indicators.json")


# ── Dimension 1 exports ──────────────────────────────────────────────────────

def export_dim1_spatiotemporal(gdf, variable: str, year: int) -> None:
    """Export spatiotemporal data as GeoJSON."""
    _ensure_dir(API_OUTPUT / "dim1")
    geojson = json.loads(gdf.to_json())
    _write_json(
        wrap_response(geojson, {"variable": variable, "year": year}),
        API_OUTPUT / "dim1" / f"spatiotemporal_{variable}_{year}.json",
    )


def export_dim1_trends(trend_df: pd.DataFrame) -> None:
    """Export trend analysis results."""
    _ensure_dir(API_OUTPUT / "dim1")
    data = df_to_records(trend_df)
    _write_json(wrap_response(data), API_OUTPUT / "dim1" / "trends.json")


def export_dim1_forecasts(forecast_results: list) -> None:
    """Export forecast results by country and indicator."""
    _ensure_dir(API_OUTPUT / "dim1")
    data = []
    for r in forecast_results:
        entry = {
            "country": r.country,
            "indicator": r.indicator,
            "method": r.method,
            "metrics": r.metrics,
            "forecast": df_to_records(r.forecast),
        }
        data.append(entry)
    _write_json(wrap_response(data), API_OUTPUT / "dim1" / "forecasts.json")


# ── Dimension 2 exports ──────────────────────────────────────────────────────

def export_dim2_paf(paf_df: pd.DataFrame) -> None:
    """Export PAF decomposition results."""
    _ensure_dir(API_OUTPUT / "dim2")
    data = df_to_records(paf_df)
    _write_json(wrap_response(data), API_OUTPUT / "dim2" / "paf.json")


def export_dim2_shapley(shapley_df: pd.DataFrame, country: str = "global") -> None:
    """Export Shapley decomposition results."""
    _ensure_dir(API_OUTPUT / "dim2")
    data = df_to_records(shapley_df)
    _write_json(
        wrap_response(data, {"country": country}),
        API_OUTPUT / "dim2" / f"shapley_{country}.json",
    )


def export_dim2_scenarios(scenario_results: dict) -> None:
    """Export scenario simulation results."""
    _ensure_dir(API_OUTPUT / "dim2")
    data = {}
    for name, result in scenario_results.items():
        data[name] = {
            "country": result.country,
            "years": result.years.tolist(),
            "trajectories": {k: v.tolist() for k, v in result.trajectories.items()},
        }
        if result.ci_lower:
            data[name]["ci_lower"] = {k: v.tolist() for k, v in result.ci_lower.items()}
            data[name]["ci_upper"] = {k: v.tolist() for k, v in result.ci_upper.items()}
    _write_json(wrap_response(data), API_OUTPUT / "dim2" / "scenarios.json")


# ── Dimension 3 exports ──────────────────────────────────────────────────────

def export_dim3_resource_gap(gap_df: pd.DataFrame) -> None:
    """Export resource gap analysis."""
    _ensure_dir(API_OUTPUT / "dim3")
    data = df_to_records(gap_df)
    _write_json(wrap_response(data), API_OUTPUT / "dim3" / "resource_gap.json")


def export_dim3_efficiency(efficiency_df: pd.DataFrame) -> None:
    """Export DEA efficiency scores and quadrant classification."""
    _ensure_dir(API_OUTPUT / "dim3")
    data = df_to_records(efficiency_df)
    _write_json(wrap_response(data), API_OUTPUT / "dim3" / "efficiency.json")


def export_dim3_optimization(optimization_result) -> None:
    """Export optimization results."""
    _ensure_dir(API_OUTPUT / "dim3")
    data = {
        "objective": optimization_result.objective,
        "status": optimization_result.status,
        "objective_value": optimization_result.objective_value,
        "allocation": df_to_records(optimization_result.optimal_allocation),
    }
    _write_json(wrap_response(data), API_OUTPUT / "dim3" / "optimization.json")


# ── Composite exports ────────────────────────────────────────────────────────

def export_ghri(ghri_df: pd.DataFrame) -> None:
    """Export GHRI composite index."""
    _ensure_dir(API_OUTPUT / "metadata")
    data = df_to_records(ghri_df)
    _write_json(wrap_response(data), API_OUTPUT / "metadata" / "ghri.json")


# ── Main export runner ───────────────────────────────────────────────────────

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(levelname)s | %(message)s")
    logger.info("Run individual export functions from notebooks or analysis scripts.")
