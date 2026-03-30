# reports 指标/缩写数据来源索引

## 1. 说明

这份索引按“**报告中的写法/缩写 -> 标准字段 -> 处理层表项 -> 原始文件/表项来源**”整理。

两条关键规则先说明：

1. 全球国家面板的标准字段主要落在：
   - `data/processed/master_panel.parquet`
   - `data/processed/resource_panel.parquet`
2. 对同一指标，若 HNP 与 WDI 都有，代码按 **HNP 优先、WDI 回退** 合并：
   - 见 `src/hdi/config.py` 中 `INDICATOR_SPECS`
   - 见 `src/hdi/data/integrator.py` 中 `_indicator_wide()`

其中：

- HNP 原始主表：`data/raw/provided/03_nutrition_population/全球各国健康营养和人口统计数据/WB_HNP.csv`
- HNP 指标释义表：`data/raw/provided/03_nutrition_population/全球各国健康营养和人口统计数据/Glossary-健康营养与人口统计.csv`
- WDI 原始主表：`data/raw/provided/04_socioeconomic/WDI_CSV/WDICSV.csv`
- WDI 指标释义表：`data/raw/provided/04_socioeconomic/WDI_CSV/WDISeries.csv`
- 全球死因原始表：`data/raw/provided/01_disease_mortality/全球主要国家死亡原因/<year>.csv`
- 中国省级卫生原始表：
  - `data/raw/provided/05_china_health/全国近20年卫生数据-国家统计局/各省近20年卫生人员数量.csv`
  - `data/raw/provided/05_china_health/全国近20年卫生数据-国家统计局/近20年各省医疗卫生机构数量.csv`

## 2. 全球指标与缩写

| 中文含义 | 报告中的写法/缩写 | 标准字段 | 处理层表项 | 原始文件 | 原始表项/指标代码 | 备注 |
|---|---|---|---|---|---|---|
| 预期寿命 | `LE` | `life_expectancy` | `master_panel.parquet`, `resource_panel.parquet` | `WB_HNP.csv`（优先）/ `WDICSV.csv`（回退） | `WB_HNP_SP_DYN_LE00_IN` / `SP.DYN.LE00.IN`；指标名 `Life expectancy at birth, total (years)` | 报告中同时用于 D1 回归、D3 产出指数、D3 需求指数 |
| 婴儿死亡率 | `IMR` | `infant_mortality` | `master_panel.parquet`, `resource_panel.parquet` | `WB_HNP.csv`（优先）/ `WDICSV.csv`（回退） | `WB_HNP_SP_DYN_IMRT_IN` / `SP.DYN.IMRT.IN`；指标名 `Mortality rate, infant (per 1,000 live births)` | D3 产出指数、需求指数 |
| 5岁以下死亡率 | `U5MR` | `under5_mortality` | `master_panel.parquet`, `resource_panel.parquet` | `WB_HNP.csv`（优先）/ `WDICSV.csv`（回退） | `WB_HNP_SH_DYN_MORT` / `SH.DYN.MORT`；指标名 `Mortality rate, under-5 (per 1,000 live births)` | D3 产出指数、需求指数 |
| 医生密度 | `Phys` | `physicians_per_1000` | `master_panel.parquet`, `resource_panel.parquet` | `WB_HNP.csv`（优先）/ `WDICSV.csv`（回退） | `WB_HNP_SH_MED_PHYS_ZS` / `SH.MED.PHYS.ZS`；指标名 `Physicians (per 1,000 people)` | D1 回归、D3 投入指数 |
| 床位密度 | `Beds` | `beds_per_1000` | `master_panel.parquet`, `resource_panel.parquet` | `WB_HNP.csv`（优先）/ `WDICSV.csv`（回退） | `WB_HNP_SH_MED_BEDS_ZS` / `SH.MED.BEDS.ZS`；指标名 `Hospital beds (per 1,000 people)` | 全局 canonical 名为 `beds_per_1000`，来源指标名称是 hospital beds |
| 卫生支出占 GDP | `HealthExp`, `HExp%` | `health_exp_pct_gdp` | `master_panel.parquet`, `resource_panel.parquet` | `WDICSV.csv` | `SH.XPD.CHEX.GD.ZS`；指标名 `Current health expenditure (% of GDP)` | D1 回归中的 `HealthExp` 实际对应这一项，不是人均卫生支出 |
| 人均卫生支出 | `HExpPC` | `health_exp_per_capita` | `master_panel.parquet`, `resource_panel.parquet` | `WDICSV.csv` | `SH.XPD.CHEX.PC.CD`；指标名 `Current health expenditure per capita (current US$)` | D3 投入指数；也是优化模型的决策变量 |
| 人均 GDP | `GDP`，回归表中为 `log_gdp_per_capita` | `gdp_per_capita` | `master_panel.parquet`, `resource_panel.parquet` | `WDICSV.csv` | `NY.GDP.PCAP.CD`；指标名 `GDP per capita (current US$)` | 报告回归实际使用其对数变换 |
| 基本饮水服务覆盖率 | `Water` | `basic_water_pct` | `master_panel.parquet` | `WB_HNP.csv`（优先）/ `WDICSV.csv`（回退） | `WB_HNP_SH_H2O_BASW_ZS` / `SH.H2O.BASW.ZS`；指标名 `People using at least basic drinking water services (% of population)` | D1 回归解释变量 |
| 基本卫生服务覆盖率 | `Sanit` | `basic_sanitation_pct` | `master_panel.parquet` | `WB_HNP.csv`（优先）/ `WDICSV.csv`（回退） | `WB_HNP_SH_STA_BASS_ZS` / `SH.STA.BASS.ZS`；指标名 `People using at least basic sanitation services (% of population)` | D1 回归解释变量 |
| 传染性疾病占比 | `CommSh` | `communicable_share` | `master_panel.parquet` | `01_disease_mortality/全球主要国家死亡原因/<year>.csv` | 原始列 `死亡或受伤原因`, `测量`, `数值`；筛 `测量=死亡` 后按死因归并并除以 `total_deaths` | 不是直接原始字段，而是派生指标 |
| 非传染性疾病占比 | `NCDSh` | `ncd_share` | `master_panel.parquet` | `01_disease_mortality/全球主要国家死亡原因/<year>.csv` | 同上；按死因归并为“非传染性疾病”后除以 `total_deaths` | D1 回归、Top/Bottom LE 表 |
| 伤害占比 | `InjSh` | `injury_share` | `master_panel.parquet` | `01_disease_mortality/全球主要国家死亡原因/<year>.csv` | 同上；按死因归并为“伤害”后除以 `total_deaths` | 报告正文提到但未进核心回归表 |

### 2.1 `communicable_share` / `ncd_share` / `injury_share` 的归并口径

这些占比不是 HNP/WDI 直接给的，而是由 `src/hdi/data/integrator.py` 中 `_disease_features()` 计算。

底层原始列来自 `01_disease_mortality` 各年度 CSV：

- `Population`
- `地理位置`
- `年份`
- `年龄`
- `性别`
- `死亡或受伤原因`
- `测量`
- `数值`

处理规则：

1. 只取 `测量 = 死亡`
2. 按 `src/hdi/config.py` 中 `CAUSE_GROUP_MAP` 把 22 个死因归并为：
   - 传染性疾病
   - 非传染性疾病
   - 伤害
3. 分别求和得到：
   - `communicable_deaths`
   - `ncd_deaths`
   - `injury_deaths`
   - `total_deaths`
4. 再计算：
   - `communicable_share = communicable_deaths / total_deaths`
   - `ncd_share = ncd_deaths / total_deaths`
   - `injury_share = injury_deaths / total_deaths`

## 3. 报告中的派生指标

下面这些不是原始 CSV 的单列，而是报告分析阶段算出来的结果列。

| 指标 | 报告写法 | 输出字段/表项 | 生成位置 | 依赖字段 |
|---|---|---|---|---|
| 投入指数 | `I^{input}` | `input_index`，在资源缺口表里对应 `actual_resource_index` | `src/hdi/analysis/competition.py` | `physicians_per_1000`, `beds_per_1000`, `health_exp_pct_gdp`, `health_exp_per_capita` |
| 产出指数 | `I^{output}` | `output_index` | `src/hdi/analysis/competition.py` | `life_expectancy`, `infant_mortality`, `under5_mortality` |
| 理论需求指数 | `I^{need}` | `theoretical_need`，在资源缺口表里对应 `theoretical_need_index` | `src/hdi/analysis/competition.py` | `communicable_share`, `infant_mortality`, `under5_mortality`, `life_expectancy`（反向） |
| 资源缺口 | `Gap` | `gap` | `api_output/dim3/resource_gap.json`，`reports/tables/tab_dim3_most_under_resourced.csv` | `actual_resource_index - theoretical_need_index` |
| 缺口等级 | A-E | `gap_grade`, `gap_grade_en` | 同上 | `gap` 的五分位分组 |
| 四象限分类 | `Q1`~`Q4` | `quadrant` | `api_output/dim3/efficiency.json` | `input_index` 与 `output_index` 的截面中位数切分 |
| 效率分数 | `Efficiency` | `efficiency` | `api_output/dim3/efficiency.json` | `output_index - input_index` |
| 当前投入 | 公式中的 `x_i^{current}` | `current` | `reports/tables/tab_dim3_top_reallocation.csv` | 当前 `health_exp_per_capita` |
| 优化后投入 | 公式中的最优投入 | `optimal` | `reports/tables/tab_dim3_top_reallocation.csv` | 优化模型解 |
| 投入变化量 | - | `change` | 同上 | `optimal - current` |
| 投入变化比例 | - | `change_pct` | 同上 | `(optimal - current) / current` |
| 当前预测产出 | - | `projected_output_current` | 同上 | 对数生产函数 `a * ln(x + 1) + b` |
| 优化后预测产出 | - | `projected_output_optimal` | 同上 | 同上 |
| 预测产出增量 | - | `projected_output_delta` | 同上 | `projected_output_optimal - projected_output_current` |

补充说明：

- 报告正文给出的 D3 公式是“简化版口径”。
- 当前代码在覆盖率足够时，还可能把 `nurses_per_1000`、`adult_mortality_male`、`adult_mortality_female` 纳入增强版指数计算；这是代码增强，不是报告正文主公式的核心口径。

## 4. 中国省级部分

中国省级面板主要落在 `data/processed/china_panel.parquet`，构建逻辑见 `src/hdi/data/china_provincial.py`。

| 中文含义 | 报告中的写法/缩写 | 标准字段 | 处理层表项 | 原始文件/来源 | 原始表项/口径 | 备注 |
|---|---|---|---|---|---|---|
| 卫生人员数量 | - | `health_personnel_wan` | `china_panel.parquet` | `各省近20年卫生人员数量.csv` | 行为 `地区`，列为各年份，数值单位为“万人” | 省级原始时序表 |
| 卫生机构数量 | - | `health_institutions` | `china_panel.parquet` | `近20年各省医疗卫生机构数量.csv` | 行为 `地区`，列为各年份，数值为机构数量 | 省级原始时序表 |
| 常住人口 | - | `population_wan` | `china_panel.parquet` | `src/hdi/data/china_provincial.py` 内嵌 `_CENSUS_2020_POP` | 2020 年人口普查口径，单位“万人” | 来自年鉴/普查整理，非赛题原始 CSV 直接给出 |
| 每千人卫生人员 | `PersonnelDensity` | `personnel_per_1000` | `china_panel.parquet` | 派生 | `health_personnel_wan / population_wan * 1000` | 省级 D3 投入指数成分 |
| 每万人机构数 | `InstitutionDensity` | `institutions_per_10k` | `china_panel.parquet` | 派生 | `health_institutions / population_wan` | 因 `population_wan` 单位为“万人” |
| 预期寿命 | `LE_p` | `life_expectancy` | `china_panel.parquet` | `src/hdi/data/china_provincial.py` 内嵌 `_LIFE_EXPECTANCY_2020` | 2020 年省级出生时预期寿命 | 省级值来自年鉴整理，不是 `近20年我国人口出生率死亡率自然增长率及平均预期寿命.csv` 中的全国总值 |
| 婴儿死亡率 | `IMR_p` | `infant_mortality` | `china_panel.parquet` | `src/hdi/data/china_provincial.py` 内嵌 `_INFANT_MORTALITY_2020` | 2020 年省级婴儿死亡率（‰） | 省级参考数据 |
| 人均卫生支出 | `HExpPC_p` | `health_exp_per_capita` | `china_panel.parquet` | `src/hdi/data/china_provincial.py` 内嵌 `_HEALTH_EXP_PER_CAPITA_2020` | 2020 年省级人均卫生支出（元/人） | 省级 D3 投入指数成分，也是省级优化输入 |
| 省级投入指数 | `I_p^{input}` | `input_index` | 中国省级快照/API 输出 | `src/hdi/data/china_provincial.py` | `personnel_per_1000`, `institutions_per_10k`, `health_exp_per_capita` 标准化均值 | 派生 |
| 省级产出指数 | `I_p^{output}` | `output_index` | 中国省级快照/API 输出 | `src/hdi/data/china_provincial.py` | `life_expectancy` 与 `infant_mortality`（反向）标准化均值 | 派生 |
| 省级理论需求指数 | `I_p^{need}` | `theoretical_need` | 中国省级快照/API 输出 | `src/hdi/data/china_provincial.py` | `life_expectancy`（反向）与 `infant_mortality` 标准化均值 | 派生 |
| 省级资源缺口 | `Gap_p` | `gap` | 中国省级快照/API 输出 | `src/hdi/data/china_provincial.py` | `input_index - theoretical_need` | 派生 |
| 省级效率 | - | `efficiency` | 中国省级快照/API 输出 | `src/hdi/data/china_provincial.py` | `output_index - input_index` | 派生 |
| 省级四象限 | - | `quadrant` | 中国省级快照/API 输出 | `src/hdi/data/china_provincial.py` | 由 `input_index`/`output_index` 中位数切分 | 派生 |

### 4.1 中国部分补充字段

虽然报告 8.1 节只重点写了几个核心字段，但 `china_panel.parquet` 还补充了以下省级参考字段，来源同样在 `src/hdi/data/china_provincial.py` 的内嵌年鉴字典中：

| 字段 | 来源口径 |
|---|---|
| `hospital_beds_per_1000` | `_HOSPITAL_BEDS_PER_1000_2020`，2020 年每千人口床位数 |
| `physicians_per_1000` | `_PHYSICIANS_PER_1000_2020`，2020 年每千人口执业医师数 |
| `nurses_per_1000` | `_NURSES_PER_1000_2020`，2020 年每千人口注册护士数 |
| `gdp_per_capita` | `_GDP_PER_CAPITA_2023`，2023 年省级人均 GDP |
| `maternal_mortality` | `_MATERNAL_MORTALITY_2020`，2020 年孕产妇死亡率 |
| `under5_mortality` | `_UNDER5_MORTALITY_2020`，2020 年 5 岁以下死亡率 |

## 5. 一眼容易混淆的几个点

1. 报告回归公式中的 `HealthExp` 对应的是 `health_exp_pct_gdp`，不是 `health_exp_per_capita`。
2. 报告中的 `Beds` 对应处理层字段 `beds_per_1000`，但原始指标名是 `Hospital beds (per 1,000 people)`。
3. `communicable_share`、`ncd_share`、`injury_share` 都是**由死因死亡数汇总后派生**，不是原始 HNP/WDI 直接字段。
4. 中国省级 `life_expectancy`、`infant_mortality`、`health_exp_per_capita` 不是赛题原始两张省级时序 CSV 直接自带，而是 `china_provincial.py` 根据年鉴整理后补入。
5. `近20年我国人口出生率死亡率自然增长率及平均预期寿命.csv` 只提供全国总量/全国平均，不提供省级预期寿命，因此不能直接作为省级 `life_expectancy` 来源。

## 6. 代码定位

如需继续往下追代码，优先看这几个文件：

- `src/hdi/config.py`
- `src/hdi/data/cleaners.py`
- `src/hdi/data/integrator.py`
- `src/hdi/analysis/competition.py`
- `src/hdi/data/china_provincial.py`

