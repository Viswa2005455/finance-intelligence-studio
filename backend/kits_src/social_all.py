"""Gumroad listing data + per-kit thumbnail and cover images for every kit not yet listed.
uv run python kits_src/social_all.py <plan.json> <out_listing.json>"""
import json
import sys
from pathlib import Path

from PIL import Image, ImageDraw

import social_banners as B
from social_slides import CORAL, CREAM, GOLD, NAVY, PREV, card, font, paste_shadow, pill

ROOT = Path(__file__).resolve().parent.parent.parent
DONE = {"expense-tracker-for-shops", "restaurant-revenue-and-expense-dashboard", "coaching-centre-fee-and-admission-dashboard",
        "resume-cv-for-finance-roles", "one-page-landing-page", "pitch-deck-financial-slides",
        "small-business-profit-and-loss-dashboard-customised", "personal-budget-tracker-customised"}
OUT = ROOT / "promo-images" / "gumroad"
TOOL = {"Excel": "Microsoft Excel (or Google Sheets)", "Word": "Microsoft Word", "PowerPoint": "Microsoft PowerPoint", "Website": "any web browser and text editor"}


def tools(items):
    kinds = []
    for i in items:
        k = i["kind"]
        if k != "Word" or len(items) == 1:
            if k not in kinds:
                kinds.append(k)
    return kinds or ["Word"]


def short(s, n):
    return s if len(s) <= n else s[: n - 1].rsplit(" ", 1)[0] + "..."


def thumb(slug, title, price, path):
    W = H = 1080
    img = B.bg(W, H)
    d = ImageDraw.Draw(img)
    pill(d, (70, 70), "READY-MADE KIT  |  INSTANT", font(28, True), CORAL, NAVY)
    y = B.draw_head(d, (70, 160), title, [], font(80, True), 940, 92)
    d.text((70, y + 10), f"From ₹{price}", font=font(52, True), fill=GOLD)
    c = card(Image.open(PREV / f"{slug}.jpg"), min(760, int(430 * Image.open(PREV / f"{slug}.jpg").width / Image.open(PREV / f"{slug}.jpg").height)))
    paste_shadow(img, c, ((W - c.width) // 2, max(y + 100, 520)))
    d = ImageDraw.Draw(img)
    d.rounded_rectangle((70, H - 100, W - 70, H - 40), 30, fill=CORAL)
    d.text((W // 2, H - 70), "finance-intelligence-studio.onrender.com", font=font(30, True), fill=NAVY, anchor="mm")
    img.convert("RGB").save(path, quality=90)


def cover(slug, title, forwho, kinds, price, path):
    old = B.OUT
    B.OUT = path.parent
    B.landscape(slug, "READY-MADE KIT", title, [], ["Instant download after payment", " + ".join(kinds) + " files", "Step-by-step guide included"], path.name)
    B.OUT = old


def main():
    plan = json.load(open(sys.argv[1], encoding="utf-8"))
    OUT.mkdir(parents=True, exist_ok=True)
    out = []
    for p in plan:
        if p["slug"] in DONE:
            continue
        kinds = tools(p["items"])
        name = short(f"{p['title']} Kit (India, ₹) | Ready-Made Template, Instant Download", 110)
        lines = [p["promise"], "", "What you get:"]
        for it in p["items"]:
            lines.append(f"{it['kind']}: {it['what']}")
        lines += ["", f"Works in {' and '.join(TOOL.get(k, k) for k in kinds)}. Instant download after payment. Built for {p['forWho'][0].lower() + p['forWho'][1:]}, with amounts in rupees where it applies.", "",
                  "Need it fitted to your business? Message me after buying and I can customise it."]
        tpath = OUT / f"{p['slug']}-thumb.jpg"
        cpath = OUT / f"{p['slug']}-cover.jpg"
        thumb(p["slug"], p["title"], p["price"], tpath)
        cover(p["slug"], p["title"], p["forWho"], kinds, p["price"], cpath)
        out.append({"slug": p["slug"], "name": name, "desc": "\n".join(lines), "price": p["price"], "zip": str(ROOT / "backend" / "app" / "payments" / "kits" / f"{p['slug']}.zip"), "thumb": str(tpath), "cover": str(cpath)})
    json.dump(out, open(sys.argv[2], "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(len(out), "kits prepared")


if __name__ == "__main__":
    main()
