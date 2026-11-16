"""Website templates (plain HTML + CSS + a little JavaScript, no build step). Open index.html to preview;
search for "EDIT:" to find every piece of text to change; upload the folder to any web host.

Design: navy, cream and coral, a dark glowing hero with fine vertical ridges, glass cards, scroll-in animation.
"""

from __future__ import annotations

CSS = """/* EDIT: change these three colours to rebrand the whole site */
:root { --navy: #14213D; --navy-2: #0E1730; --cream: #F4EDE0; --coral: #FF6B5B; --coral-dark: #D9452F; --ink: #1B2540; --muted: #5B6477; --line: rgba(20,33,61,.12); --radius: 18px; }
* { box-sizing: border-box; }
html { scroll-behavior: smooth; }
body { margin: 0; font-family: "Inter", system-ui, -apple-system, "Segoe UI", Roboto, sans-serif; color: var(--ink); background: #FBF8F2; line-height: 1.65; -webkit-font-smoothing: antialiased; }
img { max-width: 100%; height: auto; display: block; }
a { color: var(--coral-dark); }
h1, h2, h3 { line-height: 1.15; letter-spacing: -.02em; margin: 0; color: var(--navy); }
.wrap { width: min(1140px, 92%); margin-inline: auto; }
.skip { position: absolute; left: -999px; top: 8px; background: #fff; padding: 8px 14px; border-radius: 8px; z-index: 99; }
.skip:focus { left: 8px; }
:focus-visible { outline: 3px solid var(--coral); outline-offset: 2px; border-radius: 6px; }

/* header */
header.site { position: sticky; top: 0; z-index: 30; background: rgba(14,23,48,.78); -webkit-backdrop-filter: blur(14px); backdrop-filter: blur(14px); border-bottom: 1px solid rgba(244,237,224,.1); }
header.site .wrap { display: flex; align-items: center; justify-content: space-between; gap: 16px; padding: 14px 0; }
.logo { font-weight: 800; font-size: 1.15rem; color: var(--cream); text-decoration: none; letter-spacing: -.02em; display: inline-flex; align-items: center; gap: 10px; }
.logo i { display: inline-grid; place-items: center; width: 32px; height: 32px; border-radius: 10px; background: var(--coral); color: var(--navy); font-style: normal; font-weight: 800; }
nav ul { display: flex; gap: 6px; list-style: none; margin: 0; padding: 0; }
nav a { text-decoration: none; color: rgba(244,237,224,.82); font-weight: 600; padding: 8px 14px; border-radius: 999px; font-size: .95rem; }
nav a:hover { color: #fff; background: rgba(244,237,224,.1); }
nav a.active { color: var(--navy); background: var(--cream); }
.menu-btn { display: none; background: rgba(244,237,224,.1); color: var(--cream); border: 1px solid rgba(244,237,224,.25); border-radius: 10px; padding: 8px 14px; font: inherit; cursor: pointer; }

/* buttons */
.btn { display: inline-flex; align-items: center; gap: 8px; background: var(--coral); color: var(--navy); padding: 13px 24px; border-radius: 999px; font-weight: 700; text-decoration: none; border: 2px solid var(--coral); cursor: pointer; font-size: 1rem; font-family: inherit; transition: transform .15s ease, background .15s ease; }
.btn:hover { background: #FF8272; border-color: #FF8272; transform: translateY(-1px); }
.btn.alt { background: transparent; color: var(--cream); border-color: rgba(244,237,224,.4); }
.btn.alt:hover { background: rgba(244,237,224,.1); }
.btn.dark { background: var(--navy); color: var(--cream); border-color: var(--navy); }
.btn.sm { padding: 9px 18px; font-size: .92rem; }

/* hero */
.hero { position: relative; overflow: hidden; color: var(--cream); padding: 96px 0 88px; background: radial-gradient(800px 520px at 82% 105%, rgba(255,107,91,.55), transparent 62%), radial-gradient(640px 460px at 8% 0%, rgba(91,110,225,.28), transparent 62%), linear-gradient(170deg, #1A2B52, var(--navy) 55%, var(--navy-2)); }
.hero::before { content: ""; position: absolute; inset: 0; pointer-events: none; background: repeating-linear-gradient(90deg, rgba(244,237,224,.04) 0 2px, transparent 2px 9px); }
.hero .wrap { position: relative; display: grid; grid-template-columns: 1.4fr 1fr; gap: 40px; align-items: center; }
.hero.single .wrap { grid-template-columns: 1fr; }
.eyebrow { display: inline-block; color: var(--coral); font-weight: 700; letter-spacing: .1em; text-transform: uppercase; font-size: .8rem; margin-bottom: 14px; }
.hero h1 { color: var(--cream); font-size: clamp(2.2rem, 5.4vw, 4rem); font-weight: 600; letter-spacing: -.04em; line-height: 1.04; }
.hero h1 em { font-style: normal; color: var(--coral); }
.hero p.lead { color: rgba(244,237,224,.82); font-size: 1.15rem; max-width: 600px; margin: 18px 0 0; }
.actions { display: flex; flex-wrap: wrap; gap: 12px; margin-top: 28px; }
.trust { display: flex; flex-wrap: wrap; gap: 8px 22px; list-style: none; padding: 0; margin: 28px 0 0; color: rgba(244,237,224,.78); font-size: .92rem; }
.trust li::before { content: "\\2713  "; color: var(--coral); font-weight: 800; }
.glass { background: rgba(244,237,224,.09); border: 1px solid rgba(244,237,224,.2); border-radius: 20px; padding: 22px; -webkit-backdrop-filter: blur(16px); backdrop-filter: blur(16px); color: var(--cream); }
.glass h3 { color: var(--cream); font-size: 1.05rem; margin-bottom: 10px; }
.glass .row { display: flex; justify-content: space-between; gap: 12px; padding: 10px 0; border-top: 1px solid rgba(244,237,224,.14); font-size: .95rem; }
.glass .row:first-of-type { border-top: 0; }
.glass .tag { background: var(--coral); color: var(--navy); font-weight: 700; padding: 2px 10px; border-radius: 999px; font-size: .8rem; }
.avatar { width: 120px; height: 120px; border-radius: 50%; display: grid; place-items: center; font-size: 2.6rem; font-weight: 800; color: var(--navy); background: linear-gradient(135deg, var(--coral), #FFB4A8); border: 4px solid rgba(244,237,224,.35); margin-bottom: 18px; }

/* sections */
section { padding: 72px 0; }
section.alt { background: var(--cream); }
section.dark { background: var(--navy); color: var(--cream); }
section.dark h2, section.dark h3 { color: var(--cream); }
.kicker { display: block; color: var(--coral-dark); font-weight: 700; letter-spacing: .08em; text-transform: uppercase; font-size: .8rem; margin-bottom: 8px; }
section.dark .kicker { color: var(--coral); }
h2.title { font-size: clamp(1.7rem, 3.4vw, 2.5rem); font-weight: 650; }
.lead2 { color: var(--muted); margin: 10px 0 36px; max-width: 640px; font-size: 1.05rem; }
.dark .lead2 { color: rgba(244,237,224,.75); }
.grid { display: grid; gap: 20px; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); }
.grid.two { grid-template-columns: repeat(auto-fit, minmax(340px, 1fr)); }
.card { background: #fff; border: 1px solid var(--line); border-radius: var(--radius); padding: 26px; box-shadow: 0 14px 30px -22px rgba(20,33,61,.45); transition: transform .18s ease, box-shadow .18s ease; }
.card:hover { transform: translateY(-4px); box-shadow: 0 22px 40px -22px rgba(255,107,91,.5); }
.card h3 { font-size: 1.12rem; margin: 12px 0 6px; }
.card p { margin: 0; color: var(--muted); font-size: .96rem; }
.ico { display: grid; place-items: center; width: 50px; height: 50px; border-radius: 14px; background: rgba(255,107,91,.15); font-size: 1.5rem; }
.price { font-size: 2rem; font-weight: 800; color: var(--navy); letter-spacing: -.03em; }
.card.featured { border: 2px solid var(--coral); background: #FFF6EC; position: relative; }
.card.featured::after { content: "Most popular"; position: absolute; top: -13px; right: 20px; background: var(--coral); color: var(--navy); font-size: .78rem; font-weight: 800; padding: 3px 12px; border-radius: 999px; }
.list { list-style: none; padding: 0; margin: 14px 0 0; display: grid; gap: 8px; color: var(--ink); font-size: .95rem; }
.list li::before { content: "\\2713  "; color: var(--coral-dark); font-weight: 800; }
.ph { background: linear-gradient(135deg, #E9E1D2, #D5DBEB); border-radius: 14px; aspect-ratio: 4/3; display: grid; place-items: center; color: var(--muted); font-weight: 600; text-align: center; padding: 12px; }
.steps { counter-reset: s; display: grid; gap: 20px; grid-template-columns: repeat(auto-fit, minmax(240px, 1fr)); }
.steps > div { counter-increment: s; position: relative; padding: 26px 24px 24px 24px; border-radius: var(--radius); background: rgba(244,237,224,.07); border: 1px solid rgba(244,237,224,.16); }
.steps > div::before { content: counter(s); display: grid; place-items: center; width: 38px; height: 38px; border-radius: 50%; background: var(--coral); color: var(--navy); font-weight: 800; margin-bottom: 14px; }
.steps h3 { font-size: 1.1rem; margin-bottom: 6px; }
.steps p { margin: 0; color: rgba(244,237,224,.75); font-size: .96rem; }
.stats { display: grid; grid-template-columns: repeat(auto-fit, minmax(170px, 1fr)); gap: 16px; text-align: center; }
.stats b { display: block; font-size: 2.6rem; font-weight: 700; letter-spacing: -.03em; color: var(--navy); }
.dark .stats b { color: var(--coral); }
.stats span { color: var(--muted); font-size: .95rem; }
.dark .stats span { color: rgba(244,237,224,.75); }
.quote { font-size: 1.02rem; color: var(--ink); }
.quote::before { content: "\\201C"; display: block; font-size: 2.6rem; line-height: .6; color: var(--coral); font-family: Georgia, serif; }
.who { display: flex; align-items: center; gap: 10px; margin-top: 16px; font-size: .92rem; }
.who i { width: 38px; height: 38px; border-radius: 50%; background: var(--navy); color: var(--cream); display: grid; place-items: center; font-style: normal; font-weight: 700; }
.who span { color: var(--muted); display: block; font-size: .85rem; }
.bar { height: 10px; border-radius: 999px; background: rgba(20,33,61,.1); overflow: hidden; margin: 6px 0 14px; }
.bar i { display: block; height: 100%; border-radius: 999px; background: linear-gradient(90deg, var(--coral), #FFB4A8); }
.skill { display: flex; justify-content: space-between; font-weight: 600; font-size: .95rem; }
.timeline { border-left: 3px solid var(--coral); padding-left: 24px; display: grid; gap: 26px; margin-left: 8px; }
.timeline h3 { font-size: 1.05rem; }
.timeline small { color: var(--muted); }
.tags { display: flex; flex-wrap: wrap; gap: 6px; margin-top: 12px; }
.tags span { font-size: .78rem; font-weight: 700; padding: 3px 10px; border-radius: 999px; background: rgba(20,33,61,.08); color: var(--navy); }
details { background: #fff; border: 1px solid var(--line); border-radius: 14px; margin-bottom: 10px; }
details summary { cursor: pointer; padding: 16px 20px; font-weight: 650; color: var(--navy); list-style: none; display: flex; justify-content: space-between; gap: 12px; }
details summary::after { content: "+"; font-size: 1.4rem; line-height: 1; color: var(--coral-dark); }
details[open] summary::after { content: "\\2212"; }
details summary::-webkit-details-marker { display: none; }
details p { margin: 0; padding: 0 20px 18px; color: var(--muted); }
.band { position: relative; overflow: hidden; padding: 64px 0; text-align: center; color: var(--cream); background: radial-gradient(600px 300px at 80% 120%, rgba(255,107,91,.6), transparent 65%), linear-gradient(160deg, #1A2B52, var(--navy)); }
.band::before { content: ""; position: absolute; inset: 0; background: repeating-linear-gradient(90deg, rgba(244,237,224,.04) 0 2px, transparent 2px 9px); pointer-events: none; }
.band > .wrap { position: relative; }
.band h2 { color: var(--cream); font-size: clamp(1.7rem, 3.6vw, 2.6rem); font-weight: 600; letter-spacing: -.03em; }
.band p { color: rgba(244,237,224,.8); margin: 10px auto 24px; max-width: 560px; }
table.menu, table.fees { width: 100%; border-collapse: collapse; background: #fff; border-radius: 14px; overflow: hidden; }
table.menu td, table.fees td, table.fees th { padding: 14px 18px; border-bottom: 1px solid var(--line); text-align: left; vertical-align: top; }
table.fees th { background: var(--navy); color: var(--cream); font-weight: 650; }
table.menu td:last-child, table.fees td:last-child { text-align: right; font-weight: 800; white-space: nowrap; color: var(--navy); }
table.menu small { color: var(--muted); display: block; }
.veg::before, .nonveg::before { content: ""; display: inline-block; width: 10px; height: 10px; border-radius: 50%; margin-right: 8px; background: #2BB59A; }
.nonveg::before { background: var(--coral-dark); }
.chips { display: flex; flex-wrap: wrap; gap: 8px; margin-bottom: 22px; }
.chips a { text-decoration: none; padding: 8px 16px; border-radius: 999px; background: #fff; border: 1px solid var(--line); color: var(--navy); font-weight: 650; font-size: .92rem; }
.chips a:hover { background: var(--navy); color: var(--cream); }
form { display: grid; gap: 14px; max-width: 560px; }
label { font-weight: 650; display: grid; gap: 6px; font-size: .95rem; color: var(--navy); }
input, select, textarea { font: inherit; padding: 13px 14px; border: 1px solid rgba(20,33,61,.22); border-radius: 12px; width: 100%; background: #fff; color: var(--ink); }
textarea { min-height: 130px; }
.info { display: grid; gap: 14px; }
.info .card { padding: 20px; }
.small { font-size: .88rem; color: var(--muted); }
footer.site { background: var(--navy-2); color: rgba(244,237,224,.78); padding: 48px 0 28px; }
footer.site .cols { display: grid; gap: 28px; grid-template-columns: 1.4fr 1fr 1fr; }
footer.site b { color: var(--cream); }
footer.site a { color: var(--coral); }
footer.site .copy { border-top: 1px solid rgba(244,237,224,.12); margin-top: 28px; padding-top: 18px; font-size: .88rem; }
.wa { position: fixed; right: 16px; bottom: 16px; background: #25d366; color: #0b2e1a; padding: 12px 18px; border-radius: 999px; font-weight: 800; text-decoration: none; box-shadow: 0 10px 24px -8px rgba(0,0,0,.5); z-index: 40; }
.js .reveal { opacity: 0; transform: translateY(18px); transition: opacity .6s ease, transform .6s ease; }
.js .reveal.in { opacity: 1; transform: none; }
@media (max-width: 860px) {
  .hero .wrap { grid-template-columns: 1fr; }
  .hero { padding: 64px 0 56px; }
  footer.site .cols { grid-template-columns: 1fr; }
}
@media (max-width: 720px) {
  .menu-btn { display: block; }
  nav ul { display: none; position: absolute; top: 100%; left: 0; right: 0; background: var(--navy-2); flex-direction: column; gap: 0; padding: 8px 4%; border-bottom: 1px solid rgba(244,237,224,.12); }
  nav ul.open { display: flex; }
  nav a { display: block; border-radius: 10px; padding: 14px; }
  header .btn.sm { display: none; }
  section { padding: 52px 0; }
}
@media (prefers-reduced-motion: reduce) { .js .reveal { opacity: 1; transform: none; transition: none; } .card, .btn { transition: none; } }
"""

JS = """// Mobile menu, and a gentle fade-in as sections scroll into view
document.addEventListener('DOMContentLoaded', function () {
  var b = document.querySelector('.menu-btn'), u = document.querySelector('nav ul');
  if (b && u) b.addEventListener('click', function () { u.classList.toggle('open'); });
  var y = document.getElementById('yr'); if (y) y.textContent = new Date().getFullYear();
  var items = document.querySelectorAll('.reveal');
  function show(e) { e.classList.add('in'); }
  var vh = window.innerHeight || 800;
  items.forEach(function (e) { if (e.getBoundingClientRect().top < vh * 0.95) show(e); });  // already on screen: show now
  if (!('IntersectionObserver' in window)) { items.forEach(show); return; }
  var io = new IntersectionObserver(function (es) { es.forEach(function (e) { if (e.isIntersecting) { show(e.target); io.unobserve(e.target); } }); }, { threshold: 0.12 });
  items.forEach(function (e) { if (!e.classList.contains('in')) io.observe(e); });
  setTimeout(function () { items.forEach(show); }, 6000);  // safety net: never leave content hidden
});
"""

BIZ = "Your Business Name"
PHONE_WA = "919999999999"
EMAIL = "hello@yourbusiness.com"


def css() -> bytes:
    return CSS.encode()


def page(title: str, desc: str, body: str, nav: list[tuple[str, str]], active: str, logo: str = BIZ, cta: tuple[str, str] = ("Contact us", "contact.html")) -> bytes:
    items = "".join('<li><a href="{}"{}>{}</a></li>'.format(h, ' class="active"' if h == active else "", t) for t, h in nav)
    initial = (logo[:1] or "B").upper()
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title>
<meta name="description" content="{desc}">
<meta name="theme-color" content="#14213D">
<link rel="stylesheet" href="style.css">
<script>document.documentElement.className += " js";</script>
<script src="script.js" defer></script>
</head>
<body>
<a class="skip" href="#main">Skip to content</a>
<header class="site"><div class="wrap">
  <a class="logo" href="{nav[0][1]}"><i>{initial}</i>{logo}</a>
  <nav aria-label="Main"><ul>{items}</ul></nav>
  <a class="btn sm" href="{cta[1]}">{cta[0]}</a>
  <button class="menu-btn" aria-label="Menu">Menu</button>
</div></header>
<main id="main">
{body}
</main>
<footer class="site"><div class="wrap">
  <div class="cols">
    <div><b>{logo}</b><br>EDIT: one line about what you do and where.<br><span class="small">EDIT: address line, city, pin code</span></div>
    <div><b>Contact</b><br><a href="mailto:{EMAIL}">{EMAIL}</a><br><a href="https://wa.me/{PHONE_WA}">WhatsApp us</a><br>EDIT: phone number</div>
    <div><b>Hours</b><br>EDIT: Mon to Sat, 9 am to 7 pm<br>EDIT: Sunday closed</div>
  </div>
  <div class="copy">&copy; <span id="yr">2026</span> {logo}. All rights reserved.</div>
</div></footer>
<a class="wa" href="https://wa.me/{PHONE_WA}?text=Hello%2C%20I%20have%20an%20enquiry">Chat on WhatsApp</a>
</body>
</html>
""".encode()


# ------------------------------------------------------------------ reusable sections
def feat(icon: str, title: str, text: str) -> str:
    return f'<div class="card reveal"><div class="ico">{icon}</div><h3>{title}</h3><p>{text}</p></div>'


def sect(kicker: str, title: str, lead: str, inner: str, cls: str = "") -> str:
    return f'<section class="{cls}"><div class="wrap"><span class="kicker">{kicker}</span><h2 class="title">{title}</h2><p class="lead2">{lead}</p>{inner}</div></section>'


def stats(items: list[tuple[str, str]], cls: str = "") -> str:
    inner = "".join(f"<div><b>{n}</b><span>{t}</span></div>" for n, t in items)
    return f'<section class="{cls}"><div class="wrap"><div class="stats reveal">{inner}</div></div></section>'


def steps(items: list[tuple[str, str]]) -> str:
    return '<div class="steps">' + "".join(f'<div class="reveal"><h3>{t}</h3><p>{d}</p></div>' for t, d in items) + "</div>"


def quotes(n: int = 3) -> str:
    one = ('<div class="card reveal"><p class="quote">EDIT: a real review from a real customer, with their permission. Never invent reviews.</p>'
           '<div class="who"><i>C</i><div>Customer name<span>EDIT: role or area</span></div></div></div>')
    return '<div class="grid">' + one * n + "</div>"


def faq(items: list[tuple[str, str]]) -> str:
    return '<div class="reveal" style="max-width:820px">' + "".join(f"<details><summary>{q}</summary><p>{a}</p></details>" for q, a in items) + "</div>"


def cta(heading: str = "Ready to get started?", text: str = "EDIT: one friendly sentence inviting the visitor to take the next step.", href: str = "contact.html", label: str = "Get in touch") -> str:
    return f'<section class="band"><div class="wrap reveal"><h2>{heading}</h2><p>{text}</p><a class="btn" href="{href}">{label}</a></div></section>'


def form(fields: str = "", button: str = "Send enquiry", note: bool = True) -> str:
    base = fields or '<label>Your name <input name="name" required></label><label>Phone <input name="phone" type="tel" required></label><label>Email <input name="email" type="email"></label><label>Message <textarea name="message" required></textarea></label>'
    n = '<p class="small">EDIT: create a free form at formspree.io (or use a Google Form) and paste its link in the form action. Until then, visitors can use the WhatsApp button.</p>' if note else ""
    return f'<form action="https://formspree.io/f/YOUR_FORM_ID" method="post">{base}<button class="btn" type="submit">{button}</button>{n}</form>'


def hero(eyebrow: str, h1: str, lead: str, a1: tuple[str, str], a2: tuple[str, str], side: str = "", trust: list[str] | None = None, single: bool = False) -> str:
    tr = "<ul class='trust'>" + "".join(f"<li>{t}</li>" for t in trust) + "</ul>" if trust else ""
    side_html = f"<div>{side}</div>" if side else ""
    return ('<section class="hero{}"><div class="wrap"><div><span class="eyebrow">{}</span><h1>{}</h1><p class="lead">{}</p>'
            '<div class="actions"><a class="btn" href="{}">{}</a><a class="btn alt" href="{}">{}</a></div>{}</div>{}</div></section>').format(
        " single" if single or not side else "", eyebrow, h1, lead, a1[1], a1[0], a2[1], a2[0], tr, side_html)


NAV5 = [("Home", "index.html"), ("About", "about.html"), ("Services", "services.html"), ("Gallery", "gallery.html"), ("Contact", "contact.html")]
ICONS = ["&#9889;", "&#128176;", "&#11088;", "&#128222;", "&#127942;", "&#128161;"]


# ------------------------------------------------------------------ 1. landing page
def landing() -> dict[str, bytes]:
    nav = [("Benefits", "#benefits"), ("How it works", "#how"), ("Pricing", "#pricing"), ("FAQ", "#faq"), ("Contact", "#contact")]
    side = ('<div class="glass"><h3>This week&apos;s offer</h3><div class="row"><span>EDIT: Basic package</span><b>&#8377;999</b></div><div class="row"><span>EDIT: Standard package</span><b>&#8377;1,999</b></div>'
            '<div class="row"><span>Delivery</span><span class="tag">EDIT: 2 days</span></div></div>')
    pricing = ('<div class="grid" id="pricing"><div class="card reveal"><h3>Basic</h3><div class="price">&#8377;999</div><ul class="list"><li>EDIT: what is included</li><li>EDIT: what is included</li></ul><p style="margin-top:16px"><a class="btn dark sm" href="#contact">Choose Basic</a></p></div>'
               '<div class="card featured reveal"><h3>Standard</h3><div class="price">&#8377;1,999</div><ul class="list"><li>EDIT: everything in Basic</li><li>EDIT: plus this</li><li>EDIT: plus this</li></ul><p style="margin-top:16px"><a class="btn sm" href="#contact">Choose Standard</a></p></div>'
               '<div class="card reveal"><h3>Premium</h3><div class="price">&#8377;3,999</div><ul class="list"><li>EDIT: everything in Standard</li><li>EDIT: plus this</li></ul><p style="margin-top:16px"><a class="btn dark sm" href="#contact">Choose Premium</a></p></div></div>')
    benefits = ('<div class="grid" id="benefits">' + feat(ICONS[0], "Fast", "EDIT: delivery or response time.") + feat(ICONS[1], "Fair prices", "EDIT: clear prices, no surprises.") + feat(ICONS[2], "Trusted", "EDIT: years of experience or customers served.")
                + feat(ICONS[3], "Easy to reach", "EDIT: call, WhatsApp or email any time.") + feat(ICONS[4], "Quality checked", "EDIT: how you make sure the work is right.") + feat(ICONS[5], "Made for you", "EDIT: what you tailor for each customer.") + "</div>")
    questions = [("How long does it take?", "EDIT: your honest timeline."), ("How do I pay?", "EDIT: UPI, bank transfer, card."), ("Can I change my mind?", "EDIT: your refund or revision policy."),
                 ("Do you work with small businesses?", "EDIT: yes, and who you serve best."), ("How do I contact you?", "EDIT: form below, WhatsApp or phone.")]
    body = (hero("EDIT: your category", "EDIT: One clear promise <em>in one line.</em>", "EDIT: Explain in two sentences who this is for and the result they get. Keep it simple and specific.",
                 ("Get a free quote", "#contact"), ("See how it works", "#how"), side, ["EDIT: Fast delivery", "EDIT: Fair prices", "EDIT: Friendly support"])
            + sect("Why choose us", "Three reasons customers pick us", "EDIT: replace with your real strengths.", benefits)
            + sect("How it works", "From enquiry to done in 3 steps", "EDIT: describe your real process.",
                   '<div id="how">' + steps([("Tell us what you need", "EDIT: a short call or form."), ("We confirm the plan and price", "EDIT: in writing, before any work."), ("You receive the result", "EDIT: on time, with support after.")]) + "</div>", "dark")
            + stats([("500+", "EDIT: customers served"), ("4.8/5", "EDIT: average rating (real numbers only)"), ("24h", "EDIT: reply time"), ("7 yrs", "EDIT: in business")])
            + sect("Kind words", "What customers say", "EDIT: replace with real reviews.", quotes(), "alt")
            + sect("Pricing", "Simple, clear packages", "EDIT: three packages that cover most customers.", pricing)
            + sect("Questions", "Frequently asked questions", "EDIT: answer the five questions you hear most.", '<div id="faq">' + faq(questions) + "</div>", "alt")
            + cta("Let's talk about your project", "EDIT: Tell us what you need and we will reply within one working day.", "#contact", "Contact us")
            + sect("Contact", "Get your free quote", "We reply within one working day.", '<div id="contact">' + form() + "</div>"))
    return {"index.html": page(f"{BIZ} | EDIT: what you do", "EDIT: 150-character description for Google.", body, nav, "#benefits", cta=("Get a quote", "#contact")), "style.css": css(), "script.js": JS.encode()}


# ------------------------------------------------------------------ 2. five-page business site
def business5() -> dict[str, bytes]:
    d = "EDIT: 150-character description for Google."
    svc = [("Service one", "EDIT: what it is and who it is for.", "&#8377;999"), ("Service two", "EDIT: what it is and who it is for.", "&#8377;1,999"), ("Service three", "EDIT: what it is and who it is for.", "&#8377;2,999")]
    cards = "".join(f'<div class="card reveal"><div class="ico">{ICONS[i]}</div><h3>{n}</h3><p>{t}</p><p style="margin-top:12px"><span class="price" style="font-size:1.4rem">{p}</span></p></div>' for i, (n, t, p) in enumerate(svc))
    side = ('<div class="glass"><h3>Visit us</h3><div class="row"><span>EDIT: Mon to Sat</span><b>9 am to 7 pm</b></div><div class="row"><span>EDIT: Sunday</span><b>Closed</b></div>'
            '<div class="row"><span>Call or WhatsApp</span><span class="tag">EDIT: phone</span></div></div>')
    home = (hero("EDIT: your town · your trade", "EDIT: Your headline: what you do <em>and for whom.</em>", "EDIT: One short paragraph about your business and the main benefit to customers.",
                 ("Contact us", "contact.html"), ("Our services", "services.html"), side, ["EDIT: Local and trusted", "EDIT: Clear prices", "EDIT: Quick replies"])
            + sect("What we do", "Our main services", "EDIT: three services you are known for.", f'<div class="grid">{cards}</div><p style="margin-top:22px"><a class="btn dark" href="services.html">See all services</a></p>')
            + stats([("10+", "EDIT: years of experience"), ("1,000+", "EDIT: happy customers"), ("4.8/5", "EDIT: customer rating"), ("24h", "EDIT: reply time")], "alt")
            + sect("How we work", "Simple and transparent", "EDIT: your real process.", steps([("You tell us", "EDIT"), ("We agree the plan", "EDIT"), ("We deliver", "EDIT")]), "dark")
            + sect("Reviews", "What customers say", "EDIT: replace with real reviews.", quotes())
            + cta("Come and see us", "EDIT: address, opening hours and a friendly invitation.", "contact.html", "Get directions and contact"))
    team = '<div class="grid">' + "".join(f'<div class="card reveal"><div class="avatar" style="width:84px;height:84px;font-size:1.8rem">{c}</div><h3>EDIT: Name</h3><p>EDIT: role and one line about them.</p></div>' for c in "ABC") + "</div>"
    about = (hero("About us", "EDIT: A short story <em>people remember.</em>", "EDIT: Who you are, when you started and what you care about, in three or four sentences.", ("Our services", "services.html"), ("Contact", "contact.html"), single=True)
             + sect("What guides us", "Our values", "EDIT: three things you promise every customer.", '<div class="grid">' + feat("&#129309;", "Honesty", "EDIT") + feat("&#127919;", "Quality", "EDIT") + feat("&#10084;", "Care", "EDIT") + "</div>")
             + sect("The team", "The people behind the work", "EDIT: names, roles and a friendly line each.", team, "alt")
             + sect("Our journey", "How we got here", "EDIT: three milestones.", '<div class="timeline reveal"><div><small>EDIT: 2018</small><h3>Started</h3><p>EDIT</p></div><div><small>EDIT: 2021</small><h3>Grew</h3><p>EDIT</p></div><div><small>EDIT: 2025</small><h3>Today</h3><p>EDIT</p></div></div>')
             + cta())
    packages = '<div class="grid">' + "".join(
        f'<div class="card reveal"><div class="ico">{ICONS[i % 6]}</div><h3>Service {i + 1}</h3><p>EDIT: what is included and who it is for.</p><div class="price" style="margin-top:12px">&#8377;{p}</div><p style="margin-top:12px"><a class="btn dark sm" href="contact.html">Enquire</a></p></div>'
        for i, p in enumerate(["999", "1,499", "1,999", "2,499", "3,999", "4,999"])) + "</div>"
    services = (hero("Services", "EDIT: Everything we offer, <em>with prices.</em>", "EDIT: Clear lists and prices build trust. Say who each service is for.", ("Enquire now", "contact.html"), ("See gallery", "gallery.html"), single=True)
                + sect("Packages", "Choose what suits you", "EDIT: add or delete cards as needed.", packages)
                + sect("Questions", "Before you book", "EDIT", faq([("How do I book?", "EDIT"), ("Do you travel to customers?", "EDIT"), ("How do I pay?", "EDIT")]), "alt")
                + cta())
    photos = '<div class="grid">' + "".join(f'<div class="reveal"><div class="ph">Photo {i}</div><p class="small" style="margin:8px 4px">EDIT: caption</p></div>' for i in range(1, 10)) + "</div>"
    gallery = (hero("Gallery", "EDIT: Our work, <em>in pictures.</em>", "EDIT: Replace each grey box with a photo, for example &lt;img src=&quot;photos/shop1.jpg&quot; alt=&quot;Our shop&quot;&gt;", ("Contact us", "contact.html"), ("Services", "services.html"), single=True)
               + sect("Photos", "A look around", "EDIT: use bright, sharp photos of real work, not stock images.", photos) + cta())
    contact_info = ('<div class="info"><div class="card"><h3>Address</h3><p>EDIT: shop, street, city, pin code</p></div><div class="card"><h3>Phone and WhatsApp</h3><p>EDIT: number</p></div>'
                    '<div class="card"><h3>Opening hours</h3><p>EDIT: Mon to Sat, 9 am to 7 pm</p></div></div>')
    contact = (hero("Contact", "EDIT: We would love <em>to hear from you.</em>", "EDIT: Reply promise, for example: we answer within one working day.", ("WhatsApp us", f"https://wa.me/{PHONE_WA}"), ("Email us", f"mailto:{EMAIL}"), single=True)
               + sect("Get in touch", "Send us a message", "EDIT", '<div class="grid two"><div>' + form() + "</div>" + contact_info + "</div>"
                      + '<h3 style="margin-top:36px">Find us</h3><p class="small">EDIT: open Google Maps, find your shop, choose Share &gt; Embed a map, and paste the iframe here.</p>'))
    return {"index.html": page(f"{BIZ} | Home", d, home, NAV5, "index.html"), "about.html": page(f"About | {BIZ}", d, about, NAV5, "about.html"), "services.html": page(f"Services | {BIZ}", d, services, NAV5, "services.html"),
            "gallery.html": page(f"Gallery | {BIZ}", d, gallery, NAV5, "gallery.html"), "contact.html": page(f"Contact | {BIZ}", d, contact, NAV5, "contact.html"), "style.css": css(), "script.js": JS.encode()}


# ------------------------------------------------------------------ 3. portfolio
def portfolio() -> dict[str, bytes]:
    nav = [("About", "#about"), ("Skills", "#skills"), ("Experience", "#experience"), ("Projects", "#projects"), ("Contact", "#contact")]
    side = ('<div class="glass"><div class="avatar">YN</div><h3>Quick facts</h3><div class="row"><span>Education</span><b>EDIT: PGDM, 2027</b></div><div class="row"><span>Based in</span><b>EDIT: city</b></div>'
            '<div class="row"><span>Open to</span><span class="tag">EDIT: internships</span></div></div>')
    skills = [("Financial analysis", 85), ("Excel and Power BI", 90), ("Valuation basics", 70), ("Presentations", 80)]
    sk = "".join(f'<div class="skill"><span>{n}</span><span>{v}%</span></div><div class="bar"><i style="width:{v}%"></i></div>' for n, v in skills)
    proj = "".join(f'<div class="card reveal"><div class="ph" style="margin-bottom:14px">Project {i} image</div><h3>EDIT: Project title {i}</h3><p>EDIT: the problem, what you built, and the result (for example: cut report time from 2 hours to 10 minutes).</p><div class="tags"><span>Excel</span><span>Power BI</span><span>EDIT</span></div><p style="margin-top:14px"><a href="#">View project &rarr;</a></p></div>' for i in (1, 2, 3))
    about_cards = '<div id="about" class="grid"><div class="card reveal"><h3>EDIT: What I do</h3><p>EDIT</p></div><div class="card reveal"><h3>EDIT: What I enjoy</h3><p>EDIT</p></div><div class="card reveal"><h3>EDIT: What I am looking for</h3><p>EDIT</p></div></div>'
    skill_block = f'<div id="skills" class="grid two"><div class="reveal">{sk}</div><div class="card reveal"><h3>Tools</h3><div class="tags"><span>Excel</span><span>Power BI</span><span>Google Sheets</span><span>PowerPoint</span><span>EDIT</span></div></div></div>'
    timeline = ('<div id="experience" class="timeline reveal"><div><small>EDIT: 2025 to 2027</small><h3>EDIT: PGDM Finance, Your College</h3><p>EDIT: specialisation and highlights.</p></div>'
                '<div><small>EDIT: May to Jul 2025</small><h3>EDIT: Internship, Company</h3><p>EDIT: one line on what you did and the result.</p></div><div><small>EDIT: 2022 to 2025</small><h3>EDIT: B.Com, Your University</h3><p>EDIT</p></div></div>')
    body = (hero("Hello, I am", "EDIT: Your Name, <em>finance and data.</em>", "EDIT: Your role in one sentence, and what you can do for employers or clients. Be specific and use a number if you can.",
                 ("See my work", "#projects"), ("Hire me / contact", "#contact"), side, ["EDIT: PGDM Finance", "EDIT: Excel and Power BI", "EDIT: Available for internships"])
            + sect("About me", "A little about me", "EDIT: 3 to 5 sentences: education, what you enjoy, what you are looking for.", about_cards)
            + sect("Skills", "What I am good at", "EDIT: change the percentages honestly.", skill_block, "alt")
            + sect("Experience", "Education and experience", "EDIT: newest first.", timeline)
            + sect("Projects", "Selected work", "EDIT: three projects with a result for each.", f'<div id="projects" class="grid">{proj}</div>', "alt")
            + sect("Kind words", "Recommendations", "EDIT: from teachers, managers or clients.", quotes(2))
            + cta("Let's work together", "EDIT: I am open to internships and freelance projects. Say hello.", "#contact", "Contact me")
            + sect("Contact", "Get in touch", "EDIT: email, LinkedIn and phone.", '<div id="contact">' + form() + "</div>"))
    return {"index.html": page("Your Name | Portfolio", "EDIT: Finance student and freelancer portfolio.", body, nav, "#about", logo="Your Name", cta=("Hire me", "#contact")), "style.css": css(), "script.js": JS.encode()}


# ------------------------------------------------------------------ 4. coaching centre
def coaching() -> dict[str, bytes]:
    nav = [("Home", "index.html"), ("Courses", "courses.html"), ("Fees", "fees.html"), ("Enquiry", "enquiry.html")]
    d = "EDIT: Coaching centre in your city for your exams."
    courses = [("NEET", "12 months", "Biology, Chemistry, Physics"), ("JEE", "12 months", "Maths, Physics, Chemistry"), ("TNPSC", "6 months", "General studies and aptitude"), ("Spoken English", "3 months", "Speaking, listening, confidence")]
    side = ('<div class="glass"><h3>Next batches</h3>' + "".join(f'<div class="row"><span>{n}</span><span class="tag">EDIT: 1 Dec</span></div>' for n, _, _ in courses)
            + '<p class="small" style="color:rgba(244,237,224,.7);margin:10px 0 0">EDIT: seats are limited, book a free demo class.</p></div>')
    cc = "".join(f'<div class="card reveal"><div class="ico">{ICONS[i]}</div><h3>{n}</h3><p>{t}</p><ul class="list"><li>Duration: {du}</li><li>EDIT: batch timings</li><li>EDIT: seats: 30</li></ul><p style="margin-top:16px"><a class="btn dark sm" href="enquiry.html">Enquire</a></p></div>' for i, (n, du, t) in enumerate(courses))
    teachers = '<div class="grid">' + "".join(f'<div class="card reveal"><div class="avatar" style="width:84px;height:84px;font-size:1.8rem">{c}</div><h3>EDIT: Teacher name</h3><p>EDIT: subject, qualification, experience.</p></div>' for c in "ABC") + "</div>"
    why = '<div class="grid">' + feat("&#128101;", "Small batches", "Individual attention for every student.") + feat("&#128221;", "Weekly tests", "Know exactly where you stand.") + feat("&#128161;", "Doubt clearing", "Extra sessions every week.") + "</div>"
    home = (hero("EDIT: Coaching centre · your city", "EDIT: Coaching that gets <em>real results.</em>", "EDIT: Exams you prepare for, and what makes your classes different: small batches, weekly tests, doubt clearing.",
                 ("Book a free demo class", "enquiry.html"), ("See courses", "courses.html"), side, ["EDIT: Small batches", "EDIT: Weekly tests", "EDIT: Doubt-clearing sessions"])
            + stats([("250+", "EDIT: students trained"), ("92%", "EDIT: pass rate (real numbers only)"), ("15 yrs", "EDIT: teaching experience"), ("30", "EDIT: max students per batch")])
            + sect("Courses", "Programmes we offer", "EDIT: your main courses.", f'<div class="grid">{cc}</div>', "alt")
            + sect("Why us", "What students love", "EDIT", why)
            + sect("Faculty", "Meet your teachers", "EDIT: names, subjects and years of experience.", teachers, "dark")
            + sect("Results", "Student stories", "EDIT: real students, with their permission.", quotes())
            + sect("Questions", "Parents often ask", "EDIT", faq([("Can we attend a demo class?", "EDIT: yes, free, book on the enquiry page."), ("Is there a weekly test?", "EDIT"), ("What are the batch timings?", "EDIT")]), "alt")
            + cta("Book a free demo class", "EDIT: Come and see how we teach before you decide.", "enquiry.html", "Book now"))
    coursepage = (hero("Courses", "EDIT: Choose your <em>programme.</em>", "EDIT: batches, duration and timings.", ("Enquire", "enquiry.html"), ("See fees", "fees.html"), single=True)
                  + sect("All courses", "Batches and timings", "EDIT: keep this up to date.", f'<div class="grid">{cc}</div>') + cta("Not sure which course?", "EDIT: Talk to us and we will guide you.", "enquiry.html", "Ask us"))
    fee_table = ('<table class="fees reveal"><tr><th>Course</th><th>Duration</th><th>Fee</th></tr><tr><td>NEET</td><td>12 months</td><td>&#8377;30,000</td></tr><tr><td>JEE</td><td>12 months</td><td>&#8377;28,000</td></tr>'
                 '<tr><td>TNPSC</td><td>6 months</td><td>&#8377;12,000</td></tr><tr><td>Spoken English</td><td>3 months</td><td>&#8377;6,000</td></tr></table>'
                 '<p class="small" style="margin-top:14px">EDIT: payment options (UPI or instalments) and refund policy.</p>')
    fees = (hero("Fees", "EDIT: Clear fees, <em>no surprises.</em>", "EDIT: Show fees openly: parents trust centres that do. Mention instalments if you offer them.", ("Enquire", "enquiry.html"), ("Courses", "courses.html"), single=True)
            + sect("Fee structure", "What each course costs", "EDIT", fee_table)
            + sect("Questions", "About fees", "EDIT", faq([("Can I pay in instalments?", "EDIT"), ("Is there a sibling or scholarship discount?", "EDIT"), ("What is the refund policy?", "EDIT")]), "alt")
            + cta("Reserve a seat", "EDIT", "enquiry.html", "Enquire now"))
    enq_fields = ('<label>Student name <input name="student" required></label><label>Parent / guardian phone <input name="phone" type="tel" required></label>'
                  '<label>Course <select name="course"><option>NEET</option><option>JEE</option><option>TNPSC</option><option>Spoken English</option></select></label>'
                  '<label>Current class or qualification <input name="class"></label><label>Message <textarea name="message"></textarea></label>')
    enq = (hero("Admission enquiry", "EDIT: Fill the form, <em>we will call you.</em>", "We call within one working day.", ("WhatsApp us", f"https://wa.me/{PHONE_WA}"), ("See courses", "courses.html"), single=True)
           + sect("Enquiry", "Tell us about the student", "EDIT", form(enq_fields, "Submit enquiry")))
    cp = ("Contact", "enquiry.html")
    logo = "Your Coaching Centre"
    return {"index.html": page(f"{BIZ} Coaching Centre | Home", d, home, nav, "index.html", logo=logo, cta=("Free demo", "enquiry.html")), "courses.html": page(f"Courses | {logo}", d, coursepage, nav, "courses.html", logo=logo, cta=cp),
            "fees.html": page(f"Fees | {logo}", d, fees, nav, "fees.html", logo=logo, cta=cp), "enquiry.html": page(f"Admission enquiry | {logo}", d, enq, nav, "enquiry.html", logo=logo, cta=cp), "style.css": css(), "script.js": JS.encode()}


# ------------------------------------------------------------------ 5. restaurant
def restaurant() -> dict[str, bytes]:
    nav = [("Home", "index.html"), ("Menu", "menu.html"), ("Contact", "contact.html")]
    d = "EDIT: Restaurant in your city. Dine-in, takeaway and delivery."
    side = ('<div class="glass"><h3>Open today</h3><div class="row"><span>Lunch</span><b>EDIT: 12 to 3:30 pm</b></div><div class="row"><span>Dinner</span><b>EDIT: 7 to 10:30 pm</b></div>'
            '<div class="row"><span>Order by</span><span class="tag">WhatsApp</span></div></div>')
    dishes = [("Signature dish", 220, "veg"), ("Chef's special", 260, "nonveg"), ("Customer favourite", 180, "veg")]
    fav = "".join(f'<div class="card reveal"><div class="ph" style="margin-bottom:14px">Dish photo</div><h3 class="{k}">{n}</h3><p>EDIT: short, mouth-watering description.</p><div class="price" style="margin-top:10px;font-size:1.5rem">&#8377;{p}</div></div>' for n, p, k in dishes)
    story = '<div class="grid">' + feat("&#127807;", "Fresh ingredients", "EDIT") + feat("&#128293;", "Cooked to order", "EDIT") + feat("&#129309;", "Warm service", "EDIT") + "</div>"
    wa_order = f"https://wa.me/{PHONE_WA}?text=I%20would%20like%20to%20order"
    home = (hero("EDIT: Cuisine · your city", "EDIT: Fresh food, <em>made with love.</em>", "EDIT: What makes you special: family recipes, fresh ingredients, a warm welcome.",
                 ("View menu", "menu.html"), ("Order on WhatsApp", wa_order), side, ["EDIT: Fresh daily", "EDIT: Dine-in and takeaway", "EDIT: Home delivery"])
            + sect("Today's favourites", "Dishes our guests love", "EDIT: your three best sellers, with real photos.", f'<div class="grid">{fav}</div><p style="margin-top:22px"><a class="btn dark" href="menu.html">See the full menu</a></p>')
            + sect("Our story", "Cooked the way it should be", "EDIT: two or three sentences about your kitchen, your chef or your family recipes.", story, "alt")
            + stats([("12+", "EDIT: years serving"), ("4.7/5", "EDIT: guest rating"), ("60+", "EDIT: dishes on the menu")])
            + sect("Reviews", "What guests say", "EDIT: real reviews only.", quotes(), "dark")
            + cta("Hungry yet?", "EDIT: Order on WhatsApp or book a table for tonight.", "contact.html", "Book a table"))
    cats = {"Starters": [("Starter one", "EDIT: description", 120, "veg"), ("Starter two", "EDIT: description", 140, "nonveg"), ("Starter three", "EDIT: description", 160, "veg")],
            "Main course": [("Main one", "EDIT: description", 220, "veg"), ("Main two", "EDIT: description", 260, "nonveg"), ("Main three", "EDIT: description", 240, "nonveg")],
            "Desserts and drinks": [("Dessert one", "EDIT: description", 90, "veg"), ("Drink one", "EDIT: description", 70, "veg"), ("Drink two", "EDIT: description", 60, "veg")]}
    chips = '<div class="chips">' + "".join(f'<a href="#{k.split()[0].lower()}">{k}</a>' for k in cats) + "</div>"
    tbl = "".join(f"<h2 class='title' id='{k.split()[0].lower()}' style='margin:30px 0 12px'>{k}</h2><table class='menu reveal'>"
                   + "".join(f"<tr><td><b class='{kind}'>{n}</b><small>{ds}</small></td><td>&#8377;{p}</td></tr>" for n, ds, p, kind in v) + "</table>" for k, v in cats.items())
    menu = (hero("Menu", "EDIT: Something for <em>everyone.</em>", "EDIT: Replace the items and prices. Green dot = vegetarian, coral dot = non-vegetarian.", ("Order on WhatsApp", wa_order), ("Book a table", "contact.html"), single=True)
            + f'<section><div class="wrap">{chips}{tbl}</div></section>' + cta("Ready to order?", "EDIT: Message us your order and we will confirm the time.", wa_order, "Order now"))
    book = ('<label>Name <input name="name" required></label><label>Phone <input name="phone" type="tel" required></label><label>Date <input name="date" type="date" required></label>'
            '<label>Guests <select name="guests"><option>1 to 2</option><option>3 to 4</option><option>5 to 8</option><option>9+</option></select></label><label>Notes <textarea name="notes"></textarea></label>')
    info = ('<div class="info"><div class="card"><h3>Address</h3><p>EDIT: street, city, landmark</p></div><div class="card"><h3>Opening hours</h3><p>EDIT: Mon to Sun, 12 to 3:30 pm and 7 to 10:30 pm</p></div>'
            '<div class="card"><h3>Order and delivery</h3><p>EDIT: phone or WhatsApp</p></div></div>')
    contact = (hero("Find us", "EDIT: Come hungry, <em>leave happy.</em>", "EDIT: full address, phone and landmark.", ("WhatsApp us", f"https://wa.me/{PHONE_WA}"), ("Email", f"mailto:{EMAIL}"), single=True)
               + sect("Reserve", "Book a table", "EDIT", '<div class="grid two"><div>' + form(book, "Request a table") + "</div>" + info + "</div>"
                      + '<p class="small" style="margin-top:24px">EDIT: Google Maps: Share &gt; Embed a map, then paste the iframe here.</p>'))
    logo = "Your Restaurant"
    return {"index.html": page("Your Restaurant | Home", d, home, nav, "index.html", logo=logo, cta=("Book a table", "contact.html")), "menu.html": page("Menu | Your Restaurant", d, menu, nav, "menu.html", logo=logo, cta=("Book a table", "contact.html")),
            "contact.html": page("Contact | Your Restaurant", d, contact, nav, "contact.html", logo=logo, cta=("Order", wa_order)), "style.css": css(), "script.js": JS.encode()}


# ------------------------------------------------------------------ add-on packs (not full sites)
def refresh_pack() -> dict[str, bytes]:
    refresh = """/* refresh.css: drop-in visual refresh for an existing website.
   Add AFTER your current stylesheet:  <link rel="stylesheet" href="refresh.css">  Then adjust the variables. */
:root { --brand: #FF6B5B; --navy: #14213D; --cream: #F4EDE0; --text: #1B2540; --muted: #5B6477; --radius: 14px; }
html { font-size: 17px; }
body { font-family: "Inter", system-ui, -apple-system, "Segoe UI", Roboto, sans-serif !important; color: var(--text); line-height: 1.65; background: #FBF8F2; }
h1, h2, h3 { line-height: 1.15; letter-spacing: -0.02em; color: var(--navy); }
h1 { font-size: clamp(2rem, 5vw, 3.2rem); font-weight: 600; }
p { max-width: 70ch; }
a { color: #D9452F; }
img { max-width: 100%; height: auto; border-radius: var(--radius); }
button, .btn, input[type=submit] { background: var(--brand); color: var(--navy); border: 0; border-radius: 999px; padding: 12px 24px; font-weight: 700; cursor: pointer; }
input, select, textarea { border: 1px solid rgba(20,33,61,.22); border-radius: 12px; padding: 12px; font: inherit; max-width: 100%; }
section, .section { padding-block: clamp(36px, 6vw, 76px); }
.card, .box { border-radius: var(--radius); box-shadow: 0 14px 30px -22px rgba(20,33,61,.45); background: #fff; }
"""
    return {"refresh.css": refresh.encode()}


def mobile_fix_pack() -> dict[str, bytes]:
    fixes = """/* responsive-fixes.css: add AFTER your main stylesheet. Fixes the most common mobile problems. */
/* 1. Nothing wider than the screen */
html, body { max-width: 100%; overflow-x: hidden; }
img, video, iframe, table { max-width: 100%; height: auto; }
/* 2. Readable text without pinch-zoom */
body { font-size: 16px; line-height: 1.6; }
/* 3. Tap targets at least 44px */
a, button, input, select, textarea { min-height: 44px; }
/* 4. Columns stack on phones */
@media (max-width: 720px) {
  .row, .columns, .flex, [class*="col-"] { display: block !important; width: 100% !important; float: none !important; }
  table { display: block; overflow-x: auto; }
  h1 { font-size: 1.9rem; } h2 { font-size: 1.5rem; }
  .container, .wrap { padding-left: 16px; padding-right: 16px; }
  nav ul { flex-direction: column; }
}
/* 5. Forms fill the width */
input, select, textarea { width: 100%; box-sizing: border-box; }
"""
    snippet = """<!-- Put this inside <head> of EVERY page. Without it phones show a tiny desktop page. -->
<meta name="viewport" content="width=device-width, initial-scale=1">
"""
    return {"responsive-fixes.css": fixes.encode(), "viewport-snippet.html": snippet.encode()}


def seo_snippets() -> dict[str, bytes]:
    head = """<!-- Paste inside <head> on each page and edit the text. -->
<title>Main keyword | Your Business Name (max 60 characters)</title>
<meta name="description" content="One clear sentence with your main keyword and a reason to click (max 155 characters).">
<link rel="canonical" href="https://www.yourwebsite.com/this-page">
<meta property="og:title" content="Main keyword | Your Business Name">
<meta property="og:description" content="Same description as above.">
<meta property="og:image" content="https://www.yourwebsite.com/images/share.jpg">
<meta name="viewport" content="width=device-width, initial-scale=1">
<script type="application/ld+json">
{ "@context": "https://schema.org", "@type": "LocalBusiness", "name": "Your Business Name", "url": "https://www.yourwebsite.com",
  "telephone": "+91-9999999999", "address": { "@type": "PostalAddress", "streetAddress": "Street", "addressLocality": "Madurai", "addressRegion": "Tamil Nadu", "postalCode": "625001", "addressCountry": "IN" },
  "openingHours": "Mo-Su 09:00-20:00" }
</script>
"""
    robots = "User-agent: *\nAllow: /\nSitemap: https://www.yourwebsite.com/sitemap.xml\n"
    sitemap = """<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
  <url><loc>https://www.yourwebsite.com/</loc></url>
  <url><loc>https://www.yourwebsite.com/services</loc></url>
  <url><loc>https://www.yourwebsite.com/contact</loc></url>
</urlset>
"""
    return {"head-snippet.html": head.encode(), "robots.txt": robots.encode(), "sitemap.xml": sitemap.encode()}
