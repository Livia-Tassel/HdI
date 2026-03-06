"""Tests for statistical models."""

import pytest
import numpy as np
import pandas as pd


class TestPAF:
    def test_paf_basic(self):
        from hdi.models.attribution import compute_paf
        # Known example: prevalence=0.3, RR=2.0
        paf = compute_paf(0.3, 2.0)
        expected = 0.3 * 1.0 / (1 + 0.3 * 1.0)
        assert paf == pytest.approx(expected, rel=1e-6)

    def test_paf_zero_prevalence(self):
        from hdi.models.attribution import compute_paf
        assert compute_paf(0.0, 5.0) == 0.0

    def test_paf_rr_one(self):
        from hdi.models.attribution import compute_paf
        assert compute_paf(0.5, 1.0) == 0.0

    def test_joint_paf(self):
        from hdi.models.attribution import compute_joint_paf
        # Two independent risk factors
        paf1, paf2 = 0.2, 0.3
        joint = compute_joint_paf([paf1, paf2])
        expected = 1 - (1 - paf1) * (1 - paf2)
        assert joint == pytest.approx(expected, rel=1e-6)


class TestShapley:
    def test_shapley_two_factors(self):
        from hdi.models.attribution import shapley_decomposition
        df = pd.DataFrame({
            "iso3": ["USA"] * 5,
            "year": range(2019, 2024),
            "smoking_prev": [0.2] * 5,
            "obesity_prev": [0.3] * 5,
            "cvd_daly": [5000] * 5,
        })
        risk_cols = {
            "smoking": ("smoking_prev", 2.0),
            "obesity": ("obesity_prev", 1.5),
        }
        result = shapley_decomposition(df, risk_cols, "cvd_daly", country="USA")
        assert len(result) == 2
        assert result["shapley_pct"].sum() == pytest.approx(100.0, rel=0.1)


class TestClustering:
    def test_gini_perfect_equality(self):
        from hdi.models.clustering import compute_gini
        values = np.array([100.0] * 10)
        assert compute_gini(values) == pytest.approx(0.0, abs=1e-10)

    def test_theil_perfect_equality(self):
        from hdi.models.clustering import compute_theil
        values = np.array([100.0] * 10)
        assert compute_theil(values) == pytest.approx(0.0, abs=1e-10)


class TestEValue:
    def test_e_value(self):
        from hdi.models.causal import compute_e_value
        # RR=2.0 -> E-value = 2 + sqrt(2*1) = 2 + 1.414 = 3.414
        e = compute_e_value(2.0)
        assert e == pytest.approx(2.0 + np.sqrt(2.0), rel=1e-4)
