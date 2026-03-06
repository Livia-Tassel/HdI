"""Global configuration: paths, constants, and parameters."""

from pathlib import Path

# ── Paths ────────────────────────────────────────────────────────────────────
ROOT = Path(__file__).resolve().parents[2]  # HdI/
DATA = ROOT / "data"
RAW = DATA / "raw"
RAW_PROVIDED = RAW / "provided"
RAW_EXTERNAL = RAW / "external"
INTERIM = DATA / "interim"
PROCESSED = DATA / "processed"
SPATIAL = PROCESSED / "spatial"

MASTER_PANEL = PROCESSED / "master_panel.parquet"
CHINA_PANEL = PROCESSED / "china_panel.parquet"

API_OUTPUT = ROOT / "api_output"
REPORTS = ROOT / "reports"
FIGURES = REPORTS / "figures"
TABLES = REPORTS / "tables"

# ── Dataset sub-paths ────────────────────────────────────────────────────────
DS_DISEASE_MORTALITY = RAW_PROVIDED / "01_disease_mortality"
DS_RISK_FACTORS = RAW_PROVIDED / "02_risk_factors"
DS_NUTRITION_POP = RAW_PROVIDED / "03_nutrition_population"
DS_SOCIOECONOMIC = RAW_PROVIDED / "04_socioeconomic"
DS_CHINA_HEALTH = RAW_PROVIDED / "05_china_health"

EXT_IHME = RAW_EXTERNAL / "ihme_gbd"
EXT_WHO = RAW_EXTERNAL / "who_ghe"
EXT_WB = RAW_EXTERNAL / "worldbank_wdi"
EXT_UNDP = RAW_EXTERNAL / "undp_hdi"
EXT_OWID = RAW_EXTERNAL / "owid"
EXT_CHINA_NBS = RAW_EXTERNAL / "china_nbs"

# ── Analysis window ──────────────────────────────────────────────────────────
YEAR_MIN = 2000
YEAR_MAX = 2023
CHINA_YEAR_MIN = 2003
CHINA_YEAR_MAX = 2023
FORECAST_HORIZON = 2030

# ── Panel keys ───────────────────────────────────────────────────────────────
PANEL_KEY_GLOBAL = ["iso3", "year"]
PANEL_KEY_CHINA = ["province", "year"]

# ── WHO regions ──────────────────────────────────────────────────────────────
WHO_REGIONS = {
    "AFRO": "African Region",
    "AMRO": "Region of the Americas",
    "SEARO": "South-East Asia Region",
    "EURO": "European Region",
    "EMRO": "Eastern Mediterranean Region",
    "WPRO": "Western Pacific Region",
}

# ── World Bank income groups ─────────────────────────────────────────────────
WB_INCOME_GROUPS = ["LIC", "LMC", "UMC", "HIC"]

# ── Disease groups for Dimension 1 ──────────────────────────────────────────
DISEASE_GROUPS = [
    "communicable",
    "ncd",
    "injuries",
    "cardiovascular",
    "neoplasms",
    "respiratory_chronic",
    "respiratory_infectious",
    "diabetes",
    "mental",
    "musculoskeletal",
    "neurological",
]

# ── Risk factors for Dimension 2 ────────────────────────────────────────────
RISK_FACTORS = [
    "smoking",
    "pm25",
    "alcohol",
    "high_bmi",
    "high_blood_pressure",
    "high_fasting_glucose",
    "diet_low_fruit",
    "diet_high_sodium",
    "unsafe_water",
    "child_underweight",
    "low_physical_activity",
]

# ── GHRI pillars ─────────────────────────────────────────────────────────────
GHRI_PILLARS = [
    "disease_burden",
    "risk_factor_control",
    "health_system_capacity",
    "socioeconomic_foundation",
    "resilience_equity",
]

# ── Plotting defaults ────────────────────────────────────────────────────────
FIGURE_DPI = 300
FIGURE_FORMAT = "png"
COLOR_PALETTE = "Set2"

# ── Random seed ──────────────────────────────────────────────────────────────
SEED = 42

# ── Imputation ───────────────────────────────────────────────────────────────
MAX_MISSING_FRAC = 0.30  # drop columns with >30% missing
INTERP_MAX_GAP = 2  # linear interpolation for gaps <= 2 years
