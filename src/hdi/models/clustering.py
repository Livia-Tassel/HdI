"""Clustering analysis: K-means, hierarchical, efficiency quadrant analysis."""

from __future__ import annotations

import logging

import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import silhouette_score

from hdi.config import SEED

logger = logging.getLogger(__name__)


def kmeans_clustering(
    df: pd.DataFrame,
    feature_cols: list[str],
    entity_col: str = "iso3",
    n_clusters: int | None = None,
    max_k: int = 10,
    seed: int = SEED,
) -> tuple[pd.DataFrame, dict]:
    """K-means clustering with optional automatic k selection via silhouette.

    Parameters
    ----------
    df : DataFrame with entity and feature columns
    feature_cols : columns to use for clustering
    entity_col : entity identifier
    n_clusters : number of clusters (None = auto-select)
    max_k : maximum k to test for auto-selection

    Returns
    -------
    (DataFrame with cluster labels, dict with diagnostics)
    """
    data = df[[entity_col] + feature_cols].dropna()
    X = data[feature_cols].values

    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    if n_clusters is None:
        # Silhouette method for optimal k
        best_k, best_score = 2, -1
        scores = {}
        for k in range(2, min(max_k + 1, len(X))):
            km = KMeans(n_clusters=k, random_state=seed, n_init=10)
            labels = km.fit_predict(X_scaled)
            score = silhouette_score(X_scaled, labels)
            scores[k] = score
            if score > best_score:
                best_k, best_score = k, score
        n_clusters = best_k
        logger.info("Auto-selected k=%d (silhouette=%.3f)", n_clusters, best_score)
    else:
        scores = {}

    km = KMeans(n_clusters=n_clusters, random_state=seed, n_init=10)
    labels = km.fit_predict(X_scaled)

    result = data.copy()
    result["cluster"] = labels

    # Cluster profiles
    profiles = result.groupby("cluster")[feature_cols].mean()

    diagnostics = {
        "n_clusters": n_clusters,
        "silhouette_scores": scores,
        "inertia": km.inertia_,
        "cluster_sizes": result["cluster"].value_counts().to_dict(),
        "cluster_profiles": profiles,
    }

    return result, diagnostics


def compute_gini(values: np.ndarray) -> float:
    """Compute Gini coefficient for a distribution."""
    values = np.sort(np.asarray(values, dtype=float))
    values = values[~np.isnan(values)]
    n = len(values)
    if n == 0:
        return np.nan
    index = np.arange(1, n + 1)
    return (2 * np.sum(index * values) - (n + 1) * np.sum(values)) / (n * np.sum(values))


def compute_theil(values: np.ndarray) -> float:
    """Compute Theil index (GE(1)) for inequality measurement."""
    values = np.asarray(values, dtype=float)
    values = values[~np.isnan(values)]
    values = values[values > 0]
    if len(values) == 0:
        return np.nan
    mu = values.mean()
    return np.mean((values / mu) * np.log(values / mu))


def health_equity_by_group(
    df: pd.DataFrame,
    health_col: str,
    group_col: str,
) -> pd.DataFrame:
    """Compute Gini and Theil indices for health outcomes within groups."""
    results = []
    for group, subset in df.groupby(group_col):
        vals = subset[health_col].dropna().values
        if len(vals) < 3:
            continue
        results.append({
            group_col: group,
            "n_countries": len(vals),
            "mean": vals.mean(),
            "std": vals.std(),
            "gini": compute_gini(vals),
            "theil": compute_theil(vals),
        })
    return pd.DataFrame(results)
