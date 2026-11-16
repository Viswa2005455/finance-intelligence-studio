"""Word and PowerPoint kit content: checklists, guides, templates and decks."""

from __future__ import annotations

import io
import json

from docx.shared import Pt

from lib import bullets, doc_bytes, new_doc, table


def make(heading, sub, sections):
    """sections: list of (heading, items) where items are strings (paragraphs), ('b', [bullets]), ('n', [numbered]), ('t', header, rows), ('c', [checkbox lines])."""
    d = new_doc(heading, sub)
    for h, items in sections:
        if h:
            d.add_heading(h, level=1)
        for it in items:
            if isinstance(it, str):
                d.add_paragraph(it)
            elif it[0] == "b":
                bullets(d, it[1])
            elif it[0] == "n":
                bullets(d, it[1], "List Number")
            elif it[0] == "c":
                for line in it[1]:
                    d.add_paragraph("☐  " + line)
            elif it[0] == "t":
                table(d, it[1], it[2])
            elif it[0] == "code":
                p = d.add_paragraph(it[1])
                for r in p.runs:
                    r.font.name = "Consolas"
                    r.font.size = Pt(9)
    return doc_bytes(d)


# ------------------------------------------------------------------------------ checklists and guides
def gbp():
    return make("Google Business Profile setup kit", "Get found on Google Maps and Search. Free, and the best local marketing there is.", [
        ("Before you start", [("b", ["A Google account (a business Gmail is best).", "Your exact business name, address, phone, opening hours and website.", "10+ clear photos: outside, inside, products, team.", "A short description (use the template below)."])]),
        ("Setup checklist", [("c", ["Go to business.google.com and click Manage now.", "Enter the exact business name used on your board (no keyword stuffing).", "Choose the best main category; add up to 9 secondary ones.",
                                    "Add your address (or service area if you travel to customers).", "Add phone number and website.", "Complete verification (video, phone, or postcard; follow Google's prompt).",
                                    "Set opening hours, including holidays.", "Add services or products with prices.", "Upload logo, cover photo and 10+ photos.", "Turn on messaging and add attributes (Wi-Fi, women-led, etc.).",
                                    "Add your Maps short link to your website and WhatsApp bio."])]),
        ("Business description template (750 characters max)", ["[Business name] is a [type of business] in [area, city]. We help [customers] with [main services]. Since [year], we have served [number]+ customers with [what makes you different: fast delivery, fair prices, expert team]. Visit us at [landmark] or call [phone]. Open [days and hours]."]),
        ("Weekly post ideas (takes 5 minutes)", [("b", ["Offer of the week with a photo.", "Before/after of your work.", "A customer thank-you (with permission).", "A short tip related to your service.", "A new product or service announcement."])]),
        ("Ask for reviews (copy and send)", ["Hi [name], thank you for choosing us! If you were happy with the service, would you leave a short Google review? It takes 30 seconds and helps a small business a lot: [your review link]. Thank you!",
                                              "Find your review link: Google Business Profile > Ask for reviews > Copy link."]),
        ("Reply to reviews", [("b", ["Thank every reviewer by name within 2 days.", "For a bad review: apologise, offer to fix it offline, stay calm and polite.", "Never offer money for reviews; Google bans that."])]),
    ])


def maintenance_checklist():
    return make("Website maintenance checklist", "Do this every month and log it in the maintenance log workbook.", [
        ("Every month", [("c", ["Take a full backup (files and database) and store it off the server.", "Update the platform, theme and plugins (test on a copy first for important sites).", "Check every form by sending a test enquiry.",
                                "Click all menu links and buttons; fix broken ones.", "Test the site on a phone and a laptop.", "Run a speed test (PageSpeed Insights) and note the score.", "Check the security certificate (padlock) is valid.",
                                "Review user accounts and remove people who no longer need access.", "Check Google Search Console for errors.", "Update prices, hours and contact details if they changed.", "Renew domain and hosting before they expire."])]),
        ("Every quarter", [("c", ["Refresh the home page photos and offers.", "Review pages that get no visitors; improve or remove them.", "Re-check page titles and descriptions.", "Test the site in Chrome, Safari and Edge."])]),
        ("Monthly report to the owner (template)", ["Month: ____   Uptime: ____   Backups taken: ____   Updates done: ____", "Issues fixed: ____   Visitors (if tracked): ____   Page speed score: ____", "Recommended next step: ____"]),
    ])


def seo_checklist():
    return make("Basic on-page SEO checklist", "Simple changes that help Google understand and show your pages.", [
        ("For every page", [("c", ["One main keyword chosen (what a customer would type).", "Title tag under 60 characters, keyword near the start, business name at the end.", "Meta description under 155 characters; a reason to click.",
                                   "One H1 heading containing the keyword; use H2/H3 for sections.", "Keyword appears naturally in the first paragraph (do not repeat it unnaturally).", "Every image has a short descriptive alt text and is compressed (under 200 KB).",
                                   "Clean URL with words, not numbers (/excel-dashboard, not /page?id=7).", "2 to 3 links to other pages on your site.", "A clear call to action (call, WhatsApp, form)."])]),
        ("Whole site", [("c", ["Site works on mobile and loads in under 3 seconds.", "HTTPS padlock is on.", "Submit sitemap.xml in Google Search Console.", "robots.txt exists and does not block the site.",
                               "Business name, address and phone are identical everywhere (site, Google Business Profile, social).", "Google Business Profile is set up (local search).", "Add LocalBusiness schema (see head-snippet.html)."])]),
        ("Setup steps", [("n", ["Open the SEO keyword workbook and plan one row per page.", "Paste the head-snippet.html into each page's head and edit the text.", "Upload robots.txt and sitemap.xml to the website root.",
                                "Verify the site in search.google.com/search-console and submit the sitemap.", "Re-check rankings and clicks after 4 weeks; improve pages with high impressions but few clicks."])]),
        ("Honest note", ["SEO takes weeks to show results and nobody can guarantee a rank. These steps remove the common problems; steady useful content does the rest."]),
    ])


def n8n_guide():
    return make("n8n / Make simple workflow kit", "Automate a repetitive task without code: a form fills a sheet and you get an email.", [
        ("What you can build with this kit", [("b", ["Starter n8n workflow (import file): receives form data on a webhook and returns a confirmation.", "A step-by-step recipe to extend it: save to Google Sheets and email you.", "The same recipe for Make.com (scenario steps).", "A checklist of ideas worth automating."])]),
        ("Import the starter n8n workflow", [("n", ["Open n8n (cloud or self-hosted) and click Workflows > Import from file. Choose starter-form-webhook.json.", "Open the Webhook node and copy its Test URL.", "Send a test: in a terminal run  curl -X POST <URL> -H 'Content-Type: application/json' -d '{\"name\":\"Asha\",\"email\":\"a@example.com\",\"message\":\"Hello\"}'",
                                                  "See the data arrive in n8n and the confirmation reply.", "Activate the workflow and use the Production URL in your website form or Google Form script."])]),
        ("Extend it: save the enquiry to Google Sheets and email yourself", [("n", ["Add a Google Sheets node after the Set node: operation Append row; connect your Google account; pick the sheet and map name, email, message.", "Add a Gmail node (or Send Email node): To = your address, Subject = New enquiry from {{$json.name}}, Body = the details.",
                                                                            "Click Execute workflow with the test data; check the sheet and your inbox.", "Turn on Active."])]),
        ("Same flow in Make.com", [("n", ["Create scenario > add Webhooks > Custom webhook; copy the URL.", "Add Google Sheets > Add a row. Map the fields from the webhook.", "Add Gmail > Send an email to yourself.", "Run once with test data, then switch scheduling to Immediately."])]),
        ("Ideas worth automating", [("b", ["New enquiry > sheet row + WhatsApp/email alert", "Invoice paid > thank-you email and receipt", "Weekly sales summary emailed every Monday", "New order > add to stock sheet and reduce quantity", "Daily reminder of overdue payments"])]),
        ("Good practice", [("b", ["Test with fake data first.", "Never put passwords or API keys in screenshots or shared files.", "Keep an owner email for failures so you know when a workflow breaks."])]),
    ])


def n8n_json():
    wf = {"name": "Starter: form webhook to confirmation", "nodes": [
        {"parameters": {"httpMethod": "POST", "path": "enquiry", "responseMode": "responseNode", "options": {}}, "id": "a1b2c3d4-0001", "name": "Webhook", "type": "n8n-nodes-base.webhook", "typeVersion": 2, "position": [240, 300], "webhookId": "enquiry-starter"},
        {"parameters": {"assignments": {"assignments": [
            {"id": "f1", "name": "name", "value": "={{ $json.body.name }}", "type": "string"}, {"id": "f2", "name": "email", "value": "={{ $json.body.email }}", "type": "string"},
            {"id": "f3", "name": "message", "value": "={{ $json.body.message }}", "type": "string"}, {"id": "f4", "name": "received_at", "value": "={{ $now.toISO() }}", "type": "string"}]}, "options": {}},
         "id": "a1b2c3d4-0002", "name": "Set fields", "type": "n8n-nodes-base.set", "typeVersion": 3.4, "position": [480, 300]},
        {"parameters": {"respondWith": "json", "responseBody": "={{ { \"ok\": true, \"message\": \"Thanks \" + $json.name + \", we received your enquiry.\" } }}", "options": {}},
         "id": "a1b2c3d4-0003", "name": "Respond", "type": "n8n-nodes-base.respondToWebhook", "typeVersion": 1.1, "position": [720, 300]}],
          "connections": {"Webhook": {"main": [[{"node": "Set fields", "type": "main", "index": 0}]]}, "Set fields": {"main": [[{"node": "Respond", "type": "main", "index": 0}]]}},
          "active": False, "settings": {"executionOrder": "v1"}, "pinData": {}}
    return json.dumps(wf, indent=2).encode()


def analysis_report():
    return make("Company financial analysis report: template", "Fill each section. Use the ratio workbook for the numbers.", [
        ("1. Company snapshot", [("t", ["Item", "Detail"], [["Company", ""], ["Industry", ""], ["Years analysed", ""], ["Source of data", "Annual report / Screener / MCA filings"], ["Prepared by / date", ""]]), "Two sentences: what the company does and how it makes money."]),
        ("2. Key numbers (3 to 5 years)", [("t", ["Metric", "Year 1", "Year 2", "Year 3"], [["Revenue", "", "", ""], ["Operating profit", "", "", ""], ["Net profit", "", "", ""], ["Total debt", "", "", ""], ["Cash from operations", "", "", ""]])]),
        ("3. Profitability", ["Gross margin, operating margin, net margin: trend and reasons. Compare with 2 peers."]),
        ("4. Liquidity and working capital", ["Current ratio, quick ratio, debtor/inventory/creditor days. Is cash tied up? Can it pay short-term dues?"]),
        ("5. Leverage and solvency", ["Debt to equity, interest cover. Is borrowing growing faster than profit?"]),
        ("6. Efficiency and returns", ["Asset turnover, ROE, ROCE. Is management using capital well?"]),
        ("7. Cash flow quality", ["Compare net profit with operating cash flow. Persistent gap = warning sign."]),
        ("8. Strengths, risks and red flags", [("b", ["Strengths: ", "Risks: ", "Red flags (rising receivables, related-party dealings, auditor remarks): "])]),
        ("9. Conclusion", ["Three-sentence view: financial health (strong/stable/weak), the biggest risk, and what to monitor next. State clearly this is analysis, not investment advice."]),
        ("Sources and notes", ["List every document and date used."]),
    ])


def market_report():
    return make("Industry / market research report: template", "A structure that makes a research report easy to read and easy to defend.", [
        ("1. Executive summary (write last)", ["Five lines: the market, its size, growth, the opportunity and your recommendation."]),
        ("2. Scope and method", ["What is included (product, region, time). Sources used: government data, industry bodies, company filings, surveys, interviews."]),
        ("3. Market size and growth", ["Use the market size calculator workbook. Show TAM, SAM, SOM and the assumption behind each number. Include the source and year of every figure."]),
        ("4. Customers and demand", [("b", ["Who buys, how often, how much?", "What triggers a purchase?", "Key segments and their needs."])]),
        ("5. Competitors", ["Use the competitor workbook. List main players, prices, strengths and weaknesses."]),
        ("6. Trends and drivers", [("b", ["Technology, regulation, prices, consumer behaviour.", "What could grow or shrink the market in 3 years?"])]),
        ("7. Risks", ["Regulation, supply, competition, dependence on one customer or supplier."]),
        ("8. Recommendation", ["What to do, in what order, and the numbers that would prove you wrong."]),
        ("Source checklist", [("c", ["Every number has a source and year.", "Conflicting sources are noted.", "Estimates are labelled as estimates.", "Charts have titles and units."])]),
    ])


def swot():
    return make("SWOT and competitor action plan", "Turn the competitor comparison into decisions.", [
        ("SWOT grid", [("t", ["Strengths (inside)", "Weaknesses (inside)"], [["", ""], ["", ""], ["", ""]]), ("t", ["Opportunities (outside)", "Threats (outside)"], [["", ""], ["", ""], ["", ""]])]),
        ("Turn it into actions", [("t", ["Combine", "Question", "Action"], [["Strength + Opportunity", "How do we use our strength to win this opportunity?", ""], ["Weakness + Opportunity", "What must we fix to grab it?", ""],
                                                                           ["Strength + Threat", "How do we use strengths to defend?", ""], ["Weakness + Threat", "What is the biggest risk and how do we reduce it?", ""]])]),
        ("Competitor questions", [("b", ["Why do customers choose them over us?", "What do customers complain about in their reviews?", "Where is their price high or low?", "What do they not offer that customers want?"])]),
    ])


def linkedin():
    return make("LinkedIn profile optimisation kit", "Copy the patterns, replace the brackets, and your profile will read like a professional's.", [
        ("Headline formulas (220 characters)", [("b", ["[Role you want] | [Skill 1] · [Skill 2] · [Skill 3] | [Result you deliver]", "PGDM Finance Student | Financial Analysis · Excel · Power BI | Helping small businesses see their numbers clearly",
                                                    "Finance Analyst | Budgeting · MIS · Dashboards | I turn messy data into decisions"])]),
        ("About section template (first 3 lines matter most)", ["Line 1: Who you help and what you do. Line 2: Your proof (number, project, result). Line 3: What you want now.",
                                                              "I help [audience] [achieve result] using [skills]. In [period/project] I [specific outcome with a number]. I am currently looking for [role/clients]; message me or email [email].",
                                                              "Then: 3 short paragraphs (skills, experience, what you care about) and a closing call to action."]),
        ("Experience bullets: use this pattern", [("b", ["Action verb + what you did + result/number: 'Built an Excel dashboard that cut monthly reporting time from 6 hours to 45 minutes.'", "Analysed [data] and found [insight], leading to [decision].", "Led [team/project] of [size] to [outcome]."])]),
        ("Profile checklist", [("c", ["Professional, friendly photo (face fills 60%).", "Banner image with your focus or tagline.", "Custom URL (linkedin.com/in/yourname).", "Headline uses keywords recruiters search.", "About has a call to action and contact.",
                                     "Featured section: best project, resume, portfolio link.", "10+ relevant skills; ask for 3 endorsements.", "2 recommendations from teachers, managers or clients.", "Education, certifications and projects added.", "Open to Work set (recruiters only) if job hunting."])]),
        ("Posting starter plan (3 posts a week)", [("b", ["Monday: a lesson you learned.", "Wednesday: a tip with an example.", "Friday: a project or result."])]),
        ("Connection message (under 200 characters)", ["Hi [name], I'm a finance student interested in [topic]. I enjoyed your post on [subject]. Would love to connect and learn from you."]),
    ])


def resume():
    d = new_doc("YOUR NAME", "City, State · +91 99999 99999 · you@email.com · linkedin.com/in/yourname")
    for h, items in [
        ("Professional summary", ["PGDM (Finance) student with strong skills in financial analysis, Excel and Power BI. Built [X projects]. Seeking a [role] position at [type of company] to [contribute skill]. (3 lines maximum.)"]),
        ("Education", ["PGDM in Finance, Your College, City | 2025 to 2027 | CGPA: __", "B.Com / B.Sc / B.E., Your University | 2022 to 2025 | __%"]),
        ("Experience / internships", ["Role, Company, City | Month Year to Month Year"]),
    ]:
        d.add_heading(h, level=1)
        for it in items:
            d.add_paragraph(it)
    bullets(d, ["Analysed [data/financial statements] of [company] and identified [insight], supporting [decision].", "Built an Excel model that [automated/forecasted] [what], saving [hours] per [period].",
                "Prepared [reports/MIS] for [audience], improving [metric] by [x%]."])
    for h, items in [("Projects", None), ("Skills", None), ("Certifications", None)]:
        d.add_heading(h, level=1)
    d.add_paragraph("Project name: one line on the problem, what you did and the result. Tools used: Excel, Power BI.")
    d.add_paragraph("Finance: financial statement analysis, ratio analysis, budgeting and forecasting, valuation basics, MIS reporting.\nTools: Excel (SUMIFS, XLOOKUP, PivotTables), Power BI, Google Sheets, Tally (if used), PowerPoint.\nSoft skills: communication, attention to detail, teamwork.")
    d.add_paragraph("Certification name, issuer, year.")
    d.add_page_break()
    d.add_heading("Resume tips (delete this page before sending)", level=1)
    bullets(d, ["One page for freshers. Use a simple layout: no photos, tables or columns, so ATS software reads it correctly.", "Start every bullet with a verb and include a number.", "Mirror words from the job description (skills and tools).",
                "Save as PDF named YourName_Role.pdf.", "Proofread twice; ask someone else to read it.", "Use the Cover letter file for each application."])
    return doc_bytes(d)


def cover_letter():
    return make("Cover letter template", "Fill the brackets. Keep it to 3 short paragraphs.", [
        ("", ["[Your name]\n[City] · [phone] · [email]\n[Date]", "To: [Hiring manager's name]\n[Company]", "Subject: Application for [Role]"]),
        ("", ["Dear [Name],", "I am writing to apply for the [role] position at [company]. As a [PGDM finance student / analyst] with experience in [2 key skills], I believe I can help your team with [specific need from the job description].",
              "In [project/internship] I [did something with a number]. This gave me strong skills in [skill 1], [skill 2] and [skill 3], which match what you ask for in the role.",
              "I would welcome a chance to discuss how I can contribute. Thank you for your time. My resume is attached.", "Sincerely,\n[Your name]"]),
    ])


def powerbi_dax_sales():
    return make("Power BI sales dashboard: build guide", "From the starter workbook to a finished sales report in about an hour.", [
        ("1. Load and connect the data", [("n", ["Power BI Desktop > Get data > Excel > choose the starter workbook > tick Sales, Products, Customers, Calendar > Load.", "Model view: drag Sales[ProductID] to Products[ProductID], Sales[CustomerID] to Customers[CustomerID], Sales[Date] to Calendar[Date].", "Mark Calendar as a date table (Table tools > Mark as date table > Date)."])]),
        ("2. Measures (Modeling > New measure)", [("code", "Total Sales = SUM ( Sales[SalesAmount] )\nOrders = DISTINCTCOUNT ( Sales[OrderID] )\nUnits Sold = SUM ( Sales[Quantity] )\nAverage Order Value = DIVIDE ( [Total Sales], [Orders] )\n"
                                                    "Sales Last Year = CALCULATE ( [Total Sales], SAMEPERIODLASTYEAR ( Calendar[Date] ) )\nSales Growth % = DIVIDE ( [Total Sales] - [Sales Last Year], [Sales Last Year] )\n"
                                                    "Top Product Sales = CALCULATE ( [Total Sales], TOPN ( 1, VALUES ( Products[Product] ), [Total Sales] ) )")]),
        ("3. Page layout", [("n", ["Top row: four cards: Total Sales, Orders, Average Order Value, Sales Growth %.", "Left: column chart of Total Sales by Month (axis from Calendar).", "Middle: bar chart of Total Sales by Product.",
                                   "Right: map or bar of Total Sales by City/Region.", "Add slicers for Year, Region and Category (Sync across pages).", "Table at the bottom: top 10 customers by Total Sales."])]),
        ("4. Polish", [("b", ["Use two colours only; one for good, one for attention.", "Title each visual with what it shows.", "Format numbers (₹ and thousands separators).", "Check it on the phone layout (View > Phone layout)."])]),
        ("5. Publish and refresh", [("b", ["Save the .pbix, then Home > Publish to your workspace.", "Point the data source to your real Excel file and click Refresh."])]),
    ])


def powerbi_dax_fin():
    return make("Power BI financial KPI dashboard: build guide", "Revenue, margins and actual vs budget from one tidy table.", [
        ("1. Load", [("n", ["Get data > Excel > Financials > Load.", "Create a Calendar table: Modeling > New table > Calendar = CALENDARAUTO ()  then relate Financials[Month] to Calendar[Date].", "Mark Calendar as the date table."])]),
        ("2. Measures", [("code", "Actual = CALCULATE ( SUM ( Financials[Amount] ), Financials[Scenario] = \"Actual\" )\nBudget = CALCULATE ( SUM ( Financials[Amount] ), Financials[Scenario] = \"Budget\" )\n"
                                  "Revenue = CALCULATE ( [Actual], Financials[AccountGroup] = \"Revenue\" )\nCOGS = CALCULATE ( [Actual], Financials[AccountGroup] = \"COGS\" )\nOpex = CALCULATE ( [Actual], Financials[AccountGroup] = \"Opex\" )\n"
                                  "Gross Profit = [Revenue] - [COGS]\nGross Margin % = DIVIDE ( [Gross Profit], [Revenue] )\nOperating Profit = [Gross Profit] - [Opex]\nOperating Margin % = DIVIDE ( [Operating Profit], [Revenue] )\n"
                                  "Revenue Budget = CALCULATE ( [Budget], Financials[AccountGroup] = \"Revenue\" )\nRevenue Variance = [Revenue] - [Revenue Budget]\nRevenue Variance % = DIVIDE ( [Revenue Variance], [Revenue Budget] )")]),
        ("3. Layout", [("n", ["Cards: Revenue, Gross Margin %, Operating Profit, Revenue Variance %.", "Line chart: Revenue vs Revenue Budget by month.", "Waterfall: Revenue to Gross Profit to Operating Profit.", "Matrix: accounts in rows, months in columns, Actual and Budget values.", "Slicers: Year, Quarter."])]),
        ("4. Good practice", [("b", ["Keep costs positive in the data; the measures subtract them.", "Format variances: green when favourable, red when not (conditional formatting).", "Document each measure in its description."])]),
    ])


def powerbi_convert():
    return make("Excel to Power BI conversion guide", "Move a manual Excel report into a refreshable Power BI report.", [
        ("1. Prepare the Excel data", [("c", ["One header row; no merged cells; no blank rows or columns.", "One fact per column (don't mix 'Item (Category)').", "Dates stored as real dates; numbers as numbers.", "No subtotals or totals inside the data.", "Months down the rows, not across (use Power Query to unpivot if needed).", "Turn each range into an Excel Table (Ctrl+T) and name it."])]),
        ("2. Reshape with Power Query (if needed)", [("n", ["Get data > Excel > pick the sheet > Transform data.", "Use first row as headers; remove top rows.", "Select the month columns > Transform > Unpivot columns.", "Split columns, fix types (date, whole number, decimal), remove totals.", "Close & Apply."])]),
        ("3. Rebuild the report", [("n", ["Create measures for each total your Excel report calculates (SUM, DIVIDE, CALCULATE).", "Recreate each table as a Matrix visual and each chart as a visual.", "Add slicers for the filters people used.", "Compare totals with the Excel version for 2 months to confirm they match."])]),
        ("4. Refresh and share", [("b", ["Save the Excel file in a fixed folder; refresh in Power BI Desktop after updating.", "Publish to Power BI Service; set scheduled refresh with a gateway if the file is on your computer.", "Share a link or export a PDF for people without access."])]),
    ])


def pivot_guide():
    return make("PivotTable and slicer guide", "Make a real PivotTable report from the sample data in 5 minutes.", [
        ("Create the PivotTable", [("n", ["Click inside the Data table, Insert > PivotTable > OK.", "Drag Region to Rows, Product to Columns and Amount to Values (Sum).", "Right-click a value > Number Format > Currency.", "Right-click the pivot > Refresh whenever the data changes."])]),
        ("Make it useful", [("b", ["Show % of total: Value Field Settings > Show Values As > % of Grand Total.", "Group dates by month: right-click a date > Group > Months and Years.", "Add a PivotChart: PivotTable Analyze > PivotChart.", "Add Slicers: PivotTable Analyze > Insert Slicer > Region, Salesperson."])]),
        ("Common problems", [("b", ["Blank rows in the data break the range: use an Excel Table (Ctrl+T).", "Numbers stored as text sum to zero: convert them (see the cleaning kit).", "New rows missing: Refresh the pivot."])]),
    ])


def monthly_update_checklist():
    return make("Monthly dashboard update checklist", "The same 10 steps every month: takes 20 minutes once it is a habit.", [
        ("Checklist", [("c", ["Get closing balances and sales/purchase reports for the month.", "Add the month's row(s) to the data / monthly log.", "Check totals against bank statement and invoices.", "Refresh pivots and charts (Data > Refresh All).",
                              "Read the dashboard: anything unusual? Note why.", "Write 3 highlights and 3 problems.", "Compare actual with budget and last month.", "Save a dated copy (Dashboard_2026-02.xlsx).", "Email or share the PDF with the owner.", "Update the budget if business conditions changed."])]),
        ("Monthly note template", ["Month: ____   Revenue: ____ (vs last month ___%)   Profit: ____   Cash: ____", "Highlights: 1) ____ 2) ____ 3) ____", "Concerns: 1) ____ 2) ____ 3) ____", "Next month's actions: ____"]),
    ])


def redesign_checklist():
    return make("Website redesign / refresh checklist", "Use refresh.css for a quick visual lift, then work through this list.", [
        ("Audit first (30 minutes)", [("c", ["Take screenshots of every page (before).", "List the 5 pages that get the most visits (Google Analytics / Search Console).", "Write what visitors should do on each page (call, enquire, buy).", "Note slow, broken or confusing parts."])]),
        ("Quick wins", [("c", ["Add refresh.css after your current stylesheet.", "One clear headline and one main button above the fold.", "Replace blurry or stock images with real photos.", "Cut text by a third; use short paragraphs and bullet points.",
                               "Use at most 2 fonts and 3 colours.", "Make buttons big and the contact number tappable.", "Show prices, reviews and a clear phone/WhatsApp button.", "Check mobile at 375px width."])]),
        ("Before and after", ["Save screenshots after each change. Compare enquiries per week for 4 weeks before and after the refresh."]),
    ])


def mobile_checklist():
    return make("Mobile responsiveness fix checklist", "Add the viewport tag and responsive-fixes.css, then test with this list.", [
        ("Install the fixes", [("n", ["Paste viewport-snippet.html's meta tag into the head of every page.", "Add responsive-fixes.css after your main stylesheet.", "Clear your browser cache and reload on a phone."])]),
        ("Test on a phone (and in Chrome: F12 > device toolbar)", [("c", ["No sideways scrolling.", "Text is readable without zooming.", "Buttons and links are easy to tap with a thumb.", "Menu opens and closes.", "Images fit the screen.", "Forms can be filled and submitted.", "Tables scroll or stack.", "Phone number is a tap-to-call link (tel:).", "Page loads in under 3 seconds on mobile data."])]),
        ("Common causes", [("b", ["Missing viewport meta tag.", "Fixed pixel widths on containers or images.", "Tables and iframes wider than the screen.", "Tiny fonts and cramped buttons."])]),
    ])


def apps_script_weekly():
    return b"""// Weekly sales email. In Google Sheets: Extensions > Apps Script > paste > save.
// Then: Triggers (clock icon) > Add trigger > sendWeeklySales > Time-driven > Week timer > Monday 8-9 am.
// EDIT the two settings below.
const TO = 'you@example.com';
const SHEET = 'Data';       // name of the tab with your sales
const DATE_COL = 1;         // column number of the Date
const AMOUNT_COL = 8;       // column number of the Amount

function sendWeeklySales() {
  const sh = SpreadsheetApp.getActive().getSheetByName(SHEET);
  const rows = sh.getDataRange().getValues().slice(4);   // data starts on row 5
  const end = new Date(); const start = new Date(end.getTime() - 7 * 86400000);
  let total = 0, orders = 0;
  rows.forEach(r => {
    const d = r[DATE_COL - 1], a = Number(r[AMOUNT_COL - 1]);
    if (d instanceof Date && d >= start && d <= end && !isNaN(a)) { total += a; orders++; }
  });
  const body = 'Sales last 7 days: Rs ' + total.toLocaleString('en-IN') + '\\nOrders: ' + orders +
               '\\nAverage order: Rs ' + (orders ? Math.round(total / orders) : 0).toLocaleString('en-IN');
  MailApp.sendEmail(TO, 'Weekly sales report', body);
}
"""


def apps_script_form():
    return b"""// Google Form > Responses > link to a Sheet. Then in that Sheet:
// Extensions > Apps Script > paste > save > Triggers > Add trigger > onFormSubmit > From spreadsheet > On form submit.
// EDIT the owner email. Replies to the customer automatically and alerts you.
const OWNER = 'you@example.com';

function onFormSubmit(e) {
  const v = e.namedValues;                       // answers keyed by question title
  const name = (v['Name'] || [''])[0], email = (v['Email'] || [''])[0], msg = (v['Message'] || [''])[0];
  MailApp.sendEmail(OWNER, 'New enquiry from ' + name, 'Name: ' + name + '\\nEmail: ' + email + '\\nMessage: ' + msg);
  if (email) MailApp.sendEmail(email, 'We received your enquiry', 'Hi ' + name + ',\\n\\nThank you for contacting us. We will reply within one working day.\\n\\nRegards');
}
"""


def form_sheet_email_guide():
    return make("Google Form to Sheet to email automation", "A form that saves every answer and emails you and the customer: free, no code beyond a small script.", [
        ("Steps", [("n", ["Create a Google Form with the questions: Name, Email, Phone, Message (use exactly these titles: the script reads 'Name', 'Email', 'Message').", "Responses tab > Link to Sheets > Create a new spreadsheet.",
                          "In that Sheet: Extensions > Apps Script. Delete the sample code and paste the code from form-to-email.gs. Set OWNER to your email. Save.", "Triggers (clock icon) > Add trigger > function onFormSubmit > event source From spreadsheet > event type On form submit > Save. Allow permissions.",
                          "Submit a test response. You should get an email and so should the test address.", "Share the form link on WhatsApp, Instagram and your website. Use the Form responses tracker workbook to follow up."])]),
        ("Limits to know", [("b", ["Free Gmail can send about 100 emails a day through Apps Script.", "Emails may land in spam at first; ask people to mark them 'Not spam'.", "Never share the Apps Script or spreadsheet with edit access to strangers."])]),
    ])


# ------------------------------------------------------------------------------ PowerPoint decks
def _deck(title, subtitle, slides):
    from pptx import Presentation
    from pptx.chart.data import CategoryChartData
    from pptx.dml.color import RGBColor
    from pptx.enum.chart import XL_CHART_TYPE, XL_LEGEND_POSITION
    from pptx.util import Inches, Pt

    green, teal, grey = RGBColor(0x14, 0x21, 0x3D), RGBColor(0xFF, 0x6B, 0x5B), RGBColor(0x5B, 0x67, 0x70)
    prs = Presentation()
    prs.slide_width, prs.slide_height = Inches(13.333), Inches(7.5)
    blank = prs.slide_layouts[6]

    def text(slide, x, y, w, h, t, size=18, bold=False, color=None):
        tb = slide.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
        tf = tb.text_frame
        tf.word_wrap = True
        p = tf.paragraphs[0]
        p.text = t
        p.font.size, p.font.bold = Pt(size), bold
        if color:
            p.font.color.rgb = color
        return tf

    def band(slide, t):
        r = slide.shapes.add_shape(1, 0, 0, prs.slide_width, Inches(1.2))
        r.fill.solid()
        r.fill.fore_color.rgb = green
        r.line.fill.background()
        text(slide, 0.6, 0.25, 12, 0.8, t, 30, True, RGBColor(255, 255, 255))

    s = prs.slides.add_slide(blank)
    bg = s.shapes.add_shape(1, 0, 0, prs.slide_width, prs.slide_height)
    bg.fill.solid()
    bg.fill.fore_color.rgb = green
    bg.line.fill.background()
    bar_ = s.shapes.add_shape(1, Inches(0.9), Inches(2.15), Inches(1.6), Inches(0.12))
    bar_.fill.solid()
    bar_.fill.fore_color.rgb = RGBColor(0xFF, 0x6B, 0x5B)
    bar_.line.fill.background()
    text(s, 0.9, 2.4, 11.5, 1.5, title, 44, True, RGBColor(255, 255, 255))
    text(s, 0.9, 4.1, 11.5, 1, subtitle, 22, False, RGBColor(0xC9, 0xD1, 0xE6))
    text(s, 0.9, 6.4, 11.5, 0.5, "EDIT: Presenter name · Date", 14, False, RGBColor(0xC9, 0xD1, 0xE6))
    for sd in slides:
        s = prs.slides.add_slide(blank)
        band(s, sd["title"])
        kind = sd.get("kind", "bullets")
        if kind == "bullets":
            tf = text(s, 0.8, 1.6, 11.7, 5, "", 22)
            first = True
            for b in sd["bullets"]:
                p = tf.paragraphs[0] if first else tf.add_paragraph()
                first = False
                p.text = "•  " + b
                p.font.size = Pt(24)
                p.space_after = Pt(14)
        elif kind == "chart":
            cd = CategoryChartData()
            cd.categories = sd["cats"]
            for name, vals in sd["series"]:
                cd.add_series(name, vals)
            gf = s.shapes.add_chart(sd.get("type", XL_CHART_TYPE.COLUMN_CLUSTERED), Inches(0.8), Inches(1.5), Inches(7.6), Inches(5.3), cd)
            ch = gf.chart
            palette = [RGBColor(0xFF, 0x6B, 0x5B), RGBColor(0x14, 0x21, 0x3D), RGBColor(0xF5, 0xC4, 0x51), RGBColor(0x5B, 0x6E, 0xE1)]
            plot = ch.plots[0]
            if sd.get("type") == XL_CHART_TYPE.PIE:
                for i, pt in enumerate(plot.series[0].points):
                    pt.format.fill.solid()
                    pt.format.fill.fore_color.rgb = palette[i % 4]
            else:
                for i, ser in enumerate(plot.series):
                    ser.format.fill.solid()
                    ser.format.fill.fore_color.rgb = palette[i % 4]
                plot.gap_width = 70
                ch.value_axis.major_gridlines.format.line.color.rgb = RGBColor(0xE5, 0xE0, 0xD2)
            ch.font.size = Pt(14)
            ch.has_legend = True
            ch.legend.position = XL_LEGEND_POSITION.BOTTOM
            ch.legend.include_in_layout = False
            tf = text(s, 8.8, 1.7, 4.2, 4.5, "", 18)
            first = True
            for b in sd["bullets"]:
                p = tf.paragraphs[0] if first else tf.add_paragraph()
                first = False
                p.text = "•  " + b
                p.font.size = Pt(18)
                p.space_after = Pt(10)
        elif kind == "table":
            rows, cols = len(sd["rows"]) + 1, len(sd["header"])
            tb = s.shapes.add_table(rows, cols, Inches(0.8), Inches(1.7), Inches(11.7), Inches(0.5) * rows).table
            for c, h in enumerate(sd["header"]):
                tb.cell(0, c).text = h
            for r, row in enumerate(sd["rows"], start=1):
                for c, v in enumerate(row):
                    tb.cell(r, c).text = str(v)
            if sd.get("note"):
                text(s, 0.8, 6.3, 11.7, 0.8, sd["note"], 14, False, grey)
        if sd.get("note") and kind != "table":
            text(s, 0.8, 6.7, 11.7, 0.6, sd["note"], 13, False, grey)
        text(s, 12.3, 7.0, 0.8, 0.4, str(len(prs.slides)), 12, False, grey)
        text(s, 0.8, 7.0, 6, 0.4, "Finance Intelligence Studio", 11, False, grey)
    buf = io.BytesIO()
    prs.save(buf)
    return buf.getvalue()


def pitch_deck_financials():
    from pptx.chart.data import CategoryChartData  # noqa: F401  (import check)
    from pptx.enum.chart import XL_CHART_TYPE
    return _deck("EDIT: Company name: financial story", "Pitch deck: the financial slides investors read first", [
        dict(title="Traction: the numbers so far", bullets=["EDIT: Revenue to date: ₹____ (last 6 months)", "EDIT: Customers / users: ____ (growth ____% per month)", "EDIT: Repeat rate or retention: ____%", "EDIT: Key milestone achieved: ____"], note="Use real, checkable numbers. Investors will ask for the proof."),
        dict(title="How we make money", bullets=["EDIT: Who pays, for what, how often", "EDIT: Price per customer: ₹____", "EDIT: Cost to serve one customer: ₹____", "EDIT: Gross margin: ____%"]),
        dict(title="Unit economics", kind="table", header=["Metric", "Value", "How calculated"], rows=[["Customer acquisition cost (CAC)", "₹____", "Marketing + sales spend ÷ new customers"], ["Average revenue per customer per year", "₹____", "Total revenue ÷ customers"], ["Gross margin %", "____%", "(Revenue - direct cost) ÷ revenue"],
                                                                                           ["Customer lifetime value (LTV)", "₹____", "Annual revenue × margin × years retained"], ["LTV : CAC", "____ : 1", "Healthy is 3 : 1 or better"], ["Payback period", "____ months", "CAC ÷ monthly margin per customer"]]),
        dict(title="Three-year projection", kind="chart", type=XL_CHART_TYPE.COLUMN_CLUSTERED, cats=["Year 1", "Year 2", "Year 3"], series=[("Revenue (₹ lakh)", (12, 18, 26)), ("Net profit (₹ lakh)", (-1, 2.5, 6))],
             bullets=["EDIT: Revenue grows ____% a year because ____", "EDIT: Break-even in month ____", "Replace the sample bars: right-click the chart > Edit data.", "Use the financial projections workbook for your numbers."]),
        dict(title="Use of funds", kind="chart", type=XL_CHART_TYPE.PIE, cats=["Product", "Marketing", "Team", "Operations"], series=[("Share of funds", (35, 30, 25, 10))], bullets=["EDIT: Raising ₹____ for ____ months of runway", "EDIT: What each bucket will achieve", "EDIT: Milestone this funding unlocks"]),
        dict(title="Milestones and the ask", bullets=["EDIT: Next 6 months: ____", "EDIT: Next 12 months: ____", "EDIT: Funding ask: ₹____ for ____% equity / as a loan", "EDIT: How we will report progress to investors"], note="Know your numbers cold. Be honest about risks."),
    ])


def powerpoint_template():
    from pptx.enum.chart import XL_CHART_TYPE
    return _deck("EDIT: Presentation title", "EDIT: One line saying why this matters to the audience", [
        dict(title="Agenda", bullets=["EDIT: Where we are today", "EDIT: What we found", "EDIT: What we recommend", "EDIT: Next steps"], note="Tip: one idea per slide, six lines at most, large text."),
        dict(title="The situation", bullets=["EDIT: Context in one sentence", "EDIT: The problem or opportunity", "EDIT: Why it matters now"]),
        dict(title="Key findings", kind="chart", type=XL_CHART_TYPE.COLUMN_CLUSTERED, cats=["Q1", "Q2", "Q3", "Q4"], series=[("This year", (40, 52, 61, 75)), ("Last year", (35, 44, 50, 58))], bullets=["EDIT: Say what the chart shows in one line", "EDIT: Call out the biggest change", "Right-click chart > Edit data to use your numbers."]),
        dict(title="Options compared", kind="table", header=["Option", "Cost", "Benefit", "Risk"], rows=[["EDIT: Option A", "", "", ""], ["EDIT: Option B", "", "", ""], ["EDIT: Option C", "", "", ""]]),
        dict(title="Recommendation", bullets=["EDIT: What you recommend, in one sentence", "EDIT: Why (3 reasons)", "EDIT: What it will cost and return"]),
        dict(title="Next steps", kind="table", header=["Action", "Owner", "Due date"], rows=[["EDIT", "", ""], ["EDIT", "", ""], ["EDIT", "", ""]]),
        dict(title="Thank you · Questions?", bullets=["EDIT: Name · email · phone", "EDIT: Where to find more detail"]),
    ])


def deck_tips():
    return make("Presentation design tips and slide copy guide", "How to make the template look professional in 30 minutes.", [
        ("Structure that works", [("n", ["Title, agenda, situation, findings, options, recommendation, next steps, questions.", "Put the answer first for senior audiences (executive summary), then the proof.", "One message per slide: write the slide title as a sentence that states the message."])]),
        ("Design rules", [("b", ["Minimum 24 pt body text; 32 pt+ titles.", "Maximum 6 lines per slide, 6 words per line when you can.", "Two colours plus grey; keep fonts consistent.", "Use a chart instead of a table of numbers; label axes and units.", "One image per slide, large; no clip-art.", "Leave white space."])]),
        ("Chart checklist", [("c", ["Title says the insight ('Sales grew 29%'), not the topic.", "Axis starts at zero for bars.", "Source and date under the chart.", "Highlight the one bar or line that matters."])]),
        ("Delivering", [("b", ["Practise out loud twice and time yourself.", "Speak to the audience, not the slide.", "Prepare backup slides for likely questions.", "Export a PDF as well as the PPTX."])]),
    ])


def pitch_deck_notes():
    return make("Pitch deck financial slides: speaker notes and checklist", "What to say on each slide and what investors will check.", [
        ("Slide by slide", [("t", ["Slide", "Say this", "They will ask"], [["Traction", "Facts only: revenue, customers, growth, repeat rate.", "Can I see bank statements or invoices?"], ["How we make money", "Who pays, how much, how often.", "Why will they keep paying?"],
                                                                         ["Unit economics", "CAC, LTV, margin, payback.", "How did you calculate CAC?"], ["Projection", "Three-year view, main assumptions.", "What if growth is half?"],
                                                                         ["Use of funds", "Where each rupee goes and what it unlocks.", "What if you raise less?"], ["Ask", "Amount, terms, milestones.", "Who else is investing?"]])]),
        ("Checklist before sending", [("c", ["All numbers tie to your bank statements and accounts.", "Assumptions are written down.", "A cautious case exists.", "Founder salary and taxes are included.", "Typos checked; PDF exported."])]),
    ])
