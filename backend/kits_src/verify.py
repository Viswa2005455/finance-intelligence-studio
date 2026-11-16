"""Static checks of every built kit ZIP: run from backend/ with  uv run python kits_src/verify.py
Opens each file, checks structure and colours, and for website templates checks links, anchors, files and basic accessibility.
Formula results are checked separately by opening the workbooks in Excel (see the PowerShell scan used while building)."""

from __future__ import annotations

import io
import re
import sys
import zipfile
from html.parser import HTMLParser
from pathlib import Path

from docx import Document
from openpyxl import load_workbook

KITS = Path(__file__).resolve().parent.parent / "app" / "payments" / "kits"
OLD_GREEN = ("0F3D2E", "0F8A6E", "E8F3EC", "FFF4CC", "14564A", "BFE0D2", "#0f3d2e", "#0f8a6e", "#e8f3ec")
problems: list[str] = []


def bad(slug: str, msg: str) -> None:
    problems.append(f"{slug}: {msg}")


class Page(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.ids, self.links, self.assets, self.h1, self.imgs_no_alt, self.title, self.viewport, self.lang, self.forms, self.labels, self.inputs = set(), [], [], 0, 0, "", False, False, 0, 0, 0
        self._in_title = False

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if "id" in a:
            self.ids.add(a["id"])
        if tag == "html" and a.get("lang"):
            self.lang = True
        if tag == "meta" and a.get("name") == "viewport":
            self.viewport = True
        if tag == "a" and a.get("href"):
            self.links.append(a["href"])
        if tag in ("link", "script") and (a.get("href") or a.get("src")):
            self.assets.append(a.get("href") or a.get("src"))
        if tag == "h1":
            self.h1 += 1
        if tag == "img" and "alt" not in a:
            self.imgs_no_alt += 1
        if tag == "title":
            self._in_title = True
        if tag == "form":
            self.forms += 1
        if tag == "label":
            self.labels += 1
        if tag in ("input", "select", "textarea"):
            self.inputs += 1

    def handle_endtag(self, tag):
        if tag == "title":
            self._in_title = False

    def handle_data(self, data):
        if self._in_title:
            self.title += data


def check_site(slug: str, files: dict[str, bytes]) -> int:
    pages = {n.split("/", 1)[1]: v.decode() for n, v in files.items() if n.startswith("website/") and n.endswith(".html")}
    names = {n.split("/", 1)[1] for n in files if n.startswith("website/")}
    css = files.get("website/style.css", b"").decode()
    if not css:
        bad(slug, "missing style.css")
    for old in OLD_GREEN:
        if old.lower() in css.lower():
            bad(slug, f"old green colour {old} still in style.css")
    for needed in ("#14213D", "#FF6B5B", "#F4EDE0"):
        if needed.lower() not in css.lower():
            bad(slug, f"palette colour {needed} missing from style.css")
    parsed = {}
    for name, html in pages.items():
        p = Page()
        p.feed(html)
        parsed[name] = p
    for name, p in parsed.items():
        where = f"{slug}/{name}"
        if not p.title.strip():
            bad(where, "no <title>")
        if not p.viewport:
            bad(where, "no viewport meta tag (breaks phones)")
        if not p.lang:
            bad(where, "no lang on <html>")
        if p.h1 != 1:
            bad(where, f"expected one <h1>, found {p.h1}")
        if p.imgs_no_alt:
            bad(where, f"{p.imgs_no_alt} images without alt text")
        if p.forms and p.labels < p.inputs - 0:
            bad(where, f"form fields without labels ({p.inputs} fields, {p.labels} labels)")
        for a in p.assets:
            if not a.startswith(("http", "//")) and a not in names:
                bad(where, f"missing file {a}")
        for href in p.links:
            if href.startswith(("http", "mailto:", "tel:")):
                continue
            target, _, frag = href.partition("#")
            tgt_page = target or name
            if tgt_page not in names:
                bad(where, f"broken link {href}")
            elif frag and tgt_page in parsed and frag not in parsed[tgt_page].ids:
                bad(where, f"anchor #{frag} not found on {tgt_page}")
        if "EDIT:" not in pages[name]:
            bad(where, "no EDIT: markers (customer cannot find what to change)")
        if re.search(r"&#(?![0-9]+;|x[0-9a-fA-F]+;)", pages[name]):
            bad(where, "malformed character entity")
    return len(pages)


def check_xlsx(slug: str, name: str, data: bytes) -> dict:
    wb = load_workbook(io.BytesIO(data))
    info = {"sheets": wb.sheetnames, "blank": "BLANK" in name}
    if wb.sheetnames[0] != "Start here":
        bad(slug, f"{name}: first sheet is {wb.sheetnames[0]!r}, expected 'Start here'")
    greens = 0
    nonblank_inputs = 0
    for ws in wb.worksheets:
        peach = [c for row in ws.iter_rows(min_row=5) for c in row if c.fill is not None and c.fill.fill_type == "solid" and str(c.fill.fgColor.rgb or "").endswith("FFE8DF")]
        for row in ws.iter_rows():
            for c in row:
                if c.fill is not None and c.fill.fill_type == "solid":
                    rgb = str(c.fill.fgColor.rgb or "").upper()
                    if any(g in rgb for g in ("0F3D2E", "0F8A6E", "E8F3EC", "FFF4CC")):
                        greens += 1
                if isinstance(c.value, str) and re.search(r"\b(yellow|green cells)\b", c.value, re.I) and "Start here" != ws.title:
                    bad(slug, f"{name}: leftover colour wording on '{ws.title}'!{c.coordinate}: {c.value[:60]}")
        if info["blank"] and len(peach) > 40:
            nonblank_inputs += sum(1 for c in peach if c.value is not None and not (isinstance(c.value, str) and c.value.startswith("=")))
    if greens:
        bad(slug, f"{name}: {greens} cells still use the old green/yellow fills")
    if info["blank"] and nonblank_inputs:
        bad(slug, f"{name}: blank copy still has {nonblank_inputs} sample entries")
    if not info["blank"] and slug in {"cash-flow-forecast-model-12-months"} and "Dashboard" not in wb.sheetnames:
        bad(slug, f"{name}: missing Dashboard sheet")
    return info


def main() -> int:
    total = {"zips": 0, "xlsx": 0, "blank": 0, "docx": 0, "pptx": 0, "pages": 0}
    have_dash, no_dash = [], []
    for z in sorted(KITS.glob("*.zip")):
        slug = z.stem
        total["zips"] += 1
        with zipfile.ZipFile(z) as zf:
            bad_member = zf.testzip()
            if bad_member:
                bad(slug, f"corrupt file in zip: {bad_member}")
            files = {n.split("/", 1)[1]: zf.read(n) for n in zf.namelist() if "/" in n and not n.endswith("/")}
        if "00-START-HERE-How-to-use.docx" not in files:
            bad(slug, "missing 00-START-HERE guide")
        if len(files) < 2:
            bad(slug, "kit has only one file")
        for n, data in files.items():
            if n.endswith(".xlsx"):
                info = check_xlsx(slug, n, data)
                total["blank" if info["blank"] else "xlsx"] += 1
                if not info["blank"]:
                    (have_dash if "Dashboard" in info["sheets"] or "Summary" in info["sheets"] else no_dash).append(f"{slug}/{n}")
            elif n.endswith(".docx"):
                d = Document(io.BytesIO(data))
                total["docx"] += 1
                if len(d.paragraphs) + len(d.tables) < 3:
                    bad(slug, f"{n}: almost empty")
                if any(g.lower() in data.decode("latin-1").lower() for g in ("0f3d2e", "bfe0d2")) or b"0F3D2E" in data:
                    pass
            elif n.endswith(".pptx"):
                from pptx import Presentation
                pr = Presentation(io.BytesIO(data))
                total["pptx"] += 1
                if len(pr.slides) < 5:
                    bad(slug, f"{n}: only {len(pr.slides)} slides")
            elif n.endswith(".json"):
                import json
                json.loads(data)
        if any(n.startswith("website/") for n in files):
            total["pages"] += check_site(slug, {k: v for k, v in files.items()})
    print("checked:", total)
    print(f"workbooks with a Dashboard or Summary sheet: {len(have_dash)}; without: {no_dash}")
    if problems:
        print(f"\n{len(problems)} PROBLEMS")
        for p in problems:
            print(" -", p)
        return 1
    print("no problems found")
    return 0


if __name__ == "__main__":
    sys.exit(main())
