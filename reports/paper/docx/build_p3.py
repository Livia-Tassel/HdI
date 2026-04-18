from __future__ import annotations

import copy
import re
import subprocess
import zipfile
from pathlib import Path

from docx import Document
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml.ns import qn
from docx.shared import Cm, Pt
from lxml import etree


ROOT = Path(__file__).resolve().parents[3]
DOCX_DIR = ROOT / "reports" / "paper" / "docx"
TMP_DIR = ROOT / "tmp" / "docs"

TEMPLATE_DOCX = DOCX_DIR / "temp.docx"
SOURCE_MD = DOCX_DIR / "p3_build.md"
BODY_DOCX = TMP_DIR / "p3_body.docx"
STYLED_BODY_DOCX = TMP_DIR / "p3_body_styled.docx"
OUTPUT_DOCX = DOCX_DIR / "p3.docx"

W_NS = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
R_NS = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"
PKG_REL_NS = "http://schemas.openxmlformats.org/package/2006/relationships"
CT_NS = "http://schemas.openxmlformats.org/package/2006/content-types"
NS = {"w": W_NS, "r": R_NS}

CAPTION_RE = re.compile(r"^(图|表)\s*3[-0-9A-Za-z]+\s+")
TABLE_MARKERS = {
    "[[TABLE_DATA_SOURCE]]": {
        "rows": [
            ["编号", "数据集", "来源", "类型", "核心字段", "规模"],
            ["01", "全球核心疾病与死亡估算", "IHME GBD", "结构化 CSV", "地理位置、年份、死因、死亡人数及上下界", "22 类死因，2000-2023 年"],
            ["02", "全球健康风险因素", "IHME GBD", "结构化 CSV", "地理位置、年份、风险因素、死亡人数", "20 类风险，2000-2023 年"],
            ["03", "全球健康营养与人口统计", "World Bank HNP", "结构化 CSV", "SP/SH/SN/SE/SL 指标，含 LE、IMR、U5MR", "2.5 GB，多国多年"],
            ["04", "社会经济指标", "World Bank WDI", "结构化 CSV", "WDICSV、WDICountry、WDISeries 等", "1960-2024 年"],
            ["05", "中国省级卫生数据", "国家统计局", "结构化 CSV", "卫生人员、医疗机构、寿命、出生率", "31 省 x 20 年"],
        ],
        "widths": [1.0, 2.6, 1.9, 1.8, 3.9, 2.6],
        "font_size": 9,
    },
    "[[TABLE_INDICATORS]]": {
        "rows": [
            ["指标名称", "代号", "来源指标码", "说明"],
            ["医生密度", "Phys", "SH.MED.PHYS.ZS", "每千人医生数，03 优先，缺失回退 04"],
            ["床位密度", "Beds", "SH.MED.BEDS.ZS", "每千人床位数，03 优先，缺失回退 04"],
            ["卫生支出占 GDP", "HExp", "SH.XPD.CHEX.GD.ZS", "世界银行指标，单位为百分比"],
            ["人均卫生支出", "HExpPC", "SH.XPD.CHEX.PC.CD", "当前美元口径"],
            ["传染性疾病占比", "CommSh", "数据集 01 聚合", "传染病死亡占全因死亡比例"],
            ["婴儿死亡率", "IMR", "SP.DYN.IMRT.IN", "每千活产儿死亡数"],
            ["5 岁以下死亡率", "U5MR", "SH.DYN.MORT", "每千活产儿死亡数"],
            ["预期寿命", "LE", "SP.DYN.LE00.IN", "出生时预期寿命，单位为岁"],
        ],
        "widths": [2.5, 1.3, 3.1, 7.0],
        "font_size": 10,
    },
    "[[TABLE_PARAMS]]": {
        "rows": [
            ["象限", "a_k", "b_k"],
            ["Q1（高投入-高产出）", "0.2416", "-1.0029"],
            ["Q2（低投入-高产出）", "0.2231", "-0.7705"],
            ["Q3（高投入-低产出）", "0.1446", "-1.2631"],
            ["Q4（低投入-低产出）", "0.4086", "-2.6890"],
        ],
        "widths": [6.5, 2.8, 2.8],
        "font_size": 10,
    },
    "[[TABLE_TECH_STACK]]": {
        "rows": [
            ["模块", "技术栈"],
            ["数据处理", "Python 3.10+, pandas, numpy"],
            ["缺失插补", "sklearn.impute"],
            ["优化求解", "scipy.optimize, 二分注水搜索"],
            ["可视化", "matplotlib, geopandas"],
            ["分组拟合", "scipy.stats 或最小二乘 OLS"],
            ["项目落地", "src/hdi/analysis/competition.py；src/hdi/models/optimization.py"],
        ],
        "widths": [3.0, 10.0],
        "font_size": 10,
    },
    "[[TABLE_FIG_SUMMARY]]": {
        "rows": [
            ["图号", "图表内容", "核心结论"],
            ["图3-0", "技术路线图", "展示问题三整体建模流程"],
            ["图3-1", "全球资源缺口五级地图", "缺口集中于撒哈拉以南非洲"],
            ["图3-2", "缺口最严重前 15 国", "前 15 名全部位于 AFRO 地区"],
            ["图3-3", "全球四象限散点图", "Q4 国家占比最高，Q2 最少"],
            ["图3-4", "全球公平性趋势图", "Gini、Theil、sigma 均呈下降趋势"],
            ["图3-5", "分组公平性对比图", "HIC 与 LIC 差距显著，Q2 内部最平等"],
            ["图3-6", "分象限生产函数拟合图", "Q4 边际回报最高，Q3 最低"],
            ["图3-7", "全球再分配对比图", "效率优先广覆盖，公平优先定向扶持"],
            ["图3-8", "中国省级趋势图", "人口大省总量领先，西部省份追赶加快"],
            ["图3-9", "中国资源缺口与象限图", "云南、新疆、贵州等地缺口突出"],
            ["图3-10", "中国再分配对比图", "中西部补短板是共同方向"],
        ],
        "widths": [1.7, 4.1, 7.4],
        "font_size": 9,
    },
}


def run_pandoc() -> None:
    TMP_DIR.mkdir(parents=True, exist_ok=True)
    subprocess.run(
        [
            "pandoc",
            str(SOURCE_MD),
            "-o",
            str(BODY_DOCX),
            f"--reference-doc={TEMPLATE_DOCX}",
        ],
        check=True,
        cwd=ROOT,
    )


def paragraph_has_drawing(paragraph) -> bool:
    return bool(paragraph._p.xpath('.//*[local-name()="drawing"]'))


def paragraph_has_math(paragraph) -> bool:
    return bool(
        paragraph._p.xpath(
            './/*[local-name()="oMath" or local-name()="oMathPara"]'
        )
    )


def style_generated_doc() -> None:
    doc = Document(BODY_DOCX)
    current_h1 = ""

    for paragraph in doc.paragraphs:
        text = paragraph.text.strip()
        has_drawing = paragraph_has_drawing(paragraph)
        has_math = paragraph_has_math(paragraph)
        style_name = paragraph.style.name if paragraph.style is not None else ""

        if style_name == "Heading 1":
            current_h1 = text
            continue
        if style_name in {"Heading 2", "Heading 3"}:
            continue

        if has_drawing and not text:
            paragraph.style = doc.styles["图表段落"]
            paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER
            paragraph.paragraph_format.first_line_indent = None
            continue

        if has_math and not text:
            paragraph.style = doc.styles["正文段落"]
            paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER
            paragraph.paragraph_format.first_line_indent = None
            continue

        if CAPTION_RE.match(text):
            paragraph.style = doc.styles["Caption"]
            paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER
            paragraph.paragraph_format.first_line_indent = None
            continue

        if current_h1 == "参考文献":
            paragraph.style = doc.styles["正文段落"]
            paragraph.alignment = WD_ALIGN_PARAGRAPH.LEFT
            paragraph.paragraph_format.first_line_indent = None
            continue

        if current_h1 == "附录（可选）":
            paragraph.style = doc.styles["正文段落"]
            continue

        paragraph.style = doc.styles["正文段落"]

    for table in doc.tables:
        table.style = "Table Grid"
        table.alignment = WD_TABLE_ALIGNMENT.CENTER
        for row_idx, row in enumerate(table.rows):
            for cell in row.cells:
                for paragraph in cell.paragraphs:
                    paragraph.paragraph_format.first_line_indent = None
                    paragraph.alignment = (
                        WD_ALIGN_PARAGRAPH.CENTER
                        if row_idx == 0
                        else WD_ALIGN_PARAGRAPH.LEFT
                    )
                    for run in paragraph.runs:
                        run.font.size = Pt(10)

    doc.save(STYLED_BODY_DOCX)


def parse_relationships(xml_bytes: bytes):
    root = etree.fromstring(xml_bytes)
    rels = {}
    for rel in root:
        rels[rel.get("Id")] = rel
    return root, rels


def next_rid(existing_ids: set[str]) -> str:
    max_id = 0
    for rid in existing_ids:
        if rid.startswith("rId"):
            suffix = rid[3:]
            if suffix.isdigit():
                max_id = max(max_id, int(suffix))
    candidate = max_id + 1
    while f"rId{candidate}" in existing_ids:
        candidate += 1
    return f"rId{candidate}"


def paragraph_text(element) -> str:
    return "".join(element.xpath(".//w:t/text()", namespaces=NS)).strip()


def make_page_break_paragraph():
    paragraph = etree.Element(f"{{{W_NS}}}p")
    run = etree.SubElement(paragraph, f"{{{W_NS}}}r")
    etree.SubElement(run, f"{{{W_NS}}}br", attrib={f"{{{W_NS}}}type": "page"})
    return paragraph


def merge_into_template() -> None:
    with zipfile.ZipFile(TEMPLATE_DOCX) as template_zip, zipfile.ZipFile(
        STYLED_BODY_DOCX
    ) as body_zip:
        template_files = {name: template_zip.read(name) for name in template_zip.namelist()}
        body_files = {name: body_zip.read(name) for name in body_zip.namelist()}

    template_doc = etree.fromstring(template_files["word/document.xml"])
    body_doc = etree.fromstring(body_files["word/document.xml"])

    template_body = template_doc.find(f"{{{W_NS}}}body")
    body_body = body_doc.find(f"{{{W_NS}}}body")
    if template_body is None or body_body is None:
        raise RuntimeError("Unable to locate document body.")

    template_blocks = [child for child in template_body if child.tag != f"{{{W_NS}}}sectPr"]
    body_blocks = [child for child in body_body if child.tag != f"{{{W_NS}}}sectPr"]

    cover_blocks = [copy.deepcopy(block) for block in template_blocks[:9]]

    sect_pr = template_body.find(f"{{{W_NS}}}sectPr")
    if sect_pr is None:
        raise RuntimeError("Unable to locate section settings in template.")

    for child in list(template_body):
        template_body.remove(child)

    _, body_relationships = parse_relationships(
        body_files["word/_rels/document.xml.rels"]
    )
    template_relationship_root, _ = parse_relationships(
        template_files["word/_rels/document.xml.rels"]
    )

    existing_rids = {
        rel.get("Id") for rel in template_relationship_root.xpath("./pr:Relationship", namespaces={"pr": PKG_REL_NS})
    }
    copied_media: dict[str, bytes] = {}
    rel_id_map: dict[str, str] = {}
    copied_blocks = []

    for block in body_blocks:
        new_block = copy.deepcopy(block)

        for node in new_block.xpath(".//*[@r:embed or @r:id or @r:link]", namespaces=NS):
            for rel_attr in (qn("r:embed"), qn("r:id"), qn("r:link")):
                source_rid = node.get(rel_attr)
                if not source_rid:
                    continue
                if source_rid in rel_id_map:
                    node.set(rel_attr, rel_id_map[source_rid])
                    continue

                rel = body_relationships.get(source_rid)
                if rel is None:
                    continue

                new_rid = next_rid(existing_rids)
                existing_rids.add(new_rid)
                rel_id_map[source_rid] = new_rid
                node.set(rel_attr, new_rid)

                new_rel = copy.deepcopy(rel)
                new_rel.set("Id", new_rid)

                target = new_rel.get("Target", "")
                mode = new_rel.get("TargetMode")
                if mode != "External" and target.startswith("media/"):
                    source_path = f"word/{target}"
                    suffix = Path(target).suffix
                    media_name = f"word/media/{new_rid}{suffix}"
                    copied_media[media_name] = body_files[source_path]
                    new_rel.set("Target", f"media/{new_rid}{suffix}")

                template_relationship_root.append(new_rel)

        copied_blocks.append(new_block)

    for block in cover_blocks:
        template_body.append(block)
    template_body.append(make_page_break_paragraph())
    for block in copied_blocks:
        template_body.append(block)

    template_body.append(copy.deepcopy(sect_pr))

    template_files["word/document.xml"] = etree.tostring(
        template_doc, encoding="UTF-8", xml_declaration=True
    )
    template_files["word/_rels/document.xml.rels"] = etree.tostring(
        template_relationship_root, encoding="UTF-8", xml_declaration=True
    )

    content_types = etree.fromstring(template_files["[Content_Types].xml"])
    existing_extensions = {
        node.get("Extension")
        for node in content_types.findall(f"{{{CT_NS}}}Default")
    }
    for ext, content_type in (("png", "image/png"), ("jpg", "image/jpeg"), ("jpeg", "image/jpeg")):
        if ext not in existing_extensions:
            content_types.append(
                etree.Element(
                    f"{{{CT_NS}}}Default",
                    Extension=ext,
                    ContentType=content_type,
                )
            )
    template_files["[Content_Types].xml"] = etree.tostring(
        content_types, encoding="UTF-8", xml_declaration=True
    )

    template_files.update(copied_media)

    with zipfile.ZipFile(OUTPUT_DOCX, "w", compression=zipfile.ZIP_DEFLATED) as out_zip:
        for name, data in template_files.items():
            out_zip.writestr(name, data)


def set_paragraph_text(paragraph, text: str) -> None:
    for child in list(paragraph._p):
        if child.tag != qn("w:pPr"):
            paragraph._p.remove(child)
    paragraph.add_run(text)


def insert_table_after(doc: Document, paragraph, marker: str) -> None:
    spec = TABLE_MARKERS[marker]
    rows = spec["rows"]
    widths = spec["widths"]
    font_size = spec["font_size"]

    table = doc.add_table(rows=len(rows), cols=len(rows[0]))
    table.style = "Table Grid"
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    table.autofit = False

    for r_idx, row_data in enumerate(rows):
        for c_idx, value in enumerate(row_data):
            cell = table.cell(r_idx, c_idx)
            cell.width = Cm(widths[c_idx])
            cell.text = value
            for p in cell.paragraphs:
                p.style = doc.styles["Normal"]
                p.paragraph_format.first_line_indent = None
                p.alignment = WD_ALIGN_PARAGRAPH.CENTER if r_idx == 0 else WD_ALIGN_PARAGRAPH.LEFT
                for run in p.runs:
                    run.font.size = Pt(font_size)
                    if r_idx == 0:
                        run.bold = True

    paragraph._p.addnext(table._tbl)
    parent = paragraph._element.getparent()
    parent.remove(paragraph._element)


def insert_native_tables() -> None:
    doc = Document(OUTPUT_DOCX)
    markers = {marker: False for marker in TABLE_MARKERS}

    for paragraph in list(doc.paragraphs):
        text = paragraph.text.strip()
        if text in TABLE_MARKERS:
            insert_table_after(doc, paragraph, text)
            markers[text] = True

    missing = [marker for marker, found in markers.items() if not found]
    if missing:
        raise RuntimeError(f"Missing table markers: {missing}")

    doc.save(OUTPUT_DOCX)


def finalize_cover() -> None:
    doc = Document(OUTPUT_DOCX)
    set_paragraph_text(doc.paragraphs[5], "作品编号：")
    set_paragraph_text(doc.paragraphs[6], "作品名称：全球卫生资源分配与健康公平性分析")
    set_paragraph_text(doc.paragraphs[8], "填写日期：2026年4月18日")
    doc.save(OUTPUT_DOCX)


def main() -> None:
    if not TEMPLATE_DOCX.exists():
        raise FileNotFoundError(TEMPLATE_DOCX)
    if not SOURCE_MD.exists():
        raise FileNotFoundError(SOURCE_MD)

    run_pandoc()
    style_generated_doc()
    merge_into_template()
    insert_native_tables()
    finalize_cover()


if __name__ == "__main__":
    main()
