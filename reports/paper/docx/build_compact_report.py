from __future__ import annotations

import copy
import re
import shutil
import subprocess
import zipfile
from pathlib import Path

from docx import Document
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_LINE_SPACING
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Cm, Pt
from PIL import Image
from lxml import etree


ROOT = Path(__file__).resolve().parents[3]
DOCX_DIR = ROOT / "reports" / "paper" / "docx"
ASSET_DIR = ROOT / "reports" / "paper" / "assets"
TMP_DIR = ROOT / "tmp" / "docs"
TMP_ASSET_DIR = TMP_DIR / "compact_assets"

TEMPLATE_DOCX = DOCX_DIR / "temp.docx"
SOURCE_MD = DOCX_DIR / "compact_report.md"
BODY_DOCX = TMP_DIR / "compact_body.docx"
STYLED_BODY_DOCX = TMP_DIR / "compact_body_styled.docx"
OUTPUT_DOCX = DOCX_DIR / "compact_report.docx"

W_NS = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
R_NS = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"
PKG_REL_NS = "http://schemas.openxmlformats.org/package/2006/relationships"
CT_NS = "http://schemas.openxmlformats.org/package/2006/content-types"
NS = {"w": W_NS, "r": R_NS}

TABLE_MARKERS = {
    "[[TABLE_DATA_SOURCES]]": {
        "rows": [
            ["数据类型", "官方来源与地址", "关键字段", "主要用途"],
            ["全球死因数据", "IHME GBD Results Tool\nhttps://vizhub.healthdata.org/gbd-results/", "死因、死亡人数、年龄分组、国家、年份", "构建 ETI、识别疾病谱系与核心疾病"],
            ["全球风险因素数据", "IHME GBD Results Tool\nhttps://vizhub.healthdata.org/gbd-results/", "风险因素、归因死亡、暴露变化", "计算风险贡献比例与灰色关联度"],
            ["卫生与社会经济数据", "World Bank HNP / WDI\nhttps://databank.worldbank.org/source/health-nutrition-and-population-statistics\nhttps://databank.worldbank.org/source/world-development-indicators", "医生密度、床位密度、人均卫生支出、预期寿命、婴儿死亡率、收入组", "构建健康指标、投入/产出/需求指数"],
            ["中国省级卫生统计", "国家统计局年鉴数据库\nhttps://www.stats.gov.cn/sj/ndsj/", "卫生人员、医疗机构、预期寿命、出生率、死亡率", "开展中国省级风险分析与资源配置比较"],
        ],
        "widths": [2.1, 5.0, 4.0, 4.0],
        "font_size": 9,
    }
}


def extract_media(docx_name: str, image_name: str, out_path: Path) -> None:
    with zipfile.ZipFile(DOCX_DIR / docx_name) as zf:
        out_path.write_bytes(zf.read(f"word/media/{image_name}"))


def load_image(path: Path) -> Image.Image:
    return Image.open(path).convert("RGB")


def panel_side_by_side(left: Path, right: Path, out: Path, cell_w: int = 1000, cell_h: int = 700) -> None:
    images = [load_image(left), load_image(right)]
    canvas = Image.new("RGB", (cell_w * 2 + 80, cell_h + 40), "white")
    for idx, image in enumerate(images):
        fitted = image.copy()
        fitted.thumbnail((cell_w, cell_h))
        x = 20 + idx * (cell_w + 40) + (cell_w - fitted.width) // 2
        y = 20 + (cell_h - fitted.height) // 2
        canvas.paste(fitted, (x, y))
    canvas.save(out, quality=92)


def panel_three_horizontal(images: list[Path], out: Path, cell_w: int = 640, cell_h: int = 420) -> None:
    canvas = Image.new("RGB", (cell_w * 3 + 80, cell_h + 40), "white")
    for idx, path in enumerate(images):
        image = load_image(path)
        image.thumbnail((cell_w, cell_h))
        x = 20 + idx * (cell_w + 20) + (cell_w - image.width) // 2
        y = 20 + (cell_h - image.height) // 2
        canvas.paste(image, (x, y))
    canvas.save(out, quality=92)


def panel_two_by_two(images: list[Path], out: Path, cell_w: int = 760, cell_h: int = 420) -> None:
    canvas = Image.new("RGB", (cell_w * 2 + 60, cell_h * 2 + 60), "white")
    for idx, path in enumerate(images):
        image = load_image(path)
        image.thumbnail((cell_w, cell_h))
        row = idx // 2
        col = idx % 2
        x = 20 + col * (cell_w + 20) + (cell_w - image.width) // 2
        y = 20 + row * (cell_h + 20) + (cell_h - image.height) // 2
        canvas.paste(image, (x, y))
    canvas.save(out, quality=92)


def prepare_assets() -> None:
    TMP_DIR.mkdir(parents=True, exist_ok=True)
    TMP_ASSET_DIR.mkdir(parents=True, exist_ok=True)

    # Extract required images from P1/P2.
    extract_map = {
        ("p1.docx", "image19.jpeg"): TMP_ASSET_DIR / "p1_evolution.jpeg",
        ("p1.docx", "image20.jpeg"): TMP_ASSET_DIR / "p1_map.jpeg",
        ("p1.docx", "image29.jpeg"): TMP_ASSET_DIR / "p1_heatmap.jpeg",
        ("p1.docx", "image36.jpeg"): TMP_ASSET_DIR / "p1_forecast.jpeg",
        ("p2.docx", "image5.png"): TMP_ASSET_DIR / "p2_trend.png",
        ("p2.docx", "image7.png"): TMP_ASSET_DIR / "p2_attr_cvd.png",
        ("p2.docx", "image8.png"): TMP_ASSET_DIR / "p2_attr_tumor.png",
        ("p2.docx", "image9.png"): TMP_ASSET_DIR / "p2_attr_resp.png",
        ("p2.docx", "image13.png"): TMP_ASSET_DIR / "p2_policy_air.png",
        ("p2.docx", "image14.png"): TMP_ASSET_DIR / "p2_policy_manage.png",
        ("p2.docx", "image15.png"): TMP_ASSET_DIR / "p2_policy_smoke.png",
        ("p2.docx", "image16.png"): TMP_ASSET_DIR / "p2_policy_weight.png",
    }
    for (docx_name, image_name), out_path in extract_map.items():
        if not out_path.exists():
            extract_media(docx_name, image_name, out_path)

    # Copy direct assets for chapter 6.
    direct_assets = {
        ASSET_DIR / "p3_01_global_gap_map.png": TMP_ASSET_DIR / "p3_gap_map.png",
        ASSET_DIR / "p3_02_global_gap_top15.png": TMP_ASSET_DIR / "p3_gap_top15.png",
        ASSET_DIR / "p3_03_global_quadrant.png": TMP_ASSET_DIR / "p3_quadrant.png",
        ASSET_DIR / "p3_09_china_gap_efficiency.png": TMP_ASSET_DIR / "p3_china_gap.png",
        ASSET_DIR / "p3_07_global_optimization_compare.png": TMP_ASSET_DIR / "p3_global_opt.png",
        ASSET_DIR / "p3_10_china_optimization_compare.png": TMP_ASSET_DIR / "p3_china_opt.png",
    }
    for src, dst in direct_assets.items():
        if not dst.exists():
            shutil.copyfile(src, dst)

    panel_side_by_side(
        TMP_ASSET_DIR / "p1_map.jpeg",
        TMP_ASSET_DIR / "p1_evolution.jpeg",
        TMP_ASSET_DIR / "ch4_panel_a.png",
    )
    panel_side_by_side(
        TMP_ASSET_DIR / "p1_heatmap.jpeg",
        TMP_ASSET_DIR / "p1_forecast.jpeg",
        TMP_ASSET_DIR / "ch4_panel_b.png",
    )
    shutil.copyfile(TMP_ASSET_DIR / "p2_trend.png", TMP_ASSET_DIR / "ch5_trend.png")
    panel_three_horizontal(
        [
            TMP_ASSET_DIR / "p2_attr_cvd.png",
            TMP_ASSET_DIR / "p2_attr_tumor.png",
            TMP_ASSET_DIR / "p2_attr_resp.png",
        ],
        TMP_ASSET_DIR / "ch5_panel_attribution.png",
    )
    panel_two_by_two(
        [
            TMP_ASSET_DIR / "p2_policy_air.png",
            TMP_ASSET_DIR / "p2_policy_manage.png",
            TMP_ASSET_DIR / "p2_policy_smoke.png",
            TMP_ASSET_DIR / "p2_policy_weight.png",
        ],
        TMP_ASSET_DIR / "ch5_panel_policy.png",
    )
    panel_side_by_side(
        TMP_ASSET_DIR / "p3_gap_map.png",
        TMP_ASSET_DIR / "p3_gap_top15.png",
        TMP_ASSET_DIR / "ch6_panel_gap.png",
    )
    panel_side_by_side(
        TMP_ASSET_DIR / "p3_quadrant.png",
        TMP_ASSET_DIR / "p3_china_gap.png",
        TMP_ASSET_DIR / "ch6_panel_system.png",
    )
    panel_side_by_side(
        TMP_ASSET_DIR / "p3_global_opt.png",
        TMP_ASSET_DIR / "p3_china_opt.png",
        TMP_ASSET_DIR / "ch6_panel_optimization.png",
    )


def run_pandoc() -> None:
    subprocess.run(
        [
            "pandoc",
            str(SOURCE_MD),
            "-o",
            str(BODY_DOCX),
            f"--reference-doc={TEMPLATE_DOCX}",
            "--resource-path=.",
        ],
        check=True,
        cwd=ROOT,
    )


def set_run_font(run, size: int, bold: bool = False, east_asia: str = "黑体") -> None:
    run.font.size = Pt(size)
    run.bold = bold
    r_pr = run._element.get_or_add_rPr()
    r_fonts = r_pr.rFonts
    if r_fonts is None:
        r_fonts = OxmlElement("w:rFonts")
        r_pr.append(r_fonts)
    r_fonts.set(qn("w:eastAsia"), east_asia)


def apply_manual_heading(paragraph, level: int) -> None:
    paragraph.style = paragraph.part.document.styles["正文段落"]
    paragraph.alignment = WD_ALIGN_PARAGRAPH.LEFT
    paragraph.paragraph_format.first_line_indent = None
    paragraph.paragraph_format.space_before = Pt(8 if level == 1 else 4)
    paragraph.paragraph_format.space_after = Pt(4)
    for run in paragraph.runs:
        if level == 1:
            set_run_font(run, 15, True)
        elif level == 2:
            set_run_font(run, 13, True)
        elif level == 3:
            set_run_font(run, 11.5, True)


def style_generated_doc() -> None:
    doc = Document(BODY_DOCX)

    body_style = doc.styles["正文段落"]
    body_style.font.size = Pt(11)
    body_style.paragraph_format.line_spacing_rule = WD_LINE_SPACING.ONE_POINT_FIVE
    body_style.paragraph_format.line_spacing = 1.18
    body_style.paragraph_format.space_after = Pt(0)
    body_style.paragraph_format.space_before = Pt(0)
    body_style.paragraph_format.first_line_indent = Cm(0.74)

    caption_style = doc.styles["Caption"]
    caption_style.font.size = Pt(10)

    for paragraph in doc.paragraphs:
        text = paragraph.text.strip()
        has_drawing = bool(paragraph._p.xpath('.//*[local-name()="drawing"]'))
        has_math = bool(paragraph._p.xpath('.//*[local-name()="oMath" or local-name()="oMathPara"]'))
        style_name = paragraph.style.name if paragraph.style is not None else ""

        if style_name == "Heading 1" or text.startswith(("1 ", "2 ", "3 ", "4 ", "5 ", "6 ")) or text == "参考文献":
            apply_manual_heading(paragraph, 1)
            continue
        if style_name == "Heading 2" or any(text.startswith(prefix) for prefix in ("1.", "2.", "3.", "4.", "5.", "6.")):
            dot_count = text.split(" ")[0].count(".")
            apply_manual_heading(paragraph, 2 if dot_count == 1 else 3)
            continue

        if has_drawing and not text:
            paragraph.style = doc.styles["图表段落"]
            paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER
            paragraph.paragraph_format.first_line_indent = None
            continue

        if text.startswith(("图", "表")) and len(text) < 60:
            paragraph.style = doc.styles["Caption"]
            paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER
            paragraph.paragraph_format.first_line_indent = None
            continue

        if has_math and not text:
            paragraph.style = doc.styles["正文段落"]
            paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER
            paragraph.paragraph_format.first_line_indent = None
            continue

        paragraph.style = doc.styles["正文段落"]
        paragraph.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY

    for table in doc.tables:
        table.style = "Table Grid"
        table.alignment = WD_TABLE_ALIGNMENT.CENTER
        table.autofit = False
        for row_idx, row in enumerate(table.rows):
            for cell in row.cells:
                for paragraph in cell.paragraphs:
                    paragraph.paragraph_format.first_line_indent = None
                    paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER if row_idx == 0 else WD_ALIGN_PARAGRAPH.LEFT
                    for run in paragraph.runs:
                        run.font.size = Pt(9)
                        if row_idx == 0:
                            run.bold = True

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

    _, body_relationships = parse_relationships(body_files["word/_rels/document.xml.rels"])
    template_relationship_root, _ = parse_relationships(template_files["word/_rels/document.xml.rels"])

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
    for paragraph in list(doc.paragraphs):
        text = paragraph.text.strip()
        if text in TABLE_MARKERS:
            insert_table_after(doc, paragraph, text)
    doc.save(OUTPUT_DOCX)


def finalize_cover() -> None:
    doc = Document(OUTPUT_DOCX)
    doc.paragraphs[5].text = "作品编号："
    doc.paragraphs[6].text = "作品名称：全球健康转型、重点疾病负担与卫生资源配置的综合分析"
    doc.paragraphs[8].text = "填写日期：2026年4月22日"
    for paragraph in list(doc.paragraphs):
        if re.fullmatch(r"fig\d-\d", paragraph.text.strip()):
            paragraph._element.getparent().remove(paragraph._element)
    doc.save(OUTPUT_DOCX)


def main() -> None:
    prepare_assets()
    run_pandoc()
    style_generated_doc()
    merge_into_template()
    insert_native_tables()
    finalize_cover()


if __name__ == "__main__":
    main()
