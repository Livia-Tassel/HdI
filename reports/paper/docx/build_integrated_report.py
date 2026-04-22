from __future__ import annotations

import copy
import re
import zipfile
from pathlib import Path

from docx import Document
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Pt
from docx.text.paragraph import Paragraph
from lxml import etree


ROOT = Path(__file__).resolve().parents[3]
DOCX_DIR = ROOT / "reports" / "paper" / "docx"
TMP_DIR = ROOT / "tmp" / "docs"

TEMPLATE_DOCX = DOCX_DIR / "temp.docx"
OUTPUT_DOCX = DOCX_DIR / "integrated_report.docx"
FRONT_DOCX = TMP_DIR / "integrated_front.docx"

W_NS = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
R_NS = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"
PKG_REL_NS = "http://schemas.openxmlformats.org/package/2006/relationships"
CT_NS = "http://schemas.openxmlformats.org/package/2006/content-types"
NS = {"w": W_NS, "r": R_NS}

H1_RE = re.compile(r"^\d+\s+")
H2_RE = re.compile(r"^\d+\.\d+\s+")
H3_RE = re.compile(r"^\d+\.\d+\.\d+\s+")
H4_RE = re.compile(r"^\d+\.\d+\.\d+\.\d+\s+")
FIG_ONLY_RE = re.compile(r"^图\s*(\d+-\d+)")
TAB_ONLY_RE = re.compile(r"^表\s*(\d+-\d+)")


FRONT_STRUCTURE: list[tuple[str, list[tuple[str, list[str]]]]] = [
    (
        "1 研究背景和意义",
        [
            (
                "1.1 研究背景",
                [
                    "当前全球公共卫生体系正经历从传染性疾病主导向慢性非传染性疾病主导的深刻转型，但这种转型并非同步发生。不同国家和地区在疾病谱系、健康结果、风险暴露水平以及卫生资源配置能力上存在显著差异，使全球健康不平等呈现出明显的时空异质性。",
                    "赛题所关注的并不仅是疾病负担本身，更强调从“健康格局识别、重点风险解析、资源优化配置”三个层面理解健康问题的形成机制与治理路径。这意味着研究不能停留在单一指标比较上，而需要构建贯通宏观格局、中观机制与政策模拟的综合分析框架。",
                ],
            ),
            (
                "1.2 研究意义",
                [
                    "从理论上看，围绕疾病谱系演化、重点疾病风险归因以及卫生资源公平配置开展一体化研究，有助于打通“现状诊断—机制解释—策略推演”的分析链条，提升健康治理问题研究的系统性与解释力。",
                    "从实践上看，本研究既能够识别全球及中国重点地区的健康短板和风险重点，也能够为卫生资源定向投入、重点疾病防控和分类型治理提供量化依据，从而为提升公共卫生治理效能与健康公平水平提供数据支撑。",
                ],
            ),
        ],
    ),
    (
        "2 研究目标和内容",
        [
            (
                "2.1 研究目标",
                [
                    "本研究旨在构建一套覆盖全球健康格局识别、重点疾病风险解析与卫生资源优化配置的综合研究框架，系统回答三类核心问题：全球疾病谱系和健康指标如何演化，重点疾病负担由哪些风险驱动，以及有限卫生资源应如何在效率与公平之间实现更优配置。",
                    "围绕这一总体目标，研究进一步聚焦三个层面：其一，识别全球疾病谱系与健康指标的时空分布特征及变化趋势；其二，刻画重点疾病负担的历史归因、动态驱动与政策情景下的演化路径；其三，评估卫生资源与疾病负担之间的匹配程度，并模拟全球国家间及中国省级内部的资源再分配方案。",
                ],
            ),
            (
                "2.2 研究内容",
                [
                    "第4章围绕问题一展开，重点描述全球疾病谱系的时空演化与健康格局变化，识别国家间健康指标差异及其影响因素，并在此基础上讨论健康趋势预测与优化路径。",
                    "第5章围绕问题二展开，聚焦重点疾病负担的风险归因、动态驱动与政策推演，通过核心疾病识别、灰色关联分析和情景模拟提出递阶式防控策略。",
                    "第6章围绕问题三展开，从理论需求出发识别卫生资源缺口，结合投入—产出矩阵与公平性指标评估卫生系统表现，并进一步构建效率优先与公平优先两类再分配模型，形成面向全球国家与中国省级地区的治理建议。",
                ],
            ),
        ],
    ),
    (
        "3 研究方法和技术路线",
        [
            (
                "3.1 总体研究方法",
                [
                    "方法体系上，研究综合采用多源数据融合、指标构建、时空聚类、回归分析、灰色关联分析、情景模拟、优化规划与公平性测度等方法，将描述性分析、机制分析与决策模拟贯通起来，形成由“识别问题”到“解释问题”再到“优化问题”的递进式研究路径。",
                    "其中，第4章强调全球尺度下的格局识别与健康差异解释，第5章强调重点疾病的风险驱动识别与中长期推演，第6章则强调卫生资源配置的效率—公平权衡与优化决策。三部分在问题侧重点上各有分工，在方法逻辑上相互衔接。",
                ],
            ),
            (
                "3.2 技术路线与分析闭环",
                [
                    "整体技术路线遵循“宏观格局扫描—关键风险聚焦—资源配置优化”的主线。首先，在全球尺度上刻画疾病谱系、健康指标和健康差异的时空分布，明确不同国家和地区的结构位置；其次，在重点疾病层面识别静态归因与动态驱动因素，并通过政策情景模拟预测未来负担变化；最后，将前两部分形成的风险识别和需求判断回收至卫生资源配置问题中，完成资源缺口识别、效率评估和再分配推演。",
                    "在这一闭环中，前端的格局识别为中段的重点风险锁定提供了比较背景，中段的风险变化判断又为末端的资源优先序设定提供了依据，最终使模型输出能够回到分类型治理建议与政策解释层面，形成完整的研究链条。",
                ],
            ),
            (
                "3.3 数据来源和预处理",
                [
                    "数据层面，研究主要整合IHME GBD数据库中的全球死亡与风险因素数据、世界银行HNP与WDI数据库中的卫生投入和社会经济指标，以及国家统计局发布的中国省级卫生统计数据。针对不同章节的研究目标，从上述数据库中提取全球国家样本、中国长期序列样本和中国省级横截面样本，形成兼顾国际比较与国内落地的分析基础。",
                    "预处理过程中，首先统一国家名称、年份口径和指标单位，对重复指标按照数据质量优先原则进行补齐与回退；其次，根据研究需要构造流行病学转型指数、健康表现指数、风险贡献比例、投入指数、产出指数和理论需求指数等核心变量；最后，通过标准化、对数变换、缺失处理和分组聚合，保证不同来源、不同量纲数据能够进入统一分析框架，为后续建模与比较提供可靠基础。",
                ],
            ),
        ],
    ),
]

REFERENCES = [
    "[1] Omran A R. The epidemiologic transition: a theory of the epidemiology of population change[J]. The Milbank Quarterly, 1971, 49(4): 509-538.",
    "[2] Kulldorff M, Heffernan R, Hartman J, et al. A space-time permutation scan statistic for disease outbreak detection[J]. PLoS Medicine, 2005, 2(3): e59.",
    "[3] Deng J. Control problems of grey systems[J]. Systems & Control Letters, 1982, 1(5): 288-294.",
    "[4] Breiman L. Random forests[J]. Machine Learning, 2001, 45(1): 5-32.",
    "[5] World Health Organization. Noncommunicable diseases: progress monitor 2020[R]. Geneva: World Health Organization, 2020.",
    "[6] Institute for Health Metrics and Evaluation. Global Burden of Disease Results Tool[DB/OL]. Seattle: IHME, 2024[2026-04-22]. https://vizhub.healthdata.org/gbd-results/.",
    "[7] World Bank. World Development Indicators[DB/OL]. Washington, DC: World Bank, 2024[2026-04-22]. https://databank.worldbank.org/source/world-development-indicators.",
    "[8] World Bank. Health Nutrition and Population Statistics[DB/OL]. Washington, DC: World Bank, 2024[2026-04-22]. https://databank.worldbank.org/source/health-nutrition-and-population-statistics.",
    "[9] 国家统计局. 中国统计年鉴[DB/OL]. 北京: 中国统计出版社, 2024[2026-04-22]. https://www.stats.gov.cn/sj/ndsj/.",
    "[10] Rawls J. A Theory of Justice[M]. Cambridge, MA: Harvard University Press, 1971.",
]


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


def block_text(element) -> str:
    return "".join(element.xpath(".//w:t/text()", namespaces=NS)).strip()


def make_page_break_paragraph():
    paragraph = etree.Element(f"{{{W_NS}}}p")
    run = etree.SubElement(paragraph, f"{{{W_NS}}}r")
    etree.SubElement(run, f"{{{W_NS}}}br", attrib={f"{{{W_NS}}}type": "page"})
    return paragraph


def clear_document_body(doc: Document) -> None:
    body = doc._body._element
    for child in list(body):
        body.remove(child)


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
    paragraph.paragraph_format.space_before = Pt(12 if level == 1 else 6)
    paragraph.paragraph_format.space_after = Pt(6)
    for run in paragraph.runs:
        if level == 1:
            set_run_font(run, 16, True)
        elif level == 2:
            set_run_font(run, 14, True)
        elif level == 3:
            set_run_font(run, 12, True)
        else:
            set_run_font(run, 11, True)


def add_heading(doc: Document, text: str, level: int) -> None:
    paragraph = doc.add_paragraph()
    paragraph.add_run(text)
    apply_manual_heading(paragraph, level)


def add_body_paragraph(doc: Document, text: str) -> None:
    paragraph = doc.add_paragraph(style="正文段落")
    paragraph.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    paragraph.add_run(text)


def build_front_doc() -> None:
    TMP_DIR.mkdir(parents=True, exist_ok=True)
    doc = Document(TEMPLATE_DOCX)
    clear_document_body(doc)

    for section_title, blocks in FRONT_STRUCTURE:
        add_heading(doc, section_title, 1)
        for subsection_title, paragraphs in blocks:
            add_heading(doc, subsection_title, 2)
            for paragraph in paragraphs:
                add_body_paragraph(doc, paragraph)

    doc.save(FRONT_DOCX)


def load_docx_bundle(path: Path) -> dict[str, bytes]:
    with zipfile.ZipFile(path) as src:
        return {name: src.read(name) for name in src.namelist()}


def extract_blocks(files: dict[str, bytes], start_text: str | None, end_text: str | None) -> list[etree._Element]:
    doc_root = etree.fromstring(files["word/document.xml"])
    body = doc_root.find(f"{{{W_NS}}}body")
    if body is None:
        raise RuntimeError(f"Unable to locate body in source document: {start_text}")

    blocks: list[etree._Element] = []
    capture = start_text is None
    for child in body:
        if child.tag == f"{{{W_NS}}}sectPr":
            continue
        text = block_text(child)
        if not capture and start_text and text == start_text:
            capture = True
        if capture and end_text and end_text in text:
            break
        if capture:
            blocks.append(copy.deepcopy(child))
    return blocks


def copy_blocks_with_relationships(
    source_files: dict[str, bytes],
    source_blocks: list[etree._Element],
    target_files: dict[str, bytes],
    target_relationship_root,
    existing_rids: set[str],
) -> list[etree._Element]:
    _, source_relationships = parse_relationships(source_files["word/_rels/document.xml.rels"])
    rel_id_map: dict[str, str] = {}
    copied_parts: dict[str, bytes] = {}
    copied_blocks: list[etree._Element] = []

    for block in source_blocks:
        new_block = copy.deepcopy(block)

        for node in new_block.xpath(".//*[@r:embed or @r:id or @r:link]", namespaces=NS):
            for rel_attr in (qn("r:embed"), qn("r:id"), qn("r:link")):
                source_rid = node.get(rel_attr)
                if not source_rid:
                    continue
                if source_rid in rel_id_map:
                    node.set(rel_attr, rel_id_map[source_rid])
                    continue

                rel = source_relationships.get(source_rid)
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
                if mode != "External":
                    source_path = f"word/{target}"
                    suffix = Path(target).suffix
                    if source_path in source_files:
                        part_name = f"word/media/{new_rid}{suffix}" if target.startswith("media/") else f"word/embeddings/{new_rid}{suffix}"
                        if target.startswith("charts/"):
                            part_name = f"word/charts/{new_rid}{suffix}"
                        copied_parts[part_name] = source_files[source_path]
                        rel_folder = Path(part_name).parent.name
                        new_rel.set("Target", f"{rel_folder}/{Path(part_name).name}")

                target_relationship_root.append(new_rel)

        copied_blocks.append(new_block)

    target_files.update(copied_parts)
    return copied_blocks


def merge_sources() -> None:
    template_files = load_docx_bundle(TEMPLATE_DOCX)
    template_doc = etree.fromstring(template_files["word/document.xml"])
    template_body = template_doc.find(f"{{{W_NS}}}body")
    if template_body is None:
        raise RuntimeError("Unable to locate template body.")

    template_blocks = [child for child in template_body if child.tag != f"{{{W_NS}}}sectPr"]
    cover_blocks = [copy.deepcopy(block) for block in template_blocks[:9]]
    sect_pr = template_body.find(f"{{{W_NS}}}sectPr")
    if sect_pr is None:
        raise RuntimeError("Unable to locate section settings in template.")

    for child in list(template_body):
        template_body.remove(child)

    target_relationship_root, _ = parse_relationships(template_files["word/_rels/document.xml.rels"])
    existing_rids = {
        rel.get("Id")
        for rel in target_relationship_root.xpath("./pr:Relationship", namespaces={"pr": PKG_REL_NS})
    }

    source_specs = [
        (FRONT_DOCX, None, None),
        (
            DOCX_DIR / "p1.docx",
            "4．描述全球疾病谱系的时空变迁，并量化健康指标的时空分布及其变化趋势",
            "参考文献",
        ),
        (
            DOCX_DIR / "p2.docx",
            "重点疾病负担的风险归因与演变预测",
            None,
        ),
        (
            DOCX_DIR / "p3.docx",
            "6 卫生资源配置的缺口识别、类型评估与优化调配",
            "参考文献",
        ),
    ]

    merged_blocks: list[etree._Element] = []
    for path, start_text, end_text in source_specs:
        source_files = load_docx_bundle(path)
        source_blocks = extract_blocks(source_files, start_text, end_text)
        merged_blocks.extend(
            copy_blocks_with_relationships(
                source_files=source_files,
                source_blocks=source_blocks,
                target_files=template_files,
                target_relationship_root=target_relationship_root,
                existing_rids=existing_rids,
            )
        )

    for block in cover_blocks:
        template_body.append(block)
    template_body.append(make_page_break_paragraph())
    for block in merged_blocks:
        template_body.append(block)
    template_body.append(copy.deepcopy(sect_pr))

    template_files["word/document.xml"] = etree.tostring(
        template_doc, encoding="UTF-8", xml_declaration=True
    )
    template_files["word/_rels/document.xml.rels"] = etree.tostring(
        target_relationship_root, encoding="UTF-8", xml_declaration=True
    )

    content_types = etree.fromstring(template_files["[Content_Types].xml"])
    existing_extensions = {
        node.get("Extension")
        for node in content_types.findall(f"{{{CT_NS}}}Default")
    }
    for ext, content_type in (
        ("png", "image/png"),
        ("jpg", "image/jpeg"),
        ("jpeg", "image/jpeg"),
        ("emf", "image/x-emf"),
        ("bin", "application/vnd.openxmlformats-officedocument.oleObject"),
        ("xml", "application/xml"),
    ):
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

    with zipfile.ZipFile(OUTPUT_DOCX, "w", compression=zipfile.ZIP_DEFLATED) as out_zip:
        for name, data in template_files.items():
            out_zip.writestr(name, data)


def delete_paragraph(paragraph) -> None:
    element = paragraph._element
    parent = element.getparent()
    if parent is not None:
        parent.remove(element)


def insert_paragraph_after(paragraph, text: str) -> Paragraph:
    new_p = OxmlElement("w:p")
    paragraph._p.addnext(new_p)
    new_para = Paragraph(new_p, paragraph._parent)
    new_para.add_run(text)
    return new_para


def normalize_chapter_refs(text: str, chapter: int) -> str:
    text = re.sub(rf"图(?!{chapter}-)(\d+)", rf"图{chapter}-\1", text)
    text = re.sub(rf"表(?!{chapter}-)(\d+)", rf"表{chapter}-\1", text)
    return text


def caption_number(text: str) -> str | None:
    match = FIG_ONLY_RE.match(text)
    if match:
        return match.group(1)
    return None


def is_caption_text(text: str) -> bool:
    match = re.match(r"^(图|表)\s*(\d+-\d+)\s*", text)
    if not match:
        return False
    rest = text[match.end():].strip()
    if not rest:
        return False
    if rest.startswith(("展示", "显示", "表明", "说明", "进一步", "不仅", "进一步说明")):
        return False
    return len(rest) <= 80


def apply_text_fixes(doc: Document) -> None:
    current_chapter = 0
    replacements = {
        "4．描述全球疾病谱系的时空变迁，并量化健康指标的时空分布及其变化趋势": "4 全球疾病谱系的时空演化与健康格局刻画",
        "4.1全球疾病谱系的时空分布，挖掘疾病谱系的时空变化特征": "4.1 全球疾病谱系的时空特征识别",
        "4.11 数据基础": "4.1.1 数据基础与指标说明",
        "4.1.2 指标构建": "4.1.2 流行病学转型指数构建",
        "4.1.3算法实现": "4.1.3 DiST时空聚类方法",
        "4.1.4时间维度特征挖掘结果": "4.1.4 国家类型划分与时间演化特征",
        "4.1.5 全球国家疾病谱系空间分布": "4.1.5 全球空间分布与区域差异",
        "4.2形成不同国家在关键健康指标上的分布，分析影响健康指标因素": "4.2 健康指标分布及其影响因素分析",
        "4.2.1 形成不同国家在关键健康指标上的分布": "4.2.1 关键健康指标的全球分布",
        "4.2.2指标空间异常性描述": "4.2.2 空间异常与国家分层",
        "4.2.3 分析影响健康指标的因素": "4.2.3 影响因素的维度构建",
        "4.2.4 回归分析": "4.2.4 回归模型构建与结果分析",
        "4.2.5回归分析结果总结": "4.2.5 结果总结与机制解释",
        "4.2.6影响因素深度分析": "4.2.6 影响机制的深入讨论",
        "4.3建立地区疾病谱系和健康指标的关联关系，对疾病谱系和健康指标的变化进行预测": "4.3 疾病谱系与健康指标的关联建模及趋势预测",
        "4.3.2 关联模型构建": "4.3.2 关联模型构建与特征重要性识别",
        "4.3.2 健康指标变化蒙特卡洛模拟预测": "4.3.3 蒙特卡洛模拟与不确定性预测",
        "4.3.3 2030-2050年健康指标预测": "4.3.4 2030—2050年健康指标趋势预测",
        "4.3.4 政策建议": "4.3.5 基于预测结果的政策启示",
        "4.4给出导致变化的解释，并提出优化健康指标的方法（从经济人文方向分析）": "4.4 变化解释与健康改善路径",
        "4.4.1 核心发现总结": "4.4.1 核心发现与综合解释",
        "4.4.2优化健康指标的方法": "4.4.2 经济与人文双维优化策略",
        "4.4.3实施路径与预期效果": "4.4.3 分阶段实施路径与预期效果",
        "4.4.4结论": "4.4.4 本章小结",
        "重点疾病负担的风险归因与演变预测": "5 重点疾病负担的风险归因、动态驱动与防控推演",
        "核心疾病的识别与静态风险归因分析": "5.1 核心疾病识别与静态风险归因",
        "基于动态关联模型的风险驱动机制识别": "5.2 风险驱动机制的动态识别",
        "灰色关联模型": "5.2.1 灰色关联模型构建",
        "模型应用与结果分析": "5.2.2 模型应用与结果分析",
        "多政策情景下的中长期疾病负担预测模拟": "5.3 多政策情景下的中长期疾病负担预测",
        "政策情景设计与模拟参数": "5.3.1 政策情景设计与模拟参数",
        "模拟框架与结果": "5.3.2 模拟框架与结果",
        "基线增长率计算": "5.3.2.1 基线增长率计算",
        "未来风险暴露水平": "5.3.2.2 未来风险暴露水平",
        "风险影响权重归一化": "5.3.2.3 风险影响权重归一化",
        "综合干预幅度与疾病负担": "5.3.2.4 综合干预幅度与疾病负担",
        "综合研判与递阶式防控策略构建": "5.4 风险分级与递阶式防控策略",
        "风险综合分级研判": "5.4.1 风险综合分级研判",
        "三阶段递阶式防控策略建议": "5.4.2 三阶段递阶式防控策略建议",
        "优先干预级：历史贡献大且动态驱动力强。是当前导致高负担并驱动其快速增长的首要矛盾。以中国为例：空气污染（对恶性肿瘤和慢性呼吸系统疾病）、血脂异常（对心血管疾病）属于此级。需立即采取高强度、决定性措施。": "5.4.1.1 优先干预级：历史贡献大且动态驱动力强。是当前导致高负担并驱动其快速增长的首要矛盾。以中国为例：空气污染（对恶性肿瘤和慢性呼吸系统疾病）、血脂异常（对心血管疾病）属于此级。需立即采取高强度、决定性措施。",
        "重点控制级：历史贡献巨大，但动态驱动力显示为中长期影响因素；或动态驱动力强，但历史贡献占比相对略低。是需要持续巩固和深化控制的关键领域。以中国为例：烟草使用（基石性风险，历史贡献巨大）、高血压（基础性代谢风险）属于此级。": "5.4.1.2 重点控制级：历史贡献巨大，但动态驱动力显示为中长期影响因素；或动态驱动力强，但历史贡献占比相对略低。是需要持续巩固和深化控制的关键领域。以中国为例：烟草使用（基石性风险，历史贡献巨大）、高血压（基础性代谢风险）属于此级。",
        "常规管理级：贡献度和驱动力相对稳定，需纳入常态化健康管理体系，防止反弹。以中国为例：不健康饮食、高血糖等属于此级。": "5.4.1.3 常规管理级：贡献度和驱动力相对稳定，需纳入常态化健康管理体系，防止反弹。以中国为例：不健康饮食、高血糖等属于此级。",
        "第一阶段：攻坚核心，快速响应（1-5年）。目标：集中优势资源，优先解决“优先干预级”风险，快速遏制疾病负担的急剧上升势头。": "5.4.2.1 第一阶段：攻坚核心，快速响应（1-5年）。目标：集中优势资源，优先解决“优先干预级”风险，快速遏制疾病负担的急剧上升势头。",
        "第二阶段：系统深化，巩固拓展（5-10年）。目标：在控制优先风险的基础上，系统建立对“重点控制级”风险的全面防控网络，形成稳定的疾病负担下降趋势。": "5.4.2.2 第二阶段：系统深化，巩固拓展（5-10年）。目标：在控制优先风险的基础上，系统建立对“重点控制级”风险的全面防控网络，形成稳定的疾病负担下降趋势。",
        "第三阶段：整合协同，长效治理（10年以上）。目标：建成整合型、智慧化的慢性病全域健康治理体系，实现健康服务从“以治病为中心”向“以人民健康为中心”的根本转变。": "5.4.2.3 第三阶段：整合协同，长效治理（10年以上）。目标：建成整合型、智慧化的慢性病全域健康治理体系，实现健康服务从“以治病为中心”向“以人民健康为中心”的根本转变。",
        "图 【心血管疾病】风险因素贡献占比": "图5-2 心血管疾病风险因素贡献占比",
        "图 【肿瘤】风险因素贡献占比": "图5-3 恶性肿瘤风险因素贡献占比",
        "图 【慢性呼吸系统疾病】风险因素贡献占比": "图5-4 慢性呼吸系统疾病风险因素贡献占比",
        "图1中国 2000–2023 年前5大死亡原因波动趋势图": "图5-1 中国2000—2023年前5大死亡原因波动趋势图",
        "2.1.2 健康表现指数（HPI）分析": "健康表现指数（HPI）分析",
        "2.2.2 相关性分析": "相关性分析",
        "总死亡人数计算": "总死亡人数计算公式如下：",
        "流行病学转型指数（ETI）": "流行病学转型指数（ETI）计算公式如下：",
        "DiST自适应时空聚类": "DiST自适应时空聚类方法",
    }

    for paragraph in doc.paragraphs:
        text = paragraph.text.strip()
        has_drawing = bool(paragraph._p.xpath('.//*[local-name()="drawing"]'))
        if not text:
            continue
        if text in replacements:
            if has_drawing:
                continue
            paragraph.text = replacements[text]
            text = paragraph.text.strip()

        if text.startswith("1 ") and "研究背景和意义" in text:
            current_chapter = 1
        elif text.startswith("2 ") and "研究目标和内容" in text:
            current_chapter = 2
        elif text.startswith("3 ") and "研究方法和技术路线" in text:
            current_chapter = 3
        elif text.startswith("4 "):
            current_chapter = 4
        elif text.startswith("5 "):
            current_chapter = 5
        elif text.startswith("6 "):
            current_chapter = 6

        if "数据路径：e:" in text:
            delete_paragraph(paragraph)
            continue
        if has_drawing:
            continue

        if text == "其中： - ：传染性疾病死亡人数 - ：非传染性疾病死亡人数 - ：伤害死亡人数":
            paragraph.text = "其中，传染性疾病死亡人数、非传染性疾病死亡人数和伤害死亡人数共同构成全死因死亡总量。"
        elif text == "其中： - ：特征距离（ETI、NCD_Rate、Comm_Rate等） - ：地理距离 - ：自适应权重参数":
            paragraph.text = "其中，距离度量由疾病谱系特征距离、地理距离和自适应权重共同构成，用于同时刻画样本在疾病结构和空间位置上的相似性。"
        elif text == "其中： - ：样本i与同簇其他样本的平均距离 - ：样本i与最近其他簇样本的平均距离":
            paragraph.text = "其中，轮廓系数通过比较样本与同簇样本、近邻异簇样本的平均距离，衡量聚类结果的紧密度与分离度。"
        elif text == "其中： - （ETI越低越好） - （NCD_Rate越低越好） - （预期寿命越高越好）":
            paragraph.text = "其中，ETI和NCD_Rate按逆向指标处理，预期寿命按正向指标处理，三者标准化后加权合成健康表现指数。"
        elif "通过Elbow Method分析（见[图10 fig10_elbow_method.png]）" in text:
            paragraph.text = "结合肘部法则与轮廓系数的综合判断，本文最终将全球国家划分为3类疾病谱系演化簇。"
        elif "上述演化路径详见[图12 fig12_evolution_paths.png]" in text:
            paragraph.text = "全球国家疾病谱系的典型演化路径如图4-2所示。"
        elif text == "如图xxx所示，心血管疾病呈现多风险共同驱动的复杂模式。其中，高血压是历史首要归因风险，贡献占比达27.71%；不健康饮食、空气污染、烟草使用的贡献占比分别为14.18%、12.44%和9.59%。其风险结构多元，涉及代谢、环境和行为等多个维度。":
            paragraph.text = "如图5-2所示，心血管疾病呈现多风险共同驱动的复杂模式。其中，高血压是历史首要归因风险，贡献占比达27.71%；不健康饮食、空气污染、烟草使用的贡献占比分别为14.18%、12.44%和9.59%。其风险结构多元，涉及代谢、环境和行为等多个维度。"
        elif text == "如图xxx所示，恶性肿瘤的风险结构高度集中。烟草使用是占据绝对主导地位的历史风险，其52.06%的归因贡献占比凸显了控烟在肿瘤一级预防中的核心地位；空气污染与饮食风险的贡献分别为11.03%和10.29%。烟草使用的柱形显著高于其他因素。":
            paragraph.text = "如图5-3所示，恶性肿瘤的风险结构高度集中。烟草使用是占据绝对主导地位的历史风险，其52.06%的归因贡献占比凸显了控烟在肿瘤一级预防中的核心地位；空气污染与饮食风险的贡献分别为11.03%和10.29%。烟草使用的柱形显著高于其他因素。"
        elif text == "如图xxx所示，慢性呼吸系统疾病的风险则极为聚焦。烟草使用和空气污染是两大核心驱动因素，贡献占比分别为45.35%和35.13%，二者合计超过80%。其风险谱简洁明了，指向性极强。":
            paragraph.text = "如图5-4所示，慢性呼吸系统疾病的风险则极为聚焦。烟草使用和空气污染是两大核心驱动因素，贡献占比分别为45.35%和35.13%，二者合计超过80%。其风险谱简洁明了，指向性极强。"
        elif text.startswith("空气污染治理政策展现出显著的广谱效益。"):
            paragraph.text = text.replace("如图所示，", "如图5-6所示，")
        elif text.startswith("慢性病综合管理政策对心血管疾病的效果极为突出"):
            paragraph.text = text.replace("如图所示，", "如图5-7所示，")

        if current_chapter in {4, 5}:
            paragraph.text = normalize_chapter_refs(paragraph.text, current_chapter)


def remove_duplicate_figure_captions(doc: Document) -> None:
    paragraphs = list(doc.paragraphs)
    to_delete = []
    for idx, paragraph in enumerate(paragraphs):
        has_drawing = bool(paragraph._p.xpath('.//*[local-name()="drawing"]'))
        if not has_drawing or idx == 0 or idx + 1 >= len(paragraphs):
            continue
        prev_text = paragraphs[idx - 1].text.strip()
        next_text = paragraphs[idx + 1].text.strip()
        prev_num = caption_number(prev_text)
        next_num = caption_number(next_text)
        if prev_num and next_num and prev_num == next_num:
            to_delete.append(paragraphs[idx - 1])

    for paragraph in reversed(to_delete):
        delete_paragraph(paragraph)


def insert_missing_captions(doc: Document) -> None:
    paragraphs = list(doc.paragraphs)
    for paragraph in reversed(paragraphs):
        text = paragraph.text.strip()
        has_drawing = bool(paragraph._p.xpath('.//*[local-name()="drawing"]'))
        if not has_drawing:
            continue
        next_text = ""
        next_idx = paragraphs.index(paragraph) + 1
        if next_idx < len(paragraphs):
            next_text = paragraphs[next_idx].text.strip()

        caption = None
        if text.startswith("基于此框架，对中国2024-2043年的疾病负担进行模拟预测"):
            caption = "图5-6 多政策情景下的疾病负担预测结果"
        elif next_text.startswith("慢性病综合管理政策对心血管疾病的效果极为突出"):
            caption = "图5-7 慢性病综合管理政策的模拟效果"
        elif next_text.startswith("控烟政策对慢性呼吸系统疾病效果最为显著"):
            caption = "图5-8 控烟政策的模拟效果"
        elif next_text.startswith("限酒与体重控制政策则主要对恶性肿瘤负担产生降低效果"):
            caption = "图5-9 限酒与体重控制政策的模拟效果"
        elif next_text.startswith("对于心血管疾病，高低密度脂蛋白胆固醇以0.7730的关联度位居首位"):
            caption = "图5-5 核心疾病风险驱动因素的动态关联结果"

        if caption:
            inserted = insert_paragraph_after(paragraph, caption)
            inserted.style = doc.styles["Caption"]
            inserted.alignment = WD_ALIGN_PARAGRAPH.CENTER
            inserted.paragraph_format.first_line_indent = None


def set_paragraph_styles(doc: Document) -> None:
    for paragraph in doc.paragraphs:
        text = paragraph.text.strip()
        has_drawing = bool(paragraph._p.xpath('.//*[local-name()="drawing"]'))
        has_math = bool(paragraph._p.xpath('.//*[local-name()="oMath" or local-name()="oMathPara"]'))

        if not text and has_drawing:
            paragraph.style = doc.styles["图表段落"]
            paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER
            paragraph.paragraph_format.first_line_indent = None
            continue

        if is_caption_text(text):
            paragraph.style = doc.styles["Caption"]
            paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER
            paragraph.paragraph_format.first_line_indent = None
            continue

        if text == "参考文献":
            apply_manual_heading(paragraph, 1)
            continue

        if H4_RE.match(text):
            apply_manual_heading(paragraph, 4)
            continue
        if H3_RE.match(text):
            apply_manual_heading(paragraph, 3)
            continue
        if H2_RE.match(text):
            apply_manual_heading(paragraph, 2)
            continue
        if H1_RE.match(text):
            apply_manual_heading(paragraph, 1)
            continue

        if has_math and not text:
            paragraph.style = doc.styles["正文段落"]
            paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER
            paragraph.paragraph_format.first_line_indent = None
            continue

        paragraph.style = doc.styles["正文段落"]
        if text.startswith("[") and "]" in text[:5]:
            paragraph.paragraph_format.first_line_indent = None

    for table in doc.tables:
        table.style = "Table Grid"
        table.alignment = WD_TABLE_ALIGNMENT.CENTER


def finalize_output() -> None:
    doc = Document(OUTPUT_DOCX)

    doc.paragraphs[5].text = "作品编号："
    doc.paragraphs[6].text = "作品名称：全球健康转型、重点疾病负担与卫生资源配置的综合分析"
    doc.paragraphs[8].text = "填写日期：2026年4月22日"

    apply_text_fixes(doc)
    remove_duplicate_figure_captions(doc)
    insert_missing_captions(doc)

    add_heading(doc, "参考文献", 1)
    for ref in REFERENCES:
        paragraph = doc.add_paragraph(style="正文段落")
        paragraph.paragraph_format.first_line_indent = None
        paragraph.add_run(ref)

    set_paragraph_styles(doc)
    doc.save(OUTPUT_DOCX)


def main() -> None:
    if not TEMPLATE_DOCX.exists():
        raise FileNotFoundError(TEMPLATE_DOCX)

    build_front_doc()
    merge_sources()
    finalize_output()


if __name__ == "__main__":
    main()
