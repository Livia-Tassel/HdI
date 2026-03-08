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
    min_ratio: float = 0.5,
    max_ratio: float = 2.0,
) -> OptimizationResult:
    """Maximize aggregate health output subject to total budget constraint.

    max sum_i f_i(x_i) s.t. sum_i x_i <= B, x_i in [x_i_min, x_i_max]

    Uses CVXPY for convex optimization with concave production functions.
    """
    data = df[[entity_col, input_col, output_col]].dropna()
    if data.empty:
        return OptimizationResult(
            objective="max_output",
            status="no_data",
            optimal_allocation=pd.DataFrame(columns=[entity_col, "current", "optimal", "change", "change_pct"]),
            objective_value=0.0,
        )
    current_inputs = data[input_col].values
    current_outputs = data[output_col].values
    total_budget = current_inputs.sum() * budget_multiplier
    a_coef, b_coef = _fit_log_production(current_inputs, current_outputs)
    lower = current_inputs * min_ratio
    upper = current_inputs * max_ratio

    optimal, status = _solve_constrained_problem(
        current_inputs=current_inputs,
        total_budget=total_budget,
        lower=lower,
        upper=upper,
        objective="max_output",
        a_coef=a_coef,
        b_coef=b_coef,
    )
    objective_value = float(np.sum(_project_outputs(optimal, a_coef, b_coef)))

    result_df = pd.DataFrame({
        entity_col: data[entity_col].values,
        "current": current_inputs,
        "optimal": optimal,
        "change": optimal - current_inputs,
        "change_pct": (optimal - current_inputs) / current_inputs * 100,
    })

    return OptimizationResult(
        objective="max_output",
        status=status,
        optimal_allocation=result_df,
        objective_value=objective_value,
    )


def optimize_allocation_maximin(
    df: pd.DataFrame,
    output_col: str,
    input_col: str,
    entity_col: str = "iso3",
    budget_multiplier: float = 1.0,
    min_ratio: float = 0.3,
    max_ratio: float = 2.0,
) -> OptimizationResult:
    """Rawlsian maximin: maximize the minimum health output.

    max min_i {f_i(x_i)} s.t. sum_i x_i <= B, x_i >= 0
    """
    data = df[[entity_col, input_col, output_col]].dropna()
    if data.empty:
        return OptimizationResult(
            objective="maximin",
            status="no_data",
            optimal_allocation=pd.DataFrame(columns=[entity_col, "current", "optimal", "change", "change_pct"]),
            objective_value=0.0,
        )
    current_inputs = data[input_col].values
    total_budget = current_inputs.sum() * budget_multiplier
    current_outputs = data[output_col].values
    a_coef, b_coef = _fit_log_production(current_inputs, current_outputs)
    lower = current_inputs * min_ratio
    upper = current_inputs * max_ratio

    optimal, status = _solve_constrained_problem(
        current_inputs=current_inputs,
        total_budget=total_budget,
        lower=lower,
        upper=upper,
        objective="maximin",
        a_coef=a_coef,
        b_coef=b_coef,
    )
    objective_value = float(np.min(_project_outputs(optimal, a_coef, b_coef)))

    result_df = pd.DataFrame({
        entity_col: data[entity_col].values,
        "current": current_inputs,
        "optimal": optimal,
        "change": optimal - current_inputs,
        "change_pct": (optimal - current_inputs) / current_inputs * 100,
    })

    return OptimizationResult(
        objective="maximin",
        status=status,
        optimal_allocation=result_df,
        objective_value=objective_value,
    )


def _fit_log_production(current_inputs: np.ndarray, current_outputs: np.ndarray) -> tuple[float, float]:
    """Fit a monotonic log production curve used by the allocation optimizers."""
    log_inputs = np.log(np.clip(current_inputs, 0.0, None) + 1.0)
    from numpy.polynomial.polynomial import polyfit

    b_coef, a_coef = polyfit(log_inputs, current_outputs, 1)
    if not np.isfinite(a_coef):
        a_coef = 1e-6
    if not np.isfinite(b_coef):
        b_coef = 0.0
    return float(max(a_coef, 1e-6)), float(b_coef)


def _project_outputs(inputs: np.ndarray, a_coef: float, b_coef: float) -> np.ndarray:
    return a_coef * np.log(np.clip(inputs, 0.0, None) + 1.0) + b_coef


def _rebalance_to_budget(values: np.ndarray, lower: np.ndarray, upper: np.ndarray, total_budget: float) -> np.ndarray:
    """Project a candidate allocation onto box constraints and an exact total budget."""
    bounded = np.clip(values.astype(float), lower, upper)
    feasible_budget = float(np.clip(total_budget, lower.sum(), upper.sum()))
    residual = feasible_budget - float(bounded.sum())

    for _ in range(200):
        if abs(residual) < 1e-8:
            break
        if residual > 0:
            room = upper - bounded
        else:
            room = bounded - lower
        eligible = room > 1e-10
        if not eligible.any():
            break
        step = residual * room[eligible] / room[eligible].sum()
        bounded[eligible] += step
        bounded = np.clip(bounded, lower, upper)
        residual = feasible_budget - float(bounded.sum())

    return bounded


def _waterfill_box_budget(lower: np.ndarray, upper: np.ndarray, total_budget: float) -> np.ndarray:
    """Solve sum(log(x_i + 1)) with box constraints by equalizing uncapped allocations.

    With a shared concave log response curve, the aggregate-output optimum reduces to a
    capped water-filling problem over the per-entity allocations.
    """
    feasible_budget = float(np.clip(total_budget, lower.sum(), upper.sum()))
    lo = float(np.min(lower))
    hi = float(np.max(upper))

    for _ in range(200):
        mid = (lo + hi) / 2.0
        trial = np.clip(np.full_like(lower, mid, dtype=float), lower, upper)
        if float(trial.sum()) < feasible_budget:
            lo = mid
        else:
            hi = mid

    trial = np.clip(np.full_like(lower, (lo + hi) / 2.0, dtype=float), lower, upper)
    return _rebalance_to_budget(trial, lower, upper, feasible_budget)


def _solve_constrained_problem(
    current_inputs: np.ndarray,
    total_budget: float,
    lower: np.ndarray,
    upper: np.ndarray,
    objective: str,
    a_coef: float,
    b_coef: float,
) -> tuple[np.ndarray, str]:
    """Solve the resource allocation problem with SciPy SLSQP and a safe fallback."""
    from scipy.optimize import minimize

    feasible_budget = float(np.clip(total_budget, lower.sum(), upper.sum()))
    start = _rebalance_to_budget(current_inputs * (feasible_budget / max(current_inputs.sum(), 1e-9)), lower, upper, feasible_budget)

    if objective == "max_output":
        return _waterfill_box_budget(lower, upper, feasible_budget), "optimal_waterfill"

    def objective_fn(vector: np.ndarray) -> float:
        return -float(vector[-1])

    constraints = [{"type": "eq", "fun": lambda vector: float(np.sum(vector[:-1]) - feasible_budget)}]
    for index in range(len(current_inputs)):
        constraints.append(
            {
                "type": "ineq",
                "fun": lambda vector, idx=index: float(_project_outputs(np.array([vector[idx]]), a_coef, b_coef)[0] - vector[-1]),
            }
        )

    start_with_floor = np.concatenate([start, [float(np.min(_project_outputs(start, a_coef, b_coef)))]])
    result = minimize(
        objective_fn,
        start_with_floor,
        method="SLSQP",
        bounds=[*list(zip(lower, upper, strict=False)), (None, None)],
        constraints=constraints,
        options={"maxiter": 800, "ftol": 1e-9},
    )
    if result.success and result.x is not None:
        allocation = _rebalance_to_budget(result.x[:-1], lower, upper, feasible_budget)
        return allocation, "optimal_slsqp"
    logger.warning("Falling back from maximin optimization: %s", result.message if result else "unknown error")
    return start, "fallback_starting_point"


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
