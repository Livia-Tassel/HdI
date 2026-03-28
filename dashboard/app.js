const DATA_SOURCES = {
  overview: "./data/overview.json",
  riskLatest: "./data/risk_latest.json",
  globalStory: "./data/global_story.json",
  profiles: "./data/country_profiles.json",
  timeseries: "./data/overview_timeseries.json",
  chinaDeepDive: "./data/china_deep_dive.json",
  chinaProvinces: "./data/china_provinces.json",
  panorama: "./data/panorama.json",
  bubbleTimeseries: "./data/bubble_timeseries.json",
  riskIndicators: "./data/risk_indicators.json",
};

const DIMENSIONS = {
  dim1: {
    label: "疾病谱变迁",
    defaultMetric: "life_expectancy",
    mapTitle: "全球疾病谱与健康结果",
    note: "点击国家查看预期寿命、疾病结构和卫生体系状况。",
    metrics: ["life_expectancy", "ncd_share", "communicable_share", "health_exp_pct_gdp"],
  },
  dim2: {
    label: "风险因素",
    defaultMetric: "share",
    mapTitle: "全球健康风险因素分布",
    note: "选择风险因素，查看各国风险负担分布。",
    metrics: ["share", "attributable_deaths"],
  },
  dim3: {
    label: "资源配置",
    defaultMetric: "change_pct",
    mapTitle: "全球卫生资源配置分析",
    note: "调整优化目标与预算，对比不同资源配置方案。",
    metrics: ["change_pct", "gap", "efficiency"],
  },
  dim4: {
    label: "中国大陆聚焦",
    defaultMetric: "prov_gap",
    mapTitle: "中国大陆省级卫生资源配置分析",
    note: "探索中国大陆31个省级行政区的卫生资源配置、效率与优化方案。",
    metrics: ["prov_gap", "prov_efficiency", "prov_life_expectancy", "prov_infant_mortality", "prov_personnel_per_1000", "prov_hospital_beds_per_1000", "prov_physicians_per_1000", "prov_nurses_per_1000", "prov_health_exp", "prov_gdp_per_capita", "prov_optimization_change"],
  },
  dim5: {
    label: "健康全景",
    defaultMetric: "hdi",
    mapTitle: "全球健康发展全景图",
    note: "综合WHO、UNDP、世界银行数据，探索发展与健康的深层关联。",
    metrics: ["hdi", "hale", "uhc_index", "pm25", "doctor_density", "che_per_capita"],
  },
};

const METRIC_META = {
  life_expectancy: {
    label: "预期寿命",
    colorscale: [[0, "#0c1929"], [0.25, "#0e3a5e"], [0.5, "#0d6577"], [0.75, "#17a2b8"], [1, "#22d3ee"]],
    formatter: (value) => (value == null ? NO_DATA_LABEL : `${Number(value).toFixed(1)} 岁`),
    accessor: (row) => row.life_expectancy,
  },
  ncd_share: {
    label: "非传染性疾病占比",
    colorscale: [[0, "#0c1929"], [0.25, "#1a2747"], [0.5, "#2e4070"], [0.75, "#6366f1"], [1, "#a78bfa"]],
    formatter: (value) => formatShare(value),
    accessor: (row) => row.ncd_share,
  },
  communicable_share: {
    label: "传染性疾病占比",
    colorscale: [[0, "#1a1308"], [0.25, "#4a3010"], [0.5, "#7a5518"], [0.75, "#d4941a"], [1, "#fbbf24"]],
    formatter: (value) => formatShare(value),
    accessor: (row) => row.communicable_share,
  },
  health_exp_pct_gdp: {
    label: "卫生支出占GDP比重",
    colorscale: [[0, "#071a17"], [0.25, "#0c3a32"], [0.5, "#12705f"], [0.75, "#1db99a"], [1, "#2dd4bf"]],
    formatter: (value) => formatPercentValue(value),
    accessor: (row) => row.health_exp_pct_gdp,
  },
  share: {
    label: "风险因素占比",
    colorscale: [[0, "#0c1929"], [0.25, "#2a1a4e"], [0.5, "#6b21a8"], [0.75, "#9333ea"], [1, "#c084fc"]],
    formatter: (value) => formatShare(value),
    accessor: (row) => row.share,
  },
  attributable_deaths: {
    label: "风险致死",
    colorscale: [[0, "#0c1929"], [0.25, "#1e3a5f"], [0.5, "#0d6577"], [0.75, "#22d3ee"], [1, "#fbbf24"]],
    formatter: (value) => formatCompact(value),
    accessor: (row) => row.attributable_deaths,
  },
  change_pct: {
    label: "资源调整方案",
    colorscale: [[0, "#fb7185"], [0.25, "#4a1525"], [0.5, "#111827"], [0.75, "#164e63"], [1, "#22d3ee"]],
    formatter: (value) => formatSignedPercent(value),
    accessor: (row) => row.change_pct,
    diverging: true,
  },
  gap: {
    label: "资源缺口",
    colorscale: [[0, "#fb7185"], [0.25, "#4a1525"], [0.5, "#111827"], [0.75, "#0c3a32"], [1, "#2dd4bf"]],
    formatter: (value) => formatSigned(value),
    accessor: (row) => row.gap,
    diverging: true,
  },
  efficiency: {
    label: "资源使用效率",
    colorscale: [[0, "#fb7185"], [0.25, "#4a1525"], [0.5, "#111827"], [0.75, "#0c3a32"], [1, "#2dd4bf"]],
    formatter: (value) => formatSigned(value),
    accessor: (row) => row.efficiency,
    diverging: true,
  },
  health_personnel: {
    label: "卫生人员",
    colorscale: [[0, "#1a0808"], [0.25, "#4a1010"], [0.5, "#8b2020"], [0.75, "#dc2626"], [1, "#f87171"]],
    formatter: (value) => value == null ? NO_DATA_LABEL : `${formatCompact(value)} 万人`,
    accessor: (row) => row.value,
  },
  health_institutions: {
    label: "卫生机构",
    colorscale: [[0, "#1a0808"], [0.25, "#4a1010"], [0.5, "#8b2020"], [0.75, "#dc2626"], [1, "#f87171"]],
    formatter: (value) => value == null ? NO_DATA_LABEL : `${formatCompact(value)} 个`,
    accessor: (row) => row.value,
  },
  prov_gap: {
    label: "省级资源缺口",
    colorscale: [[0, "#fb7185"], [0.25, "#4a1525"], [0.5, "#111827"], [0.75, "#0c3a32"], [1, "#2dd4bf"]],
    formatter: (value) => formatSigned(value),
    accessor: (row) => row.gap,
    diverging: true,
  },
  prov_efficiency: {
    label: "省级资源效率",
    colorscale: [[0, "#fb7185"], [0.25, "#4a1525"], [0.5, "#111827"], [0.75, "#0c3a32"], [1, "#2dd4bf"]],
    formatter: (value) => formatSigned(value),
    accessor: (row) => row.efficiency,
    diverging: true,
  },
  prov_life_expectancy: {
    label: "平均预期寿命",
    colorscale: [[0, "#0c1929"], [0.25, "#0e3a5e"], [0.5, "#0d6577"], [0.75, "#17a2b8"], [1, "#22d3ee"]],
    formatter: (value) => value == null ? NO_DATA_LABEL : `${Number(value).toFixed(1)} 岁`,
    accessor: (row) => row.life_expectancy,
  },
  prov_infant_mortality: {
    label: "婴儿死亡率",
    colorscale: [[0, "#0c1929"], [0.25, "#1e3a5f"], [0.5, "#7a5518"], [0.75, "#d4941a"], [1, "#fbbf24"]],
    formatter: (value) => value == null ? NO_DATA_LABEL : `${Number(value).toFixed(1)} ‰`,
    accessor: (row) => row.infant_mortality,
  },
  prov_personnel_per_1000: {
    label: "卫生人员密度（每千人）",
    colorscale: [[0, "#071a17"], [0.25, "#0c3a32"], [0.5, "#12705f"], [0.75, "#2dd4bf"], [1, "#99f6e4"]],
    formatter: (value) => value == null ? NO_DATA_LABEL : `${Number(value).toFixed(2)}/千人`,
    accessor: (row) => row.personnel_per_1000,
  },
  prov_hospital_beds_per_1000: {
    label: "医院床位（每千人）",
    colorscale: [[0, "#071a17"], [0.25, "#0c3a32"], [0.5, "#12705f"], [0.75, "#2dd4bf"], [1, "#99f6e4"]],
    formatter: (value) => value == null ? NO_DATA_LABEL : `${Number(value).toFixed(2)}/千人`,
    accessor: (row) => row.hospital_beds_per_1000,
  },
  prov_physicians_per_1000: {
    label: "执业医师（每千人）",
    colorscale: [[0, "#0c1929"], [0.25, "#0e3a5e"], [0.5, "#0d6577"], [0.75, "#17a2b8"], [1, "#22d3ee"]],
    formatter: (value) => value == null ? NO_DATA_LABEL : `${Number(value).toFixed(2)}/千人`,
    accessor: (row) => row.physicians_per_1000,
  },
  prov_nurses_per_1000: {
    label: "注册护士（每千人）",
    colorscale: [[0, "#1a0f2e"], [0.25, "#2d1b69"], [0.5, "#6366f1"], [0.75, "#818cf8"], [1, "#c7d2fe"]],
    formatter: (value) => value == null ? NO_DATA_LABEL : `${Number(value).toFixed(2)}/千人`,
    accessor: (row) => row.nurses_per_1000,
  },
  prov_health_exp: {
    label: "人均卫生支出（元）",
    colorscale: [[0, "#0c1929"], [0.25, "#0e3a5e"], [0.5, "#1d4ed8"], [0.75, "#38bdf8"], [1, "#bae6fd"]],
    formatter: (value) => value == null ? NO_DATA_LABEL : `¥${Number(value).toLocaleString()}`,
    accessor: (row) => row.health_exp_per_capita,
  },
  prov_gdp_per_capita: {
    label: "人均GDP（元，2023）",
    colorscale: [[0, "#071a17"], [0.25, "#0c3a32"], [0.5, "#12705f"], [0.75, "#34d399"], [1, "#6ee7b7"]],
    formatter: (value) => value == null ? NO_DATA_LABEL : `¥${Number(value).toLocaleString()}`,
    accessor: (row) => row.gdp_per_capita,
  },
  prov_optimization_change: {
    label: "最优化调整方案（%）",
    colorscale: [[0, "#fb7185"], [0.25, "#4a1525"], [0.5, "#111827"], [0.75, "#164e63"], [1, "#22d3ee"]],
    formatter: (value) => formatSignedPercent(value),
    accessor: (row) => row.prov_change_pct,
    diverging: true,
  },
  hdi: {
    label: "人类发展指数",
    colorscale: [[0, "#071a17"], [0.25, "#0c3a32"], [0.5, "#12705f"], [0.75, "#34d399"], [1, "#6ee7b7"]],
    formatter: (value) => (value == null ? NO_DATA_LABEL : Number(value).toFixed(3)),
    accessor: (row) => row.hdi,
  },
  hale: {
    label: "健康预期寿命",
    colorscale: [[0, "#0c1929"], [0.25, "#0e3a5e"], [0.5, "#0d6577"], [0.75, "#17a2b8"], [1, "#22d3ee"]],
    formatter: (value) => (value == null ? NO_DATA_LABEL : `${Number(value).toFixed(1)} 岁`),
    accessor: (row) => row.hale,
  },
  uhc_index: {
    label: "全民健康覆盖指数",
    colorscale: [[0, "#1a0f2e"], [0.25, "#2d1b69"], [0.5, "#6366f1"], [0.75, "#818cf8"], [1, "#c7d2fe"]],
    formatter: (value) => (value == null ? NO_DATA_LABEL : `${Number(value).toFixed(1)}`),
    accessor: (row) => row.uhc_index,
  },
  pm25: {
    label: "PM2.5 暴露浓度",
    colorscale: [[0, "#071a17"], [0.25, "#4a3010"], [0.5, "#7a5518"], [0.75, "#d4941a"], [1, "#fbbf24"]],
    formatter: (value) => (value == null ? NO_DATA_LABEL : `${Number(value).toFixed(1)} μg/m³`),
    accessor: (row) => row.pm25,
  },
  doctor_density: {
    label: "医生密度（每万人）",
    colorscale: [[0, "#0c1929"], [0.25, "#1e3a5f"], [0.5, "#0d6577"], [0.75, "#2dd4bf"], [1, "#99f6e4"]],
    formatter: (value) => (value == null ? NO_DATA_LABEL : `${Number(value).toFixed(1)}`),
    accessor: (row) => row.doctor_density,
  },
  che_per_capita: {
    label: "人均卫生支出",
    colorscale: [[0, "#0c1929"], [0.25, "#0e3a5e"], [0.5, "#1d4ed8"], [0.75, "#38bdf8"], [1, "#bae6fd"]],
    formatter: (value) => formatCurrency(value),
    accessor: (row) => row.che_per_capita,
  },
};

const THEME = {
  ink: "#e2e8f0",
  inkBright: "#f8fafc",
  muted: "#94a3b8",
  dim: "#64748b",
  cyan: "#22d3ee",
  teal: "#2dd4bf",
  blue: "#38bdf8",
  amber: "#fbbf24",
  rose: "#fb7185",
  violet: "#a78bfa",
  emerald: "#34d399",
  grid: "rgba(148,163,184,0.08)",
  hover: "rgba(15,23,42,0.94)",
};

const OBJECTIVE_META = {
  max_output: {
    label: "最大化总产出",
    note: "优先提升全系统的总体健康产出。",
  },
  maximin: {
    label: "公平最大化",
    note: "优先提升最弱势国家的健康水平。",
  },
};

const OBJECTIVE_ALIASES = {
  max_output: "max_output",
  maximize_aggregate_output: "max_output",
  maximize_need_weighted_health_output: "max_output",
  projected_need_weighted_allocation: "max_output",
  maximin: "maximin",
};

const NO_DATA_LABEL = "暂无";

const REGION_LABELS = {
  AFRO: "非洲区域",
  AMRO: "美洲区域",
  EMRO: "东地中海区域",
  EURO: "欧洲区域",
  SEARO: "东南亚区域",
  WPRO: "西太平洋区域",
};

const INCOME_LABELS = {
  HIC: "高收入",
  LIC: "低收入",
  LMC: "中低收入",
  UMC: "中高收入",
};

const RISK_LABELS = {
  "Air pollution": "空气污染",
  "Alcohol use": "饮酒",
  "Child and maternal malnutrition": "儿童与孕产妇营养不良",
  "Child maltreatment": "儿童虐待",
  "Dietary risks": "膳食风险",
  "Drug use": "药物滥用",
  "High BMI": "高体重指数",
  "High LDL cholesterol": "高低密度脂蛋白胆固醇",
  "High fasting glucose": "高空腹血糖",
  "High systolic blood pressure": "高收缩压",
  "Intimate partner violence": "亲密伴侣暴力",
  "Kidney dysfunction": "肾功能障碍",
  "Low bone mineral density": "低骨密度",
  "Low physical activity": "身体活动不足",
  "Non-optimal temperature": "非适宜温度",
  "Occupational risks": "职业风险",
  "Other environmental risks": "其他环境风险",
  Tobacco: "烟草",
  "Unsafe sex": "不安全性行为",
  "Unsafe water, sanitation, and handwashing": "不安全饮水、卫生与洗手条件",
};

const PROVINCE_LABELS = {
  Anhui: "安徽",
  Beijing: "北京",
  Chongqing: "重庆",
  Fujian: "福建",
  Gansu: "甘肃",
  Guangdong: "广东",
  Guangxi: "广西",
  Guizhou: "贵州",
  Hainan: "海南",
  Hebei: "河北",
  Heilongjiang: "黑龙江",
  Henan: "河南",
  Hubei: "湖北",
  Hunan: "湖南",
  "Inner Mongolia": "内蒙古",
  Jiangsu: "江苏",
  Jiangxi: "江西",
  Jilin: "吉林",
  Liaoning: "辽宁",
  Ningxia: "宁夏",
  Qinghai: "青海",
  Shaanxi: "陕西",
  Shandong: "山东",
  Shanghai: "上海",
  Shanxi: "山西",
  Sichuan: "四川",
  Tianjin: "天津",
  Tibet: "西藏",
  Xinjiang: "新疆",
  Yunnan: "云南",
  Zhejiang: "浙江",
};

const ISO3_TO_ISO2 = {
  AFG:"AF",ALB:"AL",DZA:"DZ",AND:"AD",AGO:"AO",ATG:"AG",ARG:"AR",ARM:"AM",AUS:"AU",AUT:"AT",
  AZE:"AZ",BHS:"BS",BHR:"BH",BGD:"BD",BRB:"BB",BLR:"BY",BEL:"BE",BLZ:"BZ",BEN:"BJ",BTN:"BT",
  BOL:"BO",BIH:"BA",BWA:"BW",BRA:"BR",BRN:"BN",BGR:"BG",BFA:"BF",BDI:"BI",KHM:"KH",CMR:"CM",
  CAN:"CA",CPV:"CV",CAF:"CF",TCD:"TD",CHL:"CL",CHN:"CN",COL:"CO",COM:"KM",COG:"CG",COD:"CD",
  CRI:"CR",CIV:"CI",HRV:"HR",CUB:"CU",CYP:"CY",CZE:"CZ",DNK:"DK",DJI:"DJ",DMA:"DM",DOM:"DO",
  ECU:"EC",EGY:"EG",SLV:"SV",GNQ:"GQ",ERI:"ER",EST:"EE",SWZ:"SZ",ETH:"ET",FJI:"FJ",FIN:"FI",
  FRA:"FR",GAB:"GA",GMB:"GM",GEO:"GE",DEU:"DE",GHA:"GH",GRC:"GR",GRD:"GD",GTM:"GT",GIN:"GN",
  GNB:"GW",GUY:"GY",HTI:"HT",HND:"HN",HUN:"HU",ISL:"IS",IND:"IN",IDN:"ID",IRN:"IR",IRQ:"IQ",
  IRL:"IE",ISR:"IL",ITA:"IT",JAM:"JM",JPN:"JP",JOR:"JO",KAZ:"KZ",KEN:"KE",KIR:"KI",PRK:"KP",
  KOR:"KR",KWT:"KW",KGZ:"KG",LAO:"LA",LVA:"LV",LBN:"LB",LSO:"LS",LBR:"LR",LBY:"LY",LTU:"LT",
  LUX:"LU",MDG:"MG",MWI:"MW",MYS:"MY",MDV:"MV",MLI:"ML",MLT:"MT",MHL:"MH",MRT:"MR",MUS:"MU",
  MEX:"MX",FSM:"FM",MDA:"MD",MCO:"MC",MNG:"MN",MNE:"ME",MAR:"MA",MOZ:"MZ",MMR:"MM",NAM:"NA",
  NRU:"NR",NPL:"NP",NLD:"NL",NZL:"NZ",NIC:"NI",NER:"NE",NGA:"NG",MKD:"MK",NOR:"NO",OMN:"OM",
  PAK:"PK",PLW:"PW",PAN:"PA",PNG:"PG",PRY:"PY",PER:"PE",PHL:"PH",POL:"PL",PRT:"PT",QAT:"QA",
  ROU:"RO",RUS:"RU",RWA:"RW",KNA:"KN",LCA:"LC",VCT:"VC",WSM:"WS",STP:"ST",SAU:"SA",SEN:"SN",
  SRB:"RS",SYC:"SC",SLE:"SL",SGP:"SG",SVK:"SK",SVN:"SI",SLB:"SB",SOM:"SO",ZAF:"ZA",SSD:"SS",
  ESP:"ES",LKA:"LK",SDN:"SD",SUR:"SR",SWE:"SE",CHE:"CH",SYR:"SY",TJK:"TJ",TZA:"TZ",
  THA:"TH",TLS:"TL",TGO:"TG",TON:"TO",TTO:"TT",TUN:"TN",TUR:"TR",TKM:"TM",TUV:"TV",UGA:"UG",
  UKR:"UA",ARE:"AE",GBR:"GB",USA:"US",URY:"UY",UZB:"UZ",VUT:"VU",VEN:"VE",VNM:"VN",YEM:"YE",
  ZMB:"ZM",ZWE:"ZW",PSE:"PS",XKX:"XK",COK:"CK",NIU:"NU",
};

const DISPLAY_NAMES_ZH =
  typeof Intl !== "undefined" && typeof Intl.DisplayNames === "function"
    ? new Intl.DisplayNames(["zh-Hans"], { type: "region" })
    : null;

const state = {
  dimension: "dim1",
  metric: "life_expectancy",
  risk: "",
  country: "CHN",
  objective: "max_output",
  budgetMultiplier: 1.0,
  scenarioId: "",
  dialogOpen: false,
  dialogCountry: "",
  previousFocus: null,
  year: 2023,
  animating: false,
  animationTimer: null,
  province: "",
  companionView: "transition",
  chinaObjective: "max_output",
  chinaBudgetMultiplier: 1.0,
};

const store = {
  overview: null,
  riskLatest: null,
  globalStory: null,
  profiles: null,
  timeseries: null,
  chinaDeepDive: null,
  chinaProvinces: null,
  panorama: null,
  bubbleTimeseries: null,
  riskIndicators: null,
  overviewIndex: new Map(),
  riskIndex: new Map(),
  countryLookup: new Map(),
  optimizationScenarios: [],
  scenarioIndex: new Map(),
  availableYears: [],
  panoramaIndex: new Map(),
  riskIndicatorIndex: new Map(),
  bubbleYears: [],
  chinaProvinceIndex: new Map(),
  chinaOptimizationScenarios: [],
  chinaScenarioIndex: new Map(),
  chinaObjective: "max_output",
  chinaBudgetMultiplier: 1.0,
};

document.addEventListener("DOMContentLoaded", async () => {
  try {
    if (!window.Plotly) {
      throw new Error("Local Plotly bundle was not loaded.");
    }
    await loadData();
    bindEvents();
    renderAll();
    document.body.classList.add("ready");
  } catch (error) {
    console.error(error);
    renderFailure(error);
  }
});

async function loadData() {
  const entries = await Promise.all(
    Object.entries(DATA_SOURCES).map(async ([key, url]) => [key, await loadJson(url)]),
  );

  for (const [key, value] of entries) {
    store[key] = value;
  }

  for (const country of store.overview.countries ?? []) {
    store.overviewIndex.set(country.iso3, country);
    const isoKey = safeLower(country.iso3);
    const nameKey = safeLower(country.country_name);
    const zhNameKey = safeLower(countryLabel(country));
    if (isoKey) {
      store.countryLookup.set(isoKey, country.iso3);
    }
    if (nameKey) {
      store.countryLookup.set(nameKey, country.iso3);
      store.countryLookup.set(`${nameKey} (${isoKey})`, country.iso3);
    }
    if (zhNameKey) {
      store.countryLookup.set(zhNameKey, country.iso3);
      store.countryLookup.set(`${zhNameKey} (${isoKey})`, country.iso3);
    }
  }

  for (const risk of store.riskLatest.risks ?? []) {
    store.riskIndex.set(`${risk.iso3}|${risk.risk_code}`, risk);
  }

  store.optimizationScenarios = normalizeOptimizationScenarios();
  store.scenarioIndex = new Map(
    store.optimizationScenarios.map((scenario) => [scenario.scenario_id, scenario]),
  );

  if (store.timeseries?.years?.length) {
    store.availableYears = store.timeseries.years;
    state.year = store.availableYears[store.availableYears.length - 1];
  }

  // Build panorama indexes
  if (store.panorama?.countries) {
    for (const c of store.panorama.countries) {
      store.panoramaIndex.set(c.iso3, c);
    }
  }
  if (store.riskIndicators?.countries) {
    for (const c of store.riskIndicators.countries) {
      store.riskIndicatorIndex.set(c.iso3, c);
    }
  }
  if (store.bubbleTimeseries?.years?.length) {
    store.bubbleYears = store.bubbleTimeseries.years;
  }

  // Build China province index (by Chinese province name)
  for (const prov of store.chinaDeepDive?.provinces ?? []) {
    store.chinaProvinceIndex.set(prov.province, prov);
  }

  // Build China optimization scenarios index
  const chinaOpt = store.chinaDeepDive?.optimization;
  if (chinaOpt?.scenarios?.length) {
    store.chinaOptimizationScenarios = chinaOpt.scenarios;
    store.chinaScenarioIndex = new Map(
      chinaOpt.scenarios.map((sc) => [sc.scenario_id, sc])
    );
  }

  primeState();
  populateCountryDatalist();
}

async function loadJson(url) {
  const response = await fetch(url);
  if (!response.ok) {
    throw new Error(`Failed to fetch ${url}: ${response.status}`);
  }
  return response.json();
}

function primeState() {
  if (!store.overviewIndex.has(state.country)) {
    state.country = store.overview.countries?.[0]?.iso3 ?? "";
  }

  state.risk = store.riskLatest.available_risks?.[0]?.risk_code ?? "";
  syncScenarioSelection();

  // Default province: Beijing (北京市)
  if (!state.province && store.chinaDeepDive?.provinces?.length) {
    const bj = store.chinaDeepDive.provinces.find((p) => p.province === "北京市");
    state.province = bj?.province ?? store.chinaDeepDive.provinces[0]?.province ?? "";
  }
}

function normalizeOptimizationScenarios() {
  const rawCandidates = [
    store.globalStory?.optimization_lab?.scenarios,
    store.globalStory?.optimization_scenarios,
    store.overview?.optimization_lab?.scenarios,
    store.overview?.optimization_scenarios,
  ].find((candidate) => Array.isArray(candidate) && candidate.length > 0);

  const scenarios = (rawCandidates ?? [])
    .map((scenario, index) => normalizeScenario(scenario, index))
    .filter(Boolean);

  if (scenarios.length > 0) {
    return scenarios.sort((left, right) => {
      if (left.objective === right.objective) {
        return left.budget_multiplier - right.budget_multiplier;
      }
      return objectiveRank(left.objective) - objectiveRank(right.objective);
    });
  }

  const fallback = buildFallbackScenario();
  return fallback ? [fallback] : [];
}

function normalizeScenario(rawScenario, index) {
  const objective = normalizeObjective(rawScenario.objective ?? rawScenario.objective_name ?? rawScenario.status);
  const budgetMultiplier = normalizeBudget(rawScenario.budget_multiplier ?? rawScenario.budget ?? 1.0);
  const allocation = normalizeScenarioAllocation(
    rawScenario.allocation ?? rawScenario.optimal_allocation ?? rawScenario.rows ?? [],
  );

  if (!allocation.length) {
    return null;
  }

  const scenario = {
    scenario_id: rawScenario.scenario_id ?? makeScenarioId(objective, budgetMultiplier, index),
    objective,
    budget_multiplier: budgetMultiplier,
    objective_value: normalizeNumber(rawScenario.objective_value),
    status: rawScenario.status ?? "ready",
    label: `${objectiveLabel(objective)} | ${budgetLabel(budgetMultiplier)}`,
    allocation,
    summary: {},
  };

  scenario.summary = buildScenarioSummary(scenario, rawScenario.summary ?? {});
  scenario.allocationIndex = new Map(scenario.allocation.map((row) => [row.iso3, row]));
  return scenario;
}

function normalizeScenarioAllocation(rows) {
  return (rows ?? [])
    .map((row) => ({
      iso3: row.iso3,
      country_name: row.country_name ?? row.country ?? row.name ?? row.iso3,
      current: normalizeNumber(row.current),
      optimal: normalizeNumber(row.optimal),
      change: normalizeNumber(row.change),
      change_pct: normalizeNumber(row.change_pct),
      projected_output: normalizeNumber(row.projected_output),
      projected_output_change: normalizeNumber(row.projected_output_change),
      projected_output_change_pct: normalizeNumber(row.projected_output_change_pct),
    }))
    .filter((row) => row.iso3);
}

function buildFallbackScenario() {
  const allocation = (store.overview.countries ?? [])
    .filter((country) => country.current != null || country.optimal != null || country.change_pct != null)
    .map((country) => ({
      iso3: country.iso3,
      country_name: country.country_name,
      current: normalizeNumber(country.current),
      optimal: normalizeNumber(country.optimal),
      change: normalizeNumber(country.change),
      change_pct: normalizeNumber(country.change_pct),
    }));

  if (!allocation.length) {
    return null;
  }

  const scenario = {
    scenario_id: "fallback_max_output_1p0",
    objective: "max_output",
    budget_multiplier: 1.0,
    objective_value: null,
    status: "fallback_from_overview",
    label: "基准方案 | 当前预算",
    allocation,
    summary: {},
  };
  scenario.summary = buildScenarioSummary(scenario, {
    note: "从最新概览数据中衍生的回退情景。",
  });
  scenario.allocationIndex = new Map(scenario.allocation.map((row) => [row.iso3, row]));
  return scenario;
}

function buildScenarioSummary(scenario, rawSummary = {}) {
  const allocation = scenario.allocation ?? [];
  const totalCurrent = sumValues(allocation.map((row) => row.current));
  const totalOptimal = sumValues(allocation.map((row) => row.optimal));
  const recipients = allocation
    .filter((row) => (row.change ?? 0) > 0)
    .sort((left, right) => (right.change_pct ?? -Infinity) - (left.change_pct ?? -Infinity));
  const donors = allocation
    .filter((row) => (row.change ?? 0) < 0)
    .sort((left, right) => (left.change_pct ?? Infinity) - (right.change_pct ?? Infinity));
  const movedBudget = sumValues(allocation.map((row) => Math.abs(row.change ?? 0))) / 2;
  const merged = {
    label: scenario.label,
    note: OBJECTIVE_META[scenario.objective]?.note ?? "",
    recipient_count: rawSummary.recipient_count ?? recipients.length,
    donor_count: rawSummary.donor_count ?? donors.length,
    total_current: rawSummary.total_current ?? totalCurrent,
    total_optimal: rawSummary.total_optimal ?? totalOptimal,
    moved_budget: rawSummary.moved_budget ?? movedBudget,
    projected_output_change_pct:
      rawSummary.projected_output_change_pct ?? normalizeNumber(rawSummary.projected_output_change_pct),
    top_recipient: translateCountryName(rawSummary.top_recipient ?? recipients[0]?.country_name),
    top_donor: translateCountryName(rawSummary.top_donor ?? donors[0]?.country_name),
    objective_label: objectiveLabel(scenario.objective),
    budget_label: budgetLabel(scenario.budget_multiplier),
  };

  return merged;
}

function bindEvents() {
  document.querySelectorAll("[data-dimension]").forEach((button) => {
    button.addEventListener("click", () => {
      state.dimension = button.dataset.dimension;
      state.metric = DIMENSIONS[state.dimension].defaultMetric;
      renderAll();
    });
  });

  document.getElementById("metric-select").addEventListener("change", (event) => {
    state.metric = event.target.value;
    renderAll();
  });

  document.getElementById("risk-select").addEventListener("change", (event) => {
    state.risk = event.target.value;
    renderAll();
  });

  document.getElementById("objective-select").addEventListener("change", (event) => {
    if (state.dimension === "dim4") {
      state.chinaObjective = normalizeObjective(event.target.value);
    } else {
      state.objective = normalizeObjective(event.target.value);
      syncScenarioSelection();
    }
    renderAll();
  });

  document.getElementById("budget-select").addEventListener("change", (event) => {
    if (state.dimension === "dim4") {
      state.chinaBudgetMultiplier = normalizeBudget(event.target.value);
    } else {
      state.budgetMultiplier = normalizeBudget(event.target.value);
      syncScenarioSelection();
    }
    renderAll();
  });

  document.getElementById("country-jump").addEventListener("click", handleCountryJump);
  document.getElementById("country-search").addEventListener("keydown", (event) => {
    if (event.key === "Enter") {
      event.preventDefault();
      handleCountryJump();
    }
  });

  document.getElementById("year-slider").addEventListener("input", (event) => {
    state.year = Number(event.target.value);
    document.getElementById("year-display").textContent = state.year;
    if (state.dimension === "dim5") {
      renderBubbleChart();
    } else {
      renderMap();
      renderCountryPanel();
      renderRankingList();
    }
    updateMapKicker();
  });

  document.getElementById("play-button").addEventListener("click", toggleAnimation);

  document.getElementById("spotlight-close").addEventListener("click", closeSpotlightModal);
  document.getElementById("spotlight-backdrop").addEventListener("click", closeSpotlightModal);

  document.addEventListener("keydown", (event) => {
    if (event.key === "Escape" && state.dialogOpen) {
      closeSpotlightModal();
      return;
    }
    if (event.key === "Tab" && state.dialogOpen) {
      trapDialogFocus(event);
    }
  });

  window.addEventListener(
    "resize",
    debounce(() => {
      ["map-chart", "detail-chart", "companion-chart", "spotlight-chart", "quadrant-chart"].forEach((id) => {
        const node = document.getElementById(id);
        if (node) {
          Plotly.Plots.resize(node);
        }
      });
    }, 120),
  );
}

function syncScenarioSelection() {
  const scenarios = store.optimizationScenarios;
  if (!scenarios.length) {
    state.scenarioId = "";
    return;
  }

  const exact = scenarios.find(
    (scenario) =>
      scenario.objective === normalizeObjective(state.objective) &&
      Math.abs(scenario.budget_multiplier - normalizeBudget(state.budgetMultiplier)) < 1e-9,
  );

  const sameObjective = scenarios.filter((scenario) => scenario.objective === normalizeObjective(state.objective));
  const pool = sameObjective.length ? sameObjective : scenarios;
  const chosen = exact ?? nearestScenario(pool, normalizeBudget(state.budgetMultiplier));

  state.scenarioId = chosen.scenario_id;
  state.objective = chosen.objective;
  state.budgetMultiplier = chosen.budget_multiplier;
}

function nearestScenario(scenarios, budgetMultiplier) {
  return [...scenarios].sort(
    (left, right) =>
      Math.abs(left.budget_multiplier - budgetMultiplier) -
      Math.abs(right.budget_multiplier - budgetMultiplier),
  )[0];
}

function populateCountryDatalist() {
  const datalist = document.getElementById("country-list");
  datalist.innerHTML = (store.overview.countries ?? [])
    .map((country) => `<option value="${escapeHtml(countryLabel(country))} (${country.iso3})"></option>`)
    .join("");
}

function handleCountryJump() {
  const input = document.getElementById("country-search").value.trim();
  if (!input) return;

  if (state.dimension === "dim4") {
    const match = resolveProvinceInput(input);
    if (match) {
      state.province = match;
      renderPanels();
      renderChinaMap();
    }
    return;
  }

  const iso3 = resolveCountryInput(safeLower(input));
  if (!iso3) return;

  state.country = iso3;
  renderPanels();
  updateMapHighlight(iso3);
  openSpotlightModal(iso3);
}

function resolveCountryInput(input) {
  if (store.countryLookup.has(input)) {
    return store.countryLookup.get(input);
  }

  const partial = (store.overview.countries ?? []).find((country) =>
    safeLower(country.country_name).includes(input),
  );
  return partial?.iso3 ?? null;
}

function renderAll() {
  syncControls();
  renderSummaryStrip();
  renderMap();
  renderPanels();
}

function syncControls() {
  document.querySelectorAll("[data-dimension]").forEach((button) => {
    button.classList.toggle("is-active", button.dataset.dimension === state.dimension);
  });

  const metricSelect = document.getElementById("metric-select");
  metricSelect.innerHTML = DIMENSIONS[state.dimension].metrics
    .map((metric) => `<option value="${metric}">${escapeHtml(METRIC_META[metric].label)}</option>`)
    .join("");
  metricSelect.value = state.metric;

  const riskField = document.getElementById("risk-field");
  riskField.style.display = state.dimension === "dim2" ? "grid" : "none";
  if (state.dimension === "dim2") {
    const riskSelect = document.getElementById("risk-select");
    riskSelect.innerHTML = (store.riskLatest.available_risks ?? [])
      .map(
        (risk) =>
          `<option value="${escapeHtml(risk.risk_code)}">${escapeHtml(translateRiskName(risk.risk_name))}</option>`,
      )
      .join("");
    riskSelect.value = state.risk;
  }

  const objectiveField = document.getElementById("objective-field");
  const budgetField = document.getElementById("budget-field");
  const showOptControls = state.dimension === "dim3" || state.dimension === "dim4";
  objectiveField.style.display = showOptControls ? "grid" : "none";
  budgetField.style.display = showOptControls ? "grid" : "none";

  if (state.dimension === "dim3") {
    const objectiveSelect = document.getElementById("objective-select");
    const budgetSelect = document.getElementById("budget-select");
    const objectives = uniqueValues(store.optimizationScenarios.map((scenario) => scenario.objective));
    const budgets = uniqueValues(
      store.optimizationScenarios.map((scenario) => scenario.budget_multiplier.toFixed(1)),
    ).map((value) => Number(value));

    objectiveSelect.innerHTML = objectives
      .map((objective) => `<option value="${objective}">${escapeHtml(objectiveLabel(objective))}</option>`)
      .join("");
    objectiveSelect.value = state.objective;

    budgetSelect.innerHTML = budgets
      .map(
        (budget) =>
          `<option value="${budget.toFixed(1)}">${escapeHtml(budgetLabel(budget))}</option>`,
      )
      .join("");
    budgetSelect.value = normalizeBudget(state.budgetMultiplier).toFixed(1);
  } else if (state.dimension === "dim4") {
    const objectiveSelect = document.getElementById("objective-select");
    const budgetSelect = document.getElementById("budget-select");
    const chinaScenarios = store.chinaOptimizationScenarios ?? [];
    const chinaObjectives = uniqueValues(chinaScenarios.map((s) => s.objective));
    const chinaBudgets = uniqueValues(
      chinaScenarios.map((s) => s.budget_multiplier.toFixed(1)),
    ).map((v) => Number(v));

    objectiveSelect.innerHTML = chinaObjectives
      .map((o) => `<option value="${o}">${escapeHtml(objectiveLabel(o))}</option>`)
      .join("");
    objectiveSelect.value = state.chinaObjective;

    budgetSelect.innerHTML = chinaBudgets
      .map((b) => `<option value="${b.toFixed(1)}">${escapeHtml(budgetLabel(b))}</option>`)
      .join("");
    budgetSelect.value = normalizeBudget(state.chinaBudgetMultiplier).toFixed(1);
  }

  // Year slider: visible for dim1 (timeseries) and dim5 (bubble animation)
  const sliderGroup = document.getElementById("year-slider-group");
  if (state.dimension === "dim1" && store.availableYears.length > 1) {
    sliderGroup.style.display = "flex";
    const slider = document.getElementById("year-slider");
    slider.min = store.availableYears[0];
    slider.max = store.availableYears[store.availableYears.length - 1];
    slider.value = state.year;
    document.getElementById("year-display").textContent = state.year;
  } else if (state.dimension === "dim5" && store.bubbleYears.length > 1) {
    sliderGroup.style.display = "flex";
    const slider = document.getElementById("year-slider");
    slider.min = store.bubbleYears[0];
    slider.max = store.bubbleYears[store.bubbleYears.length - 1];
    slider.value = state.year;
    document.getElementById("year-display").textContent = state.year;
  } else {
    sliderGroup.style.display = "none";
    if (state.animating) stopAnimation();
  }

  // Province search for dim4
  if (state.dimension === "dim4") {
    syncProvinceSearch();
  }

  document.getElementById("map-title").textContent = DIMENSIONS[state.dimension].mapTitle;
  document.getElementById("map-note").textContent = DIMENSIONS[state.dimension].note;
  document.getElementById("context-pill").textContent =
    state.dimension === "dim3" ? "情景引擎" :
    state.dimension === "dim4" ? "中国视角" : "静态构建";

  if ((state.dimension === "dim1" && store.availableYears.length) ||
      (state.dimension === "dim5" && store.bubbleYears.length)) {
    document.getElementById("map-kicker").textContent = `全球地图 \u00B7 ${state.year}`;
  } else {
    document.getElementById("map-kicker").textContent = "全球地图";
  }

  const currentScenario = getCurrentScenario();
  const controlNote =
    state.dimension === "dim3"
      ? `${currentScenario?.summary?.label ?? "优化情景"}：${
          OBJECTIVE_META[state.objective]?.note ?? ""
        }`
      : state.dimension === "dim4"
        ? "来自数据集5的中国大陆省级卫生资源数据。"
        : state.dimension === "dim5"
          ? "综合WHO GHO、UNDP HDI、世界银行WDI等外部数据源。"
          : "基于竞赛分析产出构建的静态仪表盘。";
  document.getElementById("control-note").textContent = controlNote;

  // Update search field label based on dimension
  const searchLabel = document.querySelector(".search-field > span");
  if (searchLabel) {
    searchLabel.textContent = state.dimension === "dim4" ? "定位省份" : "定位国家";
  }

  syncSearchField();
}

function syncSearchField() {
  if (state.dimension === "dim4") return;
  const searchInput = document.getElementById("country-search");
  searchInput.placeholder = "输入国家名称或三位国家代码";
  populateCountryDatalist();
  const country = store.overviewIndex.get(state.country);
  if (country) {
    searchInput.value = `${countryLabel(country)} (${country.iso3})`;
  }
}

function syncProvinceSearch() {
  const searchInput = document.getElementById("country-search");
  const datalist = document.getElementById("country-list");
  const provinces = store.chinaDeepDive?.provinces ?? [];
  searchInput.value = state.province ? provinceLabel(state.province) : "";
  searchInput.placeholder = "输入省份名称";
  datalist.innerHTML = provinces
    .map((p) => `<option value="${escapeHtml(provinceLabel(p.province ?? p))}"></option>`)
    .join("");
}

function renderSummaryStrip() {
  const summary = store.overview.summary ?? {};
  const scenario = getCurrentScenario();
  const tiles = [
    {
      value: formatShare(summary.dimension1?.global_ncd_share),
      label: "2023 全球非传染性疾病占比",
    },
    {
      value: escapeHtml(translateCountryName(summary.dimension1?.top_life_expectancy_country)),
      label: "最高预期寿命",
    },
    {
      value: escapeHtml(translateRiskName(summary.dimension2?.top_global_risk)),
      label: "首要全球风险因素",
    },
    state.dimension === "dim3"
      ? {
          value: budgetLabel(scenario?.budget_multiplier ?? 1),
          label: objectiveLabel(scenario?.objective ?? "max_output"),
        }
      : {
          value: escapeHtml(translateCountryName(summary.dimension3?.largest_shortage_country)),
          label: "最大资源缺口",
        },
  ];

  document.getElementById("summary-strip").innerHTML = tiles
    .map(
      (tile) =>
        `<article class="summary-tile"><strong>${tile.value}</strong><span>${escapeHtml(tile.label)}</span></article>`,
    )
    .join("");
}

function renderPanels() {
  const grid = document.querySelector(".dashboard-grid");
  grid?.classList.add("dim-fading");
  window.clearTimeout(renderPanels._timer);
  renderPanels._timer = window.setTimeout(() => {
    renderCountryPanel();
    renderRankingList();
    renderDetailChart();
    renderCompanionChart();
    renderContextPanel();
    if (state.dialogOpen) {
      renderSpotlightContent(state.dialogCountry || state.country);
    }
    grid?.classList.remove("dim-fading");
  }, 120);
}

function getCurrentScenario() {
  return store.scenarioIndex.get(state.scenarioId) ?? store.optimizationScenarios[0] ?? null;
}

function getScenarioRow(iso3) {
  const scenario = getCurrentScenario();
  return scenario?.allocationIndex?.get(iso3) ?? null;
}


function getMapRecords() {
  if (state.dimension === "dim4") {
    return [];
  }

  if (state.dimension === "dim5") {
    const records = (store.panorama?.countries ?? []).filter(
      (row) => METRIC_META[state.metric]?.accessor(row) != null,
    );
    return records;
  }

  if (state.dimension === "dim2") {
    return (store.riskLatest.risks ?? []).filter(
      (row) => row.risk_code === state.risk && METRIC_META[state.metric].accessor(row) != null,
    );
  }

  if (state.dimension === "dim3") {
    const scenarioIndex = getCurrentScenario()?.allocationIndex ?? new Map();
    return (store.overview.countries ?? [])
      .map((country) => ({ ...country, ...(scenarioIndex.get(country.iso3) ?? {}) }))
      .filter((row) => METRIC_META[state.metric].accessor(row) != null);
  }

  const latestYear = store.availableYears.length
    ? store.availableYears[store.availableYears.length - 1]
    : store.overview.latest_year;

  if (state.year !== latestYear && store.timeseries?.by_year?.[String(state.year)]) {
    return store.timeseries.by_year[String(state.year)].filter(
      (row) => METRIC_META[state.metric].accessor(row) != null,
    );
  }

  return (store.overview.countries ?? []).filter(
    (row) => METRIC_META[state.metric].accessor(row) != null,
  );
}

function renderMap() {
  if (state.dimension === "dim4") {
    renderChinaMap();
    return;
  }

  const metric = METRIC_META[state.metric];
  const records = getMapRecords();
  const values = records.map((row) => metric.accessor(row));
  const bounds = getScaleBounds(values, metric.diverging);
  const selected = records.find((row) => row.iso3 === state.country);

  Plotly.react(
    "map-chart",
    [
      {
        type: "choropleth",
        locationmode: "ISO-3",
        locations: records.map((row) => row.iso3),
        z: values,
        text: records.map((row) => countryLabel(row)),
        hovertext: records.map((row) => buildHoverText(row)),
        hovertemplate: "%{hovertext}<extra></extra>",
        colorscale: metric.colorscale,
        zmin: bounds.zmin,
        zmax: bounds.zmax,
        zmid: bounds.zmid,
        marker: {
          line: {
            color: records.map((row) =>
              row.iso3 === state.country ? "rgba(34,211,238,0.72)" : "rgba(148,163,184,0.18)",
            ),
            width: records.map((row) => (row.iso3 === state.country ? 2 : 0.4)),
          },
        },
        colorbar: {
          title: metric.label,
          thickness: 12,
          len: 0.68,
          x: 0.02,
          xanchor: "left",
          tickfont: { family: "SFMono-Regular, ui-monospace, monospace", size: 11, color: THEME.muted },
          titlefont: { family: "system-ui, sans-serif", size: 12, color: THEME.muted },
          outlinewidth: 0,
        },
      },
      {
        type: "choropleth",
        locationmode: "ISO-3",
        locations: selected ? [selected.iso3] : [],
        z: selected && metric.accessor(selected) != null ? [metric.accessor(selected)] : [],
        text: selected ? [countryLabel(selected)] : [],
        hoverinfo: "skip",
        showscale: false,
        colorscale: metric.colorscale,
        zmin: bounds.zmin,
        zmax: bounds.zmax,
        zmid: bounds.zmid,
        marker: {
          line: { color: "rgba(34,211,238,0.95)", width: 3 },
        },
      },
    ],
    {
      paper_bgcolor: "rgba(0,0,0,0)",
      plot_bgcolor: "rgba(0,0,0,0)",
      margin: { l: 0, r: 0, t: 0, b: 0 },
      geo: {
        projection: { type: "natural earth", scale: 1.06 },
        showframe: false,
        showcountries: true,
        countrycolor: "rgba(148,163,184,0.18)",
        showcoastlines: false,
        landcolor: "rgba(30,41,59,0.92)",
        bgcolor: "rgba(0,0,0,0)",
      },
      font: { family: "system-ui, sans-serif", color: THEME.ink },
      hoverlabel: {
        bgcolor: THEME.hover,
        bordercolor: "rgba(34,211,238,0.22)",
        font: { family: "system-ui, sans-serif", color: THEME.inkBright, size: 13 },
      },
    },
    {
      responsive: true,
      displayModeBar: false,
      scrollZoom: false,
    },
  );

  const mapNode = document.getElementById("map-chart");
  if (!mapNode.dataset.bound) {
    mapNode.on("plotly_click", (event) => {
      if (state.dimension === "dim4") return;
      const iso3 = event?.points?.[0]?.location;
      if (!iso3) {
        return;
      }
      state.country = iso3;
      renderPanels();
      updateMapHighlight(iso3);
      openSpotlightModal(iso3);
    });
    mapNode.dataset.bound = "1";
  }
}

function getCurrentChinaScenario() {
  const id = `${state.chinaObjective}_budget_${String(Math.round(state.chinaBudgetMultiplier * 100)).padStart(3, "0")}`;
  return store.chinaScenarioIndex.get(id) ?? store.chinaOptimizationScenarios[0] ?? null;
}

function getChinaProvinceRow(province) {
  return store.chinaProvinceIndex.get(province) ?? null;
}

function renderChinaProvinceBar() {
  renderChinaMap();
}

function renderChinaMap() {
  const data = store.chinaDeepDive;
  const geojson = store.chinaProvinces;

  if (!data?.provinces?.length || !geojson?.features) {
    emptyPlot("map-chart", "暂无中国大陆省级数据。");
    return;
  }

  const metric = METRIC_META[state.metric] ?? METRIC_META["prov_gap"];
  const isOptMetric = state.metric === "prov_optimization_change";

  // Build province → value mapping
  let provinceValues = {};
  if (isOptMetric) {
    const sc = getCurrentChinaScenario();
    for (const row of sc?.allocation ?? []) {
      provinceValues[row.province] = row.change_pct;
    }
  } else {
    for (const prov of data.provinces) {
      provinceValues[prov.province] = metric.accessor(prov);
    }
  }

  const locations = [];
  const z = [];
  const hovertext = [];
  const customdata = [];

  for (const feature of geojson.features) {
    const name = feature.properties?.name;
    if (!name || name === "") continue;
    const val = provinceValues[name];
    if (val == null) continue;
    const provData = store.chinaProvinceIndex.get(name) ?? {};
    locations.push(name);
    z.push(val);
    customdata.push(name);
    hovertext.push(
      `<b>${name}</b><br>` +
      `地区：${provData.region ?? ""}（${provData.region_en ?? ""}）<br>` +
      `${metric.label}：${metric.formatter(val)}<br>` +
      `类型：${provData.quadrant ?? "—"}<br>` +
      `预期寿命：${provData.life_expectancy != null ? provData.life_expectancy.toFixed(1) + " 岁" : "暂无"}`
    );
  }

  const allVals = z.filter((v) => v != null && isFinite(v));
  const isDivergent = metric.diverging || isOptMetric;
  const absMax = isDivergent ? Math.max(Math.abs(Math.min(...allVals)), Math.abs(Math.max(...allVals))) : null;
  const zmin = isDivergent ? -absMax : Math.min(...allVals);
  const zmax = isDivergent ? absMax : Math.max(...allVals);

  Plotly.react(
    "map-chart",
    [
      {
        type: "choropleth",
        geojson: geojson,
        locations: locations,
        z: z,
        featureidkey: "properties.name",
        text: hovertext,
        hovertemplate: "%{text}<extra></extra>",
        customdata: customdata,
        colorscale: metric.colorscale,
        zmin: zmin,
        zmax: zmax,
        zmid: isDivergent ? 0 : undefined,
        marker: {
          line: {
            color: locations.map((n) => n === state.province ? "rgba(251,191,36,0.95)" : "rgba(148,163,184,0.25)"),
            width: locations.map((n) => n === state.province ? 2.5 : 0.5),
          },
        },
        colorbar: {
          title: metric.label,
          thickness: 12,
          len: 0.72,
          x: 0.02,
          xanchor: "left",
          tickfont: { family: "SFMono-Regular, ui-monospace, monospace", size: 11, color: THEME.muted },
          titlefont: { family: "system-ui, sans-serif", size: 12, color: THEME.muted },
          outlinewidth: 0,
        },
      },
    ],
    {
      paper_bgcolor: "rgba(0,0,0,0)",
      plot_bgcolor: "rgba(0,0,0,0)",
      margin: { l: 0, r: 0, t: 4, b: 0 },
      geo: {
        scope: "asia",
        fitbounds: "geojson",
        resolution: 50,
        showframe: false,
        showcoastlines: true,
        coastlinecolor: "rgba(148,163,184,0.2)",
        showland: true,
        landcolor: "rgba(15,23,42,0.85)",
        showocean: true,
        oceancolor: "rgba(15,23,42,0.5)",
        showcountries: true,
        countrycolor: "rgba(148,163,184,0.15)",
        bgcolor: "rgba(0,0,0,0)",
        showlakes: false,
        projection: { type: "mercator" },
        center: { lon: 104, lat: 35 },
        lonaxis: { range: [72, 140] },
        lataxis: { range: [15, 55] },
      },
    },
    { responsive: true, displayModeBar: false, scrollZoom: false },
  );

  const mapNode = document.getElementById("map-chart");
  if (!mapNode.dataset.dim4Bound) {
    mapNode.on("plotly_click", (event) => {
      if (state.dimension !== "dim4") return;
      const province = event?.points?.[0]?.customdata;
      if (province) {
        state.province = province;
        renderPanels();
        renderChinaMap();
      }
    });
    mapNode.dataset.dim4Bound = "1";
  }
}

function updateMapHighlight(iso3) {
  const mapNode = document.getElementById("map-chart");
  const records = getMapRecords();
  const metric = METRIC_META[state.metric];
  const selected = records.find((row) => row.iso3 === iso3);
  if (!mapNode?.data?.length) {
    return;
  }

  Plotly.restyle(
    mapNode,
    {
      "marker.line.color": [
        records.map((row) =>
          row.iso3 === iso3 ? "rgba(34,211,238,0.72)" : "rgba(148,163,184,0.18)",
        ),
      ],
      "marker.line.width": [records.map((row) => (row.iso3 === iso3 ? 2 : 0.4))],
    },
    [0],
  );

  Plotly.restyle(
    mapNode,
    {
      locations: [selected ? [selected.iso3] : []],
      z: [selected && metric.accessor(selected) != null ? [metric.accessor(selected)] : []],
      text: [selected ? [countryLabel(selected)] : []],
    },
    [1],
  );
}

function buildHoverText(row) {
  if (state.dimension === "dim2") {
    return [
      `<b>${escapeHtml(countryLabel(row))}</b>`,
      `地区：${escapeHtml(regionLabel(row.who_region))} / ${escapeHtml(incomeLabel(row.wb_income))}`,
      `风险：${escapeHtml(translateRiskName(row.risk_name ?? getRiskName(state.risk)))}`,
      `${METRIC_META[state.metric].label}: ${escapeHtml(
        METRIC_META[state.metric].formatter(METRIC_META[state.metric].accessor(row)),
      )}`,
      `风险致死：${escapeHtml(formatCompact(row.attributable_deaths))}`,
    ].join("<br>");
  }

  if (state.dimension === "dim3") {
    const scenario = getCurrentScenario();
    return [
      `<b>${escapeHtml(countryLabel(row))}</b>`,
      `地区：${escapeHtml(regionLabel(row.who_region))} / ${escapeHtml(incomeLabel(row.wb_income))}`,
      `${METRIC_META[state.metric].label}: ${escapeHtml(
        METRIC_META[state.metric].formatter(METRIC_META[state.metric].accessor(row)),
      )}`,
      `情景：${escapeHtml(scenario?.summary?.label ?? NO_DATA_LABEL)}`,
      `缺口：${escapeHtml(formatSigned(row.gap))}`,
      `效率：${escapeHtml(formatSigned(row.efficiency))}`,
    ].join("<br>");
  }

  if (state.dimension === "dim5") {
    return [
      `<b>${escapeHtml(countryLabel(row))}</b>`,
      `${METRIC_META[state.metric].label}: ${escapeHtml(
        METRIC_META[state.metric].formatter(METRIC_META[state.metric].accessor(row)),
      )}`,
      row.hdi != null ? `HDI: ${row.hdi}` : "",
      row.hale != null ? `HALE: ${row.hale} 岁` : "",
    ].filter(Boolean).join("<br>");
  }

  return [
    `<b>${escapeHtml(countryLabel(row))}</b>`,
    `地区：${escapeHtml(regionLabel(row.who_region))} / ${escapeHtml(incomeLabel(row.wb_income))}`,
    `${METRIC_META[state.metric].label}: ${escapeHtml(
      METRIC_META[state.metric].formatter(METRIC_META[state.metric].accessor(row)),
    )}`,
    `首要风险：${escapeHtml(translateRiskName(row.top_risk_name))}`,
    `首要风险占比：${escapeHtml(formatShare(row.top_risk_share))}`,
  ].join("<br>");
}

function renderCountryPanel() {
  const profile = store.profiles[state.country];
  const latest = profile?.latest ?? {};
  const meta = profile?.meta ?? {};
  const scenarioRow = getScenarioRow(state.country);

  document.getElementById("country-title").textContent = countryLabel(meta) || state.country;
  document.getElementById("country-tag").textContent = `${regionLabel(meta.who_region)} / ${
    incomeLabel(meta.wb_income)
  }`;

  const title = document.getElementById("country-title");
  title.classList.remove("flash");
  void title.offsetWidth;
  title.classList.add("flash");

  let items = [];
  if (state.dimension === "dim1") {
    const yearRecord = getMapRecords().find((r) => r.iso3 === state.country) ?? latest;
    items = [
      ["预期寿命", METRIC_META.life_expectancy.formatter(yearRecord.life_expectancy), "cyan"],
      ["传染性疾病占比", formatShare(yearRecord.communicable_share), "amber"],
      ["非传染性疾病占比", formatShare(yearRecord.ncd_share), "violet"],
      ["人均国内生产总值", formatCurrency(yearRecord.gdp_per_capita ?? latest.gdp_per_capita), "teal"],
      ["卫生支出占GDP比重", formatPercentValue(yearRecord.health_exp_pct_gdp), "blue"],
      ["首要风险", translateRiskName(yearRecord.top_risk_name ?? latest.top_risk_name), "rose"],
    ];
  } else if (state.dimension === "dim2") {
    const selectedRisk = store.riskIndex.get(`${state.country}|${state.risk}`) ?? {};
    items = [
      ["首要风险", translateRiskName(latest.top_risk_name), "cyan"],
      ["首要风险占比", formatShare(latest.top_risk_share), "teal"],
      ["首要风险致死", formatCompact(latest.top_risk_deaths), "rose"],
      ["当前风险", translateRiskName(selectedRisk.risk_name ?? getRiskName(state.risk)), "violet"],
      ["当前风险占比", formatShare(selectedRisk.share), "amber"],
      ["当前风险致死", formatCompact(selectedRisk.attributable_deaths), "blue"],
    ];
  } else if (state.dimension === "dim5") {
    const pano = store.panoramaIndex.get(state.country) ?? {};
    items = [
      ["人类发展指数", pano.hdi != null ? Number(pano.hdi).toFixed(3) : NO_DATA_LABEL, "emerald"],
      ["健康预期寿命", pano.hale != null ? `${pano.hale} 岁` : NO_DATA_LABEL, "cyan"],
      ["UHC 覆盖指数", pano.uhc_index != null ? String(pano.uhc_index) : NO_DATA_LABEL, "violet"],
      ["PM2.5 暴露", pano.pm25 != null ? `${pano.pm25} μg/m³` : NO_DATA_LABEL, "amber"],
      ["医生密度", pano.doctor_density != null ? `${pano.doctor_density}/万人` : NO_DATA_LABEL, "teal"],
      ["人均卫生支出", formatCurrency(pano.che_per_capita), "blue"],
    ];
  } else if (state.dimension === "dim4") {
    const chinaData = store.chinaDeepDive;
    const provinces = chinaData?.provinces ?? [];
    const prov = state.province || (provinces[0]?.province ?? "");
    const provData = store.chinaProvinceIndex.get(prov) ?? {};
    const chinaScenario = getCurrentChinaScenario();
    const optRow = (chinaScenario?.allocation ?? []).find((r) => r.province === prov) ?? {};

    document.getElementById("country-title").textContent = prov || "选择省份";
    document.getElementById("country-tag").textContent = `${provData.region ?? "中国"} · ${provData.region_en ?? ""}`;
    items = [
      ["象限类型", provData.quadrant ?? NO_DATA_LABEL, "rose"],
      ["资源缺口", formatSigned(provData.gap), "teal"],
      ["资源效率", formatSigned(provData.efficiency), "violet"],
      ["预期寿命", provData.life_expectancy != null ? `${provData.life_expectancy.toFixed(1)} 岁` : NO_DATA_LABEL, "cyan"],
      ["婴儿死亡率", provData.infant_mortality != null ? `${provData.infant_mortality.toFixed(1)} ‰` : NO_DATA_LABEL, "amber"],
      ["卫生人员密度", provData.personnel_per_1000 != null ? `${provData.personnel_per_1000.toFixed(1)}/千人` : NO_DATA_LABEL, "blue"],
      ["执业医师密度", provData.physicians_per_1000 != null ? `${provData.physicians_per_1000.toFixed(2)}/千人` : NO_DATA_LABEL, "violet"],
      ["医院床位密度", provData.hospital_beds_per_1000 != null ? `${provData.hospital_beds_per_1000.toFixed(2)}/千人` : NO_DATA_LABEL, "teal"],
      ["人均卫生支出", provData.health_exp_per_capita != null ? `¥${Math.round(provData.health_exp_per_capita).toLocaleString()}` : NO_DATA_LABEL, "cyan"],
      ["人均GDP", provData.gdp_per_capita != null ? `¥${Math.round(provData.gdp_per_capita).toLocaleString()}` : NO_DATA_LABEL, "teal"],
      ["优化调整", optRow.change_pct != null ? `${optRow.change_pct > 0 ? "+" : ""}${optRow.change_pct.toFixed(1)}%` : NO_DATA_LABEL, "amber"],
    ];
  } else {
    items = [
      ["优化目标", objectiveLabel(state.objective), "cyan"],
      ["当前支出", formatCurrency(scenarioRow?.current ?? latest.current), "teal"],
      ["最优方案", formatCurrency(scenarioRow?.optimal ?? latest.optimal), "blue"],
      ["建议调整", formatSignedPercent(scenarioRow?.change_pct ?? latest.change_pct), "violet"],
      ["资源缺口", formatSigned(latest.gap), "rose"],
      ["效率", formatSigned(latest.efficiency), "amber"],
    ];
  }

  document.getElementById("country-metrics").innerHTML = items
    .map(
      ([label, value, accent]) =>
        `<article class="metric-tile" data-accent="${accent}"><span>${escapeHtml(
          label,
        )}</span><strong>${escapeHtml(value)}</strong></article>`,
    )
    .join("");
}

function renderRankingList() {
  if (state.dimension === "dim4") {
    renderDim4RankingList();
    return;
  }

  const metric = METRIC_META[state.metric];
  const rows = [...getMapRecords()];
  const descending = !(state.dimension === "dim3" && state.metric === "gap");
  rows.sort((left, right) => {
    const leftValue = metric.accessor(left);
    const rightValue = metric.accessor(right);
    if (descending) {
      return (rightValue ?? -Infinity) - (leftValue ?? -Infinity);
    }
    return (leftValue ?? Infinity) - (rightValue ?? Infinity);
  });

  let caption = "按当前地图指标排序";
  if (state.dimension === "dim2") {
    caption = `${getRiskName(state.risk)} | ${metric.label}`;
  } else if (state.dimension === "dim3" && state.metric === "change_pct") {
    caption = `${objectiveLabel(state.objective)} | ${budgetLabel(state.budgetMultiplier)}`;
  } else if (state.dimension === "dim3" && state.metric === "gap") {
    caption = "最严重短缺";
  }
  document.getElementById("ranking-caption").textContent = caption;

  const topRows = rows.slice(0, 10);
  const maxValue = Math.max(...topRows.map((row) => Math.abs(metric.accessor(row) ?? 0)), 1e-9);
  document.getElementById("ranking-list").innerHTML = topRows
    .map((row, index) => {
      const progress = Math.round((Math.abs(metric.accessor(row) ?? 0) / maxValue) * 100);
      return `
        <button
          class="ranking-row ${row.iso3 === state.country ? "is-selected" : ""}"
          data-country="${escapeHtml(row.iso3)}"
          data-rank="${index + 1}"
          style="--progress:${progress}%;animation-delay:${index * 45}ms"
          type="button"
        >
          <span class="rank-badge">${index + 1}</span>
          <span class="row-info">
            <b>${escapeHtml(countryLabel(row))}</b>
            <small>${escapeHtml(row.who_region ? regionLabel(row.who_region) : (row.region || "")) } / ${escapeHtml(row.wb_income ? incomeLabel(row.wb_income) : (row.subregion || ""))}</small>
          </span>
          <span class="row-value">${escapeHtml(metric.formatter(metric.accessor(row)))}</span>
        </button>
      `;
    })
    .join("");

  document.querySelectorAll(".ranking-row").forEach((button) => {
    button.addEventListener("click", () => {
      state.country = button.dataset.country;
      renderPanels();
      updateMapHighlight(button.dataset.country);
      openSpotlightModal(button.dataset.country);
    });
  });
}

function renderDim4RankingList() {
  const data = store.chinaDeepDive;
  const provinces = data?.provinces ?? [];
  const metric = METRIC_META[state.metric] ?? METRIC_META["prov_gap"];

  // Build sortable rows from province data
  const rows = provinces
    .map((p) => ({ province: p.province, value: metric.accessor(p) }))
    .filter((r) => r.value != null && isFinite(r.value))
    .sort((a, b) => b.value - a.value)
    .slice(0, 12);

  const maxAbs = rows.length ? Math.max(...rows.map((r) => Math.abs(r.value)), 1) : 1;
  document.getElementById("ranking-caption").textContent = `${metric.label} | 省级排名`;

  document.getElementById("ranking-list").innerHTML = rows
    .map((row, index) => {
      const progress = Math.round((Math.abs(row.value) / maxAbs) * 100);
      const accent = metric.diverging
        ? row.value >= 0 ? "style='--bar-color:rgba(34,211,238,0.5)'" : "style='--bar-color:rgba(251,113,133,0.5)'"
        : "";
      return `
        <button
          class="ranking-row ${row.province === state.province ? "is-selected" : ""}"
          data-province="${escapeHtml(row.province)}"
          data-rank="${index + 1}"
          style="--progress:${progress}%;animation-delay:${index * 45}ms"
          type="button"
        >
          <span class="rank-badge">${index + 1}</span>
          <span class="row-info">
            <b>${escapeHtml(row.province)}</b>
            <small>${escapeHtml(store.chinaProvinceIndex.get(row.province)?.region ?? "中国大陆")}</small>
          </span>
          <span class="row-value">${escapeHtml(metric.formatter(row.value))}</span>
        </button>
      `;
    })
    .join("");

  document.querySelectorAll(".ranking-row[data-province]").forEach((button) => {
    button.addEventListener("click", () => {
      state.province = button.dataset.province;
      renderPanels();
      renderChinaMap();
    });
  });
}

function renderChinaOptimizationDetail() {
  const sc = getCurrentChinaScenario();
  if (!sc?.allocation?.length) {
    emptyPlot("detail-chart", "暂无省级优化数据。请确认数据已加载。");
    return;
  }

  const rows = [...sc.allocation]
    .filter((r) => r.change_pct != null)
    .sort((a, b) => b.change_pct - a.change_pct);

  const selectedProv = state.province;

  Plotly.react(
    "detail-chart",
    [
      {
        type: "bar",
        x: rows.map((r) => r.change_pct),
        y: rows.map((r) => r.province),
        customdata: rows.map((r) => r.province),
        orientation: "h",
        marker: {
          color: rows.map((r) =>
            r.province === selectedProv
              ? THEME.amber
              : r.change_pct >= 0
              ? "rgba(34,211,238,0.65)"
              : "rgba(251,113,133,0.55)"
          ),
          cornerradius: 4,
          line: { width: 0 },
        },
        hovertemplate: "<b>%{y}</b><br>调整幅度：%{x:.1f}%<extra></extra>",
      },
    ],
    {
      ...baseLayout({
        xaxis: { title: "建议调整幅度（%）", zeroline: true, zerolinecolor: "rgba(148,163,184,0.3)" },
        yaxis: { automargin: true, dtick: 1 },
        margin: { l: 110, r: 24, t: 8, b: 42 },
      }),
      height: Math.max(400, rows.length * 20),
    },
    { responsive: true, displayModeBar: false, scrollZoom: false },
  );

  const node = document.getElementById("detail-chart");
  if (!node.dataset.chinaOptBound) {
    node.on("plotly_click", (event) => {
      if (state.dimension !== "dim4") return;
      const prov = event?.points?.[0]?.customdata;
      if (prov) {
        state.province = prov;
        renderPanels();
        renderChinaMap();
      }
    });
    node.dataset.chinaOptBound = "1";
  }
}

function renderDetailChart() {
  const profile = store.profiles[state.country];

  if (state.dimension === "dim4") {
    document.getElementById("detail-title").textContent = "省级优化方案对比";
    document.getElementById("detail-pill").textContent = state.province || "省级资源调整";
    renderChinaOptimizationDetail();
    return;
  }

  if (!profile) {
    emptyPlot("detail-chart", "暂无国家概况数据。");
    return;
  }

  if (state.dimension === "dim1") {
    document.getElementById("detail-title").textContent = "健康结果与疾病结构";
    document.getElementById("detail-pill").textContent = "预期寿命与疾病占比";
    renderDimension1Detail(profile);
    return;
  }

  if (state.dimension === "dim2") {
    document.getElementById("detail-title").textContent = "最新风险构成";
    document.getElementById("detail-pill").textContent = "主要风险因素";
    renderDimension2Detail(profile);
    return;
  }

  if (state.dimension === "dim5") {
    document.getElementById("detail-title").textContent = "健康雷达对比";
    document.getElementById("detail-pill").textContent = "国家与全球对比";
    renderRadarChart();
    return;
  }

  document.getElementById("detail-title").textContent = "国家资源分析";
  document.getElementById("detail-pill").textContent = "历史支出与优化目标";
  renderDimension3Detail(profile);
}

function renderDimension1Detail(profile) {
  const trend = profile.trend ?? [];
  if (!trend.length) {
    emptyPlot("detail-chart", "暂无历史趋势数据。");
    return;
  }

  Plotly.react(
    "detail-chart",
    [
      {
        x: trend.map((row) => row.year),
        y: trend.map((row) => row.life_expectancy),
        name: "预期寿命",
        mode: "lines+markers",
        line: { color: THEME.cyan, width: 3, shape: "spline" },
        marker: { size: 6, color: THEME.cyan },
        fill: "tozeroy",
        fillcolor: "rgba(34,211,238,0.08)",
      },
      {
        x: trend.map((row) => row.year),
        y: trend.map((row) => percentValue(row.communicable_share)),
        name: "传染性疾病",
        mode: "lines",
        yaxis: "y2",
        line: { color: THEME.amber, width: 2.5, shape: "spline" },
      },
      {
        x: trend.map((row) => row.year),
        y: trend.map((row) => percentValue(row.ncd_share)),
        name: "非传染性疾病",
        mode: "lines",
        yaxis: "y2",
        line: { color: THEME.violet, width: 2.5, shape: "spline" },
      },
    ],
    baseLayout({
      yaxis: { title: "预期寿命（岁）" },
      yaxis2: {
        overlaying: "y",
        side: "right",
        title: "占比 (%)",
        gridcolor: "rgba(0,0,0,0)",
      },
    }),
    { responsive: true, displayModeBar: false, scrollZoom: false },
  );
}

function renderDimension2Detail(profile) {
  const risks = [...(profile.latest_risks ?? [])].slice(0, 6).reverse();
  if (!risks.length) {
    emptyPlot("detail-chart", "暂无风险因素记录。");
    return;
  }

  Plotly.react(
    "detail-chart",
    [
      {
        type: "bar",
        x: risks.map((row) => percentValue(row.share)),
        y: risks.map((row) => translateRiskName(row.risk_name)),
        orientation: "h",
        marker: {
          color: risks.map((_, index) => colorFromPalette(index)),
          cornerradius: 6,
          line: { width: 0 },
        },
        customdata: risks.map((row) => row.attributable_deaths),
        hovertemplate: "<b>%{y}</b><br>占比: %{x:.2f}%<br>风险致死: %{customdata:.0f}<extra></extra>",
      },
    ],
    baseLayout({
      xaxis: { title: "占比 (%)" },
      yaxis: { automargin: true },
    }),
    { responsive: true, displayModeBar: false, scrollZoom: false },
  );
}

function renderDimension3Detail(profile) {
  const trend = profile.trend ?? [];
  const scenarioRow = getScenarioRow(state.country);
  const latest = profile.latest ?? {};
  const currentValue = scenarioRow?.current ?? latest.current ?? latest.health_exp_per_capita;
  const optimalValue = scenarioRow?.optimal ?? latest.optimal;

  if (!trend.length && currentValue == null && optimalValue == null) {
    emptyPlot("detail-chart", "该国暂无分配数据。");
    return;
  }

  const traces = [];
  if (trend.length) {
    traces.push({
      x: trend.map((row) => row.year),
      y: trend.map((row) => row.health_exp_per_capita),
      name: "历史人均支出",
      mode: "lines+markers",
      line: { color: THEME.teal, width: 3, shape: "spline" },
      marker: { size: 5, color: THEME.teal },
    });
  }

  if (optimalValue != null && trend.length) {
    traces.push({
      x: trend.map((row) => row.year),
      y: trend.map(() => optimalValue),
      name: "优化目标",
      mode: "lines",
      line: { color: THEME.blue, width: 2, dash: "dash" },
    });
  }

  if (currentValue != null && optimalValue != null) {
    traces.push({
      type: "bar",
      x: ["当前", "优化目标"],
      y: [currentValue, optimalValue],
      name: "当前与目标",
      marker: {
        color: [THEME.violet, THEME.cyan],
        line: { width: 0 },
      },
      opacity: 0.34,
      yaxis: trend.length ? "y3" : "y",
      hovertemplate: "<b>%{x}</b><br>%{y:,.0f} 美元<extra></extra>",
    });
  }

  const layout = trend.length
    ? baseLayout({
        yaxis: { title: "人均美元" },
        yaxis3: {
          overlaying: "y",
          side: "right",
          title: "当前与目标",
          showgrid: false,
        },
      })
    : baseLayout({
        yaxis: { title: "人均美元" },
      });

  Plotly.react("detail-chart", traces, layout, {
    responsive: true,
    displayModeBar: false,
    scrollZoom: false,
  });
}

function renderChinaDetailChart() {
  const data = store.chinaDeepDive;
  const prov = state.province || (data?.provinces?.[0] ?? "");
  const metricKey = state.metric === "health_institutions" ? "health_institutions" : "health_personnel";
  const series = data?.[metricKey]?.[prov] ?? [];

  if (!series.length) {
    emptyPlot("detail-chart", prov ? `暂无 ${provinceLabel(prov)} 的数据。` : "选择省份以查看趋势。");
    return;
  }

  Plotly.react(
    "detail-chart",
    [
      {
        x: series.map((r) => r.year),
        y: series.map((r) => r.value),
        name: provinceLabel(prov),
        mode: "lines+markers",
        line: { color: "#f87171", width: 3, shape: "spline" },
        marker: { size: 6, color: "#f87171" },
        fill: "tozeroy",
        fillcolor: "rgba(248, 113, 113, 0.08)",
      },
    ],
    baseLayout({
      yaxis: { title: METRIC_META[metricKey].label },
    }),
    { responsive: true, displayModeBar: false, scrollZoom: false },
  );
}

function renderCompanionChart() {
  if (state.dimension === "dim1") {
    const toggleHtml = `<span class="companion-toggle" id="companion-toggle">` +
      `<button class="companion-toggle-btn ${state.companionView === "transition" ? "is-active" : ""}" data-view="transition">趋势</button>` +
      `<button class="companion-toggle-btn ${state.companionView === "equity" ? "is-active" : ""}" data-view="equity">公平</button>` +
      `</span>`;
    document.getElementById("companion-title").innerHTML =
      state.companionView === "equity" ? `健康公平趋势${toggleHtml}` : `全球疾病趋势${toggleHtml}`;
    document.getElementById("companion-pill").textContent =
      state.companionView === "equity" ? "基尼系数与离散度" : "2000-2023";

    // Bind toggle
    document.querySelectorAll(".companion-toggle-btn").forEach((btn) => {
      btn.addEventListener("click", () => {
        state.companionView = btn.dataset.view;
        renderCompanionChart();
      });
    });

    if (state.companionView === "equity") {
      renderEquityChart();
    } else {
      renderGlobalDiseaseTrend();
    }
    return;
  }

  if (state.dimension === "dim2") {
    document.getElementById("companion-title").textContent = "风险-地区流向";
    document.getElementById("companion-pill").textContent = "桑基图概览";
    renderRiskSankey();
    return;
  }

  if (state.dimension === "dim4") {
    document.getElementById("companion-title").textContent = "省份卫生人员趋势";
    document.getElementById("companion-pill").textContent = state.province || "选择省份";
    renderChinaProvincePersonnelTrend();
    return;
  }

  if (state.dimension === "dim5") {
    document.getElementById("companion-title").textContent = "发展-健康气泡图";
    document.getElementById("companion-pill").textContent = `${state.year} 年`;
    renderBubbleChart();
    return;
  }

  const dim3ToggleHtml = `<span class="companion-toggle" id="companion-toggle">` +
    `<button class="companion-toggle-btn ${state.companionView !== "equity" ? "is-active" : ""}" data-view="reallocation">重分配</button>` +
    `<button class="companion-toggle-btn ${state.companionView === "equity" ? "is-active" : ""}" data-view="equity">公平</button>` +
    `</span>`;
  document.getElementById("companion-title").innerHTML =
    state.companionView === "equity" ? `全球健康公平趋势${dim3ToggleHtml}` : `情景赢家与捐助者${dim3ToggleHtml}`;
  document.getElementById("companion-pill").textContent =
    state.companionView === "equity" ? "基尼系数" : budgetLabel(state.budgetMultiplier);
  document.querySelectorAll(".companion-toggle-btn").forEach((btn) => {
    btn.addEventListener("click", () => {
      state.companionView = btn.dataset.view;
      renderCompanionChart();
    });
  });
  if (state.companionView === "equity") {
    renderEquityChart();
  } else {
    renderOptimizationBar();
  }
}

function renderGlobalDiseaseTrend() {
  const trend = store.globalStory.global_disease_trends ?? [];
  if (!trend.length) {
    emptyPlot("companion-chart", "暂无全球趋势数据。");
    return;
  }

  Plotly.react(
    "companion-chart",
    [
      {
        x: trend.map((row) => row.year),
        y: trend.map((row) => row.communicable_share),
        name: "传染性疾病",
        mode: "lines",
        line: { color: THEME.amber, width: 0, shape: "spline" },
        fill: "tonexty",
        fillcolor: "rgba(251, 191, 36, 0.35)",
        stackgroup: "share",
        hovertemplate: "<b>传染性疾病</b><br>%{x}: %{y:.1%}<extra></extra>",
      },
      {
        x: trend.map((row) => row.year),
        y: trend.map((row) => row.ncd_share),
        name: "非传染性疾病",
        mode: "lines",
        line: { color: THEME.teal, width: 0, shape: "spline" },
        fill: "tonexty",
        fillcolor: "rgba(45, 212, 191, 0.35)",
        stackgroup: "share",
        hovertemplate: "<b>非传染性疾病</b><br>%{x}: %{y:.1%}<extra></extra>",
      },
      {
        x: trend.map((row) => row.year),
        y: trend.map((row) => row.injury_share),
        name: "伤害",
        mode: "lines",
        line: { color: THEME.rose, width: 0, shape: "spline" },
        fill: "tonexty",
        fillcolor: "rgba(251, 113, 133, 0.35)",
        stackgroup: "share",
        hovertemplate: "<b>伤害</b><br>%{x}: %{y:.1%}<extra></extra>",
      },
    ],
    baseLayout({
      yaxis: { title: "全球死亡占比", tickformat: ".0%", range: [0, 1] },
    }),
    { responsive: true, displayModeBar: false, scrollZoom: false },
  );
}

function renderRiskSankey() {
  const sankey = store.globalStory.sankey;
  if (!sankey?.nodes?.length) {
    emptyPlot("companion-chart", "暂无桑基图数据。");
    return;
  }

  Plotly.react(
    "companion-chart",
    [
      {
        type: "sankey",
        arrangement: "snap",
        node: {
          label: sankey.nodes.map((node) => translateSankeyNode(node)),
          pad: 16,
          thickness: 18,
          line: { color: "rgba(148,163,184,0.12)", width: 0.5 },
          color: sankey.nodes.map((node) =>
            REGION_LABELS[node]
              ? "rgba(167,139,250,0.72)"
              : "rgba(34,211,238,0.72)",
          ),
        },
        link: {
          source: sankey.sources,
          target: sankey.targets,
          value: sankey.values,
          color: "rgba(148,163,184,0.10)",
        },
        hoverlabel: {
          bgcolor: THEME.hover,
          bordercolor: "rgba(34,211,238,0.18)",
          font: { family: "system-ui, sans-serif", color: THEME.inkBright },
        },
      },
    ],
    baseLayout({
      margin: { l: 12, r: 12, t: 10, b: 10 },
    }),
    { responsive: true, displayModeBar: false, scrollZoom: false },
  );
}

function renderOptimizationBar() {
  const scenario = getCurrentScenario();
  const rows = [...(scenario?.allocation ?? [])]
    .filter((row) => row.change_pct != null)
    .sort((left, right) => Math.abs(right.change_pct) - Math.abs(left.change_pct))
    .slice(0, 14)
    .reverse();

  if (!rows.length) {
    emptyPlot("companion-chart", "暂无优化情景数据。");
    return;
  }

  Plotly.react(
    "companion-chart",
    [
      {
        type: "bar",
        x: rows.map((row) => row.change_pct),
        y: rows.map((row) => countryLabel(row)),
        orientation: "h",
        marker: {
          color: rows.map((row) => (row.change_pct >= 0 ? THEME.cyan : THEME.rose)),
          cornerradius: 6,
          line: { width: 0 },
        },
        customdata: rows.map((row) => [row.current, row.optimal]),
        hovertemplate:
          "<b>%{y}</b><br>调整幅度：%{x:.1f}%<br>当前：%{customdata[0]:,.0f} 美元<br>目标：%{customdata[1]:,.0f} 美元<extra></extra>",
      },
    ],
    baseLayout({
      xaxis: { title: "建议调整幅度（%）" },
      yaxis: { automargin: true },
    }),
    { responsive: true, displayModeBar: false, scrollZoom: false },
  );
}

function renderEquityChart() {
  const equity = store.globalStory?.health_equity ?? [];
  if (!equity.length) {
    emptyPlot("companion-chart", "暂无健康公平数据。");
    return;
  }

  Plotly.react(
    "companion-chart",
    [
      {
        x: equity.map((r) => r.year),
        y: equity.map((r) => r.gini),
        name: "基尼系数（预期寿命）",
        mode: "lines+markers",
        line: { color: THEME.cyan, width: 3, shape: "spline" },
        marker: { size: 5, color: THEME.cyan },
      },
      {
        x: equity.map((r) => r.year),
        y: equity.map((r) => r.sigma),
        name: "离散度收敛",
        mode: "lines+markers",
        yaxis: "y2",
        line: { color: THEME.amber, width: 2.5, shape: "spline" },
        marker: { size: 5, color: THEME.amber },
      },
    ],
    baseLayout({
      yaxis: { title: "基尼系数" },
      yaxis2: {
        overlaying: "y",
        side: "right",
        title: "对数预期寿命标准差",
        gridcolor: "rgba(0,0,0,0)",
      },
    }),
    { responsive: true, displayModeBar: false, scrollZoom: false },
  );
}

function renderChinaNationalTrend() {
  const data = store.chinaDeepDive;
  const metricKey = state.metric === "health_institutions" ? "health_institutions" : "health_personnel";
  const series = data?.national_trend?.[metricKey] ?? [];

  if (!series.length) {
    emptyPlot("companion-chart", "暂无全国汇总数据。");
    return;
  }

  Plotly.react(
    "companion-chart",
    [
      {
        x: series.map((r) => r.year),
        y: series.map((r) => r.value),
        name: `全国${METRIC_META[metricKey].label}`,
        mode: "lines+markers",
        line: { color: "#f87171", width: 3, shape: "spline" },
        marker: { size: 6, color: "#f87171" },
        fill: "tozeroy",
        fillcolor: "rgba(248, 113, 113, 0.08)",
      },
    ],
    baseLayout({
      yaxis: { title: METRIC_META[metricKey].label },
    }),
    { responsive: true, displayModeBar: false, scrollZoom: false },
  );
}

function renderChinaProvincePersonnelTrend() {
  const data = store.chinaDeepDive;
  const prov = state.province;
  if (!prov) {
    emptyPlot("companion-chart", "请在地图上点击选择省份。");
    return;
  }

  const provEn = store.chinaProvinceIndex.get(prov)?.province_en;
  const series = (data?.personnel_history?.[provEn] ?? []);

  if (!series.length) {
    emptyPlot("companion-chart", `暂无 ${prov} 的卫生人员历史数据。`);
    return;
  }

  const natSeries = data?.national_trend?.health_personnel ?? [];

  const traces = [
    {
      x: series.map((r) => r.year),
      y: series.map((r) => r.health_personnel_wan),
      name: prov,
      mode: "lines+markers",
      line: { color: THEME.amber, width: 3, shape: "spline" },
      marker: { size: 6, color: THEME.amber },
      fill: "tozeroy",
      fillcolor: "rgba(251,191,36,0.07)",
    },
  ];

  if (natSeries.length) {
    traces.push({
      x: natSeries.map((r) => r.year),
      y: natSeries.map((r) => r.value),
      name: "全国",
      mode: "lines",
      line: { color: THEME.dim, width: 1.5, dash: "dot" },
      yaxis: "y2",
    });
  }

  Plotly.react(
    "companion-chart",
    traces,
    baseLayout({
      yaxis: { title: "卫生人员（万人）" },
      yaxis2: { title: "全国（万人）", overlaying: "y", side: "right", showgrid: false },
      legend: { orientation: "h", y: 1.05, x: 0 },
    }),
    { responsive: true, displayModeBar: false, scrollZoom: false },
  );
}

function renderContextPanel() {
  if (state.dimension === "dim1") {
    document.getElementById("context-title").textContent = "全球极值与结构对比";
    renderDim1Context();
    return;
  }

  if (state.dimension === "dim2") {
    document.getElementById("context-title").textContent = "地区优先风险层级";
    renderDim2Context();
    return;
  }

  if (state.dimension === "dim4") {
    document.getElementById("context-title").textContent = "省级优化与公平分析";
    document.getElementById("context-pill").textContent = "中国视角";
    renderDim4Context();
    return;
  }

  if (state.dimension === "dim5") {
    document.getElementById("context-title").textContent = "发展-健康象限分析";
    document.getElementById("context-pill").textContent = "外部数据";
    renderQuadrantScatter();
    return;
  }

  document.getElementById("context-title").textContent = "资源配置摘要";
  renderDim3Context();
}

function renderDim1Context() {
  const countries = [...(store.overview.countries ?? [])];
  const topLife = countries
    .filter((row) => row.life_expectancy != null)
    .sort((left, right) => right.life_expectancy - left.life_expectancy)
    .slice(0, 6);
  const bottomLife = countries
    .filter((row) => row.life_expectancy != null)
    .sort((left, right) => left.life_expectancy - right.life_expectancy)
    .slice(0, 6);
  const communicable = countries
    .filter((row) => row.communicable_share != null)
    .sort((left, right) => right.communicable_share - left.communicable_share)
    .slice(0, 6);

  document.getElementById("context-panel").innerHTML = renderContextColumns([
    {
      title: "最高预期寿命",
      items: topLife.map((row) => ({ name: countryLabel(row), value: `${formatDecimal(row.life_expectancy)} 岁` })),
    },
    {
      title: "最低预期寿命",
      items: bottomLife.map((row) => ({ name: countryLabel(row), value: `${formatDecimal(row.life_expectancy)} 岁` })),
    },
    {
      title: "传染性疾病负担最高",
      items: communicable.map((row) => ({ name: countryLabel(row), value: formatShare(row.communicable_share) })),
    },
  ]);
}

function renderDim2Context() {
  const rows = store.globalStory.region_priority ?? [];
  document.getElementById("context-panel").innerHTML = renderContextColumns(
    rows.map((row) => ({
      title: regionLabel(row.who_region),
      items: [
        { name: `1. ${translateRiskName(row.primary_risk)}`, value: formatShare(row.primary_share) },
        { name: `2. ${translateRiskName(row.secondary_risk)}`, value: formatShare(row.secondary_share) },
        { name: `3. ${translateRiskName(row.tertiary_risk)}`, value: formatShare(row.tertiary_share) },
      ],
    })),
  );
}

function renderDim3Context() {
  const scenario = getCurrentScenario();
  const profile = store.profiles[state.country];
  const latest = profile?.latest ?? {};
  const selected = getScenarioRow(state.country);
  // Use pre-computed top_recipients/top_donors from scenario summary if available
  const recipients = scenario?.summary?.top_recipients?.length
    ? scenario.summary.top_recipients.slice(0, 5)
    : [...(scenario?.allocation ?? [])]
        .filter((row) => (row.change ?? 0) > 0)
        .sort((left, right) => (right.change_pct ?? -Infinity) - (left.change_pct ?? -Infinity))
        .slice(0, 5);
  const donors = scenario?.summary?.top_donors?.length
    ? scenario.summary.top_donors.slice(0, 5)
    : [...(scenario?.allocation ?? [])]
        .filter((row) => (row.change ?? 0) < 0)
        .sort((left, right) => (left.change_pct ?? Infinity) - (right.change_pct ?? Infinity))
        .slice(0, 5);

  const scenarioSummary = scenario?.summary ?? {};
  const topRecipient = scenarioSummary.top_recipients?.[0];
  const summaryGrid = `
    <div class="lab-summary-grid">
      ${renderLabStat("优化目标", scenario?.objective_label ?? objectiveLabel(state.objective))}
      ${renderLabStat("预算规模", budgetLabel(scenario?.budget_multiplier ?? state.budgetMultiplier))}
      ${renderLabStat("受益国家数", formatInteger(scenarioSummary.recipient_count))}
      ${renderLabStat("捐出国家数", formatInteger(scenarioSummary.donor_count))}
      ${renderLabStat("产出提升", scenarioSummary.projected_output_gain_pct != null ? `+${scenarioSummary.projected_output_gain_pct.toFixed(0)}%` : NO_DATA_LABEL)}
      ${renderLabStat("首要受益国", topRecipient ? (countryLabel(topRecipient) || topRecipient.iso3) : NO_DATA_LABEL)}
    </div>
  `;

  const detailColumn = {
    title: countryLabel(profile?.meta ?? store.overviewIndex.get(state.country)),
    items: [
      { name: "当前支出", value: formatCurrency(selected?.current ?? latest.current) },
      { name: "优化目标", value: formatCurrency(selected?.optimal ?? latest.optimal) },
      { name: "建议调整", value: formatSignedPercent(selected?.change_pct ?? latest.change_pct) },
      { name: "资源缺口", value: formatSigned(latest.gap) },
      { name: "效率", value: formatSigned(latest.efficiency) },
    ],
  };

  // Quadrant recommendation for selected country
  const countryQuadrant = latest.quadrant ?? selected?.quadrant ?? "";
  const globalRecs = _globalQuadrantRecommendations();
  const countryRec = countryQuadrant ? globalRecs[countryQuadrant] : null;
  const recBlock = countryRec ? `
    <div class="context-rec-block">
      <div class="rec-badge rec-${countryQuadrant.replace(/[^a-zA-Z0-9]/g, "_").toLowerCase()}">${escapeHtml(countryQuadrant.replace(/_/g, " "))}</div>
      <div class="rec-title">${escapeHtml(countryRec.title)}</div>
      <div class="rec-body">${escapeHtml(countryRec.policy)}</div>
      <div class="rec-priority"><span>优先行动：</span>${escapeHtml(countryRec.priority)}</div>
    </div>
  ` : "";

  document.getElementById("context-panel").innerHTML = `
    <p class="context-lede">${escapeHtml(
      OBJECTIVE_META[state.objective]?.note ?? "当前情景设置已应用到最新资源面板。",
    )}</p>
    ${summaryGrid}
    ${recBlock}
    ${renderContextColumns([
      {
        title: "受益最多国家",
        items: recipients.map((row) => ({ name: countryLabel(row), value: formatSignedPercent(row.change_pct) })),
      },
      {
        title: "主要捐出国家",
        items: donors.map((row) => ({ name: countryLabel(row), value: formatSignedPercent(row.change_pct) })),
      },
      detailColumn,
    ])}
  `;
}

function _globalQuadrantRecommendations() {
  return {
    "Q1_high_input_high_output": {
      title: "高投入高产出：保持领先，分享经验",
      policy: "该国卫生体系资源充足且健康产出优良。应在国际合作中发挥引领作用，向低产出国家分享管理经验与技术，同时持续优化资源结构、防范资源过剩浪费。",
      priority: "推动南南合作与知识转移，分享高效卫生体系建设经验",
    },
    "Q2_low_input_high_output": {
      title: "低投入高产出：效率领先，推广经验",
      policy: "该国以有限投入实现优异健康产出，代表高效能卫生体系典型。其经验做法（初级卫生保健强化、预防为主）值得总结推广，并可争取适度增加投入以巩固优势。",
      priority: "提炼可复制的低成本高效卫生模式，争取增加基础卫生投资",
    },
    "Q3_high_input_low_output": {
      title: "高投入低产出：提升效率，优化结构",
      policy: "该国投入充足但健康产出不足，反映卫生体系效率低下或资源错配。需推进体系改革，建立绩效考核机制，将重点从扩大投入总量转向提升服务质量与效率。",
      priority: "开展卫生体系效率审计，推进绩效导向的资源分配机制",
    },
    "Q4_low_input_low_output": {
      title: "低投入低产出：双轨并行，增投提效",
      policy: "该国卫生资源严重不足且健康产出偏低，需同步增加投入与提升效率。优先保障基础设施和基层医疗人才，争取国际援助与技术支持，同时借鉴Q2经验避免低效扩张。",
      priority: "争取国际援助，优先补足初级卫生保健基础设施和人力资源",
    },
  };
}

function renderDim4Context() {
  const data = store.chinaDeepDive;
  if (!data) {
    document.getElementById("context-panel").innerHTML = '<p class="empty-inline">暂无中国大陆数据。</p>';
    return;
  }

  const provinces = data.provinces ?? [];
  const byRegion = data.by_region ?? [];
  const equity = data.equity_metrics ?? {};
  const chinaScenario = getCurrentChinaScenario();
  const allocation = chinaScenario?.allocation ?? [];

  // Top recipients/donors from pre-computed summary or from allocation
  const recipients = chinaScenario?.summary?.top_recipients?.length
    ? chinaScenario.summary.top_recipients.slice(0, 5)
    : [...allocation].filter((r) => r.change_pct > 0)
        .sort((a, b) => b.change_pct - a.change_pct).slice(0, 5);
  const donors = chinaScenario?.summary?.top_donors?.length
    ? chinaScenario.summary.top_donors.slice(0, 5)
    : [...allocation].filter((r) => r.change_pct < 0)
        .sort((a, b) => a.change_pct - b.change_pct).slice(0, 5);

  // Quadrant counts
  const qcounts = data.quadrant_counts ?? {};
  const quadrantRecs = _chinaQuadrantRecommendations();

  const prov = state.province;
  const provData = store.chinaProvinceIndex.get(prov) ?? {};
  const quadrant = provData.quadrant ?? "";
  const rec = quadrantRecs[quadrant] ?? { title: "政策建议", policy: "根据省份资源配置类型制定差异化政策。", priority: "—" };

  const equityBlock = `
    <div class="lab-summary-grid">
      ${renderLabStat("基尼系数（预期寿命）", equity.gini_life_expectancy != null ? equity.gini_life_expectancy.toFixed(4) : NO_DATA_LABEL)}
      ${renderLabStat("基尼系数（卫生支出）", equity.gini_health_expenditure != null ? equity.gini_health_expenditure.toFixed(4) : NO_DATA_LABEL)}
      ${renderLabStat("婴儿死亡率集中指数", equity.concentration_index_exp_vs_life_expectancy != null ? equity.concentration_index_exp_vs_life_expectancy.toFixed(4) : NO_DATA_LABEL)}
      ${renderLabStat("优化目标", chinaScenario?.objective_label ?? NO_DATA_LABEL)}
      ${renderLabStat("预算情景", chinaScenario ? `${((chinaScenario.budget_multiplier - 1) * 100 >= 0 ? "+" : "")}${((chinaScenario.budget_multiplier - 1) * 100).toFixed(0)}%` : NO_DATA_LABEL)}
      ${renderLabStat("预计产出提升", chinaScenario?.summary?.projected_output_gain_pct != null ? `${chinaScenario.summary.projected_output_gain_pct.toFixed(2)}%` : NO_DATA_LABEL)}
    </div>
  `;

  const recBlock = quadrant ? `
    <div class="context-rec-block">
      <div class="rec-badge rec-${quadrant.replace(/[^a-zA-Z]/g, "_").toLowerCase()}">${escapeHtml(quadrant)}</div>
      <div class="rec-title">${escapeHtml(rec.title)}</div>
      <div class="rec-body">${escapeHtml(rec.policy)}</div>
      <div class="rec-priority"><span>优先行动：</span>${escapeHtml(rec.priority)}</div>
    </div>
  ` : "";

  document.getElementById("context-panel").innerHTML = `
    <p class="context-lede">中国省级卫生资源配置分析 · ${chinaScenario?.objective_label ?? "最优化模型"}</p>
    ${equityBlock}
    ${recBlock}
    ${renderContextColumns([
      {
        title: "优化建议受益省份",
        items: recipients.map((r) => ({ name: r.province, value: `+${r.change_pct.toFixed(1)}%` })),
      },
      {
        title: "优化建议减少省份",
        items: donors.map((r) => ({ name: r.province, value: `${r.change_pct.toFixed(1)}%` })),
      },
      {
        title: "分地区资源汇总",
        items: byRegion.map((r) => ({
          name: `${r.region_cn ?? r.region_en}（${r.province_count} 省）`,
          value: `人均支出：${r.avg_health_exp != null ? "¥" + Math.round(r.avg_health_exp).toLocaleString() : NO_DATA_LABEL}`,
        })),
      },
    ])}
  `;
}

function _chinaQuadrantRecommendations() {
  return {
    "Q1_高投入高产出": {
      title: "高投入高产出：保持优势，扩大经验辐射",
      policy: "该类省份资源充足、健康产出优良，应总结管理经验，向欠发达地区输出模式。重点防范资源浪费，优化结构而非扩大总量。",
      priority: "建立区域帮扶机制，分享精细化管理模式",
    },
    "Q2_低投入高产出": {
      title: "低投入高产出：效率领先，推广可复制经验",
      policy: "该类省份以有限资源实现高健康产出，具有较强管理效率和资源使用能力。应总结经验做法，形成可复制推广的低成本高效模式。",
      priority: "提炼效率管理经验，争取适度增加投入以巩固优势",
    },
    "Q3_高投入低产出": {
      title: "高投入低产出：提升效率，优化资源结构",
      policy: "该类省份投入充足但产出不足，反映管理效率低下或资源错配。应开展资源使用审计，优化激励机制，引入绩效管理，将重点从量的增加转向质的提升。",
      priority: "推进卫生体系管理改革，建立绩效考核机制",
    },
    "Q4_低投入低产出": {
      title: "低投入低产出：双轨并行，增投提效",
      policy: "该类省份资源严重不足且健康产出偏低，需要同步增加投入与提升效率。应优先保障基础卫生设施和基层医疗人才，同时借鉴Q2省份经验，避免重蹈投入低效覆辙。",
      priority: "争取中央转移支付，优先补齐基层医疗短板",
    },
  };
}

// ── dim5 Charts ─────────────────────────────────────────────────

const REGION_COLORS = {
  Africa: "#fb7185",
  Americas: "#22d3ee",
  Asia: "#fbbf24",
  Europe: "#a78bfa",
  Oceania: "#34d399",
  "": "#64748b",
};

function renderBubbleChart() {
  const yearStr = String(state.year);
  const records = store.bubbleTimeseries?.by_year?.[yearStr] ?? [];
  if (!records.length) {
    emptyPlot("companion-chart", `${state.year} 年暂无气泡图数据。`);
    return;
  }

  // Group by region
  const regionGroups = {};
  for (const r of records) {
    const region = r.region || "";
    if (!regionGroups[region]) regionGroups[region] = [];
    regionGroups[region].push(r);
  }

  const traces = Object.entries(regionGroups).map(([region, rows]) => ({
    x: rows.map((r) => r.gdp_pc),
    y: rows.map((r) => r.life_expectancy),
    text: rows.map((r) => countryLabel(r)),
    customdata: rows.map((r) => [r.population, r.iso3]),
    mode: "markers",
    name: region || "其他",
    marker: {
      size: rows.map((r) => Math.max(4, Math.sqrt(r.population / 500000))),
      color: REGION_COLORS[region] ?? THEME.dim,
      opacity: 0.72,
      line: {
        color: rows.map((r) =>
          r.iso3 === state.country ? "rgba(255,255,255,0.9)" : "rgba(0,0,0,0)",
        ),
        width: rows.map((r) => (r.iso3 === state.country ? 2.5 : 0)),
      },
    },
    hovertemplate:
      "<b>%{text}</b><br>人均GDP: $%{x:,.0f}<br>预期寿命: %{y:.1f} 岁<br>人口: %{customdata[0]:,.0f}<extra></extra>",
  }));

  Plotly.react(
    "companion-chart",
    traces,
    baseLayout({
      xaxis: {
        title: "人均GDP（美元，对数尺度）",
        type: "log",
        gridcolor: THEME.grid,
        tickfont: { size: 10, color: THEME.dim },
      },
      yaxis: {
        title: "预期寿命（岁）",
        gridcolor: THEME.grid,
        tickfont: { size: 10, color: THEME.dim },
      },
      legend: {
        orientation: "h",
        yanchor: "bottom",
        y: 1.02,
        xanchor: "left",
        x: 0,
        font: { color: THEME.muted, size: 11 },
      },
      margin: { l: 50, r: 20, t: 30, b: 50 },
    }),
    { responsive: true, displayModeBar: false, scrollZoom: false },
  );

  // Bind click to bubble chart
  const node = document.getElementById("companion-chart");
  if (!node.dataset.bubbleBound) {
    node.on("plotly_click", (event) => {
      if (state.dimension !== "dim5") return;
      const iso3 = event?.points?.[0]?.customdata?.[1];
      if (iso3) {
        state.country = iso3;
        renderPanels();
        updateMapHighlight(iso3);
        openSpotlightModal(iso3);
      }
    });
    node.dataset.bubbleBound = "1";
  }
}

function renderRadarChart() {
  const country = store.panoramaIndex.get(state.country);
  if (!country) {
    emptyPlot("detail-chart", "该国暂无全景数据。");
    return;
  }

  // Compute global averages from panorama data
  const all = store.panorama?.countries ?? [];
  const avg = (field) => {
    const vals = all.map((c) => c[field]).filter((v) => v != null);
    return vals.length ? vals.reduce((a, b) => a + b, 0) / vals.length : 0;
  };

  const axes = [
    { key: "hdi", label: "HDI", max: 1 },
    { key: "hale", label: "HALE", max: 85 },
    { key: "uhc_index", label: "UHC", max: 100 },
    { key: "doctor_density", label: "医生", max: 60 },
    { key: "che_per_capita", label: "卫生支出", max: 8000 },
    { key: "pm25_inv", label: "空气质量", max: 1 },
  ];

  const normalize = (val, max) => (val != null ? Math.min(val / max, 1) : 0);
  const pm25Invert = (v) => (v != null && v > 0 ? 1 / v * 10 : 0);

  const countryValues = axes.map((a) => {
    if (a.key === "pm25_inv") return normalize(pm25Invert(country.pm25), a.max);
    return normalize(country[a.key], a.max);
  });
  const globalValues = axes.map((a) => {
    if (a.key === "pm25_inv") return normalize(pm25Invert(avg("pm25")), a.max);
    return normalize(avg(a.key), a.max);
  });

  const labels = axes.map((a) => a.label);

  Plotly.react(
    "detail-chart",
    [
      {
        type: "scatterpolar",
        r: [...countryValues, countryValues[0]],
        theta: [...labels, labels[0]],
        name: countryLabel({ iso3: state.country }),
        fill: "toself",
        fillcolor: "rgba(34,211,238,0.12)",
        line: { color: THEME.cyan, width: 2.5 },
        marker: { size: 6, color: THEME.cyan },
      },
      {
        type: "scatterpolar",
        r: [...globalValues, globalValues[0]],
        theta: [...labels, labels[0]],
        name: "全球均值",
        fill: "toself",
        fillcolor: "rgba(167,139,250,0.08)",
        line: { color: THEME.violet, width: 2, dash: "dash" },
        marker: { size: 4, color: THEME.violet },
      },
    ],
    {
      paper_bgcolor: "rgba(0,0,0,0)",
      plot_bgcolor: "rgba(0,0,0,0)",
      margin: { l: 50, r: 50, t: 30, b: 30 },
      font: { family: "system-ui, sans-serif", color: THEME.muted },
      polar: {
        bgcolor: "rgba(0,0,0,0)",
        radialaxis: {
          visible: true,
          range: [0, 1],
          gridcolor: THEME.grid,
          linecolor: "rgba(0,0,0,0)",
          tickfont: { size: 9, color: THEME.dim },
        },
        angularaxis: {
          gridcolor: THEME.grid,
          linecolor: THEME.grid,
          tickfont: { size: 11, color: THEME.muted },
        },
      },
      legend: {
        orientation: "h",
        yanchor: "bottom",
        y: -0.15,
        xanchor: "center",
        x: 0.5,
        font: { color: THEME.muted, size: 11 },
      },
      hoverlabel: {
        bgcolor: THEME.hover,
        bordercolor: "rgba(34,211,238,0.20)",
        font: { family: "system-ui, sans-serif", color: THEME.inkBright, size: 12 },
      },
    },
    { responsive: true, displayModeBar: false, scrollZoom: false },
  );
}

function renderQuadrantScatter() {
  const countries = (store.panorama?.countries ?? []).filter(
    (c) => c.hdi != null && c.hale != null,
  );
  if (!countries.length) {
    emptyPlot("context-panel", "暂无象限分析数据。");
    return;
  }

  // Compute medians
  const sortedHDI = countries.map((c) => c.hdi).sort((a, b) => a - b);
  const sortedHALE = countries.map((c) => c.hale).sort((a, b) => a - b);
  const medianHDI = sortedHDI[Math.floor(sortedHDI.length / 2)];
  const medianHALE = sortedHALE[Math.floor(sortedHALE.length / 2)];

  // Group by region
  const regionGroups = {};
  for (const c of countries) {
    const region = c.region || "";
    if (!regionGroups[region]) regionGroups[region] = [];
    regionGroups[region].push(c);
  }

  const traces = Object.entries(regionGroups).map(([region, rows]) => ({
    x: rows.map((r) => r.hdi),
    y: rows.map((r) => r.hale),
    text: rows.map((r) => countryLabel(r)),
    customdata: rows.map((r) => r.iso3),
    mode: "markers",
    name: region || "其他",
    marker: {
      size: rows.map((r) => Math.max(5, r.population ? Math.sqrt(r.population / 1000000) * 1.5 : 5)),
      color: REGION_COLORS[region] ?? THEME.dim,
      opacity: 0.72,
      line: {
        color: rows.map((r) =>
          r.iso3 === state.country ? "rgba(255,255,255,0.9)" : "rgba(0,0,0,0)",
        ),
        width: rows.map((r) => (r.iso3 === state.country ? 2.5 : 0)),
      },
    },
    hovertemplate: "<b>%{text}</b><br>HDI: %{x:.3f}<br>HALE: %{y:.1f} 岁<extra></extra>",
  }));

  const quadrantAnnotations = [
    { x: medianHDI + (1 - medianHDI) / 2, y: medianHALE + (80 - medianHALE) / 2, text: "高发展-高健康" },
    { x: medianHDI / 2, y: medianHALE + (80 - medianHALE) / 2, text: "低发展-高健康" },
    { x: medianHDI + (1 - medianHDI) / 2, y: medianHALE / 2 + 20, text: "高发展-低健康" },
    { x: medianHDI / 2, y: medianHALE / 2 + 20, text: "低发展-低健康" },
  ].map((a) => ({
    x: a.x,
    y: a.y,
    xref: "x",
    yref: "y",
    text: a.text,
    showarrow: false,
    font: { size: 11, color: "rgba(148,163,184,0.45)" },
  }));

  // Render into context-panel as a plotly chart
  const panelEl = document.getElementById("context-panel");
  panelEl.innerHTML = '<div id="quadrant-chart" class="plot" style="height:340px"></div>';

  Plotly.react(
    "quadrant-chart",
    traces,
    baseLayout({
      xaxis: { title: "人类发展指数 (HDI)", gridcolor: THEME.grid },
      yaxis: { title: "健康预期寿命 (HALE)", gridcolor: THEME.grid },
      shapes: [
        { type: "line", x0: medianHDI, x1: medianHDI, y0: 0, y1: 1, yref: "paper", line: { color: "rgba(148,163,184,0.2)", width: 1, dash: "dot" } },
        { type: "line", x0: 0, x1: 1, y0: medianHALE, y1: medianHALE, xref: "paper", line: { color: "rgba(148,163,184,0.2)", width: 1, dash: "dot" } },
      ],
      annotations: quadrantAnnotations,
      legend: { orientation: "h", yanchor: "bottom", y: 1.02, xanchor: "left", x: 0, font: { color: THEME.muted, size: 10 } },
      margin: { l: 50, r: 20, t: 30, b: 50 },
    }),
    { responsive: true, displayModeBar: false, scrollZoom: false },
  );

  const qNode = document.getElementById("quadrant-chart");
  if (qNode && !qNode.dataset.quadBound) {
    qNode.on("plotly_click", (event) => {
      const iso3 = event?.points?.[0]?.customdata;
      if (iso3) {
        state.country = iso3;
        renderPanels();
        updateMapHighlight(iso3);
        openSpotlightModal(iso3);
      }
    });
    qNode.dataset.quadBound = "1";
  }
}

// ── End dim5 Charts ─────────────────────────────────────────────

function renderLabStat(label, value) {
  return `<article class="lab-stat"><span>${escapeHtml(label)}</span><strong>${escapeHtml(
    value ?? NO_DATA_LABEL,
  )}</strong></article>`;
}

function renderContextColumns(columns) {
  return `<div class="context-grid">${columns
    .map(
      (column) => `
        <section class="context-column">
          <div class="col-header"><span class="col-dot"></span><h3>${escapeHtml(column.title)}</h3></div>
          ${(column.items ?? [])
            .map(
              (item) => `
                <div class="context-item">
                  <span class="ctx-name">${escapeHtml(item.name)}</span>
                  <span class="ctx-value">${escapeHtml(item.value)}</span>
                </div>
              `,
            )
            .join("")}
        </section>
      `,
    )
    .join("")}</div>`;
}

function openSpotlightModal(iso3) {
  state.dialogOpen = true;
  state.dialogCountry = iso3;
  state.previousFocus = document.activeElement;

  const backdrop = document.getElementById("spotlight-backdrop");
  const modal = document.getElementById("spotlight-modal");
  backdrop.classList.add("is-open");
  backdrop.setAttribute("aria-hidden", "false");
  modal.classList.add("is-open");
  modal.setAttribute("aria-hidden", "false");

  document.body.style.overflow = "hidden";
  renderSpotlightContent(iso3);
  window.requestAnimationFrame(() => {
    document.getElementById("spotlight-close").focus();
  });
}

function renderSpotlightContent(iso3) {
  const profile = store.profiles[iso3];
  if (!profile) {
    return;
  }

  const meta = profile.meta ?? {};
  const latest = profile.latest ?? {};
  const risks = profile.latest_risks ?? [];
  const scenarioRow = getScenarioRow(iso3);

  document.getElementById("spotlight-name").textContent = countryLabel(meta) || iso3;
  const flagWrap = document.querySelector(".spotlight-flag-wrap");
  const flagEmoji = iso3ToFlag(iso3);
  if (flagEmoji) {
    flagWrap.innerHTML = `<div class="spotlight-flag-emoji">${flagEmoji}</div>`;
  } else {
    flagWrap.innerHTML = `<div class="spotlight-flag-fallback">${escapeHtml(iso3)}</div>`;
  }
  document.getElementById("spotlight-badges").innerHTML = [
    meta.who_region
      ? `<span class="spotlight-badge" data-type="region">${escapeHtml(regionLabel(meta.who_region))}</span>`
      : "",
    meta.wb_income
      ? `<span class="spotlight-badge" data-type="income">${escapeHtml(incomeLabel(meta.wb_income))}</span>`
      : "",
  ].join("");

  const metrics = [
    ["预期寿命", METRIC_META.life_expectancy.formatter(latest.life_expectancy), "cyan"],
    ["非传染性疾病占比", formatShare(latest.ncd_share), "violet"],
    latest.hdi != null
      ? ["人类发展指数", Number(latest.hdi).toFixed(3), "emerald"]
      : ["传染性疾病占比", formatShare(latest.communicable_share), "amber"],
    latest.hale != null
      ? ["健康预期寿命", `${latest.hale} 岁`, "teal"]
      : ["人均国内生产总值", formatCurrency(latest.gdp_per_capita), "teal"],
    latest.uhc_index != null
      ? ["UHC 覆盖指数", String(latest.uhc_index), "blue"]
      : ["卫生支出占GDP", formatPercentValue(latest.health_exp_pct_gdp), "blue"],
    latest.pm25 != null
      ? ["PM2.5 暴露", `${latest.pm25} μg/m³`, "amber"]
      : ["首要风险", translateRiskName(latest.top_risk_name), "rose"],
    latest.doctor_density != null
      ? ["医生密度", `${latest.doctor_density}/万人`, "cyan"]
      : ["优化目标", formatCurrency(scenarioRow?.optimal ?? latest.optimal), "emerald"],
    latest.che_per_capita != null
      ? ["人均卫生支出", formatCurrency(latest.che_per_capita), "rose"]
      : ["资源缺口", formatSigned(latest.gap), "cyan"],
  ];

  document.getElementById("spotlight-metrics").innerHTML = metrics
    .map(
      ([label, value, accent]) =>
        `<div class="spotlight-metric" data-accent="${accent}"><span class="sm-label">${escapeHtml(
          label,
        )}</span><span class="sm-value">${escapeHtml(value)}</span></div>`,
    )
    .join("");

  renderSpotlightChart(profile.trend ?? [], scenarioRow?.optimal ?? latest.optimal);
  renderSpotlightRisks(risks);
  renderSpotlightAllocation(scenarioRow, latest);
}

function renderSpotlightChart(trend, optimalValue) {
  if (!trend.length) {
    emptyPlot("spotlight-chart", "暂无历史趋势数据。");
    return;
  }

  const traces = [
    {
      x: trend.map((row) => row.year),
      y: trend.map((row) => row.life_expectancy),
      mode: "lines",
      name: "预期寿命",
      line: { color: THEME.cyan, width: 2.5, shape: "spline" },
      fill: "tozeroy",
      fillcolor: "rgba(34,211,238,0.08)",
      hovertemplate: "<b>%{x}</b><br>%{y:.1f} 岁<extra></extra>",
    },
  ];

  if (optimalValue != null) {
    traces.push({
      x: trend.map((row) => row.year),
      y: trend.map(() => optimalValue),
      mode: "lines",
      name: "优化目标",
      line: { color: THEME.blue, width: 1.8, dash: "dash" },
      hovertemplate: "<b>优化目标</b><br>%{y:,.0f} 美元<extra></extra>",
      yaxis: "y2",
    });
  }

  Plotly.react(
    "spotlight-chart",
    traces,
    {
      paper_bgcolor: "rgba(0,0,0,0)",
      plot_bgcolor: "rgba(0,0,0,0)",
      margin: { l: 36, r: 18, t: 6, b: 28 },
      font: { family: "system-ui, sans-serif", color: THEME.dim },
      xaxis: { gridcolor: THEME.grid, linecolor: THEME.grid, tickfont: { size: 10, color: THEME.dim } },
      yaxis: { gridcolor: THEME.grid, linecolor: THEME.grid, tickfont: { size: 10, color: THEME.dim } },
      yaxis2: {
        overlaying: "y",
        side: "right",
        showgrid: false,
        tickfont: { size: 10, color: THEME.dim },
      },
      hoverlabel: {
        bgcolor: THEME.hover,
        bordercolor: "rgba(34,211,238,0.20)",
        font: { family: "system-ui, sans-serif", color: THEME.inkBright, size: 12 },
      },
    },
    { responsive: true, displayModeBar: false, scrollZoom: false },
  );
}

function renderSpotlightRisks(risks) {
  const container = document.getElementById("spotlight-risks");
  if (!risks.length) {
    container.innerHTML = '<span class="empty-inline">暂无风险因素记录。</span>';
    return;
  }

  const topRows = risks.slice(0, 6);
  const maxShare = Math.max(...topRows.map((row) => row.share ?? 0), 0.01);
  container.innerHTML = topRows
    .map((row, index) => {
      const pct = (((row.share ?? 0) / maxShare) * 100).toFixed(1);
      return `
        <div class="spotlight-risk-row">
          <div class="spotlight-risk-label">
            <span class="sr-name">${escapeHtml(translateRiskName(row.risk_name))}</span>
            <span class="sr-value">${escapeHtml(formatShare(row.share))}</span>
          </div>
          <div class="spotlight-risk-track">
            <div class="spotlight-risk-fill" style="width:${pct}%;background:${colorFromPalette(index)};"></div>
          </div>
        </div>
      `;
    })
    .join("");
}

function renderSpotlightAllocation(scenarioRow, latest) {
  const container = document.getElementById("spotlight-allocation");
  const items = [
    ["当前支出", formatCurrency(scenarioRow?.current ?? latest.current)],
    ["优化目标", formatCurrency(scenarioRow?.optimal ?? latest.optimal)],
    ["建议调整", formatSignedPercent(scenarioRow?.change_pct ?? latest.change_pct)],
    ["效率", formatSigned(latest.efficiency)],
  ];

  container.innerHTML = items
    .map(
      ([label, value]) =>
        `<div class="spotlight-alloc-item"><span class="sa-label">${escapeHtml(
          label,
        )}</span><span class="sa-value">${escapeHtml(value)}</span></div>`,
    )
    .join("");
}

function closeSpotlightModal() {
  if (!state.dialogOpen) {
    return;
  }

  state.dialogOpen = false;
  const backdrop = document.getElementById("spotlight-backdrop");
  const modal = document.getElementById("spotlight-modal");
  backdrop.classList.remove("is-open");
  backdrop.setAttribute("aria-hidden", "true");
  modal.classList.remove("is-open");
  modal.setAttribute("aria-hidden", "true");
  document.body.style.overflow = "";

  if (state.previousFocus && typeof state.previousFocus.focus === "function") {
    state.previousFocus.focus();
  }
}

function toggleAnimation() {
  if (state.animating) {
    stopAnimation();
  } else {
    startAnimation();
  }
}

function startAnimation() {
  const years = state.dimension === "dim5" ? store.bubbleYears : store.availableYears;
  if (!years.length) return;
  state.animating = true;
  document.getElementById("play-button").classList.add("is-playing");

  let idx = years.indexOf(state.year);
  if (idx < 0 || idx >= years.length - 1) idx = 0;

  state.animationTimer = setInterval(() => {
    idx++;
    if (idx >= years.length) {
      stopAnimation();
      return;
    }
    state.year = years[idx];
    const slider = document.getElementById("year-slider");
    slider.value = state.year;
    document.getElementById("year-display").textContent = state.year;
    if (state.dimension === "dim5") {
      renderBubbleChart();
    } else {
      renderMap();
      renderCountryPanel();
      renderRankingList();
    }
    updateMapKicker();
  }, 600);
}

function stopAnimation() {
  state.animating = false;
  clearInterval(state.animationTimer);
  state.animationTimer = null;
  document.getElementById("play-button").classList.remove("is-playing");
}

function updateMapKicker() {
  const kicker = document.getElementById("map-kicker");
  if ((state.dimension === "dim1" && store.availableYears.length) ||
      (state.dimension === "dim5" && store.bubbleYears.length)) {
    kicker.textContent = `全球地图 \u00B7 ${state.year}`;
  }
}

function trapDialogFocus(event) {
  const modal = document.getElementById("spotlight-modal");
  const focusable = modal.querySelectorAll(
    'button:not([disabled]), [href], input:not([disabled]), select:not([disabled]), textarea:not([disabled]), [tabindex]:not([tabindex="-1"])',
  );

  if (!focusable.length) {
    event.preventDefault();
    modal.focus();
    return;
  }

  const first = focusable[0];
  const last = focusable[focusable.length - 1];
  if (event.shiftKey && document.activeElement === first) {
    event.preventDefault();
    last.focus();
  } else if (!event.shiftKey && document.activeElement === last) {
    event.preventDefault();
    first.focus();
  }
}

function emptyPlot(targetId, message) {
  Plotly.react(
    targetId,
    [],
    {
      paper_bgcolor: "rgba(0,0,0,0)",
      plot_bgcolor: "rgba(0,0,0,0)",
      margin: { l: 16, r: 16, t: 16, b: 16 },
      xaxis: { visible: false },
      yaxis: { visible: false },
      annotations: [
        {
          x: 0.5,
          y: 0.5,
          xref: "paper",
          yref: "paper",
          text: message,
          showarrow: false,
          font: { family: "system-ui, sans-serif", size: 13, color: THEME.muted },
        },
      ],
    },
    { responsive: true, displayModeBar: false, scrollZoom: false },
  );
}

function lineTrace(records, xKey, yKey, name, color, percentage = false) {
  return {
    x: records.map((row) => row[xKey]),
    y: records.map((row) => row[yKey]),
    mode: "lines",
    name,
    line: { color, width: 3, shape: "spline" },
    hovertemplate: percentage
      ? `<b>${name}</b><br>%{x}: %{y:.1%}<extra></extra>`
      : `<b>${name}</b><br>%{x}: %{y:.2f}<extra></extra>`,
  };
}

function baseLayout(extra = {}) {
  return {
    paper_bgcolor: "rgba(0,0,0,0)",
    plot_bgcolor: "rgba(0,0,0,0)",
    margin: { l: 46, r: 28, t: 8, b: 42 },
    font: { family: "system-ui, sans-serif", color: THEME.muted },
    xaxis: {
      gridcolor: THEME.grid,
      zerolinecolor: "rgba(148,163,184,0.12)",
      linecolor: THEME.grid,
      ticks: "",
      tickfont: { family: "SFMono-Regular, ui-monospace, monospace", size: 11, color: THEME.dim },
    },
    yaxis: {
      gridcolor: THEME.grid,
      zerolinecolor: "rgba(148,163,184,0.12)",
      linecolor: THEME.grid,
      ticks: "",
      tickfont: { family: "SFMono-Regular, ui-monospace, monospace", size: 11, color: THEME.dim },
    },
    legend: {
      orientation: "h",
      yanchor: "bottom",
      y: 1.02,
      xanchor: "left",
      x: 0,
      font: { color: THEME.muted, size: 12 },
    },
    hoverlabel: {
      bgcolor: THEME.hover,
      bordercolor: "rgba(34,211,238,0.20)",
      font: { family: "system-ui, sans-serif", color: THEME.inkBright, size: 13 },
    },
    transition: { duration: 300, easing: "cubic-in-out" },
    ...extra,
  };
}

function renderFailure(error) {
  document.body.innerHTML = `<pre style="padding:24px;color:#fb7185;background:#0f172a;font-family:ui-monospace,monospace;min-height:100vh;">仪表盘加载失败：\n${escapeHtml(
    String(error),
  )}</pre>`;
}

function objectiveLabel(value) {
  return OBJECTIVE_META[normalizeObjective(value)]?.label ?? "优化";
}

function objectiveRank(value) {
  return normalizeObjective(value) === "maximin" ? 2 : 1;
}

function normalizeObjective(value) {
  const key = safeLower(value);
  return OBJECTIVE_ALIASES[key] ?? "max_output";
}

function makeScenarioId(objective, budgetMultiplier, index) {
  return `${objective}_${budgetMultiplier.toFixed(1).replace(".", "p")}_${index + 1}`;
}

function budgetLabel(value) {
  const numeric = normalizeBudget(value);
  const delta = (numeric - 1) * 100;
  if (Math.abs(delta) < 1e-9) {
    return "当前预算";
  }
  return `${delta > 0 ? "+" : ""}${delta.toFixed(0)}% 预算`;
}

function normalizeBudget(value) {
  return Number.parseFloat(value ?? 1) || 1;
}

function getScaleBounds(values, diverging = false) {
  const numeric = values.filter((value) => value != null && Number.isFinite(value));
  if (!numeric.length) {
    return {};
  }

  if (!diverging) {
    return { zmin: Math.min(...numeric), zmax: Math.max(...numeric) };
  }

  const bound = Math.max(...numeric.map((value) => Math.abs(value)));
  return { zmin: -bound, zmax: bound, zmid: 0 };
}

function getRiskName(riskCode) {
  const row = (store.riskLatest.available_risks ?? []).find((risk) => risk.risk_code === riskCode);
  return translateRiskName(row?.risk_name ?? riskCode);
}

function colorFromPalette(index) {
  const palette = [THEME.cyan, THEME.blue, THEME.teal, THEME.violet, THEME.amber, THEME.rose];
  return palette[index % palette.length];
}

function countryLabel(record) {
  const iso3 = record?.iso3;
  if (iso3) {
    return translateCountryIso3(iso3);
  }
  return translateCountryName(record?.country_name ?? record?.name ?? record?.iso3);
}

const COUNTRY_NAME_OVERRIDES = {
  CHN: "中国大陆",
};

function translateCountryIso3(iso3) {
  const upper = String(iso3 ?? "").toUpperCase();
  if (COUNTRY_NAME_OVERRIDES[upper]) return COUNTRY_NAME_OVERRIDES[upper];
  const iso2 = ISO3_TO_ISO2[upper];
  const translated = iso2 && DISPLAY_NAMES_ZH ? DISPLAY_NAMES_ZH.of(iso2) : "";
  return translated || upper || NO_DATA_LABEL;
}

function translateCountryName(name) {
  if (!name) return NO_DATA_LABEL;
  const raw = String(name).trim();
  const exact = (store.overview?.countries ?? []).find((country) => country.country_name === raw);
  if (exact?.iso3) {
    return translateCountryIso3(exact.iso3);
  }
  if (raw.length === 3 && ISO3_TO_ISO2[raw.toUpperCase()]) {
    return translateCountryIso3(raw);
  }
  return raw;
}

function translateRiskName(name) {
  if (!name) return NO_DATA_LABEL;
  return RISK_LABELS[String(name).trim()] ?? String(name).trim();
}

function translateSankeyNode(node) {
  if (!node) return NO_DATA_LABEL;
  if (REGION_LABELS[node]) return REGION_LABELS[node];
  return translateRiskName(node);
}

function regionLabel(value) {
  if (!value) return NO_DATA_LABEL;
  return REGION_LABELS[value] ?? String(value);
}

function incomeLabel(value) {
  if (!value) return NO_DATA_LABEL;
  return INCOME_LABELS[value] ?? String(value);
}

function provinceLabel(value) {
  if (!value) return NO_DATA_LABEL;
  // Handle English names → Chinese (PROVINCE_LABELS map)
  if (PROVINCE_LABELS[value]) return PROVINCE_LABELS[value];
  // Chinese names are passed through directly (from new province data)
  return String(value);
}

function resolveProvinceInput(input) {
  const query = safeLower(input);
  const provinces = store.chinaDeepDive?.provinces ?? [];
  return (
    provinces.find((p) => {
      const name = p.province ?? p;
      return safeLower(name) === query || safeLower(provinceLabel(name)) === query;
    })?.province ??
    provinces.find((p) => {
      const name = p.province ?? p;
      return safeLower(name).includes(query) || safeLower(provinceLabel(name)).includes(query);
    })?.province ??
    null
  );
}

function normalizeNumber(value) {
  if (value == null || value === "") {
    return null;
  }
  const numeric = Number(value);
  return Number.isFinite(numeric) ? numeric : null;
}

function percentValue(value) {
  return value == null ? null : Number(value) * 100;
}

function formatDecimal(value) {
  return value == null ? NO_DATA_LABEL : Number(value).toFixed(2);
}

function formatInteger(value) {
  return value == null ? NO_DATA_LABEL : Number(value).toLocaleString("zh-CN", { maximumFractionDigits: 0 });
}

function formatShare(value) {
  return value == null ? NO_DATA_LABEL : `${(Number(value) * 100).toFixed(1)}%`;
}

function formatPercentValue(value) {
  return value == null ? NO_DATA_LABEL : `${Number(value).toFixed(1)}%`;
}

function formatSigned(value) {
  return value == null ? NO_DATA_LABEL : `${Number(value) > 0 ? "+" : ""}${Number(value).toFixed(2)}`;
}

function formatSignedPercent(value) {
  return value == null ? NO_DATA_LABEL : `${Number(value) > 0 ? "+" : ""}${Number(value).toFixed(1)}%`;
}

function formatCurrency(value) {
  if (value == null) {
    return NO_DATA_LABEL;
  }
  return `${Number(value).toLocaleString("zh-CN", { maximumFractionDigits: 0 })} 美元`;
}

function formatCompact(value) {
  if (value == null) {
    return NO_DATA_LABEL;
  }
  const number = Number(value);
  if (Math.abs(number) >= 1_000_000_000) {
    return `${(number / 1_000_000_000).toFixed(2)} 十亿`;
  }
  if (Math.abs(number) >= 1_000_000) {
    return `${(number / 1_000_000).toFixed(2)} 百万`;
  }
  if (Math.abs(number) >= 1_000) {
    return `${(number / 1_000).toFixed(1)} 千`;
  }
  return number.toFixed(0);
}

function uniqueValues(values) {
  return [...new Set(values)];
}

function sumValues(values) {
  return values.reduce((sum, value) => sum + (value ?? 0), 0);
}

function safeLower(value) {
  return value == null ? "" : String(value).toLowerCase();
}

function escapeHtml(value) {
  return String(value ?? "")
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#39;");
}

function iso3ToFlag(iso3) {
  if (!iso3 || iso3.length !== 3) return null;
  const iso2 = ISO3_TO_ISO2[iso3.toUpperCase()];
  if (!iso2) return null;
  return String.fromCodePoint(
    ...iso2.toUpperCase().split("").map((c) => 0x1f1e6 + c.charCodeAt(0) - 65)
  );
}

function debounce(fn, wait) {
  let timeout = null;
  return (...args) => {
    window.clearTimeout(timeout);
    timeout = window.setTimeout(() => fn(...args), wait);
  };
}
