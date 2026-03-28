"""Competition analysis pipeline built on the provided datasets."""

from __future__ import annotations

import json
import logging
from dataclasses import dataclass
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
import statsmodels.api as sm
from matplotlib import font_manager as fm

from hdi.api.serializers import (
    export_dim1_forecasts,
    export_dim1_spatiotemporal,
    export_dim1_trends,
    export_dim2_paf,
    export_dim2_scenarios,
    export_dim2_shapley,
    export_dim3_china_analysis,
    export_dim3_efficiency,
    export_dim3_optimization,
    export_dim3_resource_gap,
    export_ghri_unavailable,
    export_metadata_countries,
    export_metadata_indicators,
    wrap_response,
    write_json_artifact,
)
from hdi.data.china_provincial import (
    build_china_latest_snapshot,
    load_china_provincial_panel,
    PROVINCE_EN as _PROVINCE_EN_MAP,
    PROVINCE_REGION as _PROVINCE_REGION_MAP,
    PROVINCE_REGION_EN as _PROVINCE_REGION_EN_MAP,
)
from hdi.config import (
    API_OUTPUT,
    FIGURES,
    FORECAST_END_YEAR,
    INDICATOR_SPECS,
    MASTER_PANEL,
    REPORTS,
    RESOURCE_PANEL,
    RISK_LABEL_MAP,
    RISK_INTERVENTIONS,
    TABLES,
)
from hdi.data.loaders import (
    load_china_panel,
    load_disease_mortality_long,
    load_master_panel,
    load_resource_panel,
    load_risk_attribution_long,
)
from hdi.models.optimization import optimize_allocation_maximin, optimize_allocation_max_output

logger = logging.getLogger(__name__)
for font_path in (
    Path("/System/Library/Fonts/STHeiti Light.ttc"),
    Path("/System/Library/Fonts/STHeiti Medium.ttc"),
    Path("/System/Library/Fonts/Hiragino Sans GB.ttc"),
):
    if font_path.exists():
        plt.rcParams["font.family"] = fm.FontProperties(fname=str(font_path)).get_name()
        break
plt.rcParams["axes.unicode_minus"] = False
sns.set_theme(style="whitegrid")

_CAUSE_GROUP_EN = {
    "传染性疾病": "Communicable",
    "非传染性疾病": "NCD",
    "伤害": "Injuries",
}

_GAP_GRADE_EN = {
    "E_严重不足": "E_critical_shortage",
    "D_不足": "D_shortage",
    "C_匹配": "C_balanced",
    "B_较充足": "B_relatively_adequate",
    "A_富余": "A_surplus",
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

_OPTIMIZATION_BUDGETS = [0.9, 1.0, 1.1]
_OPTIMIZATION_OBJECTIVES = {
    "max_output": {
        "label": "Maximize Aggregate Health Output",
        "description": "Prioritize total modeled health output under a fixed budget.",
        "solver": optimize_allocation_max_output,
    },
    "maximin": {
        "label": "Protect Lowest-Outcome Countries",
        "description": "Maximize the minimum modeled outcome across countries.",
        "solver": optimize_allocation_maximin,
    },
}

_OPTIMIZATION_OBJECTIVES_PERSONNEL = {
    "max_output_personnel": {
        "label": "最大化总产出（人力再分配）",
        "description": "以各国医生密度为资源输入，模拟全球人力资源最优再分配，最大化总体健康产出。",
        "solver": optimize_allocation_max_output,
    },
    "maximin_personnel": {
        "label": "最小化健康不平等（人力再分配）",
        "description": "以各国医生密度为资源输入，模拟全球人力资源最优再分配，最大化最低产出国家的健康水平。",
        "solver": optimize_allocation_maximin,
    },
}


@dataclass
class SimpleForecastResult:
    method: str
    country: str
    indicator: str
    historical: pd.DataFrame
    forecast: pd.DataFrame
    metrics: dict[str, float]


def _ensure_dirs() -> None:
    for path in (FIGURES, TABLES, API_OUTPUT / "dim1", API_OUTPUT / "dim2", API_OUTPUT / "dim3", API_OUTPUT / "metadata"):
        path.mkdir(parents=True, exist_ok=True)


def _save_figure(fig: plt.Figure, name: str) -> None:
    path = FIGURES / f"{name}.png"
    fig.savefig(path, dpi=300, bbox_inches="tight")
    plt.close(fig)
    logger.info("Saved figure: %s", path)


def _save_table(df: pd.DataFrame, name: str) -> None:
    csv_path = TABLES / f"{name}.csv"
    tex_path = TABLES / f"{name}.tex"
    df.to_csv(csv_path, index=False)
    with open(tex_path, "w", encoding="utf-8") as handle:
        handle.write(df.to_latex(index=False, float_format=lambda value: f"{value:.3f}" if isinstance(value, float) else str(value)))
    logger.info("Saved table: %s", csv_path)


def _standardize(series: pd.Series, invert: bool = False) -> pd.Series:
    numeric = pd.to_numeric(series, errors="coerce")
    if numeric.dropna().empty:
        return pd.Series(np.nan, index=series.index)
    scaled = (numeric - numeric.mean()) / (numeric.std(ddof=0) or 1.0)
    if invert:
        scaled = -scaled
    return scaled


def _select_countries(master: pd.DataFrame) -> list[str]:
    preferred = ["CHN", "USA", "IND", "BRA", "ZAF", "DEU"]
    available = set(master["iso3"])
    selected = [iso3 for iso3 in preferred if iso3 in available]
    if len(selected) >= 4:
        return selected
    coverage = (
        master.groupby("iso3")["life_expectancy"]
        .apply(lambda series: series.notna().sum())
        .sort_values(ascending=False)
        .head(6)
        .index.tolist()
    )
    return coverage


def _linear_forecast(series: pd.Series, country: str, indicator: str) -> SimpleForecastResult | None:
    clean = series.dropna().sort_index()
    if len(clean) < 8:
        return None

    x = clean.index.to_numpy(dtype=float)
    y = clean.to_numpy(dtype=float)
    slope, intercept = np.polyfit(x, y, 1)
    fitted = intercept + slope * x
    rmse = float(np.sqrt(np.mean((y - fitted) ** 2)))
    mae = float(np.mean(np.abs(y - fitted)))
    denom = np.where(np.abs(y) < 1e-6, 1.0, np.abs(y))
    mape = float(np.mean(np.abs((y - fitted) / denom)) * 100)

    years = np.arange(int(x.max()) + 1, FORECAST_END_YEAR + 1)
    predicted = intercept + slope * years
    forecast = pd.DataFrame(
        {
            "year": years.astype(int),
            "predicted": predicted,
            "ci_lower": predicted - 1.96 * rmse,
            "ci_upper": predicted + 1.96 * rmse,
        }
    )
    historical = pd.DataFrame({"year": x.astype(int), "value": y})
    return SimpleForecastResult(
        method="linear_trend",
        country=country,
        indicator=indicator,
        historical=historical,
        forecast=forecast,
        metrics={"MAE": mae, "RMSE": rmse, "MAPE": mape},
    )


def _write_summary(summary: dict) -> None:
    path = REPORTS / "analysis_summary.json"
    with open(path, "w", encoding="utf-8") as handle:
        json.dump(summary, handle, ensure_ascii=False, indent=2)


def _fit_output_curve(inputs: np.ndarray, outputs: np.ndarray) -> tuple[float, float]:
    log_inputs = np.log(np.clip(inputs, 0.0, None) + 1.0)
    b_coef, a_coef = np.polynomial.polynomial.polyfit(log_inputs, outputs, 1)
    if not np.isfinite(a_coef):
        a_coef = 1e-6
    if not np.isfinite(b_coef):
        b_coef = 0.0
    return float(max(a_coef, 1e-6)), float(b_coef)


def _project_output_curve(inputs: np.ndarray, a_coef: float, b_coef: float) -> np.ndarray:
    return a_coef * np.log(np.clip(inputs, 0.0, None) + 1.0) + b_coef


def _scenario_id(objective: str, budget_multiplier: float) -> str:
    return f"{objective}_budget_{int(round(budget_multiplier * 100)):03d}"


def _build_optimization_scenario(
    optimize_base: pd.DataFrame,
    result,
    objective: str,
    budget_multiplier: float,
    a_coef: float,
    b_coef: float,
    objectives_dict: dict | None = None,
) -> dict:
    _all_objectives = {**_OPTIMIZATION_OBJECTIVES, **_OPTIMIZATION_OBJECTIVES_PERSONNEL}
    objective_meta = (objectives_dict or _all_objectives)[objective]
    _merge_cols = [c for c in ["iso3", "country_name", "who_region", "wb_income",
                               "quadrant", "theoretical_need", "gap", "efficiency",
                               "output_index", "life_expectancy"] if c in optimize_base.columns]
    allocation = result.optimal_allocation.merge(
        optimize_base[_merge_cols],
        on="iso3",
        how="left",
    )
    allocation["projected_output_current"] = _project_output_curve(allocation["current"].to_numpy(dtype=float), a_coef, b_coef)
    allocation["projected_output_optimal"] = _project_output_curve(allocation["optimal"].to_numpy(dtype=float), a_coef, b_coef)
    allocation["projected_output_delta"] = allocation["projected_output_optimal"] - allocation["projected_output_current"]
    allocation = allocation.sort_values("change_pct", ascending=False).reset_index(drop=True)

    recipients = allocation.nlargest(5, "change_pct")[
        ["iso3", "country_name", "who_region", "change", "change_pct", "projected_output_delta"]
    ]
    donors = allocation.nsmallest(5, "change_pct")[
        ["iso3", "country_name", "who_region", "change", "change_pct", "projected_output_delta"]
    ]
    current_total = float(allocation["current"].sum())
    optimal_total = float(allocation["optimal"].sum())
    projected_current = float(allocation["projected_output_current"].sum())
    projected_optimal = float(allocation["projected_output_optimal"].sum())
    projected_gain_pct = ((projected_optimal - projected_current) / abs(projected_current) * 100.0) if abs(projected_current) > 1e-9 else 0.0

    # Gini of projected output (shifted to non-negative)
    cur_proj = allocation["projected_output_current"].to_numpy(dtype=float)
    opt_proj = allocation["projected_output_optimal"].to_numpy(dtype=float)
    shift = max(-np.nanmin(cur_proj), -np.nanmin(opt_proj), 0.0) + 1.0
    gini_before_global = _compute_gini(cur_proj + shift)
    gini_after_global = _compute_gini(opt_proj + shift)
    gini_change_global = float(gini_after_global - gini_before_global) if np.isfinite(gini_before_global) and np.isfinite(gini_after_global) else None

    budget_label = f"{budget_multiplier:.0%}" if budget_multiplier != 1.0 else "基准（100%）"
    return {
        "scenario_id": _scenario_id(objective, budget_multiplier),
        "objective": objective,
        "objective_label": objective_meta["label"],
        "objective_description": objective_meta["description"],
        "budget_multiplier": budget_multiplier,
        "budget_change_pct": (budget_multiplier - 1.0) * 100.0,
        "status": result.status,
        "objective_value": float(result.objective_value),
        "summary": {
            "label": f"{objective_meta['label']} · {budget_label}",
            "budget_label": budget_label,
            "country_count": int(len(allocation)),
            "current_budget": current_total,
            "optimal_budget": optimal_total,
            "projected_output_current": projected_current,
            "projected_output_optimal": projected_optimal,
            "projected_output_gain_pct": projected_gain_pct,
            "recipient_count": int((allocation["change_pct"] > 0).sum()),
            "donor_count": int((allocation["change_pct"] < 0).sum()),
            "moved_budget": float(allocation.loc[allocation["change"] > 0, "change"].sum()),
            "gini_before": float(gini_before_global) if np.isfinite(gini_before_global) else None,
            "gini_after": float(gini_after_global) if np.isfinite(gini_after_global) else None,
            "gini_change": gini_change_global,
            "top_recipients": recipients.to_dict(orient="records"),
            "top_donors": donors.to_dict(orient="records"),
        },
        "allocation": allocation.to_dict(orient="records"),
    }


def _compute_gini(values: np.ndarray) -> float:
    """Compute Gini coefficient for a 1-D array of non-negative values."""
    v = np.sort(values[np.isfinite(values) & (values >= 0)])
    if len(v) == 0 or v.sum() < 1e-12:
        return float("nan")
    n = len(v)
    cumv = np.cumsum(v)
    return float((2 * np.sum((np.arange(1, n + 1)) * v) - (n + 1) * cumv[-1]) / (n * cumv[-1]))


def _compute_concentration_index(health_var: np.ndarray, rank_var: np.ndarray) -> float:
    """Compute concentration index of health_var ranked by rank_var (e.g., income)."""
    mask = np.isfinite(health_var) & np.isfinite(rank_var)
    h = health_var[mask]
    r = rank_var[mask]
    if len(h) < 3:
        return float("nan")
    rank = np.argsort(np.argsort(r)) + 1
    n = len(h)
    frac_rank = (rank - 0.5) / n
    mu = h.mean()
    if abs(mu) < 1e-12:
        return float("nan")
    return float(2.0 * np.cov(h, frac_rank, ddof=1)[0, 1] / mu)


def _build_china_optimization_scenarios(snap: pd.DataFrame, panel: pd.DataFrame) -> dict:
    """Run LP optimization for China provinces and return a structured payload."""
    from hdi.models.optimization import optimize_allocation_max_output, optimize_allocation_maximin

    snap_clean = snap.dropna(subset=["health_exp_per_capita", "output_index"]).copy()
    snap_clean["health_exp_per_capita"] = snap_clean["health_exp_per_capita"].clip(lower=1)
    snap_clean = snap_clean.rename(columns={"province": "entity"})

    a_coef, b_coef = _fit_output_curve(
        snap_clean["health_exp_per_capita"].to_numpy(dtype=float),
        snap_clean["output_index"].to_numpy(dtype=float),
    )

    objectives = {
        "max_output": {
            "label": "最大化健康产出",
            "label_en": "Maximize Aggregate Health Output",
            "description": "固定总卫生经费，最大化全体省份综合健康产出之和",
            "solver": optimize_allocation_max_output,
        },
        "maximin": {
            "label": "最小化健康不平等",
            "label_en": "Minimize Health Inequality (Rawlsian)",
            "description": "最大化最弱省份的健康产出（Rawls极小极大原则）",
            "solver": optimize_allocation_maximin,
        },
    }
    budgets = [0.9, 1.0, 1.1]

    # Personnel-based optimization (re-distribution of health workforce)
    personnel_objectives = {
        "max_output_personnel": {
            "label": "最大化健康产出（人力）",
            "label_en": "Maximize Output via Workforce Reallocation",
            "description": "固定总卫生人力，最大化全体省份综合健康产出之和（人力资源再分配）",
            "resource": "personnel",
            "solver": optimize_allocation_max_output,
        },
        "maximin_personnel": {
            "label": "最小化不平等（人力）",
            "label_en": "Minimize Inequality via Workforce Reallocation",
            "description": "固定总卫生人力，最大化最弱省份健康产出（Rawls原则，人力资源再分配）",
            "resource": "personnel",
            "solver": optimize_allocation_maximin,
        },
    }

    scenarios = []
    for obj_code, obj_meta in objectives.items():
        for budget_mult in budgets:
            try:
                result = obj_meta["solver"](
                    snap_clean,
                    output_col="output_index",
                    input_col="health_exp_per_capita",
                    entity_col="entity",
                    budget_multiplier=budget_mult,
                )
                allocation_df = result.optimal_allocation.merge(
                    snap_clean[["entity", "province_en", "region", "region_en", "quadrant", "quadrant_en",
                                "theoretical_need", "gap", "efficiency", "output_index",
                                "life_expectancy", "infant_mortality", "personnel_per_1000"]],
                    on="entity",
                    how="left",
                )
                # Restore 'province' column for dashboard consumption
                allocation_df = allocation_df.rename(columns={"entity": "province"})
                allocation_df["projected_output_current"] = _project_output_curve(
                    allocation_df["current"].to_numpy(dtype=float), a_coef, b_coef
                )
                allocation_df["projected_output_optimal"] = _project_output_curve(
                    allocation_df["optimal"].to_numpy(dtype=float), a_coef, b_coef
                )
                allocation_df["projected_output_delta"] = (
                    allocation_df["projected_output_optimal"] - allocation_df["projected_output_current"]
                )

                current_total = float(allocation_df["current"].sum())
                optimal_total = float(allocation_df["optimal"].sum())
                proj_curr = float(allocation_df["projected_output_current"].sum())
                proj_opt = float(allocation_df["projected_output_optimal"].sum())
                gain_pct = ((proj_opt - proj_curr) / abs(proj_curr) * 100) if abs(proj_curr) > 1e-9 else 0.0

                recipients = allocation_df.nlargest(5, "change_pct")
                donors = allocation_df.nsmallest(5, "change_pct")

                # Post-scenario Gini of projected outputs (shift to non-negative first)
                _cur_proj_arr = allocation_df["projected_output_current"].to_numpy(dtype=float)
                _opt_proj_arr = allocation_df["projected_output_optimal"].to_numpy(dtype=float)
                _shift_china = max(-np.nanmin(_cur_proj_arr), -np.nanmin(_opt_proj_arr), 0.0) + 1.0
                gini_before = _compute_gini(_cur_proj_arr + _shift_china)
                gini_after = _compute_gini(_opt_proj_arr + _shift_china)

                scenarios.append({
                    "scenario_id": f"{obj_code}_budget_{int(round(budget_mult * 100)):03d}",
                    "objective": obj_code,
                    "objective_label": obj_meta["label"],
                    "objective_label_en": obj_meta["label_en"],
                    "objective_description": obj_meta["description"],
                    "budget_multiplier": budget_mult,
                    "budget_change_pct": (budget_mult - 1.0) * 100.0,
                    "status": result.status,
                    "objective_value": float(result.objective_value),
                    "summary": {
                        "province_count": int(len(allocation_df)),
                        "current_budget_total": current_total,
                        "optimal_budget_total": optimal_total,
                        "projected_output_current": proj_curr,
                        "projected_output_optimal": proj_opt,
                        "projected_output_gain_pct": gain_pct,
                        "gini_before": gini_before,
                        "gini_after": gini_after,
                        "gini_change": gini_after - gini_before if np.isfinite(gini_before) and np.isfinite(gini_after) else None,
                        "recipient_count": int((allocation_df["change_pct"] > 0).sum()),
                        "donor_count": int((allocation_df["change_pct"] < 0).sum()),
                        "top_recipients": recipients[["province", "province_en", "region", "change", "change_pct"]].to_dict(orient="records"),
                        "top_donors": donors[["province", "province_en", "region", "change", "change_pct"]].to_dict(orient="records"),
                    },
                    "allocation": allocation_df.to_dict(orient="records"),
                })
            except Exception:
                logger.exception("China optimization failed: %s / %.1f", obj_code, budget_mult)

    # Personnel-based optimization: redistribute health workforce across provinces
    snap_personnel = snap_clean.dropna(subset=["personnel_per_1000", "output_index"]).copy()
    snap_personnel["personnel_per_1000"] = snap_personnel["personnel_per_1000"].clip(lower=0.1)
    if len(snap_personnel) >= 10:
        pa_coef, pb_coef = _fit_output_curve(
            snap_personnel["personnel_per_1000"].to_numpy(dtype=float),
            snap_personnel["output_index"].to_numpy(dtype=float),
        )
        for obj_code, obj_meta in personnel_objectives.items():
            for budget_mult in budgets:
                try:
                    result = obj_meta["solver"](
                        snap_personnel,
                        output_col="output_index",
                        input_col="personnel_per_1000",
                        entity_col="entity",
                        budget_multiplier=budget_mult,
                    )
                    alloc_df = result.optimal_allocation.merge(
                        snap_personnel[["entity", "province_en", "region", "region_en", "quadrant", "quadrant_en",
                                        "theoretical_need", "gap", "efficiency", "output_index",
                                        "life_expectancy", "infant_mortality", "health_exp_per_capita"]],
                        on="entity",
                        how="left",
                    )
                    alloc_df = alloc_df.rename(columns={"entity": "province"})
                    alloc_df["projected_output_current"] = _project_output_curve(
                        alloc_df["current"].to_numpy(dtype=float), pa_coef, pb_coef
                    )
                    alloc_df["projected_output_optimal"] = _project_output_curve(
                        alloc_df["optimal"].to_numpy(dtype=float), pa_coef, pb_coef
                    )
                    alloc_df["projected_output_delta"] = (
                        alloc_df["projected_output_optimal"] - alloc_df["projected_output_current"]
                    )

                    p_curr_total = float(alloc_df["current"].sum())
                    p_opt_total = float(alloc_df["optimal"].sum())
                    p_proj_curr = float(alloc_df["projected_output_current"].sum())
                    p_proj_opt = float(alloc_df["projected_output_optimal"].sum())
                    p_gain = ((p_proj_opt - p_proj_curr) / abs(p_proj_curr) * 100) if abs(p_proj_curr) > 1e-9 else 0.0

                    p_recipients = alloc_df.nlargest(5, "change_pct")
                    p_donors = alloc_df.nsmallest(5, "change_pct")

                    _p_cur_arr = alloc_df["projected_output_current"].to_numpy(dtype=float)
                    _p_opt_arr = alloc_df["projected_output_optimal"].to_numpy(dtype=float)
                    _p_shift = max(-np.nanmin(_p_cur_arr), -np.nanmin(_p_opt_arr), 0.0) + 1.0
                    p_gini_before = _compute_gini(_p_cur_arr + _p_shift)
                    p_gini_after = _compute_gini(_p_opt_arr + _p_shift)

                    scenarios.append({
                        "scenario_id": f"{obj_code}_budget_{int(round(budget_mult * 100)):03d}",
                        "objective": obj_code,
                        "objective_label": obj_meta["label"],
                        "objective_label_en": obj_meta["label_en"],
                        "objective_description": obj_meta["description"],
                        "resource_type": "personnel",
                        "budget_multiplier": budget_mult,
                        "budget_change_pct": (budget_mult - 1.0) * 100.0,
                        "status": result.status,
                        "objective_value": float(result.objective_value),
                        "summary": {
                            "province_count": int(len(alloc_df)),
                            "current_budget_total": p_curr_total,
                            "optimal_budget_total": p_opt_total,
                            "projected_output_current": p_proj_curr,
                            "projected_output_optimal": p_proj_opt,
                            "projected_output_gain_pct": p_gain,
                            "gini_before": float(p_gini_before) if np.isfinite(p_gini_before) else None,
                            "gini_after": float(p_gini_after) if np.isfinite(p_gini_after) else None,
                            "gini_change": float(p_gini_after - p_gini_before) if np.isfinite(p_gini_before) and np.isfinite(p_gini_after) else None,
                            "recipient_count": int((alloc_df["change_pct"] > 0).sum()),
                            "donor_count": int((alloc_df["change_pct"] < 0).sum()),
                            "top_recipients": p_recipients[["province", "province_en", "region", "change", "change_pct"]].to_dict(orient="records"),
                            "top_donors": p_donors[["province", "province_en", "region", "change", "change_pct"]].to_dict(orient="records"),
                        },
                        "allocation": alloc_df.to_dict(orient="records"),
                    })
                except Exception:
                    logger.exception("China personnel optimization failed: %s / %.1f", obj_code, budget_mult)

    # Build resource gap table
    gap_grades = pd.qcut(
        snap["gap"].dropna(),
        q=5,
        labels=["E_严重不足", "D_不足", "C_匹配", "B_较充足", "A_富余"],
        duplicates="drop",
    )
    snap = snap.copy()
    snap["gap_grade"] = pd.qcut(
        snap["gap"],
        q=5,
        labels=["E_严重不足", "D_不足", "C_匹配", "B_较充足", "A_富余"],
        duplicates="drop",
    )
    # Include extended health resource columns (present only if data available)
    _extra_cols = [c for c in [
        "hospital_beds_per_1000", "physicians_per_1000", "nurses_per_1000",
        "gdp_per_capita", "urban_income_per_capita", "rural_income_per_capita",
        "maternal_mortality", "under5_mortality",
        "elderly_share", "urbanization_rate",
        "basic_insurance_rate", "primary_care_density",
        "hypertension_prevalence", "diabetes_prevalence", "obesity_prevalence",
    ] if c in snap.columns]
    gap_records = snap[[
        "province", "province_en", "region", "region_en",
        "input_index", "theoretical_need", "gap", "gap_grade",
        "output_index", "efficiency", "quadrant", "quadrant_en",
        "personnel_per_1000", "health_exp_per_capita",
        "life_expectancy", "infant_mortality",
        *_extra_cols,
    ]].to_dict(orient="records")

    # Equity metrics
    _by_region_agg: dict = {
        "province_count": ("province", "count"),
        "avg_life_expectancy": ("life_expectancy", "mean"),
        "avg_infant_mortality": ("infant_mortality", "mean"),
        "avg_personnel_per_1000": ("personnel_per_1000", "mean"),
        "avg_health_exp": ("health_exp_per_capita", "mean"),
        "avg_input_index": ("input_index", "mean"),
        "avg_output_index": ("output_index", "mean"),
    }
    if "hospital_beds_per_1000" in snap.columns:
        _by_region_agg["avg_hospital_beds_per_1000"] = ("hospital_beds_per_1000", "mean")
    if "physicians_per_1000" in snap.columns:
        _by_region_agg["avg_physicians_per_1000"] = ("physicians_per_1000", "mean")
    if "gdp_per_capita" in snap.columns:
        _by_region_agg["avg_gdp_per_capita"] = ("gdp_per_capita", "mean")
    if "maternal_mortality" in snap.columns:
        _by_region_agg["avg_maternal_mortality"] = ("maternal_mortality", "mean")
    if "under5_mortality" in snap.columns:
        _by_region_agg["avg_under5_mortality"] = ("under5_mortality", "mean")
    if "elderly_share" in snap.columns:
        _by_region_agg["avg_elderly_share"] = ("elderly_share", "mean")
    if "urbanization_rate" in snap.columns:
        _by_region_agg["avg_urbanization_rate"] = ("urbanization_rate", "mean")
    if "basic_insurance_rate" in snap.columns:
        _by_region_agg["avg_basic_insurance_rate"] = ("basic_insurance_rate", "mean")
    if "primary_care_density" in snap.columns:
        _by_region_agg["avg_primary_care_density"] = ("primary_care_density", "mean")
    if "hypertension_prevalence" in snap.columns:
        _by_region_agg["avg_hypertension_prevalence"] = ("hypertension_prevalence", "mean")
    if "diabetes_prevalence" in snap.columns:
        _by_region_agg["avg_diabetes_prevalence"] = ("diabetes_prevalence", "mean")
    if "obesity_prevalence" in snap.columns:
        _by_region_agg["avg_obesity_prevalence"] = ("obesity_prevalence", "mean")
    by_region = snap.groupby("region").agg(**_by_region_agg).reset_index().rename(columns={"region": "region_cn"})
    by_region["region_en"] = by_region["region_cn"].map(_PROVINCE_REGION_EN_MAP)

    gini_life_exp = _compute_gini(snap["life_expectancy"].to_numpy())
    gini_infant_mort = _compute_gini(snap["infant_mortality"].to_numpy())
    gini_exp = _compute_gini(snap["health_exp_per_capita"].to_numpy())
    ci_exp_vs_life = _compute_concentration_index(
        snap["life_expectancy"].to_numpy(),
        snap["health_exp_per_capita"].to_numpy(),
    )
    gini_maternal = _compute_gini(snap["maternal_mortality"].to_numpy()) if "maternal_mortality" in snap.columns else None
    gini_under5 = _compute_gini(snap["under5_mortality"].to_numpy()) if "under5_mortality" in snap.columns else None

    quadrant_counts = snap["quadrant"].value_counts().to_dict()

    # Lorenz curves for China provinces
    def _lorenz_curve(values: np.ndarray) -> dict:
        v = np.sort(values[np.isfinite(values) & (values > 0)])
        if len(v) == 0:
            return {"x": [], "y": [], "n": 0}
        n = len(v)
        cum_x = (np.arange(1, n + 1) / n * 100).tolist()
        cum_y = (np.cumsum(v) / v.sum() * 100).tolist()
        return {
            "x": [0.0] + [round(x, 2) for x in cum_x],
            "y": [0.0] + [round(y, 2) for y in cum_y],
            "n": n,
        }

    lorenz_exp = _lorenz_curve(snap["health_exp_per_capita"].to_numpy())
    lorenz_le = _lorenz_curve(snap["life_expectancy"].to_numpy())
    lorenz_personnel = _lorenz_curve(snap["personnel_per_1000"].to_numpy()) if "personnel_per_1000" in snap.columns else {"x": [], "y": [], "n": 0}

    # Personnel trend: use full panel
    latest_year = int(panel["year"].max())
    personnel_history = {}
    for prov in panel["province"].unique():
        prov_data = panel[panel["province"] == prov].sort_values("year")
        prov_en = _PROVINCE_EN_MAP.get(prov, prov)
        personnel_history[prov_en] = prov_data[["year", "health_personnel_wan"]].dropna().to_dict(orient="records")

    # National aggregate trend
    nat_trend = panel.groupby("year", as_index=False)["health_personnel_wan"].sum()
    national_trend = {
        "health_personnel": nat_trend.rename(columns={"health_personnel_wan": "value"}).to_dict(orient="records"),
    }

    return {
        "latest_year": latest_year,
        "provinces": gap_records,   # alias for dashboard consumption
        "resource_gap": gap_records,
        "quadrant_counts": quadrant_counts,
        "equity_metrics": {
            "gini_life_expectancy": gini_life_exp,
            "gini_infant_mortality": gini_infant_mort,
            "gini_health_expenditure": gini_exp,
            "concentration_index_exp_vs_life_expectancy": ci_exp_vs_life,
            "gini_maternal_mortality": gini_maternal,
            "gini_under5_mortality": gini_under5,
            "lorenz": {
                "health_exp": {**lorenz_exp, "label": "人均卫生支出"},
                "life_expectancy": {**lorenz_le, "label": "预期寿命"},
                "personnel_per_1000": {**lorenz_personnel, "label": "卫生人员密度"},
            },
        },
        "by_region": by_region.to_dict(orient="records"),
        "optimization": {
            "default_scenario": f"max_output_budget_100",
            "scenario_options": {
                "objectives": [
                    {"code": k, "label": v["label"], "label_en": v["label_en"]} for k, v in objectives.items()
                ],
                "budget_multipliers": budgets,
            },
            "scenarios": scenarios,
        },
        "personnel_history": personnel_history,
        "national_trend": national_trend,
    }


def _risk_display_label(risk_code: str | None, risk_factor: str | None = None) -> str:
    if risk_code and str(risk_code).strip():
        return str(risk_code)
    if risk_factor and str(risk_factor).strip():
        return RISK_LABEL_MAP.get(str(risk_factor), str(risk_factor))
    return "unknown_risk"


def build_dimension1_outputs(master: pd.DataFrame, disease: pd.DataFrame) -> dict:
    latest_year = int(master["year"].max())
    deaths = disease[disease["measure"] == "deaths"].copy()
    group_trends = (
        deaths.groupby(["iso3", "country_name", "year", "cause_group"], as_index=False)["value"]
        .sum()
        .rename(columns={"value": "deaths"})
    )
    totals = group_trends.groupby(["iso3", "year"], as_index=False)["deaths"].sum().rename(columns={"deaths": "total_deaths"})
    group_trends = group_trends.merge(totals, on=["iso3", "year"], how="left")
    group_trends["share"] = group_trends["deaths"] / group_trends["total_deaths"].replace(0, np.nan)
    export_dim1_trends(group_trends)

    latest_snapshot = master[master["year"] == latest_year].copy()
    dim1_latest = latest_snapshot[
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
        ]
    ].dropna(subset=["life_expectancy"])
    export_dim1_spatiotemporal(dim1_latest, metric="life_expectancy", year=latest_year, filename="spatiotemporal_latest.json")
    export_dim1_spatiotemporal(dim1_latest, metric="ncd_share", year=latest_year, filename=f"spatiotemporal_ncd_share_{latest_year}.json")
    export_dim1_spatiotemporal(dim1_latest, metric="communicable_share", year=latest_year, filename=f"spatiotemporal_communicable_share_{latest_year}.json")

    global_shares = (
        group_trends.groupby(["year", "cause_group"], as_index=False)["deaths"]
        .sum()
    )
    global_total = global_shares.groupby("year", as_index=False)["deaths"].sum().rename(columns={"deaths": "total"})
    global_shares = global_shares.merge(global_total, on="year", how="left")
    global_shares["share"] = global_shares["deaths"] / global_shares["total"]
    global_shares["cause_group_en"] = global_shares["cause_group"].map(_CAUSE_GROUP_EN).fillna(global_shares["cause_group"])

    fig, ax = plt.subplots(figsize=(9, 5))
    sns.lineplot(data=global_shares, x="year", y="share", hue="cause_group_en", marker="o", ax=ax)
    ax.set_title("Global Cause Structure Transition, 2000-2023")
    ax.set_ylabel("Share of deaths")
    ax.set_xlabel("Year")
    _save_figure(fig, "fig01_global_disease_transition")

    fig, ax = plt.subplots(figsize=(7, 5))
    sns.regplot(data=latest_snapshot, x="communicable_share", y="life_expectancy", scatter_kws={"s": 24, "alpha": 0.6}, ax=ax)
    ax.set_title(f"Life Expectancy vs Communicable Share, {latest_year}")
    ax.set_xlabel("Communicable death share")
    ax.set_ylabel("Life expectancy (years)")
    _save_figure(fig, "fig02_life_expectancy_vs_communicable_share")

    regression_cols = [
        "life_expectancy",
        "gdp_per_capita",
        "health_exp_pct_gdp",
        "physicians_per_1000",
        "basic_water_pct",
        "basic_sanitation_pct",
        "communicable_share",
        "ncd_share",
    ]
    reg_df = latest_snapshot[regression_cols].dropna().copy()
    reg_df["log_gdp_per_capita"] = np.log(reg_df["gdp_per_capita"].clip(lower=1))
    X = reg_df[["log_gdp_per_capita", "health_exp_pct_gdp", "physicians_per_1000", "basic_water_pct", "basic_sanitation_pct", "communicable_share", "ncd_share"]]
    X = sm.add_constant(X)
    model = sm.OLS(reg_df["life_expectancy"], X).fit()
    coef_table = pd.DataFrame(
        {
            "variable": model.params.index,
            "coef": model.params.values,
            "p_value": model.pvalues.values,
        }
    )
    _save_table(coef_table, "tab_dim1_life_expectancy_regression")

    top_life = latest_snapshot.nlargest(10, "life_expectancy")[["country_name", "life_expectancy", "ncd_share", "communicable_share"]]
    bottom_life = latest_snapshot.nsmallest(10, "life_expectancy")[["country_name", "life_expectancy", "ncd_share", "communicable_share"]]
    _save_table(top_life, "tab_dim1_top_life_expectancy")
    _save_table(bottom_life, "tab_dim1_bottom_life_expectancy")

    forecasts: list[SimpleForecastResult] = []
    for iso3 in _select_countries(master):
        country_panel = master[master["iso3"] == iso3].set_index("year")
        for indicator in ("life_expectancy", "ncd_share"):
            result = _linear_forecast(country_panel[indicator], country=iso3, indicator=indicator)
            if result is not None:
                forecasts.append(result)
    export_dim1_forecasts(forecasts)

    plot_iso = _select_countries(master)[:4]
    fig, axes = plt.subplots(2, 2, figsize=(10, 7), sharex=True)
    for ax, iso3 in zip(axes.ravel(), plot_iso):
        subset = next((item for item in forecasts if item.country == iso3 and item.indicator == "life_expectancy"), None)
        if subset is None:
            ax.axis("off")
            continue
        ax.plot(subset.historical["year"], subset.historical["value"], label="Observed", color="#1f77b4")
        ax.plot(subset.forecast["year"], subset.forecast["predicted"], label="Forecast", color="#d62728")
        ax.fill_between(subset.forecast["year"], subset.forecast["ci_lower"], subset.forecast["ci_upper"], alpha=0.2, color="#d62728")
        ax.set_title(iso3)
    axes[0, 0].legend()
    fig.suptitle("Representative Country Forecasts: Life Expectancy")
    fig.tight_layout()
    _save_figure(fig, "fig03_dim1_forecasts")

    return {
        "latest_year": latest_year,
        "global_ncd_share": float(global_shares[global_shares["year"] == latest_year].loc[lambda frame: frame["cause_group"] == "非传染性疾病", "share"].iloc[0]),
        "top_life_expectancy_country": str(top_life.iloc[0]["country_name"]),
        "bottom_life_expectancy_country": str(bottom_life.iloc[0]["country_name"]),
        "regression_r2": float(model.rsquared),
    }


def build_dimension2_outputs(master: pd.DataFrame, risk: pd.DataFrame) -> dict:
    latest_year = int(risk["year"].max())
    risk_deaths = risk[risk["measure"] == "deaths"].copy()
    paf_like = (
        risk_deaths.groupby(
            ["iso3", "country_name", "who_region", "wb_income", "year", "risk_factor", "risk_code", "cause_name"],
            as_index=False,
        )["value"]
        .sum()
        .rename(columns={"value": "attributable_deaths"})
    )
    totals = (
        paf_like.groupby(["iso3", "year"], as_index=False)["attributable_deaths"]
        .sum()
        .rename(columns={"attributable_deaths": "country_total"})
    )
    paf_like = paf_like.merge(totals, on=["iso3", "year"], how="left")
    paf_like["contribution_share"] = paf_like["attributable_deaths"] / paf_like["country_total"].replace(0, np.nan)
    paf_like["rank"] = paf_like.groupby(["iso3", "year"])["attributable_deaths"].rank(method="dense", ascending=False)
    paf_like["method"] = "attributable_share"
    paf_like["paf"] = paf_like["contribution_share"]
    export_dim2_paf(paf_like)

    latest = paf_like[paf_like["year"] == latest_year].copy()
    latest["risk_label"] = latest.apply(
        lambda row: _risk_display_label(row.get("risk_code"), row.get("risk_factor")),
        axis=1,
    )
    global_top = latest.groupby(["risk_factor", "risk_code"], as_index=False)["attributable_deaths"].sum().sort_values("attributable_deaths", ascending=False)
    global_top["risk_label"] = global_top.apply(
        lambda row: _risk_display_label(row.get("risk_code"), row.get("risk_factor")),
        axis=1,
    )
    fig, ax = plt.subplots(figsize=(9, 5))
    top10 = global_top.head(10).copy()
    sns.barplot(data=top10, x="attributable_deaths", y="risk_label", hue="risk_label", palette="crest", legend=False, ax=ax)
    ax.set_title(f"Global Leading Attributable Risks, {latest_year}")
    ax.set_xlabel("Attributable deaths")
    ax.set_ylabel("")
    _save_figure(fig, "fig04_dim2_global_risk_bar")

    region_heatmap = (
        latest.groupby(["who_region", "risk_label"], as_index=False)["contribution_share"]
        .mean()
        .pivot(index="who_region", columns="risk_label", values="contribution_share")
        .fillna(0)
    )
    fig, ax = plt.subplots(figsize=(12, 4))
    sns.heatmap(region_heatmap, cmap="YlOrRd", ax=ax)
    ax.set_title(f"WHO Region Risk Contribution Heatmap, {latest_year}")
    ax.set_xlabel("Risk factor")
    ax.set_ylabel("WHO region")
    _save_figure(fig, "fig05_dim2_region_heatmap")

    sankey_links = (
        latest[latest["risk_label"].isin(global_top.head(8)["risk_label"])]
        .groupby(["risk_label", "who_region"], as_index=False)["attributable_deaths"]
        .sum()
        .sort_values("attributable_deaths", ascending=False)
    )
    sankey_nodes = sankey_links["risk_label"].drop_duplicates().tolist() + sankey_links["who_region"].drop_duplicates().tolist()
    sankey_index = {label: idx for idx, label in enumerate(sankey_nodes)}
    sankey_payload = {
        "title": f"Risk-to-region attributable death flow, {latest_year}",
        "method": "risk_to_region_attributable_deaths",
        "nodes": sankey_nodes,
        "sources": [sankey_index[label] for label in sankey_links["risk_label"]],
        "targets": [sankey_index[label] for label in sankey_links["who_region"]],
        "values": sankey_links["attributable_deaths"].round(3).tolist(),
    }
    write_json_artifact(
        wrap_response(sankey_payload, {"year": latest_year, "top_risks": 8}),
        API_OUTPUT / "dim2" / "sankey.json",
    )
    try:
        import plotly.graph_objects as go

        sankey_fig = go.Figure(
            data=[
                go.Sankey(
                    node=dict(
                        pad=15,
                        thickness=18,
                        line=dict(color="rgba(80, 80, 80, 0.4)", width=0.5),
                        label=sankey_payload["nodes"],
                    ),
                    link=dict(
                        source=sankey_payload["sources"],
                        target=sankey_payload["targets"],
                        value=sankey_payload["values"],
                    ),
                )
            ]
        )
        sankey_fig.update_layout(title_text=sankey_payload["title"], font_size=10, height=620)
        sankey_fig.write_html(FIGURES / "fig05b_dim2_risk_region_sankey.html", include_plotlyjs="cdn")
    except Exception as exc:  # pragma: no cover - optional visualization backend
        logger.warning("Skipping Sankey HTML export: %s", exc)

    shapley_proxy = global_top.head(10).copy()
    shapley_proxy["shapley_value"] = shapley_proxy["attributable_deaths"]
    shapley_proxy["shapley_pct"] = shapley_proxy["attributable_deaths"] / shapley_proxy["attributable_deaths"].sum() * 100
    shapley_proxy = shapley_proxy.rename(columns={"risk_factor": "risk_factor_name"})
    export_dim2_shapley(
        shapley_proxy.rename(columns={"risk_factor_name": "risk_factor"})[
            ["risk_factor", "shapley_value", "shapley_pct"]
        ],
        country="global",
    )

    top_risk_codes = global_top.head(3)["risk_code"].tolist()
    scenario_years = np.arange(latest_year + 1, FORECAST_END_YEAR + 1)
    baseline_trajectories: dict[str, np.ndarray] = {}
    for risk_code in top_risk_codes:
        series = (
            paf_like[paf_like["risk_code"] == risk_code]
            .groupby("year")["attributable_deaths"]
            .sum()
            .sort_index()
        )
        forecast = _linear_forecast(series, country="global", indicator=risk_code)
        if forecast is None:
            continue
        baseline_trajectories[risk_code] = forecast.forecast.set_index("year")["predicted"].reindex(scenario_years).to_numpy()

    total_baseline = np.sum(list(baseline_trajectories.values()), axis=0)
    scenarios = {
        "A_baseline": {
            "country": "global",
            "years": scenario_years,
            "trajectories": {"total_attributable_deaths": total_baseline, **baseline_trajectories},
        },
        "B_moderate_intervention": {
            "country": "global",
            "years": scenario_years,
            "trajectories": {
                "total_attributable_deaths": total_baseline * np.linspace(1.0, 0.90, len(scenario_years)),
            },
        },
        "C_aggressive_intervention": {
            "country": "global",
            "years": scenario_years,
            "trajectories": {
                "total_attributable_deaths": total_baseline * np.linspace(1.0, 0.80, len(scenario_years)),
            },
        },
    }
    export_dim2_scenarios(scenarios)

    fig, ax = plt.subplots(figsize=(8, 5))
    for scenario_name, payload in scenarios.items():
        ax.plot(payload["years"], payload["trajectories"]["total_attributable_deaths"], label=scenario_name)
    ax.set_title("Projected Attributable Deaths Under Intervention Scenarios")
    ax.set_xlabel("Year")
    ax.set_ylabel("Attributable deaths")
    ax.legend()
    _save_figure(fig, "fig06_dim2_scenarios")

    region_priority_rows = []
    for who_region, subset in latest.groupby("who_region"):
        ordered = subset.groupby(["risk_factor", "risk_code", "risk_label"], as_index=False)["contribution_share"].mean().sort_values("contribution_share", ascending=False)
        if ordered.empty:
            continue
        top1 = ordered.iloc[0]
        top2 = ordered.iloc[1] if len(ordered) > 1 else ordered.iloc[0]
        region_priority_rows.append(
            {
                "who_region": who_region,
                "primary_risk": top1["risk_factor"],
                "primary_risk_code": top1["risk_label"],
                "primary_share": top1["contribution_share"],
                "secondary_risk": top2["risk_factor"],
                "secondary_risk_code": top2["risk_label"],
                "secondary_share": top2["contribution_share"],
                "recommended_intervention": RISK_INTERVENTIONS.get(str(top1["risk_code"]), "结合地区实际制定风险干预组合"),
            }
        )
    region_priority = pd.DataFrame(region_priority_rows).sort_values("primary_share", ascending=False)
    region_priority.to_parquet(Path(RESOURCE_PANEL).with_name("dim2_intervention_priority.parquet"), index=False)
    _save_table(region_priority, "tab_dim2_region_priority")

    return {
        "latest_year": latest_year,
        "top_global_risk": str(global_top.iloc[0]["risk_factor"]),
        "top_global_risk_deaths": float(global_top.iloc[0]["attributable_deaths"]),
    }


def build_dimension3_outputs(master: pd.DataFrame, resource_panel: pd.DataFrame, china: pd.DataFrame) -> dict:
    latest_year = int(resource_panel["year"].max())
    latest = resource_panel[resource_panel["year"] == latest_year].copy()

    # Forward-fill physicians_per_1000 and beds_per_1000 from most recent available year
    # (these metrics lag in official reports by 2-4 years)
    for _lag_col in ["physicians_per_1000", "beds_per_1000"]:
        if _lag_col not in latest.columns:
            continue
        missing_mask = latest[_lag_col].isna()
        if not missing_mask.any():
            continue
        for _backfill_yr in range(latest_year - 1, max(latest_year - 6, 2015), -1):
            _back = resource_panel[resource_panel["year"] == _backfill_yr][["iso3", _lag_col]].dropna(subset=[_lag_col])
            if _back.empty:
                continue
            _fill_map = _back.set_index("iso3")[_lag_col]
            still_missing = latest[_lag_col].isna()
            latest.loc[still_missing, _lag_col] = latest.loc[still_missing, "iso3"].map(_fill_map)
            if not latest[_lag_col].isna().any():
                break

    latest["input_index"] = pd.concat(
        [
            _standardize(latest["physicians_per_1000"]),
            _standardize(latest["beds_per_1000"]),
            _standardize(latest["health_exp_pct_gdp"]),
            _standardize(latest["health_exp_per_capita"]),
        ],
        axis=1,
    ).mean(axis=1)
    latest["output_index"] = pd.concat(
        [
            _standardize(latest["life_expectancy"]),
            _standardize(latest["infant_mortality"], invert=True),
            _standardize(latest["under5_mortality"], invert=True),
        ],
        axis=1,
    ).mean(axis=1)
    latest["theoretical_need"] = pd.concat(
        [
            _standardize(master.loc[master["year"] == latest_year, "communicable_share"]),
            _standardize(latest["infant_mortality"]),
            _standardize(latest["under5_mortality"]),
            _standardize(latest["life_expectancy"], invert=True),
        ],
        axis=1,
    ).mean(axis=1)
    latest["actual_resource"] = latest["input_index"]
    latest["gap"] = latest["actual_resource"] - latest["theoretical_need"]
    latest["gap_grade"] = pd.qcut(latest["gap"], q=5, labels=["E_严重不足", "D_不足", "C_匹配", "B_较充足", "A_富余"])
    latest["gap_grade_en"] = latest["gap_grade"].astype(str).map(_GAP_GRADE_EN).fillna(latest["gap_grade"].astype(str))

    resource_gap = latest[
        ["iso3", "country_name", "who_region", "wb_income", "year", "actual_resource", "theoretical_need", "gap", "gap_grade", "gap_grade_en"]
    ].rename(columns={"actual_resource": "actual_resource_index", "theoretical_need": "theoretical_need_index"})
    export_dim3_resource_gap(resource_gap)
    _save_table(resource_gap.sort_values("gap").head(15), "tab_dim3_most_under_resourced")

    input_median = latest["input_index"].median()
    output_median = latest["output_index"].median()
    latest["quadrant"] = np.select(
        [
            (latest["input_index"] >= input_median) & (latest["output_index"] >= output_median),
            (latest["input_index"] < input_median) & (latest["output_index"] >= output_median),
            (latest["input_index"] >= input_median) & (latest["output_index"] < output_median),
            (latest["input_index"] < input_median) & (latest["output_index"] < output_median),
        ],
        ["Q1_high_input_high_output", "Q2_low_input_high_output", "Q3_high_input_low_output", "Q4_low_input_low_output"],
        default="unclassified",
    )
    latest["efficiency"] = latest["output_index"] - latest["input_index"]
    efficiency = latest[
        ["iso3", "country_name", "who_region", "wb_income", "year", "efficiency", "quadrant", "input_index", "output_index"]
    ]
    export_dim3_efficiency(efficiency)

    fig, ax = plt.subplots(figsize=(8, 6))
    sns.scatterplot(data=efficiency, x="input_index", y="output_index", hue="quadrant", s=50, ax=ax)
    ax.axvline(input_median, color="grey", linestyle="--", linewidth=1)
    ax.axhline(output_median, color="grey", linestyle="--", linewidth=1)
    ax.set_title(f"Health Resource Input-Output Quadrants, {latest_year}")
    ax.set_xlabel("Input index")
    ax.set_ylabel("Output index")
    _save_figure(fig, "fig07_dim3_quadrant")

    _opt_cols = [c for c in ["iso3", "country_name", "who_region", "wb_income",
                             "health_exp_per_capita", "output_index", "theoretical_need",
                             "gap", "efficiency", "quadrant", "life_expectancy"] if c in latest.columns]
    optimize_base = latest[_opt_cols].dropna(subset=["health_exp_per_capita", "output_index"]).copy()
    optimize_base["health_exp_per_capita"] = optimize_base["health_exp_per_capita"].clip(lower=1)
    a_coef, b_coef = _fit_output_curve(
        optimize_base["health_exp_per_capita"].to_numpy(dtype=float),
        optimize_base["output_index"].to_numpy(dtype=float),
    )

    scenario_rows: list[dict[str, object]] = []
    default_scenario_id = _scenario_id("max_output", 1.0)
    default_allocation = pd.DataFrame()

    for objective_code, meta in _OPTIMIZATION_OBJECTIVES.items():
        for budget_multiplier in _OPTIMIZATION_BUDGETS:
            try:
                result = meta["solver"](
                    optimize_base,
                    output_col="output_index",
                    input_col="health_exp_per_capita",
                    budget_multiplier=budget_multiplier,
                )
                scenario_payload = _build_optimization_scenario(
                    optimize_base=optimize_base,
                    result=result,
                    objective=objective_code,
                    budget_multiplier=budget_multiplier,
                    a_coef=a_coef,
                    b_coef=b_coef,
                )
            except Exception as exc:
                logger.exception("Optimization scenario failed: %s / %.1f", objective_code, budget_multiplier)
                fallback_result = optimize_base.assign(
                    current=optimize_base["health_exp_per_capita"],
                    optimal=optimize_base["health_exp_per_capita"],
                    change=0.0,
                    change_pct=0.0,
                )
                scenario_payload = {
                    "scenario_id": _scenario_id(objective_code, budget_multiplier),
                    "objective": objective_code,
                    "objective_label": meta["label"],
                    "objective_description": meta["description"],
                    "budget_multiplier": float(budget_multiplier),
                    "budget_change_pct": float((budget_multiplier - 1.0) * 100.0),
                    "status": f"error: {exc}",
                    "objective_value": 0.0,
                    "summary": {
                        "country_count": int(len(fallback_result)),
                        "current_budget": float(fallback_result["current"].sum()),
                        "optimal_budget": float(fallback_result["optimal"].sum()),
                        "projected_output_current": float(np.sum(_project_output_curve(fallback_result["current"].to_numpy(dtype=float), a_coef, b_coef))),
                        "projected_output_optimal": float(np.sum(_project_output_curve(fallback_result["optimal"].to_numpy(dtype=float), a_coef, b_coef))),
                        "projected_output_gain_pct": 0.0,
                        "recipient_count": 0,
                        "donor_count": 0,
                        "top_recipients": [],
                        "top_donors": [],
                    },
                    "allocation": fallback_result[
                        [
                            "iso3",
                            "country_name",
                            "who_region",
                            "wb_income",
                            "quadrant",
                            "theoretical_need",
                            "gap",
                            "efficiency",
                            "output_index",
                            "current",
                            "optimal",
                            "change",
                            "change_pct",
                        ]
                    ].to_dict(orient="records"),
                }

            if scenario_payload["scenario_id"] == default_scenario_id:
                default_allocation = pd.DataFrame(scenario_payload["allocation"])
            scenario_rows.append(scenario_payload)

    # --- Personnel (physician density) optimization loop ---
    _pers_cols = [c for c in ["iso3", "country_name", "who_region", "wb_income",
                               "physicians_per_1000", "output_index", "theoretical_need",
                               "gap", "efficiency", "quadrant", "life_expectancy"] if c in latest.columns]
    optimize_base_pers = latest[_pers_cols].dropna(subset=["physicians_per_1000", "output_index"]).copy()
    optimize_base_pers["physicians_per_1000"] = optimize_base_pers["physicians_per_1000"].clip(lower=0.01)
    a_coef_p, b_coef_p = _fit_output_curve(
        optimize_base_pers["physicians_per_1000"].to_numpy(dtype=float),
        optimize_base_pers["output_index"].to_numpy(dtype=float),
    )

    for objective_code, meta in _OPTIMIZATION_OBJECTIVES_PERSONNEL.items():
        for budget_multiplier in _OPTIMIZATION_BUDGETS:
            try:
                result = meta["solver"](
                    optimize_base_pers,
                    output_col="output_index",
                    input_col="physicians_per_1000",
                    budget_multiplier=budget_multiplier,
                )
                scenario_payload = _build_optimization_scenario(
                    optimize_base=optimize_base_pers,
                    result=result,
                    objective=objective_code,
                    budget_multiplier=budget_multiplier,
                    a_coef=a_coef_p,
                    b_coef=b_coef_p,
                    objectives_dict=_OPTIMIZATION_OBJECTIVES_PERSONNEL,
                )
            except Exception as exc:
                logger.exception("Personnel optimization scenario failed: %s / %.1f", objective_code, budget_multiplier)
                fallback_result_p = optimize_base_pers.assign(
                    current=optimize_base_pers["physicians_per_1000"],
                    optimal=optimize_base_pers["physicians_per_1000"],
                    change=0.0,
                    change_pct=0.0,
                )
                _merge_cols_p = [c for c in ["iso3", "country_name", "who_region", "wb_income",
                                              "quadrant", "theoretical_need", "gap", "efficiency",
                                              "output_index"] if c in optimize_base_pers.columns]
                scenario_payload = {
                    "scenario_id": _scenario_id(objective_code, budget_multiplier),
                    "objective": objective_code,
                    "objective_label": meta["label"],
                    "objective_description": meta["description"],
                    "budget_multiplier": float(budget_multiplier),
                    "budget_change_pct": float((budget_multiplier - 1.0) * 100.0),
                    "status": f"error: {exc}",
                    "objective_value": 0.0,
                    "summary": {
                        "country_count": int(len(fallback_result_p)),
                        "current_budget": float(fallback_result_p["current"].sum()),
                        "optimal_budget": float(fallback_result_p["optimal"].sum()),
                        "projected_output_current": 0.0,
                        "projected_output_optimal": 0.0,
                        "projected_output_gain_pct": 0.0,
                        "recipient_count": 0,
                        "donor_count": 0,
                        "top_recipients": [],
                        "top_donors": [],
                    },
                    "allocation": fallback_result_p[_merge_cols_p + ["current", "optimal", "change", "change_pct"]].to_dict(orient="records"),
                }
            scenario_rows.append(scenario_payload)

    _all_obj_meta = {**_OPTIMIZATION_OBJECTIVES, **_OPTIMIZATION_OBJECTIVES_PERSONNEL}

    export_dim3_optimization(
        {
            "latest_year": latest_year,
            "default_scenario": default_scenario_id,
            "scenario_options": {
                "objectives": [
                    {"code": code, "label": meta["label"], "description": meta["description"]}
                    for code, meta in _all_obj_meta.items()
                ],
                "budget_multipliers": _OPTIMIZATION_BUDGETS,
            },
            "available_objectives": [
                {"code": code, "label": meta["label"], "description": meta["description"]}
                for code, meta in _all_obj_meta.items()
            ],
            "budget_options": _OPTIMIZATION_BUDGETS,
            "scenarios": scenario_rows,
        }
    )

    top_reallocation = (
        default_allocation.sort_values(["change_pct", "change"], ascending=False).head(15)
        if not default_allocation.empty
        else pd.DataFrame()
    )
    _save_table(top_reallocation, "tab_dim3_top_reallocation")

    china_staff = china[china["indicator"] == "各省近20年卫生人员数量"].copy()
    china_inst = china[china["indicator"] == "近20年各省医疗卫生机构数量"].copy()
    if not china_staff.empty and not china_inst.empty:
        china_staff["province_en"] = china_staff["province"].map(_PROVINCE_EN).fillna(china_staff["province"])
        china_inst["province_en"] = china_inst["province"].map(_PROVINCE_EN).fillna(china_inst["province"])
        latest_staff = china_staff[china_staff["year"] == china_staff["year"].max()].nlargest(5, "value")["province"].tolist()
        plot_provinces = latest_staff
        fig, axes = plt.subplots(1, 2, figsize=(12, 4), sharex=True)
        sns.lineplot(data=china_staff[china_staff["province"].isin(plot_provinces)], x="year", y="value", hue="province_en", ax=axes[0])
        axes[0].set_title("China: Health Personnel Trends in Selected Provinces")
        axes[0].set_xlabel("Year")
        axes[0].set_ylabel("Health personnel")
        sns.lineplot(data=china_inst[china_inst["province"].isin(plot_provinces)], x="year", y="value", hue="province_en", ax=axes[1])
        axes[1].set_title("China: Health Institution Trends in Selected Provinces")
        axes[1].set_xlabel("Year")
        axes[1].set_ylabel("Health institutions")
        axes[1].legend_.remove()
        _save_figure(fig, "fig08_china_province_trends")

    # --- China provincial optimization (sub-question 3: one-country redistribution) ---
    try:
        china_panel = load_china_provincial_panel()
        china_snap = build_china_latest_snapshot(china_panel)
        china_payload = _build_china_optimization_scenarios(china_snap, china_panel)
        export_dim3_china_analysis(china_payload)
        logger.info("China provincial optimization complete: %d provinces, %d scenarios",
                    len(china_snap), len(china_payload.get("optimization", {}).get("scenarios", [])))
    except Exception:
        logger.exception("China provincial optimization failed")

    # --- Global equity metrics (sub-question 2) ---
    try:
        exp_vals = latest["health_exp_per_capita"].dropna().to_numpy()
        le_vals = latest.loc[latest["health_exp_per_capita"].notna(), "life_expectancy"].to_numpy()
        gini_global_life_exp = _compute_gini(latest["life_expectancy"].dropna().to_numpy())
        gini_global_health_exp = _compute_gini(exp_vals)
        ci_exp_vs_le = _compute_concentration_index(le_vals, exp_vals)
        equity_summary = {
            "gini_life_expectancy": gini_global_life_exp,
            "gini_health_expenditure": gini_global_health_exp,
            "concentration_index_exp_vs_life_expectancy": ci_exp_vs_le,
            "by_income_group": latest.groupby("wb_income").agg(
                country_count=("iso3", "count"),
                avg_life_expectancy=("life_expectancy", "mean"),
                avg_health_exp=("health_exp_per_capita", "mean"),
                avg_input_index=("input_index", "mean"),
                avg_output_index=("output_index", "mean"),
            ).reset_index().rename(columns={"wb_income": "income_group"}).to_dict(orient="records"),
            "by_who_region": latest.groupby("who_region").agg(
                country_count=("iso3", "count"),
                avg_life_expectancy=("life_expectancy", "mean"),
                avg_health_exp=("health_exp_per_capita", "mean"),
                avg_input_index=("input_index", "mean"),
                avg_output_index=("output_index", "mean"),
            ).reset_index().rename(columns={"who_region": "region"}).to_dict(orient="records"),
        }
        write_json_artifact(
            wrap_response(equity_summary),
            API_OUTPUT / "dim3" / "equity.json",
        )
    except Exception:
        logger.exception("Global equity metrics failed")

    return {
        "latest_year": latest_year,
        "largest_shortage_country": str(resource_gap.sort_values("gap").iloc[0]["country_name"]),
        "best_quadrant_count": int((efficiency["quadrant"] == "Q2_low_input_high_output").sum()),
    }


def run_competition_pipeline() -> dict:
    """Generate figures, tables, and JSON artifacts for all dimensions."""
    _ensure_dirs()
    master = load_master_panel()
    resource_panel = load_resource_panel()
    disease = load_disease_mortality_long()
    risk = load_risk_attribution_long()
    china = load_china_panel()

    summary = {
        "dimension1": build_dimension1_outputs(master, disease),
        "dimension2": build_dimension2_outputs(master, risk),
        "dimension3": build_dimension3_outputs(master, resource_panel, china),
    }

    export_metadata_countries(master)
    export_metadata_indicators(
        [
            {
                "code": code,
                "name": spec["label"],
                "description": f"{spec['label']}（候选原始指标：{', '.join(spec['candidates'])}）",
                "dimension": spec["dimension"],
                "unit": spec["unit"],
            }
            for code, spec in INDICATOR_SPECS.items()
        ]
    )
    export_ghri_unavailable()
    write_json_artifact(
        wrap_response(summary, query_params={"source": "competition_pipeline"}),
        API_OUTPUT / "metadata" / "summary.json",
    )
    _write_summary(summary)
    logger.info("Competition pipeline finished.")
    return summary


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(levelname)s | %(message)s")
    run_competition_pipeline()
