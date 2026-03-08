"""Tests for data cleaning and processed panel validation."""

import numpy as np
import pandas as pd
import pytest


class TestCountryHarmonization:
    def test_iso3_passthrough(self):
        from hdi.data.cleaners import harmonize_country_code

        assert harmonize_country_code("USA") == "USA"
        assert harmonize_country_code("CHN") == "CHN"
        assert harmonize_country_code("GBR") == "GBR"

    def test_english_and_chinese_names(self):
        from hdi.data.cleaners import harmonize_country_code

        assert harmonize_country_code("United States") == "USA"
        assert harmonize_country_code("中国") == "CHN"
        assert harmonize_country_code("俄罗斯") == "RUS"
        assert harmonize_country_code("纳米比亚") == "NAM"

    def test_manual_aliases(self):
        from hdi.data.cleaners import harmonize_country_code

        assert harmonize_country_code("捷克共和国") == "CZE"
        assert harmonize_country_code("老挝人民民主共和国") == "LAO"
        assert harmonize_country_code("美利坚合众国") == "USA"

    def test_invalid_returns_none(self):
        from hdi.data.cleaners import harmonize_country_code

        assert harmonize_country_code("") is None
        assert harmonize_country_code("nan") is None
        assert harmonize_country_code("ZZZZZ") is None

    def test_harmonize_column(self):
        from hdi.data.cleaners import harmonize_country_column

        df = pd.DataFrame({"country": ["United States", "中国", "Invalid"]})
        result = harmonize_country_column(df)
        assert result["iso3"].iloc[0] == "USA"
        assert result["iso3"].iloc[1] == "CHN"
        assert pd.isna(result["iso3"].iloc[2])


class TestCleaningUtils:
    def test_normalize_column_names_preserves_chinese(self):
        from hdi.data.cleaners import normalize_column_names

        df = pd.DataFrame({"Country Name": [1], "GDP (PPP)": [2], "死亡或受伤原因": [3]})
        result = normalize_column_names(df)
        assert "country_name" in result.columns
        assert "gdp_ppp" in result.columns
        assert "死亡或受伤原因" in result.columns

    def test_filter_year_range(self):
        from hdi.data.cleaners import filter_year_range

        df = pd.DataFrame({"year": [1990, 2000, 2010, 2023, 2030]})
        result = filter_year_range(df, year_min=2000, year_max=2023)
        assert len(result) == 3
        assert result["year"].min() == 2000
        assert result["year"].max() == 2023

    def test_interpolate_gaps(self):
        from hdi.data.cleaners import interpolate_gaps

        df = pd.DataFrame(
            {
                "iso3": ["USA"] * 5,
                "year": [2000, 2001, 2002, 2003, 2004],
                "value": [1.0, np.nan, 3.0, np.nan, 5.0],
            }
        )
        result = interpolate_gaps(df, ["iso3"], ["value"], max_gap=2)
        assert result["value"].iloc[1] == pytest.approx(2.0)

    def test_clean_country_year_dataset_wide_years(self):
        from hdi.data.cleaners import clean_country_year_dataset

        df = pd.DataFrame(
            {
                "Country": ["United States", "China"],
                "2000": ["1.0", "2.0"],
                "2001": ["3.0", "4.0"],
                "2002": ["5.0", "6.0"],
            }
        )
        result = clean_country_year_dataset(df)
        assert set(result["iso3"].dropna()) == {"USA", "CHN"}
        assert set(result["year"].astype(int)) == {2000, 2001, 2002}
        assert "value" in result.columns

    def test_metadata_backfill(self):
        from hdi.data.cleaners import add_wb_income, add_who_region

        df = pd.DataFrame({"iso3": ["USA", "CHN"]})
        result = add_wb_income(add_who_region(df))
        assert set(result["who_region"]) == {"AMRO", "WPRO"}
        assert set(result["wb_income"]) == {"HIC", "UMC"}


class TestValidators:
    def test_master_panel_schema_valid(self):
        from hdi.data.validators import validate_master_panel

        df = pd.DataFrame(
            {
                "iso3": ["USA", "CHN", "GBR"],
                "year": [2020, 2020, 2020],
                "life_expectancy": [78.0, 77.0, 81.0],
                "communicable_share": [0.05, 0.08, 0.04],
            }
        )
        validate_master_panel(df)

    def test_master_panel_schema_invalid_iso(self):
        import pandera
        from hdi.data.validators import validate_master_panel

        df = pd.DataFrame({"iso3": ["US", "CHN", "GBR"], "year": [2020, 2020, 2020]})
        with pytest.raises(pandera.errors.SchemaErrors):
            validate_master_panel(df)

    def test_china_panel_schema_valid(self):
        from hdi.data.validators import validate_china_panel

        df = pd.DataFrame(
            {
                "province": ["北京市", "全国"],
                "year": [2024, 2020],
                "indicator": ["各省近20年卫生人员数量", "平均预期寿命(岁)"],
                "value": [40.16, 77.93],
            }
        )
        validate_china_panel(df)


class TestDashboardOptimizationParsing:
    def test_extract_optimization_lab_supports_multi_scenario_payload(self):
        from hdi.analysis.dashboard import _extract_optimization_lab

        parsed = _extract_optimization_lab(
            {
                "data": {
                    "default_scenario": "max_output__budget_1p0",
                    "scenario_options": {"budget_multipliers": [0.9, 1.0, 1.1]},
                    "scenarios": [
                        {
                            "scenario_id": "max_output__budget_1p0",
                            "objective": "max_output",
                            "budget_multiplier": 1.0,
                            "summary": {"predicted_output_gain_pct": 2.3},
                            "allocation": [{"iso3": "USA", "change_pct": -1.0}],
                        }
                    ],
                }
            }
        )

        assert parsed["default_scenario"] == "max_output__budget_1p0"
        assert parsed["scenario_options"]["budget_multipliers"] == [0.9, 1.0, 1.1]
        assert len(parsed["scenarios"]) == 1
        assert parsed["default_allocation"][0]["iso3"] == "USA"

    def test_extract_optimization_lab_falls_back_for_legacy_payload(self):
        from hdi.analysis.dashboard import _extract_optimization_lab

        parsed = _extract_optimization_lab(
            {
                "data": {
                    "objective": "maximize_need_weighted_health_output",
                    "status": "legacy",
                    "allocation": [{"iso3": "CHN", "change_pct": 5.0}],
                }
            }
        )

        assert parsed["default_scenario"] == "legacy_default"
        assert parsed["scenarios"][0]["objective"] == "maximize_need_weighted_health_output"
        assert parsed["default_allocation"][0]["iso3"] == "CHN"
