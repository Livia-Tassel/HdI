"""Build dashboard-specific JSON payloads for the interactive website."""

from __future__ import annotations

import json
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd

from hdi.config import API_OUTPUT, DASHBOARD_DATA, REPORTS
from hdi.data.loaders import load_master_panel, load_risk_attribution_long

logger = logging.getLogger(__name__)


def _ensure_dirs() -> None:
    DASHBOARD_DATA.mkdir(parents=True, exist_ok=True)


def _read_json(path: Path) -> dict[str, Any] | list[Any]:
    with open(path, "r", encoding="utf-8") as handle:
        return json.load(handle)


def _payload_data(path: Path) -> Any:
    payload = _read_json(path)
    if isinstance(payload, dict) and "data" in payload:
        return payload["data"]
    return payload


def _normalize_value(value: Any) -> Any:
    if pd.isna(value):
        return None
    if hasattr(value, "item"):
        try:
            return value.item()
        except Exception:
            return value
    return value


def _records(df: pd.DataFrame) -> list[dict[str, Any]]:
    clean = df.copy()
    clean = clean.where(pd.notna(clean), None)
    return [{key: _normalize_value(value) for key, value in row.items()} for row in clean.to_dict(orient="records")]


def _write_json(data: Any, path: Path) -> None:
    with open(path, "w", encoding="utf-8") as handle:
        json.dump(data, handle, ensure_ascii=False, indent=2)
    logger.info("Wrote dashboard asset: %s", path)


def build_dashboard_assets() -> dict[str, Any]:
    _ensure_dirs()

    master = load_master_panel()
    risk = load_risk_attribution_long()

    latest_year = int(master["year"].max())
    overview_latest = master[master["year"] == latest_year].copy()

    summary = _read_json(REPORTS / "analysis_summary.json")
    resource_gap = pd.DataFrame(_payload_data(API_OUTPUT / "dim3" / "resource_gap.json"))
    efficiency = pd.DataFrame(_payload_data(API_OUTPUT / "dim3" / "efficiency.json"))
    allocation = pd.DataFrame(_payload_data(API_OUTPUT / "dim3" / "optimization.json")["allocation"])
    sankey = _payload_data(API_OUTPUT / "dim2" / "sankey.json")

    risk_deaths = risk[risk["measure"] == "deaths"].copy()
    latest_risk = (
        risk_deaths[risk_deaths["year"] == latest_year]
        .groupby(["iso3", "country_name", "who_region", "wb_income", "risk_code", "risk_factor"], as_index=False)["value"]
        .sum()
        .rename(columns={"value": "attributable_deaths", "risk_factor": "risk_name"})
    )
    latest_risk["country_total"] = latest_risk.groupby("iso3")["attributable_deaths"].transform("sum")
    latest_risk["share"] = latest_risk["attributable_deaths"] / latest_risk["country_total"]

    dominant_risk = (
        latest_risk.sort_values(["iso3", "attributable_deaths"], ascending=[True, False])
        .groupby("iso3", as_index=False)
        .first()[["iso3", "risk_code", "risk_name", "attributable_deaths", "share"]]
        .rename(
            columns={
                "risk_code": "top_risk_code",
                "risk_name": "top_risk_name",
                "attributable_deaths": "top_risk_deaths",
                "share": "top_risk_share",
            }
        )
    )

    world_latest = overview_latest.merge(dominant_risk, on="iso3", how="left")
    if not resource_gap.empty:
        world_latest = world_latest.merge(
            resource_gap[["iso3", "actual_resource_index", "theoretical_need_index", "gap", "gap_grade", "gap_grade_en"]],
            on="iso3",
            how="left",
        )
    if not efficiency.empty:
        world_latest = world_latest.merge(
            efficiency[["iso3", "efficiency", "quadrant", "input_index", "output_index"]],
            on="iso3",
            how="left",
        )
    if not allocation.empty:
        world_latest = world_latest.merge(
            allocation[["iso3", "current", "optimal", "change", "change_pct"]],
            on="iso3",
            how="left",
        )

    overview = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "latest_year": latest_year,
        "summary": summary,
        "metrics": {
            "dim1": [
                {"code": "life_expectancy", "label": "预期寿命", "type": "continuous", "format": "year"},
                {"code": "ncd_share", "label": "非传染性疾病占比", "type": "continuous", "format": "pct"},
                {"code": "communicable_share", "label": "传染性疾病占比", "type": "continuous", "format": "pct"},
                {"code": "health_exp_pct_gdp", "label": "卫生支出占GDP比重", "type": "continuous", "format": "pct"},
            ],
            "dim2": [
                {"code": "share", "label": "风险归因占比", "type": "continuous", "format": "pct"},
                {"code": "attributable_deaths", "label": "风险归因死亡", "type": "continuous", "format": "number"},
            ],
            "dim3": [
                {"code": "gap", "label": "资源缺口", "type": "diverging", "format": "decimal"},
                {"code": "efficiency", "label": "投入产出效率", "type": "diverging", "format": "decimal"},
                {"code": "change_pct", "label": "建议再分配变化", "type": "pct_diverging", "format": "pct"},
            ],
        },
        "countries": _records(
            world_latest[
                [
                    "iso3",
                    "country_name",
                    "who_region",
                    "wb_income",
                    "year",
                    "life_expectancy",
                    "communicable_share",
                    "ncd_share",
                    "injury_share",
                    "gdp_per_capita",
                    "health_exp_pct_gdp",
                    "health_exp_per_capita",
                    "physicians_per_1000",
                    "beds_per_1000",
                    "top_risk_code",
                    "top_risk_name",
                    "top_risk_deaths",
                    "top_risk_share",
                    "actual_resource_index",
                    "theoretical_need_index",
                    "gap",
                    "gap_grade",
                    "gap_grade_en",
                    "efficiency",
                    "quadrant",
                    "input_index",
                    "output_index",
                    "current",
                    "optimal",
                    "change",
                    "change_pct",
                ]
            ].sort_values("country_name")
        ),
    }

    risk_latest_payload = {
        "latest_year": latest_year,
        "risks": _records(
            latest_risk[
                [
                    "iso3",
                    "country_name",
                    "who_region",
                    "wb_income",
                    "risk_code",
                    "risk_name",
                    "attributable_deaths",
                    "country_total",
                    "share",
                ]
            ].sort_values(["risk_code", "country_name"])
        ),
        "available_risks": _records(
            latest_risk[["risk_code", "risk_name"]].drop_duplicates().sort_values("risk_name")
        ),
    }

    global_trends = (
        master.groupby("year", as_index=False)[["communicable_deaths", "ncd_deaths", "injury_deaths", "total_deaths"]]
        .sum()
        .assign(
            communicable_share=lambda frame: frame["communicable_deaths"] / frame["total_deaths"],
            ncd_share=lambda frame: frame["ncd_deaths"] / frame["total_deaths"],
            injury_share=lambda frame: frame["injury_deaths"] / frame["total_deaths"],
        )
    )

    global_top_risks = (
        latest_risk.groupby(["risk_code", "risk_name"], as_index=False)["attributable_deaths"]
        .sum()
        .sort_values("attributable_deaths", ascending=False)
        .head(12)
    )

    region_priority = (
        latest_risk.groupby(["who_region", "risk_code", "risk_name"], as_index=False)["share"]
        .mean()
        .sort_values(["who_region", "share"], ascending=[True, False])
    )

    region_priority_rows = []
    for region, subset in region_priority.groupby("who_region"):
        top = subset.head(3).copy()
        region_priority_rows.append(
            {
                "who_region": region,
                "primary_risk": _normalize_value(top.iloc[0]["risk_name"]) if len(top) > 0 else None,
                "primary_share": _normalize_value(top.iloc[0]["share"]) if len(top) > 0 else None,
                "secondary_risk": _normalize_value(top.iloc[1]["risk_name"]) if len(top) > 1 else None,
                "secondary_share": _normalize_value(top.iloc[1]["share"]) if len(top) > 1 else None,
                "tertiary_risk": _normalize_value(top.iloc[2]["risk_name"]) if len(top) > 2 else None,
                "tertiary_share": _normalize_value(top.iloc[2]["share"]) if len(top) > 2 else None,
            }
        )

    if not resource_gap.empty:
        under_resourced = resource_gap.sort_values("gap").head(12)
    else:
        under_resourced = pd.DataFrame()
    if not efficiency.empty:
        efficient_countries = efficiency[efficiency["quadrant"] == "Q2_low_input_high_output"].sort_values("efficiency", ascending=False).head(12)
    else:
        efficient_countries = pd.DataFrame()
    top_reallocation = allocation.sort_values("change_pct", ascending=False).head(12) if not allocation.empty else pd.DataFrame()

    global_story = {
        "summary": summary,
        "global_disease_trends": _records(global_trends[["year", "communicable_share", "ncd_share", "injury_share"]]),
        "global_top_risks": _records(global_top_risks),
        "region_priority": region_priority_rows,
        "resource_highlights": {
            "under_resourced": _records(
                under_resourced[["iso3", "country_name", "who_region", "gap", "gap_grade_en"]] if not under_resourced.empty else under_resourced
            ),
            "efficient": _records(
                efficient_countries[["iso3", "country_name", "who_region", "efficiency", "quadrant"]] if not efficient_countries.empty else efficient_countries
            ),
            "reallocation": _records(
                top_reallocation[["iso3", "country_name", "change", "change_pct"]] if not top_reallocation.empty else top_reallocation
            ),
        },
        "sankey": sankey,
    }

    country_profiles: dict[str, Any] = {}
    trend_cols = [
        "year",
        "life_expectancy",
        "communicable_share",
        "ncd_share",
        "injury_share",
        "gdp_per_capita",
        "health_exp_pct_gdp",
        "health_exp_per_capita",
        "physicians_per_1000",
        "beds_per_1000",
    ]
    risk_history_base = (
        risk_deaths.groupby(["iso3", "year", "risk_code", "risk_factor"], as_index=False)["value"]
        .sum()
        .rename(columns={"value": "attributable_deaths", "risk_factor": "risk_name"})
    )
    risk_history_base["country_total"] = risk_history_base.groupby(["iso3", "year"])["attributable_deaths"].transform("sum")
    risk_history_base["share"] = risk_history_base["attributable_deaths"] / risk_history_base["country_total"]

    world_latest_indexed = world_latest.set_index("iso3", drop=False)
    allocation_indexed = allocation.set_index("iso3", drop=False) if not allocation.empty else pd.DataFrame()

    for iso3, country_df in master.groupby("iso3"):
        country_df = country_df.sort_values("year")
        latest_row = world_latest_indexed.loc[iso3] if iso3 in world_latest_indexed.index else None
        latest_risks = latest_risk[latest_risk["iso3"] == iso3].sort_values("attributable_deaths", ascending=False).head(5)
        tracked_codes = latest_risks["risk_code"].tolist()
        risk_trend = risk_history_base[(risk_history_base["iso3"] == iso3) & (risk_history_base["risk_code"].isin(tracked_codes))]
        latest_payload = {
            key: _normalize_value(value)
            for key, value in (latest_row.to_dict().items() if latest_row is not None else {})
        }
        allocation_payload = {}
        if not allocation_indexed.empty and iso3 in allocation_indexed.index:
            allocation_payload = {
                key: _normalize_value(value) for key, value in allocation_indexed.loc[iso3].to_dict().items()
            }
        country_profiles[iso3] = {
            "meta": {
                "iso3": iso3,
                "country_name": _normalize_value(country_df["country_name"].dropna().iloc[0]) if country_df["country_name"].dropna().any() else iso3,
                "who_region": _normalize_value(country_df["who_region"].dropna().iloc[0]) if country_df["who_region"].dropna().any() else None,
                "wb_income": _normalize_value(country_df["wb_income"].dropna().iloc[0]) if country_df["wb_income"].dropna().any() else None,
            },
            "latest": latest_payload,
            "trend": _records(country_df[trend_cols]),
            "latest_risks": _records(latest_risks[["risk_code", "risk_name", "attributable_deaths", "share"]]),
            "risk_trend": _records(risk_trend[["year", "risk_code", "risk_name", "attributable_deaths", "share"]]),
            "allocation": allocation_payload,
        }

    payloads = {
        "overview.json": overview,
        "risk_latest.json": risk_latest_payload,
        "global_story.json": global_story,
        "country_profiles.json": country_profiles,
    }
    for filename, payload in payloads.items():
        _write_json(payload, DASHBOARD_DATA / filename)

    logger.info("Dashboard data build finished.")
    return {"latest_year": latest_year, "files": sorted(payloads)}


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(levelname)s | %(message)s")
    build_dashboard_assets()
