"""Panel regression models: Fixed Effects, GMM, Driscoll-Kraay."""

from __future__ import annotations

import logging
from dataclasses import dataclass, field

import numpy as np
import pandas as pd

logger = logging.getLogger(__name__)


@dataclass
class PanelResult:
    """Container for panel regression results."""
    model_name: str
    dependent_var: str
    coefficients: dict[str, float]
    std_errors: dict[str, float]
    p_values: dict[str, float]
    r_squared: float
    r_squared_within: float | None = None
    n_obs: int = 0
    n_groups: int = 0
    f_stat: float | None = None
    summary_text: str = ""


def panel_fixed_effects(
    df: pd.DataFrame,
    dep_var: str,
    indep_vars: list[str],
    entity_col: str = "iso3",
    time_col: str = "year",
    time_effects: bool = True,
    cov_type: str = "kernel",
) -> PanelResult:
    """Estimate panel Fixed Effects model with Driscoll-Kraay standard errors.

    Parameters
    ----------
    df : panel DataFrame
    dep_var : dependent variable column name
    indep_vars : list of independent variable column names
    entity_col : entity identifier (country)
    time_col : time identifier (year)
    time_effects : include time fixed effects
    cov_type : 'kernel' for Driscoll-Kraay, 'clustered' for entity clusters

    Returns
    -------
    PanelResult with coefficients, SEs, p-values, R²
    """
    from linearmodels.panel import PanelOLS

    # Prepare panel data
    data = df[[entity_col, time_col, dep_var] + indep_vars].dropna()
    data = data.set_index([entity_col, time_col])

    y = data[dep_var]
    X = data[indep_vars]

    model = PanelOLS(y, X, entity_effects=True, time_effects=time_effects)
    result = model.fit(cov_type=cov_type)

    return PanelResult(
        model_name="Panel FE (Driscoll-Kraay)" if cov_type == "kernel" else "Panel FE (Clustered)",
        dependent_var=dep_var,
        coefficients=dict(result.params),
        std_errors=dict(result.std_errors),
        p_values=dict(result.pvalues),
        r_squared=result.rsquared,
        r_squared_within=result.rsquared_within,
        n_obs=result.nobs,
        n_groups=result.entity_info.total,
        f_stat=result.f_statistic.stat if result.f_statistic else None,
        summary_text=str(result.summary),
    )


def mundlak_cre(
    df: pd.DataFrame,
    dep_var: str,
    indep_vars: list[str],
    entity_col: str = "iso3",
    time_col: str = "year",
) -> PanelResult:
    """Mundlak (Correlated Random Effects) model.

    Adds group means of time-varying regressors to a RE model.
    This allows testing FE vs RE via a Hausman-like test on the group means.
    """
    from linearmodels.panel import RandomEffects

    data = df[[entity_col, time_col, dep_var] + indep_vars].dropna().copy()

    # Add group means (Mundlak terms)
    mundlak_vars = []
    for var in indep_vars:
        mean_col = f"{var}_mean"
        data[mean_col] = data.groupby(entity_col)[var].transform("mean")
        mundlak_vars.append(mean_col)

    data = data.set_index([entity_col, time_col])
    y = data[dep_var]
    X = data[indep_vars + mundlak_vars]

    model = RandomEffects(y, X)
    result = model.fit()

    return PanelResult(
        model_name="Mundlak CRE",
        dependent_var=dep_var,
        coefficients=dict(result.params),
        std_errors=dict(result.std_errors),
        p_values=dict(result.pvalues),
        r_squared=result.rsquared,
        n_obs=result.nobs,
        n_groups=result.entity_info.total,
        summary_text=str(result.summary),
    )


def shap_importance(
    df: pd.DataFrame,
    dep_var: str,
    indep_vars: list[str],
    n_estimators: int = 200,
    seed: int = 42,
) -> tuple[pd.DataFrame, object]:
    """SHAP-based variable importance using XGBoost.

    Returns (shap_values_df, shap_explainer) for visualization.
    """
    import xgboost as xgb
    import shap

    data = df[indep_vars + [dep_var]].dropna()
    X = data[indep_vars]
    y = data[dep_var]

    model = xgb.XGBRegressor(
        n_estimators=n_estimators,
        max_depth=6,
        learning_rate=0.1,
        random_state=seed,
    )
    model.fit(X, y)

    explainer = shap.TreeExplainer(model)
    shap_values = explainer.shap_values(X)

    shap_df = pd.DataFrame(shap_values, columns=indep_vars, index=X.index)
    mean_abs_shap = shap_df.abs().mean().sort_values(ascending=False)

    logger.info("SHAP importance (top 10):\n%s", mean_abs_shap.head(10))
    return shap_df, explainer


def results_to_table(results: list[PanelResult]) -> pd.DataFrame:
    """Format multiple panel regression results into a comparison table."""
    rows = []
    all_vars = set()
    for r in results:
        all_vars.update(r.coefficients.keys())

    for var in sorted(all_vars):
        row = {"variable": var}
        for r in results:
            coef = r.coefficients.get(var, np.nan)
            se = r.std_errors.get(var, np.nan)
            p = r.p_values.get(var, np.nan)
            stars = ""
            if pd.notna(p):
                if p < 0.01:
                    stars = "***"
                elif p < 0.05:
                    stars = "**"
                elif p < 0.1:
                    stars = "*"
            row[f"{r.model_name}_coef"] = f"{coef:.4f}{stars}" if pd.notna(coef) else ""
            row[f"{r.model_name}_se"] = f"({se:.4f})" if pd.notna(se) else ""
        rows.append(row)

    # Add summary stats
    for stat_name, getter in [
        ("R²", lambda r: r.r_squared),
        ("R² (within)", lambda r: r.r_squared_within),
        ("N", lambda r: r.n_obs),
        ("Groups", lambda r: r.n_groups),
    ]:
        row = {"variable": stat_name}
        for r in results:
            val = getter(r)
            row[f"{r.model_name}_coef"] = f"{val}" if val is not None else ""
            row[f"{r.model_name}_se"] = ""
        rows.append(row)

    return pd.DataFrame(rows)
