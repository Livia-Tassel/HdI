"""Data cleaning pipelines for each dataset."""

from __future__ import annotations

import logging
import re
from collections.abc import Iterable

import pandas as pd

from hdi.config import INTERP_MAX_GAP, YEAR_MAX, YEAR_MIN

logger = logging.getLogger(__name__)

# ── Country code harmonization ───────────────────────────────────────────────

_ALIAS_MAP: dict[str, str] = {
    "Australia": "AUS",
    "Bolivia (Plurinational State of)": "BOL",
    "Bolivarian Republic of Venezuela": "VEN",
    "Brazil": "BRA",
    "Cabo Verde": "CPV",
    "Canada": "CAN",
    "China": "CHN",
    "Congo": "COG",
    "Côte d'Ivoire": "CIV",
    "Czechia": "CZE",
    "Democratic People's Republic of Korea": "PRK",
    "Democratic Republic of the Congo": "COD",
    "France": "FRA",
    "Germany": "DEU",
    "India": "IND",
    "Japan": "JPN",
    "Mexico": "MEX",
    "Nigeria": "NGA",
    "Eswatini": "SWZ",
    "Hong Kong SAR, China": "HKG",
    "Iran (Islamic Republic of)": "IRN",
    "Korea, Rep.": "KOR",
    "Lao People's Democratic Republic": "LAO",
    "Macao SAR, China": "MAC",
    "Micronesia (Federated States of)": "FSM",
    "Moldova": "MDA",
    "North Macedonia": "MKD",
    "Republic of Korea": "KOR",
    "Republic of Moldova": "MDA",
    "Russian Federation": "RUS",
    "South Korea": "KOR",
    "Syria": "SYR",
    "Taiwan": "TWN",
    "Taiwan, China": "TWN",
    "Tanzania": "TZA",
    "The former Yugoslav Republic of Macedonia": "MKD",
    "Timor-Leste": "TLS",
    "Turkey": "TUR",
    "Türkiye": "TUR",
    "United Kingdom": "GBR",
    "United Kingdom of Great Britain and Northern Ireland": "GBR",
    "United Republic of Tanzania": "TZA",
    "United States": "USA",
    "United States of America": "USA",
    "Venezuela (Bolivarian Republic of)": "VEN",
    "Viet Nam": "VNM",
    "Vietnam": "VNM",
}

_FALLBACK_ALPHA2_TO_ALPHA3 = {
    "AU": "AUS",
    "BR": "BRA",
    "CA": "CAN",
    "CH": "CHE",
    "CN": "CHN",
    "DE": "DEU",
    "ES": "ESP",
    "FR": "FRA",
    "GB": "GBR",
    "HK": "HKG",
    "ID": "IDN",
    "IN": "IND",
    "IT": "ITA",
    "JP": "JPN",
    "KR": "KOR",
    "MX": "MEX",
    "NG": "NGA",
    "RU": "RUS",
    "TR": "TUR",
    "TW": "TWN",
    "US": "USA",
    "VN": "VNM",
    "ZA": "ZAF",
}

_COUNTRY_COLUMN_CANDIDATES = (
    "iso3",
    "iso_code",
    "country_code",
    "economy",
    "country",
    "country_name",
    "location",
    "location_name",
    "entity",
)
_YEAR_COLUMN_CANDIDATES = ("year", "time", "period", "date")
_PROVINCE_COLUMN_CANDIDATES = ("province", "region", "area", "location")
_WHO_REGION_COLUMN_CANDIDATES = ("who_region", "who_region_name", "region")
_WB_INCOME_COLUMN_CANDIDATES = (
    "wb_income",
    "income_group",
    "wb_income_group",
    "world_bank_income_group",
)
_WHO_REGION_ALIASES = {
    "AFRICA": "AFRO",
    "AFRO": "AFRO",
    "AMERICAS": "AMRO",
    "AMRO": "AMRO",
    "EASTERN MEDITERRANEAN": "EMRO",
    "EMRO": "EMRO",
    "EUROPE": "EURO",
    "EURO": "EURO",
    "SOUTH-EAST ASIA": "SEARO",
    "SOUTHEAST ASIA": "SEARO",
    "SEARO": "SEARO",
    "WESTERN PACIFIC": "WPRO",
    "WPRO": "WPRO",
}
_WB_INCOME_ALIASES = {
    "HIGH INCOME": "HIC",
    "HIC": "HIC",
    "LOW INCOME": "LIC",
    "LIC": "LIC",
    "LOWER MIDDLE INCOME": "LMC",
    "LOWER-MIDDLE INCOME": "LMC",
    "LMC": "LMC",
    "UMC": "UMC",
    "UPPER MIDDLE INCOME": "UMC",
    "UPPER-MIDDLE INCOME": "UMC",
}
_YEAR_COL_PATTERN = re.compile(r"^(19|20)\d{2}$")


def _try_import_pycountry():
    try:
        import pycountry  # type: ignore
    except ImportError:
        return None
    return pycountry


def _detect_column(
    columns: Iterable[str],
    candidates: tuple[str, ...],
    contains: tuple[str, ...] = (),
) -> str | None:
    cols = list(columns)
    for candidate in candidates:
        if candidate in cols:
            return candidate
    for col in cols:
        if any(token in col for token in contains):
            return col
    return None


def _extract_year_columns(columns: Iterable[str]) -> list[str]:
    return [col for col in columns if _YEAR_COL_PATTERN.fullmatch(col)]


def _melt_year_columns_if_needed(df: pd.DataFrame) -> pd.DataFrame:
    """Reshape wide year columns to a standard long panel when possible."""
    year_cols = _extract_year_columns(df.columns)
    if "year" in df.columns or len(year_cols) < 3:
        return df

    id_cols = [col for col in df.columns if col not in year_cols]
    value_name = "value" if "value" not in id_cols else "observed_value"
    logger.info(
        "Detected wide year columns; reshaping %d yearly columns into long format.",
        len(year_cols),
    )
    return df.melt(
        id_vars=id_cols,
        value_vars=year_cols,
        var_name="year",
        value_name=value_name,
    )


def _standardize_metadata_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Normalize metadata column names and values when they exist."""
    df = df.copy()

    region_col = _detect_column(df.columns, _WHO_REGION_COLUMN_CANDIDATES, ("region",))
    if region_col and region_col != "who_region" and "who_region" not in df.columns:
        df = df.rename(columns={region_col: "who_region"})

    income_col = _detect_column(df.columns, _WB_INCOME_COLUMN_CANDIDATES, ("income",))
    if income_col and income_col != "wb_income" and "wb_income" not in df.columns:
        df = df.rename(columns={income_col: "wb_income"})

    if "who_region" in df.columns:
        region = df["who_region"].astype("string").str.strip().str.upper()
        df["who_region"] = region.replace(_WHO_REGION_ALIASES)

    if "wb_income" in df.columns:
        income = df["wb_income"].astype("string").str.strip().str.upper()
        df["wb_income"] = income.replace(_WB_INCOME_ALIASES)

    return df


def _coerce_numeric_like_columns(
    df: pd.DataFrame,
    skip_cols: set[str] | None = None,
) -> pd.DataFrame:
    """Convert numeric-looking string columns while leaving categorical fields intact."""
    df = df.copy()
    skip_cols = skip_cols or set()

    for col in df.columns:
        if col in skip_cols or pd.api.types.is_numeric_dtype(df[col]):
            continue

        series = df[col]
        if not (
            pd.api.types.is_object_dtype(series) or pd.api.types.is_string_dtype(series)
        ):
            continue

        cleaned = (
            series.astype("string")
            .str.replace(",", "", regex=False)
            .str.replace("%", "", regex=False)
            .str.replace(r"\s+", "", regex=True)
        )
        non_empty = cleaned.notna() & cleaned.ne("")
        if non_empty.sum() == 0:
            continue

        converted = pd.to_numeric(cleaned.where(non_empty), errors="coerce")
        if converted.notna().sum() >= max(1, int(non_empty.sum() * 0.8)):
            df[col] = converted

    return df


def _clean_country_year_dataset(df: pd.DataFrame) -> pd.DataFrame:
    """Apply common country-year cleaning logic used by multiple datasets."""
    df = normalize_column_names(df)
    df = _melt_year_columns_if_needed(df)
    df = _standardize_metadata_columns(df)

    country_col = _detect_column(
        df.columns,
        _COUNTRY_COLUMN_CANDIDATES,
        ("country", "location", "economy", "entity", "iso"),
    )
    year_col = _detect_column(df.columns, _YEAR_COLUMN_CANDIDATES, ("year", "time", "period"))

    if country_col:
        df = harmonize_country_column(df, col=country_col, target="iso3")

    if year_col and year_col != "year":
        df = df.rename(columns={year_col: "year"})

    df = _coerce_numeric_like_columns(
        df,
        skip_cols={"iso3", "year", "who_region", "wb_income"},
    )

    if "year" in df.columns:
        df["year"] = pd.to_numeric(df["year"], errors="coerce")
        df = filter_year_range(df)
        df["year"] = df["year"].astype("Int64")

    df = df.drop_duplicates().reset_index(drop=True)
    learn_metadata_maps(df)
    return df


def harmonize_country_code(name_or_code: str) -> str | None:
    """Convert a country name or code to ISO 3166-1 alpha-3."""
    s = str(name_or_code).strip()
    if not s or s.lower() in ("nan", "none", ""):
        return None

    if s in _ALIAS_MAP:
        return _ALIAS_MAP[s]

    s_upper = s.upper()
    if len(s) == 2 and s_upper in _FALLBACK_ALPHA2_TO_ALPHA3:
        return _FALLBACK_ALPHA2_TO_ALPHA3[s_upper]

    pycountry = _try_import_pycountry()

    if len(s) == 3 and s.isalpha():
        if pycountry is None:
            return s_upper
        try:
            country = pycountry.countries.get(alpha_3=s_upper)
            if country:
                return s_upper
        except (KeyError, AttributeError):
            pass

    if pycountry is not None:
        try:
            matches = pycountry.countries.search_fuzzy(s)
            if matches:
                return matches[0].alpha_3
        except LookupError:
            pass

        if len(s) == 2 and s.isalpha():
            try:
                country = pycountry.countries.get(alpha_2=s_upper)
                if country:
                    return country.alpha_3
            except (KeyError, AttributeError):
                pass

    logger.warning("Could not resolve country: %s", s)
    return None


def harmonize_country_column(
    df: pd.DataFrame,
    col: str = "country",
    target: str = "iso3",
) -> pd.DataFrame:
    """Add an ISO3 column by harmonizing a country name/code column."""
    if col not in df.columns:
        logger.warning("Country column not found: %s", col)
        return df.copy()

    df = df.copy()
    df[target] = df[col].map(harmonize_country_code)
    n_fail = df[target].isna().sum()
    if n_fail > 0:
        failed = df.loc[df[target].isna(), col].dropna().unique()
        logger.warning(
            "Failed to harmonize %d rows (%d unique values): %s",
            n_fail,
            len(failed),
            failed[:10],
        )
    return df


# ── WHO region / WB income group lookups ─────────────────────────────────────

_WHO_REGION_MAP: dict[str, str] = {}
_WB_INCOME_MAP: dict[str, str] = {}


def learn_metadata_maps(df: pd.DataFrame, iso3_col: str = "iso3") -> None:
    """Capture WHO region and income mappings from any dataset that already has them."""
    if iso3_col not in df.columns:
        return

    if "who_region" in df.columns:
        who_map = (
            df[[iso3_col, "who_region"]]
            .dropna()
            .drop_duplicates(subset=[iso3_col])
            .set_index(iso3_col)["who_region"]
            .to_dict()
        )
        _WHO_REGION_MAP.update(who_map)

    if "wb_income" in df.columns:
        income_map = (
            df[[iso3_col, "wb_income"]]
            .dropna()
            .drop_duplicates(subset=[iso3_col])
            .set_index(iso3_col)["wb_income"]
            .to_dict()
        )
        _WB_INCOME_MAP.update(income_map)


def add_who_region(df: pd.DataFrame, iso3_col: str = "iso3") -> pd.DataFrame:
    """Add or backfill who_region using any learned metadata."""
    df = df.copy()
    existing = (
        df["who_region"]
        if "who_region" in df.columns
        else pd.Series(pd.NA, index=df.index, dtype="object")
    )
    if iso3_col in df.columns:
        mapped = df[iso3_col].map(_WHO_REGION_MAP)
        df["who_region"] = existing.fillna(mapped)
    else:
        df["who_region"] = existing
    return df


def add_wb_income(df: pd.DataFrame, iso3_col: str = "iso3") -> pd.DataFrame:
    """Add or backfill wb_income using any learned metadata."""
    df = df.copy()
    existing = (
        df["wb_income"]
        if "wb_income" in df.columns
        else pd.Series(pd.NA, index=df.index, dtype="object")
    )
    if iso3_col in df.columns:
        mapped = df[iso3_col].map(_WB_INCOME_MAP)
        df["wb_income"] = existing.fillna(mapped)
    else:
        df["wb_income"] = existing
    return df


# ── Generic cleaning utilities ───────────────────────────────────────────────

def normalize_column_names(df: pd.DataFrame) -> pd.DataFrame:
    """Lowercase, strip, and replace spaces/special chars with underscores."""
    df = df.copy()
    df.columns = [
        re.sub(r"[^a-z0-9_]", "_", str(col).strip().lower()).strip("_")
        for col in df.columns
    ]
    df.columns = [re.sub(r"_+", "_", col) for col in df.columns]
    return df


def filter_year_range(
    df: pd.DataFrame,
    year_col: str = "year",
    year_min: int = YEAR_MIN,
    year_max: int = YEAR_MAX,
) -> pd.DataFrame:
    """Keep only rows within the analysis window, ignoring invalid years."""
    if year_col not in df.columns:
        return df.copy()
    year = pd.to_numeric(df[year_col], errors="coerce")
    mask = year.between(year_min, year_max)
    return df.loc[mask.fillna(False)].copy()


def interpolate_gaps(
    df: pd.DataFrame,
    group_cols: list[str],
    value_cols: list[str],
    max_gap: int = INTERP_MAX_GAP,
) -> pd.DataFrame:
    """Linear interpolation within groups for gaps <= max_gap years."""
    df = df.copy()
    sort_cols = [col for col in [*group_cols, "year"] if col in df.columns]
    if sort_cols:
        df = df.sort_values(sort_cols)

    for col in value_cols:
        if col in df.columns:
            df[col] = df.groupby(group_cols)[col].transform(
                lambda series: series.interpolate(method="linear", limit=max_gap)
            )
    return df


def drop_high_missing(df: pd.DataFrame, threshold: float = 0.30) -> pd.DataFrame:
    """Drop columns where missing fraction exceeds threshold."""
    frac_missing = df.isna().mean()
    to_drop = frac_missing[frac_missing > threshold].index.tolist()
    if to_drop:
        logger.info(
            "Dropping %d columns with >%.0f%% missing: %s",
            len(to_drop),
            threshold * 100,
            to_drop[:10],
        )
    return df.drop(columns=to_drop)


# ── Dataset-specific cleaners ────────────────────────────────────────────────

def clean_country_year_dataset(df: pd.DataFrame) -> pd.DataFrame:
    """Public wrapper for generic country-year datasets."""
    return _clean_country_year_dataset(df)


def clean_disease_mortality(df: pd.DataFrame) -> pd.DataFrame:
    """Clean Dataset 1: Global disease and mortality."""
    return _clean_country_year_dataset(df)


def clean_risk_factors(df: pd.DataFrame) -> pd.DataFrame:
    """Clean Dataset 2: Risk factor exposure."""
    return _clean_country_year_dataset(df)


def clean_nutrition_population(df: pd.DataFrame) -> pd.DataFrame:
    """Clean Dataset 3: Nutrition and population."""
    return _clean_country_year_dataset(df)


def clean_socioeconomic(df: pd.DataFrame) -> pd.DataFrame:
    """Clean Dataset 4: Socioeconomic indicators."""
    return _clean_country_year_dataset(df)


def clean_china_health(df: pd.DataFrame) -> pd.DataFrame:
    """Clean Dataset 5: China provincial health data."""
    df = normalize_column_names(df)
    df = _melt_year_columns_if_needed(df)

    province_col = _detect_column(
        df.columns,
        _PROVINCE_COLUMN_CANDIDATES,
        ("province", "region", "area"),
    )
    year_col = _detect_column(df.columns, _YEAR_COLUMN_CANDIDATES, ("year", "time"))

    if province_col and province_col != "province":
        df = df.rename(columns={province_col: "province"})
    if "province" in df.columns:
        df["province"] = df["province"].astype("string").str.strip()

    if year_col and year_col != "year":
        df = df.rename(columns={year_col: "year"})

    df = _standardize_metadata_columns(df)

    df = _coerce_numeric_like_columns(
        df,
        skip_cols={"province", "year", "who_region", "wb_income"},
    )

    if "year" in df.columns:
        df["year"] = pd.to_numeric(df["year"], errors="coerce")
        df = filter_year_range(df)
        df["year"] = df["year"].astype("Int64")

    return df.drop_duplicates().reset_index(drop=True)
