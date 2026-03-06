"""Time series, heatmaps, and standard chart generators."""

from __future__ import annotations

import logging

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

from hdi.visualization.themes import (
    apply_theme, save_figure, get_fig_ax,
    PALETTE_REGIONS, PALETTE_INCOME, PALETTE_SCENARIOS,
)

logger = logging.getLogger(__name__)


def time_series_multi_country(
    df: pd.DataFrame,
    indicator: str,
    countries: list[str],
    color_by: str | None = None,
    title: str = "",
    save_name: str | None = None,
) -> plt.Figure:
    """Multi-country time series overlay."""
    fig, ax = get_fig_ax()
    palette = PALETTE_REGIONS if color_by == "who_region" else None

    for iso3 in countries:
        subset = df[df["iso3"] == iso3].sort_values("year")
        if indicator not in subset.columns:
            continue
        color = None
        if palette and color_by and color_by in subset.columns:
            region = subset[color_by].iloc[0]
            color = palette.get(region)
        ax.plot(subset["year"], subset[indicator], label=iso3, color=color, linewidth=1.5)

    ax.set_xlabel("Year")
    ax.set_ylabel(indicator.replace("_", " ").title())
    ax.set_title(title)
    ax.legend(bbox_to_anchor=(1.02, 1), loc="upper left", fontsize=8)

    if save_name:
        save_figure(fig, save_name)
    return fig


def forecast_fan_chart(
    historical: pd.DataFrame,
    forecast: pd.DataFrame,
    title: str = "",
    save_name: str | None = None,
) -> plt.Figure:
    """Fan chart showing historical data + forecast with confidence interval."""
    fig, ax = get_fig_ax()

    ax.plot(historical["year"], historical["value"], "k-", linewidth=1.5, label="Historical")
    ax.plot(forecast["year"], forecast["predicted"], "b--", linewidth=1.5, label="Forecast")
    ax.fill_between(
        forecast["year"],
        forecast["ci_lower"],
        forecast["ci_upper"],
        alpha=0.2,
        color="blue",
        label="95% CI",
    )

    ax.axvline(x=historical["year"].iloc[-1], color="gray", linestyle=":", alpha=0.5)
    ax.set_xlabel("Year")
    ax.set_title(title)
    ax.legend()

    if save_name:
        save_figure(fig, save_name)
    return fig


def scenario_comparison(
    scenarios: dict[str, pd.DataFrame],
    variable: str = "total_daly",
    title: str = "",
    show_ci: bool = True,
    save_name: str | None = None,
) -> plt.Figure:
    """Compare multiple scenario trajectories with uncertainty bands."""
    fig, ax = get_fig_ax()

    for name, data in scenarios.items():
        color = PALETTE_SCENARIOS.get(name, None)
        ax.plot(data["year"], data[variable], label=name, color=color, linewidth=1.5)
        if show_ci and f"{variable}_lower" in data.columns:
            ax.fill_between(
                data["year"],
                data[f"{variable}_lower"],
                data[f"{variable}_upper"],
                alpha=0.15,
                color=color,
            )

    ax.set_xlabel("Year")
    ax.set_ylabel(variable.replace("_", " ").title())
    ax.set_title(title)
    ax.legend()

    if save_name:
        save_figure(fig, save_name)
    return fig


def heatmap_trends(
    df: pd.DataFrame,
    row_col: str = "iso3",
    col_col: str = "disease_group",
    value_col: str = "trend_slope",
    title: str = "Disease Burden Trends",
    save_name: str | None = None,
) -> plt.Figure:
    """Heatmap of trends (countries x diseases or similar)."""
    pivot = df.pivot_table(index=row_col, columns=col_col, values=value_col)

    fig, ax = get_fig_ax(figsize=(14, max(8, len(pivot) * 0.3)))
    sns.heatmap(
        pivot,
        ax=ax,
        cmap="RdBu_r",
        center=0,
        linewidths=0.5,
        cbar_kws={"label": value_col.replace("_", " ").title()},
    )
    ax.set_title(title)

    if save_name:
        save_figure(fig, save_name)
    return fig


def bump_chart(
    df: pd.DataFrame,
    entity_col: str = "iso3",
    time_col: str = "year",
    rank_col: str = "rank",
    top_n: int = 30,
    title: str = "Rank Evolution",
    save_name: str | None = None,
) -> plt.Figure:
    """Bump chart showing rank evolution over time."""
    fig, ax = get_fig_ax(figsize=(14, 10))

    # Filter to top N entities (by most recent rank)
    latest = df[df[time_col] == df[time_col].max()].nsmallest(top_n, rank_col)
    entities = latest[entity_col].tolist()
    plot_data = df[df[entity_col].isin(entities)]

    for entity in entities:
        subset = plot_data[plot_data[entity_col] == entity].sort_values(time_col)
        ax.plot(subset[time_col], subset[rank_col], "o-", markersize=3, linewidth=1.2)
        # Label at end
        last = subset.iloc[-1]
        ax.text(last[time_col] + 0.3, last[rank_col], entity, fontsize=7, va="center")

    ax.invert_yaxis()
    ax.set_xlabel("Year")
    ax.set_ylabel("Rank")
    ax.set_title(title)

    if save_name:
        save_figure(fig, save_name)
    return fig


def radar_chart(
    values: dict[str, list[float]],
    categories: list[str],
    title: str = "",
    save_name: str | None = None,
) -> plt.Figure:
    """Radar/spider chart comparing entities across multiple dimensions."""
    import matplotlib.pyplot as plt

    N = len(categories)
    angles = np.linspace(0, 2 * np.pi, N, endpoint=False).tolist()
    angles += angles[:1]

    fig, ax = plt.subplots(figsize=(8, 8), subplot_kw=dict(polar=True))

    for label, vals in values.items():
        vals_closed = vals + vals[:1]
        ax.plot(angles, vals_closed, "o-", linewidth=1.5, label=label, markersize=4)
        ax.fill(angles, vals_closed, alpha=0.1)

    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(categories, fontsize=9)
    ax.set_title(title, y=1.08, fontsize=13, fontweight="bold")
    ax.legend(loc="upper right", bbox_to_anchor=(1.3, 1.1), fontsize=9)

    if save_name:
        save_figure(fig, save_name)
    return fig


def stacked_bar_paf(
    df: pd.DataFrame,
    group_col: str = "who_region",
    risk_col: str = "risk_factor",
    value_col: str = "paf",
    title: str = "PAF by Risk Factor",
    save_name: str | None = None,
) -> plt.Figure:
    """Stacked bar chart of PAF by risk factor per group."""
    pivot = df.pivot_table(index=group_col, columns=risk_col, values=value_col, aggfunc="mean")

    fig, ax = get_fig_ax(figsize=(12, 7))
    pivot.plot(kind="barh", stacked=True, ax=ax, colormap="Set2")

    ax.set_xlabel("Population Attributable Fraction")
    ax.set_title(title)
    ax.legend(bbox_to_anchor=(1.02, 1), loc="upper left", fontsize=8)

    if save_name:
        save_figure(fig, save_name)
    return fig


def quadrant_scatter(
    df: pd.DataFrame,
    x_col: str,
    y_col: str,
    label_col: str = "iso3",
    quadrant_col: str = "quadrant",
    title: str = "Health System Efficiency Quadrants",
    save_name: str | None = None,
) -> plt.Figure:
    """Four-quadrant scatter plot for efficiency analysis."""
    from hdi.visualization.themes import PALETTE_QUADRANT

    fig, ax = get_fig_ax(figsize=(12, 10))

    for q, color in PALETTE_QUADRANT.items():
        mask = df[quadrant_col] == q
        subset = df[mask]
        ax.scatter(subset[x_col], subset[y_col], c=color, label=q, s=40, alpha=0.7)

    # Add median lines
    ax.axhline(y=df[y_col].median(), color="gray", linestyle="--", alpha=0.5)
    ax.axvline(x=df[x_col].median(), color="gray", linestyle="--", alpha=0.5)

    # Label notable points
    for _, row in df.iterrows():
        ax.annotate(row[label_col], (row[x_col], row[y_col]), fontsize=6, alpha=0.7)

    ax.set_xlabel(x_col.replace("_", " ").title())
    ax.set_ylabel(y_col.replace("_", " ").title())
    ax.set_title(title)
    ax.legend()

    if save_name:
        save_figure(fig, save_name)
    return fig
