"""Choropleth and spatial visualization maps."""

from __future__ import annotations

import logging

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from hdi.visualization.themes import (
    apply_theme,
    save_figure,
    get_fig_ax,
    PALETTE_REGIONS,
    PALETTE_SEQUENTIAL,
    PALETTE_DIVERGING,
    PALETTE_BIVARIATE_3x3,
)

logger = logging.getLogger(__name__)


def choropleth_static(
    gdf: "geopandas.GeoDataFrame",
    column: str,
    title: str = "",
    cmap: str = PALETTE_SEQUENTIAL,
    legend: bool = True,
    missing_color: str = "#d9d9d9",
    figsize: tuple = (16, 8),
    save_name: str | None = None,
) -> plt.Figure:
    """Static choropleth map using geopandas + matplotlib."""
    apply_theme()
    fig, ax = plt.subplots(1, 1, figsize=figsize)

    gdf.plot(
        column=column,
        ax=ax,
        legend=legend,
        cmap=cmap,
        missing_kwds={"color": missing_color, "label": "No data"},
        edgecolor="white",
        linewidth=0.3,
    )

    ax.set_title(title, fontsize=14, fontweight="bold")
    ax.set_axis_off()

    if save_name:
        save_figure(fig, save_name)
    return fig


def choropleth_diverging(
    gdf: "geopandas.GeoDataFrame",
    column: str,
    title: str = "",
    center: float = 0,
    save_name: str | None = None,
) -> plt.Figure:
    """Diverging choropleth (e.g., resource surplus/deficit)."""
    apply_theme()
    fig, ax = plt.subplots(1, 1, figsize=(16, 8))

    vmax = max(abs(gdf[column].min()), abs(gdf[column].max()))

    gdf.plot(
        column=column,
        ax=ax,
        legend=True,
        cmap=PALETTE_DIVERGING,
        vmin=-vmax,
        vmax=vmax,
        missing_kwds={"color": "#d9d9d9"},
        edgecolor="white",
        linewidth=0.3,
    )

    ax.set_title(title, fontsize=14, fontweight="bold")
    ax.set_axis_off()

    if save_name:
        save_figure(fig, save_name)
    return fig


def lisa_cluster_map(
    gdf: "geopandas.GeoDataFrame",
    lisa_df: pd.DataFrame,
    title: str = "LISA Cluster Map",
    save_name: str | None = None,
) -> plt.Figure:
    """LISA cluster significance map (HH, HL, LH, LL)."""
    apply_theme()
    fig, ax = plt.subplots(1, 1, figsize=(16, 8))

    merged = gdf.merge(lisa_df, on="iso3", how="left")
    merged["cluster"] = merged["cluster"].fillna("Not Significant")

    cluster_colors = {
        "HH": "#d7191c",
        "HL": "#fdae61",
        "LH": "#abd9e9",
        "LL": "#2c7bb6",
        "Not Significant": "#d9d9d9",
    }

    merged["color"] = merged["cluster"].map(cluster_colors)
    merged.plot(ax=ax, color=merged["color"], edgecolor="white", linewidth=0.3)

    # Legend
    from matplotlib.patches import Patch
    legend_elements = [Patch(facecolor=c, label=l) for l, c in cluster_colors.items()]
    ax.legend(handles=legend_elements, loc="lower left", fontsize=9)

    ax.set_title(title, fontsize=14, fontweight="bold")
    ax.set_axis_off()

    if save_name:
        save_figure(fig, save_name)
    return fig


def bivariate_choropleth(
    gdf: "geopandas.GeoDataFrame",
    col_x: str,
    col_y: str,
    title: str = "",
    save_name: str | None = None,
) -> plt.Figure:
    """3x3 bivariate choropleth showing two variables simultaneously."""
    apply_theme()
    fig, ax = plt.subplots(1, 1, figsize=(16, 8))

    data = gdf.copy()
    # Tertile classification
    for col, suffix in [(col_x, "x"), (col_y, "y")]:
        q33 = data[col].quantile(1/3)
        q66 = data[col].quantile(2/3)
        data[f"cat_{suffix}"] = pd.cut(
            data[col],
            bins=[-np.inf, q33, q66, np.inf],
            labels=[0, 1, 2],
        ).astype(int)

    # Assign bivariate color
    colors = PALETTE_BIVARIATE_3x3
    data["biv_color"] = data.apply(
        lambda r: colors[int(r["cat_y"])][int(r["cat_x"])]
        if pd.notna(r.get("cat_x")) and pd.notna(r.get("cat_y"))
        else "#d9d9d9",
        axis=1,
    )

    data.plot(ax=ax, color=data["biv_color"], edgecolor="white", linewidth=0.3)

    # Add bivariate legend
    from matplotlib.patches import Rectangle
    legend_ax = fig.add_axes([0.15, 0.15, 0.1, 0.1])
    for i in range(3):
        for j in range(3):
            legend_ax.add_patch(Rectangle((j, i), 1, 1, facecolor=colors[i][j]))
    legend_ax.set_xlim(0, 3)
    legend_ax.set_ylim(0, 3)
    legend_ax.set_xlabel(col_x, fontsize=8)
    legend_ax.set_ylabel(col_y, fontsize=8)
    legend_ax.set_xticks([])
    legend_ax.set_yticks([])

    ax.set_title(title, fontsize=14, fontweight="bold")
    ax.set_axis_off()

    if save_name:
        save_figure(fig, save_name)
    return fig


def choropleth_plotly(
    df: pd.DataFrame,
    iso3_col: str = "iso3",
    value_col: str = "value",
    title: str = "",
    color_scale: str = "YlOrRd",
) -> "plotly.graph_objects.Figure":
    """Interactive choropleth using Plotly."""
    import plotly.express as px

    fig = px.choropleth(
        df,
        locations=iso3_col,
        color=value_col,
        hover_name=iso3_col,
        color_continuous_scale=color_scale,
        title=title,
    )
    fig.update_layout(
        geo=dict(showframe=False, showcoastlines=True, projection_type="natural earth"),
        margin=dict(l=0, r=0, t=40, b=0),
    )
    return fig
