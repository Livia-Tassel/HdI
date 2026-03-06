"""Consistent styling and themes for all visualizations."""

from __future__ import annotations

import matplotlib.pyplot as plt
import matplotlib as mpl

# ── Color palettes ───────────────────────────────────────────────────────────

PALETTE_REGIONS = {
    "AFRO": "#E41A1C",
    "AMRO": "#377EB8",
    "SEARO": "#4DAF4A",
    "EURO": "#984EA3",
    "EMRO": "#FF7F00",
    "WPRO": "#A65628",
}

PALETTE_INCOME = {
    "HIC": "#1B9E77",
    "UMC": "#D95F02",
    "LMC": "#7570B3",
    "LIC": "#E7298A",
}

PALETTE_QUADRANT = {
    "Q1_high_high": "#2166AC",
    "Q2_low_high": "#4DAF4A",
    "Q3_high_low": "#E41A1C",
    "Q4_low_low": "#FF7F00",
}

PALETTE_SCENARIOS = {
    "A_tobacco_control": "#E41A1C",
    "B_air_quality": "#377EB8",
    "C_combined": "#4DAF4A",
    "D_status_quo": "#999999",
}

PALETTE_SEQUENTIAL = "YlOrRd"
PALETTE_DIVERGING = "RdBu_r"
PALETTE_BIVARIATE_3x3 = [
    ["#e8e8e8", "#ace4e4", "#5ac8c8"],
    ["#dfb0d6", "#a5add3", "#5698b9"],
    ["#be64ac", "#8c62aa", "#3b4994"],
]

# ── Matplotlib RC params ─────────────────────────────────────────────────────

RC_PARAMS = {
    "figure.figsize": (10, 6),
    "figure.dpi": 150,
    "savefig.dpi": 300,
    "savefig.bbox": "tight",
    "font.family": "sans-serif",
    "font.sans-serif": ["Helvetica", "Arial", "DejaVu Sans"],
    "font.size": 11,
    "axes.titlesize": 13,
    "axes.labelsize": 11,
    "axes.spines.top": False,
    "axes.spines.right": False,
    "legend.fontsize": 10,
    "legend.frameon": False,
    "xtick.labelsize": 10,
    "ytick.labelsize": 10,
}


def apply_theme():
    """Apply the HdI publication theme to matplotlib."""
    plt.rcParams.update(RC_PARAMS)


def get_fig_ax(
    nrows: int = 1, ncols: int = 1, figsize: tuple | None = None, **kwargs
) -> tuple:
    """Create figure and axes with theme applied."""
    apply_theme()
    if figsize is None:
        w = 10 * ncols
        h = 6 * nrows
        figsize = (min(w, 20), min(h, 16))
    return plt.subplots(nrows, ncols, figsize=figsize, **kwargs)


def save_figure(fig, name: str, formats: list[str] | None = None) -> list[str]:
    """Save figure to reports/figures/ in specified formats."""
    from hdi.config import FIGURES
    FIGURES.mkdir(parents=True, exist_ok=True)

    if formats is None:
        formats = ["png", "svg"]

    paths = []
    for fmt in formats:
        path = FIGURES / f"{name}.{fmt}"
        fig.savefig(path, dpi=300, bbox_inches="tight")
        paths.append(str(path))

    plt.close(fig)
    return paths
