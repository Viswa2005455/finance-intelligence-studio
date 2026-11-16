"""Makes 10 designed 1080x1350 LinkedIn slides from the kit previews: uv run python kits_src/social_slides.py"""
import json
import math
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont

ROOT = Path(__file__).resolve().parent.parent.parent
PREV = ROOT / "frontend" / "public" / "previews"
OUT = ROOT / "linkedin-post-images"
CAT = json.loads((ROOT / "backend" / "app" / "payments" / "service_catalog.json").read_text(encoding="utf-8"))
NAVY, CREAM, CORAL, GOLD = (20, 33, 61), (244, 237, 224), (255, 107, 91), (245, 196, 81)
W, H = 1080, 1350
F = "C:/Windows/Fonts/"


def font(size, bold=False, light=False):
    return ImageFont.truetype(F + ("segoeuib.ttf" if bold else "segoeuil.ttf" if light else "segoeui.ttf"), size)


def background():
    img = Image.new("RGB", (W, H), NAVY)
    glow = Image.new("RGB", (W, H), NAVY)
    d = ImageDraw.Draw(glow)
    d.ellipse((-200, H - 520, W + 200, H + 700), fill=(150, 62, 70))
    d.ellipse((W - 420, -300, W + 300, 300), fill=(48, 62, 120))
    glow = glow.filter(ImageFilter.GaussianBlur(160))
    img = Image.blend(img, glow, 0.9)
    rib = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    rd = ImageDraw.Draw(rib)
    for x in range(0, W, 10):  # soft ribbed-glass lines
        rd.line((x, 0, x, H), fill=(255, 255, 255, 9), width=3)
    img = Image.alpha_composite(img.convert("RGBA"), rib).convert("RGB")
    return img


def wrap(draw, text, fnt, width):
    lines, cur = [], ""
    for w in text.split():
        t = (cur + " " + w).strip()
        if draw.textlength(t, font=fnt) <= width:
            cur = t
        else:
            lines.append(cur)
            cur = w
    return lines + [cur]


def card(shot, width):
    shot = shot.convert("RGB")
    shot = shot.resize((width, round(shot.height * width / shot.width)), Image.LANCZOS)
    pad = 14
    base = Image.new("RGBA", (shot.width + pad * 2, shot.height + pad * 2), CREAM + (255,))
    base.paste(shot, (pad, pad))
    mask = Image.new("L", base.size, 0)
    ImageDraw.Draw(mask).rounded_rectangle((0, 0, base.width, base.height), 26, fill=255)
    base.putalpha(mask)
    return base


def paste_shadow(img, card_img, xy, blur=30, off=22):
    sh = Image.new("RGBA", img.size, (0, 0, 0, 0))
    m = Image.new("L", card_img.size, 0)
    m.paste(card_img.split()[3].point(lambda p: 150 if p else 0))
    sh.paste((0, 0, 0, 255), (xy[0], xy[1] + off), m)
    sh = sh.filter(ImageFilter.GaussianBlur(blur))
    img.paste(sh, (0, 0), sh)
    img.paste(card_img, xy, card_img)


def pill(d, xy, text, fnt, fill, color):
    w = d.textlength(text, font=fnt)
    x, y = xy
    d.rounded_rectangle((x, y, x + w + 56, y + fnt.size + 28), 40, fill=fill)
    d.text((x + 28, y + 12), text, font=fnt, fill=color)
    return w + 56


def footer(d, n, total=10):
    d.text((70, H - 72), "Finance Intelligence Studio", font=font(28, True), fill=CREAM)
    d.text((W - 70 - d.textlength(f"{n} / {total}", font=font(28)), H - 72), f"{n} / {total}", font=font(28), fill=(190, 195, 215))


def price_of(slug):
    return CAT[slug]["tiers"]["Basic"]["price"]


KITS = [
    ("expense-tracker-for-shops", "FOR SHOP OWNERS", "Where did this month's money go?", ["money", "go?"], ["Log daily expenses in seconds", "Totals and charts update by themselves", "Sample data plus a blank copy"]),
    ("restaurant-revenue-and-expense-dashboard", "FOR RESTAURANT OWNERS", "Know what each day really earns", ["really", "earns"], ["Revenue and costs on one dashboard", "Spot slow days at a glance", "Sample data plus a blank copy"]),
    ("coaching-centre-fee-and-admission-dashboard", "FOR COACHING CENTRES", "Stop chasing fees from memory", ["fees"], ["Track admissions and fee dues", "A dashboard shows the totals", "Sample data plus a blank copy"]),
    ("personal-budget-tracker-customised", "FOR EVERYONE", "Save money without a finance degree", ["Save", "money"], ["Income, spending and savings by month", "Charts that update by themselves", "Sample data plus a blank copy"]),
    ("small-business-profit-and-loss-dashboard-customised", "FOR SMALL BUSINESSES", "Know your profit, not just your sales", ["profit,"], ["Revenue, costs and margin on one page", "Charts update from your entries", "Sample data plus a blank copy"]),
    ("resume-cv-for-finance-roles", "FOR JOB SEEKERS", "A resume recruiters actually read", ["actually", "read"], ["A clean Word template", "The sections recruiters scan first", "A guide on what to write in each"]),
    ("pitch-deck-financial-slides", "FOR STARTUPS AND STUDENTS", "A pitch deck that looks ready", ["looks", "ready"], ["Seven designed slides with charts", "Brand colours, easy to edit", "A guide on what to say on each slide"]),
    ("one-page-landing-page", "FOR ANYONE WITH A BUSINESS", "Get your business online today", ["online", "today"], ["Works on phone and desktop", "Replace the marked text and publish", "A step-by-step guide is included"]),
]


def cover():
    img = background().convert("RGBA")
    d = ImageDraw.Draw(img)
    pill(d, (70, 90), "NEW  |  READY IN 1 MINUTE", font(30, True), CORAL, NAVY)
    y = 200
    for line, col in (("Still running", CREAM), ("your business", CREAM), ("on a notebook?", CORAL)):
        d.text((70, y), line, font=font(112, True), fill=col)
        y += 128
    for t in ("50 ready-made kits: Excel, Word, decks, websites.", "From ₹99. Pay, and it lands in your inbox."):
        d.text((70, y + 24), t, font=font(38, True), fill=GOLD if "₹99" in t else (222, 226, 238))
        y += 56
    shots = ["small-business-profit-and-loss-dashboard-customised", "restaurant-revenue-and-expense-dashboard", "pitch-deck-financial-slides"]
    spots = [(-60, 810, -6), (300, 880, 4), (560, 770, -3)]
    for sl, (x, yy, ang) in zip(shots, spots):
        c = card(Image.open(PREV / f"{sl}.jpg"), 540).rotate(ang, expand=True, resample=Image.BICUBIC)
        paste_shadow(img, c, (x, yy))
    d = ImageDraw.Draw(img)
    d.rounded_rectangle((70, H - 150, W - 70, H - 60), 45, fill=CORAL)
    d.text((W // 2, H - 105), "finance-intelligence-studio.onrender.com", font=font(40, True), fill=NAVY, anchor="mm")
    d.rounded_rectangle((W - 70 - 230, 88, W - 70, 150), 31, fill=GOLD)
    d.text((W - 70 - 115, 119), "Swipe  →", font=font(32, True), fill=NAVY, anchor="mm")
    return img.convert("RGB")


def kit_slide(i, slug, tag, head, keys, bullets):
    img = background().convert("RGBA")
    d = ImageDraw.Draw(img)
    pill(d, (70, 80), tag, font(28, True), GOLD, NAVY)
    y = 190
    fnt = font(92, True)
    for t in wrap(d, head, fnt, 940):
        x = 70
        for word in t.split(" "):
            d.text((x, y), word, font=fnt, fill=CORAL if word in keys else CREAM)
            x += d.textlength(word + " ", font=fnt)
        y += 104
    im = Image.open(PREV / f"{slug}.jpg")
    c = card(im, min(860, int(450 * im.width / im.height)))
    top = y + 40
    paste_shadow(img, c, ((W - c.width) // 2, top))
    d = ImageDraw.Draw(img)
    by = top + c.height + 40
    for b in bullets:
        d.ellipse((70, by + 4, 106, by + 40), fill=GOLD)
        d.line([(79, by + 23), (86, by + 30), (98, by + 15)], fill=NAVY, width=5, joint="curve")
        d.text((126, by), b, font=font(36), fill=CREAM)
        by += 56
    d.rounded_rectangle((W - 70 - 300, H - 200, W - 70, H - 100), 50, fill=CORAL)
    d.text((W - 70 - 150, H - 150), f"From ₹{price_of(slug)}", font=font(52, True), fill=NAVY, anchor="mm")
    footer(d, i)
    return img.convert("RGB")


def cta():
    img = background().convert("RGBA")
    d = ImageDraw.Draw(img)
    d.text((70, 150), "Pick it.", font=font(130, True), fill=CREAM)
    d.text((70, 290), "Pay it.", font=font(130, True), fill=CREAM)
    d.text((70, 430), "Use it today.", font=font(130, True), fill=CORAL)
    y = 650
    for n, t in (("1", "Choose a kit on the site"), ("2", "Pay securely with Razorpay"), ("3", "Download it and get the email copy instantly")):
        d.ellipse((70, y, 150, y + 80), fill=GOLD)
        d.text((110, y + 40), n, font=font(46, True), fill=NAVY, anchor="mm")
        d.text((185, y + 40), t, font=font(40), fill=CREAM, anchor="lm")
        y += 115
    d.rounded_rectangle((70, 1010, W - 70, 1140), 70, fill=CORAL)
    d.text((W // 2, 1075), "finance-intelligence-studio.onrender.com", font=font(40, True), fill=NAVY, anchor="mm")
    d.text((W // 2, 1200), "Every price ₹99 to ₹499  |  Link in the first comment", font=font(32), fill=(214, 218, 232), anchor="mm")
    footer(d, 10)
    return img.convert("RGB")


def main():
    OUT.mkdir(exist_ok=True)
    for old in OUT.glob("*.jpg"):
        old.unlink()
    slides = [cover()] + [kit_slide(i + 2, *k) for i, k in enumerate(KITS)] + [cta()]
    for n, s in enumerate(slides, 1):
        s.save(OUT / f"slide-{n:02d}.jpg", quality=92)
    print(len(slides), "slides")


if __name__ == "__main__":
    main()
