"""Tests for data pipeline: loaders, cleaners, integrator."""

import pytest
import pandas as pd
import numpy as np


class TestCountryHarmonization:
    def test_iso3_passthrough(self):
        from hdi.data.cleaners import harmonize_country_code
        assert harmonize_country_code("USA") == "USA"
        assert harmonize_country_code("CHN") == "CHN"
        assert harmonize_country_code("GBR") == "GBR"

    def test_common_names(self):
        from hdi.data.cleaners import harmonize_country_code
        assert harmonize_country_code("United States") == "USA"
        assert harmonize_country_code("United Kingdom") == "GBR"
        assert harmonize_country_code("South Korea") == "KOR"

    def test_alias_map(self):
        from hdi.data.cleaners import harmonize_country_code
        assert harmonize_country_code("Türkiye") == "TUR"
        assert harmonize_country_code("Viet Nam") == "VNM"
        assert harmonize_country_code("Russian Federation") == "RUS"

    def test_invalid_returns_none(self):
        from hdi.data.cleaners import harmonize_country_code
        assert harmonize_country_code("") is None
        assert harmonize_country_code("nan") is None
        assert harmonize_country_code("ZZZZZ") is None

    def test_harmonize_column(self):
        from hdi.data.cleaners import harmonize_country_column
        df = pd.DataFrame({"country": ["United States", "China", "Invalid"]})
        result = harmonize_country_column(df)
        assert result["iso3"].iloc[0] == "USA"
        assert result["iso3"].iloc[1] == "CHN"
        assert pd.isna(result["iso3"].iloc[2])


class TestCleaningUtils:
    def test_normalize_column_names(self):
        from hdi.data.cleaners import normalize_column_names
        df = pd.DataFrame({"Country Name": [1], "GDP (PPP)": [2], "Year  ": [3]})
        result = normalize_column_names(df)
        assert "country_name" in result.columns
        assert "gdp_ppp" in result.columns
        assert "year" in result.columns

    def test_filter_year_range(self):
        from hdi.data.cleaners import filter_year_range
        df = pd.DataFrame({"year": [1990, 2000, 2010, 2023, 2030]})
        result = filter_year_range(df, year_min=2000, year_max=2023)
        assert len(result) == 3
        assert result["year"].min() == 2000
        assert result["year"].max() == 2023

    def test_interpolate_gaps(self):
        from hdi.data.cleaners import interpolate_gaps
        df = pd.DataFrame({
            "iso3": ["USA"] * 5,
            "year": [2000, 2001, 2002, 2003, 2004],
            "value": [1.0, np.nan, 3.0, np.nan, 5.0],
        })
        result = interpolate_gaps(df, ["iso3"], ["value"], max_gap=2)
        assert result["value"].iloc[1] == pytest.approx(2.0)

    def test_clean_country_year_dataset_wide_years(self):
        from hdi.data.cleaners import clean_country_year_dataset
        df = pd.DataFrame({
            "Country": ["United States", "China"],
            "2000": ["1.0", "2.0"],
            "2001": ["3.0", "4.0"],
            "2002": ["5.0", "6.0"],
        })
        result = clean_country_year_dataset(df)
        assert set(result["iso3"].dropna()) == {"USA", "CHN"}
        assert set(result["year"].astype(int)) == {2000, 2001, 2002}
        assert "value" in result.columns

    def test_add_who_region_preserves_existing_values(self):
        from hdi.data.cleaners import add_who_region
        df = pd.DataFrame({"iso3": ["USA"], "who_region": ["AMRO"]})
        result = add_who_region(df)
        assert result["who_region"].iloc[0] == "AMRO"


class TestValidators:
    def test_master_panel_schema_valid(self):
        from hdi.data.validators import validate_master_panel
        df = pd.DataFrame({
            "iso3": ["USA", "CHN", "GBR"],
            "year": [2020, 2020, 2020],
        })
        validate_master_panel(df)  # should not raise

    def test_master_panel_schema_invalid_iso(self):
        from hdi.data.validators import validate_master_panel
        import pandera
        df = pd.DataFrame({
            "iso3": ["US", "CHN", "GBR"],  # "US" is only 2 chars
            "year": [2020, 2020, 2020],
        })
        with pytest.raises(pandera.errors.SchemaErrors):
            validate_master_panel(df)
