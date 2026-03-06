"""Causal inference: DoWhy DAGs, IV estimation, DiD, mediation analysis."""

from __future__ import annotations

import logging
from dataclasses import dataclass

import numpy as np
import pandas as pd

logger = logging.getLogger(__name__)


@dataclass
class CausalResult:
    """Container for causal estimation results."""
    method: str
    treatment: str
    outcome: str
    estimate: float
    std_error: float | None = None
    p_value: float | None = None
    ci_lower: float | None = None
    ci_upper: float | None = None
    first_stage_f: float | None = None  # IV-specific
    e_value: float | None = None
    refutation_results: dict | None = None


def build_causal_dag(
    treatment: str,
    outcome: str,
    confounders: list[str],
    instruments: list[str] | None = None,
    mediators: list[str] | None = None,
) -> "dowhy.CausalModel":
    """Build a DoWhy causal model from a DAG specification.

    Parameters
    ----------
    treatment : treatment variable name
    outcome : outcome variable name
    confounders : common causes of treatment and outcome
    instruments : instrumental variables (affect treatment, not outcome directly)
    mediators : variables on the causal path treatment -> mediator -> outcome
    """
    import dowhy

    # Build GML graph string
    nodes = set([treatment, outcome] + confounders)
    if instruments:
        nodes.update(instruments)
    if mediators:
        nodes.update(mediators)

    edges = []
    # Confounders -> treatment and outcome
    for c in confounders:
        edges.append(f'  {c} -> {treatment}')
        edges.append(f'  {c} -> {outcome}')
    # Treatment -> outcome
    edges.append(f'  {treatment} -> {outcome}')
    # Instruments -> treatment
    if instruments:
        for iv in instruments:
            edges.append(f'  {iv} -> {treatment}')
    # Treatment -> mediators -> outcome
    if mediators:
        for m in mediators:
            edges.append(f'  {treatment} -> {m}')
            edges.append(f'  {m} -> {outcome}')

    gml = "digraph {\n" + "\n".join(edges) + "\n}"

    return gml


def iv_2sls(
    df: pd.DataFrame,
    dep_var: str,
    endog_var: str,
    instruments: list[str],
    exog_vars: list[str] | None = None,
    entity_col: str = "iso3",
    time_col: str = "year",
) -> CausalResult:
    """Two-Stage Least Squares (2SLS) instrumental variable estimation.

    Parameters
    ----------
    dep_var : outcome variable
    endog_var : endogenous treatment variable
    instruments : excluded instruments
    exog_vars : exogenous control variables
    """
    from linearmodels.iv import IV2SLS

    data = df.copy()
    cols_needed = [entity_col, time_col, dep_var, endog_var] + instruments
    if exog_vars:
        cols_needed += exog_vars
    data = data[cols_needed].dropna()
    data = data.set_index([entity_col, time_col])

    y = data[dep_var]
    endog = data[[endog_var]]
    exog = data[exog_vars] if exog_vars else None
    instr = data[instruments]

    model = IV2SLS(y, exog, endog, instr)
    result = model.fit(cov_type="kernel")

    # First-stage F-statistic
    first_f = result.first_stage.diagnostics["f.stat"].iloc[0] if hasattr(result, "first_stage") else None

    return CausalResult(
        method="IV-2SLS",
        treatment=endog_var,
        outcome=dep_var,
        estimate=result.params[endog_var],
        std_error=result.std_errors[endog_var],
        p_value=result.pvalues[endog_var],
        ci_lower=result.conf_int().loc[endog_var, "lower"],
        ci_upper=result.conf_int().loc[endog_var, "upper"],
        first_stage_f=first_f,
    )


def difference_in_differences(
    df: pd.DataFrame,
    dep_var: str,
    treat_col: str,
    post_col: str,
    controls: list[str] | None = None,
    entity_col: str = "iso3",
    time_col: str = "year",
) -> CausalResult:
    """Difference-in-Differences estimation with entity and time fixed effects.

    Parameters
    ----------
    dep_var : outcome variable
    treat_col : binary treatment group indicator
    post_col : binary post-treatment period indicator
    controls : additional control variables
    """
    from linearmodels.panel import PanelOLS

    data = df.copy()
    data["did_interaction"] = data[treat_col] * data[post_col]

    indep = ["did_interaction", treat_col, post_col]
    if controls:
        indep += controls

    cols = [entity_col, time_col, dep_var] + indep
    data = data[cols].dropna()
    data = data.set_index([entity_col, time_col])

    y = data[dep_var]
    X = data[indep]

    model = PanelOLS(y, X, entity_effects=True, time_effects=True)
    result = model.fit(cov_type="kernel")

    return CausalResult(
        method="DiD",
        treatment=treat_col,
        outcome=dep_var,
        estimate=result.params["did_interaction"],
        std_error=result.std_errors["did_interaction"],
        p_value=result.pvalues["did_interaction"],
        ci_lower=result.conf_int().loc["did_interaction", "lower"],
        ci_upper=result.conf_int().loc["did_interaction", "upper"],
    )


def mediation_analysis(
    df: pd.DataFrame,
    treatment: str,
    outcome: str,
    mediator: str,
    controls: list[str] | None = None,
    n_bootstrap: int = 1000,
    seed: int = 42,
) -> dict:
    """Baron-Kenny mediation analysis with bootstrap confidence intervals.

    Decomposes total effect into:
    - Direct effect: treatment -> outcome
    - Indirect effect: treatment -> mediator -> outcome

    Returns dict with total, direct, indirect effects and CIs.
    """
    from sklearn.linear_model import LinearRegression

    rng = np.random.RandomState(seed)
    cols = [treatment, outcome, mediator]
    if controls:
        cols += controls
    data = df[cols].dropna()

    X_base = [treatment] + (controls or [])

    def _estimate(sample):
        # Path c: total effect (treatment -> outcome)
        X_c = sample[X_base].values
        y_c = sample[outcome].values
        model_c = LinearRegression().fit(X_c, y_c)
        total_effect = model_c.coef_[0]

        # Path a: treatment -> mediator
        X_a = sample[X_base].values
        y_a = sample[mediator].values
        model_a = LinearRegression().fit(X_a, y_a)
        a = model_a.coef_[0]

        # Path b + c': mediator + treatment -> outcome
        X_bc = sample[X_base + [mediator]].values
        y_bc = sample[outcome].values
        model_bc = LinearRegression().fit(X_bc, y_bc)
        direct_effect = model_bc.coef_[0]
        b = model_bc.coef_[-1]

        indirect_effect = a * b
        return total_effect, direct_effect, indirect_effect

    # Point estimates
    total, direct, indirect = _estimate(data)

    # Bootstrap CIs
    boot_results = []
    for _ in range(n_bootstrap):
        boot_idx = rng.choice(len(data), size=len(data), replace=True)
        boot_sample = data.iloc[boot_idx]
        boot_results.append(_estimate(boot_sample))

    boot_arr = np.array(boot_results)

    return {
        "total_effect": total,
        "direct_effect": direct,
        "indirect_effect": indirect,
        "mediated_fraction": indirect / total if abs(total) > 1e-10 else np.nan,
        "total_ci": tuple(np.percentile(boot_arr[:, 0], [2.5, 97.5])),
        "direct_ci": tuple(np.percentile(boot_arr[:, 1], [2.5, 97.5])),
        "indirect_ci": tuple(np.percentile(boot_arr[:, 2], [2.5, 97.5])),
    }


def compute_e_value(rr: float) -> float:
    """Compute the E-value for unmeasured confounding sensitivity.

    The E-value is the minimum strength of association an unmeasured
    confounder would need to fully explain away the observed effect.

    Parameters
    ----------
    rr : observed risk ratio (or exp(coefficient) for log-linear models)
    """
    if rr < 1:
        rr = 1.0 / rr
    return rr + np.sqrt(rr * (rr - 1))
