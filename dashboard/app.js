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
    metrics: ["life_expectancy", "ncd_share", "communicable_share", "health_exp_pct_gdp",
              "infant_mortality", "under5_mortality", "adult_mortality_male", "adult_mortality_female",
              "physicians_per_1000", "nurses_per_1000", "beds_per_1000", "health_exp_per_capita", "gdp_per_capita",
              "basic_water_pct", "basic_sanitation_pct", "measles_immunization_pct",
              "urban_population_pct", "fertility_rate", "population", "uhc_index",
              "cardiovascular_share", "cancer_share", "diabetes_kidney_share",
              "respiratory_chronic_share", "maternal_neonatal_share"],
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
    metrics: ["change_pct", "gap", "gap_grade_num", "gap_abs_millions", "efficiency", "uhc_index", "physicians_per_1000", "nurses_per_1000", "beds_per_1000", "health_exp_per_capita", "gdp_per_capita"],
  },
  dim4: {
    label: "中国大陆聚焦",
    defaultMetric: "prov_gap",
    mapTitle: "中国大陆省级卫生资源配置分析",
    note: "探索中国大陆31个省级行政区的卫生资源配置、效率与优化方案。",
    metrics: ["prov_gap", "prov_efficiency", "prov_life_expectancy", "prov_infant_mortality", "prov_maternal_mortality", "prov_under5_mortality", "prov_personnel_per_1000", "prov_hospital_beds_per_1000", "prov_physicians_per_1000", "prov_nurses_per_1000", "prov_health_exp", "prov_gdp_per_capita", "prov_rural_income", "prov_optimization_change", "prov_elderly_share", "prov_urbanization", "prov_basic_insurance", "prov_primary_care", "prov_hypertension", "prov_diabetes", "prov_obesity"],
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
    colorscale: [[0, "#EEF5FB"], [0.25, "#CBDEF0"], [0.5, "#8FB8DE"], [0.75, "#4A8FC4"], [1, "#0B6FB8"]],
    formatter: (value) => (value == null ? NO_DATA_LABEL : `${Number(value).toFixed(1)} 岁`),
    accessor: (row) => row.life_expectancy,
  },
  ncd_share: {
    label: "非传染性疾病占比",
    colorscale: [[0, "#F4F2FA"], [0.25, "#DCCFEC"], [0.5, "#B097D0"], [0.75, "#7D61B0"], [1, "#5A3F9E"]],
    formatter: (value) => formatShare(value),
    accessor: (row) => row.ncd_share,
  },
  communicable_share: {
    label: "传染性疾病占比",
    colorscale: [[0, "#FDF6EA"], [0.25, "#F5DFB0"], [0.5, "#E7B76E"], [0.75, "#C68A2F"], [1, "#8A5C16"]],
    formatter: (value) => formatShare(value),
    accessor: (row) => row.communicable_share,
  },
  health_exp_pct_gdp: {
    label: "卫生支出占GDP比重",
    colorscale: [[0, "#F0F9F5"], [0.25, "#C8E6D7"], [0.5, "#8DCAB0"], [0.75, "#4CB58F"], [1, "#1F7E5C"]],
    formatter: (value) => formatPercentValue(value),
    accessor: (row) => row.health_exp_pct_gdp,
  },
  share: {
    label: "风险因素占比",
    colorscale: [[0, "#FDF4F1"], [0.25, "#F5CEC0"], [0.5, "#E68A6F"], [0.75, "#B84A2F"], [1, "#7A2815"]],
    formatter: (value) => formatShare(value),
    accessor: (row) => row.share,
  },
  attributable_deaths: {
    label: "风险致死",
    colorscale: [[0, "#EEF5FB"], [0.25, "#CBDEF0"], [0.5, "#8FB8DE"], [0.75, "#D99938"], [1, "#A9701F"]],
    formatter: (value) => formatCompact(value),
    accessor: (row) => row.attributable_deaths,
  },
  change_pct: {
    label: "资源调整方案",
    colorscale: [[0, "#C0432C"], [0.2, "#E86A4F"], [0.45, "#F6C6B7"], [0.5, "#F2F4F8"], [0.55, "#B3D3EC"], [0.8, "#4A8FC4"], [1, "#0B6FB8"]],
    formatter: (value) => formatSignedPercent(value),
    accessor: (row) => row.change_pct,
    diverging: true,
  },
  gap: {
    label: "资源缺口",
    colorscale: [[0, "#C0432C"], [0.2, "#E86A4F"], [0.45, "#F6C6B7"], [0.5, "#F2F4F8"], [0.55, "#B3E2CF"], [0.8, "#4CB58F"], [1, "#1F7E5C"]],
    formatter: (value) => formatSigned(value),
    accessor: (row) => row.gap,
    diverging: true,
  },
  gap_grade_num: {
    label: "资源缺口等级（A–E）",
    colorscale: [
      [0, "#C0432C"], [0.2, "#C0432C"],
      [0.2, "#E7A64A"], [0.4, "#E7A64A"],
      [0.4, "#9AA3B2"], [0.6, "#9AA3B2"],
      [0.6, "#4CB58F"], [0.8, "#4CB58F"],
      [0.8, "#1B9E6A"], [1, "#1B9E6A"],
    ],
    formatter: (value) => {
      const labels = { 1: "E 严重不足", 2: "D 不足", 3: "C 匹配", 4: "B 较充足", 5: "A 富余" };
      return value == null ? NO_DATA_LABEL : (labels[Math.round(value)] ?? NO_DATA_LABEL);
    },
    accessor: (row) => {
      const gradeMap = {
        "E_severe_shortage": 1, "E_critical_shortage": 1, "E_严重不足": 1,
        "D_shortage": 2, "D_不足": 2,
        "C_matched": 3, "C_balanced": 3, "C_匹配": 3,
        "B_slight_surplus": 4, "B_relatively_adequate": 4, "B_较充足": 4,
        "A_surplus": 5, "A_富余": 5,
      };
      const grade = row.gap_grade_en ?? row.gap_grade;
      return grade && grade !== "nan" ? (gradeMap[grade] ?? null) : null;
    },
    colorbarExtra: {
      tickvals: [1, 2, 3, 4, 5],
      ticktext: ["E 严重不足", "D 不足", "C 匹配", "B 较充足", "A 富余"],
    },
    fixedRange: [0.5, 5.5],
  },
  efficiency: {
    label: "资源使用效率",
    colorscale: [[0, "#C0432C"], [0.2, "#E86A4F"], [0.45, "#F6C6B7"], [0.5, "#F2F4F8"], [0.55, "#B3E2CF"], [0.8, "#4CB58F"], [1, "#1F7E5C"]],
    formatter: (value) => formatSigned(value),
    accessor: (row) => row.efficiency,
    diverging: true,
  },
  uhc_index: {
    label: "UHC服务覆盖指数",
    colorscale: [[0, "#F6F3FA"], [0.25, "#DED1EB"], [0.5, "#B399D1"], [0.75, "#8467B4"], [1, "#5A3F9E"]],
    formatter: (value) => value == null ? NO_DATA_LABEL : `${Number(value).toFixed(0)} 分`,
    accessor: (row) => row.uhc_index,
  },
  gap_abs_millions: {
    label: "绝对资源缺口（人口加权）",
    colorscale: [[0, "#FDF4F0"], [0.25, "#F6C6B7"], [0.5, "#E99275"], [0.75, "#D4563A"], [1, "#A0331F"]],
    formatter: (value) => value == null ? NO_DATA_LABEL : `${Number(value).toFixed(1)}`,
    accessor: (row) => row.gap_abs_millions,
    diverging: true,
  },
  health_personnel: {
    label: "卫生人员",
    colorscale: [[0, "#FDF4F0"], [0.25, "#F6C6B7"], [0.5, "#E99275"], [0.75, "#D4563A"], [1, "#A0331F"]],
    formatter: (value) => value == null ? NO_DATA_LABEL : `${formatCompact(value)} 万人`,
    accessor: (row) => row.value,
  },
  health_institutions: {
    label: "卫生机构",
    colorscale: [[0, "#FDF4F0"], [0.25, "#F6C6B7"], [0.5, "#E99275"], [0.75, "#D4563A"], [1, "#A0331F"]],
    formatter: (value) => value == null ? NO_DATA_LABEL : `${formatCompact(value)} 个`,
    accessor: (row) => row.value,
  },
  prov_gap: {
    label: "省级资源缺口",
    colorscale: [[0, "#C0432C"], [0.2, "#E86A4F"], [0.45, "#F6C6B7"], [0.5, "#F2F4F8"], [0.55, "#B3E2CF"], [0.8, "#4CB58F"], [1, "#1F7E5C"]],
    formatter: (value) => formatSigned(value),
    accessor: (row) => row.gap,
    diverging: true,
  },
  prov_efficiency: {
    label: "省级资源效率",
    colorscale: [[0, "#C0432C"], [0.2, "#E86A4F"], [0.45, "#F6C6B7"], [0.5, "#F2F4F8"], [0.55, "#B3E2CF"], [0.8, "#4CB58F"], [1, "#1F7E5C"]],
    formatter: (value) => formatSigned(value),
    accessor: (row) => row.efficiency,
    diverging: true,
  },
  prov_life_expectancy: {
    label: "平均预期寿命",
    colorscale: [[0, "#EEF5FB"], [0.25, "#CBDEF0"], [0.5, "#8FB8DE"], [0.75, "#4A8FC4"], [1, "#0B6FB8"]],
    formatter: (value) => value == null ? NO_DATA_LABEL : `${Number(value).toFixed(1)} 岁`,
    accessor: (row) => row.life_expectancy,
  },
  prov_infant_mortality: {
    label: "婴儿死亡率",
    colorscale: [[0, "#FDF7EA"], [0.25, "#F7DFAA"], [0.5, "#EDBF68"], [0.75, "#D99938"], [1, "#A9701F"]],
    formatter: (value) => value == null ? NO_DATA_LABEL : `${Number(value).toFixed(1)} ‰`,
    accessor: (row) => row.infant_mortality,
  },
  prov_personnel_per_1000: {
    label: "卫生人员密度（每千人）",
    colorscale: [[0, "#F0F9F5"], [0.25, "#C8E6D7"], [0.5, "#8DCAB0"], [0.75, "#4CB58F"], [1, "#1F7E5C"]],
    formatter: (value) => value == null ? NO_DATA_LABEL : `${Number(value).toFixed(2)}/千人`,
    accessor: (row) => row.personnel_per_1000,
  },
  prov_hospital_beds_per_1000: {
    label: "医院床位（每千人）",
    colorscale: [[0, "#F0F9F5"], [0.25, "#C8E6D7"], [0.5, "#8DCAB0"], [0.75, "#4CB58F"], [1, "#1F7E5C"]],
    formatter: (value) => value == null ? NO_DATA_LABEL : `${Number(value).toFixed(2)}/千人`,
    accessor: (row) => row.hospital_beds_per_1000,
  },
  prov_physicians_per_1000: {
    label: "执业医师（每千人）",
    colorscale: [[0, "#EEF5FB"], [0.25, "#CBDEF0"], [0.5, "#8FB8DE"], [0.75, "#4A8FC4"], [1, "#0B6FB8"]],
    formatter: (value) => value == null ? NO_DATA_LABEL : `${Number(value).toFixed(2)}/千人`,
    accessor: (row) => row.physicians_per_1000,
  },
  prov_nurses_per_1000: {
    label: "注册护士（每千人）",
    colorscale: [[0, "#F2F4FB"], [0.25, "#C9D0EC"], [0.5, "#9AA3D8"], [0.75, "#6770B4"], [1, "#3F458A"]],
    formatter: (value) => value == null ? NO_DATA_LABEL : `${Number(value).toFixed(2)}/千人`,
    accessor: (row) => row.nurses_per_1000,
  },
  prov_health_exp: {
    label: "人均卫生支出（元）",
    colorscale: [[0, "#EEF5FB"], [0.25, "#CBDEF0"], [0.5, "#8FB8DE"], [0.75, "#4A8FC4"], [1, "#0B6FB8"]],
    formatter: (value) => value == null ? NO_DATA_LABEL : `¥${Number(value).toLocaleString()}`,
    accessor: (row) => row.health_exp_per_capita,
  },
  prov_gdp_per_capita: {
    label: "人均GDP（元，2023）",
    colorscale: [[0, "#F2F9F2"], [0.25, "#D3E9D4"], [0.5, "#9FCCA5"], [0.75, "#5EB276"], [1, "#1F8540"]],
    formatter: (value) => value == null ? NO_DATA_LABEL : `¥${Number(value).toLocaleString()}`,
    accessor: (row) => row.gdp_per_capita,
  },
  prov_rural_income: {
    label: "农村人均收入（元，2023）",
    colorscale: [[0, "#F4F1F9"], [0.25, "#DBCBEC"], [0.5, "#B395D0"], [0.75, "#875AAB"], [1, "#4E2A7F"]],
    formatter: (value) => value == null ? NO_DATA_LABEL : `¥${Number(value).toLocaleString()}`,
    accessor: (row) => row.rural_income_per_capita,
  },
  prov_maternal_mortality: {
    label: "产妇死亡率（/10万，2020）",
    colorscale: [[0, "#F4FAF5"], [0.25, "#BEDFCA"], [0.5, "#F3D893"], [0.75, "#E48572"], [1, "#8A2818"]],
    formatter: (value) => value == null ? NO_DATA_LABEL : `${Number(value).toFixed(1)}/10万`,
    accessor: (row) => row.maternal_mortality,
  },
  prov_under5_mortality: {
    label: "5岁以下死亡率（‰，2020）",
    colorscale: [[0, "#F4FAF5"], [0.25, "#BEDFCA"], [0.5, "#F3D893"], [0.75, "#E48572"], [1, "#8A2818"]],
    formatter: (value) => value == null ? NO_DATA_LABEL : `${Number(value).toFixed(1)} ‰`,
    accessor: (row) => row.under5_mortality,
  },
  prov_optimization_change: {
    label: "最优化调整方案（%）",
    colorscale: [[0, "#C0432C"], [0.2, "#E86A4F"], [0.45, "#F6C6B7"], [0.5, "#F2F4F8"], [0.55, "#B3D3EC"], [0.8, "#4A8FC4"], [1, "#0B6FB8"]],
    formatter: (value) => formatSignedPercent(value),
    accessor: (row) => row.prov_change_pct,
    diverging: true,
  },
  prov_elderly_share: {
    label: "老龄化率（65岁以上，%，2020）",
    colorscale: [[0, "#F6EFF6"], [0.25, "#E1BDE1"], [0.5, "#BE82BE"], [0.75, "#914891"], [1, "#5B195B"]],
    formatter: (value) => value == null ? NO_DATA_LABEL : `${Number(value).toFixed(1)} %`,
    accessor: (row) => row.elderly_share,
  },
  prov_urbanization: {
    label: "城镇化率（%，2022）",
    colorscale: [[0, "#F0F9F5"], [0.25, "#C8E6D7"], [0.5, "#8DCAB0"], [0.75, "#4CB58F"], [1, "#1F7E5C"]],
    formatter: (value) => value == null ? NO_DATA_LABEL : `${Number(value).toFixed(1)} %`,
    accessor: (row) => row.urbanization_rate,
  },
  prov_basic_insurance: {
    label: "基本医疗保险参保率（%，2022）",
    colorscale: [[0, "#F2F4FB"], [0.25, "#C9D0EC"], [0.5, "#9AA3D8"], [0.75, "#6770B4"], [1, "#3F458A"]],
    formatter: (value) => value == null ? NO_DATA_LABEL : `${Number(value).toFixed(1)} %`,
    accessor: (row) => row.basic_insurance_rate,
  },
  prov_primary_care: {
    label: "基层医疗机构密度（/万人，2020）",
    colorscale: [[0, "#F2F9F2"], [0.25, "#D3E9D4"], [0.5, "#9FCCA5"], [0.75, "#5EB276"], [1, "#1F8540"]],
    formatter: (value) => value == null ? NO_DATA_LABEL : `${Number(value).toFixed(2)} /万人`,
    accessor: (row) => row.primary_care_density,
  },
  prov_hypertension: {
    label: "高血压患病率（%，2018）",
    colorscale: [[0, "#F4FAF5"], [0.25, "#BEDFCA"], [0.5, "#F3D893"], [0.75, "#E48572"], [1, "#8A2818"]],
    formatter: (value) => value == null ? NO_DATA_LABEL : `${Number(value).toFixed(1)} %`,
    accessor: (row) => row.hypertension_prevalence,
    invertGradient: true,
  },
  prov_diabetes: {
    label: "糖尿病患病率（%，2018）",
    colorscale: [[0, "#F4F1F9"], [0.25, "#D5CEEC"], [0.5, "#A494D6"], [0.75, "#6D58B3"], [1, "#3F2584"]],
    formatter: (value) => value == null ? NO_DATA_LABEL : `${Number(value).toFixed(1)} %`,
    accessor: (row) => row.diabetes_prevalence,
    invertGradient: true,
  },
  prov_obesity: {
    label: "超重/肥胖率（BMI≥28，%，2018）",
    colorscale: [[0, "#F4FAF5"], [0.25, "#BEDFCA"], [0.5, "#F3D893"], [0.75, "#E48572"], [1, "#8A2818"]],
    formatter: (value) => value == null ? NO_DATA_LABEL : `${Number(value).toFixed(1)} %`,
    accessor: (row) => row.obesity_prevalence,
    invertGradient: true,
  },
  hdi: {
    label: "人类发展指数",
    colorscale: [[0, "#F2F9F2"], [0.25, "#D3E9D4"], [0.5, "#9FCCA5"], [0.75, "#5EB276"], [1, "#1F8540"]],
    formatter: (value) => (value == null ? NO_DATA_LABEL : Number(value).toFixed(3)),
    accessor: (row) => row.hdi,
  },
  hale: {
    label: "健康预期寿命",
    colorscale: [[0, "#EEF5FB"], [0.25, "#CBDEF0"], [0.5, "#8FB8DE"], [0.75, "#4A8FC4"], [1, "#0B6FB8"]],
    formatter: (value) => (value == null ? NO_DATA_LABEL : `${Number(value).toFixed(1)} 岁`),
    accessor: (row) => row.hale,
  },
  uhc_index: {
    label: "全民健康覆盖指数",
    colorscale: [[0, "#F2F4FB"], [0.25, "#C9D0EC"], [0.5, "#9AA3D8"], [0.75, "#6770B4"], [1, "#3F458A"]],
    formatter: (value) => (value == null ? NO_DATA_LABEL : `${Number(value).toFixed(1)}`),
    accessor: (row) => row.uhc_index,
  },
  pm25: {
    label: "PM2.5 暴露浓度",
    colorscale: [[0, "#FDF6EA"], [0.25, "#F5DFB0"], [0.5, "#E7B76E"], [0.75, "#C68A2F"], [1, "#8A5C16"]],
    formatter: (value) => (value == null ? NO_DATA_LABEL : `${Number(value).toFixed(1)} μg/m³`),
    accessor: (row) => row.pm25,
  },
  doctor_density: {
    label: "医生密度（每万人）",
    colorscale: [[0, "#EEF5FB"], [0.25, "#CBDEF0"], [0.5, "#8FB8DE"], [0.75, "#4A8FC4"], [1, "#0B6FB8"]],
    formatter: (value) => (value == null ? NO_DATA_LABEL : `${Number(value).toFixed(1)}`),
    accessor: (row) => row.doctor_density,
  },
  che_per_capita: {
    label: "人均卫生支出",
    colorscale: [[0, "#EEF5FB"], [0.25, "#CBDEF0"], [0.5, "#8FB8DE"], [0.75, "#4A8FC4"], [1, "#0B6FB8"]],
    formatter: (value) => formatCurrency(value),
    accessor: (row) => row.che_per_capita,
  },
  gdp_per_capita: {
    label: "人均GDP（美元）",
    colorscale: [[0, "#F2F9F2"], [0.25, "#D3E9D4"], [0.5, "#9FCCA5"], [0.75, "#5EB276"], [1, "#1F8540"]],
    formatter: (value) => value == null ? NO_DATA_LABEL : `$${Math.round(Number(value)).toLocaleString()}`,
    accessor: (row) => row.gdp_per_capita,
  },
  health_exp_per_capita: {
    label: "人均卫生支出（美元）",
    colorscale: [[0, "#EEF5FB"], [0.25, "#CBDEF0"], [0.5, "#8FB8DE"], [0.75, "#4A8FC4"], [1, "#0B6FB8"]],
    formatter: (value) => value == null ? NO_DATA_LABEL : `$${Math.round(Number(value)).toLocaleString()}`,
    accessor: (row) => row.health_exp_per_capita,
  },
  adult_mortality_male: {
    label: "男性成人死亡率（‰）",
    colorscale: [[0, "#F4FAF5"], [0.25, "#BEDFCA"], [0.5, "#F3D893"], [0.75, "#E48572"], [1, "#8A2818"]],
    formatter: (value) => value == null ? NO_DATA_LABEL : `${Number(value).toFixed(0)} ‰`,
    accessor: (row) => row.adult_mortality_male,
    invertGradient: true,
  },
  adult_mortality_female: {
    label: "女性成人死亡率（‰）",
    colorscale: [[0, "#F4FAF5"], [0.25, "#BEDFCA"], [0.5, "#F3D893"], [0.75, "#E48572"], [1, "#8A2818"]],
    formatter: (value) => value == null ? NO_DATA_LABEL : `${Number(value).toFixed(0)} ‰`,
    accessor: (row) => row.adult_mortality_female,
    invertGradient: true,
  },
  infant_mortality: {
    label: "婴儿死亡率（‰）",
    colorscale: [[0, "#F4FAF5"], [0.25, "#BEDFCA"], [0.5, "#F3D893"], [0.75, "#E48572"], [1, "#8A2818"]],
    formatter: (value) => value == null ? NO_DATA_LABEL : `${Number(value).toFixed(1)} ‰`,
    accessor: (row) => row.infant_mortality,
    invertGradient: true,
  },
  under5_mortality: {
    label: "5岁以下死亡率（‰）",
    colorscale: [[0, "#F4FAF5"], [0.25, "#BEDFCA"], [0.5, "#F3D893"], [0.75, "#E48572"], [1, "#8A2818"]],
    formatter: (value) => value == null ? NO_DATA_LABEL : `${Number(value).toFixed(1)} ‰`,
    accessor: (row) => row.under5_mortality,
    invertGradient: true,
  },
  basic_water_pct: {
    label: "安全饮水覆盖率（%）",
    colorscale: [[0, "#EEF5FB"], [0.25, "#CBDEF0"], [0.5, "#8FB8DE"], [0.75, "#4A8FC4"], [1, "#0B6FB8"]],
    formatter: (value) => value == null ? NO_DATA_LABEL : `${Number(value).toFixed(1)} %`,
    accessor: (row) => row.basic_water_pct,
  },
  basic_sanitation_pct: {
    label: "基本卫生设施覆盖率（%）",
    colorscale: [[0, "#F0F9F5"], [0.25, "#C8E6D7"], [0.5, "#8DCAB0"], [0.75, "#4CB58F"], [1, "#1F7E5C"]],
    formatter: (value) => value == null ? NO_DATA_LABEL : `${Number(value).toFixed(1)} %`,
    accessor: (row) => row.basic_sanitation_pct,
  },
  measles_immunization_pct: {
    label: "麻疹疫苗接种率（%）",
    colorscale: [[0, "#F2F4FB"], [0.25, "#C9D0EC"], [0.5, "#9AA3D8"], [0.75, "#6770B4"], [1, "#3F458A"]],
    formatter: (value) => value == null ? NO_DATA_LABEL : `${Number(value).toFixed(0)} %`,
    accessor: (row) => row.measles_immunization_pct,
  },
  urban_population_pct: {
    label: "城镇人口比例（%）",
    colorscale: [[0, "#F2F9F2"], [0.25, "#D3E9D4"], [0.5, "#9FCCA5"], [0.75, "#5EB276"], [1, "#1F8540"]],
    formatter: (value) => value == null ? NO_DATA_LABEL : `${Number(value).toFixed(1)} %`,
    accessor: (row) => row.urban_population_pct,
  },
  fertility_rate: {
    label: "总和生育率",
    colorscale: [[0, "#FDF6EA"], [0.25, "#F5DFB0"], [0.5, "#E7B76E"], [0.75, "#C68A2F"], [1, "#8A5C16"]],
    formatter: (value) => value == null ? NO_DATA_LABEL : Number(value).toFixed(2),
    accessor: (row) => row.fertility_rate,
  },
  physicians_per_1000: {
    label: "医生密度（每千人）",
    colorscale: [[0, "#EEF5FB"], [0.25, "#CBDEF0"], [0.5, "#8FB8DE"], [0.75, "#4A8FC4"], [1, "#0B6FB8"]],
    formatter: (value) => value == null ? NO_DATA_LABEL : `${Number(value).toFixed(2)}/千人`,
    accessor: (row) => row.physicians_per_1000,
  },
  beds_per_1000: {
    label: "医院床位（每千人）",
    colorscale: [[0, "#F0F9F5"], [0.25, "#C8E6D7"], [0.5, "#8DCAB0"], [0.75, "#4CB58F"], [1, "#1F7E5C"]],
    formatter: (value) => value == null ? NO_DATA_LABEL : `${Number(value).toFixed(2)}/千人`,
    accessor: (row) => row.beds_per_1000,
  },
  nurses_per_1000: {
    label: "护士密度（每千人）",
    colorscale: [[0, "#EEF5FB"], [0.25, "#CBDEF0"], [0.5, "#8FB8DE"], [0.75, "#4A8FC4"], [1, "#0B6FB8"]],
    formatter: (value) => value == null ? NO_DATA_LABEL : `${Number(value).toFixed(2)}/千人`,
    accessor: (row) => row.nurses_per_1000,
  },
  cardiovascular_share: {
    label: "心血管病死亡占比",
    colorscale: [[0, "#F4F2FA"], [0.25, "#DCCFEC"], [0.5, "#B097D0"], [0.75, "#7D61B0"], [1, "#5A3F9E"]],
    formatter: (value) => formatShare(value),
    accessor: (row) => row.cardiovascular_share,
  },
  cancer_share: {
    label: "癌症死亡占比",
    colorscale: [[0, "#FDF4F0"], [0.25, "#F6C6B7"], [0.5, "#E99275"], [0.75, "#D4563A"], [1, "#A0331F"]],
    formatter: (value) => formatShare(value),
    accessor: (row) => row.cancer_share,
  },
  diabetes_kidney_share: {
    label: "糖尿病/肾病死亡占比",
    colorscale: [[0, "#F0F9F5"], [0.25, "#C8E6D7"], [0.5, "#8DCAB0"], [0.75, "#4CB58F"], [1, "#1F7E5C"]],
    formatter: (value) => formatShare(value),
    accessor: (row) => row.diabetes_kidney_share,
  },
  respiratory_chronic_share: {
    label: "慢性呼吸病死亡占比",
    colorscale: [[0, "#FDF4F0"], [0.25, "#F6C6B7"], [0.5, "#E99275"], [0.75, "#D4563A"], [1, "#A0331F"]],
    formatter: (value) => formatShare(value),
    accessor: (row) => row.respiratory_chronic_share,
  },
  maternal_neonatal_share: {
    label: "孕产妇/新生儿死亡占比",
    colorscale: [[0, "#FDF6EA"], [0.25, "#F5DFB0"], [0.5, "#E7B76E"], [0.75, "#C68A2F"], [1, "#8A5C16"]],
    formatter: (value) => formatShare(value),
    accessor: (row) => row.maternal_neonatal_share,
    invertGradient: true,
  },
  population: {
    label: "人口规模",
    colorscale: [[0, "#F0F9F5"], [0.25, "#C8E6D7"], [0.5, "#8DCAB0"], [0.75, "#4CB58F"], [1, "#1F7E5C"]],
    formatter: (value) => value == null ? NO_DATA_LABEL : (value >= 1e9 ? `${(value / 1e9).toFixed(2)}亿` : value >= 1e6 ? `${(value / 1e6).toFixed(1)}百万` : `${Math.round(value / 1000)}千`),
    accessor: (row) => row.population,
  },
};

const THEME = {
  ink: "#0F172A",
  inkBright: "#0B1220",
  inkBody: "#1F2937",
  muted: "#4B5563",
  dim: "#6B7280",
  placeholder: "#9CA3AF",
  surface: "#FFFFFF",
  surfaceAlt: "#F2F4F8",
  line: "#E3E7EE",
  grid: "#E3E7EE",
  gridSoft: "#EEF1F6",
  primary: "#0B6FB8",
  primaryInk: "#084E82",
  primarySoft: "#E6F0F8",
  cyan: "#0B6FB8",
  highlight: "#D81B60",
  highlightInk: "#A01145",
  teal: "#4CB58F",
  blue: "#3A8CCF",
  amber: "#E7A64A",
  rose: "#E86A4F",
  violet: "#6D5FB0",
  coral: "#E86A4F",
  emerald: "#4CB58F",
  critical: "#C0432C",
  positive: "#1B9E6A",
  regions: {
    AFRO: "#6D5FB0",
    AMRO: "#E86A4F",
    EMRO: "#B87FC0",
    EURO: "#3A8CCF",
    SEARO: "#4CB58F",
    WPRO: "#E7A64A",
  },
  hover: "rgba(255,255,255,0.98)",
};

const FONT_FAMILY_DISPLAY = "\"Alibaba PuHuiTi 3.0\", \"PingFang SC\", \"Hiragino Sans GB\", system-ui, sans-serif";
const FONT_FAMILY_BODY = FONT_FAMILY_DISPLAY;
const FONT_FAMILY_MONO = "\"IBM Plex Mono\", \"SF Mono\", Menlo, monospace";

const OBJECTIVE_META = {
  max_output: {
    label: "最大化总产出（资金）",
    note: "功利主义目标：将资金优先分配至边际健康产出最高的省份/国家（类似「水填充」算法），以最大化全系统总健康产出。优先受益方为投入边际效率高的中低收入地区。",
  },
  maximin: {
    label: "最小化不平等（资金）",
    note: "罗尔斯正义目标：通过资金再分配优先提升最弱势省份的健康水平，实现「最大化最低产出」。通过减少资源集中、向低产出地区再分配来缩小健康不平等。",
  },
  max_output_personnel: {
    label: "最大化总产出（人力）",
    note: "功利主义目标：将卫生人力资源优先分配至边际健康产出最高的省份，以最大化全系统总健康产出。优先受益方为人力资源边际效率高的欠发达省份。",
  },
  maximin_personnel: {
    label: "最小化不平等（人力）",
    note: "罗尔斯正义目标：通过卫生人力再分配优先提升最弱势省份的健康水平，实现「最大化最低产出」。关注人力资源的公平分布，减少城乡和区域间卫生服务可及性差距。",
  },
};

const OBJECTIVE_ALIASES = {
  max_output: "max_output",
  maximize_aggregate_output: "max_output",
  maximize_need_weighted_health_output: "max_output",
  projected_need_weighted_allocation: "max_output",
  maximin: "maximin",
  max_output_personnel: "max_output_personnel",
  maximin_personnel: "maximin_personnel",
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

function updateSliderFill(slider) {
  const min = Number(slider.min) || 2000;
  const max = Number(slider.max) || 2023;
  const val = Number(slider.value);
  const pct = ((val - min) / (max - min)) * 100;
  slider.style.setProperty("--slider-fill", `${pct.toFixed(1)}%`);
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

  initCombobox();

  const yearSliderEl = document.getElementById("year-slider");
  updateSliderFill(yearSliderEl);

  yearSliderEl.addEventListener("input", (event) => {
    state.year = Number(event.target.value);
    document.getElementById("year-display").textContent = state.year;
    updateSliderFill(event.target);
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

function getCountryOptions() {
  return (store.overview.countries ?? [])
    .map((country) => ({
      id: country.iso3,
      name: countryLabel(country),
      code: country.iso3,
    }))
    .sort((a, b) => a.name.localeCompare(b.name, "zh-Hans-CN"));
}

function getProvinceOptions() {
  const provinces = store.chinaDeepDive?.provinces ?? [];
  return provinces
    .map((p) => {
      const key = p.province ?? p;
      return { id: key, name: provinceLabel(key), code: "" };
    })
    .sort((a, b) => a.name.localeCompare(b.name, "zh-Hans-CN"));
}

function selectCountry(iso3) {
  if (!iso3) return;
  state.country = iso3;
  renderPanels();
  updateMapHighlight(iso3);
  openSpotlightModal(iso3);
}

function selectProvince(name) {
  if (!name) return;
  state.province = name;
  renderPanels();
  renderChinaMap();
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
  syncLayoutMode();
  syncControls();
  renderSummaryStrip();
  renderMap();
  renderPanels();
}

function syncLayoutMode() {
  const grid = document.querySelector(".dashboard-grid");
  grid?.classList.toggle("dim4-layout", state.dimension === "dim4");
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
    updateSliderFill(slider);
  } else if (state.dimension === "dim5" && store.bubbleYears.length > 1) {
    sliderGroup.style.display = "flex";
    const slider = document.getElementById("year-slider");
    slider.min = store.bubbleYears[0];
    slider.max = store.bubbleYears[store.bubbleYears.length - 1];
    slider.value = state.year;
    document.getElementById("year-display").textContent = state.year;
    updateSliderFill(slider);
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
  // Delegates to the combobox controller so dim1-3,5 and dim4 share one UI.
  syncCombobox();
}

function syncProvinceSearch() {
  syncCombobox();
}

function syncCombobox() {
  if (!comboboxController) return;
  comboboxController.refresh();
}

// ── Combobox controller ───────────────────────────────────────────
// Single-click country/province picker. Focus opens the listbox with all
// options; typing filters; clicking or pressing Enter on a highlighted row
// locks the selection immediately — no separate 定位 button.

let comboboxController = null;

function initCombobox() {
  const root = document.getElementById("country-combobox");
  const input = document.getElementById("country-search");
  const listbox = document.getElementById("country-listbox");
  const clearBtn = document.getElementById("country-clear");
  const label = document.getElementById("country-search-label");
  if (!root || !input || !listbox || !clearBtn) return;

  let options = [];
  let filtered = [];
  let activeIndex = -1;
  let open = false;
  let query = "";
  let suppressNextFocusOpen = false;

  const modeConfig = () => {
    const isProvince = state.dimension === "dim4";
    return {
      isProvince,
      placeholder: isProvince ? "搜索省份" : "搜索国家或地区",
      labelText: isProvince ? "定位省份" : "定位国家",
      options: isProvince ? getProvinceOptions() : getCountryOptions(),
      selectedId: isProvince ? state.province : state.country,
      select: isProvince ? selectProvince : selectCountry,
      displayFor: (opt) => opt.code ? `${opt.name} (${opt.code})` : opt.name,
    };
  };

  let cfg = modeConfig();

  function getSelectedOption() {
    return cfg.options.find((o) => o.id === cfg.selectedId) ?? null;
  }

  function matchesQuery(opt, q) {
    if (!q) return true;
    const name = opt.name.toLowerCase();
    const code = (opt.code || "").toLowerCase();
    return name.includes(q) || code.includes(q);
  }

  function highlightMatch(text, q) {
    if (!q) return escapeHtml(text);
    const idx = text.toLowerCase().indexOf(q);
    if (idx < 0) return escapeHtml(text);
    const before = escapeHtml(text.slice(0, idx));
    const match = escapeHtml(text.slice(idx, idx + q.length));
    const after = escapeHtml(text.slice(idx + q.length));
    return `${before}<span class="opt-match">${match}</span>${after}`;
  }

  function renderListbox() {
    if (!filtered.length) {
      listbox.innerHTML = `<li class="combobox-empty">无匹配结果</li>`;
      return;
    }
    const q = query;
    listbox.innerHTML = filtered.map((opt, idx) => {
      const isSelected = opt.id === cfg.selectedId;
      const isActive = idx === activeIndex;
      const cls = [
        "combobox-option",
        isSelected ? "is-selected" : "",
        isActive ? "is-active" : "",
      ].filter(Boolean).join(" ");
      const codeSpan = opt.code ? `<span class="opt-code">${escapeHtml(opt.code)}</span>` : "";
      return `<li class="${cls}" role="option" aria-selected="${isSelected}" data-index="${idx}">
        <span class="opt-name">${highlightMatch(opt.name, q)}</span>
        ${codeSpan}
      </li>`;
    }).join("");
  }

  function applyFilter() {
    filtered = cfg.options.filter((o) => matchesQuery(o, query));
    if (activeIndex >= filtered.length) activeIndex = filtered.length - 1;
    if (activeIndex < 0 && filtered.length) activeIndex = 0;
    renderListbox();
    scrollActiveIntoView();
  }

  function scrollActiveIntoView() {
    if (!open || activeIndex < 0) return;
    const el = listbox.querySelector(`[data-index="${activeIndex}"]`);
    if (el) el.scrollIntoView({ block: "nearest" });
  }

  function openListbox() {
    if (open) return;
    open = true;
    root.dataset.open = "true";
    root.classList.add("is-open");
    input.setAttribute("aria-expanded", "true");
    listbox.hidden = false;

    // Preselect the currently-locked option if no query
    if (!query) {
      const sel = cfg.selectedId;
      const idx = filtered.findIndex((o) => o.id === sel);
      activeIndex = idx >= 0 ? idx : (filtered.length ? 0 : -1);
      renderListbox();
      scrollActiveIntoView();
    }
  }

  function closeListbox() {
    if (!open) return;
    open = false;
    root.dataset.open = "false";
    root.classList.remove("is-open");
    input.setAttribute("aria-expanded", "false");
    listbox.hidden = true;
  }

  function commit(idx) {
    const opt = filtered[idx];
    if (!opt) return;
    cfg.select(opt.id);
    query = "";
    input.value = cfg.displayFor(opt);
    clearBtn.hidden = !input.value;
    closeListbox();
    input.blur();
  }

  function updateClearVisibility() {
    clearBtn.hidden = !input.value;
  }

  function resetInputFromSelection() {
    const sel = getSelectedOption();
    input.value = sel ? cfg.displayFor(sel) : "";
    query = "";
    updateClearVisibility();
  }

  // ── Event wiring ────────────────────────────────────────────
  input.addEventListener("focus", () => {
    if (suppressNextFocusOpen) {
      suppressNextFocusOpen = false;
      return;
    }
    // When the input shows the currently locked selection, focusing should
    // show the full list (not a filter for the current value). We reset query.
    query = "";
    applyFilter();
    openListbox();
    // Select all text so typing replaces it immediately
    requestAnimationFrame(() => input.select());
  });

  input.addEventListener("click", () => {
    if (!open) {
      query = "";
      applyFilter();
      openListbox();
    }
  });

  input.addEventListener("input", () => {
    query = input.value.trim().toLowerCase();
    if (!open) openListbox();
    applyFilter();
    updateClearVisibility();
  });

  input.addEventListener("keydown", (event) => {
    if (event.key === "ArrowDown") {
      event.preventDefault();
      if (!open) {
        openListbox();
        return;
      }
      if (filtered.length) {
        activeIndex = (activeIndex + 1) % filtered.length;
        renderListbox();
        scrollActiveIntoView();
      }
    } else if (event.key === "ArrowUp") {
      event.preventDefault();
      if (!open) {
        openListbox();
        return;
      }
      if (filtered.length) {
        activeIndex = (activeIndex - 1 + filtered.length) % filtered.length;
        renderListbox();
        scrollActiveIntoView();
      }
    } else if (event.key === "Enter") {
      if (open && activeIndex >= 0) {
        event.preventDefault();
        commit(activeIndex);
      }
    } else if (event.key === "Escape") {
      if (open) {
        event.preventDefault();
        closeListbox();
        resetInputFromSelection();
      }
    } else if (event.key === "Tab") {
      closeListbox();
    }
  });

  input.addEventListener("blur", (event) => {
    // Delay so option mousedown (which happens before blur) can commit first
    setTimeout(() => {
      if (!root.contains(document.activeElement)) {
        closeListbox();
        // If the user typed something non-matching, restore the locked value
        const sel = getSelectedOption();
        if (sel && input.value !== cfg.displayFor(sel)) {
          input.value = cfg.displayFor(sel);
          query = "";
          updateClearVisibility();
        }
      }
    }, 120);
  });

  listbox.addEventListener("mousedown", (event) => {
    // Prevent input blur before click handler fires
    event.preventDefault();
  });

  listbox.addEventListener("click", (event) => {
    const li = event.target.closest(".combobox-option");
    if (!li) return;
    const idx = Number(li.dataset.index);
    if (!Number.isNaN(idx)) commit(idx);
  });

  listbox.addEventListener("mousemove", (event) => {
    const li = event.target.closest(".combobox-option");
    if (!li) return;
    const idx = Number(li.dataset.index);
    if (!Number.isNaN(idx) && idx !== activeIndex) {
      activeIndex = idx;
      renderListbox();
    }
  });

  clearBtn.addEventListener("click", () => {
    input.value = "";
    query = "";
    updateClearVisibility();
    applyFilter();
    openListbox();
    suppressNextFocusOpen = true;
    input.focus();
  });

  document.addEventListener("click", (event) => {
    if (!root.contains(event.target)) closeListbox();
  });

  comboboxController = {
    refresh() {
      cfg = modeConfig();
      if (label) label.textContent = cfg.labelText;
      input.placeholder = cfg.placeholder;
      resetInputFromSelection();
      query = "";
      filtered = cfg.options.slice();
      activeIndex = -1;
      if (open) applyFilter();
    },
  };

  comboboxController.refresh();
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

  // Cap: if a fade batch has been running for >220ms, render immediately on next tick
  const now = Date.now();
  if (!renderPanels._fadeStart) renderPanels._fadeStart = now;
  const elapsed = now - renderPanels._fadeStart;
  const delay = elapsed > 220 ? 0 : 120;

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
    renderPanels._fadeStart = null;
  }, delay);
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
  const bounds = metric.fixedRange
    ? { zmin: metric.fixedRange[0], zmax: metric.fixedRange[1], zmid: null }
    : getScaleBounds(values, metric.diverging);
  const selected = records.find((row) => row.iso3 === state.country);
  const colorbarBase = {
    title: metric.label,
    thickness: 12,
    len: 0.68,
    x: 0.02,
    xanchor: "left",
    tickfont: { family: "SFMono-Regular, ui-monospace, monospace", size: 11, color: THEME.muted },
    titlefont: { family: "system-ui, sans-serif", size: 12, color: THEME.muted },
    outlinewidth: 0,
    ...(metric.colorbarExtra ?? {}),
  };

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
              row.iso3 === state.country ? "rgba(241,174,40,0.92)" : "rgba(198,204,212,0.9)",
            ),
            width: records.map((row) => (row.iso3 === state.country ? 2.5 : 0.4)),
          },
        },
        colorbar: colorbarBase,
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
          line: { color: "rgba(241,174,40,0.98)", width: 3 },
        },
      },
    ],
    {
      paper_bgcolor: "rgba(0,0,0,0)",
      plot_bgcolor: "rgba(0,0,0,0)",
      margin: { l: 0, r: 0, t: 0, b: 0 },
      geo: {
        projection: { type: "robinson", scale: 1.06 },
        showframe: false,
        showcountries: true,
        countrycolor: "#D7DDE5",
        showcoastlines: true,
        coastlinecolor: "#C6CCD4",
        showocean: false,
        landcolor: "#F4F6FA",
        bgcolor: "rgba(0,0,0,0)",
        lakecolor: "#FFFFFF",
      },
      font: { family: FONT_FAMILY_BODY, color: THEME.inkBody },
      hoverlabel: {
        bgcolor: "#FFFFFF",
        bordercolor: THEME.line,
        font: { family: FONT_FAMILY_BODY, color: THEME.ink, size: 13 },
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

  const allVals = geojson.features
    .map((feature) => provinceValues[feature.properties?.name])
    .filter((value) => value != null && Number.isFinite(value));
  const isDivergent = metric.diverging || isOptMetric;
  const bounds = metric.fixedRange
    ? { zmin: metric.fixedRange[0], zmax: metric.fixedRange[1], zmid: isDivergent ? 0 : null }
    : getScaleBounds(allVals, isDivergent);
  const zmin = bounds.zmin;
  const zmax = bounds.zmax;
  // Use plain polygon fills on Cartesian axes. Plotly's geo-based traces render this
  // province GeoJSON as bbox-backed compound paths, which is why dim4 was painting a
  // large rectangle instead of individual provinces.
  const traces = [];

  if (allVals.length) {
    traces.push({
      type: "scatter",
      x: [104, 105],
      y: [36, 36],
      mode: "markers",
      hoverinfo: "skip",
      showlegend: false,
      marker: {
        size: 0.1,
        opacity: 0,
        color: [zmin, zmax],
        cmin: zmin,
        cmax: zmax,
        cmid: isDivergent ? 0 : undefined,
        colorscale: metric.colorscale,
        showscale: true,
        colorbar: {
          title: metric.label,
          thickness: 12,
          len: 0.72,
          x: 0.02,
          xanchor: "left",
          tickfont: { family: "SFMono-Regular, ui-monospace, monospace", size: 11, color: THEME.muted },
          titlefont: { family: "system-ui, sans-serif", size: 12, color: THEME.muted },
          outlinewidth: 0,
          ...(metric.colorbarExtra ?? {}),
        },
      },
    });
  }

  for (const feature of geojson.features) {
    const name = feature.properties?.name;
    if (!name) continue;

    const { lon, lat } = chinaGeometryToLonLat(feature.geometry);
    if (!lon.length || !lat.length) continue;

    const val = provinceValues[name];
    const hasData = val != null && Number.isFinite(val);
    const provData = store.chinaProvinceIndex.get(name) ?? {};
    const isSelected = name === state.province;

    traces.push({
      type: "scatter",
      name,
      x: lon,
      y: lat,
      mode: "lines",
      fill: "toself",
      fillcolor: hasData
        ? colorFromScale(val, metric.colorscale, zmin, zmax)
        : "rgba(100,116,139,0.34)",
      hoveron: "fills",
      hovertemplate: hasData
        ? `<b>${name}</b><br>` +
          `地区：${provData.region ?? ""}（${provData.region_en ?? ""}）<br>` +
          `${metric.label}：${metric.formatter(val)}<br>` +
          `类型：${provData.quadrant ?? "—"}<br>` +
          `预期寿命：${provData.life_expectancy != null ? provData.life_expectancy.toFixed(1) + " 岁" : "暂无"}<extra></extra>`
        : `<b>${name}</b><br>暂无数据<extra></extra>`,
      showlegend: false,
      line: {
        color: isSelected
          ? "rgba(20,184,166,0.90)"
          : hasData
            ? "#9AA3B2"
            : "#6B7280",
        width: isSelected ? 2.5 : 0.85,
      },
    });
  }

  Plotly.react(
    "map-chart",
    traces,
    {
      paper_bgcolor: "rgba(0,0,0,0)",
      plot_bgcolor: "rgba(0,0,0,0)",
      margin: { l: 0, r: 0, t: 4, b: 0 },
      xaxis: {
        visible: false,
        showgrid: false,
        zeroline: false,
        fixedrange: true,
        range: [72, 136],
      },
      yaxis: {
        visible: false,
        showgrid: false,
        zeroline: false,
        fixedrange: true,
        range: [15, 55],
        scaleanchor: "x",
        scaleratio: 1.2,
      },
      font: { family: "system-ui, sans-serif", color: THEME.ink },
      hoverlabel: {
        bgcolor: THEME.hover,
        bordercolor: THEME.line,
        font: { family: "system-ui, sans-serif", color: THEME.inkBright, size: 13 },
      },
    },
    { responsive: true, displayModeBar: false, scrollZoom: false },
  );

  const mapNode = document.getElementById("map-chart");
  if (!mapNode.dataset.dim4Bound) {
    mapNode.on("plotly_click", (event) => {
      if (state.dimension !== "dim4") return;
      const province = event?.points?.[0]?.data?.name;
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
          row.iso3 === iso3 ? "rgba(241,174,40,0.92)" : "rgba(198,204,212,0.9)",
        ),
      ],
      "marker.line.width": [records.map((row) => (row.iso3 === iso3 ? 2.5 : 0.4))],
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
    const QUAD_ZH_SHORT = {
      "Q1_high_input_high_output": "Q1 高投入高产出",
      "Q2_low_input_high_output": "Q2 低投入高产出",
      "Q3_high_input_low_output": "Q3 高投入低产出",
      "Q4_low_input_low_output": "Q4 低投入低产出",
    };
    const GAP_GRADE_ZH = {
      "A_surplus": "A 富余", "A_富余": "A 富余",
      "B_slight_surplus": "B 较充足", "B_较充足": "B 较充足",
      "B_relatively_adequate": "B 较充足",
      "C_matched": "C 匹配", "C_匹配": "C 匹配",
      "C_balanced": "C 匹配",
      "D_shortage": "D 不足", "D_不足": "D 不足",
      "E_severe_shortage": "E 严重不足", "E_严重不足": "E 严重不足",
      "E_critical_shortage": "E 严重不足",
    };
    return [
      `<b>${escapeHtml(countryLabel(row))}</b>`,
      `地区：${escapeHtml(regionLabel(row.who_region))} / ${escapeHtml(incomeLabel(row.wb_income))}`,
      `${METRIC_META[state.metric].label}: ${escapeHtml(
        METRIC_META[state.metric].formatter(METRIC_META[state.metric].accessor(row)),
      )}`,
      row.quadrant ? `类型：${escapeHtml(QUAD_ZH_SHORT[row.quadrant] ?? row.quadrant)}` : "",
      row.gap_grade || row.gap_grade_en ? `缺口等级：${escapeHtml(GAP_GRADE_ZH[row.gap_grade_en ?? row.gap_grade] ?? row.gap_grade ?? "")}` : "",
      `缺口：${escapeHtml(formatSigned(row.gap))}`,
      `情景调整：${escapeHtml(formatSignedPercent(row.change_pct))}`,
    ].filter(Boolean).join("<br>");
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

  const flag = iso3ToFlag(state.country);
  const nameText = countryLabel(meta) || state.country;
  document.getElementById("country-title").textContent = flag ? `${flag} ${nameText}` : nameText;
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
      ...(latest.infant_mortality != null ? [["婴儿死亡率", `${Number(latest.infant_mortality).toFixed(1)} ‰`, "rose"]] : []),
      ...(latest.under5_mortality != null ? [["5岁以下死亡率", `${Number(latest.under5_mortality).toFixed(1)} ‰`, "amber"]] : []),
      ...(latest.physicians_per_1000 != null ? [["医生密度", `${Number(latest.physicians_per_1000).toFixed(2)}/千人`, "teal"]] : []),
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
      ["农村人均收入", provData.rural_income_per_capita != null ? `¥${Math.round(provData.rural_income_per_capita).toLocaleString()}` : NO_DATA_LABEL, "violet"],
      ["产妇死亡率", provData.maternal_mortality != null ? `${provData.maternal_mortality.toFixed(1)}/10万` : NO_DATA_LABEL, "rose"],
      ["5岁以下死亡率", provData.under5_mortality != null ? `${provData.under5_mortality.toFixed(1)} ‰` : NO_DATA_LABEL, "amber"],
      ["老龄化率", provData.elderly_share != null ? `${provData.elderly_share.toFixed(1)} %` : NO_DATA_LABEL, "violet"],
      ["城镇化率", provData.urbanization_rate != null ? `${provData.urbanization_rate.toFixed(1)} %` : NO_DATA_LABEL, "teal"],
      ["基本医保参保率", provData.basic_insurance_rate != null ? `${provData.basic_insurance_rate.toFixed(1)} %` : NO_DATA_LABEL, "blue"],
      ["基层医疗密度", provData.primary_care_density != null ? `${provData.primary_care_density.toFixed(2)}/万人` : NO_DATA_LABEL, "emerald"],
      ["高血压患病率", provData.hypertension_prevalence != null ? `${provData.hypertension_prevalence.toFixed(1)} %` : NO_DATA_LABEL, "rose"],
      ["糖尿病患病率", provData.diabetes_prevalence != null ? `${provData.diabetes_prevalence.toFixed(1)} %` : NO_DATA_LABEL, "violet"],
      ["超重/肥胖率", provData.obesity_prevalence != null ? `${provData.obesity_prevalence.toFixed(1)} %` : NO_DATA_LABEL, "amber"],
      ["优化调整", optRow.change_pct != null ? `${optRow.change_pct > 0 ? "+" : ""}${optRow.change_pct.toFixed(1)}%` : NO_DATA_LABEL, "cyan"],
    ];
  } else {
    const gapGradeDisplay = (code) => {
      const map = { "A_surplus":"A 富余", "B_relatively_adequate":"B 较充足", "C_balanced":"C 匹配", "D_shortage":"D 不足", "E_critical_shortage":"E 严重不足" };
      return map[code] ?? code ?? NO_DATA_LABEL;
    };
    const gapGradeAccent = (code) => {
      if (!code) return "amber";
      if (code.startsWith("A") || code.startsWith("B")) return "emerald";
      if (code.startsWith("E")) return "rose";
      return "amber";
    };
    items = [
      ["缺口等级", gapGradeDisplay(latest.gap_grade_en), gapGradeAccent(latest.gap_grade_en)],
      ["象限类型", (() => { const m = {"Q1_high_input_high_output":"Q1高投高产","Q2_low_input_high_output":"Q2低投高产","Q3_high_input_low_output":"Q3高投低产","Q4_low_input_low_output":"Q4低投低产"}; return m[latest.quadrant] ?? latest.quadrant ?? NO_DATA_LABEL; })(), "violet"],
      ["当前支出", formatCurrency(scenarioRow?.current ?? latest.current ?? latest.health_exp_per_capita), "teal"],
      ["最优方案", formatCurrency(scenarioRow?.optimal ?? latest.optimal), "blue"],
      ["建议调整", formatSignedPercent(scenarioRow?.change_pct ?? latest.change_pct), "cyan"],
      ["预期寿命", latest.life_expectancy != null ? `${Number(latest.life_expectancy).toFixed(1)} 岁` : NO_DATA_LABEL, "emerald"],
      ...(latest.uhc_index != null ? [["UHC指数", `${latest.uhc_index} 分`, "violet"]] : []),
      ["资源缺口指数", formatSigned(latest.gap), "rose"],
      ["效率评分", formatSigned(latest.efficiency), "amber"],
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
      const value = metric.accessor(row) ?? 0;
      const progress = Math.round((Math.abs(value) / maxValue) * 100);
      const barColor = metricBarColor(metric, value);
      const flag = iso3ToFlag(row.iso3);
      const flagHtml = flag ? `<span class="row-flag">${flag}</span>` : "";
      return `
        <button
          class="ranking-row ${row.iso3 === state.country ? "is-selected" : ""}"
          data-country="${escapeHtml(row.iso3)}"
          data-rank="${index + 1}"
          style="--progress:${progress}%;--bar-color:${barColor};animation-delay:${index * 45}ms"
          type="button"
        >
          <span class="rank-badge">${index + 1}</span>
          <span class="row-info">
            <b>${flagHtml}${escapeHtml(countryLabel(row))}</b>
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
      const barColor = metric.diverging
        ? row.value >= 0 ? "rgba(11,111,184,0.45)" : "rgba(232,106,79,0.45)"
        : "rgba(20,184,166,0.35)";
      return `
        <button
          class="ranking-row ${row.province === state.province ? "is-selected" : ""}"
          data-province="${escapeHtml(row.province)}"
          data-rank="${index + 1}"
          style="--progress:${progress}%;--bar-color:${barColor};animation-delay:${index * 45}ms"
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
              ? THEME.highlight
              : r.change_pct >= 0
              ? "rgba(11,111,184,0.65)"
              : "rgba(232,106,79,0.55)"
          ),
          cornerradius: 4,
          line: { width: 0 },
        },
        hovertemplate: "<b>%{y}</b><br>调整幅度：%{x:.1f}%<extra></extra>",
      },
    ],
    {
      ...baseLayout({
        xaxis: { title: "建议调整幅度（%）", zeroline: true, zerolinecolor: "#CBD2DC" },
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
        line: { color: THEME.highlight, width: 3, shape: "spline" },
        marker: { size: 6, color: THEME.highlight },
        fill: "tozeroy",
        fillcolor: "rgba(216,27,96,0.08)",
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
  const expTrend = trend.filter((row) => row.health_exp_per_capita != null);
  const leTrend = trend.filter((row) => row.life_expectancy != null);

  if (expTrend.length) {
    traces.push({
      x: expTrend.map((row) => row.year),
      y: expTrend.map((row) => row.health_exp_per_capita),
      name: "人均卫生支出",
      mode: "lines+markers",
      line: { color: THEME.teal, width: 2.5, shape: "spline" },
      marker: { size: 4, color: THEME.teal },
      fill: "tozeroy",
      fillcolor: "rgba(76,181,143,0.08)",
      hovertemplate: "<b>人均卫生支出</b><br>%{x}: $%{y:,.0f}<extra></extra>",
    });
  }

  if (optimalValue != null && expTrend.length) {
    traces.push({
      x: expTrend.map((row) => row.year),
      y: expTrend.map(() => optimalValue),
      name: `优化目标 ($${Math.round(optimalValue).toLocaleString()})`,
      mode: "lines",
      line: { color: THEME.blue, width: 1.5, dash: "dash" },
      hovertemplate: `优化目标: $${Math.round(optimalValue).toLocaleString()}<extra></extra>`,
    });
  }

  if (leTrend.length) {
    traces.push({
      x: leTrend.map((row) => row.year),
      y: leTrend.map((row) => row.life_expectancy),
      name: "预期寿命（右轴）",
      mode: "lines",
      yaxis: "y2",
      line: { color: THEME.violet, width: 2, shape: "spline", dash: "dot" },
      opacity: 0.85,
      hovertemplate: "<b>预期寿命</b><br>%{x}: %{y:.1f} 岁<extra></extra>",
    });
  }

  Plotly.react("detail-chart", traces, baseLayout({
    yaxis: { title: "人均支出（美元）" },
    yaxis2: {
      title: "预期寿命（岁）",
      overlaying: "y",
      side: "right",
      showgrid: false,
      tickfont: { color: "#6D5FB0" },
    },
    legend: { orientation: "h", y: -0.18, x: 0, font: { size: 10 } },
  }), {
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
        line: { color: "#C0432C", width: 3, shape: "spline" },
        marker: { size: 6, color: "#C0432C" },
        fill: "tozeroy",
        fillcolor: "rgba(192,67,44,0.10)",
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
      `<button class="companion-toggle-btn ${state.companionView === "transition" || !["equity","lorenz"].includes(state.companionView) ? "is-active" : ""}" data-view="transition">趋势</button>` +
      `<button class="companion-toggle-btn ${state.companionView === "equity" ? "is-active" : ""}" data-view="equity">公平</button>` +
      `<button class="companion-toggle-btn ${state.companionView === "lorenz" ? "is-active" : ""}" data-view="lorenz">洛伦兹</button>` +
      `</span>`;
    const dim1Titles = {
      equity: `健康公平趋势${toggleHtml}`,
      lorenz: `洛伦兹曲线${toggleHtml}`,
    };
    document.getElementById("companion-title").innerHTML = dim1Titles[state.companionView] ?? `全球疾病趋势${toggleHtml}`;
    document.getElementById("companion-pill").textContent =
      state.companionView === "equity" ? "基尼系数与离散度" :
      state.companionView === "lorenz" ? "卫生支出 / 预期寿命" :
      "2000-2023";

    // Bind toggle
    document.querySelectorAll(".companion-toggle-btn").forEach((btn) => {
      btn.addEventListener("click", () => {
        state.companionView = btn.dataset.view;
        renderCompanionChart();
      });
    });

    if (state.companionView === "equity") {
      renderEquityChart();
    } else if (state.companionView === "lorenz") {
      renderLorenzChart();
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
    const dim4ToggleHtml = `<span class="companion-toggle" id="companion-toggle">` +
      `<button class="companion-toggle-btn ${!["quadrant","lorenz","lorenz_opt"].includes(state.companionView) ? "is-active" : ""}" data-view="trend">趋势</button>` +
      `<button class="companion-toggle-btn ${state.companionView === "quadrant" ? "is-active" : ""}" data-view="quadrant">象限</button>` +
      `<button class="companion-toggle-btn ${state.companionView === "lorenz" ? "is-active" : ""}" data-view="lorenz">洛伦兹</button>` +
      `<button class="companion-toggle-btn ${state.companionView === "lorenz_opt" ? "is-active" : ""}" data-view="lorenz_opt">优化洛伦兹</button>` +
      `</span>`;
    const dim4Titles = {
      quadrant: `省级象限分布${dim4ToggleHtml}`,
      lorenz: `省级洛伦兹曲线${dim4ToggleHtml}`,
      lorenz_opt: `省级优化前后洛伦兹${dim4ToggleHtml}`,
    };
    document.getElementById("companion-title").innerHTML = dim4Titles[state.companionView] ?? `省份卫生人员趋势${dim4ToggleHtml}`;
    document.getElementById("companion-pill").textContent =
      state.companionView === "quadrant" ? "投入-产出散点" :
      state.companionView === "lorenz" ? "省级不平等分布" :
      state.companionView === "lorenz_opt" ? "优化前后健康产出" :
      state.province || "选择省份";

    document.querySelectorAll(".companion-toggle-btn").forEach((btn) => {
      btn.addEventListener("click", () => {
        state.companionView = btn.dataset.view;
        renderCompanionChart();
      });
    });
    if (state.companionView === "quadrant") {
      renderChinaQuadrantScatter();
    } else if (state.companionView === "lorenz") {
      renderChinaLorenzChart();
    } else if (state.companionView === "lorenz_opt") {
      renderChinaOptimizationLorenz();
    } else {
      renderChinaProvincePersonnelTrend();
    }
    return;
  }

  if (state.dimension === "dim5") {
    document.getElementById("companion-title").textContent = "发展-健康气泡图";
    document.getElementById("companion-pill").textContent = `${state.year} 年`;
    renderBubbleChart();
    return;
  }

  const dim3ToggleHtml = `<span class="companion-toggle" id="companion-toggle">` +
    `<button class="companion-toggle-btn ${state.companionView === "reallocation" || !["equity","quadrant","lorenz_opt","transitions"].includes(state.companionView) ? "is-active" : ""}" data-view="reallocation">重分配</button>` +
    `<button class="companion-toggle-btn ${state.companionView === "quadrant" ? "is-active" : ""}" data-view="quadrant">象限</button>` +
    `<button class="companion-toggle-btn ${state.companionView === "equity" ? "is-active" : ""}" data-view="equity">公平</button>` +
    `<button class="companion-toggle-btn ${state.companionView === "lorenz_opt" ? "is-active" : ""}" data-view="lorenz_opt">洛伦兹</button>` +
    `<button class="companion-toggle-btn ${state.companionView === "transitions" ? "is-active" : ""}" data-view="transitions">象限迁移</button>` +
    `</span>`;
  const dim3Titles = {
    equity: `全球健康公平趋势${dim3ToggleHtml}`,
    quadrant: `全球投入-产出象限${dim3ToggleHtml}`,
    lorenz_opt: `优化前后洛伦兹曲线${dim3ToggleHtml}`,
    transitions: `象限迁移分析${dim3ToggleHtml}`,
  };
  document.getElementById("companion-title").innerHTML = dim3Titles[state.companionView] ?? `情景赢家与捐助者${dim3ToggleHtml}`;
  document.getElementById("companion-pill").textContent =
    state.companionView === "equity" ? "基尼系数" :
    state.companionView === "quadrant" ? "四象限分类" :
    state.companionView === "lorenz_opt" ? "健康产出分布" :
    state.companionView === "transitions" ? "2003-2023变化" :
    budgetLabel(state.budgetMultiplier);
  document.querySelectorAll(".companion-toggle-btn").forEach((btn) => {
    btn.addEventListener("click", () => {
      state.companionView = btn.dataset.view;
      renderCompanionChart();
    });
  });
  if (state.companionView === "equity") {
    renderEquityChart();
  } else if (state.companionView === "quadrant") {
    renderGlobalQuadrantScatter();
  } else if (state.companionView === "lorenz_opt") {
    renderOptimizationLorenz();
  } else if (state.companionView === "transitions") {
    renderQuadrantTransitions();
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
        fillcolor: "rgba(231,166,74,0.35)",
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
        fillcolor: "rgba(76,181,143,0.35)",
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
        fillcolor: "rgba(232,106,79,0.35)",
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
          line: { color: "#EEF1F6", width: 0.5 },
          color: sankey.nodes.map((node) =>
            REGION_LABELS[node]
              ? "rgba(109,95,176,0.72)"
              : "rgba(11,111,184,0.85)",
          ),
        },
        link: {
          source: sankey.sources,
          target: sankey.targets,
          value: sankey.values,
          color: "#EEF1F6",
        },
        hoverlabel: {
          bgcolor: THEME.hover,
          bordercolor: THEME.line,
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

const QUADRANT_SHORT = {
  "Q1_high_input_high_output": "Q1高投入高产出",
  "Q2_low_input_high_output": "Q2低投入高产出",
  "Q3_high_input_low_output": "Q3高投入低产出",
  "Q4_low_input_low_output": "Q4低投入低产出",
  "unclassified": "未分类",
};

function renderQuadrantTransitions() {
  const qt = store.globalStory?.quadrant_transitions;
  if (!qt?.movers?.length) {
    emptyPlot("companion-chart", "暂无象限迁移数据。");
    return;
  }

  const movers = qt.movers;
  const fromYear = qt.from_year;
  const toYear = qt.to_year;

  // Group by transition type
  const grouped = {};
  for (const m of movers) {
    const key = m.transition;
    if (!grouped[key]) grouped[key] = [];
    grouped[key].push(m);
  }

  // Color transitions: Q→Q4 is bad (rose), Q4→Q is good (teal), else amber
  const transitionColor = (t) => {
    if (t.endsWith("Q4_low_input_low_output")) return THEME.rose;
    if (t.startsWith("Q4_low_input_low_output")) return THEME.teal;
    if (t.includes("Q3_high_input_low_output") && t.startsWith("Q")) return THEME.amber;
    return THEME.cyan;
  };

  const sortedKeys = Object.keys(grouped).sort((a, b) => grouped[b].length - grouped[a].length);
  const traces = sortedKeys.map((key) => {
    const cs = grouped[key];
    const parts = key.split("→");
    const label = `${QUADRANT_SHORT[parts[0]] ?? parts[0]} → ${QUADRANT_SHORT[parts[1]] ?? parts[1]}（${cs.length}国）`;
    return {
      type: "bar",
      orientation: "h",
      x: [cs.length],
      y: [label],
      name: label,
      marker: { color: transitionColor(key), cornerradius: 4 },
      text: cs.map((c) => c.country_name).join("、"),
      hovertemplate: `<b>${label}</b><br>%{text}<extra></extra>`,
      textposition: "none",
    };
  });

  Plotly.react(
    "companion-chart",
    traces,
    baseLayout({
      barmode: "stack",
      xaxis: { title: "国家数量" },
      yaxis: { automargin: true, tickfont: { size: 10 } },
      showlegend: false,
      annotations: [{
        xref: "paper", yref: "paper",
        x: 0.01, y: 1.05,
        xanchor: "left", yanchor: "bottom",
        text: `${fromYear}→${toYear}：${qt.changed_count}/${qt.total_count} 个国家改变象限`,
        font: { size: 11, color: THEME.muted },
        showarrow: false,
      }],
    }),
    { responsive: true, displayModeBar: false, scrollZoom: false },
  );
}

function _computeLorenzFromArray(values) {
  // Returns {x, y} as percentage arrays for Lorenz curve (sorted ascending)
  const sorted = values.filter((v) => v != null && isFinite(v)).sort((a, b) => a - b);
  if (!sorted.length) return null;
  const n = sorted.length;
  const total = sorted.reduce((acc, v) => acc + v, 0);
  if (total <= 0) return null;
  const x = [0], y = [0];
  let cumSum = 0;
  for (let i = 0; i < n; i++) {
    cumSum += sorted[i];
    x.push(((i + 1) / n) * 100);
    y.push((cumSum / total) * 100);
  }
  return { x, y };
}

function renderOptimizationLorenz() {
  const scenario = getCurrentScenario();
  if (!scenario?.allocation?.length) {
    emptyPlot("companion-chart", "暂无优化情景数据。");
    return;
  }

  const allocation = scenario.allocation;
  const curValues = allocation.map((r) => r.projected_output_current ?? r.output_index).filter((v) => v != null);
  const optValues = allocation.map((r) => r.projected_output_optimal ?? r.output_index).filter((v) => v != null);

  const curLorenz = _computeLorenzFromArray(curValues);
  const optLorenz = _computeLorenzFromArray(optValues);

  if (!curLorenz && !optLorenz) {
    emptyPlot("companion-chart", "暂无产出分布数据。");
    return;
  }

  const summary = scenario.summary ?? {};
  const giniB = summary.gini_before != null ? summary.gini_before.toFixed(3) : "—";
  const giniA = summary.gini_after != null ? summary.gini_after.toFixed(3) : "—";

  const traces = [
    {
      x: [0, 100], y: [0, 100],
      mode: "lines", name: "完全平等线",
      line: { color: "#9AA3B2", width: 1.5, dash: "dot" },
      hoverinfo: "skip",
    },
  ];
  if (curLorenz) {
    traces.push({
      x: curLorenz.x, y: curLorenz.y,
      mode: "lines", name: `优化前（基尼=${giniB}）`,
      line: { color: THEME.rose, width: 2.5, shape: "spline" },
      fill: "tonexty", fillcolor: "rgba(232,106,79,0.09)",
      hovertemplate: "底部 %{x:.0f}% 国家占 %{y:.1f}% 健康产出<extra></extra>",
    });
  }
  if (optLorenz) {
    traces.push({
      x: optLorenz.x, y: optLorenz.y,
      mode: "lines", name: `优化后（基尼=${giniA}）`,
      line: { color: THEME.teal, width: 2.5, shape: "spline" },
      hovertemplate: "底部 %{x:.0f}% 国家占 %{y:.1f}% 健康产出<extra></extra>",
    });
  }

  Plotly.react(
    "companion-chart",
    traces,
    baseLayout({
      xaxis: { title: "国家累计比例（%，按健康产出升序）", range: [0, 100] },
      yaxis: { title: "健康产出累计比例（%）", range: [0, 100] },
      legend: { orientation: "h", y: -0.22, x: 0, font: { size: 10 } },
    }),
    { responsive: true, displayModeBar: false, scrollZoom: false },
  );
}

function renderEquityChart() {
  const equity = store.globalStory?.health_equity ?? [];
  const byQuadrant = store.globalStory?.equity_snapshot?.by_quadrant ?? [];
  const QQ_LABELS = {
    "Q1_high_input_high_output": "Q1高投入\n高产出",
    "Q2_low_input_high_output": "Q2低投入\n高产出",
    "Q3_high_input_low_output": "Q3高投入\n低产出",
    "Q4_low_input_low_output": "Q4低投入\n低产出",
  };
  const qRows = byQuadrant.filter((q) => QQ_LABELS[q.quadrant]);

  if (!equity.length && !qRows.length) {
    emptyPlot("companion-chart", "暂无健康公平数据。");
    return;
  }

  const QUAD_COLORS = {
    "Q1_high_input_high_output": THEME.teal,
    "Q2_low_input_high_output": THEME.cyan,
    "Q3_high_input_low_output": THEME.amber,
    "Q4_low_input_low_output": THEME.rose,
  };

  const traces = [];
  if (equity.length) {
    traces.push({
      x: equity.map((r) => r.year),
      y: equity.map((r) => r.gini),
      name: "全球基尼（预期寿命）",
      mode: "lines+markers",
      line: { color: THEME.cyan, width: 3, shape: "spline" },
      marker: { size: 5, color: THEME.cyan },
    });
    traces.push({
      x: equity.map((r) => r.year),
      y: equity.map((r) => r.sigma),
      name: "离散度收敛（σ）",
      mode: "lines+markers",
      yaxis: "y2",
      line: { color: THEME.amber, width: 2.5, shape: "spline", dash: "dot" },
      marker: { size: 5, color: THEME.amber },
    });
  }
  if (qRows.length && equity.length) {
    // Overlay horizontal lines for each quadrant's Gini (within-quadrant)
    const lastYear = equity[equity.length - 1]?.year;
    qRows.forEach((q) => {
      if (q.gini_life_expectancy == null) return;
      traces.push({
        x: [equity[0]?.year, lastYear],
        y: [q.gini_life_expectancy, q.gini_life_expectancy],
        name: `${QQ_LABELS[q.quadrant]?.replace("\n", " ")} 内基尼`,
        mode: "lines",
        line: { color: QUAD_COLORS[q.quadrant] ?? THEME.muted, width: 1.5, dash: "dash" },
        hovertemplate: `<b>${QQ_LABELS[q.quadrant]?.replace("\n", " ")}</b><br>内部基尼：${q.gini_life_expectancy.toFixed(4)}<br>国家数：${q.country_count}<extra></extra>`,
      });
    });
  }

  Plotly.react(
    "companion-chart",
    traces,
    baseLayout({
      yaxis: { title: "基尼系数（预期寿命）" },
      yaxis2: {
        overlaying: "y",
        side: "right",
        title: "对数σ收敛",
        gridcolor: "rgba(0,0,0,0)",
      },
      legend: { orientation: "h", y: -0.25, x: 0, font: { size: 9 } },
    }),
    { responsive: true, displayModeBar: false, scrollZoom: false },
  );
}

function renderLorenzChart() {
  const lorenz = store.globalStory?.lorenz ?? {};
  const expData = lorenz.health_exp;
  const leData = lorenz.life_expectancy;

  if (!expData?.x?.length && !leData?.x?.length) {
    emptyPlot("companion-chart", "暂无洛伦兹曲线数据。");
    return;
  }

  const traces = [];

  // Perfect equality line
  traces.push({
    x: [0, 100],
    y: [0, 100],
    mode: "lines",
    name: "完全平等线",
    line: { color: "#9AA3B2", width: 1.5, dash: "dot" },
    hoverinfo: "skip",
  });

  if (expData?.x?.length) {
    traces.push({
      x: expData.x,
      y: expData.y,
      mode: "lines",
      name: `${expData.label}（${expData.year}）`,
      line: { color: THEME.rose, width: 2.5, shape: "spline" },
      fill: "tonexty",
      fillcolor: "rgba(232,106,79,0.10)",
      hovertemplate: "底部 %{x:.0f}% 国家占 %{y:.1f}% 支出<extra></extra>",
    });
  }

  if (leData?.x?.length) {
    traces.push({
      x: leData.x,
      y: leData.y,
      mode: "lines",
      name: `${leData.label}（${leData.year}）`,
      line: { color: THEME.teal, width: 2.5, shape: "spline" },
      hovertemplate: "底部 %{x:.0f}% 国家占 %{y:.1f}% 寿命<extra></extra>",
    });
  }

  Plotly.react(
    "companion-chart",
    traces,
    baseLayout({
      xaxis: { title: "国家累计比例（%，按升序排列）", range: [0, 100] },
      yaxis: { title: "指标累计比例（%）", range: [0, 100] },
      legend: { orientation: "h", y: -0.2, x: 0, font: { size: 10 } },
    }),
    { responsive: true, displayModeBar: false, scrollZoom: false },
  );
}

function renderGlobalQuadrantScatter() {
  const countries = store.overview?.countries ?? [];
  if (!countries.length) {
    emptyPlot("companion-chart", "暂无全球效率数据。");
    return;
  }

  const QUADRANT_COLORS = {
    "Q1_high_input_high_output": THEME.teal,
    "Q2_low_input_high_output": THEME.emerald,
    "Q3_high_input_low_output": THEME.rose,
    "Q4_low_input_low_output": THEME.amber,
    "unclassified": THEME.dim,
  };
  const QUADRANT_LABELS = {
    "Q1_high_input_high_output": "高投入高产出",
    "Q2_low_input_high_output": "低投入高产出",
    "Q3_high_input_low_output": "高投入低产出",
    "Q4_low_input_low_output": "低投入低产出",
    "unclassified": "未分类",
  };

  const byQuadrant = {};
  for (const c of countries) {
    if (c.input_index == null || c.output_index == null) continue;
    const q = c.quadrant ?? "unclassified";
    if (!byQuadrant[q]) byQuadrant[q] = [];
    byQuadrant[q].push(c);
  }

  const traces = Object.entries(byQuadrant).map(([q, cs]) => ({
    type: "scatter",
    mode: "markers",
    x: cs.map((c) => c.input_index),
    y: cs.map((c) => c.output_index),
    marker: {
      size: cs.map((c) => c.iso3 === state.country ? 12 : 7),
      color: cs.map((c) => c.iso3 === state.country ? THEME.highlight : (QUADRANT_COLORS[q] ?? THEME.dim)),
      opacity: 0.8,
      line: { color: "rgba(255,255,255,0.15)", width: 1 },
    },
    name: QUADRANT_LABELS[q] ?? q,
    hovertemplate: cs.map((c) =>
      `<b>${c.country_name ?? c.iso3}</b><br>投入指数：${c.input_index.toFixed(2)}<br>产出指数：${c.output_index.toFixed(2)}<br>象限：${QUADRANT_LABELS[q] ?? q}` +
      (c.health_exp_per_capita != null ? `<br>人均支出：$${Math.round(c.health_exp_per_capita).toLocaleString()}` : "") +
      (c.life_expectancy != null ? `<br>预期寿命：${c.life_expectancy.toFixed(1)}岁` : "") +
      (c.uhc_index != null ? `<br>UHC指数：${c.uhc_index.toFixed(0)}` : "") +
      `<extra></extra>`
    ),
    customdata: cs.map((c) => c.iso3),
  }));

  const shapes = [
    { type: "line", x0: 0, x1: 0, y0: -5, y1: 5, line: { color: "#CBD2DC", width: 1, dash: "dash" } },
    { type: "line", x0: -5, x1: 5, y0: 0, y1: 0, line: { color: "#CBD2DC", width: 1, dash: "dash" } },
  ];

  Plotly.react(
    "companion-chart",
    traces,
    baseLayout({
      xaxis: { title: "投入指数（标准化）", zeroline: false },
      yaxis: { title: "产出指数（标准化）", zeroline: false },
      legend: { orientation: "h", y: -0.18, x: 0, font: { size: 10 } },
      shapes,
    }),
    { responsive: true, displayModeBar: false, scrollZoom: false },
  );

  const scatterNode = document.getElementById("companion-chart");
  if (scatterNode && !scatterNode.dataset.globalQuadrantBound) {
    scatterNode.on("plotly_click", (event) => {
      if (state.dimension !== "dim3") return;
      const iso3 = event.points?.[0]?.customdata;
      if (iso3) {
        state.country = iso3;
        renderPanels();
        updateMapHighlight(iso3);
      }
    });
    scatterNode.dataset.globalQuadrantBound = "1";
  }
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
        line: { color: "#C0432C", width: 3, shape: "spline" },
        marker: { size: 6, color: "#C0432C" },
        fill: "tozeroy",
        fillcolor: "rgba(192,67,44,0.10)",
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
      fillcolor: "rgba(231,166,74,0.10)",
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

function renderChinaLorenzChart() {
  const data = store.chinaDeepDive;
  const lorenzData = data?.equity_metrics?.lorenz ?? {};

  if (!Object.keys(lorenzData).length) {
    emptyPlot("companion-chart", "暂无省级洛伦兹曲线数据。");
    return;
  }

  const traces = [
    {
      x: [0, 100],
      y: [0, 100],
      mode: "lines",
      name: "完全平等线",
      line: { color: "#9AA3B2", width: 1.5, dash: "dot" },
      hoverinfo: "skip",
    },
  ];

  const seriesConfig = [
    { key: "health_exp", color: THEME.rose, fill: "rgba(232,106,79,0.10)" },
    { key: "life_expectancy", color: THEME.teal, fill: null },
    { key: "personnel_per_1000", color: THEME.amber, fill: null },
  ];

  for (const { key, color, fill } of seriesConfig) {
    const series = lorenzData[key];
    if (!series?.x?.length) continue;
    traces.push({
      x: series.x,
      y: series.y,
      mode: "lines",
      name: `${series.label ?? key}（${series.n} 省）`,
      line: { color, width: 2.5, shape: "spline" },
      ...(fill ? { fill: "tonexty", fillcolor: fill } : {}),
      hovertemplate: `底部 %{x:.0f}% 省份占 %{y:.1f}% ${series.label ?? ""}<extra></extra>`,
    });
  }

  Plotly.react(
    "companion-chart",
    traces,
    baseLayout({
      xaxis: { title: "省份累计比例（%）", range: [0, 100] },
      yaxis: { title: "指标累计比例（%）", range: [0, 100] },
      legend: { orientation: "h", y: -0.22, x: 0, font: { size: 10 } },
    }),
    { responsive: true, displayModeBar: false, scrollZoom: false },
  );
}

function renderChinaOptimizationLorenz() {
  const data = store.chinaDeepDive;
  const opt = data?.optimization ?? {};
  const scenarios = opt.scenarios ?? [];

  // Find current scenario
  const objKey = OBJECTIVE_ALIASES[state.objective] ?? state.objective;
  const budgetKey = Number(state.budgetMultiplier).toFixed(1);
  const scenario = scenarios.find((s) => {
    const obj = OBJECTIVE_ALIASES[s.objective] ?? s.objective;
    return obj === objKey && Number(s.budget_multiplier).toFixed(1) === budgetKey;
  }) ?? scenarios[0];

  if (!scenario?.allocation?.length) {
    emptyPlot("companion-chart", "暂无中国省级优化情景数据。");
    return;
  }

  const allocation = scenario.allocation;
  const curValues = allocation.map((r) => r.projected_output_current).filter((v) => v != null && isFinite(v));
  const optValues = allocation.map((r) => r.projected_output_optimal).filter((v) => v != null && isFinite(v));

  const curLorenz = _computeLorenzFromArray(curValues);
  const optLorenz = _computeLorenzFromArray(optValues);

  if (!curLorenz && !optLorenz) {
    emptyPlot("companion-chart", "暂无省级产出分布数据。");
    return;
  }

  const summary = scenario.summary ?? {};
  const giniB = summary.gini_before != null ? summary.gini_before.toFixed(3) : "—";
  const giniA = summary.gini_after != null ? summary.gini_after.toFixed(3) : "—";

  const traces = [
    {
      x: [0, 100], y: [0, 100],
      mode: "lines", name: "完全平等线",
      line: { color: "#9AA3B2", width: 1.5, dash: "dot" },
      hoverinfo: "skip",
    },
  ];
  if (curLorenz) {
    traces.push({
      x: curLorenz.x, y: curLorenz.y,
      mode: "lines", name: `优化前（基尼=${giniB}）`,
      line: { color: THEME.rose, width: 2.5, shape: "spline" },
      fill: "tonexty", fillcolor: "rgba(232,106,79,0.09)",
      hovertemplate: "底部 %{x:.0f}% 省份占 %{y:.1f}% 健康产出<extra></extra>",
    });
  }
  if (optLorenz) {
    traces.push({
      x: optLorenz.x, y: optLorenz.y,
      mode: "lines", name: `优化后（基尼=${giniA}）`,
      line: { color: THEME.teal, width: 2.5, shape: "spline" },
      hovertemplate: "底部 %{x:.0f}% 省份占 %{y:.1f}% 健康产出<extra></extra>",
    });
  }

  Plotly.react(
    "companion-chart",
    traces,
    baseLayout({
      xaxis: { title: "省份累计比例（%，按健康产出升序）", range: [0, 100] },
      yaxis: { title: "健康产出累计比例（%）", range: [0, 100] },
      legend: { orientation: "h", y: -0.22, x: 0, font: { size: 10 } },
    }),
    { responsive: true, displayModeBar: false, scrollZoom: false },
  );
}

function renderChinaQuadrantScatter() {
  const data = store.chinaDeepDive;
  const provinces = data?.provinces ?? [];
  if (!provinces.length) {
    emptyPlot("companion-chart", "暂无省级象限数据。");
    return;
  }

  const QUADRANT_COLORS = {
    "Q1_高投入高产出": THEME.teal,
    "Q2_低投入高产出": THEME.emerald,
    "Q3_高投入低产出": THEME.rose,
    "Q4_低投入低产出": THEME.amber,
  };
  const QUADRANT_LABELS = {
    "Q1_高投入高产出": "高投入高产出",
    "Q2_低投入高产出": "低投入高产出",
    "Q3_高投入低产出": "高投入低产出",
    "Q4_低投入低产出": "低投入低产出",
  };

  // Group provinces by quadrant
  const byQuadrant = {};
  for (const p of provinces) {
    const q = p.quadrant ?? "未知";
    if (!byQuadrant[q]) byQuadrant[q] = [];
    byQuadrant[q].push(p);
  }

  const traces = Object.entries(byQuadrant).map(([q, provs]) => ({
    type: "scatter",
    mode: "markers+text",
    x: provs.map((p) => p.input_index),
    y: provs.map((p) => p.output_index),
    text: provs.map((p) => p.province_en),
    textposition: "top center",
    textfont: { size: 9, color: "#4B5563" },
    marker: {
      size: provs.map((p) => p.province === state.province ? 14 : 9),
      color: provs.map((p) => p.province === state.province ? THEME.highlight : (QUADRANT_COLORS[q] ?? THEME.dim)),
      opacity: 0.85,
      line: { color: "rgba(255,255,255,0.2)", width: 1 },
    },
    name: QUADRANT_LABELS[q] ?? q,
    hovertemplate: provs.map((p) =>
      `<b>${p.province}</b><br>投入指数：${p.input_index.toFixed(3)}<br>产出指数：${p.output_index.toFixed(3)}<br>象限：${p.quadrant}<extra></extra>`
    ),
    customdata: provs.map((p) => p.province),
  }));

  // Quadrant dividers at x=0, y=0
  const shapes = [
    { type: "line", x0: 0, x1: 0, y0: -3, y1: 3, line: { color: "#CBD2DC", width: 1, dash: "dash" } },
    { type: "line", x0: -3, x1: 3, y0: 0, y1: 0, line: { color: "#CBD2DC", width: 1, dash: "dash" } },
  ];

  Plotly.react(
    "companion-chart",
    traces,
    baseLayout({
      xaxis: { title: "投入指数（标准化）", zeroline: false },
      yaxis: { title: "产出指数（标准化）", zeroline: false },
      legend: { orientation: "h", y: -0.18, x: 0, font: { size: 10 } },
      shapes,
    }),
    { responsive: true, displayModeBar: false, scrollZoom: false },
  );

  const scatterNode = document.getElementById("companion-chart");
  if (scatterNode && !scatterNode.dataset.quadrantBound) {
    scatterNode.on("plotly_click", (event) => {
      if (state.dimension !== "dim4") return;
      const prov = event.points?.[0]?.customdata;
      if (prov) {
        state.province = prov;
        renderPanels();
        renderChinaMap();
      }
    });
    scatterNode.dataset.quadrantBound = "1";
  }
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
  const globalEquity = store.globalStory?.equity_snapshot ?? {};
  const summaryGrid = `
    <div class="lab-summary-grid">
      ${renderLabStat("优化目标", scenario?.objective_label ?? objectiveLabel(state.objective))}
      ${renderLabStat("预算规模", budgetLabel(scenario?.budget_multiplier ?? state.budgetMultiplier))}
      ${renderLabStat("受益国家数", formatInteger(scenarioSummary.recipient_count))}
      ${renderLabStat("捐出国家数", formatInteger(scenarioSummary.donor_count))}
      ${renderLabStat("基尼降幅", (scenarioSummary.gini_before != null && scenarioSummary.gini_after != null && scenarioSummary.gini_before > 0)
        ? `${(((scenarioSummary.gini_before - scenarioSummary.gini_after) / scenarioSummary.gini_before) * 100).toFixed(1)}%`
        : NO_DATA_LABEL)}
      ${renderLabStat("首要受益国", topRecipient ? (countryLabel(topRecipient) || topRecipient.iso3) : NO_DATA_LABEL)}
      ${renderLabStat("全球基尼（预期寿命）", globalEquity.gini_life_expectancy != null ? globalEquity.gini_life_expectancy.toFixed(4) : NO_DATA_LABEL)}
      ${renderLabStat("人口加权基尼（预期寿命）", globalEquity.population_weighted_gini_le != null ? globalEquity.population_weighted_gini_le.toFixed(4) : NO_DATA_LABEL)}
      ${renderLabStat("全球基尼（卫生支出）", globalEquity.gini_health_expenditure != null ? globalEquity.gini_health_expenditure.toFixed(4) : NO_DATA_LABEL)}
      ${renderLabStat("集中指数（支出→寿命）", globalEquity.concentration_index != null ? globalEquity.concentration_index.toFixed(4) : NO_DATA_LABEL)}
      ${renderLabStat("基尼变化（优化后）", scenarioSummary.gini_change != null ? (scenarioSummary.gini_change > 0 ? "+" : "") + scenarioSummary.gini_change.toFixed(4) : NO_DATA_LABEL)}
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

  const incomeGroups = globalEquity.by_income_group ?? [];
  const INCOME_LABELS = { HIC: "高收入", UMC: "中高收入", LMC: "中低收入", LIC: "低收入" };
  const incomeColumn = incomeGroups.length ? {
    title: "收入组健康差距",
    items: incomeGroups.map((g) => ({
      name: INCOME_LABELS[g.income_group] ?? g.income_group,
      value: `寿命 ${g.avg_life_expectancy != null ? g.avg_life_expectancy.toFixed(1) + "岁" : NO_DATA_LABEL}｜支出 $${g.avg_health_exp != null ? Math.round(g.avg_health_exp) : "—"}`,
    })),
  } : null;

  const whoGroups = globalEquity.by_who_region ?? [];
  const WHO_LABELS = { AFRO: "非洲区", AMRO: "美洲区", EMRO: "东地中海区", EURO: "欧洲区", SEARO: "东南亚区", WPRO: "西太平洋区" };
  const whoColumn = whoGroups.length ? {
    title: "WHO区域资源差异",
    items: whoGroups
      .sort((a, b) => (b.avg_life_expectancy ?? 0) - (a.avg_life_expectancy ?? 0))
      .map((g) => ({
        name: WHO_LABELS[g.region] ?? g.region,
        value: `寿命 ${g.avg_life_expectancy != null ? g.avg_life_expectancy.toFixed(1) + "岁" : NO_DATA_LABEL}｜支出 $${g.avg_health_exp != null ? Math.round(g.avg_health_exp) : "—"}`,
      })),
  } : null;

  // Show Gini improvement from optimization in summary
  const giniBeforeStr = scenarioSummary.gini_before != null ? scenarioSummary.gini_before.toFixed(4) : null;
  const giniAfterStr = scenarioSummary.gini_after != null ? scenarioSummary.gini_after.toFixed(4) : null;
  const giniImprovNote = (giniBeforeStr && giniAfterStr)
    ? `<p class="context-lede" style="font-size:0.8rem;opacity:0.8">基尼系数（预期寿命）：优化前 ${giniBeforeStr} → 优化后 ${giniAfterStr}（${scenarioSummary.gini_change > 0 ? "+" : ""}${scenarioSummary.gini_change?.toFixed(4) ?? "—"}）</p>`
    : "";

  // Quadrant distribution stats from overview countries
  const countries = store.overview?.countries ?? [];
  const qStats = {};
  for (const c of countries) {
    if (!c.quadrant) continue;
    if (!qStats[c.quadrant]) qStats[c.quadrant] = { n: 0, leSum: 0, leN: 0, expSum: 0, expN: 0 };
    qStats[c.quadrant].n++;
    if (c.life_expectancy != null) { qStats[c.quadrant].leSum += c.life_expectancy; qStats[c.quadrant].leN++; }
    if (c.health_exp_per_capita != null) { qStats[c.quadrant].expSum += c.health_exp_per_capita; qStats[c.quadrant].expN++; }
  }
  const QUADRANT_CN_LABELS = {
    "Q1_high_input_high_output": "Q1 高投入高产出",
    "Q2_low_input_high_output": "Q2 低投入高产出",
    "Q3_high_input_low_output": "Q3 高投入低产出",
    "Q4_low_input_low_output": "Q4 低投入低产出",
  };
  // Prefer pre-computed by_quadrant (includes Gini) over live-computed stats
  const byQuadrantArr = globalEquity.by_quadrant ?? [];
  const byQuadrantMap = Object.fromEntries(byQuadrantArr.map((q) => [q.quadrant, q]));
  const quadrantStatsColumn = {
    title: "四象限健康公平分析",
    items: Object.entries(QUADRANT_CN_LABELS).map(([q, label]) => {
      const pre = byQuadrantMap[q];
      const s = qStats[q] ?? { n: 0, leN: 0, leSum: 0, expN: 0, expSum: 0 };
      const n = pre?.country_count ?? s.n;
      const avgLe = pre?.avg_life_expectancy != null ? pre.avg_life_expectancy.toFixed(1) + "岁"
        : s.leN > 0 ? (s.leSum / s.leN).toFixed(1) + "岁" : NO_DATA_LABEL;
      const giniLe = pre?.gini_life_expectancy != null ? `基尼${pre.gini_life_expectancy.toFixed(3)}` : "";
      return { name: `${label}（${n}国）`, value: `寿命${avgLe}${giniLe ? "·" + giniLe : ""}` };
    }),
  };

  const isPersonnel = state.objective?.includes("personnel");
  const methodBlock = `
    <div class="context-method-block" style="font-size:0.8rem;line-height:1.6;padding:0.6rem 0.8rem;background:#F2F4F8;border-radius:8px;border-left:3px solid rgba(11,111,184,0.45);margin-bottom:0.75rem">
      <strong style="display:block;margin-bottom:0.3rem;color:#0F172A">数学规划模型说明</strong>
      ${isPersonnel
        ? `决策变量：各国医生密度 xᵢ（每千人）。约束：Σxᵢ = ${scenarioSummary.budget_multiplier ?? state.budgetMultiplier}×Σx₀ᵢ（总人力预算守恒）；xᵢ ≥ 0.01。`
        : `决策变量：各国人均卫生支出 xᵢ（$USD）。约束：Σxᵢ = ${scenarioSummary.budget_multiplier ?? state.budgetMultiplier ?? "1.0"}×Σx₀ᵢ（总预算守恒）；xᵢ ≥ 0.`
      }
      ${state.objective === "maximin" || state.objective === "maximin_personnel"
        ? "目标函数：max min₍ᵢ₎ ŷᵢ（罗尔斯正义准则——最大化最小产出，即最弱势优先）。"
        : "目标函数：max Σ ŷᵢ（功利主义——最大化全系统总健康产出，边际效益递减约束）。"
      }
      产出函数：ŷᵢ = a·ln(xᵢ) + b（对数型，拟合自各国人均投入-产出散点）。
    </div>
  `;

  // Q2 efficiency leaders case study (sub-question 4: 可推广经验)
  const allCountries = store.overview?.countries ?? [];
  const q2Leaders = allCountries
    .filter((c) => c.quadrant === "Q2_low_input_high_output" && c.life_expectancy != null && c.health_exp_per_capita != null)
    .sort((a, b) => (b.life_expectancy ?? 0) - (a.life_expectancy ?? 0))
    .slice(0, 6);
  const globalMedianLE = (() => {
    const les = allCountries.map((c) => c.life_expectancy).filter((v) => v != null).sort((a, b) => a - b);
    return les.length > 0 ? les[Math.floor(les.length / 2)] : null;
  })();
  const globalMedianExp = (() => {
    const exps = allCountries.map((c) => c.health_exp_per_capita).filter((v) => v != null).sort((a, b) => a - b);
    return exps.length > 0 ? exps[Math.floor(exps.length / 2)] : null;
  })();
  const q2LeaderBlock = q2Leaders.length >= 3 ? `
    <div class="context-method-block" style="font-size:0.79rem;line-height:1.6;padding:0.65rem 0.85rem;background:#EFF8F2;border-radius:8px;border-left:3px solid #4CB58F;margin-bottom:0.75rem">
      <strong style="display:block;margin-bottom:0.4rem;color:#156E4A">Q2 效率标杆：低投入高产出典型案例</strong>
      <div style="display:grid;grid-template-columns:repeat(auto-fill,minmax(160px,1fr));gap:0.35rem 0.6rem;margin-bottom:0.5rem">
        ${q2Leaders.map((c) => `
          <div style="background:#FFFFFF;border:1px solid #DDECE3;border-radius:5px;padding:0.3rem 0.5rem">
            <div style="font-weight:600;color:#0F172A">${escapeHtml(translateCountryIso3(c.iso3))}</div>
            <div style="color:#4B5563">支出：$${Math.round(c.health_exp_per_capita)}/人</div>
            <div style="color:#1F7E5C">寿命：${c.life_expectancy.toFixed(1)}岁</div>
            ${c.physicians_per_1000 != null ? `<div style="color:#6B7280">医生：${c.physicians_per_1000.toFixed(2)}/千人</div>` : ""}
          </div>
        `).join("")}
      </div>
      <p style="margin:0;color:#4B5563">以上国家人均卫生支出均低于全球中位数${globalMedianExp != null ? "（$" + Math.round(globalMedianExp) + "）" : ""}，却实现了高于全球中位预期寿命${globalMedianLE != null ? "（" + globalMedianLE.toFixed(1) + "岁）" : ""}的健康产出。共同经验：<b>强基层卫生网络</b>（社区卫生工作者、全科医生制度）、<b>高免疫覆盖率</b>、<b>重预防轻住院</b>的支出结构及良好的健康行为干预机制。这些可复制经验尤其适合向Q4低投入低产出国家推广。</p>
    </div>
  ` : "";

  // Q3 inefficiency warning block: show high-spending, low-output countries
  const q3Cases = allCountries
    .filter((c) => c.quadrant === "Q3_high_input_low_output" && c.life_expectancy != null && c.health_exp_per_capita != null)
    .sort((a, b) => (b.health_exp_per_capita ?? 0) - (a.health_exp_per_capita ?? 0))
    .slice(0, 5);
  const q3CaseBlock = q3Cases.length >= 3 ? `
    <div class="context-method-block" style="font-size:0.79rem;line-height:1.6;padding:0.65rem 0.85rem;background:#FCF1EE;border-radius:8px;border-left:3px solid #C0432C;margin-bottom:0.75rem">
      <strong style="display:block;margin-bottom:0.4rem;color:#8A2818">Q3 效率警示：高投入低产出典型案例</strong>
      <div style="display:grid;grid-template-columns:repeat(auto-fill,minmax(160px,1fr));gap:0.35rem 0.6rem;margin-bottom:0.5rem">
        ${q3Cases.map((c) => `
          <div style="background:#FFFFFF;border:1px solid #F1D3C9;border-radius:5px;padding:0.3rem 0.5rem">
            <div style="font-weight:600;color:#0F172A">${escapeHtml(translateCountryIso3(c.iso3))}</div>
            <div style="color:#B14A35">支出：$${Math.round(c.health_exp_per_capita)}/人</div>
            <div style="color:#6B7280">寿命：${c.life_expectancy.toFixed(1)}岁</div>
            ${c.efficiency != null ? `<div style="color:#C0432C">效率：${c.efficiency.toFixed(2)}</div>` : ""}
          </div>
        `).join("")}
      </div>
      <p style="margin:0;color:#4B5563">这些国家卫生投入高于全球中位数，却未能转化为相应的健康产出，是典型的<b>效率损失</b>情形。常见根因：资源过度集中于三级医疗、慢病管理薄弱（高BMI/高血压/糖尿病未控制）、预防投入不足、以及社会决定因素（不平等、贫困）阻碍投入转化。建议优先开展卫生系统效率审计，推进<b>价值导向支出改革</b>（Value-Based Healthcare）。</p>
    </div>
  ` : "";

  document.getElementById("context-panel").innerHTML = `
    <p class="context-lede">${escapeHtml(
      OBJECTIVE_META[state.objective]?.note ?? "当前情景设置已应用到最新资源面板。",
    )}</p>
    ${giniImprovNote}
    ${methodBlock}
    ${summaryGrid}
    ${recBlock}
    ${q2LeaderBlock}
    ${q3CaseBlock}
    ${renderContextColumns([
      {
        title: "受益最多国家",
        items: recipients.map((row) => ({ name: countryLabel(row), value: formatSignedPercent(row.change_pct) })),
      },
      {
        title: "主要捐出国家",
        items: donors.map((row) => ({ name: countryLabel(row), value: formatSignedPercent(row.change_pct) })),
      },
      whoColumn ?? quadrantStatsColumn ?? incomeColumn ?? detailColumn,
    ])}
  `;
}

function _globalQuadrantRecommendations() {
  return {
    "Q1_high_input_high_output": {
      title: "高投入高产出：保持领先，优化结构，扩大辐射",
      policy: "该国卫生体系资源充足、健康产出优良，具备向外输出经验的基础。应防止资源错配（如过度集中于三级医疗），强化初级卫生保健，推动预防为主转型。在国际合作中积极提供技术支持与能力建设援助，特别是向Q4国家转移疾病管理、全科医生培训等可操作经验。",
      priority: "推动南南合作，向低资源国家输出精细化卫生管理模式与技术",
    },
    "Q2_low_input_high_output": {
      title: "低投入高产出：深挖效率优势，争取增加投入",
      policy: "该国以有限资源实现优异健康产出，通常依赖社区卫生网络、全科医生体系或文化因素。这类「低成本高效」模式具有极高推广价值。需总结核心经验（如预防接种覆盖率、基层卫生工作者密度、健康行为干预策略），形成可操作的指导手册。同时，应积极争取国际援助与ODA资金，将效率优势转化为更高健康产出的持续能力。",
      priority: "提炼可复制的低成本卫生效率模式，争取增加基层卫生投入",
    },
    "Q3_high_input_low_output": {
      title: "高投入低产出：系统审计，绩效改革，消除错配",
      policy: "该国卫生支出高但健康产出不足，典型原因包括：医院服务过度、预防投入不足、行政效率低下、药品定价不合理或健康不平等严重。建议开展全系统资源利用审计，引入价值导向医疗（Value-Based Healthcare）框架，建立明确的卫生系统绩效考核指标（如DALY减少量/万美元支出）。应将资源结构从三级医疗向基层卫生服务重新倾斜，并加强卫生统计数据质量以提升决策精度。",
      priority: "开展卫生系统效率审计，推进绩效导向的支出结构改革",
    },
    "Q4_low_input_low_output": {
      title: "低投入低产出：双轨并行——增加基础投入与提升效率同步推进",
      policy: "该国面临资源绝对不足与效率低下的双重困境，需要「增投」与「提效」并行而非先后。短期：优先确保基本药品供应、孕产妇与儿童保健、传染病防控的最低投入标准；争取全球健康基金、世界银行卫生专项贷款等外部资源。中期：借鉴Q2国家经验，推广社区卫生工作者（CHW）模式，以最低成本实现覆盖广度。长期：建立卫生系统数据基础设施，支撑循证决策，避免增加投入却重蹈低效覆辙。",
      priority: "争取国际援助，优先补足基层医疗人力与基础设施，同步引入效率机制",
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
      ${renderLabStat("基尼（预期寿命）", equity.gini_life_expectancy != null ? equity.gini_life_expectancy.toFixed(4) : NO_DATA_LABEL)}
      ${renderLabStat("基尼（卫生支出）", equity.gini_health_expenditure != null ? equity.gini_health_expenditure.toFixed(4) : NO_DATA_LABEL)}
      ${renderLabStat("基尼（婴儿死亡率）", equity.gini_infant_mortality != null ? equity.gini_infant_mortality.toFixed(4) : NO_DATA_LABEL)}
      ${renderLabStat("基尼（产妇死亡率）", equity.gini_maternal_mortality != null ? equity.gini_maternal_mortality.toFixed(4) : NO_DATA_LABEL)}
      ${renderLabStat("基尼（5岁以下死亡率）", equity.gini_under5_mortality != null ? equity.gini_under5_mortality.toFixed(4) : NO_DATA_LABEL)}
      ${renderLabStat("集中指数（支出→寿命）", equity.concentration_index_exp_vs_life_expectancy != null ? equity.concentration_index_exp_vs_life_expectancy.toFixed(4) : NO_DATA_LABEL)}
      ${renderLabStat("优化目标", chinaScenario?.objective_label ?? NO_DATA_LABEL)}
      ${renderLabStat("预算情景", chinaScenario ? `${((chinaScenario.budget_multiplier - 1) * 100 >= 0 ? "+" : "")}${((chinaScenario.budget_multiplier - 1) * 100).toFixed(0)}%` : NO_DATA_LABEL)}
      ${renderLabStat("基尼变化（优化后）", chinaScenario?.summary?.gini_change != null ? (chinaScenario.summary.gini_change > 0 ? "+" : "") + chinaScenario.summary.gini_change.toFixed(4) : NO_DATA_LABEL)}
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

  const chinaGiniNote = (chinaScenario?.summary?.gini_before != null && chinaScenario?.summary?.gini_after != null && chinaScenario.summary.gini_before > 0)
    ? `<p class="context-lede" style="font-size:0.8rem;opacity:0.8">基尼系数（产出指数）：优化前 ${chinaScenario.summary.gini_before.toFixed(4)} → 优化后 ${chinaScenario.summary.gini_after.toFixed(4)}（${chinaScenario.summary.gini_change > 0 ? "+" : ""}${chinaScenario.summary.gini_change.toFixed(4)}）</p>`
    : "";

  const isChinaPersonnel = chinaScenario?.objective?.includes("personnel");
  const chinaMethodBlock = `
    <div class="context-method-block" style="font-size:0.78rem;line-height:1.6;padding:0.5rem 0.75rem;background:#FFF7E6;border-radius:8px;border-left:3px solid #E7A64A;margin-bottom:0.75rem">
      <strong style="display:block;margin-bottom:0.25rem;color:#0F172A">中国省级LP模型</strong>
      ${isChinaPersonnel
        ? "决策变量：各省卫生人员数量 xᵢ。约束：Σxᵢ = 预算系数 × Σx₀ᵢ；xᵢ ≥ 0。"
        : "决策变量：各省人均卫生支出 xᵢ（元）。约束：Σxᵢ = 预算系数 × Σx₀ᵢ（省级总预算守恒）；xᵢ ≥ 0。"
      }
      ${chinaScenario?.objective === "maximin" || chinaScenario?.objective === "maximin_personnel"
        ? "目标：max min₍ᵢ₎ ŷᵢ（优先提升最弱省份健康产出，缩小东西部差距）。"
        : "目标：max Σ ŷᵢ（最大化全国总健康产出，向边际效率高的中西部省份倾斜）。"
      }
      产出函数：ŷᵢ = a·ln(xᵢ) + b（对数型增长，拟合自省级投入-产出数据）。
    </div>
  `;

  document.getElementById("context-panel").innerHTML = `
    <p class="context-lede">中国省级卫生资源配置分析 · ${chinaScenario?.objective_label ?? "最优化模型"}</p>
    ${chinaGiniNote}
    ${chinaMethodBlock}
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
        title: "分地区资源与NCD负担",
        items: byRegion.map((r) => ({
          name: `${r.region_cn ?? r.region_en}（${r.province_count} 省）`,
          value: [
            `人均支出：${r.avg_health_exp != null ? "¥" + Math.round(r.avg_health_exp).toLocaleString() : NO_DATA_LABEL}`,
            `高血压：${r.avg_hypertension_prevalence != null ? r.avg_hypertension_prevalence.toFixed(1) + "%" : NO_DATA_LABEL}`,
            `糖尿病：${r.avg_diabetes_prevalence != null ? r.avg_diabetes_prevalence.toFixed(1) + "%" : NO_DATA_LABEL}`,
          ].join(" · "),
        })),
      },
    ])}
  `;
}

function _chinaQuadrantRecommendations() {
  return {
    "Q1_高投入高产出": {
      title: "高投入高产出：保持领先，深化精细化管理",
      policy: "该类省份卫生资源充足、健康产出优良（如京沪浙），代表中国卫生体系的领先水平。核心任务是防止资源边际效益递减，聚焦结构优化而非总量扩张：将资源向社区卫生服务中心倾斜，减少过度医疗，推进慢病精细化管理。同时，积极承担区域帮扶责任，通过「对口支援」机制向欠发达省份输出先进管理经验、师资培训和专科诊断能力。",
      priority: "防止过度医疗，推进价值医疗导向；对口支援西部省份",
    },
    "Q2_低投入高产出": {
      title: "低投入高产出：提炼效率机制，争取增加投入",
      policy: "该类省份以较低投入实现较好健康产出，通常具有稳健的基层卫生网络、较高的健康意识或文化因素。应系统总结核心经验：如乡村医生覆盖率、家庭医生签约率、慢病早筛制度。在争取中央卫生转移支付时，可以效率优势为依据申请专项资金，将优势转化为更高产出基线。建议国家卫健委将此类省份经验汇编为「基层卫生效率标杆手册」。",
      priority: "申请专项转移支付，建立基层效率示范区",
    },
    "Q3_高投入低产出": {
      title: "高投入低产出：推进效率审计，构建绩效考核体系",
      policy: "该类省份卫生支出充足但健康产出偏低，典型问题包括：资源集中于大型医院、基层能力弱、慢病管理断层或卫生人力结构失衡（专科多、全科少）。应开展系统性卫生资源利用审计，建立以「每万元支出减少DALY」为核心的绩效考核指标；推进家庭医生签约制，将大医院门诊量向社区引流；加强全科医生培训，形成「强基层、减虹吸」政策合力。",
      priority: "建立绩效导向支出体系，推进「强基层」结构性改革",
    },
    "Q4_低投入低产出": {
      title: "低投入低产出：增投与提效双轨并行的综合方案",
      policy: "该类省份（多为西部欠发达省区）面临绝对资源不足与效率低下的叠加困境。综合方案分三层推进：【短期】优先保障妇幼保健、传染病防控和基本药物的最低投入标准，争取中央均等化转移支付；【中期】借鉴Q2省份经验推广村级卫生室与乡镇卫生院协同模式，以最低边际成本扩大覆盖广度；【长期】建立省级卫生数据系统，支撑循证决策，避免增量投入流入低效环节。同步推进人才「引进+留用」机制，解决卫生人力流失问题。",
      priority: "争取中央转移支付，优先补足基层人力与基础设施，同步建立效率监测机制",
    },
  };
}

// ── dim5 Charts ─────────────────────────────────────────────────

const REGION_COLORS = {
  Africa: "#6D5FB0",
  Americas: "#E86A4F",
  Asia: "#E7A64A",
  Europe: "#3A8CCF",
  Oceania: "#4CB58F",
  "": "#6B7280",
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
          r.iso3 === state.country ? THEME.highlight : "rgba(0,0,0,0)",
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
        fillcolor: "rgba(216,27,96,0.10)",
        line: { color: THEME.highlight, width: 2.5 },
        marker: { size: 6, color: THEME.highlight },
      },
      {
        type: "scatterpolar",
        r: [...globalValues, globalValues[0]],
        theta: [...labels, labels[0]],
        name: "全球均值",
        fill: "toself",
        fillcolor: "rgba(109,95,176,0.14)",
        line: { color: THEME.violet, width: 2, dash: "dash" },
        marker: { size: 4, color: THEME.violet },
      },
    ],
    {
      paper_bgcolor: "rgba(0,0,0,0)",
      plot_bgcolor: "rgba(0,0,0,0)",
      margin: { l: 56, r: 56, t: 40, b: 80 },
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
        bordercolor: THEME.line,
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
          r.iso3 === state.country ? THEME.highlight : "rgba(0,0,0,0)",
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
    font: { size: 11, color: "#6B7280" },
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
        { type: "line", x0: medianHDI, x1: medianHDI, y0: 0, y1: 1, yref: "paper", line: { color: "#CBD2DC", width: 1, dash: "dot" } },
        { type: "line", x0: 0, x1: 1, y0: medianHALE, y1: medianHALE, xref: "paper", line: { color: "#CBD2DC", width: 1, dash: "dot" } },
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
      ? `<span class="spotlight-badge" data-type="region" data-region="${escapeHtml(meta.who_region)}">${escapeHtml(regionLabel(meta.who_region))}</span>`
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
    // Social determinants of health (shown when available)
    ...(latest.measles_immunization_pct != null ? [["麻疹疫苗接种率", `${Number(latest.measles_immunization_pct).toFixed(0)} %`, "emerald"]] : []),
    ...(latest.basic_water_pct != null ? [["安全饮水覆盖率", `${Number(latest.basic_water_pct).toFixed(0)} %`, "teal"]] : []),
    ...(latest.basic_sanitation_pct != null ? [["卫生设施覆盖率", `${Number(latest.basic_sanitation_pct).toFixed(0)} %`, "blue"]] : []),
    ...(latest.urban_population_pct != null ? [["城镇人口比例", `${Number(latest.urban_population_pct).toFixed(1)} %`, "violet"]] : []),
    ...(latest.fertility_rate != null ? [["总和生育率", `${Number(latest.fertility_rate).toFixed(2)}`, "amber"]] : []),
    ...(latest.infant_mortality != null ? [["婴儿死亡率", `${Number(latest.infant_mortality).toFixed(1)} ‰`, "rose"]] : []),
    ...(latest.under5_mortality != null ? [["5岁以下死亡率", `${Number(latest.under5_mortality).toFixed(1)} ‰`, "amber"]] : []),
    ...(latest.physicians_per_1000 != null && latest.doctor_density == null ? [["医生密度（每千人）", `${Number(latest.physicians_per_1000).toFixed(2)}/千人`, "teal"]] : []),
    ...(latest.nurses_per_1000 != null ? [["护士密度（每千人）", `${Number(latest.nurses_per_1000).toFixed(2)}/千人`, "cyan"]] : []),
    ...(latest.population != null ? [["人口规模", METRIC_META.population.formatter(latest.population), "violet"]] : []),
    ...(latest.cardiovascular_share != null ? [["心血管病占比", formatShare(latest.cardiovascular_share), "rose"]] : []),
    ...(latest.cancer_share != null ? [["癌症死亡占比", formatShare(latest.cancer_share), "amber"]] : []),
    ...(latest.gap_grade_en ? [["资源缺口等级", ({"A_surplus":"A 富余","B_relatively_adequate":"B 较充足","C_balanced":"C 匹配","D_shortage":"D 不足","E_critical_shortage":"E 严重不足"}[latest.gap_grade_en] ?? latest.gap_grade_en), latest.gap_grade_en?.startsWith("A") || latest.gap_grade_en?.startsWith("B") ? "emerald" : latest.gap_grade_en?.startsWith("E") ? "rose" : "amber"]] : []),
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
  renderSpotlightRec(latest.quadrant);
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
      line: { color: THEME.highlight, width: 2.5, shape: "spline" },
      fill: "tozeroy",
      fillcolor: "rgba(216,27,96,0.08)",
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
        bordercolor: THEME.line,
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
  const QUADRANT_ZH = {
    "Q1_high_input_high_output": "Q1 高投入高产出",
    "Q2_low_input_high_output": "Q2 低投入高产出",
    "Q3_high_input_low_output": "Q3 高投入低产出",
    "Q4_low_input_low_output": "Q4 低投入低产出",
    "unclassified": "未分类",
  };
  const items = [
    ["象限类型", QUADRANT_ZH[latest.quadrant] ?? latest.quadrant ?? NO_DATA_LABEL],
    ["资源缺口", formatSigned(latest.gap)],
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

function renderSpotlightRec(quadrant) {
  const section = document.getElementById("spotlight-rec-section");
  const content = document.getElementById("spotlight-rec-content");
  if (!quadrant || quadrant === "unclassified" || !section || !content) {
    if (section) section.style.display = "none";
    return;
  }
  const recs = _globalQuadrantRecommendations();
  const rec = recs[quadrant];
  if (!rec) { section.style.display = "none"; return; }
  section.style.display = "";
  content.innerHTML = `
    <div class="context-rec-block">
      <div class="rec-title">${escapeHtml(rec.title)}</div>
      <div class="rec-body">${escapeHtml(rec.policy)}</div>
      <div class="rec-priority"><span>优先行动：</span>${escapeHtml(rec.priority)}</div>
    </div>
  `;
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
    updateSliderFill(slider);
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
      zerolinecolor: "#EEF1F6",
      linecolor: THEME.grid,
      ticks: "",
      tickfont: { family: "SFMono-Regular, ui-monospace, monospace", size: 11, color: THEME.dim },
    },
    yaxis: {
      gridcolor: THEME.grid,
      zerolinecolor: "#EEF1F6",
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
      bordercolor: THEME.line,
      font: { family: "system-ui, sans-serif", color: THEME.inkBright, size: 13 },
    },
    transition: { duration: 300, easing: "cubic-in-out" },
    ...extra,
  };
}

function renderFailure(error) {
  document.body.innerHTML = `<pre style="padding:24px;color:#C0432C;background:#F7F8FB;font-family:ui-monospace,monospace;min-height:100vh;">仪表盘加载失败：\n${escapeHtml(
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

function clampNumber(value, min, max) {
  return Math.min(Math.max(value, min), max);
}

function hexToRgb(hex) {
  const value = String(hex ?? "").trim().replace("#", "");
  if (value.length !== 6) {
    return null;
  }
  return {
    r: Number.parseInt(value.slice(0, 2), 16),
    g: Number.parseInt(value.slice(2, 4), 16),
    b: Number.parseInt(value.slice(4, 6), 16),
  };
}

function mixColor(left, right, ratio) {
  const start = hexToRgb(left);
  const end = hexToRgb(right);
  if (!start || !end) {
    return right || left || THEME.dim;
  }
  const t = clampNumber(ratio, 0, 1);
  const r = Math.round(start.r + (end.r - start.r) * t);
  const g = Math.round(start.g + (end.g - start.g) * t);
  const b = Math.round(start.b + (end.b - start.b) * t);
  return `rgb(${r}, ${g}, ${b})`;
}

function colorFromScale(value, colorscale, zmin, zmax) {
  if (!Number.isFinite(value) || !Array.isArray(colorscale) || !colorscale.length) {
    return THEME.dim;
  }

  if (!Number.isFinite(zmin) || !Number.isFinite(zmax) || zmin === zmax) {
    return colorscale[Math.floor(colorscale.length / 2)]?.[1] ?? THEME.dim;
  }

  const normalized = clampNumber((value - zmin) / (zmax - zmin), 0, 1);
  for (let i = 1; i < colorscale.length; i += 1) {
    const [stopLeft, colorLeft] = colorscale[i - 1];
    const [stopRight, colorRight] = colorscale[i];
    if (normalized <= stopRight) {
      const ratio = stopRight === stopLeft ? 1 : (normalized - stopLeft) / (stopRight - stopLeft);
      return mixColor(colorLeft, colorRight, ratio);
    }
  }
  return colorscale[colorscale.length - 1]?.[1] ?? THEME.dim;
}

function chinaGeometryToLonLat(geometry) {
  const polygons =
    geometry?.type === "Polygon"
      ? [geometry.coordinates]
      : geometry?.type === "MultiPolygon"
        ? geometry.coordinates
        : [];

  const lon = [];
  const lat = [];

  for (const polygon of polygons) {
    const ring = polygon?.[0];
    if (!ring?.length) continue;
    for (const point of ring) {
      lon.push(point[0]);
      lat.push(point[1]);
    }
    lon.push(null);
    lat.push(null);
  }

  if (lon.length) {
    lon.pop();
    lat.pop();
  }

  return { lon, lat };
}

function getRiskName(riskCode) {
  const row = (store.riskLatest.available_risks ?? []).find((risk) => risk.risk_code === riskCode);
  return translateRiskName(row?.risk_name ?? riskCode);
}

function colorFromPalette(index) {
  const palette = [THEME.teal, THEME.blue, THEME.violet, THEME.amber, THEME.rose, THEME.primary];
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

/** Derive a low-opacity bar colour from a metric's colorscale dominant hue. */
function metricBarColor(metric, value) {
  if (metric.diverging) {
    return value >= 0 ? "rgba(11,111,184,0.40)" : "rgba(192,67,44,0.40)";
  }
  const lastStop = metric.colorscale?.[metric.colorscale.length - 1]?.[1];
  if (!lastStop || lastStop.length < 7) return "rgba(11,111,184,0.30)";
  const r = parseInt(lastStop.slice(1, 3), 16);
  const g = parseInt(lastStop.slice(3, 5), 16);
  const b = parseInt(lastStop.slice(5, 7), 16);
  return `rgba(${r},${g},${b},0.28)`;
}

function debounce(fn, wait) {
  let timeout = null;
  return (...args) => {
    window.clearTimeout(timeout);
    timeout = window.setTimeout(() => fn(...args), wait);
  };
}
