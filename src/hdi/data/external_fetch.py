"""Programmatic external data acquisition."""

from __future__ import annotations

import logging
from pathlib import Path

import pandas as pd

from hdi.config import EXT_WB, EXT_OWID, EXT_UNDP, YEAR_MIN, YEAR_MAX
from hdi.data.cleaners import clean_country_year_dataset

logger = logging.getLogger(__name__)


# ── World Bank WDI via wbgapi ────────────────────────────────────────────────

WB_INDICATORS = {
    "SP.DYN.LE00.IN": "life_expectancy",
    "SP.DYN.IMRT.IN": "infant_mortality_rate",
    "SH.DYN.MORT": "under5_mortality_rate",
    "SH.STA.MMRT": "maternal_mortality_ratio",
    "SH.XPD.CHEX.GD.ZS": "health_exp_pct_gdp",
    "SH.XPD.CHEX.PC.CD": "health_exp_pc_usd",
    "SH.MED.BEDS.ZS": "hospital_beds_per_1000",
    "SH.MED.PHYS.ZS": "physicians_per_1000",
    "SH.MED.NUMW.P3": "nurses_per_1000",
    "NY.GDP.PCAP.PP.KD": "gdp_pc_ppp",
    "NY.GDP.PCAP.CD": "gdp_pc_usd",
    "SE.ADT.LITR.ZS": "literacy_rate",
    "SE.XPD.TOTL.GD.ZS": "education_exp_pct_gdp",
    "SP.URB.TOTL.IN.ZS": "urban_pct",
    "SP.POP.TOTL": "population",
    "SI.POV.GINI": "gini_index",
    "SH.STA.WASH.P5": "basic_sanitation_pct",
    "SH.H2O.BASW.ZS": "basic_water_pct",
    "SH.IMM.MEAS": "measles_immunization_pct",
    "SH.TBS.INCD": "tb_incidence_per_100k",
    "EN.ATM.PM25.MC.M3": "pm25_annual_mean",
}


def fetch_worldbank_wdi(
    indicators: dict[str, str] | None = None,
    year_range: range | None = None,
    save: bool = True,
) -> pd.DataFrame:
    """Fetch World Bank WDI indicators using wbgapi.

    Parameters
    ----------
    indicators : dict mapping WB indicator code -> friendly column name
    year_range : range of years to fetch
    save : whether to save as parquet
    """
    try:
        import wbgapi as wb
    except ImportError:
        logger.error("wbgapi not installed. Run: pip install wbgapi")
        return pd.DataFrame()

    if indicators is None:
        indicators = WB_INDICATORS
    if year_range is None:
        year_range = range(YEAR_MIN, YEAR_MAX + 1)

    logger.info("Fetching %d WDI indicators for %d-%d...",
                len(indicators), year_range.start, year_range.stop - 1)

    frames = []
    for wb_code, col_name in indicators.items():
        try:
            df = wb.data.DataFrame(
                wb_code, time=year_range, labels=False, skipBlanks=True
            )
            if df.empty:
                continue
            # wbgapi returns economy x year matrix; melt to long format
            df = df.reset_index()
            df = df.melt(id_vars=["economy"], var_name="year", value_name=col_name)
            df = df.rename(columns={"economy": "iso3"})
            df["year"] = df["year"].str.replace("YR", "").astype(int)
            frames.append(df)
            logger.info("  Fetched: %s -> %s (%d rows)", wb_code, col_name, len(df))
        except Exception as e:
            logger.warning("  Failed: %s -> %s: %s", wb_code, col_name, e)

    if not frames:
        return pd.DataFrame()

    # Merge all indicators on (iso3, year)
    panel = frames[0]
    for f in frames[1:]:
        panel = panel.merge(f, on=["iso3", "year"], how="outer")

    if save:
        EXT_WB.mkdir(parents=True, exist_ok=True)
        out = EXT_WB / "wdi_panel.parquet"
        panel.to_parquet(out, index=False)
        logger.info("Saved WDI panel: %s (%d rows)", out, len(panel))

    return panel


# ── Our World in Data ────────────────────────────────────────────────────────

OWID_DATASETS = {
    "smoking": "https://raw.githubusercontent.com/owid/owid-datasets/master/datasets/Share%20of%20adults%20who%20smoke/Share%20of%20adults%20who%20smoke.csv",
}


def fetch_owid(save: bool = True) -> pd.DataFrame:
    """Fetch selected OWID datasets from GitHub CSVs.

    Note: URLs may change. Adapt as needed.
    """
    frames = []
    for name, url in OWID_DATASETS.items():
        try:
            df = pd.read_csv(url)
            frames.append(df)
            logger.info("Fetched OWID: %s (%d rows)", name, len(df))
        except Exception as e:
            logger.warning("Failed to fetch OWID %s: %s", name, e)

    if not frames:
        return pd.DataFrame()

    combined = clean_country_year_dataset(pd.concat(frames, ignore_index=True))
    if save:
        EXT_OWID.mkdir(parents=True, exist_ok=True)
        out = EXT_OWID / "owid_combined.parquet"
        combined.to_parquet(out, index=False)

    return combined


# ── UNDP HDI ─────────────────────────────────────────────────────────────────

def fetch_undp_hdi(filepath: Path | None = None, save: bool = True) -> pd.DataFrame:
    """Load UNDP HDI data from a downloaded CSV file.

    The HDI data typically needs manual download from hdr.undp.org.
    This function handles reshaping the wide-format HDI table.
    """
    if filepath is None:
        candidates = list(EXT_UNDP.glob("*.csv"))
        if not candidates:
            logger.warning("No UNDP HDI CSV found in %s", EXT_UNDP)
            return pd.DataFrame()
        filepath = candidates[0]

    df = clean_country_year_dataset(pd.read_csv(filepath))
    logger.info("Loaded UNDP HDI: %s (%d rows)", filepath.name, len(df))

    if save:
        EXT_UNDP.mkdir(parents=True, exist_ok=True)
        out = EXT_UNDP / "hdi_panel.parquet"
        df.to_parquet(out, index=False)

    return df


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(levelname)s | %(message)s")
    fetch_worldbank_wdi()
