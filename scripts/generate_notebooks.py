#!/usr/bin/env python3
"""Regenerate the competition notebooks around existing pipeline outputs."""

from __future__ import annotations

from pathlib import Path

import nbformat as nbf


ROOT = Path(__file__).resolve().parents[1]
NOTEBOOKS = ROOT / "notebooks"

COMMON_SETUP = """from pathlib import Path
import json
import sys

import pandas as pd
from IPython.display import Image, Markdown, display

ROOT = Path.cwd()
if not (ROOT / "src").exists():
    if ROOT.name == "notebooks" and (ROOT.parent / "src").exists():
        ROOT = ROOT.parent
    elif (ROOT.parent / "src").exists():
        ROOT = ROOT.parent
    else:
        raise RuntimeError("无法定位仓库根目录，请从项目根目录或 notebooks/ 目录启动 Notebook。")
if str(ROOT / "src") not in sys.path:
    sys.path.insert(0, str(ROOT / "src"))

def read_json(path: Path):
    with open(path, "r", encoding="utf-8") as handle:
        return json.load(handle)

def read_api(relpath: str):
    payload = read_json(ROOT / relpath)
    return payload.get("data", payload)

def show_image(relpath: str, width: int = 900):
    display(Image(filename=str(ROOT / relpath), width=width))

def require(*relpaths: str):
    missing = [path for path in relpaths if not (ROOT / path).exists()]
    if missing:
        raise FileNotFoundError(
            "缺少以下产物，请先运行 `PYTHONPATH=src python -m hdi.data.integrator` 和 "
            "`PYTHONPATH=src python -m hdi.analysis.competition`:\\n- " + "\\n- ".join(missing)
        )
"""


def md(text: str):
    return nbf.v4.new_markdown_cell(text.strip() + "\n")


def code(text: str):
    return nbf.v4.new_code_cell(text.strip() + "\n")


def notebook(title: str, intro: str, cells: list) -> nbf.NotebookNode:
    nb = nbf.v4.new_notebook()
    nb.metadata["kernelspec"] = {
        "display_name": "Python 3",
        "language": "python",
        "name": "python3",
    }
    nb.metadata["language_info"] = {"name": "python", "version": "3"}
    nb.cells = [
        md(f"# {title}\n\n{intro}"),
        code(COMMON_SETUP),
        *cells,
    ]
    return nb


NOTEBOOK_SPECS: dict[str, tuple[str, str, list]] = {
    "00_data_acquisition.ipynb": (
        "数据资产总览",
        "核查 provided 数据、处理后面板以及分析输出是否齐备。",
        [
            code(
                """
require(
    "data/raw/provided/01_disease_mortality/全球主要国家死亡原因/2000.csv",
    "data/raw/provided/02_risk_factors/全球各国健康风险因素数据/2000.csv",
    "data/raw/provided/03_nutrition_population/全球各国健康营养和人口统计数据/WB_HNP.csv",
    "data/raw/provided/04_socioeconomic/WDI_CSV/WDICSV.csv",
    "data/raw/provided/05_china_health/全国近20年卫生数据-国家统计局/各省近20年卫生人员数量.csv",
    "data/processed/master_panel.parquet",
    "api_output/metadata/summary.json",
)

datasets = [
    ("疾病死亡数据", "data/raw/provided/01_disease_mortality"),
    ("风险因素数据", "data/raw/provided/02_risk_factors"),
    ("健康营养与人口统计", "data/raw/provided/03_nutrition_population"),
    ("社会经济背景", "data/raw/provided/04_socioeconomic"),
    ("中国卫生数据", "data/raw/provided/05_china_health"),
]

rows = []
for label, relpath in datasets:
    directory = ROOT / relpath
    files = sorted([path for path in directory.rglob("*") if path.is_file() and not path.name.startswith(".")])
    rows.append({"数据集": label, "目录": relpath, "文件数": len(files), "样例文件": files[0].name if files else "无"})

display(pd.DataFrame(rows))
"""
            ),
            code(
                """
processed = [
    "data/processed/master_panel.parquet",
    "data/processed/resource_panel.parquet",
    "data/processed/china_panel.parquet",
    "api_output/dim1/trends.json",
    "api_output/dim2/paf.json",
    "api_output/dim3/resource_gap.json",
    "reports/figures/fig01_global_disease_transition.png",
]

status = [{"产物": relpath, "存在": (ROOT / relpath).exists()} for relpath in processed]
display(pd.DataFrame(status))
"""
            ),
        ],
    ),
    "01_data_cleaning.ipynb": (
        "清洗与面板构建",
        "展示真实数据经过清洗后生成的全球主面板、资源面板和中国省级面板。",
        [
            code(
                """
require(
    "data/processed/master_panel.parquet",
    "data/processed/resource_panel.parquet",
    "data/processed/china_panel.parquet",
)

master = pd.read_parquet(ROOT / "data/processed/master_panel.parquet")
resource = pd.read_parquet(ROOT / "data/processed/resource_panel.parquet")
china = pd.read_parquet(ROOT / "data/processed/china_panel.parquet")

display(pd.DataFrame([
    {"面板": "master_panel", "形状": master.shape, "国家数": master["iso3"].nunique(), "年份范围": f'{master["year"].min()}-{master["year"].max()}'},
    {"面板": "resource_panel", "形状": resource.shape, "国家数": resource["iso3"].nunique(), "年份范围": f'{resource["year"].min()}-{resource["year"].max()}'},
    {"面板": "china_panel", "形状": china.shape, "地区数": china["province"].nunique(), "年份范围": f'{china["year"].min()}-{china["year"].max()}'},
]))
"""
            ),
            code(
                """
display(master.head())
display(china.head())
"""
            ),
        ],
    ),
    "02_eda_overview.ipynb": (
        "探索性概览",
        "基于主面板快速浏览全球健康结果、资源和疾病结构。",
        [
            code(
                """
require("data/processed/master_panel.parquet", "api_output/metadata/summary.json")
master = pd.read_parquet(ROOT / "data/processed/master_panel.parquet")
summary = read_api("api_output/metadata/summary.json")

display(pd.Series(summary, name="summary").to_frame())
display(master[["life_expectancy", "communicable_share", "ncd_share", "gdp_per_capita"]].describe().T)
"""
            ),
            code(
                """
latest = master[master["year"] == master["year"].max()].copy()
latest = latest.sort_values("life_expectancy", ascending=False)
display(latest[["country_name", "who_region", "life_expectancy", "communicable_share", "ncd_share"]].head(15))
"""
            ),
        ],
    ),
    "10_dim1_spatiotemporal.ipynb": (
        "维度一：疾病谱系时空变迁",
        "读取真实导出的趋势数据和报告图，展示全球疾病谱系从传染性疾病向非传染性疾病的转变。",
        [
            code(
                """
require("api_output/dim1/trends.json", "reports/figures/fig01_global_disease_transition.png")
trends = pd.DataFrame(read_api("api_output/dim1/trends.json"))
display(trends.head())

latest_year = trends["year"].max()
latest = trends[trends["year"] == latest_year].copy()
latest["share"] = latest["deaths"] / latest["total_deaths"]
display(latest.sort_values(["cause_group", "share"], ascending=[True, False]).head(12))
"""
            ),
            code("""show_image("reports/figures/fig01_global_disease_transition.png")"""),
            code("""show_image("reports/figures/fig02_life_expectancy_vs_communicable_share.png")"""),
        ],
    ),
    "11_dim1_health_indicators.ipynb": (
        "维度一：关键健康指标差异与解释",
        "展示预期寿命回归结果及 2023 年高低表现国家的对比。",
        [
            code(
                """
require(
    "reports/tables/tab_dim1_life_expectancy_regression.csv",
    "reports/tables/tab_dim1_top_life_expectancy.csv",
    "reports/tables/tab_dim1_bottom_life_expectancy.csv",
)

reg = pd.read_csv(ROOT / "reports/tables/tab_dim1_life_expectancy_regression.csv")
top = pd.read_csv(ROOT / "reports/tables/tab_dim1_top_life_expectancy.csv")
bottom = pd.read_csv(ROOT / "reports/tables/tab_dim1_bottom_life_expectancy.csv")

display(reg)
display(top)
display(bottom)
"""
            ),
        ],
    ),
    "12_dim1_disease_prediction.ipynb": (
        "维度一：健康指标预测",
        "读取真实预测结果，查看代表国家预期寿命和疾病结构的延伸趋势。",
        [
            code(
                """
require("api_output/dim1/forecasts.json", "reports/figures/fig03_dim1_forecasts.png")
payload = read_api("api_output/dim1/forecasts.json")
display(pd.DataFrame([
    {
        "country": item["country"],
        "indicator": item["indicator"],
        "method": item["method"],
        "RMSE": item["metrics"]["RMSE"],
    }
    for item in payload
]))
"""
            ),
            code(
                """
sample = next(item for item in payload if item["country"] == payload[0]["country"] and item["indicator"] == payload[0]["indicator"])
display(pd.DataFrame(sample["forecast"]).head())
"""
            ),
            code("""show_image("reports/figures/fig03_dim1_forecasts.png")"""),
        ],
    ),
    "20_dim2_paf_attribution.ipynb": (
        "维度二：风险归因分解",
        "基于真实 provided 风险归因死亡数据展示最新年份的全球与地区风险贡献结构。",
        [
            code(
                """
require(
    "api_output/dim2/paf.json",
    "api_output/dim2/shapley_global.json",
    "reports/figures/fig04_dim2_global_risk_bar.png",
    "reports/figures/fig05_dim2_region_heatmap.png",
)

paf = pd.DataFrame(read_api("api_output/dim2/paf.json"))
shapley = pd.DataFrame(read_api("api_output/dim2/shapley_global.json"))

latest_year = paf["year"].max()
latest = paf[paf["year"] == latest_year].copy()
top_global = latest.groupby("risk_factor", as_index=False)["attributable_deaths"].sum().sort_values("attributable_deaths", ascending=False).head(10)

display(top_global)
display(shapley)
"""
            ),
            code("""show_image("reports/figures/fig04_dim2_global_risk_bar.png")"""),
            code("""show_image("reports/figures/fig05_dim2_region_heatmap.png")"""),
        ],
    ),
    "21_dim2_burden_projection.ipynb": (
        "维度二：归因死亡预测",
        "读取情景模拟输出，查看 2024-2030 年不同干预情景下的全球归因死亡趋势。",
        [
            code(
                """
require("api_output/dim2/scenarios.json", "reports/figures/fig06_dim2_scenarios.png")
scenarios = read_api("api_output/dim2/scenarios.json")

rows = []
for name, payload in scenarios.items():
    endpoint = payload["trajectories"]["total_attributable_deaths"][-1]
    rows.append({"scenario": name, "start_year": payload["years"][0], "end_year": payload["years"][-1], "2030预测": endpoint})

display(pd.DataFrame(rows))
"""
            ),
            code("""show_image("reports/figures/fig06_dim2_scenarios.png")"""),
        ],
    ),
    "22_dim2_policy_simulation.ipynb": (
        "维度二：政策强度比较",
        "对比基线、中等干预和强化干预情景的末端效果差异。",
        [
            code(
                """
require("api_output/dim2/scenarios.json")
scenarios = read_api("api_output/dim2/scenarios.json")

baseline = scenarios["A_baseline"]["trajectories"]["total_attributable_deaths"][-1]
comparison = []
for name, payload in scenarios.items():
    endpoint = payload["trajectories"]["total_attributable_deaths"][-1]
    comparison.append({
        "scenario": name,
        "2030预测": endpoint,
        "相对基线变化": endpoint - baseline,
        "相对基线变化率": (endpoint - baseline) / baseline if baseline else None,
    })

display(pd.DataFrame(comparison))
"""
            ),
        ],
    ),
    "23_dim2_intervention_priority.ipynb": (
        "维度二：优先干预清单",
        "读取各 WHO 地区主导风险与建议干预措施清单。",
        [
            code(
                """
require("data/processed/dim2_intervention_priority.parquet", "reports/tables/tab_dim2_region_priority.csv")
priority = pd.read_parquet(ROOT / "data/processed/dim2_intervention_priority.parquet")
display(priority)
"""
            ),
        ],
    ),
    "30_dim3_resource_gap.ipynb": (
        "维度三：资源缺口测算",
        "展示全球资源配置缺口最大的国家名单。",
        [
            code(
                """
require("api_output/dim3/resource_gap.json", "reports/tables/tab_dim3_most_under_resourced.csv")
resource_gap = pd.DataFrame(read_api("api_output/dim3/resource_gap.json"))
under = pd.read_csv(ROOT / "reports/tables/tab_dim3_most_under_resourced.csv")
display(resource_gap.head())
display(under)
"""
            ),
        ],
    ),
    "31_dim3_efficiency_matrix.ipynb": (
        "维度三：投入产出效率矩阵",
        "读取效率矩阵结果并展示四象限散点图。",
        [
            code(
                """
require("api_output/dim3/efficiency.json", "reports/figures/fig07_dim3_quadrant.png")
efficiency = pd.DataFrame(read_api("api_output/dim3/efficiency.json"))
display(efficiency["quadrant"].value_counts().rename_axis("quadrant").reset_index(name="count"))
display(efficiency.sort_values("efficiency", ascending=False).head(15))
"""
            ),
            code("""show_image("reports/figures/fig07_dim3_quadrant.png")"""),
        ],
    ),
    "32_dim3_optimization.ipynb": (
        "维度三：资源再分配模拟",
        "展示 need-weighted 优化模型下的资源再分配结果。",
        [
            code(
                """
require("api_output/dim3/optimization.json", "reports/tables/tab_dim3_top_reallocation.csv")
optimization = read_json(ROOT / "api_output/dim3/optimization.json")["data"]
allocation = pd.DataFrame(optimization["allocation"])
display(pd.Series({
    "objective": optimization["objective"],
    "status": optimization["status"],
    "objective_value": optimization["objective_value"],
}).to_frame("value"))
display(allocation.sort_values("change_pct", ascending=False).head(15))
"""
            ),
        ],
    ),
    "33_dim3_recommendations.ipynb": (
        "维度三：数据驱动建议",
        "综合缺口、效率和优化结果生成针对性的政策建议。",
        [
            code(
                """
require(
    "api_output/dim3/resource_gap.json",
    "api_output/dim3/efficiency.json",
    "data/processed/dim2_intervention_priority.parquet",
)

gap = pd.DataFrame(read_api("api_output/dim3/resource_gap.json")).sort_values("gap").head(5)
eff = pd.DataFrame(read_api("api_output/dim3/efficiency.json"))
priority = pd.read_parquet(ROOT / "data/processed/dim2_intervention_priority.parquet")

display(Markdown("## 资源缺口最大国家"))
display(gap[["country_name", "gap_grade", "gap"]])

display(Markdown("## Q2 低投入高产出样本"))
display(eff[eff["quadrant"] == "Q2_low_input_high_output"][["country_name", "efficiency"]].sort_values("efficiency", ascending=False).head(10))

display(Markdown("## 区域主导风险与建议干预"))
display(priority[["who_region", "primary_risk", "recommended_intervention"]])
"""
            ),
        ],
    ),
    "40_composite_index.ipynb": (
        "附录：综合指数说明",
        "GHRI 在本轮交付中不作为主线结果，Notebook 用于说明其状态和原因。",
        [
            code(
                """
require("api_output/metadata/ghri.json")
ghri = read_json(ROOT / "api_output/metadata/ghri.json")
display(pd.Series(ghri["meta"], name="ghri_meta").to_frame())
display(Markdown("当前主线交付聚焦赛题要求的三大维度，综合指数留作可选附录，因此接口返回不可用状态。"))
"""
            ),
        ],
    ),
    "99_report_figures.ipynb": (
        "报告图表总览",
        "汇总展示当前报告已经生成的核心图表。",
        [
            code(
                """
require(
    "reports/figures/fig01_global_disease_transition.png",
    "reports/figures/fig08_china_province_trends.png",
)

figures = sorted((ROOT / "reports/figures").glob("fig*.png"))
display(pd.DataFrame({"figure": [path.name for path in figures]}))
"""
            ),
            code(
                """
for relpath in [
    "reports/figures/fig01_global_disease_transition.png",
    "reports/figures/fig02_life_expectancy_vs_communicable_share.png",
    "reports/figures/fig03_dim1_forecasts.png",
    "reports/figures/fig04_dim2_global_risk_bar.png",
    "reports/figures/fig05_dim2_region_heatmap.png",
    "reports/figures/fig06_dim2_scenarios.png",
    "reports/figures/fig07_dim3_quadrant.png",
    "reports/figures/fig08_china_province_trends.png",
]:
    display(Markdown(f"### {Path(relpath).name}"))
    show_image(relpath, width=1000)
"""
            ),
        ],
    ),
}


def build_notebook(filename: str, title: str, intro: str, cells: list) -> None:
    nb = notebook(title=title, intro=intro, cells=cells)
    path = NOTEBOOKS / filename
    with open(path, "w", encoding="utf-8") as handle:
        nbf.write(nb, handle)


def main() -> None:
    NOTEBOOKS.mkdir(parents=True, exist_ok=True)
    for filename, (title, intro, cells) in NOTEBOOK_SPECS.items():
        build_notebook(filename, title, intro, cells)
        print(f"updated {filename}")


if __name__ == "__main__":
    main()
