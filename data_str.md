# 数据表单总览 (Data Dictionary)

> 赛题提供数据: `data/raw/provided/` — 5 大模块、约 60 个文件
> 自建补充数据: `data/raw/external/` — 6 大模块、约 30 个文件
> 总覆盖: 全球 ~250 国 + 中国 31 省

---

# 一、赛题提供数据 (`data/raw/provided/`)

---

## 01 · 疾病死亡 `01_disease_mortality/全球主要国家死亡原因/`

| 属性 | 说明 |
|------|------|
| 文件 | `2000.csv` ~ `2023.csv`（24 个年度文件） |
| 行数 | 每文件 ~8,933 行 |
| 国家 | ~205 个（中文名，如 "澳大利亚"、"中国"） |
| 来源 | IHME GBD (全球疾病负担) |

**表头:**

| 列名 | 类型 | 说明 |
|------|------|------|
| `Population` | str | 人群，固定为 "全人口" |
| `地理位置` | str | 国家名（中文） |
| `年份` | int | 数据年份 |
| `年龄` | str | 固定为 "全部" |
| `性别` | str | 固定为 "合计" |
| `死亡或受伤原因` | str | 疾病大类（22 类，见下） |
| `测量` | str | `死亡` = 死亡人数估计值；`死亡排名` = 该类疾病排名 |
| `数值` | float | 对应测量的数值 |
| `下限` | float | 95% 不确定区间下界 |
| `上限` | float | 95% 不确定区间上界 |

**22 类死因:** 心血管疾病、肿瘤、慢性呼吸系统疾病、糖尿病和肾病、消化系统疾病、神经系统疾病、精神障碍、物质使用障碍、肌肉骨骼疾病、皮肤和皮下疾病、感觉器官疾病、呼吸道感染及结核病、肠道感染、艾滋病毒/艾滋病和性传播感染、被忽视的热带病和疟疾、其他传染性疾病、孕产妇和新生儿疾病、营养不良、意外伤害、运输伤害、自残和人际暴力、其他非传染性疾病

> **注意:** `死亡排名` 行的 `下限`/`上限` 为空，这是设计如此，非缺失值。

---

## 02 · 健康风险因素 `02_risk_factors/全球各国健康风险因素数据/`

| 属性 | 说明 |
|------|------|
| 文件 | `2000.csv` ~ `2023.csv`（24 个年度文件） |
| 行数 | 每文件 ~8,121 行 |
| 国家 | ~205 个（同 01） |
| 来源 | IHME GBD |

**表头:**

| 列名 | 类型 | 说明 |
|------|------|------|
| `Population` | str | 固定 "全人口" |
| `地理位置` | str | 国家名（中文） |
| `年份` | int | 数据年份 |
| `年龄` | str | 固定 "全部" |
| `性别` | str | 固定 "合计" |
| `死亡或受伤原因` | str | 固定 "所有原因" |
| `风险因素` | str | 风险因素类别（20 类，见下） |
| `测量` | str | `死亡` / `死亡排名` |
| `数值` | float | 对应测量的数值 |
| `下限` | float | 95% 不确定区间下界 |
| `上限` | float | 95% 不确定区间上界 |

**20 类风险因素:** 高血压、高BMI指数、高血糖、高低密度脂蛋白胆固醇、烟草烟雾、饮酒、饮食风险、空气污染、不安全的水/环境卫生和洗手、不安全性、身体活动不足、低骨密度、肾脏功能受损、儿童和孕产妇营养不良、儿童虐待、亲密伴侣间的暴力、职业风险、用药、其他环境危险因素、体温

> **注意:** 同 01，排名行的置信区间列为空。

---

## 03 · 健康营养与人口统计 `03_nutrition_population/全球各国健康营养和人口统计数据/`

### 3a. 指标词典 `Glossary-健康营养与人口统计.csv`

| 属性 | 说明 |
|------|------|
| 行数 | ~525 行（每行一个指标定义） |
| 用途 | WB_HNP 数据的指标代码查询表 |

| 列名 | 说明 |
|------|------|
| `Code` | 指标代码（如 `SP.ADO.TFRT`） |
| `Indicator Name` | 指标英文名 |
| `Long definition` | 指标详细定义 |
| `Source` | 数据来源 |
| `Dimension` | 维度（固定 "Series"） |
| `Datasource_Name` | 固定 "Health Nutrition and Population Statistics" |

### 3b. 主数据 `WB_HNP.csv`

| 属性 | 说明 |
|------|------|
| 行数 | **~7,081,984 行**（超大文件） |
| 格式 | SDMX 长格式 |
| 来源 | 世界银行 HNP 数据库 |

| 列名 | 说明 |
|------|------|
| `REF_AREA` / `REF_AREA_LABEL` | 国家/地区代码 & 名称 |
| `INDICATOR` / `INDICATOR_LABEL` | 指标代码 & 名称（对应 Glossary） |
| `SEX` / `SEX_LABEL` | 性别维度（Total / Male / Female） |
| `AGE` / `AGE_LABEL` | 年龄维度 |
| `URBANISATION` / `URBANISATION_LABEL` | 城乡维度 |
| `UNIT_MEASURE` / `UNIT_MEASURE_LABEL` | 计量单位 |
| `COMP_BREAKDOWN_1~3` | 补充分类维度 |
| `TIME_PERIOD` | 年份 |
| `OBS_VALUE` | **核心数据列** |
| `OBS_STATUS` / `OBS_STATUS_LABEL` | 观测状态（`O` = Missing） |
| 其余元数据列 | STRUCTURE, FREQ, DATABASE_ID, UNIT_MULT, UNIT_TYPE, TIME_FORMAT, OBS_CONF |

> **注意:** `OBS_VALUE` 大量为空（标记为 `OBS_STATUS=O`），尤其是早期年份和小国。文件 ~2.5GB，读取时建议分块加载或按 INDICATOR 筛选。

---

## 04 · 社会经济指标 `04_socioeconomic/WDI_CSV/`

世界银行 World Development Indicators (WDI) 完整导出，共 6 个文件。

### 4a. 主数据 `WDICSV.csv`

| 属性 | 说明 |
|------|------|
| 行数 | ~402,458 行 |
| 格式 | **宽格式**（年份为列） |

| 列名 | 说明 |
|------|------|
| `Country Name` | 国家/地区名称（英文） |
| `Country Code` | ISO3 国家代码 |
| `Indicator Name` | 指标名称（英文） |
| `Indicator Code` | 指标代码 |
| `1960` ~ `2024` | 各年份数值（65 列） |

> **注意:** 1960-1999 年份列大面积为空（许多指标仅有近 20 年数据）。行数多因指标多（~1,400+ 指标 × ~270 国家/地区）。

### 4b. 国家元数据 `WDICountry.csv`

| 属性 | 说明 |
|------|------|
| 行数 | ~276 行 |
| 用途 | 国家代码 → 名称 / 区域 / 收入分组等映射 |

| 关键列 | 说明 |
|--------|------|
| `Country Code` | ISO3 代码（关联主键） |
| `Short Name` / `Long Name` | 国家名称 |
| `Region` | 所属区域（如 Latin America & Caribbean） |
| `Income Group` | 收入分组（High income / Upper middle income 等） |
| `Currency Unit` | 货币单位 |
| 其余 | 2-alpha code, SNA, PPP 等统计方法元数据 |

### 4c. 指标元数据 `WDISeries.csv`

| 属性 | 说明 |
|------|------|
| 行数 | ~27,146 行 |
| 用途 | 指标代码 → 定义 / 主题 / 单位 / 方法论 |

| 关键列 | 说明 |
|--------|------|
| `Series Code` | 指标代码（关联主键） |
| `Topic` | 主题分类 |
| `Indicator Name` | 指标名称 |
| `Short definition` / `Long definition` | 指标定义 |
| `Unit of measure` | 计量单位 |
| `Periodicity` | 周期（Annual 等） |
| `Source` | 数据来源 |
| `Aggregation method` | 聚合方式 |

### 4d. 国家-指标脚注 `WDIcountry-series.csv`

| 属性 | 说明 |
|------|------|
| 行数 | ~7,945 行 |
| 列 | `CountryCode`, `SeriesCode`, `DESCRIPTION` |
| 用途 | 特定国家×指标的数据来源说明 |

### 4e. 国家-指标-年份脚注 `WDIfootnote.csv`

| 属性 | 说明 |
|------|------|
| 行数 | ~849,581 行 |
| 列 | `CountryCode`, `SeriesCode`, `Year`, `DESCRIPTION` |
| 用途 | 最细粒度脚注（通常不必读取，仅供溯源） |

### 4f. 指标-时间脚注 `WDIseries-time.csv`

| 属性 | 说明 |
|------|------|
| 行数 | ~143 行 |
| 列 | `SeriesCode`, `Year`, `DESCRIPTION` |
| 用途 | 部分指标特定年份的聚合说明 |

---

## 05 · 中国卫生数据 `05_china_health/全国近20年卫生数据-国家统计局/`

来源：国家统计局，覆盖 31 省 × 20 年 (2005-2024)。

### 5a. 各省卫生人员数量 `各省近20年卫生人员数量.csv`

| 属性 | 说明 |
|------|------|
| 行数 | 31 行（31 省/自治区/直辖市） |
| 单位 | **万人** |

| 列名 | 说明 |
|------|------|
| `地区` | 省份名称 |
| `2024年` ~ `2005年` | 各年份卫生人员总数（20 列） |

### 5b. 各省医疗卫生机构数量 `近20年各省医疗卫生机构数量.csv`

| 属性 | 说明 |
|------|------|
| 行数 | 31 行 |
| 单位 | **个** |

| 列名 | 说明 |
|------|------|
| `地区` | 省份名称 |
| `2024年` ~ `2005年` | 各年份医疗卫生机构数（20 列） |

### 5c. 全国人口生命统计 `近20年我国人口出生率死亡率自然增长率及平均预期寿命.csv`

| 属性 | 说明 |
|------|------|
| 行数 | 6 行（6 项指标） |
| 粒度 | 全国级别，非分省 |

| 指标 | 单位 | 说明 |
|------|------|------|
| 人口出生率 | ‰ | 每千人出生数 |
| 人口死亡率 | ‰ | 每千人死亡数 |
| 人口自然增长率 | ‰ | 出生率 - 死亡率 |
| 平均预期寿命 | 岁 | 总体 |
| 男性平均预期寿命 | 岁 | 男 |
| 女性平均预期寿命 | 岁 | 女 |

> **注意:** 平均预期寿命仅每 5 年公布一次（2005、2010、2015、2020），其余年份为空。2024 年出生/死亡率已更新但预期寿命尚未公布。

---

## 快速参考：数据关联关系

```
01 死亡原因 ──┐
              ├── 通过「国家名(中文)」+「年份」关联 → 构建 master_panel
02 风险因素 ──┘

03 WB_HNP ─────── 通过 REF_AREA(ISO) + TIME_PERIOD 关联
                   使用 Glossary 解码 INDICATOR

04 WDI ─────────── 通过 Country Code(ISO3) + 年份列 关联
                   使用 WDICountry/WDISeries 解码

05 中国卫生 ────── 通过「地区」+「年份」关联 → 构建 china_panel
```

> **维护提醒:** 01/02 国家名为中文，04 为英文，合并时需要 `pycountry` 或手工映射表做国家代码统一（参见 `src/hdi/data/cleaners.py`，以及 `data/raw/external/geo/chinese_to_iso3.csv`）。

---

# 二、自建补充数据 (`data/raw/external/`)

> 数据获取时间: 2026-03-12
> 所有数据通过 API 或公开下载链接获取，均为权威国际组织官方发布数据

---

## E1 · WHO 全球卫生数据 `who_ghe/`

来源: **WHO Global Health Observatory (GHO) OData API** (`ghoapi.azureedge.net`)

所有文件为 JSON→CSV 转换的长格式，公共列结构:

| 列名 | 说明 |
|------|------|
| `Id` | 记录 ID |
| `IndicatorCode` | WHO 指标代码 |
| `SpatialDim` | ISO3 国家代码 |
| `ParentLocation` | WHO 区域名称 |
| `TimeDim` | 年份 |
| `Dim1` | 维度1（通常为性别: SEX_BTSX/SEX_MLE/SEX_FMLE） |
| `NumericValue` | **核心数值** |
| `Low` / `High` | 置信区间（部分指标有） |

### 健康结果指标

| 文件 | 行数 | 指标代码 | 说明 | 用于维度 |
|------|------|----------|------|----------|
| `life_expectancy_at_birth.csv` | 12,936 | WHOSIS_000001 | 出生时预期寿命（岁） | 维度1 |
| `hale_at_birth.csv` | 12,936 | WHOSIS_000002 | 健康调整预期寿命 HALE（岁） | 维度1 |
| `infant_mortality_rate.csv` | 43,513 | MDG_0000000001 | 婴儿死亡率（每千活产） | 维度1 |
| `under5_mortality_rate.csv` | 63,070 | MDG_0000000007 | 5 岁以下儿童死亡率（每千活产） | 维度1 |
| `maternal_mortality_ratio.csv` | 7,878 | MDG_0000000026 | 孕产妇死亡率（每 10 万活产） | 维度1 |
| `ncd_mortality_30_70.csv` | 12,936 | NCDMORT3070 | 30-70 岁 NCD 死亡概率（%） | 维度1+2 |
| `suicide_rate.csv` | 19,041 | SDGSUICIDE | 自杀率（每 10 万人） | 维度1 |

### 风险因素指标

| 文件 | 行数 | 指标代码 | 说明 | 用于维度 |
|------|------|----------|------|----------|
| `pm25_exposure.csv` | 10,750 | SDGPM25 | PM2.5 年均暴露浓度（μg/m³） | 维度2 |
| `obesity_prevalence.csv` | 20,790 | NCD_BMI_30A | 肥胖率 BMI≥30（%） | 维度2 |
| `smoking_prevalence.csv` | 5,511 | M_Est_smk_curr_std | 当前吸烟率（年龄标化 %） | 维度2 |
| `alcohol_consumption_per_capita.csv` | 582 | SA_0000001462 | 人均纯酒精消费（升/年） | 维度2 |

### 卫生资源指标

| 文件 | 行数 | 指标代码 | 说明 | 用于维度 |
|------|------|----------|------|----------|
| `medical_doctors_per_10k.csv` | 3,693 | HWF_0001 | 医生密度（每万人） | 维度3 |
| `nursing_midwifery_per_10k.csv` | 3,593 | HWF_0006 | 护理/助产人员密度（每万人） | 维度3 |
| `hospital_beds_per_10k.csv` | 2,960 | WHS6_102 | 医院床位（每万人） | 维度3 |
| `uhc_service_coverage.csv` | 5,160 | UHC_INDEX_REPORTED | 全民健康覆盖指数 UHC (0-100) | 维度3 |

### 卫生支出指标

| 文件 | 行数 | 指标代码 | 说明 | 用于维度 |
|------|------|----------|------|----------|
| `che_per_capita_usd.csv` | 4,849 | GHED_CHE_pc_US_SHA2011 | 当前卫生支出/人均（US$） | 维度3 |
| `govt_health_exp_pct_gdp.csv` | 4,852 | GHED_GGHE-DGDP_SHA2011 | 政府卫生支出占 GDP（%） | 维度3 |
| `oop_pct_che.csv` | 4,852 | GHED_OOPSCHE_SHA2011 | 自付费用占卫生总支出（%） | 维度3 |
| `external_health_exp_pct_che.csv` | 4,851 | GHED_EXTCHE_SHA2011 | 外部援助占卫生总支出（%） | 维度3 |

> **注意:** WHO GHO API 于 2025 年末宣布迁移，当前仍可用。卫生支出数据覆盖 ~2000-2022。

---

## E2 · 世界银行经济指标 `worldbank_wdi/`

来源: **World Bank Open Data API** (`api.worldbank.org/v2`)，2000-2024 年。

| 列名 | 说明 |
|------|------|
| `country_code` | ISO3 国家代码 |
| `country_name` | 英文名 |
| `indicator_code` | WDI 指标代码 |
| `indicator_name` | 指标名称 |
| `year` | 年份 |
| `value` | 数值（可为空） |

| 文件 | 行数 | 指标代码 | 说明 |
|------|------|----------|------|
| `NY.GDP.PCAP.CD.csv` | 6,650 | NY.GDP.PCAP.CD | 人均 GDP（当前美元） |
| `NY.GDP.PCAP.PP.CD.csv` | 6,650 | NY.GDP.PCAP.PP.CD | 人均 GDP（PPP 国际美元） |
| `SP.POP.TOTL.csv` | 6,650 | SP.POP.TOTL | 总人口 |
| `SP.URB.TOTL.IN.ZS.csv` | 6,650 | SP.URB.TOTL.IN.ZS | 城市化率（%） |
| `SI.POV.GINI.csv` | 6,650 | SI.POV.GINI | 基尼系数 |
| `SL.UEM.TOTL.ZS.csv` | 6,650 | SL.UEM.TOTL.ZS | 失业率（%） |
| `SE.ADT.LITR.ZS.csv` | 6,650 | SE.ADT.LITR.ZS | 成人识字率（%） |

> **注意:** 这些指标从 WDI 主表 (04 WDICSV) 中也可提取，此处为预处理好的长格式方便直接使用。基尼系数缺失较多（约 60% 为空）。

---

## E3 · UNDP 人类发展指数 `undp_hdi/`

来源: **UNDP Human Development Report 2025** (`hdr.undp.org`)

### `hdi_composite_indices.csv`

| 属性 | 说明 |
|------|------|
| 行数 | 206 行（国家/地区） |
| 时间跨度 | 1990-2023 |
| 格式 | 宽格式（`{indicator}_{year}` 为列名） |

| 关键列 | 说明 |
|--------|------|
| `iso3` | ISO3 国家代码 |
| `country` | 英文国名 |
| `region` | UNDP 区域分类 |
| `hdi_rank_2023` | 2023 年 HDI 排名 |
| `hdi_{year}` | 人类发展指数 (0-1) |
| `le_{year}` | 预期寿命（岁） |
| `eys_{year}` | 预期受教育年限 |
| `mys_{year}` | 平均受教育年限 |
| `gnipc_{year}` | 人均 GNI（2017 PPP $） |
| `ihdi_{year}` | 不平等调整 HDI |
| `gdi_{year}` | 性别发展指数 |
| `gii_{year}` | 性别不平等指数 |
| `phdi_{year}` | 地球压力调整 HDI |
| `co2_prod_{year}` | 人均 CO₂ 排放量 |
| `pop_total_{year}` | 总人口（百万） |

> **注意:** 此文件列数极多（~1,000+ 列），包含 HDI/IHDI/GDI/GII/PHDI 五大复合指数的完整时间序列。适合用于国家发展水平分类和健康-发展关联分析。

---

## E4 · 地理与映射数据 `geo/`

### `country_meta.csv` (250 行)

来源: **restcountries.com API**

| 列名 | 说明 |
|------|------|
| `name_common` | 英文常用名 |
| `name_official` | 英文官方名 |
| `iso2` | ISO 3166-1 alpha-2 |
| `iso3` | ISO 3166-1 alpha-3 |
| `region` | 大洲（Asia / Europe / Africa 等） |
| `subregion` | 子区域 |
| `latitude` | 质心纬度 |
| `longitude` | 质心经度 |
| `population` | 总人口 |

> 用于 Moran's I 空间自相关分析和地图可视化。

### `country_centroids.csv` (248 行)

来源: **gavinr/world-countries-centroids (GitHub)**

| 列名 | 说明 |
|------|------|
| `COUNTRY` | 国家名 |
| `ISO` | ISO2 代码 |
| `longitude` / `latitude` | 质心坐标 |

### `chinese_to_iso3.csv` (206 行)

**自建映射表** — 将赛题数据 01/02 中的中文国名映射到 ISO3 代码。

| 列名 | 说明 |
|------|------|
| `chinese_name` | 中文国名（与赛题数据一致） |
| `iso3` | ISO 3166-1 alpha-3 代码 |

> **关键工具:** 此映射表是连接中文命名的 IHME 数据与英文命名的 WHO/WDI/UNDP 数据的桥梁。

---

## E5 · OWID 数据 `owid/`

来源: **Our World in Data** (GitHub: `owid/covid-19-data`)

### `owid-covid-data.csv`

| 属性 | 说明 |
|------|------|
| 行数 | ~429,435 行 |
| 文件大小 | ~94 MB |
| 时间跨度 | 2020-01 ~ 2024 |

| 关键列 | 说明 |
|--------|------|
| `iso_code` | ISO3 国家代码 |
| `location` | 国家名 |
| `date` | 日期 |
| `total_cases` / `new_cases` | 累计/新增确诊 |
| `total_deaths` / `new_deaths` | 累计/新增死亡 |
| `total_vaccinations` | 累计接种 |
| `people_vaccinated` | 至少接种一剂人数 |
| `hospital_patients` / `icu_patients` | 住院/ICU 人数 |
| `population` / `population_density` | 人口相关 |
| `gdp_per_capita` | 人均 GDP |
| `life_expectancy` | 预期寿命 |
| `human_development_index` | HDI |

> **用途:** COVID-19 疫情冲击作为卫生系统"压力测试"的自然实验数据。可用于分析卫生资源配置与疫情应对效果的关联（维度3）。

---

## 快速参考：数据关联关系

```
赛题提供数据:
  01 死亡原因 ──┐
                ├── 中文国名 + 年份 ──→ chinese_to_iso3.csv ──→ iso3
  02 风险因素 ──┘                                                  │
                                                                   ↓
  03 WB_HNP ─── REF_AREA(ISO) + TIME_PERIOD ──────────────────→ iso3 + year
  04 WDI ────── Country Code(ISO3) + 年份列 ───────────────────→ iso3 + year
  05 中国卫生 ── 地区 + 年份 → china_panel (独立)

自建补充数据:
  E1 WHO GHE ── SpatialDim(ISO3) + TimeDim ───────────────────→ iso3 + year
  E2 WB API ─── country_code(ISO3) + year ────────────────────→ iso3 + year
  E3 UNDP HDI ── iso3 + 宽格式年份列 ─────────────────────────→ iso3 + year
  E4 Geo ─────── iso3 → lat/lng + region + subregion (空间分析)
  E5 OWID ────── iso_code(ISO3) + date ───────────────────────→ iso3 + date
```

> **全局关联键:** `iso3` (ISO 3166-1 alpha-3) 是串联所有数据集的核心主键。
> 赛题 01/02 使用中文国名 → 通过 `chinese_to_iso3.csv` 映射到 iso3。
