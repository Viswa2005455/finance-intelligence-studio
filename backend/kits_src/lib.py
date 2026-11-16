"""Shared helpers for building the ready-made service kits (Excel, Word, PowerPoint, web templates).

Run `uv run --with python-pptx python kits_src/build.py` from backend/ to rebuild every kit ZIP
into app/payments/kits/. The ZIPs are committed; the web app only reads them.
"""

from __future__ import annotations

import io
import zipfile
from pathlib import Path

from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.shared import Pt, RGBColor
from openpyxl import Workbook
from openpyxl.chart import BarChart, LineChart, Reference
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import get_column_letter
from openpyxl.worksheet.datavalidation import DataValidation

GREEN = "0F3D2E"
TEAL = "0F8A6E"
SOFT = "E8F3EC"
INPUT = "FFF4CC"
GREY = "F3F1EA"
MONEY = '"₹"#,##0'
MONEY2 = '"₹"#,##0.00'
PCT = "0.0%"
LAST = 1004  # tables are formatted and summed down to this row
FIRST = 5

thin = Side(style="thin", color="D9D4C5")
BORDER = Border(left=thin, right=thin, top=thin, bottom=thin)


def col(n: int) -> str:
    return get_column_letter(n)


def new_wb() -> Workbook:
    wb = Workbook()
    wb.remove(wb.active)
    return wb


def head(ws, row: int, labels: list[str], start: int = 1) -> None:
    for i, label in enumerate(labels):
        c = ws.cell(row=row, column=start + i, value=label)
        c.font = Font(bold=True, color="FFFFFF")
        c.fill = PatternFill("solid", fgColor=GREEN)
        c.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
        c.border = BORDER
    ws.row_dimensions[row].height = 30


def title(ws, text: str, sub: str = "") -> None:
    """A dark-green banner across the top of every sheet with the sheet title and a one-line hint."""
    for r in (1, 2):
        for c in range(1, 22):
            ws.cell(row=r, column=c).fill = PatternFill("solid", fgColor=GREEN)
    ws["A1"] = text
    ws["A1"].font = Font(size=18, bold=True, color="FFFFFF")
    ws.row_dimensions[1].height = 32
    if sub:
        ws["A2"] = sub
        ws["A2"].font = Font(italic=True, color="BFE0D2")
    ws.row_dimensions[2].height = 20


def widths(ws, values: list[float], start: int = 1) -> None:
    for i, w in enumerate(values):
        ws.column_dimensions[col(start + i)].width = w


def inp(cell, fmt: str | None = None) -> None:
    """Marks a cell as one the customer fills in (pale yellow)."""
    cell.fill = PatternFill("solid", fgColor=INPUT)
    cell.border = BORDER
    if fmt:
        cell.number_format = fmt


def calc(cell, fmt: str | None = None, bold: bool = False) -> None:
    cell.fill = PatternFill("solid", fgColor=SOFT)
    cell.border = BORDER
    if bold:
        cell.font = Font(bold=True)
    if fmt:
        cell.number_format = fmt


def start_sheet(wb: Workbook, name: str, heading: str, steps: list[str], note: str = "") -> None:
    """The first sheet of every workbook: a designed how-to-use page with numbered steps and a colour guide."""
    ws = wb.create_sheet(name, 0)
    ws.sheet_view.showGridLines = False
    title(ws, heading, "Ready-made template. Yellow cells are for you to fill in; green cells calculate by themselves.")
    ws.column_dimensions["A"].width = 7
    ws.column_dimensions["B"].width = 104
    h = ws.cell(row=4, column=2, value="How to use this template")
    h.font = Font(bold=True, size=15, color=GREEN)
    ws.row_dimensions[4].height = 30
    for i, text in enumerate(steps, start=1):
        r = 5 + i
        n = ws.cell(row=r, column=1, value=i)
        n.fill = PatternFill("solid", fgColor=TEAL)
        n.font = Font(bold=True, size=13, color="FFFFFF")
        n.alignment = Alignment(horizontal="center", vertical="center")
        t = ws.cell(row=r, column=2, value=text)
        t.font = Font(size=12)
        t.alignment = Alignment(wrap_text=True, vertical="center", indent=1)
        t.fill = PatternFill("solid", fgColor=GREY)
        ws.row_dimensions[r].height = 38 if len(text) > 95 else 30
    r = 7 + len(steps)
    ws.cell(row=r, column=2, value="Colour guide").font = Font(bold=True, size=13, color=GREEN)
    ya = ws.cell(row=r + 1, column=1)
    inp(ya)
    ws.cell(row=r + 1, column=2, value="Yellow cells: type your own data here").alignment = Alignment(indent=1, vertical="center")
    ga = ws.cell(row=r + 2, column=1)
    calc(ga)
    ws.cell(row=r + 2, column=2, value="Green cells: calculated automatically, please do not type over them").alignment = Alignment(indent=1, vertical="center")
    if note:
        nn = ws.cell(row=r + 4, column=2, value=note)
        nn.alignment = Alignment(wrap_text=True, vertical="top", indent=1)
        nn.font = Font(italic=True, color="5B6770")
        ws.row_dimensions[r + 4].height = 48
    f = ws.cell(row=r + 6, column=2, value="Finance Intelligence Studio  ·  Ready-made kits by Viswa Kumar  ·  fabulousviswa2005@gmail.com")
    f.font = Font(size=10, color="5B6770")


def dropdown(ws, rng: str, options: list[str]) -> None:
    dv = DataValidation(type="list", formula1='"' + ",".join(options) + '"', allow_blank=True)
    dv.error = "Please pick a value from the list."
    dv.errorTitle = "Not in list"
    ws.add_data_validation(dv)
    dv.add(rng)


def bar(ws, anchor: str, title_: str, cats: Reference, vals: Reference, w: float = 16, h: float = 8, line: bool = False) -> None:
    ch = LineChart() if line else BarChart()
    ch.title = title_
    ch.add_data(vals, titles_from_data=True)
    ch.set_categories(cats)
    ch.width, ch.height = w, h
    # openpyxl hides axes by default in current Excel; show them, and keep lines straight with one colour.
    ch.x_axis.delete = False
    ch.y_axis.delete = False
    ch.varyColors = False
    if line:
        for srs in ch.series:
            srs.smooth = False
    if len(ch.series) == 1:
        ch.legend = None
    ws.add_chart(ch, anchor)


def pack(files: dict[str, bytes], out: Path, folder: str) -> None:
    out.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as z:
        for name, data in files.items():
            z.writestr(f"{folder}/{name}", data)


PALETTE = ["0F8A6E", "F5C451", "14564A", "D9480F", "4F46E5"]


def _style_chart(ch) -> None:
    """Brand colours, light gridlines and no heavy borders, so charts look designed rather than default."""
    from openpyxl.chart.shapes import GraphicalProperties
    from openpyxl.drawing.line import LineProperties
    for i, srs in enumerate(ch.series):
        colour = PALETTE[i % len(PALETTE)]
        srs.graphicalProperties = GraphicalProperties(solidFill=colour)
        srs.graphicalProperties.line = LineProperties(solidFill=colour, w=28575)
    try:
        ch.y_axis.majorGridlines.spPr = GraphicalProperties(ln=LineProperties(solidFill="E5E0D2", w=6350))
    except AttributeError:
        pass
    ch.graphical_properties = GraphicalProperties(ln=LineProperties(noFill=True))


def _is_input_fill(cell) -> bool:
    f = cell.fill
    return f is not None and f.fill_type == "solid" and str(f.fgColor.rgb or "").endswith(INPUT)


def make_blank(wb: Workbook) -> None:
    """Empties the sample entries of big input sheets (more than 40 yellow cells), keeping formulas, dropdowns,
    formatting and the settings in the first four rows. Small settings sheets keep their example values."""
    for ws in wb.worksheets:
        yellow = [c for row in ws.iter_rows(min_row=FIRST) for c in row if _is_input_fill(c)]
        if len(yellow) <= 40:
            continue
        for c in yellow:
            if c.value is not None and not (isinstance(c.value, str) and c.value.startswith("=")):
                c.value = None


def wb_bytes(wb: Workbook, blank: bool = False) -> bytes:
    from openpyxl.chart import LineChart
    if blank:
        make_blank(wb)
    for ws in wb.worksheets:  # tab colours: gold for the start sheet, teal for the rest
        ws.sheet_properties.tabColor = "F5C451" if ws.title == "Start here" else TEAL
    for ws in wb.worksheets:  # charts whose series were replaced after bar(): apply the same display fixes
        for ch in ws._charts:
            ch.x_axis.delete = False
            ch.y_axis.delete = False
            ch.varyColors = False
            for srs in ch.series:
                if isinstance(ch, LineChart):
                    srs.smooth = False
            if len(ch.series) == 1:
                ch.legend = None
            _style_chart(ch)
        ws.page_setup.orientation = "landscape"
        ws.page_setup.fitToWidth = 1
        ws.page_setup.fitToHeight = 0
        ws.sheet_properties.pageSetUpPr.fitToPage = True
    buf = io.BytesIO()
    wb.save(buf)
    return buf.getvalue()


# ----------------------------------------------------------------------------- Word helpers
def _shade(cell, hex_: str) -> None:
    from docx.oxml import OxmlElement
    from docx.oxml.ns import qn
    tcPr = cell._tc.get_or_add_tcPr()
    shd = OxmlElement("w:shd")
    shd.set(qn("w:val"), "clear")
    shd.set(qn("w:color"), "auto")
    shd.set(qn("w:fill"), hex_)
    tcPr.append(shd)


def _page_field(paragraph) -> None:
    from docx.oxml import OxmlElement
    from docx.oxml.ns import qn
    run = paragraph.add_run()
    for kind, text in (("begin", None), (None, "PAGE"), ("end", None)):
        if kind:
            el = OxmlElement("w:fldChar")
            el.set(qn("w:fldCharType"), kind)
        else:
            el = OxmlElement("w:instrText")
            el.set(qn("xml:space"), "preserve")
            el.text = text
        run._r.append(el)


def new_doc(heading: str, sub: str = "", banner: bool = True, footer: bool = True) -> Document:
    """A branded Word document: green title banner, consistent heading styles, footer with page numbers."""
    from docx.shared import Cm
    d = Document()
    sec = d.sections[0]
    sec.left_margin = sec.right_margin = Cm(2.2)
    sec.top_margin, sec.bottom_margin = Cm(2.0), Cm(2.0)
    normal = d.styles["Normal"]
    normal.font.name = "Calibri"
    normal.font.size = Pt(11)
    normal.paragraph_format.space_after = Pt(6)
    normal.paragraph_format.line_spacing = 1.15
    for name, size, before in (("Heading 1", 16, 16), ("Heading 2", 13, 10)):
        st = d.styles[name]
        st.font.name = "Calibri"
        st.font.size = Pt(size)
        st.font.bold = True
        st.font.color.rgb = RGBColor(0x0F, 0x3D, 0x2E)
        st.paragraph_format.space_before = Pt(before)
        st.paragraph_format.space_after = Pt(4)
        st.paragraph_format.keep_with_next = True
    if banner:
        t = d.add_table(rows=1, cols=1)
        cell = t.rows[0].cells[0]
        _shade(cell, GREEN)
        p = cell.paragraphs[0]
        p.paragraph_format.space_before = Pt(10)
        r = p.add_run(heading)
        r.font.size, r.font.bold, r.font.color.rgb = Pt(24), True, RGBColor(255, 255, 255)
        if sub:
            p2 = cell.add_paragraph()
            r2 = p2.add_run(sub)
            r2.font.size, r2.font.italic, r2.font.color.rgb = Pt(11), True, RGBColor(0xBF, 0xE0, 0xD2)
            p2.paragraph_format.space_after = Pt(10)
        d.add_paragraph()
    else:
        h = d.add_paragraph()
        hr = h.add_run(heading)
        hr.font.size, hr.font.bold, hr.font.color.rgb = Pt(26), True, RGBColor(0x0F, 0x3D, 0x2E)
        if sub:
            sp = d.add_paragraph(sub)
            sp.runs[0].font.color.rgb = RGBColor(0x5B, 0x67, 0x70)
    if footer:
        fp = sec.footer.paragraphs[0]
        fr = fp.add_run("Finance Intelligence Studio · ready-made kit      Page ")
        fr.font.size, fr.font.color.rgb = Pt(9), RGBColor(0x5B, 0x67, 0x70)
        _page_field(fp)
    return d


def doc_bytes(d: Document) -> bytes:
    buf = io.BytesIO()
    d.save(buf)
    return buf.getvalue()


def bullets(d: Document, items: list[str], style: str = "List Bullet") -> None:
    for it in items:
        d.add_paragraph(it, style=style)


def table(d: Document, header: list[str], rows: list[list[str]]) -> None:
    t = d.add_table(rows=1, cols=len(header))
    t.style = "Table Grid"
    for i, h in enumerate(header):
        c = t.rows[0].cells[i]
        c.text = ""
        run = c.paragraphs[0].add_run(h)
        run.font.bold, run.font.color.rgb = True, RGBColor(255, 255, 255)
        _shade(c, GREEN)
    for n, r in enumerate(rows):
        cells = t.add_row().cells
        for i, v in enumerate(r):
            cells[i].text = v
            if n % 2 == 1:
                _shade(cells[i], "F3F1EA")
    d.add_paragraph()


def howto(heading: str, promise: str, inside: list[str], steps: list[str], tips: list[str], extra_note: str = "") -> bytes:
    """The one-page '00 How to use' guide that goes in every kit."""
    d = new_doc(heading, promise)
    d.add_heading("What is in this kit", level=1)
    bullets(d, inside)
    d.add_heading("How to use it (10 minutes)", level=1)
    bullets(d, steps, "List Number")
    d.add_heading("Tips", level=1)
    bullets(d, tips)
    d.add_heading("Need it customised for you?", level=1)
    d.add_paragraph(
        "This kit is a ready-made template you can use today. If you want it built around your own data, "
        "logo and requirements, reply to the order email, or order the Standard or Premium package on the "
        "service page: https://finance-intelligence-studio.onrender.com/services")
    if extra_note:
        p = d.add_paragraph(extra_note)
        p.runs[0].italic = True
    d.add_paragraph("Finance Intelligence Studio, by Viswa Kumar. fabulousviswa2005@gmail.com").alignment = WD_ALIGN_PARAGRAPH.LEFT
    return doc_bytes(d)
