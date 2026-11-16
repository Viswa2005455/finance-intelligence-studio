"""Static website templates (plain HTML + CSS, no build step). Open index.html to preview; edit the text; upload to any host."""

from __future__ import annotations

CSS = """/* EDIT: change these colours to match your brand */
:root { --brand: %(brand)s; --brand-dark: %(dark)s; --soft: %(soft)s; --text: #1f2933; --muted: #5b6770; --bg: #ffffff; }
* { box-sizing: border-box; }
html { scroll-behavior: smooth; }
body { margin: 0; font-family: system-ui, -apple-system, "Segoe UI", Roboto, sans-serif; color: var(--text); background: var(--bg); line-height: 1.6; }
img { max-width: 100%%; height: auto; display: block; }
a { color: var(--brand-dark); }
.wrap { width: min(1100px, 92%%); margin-inline: auto; }
header.site { position: sticky; top: 0; background: #fff; border-bottom: 1px solid #e5e7eb; z-index: 10; }
header.site .wrap { display: flex; align-items: center; justify-content: space-between; padding: 14px 0; gap: 16px; }
.logo { font-weight: 800; font-size: 1.2rem; color: var(--brand-dark); text-decoration: none; }
nav ul { display: flex; gap: 22px; list-style: none; margin: 0; padding: 0; }
nav a { text-decoration: none; color: var(--text); font-weight: 600; }
nav a:hover, nav a.active { color: var(--brand); }
.menu-btn { display: none; background: none; border: 1px solid #cbd5e1; border-radius: 8px; padding: 8px 12px; font-size: 1rem; cursor: pointer; }
.btn { display: inline-block; background: var(--brand); color: #fff; padding: 12px 22px; border-radius: 10px; font-weight: 700; text-decoration: none; border: 0; cursor: pointer; font-size: 1rem; }
.btn:hover { background: var(--brand-dark); }
.btn.alt { background: #fff; color: var(--brand-dark); border: 2px solid var(--brand); }
.hero { background: radial-gradient(700px 300px at 90%% 0%%, var(--soft), transparent 70%%), linear-gradient(135deg, var(--soft), #fff); padding: 84px 0; }
.hero h1 { font-size: clamp(2rem, 5vw, 3.2rem); line-height: 1.15; margin: 0 0 16px; color: var(--brand-dark); }
.hero p { font-size: 1.15rem; color: var(--muted); max-width: 640px; }
.hero .actions { display: flex; flex-wrap: wrap; gap: 12px; margin-top: 24px; }
section { padding: 56px 0; }
section.alt { background: var(--soft); }
h2 { font-size: 1.8rem; margin: 0 0 8px; color: var(--brand-dark); }
.lead { color: var(--muted); margin: 0 0 28px; }
.grid { display: grid; gap: 20px; grid-template-columns: repeat(auto-fit, minmax(240px, 1fr)); }
.card { background: #fff; border: 1px solid #e5e7eb; border-radius: 16px; padding: 24px; box-shadow: 0 6px 18px -12px rgba(15, 61, 46, .35); transition: transform .15s ease, box-shadow .15s ease; }
.card:hover { transform: translateY(-3px); box-shadow: 0 14px 28px -14px rgba(15, 61, 46, .45); }
.card .ico { display: grid; place-items: center; width: 46px; height: 46px; border-radius: 12px; background: var(--soft); font-size: 1.4rem; margin-bottom: 12px; }
.band { background: linear-gradient(135deg, var(--brand-dark), var(--brand)); color: #fff; padding: 52px 0; text-align: center; }
.band h2 { color: #fff; }
.band p { color: rgba(255,255,255,.85); margin: 6px 0 20px; }
.band .btn { background: #fff; color: var(--brand-dark); }
.stats { display: grid; grid-template-columns: repeat(auto-fit, minmax(160px, 1fr)); gap: 16px; text-align: center; }
.stats b { display: block; font-size: 2.2rem; color: var(--brand-dark); }
.stats span { color: var(--muted); }
.card h3 { margin: 0 0 6px; }
.price { font-size: 1.6rem; font-weight: 800; color: var(--brand-dark); }
.ph { background: linear-gradient(135deg, var(--soft), #e2e8f0); border-radius: 14px; aspect-ratio: 4/3; display: grid; place-items: center; color: var(--muted); font-weight: 600; text-align: center; padding: 12px; }
form { display: grid; gap: 14px; max-width: 520px; }
label { font-weight: 600; display: grid; gap: 6px; }
input, select, textarea { font: inherit; padding: 12px; border: 1px solid #cbd5e1; border-radius: 10px; width: 100%%; }
textarea { min-height: 120px; }
table.menu { width: 100%%; border-collapse: collapse; }
table.menu td { padding: 10px 0; border-bottom: 1px dashed #cbd5e1; }
table.menu td:last-child { text-align: right; font-weight: 700; white-space: nowrap; }
footer.site { background: var(--brand-dark); color: #e5f2ec; padding: 36px 0; }
footer.site a { color: #fff; }
.small { font-size: .9rem; color: var(--muted); }
.wa { position: fixed; right: 16px; bottom: 16px; background: #25d366; color: #fff; padding: 12px 18px; border-radius: 999px; font-weight: 700; text-decoration: none; box-shadow: 0 4px 14px rgba(0,0,0,.2); z-index: 20; }
@media (max-width: 720px) {
  .menu-btn { display: block; }
  nav ul { display: none; position: absolute; top: 100%%; left: 0; right: 0; background: #fff; flex-direction: column; gap: 0; border-bottom: 1px solid #e5e7eb; }
  nav ul.open { display: flex; }
  nav li a { display: block; padding: 14px 4%%; border-top: 1px solid #f1f5f9; }
  .hero { padding: 44px 0; }
  section { padding: 40px 0; }
}
"""

JS = """// Opens and closes the mobile menu
document.addEventListener('DOMContentLoaded', function () {
  var b = document.querySelector('.menu-btn'), u = document.querySelector('nav ul');
  if (b && u) b.addEventListener('click', function () { u.classList.toggle('open'); });
});
"""

# EDIT these once and search-replace across files: business name, phone, email, city.
BIZ = "Your Business Name"
PHONE_WA = "919999999999"
EMAIL = "hello@yourbusiness.com"


def css(brand="#0f8a6e", dark="#0f3d2e", soft="#e8f3ec") -> bytes:
    return (CSS % {"brand": brand, "dark": dark, "soft": soft}).encode()


def page(title: str, desc: str, body: str, nav: list[tuple[str, str]], active: str, logo: str = BIZ) -> bytes:
    items = "".join(f'<li><a href="{h}"{" class=\"active\"" if h == active else ""}>{t}</a></li>' for t, h in nav)
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title>
<meta name="description" content="{desc}">
<link rel="stylesheet" href="style.css">
<script src="script.js" defer></script>
</head>
<body>
<header class="site"><div class="wrap">
  <a class="logo" href="index.html">{logo}</a>
  <button class="menu-btn" aria-label="Menu">Menu</button>
  <nav><ul>{items}</ul></nav>
</div></header>
{body}
<footer class="site"><div class="wrap">
  <strong>{logo}</strong><br>
  <span>EDIT: address line, city · <a href="mailto:{EMAIL}">{EMAIL}</a> · <a href="https://wa.me/{PHONE_WA}">WhatsApp</a></span>
  <p class="small" style="color:#bfe0d2">&copy; <span id="yr">2026</span> {logo}. All rights reserved.</p>
</div></footer>
<a class="wa" href="https://wa.me/{PHONE_WA}?text=Hello%2C%20I%20have%20an%20enquiry">Chat on WhatsApp</a>
</body>
</html>
""".encode()


def cta(heading="Ready to get started?", text="EDIT: one friendly sentence inviting the visitor to contact you.", href="contact.html", label="Contact us") -> str:
    return f'<section class="band"><div class="wrap"><h2>{heading}</h2><p>{text}</p><a class="btn" href="{href}">{label}</a></div></section>'


def contact_form(action_note=True) -> str:
    return f"""<form action="https://formspree.io/f/YOUR_FORM_ID" method="post">
  <label>Your name <input name="name" required></label>
  <label>Phone <input name="phone" type="tel" required></label>
  <label>Email <input name="email" type="email"></label>
  <label>Message <textarea name="message" required></textarea></label>
  <button class="btn" type="submit">Send enquiry</button>
  {'<p class="small">EDIT: create a free form at formspree.io (or use a Google Form) and paste its link in the form action above. Until then, visitors can use the WhatsApp button.</p>' if action_note else ''}
</form>"""


NAV5 = [("Home", "index.html"), ("About", "about.html"), ("Services", "services.html"), ("Gallery", "gallery.html"), ("Contact", "contact.html")]


def landing() -> dict[str, bytes]:
    nav = [("Benefits", "#benefits"), ("Pricing", "#pricing"), ("Contact", "#contact")]
    body = """
<section class="hero"><div class="wrap">
  <h1>EDIT: One clear promise in one line</h1>
  <p>EDIT: Explain in two sentences who this is for and the result they get. Keep it simple.</p>
  <div class="actions"><a class="btn" href="#contact">Get a free quote</a><a class="btn alt" href="#benefits">See how it works</a></div>
</div></section>
<section id="benefits"><div class="wrap">
  <h2>Why choose us</h2><p class="lead">EDIT: three reasons customers pick you.</p>
  <div class="grid">
    <div class="card"><div class="ico">&#9889;</div><h3>Fast</h3><p>EDIT: delivery time or response time.</p></div>
    <div class="card"><div class="ico">&#128176;</div><h3>Fair prices</h3><p>EDIT: clear prices, no surprises.</p></div>
    <div class="card"><div class="ico">&#11088;</div><h3>Trusted</h3><p>EDIT: years of experience, customers served, reviews.</p></div>
  </div>
</div></section>
<section><div class="wrap"><div class="stats"><div><b>500+</b><span>EDIT: customers served</span></div><div><b>4.8/5</b><span>EDIT: average rating (use real numbers only)</span></div><div><b>24h</b><span>EDIT: reply time</span></div></div></div></section>
<section class="alt"><div class="wrap">
  <h2>What customers say</h2><p class="lead">EDIT: replace with real reviews (with permission).</p>
  <div class="grid">
    <div class="card"><p>"Great service and on time."</p><strong>Customer name</strong></div>
    <div class="card"><p>"Very helpful and easy to work with."</p><strong>Customer name</strong></div>
  </div>
</div></section>
<section id="pricing"><div class="wrap">
  <h2>Pricing</h2><p class="lead">EDIT: three simple packages.</p>
  <div class="grid">
    <div class="card"><h3>Basic</h3><div class="price">&#8377;999</div><p>EDIT: what is included.</p></div>
    <div class="card"><h3>Standard</h3><div class="price">&#8377;1,999</div><p>EDIT: what is included.</p></div>
    <div class="card"><h3>Premium</h3><div class="price">&#8377;3,999</div><p>EDIT: what is included.</p></div>
  </div>
</div></section>
<section class="alt" id="contact"><div class="wrap">
  <h2>Contact us</h2><p class="lead">We reply within one working day.</p>
""" + contact_form() + "\n</div></section>"
    return {"index.html": page(f"{BIZ} | EDIT: what you do", "EDIT: 150-character description for Google.", body, nav, "#contact"), "style.css": css(), "script.js": JS.encode()}


def business5() -> dict[str, bytes]:
    d = "EDIT: 150-character description for Google."
    home = """
<section class="hero"><div class="wrap">
  <h1>EDIT: Your headline: what you do and for whom</h1>
  <p>EDIT: One short paragraph about your business and the main benefit to customers.</p>
  <div class="actions"><a class="btn" href="contact.html">Contact us</a><a class="btn alt" href="services.html">Our services</a></div>
</div></section>
<section><div class="wrap"><h2>What we do</h2><p class="lead">EDIT: three main services.</p>
  <div class="grid"><div class="card"><h3>Service one</h3><p>Short description.</p></div><div class="card"><h3>Service two</h3><p>Short description.</p></div><div class="card"><h3>Service three</h3><p>Short description.</p></div></div>
</div></section>
<section class="alt"><div class="wrap"><h2>Visit or call us</h2><p>EDIT: address, opening hours and phone number.</p><a class="btn" href="contact.html">Get directions and contact</a></div></section>""" + cta()
    about = """
<section class="hero"><div class="wrap"><h1>About us</h1><p>EDIT: Your story in 3 to 4 sentences: who you are, when you started, what you care about.</p></div></section>
<section><div class="wrap"><div class="grid"><div class="card"><h3>Our mission</h3><p>EDIT</p></div><div class="card"><h3>Our values</h3><p>EDIT</p></div><div class="card"><h3>Our team</h3><p>EDIT: names and roles.</p></div></div></div></section>"""
    services = """
<section class="hero"><div class="wrap"><h1>Our services</h1><p>EDIT: clear list with prices where possible.</p></div></section>
<section><div class="wrap"><div class="grid">""" + "".join(f'<div class="card"><h3>Service {i}</h3><p>EDIT: what is included and who it is for.</p><div class="price">&#8377;{p}</div><a class="btn" href="contact.html">Enquire</a></div>' for i, p in ((1, "999"), (2, "1,999"), (3, "2,999"), (4, "4,999"))) + "</div></div></section>"
    gallery = """
<section class="hero"><div class="wrap"><h1>Gallery</h1><p>EDIT: add your photos. Replace each grey box with an image tag, for example &lt;img src="photos/shop1.jpg" alt="Our shop"&gt;</p></div></section>
<section><div class="wrap"><div class="grid">""" + '<div class="ph">Photo here</div>' * 6 + "</div></div></section>"
    contact = """
<section class="hero"><div class="wrap"><h1>Contact us</h1><p>EDIT: address, phone, email and opening hours.</p></div></section>
<section><div class="wrap">""" + contact_form() + """
  <h2 style="margin-top:36px">Find us</h2><p class="small">EDIT: open Google Maps, find your shop, choose Share &gt; Embed a map, and paste the iframe here.</p>
</div></section>"""
    return {"index.html": page(f"{BIZ} | Home", d, home, NAV5, "index.html"), "about.html": page(f"About | {BIZ}", d, about, NAV5, "about.html"),
            "services.html": page(f"Services | {BIZ}", d, services, NAV5, "services.html"), "gallery.html": page(f"Gallery | {BIZ}", d, gallery, NAV5, "gallery.html"),
            "contact.html": page(f"Contact | {BIZ}", d, contact, NAV5, "contact.html"), "style.css": css(), "script.js": JS.encode()}


def portfolio() -> dict[str, bytes]:
    nav = [("About", "#about"), ("Skills", "#skills"), ("Projects", "#projects"), ("Contact", "#contact")]
    body = """
<section class="hero"><div class="wrap">
  <p class="small">Hello, I am</p>
  <h1>EDIT: Your Name</h1>
  <p>EDIT: Your role (for example: Finance student and Excel/Power BI freelancer). One sentence on what you can do for employers or clients.</p>
  <div class="actions"><a class="btn" href="#projects">See my work</a><a class="btn alt" href="#contact">Hire me / contact</a></div>
</div></section>
<section id="about"><div class="wrap"><h2>About me</h2><p>EDIT: 3 to 5 sentences: education, what you enjoy, what you are looking for.</p></div></section>
<section class="alt" id="skills"><div class="wrap"><h2>Skills</h2>
  <div class="grid"><div class="card"><h3>Finance</h3><p>Financial statements, ratio analysis, budgeting, valuation basics.</p></div><div class="card"><h3>Tools</h3><p>Excel, Power BI, Google Sheets, PowerPoint.</p></div><div class="card"><h3>Soft skills</h3><p>Communication, teamwork, attention to detail.</p></div></div></div></section>
<section id="projects"><div class="wrap"><h2>Projects</h2><p class="lead">EDIT: 3 projects. For each: the problem, what you did, the result, and a link.</p>
  <div class="grid">""" + "".join(f'<div class="card"><div class="ph" style="margin-bottom:12px">Project {i} image</div><h3>Project title {i}</h3><p>EDIT: what you built and the result (for example: cut report time from 2 hours to 10 minutes).</p><a href="#">View project</a></div>' for i in (1, 2, 3)) + """</div></div></section>
<section class="alt"><div class="wrap"><h2>Education and experience</h2>
  <div class="card"><strong>EDIT: PGDM, Your College (2025 to 2027)</strong><p>Specialisation and highlights.</p></div><div style="height:12px"></div>
  <div class="card"><strong>EDIT: Internship / project, Company (months)</strong><p>One line on what you did.</p></div></div></section>
<section id="contact"><div class="wrap"><h2>Get in touch</h2><p class="lead">EDIT: email, LinkedIn and phone.</p>""" + contact_form() + "</div></section>"
    return {"index.html": page("Your Name | Portfolio", "EDIT: Finance student and freelancer portfolio.", body, nav, "#about", logo="Your Name"), "style.css": css("#2563eb", "#1e3a8a", "#eef4ff"), "script.js": JS.encode()}


def coaching() -> dict[str, bytes]:
    nav = [("Home", "index.html"), ("Courses", "courses.html"), ("Fees", "fees.html"), ("Enquiry", "enquiry.html")]
    d = "EDIT: Coaching centre in your city for your exams."
    home = """
<section class="hero"><div class="wrap"><h1>EDIT: Coaching that gets results</h1><p>EDIT: Exams you prepare for, your city, and what makes your classes different (small batches, weekly tests, doubt clearing).</p>
  <div class="actions"><a class="btn" href="enquiry.html">Book a free demo class</a><a class="btn alt" href="courses.html">See courses</a></div></div></section>
<section><div class="wrap"><h2>Our results</h2><p class="lead">EDIT: real numbers only.</p>
  <div class="grid"><div class="card"><div class="price">250+</div><p>Students trained</p></div><div class="card"><div class="price">92%</div><p>Pass rate</p></div><div class="card"><div class="price">15 yrs</div><p>Teaching experience</p></div></div></div></section>
<section class="alt"><div class="wrap"><h2>Why students join us</h2>
  <div class="grid"><div class="card"><h3>Small batches</h3><p>Individual attention.</p></div><div class="card"><h3>Weekly tests</h3><p>Know where you stand.</p></div><div class="card"><h3>Doubt clearing</h3><p>Extra sessions every week.</p></div></div></div></section>"""
    courses = """
<section class="hero"><div class="wrap"><h1>Courses</h1><p>EDIT: batches, duration and timings.</p></div></section>
<section><div class="wrap"><div class="grid">""" + "".join(f'<div class="card"><h3>{n}</h3><p>Duration: {du}<br>Timings: EDIT<br>Seats: 30</p><a class="btn" href="enquiry.html">Enquire</a></div>' for n, du in (("Course one (e.g. NEET)", "12 months"), ("Course two (e.g. JEE)", "12 months"), ("Course three (e.g. TNPSC)", "6 months"), ("Spoken English", "3 months"))) + "</div></div></section>"
    fees = """
<section class="hero"><div class="wrap"><h1>Fees</h1><p>EDIT: clear fees build trust. Mention instalments if you offer them.</p></div></section>
<section><div class="wrap"><table class="menu"><tr><td>Course one</td><td>&#8377;30,000 / year</td></tr><tr><td>Course two</td><td>&#8377;28,000 / year</td></tr><tr><td>Course three</td><td>&#8377;12,000 / 6 months</td></tr><tr><td>Spoken English</td><td>&#8377;6,000 / 3 months</td></tr></table>
  <p class="small">EDIT: payment options (UPI / instalments) and refund policy.</p></div></section>"""
    enq = """
<section class="hero"><div class="wrap"><h1>Admission enquiry</h1><p>Fill the form and we will call you within one working day.</p></div></section>
<section><div class="wrap"><form action="https://formspree.io/f/YOUR_FORM_ID" method="post">
  <label>Student name <input name="student" required></label>
  <label>Parent / guardian phone <input name="phone" type="tel" required></label>
  <label>Course <select name="course"><option>Course one</option><option>Course two</option><option>Course three</option><option>Spoken English</option></select></label>
  <label>Current class / qualification <input name="class"></label>
  <label>Message <textarea name="message"></textarea></label>
  <button class="btn" type="submit">Submit enquiry</button>
  <p class="small">EDIT: create a free form at formspree.io (or Google Form) and paste its link in the form action.</p></form></div></section>"""
    return {"index.html": page(f"{BIZ} Coaching Centre | Home", d, home, nav, "index.html", logo="Your Coaching Centre"), "courses.html": page("Courses | Your Coaching Centre", d, courses, nav, "courses.html", logo="Your Coaching Centre"),
            "fees.html": page("Fees | Your Coaching Centre", d, fees, nav, "fees.html", logo="Your Coaching Centre"), "enquiry.html": page("Admission enquiry | Your Coaching Centre", d, enq, nav, "enquiry.html", logo="Your Coaching Centre"),
            "style.css": css("#7c3aed", "#4c1d95", "#f3edff"), "script.js": JS.encode()}


def restaurant() -> dict[str, bytes]:
    nav = [("Home", "index.html"), ("Menu", "menu.html"), ("Contact", "contact.html")]
    d = "EDIT: Restaurant in your city. Dine-in, takeaway and delivery."
    home = f"""
<section class="hero"><div class="wrap"><h1>EDIT: Fresh food, made with love</h1><p>EDIT: Cuisine, location, and what makes you special.</p>
  <div class="actions"><a class="btn" href="menu.html">View menu</a><a class="btn alt" href="https://wa.me/{PHONE_WA}?text=I%20would%20like%20to%20order">Order on WhatsApp</a></div></div></section>
<section><div class="wrap"><h2>Today's favourites</h2><div class="grid">""" + "".join(f'<div class="card"><div class="ph" style="margin-bottom:12px">Dish photo</div><h3>{n}</h3><p>EDIT: short description.</p><div class="price">&#8377;{p}</div></div>' for n, p in (("Signature dish", 220), ("Chef's special", 260), ("Customer favourite", 180))) + """</div></div></section>
<section class="alt"><div class="wrap"><h2>Opening hours</h2><p>EDIT: Mon-Sun, 11:00 am to 10:30 pm.</p></div></section>"""
    sections = {"Starters": [("Starter one", "EDIT: description", 120), ("Starter two", "EDIT: description", 140), ("Starter three", "EDIT: description", 160)],
                "Main course": [("Main one", "EDIT: description", 220), ("Main two", "EDIT: description", 260), ("Main three", "EDIT: description", 240)],
                "Desserts and drinks": [("Dessert one", "EDIT: description", 90), ("Drink one", "EDIT: description", 70), ("Drink two", "EDIT: description", 60)]}
    menu = '<section class="hero"><div class="wrap"><h1>Menu</h1><p>EDIT: Replace the items and prices. Add or delete rows as needed.</p></div></section><section><div class="wrap">'
    for h, items in sections.items():
        menu += f"<h2 style='margin-top:24px'>{h}</h2><table class='menu'>" + "".join(f"<tr><td><strong>{n}</strong><br><span class='small'>{ds}</span></td><td>&#8377;{p}</td></tr>" for n, ds, p in items) + "</table>"
    menu += "</div></section>"
    contact = f"""
<section class="hero"><div class="wrap"><h1>Find us</h1><p>EDIT: full address, phone and landmark.</p></div></section>
<section><div class="wrap"><div class="grid"><div class="card"><h3>Order and reservations</h3><p>Call or WhatsApp: EDIT phone</p><a class="btn" href="https://wa.me/{PHONE_WA}">WhatsApp us</a></div>
  <div class="card"><h3>Hours</h3><p>EDIT: Mon-Sun, 11:00 am to 10:30 pm</p></div></div>
  <p class="small" style="margin-top:20px">EDIT: Google Maps: Share &gt; Embed a map, then paste the iframe here.</p></div></section>"""
    return {"index.html": page("Your Restaurant | Home", d, home, nav, "index.html", logo="Your Restaurant"), "menu.html": page("Menu | Your Restaurant", d, menu, nav, "menu.html", logo="Your Restaurant"),
            "contact.html": page("Contact | Your Restaurant", d, contact, nav, "contact.html", logo="Your Restaurant"), "style.css": css("#d9480f", "#7c2d12", "#fff1e8"), "script.js": JS.encode()}


# ---- add-on packs (not full sites)
def refresh_pack() -> dict[str, bytes]:
    refresh = """/* refresh.css: drop-in visual refresh for an existing website.
   Add AFTER your current stylesheet:  <link rel="stylesheet" href="refresh.css">  Then adjust the variables. */
:root { --brand: #0f8a6e; --text: #1f2933; --muted: #5b6770; --radius: 12px; }
html { font-size: 17px; }
body { font-family: system-ui, -apple-system, "Segoe UI", Roboto, sans-serif !important; color: var(--text); line-height: 1.65; }
h1, h2, h3 { line-height: 1.2; letter-spacing: -0.01em; }
h1 { font-size: clamp(2rem, 5vw, 3rem); }
p { max-width: 70ch; }
a { color: var(--brand); }
img { max-width: 100%; height: auto; border-radius: var(--radius); }
button, .btn, input[type=submit] { background: var(--brand); color: #fff; border: 0; border-radius: var(--radius); padding: 12px 22px; font-weight: 700; cursor: pointer; }
input, select, textarea { border: 1px solid #cbd5e1; border-radius: 10px; padding: 12px; font: inherit; max-width: 100%; }
section, .section { padding-block: clamp(32px, 6vw, 72px); }
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
