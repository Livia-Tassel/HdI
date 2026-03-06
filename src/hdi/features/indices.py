"""GHRI (Global Health Resilience Index) composite index construction."""

from __future__ import annotations

import logging

import numpy as np
import pandas as pd
from sklearn.decomposition import PCA
from sklearn.preprocessing import MinMaxScaler

from hdi.config import GHRI_PILLARS

logger = logging.getLogger(__name__)


# ── Pillar indicator mappings ────────────────────────────────────────────────

PILLAR_INDICATORS = {
    "disease_burden": {
        "inv_daly_rate": ("daly_rate", True),   # (source_col, invert?)
        "inv_yll_rate": ("yll_rate", True),
        "inv_yld_rate": ("yld_rate", True),
    },
    "risk_factor_control": {
        "inv_smoking_prev": ("smoking_prev", True),
        "inv_pm25": ("pm25_annual_mean", True),
        "basic_water_pct": ("basic_water_pct", False),
        "basic_sanitation_pct": ("basic_sanitation_pct", False),
    },
    "health_system_capacity": {
        "physicians_per_1000": ("physicians_per_1000", False),
        "hospital_beds_per_1000": ("hospital_beds_per_1000", False),
        "health_exp_pct_gdp": ("health_exp_pct_gdp", False),
        "measles_immunization_pct": ("measles_immunization_pct", False),
    },
    "socioeconomic_foundation": {
        "log_gdp_pc": ("gdp_pc_ppp", False),  # log-transformed during prep
        "literacy_rate": ("literacy_rate", False),
        "urban_pct": ("urban_pct", False),
    },
    "resilience_equity": {
        "inv_gini": ("gini_index", True),
        "life_expectancy": ("life_expectancy", False),
    },
}


def _prepare_pillar_data(
    df: pd.DataFrame, pillar: str
) -> pd.DataFrame:
    """Extract and transform indicators for a given pillar."""
    indicators = PILLAR_INDICATORS[pillar]
    result = df[["iso3", "year"]].copy()

    for target_col, (source_col, invert) in indicators.items():
        if source_col not in df.columns:
            logger.warning("Missing indicator %s for pillar %s", source_col, pillar)
            result[target_col] = np.nan
            continue

        values = df[source_col].copy()

        # Special: log-transform GDP
        if target_col == "log_gdp_pc":
            values = np.log1p(values)

        # Invert if higher is worse
        if invert:
            valid_max = values.max()
            if pd.notna(valid_max) and valid_max > 0:
                values = valid_max - values

        result[target_col] = values

    return result


def _pca_weights(data: np.ndarray) -> np.ndarray:
    """Derive PCA-based weights from first principal component loadings."""
    if data.shape[1] == 0:
        return np.array([])
    # Handle missing data: use only complete rows for PCA
    mask = ~np.isnan(data).any(axis=1)
    if mask.sum() < max(10, data.shape[1] + 1):
        # Not enough complete rows; use equal weights
        n = data.shape[1]
        return np.ones(n) / n

    pca = PCA(n_components=1)
    pca.fit(data[mask])
    loadings = np.abs(pca.components_[0])
    weights = loadings / loadings.sum()
    return weights


def compute_pillar_scores(
    df: pd.DataFrame, year: int | None = None
) -> pd.DataFrame:
    """Compute GHRI pillar scores for all countries.

    Parameters
    ----------
    df : master panel DataFrame
    year : if specified, compute for a single year; otherwise latest available

    Returns
    -------
    DataFrame with columns: iso3, year, + one column per pillar
    """
    if year is not None:
        df = df[df["year"] == year].copy()
    else:
        # Use latest year per country
        df = df.sort_values("year").groupby("iso3").last().reset_index()

    pillar_scores = df[["iso3", "year"]].copy()

    for pillar in GHRI_PILLARS:
        pillar_data = _prepare_pillar_data(df, pillar)
        indicator_cols = [
            c for c in pillar_data.columns if c not in ("iso3", "year")
        ]

        if not indicator_cols:
            pillar_scores[pillar] = np.nan
            continue

        # Min-max normalize each indicator
        scaler = MinMaxScaler()
        values = pillar_data[indicator_cols].values
        # Only fit on non-NaN values
        mask = ~np.isnan(values).all(axis=1)
        if mask.sum() == 0:
            pillar_scores[pillar] = np.nan
            continue

        normalized = np.full_like(values, np.nan)
        for j in range(values.shape[1]):
            col_vals = values[:, j]
            valid = ~np.isnan(col_vals)
            if valid.sum() > 1:
                vmin, vmax = np.nanmin(col_vals), np.nanmax(col_vals)
                if vmax > vmin:
                    normalized[:, j] = (col_vals - vmin) / (vmax - vmin)
                else:
                    normalized[:, j] = 0.5

        # PCA weights
        weights = _pca_weights(normalized)

        # Weighted average (handling NaN)
        score = np.nansum(normalized * weights, axis=1) / np.nansum(
            np.where(np.isnan(normalized), 0, 1) * weights, axis=1
        )
        pillar_scores[pillar] = score

    return pillar_scores


def compute_ghri(
    df: pd.DataFrame, year: int | None = None
) -> pd.DataFrame:
    """Compute the Global Health Resilience Index.

    Aggregation: geometric mean across pillar scores.

    Returns
    -------
    DataFrame with columns: iso3, year, pillar scores, ghri, ghri_rank
    """
    scores = compute_pillar_scores(df, year=year)
    pillar_cols = [c for c in GHRI_PILLARS if c in scores.columns]

    # Geometric mean across pillars (with floor at 0.001 to avoid log(0))
    pillar_values = scores[pillar_cols].clip(lower=0.001)
    scores["ghri"] = np.exp(np.log(pillar_values).mean(axis=1))

    # Rank (1 = best)
    scores["ghri_rank"] = scores["ghri"].rank(ascending=False, method="min").astype("Int64")

    scores = scores.sort_values("ghri_rank")
    logger.info("GHRI computed for %d countries", len(scores))
    return scores


def bootstrap_ghri_ci(
    df: pd.DataFrame, year: int | None = None, n_boot: int = 1000, seed: int = 42
) -> pd.DataFrame:
    """Bootstrap confidence intervals for GHRI ranks.

    Returns DataFrame with iso3, ghri, ghri_rank, rank_lo, rank_hi (95% CI).
    """
    rng = np.random.RandomState(seed)
    base = compute_ghri(df, year=year)

    if base.empty:
        return base

    all_ranks = []
    n_countries = len(base)

    for _ in range(n_boot):
        # Resample within each pillar's indicator set (add noise)
        noisy = df.copy()
        numeric_cols = noisy.select_dtypes(include="number").columns
        noise = rng.normal(0, 0.02, size=(len(noisy), len(numeric_cols)))
        noisy[numeric_cols] = noisy[numeric_cols] + noisy[numeric_cols] * noise
        boot_scores = compute_ghri(noisy, year=year)
        if not boot_scores.empty:
            rank_map = dict(zip(boot_scores["iso3"], boot_scores["ghri_rank"]))
            all_ranks.append(rank_map)

    if not all_ranks:
        base["rank_lo"] = base["ghri_rank"]
        base["rank_hi"] = base["ghri_rank"]
        return base

    # Compute 2.5th and 97.5th percentile of ranks
    rank_df = pd.DataFrame(all_ranks)
    base["rank_lo"] = base["iso3"].map(rank_df.quantile(0.025).to_dict()).astype("Int64")
    base["rank_hi"] = base["iso3"].map(rank_df.quantile(0.975).to_dict()).astype("Int64")

    return base
