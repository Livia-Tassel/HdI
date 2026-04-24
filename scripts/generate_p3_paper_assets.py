#!/usr/bin/env python3
"""Generate static assets for reports/paper/p3/paper.md."""

from __future__ import annotations

import json
import subprocess
import tempfile
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import plotly.express as px
import seaborn as sns
from matplotlib import font_manager as fm
from matplotlib.patches import Patch, Polygon
from matplotlib.ticker import FuncFormatter
from PIL import Image
from plotly.io import to_html

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "reports" / "paper" / "assets"

RESOURCE_GAP_PATH = ROOT / "api_output" / "dim3" / "resource_gap.json"
EFFICIENCY_PATH = ROOT / "api_output" / "dim3" / "efficiency.json"
EQUITY_PATH = ROOT / "api_output" / "dim3" / "equity.json"
OPTIMIZATION_PATH = ROOT / "api_output" / "dim3" / "optimization.json"
CHINA_ANALYSIS_PATH = ROOT / "api_output" / "dim3" / "china_analysis.json"

GLOBAL_STORY_PATH = ROOT / "dashboard" / "data" / "global_story.json"
CHINA_STORY_PATH = ROOT / "dashboard" / "data" / "china_deep_dive.json"
CHINA_GEOJSON_PATH = ROOT / "dashboard" / "data" / "china_provinces.json"

CHROME_CANDIDATES = [
    Path("/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"),
    Path("/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge"),
]

WHO_REGION_COLORS = {
    "AFRO": "#D1495B",
    "AMRO": "#2E86AB",
    "EMRO": "#F18F01",
    "EURO": "#6C5B7B",
    "SEARO": "#4DAA57",
    "WPRO": "#8A5A44",
}

INCOME_COLORS = {
    "LIC": "#C73E1D",
    "LMC": "#E07A5F",
    "UMC": "#3D405B",
    "HIC": "#2A9D8F",
}

QUADRANT_COLORS = {
    "Q1_high_input_high_output": "#4E79A7",
    "Q2_low_input_high_output": "#59A14F",
    "Q3_high_input_low_output": "#E15759",
    "Q4_low_input_low_output": "#F28E2B",
    "Q1_高投入高产出": "#4E79A7",
    "Q2_低投入高产出": "#59A14F",
    "Q3_高投入低产出": "#E15759",
    "Q4_低投入低产出": "#F28E2B",
}

GAP_GRADE_COLORS = {
    "A_富余": "#2E86AB",
    "B_较充足": "#7EC8A5",
    "C_匹配": "#F3D36B",
    "D_不足": "#F4A261",
    "E_严重不足": "#C73E1D",
}
GAP_GRADE_ORDER = ["A_富余", "B_较充足", "C_匹配", "D_不足", "E_严重不足"]
GAP_GRADE_DISPLAY = {
    "A_富余": "A 富余",
    "B_较充足": "B 较充足",
    "C_匹配": "C 匹配",
    "D_不足": "D 不足",
    "E_严重不足": "E 严重不足",
}

QUADRANT_LABELS = {
    "Q1_high_input_high_output": "Q1 高投入-高产出",
    "Q2_low_input_high_output": "Q2 低投入-高产出",
    "Q3_high_input_low_output": "Q3 高投入-低产出",
    "Q4_low_input_low_output": "Q4 低投入-低产出",
    "unclassified": "未分类",
    "Q1_高投入高产出": "Q1 高投入-高产出",
    "Q2_低投入高产出": "Q2 低投入-高产出",
    "Q3_高投入低产出": "Q3 高投入-低产出",
    "Q4_低投入低产出": "Q4 低投入-低产出",
}

COUNTRY_TRANSLATIONS = {
    "Afghanistan": "阿富汗",
    "Algeria": "阿尔及利亚",
    "Argentina": "阿根廷",
    "Australia": "澳大利亚",
    "Austria": "奥地利",
    "Bahrain": "巴林",
    "Barbados": "巴巴多斯",
    "Belgium": "比利时",
    "Benin": "贝宁",
    "Burundi": "布隆迪",
    "Cabo Verde": "佛得角",
    "Canada": "加拿大",
    "Central African Republic": "中非共和国",
    "Chad": "乍得",
    "China": "中国",
    "Congo, Democratic Republic of": "刚果（金）",
    "Côte d'Ivoire": "科特迪瓦",
    "Croatia": "克罗地亚",
    "Cuba": "古巴",
    "Equatorial Guinea": "赤道几内亚",
    "Eritrea": "厄立特里亚",
    "Gambia, The": "冈比亚",
    "Greece": "希腊",
    "Guinea": "几内亚",
    "Hungary": "匈牙利",
    "Iceland": "冰岛",
    "Iran, Islamic Republic of": "伊朗",
    "Japan": "日本",
    "Lesotho": "莱索托",
    "Liberia": "利比里亚",
    "Madagascar": "马达加斯加",
    "Malaysia": "马来西亚",
    "Mali": "马里",
    "Malawi": "马拉维",
    "Montenegro": "黑山",
    "Mongolia": "蒙古",
    "Morocco": "摩洛哥",
    "Mozambique": "莫桑比克",
    "Namibia": "纳米比亚",
    "Niger": "尼日尔",
    "Nigeria": "尼日利亚",
    "Oman": "阿曼",
    "Panama": "巴拿马",
    "Qatar": "卡塔尔",
    "Senegal": "塞内加尔",
    "Sierra Leone": "塞拉利昂",
    "Somalia, Fed. Rep.": "索马里",
    "South Sudan": "南苏丹",
    "Sri Lanka": "斯里兰卡",
    "Sudan": "苏丹",
    "Sweden": "瑞典",
    "Switzerland": "瑞士",
    "Syrian Arab Republic": "叙利亚",
    "Tanzania": "坦桑尼亚",
    "Türkiye": "土耳其",
    "United States": "美国",
    "Uruguay": "乌拉圭",
    "Yemen, Republic of": "也门",
    "Zimbabwe": "津巴布韦",
}


def configure_style() -> None:
    sns.set_theme(style="whitegrid")
    plt.rcParams["axes.unicode_minus"] = False
    plt.rcParams["figure.facecolor"] = "white"
    plt.rcParams["savefig.facecolor"] = "white"
    plt.rcParams["font.size"] = 11
    plt.rcParams["axes.titlesize"] = 14
    plt.rcParams["axes.labelsize"] = 11
    plt.rcParams["legend.frameon"] = False

    for font_path in (
        Path("/System/Library/Fonts/STHeiti Light.ttc"),
        Path("/System/Library/Fonts/STHeiti Medium.ttc"),
        Path("/System/Library/Fonts/Hiragino Sans GB.ttc"),
        Path("/System/Library/Fonts/PingFang.ttc"),
    ):
        if font_path.exists():
            plt.rcParams["font.family"] = fm.FontProperties(fname=str(font_path)).get_name()
            break


def load_wrapped_dataframe(path: Path) -> pd.DataFrame:
    return pd.DataFrame(load_json(path)["data"])


def load_json(path: Path) -> dict:
    with open(path, "r", encoding="utf-8") as handle:
        return json.load(handle)


def save_matplotlib(fig: plt.Figure, filename: str, dpi: int = 260, *, tight: bool = True) -> Path:
    path = ASSETS / filename
    ASSETS.mkdir(parents=True, exist_ok=True)
    save_kwargs = {"dpi": dpi, "facecolor": "white"}
    if tight:
        save_kwargs["bbox_inches"] = "tight"
    fig.savefig(path, **save_kwargs)
    plt.close(fig)
    print(f"[saved] {path.relative_to(ROOT)}")
    return path


def pick_browser() -> Path:
    for candidate in CHROME_CANDIDATES:
        if candidate.exists():
            return candidate
    raise FileNotFoundError("No supported browser found for headless screenshots.")


def save_plotly(fig, filename: str, width: int = 1500, height: int = 920) -> Path:
    browser = pick_browser()
    output = ASSETS / filename
    ASSETS.mkdir(parents=True, exist_ok=True)
    fig.update_layout(width=width, height=height)

    config = {"displayModeBar": False, "responsive": False}
    with tempfile.TemporaryDirectory() as tmpdir:
        html_path = Path(tmpdir) / "figure.html"
        html_path.write_text(
            to_html(fig, include_plotlyjs="inline", full_html=True, config=config),
            encoding="utf-8",
        )
        cmd = [
            str(browser),
            "--headless",
            "--disable-gpu",
            "--hide-scrollbars",
            f"--window-size={width},{height}",
            "--virtual-time-budget=4000",
            f"--screenshot={output}",
            html_path.as_uri(),
        ]
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        if result.stdout.strip():
            print(result.stdout.strip())
    print(f"[saved] {output.relative_to(ROOT)}")
    return output


def stitch_horizontal(images: list[Path], filename: str, gap: int = 24, bg: str = "white") -> Path:
    opened = [Image.open(path).convert("RGB") for path in images]
    target_height = max(img.height for img in opened)
    resized = []
    for img in opened:
        if img.height != target_height:
            new_width = int(img.width * (target_height / img.height))
            img = img.resize((new_width, target_height), Image.Resampling.LANCZOS)
        resized.append(img)

    total_width = sum(img.width for img in resized) + gap * (len(resized) - 1)
    canvas = Image.new("RGB", (total_width, target_height), bg)
    x = 0
    for img in resized:
        canvas.paste(img, (x, 0))
        x += img.width + gap

    output = ASSETS / filename
    canvas.save(output)
    print(f"[saved] {output.relative_to(ROOT)}")
    return output


def draw_china_map(
    ax: plt.Axes,
    geojson: dict,
    fill_lookup: dict[str, str],
    missing_color: str = "#D9DEE7",
) -> None:
    for feature in geojson["features"]:
        name = feature["properties"].get("name")
        facecolor = fill_lookup.get(name, missing_color)
        geometry = feature["geometry"]
        polygons = geometry["coordinates"] if geometry["type"] == "MultiPolygon" else [geometry["coordinates"]]

        for polygon_group in polygons:
            if not polygon_group:
                continue
            shell = polygon_group[0]
            patch = Polygon(
                shell,
                closed=True,
                facecolor=facecolor,
                edgecolor="white",
                linewidth=0.6,
                joinstyle="round",
            )
            ax.add_patch(patch)

    ax.set_xlim(73, 136)
    ax.set_ylim(17, 55)
    ax.set_aspect("equal", adjustable="box")
    ax.set_xticks([])
    ax.set_yticks([])
    for spine in ax.spines.values():
        spine.set_visible(False)
    ax.set_facecolor("#F8FAFC")


def translate_country(name: str) -> str:
    return COUNTRY_TRANSLATIONS.get(name, name)


def short_objective_label(code: str) -> str:
    if "maximin" in code:
        return "公平优先"
    return "效率优先"


def fit_log_curve(x: np.ndarray, y: np.ndarray) -> tuple[float, float, float]:
    x = np.asarray(x, dtype=float)
    y = np.asarray(y, dtype=float)
    x = np.clip(x, 0.0, None)
    log_x = np.log(x + 1.0)
    b_coef, a_coef = np.polynomial.polynomial.polyfit(log_x, y, 1)
    y_hat = a_coef * log_x + b_coef
    ss_res = float(np.sum((y - y_hat) ** 2))
    ss_tot = float(np.sum((y - np.mean(y)) ** 2))
    r2 = 1.0 - ss_res / ss_tot if ss_tot else float("nan")
    return float(a_coef), float(b_coef), float(r2)


def format_number(value: float) -> str:
    if abs(value) >= 1000:
        return f"{value:,.0f}"
    if abs(value) >= 100:
        return f"{value:,.1f}"
    if abs(value) >= 10:
        return f"{value:,.1f}"
    return f"{value:.2f}"


def generate_global_gap_map(resource_gap: pd.DataFrame) -> None:
    df = resource_gap.copy()
    df["gap_grade"] = pd.Categorical(df["gap_grade"], categories=GAP_GRADE_ORDER, ordered=True)
    df["gap_grade_label"] = df["gap_grade"].astype(str).map(GAP_GRADE_DISPLAY)
    display_order = [GAP_GRADE_DISPLAY[item] for item in GAP_GRADE_ORDER]
    display_colors = {GAP_GRADE_DISPLAY[key]: value for key, value in GAP_GRADE_COLORS.items()}
    fig = px.choropleth(
        df,
        locations="iso3",
        color="gap_grade_label",
        hover_name="country_name",
        category_orders={"gap_grade_label": display_order},
        color_discrete_map=display_colors,
        projection="natural earth",
        custom_data=["gap", "who_region", "wb_income", "gap_grade_label"],
    )
    fig.update_traces(
        hovertemplate="<b>%{hovertext}</b><br>缺口等级：%{customdata[3]}<br>资源缺口：%{customdata[0]:.2f}<br>WHO地区：%{customdata[1]}<br>收入组：%{customdata[2]}<extra></extra>"
    )
    fig.update_geos(
        showframe=False,
        showcoastlines=True,
        coastlinecolor="#999999",
        bgcolor="white",
        projection_scale=1.18,
        domain=dict(x=[0.0, 0.90], y=[0.02, 0.98]),
    )
    fig.update_layout(
        paper_bgcolor="white",
        plot_bgcolor="white",
        legend_title_text="缺口等级",
        legend=dict(x=0.92, y=0.95, xanchor="left", yanchor="top"),
        font=dict(family="PingFang SC, Hiragino Sans GB, Microsoft YaHei, SimHei, Arial", size=18),
        margin=dict(l=10, r=10, t=10, b=10),
    )
    save_plotly(fig, "p3_01_global_gap_map.png", width=1440, height=1080)


def generate_global_gap_top15(resource_gap: pd.DataFrame) -> None:
    top15 = resource_gap.sort_values("gap").head(15).copy()
    top15["country_label"] = top15["country_name"].map(translate_country)
    fig, ax = plt.subplots(figsize=(10.5, 7.8))
    colors = top15["who_region"].map(WHO_REGION_COLORS)
    ax.barh(top15["country_label"], top15["gap"], color=colors)
    ax.axvline(0, color="#666666", linewidth=1.0)
    ax.set_title("图3-2 2023年资源缺口最严重的前15个国家")
    ax.set_xlabel("资源缺口指数（越低表示越不足）")
    ax.set_ylabel("")
    for y, value in enumerate(top15["gap"]):
        ax.text(value - 0.05, y, f"{value:.2f}", va="center", ha="right", color="black", fontsize=10)
    handles = [
        plt.Line2D([0], [0], color=color, lw=8, label=region)
        for region, color in WHO_REGION_COLORS.items()
        if region in set(top15["who_region"])
    ]
    ax.legend(handles=handles, title="WHO地区", loc="lower right")
    ax.text(
        0.01,
        0.03,
        f"前15个严重不足国家中，AFRO地区占 {int((top15['who_region'] == 'AFRO').sum())} 个。",
        transform=ax.transAxes,
        fontsize=10,
        color="#555555",
    )
    save_matplotlib(fig, "p3_02_global_gap_top15.png")


def generate_global_quadrant(efficiency: pd.DataFrame) -> None:
    df = efficiency[efficiency["quadrant"] != "unclassified"].copy()
    input_median = df["input_index"].median()
    output_median = df["output_index"].median()
    fig, ax = plt.subplots(figsize=(10.5, 8.5))

    order = [
        "Q1_high_input_high_output",
        "Q2_low_input_high_output",
        "Q3_high_input_low_output",
        "Q4_low_input_low_output",
    ]
    for quadrant in order:
        subset = df[df["quadrant"] == quadrant]
        ax.scatter(
            subset["input_index"],
            subset["output_index"],
            s=42,
            alpha=0.78,
            color=QUADRANT_COLORS[quadrant],
            label=QUADRANT_LABELS[quadrant],
            edgecolors="white",
            linewidths=0.5,
        )

    ax.axvline(input_median, color="#666666", linestyle="--", linewidth=1.2)
    ax.axhline(output_median, color="#666666", linestyle="--", linewidth=1.2)
    ax.set_title("图3-3 2023年全球卫生资源投入-产出四象限")
    ax.set_xlabel("投入指数")
    ax.set_ylabel("产出指数")
    ax.legend(loc="upper left")

    selected = {
        "China": (10, 8),
        "Türkiye": (8, -14),
        "Sri Lanka": (8, 8),
        "Malaysia": (8, -12),
        "Chad": (8, -10),
        "Somalia, Fed. Rep.": (8, -8),
        "Niger": (8, 8),
        "Mali": (8, 8),
    }
    for country_name, offset in selected.items():
        row = df[df["country_name"] == country_name]
        if row.empty:
            continue
        x = float(row.iloc[0]["input_index"])
        y = float(row.iloc[0]["output_index"])
        ax.annotate(
            translate_country(country_name),
            (x, y),
            textcoords="offset points",
            xytext=offset,
            fontsize=10,
            color="#222222",
        )

    ax.text(input_median + 0.05, output_median + 1.0, "Q1", fontsize=12, color="#4E79A7", fontweight="bold")
    ax.text(input_median - 1.15, output_median + 1.0, "Q2", fontsize=12, color="#59A14F", fontweight="bold")
    ax.text(input_median + 0.05, output_median - 1.2, "Q3", fontsize=12, color="#E15759", fontweight="bold")
    ax.text(input_median - 1.15, output_median - 1.2, "Q4", fontsize=12, color="#F28E2B", fontweight="bold")
    save_matplotlib(fig, "p3_03_global_quadrant.png")


def generate_global_equity_trends(global_story: dict) -> None:
    equity = pd.DataFrame(global_story["health_equity"])
    metric_specs = [
        ("theil", "#C73E1D"),
        ("sigma", "#6C5B7B"),
    ]
    fig, axes = plt.subplots(2, 1, figsize=(10, 7.5), sharex=True)
    for ax, (column, color) in zip(axes, metric_specs, strict=False):
        ax.plot(equity["year"], equity[column], color=color, linewidth=2.4)
        ax.fill_between(equity["year"], equity[column], color=color, alpha=0.12)
        ax.scatter([equity["year"].iloc[0], equity["year"].iloc[-1]], [equity[column].iloc[0], equity[column].iloc[-1]], color=color, s=34)
        ax.yaxis.set_major_formatter(FuncFormatter(lambda value, _: f"{value:.3f}"))
        ax.tick_params(axis="x", labelbottom=True)
        ax.text(
            0.02,
            0.05,
            f"2000: {equity[column].iloc[0]:.3f}\n2023: {equity[column].iloc[-1]:.3f}",
            transform=ax.transAxes,
            fontsize=9,
            color="#555555",
        )
    axes[0].set_ylabel("指标值")
    axes[1].set_ylabel("指标值")
    axes[1].set_xlabel("年份")
    fig.subplots_adjust(left=0.10, right=0.97, top=0.96, bottom=0.10, hspace=0.30)
    save_matplotlib(fig, "p3_04_global_equity_trends.png", tight=False)


def generate_global_group_fairness(equity_payload: dict) -> None:
    income = pd.DataFrame(equity_payload["by_income_group"]).copy()
    income["income_group"] = pd.Categorical(income["income_group"], categories=["LIC", "LMC", "UMC", "HIC"], ordered=True)
    income = income.sort_values("income_group")

    quadrant = pd.DataFrame(equity_payload["by_quadrant"]).copy()
    quadrant = quadrant[quadrant["quadrant"] != "unclassified"].copy()
    quadrant["quadrant_label"] = quadrant["quadrant"].map(QUADRANT_LABELS)

    fig, axes = plt.subplots(1, 2, figsize=(15.2, 5.4))

    ax = axes[0]
    ax2 = ax.twinx()
    ax.bar(
        income["income_group"],
        income["avg_health_exp"],
        color=[INCOME_COLORS[group] for group in income["income_group"]],
        alpha=0.85,
    )
    ax2.plot(income["income_group"], income["avg_life_expectancy"], color="#2E4057", marker="o", linewidth=2.2)
    ax.set_title("收入组：平均卫生支出与寿命水平")
    ax.set_ylabel("人均卫生支出（美元）")
    ax2.set_ylabel("平均预期寿命（岁）")
    ax.yaxis.set_major_formatter(FuncFormatter(lambda value, _: f"{value:,.0f}"))

    ax = axes[1]
    x = np.arange(len(quadrant))
    width = 0.36
    ax.bar(x - width / 2, quadrant["gini_life_expectancy"], width=width, label="寿命Gini", color="#4E79A7")
    ax.bar(x + width / 2, quadrant["gini_health_exp"], width=width, label="卫生支出Gini", color="#F28E2B")
    ax.set_xticks(x)
    ax.set_xticklabels(quadrant["quadrant_label"], rotation=12)
    ax.set_ylabel("组内不平等指标")
    ax.set_title("四象限：组内寿命与卫生支出不平等")
    ax.legend(loc="upper left")
    ax.yaxis.set_major_formatter(FuncFormatter(lambda value, _: f"{value:.2f}"))

    fig.suptitle("图3-5 全球分组公平性对比", y=1.03, fontsize=15)
    fig.tight_layout()
    save_matplotlib(fig, "p3_05_global_group_fairness.png")


def generate_production_fit(global_opt: dict, china_payload: dict) -> None:
    global_base = pd.DataFrame(
        next(item for item in global_opt["scenarios"] if item["scenario_id"] == "max_output_budget_100")["allocation"]
    )
    china_base = pd.DataFrame(china_payload["provinces"]).copy()
    china_x = china_base["health_exp_per_capita"].to_numpy(dtype=float)
    china_y = china_base["output_index"].to_numpy(dtype=float)
    china_a, china_b, china_r2 = fit_log_curve(china_x, china_y)

    # --- Per-quadrant fits for global ---
    _q_order = [
        "Q1_high_input_high_output",
        "Q2_low_input_high_output",
        "Q3_high_input_low_output",
        "Q4_low_input_low_output",
    ]
    quad_fits: dict[str, tuple[float, float, float, np.ndarray, np.ndarray]] = {}
    for q in _q_order:
        qdf = global_base[global_base["quadrant"] == q] if "quadrant" in global_base.columns else pd.DataFrame()
        if len(qdf) >= 5:
            qx = qdf["current"].to_numpy(dtype=float)
            qy = qdf["output_index"].to_numpy(dtype=float)
            qa, qb, qr2 = fit_log_curve(qx, qy)
        else:
            gx = global_base["current"].to_numpy(dtype=float)
            gy = global_base["output_index"].to_numpy(dtype=float)
            qa, qb, qr2 = fit_log_curve(gx, gy)
            qx, qy = gx, gy
        quad_fits[q] = (qa, qb, qr2, qdf["current"].to_numpy(dtype=float) if len(qdf) >= 1 else np.array([]),
                        qdf["output_index"].to_numpy(dtype=float) if len(qdf) >= 1 else np.array([]))

    fig, axes = plt.subplots(1, 2, figsize=(15.5, 5.8))

    # --- Left subplot: global per-quadrant scatter + 4 fit curves ---
    ax_global = axes[0]
    for q in _q_order:
        qa, qb, qr2, qx, qy = quad_fits[q]
        color = QUADRANT_COLORS.get(q, "#888888")
        label = QUADRANT_LABELS.get(q, q)
        ax_global.scatter(qx, qy, s=28, alpha=0.72, color=color, edgecolors="white", linewidths=0.3, label=label)
        if len(qx) >= 2:
            x_line = np.linspace(max(1.0, float(np.min(qx))), float(np.max(qx)), 200)
            y_line = qa * np.log(x_line + 1.0) + qb
            ax_global.plot(x_line, y_line, color=color, linewidth=1.8, alpha=0.9)
    ax_global.set_xscale("log")
    ax_global.set_title("全球国家样本（按四象限分组拟合）")
    ax_global.set_xlabel("人均卫生支出（对数刻度）")
    ax_global.set_ylabel("产出指数")
    ax_global.legend(loc="lower right", fontsize=8, framealpha=0.8)

    # Annotation: per-quadrant params
    lines = []
    for q in _q_order:
        qa, qb, qr2, _, _ = quad_fits[q]
        short = QUADRANT_LABELS.get(q, q).split(" ")[0]
        lines.append(f"{short}: a={qa:.3f}, b={qb:+.3f}, $R^2$={qr2:.3f}")
    ax_global.text(
        0.02, 0.03,
        "\n".join(lines),
        transform=ax_global.transAxes,
        fontsize=7.5,
        color="#333333",
        verticalalignment="bottom",
        bbox={"boxstyle": "round,pad=0.3", "facecolor": "white", "alpha": 0.7},
    )

    # --- Right subplot: China (unchanged) ---
    ax_china = axes[1]
    ax_china.scatter(china_x, china_y, s=32, alpha=0.72, color="#4E79A7", edgecolors="white", linewidths=0.4)
    x_line = np.linspace(max(1.0, float(np.min(china_x))), float(np.max(china_x)), 300)
    y_line = china_a * np.log(x_line + 1.0) + china_b
    ax_china.plot(x_line, y_line, color="#C73E1D", linewidth=2.4)
    ax_china.set_xscale("log")
    ax_china.set_title("中国省级样本")
    ax_china.set_xlabel("人均卫生支出（对数刻度）")
    ax_china.text(
        0.03, 0.05,
        f"f(x) = {china_a:.3f}·ln(x+1) {china_b:+.3f}\n$R^2$ = {china_r2:.3f}",
        transform=ax_china.transAxes,
        fontsize=10,
        color="#444444",
    )

    fig.suptitle("图3-6 人均卫生支出与健康产出的对数生产函数拟合", y=1.03, fontsize=15)
    fig.tight_layout()
    save_matplotlib(fig, "p3_06_production_fit.png")


def combined_bar_entries(entries: list[dict], objective_code: str, label_key: str) -> list[dict]:
    rows = []
    for item in entries:
        rows.append(
            {
                "objective": short_objective_label(objective_code),
                "label": f"{short_objective_label(objective_code)}·{item[label_key]}",
                "value": abs(float(item["change"])),
            }
        )
    return rows


def generate_global_optimization_compare(global_opt: dict) -> None:
    scenarios = {
        item["scenario_id"]: item
        for item in global_opt["scenarios"]
        if item["scenario_id"] in {"max_output_budget_100", "maximin_budget_100"}
    }
    objective_color = {"效率优先": "#4E79A7", "公平优先": "#F28E2B"}

    fig, axes = plt.subplots(2, 2, figsize=(15.6, 10.2))

    moved = pd.DataFrame(
        [
            {
                "objective": short_objective_label(scenario["objective"]),
                "moved_budget": scenario["summary"]["moved_budget"],
            }
            for scenario in scenarios.values()
        ]
    )
    axes[0, 0].bar(
        moved["objective"],
        moved["moved_budget"],
        color=[objective_color[item] for item in moved["objective"]],
    )
    axes[0, 0].set_yscale("log")
    axes[0, 0].set_title("预算移动总量")
    axes[0, 0].set_ylabel("资源调整量（对数刻度）")
    for idx, value in enumerate(moved["moved_budget"]):
        axes[0, 0].text(idx, value * 1.08, format_number(value), ha="center", va="bottom", fontsize=10)

    counts = pd.DataFrame(
        [
            {
                "objective": short_objective_label(scenario["objective"]),
                "recipient_count": scenario["summary"]["recipient_count"],
                "donor_count": scenario["summary"]["donor_count"],
            }
            for scenario in scenarios.values()
        ]
    )
    x = np.arange(len(counts))
    width = 0.35
    axes[0, 1].bar(x - width / 2, counts["recipient_count"], width=width, color="#59A14F", label="净受益国")
    axes[0, 1].bar(x + width / 2, counts["donor_count"], width=width, color="#E15759", label="净转出国")
    axes[0, 1].set_xticks(x)
    axes[0, 1].set_xticklabels(counts["objective"])
    axes[0, 1].set_title("受益国与转出国数量")
    axes[0, 1].legend(loc="upper center")

    recipient_rows = []
    donor_rows = []
    for scenario in scenarios.values():
        recipient_rows.extend(combined_bar_entries(scenario["summary"]["top_recipients"][:5], scenario["objective"], "country_name"))
        donor_rows.extend(combined_bar_entries(scenario["summary"]["top_donors"][:5], scenario["objective"], "country_name"))

    recipient_df = pd.DataFrame(recipient_rows)
    recipient_df["label"] = recipient_df["label"].map(lambda value: "·".join([value.split("·", 1)[0], translate_country(value.split("·", 1)[1])]))
    recipient_df = recipient_df.sort_values("value")
    axes[1, 0].barh(
        recipient_df["label"],
        recipient_df["value"],
        color=[objective_color[item] for item in recipient_df["objective"]],
    )
    axes[1, 0].set_xscale("log")
    axes[1, 0].set_title("前5受益国家")
    axes[1, 0].set_xlabel("新增资源量（对数刻度）")

    donor_df = pd.DataFrame(donor_rows)
    donor_df["label"] = donor_df["label"].map(lambda value: "·".join([value.split("·", 1)[0], translate_country(value.split("·", 1)[1])]))
    donor_df = donor_df.sort_values("value")
    axes[1, 1].barh(
        donor_df["label"],
        donor_df["value"],
        color=[objective_color[item] for item in donor_df["objective"]],
    )
    axes[1, 1].set_xscale("log")
    axes[1, 1].set_title("前5转出国家")
    axes[1, 1].set_xlabel("转出资源量（对数刻度）")

    handles = [plt.Line2D([0], [0], color=color, lw=8, label=label) for label, color in objective_color.items()]
    fig.legend(handles=handles, loc="lower center", ncol=2, bbox_to_anchor=(0.5, -0.01))
    fig.suptitle("图3-7 全球预算持平情景下两类优化目标的再分配对比", y=1.02, fontsize=15)
    fig.tight_layout()
    save_matplotlib(fig, "p3_07_global_optimization_compare.png")


def generate_china_trends(china_story: dict, china_payload: dict) -> None:
    selected_provinces = [
        "广东省",
        "山东省",
        "河南省",
        "四川省",
        "西藏自治区",
        "宁夏回族自治区",
    ]
    province_map = {
        row["province"]: row["province_en"]
        for row in china_payload["provinces"]
    }
    palette = dict(zip(selected_provinces, sns.color_palette("tab10", len(selected_provinces)), strict=False))
    fig, axes = plt.subplots(1, 2, figsize=(15.2, 5.8), sharex=True)

    for province in selected_provinces:
        province_en = province_map[province]
        staff = pd.DataFrame(china_story["health_personnel"][province_en])
        inst = pd.DataFrame(china_story["health_institutions"][province_en])
        axes[0].plot(staff["year"], staff["value"], label=province, linewidth=2.0, color=palette[province])
        axes[1].plot(inst["year"], inst["value"], label=province, linewidth=2.0, color=palette[province])

    axes[0].set_title("卫生人员数量变化")
    axes[0].set_ylabel("万人")
    axes[0].set_xlabel("年份")
    axes[1].set_title("医疗卫生机构数量变化")
    axes[1].set_ylabel("个")
    axes[1].set_xlabel("年份")
    axes[0].legend(loc="upper left", fontsize=9)
    fig.suptitle("图3-8 2005–2024年中国代表性省份卫生资源趋势", y=1.03, fontsize=15)
    fig.tight_layout()
    save_matplotlib(fig, "p3_08_china_trends.png")


def generate_china_gap_efficiency(china_payload: dict, china_geojson: dict) -> None:
    provinces = pd.DataFrame(china_payload["provinces"]).copy()
    provinces["gap_grade"] = pd.Categorical(provinces["gap_grade"], categories=GAP_GRADE_ORDER, ordered=True)
    map_fig, map_ax = plt.subplots(figsize=(8.2, 6.8))
    fill_lookup = {row["province"]: GAP_GRADE_COLORS[row["gap_grade"]] for _, row in provinces.iterrows()}
    draw_china_map(map_ax, china_geojson, fill_lookup)
    map_ax.set_title("省级资源缺口分级", pad=14)
    legend_handles = [Patch(facecolor=GAP_GRADE_COLORS[item], label=GAP_GRADE_DISPLAY[item]) for item in GAP_GRADE_ORDER]
    legend_handles.append(Patch(facecolor="#D9DEE7", label="未纳入样本"))
    map_ax.legend(handles=legend_handles, title="缺口等级", loc="upper right", fontsize=9)
    map_path = save_matplotlib(map_fig, "_tmp_china_gap_map.png")

    fig, ax = plt.subplots(figsize=(8.4, 6.8))
    quadrant_order = ["Q1_高投入高产出", "Q2_低投入高产出", "Q3_高投入低产出", "Q4_低投入低产出"]
    for quadrant in quadrant_order:
        subset = provinces[provinces["quadrant"] == quadrant]
        ax.scatter(
            subset["input_index"],
            subset["output_index"],
            s=64,
            alpha=0.85,
            label=QUADRANT_LABELS[quadrant],
            color=QUADRANT_COLORS[quadrant],
            edgecolors="white",
            linewidths=0.5,
        )
    ax.axvline(provinces["input_index"].median(), color="#666666", linestyle="--", linewidth=1.1)
    ax.axhline(provinces["output_index"].median(), color="#666666", linestyle="--", linewidth=1.1)
    ax.set_title("省级投入-产出四象限")
    ax.set_xlabel("投入指数")
    ax.set_ylabel("产出指数")
    ax.legend(loc="upper left", fontsize=9)

    for province in ["云南省", "贵州省", "安徽省", "宁夏回族自治区", "新疆维吾尔自治区", "西藏自治区", "江苏省", "福建省", "广东省", "重庆市"]:
        row = provinces[provinces["province"] == province]
        if row.empty:
            continue
        ax.annotate(
            province.replace("维吾尔自治区", "").replace("壮族自治区", "").replace("回族自治区", "").replace("自治区", "").replace("省", "").replace("市", ""),
            (float(row.iloc[0]["input_index"]), float(row.iloc[0]["output_index"])),
            xytext=(6, 6),
            textcoords="offset points",
            fontsize=9,
            color="#333333",
        )

    scatter_path = save_matplotlib(fig, "_tmp_china_efficiency.png")
    stitch_horizontal([map_path, scatter_path], "p3_09_china_gap_efficiency.png")
    map_path.unlink(missing_ok=True)
    scatter_path.unlink(missing_ok=True)


def generate_china_optimization_compare(china_payload: dict) -> None:
    scenarios = {
        item["scenario_id"]: item
        for item in china_payload["optimization"]["scenarios"]
        if item["scenario_id"] in {"max_output_budget_100", "maximin_budget_100"}
    }
    objective_color = {"效率优先": "#4E79A7", "公平优先": "#F28E2B"}

    def moved_budget(scenario: dict) -> float:
        allocation = pd.DataFrame(scenario["allocation"])
        return float(allocation.loc[allocation["change"] > 0, "change"].sum())

    fig, axes = plt.subplots(2, 2, figsize=(15.6, 10.2))

    moved = pd.DataFrame(
        [
            {
                "objective": short_objective_label(scenario["objective"]),
                "moved_budget": moved_budget(scenario),
            }
            for scenario in scenarios.values()
        ]
    )
    axes[0, 0].bar(
        moved["objective"],
        moved["moved_budget"],
        color=[objective_color[item] for item in moved["objective"]],
    )
    axes[0, 0].set_title("预算移动总量")
    axes[0, 0].set_ylabel("资源调整量")
    for idx, value in enumerate(moved["moved_budget"]):
        axes[0, 0].text(idx, value * 1.02, format_number(value), ha="center", va="bottom", fontsize=10)

    counts = pd.DataFrame(
        [
            {
                "objective": short_objective_label(scenario["objective"]),
                "recipient_count": scenario["summary"]["recipient_count"],
                "donor_count": scenario["summary"]["donor_count"],
            }
            for scenario in scenarios.values()
        ]
    )
    x = np.arange(len(counts))
    width = 0.35
    axes[0, 1].bar(x - width / 2, counts["recipient_count"], width=width, color="#59A14F", label="净受益省份")
    axes[0, 1].bar(x + width / 2, counts["donor_count"], width=width, color="#E15759", label="净转出省份")
    axes[0, 1].set_xticks(x)
    axes[0, 1].set_xticklabels(counts["objective"])
    axes[0, 1].set_title("受益省份与转出省份数量")
    axes[0, 1].legend(loc="upper center")

    recipient_rows = []
    donor_rows = []
    for scenario in scenarios.values():
        recipient_rows.extend(combined_bar_entries(scenario["summary"]["top_recipients"][:5], scenario["objective"], "province"))
        donor_rows.extend(combined_bar_entries(scenario["summary"]["top_donors"][:5], scenario["objective"], "province"))

    recipient_df = pd.DataFrame(recipient_rows).sort_values("value")
    axes[1, 0].barh(
        recipient_df["label"],
        recipient_df["value"],
        color=[objective_color[item] for item in recipient_df["objective"]],
    )
    axes[1, 0].set_title("前5受益省份")
    axes[1, 0].set_xlabel("新增资源量")

    donor_df = pd.DataFrame(donor_rows).sort_values("value")
    axes[1, 1].barh(
        donor_df["label"],
        donor_df["value"],
        color=[objective_color[item] for item in donor_df["objective"]],
    )
    axes[1, 1].set_title("前5转出省份")
    axes[1, 1].set_xlabel("转出资源量")

    handles = [plt.Line2D([0], [0], color=color, lw=8, label=label) for label, color in objective_color.items()]
    fig.legend(handles=handles, loc="lower center", ncol=2, bbox_to_anchor=(0.5, -0.01))
    fig.suptitle("图3-10 中国预算持平情景下两类优化目标的再分配对比", y=1.02, fontsize=15)
    fig.tight_layout()
    save_matplotlib(fig, "p3_10_china_optimization_compare.png")


def main() -> None:
    configure_style()
    ASSETS.mkdir(parents=True, exist_ok=True)

    resource_gap = load_wrapped_dataframe(RESOURCE_GAP_PATH)
    efficiency = load_wrapped_dataframe(EFFICIENCY_PATH)
    equity_payload = load_json(EQUITY_PATH)["data"]
    global_opt = load_json(OPTIMIZATION_PATH)["data"]
    china_payload = load_json(CHINA_ANALYSIS_PATH)["data"]
    global_story = load_json(GLOBAL_STORY_PATH)
    china_story = load_json(CHINA_STORY_PATH)
    china_geojson = load_json(CHINA_GEOJSON_PATH)

    generate_global_gap_map(resource_gap)
    generate_global_gap_top15(resource_gap)
    generate_global_quadrant(efficiency)
    generate_global_equity_trends(global_story)
    generate_global_group_fairness(equity_payload)
    generate_production_fit(global_opt, china_payload)
    generate_global_optimization_compare(global_opt)
    generate_china_trends(china_story, china_payload)
    generate_china_gap_efficiency(china_payload, china_geojson)
    generate_china_optimization_compare(china_payload)


if __name__ == "__main__":
    main()
