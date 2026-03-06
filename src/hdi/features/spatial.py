"""Spatial feature engineering: neighbor weights, spatial lags."""

from __future__ import annotations

import logging
from pathlib import Path

import numpy as np
import pandas as pd

from hdi.config import SPATIAL

logger = logging.getLogger(__name__)


def load_world_geometries() -> "geopandas.GeoDataFrame":
    """Load world country polygons (Natural Earth via geopandas)."""
    import geopandas as gpd

    world = gpd.read_file(gpd.datasets.get_path("naturalearth_lowres"))
    world = world.rename(columns={"iso_a3": "iso3"})
    # Fix known issues
    world.loc[world["name"] == "France", "iso3"] = "FRA"
    world.loc[world["name"] == "Norway", "iso3"] = "NOR"
    world.loc[world["name"] == "Kosovo", "iso3"] = "XKX"
    world = world[world["iso3"] != "-99"]
    return world


def build_spatial_weights(gdf: "geopandas.GeoDataFrame") -> "libpysal.weights.W":
    """Build Queen contiguity spatial weights matrix."""
    from libpysal.weights import Queen

    w = Queen.from_dataframe(gdf, ids="iso3")
    w.transform = "r"  # row-standardize
    return w


def compute_spatial_lag(
    gdf: "geopandas.GeoDataFrame",
    w: "libpysal.weights.W",
    col: str,
) -> pd.Series:
    """Compute spatial lag (weighted average of neighbors) for a variable."""
    from libpysal.weights import lag_spatial

    return pd.Series(lag_spatial(w, gdf[col].values), index=gdf.index, name=f"slag_{col}")


def compute_morans_i(
    gdf: "geopandas.GeoDataFrame",
    w: "libpysal.weights.W",
    col: str,
) -> dict:
    """Compute Global Moran's I for spatial autocorrelation.

    Returns dict with I statistic, expected I, p-value, z-score.
    """
    from esda.moran import Moran

    y = gdf[col].values
    mask = ~np.isnan(y)
    if mask.sum() < 10:
        return {"I": np.nan, "EI": np.nan, "p_value": np.nan, "z_score": np.nan}

    mi = Moran(y[mask], w)
    return {
        "I": mi.I,
        "EI": mi.EI,
        "p_value": mi.p_sim,
        "z_score": mi.z_sim,
    }


def compute_lisa(
    gdf: "geopandas.GeoDataFrame",
    w: "libpysal.weights.W",
    col: str,
) -> pd.DataFrame:
    """Compute Local Indicators of Spatial Association (LISA).

    Returns DataFrame with local I, p-values, and cluster labels (HH, HL, LH, LL).
    """
    from esda.moran import Moran_Local

    y = gdf[col].values
    lisa = Moran_Local(y, w, permutations=999)

    labels = ["Not Significant", "HH", "LH", "LL", "HL"]
    cluster = [
        labels[q] if p < 0.05 else "Not Significant"
        for q, p in zip(lisa.q, lisa.p_sim)
    ]

    return pd.DataFrame({
        "iso3": gdf["iso3"].values,
        "local_I": lisa.Is,
        "p_value": lisa.p_sim,
        "quadrant": lisa.q,
        "cluster": cluster,
    })


def merge_spatial_data(
    panel: pd.DataFrame,
    year: int,
    columns: list[str],
) -> "geopandas.GeoDataFrame":
    """Merge panel data with world geometries for a given year.

    Returns a GeoDataFrame ready for mapping.
    """
    import geopandas as gpd

    world = load_world_geometries()
    year_data = panel[panel["year"] == year][["iso3"] + columns].copy()

    gdf = world.merge(year_data, on="iso3", how="left")
    return gdf


def save_geojson(gdf: "geopandas.GeoDataFrame", name: str) -> Path:
    """Save GeoDataFrame as GeoJSON to processed/spatial/."""
    SPATIAL.mkdir(parents=True, exist_ok=True)
    path = SPATIAL / f"{name}.geojson"
    gdf.to_file(path, driver="GeoJSON")
    logger.info("Saved GeoJSON: %s", path)
    return path
