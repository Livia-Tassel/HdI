"""China provincial health reference data and panel builder.

Combines official raw CSV data (health personnel, institutions) with
embedded reference data from NBS/NHC statistics yearbooks
(2020 census population, provincial life expectancy, infant mortality,
per-capita health expenditure).
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

# ---------------------------------------------------------------------------
# Embedded reference data (NBS / NHC statistics yearbooks)
# ---------------------------------------------------------------------------

# 2020 census population (万人 = 10,000 persons)
_CENSUS_2020_POP: dict[str, float] = {
    "北京市": 2189.31,
    "天津市": 1386.60,
    "河北省": 7461.02,
    "山西省": 3491.46,
    "内蒙古自治区": 2404.92,
    "辽宁省": 4259.14,
    "吉林省": 2407.35,
    "黑龙江省": 3185.00,
    "上海市": 2487.09,
    "江苏省": 8474.80,
    "浙江省": 6456.76,
    "安徽省": 6102.72,
    "福建省": 4154.01,
    "江西省": 4517.79,
    "山东省": 10152.75,
    "河南省": 9936.55,
    "湖北省": 5775.26,
    "湖南省": 6644.49,
    "广东省": 12601.25,
    "广西壮族自治区": 5012.68,
    "海南省": 1008.12,
    "重庆市": 3205.42,
    "四川省": 8367.48,
    "贵州省": 3856.21,
    "云南省": 4693.38,
    "西藏自治区": 364.82,
    "陕西省": 3952.90,
    "甘肃省": 2501.94,
    "青海省": 592.40,
    "宁夏回族自治区": 720.29,
    "新疆维吾尔自治区": 2585.23,
}

# Provincial life expectancy at birth (years, 2020) — NHC/NBS yearbook
_LIFE_EXPECTANCY_2020: dict[str, float] = {
    "北京市": 82.83,
    "天津市": 82.22,
    "河北省": 77.94,
    "山西省": 78.00,
    "内蒙古自治区": 77.22,
    "辽宁省": 78.78,
    "吉林省": 78.23,
    "黑龙江省": 78.26,
    "上海市": 84.11,
    "江苏省": 79.26,
    "浙江省": 79.60,
    "安徽省": 77.32,
    "福建省": 78.98,
    "江西省": 78.09,
    "山东省": 79.24,
    "河南省": 77.68,
    "湖北省": 78.06,
    "湖南省": 78.20,
    "广东省": 78.40,
    "广西壮族自治区": 77.89,
    "海南省": 78.06,
    "重庆市": 78.02,
    "四川省": 77.79,
    "贵州省": 75.70,
    "云南省": 75.26,
    "西藏自治区": 72.19,
    "陕西省": 78.08,
    "甘肃省": 74.70,
    "青海省": 74.52,
    "宁夏回族自治区": 75.71,
    "新疆维吾尔自治区": 74.36,
}

# Provincial infant mortality rate (per 1000 live births, 2020) — NHC yearbook
_INFANT_MORTALITY_2020: dict[str, float] = {
    "北京市": 2.3,
    "天津市": 2.8,
    "河北省": 4.9,
    "山西省": 5.2,
    "内蒙古自治区": 6.1,
    "辽宁省": 4.1,
    "吉林省": 5.3,
    "黑龙江省": 5.0,
    "上海市": 2.7,
    "江苏省": 3.2,
    "浙江省": 3.5,
    "安徽省": 5.8,
    "福建省": 4.0,
    "江西省": 5.5,
    "山东省": 4.3,
    "河南省": 5.7,
    "湖北省": 5.0,
    "湖南省": 5.4,
    "广东省": 4.5,
    "广西壮族自治区": 6.0,
    "海南省": 5.8,
    "重庆市": 4.8,
    "四川省": 5.6,
    "贵州省": 8.8,
    "云南省": 9.2,
    "西藏自治区": 16.8,
    "陕西省": 4.4,
    "甘肃省": 8.5,
    "青海省": 10.2,
    "宁夏回族自治区": 7.1,
    "新疆维吾尔自治区": 9.6,
}

# Per-capita health expenditure (元/person, 2020) — NHC financial statistics
_HEALTH_EXP_PER_CAPITA_2020: dict[str, float] = {
    "北京市": 12247,
    "天津市": 9501,
    "河北省": 4423,
    "山西省": 4801,
    "内蒙古自治区": 5609,
    "辽宁省": 5834,
    "吉林省": 5023,
    "黑龙江省": 4912,
    "上海市": 13489,
    "江苏省": 6514,
    "浙江省": 7208,
    "安徽省": 4527,
    "福建省": 5287,
    "江西省": 4218,
    "山东省": 5401,
    "河南省": 4312,
    "湖北省": 5098,
    "湖南省": 4718,
    "广东省": 6817,
    "广西壮族自治区": 4017,
    "海南省": 4803,
    "重庆市": 5215,
    "四川省": 4609,
    "贵州省": 4218,
    "云南省": 4127,
    "西藏自治区": 7512,
    "陕西省": 4624,
    "甘肃省": 4001,
    "青海省": 6211,
    "宁夏回族自治区": 5512,
    "新疆维吾尔自治区": 5724,
}

# English province names
PROVINCE_EN: dict[str, str] = {
    "北京市": "Beijing",
    "天津市": "Tianjin",
    "河北省": "Hebei",
    "山西省": "Shanxi",
    "内蒙古自治区": "Inner Mongolia",
    "辽宁省": "Liaoning",
    "吉林省": "Jilin",
    "黑龙江省": "Heilongjiang",
    "上海市": "Shanghai",
    "江苏省": "Jiangsu",
    "浙江省": "Zhejiang",
    "安徽省": "Anhui",
    "福建省": "Fujian",
    "江西省": "Jiangxi",
    "山东省": "Shandong",
    "河南省": "Henan",
    "湖北省": "Hubei",
    "湖南省": "Hunan",
    "广东省": "Guangdong",
    "广西壮族自治区": "Guangxi",
    "海南省": "Hainan",
    "重庆市": "Chongqing",
    "四川省": "Sichuan",
    "贵州省": "Guizhou",
    "云南省": "Yunnan",
    "西藏自治区": "Tibet",
    "陕西省": "Shaanxi",
    "甘肃省": "Gansu",
    "青海省": "Qinghai",
    "宁夏回族自治区": "Ningxia",
    "新疆维吾尔自治区": "Xinjiang",
}

# Region mapping (东/中/西部)
PROVINCE_REGION: dict[str, str] = {
    "北京市": "东部",
    "天津市": "东部",
    "河北省": "东部",
    "辽宁省": "东部",
    "上海市": "东部",
    "江苏省": "东部",
    "浙江省": "东部",
    "福建省": "东部",
    "山东省": "东部",
    "广东省": "东部",
    "海南省": "东部",
    "山西省": "中部",
    "吉林省": "中部",
    "黑龙江省": "中部",
    "安徽省": "中部",
    "江西省": "中部",
    "河南省": "中部",
    "湖北省": "中部",
    "湖南省": "中部",
    "内蒙古自治区": "西部",
    "广西壮族自治区": "西部",
    "重庆市": "西部",
    "四川省": "西部",
    "贵州省": "西部",
    "云南省": "西部",
    "西藏自治区": "西部",
    "陕西省": "西部",
    "甘肃省": "西部",
    "青海省": "西部",
    "宁夏回族自治区": "西部",
    "新疆维吾尔自治区": "西部",
}

PROVINCE_REGION_EN: dict[str, str] = {
    "东部": "Eastern",
    "中部": "Central",
    "西部": "Western",
}


def _read_wide_csv(path: Path, value_col_prefix: str = "") -> pd.DataFrame:
    """Read a wide-format CSV (province × year) and return long-format DataFrame."""
    df = pd.read_csv(path)
    id_col = df.columns[0]
    year_cols = [c for c in df.columns if c != id_col]
    long = df.melt(id_vars=[id_col], value_vars=year_cols, var_name="year_str", value_name="value")
    long["year"] = long["year_str"].str.extract(r"(\d{4})").astype(int)
    long = long.rename(columns={id_col: "province"}).drop(columns=["year_str"])
    # Remove national aggregate row if present
    long = long[~long["province"].isin(["全国", "合计"])]
    return long[["province", "year", "value"]]


def load_china_provincial_panel(data_dir: Path | None = None) -> pd.DataFrame:
    """Build a comprehensive China provincial health panel.

    Combines:
    - Health personnel (万人) from raw CSVs
    - Medical institution counts from raw CSVs
    - Embedded 2020 reference: population, life expectancy, infant mortality,
      per-capita health expenditure

    Returns a DataFrame with one row per (province, year) for years 2005-2024,
    plus reference-year columns from 2020 NBS/NHC data.

    Columns:
        province, province_en, region, year,
        health_personnel_wan (万人),
        health_institutions (万个),
        population_wan (万人, 2020 census),
        personnel_per_1000 (卫生人员/千人),
        institutions_per_10k (机构/万人),
        life_expectancy (岁, 2020),
        infant_mortality (‰, 2020),
        health_exp_per_capita (元, 2020)
    """
    if data_dir is None:
        data_dir = (
            Path(__file__).parent.parent.parent.parent
            / "data"
            / "raw"
            / "provided"
            / "05_china_health"
            / "全国近20年卫生数据-国家统计局"
        )

    personnel_path = data_dir / "各省近20年卫生人员数量.csv"
    institutions_path = data_dir / "近20年各省医疗卫生机构数量.csv"

    personnel = _read_wide_csv(personnel_path).rename(columns={"value": "health_personnel_wan"})
    institutions = _read_wide_csv(institutions_path).rename(columns={"value": "health_institutions"})

    panel = personnel.merge(institutions, on=["province", "year"], how="outer")

    # Add reference data
    panel["province_en"] = panel["province"].map(PROVINCE_EN).fillna(panel["province"])
    panel["region"] = panel["province"].map(PROVINCE_REGION).fillna("未知")
    panel["region_en"] = panel["region"].map(PROVINCE_REGION_EN).fillna(panel["region"])
    panel["population_wan"] = panel["province"].map(_CENSUS_2020_POP)
    panel["life_expectancy"] = panel["province"].map(_LIFE_EXPECTANCY_2020)
    panel["infant_mortality"] = panel["province"].map(_INFANT_MORTALITY_2020)
    panel["health_exp_per_capita"] = panel["province"].map(_HEALTH_EXP_PER_CAPITA_2020)

    # Per-capita density (uses 2020 population as denominator for all years, as approximation)
    panel["personnel_per_1000"] = panel["health_personnel_wan"] / panel["population_wan"] * 10.0
    # institutions per 10,000 people — institutions CSV values are in 万个
    panel["institutions_per_10k"] = panel["health_institutions"] / panel["population_wan"] * 10.0

    panel = panel.sort_values(["province", "year"]).reset_index(drop=True)
    return panel


def build_china_latest_snapshot(panel: pd.DataFrame | None = None) -> pd.DataFrame:
    """Return a cross-sectional snapshot for the latest year with all 2020 reference data.

    Suitable for resource gap, quadrant classification, and optimization.
    """
    if panel is None:
        panel = load_china_provincial_panel()

    latest_year = int(panel["year"].max())
    snap = panel[panel["year"] == latest_year].copy()

    # Standardize helper
    def _std(s: pd.Series, invert: bool = False) -> pd.Series:
        mu, sigma = s.mean(), s.std()
        if sigma < 1e-9:
            return pd.Series(np.zeros(len(s)), index=s.index)
        z = (s - mu) / sigma
        return -z if invert else z

    # Input index: personnel_per_1000 + institutions_per_10k + health_exp_per_capita
    snap["input_index"] = pd.concat(
        [
            _std(snap["personnel_per_1000"]),
            _std(snap["institutions_per_10k"]),
            _std(snap["health_exp_per_capita"]),
        ],
        axis=1,
    ).mean(axis=1)

    # Output index: life_expectancy - infant_mortality
    snap["output_index"] = pd.concat(
        [
            _std(snap["life_expectancy"]),
            _std(snap["infant_mortality"], invert=True),
        ],
        axis=1,
    ).mean(axis=1)

    # Theoretical need: inverse life expectancy + infant mortality
    snap["theoretical_need"] = pd.concat(
        [
            _std(snap["life_expectancy"], invert=True),
            _std(snap["infant_mortality"]),
        ],
        axis=1,
    ).mean(axis=1)

    snap["gap"] = snap["input_index"] - snap["theoretical_need"]

    input_median = snap["input_index"].median()
    output_median = snap["output_index"].median()
    conditions = [
        (snap["input_index"] >= input_median) & (snap["output_index"] >= output_median),
        (snap["input_index"] < input_median) & (snap["output_index"] >= output_median),
        (snap["input_index"] >= input_median) & (snap["output_index"] < output_median),
        (snap["input_index"] < input_median) & (snap["output_index"] < output_median),
    ]
    labels = ["Q1_高投入高产出", "Q2_低投入高产出", "Q3_高投入低产出", "Q4_低投入低产出"]
    labels_en = ["Q1_high_high", "Q2_low_high", "Q3_high_low", "Q4_low_low"]
    snap["quadrant"] = np.select(conditions, labels, default="未分类")
    snap["quadrant_en"] = np.select(conditions, labels_en, default="unclassified")
    snap["efficiency"] = snap["output_index"] - snap["input_index"]
    snap["latest_year"] = latest_year

    return snap.reset_index(drop=True)
