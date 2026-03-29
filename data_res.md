# `data/raw/external/` 数据来源整理

整理日期: `2026-03-29`

## 范围与结论

- 本文覆盖 `data/raw/external/` 下当前实际存在的 `31` 个 CSV 数据文件。
- 已排除 `.gitkeep` 和 `.DS_Store`。
- `data/raw/external/ihme_gbd/` 与 `data/raw/external/china_nbs/` 当前只有 `.gitkeep`，没有可追溯的数据文件。
- `who_ghe/`、`worldbank_wdi/`、`undp_hdi/`、`owid/`、`geo/` 这五组都能对应到明确的线上来源。
- `geo/chinese_to_iso3.csv` 不是直接下载文件，而是项目自建映射表；它参考外部国家代码源并叠加了项目内手工别名。

## 目录概览

| 子目录 | 文件数 | 上游来源 |
|---|---:|---|
| `who_ghe/` | 19 | WHO Global Health Observatory OData API |
| `worldbank_wdi/` | 7 | World Bank Indicators API / 指标页 |
| `undp_hdi/` | 1 | UNDP Human Development Reports |
| `owid/` | 1 | Our World in Data COVID-19 Data |
| `geo/` | 3 | restcountries API / GitHub 原始 CSV / 项目自建 |

## 1. WHO `who_ghe/`

通用说明:

- 官方说明页: [WHO GHO OData API](https://www.who.int/data/gho/info/gho-odata-api)
- 本地文件表头 `Id / IndicatorCode / SpatialDim / TimeDim / NumericValue ...` 与 WHO GHO OData API 返回结构一致。
- 每个文件都可对应到一个 WHO 指标代码，数据实体端点模式为 `https://ghoapi.azureedge.net/api/{IndicatorCode}`。

| 本地文件 | 指标代码 | 官方数据端点 | 备注 |
|---|---|---|---|
| `data/raw/external/who_ghe/alcohol_consumption_per_capita.csv` | `SA_0000001462` | [WHO API](https://ghoapi.azureedge.net/api/SA_0000001462) | 酒精消费量相关指标；本地文件首行 `IndicatorCode` 与端点一致 |
| `data/raw/external/who_ghe/che_per_capita_usd.csv` | `GHED_CHE_pc_US_SHA2011` | [WHO API](https://ghoapi.azureedge.net/api/GHED_CHE_pc_US_SHA2011) | 人均经常性卫生支出（US$），属 WHO GHED 体系 |
| `data/raw/external/who_ghe/external_health_exp_pct_che.csv` | `GHED_EXTCHE_SHA2011` | [WHO API](https://ghoapi.azureedge.net/api/GHED_EXTCHE_SHA2011) | 外部卫生支出占经常性卫生支出比例 |
| `data/raw/external/who_ghe/govt_health_exp_pct_gdp.csv` | `GHED_GGHE-DGDP_SHA2011` | [WHO API](https://ghoapi.azureedge.net/api/GHED_GGHE-DGDP_SHA2011) | 政府卫生支出占 GDP 比例 |
| `data/raw/external/who_ghe/hale_at_birth.csv` | `WHOSIS_000002` | [WHO API](https://ghoapi.azureedge.net/api/WHOSIS_000002) | 健康调整预期寿命（HALE） |
| `data/raw/external/who_ghe/hospital_beds_per_10k.csv` | `WHS6_102` | [WHO API](https://ghoapi.azureedge.net/api/WHS6_102) | 每万人医院床位数 |
| `data/raw/external/who_ghe/infant_mortality_rate.csv` | `MDG_0000000001` | [WHO API](https://ghoapi.azureedge.net/api/MDG_0000000001) | 婴儿死亡率 |
| `data/raw/external/who_ghe/life_expectancy_at_birth.csv` | `WHOSIS_000001` | [WHO API](https://ghoapi.azureedge.net/api/WHOSIS_000001) | 出生时预期寿命 |
| `data/raw/external/who_ghe/maternal_mortality_ratio.csv` | `MDG_0000000026` | [WHO API](https://ghoapi.azureedge.net/api/MDG_0000000026) | 孕产妇死亡率 |
| `data/raw/external/who_ghe/medical_doctors_per_10k.csv` | `HWF_0001` | [WHO API](https://ghoapi.azureedge.net/api/HWF_0001) | 每万人执业医生数；本地 `Comments` 也指向 NHWA 门户 |
| `data/raw/external/who_ghe/ncd_mortality_30_70.csv` | `NCDMORT3070` | [WHO API](https://ghoapi.azureedge.net/api/NCDMORT3070) | 30-70 岁四类主要 NCD 过早死亡概率 |
| `data/raw/external/who_ghe/nursing_midwifery_per_10k.csv` | `HWF_0006` | [WHO API](https://ghoapi.azureedge.net/api/HWF_0006) | 每万人护理和助产人员数；本地 `Comments` 指向 NHWA 门户 |
| `data/raw/external/who_ghe/obesity_prevalence.csv` | `NCD_BMI_30A` | [WHO API](https://ghoapi.azureedge.net/api/NCD_BMI_30A) | 成人肥胖率 |
| `data/raw/external/who_ghe/oop_pct_che.csv` | `GHED_OOPSCHE_SHA2011` | [WHO API](https://ghoapi.azureedge.net/api/GHED_OOPSCHE_SHA2011) | 自付卫生支出占经常性卫生支出比例 |
| `data/raw/external/who_ghe/pm25_exposure.csv` | `SDGPM25` | [WHO API](https://ghoapi.azureedge.net/api/SDGPM25) | PM2.5 暴露浓度 |
| `data/raw/external/who_ghe/smoking_prevalence.csv` | `M_Est_smk_curr_std` | [WHO API](https://ghoapi.azureedge.net/api/M_Est_smk_curr_std) | 当前吸烟率（年龄标化） |
| `data/raw/external/who_ghe/suicide_rate.csv` | `SDGSUICIDE` | [WHO API](https://ghoapi.azureedge.net/api/SDGSUICIDE) | 自杀死亡率 |
| `data/raw/external/who_ghe/uhc_service_coverage.csv` | `UHC_INDEX_REPORTED` | [WHO API](https://ghoapi.azureedge.net/api/UHC_INDEX_REPORTED) | 全民健康覆盖服务覆盖指数 |
| `data/raw/external/who_ghe/under5_mortality_rate.csv` | `MDG_0000000007` | [WHO API](https://ghoapi.azureedge.net/api/MDG_0000000007) | 5 岁以下儿童死亡率 |

补充:

- 医疗人力数据的本地文件 `Comments` 字段明确出现 NHWA 门户: [WHO National Health Workforce Accounts portal](https://apps.who.int/nhwaportal/)
- 卫生支出类数据代码以 `GHED_` 开头，属于 WHO Global Health Expenditure Database 的 GHO 发布口径。

## 2. World Bank `worldbank_wdi/`

通用说明:

- 官方指标页模式: `https://data.worldbank.org/indicator/{indicator_code}`
- 官方 API 模式: `https://api.worldbank.org/v2/country/all/indicator/{indicator_code}?format=json`
- 本地文件并不是 World Bank 原始压缩包，而是已经整理成统一长表格式: `country_code,country_name,indicator_code,indicator_name,year,value`

| 本地文件 | 指标代码 | 官方指标页 | 官方 API | 备注 |
|---|---|---|---|---|
| `data/raw/external/worldbank_wdi/NY.GDP.PCAP.CD.csv` | `NY.GDP.PCAP.CD` | [Indicator](https://data.worldbank.org/indicator/NY.GDP.PCAP.CD) | [API](https://api.worldbank.org/v2/country/all/indicator/NY.GDP.PCAP.CD?format=json) | 人均 GDP（current US$） |
| `data/raw/external/worldbank_wdi/NY.GDP.PCAP.PP.CD.csv` | `NY.GDP.PCAP.PP.CD` | [Indicator](https://data.worldbank.org/indicator/NY.GDP.PCAP.PP.CD) | [API](https://api.worldbank.org/v2/country/all/indicator/NY.GDP.PCAP.PP.CD?format=json) | 人均 GDP，PPP（current international $） |
| `data/raw/external/worldbank_wdi/SE.ADT.LITR.ZS.csv` | `SE.ADT.LITR.ZS` | [Indicator](https://data.worldbank.org/indicator/SE.ADT.LITR.ZS) | [API](https://api.worldbank.org/v2/country/all/indicator/SE.ADT.LITR.ZS?format=json) | 成人识字率 |
| `data/raw/external/worldbank_wdi/SI.POV.GINI.csv` | `SI.POV.GINI` | [Indicator](https://data.worldbank.org/indicator/SI.POV.GINI) | [API](https://api.worldbank.org/v2/country/all/indicator/SI.POV.GINI?format=json) | 基尼系数 |
| `data/raw/external/worldbank_wdi/SL.UEM.TOTL.ZS.csv` | `SL.UEM.TOTL.ZS` | [Indicator](https://data.worldbank.org/indicator/SL.UEM.TOTL.ZS) | [API](https://api.worldbank.org/v2/country/all/indicator/SL.UEM.TOTL.ZS?format=json) | 总失业率 |
| `data/raw/external/worldbank_wdi/SP.POP.TOTL.csv` | `SP.POP.TOTL` | [Indicator](https://data.worldbank.org/indicator/SP.POP.TOTL) | [API](https://api.worldbank.org/v2/country/all/indicator/SP.POP.TOTL?format=json) | 总人口 |
| `data/raw/external/worldbank_wdi/SP.URB.TOTL.IN.ZS.csv` | `SP.URB.TOTL.IN.ZS` | [Indicator](https://data.worldbank.org/indicator/SP.URB.TOTL.IN.ZS) | [API](https://api.worldbank.org/v2/country/all/indicator/SP.URB.TOTL.IN.ZS?format=json) | 城市人口占比 |

## 3. UNDP `undp_hdi/`

通用说明:

- 官方下载页: [UNDP Documentation and downloads](https://hdr.undp.org/data-center/documentation-and-downloads)
- 本地文件字段结构与 UNDP 在 2025 HDR 页面提供的 “All composite indices and components time series (1990-2023)” 一致。

| 本地文件 | 官方来源 | 官方下载链接 | 备注 |
|---|---|---|---|
| `data/raw/external/undp_hdi/hdi_composite_indices.csv` | UNDP Human Development Reports | [CSV](https://hdr.undp.org/sites/default/files/2025_HDR/HDR25_Composite_indices_complete_time_series.csv) | 宽表，覆盖 `1990-2023`，列名形如 `hdi_2023`、`le_2023`、`eys_2023`、`mys_2023`、`gnipc_2023` |

## 4. OWID `owid/`

通用说明:

- 官方仓库: [owid/covid-19-data](https://github.com/owid/covid-19-data)
- 本地文件表头与官方发布的 `owid-covid-data.csv` 一致。

| 本地文件 | 官方来源 | 官方下载链接 | 备注 |
|---|---|---|---|
| `data/raw/external/owid/owid-covid-data.csv` | Our World in Data COVID-19 Data | [CSV](https://covid.ourworldindata.org/data/owid-covid-data.csv) | 也可从 [GitHub raw](https://raw.githubusercontent.com/owid/covid-19-data/master/public/data/owid-covid-data.csv) 获取；本地表头与该文件一致 |

## 5. 地理与映射 `geo/`

| 本地文件 | 官方来源 | 官方链接 | 备注 |
|---|---|---|---|
| `data/raw/external/geo/country_meta.csv` | restcountries API | [API](https://restcountries.com/v3.1/all?fields=name,cca2,cca3,region,subregion,latlng,population) | 本地列 `name_common/name_official/iso2/iso3/region/subregion/latitude/longitude/population` 对应 API 的 `name.common/name.official/cca2/cca3/region/subregion/latlng/population` |
| `data/raw/external/geo/country_centroids.csv` | GitHub `gavinr/world-countries-centroids` | [CSV](https://raw.githubusercontent.com/gavinr/world-countries-centroids/master/dist/countries.csv) | 本地表头与上游 CSV 完全一致: `longitude,latitude,COUNTRY,ISO,COUNTRYAFF,AFF_ISO` |
| `data/raw/external/geo/chinese_to_iso3.csv` | 项目自建映射表 | 直接线上原始文件: 无 | 本文件用于把赛题中的中文国名映射到 ISO3；参考国家代码可来自 [restcountries](https://restcountries.com/)，并叠加项目内手工别名，见 `src/hdi/data/cleaners.py` 中 `_MANUAL_COUNTRY_ALIASES` |

## 核对说明

- 已逐个检查 `data/raw/external/` 下所有实际 CSV 文件名、表头和样例行。
- WHO 组的 `IndicatorCode`、World Bank 组的 `indicator_code`，以及 UNDP、OWID、`geo/` 的表头结构，都能和上表所列线上来源对应上。
- 唯一没有单一外部下载源的是 `geo/chinese_to_iso3.csv`，该文件应视为“基于外部国家代码源整理的项目内部派生表”，而不是第三方原始数据镜像。
