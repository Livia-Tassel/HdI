"""Sankey diagram generators for risk factor attribution flows."""

from __future__ import annotations

import logging

import pandas as pd

logger = logging.getLogger(__name__)


def create_sankey_data(
    paf_df: pd.DataFrame,
    risk_col: str = "risk_factor",
    disease_col: str = "disease",
    outcome_col: str = "outcome",
    value_col: str = "attributable_burden",
) -> dict:
    """Prepare Sankey diagram data from PAF decomposition.

    Creates a three-level flow: Risk Factors -> Diseases -> Outcomes (Death/DALY).

    Returns dict ready for plotly.graph_objects.Sankey.
    """
    # Build node list
    risks = paf_df[risk_col].unique().tolist()
    diseases = paf_df[disease_col].unique().tolist() if disease_col in paf_df.columns else []
    outcomes = paf_df[outcome_col].unique().tolist() if outcome_col in paf_df.columns else ["DALY", "Death"]

    nodes = risks + diseases + outcomes
    node_map = {name: i for i, name in enumerate(nodes)}

    sources, targets, values, labels = [], [], [], []

    # Risk -> Disease links
    if disease_col in paf_df.columns:
        for _, row in paf_df.groupby([risk_col, disease_col])[value_col].sum().reset_index().iterrows():
            sources.append(node_map[row[risk_col]])
            targets.append(node_map[row[disease_col]])
            values.append(row[value_col])

    # Disease -> Outcome links
    if disease_col in paf_df.columns and outcome_col in paf_df.columns:
        for _, row in paf_df.groupby([disease_col, outcome_col])[value_col].sum().reset_index().iterrows():
            sources.append(node_map[row[disease_col]])
            targets.append(node_map[row[outcome_col]])
            values.append(row[value_col])

    return {
        "nodes": nodes,
        "sources": sources,
        "targets": targets,
        "values": values,
    }


def plot_sankey(
    sankey_data: dict,
    title: str = "Risk Factor Attribution Flow",
) -> "plotly.graph_objects.Figure":
    """Create an interactive Sankey diagram using Plotly."""
    import plotly.graph_objects as go

    fig = go.Figure(data=[go.Sankey(
        node=dict(
            pad=15,
            thickness=20,
            line=dict(color="black", width=0.5),
            label=sankey_data["nodes"],
            color="rgba(31, 119, 180, 0.8)",
        ),
        link=dict(
            source=sankey_data["sources"],
            target=sankey_data["targets"],
            value=sankey_data["values"],
            color="rgba(31, 119, 180, 0.3)",
        ),
    )])

    fig.update_layout(
        title_text=title,
        font_size=11,
        height=600,
    )

    return fig
