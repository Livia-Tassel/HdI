"""System dynamics simulation and Monte Carlo scenario analysis."""

from __future__ import annotations

import logging
from dataclasses import dataclass

import numpy as np
import pandas as pd
from scipy.integrate import solve_ivp

from hdi.config import SEED

logger = logging.getLogger(__name__)


@dataclass
class ScenarioResult:
    """Container for scenario simulation outputs."""
    scenario_name: str
    country: str
    years: np.ndarray
    trajectories: dict[str, np.ndarray]  # variable_name -> array of values
    ci_lower: dict[str, np.ndarray] | None = None
    ci_upper: dict[str, np.ndarray] | None = None


# ── Scenario definitions ─────────────────────────────────────────────────────

SCENARIOS = {
    "A_tobacco_control": {
        "description": "Aggressive tobacco control (MPOWER), smoking -30% over 20yr",
        "smoking_reduction_rate": 0.30,
        "pm25_target": None,
        "diet_improvement": 0.0,
    },
    "B_air_quality": {
        "description": "PM2.5 -> 15ug/m3 by 2035, 10ug/m3 by 2045",
        "smoking_reduction_rate": 0.0,
        "pm25_target_2035": 15.0,
        "pm25_target_2045": 10.0,
        "diet_improvement": 0.0,
    },
    "C_combined": {
        "description": "Combined tobacco + air quality + dietary improvement",
        "smoking_reduction_rate": 0.30,
        "pm25_target_2035": 15.0,
        "pm25_target_2045": 10.0,
        "diet_improvement": 0.15,
    },
    "D_status_quo": {
        "description": "Status quo - trend extrapolation",
        "smoking_reduction_rate": 0.0,
        "pm25_target": None,
        "diet_improvement": 0.0,
    },
}


def _disease_burden_ode(t, y, params):
    """ODE system for disease burden dynamics.

    State variables:
    y[0] = CVD DALY rate
    y[1] = Respiratory DALY rate
    y[2] = Cancer DALY rate
    y[3] = Smoking prevalence
    y[4] = PM2.5 level

    Parameters encode the exposure-response relationships.
    """
    cvd, resp, cancer, smoking, pm25 = y

    # Exposure-response elasticities
    e_smoking_cvd = params.get("e_smoking_cvd", 0.3)
    e_smoking_cancer = params.get("e_smoking_cancer", 0.5)
    e_pm25_resp = params.get("e_pm25_resp", 0.2)
    e_pm25_cvd = params.get("e_pm25_cvd", 0.1)

    # Background improvement rate (medical progress)
    bg_improvement = params.get("bg_improvement", -0.005)

    # Intervention trajectories
    smoking_trend = params.get("smoking_trend", 0.0)
    pm25_trend = params.get("pm25_trend", 0.0)

    # ODEs
    d_cvd = bg_improvement * cvd + e_smoking_cvd * smoking_trend * cvd + e_pm25_cvd * pm25_trend * cvd
    d_resp = bg_improvement * resp + e_pm25_resp * pm25_trend * resp
    d_cancer = bg_improvement * cancer + e_smoking_cancer * smoking_trend * cancer
    d_smoking = smoking_trend * smoking
    d_pm25 = pm25_trend * pm25

    return [d_cvd, d_resp, d_cancer, d_smoking, d_pm25]


def simulate_scenario(
    initial_conditions: dict[str, float],
    scenario_name: str,
    country: str,
    start_year: int = 2024,
    end_year: int = 2045,
    params: dict | None = None,
) -> ScenarioResult:
    """Simulate a single disease burden scenario.

    Parameters
    ----------
    initial_conditions : dict with keys cvd_daly, resp_daly, cancer_daly, smoking_prev, pm25
    scenario_name : one of SCENARIOS keys
    country : ISO3 code
    start_year, end_year : simulation window
    params : override ODE parameters
    """
    scenario = SCENARIOS.get(scenario_name, SCENARIOS["D_status_quo"])
    sim_params = params or {}

    # Set intervention trajectories based on scenario
    years_span = end_year - start_year
    smoking_rate = scenario.get("smoking_reduction_rate", 0.0)
    sim_params["smoking_trend"] = -smoking_rate / years_span if smoking_rate else 0.0

    pm25_target = scenario.get("pm25_target_2045") or scenario.get("pm25_target")
    if pm25_target and initial_conditions.get("pm25", 0) > pm25_target:
        reduction_frac = (initial_conditions["pm25"] - pm25_target) / initial_conditions["pm25"]
        sim_params["pm25_trend"] = -reduction_frac / years_span
    else:
        sim_params.setdefault("pm25_trend", 0.0)

    # Initial state vector
    y0 = [
        initial_conditions.get("cvd_daly", 5000),
        initial_conditions.get("resp_daly", 2000),
        initial_conditions.get("cancer_daly", 3000),
        initial_conditions.get("smoking_prev", 0.25),
        initial_conditions.get("pm25", 30),
    ]

    t_span = (0, years_span)
    t_eval = np.arange(0, years_span + 1)

    sol = solve_ivp(
        _disease_burden_ode,
        t_span,
        y0,
        args=(sim_params,),
        t_eval=t_eval,
        method="RK45",
    )

    years = np.arange(start_year, start_year + len(sol.t))

    return ScenarioResult(
        scenario_name=scenario_name,
        country=country,
        years=years,
        trajectories={
            "cvd_daly": sol.y[0],
            "resp_daly": sol.y[1],
            "cancer_daly": sol.y[2],
            "smoking_prev": sol.y[3],
            "pm25": sol.y[4],
            "total_daly": sol.y[0] + sol.y[1] + sol.y[2],
        },
    )


def monte_carlo_scenarios(
    initial_conditions: dict[str, float],
    scenario_name: str,
    country: str,
    n_simulations: int = 1000,
    rr_cv: float = 0.15,
    exposure_cv: float = 0.10,
    seed: int = SEED,
    **kwargs,
) -> ScenarioResult:
    """Monte Carlo simulation with parameter uncertainty.

    Draws from RR confidence intervals and exposure trajectory variance
    to produce median + 95% CI for burden projections.
    """
    rng = np.random.RandomState(seed)
    all_trajectories = {}

    for i in range(n_simulations):
        # Perturb parameters
        perturbed_params = {
            "e_smoking_cvd": max(0, rng.normal(0.3, 0.3 * rr_cv)),
            "e_smoking_cancer": max(0, rng.normal(0.5, 0.5 * rr_cv)),
            "e_pm25_resp": max(0, rng.normal(0.2, 0.2 * rr_cv)),
            "e_pm25_cvd": max(0, rng.normal(0.1, 0.1 * rr_cv)),
            "bg_improvement": rng.normal(-0.005, 0.002),
        }

        # Perturb initial conditions
        perturbed_ic = {
            k: max(0, v * rng.normal(1, exposure_cv))
            for k, v in initial_conditions.items()
        }

        result = simulate_scenario(
            perturbed_ic, scenario_name, country, params=perturbed_params, **kwargs
        )

        for var, vals in result.trajectories.items():
            if var not in all_trajectories:
                all_trajectories[var] = []
            all_trajectories[var].append(vals)

    # Compute median and CIs
    median_traj = {}
    ci_lower = {}
    ci_upper = {}

    for var, runs in all_trajectories.items():
        arr = np.array(runs)
        median_traj[var] = np.median(arr, axis=0)
        ci_lower[var] = np.percentile(arr, 2.5, axis=0)
        ci_upper[var] = np.percentile(arr, 97.5, axis=0)

    return ScenarioResult(
        scenario_name=scenario_name,
        country=country,
        years=result.years,
        trajectories=median_traj,
        ci_lower=ci_lower,
        ci_upper=ci_upper,
    )
