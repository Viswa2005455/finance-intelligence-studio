"""Makes frontend/public/previews/<slug>.jpg: a picture of what is inside each kit, for the service pages.

Run from backend/ (Windows with Microsoft Office and Chrome installed):
    uv run python kits_src/previews.py            # fills in any missing pictures (resumable)
    uv run python kits_src/previews.py --fresh    # starts again from scratch
Needs the kit ZIPs already built (build.py). Raw pictures are cached in the temp folder so a stopped run can be resumed.
"""

from __future__ import annotations

import json
import shutil
import subprocess
import sys
import tempfile
import zipfile
from pathlib import Path

from PIL import Image, ImageChops, ImageDraw, ImageFilter, ImageFont

HERE = Path(__file__).resolve().parent
KITS = HERE.parent / "app" / "payments" / "kits"
OUT = HERE.parent.parent / "frontend" / "public" / "previews"
CACHE = Path(tempfile.gettempdir()) / "kitprev_raw"
W, MIN_H, MAX_H = 1000, 520, 1000
BATCH = 6
CHROME = next((p for p in (r"C:\Program Files\Google\Chrome\Application\chrome.exe", r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe") if Path(p).exists()), None)
DOC_PICK = {"google-business-profile-setup": "Google-Business-Profile-Kit.docx", "linkedin-profile-optimisation": "LinkedIn-Profile-Kit.docx", "resume-cv-for-finance-roles": "Resume-Template.docx",
            "n8n-make-workflow-setup-simple": "n8n-Make-Workflow-Guide.docx", "website-redesign-refresh": "Redesign-Checklist.docx", "mobile-responsiveness-fix": "Mobile-Test-Checklist.docx"}


def fit(img: Image.Image) -> Image.Image:
    """Trim blank margins, scale to the card width, and keep a sensible height (white padding if short)."""
    img = img.convert("RGB")
    bbox = ImageChops.difference(img, Image.new("RGB", img.size, (255, 255, 255))).getbbox()
    if bbox:
        pad = 14
        img = img.crop((max(0, bbox[0] - pad), max(0, bbox[1] - pad), min(img.width, bbox[2] + pad), min(img.height, bbox[3] + pad)))
    img = img.resize((W, max(1, round(img.height * W / img.width))), Image.LANCZOS)
    if img.height > MAX_H:
        img = img.crop((0, 0, W, MAX_H))
    if img.height < MIN_H:
        canvas = Image.new("RGB", (W, MIN_H), "white")
        canvas.paste(img, (0, 0))
        img = canvas
    return img


def cover(title: str) -> Image.Image:
    """Fallback picture when a real screenshot is not possible: a designed cover card in the site's palette."""
    h = 625
    base = Image.new("RGB", (W, h), "#14213D")
    glow = Image.new("RGB", (W, h), "#14213D")
    ImageDraw.Draw(glow).ellipse((520, 180, 1180, 780), fill="#FF6B5B")
    img = Image.blend(base, glow.filter(ImageFilter.GaussianBlur(140)), 0.55)
    d = ImageDraw.Draw(img)
    try:
        font, small = ImageFont.truetype("arialbd.ttf", 58), ImageFont.truetype("arial.ttf", 28)
    except OSError:
        font = small = ImageFont.load_default()
    lines, cur = [], ""
    for w in title.split():
        t = (cur + " " + w).strip()
        if d.textlength(t, font=font) > W - 140:
            lines.append(cur)
            cur = w
        else:
            cur = t
    lines.append(cur)
    y = 190 - 30 * (len(lines) - 1)
    for ln in lines[:4]:
        d.text((70, y), ln, fill="#F4EDE0", font=font)
        y += 74
    d.rounded_rectangle((70, 500, 470, 556), radius=28, fill="#FF6B5B")
    d.text((98, 511), "Instant download", fill="#14213D", font=small)
    return img


def doc_page(path: Path) -> Image.Image:
    """A page preview of a Word document, drawn from its real title, headings and text (no Word needed)."""
    from docx import Document
    d = Document(str(path))
    img = Image.new("RGB", (W, 760), "white")
    dr = ImageDraw.Draw(img)
    try:
        f_title, f_sub, f_h, f_t = (ImageFont.truetype("arialbd.ttf", 40), ImageFont.truetype("ariali.ttf", 22),
                                    ImageFont.truetype("arialbd.ttf", 28), ImageFont.truetype("arial.ttf", 21))
    except OSError:
        f_title = f_sub = f_h = f_t = ImageFont.load_default()
    title, sub = "", ""
    if d.tables and d.tables[0].rows and len(d.tables[0].rows[0].cells) == 1:
        paras = d.tables[0].rows[0].cells[0].paragraphs
        title = paras[0].text if paras else ""
        sub = paras[1].text if len(paras) > 1 else ""
    body = [p for p in d.paragraphs if p.text.strip()]
    if not title and body:
        title, body = body[0].text, body[1:]
        if body and not body[0].style.name.startswith("Heading"):
            sub, body = body[0].text, body[1:]
    dr.rectangle((0, 0, W, 150), fill="#0F3D2E")
    dr.text((50, 36), title[:44], fill="white", font=f_title)
    dr.text((50, 100), sub[:80], fill="#BFE0D2", font=f_sub)
    y = 190
    for p in body:
        if y > 700:
            break
        if p.style.name.startswith("Heading"):
            y += 8
            dr.text((50, y), p.text[:60], fill="#0F3D2E", font=f_h)
            y += 44
        else:
            bullet = "•  " if "List" in p.style.name else ""
            dr.text((60, y), (bullet + p.text)[:78], fill="#3C4760", font=f_t)
            y += 32
    dr.rectangle((0, 0, W - 1, 759), outline="#D9D4C5")
    return img


def main() -> None:
    if "--fresh" in sys.argv:
        shutil.rmtree(CACHE, ignore_errors=True)
    CACHE.mkdir(exist_ok=True)
    catalog = json.loads((HERE.parent / "app" / "payments" / "service_catalog.json").read_text(encoding="utf-8"))
    OUT.mkdir(parents=True, exist_ok=True)
    work = Path(tempfile.mkdtemp(prefix="kitprev_"))
    spec, web_jobs = [], []
    for slug in catalog:
        d = work / slug
        with zipfile.ZipFile(KITS / f"{slug}.zip") as z:
            z.extractall(d)
        files = [p for p in d.rglob("*") if p.is_file()]
        site = next((p for p in files if p.name == "index.html" and "website" in p.parts), None)
        pptx = next((p for p in files if p.suffix == ".pptx"), None)
        xlsx = next((p for p in sorted(files) if p.suffix == ".xlsx" and "BLANK" not in p.name), None)
        docx = next((p for p in files if p.name == DOC_PICK.get(slug)), None)
        have = (CACHE / f"{slug}.png").exists()
        if site:
            web_jobs.append((slug, site))
        elif have:
            continue
        elif pptx:
            spec.append({"slug": slug, "kind": "pptx", "file": str(pptx), "slide": 5 if "pitch" in slug else 4})
        elif xlsx:
            spec.append({"slug": slug, "kind": "xlsx", "file": str(xlsx)})
        elif docx:
            doc_page(docx).save(CACHE / f"{slug}.png")
    print(f"{len(spec)} Office pictures to take, {len(web_jobs)} websites")
    for i in range(0, len(spec), BATCH):
        chunk = spec[i:i + BATCH]
        sp = work / f"spec{i}.json"
        sp.write_text(json.dumps(chunk), encoding="utf-8")
        try:
            r = subprocess.run(["powershell", "-STA", "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", str(HERE / "previews.ps1"), "-SpecPath", str(sp), "-OutDir", str(CACHE)],
                               capture_output=True, text=True, timeout=240)
            msgs = [ln for ln in r.stdout.splitlines() if ln.startswith(("FAIL", "NOIMG"))]
            print(f"batch {i // BATCH + 1}: {len(chunk)} items", *msgs)
        except subprocess.TimeoutExpired:
            print(f"batch {i // BATCH + 1}: timed out, will be retried on the next run")
    for slug, site in web_jobs:
        png = CACHE / f"{slug}.png"
        if CHROME:
            subprocess.run([CHROME, "--headless=new", "--disable-gpu", "--window-size=1280,860", f"--screenshot={png}", site.as_uri()], capture_output=True, timeout=120)
    made, fallback = 0, []
    for slug, svc in catalog.items():
        png = CACHE / f"{slug}.png"
        if png.exists() and png.stat().st_size > 5000:
            fit(Image.open(png)).save(OUT / f"{slug}.jpg", "JPEG", quality=82, optimize=True)
            made += 1
        else:
            cover(svc["title"]).save(OUT / f"{slug}.jpg", "JPEG", quality=82)
            fallback.append(slug)
    shutil.rmtree(work, ignore_errors=True)
    print(f"{made} real previews, {len(fallback)} cover fallbacks: {fallback}")


if __name__ == "__main__":
    main()
