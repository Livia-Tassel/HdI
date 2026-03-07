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
RESOURCE_PANEL = PROCESSED / "resource_panel.parquet"
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
CHINA_YEAR_MIN = 2005
CHINA_YEAR_MAX = 2024
FORECAST_END_YEAR = 2030
FORECAST_STEPS = FORECAST_END_YEAR - YEAR_MAX
FORECAST_HORIZON = FORECAST_STEPS

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

WDI_TO_WHO_REGION = {
    "East Asia & Pacific": "WPRO",
    "Europe & Central Asia": "EURO",
    "Latin America & Caribbean": "AMRO",
    "Middle East & North Africa": "EMRO",
    "North America": "AMRO",
    "South Asia": "SEARO",
    "Sub-Saharan Africa": "AFRO",
}

WDI_TO_INCOME_CODE = {
    "High income": "HIC",
    "Lower middle income": "LMC",
    "Low income": "LIC",
    "Upper middle income": "UMC",
}

# ── Disease groups for Dimension 1 ──────────────────────────────────────────
CAUSE_GROUP_MAP = {
    "艾滋病毒/艾滋病和性传播感染": "传染性疾病",
    "其他传染性疾病": "传染性疾病",
    "呼吸道感染及结核病": "传染性疾病",
    "孕产妇和新生儿疾病": "传染性疾病",
    "肠道感染": "传染性疾病",
    "营养不良": "传染性疾病",
    "被忽视的热带病和疟疾": "传染性疾病",
    "其他非传染性疾病": "非传染性疾病",
    "心血管疾病": "非传染性疾病",
    "感觉器官疾病": "非传染性疾病",
    "慢性呼吸系统疾病": "非传染性疾病",
    "消化系统疾病": "非传染性疾病",
    "物质使用障碍": "非传染性疾病",
    "皮肤和皮下疾病": "非传染性疾病",
    "神经系统疾病": "非传染性疾病",
    "精神障碍": "非传染性疾病",
    "糖尿病和肾病": "非传染性疾病",
    "肌肉骨骼疾病": "非传染性疾病",
    "肿瘤": "非传染性疾病",
    "意外伤害": "伤害",
    "自残和人际暴力": "伤害",
    "运输伤害": "伤害",
}

# ── Risk factors for Dimension 2 ────────────────────────────────────────────
RISK_LABEL_MAP = {
    "不安全性": "unsafe_sex",
    "不安全的水，环境卫生和洗手": "unsafe_wash",
    "亲密伴侣间的暴力": "intimate_partner_violence",
    "低骨密度": "low_bone_density",
    "体温": "non_optimal_temperature",
    "儿童和孕产妇营养不良": "child_maternal_malnutrition",
    "儿童虐待": "child_maltreatment",
    "其他环境危险因素": "other_environmental",
    "烟草烟雾": "tobacco",
    "用药": "drug_use",
    "空气污染": "air_pollution",
    "职业风险": "occupational_risks",
    "肾脏功能受损": "kidney_dysfunction",
    "身体活动不足": "low_physical_activity",
    "饮酒": "alcohol_use",
    "饮食风险": "dietary_risks",
    "高BMI指数": "high_bmi",
    "高低密度脂蛋白胆固醇": "high_ldl",
    "高血压": "high_systolic_bp",
    "高血糖": "high_fasting_glucose",
}

RISK_INTERVENTIONS = {
    "tobacco": "强化控烟立法、提高烟草税、戒烟门诊覆盖",
    "air_pollution": "推进清洁能源替代、工业减排和空气质量治理",
    "dietary_risks": "推广减盐减糖、健康食物可及性和营养标签",
    "high_bmi": "社区体重管理、学校膳食改善、运动处方",
    "high_systolic_bp": "基层筛查、高血压规范管理和药物可及性",
    "high_fasting_glucose": "糖尿病早筛、生活方式干预和基层随访",
    "unsafe_wash": "安全饮水、厕所和手卫生基础设施投入",
    "child_maternal_malnutrition": "孕产妇营养补充、儿童早期营养支持",
    "alcohol_use": "限制销售时段、酒精税和高危人群干预",
    "low_physical_activity": "城市步行骑行环境、学校和职场运动促进",
}

MASTER_CANONICAL_COLUMNS = [
    "country_name",
    "who_region",
    "wb_income",
    "total_deaths",
    "communicable_deaths",
    "ncd_deaths",
    "injury_deaths",
    "communicable_share",
    "ncd_share",
    "injury_share",
    "cardiovascular_deaths",
    "cancer_deaths",
    "diabetes_kidney_deaths",
    "respiratory_chronic_deaths",
    "maternal_neonatal_deaths",
    "life_expectancy",
    "infant_mortality",
    "under5_mortality",
    "adult_mortality_male",
    "adult_mortality_female",
    "physicians_per_1000",
    "beds_per_1000",
    "nurses_per_1000",
    "health_exp_pct_gdp",
    "health_exp_per_capita",
    "gdp_per_capita",
    "urban_population_pct",
    "basic_water_pct",
    "basic_sanitation_pct",
    "measles_immunization_pct",
    "fertility_rate",
]

INDICATOR_SPECS = {
    "life_expectancy": {
        "label": "出生时预期寿命",
        "unit": "岁",
        "dimension": "dim1",
        "candidates": ["WB_HNP_SP_DYN_LE00_IN", "SP.DYN.LE00.IN"],
    },
    "infant_mortality": {
        "label": "婴儿死亡率",
        "unit": "每千活产",
        "dimension": "dim1",
        "candidates": ["WB_HNP_SP_DYN_IMRT_IN", "SP.DYN.IMRT.IN"],
    },
    "under5_mortality": {
        "label": "5岁以下死亡率",
        "unit": "每千活产",
        "dimension": "dim1",
        "candidates": ["WB_HNP_SH_DYN_MORT", "SH.DYN.MORT"],
    },
    "adult_mortality_male": {
        "label": "男性成人死亡率",
        "unit": "每千人",
        "dimension": "dim1",
        "candidates": ["SP.DYN.AMRT.MA"],
    },
    "adult_mortality_female": {
        "label": "女性成人死亡率",
        "unit": "每千人",
        "dimension": "dim1",
        "candidates": ["SP.DYN.AMRT.FE"],
    },
    "physicians_per_1000": {
        "label": "医生密度",
        "unit": "每千人",
        "dimension": "dim3",
        "candidates": ["WB_HNP_SH_MED_PHYS_ZS", "SH.MED.PHYS.ZS"],
    },
    "beds_per_1000": {
        "label": "病床密度",
        "unit": "每千人",
        "dimension": "dim3",
        "candidates": ["WB_HNP_SH_MED_BEDS_ZS", "SH.MED.BEDS.ZS"],
    },
    "nurses_per_1000": {
        "label": "护士和助产士密度",
        "unit": "每千人",
        "dimension": "dim3",
        "candidates": ["WB_HNP_SH_MED_NUMW_P3"],
    },
    "health_exp_pct_gdp": {
        "label": "卫生支出占GDP比重",
        "unit": "%",
        "dimension": "dim3",
        "candidates": ["SH.XPD.CHEX.GD.ZS"],
    },
    "health_exp_per_capita": {
        "label": "人均卫生支出",
        "unit": "现价美元",
        "dimension": "dim3",
        "candidates": ["SH.XPD.CHEX.PC.CD"],
    },
    "gdp_per_capita": {
        "label": "人均GDP",
        "unit": "现价美元",
        "dimension": "dim1",
        "candidates": ["NY.GDP.PCAP.CD"],
    },
    "urban_population_pct": {
        "label": "城镇人口占比",
        "unit": "%",
        "dimension": "dim1",
        "candidates": ["SP.URB.TOTL.IN.ZS"],
    },
    "basic_water_pct": {
        "label": "基本饮水服务覆盖率",
        "unit": "%",
        "dimension": "dim1",
        "candidates": ["WB_HNP_SH_H2O_BASW_ZS", "SH.H2O.BASW.ZS"],
    },
    "basic_sanitation_pct": {
        "label": "基本卫生服务覆盖率",
        "unit": "%",
        "dimension": "dim1",
        "candidates": ["WB_HNP_SH_STA_BASS_ZS", "SH.STA.BASS.ZS"],
    },
    "measles_immunization_pct": {
        "label": "麻疹免疫覆盖率",
        "unit": "%",
        "dimension": "dim1",
        "candidates": ["WB_HNP_SH_IMM_MEAS"],
    },
    "fertility_rate": {
        "label": "总和生育率",
        "unit": "每名妇女生育数",
        "dimension": "dim1",
        "candidates": ["WB_HNP_SP_DYN_TFRT_IN"],
    },
}

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
