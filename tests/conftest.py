"""Pytest configuration and shared fixtures."""

import sys
from pathlib import Path

import pytest
import pandas as pd
import numpy as np

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))


@pytest.fixture
def sample_panel():
    """Create a small sample panel for testing."""
    np.random.seed(42)
    countries = ["USA", "CHN", "GBR", "IND", "BRA", "NGA", "JPN", "DEU", "FRA", "AUS"]
    years = range(2000, 2024)

    rows = []
    for iso3 in countries:
        base_le = np.random.uniform(55, 80)
        base_gdp = np.random.uniform(1000, 50000)
        for year in years:
            rows.append({
                "iso3": iso3,
                "year": year,
                "life_expectancy": base_le + (year - 2000) * 0.2 + np.random.normal(0, 0.5),
                "gdp_pc_ppp": base_gdp * (1.02 ** (year - 2000)) + np.random.normal(0, 500),
                "health_exp_pct_gdp": np.random.uniform(3, 12),
                "physicians_per_1000": np.random.uniform(0.1, 4),
                "hospital_beds_per_1000": np.random.uniform(0.5, 8),
                "daly_rate": np.random.uniform(10000, 60000),
                "smoking_prev": np.random.uniform(0.05, 0.40),
                "pm25_annual_mean": np.random.uniform(5, 80),
                "who_region": np.random.choice(["AFRO", "AMRO", "SEARO", "EURO", "EMRO", "WPRO"]),
                "wb_income": np.random.choice(["LIC", "LMC", "UMC", "HIC"]),
            })

    return pd.DataFrame(rows)


@pytest.fixture
def sample_china_panel():
    """Create a small sample China province panel."""
    np.random.seed(42)
    provinces = ["Beijing", "Shanghai", "Guangdong", "Sichuan", "Henan"]
    years = range(2003, 2024)

    rows = []
    for province in provinces:
        for year in years:
            rows.append({
                "province": province,
                "year": year,
                "hospital_beds_per_1000": np.random.uniform(3, 8),
                "physicians_per_1000": np.random.uniform(1, 4),
                "health_expenditure_pc": np.random.uniform(2000, 10000),
            })

    return pd.DataFrame(rows)
