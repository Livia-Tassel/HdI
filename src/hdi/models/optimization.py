"""DEA, LP optimization, and multi-objective optimization for resource allocation."""

from __future__ import annotations

import logging
from dataclasses import dataclass

import numpy as np
import pandas as pd

logger = logging.getLogger(__name__)


@dataclass
class DEAResult:
    """Container for DEA efficiency scores."""
    country_scores: pd.DataFrame  # iso3, efficiency, returns_to_scale
    input_slacks: pd.DataFrame | None = None
    output_slacks: pd.DataFrame | None = None


@dataclass
class OptimizationResult:
    """Container for resource allocation optimization results."""
    objective: str
    status: str
    optimal_allocation: pd.DataFrame  # iso3, current, optimal, change
    objective_value: float
    shadow_prices: dict | None = None


def dea_efficiency(
    df: pd.DataFrame,
    input_cols: list[str],
    output_cols: list[str],
    entity_col: str = "iso3",
    orientation: str = "input",
    returns: str = "vrs",
) -> DEAResult:
    """Data Envelopment Analysis using PuLP linear programming.

    Parameters
    ----------
    df : DataFrame with entity, inputs, and outputs
    input_cols : input variable column names (e.g., expenditure, beds, physicians)
    output_cols : output variable column names (e.g., life_expectancy, 1/mortality)
    entity_col : entity identifier
    orientation : 'input' (minimize inputs) or 'output' (maximize outputs)
    returns : 'crs' (constant) or 'vrs' (variable returns to scale)
    """
    from pulp import LpProblem, LpMinimize, LpMaximize, LpVariable, lpSum, value

    data = df[[entity_col] + input_cols + output_cols].dropna()
    entities = data[entity_col].values
    n = len(entities)

    inputs = data[input_cols].values
    outputs = data[output_cols].values

    scores = []

    for k in range(n):
        if orientation == "input":
            prob = LpProblem(f"DEA_{entities[k]}", LpMinimize)
            theta = LpVariable("theta", 0)
            lambdas = [LpVariable(f"lambda_{j}", 0) for j in range(n)]

            prob += theta  # minimize efficiency score

            # Output constraints: sum(lambda_j * y_j) >= y_k
            for r in range(len(output_cols)):
                prob += lpSum(lambdas[j] * outputs[j, r] for j in range(n)) >= outputs[k, r]

            # Input constraints: sum(lambda_j * x_j) <= theta * x_k
            for i_idx in range(len(input_cols)):
                prob += lpSum(lambdas[j] * inputs[j, i_idx] for j in range(n)) <= theta * inputs[k, i_idx]

        else:  # output orientation
            prob = LpProblem(f"DEA_{entities[k]}", LpMaximize)
            theta = LpVariable("theta", 0)
            lambdas = [LpVariable(f"lambda_{j}", 0) for j in range(n)]

            prob += theta

            for i_idx in range(len(input_cols)):
                prob += lpSum(lambdas[j] * inputs[j, i_idx] for j in range(n)) <= inputs[k, i_idx]

            for r in range(len(output_cols)):
                prob += lpSum(lambdas[j] * outputs[j, r] for j in range(n)) >= theta * outputs[k, r]

        # VRS constraint
        if returns == "vrs":
            prob += lpSum(lambdas) == 1

        prob.solve()
        eff = value(theta) if value(theta) is not None else np.nan
        scores.append({
            entity_col: entities[k],
            "efficiency": eff,
            "efficient": abs(eff - 1.0) < 1e-6 if orientation == "input" else eff >= 1.0 - 1e-6,
        })

    return DEAResult(
        country_scores=pd.DataFrame(scores),
    )


def classify_quadrants(
    df: pd.DataFrame,
    input_index_col: str,
    output_index_col: str,
    entity_col: str = "iso3",
) -> pd.DataFrame:
    """Classify countries into four quadrants based on input/output indices.

    Q1: High Input / High Output (efficient, well-resourced)
    Q2: Low Input / High Output (efficient, resource-constrained)
    Q3: High Input / Low Output (inefficient)
    Q4: Low Input / Low Output (under-resourced, poor outcomes)
    """
    data = df[[entity_col, input_index_col, output_index_col]].dropna().copy()

    input_median = data[input_index_col].median()
    output_median = data[output_index_col].median()

    conditions = [
        (data[input_index_col] >= input_median) & (data[output_index_col] >= output_median),
        (data[input_index_col] < input_median) & (data[output_index_col] >= output_median),
        (data[input_index_col] >= input_median) & (data[output_index_col] < output_median),
        (data[input_index_col] < input_median) & (data[output_index_col] < output_median),
    ]
    labels = ["Q1_high_high", "Q2_low_high", "Q3_high_low", "Q4_low_low"]
    data["quadrant"] = np.select(conditions, labels, default="unclassified")

    return data


def optimize_allocation_max_output(
    df: pd.DataFrame,
    output_col: str,
    input_col: str,
    entity_col: str = "iso3",
    budget_multiplier: float = 1.0,
) -> OptimizationResult:
    """Maximize aggregate health output subject to total budget constraint.

    max sum_i f_i(x_i) s.t. sum_i x_i <= B, x_i in [x_i_min, x_i_max]

    Uses CVXPY for convex optimization with concave production functions.
    """
    import cvxpy as cp

    data = df[[entity_col, input_col, output_col]].dropna()
    n = len(data)
    current_inputs = data[input_col].values
    current_outputs = data[output_col].values

    total_budget = current_inputs.sum() * budget_multiplier

    # Estimate concave production function parameters (log model)
    # output = a * log(input) + b
    log_inputs = np.log(current_inputs + 1)
    from numpy.polynomial.polynomial import polyfit
    b_coef, a_coef = polyfit(log_inputs, current_outputs, 1)

    # Optimization
    x = cp.Variable(n, nonneg=True)

    # Objective: maximize sum of estimated outputs
    # Using concave approximation: a * log(x) + b
    objective = cp.Maximize(cp.sum(a_coef * cp.log(x + 1) + b_coef))

    constraints = [
        cp.sum(x) <= total_budget,
        x >= current_inputs * 0.5,  # min 50% of current
        x <= current_inputs * 2.0,  # max 200% of current
    ]

    prob = cp.Problem(objective, constraints)
    prob.solve()

    optimal = x.value if x.value is not None else current_inputs

    result_df = pd.DataFrame({
        entity_col: data[entity_col].values,
        "current": current_inputs,
        "optimal": optimal,
        "change": optimal - current_inputs,
        "change_pct": (optimal - current_inputs) / current_inputs * 100,
    })

    return OptimizationResult(
        objective="maximize_aggregate_output",
        status=prob.status,
        optimal_allocation=result_df,
        objective_value=prob.value if prob.value else 0.0,
    )


def optimize_allocation_maximin(
    df: pd.DataFrame,
    output_col: str,
    input_col: str,
    entity_col: str = "iso3",
    budget_multiplier: float = 1.0,
) -> OptimizationResult:
    """Rawlsian maximin: maximize the minimum health output.

    max min_i {f_i(x_i)} s.t. sum_i x_i <= B, x_i >= 0
    """
    import cvxpy as cp

    data = df[[entity_col, input_col, output_col]].dropna()
    n = len(data)
    current_inputs = data[input_col].values

    total_budget = current_inputs.sum() * budget_multiplier

    log_inputs = np.log(current_inputs + 1)
    current_outputs = data[output_col].values
    from numpy.polynomial.polynomial import polyfit
    b_coef, a_coef = polyfit(log_inputs, current_outputs, 1)

    x = cp.Variable(n, nonneg=True)
    z = cp.Variable()  # auxiliary for min

    objective = cp.Maximize(z)

    constraints = [
        cp.sum(x) <= total_budget,
        x >= current_inputs * 0.3,
    ]
    # z <= f_i(x_i) for all i
    for i in range(n):
        constraints.append(z <= a_coef * cp.log(x[i] + 1) + b_coef)

    prob = cp.Problem(objective, constraints)
    prob.solve()

    optimal = x.value if x.value is not None else current_inputs

    result_df = pd.DataFrame({
        entity_col: data[entity_col].values,
        "current": current_inputs,
        "optimal": optimal,
        "change": optimal - current_inputs,
        "change_pct": (optimal - current_inputs) / current_inputs * 100,
    })

    return OptimizationResult(
        objective="maximin",
        status=prob.status,
        optimal_allocation=result_df,
        objective_value=prob.value if prob.value else 0.0,
    )


def malmquist_index(
    df: pd.DataFrame,
    input_cols: list[str],
    output_cols: list[str],
    entity_col: str = "iso3",
    year_col: str = "year",
    year_pairs: list[tuple[int, int]] | None = None,
) -> pd.DataFrame:
    """Compute Malmquist Productivity Index between year pairs.

    Decomposes productivity change into:
    - Technical efficiency change (catching up)
    - Technological change (frontier shift)
    """
    if year_pairs is None:
        years = sorted(df[year_col].unique())
        year_pairs = [(years[i], years[i + 1]) for i in range(len(years) - 1)]

    results = []

    for y0, y1 in year_pairs:
        df0 = df[df[year_col] == y0]
        df1 = df[df[year_col] == y1]

        # DEA scores for each period against own and cross frontiers
        dea_00 = dea_efficiency(df0, input_cols, output_cols, entity_col)
        dea_11 = dea_efficiency(df1, input_cols, output_cols, entity_col)

        # Merge scores
        scores = dea_00.country_scores[[entity_col, "efficiency"]].rename(
            columns={"efficiency": f"eff_{y0}"}
        ).merge(
            dea_11.country_scores[[entity_col, "efficiency"]].rename(
                columns={"efficiency": f"eff_{y1}"}
            ),
            on=entity_col,
            how="inner",
        )

        scores["period"] = f"{y0}-{y1}"
        scores["efficiency_change"] = scores[f"eff_{y1}"] / scores[f"eff_{y0}"]
        # Simplified Malmquist (full version needs cross-period DEA)
        scores["malmquist"] = scores["efficiency_change"]

        results.append(scores)

    return pd.concat(results, ignore_index=True) if results else pd.DataFrame()
