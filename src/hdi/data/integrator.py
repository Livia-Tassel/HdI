"""Panel assembly and integration: build master_panel.parquet."""

from __future__ import annotations

import logging

import pandas as pd

from hdi.config import (
    INTERIM,
    MASTER_PANEL,
    CHINA_PANEL,
    PROCESSED,
    PANEL_KEY_GLOBAL,
    PANEL_KEY_CHINA,
    YEAR_MIN,
    YEAR_MAX,
)
from hdi.data.loaders import (
    load_disease_mortality,
    load_risk_factors,
    load_nutrition_population,
    load_socioeconomic,
    load_china_health,
    load_ihme_gbd,
    load_worldbank_wdi,
    load_undp_hdi,
    load_owid,
)
from hdi.data.cleaners import (
    clean_country_year_dataset,
    clean_disease_mortality,
    clean_risk_factors,
    clean_nutrition_population,
    clean_socioeconomic,
    clean_china_health,
    interpolate_gaps,
    add_who_region,
    add_wb_income,
    learn_metadata_maps,
)

logger = logging.getLogger(__name__)


def _save_interim(df: pd.DataFrame, name: str) -> None:
    """Save a cleaned dataset to interim storage."""
    INTERIM.mkdir(parents=True, exist_ok=True)
    path = INTERIM / f"{name}.parquet"
    df.to_parquet(path, index=False)
    logger.info("Saved interim: %s (%d rows, %d cols)", path.name, len(df), len(df.columns))


def _merge_panel(
    left: pd.DataFrame,
    right: pd.DataFrame,
    keys: list[str],
    suffixes: tuple[str, str] = ("", "_dup"),
) -> pd.DataFrame:
    """Outer-merge two panels on keys, dropping duplicate columns."""
    merged = left.merge(right, on=keys, how="outer", suffixes=suffixes)
    dup_cols = [c for c in merged.columns if c.endswith("_dup")]
    if dup_cols:
        # prefer left values, fill with right
        for dc in dup_cols:
            orig = dc.replace("_dup", "")
            if orig in merged.columns:
                merged[orig] = merged[orig].fillna(merged[dc])
        merged = merged.drop(columns=dup_cols)
    return merged


def _collapse_to_panel(
    df: pd.DataFrame,
    keys: list[str],
    dataset_name: str,
) -> pd.DataFrame:
    """Collapse duplicate key rows before panel merges to avoid cartesian blow-ups."""
    if df.empty or any(key not in df.columns for key in keys):
        return df

    dup_mask = df.duplicated(keys, keep=False)
    if not dup_mask.any():
        return df

    numeric_cols = [
        col
        for col in df.columns
        if col not in keys and pd.api.types.is_numeric_dtype(df[col])
    ]
    other_cols = [col for col in df.columns if col not in keys and col not in numeric_cols]

    agg_spec = {col: "mean" for col in numeric_cols}
    agg_spec.update({col: "first" for col in other_cols})
    if not agg_spec:
        return df[keys].drop_duplicates().reset_index(drop=True)

    collapsed = (
        df.groupby(keys, dropna=False)
        .agg(agg_spec)
        .reset_index()
    )
    logger.warning(
        "Collapsed %s from %d rows to %d unique %s rows before merge.",
        dataset_name,
        len(df),
        len(collapsed),
        "/".join(keys),
    )
    return collapsed


def build_master_panel() -> pd.DataFrame:
    """Build the global country-year master panel from all data sources.

    Pipeline:
    1. Load & clean each provided dataset -> save to interim
    2. Load & clean each external dataset -> save to interim
    3. Merge all on (iso3, year)
    4. Interpolate small gaps
    5. Add metadata (WHO region, WB income)
    6. Save to processed/master_panel.parquet
    """
    logger.info("=== Building master panel ===")
    keys = PANEL_KEY_GLOBAL
    panel = pd.DataFrame()

    # Step 1: Provided datasets
    datasets = [
        ("disease_mortality", load_disease_mortality, clean_disease_mortality),
        ("risk_factors", load_risk_factors, clean_risk_factors),
        ("nutrition_population", load_nutrition_population, clean_nutrition_population),
        ("socioeconomic", load_socioeconomic, clean_socioeconomic),
    ]

    for name, loader, cleaner in datasets:
        try:
            raw = loader()
            if raw.empty:
                logger.warning("Empty dataset: %s (skipping)", name)
                continue
            cleaned = cleaner(raw)
            learn_metadata_maps(cleaned)
            _save_interim(cleaned, name)
            panel_ready = _collapse_to_panel(cleaned, keys, name)
            if "iso3" in panel_ready.columns and "year" in panel_ready.columns:
                if panel.empty:
                    panel = panel_ready
                else:
                    panel = _merge_panel(panel, panel_ready, keys)
            logger.info("Integrated: %s -> panel shape %s", name, panel.shape)
        except Exception as e:
            logger.error("Failed to process %s: %s", name, e)

    # Step 2: External datasets
    external_datasets = [
        ("ihme_gbd", load_ihme_gbd),
        ("worldbank_wdi", load_worldbank_wdi),
        ("undp_hdi", load_undp_hdi),
        ("owid", load_owid),
    ]

    for name, loader in external_datasets:
        try:
            raw = loader()
            if raw.empty:
                logger.warning("Empty external dataset: %s (skipping)", name)
                continue
            cleaned = clean_country_year_dataset(raw)
            learn_metadata_maps(cleaned)
            _save_interim(cleaned, f"ext_{name}")
            panel_ready = _collapse_to_panel(cleaned, keys, f"ext_{name}")
            if "iso3" in panel_ready.columns and "year" in panel_ready.columns:
                if panel.empty:
                    panel = panel_ready
                else:
                    panel = _merge_panel(panel, panel_ready, keys)
            logger.info("Integrated external: %s -> panel shape %s", name, panel.shape)
        except Exception as e:
            logger.error("Failed to load external %s: %s", name, e)

    if panel.empty:
        logger.error("No data loaded. Check data/raw/ directories.")
        return panel

    # Step 3: Filter to analysis window
    if "year" in panel.columns:
        panel = panel[
            (panel["year"] >= YEAR_MIN) & (panel["year"] <= YEAR_MAX)
        ]

    # Step 4: Interpolate small gaps
    numeric_cols = panel.select_dtypes(include="number").columns.tolist()
    value_cols = [c for c in numeric_cols if c != "year"]
    if value_cols and "iso3" in panel.columns:
        panel = panel.sort_values(keys)
        panel = interpolate_gaps(panel, group_cols=["iso3"], value_cols=value_cols)

    # Step 5: Metadata
    panel = add_who_region(panel)
    panel = add_wb_income(panel)

    # Step 6: Save
    PROCESSED.mkdir(parents=True, exist_ok=True)
    panel.to_parquet(MASTER_PANEL, index=False)
    logger.info(
        "Master panel saved: %s (%d rows, %d cols)",
        MASTER_PANEL, len(panel), len(panel.columns),
    )
    return panel


def build_china_panel() -> pd.DataFrame:
    """Build the China province-year panel from Dataset 5."""
    logger.info("=== Building China panel ===")

    try:
        raw = load_china_health()
        if raw.empty:
            logger.warning("China health dataset is empty.")
            return raw
        cleaned = clean_china_health(raw)
        _save_interim(cleaned, "china_health")
    except Exception as e:
        logger.error("Failed to load China health data: %s", e)
        return pd.DataFrame()

    panel = cleaned
    if "province" in panel.columns and "year" in panel.columns:
        panel = panel.sort_values(PANEL_KEY_CHINA)
        numeric_cols = panel.select_dtypes(include="number").columns.tolist()
        value_cols = [c for c in numeric_cols if c != "year"]
        if value_cols:
            panel = interpolate_gaps(
                panel, group_cols=["province"], value_cols=value_cols
            )

    PROCESSED.mkdir(parents=True, exist_ok=True)
    panel.to_parquet(CHINA_PANEL, index=False)
    logger.info(
        "China panel saved: %s (%d rows, %d cols)",
        CHINA_PANEL, len(panel), len(panel.columns),
    )
    return panel


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(levelname)s | %(message)s")
    build_master_panel()
    build_china_panel()
