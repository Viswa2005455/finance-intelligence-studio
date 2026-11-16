"""Landscape (1600x900) and square (1080x1080) promo images: uv run python kits_src/social_banners.py"""
from PIL import Image, ImageDraw, ImageFilter

import social_slides as S
from social_slides import CORAL, CREAM, GOLD, NAVY, PREV, font, card, paste_shadow, pill, price_of, wrap

OUT = S.OUT.parent / "promo-images"


def bg(w, h):
    img = Image.new("RGB", (w, h), NAVY)
    glow = Image.new("RGB", (w, h), NAVY)
    d = ImageDraw.Draw(glow)
    d.ellipse((-w // 4, h - h // 2, w + w // 4, h + h), fill=(150, 62, 70))
    d.ellipse((w - w // 3, -h // 3, w + w // 4, h // 3), fill=(48, 62, 120))
    img = Image.blend(img, glow.filter(ImageFilter.GaussianBlur(120)), 0.9).convert("RGBA")
    rib = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    rd = ImageDraw.Draw(rib)
    for x in range(0, w, 10):
        rd.line((x, 0, x, h), fill=(255, 255, 255, 9), width=3)
    return Image.alpha_composite(img, rib)


def draw_head(d, xy, text, keys, fnt, maxw, step):
    x0, y = xy
    for t in wrap(d, text, fnt, maxw):
        x = x0
        for word in t.split(" "):
            d.text((x, y), word, font=fnt, fill=CORAL if word in keys else CREAM)
            x += d.textlength(word + " ", font=fnt)
        y += step
    return y


def landscape(slug, tag, head, keys, bullets, name):
    W, H = 1600, 900
    img = bg(W, H)
    d = ImageDraw.Draw(img)
    pill(d, (70, 70), tag, font(28, True), GOLD, NAVY)
    y = draw_head(d, (70, 160), head, keys, font(68, True), 740, 80)
    by = y + 30
    for b in bullets:
        d.ellipse((70, by + 4, 106, by + 40), fill=GOLD)
        d.line([(79, by + 23), (86, by + 30), (98, by + 15)], fill=NAVY, width=5, joint="curve")
        d.text((126, by), b, font=font(34), fill=CREAM)
        by += 54
    d.rounded_rectangle((70, H - 150, 560, H - 60), 45, fill=CORAL)
    d.text((315, H - 105), f"From ₹{price_of(slug)}  |  instant", font=font(40, True), fill=NAVY, anchor="mm")
    im = Image.open(PREV / f"{slug}.jpg")
    c = card(im, min(780, int(560 * im.width / im.height)))
    paste_shadow(img, c, (W - c.width - 60, (H - c.height) // 2 - 20))
    d = ImageDraw.Draw(img)
    d.text((W - 60 - d.textlength("finance-intelligence-studio.onrender.com", font=font(28, True)), H - 60), "finance-intelligence-studio.onrender.com", font=font(28, True), fill=(214, 218, 232))
    img.convert("RGB").save(OUT / name, quality=92)


def hero():
    W, H = 1600, 900
    img = bg(W, H)
    d = ImageDraw.Draw(img)
    pill(d, (70, 70), "NEW  |  READY IN 1 MINUTE", font(28, True), CORAL, NAVY)
    y = draw_head(d, (70, 150), "50 business kits. From ₹99.", ["From", "₹99."], font(92, True), 760, 104)
    for t in wrap(d, "Excel dashboards, resume, pitch deck and website templates. Pay, and it lands in your inbox the same minute.", font(36), 700):
        d.text((70, y + 20), t, font=font(36), fill=(222, 226, 238))
        y += 50
    for s, (x, yy, ang) in zip(["small-business-profit-and-loss-dashboard-customised", "restaurant-revenue-and-expense-dashboard", "pitch-deck-financial-slides"], [(830, 70, 4), (900, 300, -3), (860, 540, 3)]):
        c = card(Image.open(PREV / f"{s}.jpg"), 620).rotate(ang, expand=True, resample=Image.BICUBIC)
        paste_shadow(img, c, (x, yy))
    d = ImageDraw.Draw(img)
    d.rounded_rectangle((70, H - 150, 800, H - 60), 45, fill=CORAL)
    d.text((435, H - 105), "finance-intelligence-studio.onrender.com", font=font(32, True), fill=NAVY, anchor="mm")
    img.convert("RGB").save(OUT / "00-hero-banner.jpg", quality=92)


def square():
    W = H = 1080
    img = bg(W, H)
    d = ImageDraw.Draw(img)
    pill(d, (70, 70), "NEW  |  READY IN 1 MINUTE", font(28, True), CORAL, NAVY)
    y = draw_head(d, (70, 160), "Still running your business on a notebook?", ["notebook?"], font(86, True), 940, 98)
    d.text((70, y + 10), "50 kits. From ₹99. Instant.", font=font(46, True), fill=GOLD)
    c = card(Image.open(PREV / "small-business-profit-and-loss-dashboard-customised.jpg"), 700)
    paste_shadow(img, c, ((W - c.width) // 2, y + 90))
    d = ImageDraw.Draw(img)
    d.rounded_rectangle((70, H - 120, W - 70, H - 50), 35, fill=CORAL)
    d.text((W // 2, H - 85), "finance-intelligence-studio.onrender.com", font=font(34, True), fill=NAVY, anchor="mm")
    img.convert("RGB").save(OUT / "01-square-post.jpg", quality=92)


KITS = [
    ("expense-tracker-for-shops", "FOR SHOP OWNERS", "Where did this month's money go?", ["money", "go?"], ["Log daily expenses in seconds", "Totals and charts update themselves", "Sample data plus a blank copy"]),
    ("restaurant-revenue-and-expense-dashboard", "FOR RESTAURANT OWNERS", "Know what each day really earns", ["really", "earns"], ["Revenue and costs on one dashboard", "Spot slow days at a glance", "Sample data plus a blank copy"]),
    ("coaching-centre-fee-and-admission-dashboard", "FOR COACHING CENTRES", "Stop chasing fees from memory", ["fees"], ["Track admissions and fee dues", "A dashboard shows the totals", "Sample data plus a blank copy"]),
    ("personal-budget-tracker-customised", "FOR EVERYONE", "Save money without a finance degree", ["Save", "money"], ["Income, spending and savings by month", "Charts that update themselves", "Sample data plus a blank copy"]),
    ("resume-cv-for-finance-roles", "FOR JOB SEEKERS", "A resume recruiters actually read", ["actually", "read"], ["A clean Word template", "The sections recruiters scan first", "A guide on what to write"]),
    ("one-page-landing-page", "FOR ANYONE WITH A BUSINESS", "Get your business online today", ["online", "today"], ["Works on phone and desktop", "Replace the marked text and publish", "A step-by-step guide is included"]),
]


def main():
    OUT.mkdir(exist_ok=True)
    for old in OUT.glob("*.jpg"):
        old.unlink()
    hero()
    square()
    for i, k in enumerate(KITS, 2):
        landscape(*k[:5], name=f"{i:02d}-{k[0]}.jpg")
    print(len(list(OUT.glob('*.jpg'))), "images")


if __name__ == "__main__":
    main()
