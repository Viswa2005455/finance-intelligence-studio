"""Builds all 50 ready-made kits into app/payments/kits/<slug>.zip.

Run from backend/:   uv run --with python-pptx python kits_src/build.py
Needs openpyxl and python-docx (already installed); python-pptx is only used here, never at runtime.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

import doc_kits as dk  # noqa: E402
import web_kits as wk  # noqa: E402
import xlsx_core as xc  # noqa: E402
import xlsx_more as xm  # noqa: E402
from lib import howto, pack, wb_bytes  # noqa: E402

OUT = Path(__file__).resolve().parent.parent / "app" / "payments" / "kits"
CAT = json.loads((OUT.parent / "service_catalog.json").read_text(encoding="utf-8"))


class XB:
    """An Excel kit file: call it for the example version, or with blank=True for the empty version."""

    def __init__(self, fn, *a, **k):
        self.fn, self.a, self.k = fn, a, k

    def __call__(self, blank: bool = False) -> bytes:
        return wb_bytes(self.fn(*self.a, **self.k), blank=blank)


def X(fn, *a, **k):
    return XB(fn, *a, **k)


# Kits that also get an empty copy of the workbook (checked for error cells in Excel).
BLANK_FOR = {
    "custom-excel-dashboard", "personal-budget-tracker-customised", "small-business-profit-and-loss-dashboard-customised", "budget-vs-actual-variance-report",
    "cash-flow-forecast-model-12-months", "sales-tracking-dashboard", "inventory-stock-tracker", "expense-tracker-for-shops", "gst-invoice-and-register-template",
    "excel-data-cleaning-and-formatting", "monthly-management-report-mis", "coaching-centre-fee-and-admission-dashboard", "restaurant-revenue-and-expense-dashboard",
    "retail-shop-profit-dashboard", "budget-planning-model-for-startups", "monthly-dashboard-update-recurring", "website-maintenance-monthly", "basic-on-page-seo-setup",
    "automated-weekly-sales-report", "google-sheets-lead-enquiry-tracker", "google-form-to-sheet-to-email-automation", "invoice-generator-in-sheets-excel",
    "student-attendance-and-fee-tracker", "appointment-booking-tracker", "data-entry-system-with-dropdowns-and-validation", "competitor-analysis",
    "social-media-content-calendar-1-month",
}


def blank_name(name: str) -> str:
    return name.replace(".xlsx", "-BLANK.xlsx")


def B(fn):
    return fn


def site(fn, folder="website"):
    return lambda: {f"{folder}/{n}": b for n, b in fn().items()}


# slug: (promise, [(filename, builder, what it is)], tip)
def kits():
    xl = "Excel workbook"
    return {
        "custom-excel-dashboard": ("A one-screen Excel dashboard that updates when you add data.", [("Custom-Excel-Dashboard.xlsx", X(xm.custom_dashboard), f"{xl}: Data sheet plus an automatic Summary dashboard with charts")], "Keep the Date, Category and Amount columns; rename categories to match your business."),
        "personal-budget-tracker-customised": ("A personal budget tracker with monthly budgets, savings goals and an EMI calculator.", [("Personal-Budget-Tracker.xlsx", X(xc.budget_tracker), f"{xl}: budget, transactions, month view, savings goals, EMI tracker")], "Log expenses the same day; weekly is too late to remember them."),
        "small-business-profit-and-loss-dashboard-customised": ("A monthly profit and loss dashboard with margins and a profit chart.", [("Profit-and-Loss-Dashboard.xlsx", X(xc.pnl_dashboard), f"{xl}: monthly P&L with gross and net margin")], "Rename the revenue and cost lines to match how your business actually earns and spends."),
        "budget-vs-actual-variance-report": ("A budget vs actual report that flags overspends and records the reasons.", [("Budget-vs-Actual-Variance.xlsx", X(xc.variance_report), f"{xl}: variance sheet plus a commentary sheet")], "Always write the 'why' on the Commentary sheet; the number alone is not the report."),
        "cash-flow-forecast-model-12-months": ("A 12-month cash flow forecast that warns you before cash runs short.", [("Cash-Flow-Forecast-12-Months.xlsx", X(xc.cashflow_forecast), f"{xl}: receipts, payments, closing cash and warnings")], "Be cautious with receipts: assume customers pay a week later than they promise."),
        "sales-tracking-dashboard": ("A sales tracker with a summary by product, month and payment status.", [("Sales-Tracking-Dashboard.xlsx", X(xm.sales_tracker), f"{xl}: sales log and automatic summary")], "Enter each sale the day it happens and chase the 'Pending' ones weekly."),
        "inventory-stock-tracker": ("A stock tracker that shows closing stock, reorder alerts and stock value.", [("Inventory-Stock-Tracker.xlsx", X(xm.inventory), f"{xl}: item list with reorder status")], "Do a physical count monthly and correct the opening stock."),
        "expense-tracker-for-shops": ("A shop expense tracker with category and monthly totals.", [("Shop-Expense-Tracker.xlsx", X(xm.shop_expenses), f"{xl}: expense log and summary")], "Keep bills or UPI screenshots for every expense above ₹500."),
        "gst-invoice-and-register-template": ("A GST invoice with CGST/SGST/IGST, a sales register and a monthly tax summary.", [("GST-Invoice-and-Register.xlsx", X(xm.gst_invoice), f"{xl}: printable invoice, sales register, monthly summary")], "Confirm rates, HSN codes and filing rules with your CA; GST rules change."),
        "financial-ratio-analysis-workbook": ("Type two years of financials and get ratios with plain-English readings.", [("Financial-Ratio-Analysis.xlsx", X(xc.ratio_workbook), f"{xl}: inputs and 14 ratios with interpretation")], "Compare against 2 peers in the same industry; ratios alone mean little."),
        "excel-data-cleaning-and-formatting": ("A toolkit that cleans names, phone numbers, dates and amounts and flags duplicates.", [("Data-Cleaning-Toolkit.xlsx", X(xm.cleaning_toolkit), f"{xl}: paste messy data, get clean data, plus a checklist")], "Always keep the original file untouched and clean a copy."),
        "pivottable-reports-from-your-data": ("Pivot-style reports that update automatically, plus a guide to real PivotTables and slicers.", [("PivotTable-Reports.xlsx", X(xm.pivot_report), f"{xl}: data, formula-based pivot report"), ("PivotTable-Guide.docx", dk.pivot_guide, "Word guide: build a real PivotTable, slicers and charts")], "Use an Excel Table (Ctrl+T) so new rows are included automatically."),
        "power-bi-sales-dashboard": ("A clean sales data model and a build guide for a Power BI sales dashboard.", [("PowerBI-Sales-Data.xlsx", X(xm.powerbi_sales_data), f"{xl}: Sales, Products, Customers and Calendar tables (240 sample orders)"), ("PowerBI-Sales-Build-Guide.docx", dk.powerbi_dax_sales, "Word guide: relationships, DAX measures, page layout")], "Replace the sample rows but keep the column names so the measures keep working."),
        "power-bi-financial-kpi-dashboard": ("A tidy financials table and a build guide for revenue, margin and budget variance KPIs.", [("PowerBI-Financial-Data.xlsx", X(xm.powerbi_fin_data), f"{xl}: 12 months of Actual and Budget accounts"), ("PowerBI-Financial-KPI-Guide.docx", dk.powerbi_dax_fin, "Word guide: DAX measures and layout")], "Keep costs positive in the data; the measures do the subtraction."),
        "excel-to-power-bi-conversion": ("A clean-table template and step-by-step guide to move an Excel report into Power BI.", [("Clean-Table-Template.xlsx", X(xm.powerbi_ready_table), f"{xl}: clean layout vs messy example"), ("Excel-to-PowerBI-Guide.docx", dk.powerbi_convert, "Word guide: prepare, reshape with Power Query, rebuild, refresh")], "Fix the data layout first; most Power BI problems start in the spreadsheet."),
        "monthly-management-report-mis": ("A one-page monthly MIS report with actual, budget and last-month comparisons.", [("Monthly-MIS-Report.xlsx", X(xc.mis_report), f"{xl}: one-page report with notes boxes")], "Write the highlights and actions yourself: that is the part owners read."),
        "coaching-centre-fee-and-admission-dashboard": ("A coaching centre tracker for admissions, fees collected and balances due.", [("Coaching-Fee-and-Admission-Dashboard.xlsx", X(xm.coaching_dashboard), f"{xl}: student fee log and summary")], "Update fees the day money is received so balances are always right."),
        "restaurant-revenue-and-expense-dashboard": ("A restaurant tracker showing revenue, expenses and daily/monthly profit.", [("Restaurant-Revenue-and-Expense-Dashboard.xlsx", X(xm.restaurant), f"{xl}: daily log and summary")], "Record food cost separately; it is the number that decides profit."),
        "retail-shop-profit-dashboard": ("A retail tracker that works out revenue, profit and margin by product category.", [("Retail-Shop-Profit-Dashboard.xlsx", X(xm.retail_profit), f"{xl}: sales log with profit and margin")], "Update cost prices when suppliers change them; old costs hide losses."),
        "budget-planning-model-for-startups": ("A 12-month startup budget showing cash runway and when you run out of money.", [("Startup-Budget-Model.xlsx", X(xc.startup_budget), f"{xl}: revenue growth, costs, funding and runway")], "Always model a slower-growth case too; investors will ask."),
        "break-even-and-pricing-analysis": ("Find your break-even point and test prices before you change them.", [("Break-Even-and-Pricing.xlsx", X(xc.breakeven), f"{xl}: break-even calculator, chart and price test")], "Include every fixed cost (your own salary too) or break-even will look too easy."),
        "monthly-dashboard-update-recurring": ("A monthly figures log and checklist to keep your dashboard up to date.", [("Monthly-Figures-Log.xlsx", X(xm.monthly_log), f"{xl}: month-by-month log with profit chart"), ("Monthly-Update-Checklist.docx", dk.monthly_update_checklist, "Word checklist and monthly note template")], "Pick one fixed day each month for the update and set a calendar reminder."),
        "one-page-landing-page": ("A mobile-friendly one-page landing page you can edit and upload today.", [("website", site(wk.landing), "HTML and CSS files: open index.html in a browser")], "Search the files for 'EDIT:' to find every place that needs your text."),
        "small-business-website-up-to-5-pages": ("A 5-page business website: home, about, services, gallery and contact.", [("website", site(wk.business5), "HTML and CSS files: five pages sharing one stylesheet")], "Put real photos in the gallery; stock images lower trust."),
        "personal-portfolio-website": ("A one-page portfolio for students and freelancers.", [("website", site(wk.portfolio), "HTML and CSS files: about, skills, projects and contact")], "Show 3 projects with a result for each: employers look at results, not skills lists."),
        "coaching-centre-website-with-enquiry-form": ("A coaching centre website with courses, fees and an enquiry form.", [("website", site(wk.coaching), "HTML and CSS files: home, courses, fees, enquiry")], "Show fees openly: parents trust centres that do."),
        "restaurant-website-with-menu": ("A restaurant website with menu, hours, location and WhatsApp ordering.", [("website", site(wk.restaurant), "HTML and CSS files: home, menu, contact")], "Add real food photos and keep the menu prices current."),
        "website-redesign-refresh": ("A drop-in stylesheet and checklist to give an existing website a modern look.", [("refresh.css", lambda: wk.refresh_pack()["refresh.css"], "Stylesheet: add after your existing CSS"), ("Redesign-Checklist.docx", dk.redesign_checklist, "Word checklist: audit, quick wins, before/after")], "Change one thing at a time and keep before/after screenshots."),
        "mobile-responsiveness-fix": ("A responsive CSS fix pack and test checklist for sites that look bad on phones.", [("responsive-fixes.css", lambda: wk.mobile_fix_pack()["responsive-fixes.css"], "Stylesheet: add after your main CSS"), ("viewport-snippet.html", lambda: wk.mobile_fix_pack()["viewport-snippet.html"], "The meta tag every page needs"), ("Mobile-Test-Checklist.docx", dk.mobile_checklist, "Word checklist: test on a real phone")], "Test on a real phone, not just a narrow browser window."),
        "google-business-profile-setup": ("A checklist, description and review templates to set up Google Business Profile properly.", [("Google-Business-Profile-Kit.docx", dk.gbp, "Word kit: setup checklist, description, post ideas, review requests")], "Ask every happy customer for a review: it is the strongest local ranking signal you control."),
        "website-maintenance-monthly": ("A monthly maintenance checklist and a log to show your client what you did.", [("Maintenance-Log.xlsx", X(xm.maintenance_log), f"{xl}: task log with hours"), ("Maintenance-Checklist.docx", dk.maintenance_checklist, "Word checklist and monthly report template")], "Always take a backup before any update."),
        "basic-on-page-seo-setup": ("An SEO plan, checklist and ready-to-paste snippets for titles, descriptions and schema.", [("SEO-Keyword-and-Page-Plan.xlsx", X(xm.seo_keywords), f"{xl}: one row per page with length checks"), ("SEO-Checklist.docx", dk.seo_checklist, "Word checklist"), ("seo/head-snippet.html", lambda: wk.seo_snippets()["head-snippet.html"], "HTML to paste in each page's head"), ("seo/robots.txt", lambda: wk.seo_snippets()["robots.txt"], "robots.txt"), ("seo/sitemap.xml", lambda: wk.seo_snippets()["sitemap.xml"], "sitemap.xml")], "SEO takes weeks; fix the basics, then keep publishing useful pages."),
        "automated-weekly-sales-report": ("A sales sheet with a weekly report and a script that emails you the weekly total.", [("Weekly-Sales-Report.xlsx", X(xm.weekly_sales), f"{xl}: sales log and weekly report"), ("weekly-sales-email.gs", dk.apps_script_weekly, "Google Apps Script: emails last week's sales every Monday")], "Upload the workbook to Google Sheets (File > Import) to use the email script."),
        "google-sheets-lead-enquiry-tracker": ("A lead tracker with status, follow-up dates and overdue counts.", [("Lead-Enquiry-Tracker.xlsx", X(xm.lead_tracker), f"{xl}: lead log and pipeline summary")], "Set a next follow-up date on every lead: leads rarely die from rejection, they die from silence."),
        "google-form-to-sheet-to-email-automation": ("A form-to-sheet-to-email setup: every answer saved, you and the customer emailed.", [("Form-Responses-Tracker.xlsx", X(xm.form_responses), f"{xl}: tracker for form responses"), ("Form-to-Email-Guide.docx", dk.form_sheet_email_guide, "Word guide: step by step"), ("form-to-email.gs", dk.apps_script_form, "Google Apps Script")], "Test with your own email first, then share the form."),
        "invoice-generator-in-sheets-excel": ("An invoice generator with customer and item dropdowns and an invoice log.", [("Invoice-Generator.xlsx", X(xm.invoice_generator), f"{xl}: customers, items, invoice, log")], "Save each invoice as PDF named with its number and customer."),
        "student-attendance-and-fee-tracker": ("A student attendance and monthly fee tracker with attendance percentage and balances.", [("Student-Attendance-and-Fee-Tracker.xlsx", X(xm.attendance_fees), f"{xl}: students, attendance grid, fees")], "Mark attendance daily; weekly guessing is how disputes start."),
        "appointment-booking-tracker": ("An appointment tracker with status, fees and no-show counts.", [("Appointment-Booking-Tracker.xlsx", X(xm.appointments), f"{xl}: bookings and summary")], "Send a reminder the day before; it cuts no-shows."),
        "n8n-make-workflow-setup-simple": ("A starter n8n workflow and a recipe to save enquiries and email yourself.", [("n8n-Make-Workflow-Guide.docx", dk.n8n_guide, "Word guide: n8n and Make recipes"), ("starter-form-webhook.json", dk.n8n_json, "Importable n8n starter workflow (webhook to confirmation)")], "Test with fake data first and add an email alert for failures."),
        "excel-automation-with-formulas-no-macros": ("Working examples of the formulas that replace manual work, with no macros.", [("Excel-Formula-Automation.xlsx", X(xm.formula_automation), f"{xl}: formula demos, lookup data, cheat sheet")], "Prefer Tables, Data Validation and Conditional Formatting over macros."),
        "data-entry-system-with-dropdowns-and-validation": ("A data entry sheet with dropdowns, automatic totals and duplicate checks.", [("Data-Entry-System.xlsx", X(xm.data_entry_system), f"{xl}: validated entry sheet with a check column")], "Fix every row marked 'Missing field' or 'Possible duplicate' before using the data."),
        "company-financial-analysis-report": ("A report template and ratio workbook for analysing a company's financial health.", [("Financial-Analysis-Report-Template.docx", dk.analysis_report, "Word template: nine-section analysis report"), ("Company-Ratio-Workbook.xlsx", X(xc.ratio_workbook, "Company financial ratio workbook"), f"{xl}: inputs and ratios with readings")], "Use 3 to 5 years of data and compare with at least two peers."),
        "industry-market-research-report": ("A research report template with a TAM/SAM/SOM market size calculator.", [("Market-Research-Report-Template.docx", dk.market_report, "Word template and source checklist"), ("Market-Size-Calculator.xlsx", X(xm.market_size), f"{xl}: TAM, SAM, SOM calculator")], "Write down the source and year of every number."),
        "competitor-analysis": ("A competitor comparison matrix, profile sheet and SWOT action plan.", [("Competitor-Analysis.xlsx", X(xm.comparison_matrix), f"{xl}: weighted scoring and competitor profiles"), ("SWOT-and-Action-Plan.docx", dk.swot, "Word template: SWOT and actions")], "Read competitors' reviews: customers tell you exactly where they are weak."),
        "business-plan-financial-projections": ("A 3-year projection model for revenue, costs, profit, tax and cash.", [("Business-Plan-Financial-Projections.xlsx", X(xc.projections), f"{xl}: assumptions and 3-year projections")], "State every assumption in words in your business plan; banks read those first."),
        "pitch-deck-financial-slides": ("Investor-ready financial slides (traction, unit economics, projections, use of funds) plus a projection model.", [("Pitch-Deck-Financial-Slides.pptx", dk.pitch_deck_financials, "PowerPoint: six financial slides with charts"), ("Pitch-Deck-Speaker-Notes.docx", dk.pitch_deck_notes, "Word: what to say and what investors ask"), ("Financial-Projections.xlsx", X(xc.projections, "3-year projections for your pitch"), f"{xl}: numbers to paste into the slides")], "Right-click a chart and choose Edit data to put in your numbers."),
        "professional-powerpoint-presentation": ("A clean 8-slide presentation template with charts and tables, plus design tips.", [("Presentation-Template.pptx", dk.powerpoint_template, "PowerPoint: agenda, findings, options, recommendation, next steps"), ("Presentation-Design-Tips.docx", dk.deck_tips, "Word: structure and design rules")], "One message per slide; write each slide title as a sentence."),
        "linkedin-profile-optimisation": ("Headline formulas, About templates and a profile checklist for LinkedIn.", [("LinkedIn-Profile-Kit.docx", dk.linkedin, "Word kit: headline, About, experience bullets, checklist, posting plan")], "Fix the headline and About first; they decide who reads the rest."),
        "resume-cv-for-finance-roles": ("An ATS-friendly resume template for finance roles plus a cover letter.", [("Resume-Template.docx", dk.resume, "Word resume with finance bullet patterns"), ("Cover-Letter-Template.docx", dk.cover_letter, "Word cover letter")], "Put a number in every bullet and mirror words from the job description."),
        "social-media-content-calendar-1-month": ("A 30-day content calendar with caption openers and posting times.", [("Content-Calendar-30-Days.xlsx", X(xm.content_calendar), f"{xl}: 30 posts, caption templates, posting times")], "Batch-write a week of posts in one sitting."),
    }


def build_one(slug: str, spec, out_dir: Path) -> dict:
    promise, files, tip = spec
    svc = CAT[slug]
    outputs: dict[str, bytes] = {}
    inside: list[str] = []
    for name, builder, what in files:
        res = builder() if callable(builder) else builder
        if isinstance(res, dict):  # website folder
            for n, b in res.items():
                outputs[n] = b
            inside.append(f"website/: {what}")
        else:
            outputs[name] = res
            inside.append(f"{name}: {what}")
            if slug in BLANK_FOR and isinstance(builder, XB):
                outputs[blank_name(name)] = builder(blank=True)
                inside.append(f"{blank_name(name)}: The same workbook, empty and ready for your own data")
    steps = ["Unzip this folder (right-click > Extract All) and open the main file.",
             "Read the Start here sheet or the comments at the top: they take two minutes.",
             "Replace the sample data/text with your own. Peach cells (Excel) or lines marked EDIT are yours to change.",
             "Save a copy before big changes, then use it every day or week as described in the file."]
    has_blank = any("BLANK" in n for n in outputs)
    extra = ["Open the file with example data first to see how it works, then use the BLANK file for your real data."] if has_blank else []
    guide = howto(f"{svc['title']}: ready-made kit", promise, inside, steps, [tip, *extra, "Sample data is only an example: replace it before you rely on any number.",
                                                                               "Open Excel files in desktop Excel (or Excel online). Google Sheets works too (File > Import); a few formats may differ."])
    folder = f"{svc['id']:02d}-{slug}"
    files_out = {"00-START-HERE-How-to-use.docx": guide, **outputs}
    out = out_dir / f"{slug}.zip"
    pack(files_out, out, folder)
    return {"slug": slug, "zip": out.name, "files": sorted(files_out), "bytes": out.stat().st_size}


KIND = {".xlsx": "Excel", ".docx": "Word", ".pptx": "PowerPoint", ".css": "Web", ".html": "Web", ".gs": "Script", ".json": "Workflow", ".txt": "Web", ".xml": "Web"}


def export_contents(dest: Path) -> None:
    """Writes frontend/src/lib/kitContents.ts: what is inside each kit, shown on the service pages."""
    out: dict[str, dict] = {}
    for slug, (promise, files, tip) in kits().items():
        items = []
        for name, builder, what in files:
            if name == "website":
                pages = sorted(n.split("/")[-1] for n in builder() if n.endswith(".html"))
                items.append({"file": f"{len(pages)}-page website ({', '.join(pages)}) + style.css", "what": "Mobile-friendly HTML and CSS you can edit and upload; open index.html to preview", "kind": "Website"})
            else:
                suffix = Path(name).suffix.lower()
                desc = what.split(": ", 1)[-1] if what.startswith(("Excel workbook:", "Word ", "PowerPoint:", "Google Apps Script", "Stylesheet", "Importable")) and ": " in what else what
                items.append({"file": Path(name).name, "what": desc[:1].upper() + desc[1:], "kind": KIND.get(suffix, "File")})
                if slug in BLANK_FOR and isinstance(builder, XB):
                    items.append({"file": Path(blank_name(name)).name, "what": "The same workbook, empty and ready for your own data", "kind": "Excel"})
        items.insert(0, {"file": "00-START-HERE how-to guide", "what": "A two-minute guide: what is in the kit and how to use it", "kind": "Word"})
        out[slug] = {"tip": tip, "items": items}
    body = json.dumps(out, indent=1, ensure_ascii=False)
    dest.write_text("// Generated by backend/kits_src/build.py (export_contents). Do not edit by hand.\n"
                    "export interface KitItem { file: string; what: string; kind: string }\n"
                    f"export const KIT_CONTENTS: Record<string, {{ tip: string; items: KitItem[] }}> = {body};\n", encoding="utf-8")


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    spec = kits()
    missing = set(CAT) - set(spec)
    extra = set(spec) - set(CAT)
    assert not missing and not extra, (missing, extra)
    manifest = []
    for slug in CAT:
        info = build_one(slug, spec[slug], OUT)
        manifest.append(info)
        print(f"{info['slug']:55s} {info['bytes'] // 1024:>5d} KB  {len(info['files'])} files")
    (OUT / "manifest.json").write_text(json.dumps(manifest, indent=1), encoding="utf-8")
    print(f"\n{len(manifest)} kits, {sum(m['bytes'] for m in manifest) // 1024} KB total")


if __name__ == "__main__":
    if "--contents" in sys.argv:
        export_contents(OUT.parent.parent.parent.parent / "frontend" / "src" / "lib" / "kitContents.ts")
        print("kitContents.ts written")
    else:
        main()
