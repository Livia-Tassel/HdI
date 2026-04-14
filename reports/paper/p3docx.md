# 问题3内容对应 report.docx 填写说明

> 本文件按照 `reports/report.docx` 的节结构，列出问题3（医疗资源模型）各部分内容应填入的位置及建议写法。
> 模板章节顺序：作品概述 → 问题分析与研究思路 → 数据集与预处理 → 分析框架与方法应用 → 系统实现与结果验证 → 作品总结与展望 → 参考文献 → 附录

---

## 一、作品概述

**对应模板**：`Heading 1 > 作品概述`

**填写内容**（建议不超过 1 页）：

本作品围绕"全球卫生资源分配与健康公平性"主题，以世界银行、WHO/IHME 等多源公开数据为基础，针对赛题提出的四个子问题，构建了一套"缺口识别—类型划分—优化模拟—政策建议"的闭环分析框架：

- **问题3-1**：定义投入指数、产出指数与理论需求指数，计算各国资源缺口并在全球地图上五级分类标注；
- **问题3-2**：以投入/产出双中位数为阈值将各国划入高投入-高产出（Q1）、低投入-高产出（Q2）、高投入-低产出（Q3）、低投入-低产出（Q4）四个象限，并通过 Gini 系数、Theil 指数、σ-收敛刻画健康公平性演变；
- **问题3-3**：以人均卫生支出为决策变量，分别建立"总产出最大化"（广义注水模型）和"公平优先"（Rawlsian maximin 模型）两套约束优化方案，并按四象限独立拟合对数生产函数参数，同时在中国 31 省样本中复刻省级规划；
- **问题3-4**：依据四象限分类，为 Q3 地区提出效率治理建议，为 Q2 地区总结可推广经验，为 Q4 地区设计补短板与提效并行方案。

---

## 二、问题分析与研究思路

### 2.1 问题分析

**对应模板**：`Heading 2 > 问题分析`

赛题第3问从四个维度提出要求：
1. 测算各国"实际资源配置水平"与"基于疾病负担的理论需求水平"之间的缺口并在地图上分级标注；
2. 建立评估矩阵，将各国分为四种投入-产出类型，并分析健康公平性；
3. 通过数学规划模型模拟卫生资源最优再分配（全球与一国内部两个场景）；
4. 为不同类型地区提供差异化政策建议。

核心挑战在于：健康系统涉及多维指标，需要构建可比较的综合指数；优化模型需同时兼顾效率目标与公平目标；跨国异质性（收入组、地区、象限）要求在建模时区分群体。

### 2.2 研究思路

**对应模板**：`Heading 2 > 研究思路`

整体研究脉络为**"指标构建 → 缺口识别 → 类型划分 → 公平评估 → 优化模拟 → 政策建议"**六步闭环：

1. 从多源数据中提取医生密度、床位密度、卫生支出等一级指标，构造投入指数 $I^{\text{input}}$、产出指数 $I^{\text{output}}$ 和需求指数 $I^{\text{need}}$ 三个综合二级指标；
2. 以 $\text{Gap} = I^{\text{input}} - I^{\text{need}}$ 量化各国资源缺口，五分位划级并可视化；
3. 以投入/产出双中位数划分四象限，获得国家类型标签；
4. 用 Gini、Theil、σ-收敛三种指标从时序与分组两个维度评估健康公平性；
5. 为每个象限单独拟合对数生产函数 $f_k(x) = a_k \ln(x+1) + b_k$，再分别在"效率优先"（广义注水）和"公平优先"（maximin SLSQP）框架下求解最优再分配；
6. 结合缺口与象限类型，提炼 Q3/Q2/Q4 三类地区的差异化政策建议。

### 2.3 技术路线

**对应模板**：`Heading 2 > 技术路线`

建议在此处插入技术路线图，主要模块包括：

```
原始数据（WB HNP/WDI, IHME GBD, 国家统计局）
    ↓  数据清洗与插补（pandas, sklearn.impute）
一级指标（Phys, Beds, HExp, HExpPC, CommSh, IMR, U5MR, LE）
    ↓  标准化 z-score → 加权合成
三类综合指数（Input / Output / Need）
    ├→ 资源缺口 Gap → 五级分类 → 全球地图（matplotlib, geopandas）
    ├→ 四象限分类 → 公平性分析（Gini/Theil/σ）→ 趋势图与分组图
    └→ 四象限分组拟合 f_k(x) → 约束优化（scipy.optimize.minimize）
            ├→ 全球6种再分配方案 → 对比可视化
            └→ 中国省级3种再分配方案 → 省级地图
    ↓
政策建议（Q3/Q2/Q4 差异化）
```

---

## 三、数据集与预处理

### 3.1 数据来源与类型

**对应模板**：`Heading 2 > 数据来源与类型`

| 编号 | 数据集 | 来源 | 类型 | 核心字段 | 规模 |
|------|--------|------|------|----------|------|
| 01 | 全球核心疾病与死亡估算 | IHME GBD | 结构化 CSV | 地理位置、年份、死因、死亡人数及上下界 | 22类死因，2000–2023年 |
| 02 | 全球健康风险因素 | IHME GBD | 结构化 CSV | 地理位置、年份、死因、风险因素、死亡人数 | 20类风险，2000–2023年 |
| 03 | 全球健康营养与人口统计 | 世界银行 HNP | 结构化 CSV | SP/SH/SN/SE/SL 类指标，含 LE、IMR、U5MR 等 | 2.5 GB，多国多年 |
| 04 | 社会经济指标 | 世界银行 WDI | 结构化 CSV（6文件） | WDICSV、WDICountry（含收入组）、WDISeries 等 | 1960–2024年 |
| 05 | 中国省级卫生数据 | 国家统计局 | 结构化 CSV | 卫生人员、医疗机构数、LE、IMR、出生率 | 31省×20年（2005–2024）|

### 3.2 数据预处理流程

**对应模板**：`Heading 2 > 数据预处理流程`

**一级指标提取**：

| 指标名称 | 代号 | 来源指标码 | 说明 |
|----------|------|-----------|------|
| 医生密度 | Phys | SH.MED.PHYS.ZS | 每千人医生数，03优先，缺失回退04 |
| 床位密度 | Beds | SH.MED.BEDS.ZS | 每千人床位数，03优先，缺失回退04 |
| 卫生支出占GDP | HExp | SH.XPD.CHEX.GD.ZS | 来自04 |
| 人均卫生支出 | HExpPC | SH.XPD.CHEX.PC.CD | 来自04，单位：当前美元 |
| 传染病占比 | CommSh | 数据集01聚合 | 传染病死亡/全因死亡 |
| 婴儿死亡率 | IMR | SP.DYN.IMRT.IN | 每千活产儿，03优先，缺失回退04 |
| 5岁以下死亡率 | U5MR | SH.DYN.MORT | 每千活产儿，03优先，缺失回退04 |
| 预期寿命 | LE | SP.DYN.LE00.IN | 岁，03优先，缺失回退04 |

**综合指数合成**（z-score 标准化后等权合成）：

$$I^{\text{input}} = \frac{1}{4}\left[z(\text{Phys}) + z(\text{Beds}) + z(\text{HExp\%}) + z(\text{HExpPC})\right]$$

$$I^{\text{output}} = \frac{1}{3}\left[z(\text{LE}) + z^{-}(\text{IMR}) + z^{-}(\text{U5MR})\right]$$

$$I^{\text{need}} = \frac{1}{4}\left[z(\text{CommSh}) + z(\text{IMR}) + z(\text{U5MR}) + z^{-}(\text{LE})\right]$$

---

## 四、分析框架与方法应用

**对应模板**：`Heading 1 > 分析框架与方法应用`

本节按赛题四个子问题分述各方法的逻辑与公式。

### 4.1 资源缺口识别（3-1）

**资源缺口**：

$$\text{Gap}_i = I_i^{\text{input}} - I_i^{\text{need}}$$

$\text{Gap}_i < 0$ 表示资源低于理论需求。按截面五分位将各国划分 A（富余）至 E（严重不足）五级，以 2023 年为基准截面。

2023 年资源缺口最严重的前 15 国**全部位于 AFRO 地区**，前五位依次为乍得、尼日利亚、索马里、中非共和国、南苏丹。

### 4.2 评估矩阵与公平性分析（3-2）

**四象限分类**（以投入/产出双中位数为阈值）：

$$Q_i = \begin{cases} \text{Q1: 高投入–高产出} & I_i^{\text{input}} \geq M^{\text{input}} \land I_i^{\text{output}} \geq M^{\text{output}} \\ \text{Q2: 低投入–高产出} & I_i^{\text{input}} < M^{\text{input}} \land I_i^{\text{output}} \geq M^{\text{output}} \\ \text{Q3: 高投入–低产出} & I_i^{\text{input}} \geq M^{\text{input}} \land I_i^{\text{output}} < M^{\text{output}} \\ \text{Q4: 低投入–低产出} & I_i^{\text{input}} < M^{\text{input}} \land I_i^{\text{output}} < M^{\text{output}} \end{cases}$$

2023 年 Q1/Q2/Q3/Q4 国家数量：71/24/26/72（另 10 国缺失）。

**公平性指标**：

- **Gini 系数**：$G = \frac{2\sum_{i} i \cdot y_i}{n \sum_i y_i} - \frac{n+1}{n}$（按预期寿命计算）
- **Theil 指数**：$T = \frac{1}{n}\sum_i \frac{y_i}{\bar{y}}\ln\frac{y_i}{\bar{y}}$，可分解为区域间与区域内
- **σ-收敛**：$\sigma_t = \sqrt{\frac{1}{n}\sum_i [\ln(y_{it}) - \overline{\ln(y_t)}]^2}$

2000–2023 年趋势：Gini 从 0.0816 降至 0.0600，Theil 从 0.0112 降至 0.0057，σ 从 0.1577 降至 0.1093，均呈收敛。

### 4.3 优化模型（3-3）

#### 4.3.1 分象限生产函数

为各象限 $k \in \{\text{Q1,Q2,Q3,Q4}\}$ 单独拟合：

$$f_k(x) = a_k \cdot \ln(x + 1) + b_k$$

参数 $(a_k, b_k)$ 由各象限国家截面最小二乘法拟合（象限内国家数 < 5 时退化为全局拟合）。

#### 4.3.2 总产出最大化（效率优先）

$$\max_{\mathbf{x}} \sum_{i} f_{k(i)}(x_i), \quad \text{s.t. } \sum_i x_i \leq B,\; x_i^{\min} \leq x_i \leq x_i^{\max}$$

预算情景：$B = \alpha \cdot \sum_i x_i^{\text{current}}$，$\alpha \in \{0.9, 1.0, 1.1\}$；约束区间 $[0.5x^{\text{cur}}, 2.0x^{\text{cur}}]$。

最优解（广义注水结构）：$x_i^* = \operatorname{clip}\!\left(\frac{a_{k(i)}}{\mu} - 1,\; x_i^{\min},\; x_i^{\max}\right)$，二分法求 $\mu$。

#### 4.3.3 Rawlsian maximin（公平优先）

$$\max_{\mathbf{x},\tau} \tau, \quad \text{s.t. } f_{k(i)}(x_i) \geq \tau,\; \sum_i x_i \leq B,\; x_i^{\min} \leq x_i \leq x_i^{\max}$$

约束区间 $[0.3x^{\text{cur}}, 2.0x^{\text{cur}}]$，SLSQP 求解。

---

## 五、系统实现与结果验证

### 5.1 技术选型与实现细节

**对应模板**：`Heading 2 > 技术选型与实现细节`

| 模块 | 技术栈 |
|------|--------|
| 数据处理 | Python 3.10+, pandas, numpy |
| 优化求解 | scipy.optimize（SLSQP，二分法注水） |
| 可视化 | matplotlib, geopandas（世界地图） |
| 分象限拟合 | scipy.stats.linregress（对数变换后 OLS） |
| 中国地图 | shapefile + geopandas |
| 项目结构 | `src/hdi/analysis/competition.py`（主分析管线），`src/hdi/models/optimization.py`（优化算法），`scripts/generate_p3_paper_assets.py`（图表生成） |

关键实现细节：
- 分象限拟合后，各国的 $(a_{k(i)}, b_{k(i)})$ 存入 `optimize_base` DataFrame 的 `a_coef_fit`/`b_coef_fit` 列，通过列合并传入优化器，避免索引对齐错误；
- 广义注水算法（`_waterfill_box_budget_hetero`）通过二分法在 $\mu \in [0, \max(a_k)]$ 上搜索，当所有 $a_k$ 相等时自动退化为均匀注水；
- 中国省级优化仍沿用单组参数，不受分象限修改影响。

### 5.2 结果可视化呈现

**对应模板**：`Heading 2 > 结果可视化呈现`

| 图号 | 文件名 | 内容 | 核心结论 |
|------|--------|------|----------|
| 图3-1 | p3_01_global_gap_map.png | 2023年全球资源缺口五级地图 | 缺口集中于撒哈拉以南非洲 |
| 图3-2 | p3_02_global_gap_top15.png | 缺口最严重前15国 | 全部为AFRO国家，乍得居首 |
| 图3-3 | p3_03_global_quadrant.png | 2023年全球四象限散点图 | Q4占比最多（72国），Q2最少（24国） |
| 图3-4 | p3_04_global_equity_trends.png | 2000–2023年公平性趋势 | Gini/Theil/σ均呈下降收敛 |
| 图3-5 | p3_05_global_group_fairness.png | 收入组与象限内公平性对比 | HIC与LIC收入差距极大，Q2内部最平等 |
| 图3-6 | p3_06_production_fit.png | 四象限分组生产函数拟合 | 各象限斜率与截距差异明显 |
| 图3-7 | p3_07_global_optimization_compare.png | 全球预算持平再分配对比 | 效率优先：163受益/28转出；公平优先：9受益/182转出 |
| 图3-8 | p3_08_china_trends.png | 中国省份卫生资源趋势 | 人口大省总量领先，西部省份追赶加速 |
| 图3-9 | p3_09_china_gap_efficiency.png | 中国省级资源缺口与四象限 | 云南、新疆、贵州缺口最大 |
| 图3-10 | p3_10_china_optimization_compare.png | 中国预算持平再分配对比 | 效率与公平均指向"中西部补短板" |

---

## 六、作品总结与展望

### 6.1 作品特色与创新点

**对应模板**：`Heading 2 > 作品特色与创新点`

1. **分象限生产函数**：不同于统一拟合，本作品为 Q1–Q4 四类国家各自拟合对数生产函数，捕捉不同效率结构下卫生投入-产出的异质性，广义注水算法的最优解形式仍保留解析性；
2. **效率与公平双目标优化**：同时实现效率优先（注水模型）与公平优先（Rawlsian maximin）两套方案，并以三种预算情景形成 6 × 2 的对比矩阵；
3. **全球-中国双层分析**：在同一分析框架下同时完成全球国家间与中国省级内部的资源再分配模拟，结论互相印证；
4. **闭环政策建议**：将优化结果与四象限类型标签结合，为 Q3/Q2/Q4 三类地区分别提炼治理策略，形成"识别—模拟—建议"完整闭环。

### 6.2 应用推广与前景

**对应模板**：`Heading 2 > 应用推广与前景`

本框架可推广至更广泛的公共资源配置场景（教育资源、环境治理投入等），核心方法（分组生产函数拟合 + 广义注水/maximin 二选一优化）具有通用性。对于政策制定者，分象限结论可直接作为不同类型国家制定卫生财政策略的参考依据；Q2 国家的效率经验可作为 Q4 国家的学习样本。

### 6.3 作品不足与展望

**对应模板**：`Heading 2 > 作品不足与展望`

- 当前以人均卫生支出为唯一决策变量，未将医疗人力（医生密度、床位）纳入联合优化；
- 生产函数采用截面拟合，未考虑动态路径（面板数据模型）；
- 中国省级优化沿用单组参数，尚未对省内做进一步类型划分；
- 象限分类依赖中位数阈值，对极端国家/省份敏感性较高，未来可改用基于分位数或聚类的动态分组。

---

## 七、参考文献

**对应模板**：`Heading 1 > 参考文献`（按 GB/T 7714-2015 格式排列）

建议补充：
- World Bank, World Development Indicators (WDI). https://databank.worldbank.org/source/world-development-indicators
- IHME, Global Burden of Disease Study 2019. https://www.healthdata.org/gbd
- WHO, World Health Statistics 2023.
- Rawls, J. A Theory of Justice. Harvard University Press, 1971.
- 相关 scipy/numpy 技术文档（视引用需要）

---

## 八、附录

**对应模板**：`Heading 1 > 附录（可选）`

可放置以下补充材料：
- 核心代码片段：`src/hdi/models/optimization.py` 中的广义注水算法 `_waterfill_box_budget_hetero`；
- 四象限分组拟合参数表（各象限 $a_k$、$b_k$、$R^2$）；
- 全球 6 种再分配方案的完整对比数据表；
- 中国省级再分配方案详细结果表（各省净变化量）；
- 可视化 Dashboard 链接（如部署）。
