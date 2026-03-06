"""Feature transformations and engineering."""

from __future__ import annotations

import numpy as np
import pandas as pd
from sklearn.preprocessing import MinMaxScaler, StandardScaler


def log_transform(df: pd.DataFrame, columns: list[str]) -> pd.DataFrame:
    """Apply log(1+x) transformation to specified columns."""
    df = df.copy()
    for col in columns:
        if col in df.columns:
            df[f"log_{col}"] = np.log1p(df[col].clip(lower=0))
    return df


def per_capita(
    df: pd.DataFrame,
    numerator: str,
    denominator: str = "population",
    scale: float = 1.0,
    name: str | None = None,
) -> pd.DataFrame:
    """Compute per-capita (or per-1000, etc.) ratio."""
    df = df.copy()
    target = name or f"{numerator}_pc"
    df[target] = (df[numerator] / df[denominator]) * scale
    return df


def growth_rate(
    df: pd.DataFrame,
    col: str,
    group_col: str = "iso3",
    periods: int = 1,
) -> pd.DataFrame:
    """Compute year-over-year growth rate within groups."""
    df = df.copy()
    df[f"{col}_growth"] = df.groupby(group_col)[col].pct_change(periods=periods)
    return df


def lag_variable(
    df: pd.DataFrame,
    col: str,
    group_col: str = "iso3",
    n_lags: int = 1,
) -> pd.DataFrame:
    """Create lagged version of a variable within groups."""
    df = df.copy()
    for lag in range(1, n_lags + 1):
        df[f"{col}_lag{lag}"] = df.groupby(group_col)[col].shift(lag)
    return df


def rolling_mean(
    df: pd.DataFrame,
    col: str,
    group_col: str = "iso3",
    window: int = 5,
) -> pd.DataFrame:
    """Compute rolling mean within groups."""
    df = df.copy()
    df[f"{col}_rm{window}"] = df.groupby(group_col)[col].transform(
        lambda s: s.rolling(window, min_periods=1).mean()
    )
    return df


def normalize_minmax(
    df: pd.DataFrame, columns: list[str]
) -> tuple[pd.DataFrame, MinMaxScaler]:
    """Min-max normalize columns to [0, 1]."""
    df = df.copy()
    scaler = MinMaxScaler()
    df[columns] = scaler.fit_transform(df[columns])
    return df, scaler


def normalize_zscore(
    df: pd.DataFrame, columns: list[str]
) -> tuple[pd.DataFrame, StandardScaler]:
    """Z-score standardize columns."""
    df = df.copy()
    scaler = StandardScaler()
    df[columns] = scaler.fit_transform(df[columns])
    return df, scaler


def create_interaction(
    df: pd.DataFrame, col1: str, col2: str
) -> pd.DataFrame:
    """Create an interaction term between two columns."""
    df = df.copy()
    df[f"{col1}_x_{col2}"] = df[col1] * df[col2]
    return df


def bin_variable(
    df: pd.DataFrame,
    col: str,
    bins: int | list[float] = 5,
    labels: list[str] | None = None,
) -> pd.DataFrame:
    """Bin a continuous variable into categories."""
    df = df.copy()
    df[f"{col}_bin"] = pd.cut(df[col], bins=bins, labels=labels)
    return df
