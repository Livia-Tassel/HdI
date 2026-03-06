"""Interactive Plotly visualization components."""

from __future__ import annotations

import logging

import numpy as np
import pandas as pd

logger = logging.getLogger(__name__)


def interactive_choropleth_timeseries(
    df: pd.DataFrame,
    iso3_col: str = "iso3",
    year_col: str = "year",
    value_col: str = "value",
    title: str = "",
) -> "plotly.graph_objects.Figure":
    """Animated choropleth with year slider."""
    import plotly.express as px

    fig = px.choropleth(
        df,
        locations=iso3_col,
        color=value_col,
        animation_frame=year_col,
        hover_name=iso3_col,
        color_continuous_scale="YlOrRd",
        title=title,
        range_color=(df[value_col].quantile(0.05), df[value_col].quantile(0.95)),
    )

    fig.update_layout(
        geo=dict(showframe=False, showcoastlines=True, projection_type="natural earth"),
        margin=dict(l=0, r=0, t=50, b=0),
    )
    return fig


def interactive_quadrant_explorer(
    df: pd.DataFrame,
    x_col: str,
    y_col: str,
    size_col: str | None = None,
    color_col: str = "quadrant",
    hover_cols: list[str] | None = None,
    title: str = "Health System Efficiency",
) -> "plotly.graph_objects.Figure":
    """Interactive efficiency quadrant scatter with hover details."""
    import plotly.express as px

    hover = hover_cols or [x_col, y_col]
    fig = px.scatter(
        df,
        x=x_col,
        y=y_col,
        color=color_col,
        size=size_col,
        hover_name="iso3" if "iso3" in df.columns else None,
        hover_data=hover,
        title=title,
    )

    # Add median lines
    fig.add_hline(y=df[y_col].median(), line_dash="dash", line_color="gray", opacity=0.5)
    fig.add_vline(x=df[x_col].median(), line_dash="dash", line_color="gray", opacity=0.5)

    fig.update_layout(height=700)
    return fig


def interactive_scenario_simulator(
    scenarios: dict[str, "ScenarioResult"],
    variable: str = "total_daly",
    title: str = "Policy Scenario Simulator",
) -> "plotly.graph_objects.Figure":
    """Interactive scenario comparison with CI bands."""
    import plotly.graph_objects as go

    fig = go.Figure()

    colors = {
        "A_tobacco_control": "red",
        "B_air_quality": "blue",
        "C_combined": "green",
        "D_status_quo": "gray",
    }

    for name, result in scenarios.items():
        color = colors.get(name, "black")
        years = result.years
        values = result.trajectories[variable]

        fig.add_trace(go.Scatter(
            x=years, y=values, mode="lines", name=name,
            line=dict(color=color, width=2),
        ))

        if result.ci_lower and variable in result.ci_lower:
            fig.add_trace(go.Scatter(
                x=np.concatenate([years, years[::-1]]),
                y=np.concatenate([result.ci_upper[variable], result.ci_lower[variable][::-1]]),
                fill="toself",
                fillcolor=f"rgba({','.join(['255' if color == 'red' else '0', '0' if color != 'green' else '128', '255' if color == 'blue' else '0'])}, 0.1)",
                line=dict(color="rgba(0,0,0,0)"),
                showlegend=False,
                name=f"{name} CI",
            ))

    fig.update_layout(
        title=title,
        xaxis_title="Year",
        yaxis_title=variable.replace("_", " ").title(),
        height=600,
    )
    return fig


def interactive_ghri_radar(
    ghri_df: pd.DataFrame,
    countries: list[str],
    pillar_cols: list[str],
    title: str = "GHRI Pillar Comparison",
) -> "plotly.graph_objects.Figure":
    """Interactive radar chart comparing GHRI pillars across countries."""
    import plotly.graph_objects as go

    fig = go.Figure()

    for iso3 in countries:
        row = ghri_df[ghri_df["iso3"] == iso3]
        if row.empty:
            continue
        values = row[pillar_cols].values[0].tolist()
        values += values[:1]  # close the polygon

        fig.add_trace(go.Scatterpolar(
            r=values,
            theta=pillar_cols + [pillar_cols[0]],
            fill="toself",
            name=iso3,
            opacity=0.6,
        ))

    fig.update_layout(
        polar=dict(radialaxis=dict(visible=True, range=[0, 1])),
        title=title,
        showlegend=True,
        height=600,
    )
    return fig
