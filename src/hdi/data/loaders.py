"""Dataset loading helpers for raw, interim, and processed artifacts."""

from __future__ import annotations

import logging
from pathlib import Path

import pandas as pd

from hdi.config import (
    API_OUTPUT,
    CHINA_PANEL,
    DS_CHINA_HEALTH,
    DS_DISEASE_MORTALITY,
    DS_NUTRITION_POP,
    DS_RISK_FACTORS,
    DS_SOCIOECONOMIC,
    INTERIM,
    MASTER_PANEL,
    PROCESSED,
    RESOURCE_PANEL,
)

logger = logging.getLogger(__name__)


def _read_csv(path: Path, **kwargs) -> pd.DataFrame:
    if not path.exists():
        logger.warning("Missing file: %s", path)
        return pd.DataFrame()
    return pd.read_csv(path, **kwargs)


def _read_dir_csvs(directory: Path) -> pd.DataFrame:
    if not directory.exists():
        logger.warning("Missing directory: %s", directory)
        return pd.DataFrame()

    frames = []
    for path in sorted(directory.rglob("*.csv")):
        if path.name.startswith("."):
            continue
        frame = pd.read_csv(path)
        if frame.empty:
            continue
        frame = frame.copy()
        frame["_source_file"] = path.relative_to(directory).as_posix()
        frames.append(frame)
    if not frames:
        return pd.DataFrame()
    return pd.concat(frames, ignore_index=True)


def load_disease_mortality() -> pd.DataFrame:
    """Load raw dataset 1."""
    return _read_dir_csvs(DS_DISEASE_MORTALITY)


def load_risk_factors() -> pd.DataFrame:
    """Load raw dataset 2."""
    return _read_dir_csvs(DS_RISK_FACTORS)


def load_nutrition_population() -> pd.DataFrame:
    """Load raw dataset 3 main table."""
    path = DS_NUTRITION_POP / "全球各国健康营养和人口统计数据" / "WB_HNP.csv"
    df = _read_csv(path)
    if not df.empty:
        df["_source_file"] = path.name
    return df


def load_nutrition_glossary() -> pd.DataFrame:
    path = DS_NUTRITION_POP / "全球各国健康营养和人口统计数据" / "Glossary-健康营养与人口统计.csv"
    return _read_csv(path)


def load_socioeconomic() -> pd.DataFrame:
    """Load raw dataset 4 main indicator table."""
    path = DS_SOCIOECONOMIC / "WDI_CSV" / "WDICSV.csv"
    df = _read_csv(path)
    if not df.empty:
        df["_source_file"] = path.name
    return df


def load_wdi_country_metadata() -> pd.DataFrame:
    path = DS_SOCIOECONOMIC / "WDI_CSV" / "WDICountry.csv"
    return _read_csv(path)


def load_china_health() -> pd.DataFrame:
    """Load raw dataset 5."""
    return _read_dir_csvs(DS_CHINA_HEALTH)


def load_ihme_gbd() -> pd.DataFrame:
    return pd.DataFrame()


def load_who_ghe() -> pd.DataFrame:
    return pd.DataFrame()


def load_worldbank_wdi() -> pd.DataFrame:
    return pd.DataFrame()


def load_undp_hdi() -> pd.DataFrame:
    return pd.DataFrame()


def load_owid() -> pd.DataFrame:
    return pd.DataFrame()


def load_interim(name: str) -> pd.DataFrame:
    path = INTERIM / f"{name}.parquet"
    if not path.exists():
        raise FileNotFoundError(f"Interim dataset not found: {path}")
    return pd.read_parquet(path)


def load_disease_mortality_long() -> pd.DataFrame:
    return load_interim("disease_mortality")


def load_risk_attribution_long() -> pd.DataFrame:
    return load_interim("risk_factors")


def load_hnp_long() -> pd.DataFrame:
    return load_interim("nutrition_population")


def load_wdi_long() -> pd.DataFrame:
    return load_interim("socioeconomic")


def load_master_panel() -> pd.DataFrame:
    if not MASTER_PANEL.exists():
        raise FileNotFoundError(f"Master panel not found: {MASTER_PANEL}")
    return pd.read_parquet(MASTER_PANEL)


def load_resource_panel() -> pd.DataFrame:
    if not RESOURCE_PANEL.exists():
        raise FileNotFoundError(f"Resource panel not found: {RESOURCE_PANEL}")
    return pd.read_parquet(RESOURCE_PANEL)


def load_china_panel() -> pd.DataFrame:
    if not CHINA_PANEL.exists():
        raise FileNotFoundError(f"China panel not found: {CHINA_PANEL}")
    return pd.read_parquet(CHINA_PANEL)


def load_paf_results() -> pd.DataFrame:
    path = API_OUTPUT / "dim2" / "paf.json"
    if not path.exists():
        return pd.DataFrame()
    data = pd.read_json(path)
    if "data" in data.columns:
        return pd.DataFrame(data["data"].iloc[0])
    return data


def load_intervention_db() -> pd.DataFrame:
    path = PROCESSED / "dim2_intervention_priority.parquet"
    if path.exists():
        return pd.read_parquet(path)
    return pd.DataFrame()
