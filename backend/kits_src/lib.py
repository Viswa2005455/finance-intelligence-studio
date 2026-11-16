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
    ws["A1"] = text
    ws["A1"].font = Font(size=16, bold=True, color=GREEN)
    if sub:
        ws["A2"] = sub
        ws["A2"].font = Font(italic=True, color="5B6770")


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
    ws = wb.create_sheet(name, 0)
    ws.sheet_view.showGridLines = False
    title(ws, heading, "Ready-made template. Yellow cells are for you to fill in; green cells calculate by themselves.")
    ws["A4"] = "How to use"
    ws["A4"].font = Font(bold=True, size=12, color=TEAL)
    for i, s in enumerate(steps, start=1):
        ws.cell(row=4 + i, column=1, value=f"{i}. {s}").alignment = Alignment(wrap_text=True, vertical="top")
    r = 6 + len(steps)
    ws.cell(row=r, column=1, value="Colour guide").font = Font(bold=True, size=12, color=TEAL)
    a = ws.cell(row=r + 1, column=1, value="Yellow = type here")
    inp(a)
    b = ws.cell(row=r + 2, column=1, value="Green = calculated, do not type over")
    calc(b)
    if note:
        ws.cell(row=r + 4, column=1, value=note).alignment = Alignment(wrap_text=True, vertical="top")
        ws.row_dimensions[r + 4].height = 60
    ws.column_dimensions["A"].width = 100


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


def wb_bytes(wb: Workbook) -> bytes:
    from openpyxl.chart import LineChart
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
    buf = io.BytesIO()
    wb.save(buf)
    return buf.getvalue()


# ----------------------------------------------------------------------------- Word helpers
def new_doc(heading: str, sub: str = "") -> Document:
    d = Document()
    st = d.styles["Normal"]
    st.font.name = "Calibri"
    st.font.size = Pt(11)
    h = d.add_heading(heading, level=0)
    for r in h.runs:
        r.font.color.rgb = RGBColor(0x0F, 0x3D, 0x2E)
    if sub:
        p = d.add_paragraph(sub)
        p.runs[0].italic = True
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
    t.style = "Light Grid Accent 1"
    for i, h in enumerate(header):
        t.rows[0].cells[i].text = h
    for r in rows:
        cells = t.add_row().cells
        for i, v in enumerate(r):
            cells[i].text = v
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
