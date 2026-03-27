"""Static JSON artifact exporters for the FastAPI layer."""

from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

from hdi.config import API_OUTPUT

logger = logging.getLogger(__name__)


def _ensure_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def _normalize_payload(data: Any) -> Any:
    if isinstance(data, pd.DataFrame):
        return json.loads(data.to_json(orient="records", date_format="iso"))
    if isinstance(data, pd.Series):
        return data.to_dict()
    if isinstance(data, np.ndarray):
        return data.tolist()
    if isinstance(data, dict):
        return {key: _normalize_payload(value) for key, value in data.items()}
    if isinstance(data, (list, tuple)):
        return [_normalize_payload(value) for value in data]
    return data


def wrap_response(data: Any, query_params: dict | None = None, version: str = "2026-03-07") -> dict:
    normalized = _normalize_payload(data)
    record_count = len(normalized) if isinstance(normalized, list) else 1
    return {
        "status": "success",
        "meta": {
            "query_params": query_params or {},
            "data_version": version,
            "record_count": record_count,
        },
        "data": normalized,
    }


def write_json_artifact(data: dict | list, path: Path) -> None:
    _ensure_dir(path.parent)
    with open(path, "w", encoding="utf-8") as handle:
        json.dump(data, handle, ensure_ascii=False, indent=2, default=str)
    logger.info("Wrote JSON artifact: %s", path)


def export_metadata_countries(panel: pd.DataFrame) -> None:
    countries = (
        panel.groupby("iso3", as_index=False)
        .agg(country_name=("country_name", "first"), who_region=("who_region", "first"), wb_income=("wb_income", "first"))
        .rename(columns={"country_name": "name"})
    )
    write_json_artifact(wrap_response(countries), API_OUTPUT / "metadata" / "countries.json")


def export_metadata_indicators(indicator_list: list[dict]) -> None:
    write_json_artifact(wrap_response(indicator_list), API_OUTPUT / "metadata" / "indicators.json")


def export_dim1_spatiotemporal(df: pd.DataFrame, metric: str, year: int, filename: str | None = None) -> None:
    payload = df.copy()
    write_json_artifact(
        wrap_response(payload, {"metric": metric, "year": year}),
        API_OUTPUT / "dim1" / (filename or f"spatiotemporal_{metric}_{year}.json"),
    )


def export_dim1_trends(trend_df: pd.DataFrame) -> None:
    write_json_artifact(wrap_response(trend_df), API_OUTPUT / "dim1" / "trends.json")


def export_dim1_forecasts(forecast_results: list[Any]) -> None:
    payload = []
    for result in forecast_results:
        payload.append(
            {
                "country": result.country,
                "indicator": result.indicator,
                "method": result.method,
                "metrics": result.metrics,
                "historical": _normalize_payload(result.historical),
                "forecast": _normalize_payload(result.forecast),
            }
        )
    write_json_artifact(wrap_response(payload), API_OUTPUT / "dim1" / "forecasts.json")


def export_dim2_paf(paf_df: pd.DataFrame) -> None:
    payload = wrap_response(paf_df)
    if isinstance(payload.get("meta"), dict):
        payload["meta"].update(
            {
                "method": "attributable_share",
                "compatibility_endpoint": "paf",
                "note": "赛题第二类数据为归因死亡结果；当前接口返回归因死亡贡献占比，而非基于暴露率与RR的严格PAF。",
            }
        )
    write_json_artifact(payload, API_OUTPUT / "dim2" / "paf.json")


def export_dim2_shapley(shapley_df: pd.DataFrame, country: str = "global") -> None:
    write_json_artifact(
        wrap_response(shapley_df, {"country": country}),
        API_OUTPUT / "dim2" / f"shapley_{country}.json",
    )


def export_dim2_scenarios(scenario_results: dict[str, dict]) -> None:
    write_json_artifact(wrap_response(scenario_results), API_OUTPUT / "dim2" / "scenarios.json")


def export_dim3_resource_gap(gap_df: pd.DataFrame) -> None:
    write_json_artifact(wrap_response(gap_df), API_OUTPUT / "dim3" / "resource_gap.json")


def export_dim3_efficiency(efficiency_df: pd.DataFrame) -> None:
    write_json_artifact(wrap_response(efficiency_df), API_OUTPUT / "dim3" / "efficiency.json")


def export_dim3_optimization(optimization_result: dict | Any) -> None:
    if isinstance(optimization_result, dict):
        payload = _normalize_payload(optimization_result)
        if isinstance(payload, dict) and "optimal_allocation" in payload:
            payload["allocation"] = payload.pop("optimal_allocation")
    else:
        payload = {
            "objective": optimization_result.objective,
            "status": optimization_result.status,
            "objective_value": optimization_result.objective_value,
            "allocation": _normalize_payload(optimization_result.optimal_allocation),
        }
    write_json_artifact(wrap_response(payload), API_OUTPUT / "dim3" / "optimization.json")


def export_dim3_china_analysis(china_payload: dict) -> None:
    write_json_artifact(wrap_response(china_payload), API_OUTPUT / "dim3" / "china_analysis.json")


def export_ghri_unavailable() -> None:
    data = {
        "status": "success",
        "meta": {"available": False, "reason": "GHRI未纳入本次主线交付"},
        "data": [],
    }
    write_json_artifact(data, API_OUTPUT / "metadata" / "ghri.json")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(levelname)s | %(message)s")
    logger.info("Run `python -m hdi.analysis.competition` to generate artifacts.")
