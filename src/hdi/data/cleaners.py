"""Dataset-specific cleaning and harmonization utilities."""

from __future__ import annotations

import logging
import re
from functools import lru_cache
from itertools import chain
from pathlib import Path

import pandas as pd
from babel import Locale

from hdi.config import (
    CAUSE_GROUP_MAP,
    CHINA_YEAR_MAX,
    CHINA_YEAR_MIN,
    DS_SOCIOECONOMIC,
    INDICATOR_SPECS,
    RISK_LABEL_MAP,
    WDI_TO_INCOME_CODE,
    WDI_TO_WHO_REGION,
    YEAR_MAX,
    YEAR_MIN,
)

logger = logging.getLogger(__name__)

_YEAR_PATTERN = re.compile(r"^(?P<year>(19|20)\d{2})(年)?$")
_ASCII_ALPHA2 = re.compile(r"^[A-Z]{2}$")
_ASCII_ALPHA3 = re.compile(r"^[A-Z]{3}$")

_WHO_REGION_MAP: dict[str, str] = {}
_WB_INCOME_MAP: dict[str, str] = {}
_COUNTRY_NAME_MAP: dict[str, str] = {}

_MANUAL_COUNTRY_ALIASES: dict[str, str] = {
    "东帝汶民主共和国": "TLS",
    "伊朗伊斯兰共和国": "IRN",
    "伯利兹城": "BLZ",
    "刚果": "COG",
    "刚果民主共和国": "COD",
    "卢森堡公国": "LUX",
    "厄立特里亚国": "ERI",
    "圣卢西亚岛": "LCA",
    "圣基茨和尼维斯联邦": "KNA",
    "圣多美和普林西比民主共和国": "STP",
    "圣马力诺共和国": "SMR",
    "坦桑尼亚联合共和国": "TZA",
    "多米尼加岛": "DMA",
    "大韩民国": "KOR",
    "委内瑞拉玻利瓦尔共和国": "VEN",
    "安道尔共和国": "AND",
    "密克罗尼西亚联邦": "FSM",
    "巴勒斯坦": "PSE",
    "巴林岛": "BHR",
    "帕劳共和国": "PLW",
    "托克劳群岛": "TKL",
    "捷克共和国": "CZE",
    "摩尔多瓦共和国": "MDA",
    "摩纳哥公国": "MCO",
    "文莱达鲁萨兰国": "BRN",
    "朝鲜民主主义人民共和国": "PRK",
    "特立尼达拉岛和多巴哥": "TTO",
    "玻利维亚国": "BOL",
    "瑙鲁共和国": "NRU",
    "科特廸亚": "CIV",
    "美利坚合众国": "USA",
    "美属萨摩亚群岛": "ASM",
    "老挝人民民主共和国": "LAO",
    "阿拉伯叙利亚共和国": "SYR",
    "马尔他": "MLT",
    "黑山共和国": "MNE",
    "中国香港特别行政区": "HKG",
    "中国澳门特别行政区": "MAC",
    "中国台湾": "TWN",
    "台湾": "TWN",
    "库克群岛": "COK",
    "纽埃": "NIU",
    "纳米比亚": "NAM",
}

_ENGLISH_COUNTRY_ALIASES: dict[str, str] = {
    "Bolivia (Plurinational State of)": "BOL",
    "Bolivarian Republic of Venezuela": "VEN",
    "Cabo Verde": "CPV",
    "Czechia": "CZE",
    "Democratic People's Republic of Korea": "PRK",
    "Democratic Republic of the Congo": "COD",
    "Eswatini": "SWZ",
    "Hong Kong SAR, China": "HKG",
    "Iran (Islamic Republic of)": "IRN",
    "Korea, Rep.": "KOR",
    "Lao People's Democratic Republic": "LAO",
    "Macao SAR, China": "MAC",
    "Micronesia (Federated States of)": "FSM",
    "North Macedonia": "MKD",
    "Russian Federation": "RUS",
    "Slovak Republic": "SVK",
    "South Korea": "KOR",
    "Syrian Arab Republic": "SYR",
    "Tanzania": "TZA",
    "Timor-Leste": "TLS",
    "Türkiye": "TUR",
    "Turkey": "TUR",
    "United Kingdom": "GBR",
    "United States": "USA",
    "United States of America": "USA",
    "Venezuela (Bolivarian Republic of)": "VEN",
    "Viet Nam": "VNM",
}

_SELECTED_INDICATOR_CODES = set(
    chain.from_iterable(spec["candidates"] for spec in INDICATOR_SPECS.values())
)
_MISSED_COUNTRY_LOGS: set[str] = set()


def _year_token(value: object) -> str | None:
    match = _YEAR_PATTERN.fullmatch(str(value).strip())
    return match.group("year") if match else None


def normalize_column_names(df: pd.DataFrame) -> pd.DataFrame:
    """Normalize column names while preserving Chinese characters."""
    normalized = []
    for col in df.columns:
        text = str(col).strip().lower()
        text = (
            text.replace("%", " pct ")
            .replace("(", " ")
            .replace(")", " ")
            .replace("/", " ")
            .replace("-", " ")
        )
        text = re.sub(r"[^\w]+", "_", text, flags=re.UNICODE)
        text = re.sub(r"_+", "_", text).strip("_")
        normalized.append(text)

    out = df.copy()
    out.columns = normalized
    return out


def _ensure_metadata_maps() -> None:
    if _COUNTRY_NAME_MAP and _WHO_REGION_MAP and _WB_INCOME_MAP:
        return

    meta = get_country_metadata()
    if meta.empty:
        return

    _COUNTRY_NAME_MAP.update(
        meta.drop_duplicates(subset=["iso3"]).set_index("iso3")["country_name"].dropna().to_dict()
    )
    _WHO_REGION_MAP.update(
        meta.drop_duplicates(subset=["iso3"]).set_index("iso3")["who_region"].dropna().to_dict()
    )
    _WB_INCOME_MAP.update(
        meta.drop_duplicates(subset=["iso3"]).set_index("iso3")["wb_income"].dropna().to_dict()
    )


@lru_cache(maxsize=1)
def get_country_metadata() -> pd.DataFrame:
    """Load country metadata from World Bank country definitions."""
    path = DS_SOCIOECONOMIC / "WDI_CSV" / "WDICountry.csv"
    if not path.exists():
        logger.warning("Country metadata file not found: %s", path)
        return pd.DataFrame(
            columns=[
                "iso3",
                "alpha2",
                "country_name",
                "table_name",
                "long_name",
                "region_name",
                "income_name",
                "who_region",
                "wb_income",
            ]
        )

    meta = pd.read_csv(path, dtype=str).rename(
        columns={
            "Country Code": "iso3",
            "2-alpha code": "alpha2",
            "Short Name": "country_name",
            "Table Name": "table_name",
            "Long Name": "long_name",
            "Region": "region_name",
            "Income Group": "income_name",
        }
    )
    meta = meta[["iso3", "alpha2", "country_name", "table_name", "long_name", "region_name", "income_name"]]
    meta = meta[meta["iso3"].astype(str).str.fullmatch(r"[A-Z]{3}", na=False)].copy()
    meta["alpha2"] = meta["alpha2"].fillna("").str.upper()
    meta["who_region"] = meta["region_name"].map(WDI_TO_WHO_REGION)
    meta["wb_income"] = meta["income_name"].map(WDI_TO_INCOME_CODE)
    return meta


@lru_cache(maxsize=1)
def _country_name_lookup() -> dict[str, str]:
    """Build a country-name-to-ISO3 lookup using WDI metadata and Babel."""
    meta = get_country_metadata()
    lookup: dict[str, str] = {}

    for _, row in meta.iterrows():
        iso3 = row["iso3"]
        for name in (row["country_name"], row["table_name"], row["long_name"]):
            if pd.notna(name):
                lookup[str(name).strip()] = iso3
                lookup[str(name).strip().lower()] = iso3

        alpha2 = row["alpha2"]
        if isinstance(alpha2, str) and _ASCII_ALPHA2.fullmatch(alpha2):
            lookup[alpha2] = iso3

    locale = Locale.parse("zh_Hans")
    alpha2_to_iso3 = {
        str(row.alpha2): str(row.iso3)
        for row in meta.itertuples(index=False)
        if isinstance(row.alpha2, str) and _ASCII_ALPHA2.fullmatch(row.alpha2)
    }
    for alpha2, zh_name in locale.territories.items():
        if isinstance(alpha2, str) and _ASCII_ALPHA2.fullmatch(alpha2):
            iso3 = alpha2_to_iso3.get(alpha2)
            if iso3 and zh_name:
                lookup[str(zh_name).strip()] = iso3

    lookup.update(_MANUAL_COUNTRY_ALIASES)
    lookup.update({key.lower(): value for key, value in _ENGLISH_COUNTRY_ALIASES.items()})
    lookup.update(_ENGLISH_COUNTRY_ALIASES)
    return lookup


def learn_metadata_maps(df: pd.DataFrame, iso3_col: str = "iso3") -> None:
    """Store country name, WHO region, and income maps for later backfill."""
    _ensure_metadata_maps()

    if iso3_col not in df.columns:
        return

    if "country_name" in df.columns:
        name_map = (
            df[[iso3_col, "country_name"]]
            .dropna()
            .drop_duplicates(subset=[iso3_col])
            .set_index(iso3_col)["country_name"]
            .to_dict()
        )
        _COUNTRY_NAME_MAP.update(name_map)

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
    _ensure_metadata_maps()
    out = df.copy()
    if iso3_col in out.columns:
        mapped = out[iso3_col].map(_WHO_REGION_MAP)
        if "who_region" in out.columns:
            out["who_region"] = out["who_region"].fillna(mapped)
        else:
            out["who_region"] = mapped
    return out


def add_wb_income(df: pd.DataFrame, iso3_col: str = "iso3") -> pd.DataFrame:
    _ensure_metadata_maps()
    out = df.copy()
    if iso3_col in out.columns:
        mapped = out[iso3_col].map(_WB_INCOME_MAP)
        if "wb_income" in out.columns:
            out["wb_income"] = out["wb_income"].fillna(mapped)
        else:
            out["wb_income"] = mapped
    return out


def add_country_name(df: pd.DataFrame, iso3_col: str = "iso3") -> pd.DataFrame:
    _ensure_metadata_maps()
    out = df.copy()
    if iso3_col in out.columns:
        mapped = out[iso3_col].map(_COUNTRY_NAME_MAP)
        if "country_name" in out.columns:
            out["country_name"] = out["country_name"].fillna(mapped)
        else:
            out["country_name"] = mapped
    return out


@lru_cache(maxsize=4096)
def harmonize_country_code(name_or_code: object) -> str | None:
    """Convert a country name or code into ISO alpha-3 using local metadata."""
    if name_or_code is None:
        return None

    text = str(name_or_code).strip()
    if not text or text.lower() in {"nan", "none", "null"}:
        return None

    lookup = _country_name_lookup()

    upper = text.upper()
    if _ASCII_ALPHA3.fullmatch(upper):
        meta = get_country_metadata()
        if meta["iso3"].eq(upper).any():
            return upper

    if _ASCII_ALPHA2.fullmatch(upper):
        iso3 = lookup.get(upper)
        if iso3:
            return iso3

    direct = lookup.get(text) or lookup.get(text.lower())
    if direct:
        return direct

    if text not in _MISSED_COUNTRY_LOGS:
        logger.warning("Could not resolve country: %s", text)
        _MISSED_COUNTRY_LOGS.add(text)
    return None


def harmonize_country_column(
    df: pd.DataFrame,
    col: str = "country",
    target: str = "iso3",
) -> pd.DataFrame:
    """Add an ISO3 column by harmonizing an existing country/name/code column."""
    out = df.copy()
    if col not in out.columns:
        return out
    out[target] = out[col].map(harmonize_country_code)
    return out


def filter_year_range(
    df: pd.DataFrame,
    year_col: str = "year",
    year_min: int = YEAR_MIN,
    year_max: int = YEAR_MAX,
) -> pd.DataFrame:
    """Keep only rows inside a year window."""
    if year_col not in df.columns:
        return df.copy()
    years = pd.to_numeric(df[year_col], errors="coerce")
    return df.loc[years.between(year_min, year_max, inclusive="both").fillna(False)].copy()


def interpolate_gaps(
    df: pd.DataFrame,
    group_cols: list[str],
    value_cols: list[str],
    max_gap: int = 2,
) -> pd.DataFrame:
    """Linearly interpolate short numeric gaps within panels."""
    out = df.copy()
    sort_cols = [col for col in [*group_cols, "year"] if col in out.columns]
    if sort_cols:
        out = out.sort_values(sort_cols)
    for col in value_cols:
        if col in out.columns:
            out[col] = out.groupby(group_cols)[col].transform(
                lambda s: s.interpolate(method="linear", limit=max_gap, limit_direction="both")
            )
    return out


def drop_high_missing(df: pd.DataFrame, threshold: float = 0.30) -> pd.DataFrame:
    """Drop columns with missingness above a threshold."""
    missing_frac = df.isna().mean()
    to_drop = missing_frac[missing_frac > threshold].index.tolist()
    return df.drop(columns=to_drop)


def _extract_year_columns(columns: list[str]) -> dict[str, str]:
    return {col: _year_token(col) for col in columns if _year_token(col)}


def _melt_year_columns_if_needed(
    df: pd.DataFrame,
    id_vars: list[str] | None = None,
    value_name: str = "value",
) -> pd.DataFrame:
    year_cols = _extract_year_columns(list(df.columns))
    if not year_cols or "year" in df.columns:
        return df

    id_columns = id_vars or [col for col in df.columns if col not in year_cols]
    melted = df.melt(
        id_vars=id_columns,
        value_vars=list(year_cols.keys()),
        var_name="year",
        value_name=value_name,
    )
    melted["year"] = melted["year"].map(year_cols)
    return melted


def _coerce_numeric(df: pd.DataFrame, skip: set[str] | None = None) -> pd.DataFrame:
    out = df.copy()
    skip = skip or set()
    for col in out.columns:
        if col in skip or pd.api.types.is_numeric_dtype(out[col]):
            continue
        if not (pd.api.types.is_object_dtype(out[col]) or pd.api.types.is_string_dtype(out[col])):
            continue
        cleaned = (
            out[col]
            .astype("string")
            .str.replace(",", "", regex=False)
            .str.replace("%", "", regex=False)
            .str.strip()
        )
        converted = pd.to_numeric(cleaned, errors="coerce")
        if converted.notna().sum() >= max(1, int(cleaned.notna().sum() * 0.75)):
            out[col] = converted
    return out


def clean_country_year_dataset(df: pd.DataFrame) -> pd.DataFrame:
    """Generic cleaner used by tests and simple panel inputs."""
    out = normalize_column_names(df)
    out = _melt_year_columns_if_needed(out)

    country_col = next(
        (col for col in ("country", "country_name", "location", "地理位置") if col in out.columns),
        None,
    )
    if country_col:
        out = harmonize_country_column(out, country_col, "iso3")

    if "year" in out.columns:
        out["year"] = pd.to_numeric(out["year"], errors="coerce")
        out = filter_year_range(out)
        out["year"] = out["year"].astype("Int64")

    out = _coerce_numeric(out, skip={"iso3", "year"})
    out = add_country_name(add_wb_income(add_who_region(out)))
    out = out.drop_duplicates().reset_index(drop=True)
    learn_metadata_maps(out)
    return out


def _apply_country_metadata(df: pd.DataFrame) -> pd.DataFrame:
    out = add_country_name(add_wb_income(add_who_region(df)))
    learn_metadata_maps(out)
    return out


def _rename_columns(df: pd.DataFrame, mapping: dict[str, str]) -> pd.DataFrame:
    return df.rename(columns={key: value for key, value in mapping.items() if key in df.columns})


def clean_disease_mortality(df: pd.DataFrame) -> pd.DataFrame:
    """Clean dataset 1 into a country-year-cause table."""
    out = _rename_columns(
        df.copy(),
        {
            "Population": "population_scope",
            "地理位置": "country_zh",
            "年份": "year",
            "年龄": "age_label",
            "性别": "sex_label",
            "死亡或受伤原因": "cause_name",
            "测量": "measure_name",
            "数值": "value",
            "下限": "lower",
            "上限": "upper",
            "_source_file": "source_file",
        },
    )
    out["iso3"] = out["country_zh"].map(harmonize_country_code)
    out["year"] = pd.to_numeric(out["year"], errors="coerce")
    out = filter_year_range(out)
    out = _coerce_numeric(out, skip={"country_zh", "iso3", "cause_name", "measure_name", "source_file", "population_scope", "age_label", "sex_label"})
    out["year"] = out["year"].astype("Int64")
    out["measure"] = out["measure_name"].map({"死亡": "deaths", "死亡排名": "death_rank"}).fillna(out["measure_name"])
    out["cause_group"] = out["cause_name"].map(CAUSE_GROUP_MAP).fillna("其他")
    out = out[out["iso3"].notna()].copy()
    out = _apply_country_metadata(out)
    keep_cols = [
        "iso3",
        "country_name",
        "country_zh",
        "year",
        "cause_name",
        "cause_group",
        "measure",
        "value",
        "lower",
        "upper",
        "population_scope",
        "age_label",
        "sex_label",
        "who_region",
        "wb_income",
        "source_file",
    ]
    return out[keep_cols].drop_duplicates().reset_index(drop=True)


def clean_risk_factors(df: pd.DataFrame) -> pd.DataFrame:
    """Clean dataset 2 into a country-year-risk table."""
    out = _rename_columns(
        df.copy(),
        {
            "Population": "population_scope",
            "地理位置": "country_zh",
            "年份": "year",
            "年龄": "age_label",
            "性别": "sex_label",
            "死亡或受伤原因": "cause_name",
            "风险因素": "risk_factor",
            "测量": "measure_name",
            "数值": "value",
            "下限": "lower",
            "上限": "upper",
            "_source_file": "source_file",
        },
    )
    out["iso3"] = out["country_zh"].map(harmonize_country_code)
    out["year"] = pd.to_numeric(out["year"], errors="coerce")
    out = filter_year_range(out)
    out = _coerce_numeric(out, skip={"country_zh", "iso3", "cause_name", "risk_factor", "measure_name", "source_file", "population_scope", "age_label", "sex_label"})
    out["year"] = out["year"].astype("Int64")
    out["measure"] = out["measure_name"].map({"死亡": "deaths", "死亡排名": "death_rank"}).fillna(out["measure_name"])
    out["risk_code"] = out["risk_factor"].map(RISK_LABEL_MAP).fillna("other_risk")
    out = out[out["iso3"].notna()].copy()
    out = _apply_country_metadata(out)
    keep_cols = [
        "iso3",
        "country_name",
        "country_zh",
        "year",
        "cause_name",
        "risk_factor",
        "risk_code",
        "measure",
        "value",
        "lower",
        "upper",
        "population_scope",
        "age_label",
        "sex_label",
        "who_region",
        "wb_income",
        "source_file",
    ]
    return out[keep_cols].drop_duplicates().reset_index(drop=True)


def clean_nutrition_population(df: pd.DataFrame) -> pd.DataFrame:
    """Clean dataset 3 into a filtered long indicator table."""
    out = _rename_columns(
        df.copy(),
        {
            "REF_AREA": "iso3",
            "REF_AREA_LABEL": "country_name",
            "INDICATOR": "indicator_code",
            "INDICATOR_LABEL": "indicator_name",
            "TIME_PERIOD": "year",
            "OBS_VALUE": "value",
            "SEX": "sex_code",
            "SEX_LABEL": "sex_label",
            "AGE": "age_code",
            "AGE_LABEL": "age_label",
            "_source_file": "source_file",
        },
    )
    out["iso3"] = out["iso3"].astype("string").str.upper()
    out = out[out["indicator_code"].isin(_SELECTED_INDICATOR_CODES)].copy()
    out = out[out["sex_code"].fillna("_T").eq("_T") & out["age_code"].fillna("_T").eq("_T")].copy()
    out["year"] = pd.to_numeric(out["year"], errors="coerce")
    out = filter_year_range(out)
    out["year"] = out["year"].astype("Int64")
    out["value"] = pd.to_numeric(out["value"], errors="coerce")

    valid_iso3 = set(get_country_metadata()["iso3"])
    out = out[out["iso3"].isin(valid_iso3)].copy()
    out = _apply_country_metadata(out)
    keep_cols = [
        "iso3",
        "country_name",
        "year",
        "indicator_code",
        "indicator_name",
        "value",
        "who_region",
        "wb_income",
        "source_file",
    ]
    return out[keep_cols].drop_duplicates().reset_index(drop=True)


def clean_socioeconomic(df: pd.DataFrame) -> pd.DataFrame:
    """Clean dataset 4 (WDI) into a filtered long indicator table."""
    out = _rename_columns(
        df.copy(),
        {
            "Country Name": "country_name",
            "Country Code": "iso3",
            "Indicator Name": "indicator_name",
            "Indicator Code": "indicator_code",
            "_source_file": "source_file",
        },
    )
    year_columns = [col for col in out.columns if _year_token(col)]
    id_columns = [col for col in ("country_name", "iso3", "indicator_name", "indicator_code", "source_file") if col in out.columns]
    out = out[out["indicator_code"].isin(_SELECTED_INDICATOR_CODES)].copy()
    out = out.melt(id_vars=id_columns, value_vars=year_columns, var_name="year", value_name="value")
    out["year"] = out["year"].map({col: int(_year_token(col)) for col in year_columns})
    out["value"] = pd.to_numeric(out["value"], errors="coerce")
    out = filter_year_range(out)
    out["year"] = out["year"].astype("Int64")

    meta = get_country_metadata()[["iso3", "country_name", "who_region", "wb_income", "region_name", "income_name"]]
    out = out.merge(meta, on="iso3", how="left", suffixes=("", "_meta"))
    out["country_name"] = out["country_name_meta"].fillna(out["country_name"])
    out = out.drop(columns=["country_name_meta"])
    out = out[out["who_region"].notna()].copy()
    learn_metadata_maps(out)
    keep_cols = [
        "iso3",
        "country_name",
        "year",
        "indicator_code",
        "indicator_name",
        "value",
        "who_region",
        "wb_income",
        "source_file",
    ]
    return out[keep_cols].drop_duplicates().reset_index(drop=True)


def clean_china_health(df: pd.DataFrame) -> pd.DataFrame:
    """Clean dataset 5 into a province/year/indicator long table."""
    frames: list[pd.DataFrame] = []
    for source_file, subset in df.groupby("_source_file", dropna=False):
        frame = subset.copy()
        frame.columns = [str(col).strip() for col in frame.columns]
        source_name = Path(str(source_file)).stem if pd.notna(source_file) else "unknown"
        year_cols = [col for col in frame.columns if _year_token(col)]
        if not year_cols:
            continue

        if "地区" in frame.columns and frame["地区"].notna().any():
            melted = frame.melt(id_vars=["地区"], value_vars=year_cols, var_name="year", value_name="value")
            melted = melted.rename(columns={"地区": "province"})
            melted["indicator"] = source_name
        elif "指标" in frame.columns and frame["指标"].notna().any():
            melted = frame.melt(id_vars=["指标"], value_vars=year_cols, var_name="year", value_name="value")
            melted = melted.rename(columns={"指标": "indicator"})
            melted["province"] = "全国"
        else:
            continue

        melted["year"] = melted["year"].map(_year_token).astype("Int64")
        melted["value"] = pd.to_numeric(melted["value"], errors="coerce")
        melted["source_file"] = source_file
        frames.append(melted[["province", "year", "indicator", "value", "source_file"]])

    if not frames:
        return pd.DataFrame(columns=["province", "year", "indicator", "value", "source_file"])

    out = pd.concat(frames, ignore_index=True)
    out["province"] = out["province"].astype("string").str.strip()
    out["indicator"] = out["indicator"].astype("string").str.strip()
    out = filter_year_range(out, year_col="year", year_min=CHINA_YEAR_MIN, year_max=CHINA_YEAR_MAX)
    return out.drop_duplicates().reset_index(drop=True)
