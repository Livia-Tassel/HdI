"""Build cleaned interim datasets and processed analysis panels."""

from __future__ import annotations

import logging
from collections import OrderedDict

import pandas as pd

from hdi.config import (
    CHINA_PANEL,
    INDICATOR_SPECS,
    INTERIM,
    MASTER_PANEL,
    PANEL_KEY_CHINA,
    PANEL_KEY_GLOBAL,
    PROCESSED,
    RESOURCE_PANEL,
)
from hdi.data.cleaners import (
    clean_china_health,
    clean_disease_mortality,
    clean_nutrition_population,
    clean_risk_factors,
    clean_socioeconomic,
    interpolate_gaps,
)
from hdi.data.loaders import (
    load_china_health,
    load_disease_mortality,
    load_nutrition_population,
    load_risk_factors,
    load_socioeconomic,
)
from hdi.data.validators import validate_china_panel, validate_master_panel

logger = logging.getLogger(__name__)

_KEY_CAUSES = OrderedDict(
    [
        ("心血管疾病", "cardiovascular_deaths"),
        ("肿瘤", "cancer_deaths"),
        ("糖尿病和肾病", "diabetes_kidney_deaths"),
        ("慢性呼吸系统疾病", "respiratory_chronic_deaths"),
        ("孕产妇和新生儿疾病", "maternal_neonatal_deaths"),
    ]
)

_RESOURCE_COLUMNS = [
    "country_name",
    "who_region",
    "wb_income",
    "life_expectancy",
    "infant_mortality",
    "under5_mortality",
    "adult_mortality_male",
    "adult_mortality_female",
    "physicians_per_1000",
    "beds_per_1000",
    "nurses_per_1000",
    "health_exp_pct_gdp",
    "health_exp_per_capita",
    "gdp_per_capita",
    "basic_water_pct",
    "basic_sanitation_pct",
    "measles_immunization_pct",
]


def _save_interim(name: str, df: pd.DataFrame) -> None:
    INTERIM.mkdir(parents=True, exist_ok=True)
    path = INTERIM / f"{name}.parquet"
    df.to_parquet(path, index=False)
    logger.info("Saved interim %s with %d rows", path.name, len(df))


def _disease_features(disease_long: pd.DataFrame) -> pd.DataFrame:
    deaths = disease_long[disease_long["measure"] == "deaths"].copy()
    grouped = (
        deaths.groupby(["iso3", "year", "cause_group"], as_index=False)["value"]
        .sum()
        .pivot(index=PANEL_KEY_GLOBAL, columns="cause_group", values="value")
        .reset_index()
        .rename_axis(columns=None)
        .rename(
            columns={
                "传染性疾病": "communicable_deaths",
                "非传染性疾病": "ncd_deaths",
                "伤害": "injury_deaths",
            }
        )
    )

    total = (
        deaths.groupby(PANEL_KEY_GLOBAL, as_index=False)["value"]
        .sum()
        .rename(columns={"value": "total_deaths"})
    )

    key_cause = (
        deaths[deaths["cause_name"].isin(_KEY_CAUSES)]
        .groupby(["iso3", "year", "cause_name"], as_index=False)["value"]
        .sum()
        .pivot(index=PANEL_KEY_GLOBAL, columns="cause_name", values="value")
        .reset_index()
        .rename_axis(columns=None)
        .rename(columns=_KEY_CAUSES)
    )

    meta = (
        deaths.groupby(PANEL_KEY_GLOBAL, as_index=False)
        .agg(
            country_name=("country_name", "first"),
            who_region=("who_region", "first"),
            wb_income=("wb_income", "first"),
        )
    )

    panel = meta.merge(total, on=PANEL_KEY_GLOBAL, how="left")
    panel = panel.merge(grouped, on=PANEL_KEY_GLOBAL, how="left")
    panel = panel.merge(key_cause, on=PANEL_KEY_GLOBAL, how="left")

    for col in ("communicable_deaths", "ncd_deaths", "injury_deaths"):
        if col not in panel.columns:
            panel[col] = pd.NA

    denominator = panel["total_deaths"].replace(0, pd.NA)
    panel["communicable_share"] = panel["communicable_deaths"] / denominator
    panel["ncd_share"] = panel["ncd_deaths"] / denominator
    panel["injury_share"] = panel["injury_deaths"] / denominator
    return panel


def _indicator_wide(hnp_long: pd.DataFrame, wdi_long: pd.DataFrame) -> pd.DataFrame:
    combined = pd.concat(
        [
            hnp_long.assign(source_priority=0),
            wdi_long.assign(source_priority=1),
        ],
        ignore_index=True,
    )
    combined = combined.dropna(subset=["iso3", "year", "indicator_code"])

    base = combined[PANEL_KEY_GLOBAL].drop_duplicates().sort_values(PANEL_KEY_GLOBAL)
    wide = base.copy()

    for canonical, spec in INDICATOR_SPECS.items():
        candidates = spec["candidates"]
        subset = combined[combined["indicator_code"].isin(candidates)].copy()
        if subset.empty:
            continue
        order = {code: idx for idx, code in enumerate(candidates)}
        subset["candidate_order"] = subset["indicator_code"].map(order).fillna(len(order))
        subset = subset.sort_values(
            ["iso3", "year", "source_priority", "candidate_order"]
        ).drop_duplicates(PANEL_KEY_GLOBAL, keep="first")
        subset = subset[PANEL_KEY_GLOBAL + ["value"]].rename(columns={"value": canonical})
        wide = wide.merge(subset, on=PANEL_KEY_GLOBAL, how="left")

    return wide


def build_master_panel() -> pd.DataFrame:
    """Build interim tables and the global country-year master panel."""
    logger.info("Building cleaned interim tables and master panel")
    disease = clean_disease_mortality(load_disease_mortality())
    risk = clean_risk_factors(load_risk_factors())
    hnp = clean_nutrition_population(load_nutrition_population())
    wdi = clean_socioeconomic(load_socioeconomic())

    _save_interim("disease_mortality", disease)
    _save_interim("risk_factors", risk)
    _save_interim("nutrition_population", hnp)
    _save_interim("socioeconomic", wdi)

    master = _disease_features(disease)
    indicators = _indicator_wide(hnp, wdi)
    master = master.merge(indicators, on=PANEL_KEY_GLOBAL, how="left")

    numeric_cols = [
        col
        for col in master.columns
        if col not in (*PANEL_KEY_GLOBAL, "country_name", "who_region", "wb_income")
        and pd.api.types.is_numeric_dtype(master[col])
    ]
    if numeric_cols:
        master = interpolate_gaps(master.sort_values(PANEL_KEY_GLOBAL), ["iso3"], numeric_cols)

    validate_master_panel(master)
    PROCESSED.mkdir(parents=True, exist_ok=True)
    master.to_parquet(MASTER_PANEL, index=False)
    logger.info("Saved master panel: %s", MASTER_PANEL)

    resource_cols = [*PANEL_KEY_GLOBAL, *[col for col in _RESOURCE_COLUMNS if col in master.columns]]
    resource_panel = master[resource_cols].copy()
    resource_panel.to_parquet(RESOURCE_PANEL, index=False)
    logger.info("Saved resource panel: %s", RESOURCE_PANEL)
    return master


def build_china_panel() -> pd.DataFrame:
    """Build the China province-year panel."""
    china = clean_china_health(load_china_health())
    _save_interim("china_health", china)
    validate_china_panel(china)
    PROCESSED.mkdir(parents=True, exist_ok=True)
    china.to_parquet(CHINA_PANEL, index=False)
    logger.info("Saved China panel: %s", CHINA_PANEL)
    return china


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(levelname)s | %(message)s")
    build_master_panel()
    build_china_panel()
