"""Dataset loading functions for all provided and external data sources."""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Optional

import pandas as pd

from hdi.config import (
    DS_CHINA_HEALTH,
    DS_DISEASE_MORTALITY,
    DS_NUTRITION_POP,
    DS_RISK_FACTORS,
    DS_SOCIOECONOMIC,
    EXT_IHME,
    EXT_OWID,
    EXT_UNDP,
    EXT_WB,
    EXT_WHO,
    INTERIM,
    MASTER_PANEL,
    CHINA_PANEL,
)

logger = logging.getLogger(__name__)


def _read_auto(path: Path, **kwargs) -> pd.DataFrame:
    """Read CSV or Excel file based on extension."""
    suffix = path.suffix.lower()
    if suffix == ".csv":
        return pd.read_csv(path, **kwargs)
    if suffix in (".xls", ".xlsx"):
        if "sheet_name" in kwargs:
            return pd.read_excel(path, **kwargs)

        workbook = pd.read_excel(path, sheet_name=None, **kwargs)
        if isinstance(workbook, dict):
            if len(workbook) == 1:
                return next(iter(workbook.values()))

            frames = []
            for sheet_name, frame in workbook.items():
                frame = frame.copy()
                frame["_source_sheet"] = sheet_name
                frames.append(frame)
            return pd.concat(frames, ignore_index=True)
        return workbook
    if suffix == ".parquet":
        return pd.read_parquet(path, **kwargs)
    raise ValueError(f"Unsupported file format: {suffix}")


def _iter_tabular_files(directory: Path) -> list[Path]:
    if not directory.exists():
        return []

    files = [
        path
        for path in directory.rglob("*")
        if path.is_file()
        and not path.name.startswith(".")
        and path.suffix.lower() in (".csv", ".xls", ".xlsx", ".parquet")
    ]
    return sorted(files)


def _load_dir(directory: Path, **kwargs) -> pd.DataFrame:
    """Load and concatenate all tabular files in a directory tree."""
    frames = []
    if not directory.exists():
        logger.warning("Directory not found: %s", directory)
        return pd.DataFrame()

    for path in _iter_tabular_files(directory):
        logger.info("Loading %s", path.relative_to(directory))
        frame = _read_auto(path, **kwargs)
        if frame.empty:
            continue
        frame = frame.copy()
        frame["_source_file"] = path.relative_to(directory).as_posix()
        frames.append(frame)

    if not frames:
        logger.warning("No data files found in %s", directory)
        return pd.DataFrame()
    return pd.concat(frames, ignore_index=True)


# ── Provided datasets ────────────────────────────────────────────────────────

def load_disease_mortality(**kwargs) -> pd.DataFrame:
    """Load global disease and mortality data (Dataset 1)."""
    return _load_dir(DS_DISEASE_MORTALITY, **kwargs)


def load_risk_factors(**kwargs) -> pd.DataFrame:
    """Load risk factor exposure data (Dataset 2)."""
    return _load_dir(DS_RISK_FACTORS, **kwargs)


def load_nutrition_population(**kwargs) -> pd.DataFrame:
    """Load nutrition and population data (Dataset 3)."""
    return _load_dir(DS_NUTRITION_POP, **kwargs)


def load_socioeconomic(**kwargs) -> pd.DataFrame:
    """Load socioeconomic indicators (Dataset 4)."""
    return _load_dir(DS_SOCIOECONOMIC, **kwargs)


def load_china_health(**kwargs) -> pd.DataFrame:
    """Load China provincial health data (Dataset 5)."""
    return _load_dir(DS_CHINA_HEALTH, **kwargs)


# ── External datasets ────────────────────────────────────────────────────────

def load_ihme_gbd(**kwargs) -> pd.DataFrame:
    """Load IHME Global Burden of Disease data."""
    return _load_dir(EXT_IHME, **kwargs)


def load_who_ghe(**kwargs) -> pd.DataFrame:
    """Load WHO Global Health Estimates."""
    return _load_dir(EXT_WHO, **kwargs)


def load_worldbank_wdi(
    indicators: Optional[list[str]] = None,
    years: Optional[range] = None,
) -> pd.DataFrame:
    """Load World Bank WDI data.

    If cached parquet exists, load from disk. Otherwise, try wbgapi.
    """
    cache = EXT_WB / "wdi_panel.parquet"
    if cache.exists():
        df = pd.read_parquet(cache)
        if years and "year" in df.columns:
            df = df[df["year"].isin(list(years))]
        if indicators:
            cols = ["iso3", "year"] + [c for c in indicators if c in df.columns]
            df = df[cols]
        return df

    df = _load_dir(EXT_WB, **{})
    if years and "year" in df.columns:
        df = df[df["year"].isin(list(years))]
    if indicators:
        cols = ["iso3", "year"] + [c for c in indicators if c in df.columns]
        available = [col for col in cols if col in df.columns]
        if available:
            df = df[available]
    return df


def load_undp_hdi(**kwargs) -> pd.DataFrame:
    """Load UNDP Human Development Index data."""
    return _load_dir(EXT_UNDP, **kwargs)


def load_owid(**kwargs) -> pd.DataFrame:
    """Load Our World in Data indicators."""
    return _load_dir(EXT_OWID, **kwargs)


# ── Processed panels ─────────────────────────────────────────────────────────

def load_master_panel() -> pd.DataFrame:
    """Load the assembled country-year master panel."""
    if not MASTER_PANEL.exists():
        raise FileNotFoundError(
            f"Master panel not found at {MASTER_PANEL}. "
            "Run the data pipeline first (make data)."
        )
    return pd.read_parquet(MASTER_PANEL)


def load_china_panel() -> pd.DataFrame:
    """Load the assembled China province-year panel."""
    if not CHINA_PANEL.exists():
        raise FileNotFoundError(
            f"China panel not found at {CHINA_PANEL}. "
            "Run the data pipeline first (make data)."
        )
    return pd.read_parquet(CHINA_PANEL)


def load_interim(name: str) -> pd.DataFrame:
    """Load an interim cleaned dataset by name."""
    path = INTERIM / f"{name}.parquet"
    if not path.exists():
        raise FileNotFoundError(f"Interim dataset not found: {path}")
    return pd.read_parquet(path)
