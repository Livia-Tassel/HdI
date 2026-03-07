"""Schema validation for processed panels."""

from __future__ import annotations

import pandera as pa
from pandera import Check, Column


master_panel_schema = pa.DataFrameSchema(
    columns={
        "iso3": Column(
            str,
            Check(
                lambda series: series.astype("string").str.fullmatch(r"[A-Z]{3}"),
                "ISO alpha-3 country code",
            ),
            nullable=False,
            description="ISO 3166-1 alpha-3 country code",
        ),
        "year": Column(
            int,
            Check.in_range(2000, 2023),
            nullable=False,
            description="Calendar year",
        ),
    },
    strict=False,
    description="Global country-year master panel",
)


china_panel_schema = pa.DataFrameSchema(
    columns={
        "province": Column(str, nullable=False, description="Chinese province or national scope"),
        "year": Column(int, Check.in_range(2005, 2024), nullable=False),
        "indicator": Column(str, nullable=False),
        "value": Column(float, nullable=True),
    },
    strict=False,
    description="China province-year long panel",
)


def _non_negative(nullable: bool = True) -> Column:
    return Column(float, Check.greater_than_or_equal_to(0), nullable=nullable)


HEALTH_INDICATOR_SCHEMAS = {
    "total_deaths": _non_negative(),
    "communicable_deaths": _non_negative(),
    "ncd_deaths": _non_negative(),
    "injury_deaths": _non_negative(),
    "communicable_share": Column(float, Check.in_range(0, 1), nullable=True),
    "ncd_share": Column(float, Check.in_range(0, 1), nullable=True),
    "injury_share": Column(float, Check.in_range(0, 1), nullable=True),
    "life_expectancy": Column(float, Check.in_range(20, 100), nullable=True),
    "infant_mortality": _non_negative(),
    "under5_mortality": _non_negative(),
    "adult_mortality_male": _non_negative(),
    "adult_mortality_female": _non_negative(),
    "physicians_per_1000": _non_negative(),
    "beds_per_1000": _non_negative(),
    "nurses_per_1000": _non_negative(),
    "health_exp_pct_gdp": _non_negative(),
    "health_exp_per_capita": _non_negative(),
    "gdp_per_capita": _non_negative(),
    "urban_population_pct": Column(float, Check.in_range(0, 100), nullable=True),
    "basic_water_pct": Column(float, Check.in_range(0, 100), nullable=True),
    "basic_sanitation_pct": Column(float, Check.in_range(0, 100), nullable=True),
    "measles_immunization_pct": Column(float, Check.in_range(0, 100), nullable=True),
    "fertility_rate": _non_negative(),
}


def validate_master_panel(df) -> None:
    schema = master_panel_schema
    for name, col_schema in HEALTH_INDICATOR_SCHEMAS.items():
        if name in df.columns:
            schema = schema.add_columns({name: col_schema})
    schema.validate(df, lazy=True)


def validate_china_panel(df) -> None:
    china_panel_schema.validate(df, lazy=True)
