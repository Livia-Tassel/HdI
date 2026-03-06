"""PAF calculation, Shapley value decomposition for risk factor attribution."""

from __future__ import annotations

import logging
from itertools import combinations

import numpy as np
import pandas as pd
from math import factorial

logger = logging.getLogger(__name__)


def compute_paf(
    prevalence: float | np.ndarray,
    relative_risk: float | np.ndarray,
) -> float | np.ndarray:
    """Compute Population Attributable Fraction.

    PAF = sum_i[p_i * (RR_i - 1)] / (1 + sum_i[p_i * (RR_i - 1)])

    For a single exposure level (binary):
    PAF = p * (RR - 1) / (1 + p * (RR - 1))
    """
    numerator = prevalence * (relative_risk - 1)
    denominator = 1 + numerator
    return numerator / denominator


def compute_joint_paf(paf_values: list[float] | np.ndarray) -> float:
    """Compute joint PAF for multiple independent risk factors.

    JointPAF = 1 - prod_k(1 - PAF_k)

    Assumes independence between risk factors (conservative estimate).
    """
    paf_arr = np.asarray(paf_values)
    return 1 - np.prod(1 - paf_arr)


def compute_paf_by_country(
    df: pd.DataFrame,
    risk_cols: dict[str, tuple[str, float]],
    disease_col: str,
) -> pd.DataFrame:
    """Compute PAF for each risk factor × country combination.

    Parameters
    ----------
    df : panel DataFrame with iso3, year, risk factor prevalences
    risk_cols : dict mapping risk_factor_name -> (prevalence_col, RR)
    disease_col : disease burden column name

    Returns
    -------
    DataFrame with iso3, year, risk_factor, paf, attributable_burden
    """
    results = []

    for risk_name, (prev_col, rr) in risk_cols.items():
        if prev_col not in df.columns:
            logger.warning("Missing prevalence column: %s", prev_col)
            continue

        subset = df[["iso3", "year", prev_col, disease_col]].dropna()
        paf = compute_paf(subset[prev_col], rr)
        attributable = paf * subset[disease_col]

        result = pd.DataFrame({
            "iso3": subset["iso3"],
            "year": subset["year"],
            "risk_factor": risk_name,
            "prevalence": subset[prev_col],
            "relative_risk": rr,
            "paf": paf,
            "attributable_burden": attributable,
        })
        results.append(result)

    if not results:
        return pd.DataFrame()

    return pd.concat(results, ignore_index=True)


def shapley_decomposition(
    df: pd.DataFrame,
    risk_cols: dict[str, tuple[str, float]],
    disease_col: str,
    country: str | None = None,
    year: int | None = None,
) -> pd.DataFrame:
    """Shapley value decomposition of disease burden among risk factors.

    Uses the game-theoretic approach where each "player" (risk factor)
    receives credit proportional to their marginal contribution across
    all possible coalitions.

    Parameters
    ----------
    df : panel DataFrame
    risk_cols : dict mapping risk_factor_name -> (prevalence_col, RR)
    disease_col : disease burden column
    country : optional ISO3 filter
    year : optional year filter

    Returns
    -------
    DataFrame with risk_factor, shapley_value, shapley_pct
    """
    data = df.copy()
    if country:
        data = data[data["iso3"] == country]
    if year:
        data = data[data["year"] == year]

    # Average prevalence across selected data
    risk_factors = []
    prevalences = {}
    rrs = {}
    for name, (col, rr) in risk_cols.items():
        if col in data.columns and data[col].notna().any():
            risk_factors.append(name)
            prevalences[name] = data[col].mean()
            rrs[name] = rr

    n = len(risk_factors)
    if n == 0:
        return pd.DataFrame(columns=["risk_factor", "shapley_value", "shapley_pct"])

    # Value function: joint PAF of a coalition
    def v(coalition: set[str]) -> float:
        if not coalition:
            return 0.0
        pafs = [compute_paf(prevalences[rf], rrs[rf]) for rf in coalition]
        return compute_joint_paf(pafs)

    # Shapley values
    shapley_values = {}
    for i in risk_factors:
        sv = 0.0
        others = [rf for rf in risk_factors if rf != i]
        for k in range(len(others) + 1):
            for S in combinations(others, k):
                S_set = set(S)
                weight = factorial(len(S_set)) * factorial(n - len(S_set) - 1) / factorial(n)
                marginal = v(S_set | {i}) - v(S_set)
                sv += weight * marginal
        shapley_values[i] = sv

    total = sum(shapley_values.values())
    result = pd.DataFrame([
        {
            "risk_factor": rf,
            "shapley_value": sv,
            "shapley_pct": sv / total * 100 if total > 0 else 0,
        }
        for rf, sv in shapley_values.items()
    ])

    return result.sort_values("shapley_value", ascending=False).reset_index(drop=True)


# ── Reference relative risks (from GBD/literature) ──────────────────────────

REFERENCE_RR = {
    "smoking_cvd": {"prevalence_col": "smoking_prev", "rr": 2.0},
    "smoking_lung_cancer": {"prevalence_col": "smoking_prev", "rr": 15.0},
    "smoking_copd": {"prevalence_col": "smoking_prev", "rr": 4.0},
    "pm25_respiratory": {"prevalence_col": "pm25_high_exposure", "rr": 1.3},
    "pm25_cvd": {"prevalence_col": "pm25_high_exposure", "rr": 1.15},
    "high_bmi_diabetes": {"prevalence_col": "obesity_prev", "rr": 7.0},
    "high_bmi_cvd": {"prevalence_col": "obesity_prev", "rr": 1.5},
    "alcohol_liver": {"prevalence_col": "heavy_drinking_prev", "rr": 3.0},
    "unsafe_water_diarrhea": {"prevalence_col": "unsafe_water_pct", "rr": 2.5},
}
