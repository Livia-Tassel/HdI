"""Schema validation using pandera."""

from __future__ import annotations

import pandera as pa
from pandera import Column, Check, Index


# ── Master panel schema ──────────────────────────────────────────────────────

master_panel_schema = pa.DataFrameSchema(
    columns={
        "iso3": Column(
            str,
            Check.str_length(3, 3),
            nullable=False,
            description="ISO 3166-1 alpha-3 country code",
        ),
        "year": Column(
            int,
            Check.in_range(1990, 2025),
            nullable=False,
            description="Calendar year",
        ),
    },
    # Additional columns are allowed (coerce=False by default)
    strict=False,
    description="Global country-year master panel",
)


# ── China panel schema ───────────────────────────────────────────────────────

china_panel_schema = pa.DataFrameSchema(
    columns={
        "province": Column(
            str,
            nullable=False,
            description="Chinese province name",
        ),
        "year": Column(
            int,
            Check.in_range(2000, 2025),
            nullable=False,
            description="Calendar year",
        ),
    },
    strict=False,
    description="China province-year panel",
)


# ── Health indicators (non-negative) ────────────────────────────────────────

def make_nonneg_check(col_name: str) -> Column:
    """Create a Column schema for non-negative numeric values."""
    return Column(
        float,
        Check.greater_than_or_equal_to(0),
        nullable=True,
        description=f"{col_name} (non-negative)",
    )


# Common health indicator constraints
HEALTH_INDICATOR_SCHEMAS = {
    "life_expectancy": Column(float, Check.in_range(20, 100), nullable=True),
    "daly_rate": make_nonneg_check("daly_rate"),
    "yll_rate": make_nonneg_check("yll_rate"),
    "yld_rate": make_nonneg_check("yld_rate"),
    "mortality_rate": make_nonneg_check("mortality_rate"),
    "gdp_pc": make_nonneg_check("gdp_pc"),
    "health_exp_pct_gdp": Column(float, Check.in_range(0, 30), nullable=True),
    "physicians_per_1000": Column(float, Check.in_range(0, 100), nullable=True),
    "hospital_beds_per_1000": Column(float, Check.in_range(0, 200), nullable=True),
}


def validate_master_panel(df) -> None:
    """Validate the master panel against its schema.

    Raises pandera.errors.SchemaError on failure.
    """
    schema = master_panel_schema
    # Add known health indicator columns if present
    for col_name, col_schema in HEALTH_INDICATOR_SCHEMAS.items():
        if col_name in df.columns:
            schema = schema.add_columns({col_name: col_schema})
    schema.validate(df, lazy=True)


def validate_china_panel(df) -> None:
    """Validate the China panel against its schema."""
    china_panel_schema.validate(df, lazy=True)
