"""Build dashboard-specific JSON payloads for the interactive website."""

from __future__ import annotations

import copy
import json
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

from hdi.config import API_OUTPUT, DASHBOARD_DATA, REPORTS
from hdi.data.loaders import load_china_panel, load_master_panel, load_risk_attribution_long

logger = logging.getLogger(__name__)

_METRIC_LABELS = {
    "life_expectancy": "Life Expectancy",
    "ncd_share": "NCD Share",
    "communicable_share": "Communicable Disease Share",
    "health_exp_pct_gdp": "Health Expenditure (% GDP)",
    "share": "Risk Attribution Share",
    "attributable_deaths": "Attributable Deaths",
    "gap": "Resource Gap",
    "efficiency": "Input-Output Efficiency",
    "change_pct": "Scenario Reallocation",
}

_RISK_CODE_LABELS = {
    "unsafe_sex": "Unsafe sex",
    "unsafe_wash": "Unsafe water, sanitation, and handwashing",
    "intimate_partner_violence": "Intimate partner violence",
    "low_bone_density": "Low bone mineral density",
    "non_optimal_temperature": "Non-optimal temperature",
    "child_maternal_malnutrition": "Child and maternal malnutrition",
    "child_maltreatment": "Child maltreatment",
    "other_environmental": "Other environmental risks",
    "tobacco": "Tobacco",
    "drug_use": "Drug use",
    "air_pollution": "Air pollution",
    "occupational_risks": "Occupational risks",
    "kidney_dysfunction": "Kidney dysfunction",
    "low_physical_activity": "Low physical activity",
    "alcohol_use": "Alcohol use",
    "dietary_risks": "Dietary risks",
    "high_bmi": "High BMI",
    "high_ldl": "High LDL cholesterol",
    "high_systolic_bp": "High systolic blood pressure",
    "high_fasting_glucose": "High fasting glucose",
    "other_risk": "Other risk",
}

_GAP_GRADE_LABELS = {
    "E_严重不足": "E_critical_shortage",
    "D_不足": "D_shortage",
    "C_匹配": "C_balanced",
    "B_较充足": "B_relatively_adequate",
    "A_富余": "A_surplus",
}


def _ensure_dirs() -> None:
    DASHBOARD_DATA.mkdir(parents=True, exist_ok=True)


def _read_json(path: Path) -> dict[str, Any] | list[Any]:
    if not path.exists():
        logger.warning("Dashboard asset source missing: %s", path)
        return {}
    try:
        with open(path, "r", encoding="utf-8") as handle:
            return json.load(handle)
    except json.JSONDecodeError:
        logger.exception("Dashboard asset source is not valid JSON: %s", path)
        return {}


def _payload_data(path: Path) -> Any:
    payload = _read_json(path)
    if isinstance(payload, dict) and "data" in payload:
        return payload["data"]
    return payload


def _frame_from_records(records: Any, columns: list[str]) -> pd.DataFrame:
    frame = pd.DataFrame(records if isinstance(records, list) else [])
    for column in columns:
        if column not in frame.columns:
            frame[column] = None
    return frame[columns] if columns else frame


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


def _has_cjk(text: Any) -> bool:
    return any("\u4e00" <= char <= "\u9fff" for char in str(text or ""))


def _risk_display_name(risk_code: Any, risk_name: Any = None) -> str | None:
    code = str(risk_code or "").strip()
    if code in _RISK_CODE_LABELS:
        return _RISK_CODE_LABELS[code]
    raw = str(risk_name or "").strip()
    if raw and not _has_cjk(raw):
        return raw
    if code:
        return code.replace("_", " ").strip().title()
    if raw:
        return raw if not _has_cjk(raw) else "Other risk"
    return None


def _gap_grade_label(gap_grade: Any, gap_grade_en: Any = None) -> str | None:
    preferred = str(gap_grade_en or "").strip()
    if preferred:
        return preferred
    raw = str(gap_grade or "").strip()
    if not raw:
        return None
    return _GAP_GRADE_LABELS.get(raw, raw)


def _english_metric_bundle(codes: list[str], kind: str) -> list[dict[str, Any]]:
    type_map = {
        "life_expectancy": "continuous",
        "ncd_share": "continuous",
        "communicable_share": "continuous",
        "health_exp_pct_gdp": "continuous",
        "share": "continuous",
        "attributable_deaths": "continuous",
        "gap": "diverging",
        "efficiency": "diverging",
        "change_pct": "pct_diverging",
    }
    format_map = {
        "life_expectancy": "year",
        "ncd_share": "pct",
        "communicable_share": "pct",
        "health_exp_pct_gdp": "pct",
        "share": "pct",
        "attributable_deaths": "number",
        "gap": "decimal",
        "efficiency": "decimal",
        "change_pct": "pct",
    }
    return [
        {
            "code": code,
            "label": _METRIC_LABELS[code],
            "type": type_map[code],
            "format": format_map[code],
            "dimension": kind,
        }
        for code in codes
    ]


def _translate_summary(summary: Any, top_global_risk: str | None = None) -> dict[str, Any]:
    if not isinstance(summary, dict):
        return {}
    translated = copy.deepcopy(summary)
    dimension2 = translated.get("dimension2")
    if isinstance(dimension2, dict):
        dimension2["top_global_risk"] = top_global_risk or _risk_display_name(None, dimension2.get("top_global_risk"))
    return translated


def _translate_sankey(payload: Any) -> Any:
    if not isinstance(payload, dict):
        return payload
    nodes = payload.get("nodes")
    if isinstance(nodes, list):
        payload = dict(payload)
        payload["nodes"] = [_risk_display_name(node, node) or node for node in nodes]
    return payload


def _extract_optimization_lab(payload: Any) -> dict[str, Any]:
    data = payload.get("data", payload) if isinstance(payload, dict) else {}
    if not isinstance(data, dict):
        return {"default_scenario": None, "scenario_options": {}, "scenarios": [], "default_allocation": []}

    scenarios = data.get("scenarios")
    if not isinstance(scenarios, list):
        allocation = data.get("allocation")
        if isinstance(allocation, list):
            scenarios = [{
                "scenario_id": "legacy_default",
                "objective": data.get("objective", "legacy"),
                "objective_label": str(data.get("objective", "Legacy")),
                "budget_multiplier": 1.0,
                "status": data.get("status"),
                "objective_value": data.get("objective_value"),
                "summary": {},
                "allocation": allocation,
            }]
        else:
            scenarios = []

    default_scenario = data.get("default_scenario")
    if not default_scenario and scenarios:
        default_scenario = scenarios[0].get("scenario_id")

    scenario_entries = []
    default_allocation: list[dict[str, Any]] = []
    for scenario in scenarios:
        if not isinstance(scenario, dict):
            continue
        allocation = scenario.get("allocation")
        allocation_rows = allocation if isinstance(allocation, list) else []
        summary = scenario.get("summary") if isinstance(scenario.get("summary"), dict) else {}
        entry = {
            "scenario_id": scenario.get("scenario_id"),
            "objective": scenario.get("objective"),
            "objective_label": scenario.get("objective_label"),
            "budget_multiplier": scenario.get("budget_multiplier"),
            "status": scenario.get("status"),
            "objective_value": scenario.get("objective_value"),
            "summary": summary,
            "allocation": allocation_rows,
        }
        scenario_entries.append(entry)
        if entry["scenario_id"] == default_scenario:
            default_allocation = allocation_rows

    if not default_allocation and scenario_entries:
        default_allocation = scenario_entries[0]["allocation"]

    return {
        "default_scenario": default_scenario,
        "scenario_options": data.get("scenario_options", {
            "objectives": data.get("available_objectives", []),
            "budget_multipliers": data.get("budget_options", []),
        }),
        "scenarios": scenario_entries,
        "default_allocation": default_allocation,
    }


_PROVINCE_EN = {
    "北京市": "Beijing",
    "天津市": "Tianjin",
    "河北省": "Hebei",
    "山西省": "Shanxi",
    "内蒙古自治区": "Inner Mongolia",
    "辽宁省": "Liaoning",
    "吉林省": "Jilin",
    "黑龙江省": "Heilongjiang",
    "上海市": "Shanghai",
    "江苏省": "Jiangsu",
    "浙江省": "Zhejiang",
    "安徽省": "Anhui",
    "福建省": "Fujian",
    "江西省": "Jiangxi",
    "山东省": "Shandong",
    "河南省": "Henan",
    "湖北省": "Hubei",
    "湖南省": "Hunan",
    "广东省": "Guangdong",
    "广西壮族自治区": "Guangxi",
    "海南省": "Hainan",
    "重庆市": "Chongqing",
    "四川省": "Sichuan",
    "贵州省": "Guizhou",
    "云南省": "Yunnan",
    "西藏自治区": "Tibet",
    "陕西省": "Shaanxi",
    "甘肃省": "Gansu",
    "青海省": "Qinghai",
    "宁夏回族自治区": "Ningxia",
    "新疆维吾尔自治区": "Xinjiang",
    "全国": "China",
}


def _build_overview_timeseries(master: pd.DataFrame) -> dict[str, Any]:
    """Build per-year dim1 metrics for all countries (2000-2023)."""
    cols = ["iso3", "country_name", "who_region", "wb_income", "year",
            "life_expectancy", "ncd_share", "communicable_share", "health_exp_pct_gdp"]
    subset = master[cols].dropna(subset=["life_expectancy"]).copy()
    years = sorted(subset["year"].unique().tolist())
    by_year: dict[str, list[dict[str, Any]]] = {}
    for year in years:
        year_df = subset[subset["year"] == year]
        by_year[str(int(year))] = _records(year_df[cols])
    return {"years": [int(y) for y in years], "by_year": by_year}


def _build_china_deep_dive(china: pd.DataFrame) -> dict[str, Any]:
    """Build China provincial data payload for the dashboard."""
    china = china.copy()
    china["province_en"] = china["province"].map(_PROVINCE_EN).fillna(china["province"])

    # Separate national aggregate
    national = china[china["province"] == "全国"]
    provinces_df = china[china["province"] != "全国"]

    province_list = sorted(provinces_df["province_en"].unique().tolist())

    staff = provinces_df[provinces_df["indicator"] == "各省近20年卫生人员数量"]
    inst = provinces_df[provinces_df["indicator"] == "近20年各省医疗卫生机构数量"]

    def _build_series(df: pd.DataFrame) -> dict[str, list[dict[str, Any]]]:
        result: dict[str, list[dict[str, Any]]] = {}
        for prov, grp in df.groupby("province_en"):
            grp = grp.sort_values("year")
            result[str(prov)] = [
                {"year": int(r["year"]), "value": _normalize_value(r["value"])}
                for _, r in grp.iterrows()
            ]
        return result

    staff_series = _build_series(staff)
    inst_series = _build_series(inst)

    # Latest year rankings
    latest_year = int(provinces_df["year"].max()) if not provinces_df.empty else 0
    latest_staff = staff[staff["year"] == latest_year].sort_values("value", ascending=False)
    latest_inst = inst[inst["year"] == latest_year].sort_values("value", ascending=False)

    staff_ranking = [
        {"province": str(r["province_en"]), "value": _normalize_value(r["value"])}
        for _, r in latest_staff.iterrows()
    ]
    inst_ranking = [
        {"province": str(r["province_en"]), "value": _normalize_value(r["value"])}
        for _, r in latest_inst.iterrows()
    ]

    # National aggregate trend
    nat_staff = national[national["indicator"] == "各省近20年卫生人员数量"].sort_values("year")
    nat_inst = national[national["indicator"] == "近20年各省医疗卫生机构数量"].sort_values("year")
    national_trend = {
        "health_personnel": [
            {"year": int(r["year"]), "value": _normalize_value(r["value"])}
            for _, r in nat_staff.iterrows()
        ],
        "health_institutions": [
            {"year": int(r["year"]), "value": _normalize_value(r["value"])}
            for _, r in nat_inst.iterrows()
        ],
    }

    # Load China optimization analysis from competition pipeline output (if available)
    china_analysis_path = API_OUTPUT / "dim3" / "china_analysis.json"
    china_analysis: dict[str, Any] = {}
    if china_analysis_path.exists():
        try:
            with open(china_analysis_path, encoding="utf-8") as _f:
                _wrapped = json.load(_f)
            china_analysis = _wrapped.get("data", _wrapped)
        except Exception:
            pass

    payload: dict[str, Any] = {
        "latest_year": china_analysis.get("latest_year", latest_year),
        # Full province objects from optimization analysis (personnel_per_1000, gap, quadrant, etc.)
        "provinces": china_analysis.get("provinces", province_list),
        "resource_gap": china_analysis.get("resource_gap", []),
        "quadrant_counts": china_analysis.get("quadrant_counts", {}),
        "equity_metrics": china_analysis.get("equity_metrics", {}),
        "by_region": china_analysis.get("by_region", []),
        "optimization": china_analysis.get("optimization", {}),
        "personnel_history": china_analysis.get("personnel_history", {}),
        # Time-series data from raw China panel CSV
        "health_personnel": staff_series,
        "health_institutions": inst_series,
        "rankings": {
            "health_personnel": staff_ranking,
            "health_institutions": inst_ranking,
        },
        "national_trend": china_analysis.get("national_trend", national_trend),
    }
    return payload


def _load_global_equity_snapshot() -> dict[str, Any]:
    """Load global equity breakdown (by income, by region) from api_output."""
    equity_path = API_OUTPUT / "dim3" / "equity.json"
    if not equity_path.exists():
        return {}
    import json
    with open(equity_path, encoding="utf-8") as _f:
        wrapped = json.load(_f)
    data = wrapped.get("data", wrapped) if isinstance(wrapped, dict) else {}
    return {
        "equity_snapshot": {
            "gini_life_expectancy": data.get("gini_life_expectancy"),
            "gini_health_expenditure": data.get("gini_health_expenditure"),
            "concentration_index": data.get("concentration_index_exp_vs_life_expectancy"),
            "by_income_group": data.get("by_income_group", []),
            "by_who_region": data.get("by_who_region", []),
        }
    }


def _build_lorenz_data(master: pd.DataFrame) -> dict[str, Any]:
    """Compute Lorenz curves for health expenditure and life expectancy (latest year)."""
    latest_year = int(master["year"].max())
    snap = master[master["year"] == latest_year].dropna(subset=["health_exp_per_capita", "life_expectancy"]).copy()
    if snap.empty:
        return {"lorenz": {}}

    # Lorenz curve: sort by health_exp, compute cumulative shares
    snap_sorted = snap.sort_values("health_exp_per_capita").reset_index(drop=True)
    n = len(snap_sorted)
    cum_pop = np.arange(1, n + 1) / n * 100  # cumulative % of countries

    exp_vals = snap_sorted["health_exp_per_capita"].values.astype(float)
    cum_exp = np.cumsum(exp_vals) / exp_vals.sum() * 100

    le_sorted = snap.sort_values("life_expectancy").reset_index(drop=True)
    le_vals = le_sorted["life_expectancy"].values.astype(float)
    cum_le = np.cumsum(le_vals) / le_vals.sum() * 100
    cum_pop_le = np.arange(1, len(le_vals) + 1) / len(le_vals) * 100

    return {
        "lorenz": {
            "health_exp": {
                "x": [round(v, 2) for v in [0.0] + cum_pop.tolist()],
                "y": [round(v, 2) for v in [0.0] + cum_exp.tolist()],
                "label": "人均卫生支出",
                "country_count": n,
                "year": latest_year,
            },
            "life_expectancy": {
                "x": [round(v, 2) for v in [0.0] + cum_pop_le.tolist()],
                "y": [round(v, 2) for v in [0.0] + cum_le.tolist()],
                "label": "预期寿命",
                "country_count": len(le_vals),
                "year": latest_year,
            },
        }
    }


def _build_equity_data(master: pd.DataFrame) -> dict[str, Any]:
    """Compute per-year health equity metrics across countries."""
    years = sorted(master["year"].unique())
    records = []
    for year in years:
        snapshot = master[master["year"] == year]["life_expectancy"].dropna()
        if len(snapshot) < 5:
            continue
        values = snapshot.values.astype(float)
        n = len(values)

        # Gini coefficient
        sorted_vals = np.sort(values)
        index_arr = np.arange(1, n + 1)
        gini = float((2 * np.sum(index_arr * sorted_vals) - (n + 1) * np.sum(sorted_vals)) / (n * np.sum(sorted_vals)))

        # Theil index (GE(1))
        mu = values.mean()
        ratios = values / mu
        theil = float(np.mean(ratios * np.log(np.clip(ratios, 1e-10, None))))

        # Sigma convergence (SD of log life expectancy)
        log_vals = np.log(np.clip(values, 1e-10, None))
        sigma = float(np.std(log_vals, ddof=1))

        records.append({
            "year": int(year),
            "gini": round(gini, 6),
            "theil": round(theil, 6),
            "sigma": round(sigma, 6),
            "country_count": n,
        })
    return {"health_equity": records}


def build_dashboard_assets() -> dict[str, Any]:
    _ensure_dirs()

    master = load_master_panel()
    risk = load_risk_attribution_long()
    china = load_china_panel()

    latest_year = int(master["year"].max())
    overview_latest = master[master["year"] == latest_year].copy()

    # Backfill physicians_per_1000 and beds_per_1000 from up to 6 prior years to
    # improve global coverage (official data typically lags 2-4 years)
    for _lag_col in ["physicians_per_1000", "beds_per_1000"]:
        if _lag_col not in overview_latest.columns:
            continue
        for _backfill_yr in range(latest_year - 1, max(latest_year - 6, 2015), -1):
            _back = master[master["year"] == _backfill_yr][["iso3", _lag_col]].dropna(subset=[_lag_col])
            if _back.empty:
                continue
            _fill_map = _back.set_index("iso3")[_lag_col]
            still_missing = overview_latest[_lag_col].isna()
            overview_latest.loc[still_missing, _lag_col] = overview_latest.loc[still_missing, "iso3"].map(_fill_map)

    summary = _read_json(REPORTS / "analysis_summary.json") or {}
    resource_gap = _frame_from_records(
        _payload_data(API_OUTPUT / "dim3" / "resource_gap.json"),
        ["iso3", "actual_resource_index", "theoretical_need_index", "gap", "gap_grade", "gap_grade_en", "country_name", "who_region"],
    )
    efficiency = _frame_from_records(
        _payload_data(API_OUTPUT / "dim3" / "efficiency.json"),
        ["iso3", "efficiency", "quadrant", "input_index", "output_index", "country_name", "who_region"],
    )
    optimization_lab = _extract_optimization_lab(_read_json(API_OUTPUT / "dim3" / "optimization.json"))
    allocation = _frame_from_records(
        optimization_lab["default_allocation"],
        ["iso3", "current", "optimal", "change", "change_pct", "country_name", "who_region", "wb_income", "rank"],
    )
    sankey = _translate_sankey(
        _payload_data(API_OUTPUT / "dim2" / "sankey.json") or {"nodes": [], "sources": [], "targets": [], "values": []}
    )

    risk_deaths = risk[risk["measure"] == "deaths"].copy()
    latest_risk = (
        risk_deaths[risk_deaths["year"] == latest_year]
        .groupby(["iso3", "country_name", "who_region", "wb_income", "risk_code", "risk_factor"], as_index=False)["value"]
        .sum()
        .rename(columns={"value": "attributable_deaths", "risk_factor": "risk_name"})
    )
    latest_risk["risk_name"] = latest_risk.apply(
        lambda row: _risk_display_name(row.get("risk_code"), row.get("risk_name")),
        axis=1,
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
        resource_gap["gap_grade"] = resource_gap.apply(
            lambda row: _gap_grade_label(row.get("gap_grade"), row.get("gap_grade_en")),
            axis=1,
        )
        resource_gap["gap_grade_en"] = resource_gap["gap_grade"]
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
    translated_summary = _translate_summary(
        summary,
        top_global_risk=_normalize_value(global_top_risks.iloc[0]["risk_name"]) if not global_top_risks.empty else None,
    )

    overview = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "latest_year": latest_year,
        "summary": translated_summary,
        "metrics": {
            "dim1": _english_metric_bundle(["life_expectancy", "ncd_share", "communicable_share", "health_exp_pct_gdp"], "dim1"),
            "dim2": _english_metric_bundle(["share", "attributable_deaths"], "dim2"),
            "dim3": _english_metric_bundle(["gap", "efficiency", "change_pct"], "dim3"),
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
    top_reallocation = allocation.sort_values(["change_pct", "change"], ascending=False).head(12) if not allocation.empty else pd.DataFrame()

    global_story = {
        "summary": translated_summary,
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
        "optimization_lab": {
            "default_scenario": optimization_lab["default_scenario"],
            "scenario_options": optimization_lab["scenario_options"],
            "scenarios": optimization_lab["scenarios"],
        },
        **_build_equity_data(master),
        **_load_global_equity_snapshot(),
        **_build_lorenz_data(master),
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
    risk_history_base["risk_name"] = risk_history_base.apply(
        lambda row: _risk_display_name(row.get("risk_code"), row.get("risk_name")),
        axis=1,
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
        "overview_timeseries.json": _build_overview_timeseries(master),
        "china_deep_dive.json": _build_china_deep_dive(china),
    }
    for filename, payload in payloads.items():
        _write_json(payload, DASHBOARD_DATA / filename)

    logger.info("Dashboard data build finished.")
    return {"latest_year": latest_year, "files": sorted(payloads)}


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(levelname)s | %(message)s")
    build_dashboard_assets()
