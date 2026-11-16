"""More Excel kits: ready-to-use trackers (built on the tracker engine) and bespoke workbooks."""

from __future__ import annotations

import datetime as dt
import random

from openpyxl.chart import Reference
from openpyxl.formatting.rule import FormulaRule
from openpyxl.styles import Alignment, Font, PatternFill

from lib import BORDER, FIRST, GREEN, LAST, MONEY, PCT, bar, calc, col, dropdown, head, inp, new_wb, start_sheet, title, widths
from xlsx_core import MONTHS, tracker

D = dt.date
rnd = random.Random(7)


def dates(n, start=D(2026, 1, 3), step=3):
    return [start + dt.timedelta(days=i * step) for i in range(n)]


def F(n, k, w=16, **kw):
    return dict(n=n, k=k, w=w, **kw)


# ---------------------------------------------------------------------------- tracker-based kits
def custom_dashboard():
    return tracker("Custom Excel dashboard", "Type your records in Data; the Summary sheet is your one-screen dashboard.", [
        F("Date", "date", 14, s=dates(10)), F("Category", "list", 16, o=["Sales", "Marketing", "Operations", "Payroll", "Other"],
                                              s=["Sales", "Marketing", "Operations", "Sales", "Payroll", "Sales", "Other", "Marketing", "Sales", "Operations"]),
        F("Description", "text", 28, s=["Order A101", "Social ads", "Packaging", "Order A102", "Staff pay", "Order A103", "Misc", "Flyers", "Order A104", "Courier"]),
        F("Amount", "money", 14, s=[12000, 3000, 1800, 9500, 25000, 14500, 700, 1200, 8800, 950]),
        F("Status", "list", 12, o=["Done", "Pending"], s=["Done", "Done", "Done", "Pending", "Done", "Done", "Done", "Pending", "Done", "Done"])],
        "Amount", "Category", "Date", kpis=[("Pending amount", '=SUMIFS([Amount],[Status],"Pending")', MONEY)])


def sales_tracker():
    prods = ["Product A", "Product B", "Product C", "Service pack"]
    return tracker("Sales tracking dashboard", "Add every sale as a row. Amount is calculated from quantity and rate.", [
        F("Date", "date", 14, s=dates(10, step=2)), F("Invoice no", "text", 12, s=[f"INV-{101 + i}" for i in range(10)]),
        F("Customer", "text", 22, s=["Ravi Stores", "Meena Traders", "Arun & Co", "Kavya Boutique", "Ravi Stores", "Selvi Mart", "Arun & Co", "Meena Traders", "Kavya Boutique", "Ravi Stores"]),
        F("Product", "list", 16, o=prods, s=[prods[i % 4] for i in range(10)]), F("Salesperson", "list", 14, o=["Anand", "Priya", "Karthik"], s=["Anand", "Priya", "Karthik", "Anand", "Priya", "Karthik", "Anand", "Priya", "Karthik", "Anand"]),
        F("Qty", "num", 8, s=[10, 4, 20, 2, 12, 6, 15, 3, 9, 7]), F("Rate", "money", 12, s=[450, 1200, 300, 2500, 450, 1200, 300, 2500, 450, 1200]),
        F("Amount", "formula", 14, f='=IF(F{r}="","",F{r}*G{r})', fmt=MONEY), F("Status", "list", 12, o=["Paid", "Pending"], s=["Paid", "Paid", "Pending", "Paid", "Paid", "Pending", "Paid", "Paid", "Paid", "Pending"])],
        "Amount", "Product", "Date", kpis=[("Pending payments", '=SUMIFS([Amount],[Status],"Pending")', MONEY), ("Paid so far", '=SUMIFS([Amount],[Status],"Paid")', MONEY)])


def inventory():
    cats = ["Grocery", "Stationery", "Electronics", "Other"]
    return tracker("Inventory / stock tracker", "One row per item. Closing stock, status and stock value are calculated.", [
        F("Item", "text", 24, s=["Rice 25kg", "Notebook A4", "USB cable", "Pen box", "Charger", "Sugar 1kg", "Marker set", "Earphones"]),
        F("Category", "list", 14, o=cats, s=["Grocery", "Stationery", "Electronics", "Stationery", "Electronics", "Grocery", "Stationery", "Electronics"]),
        F("Unit cost", "money", 12, s=[1100, 40, 90, 60, 250, 45, 120, 180]), F("Opening", "num", 10, s=[40, 200, 60, 80, 30, 120, 25, 45]),
        F("Received", "num", 10, s=[20, 100, 0, 40, 0, 60, 10, 20]), F("Issued", "num", 10, s=[35, 260, 25, 90, 22, 150, 20, 30]),
        F("Closing", "formula", 10, f='=IF(D{r}="","",D{r}+E{r}-F{r})', fmt="0"), F("Reorder level", "num", 12, s=[15, 80, 20, 30, 10, 50, 10, 15]),
        F("Status", "formula", 12, f='=IF(A{r}="","",IF(G{r}<=H{r},"Reorder","OK"))', cf_text={"Reorder": "FFC7CE"}),
        F("Stock value", "formula", 14, f='=IF(A{r}="","",G{r}*C{r})', fmt=MONEY)],
        "Stock value", "Category", None, kpis=[("Items to reorder", '=COUNTIF([Status],"Reorder")', "0")],
        steps=["Data sheet: list each item with its unit cost, opening stock, quantity received and quantity issued.",
               "Closing stock, Reorder status and stock value calculate by themselves. Red = reorder now.",
               "Summary sheet: total stock value, number of items to reorder and value by category.",
               "At the start of each month, copy Closing into Opening and clear Received and Issued."])


def shop_expenses():
    cats = ["Rent", "Stock purchase", "Salaries", "Electricity", "Transport", "Repairs", "Marketing", "Other"]
    return tracker("Expense tracker for shops", "Enter every shop expense. See where the money goes each month.", [
        F("Date", "date", 14, s=dates(10, step=2)), F("Category", "list", 16, o=cats, s=[cats[i % 8] for i in range(10)]),
        F("Paid to", "text", 22, s=["Landlord", "Wholesaler", "Staff", "TNEB", "Auto", "Mechanic", "Printer", "Misc"] * 2),
        F("Payment mode", "list", 14, o=["Cash", "UPI", "Bank transfer", "Card"], s=["Bank transfer", "UPI", "Cash", "UPI", "Cash", "Cash", "UPI", "Cash"]),
        F("Amount", "money", 14, s=[12000, 45000, 18000, 2400, 800, 1500, 2000, 600, 12000, 38000]), F("Note", "text", 28)],
        "Amount", "Category", "Date")


def coaching_dashboard():
    courses = ["NEET", "JEE", "TNPSC", "Spoken English", "Other"]
    return tracker("Coaching centre fee and admission dashboard", "One row per student. Balance and fee status are calculated.", [
        F("Admission date", "date", 16, s=dates(10, step=4)), F("Student", "text", 22, s=["Arun", "Divya", "Karthik", "Meena", "Suresh", "Nisha", "Vijay", "Lakshmi", "Hari", "Pooja"]),
        F("Course", "list", 16, o=courses, s=[courses[i % 5] for i in range(10)]), F("Total fee", "money", 14, s=[30000, 28000, 12000, 6000, 30000, 28000, 12000, 6000, 30000, 12000]),
        F("Fee paid", "money", 14, s=[30000, 14000, 12000, 3000, 10000, 28000, 6000, 6000, 15000, 12000]),
        F("Balance", "formula", 12, f='=IF(D{r}="","",D{r}-E{r})', fmt=MONEY), F("Fee status", "formula", 14, f='=IF(D{r}="","",IF(F{r}<=0,"Paid",IF(E{r}=0,"Not paid","Part paid")))', cf_text={"Not paid": "FFC7CE", "Part paid": "FFE5B4"})],
        "Fee paid", "Course", "Admission date", kpis=[("Total fees due (all students)", "=SUM([Total fee])", MONEY), ("Balance still to collect", "=SUM([Balance])", MONEY),
                                                       ("Students admitted", "=COUNTA([Student])", "0"), ("Students with pending fee", '=COUNTIF([Fee status],"Part paid")+COUNTIF([Fee status],"Not paid")', "0")])


def restaurant():
    cats = ["Dine-in sales", "Takeaway", "Delivery apps", "Ingredients", "Staff", "Rent", "Gas and utilities", "Other"]
    return tracker("Restaurant revenue and expense dashboard", "Enter daily takings and costs. Net amount shows profit (sales positive, expenses negative).", [
        F("Date", "date", 14, s=dates(12, step=1)), F("Type", "list", 12, o=["Revenue", "Expense"], s=["Revenue", "Revenue", "Revenue", "Expense", "Expense", "Revenue", "Revenue", "Revenue", "Expense", "Expense", "Revenue", "Expense"]),
        F("Category", "list", 18, o=cats, s=["Dine-in sales", "Takeaway", "Delivery apps", "Ingredients", "Staff", "Dine-in sales", "Takeaway", "Delivery apps", "Rent", "Gas and utilities", "Dine-in sales", "Other"]),
        F("Amount", "money", 14, s=[14500, 3200, 5400, 9800, 7000, 15800, 3600, 4900, 25000, 2800, 16200, 1200]), F("Note", "text", 24),
        F("Net amount", "formula", 14, f='=IF(D{r}="","",IF(B{r}="Expense",-D{r},D{r}))', fmt=MONEY)],
        "Net amount", "Category", "Date", share=False, kpis=[("Total revenue", '=SUMIFS([Amount],[Type],"Revenue")', MONEY), ("Total expenses", '=SUMIFS([Amount],[Type],"Expense")', MONEY),
                                               ("Profit margin", '=IFERROR(SUM([Net amount])/SUMIFS([Amount],[Type],"Revenue"),0)', PCT)])


def retail_profit():
    cats = ["Clothing", "Footwear", "Accessories", "Other"]
    return tracker("Retail shop profit dashboard", "One row per sale. Revenue, profit and margin calculate from price and cost.", [
        F("Date", "date", 14, s=dates(10, step=2)), F("Product", "text", 22, s=["T-shirt", "Jeans", "Sandals", "Belt", "Kurta", "Sports shoes", "Wallet", "Saree", "Cap", "Shirt"]),
        F("Category", "list", 14, o=cats, s=["Clothing", "Clothing", "Footwear", "Accessories", "Clothing", "Footwear", "Accessories", "Clothing", "Accessories", "Clothing"]),
        F("Qty", "num", 8, s=[3, 2, 4, 6, 2, 1, 5, 2, 4, 3]), F("Selling price", "money", 14, s=[499, 1299, 699, 399, 899, 2499, 499, 2999, 249, 799]),
        F("Cost price", "money", 14, s=[300, 800, 420, 220, 520, 1600, 280, 1900, 120, 450]),
        F("Revenue", "formula", 14, f='=IF(D{r}="","",D{r}*E{r})', fmt=MONEY), F("Profit", "formula", 14, f='=IF(D{r}="","",D{r}*(E{r}-F{r}))', fmt=MONEY)],
        "Profit", "Category", "Date", kpis=[("Total revenue", "=SUM([Revenue])", MONEY), ("Overall margin", "=IFERROR(SUM([Profit])/SUM([Revenue]),0)", PCT)])


def monthly_log():
    return tracker("Monthly figures log", "Add one row per month. Profit is calculated. Use with your dashboard each month.", [
        F("Month", "date", 14, s=[D(2026, m, 1) for m in range(1, 7)]), F("Revenue", "money", 14, s=[420000, 450000, 480000, 460000, 520000, 540000]),
        F("Expenses", "money", 14, s=[360000, 380000, 395000, 410000, 430000, 440000]),
        F("Profit", "formula", 14, f='=IF(B{r}="","",B{r}-C{r})', fmt=MONEY), F("Notes", "text", 30)],
        "Profit", None, "Month", first_month=D(2026, 1, 1),
        kpis=[("Total revenue", "=SUM([Revenue])", MONEY), ("Total expenses", "=SUM([Expenses])", MONEY)],
        steps=["Add one row each month: month (1st of month), revenue and expenses. Profit calculates by itself.",
               "Open Summary to see total and monthly profit as a chart.",
               "Follow the Monthly update checklist (Word file) on the same day each month.",
               "Keep this workbook; the history is what makes your dashboard valuable."])


def lead_tracker():
    st = ["New", "Contacted", "Meeting set", "Quote sent", "Won", "Lost"]
    return tracker("Lead / enquiry tracker", "One row per enquiry. Follow-ups that are overdue are counted on Summary.", [
        F("Date", "date", 14, s=dates(10, step=2)), F("Name", "text", 20, s=["Ravi", "Meena", "Arun", "Kavya", "Selvi", "Hari", "Divya", "Karthik", "Pooja", "Vijay"]),
        F("Phone", "text", 14, s=[f"98765432{10 + i}" for i in range(10)]), F("Source", "list", 14, o=["Website", "Instagram", "Referral", "WhatsApp", "Walk-in", "Other"], s=["Website", "Instagram", "Referral", "WhatsApp", "Walk-in", "Website", "Instagram", "Referral", "WhatsApp", "Other"]),
        F("Status", "list", 14, o=st, s=["Won", "Quote sent", "Contacted", "New", "Lost", "Meeting set", "Won", "New", "Contacted", "Quote sent"]),
        F("Next follow-up", "date", 16, s=[f"=TODAY()+{i * 2 - 3}" for i in range(10)]), F("Expected value", "money", 14, s=[15000, 8000, 22000, 5000, 12000, 30000, 9000, 6000, 18000, 7000]),
        F("Notes", "text", 28)],
        "Expected value", "Status", "Date", kpis=[("Won value", '=SUMIFS([Expected value],[Status],"Won")', MONEY),
                                                  ("Overdue follow-ups", '=COUNTIFS([Next follow-up],"<"&TODAY(),[Status],"<>Won",[Status],"<>Lost")', "0")])


def appointments():
    sv = ["Consultation", "Haircut", "Facial", "Check-up", "Class", "Other"]
    return tracker("Appointment / booking tracker", "One row per booking. Status and fee roll up on Summary.", [
        F("Date", "date", 14, s=dates(10, step=1)), F("Time", "text", 10, s=["10:00", "11:30", "14:00", "15:30", "09:00", "16:30", "12:00", "17:00", "10:30", "13:00"]),
        F("Client", "text", 20, s=["Asha", "Ravi", "Meena", "Kumar", "Divya", "Hari", "Priya", "Arun", "Nisha", "Vijay"]), F("Service", "list", 16, o=sv, s=[sv[i % 6] for i in range(10)]),
        F("Status", "list", 12, o=["Booked", "Completed", "Cancelled", "No-show"], s=["Completed", "Completed", "Booked", "Completed", "Cancelled", "Completed", "Booked", "No-show", "Completed", "Booked"]),
        F("Fee", "money", 12, s=[500, 300, 800, 400, 600, 300, 800, 400, 500, 600]), F("Phone", "text", 14)],
        "Fee", "Service", "Date", kpis=[("Completed fees", '=SUMIFS([Fee],[Status],"Completed")', MONEY), ("Cancellations and no-shows", '=COUNTIF([Status],"Cancelled")+COUNTIF([Status],"No-show")', "0")])


def data_entry_system():
    cities = ["Madurai", "Chennai", "Coimbatore", "Trichy", "Salem", "Other"]
    prods = ["Item A", "Item B", "Item C"]
    return tracker("Data entry system with dropdowns and validation", "Fill each row using the dropdowns. Duplicates and missing fields are flagged automatically.", [
        F("Entry date", "date", 14, s=dates(8, step=1)), F("Customer", "text", 22, s=["Ravi", "Meena", "Arun", "Kavya", "Ravi", "Selvi", "Hari", "Divya"]),
        F("City", "list", 14, o=cities, s=[cities[i % 6] for i in range(8)]), F("Product", "list", 12, o=prods, s=[prods[i % 3] for i in range(8)]),
        F("Qty", "num", 8, s=[2, 5, 1, 4, 2, 7, 3, 6]), F("Price", "money", 12, s=[450, 1200, 300, 450, 450, 1200, 300, 450]),
        F("Total", "formula", 12, f='=IF(OR(E{r}="",F{r}=""),"",E{r}*F{r})', fmt=MONEY), F("Entered by", "list", 12, o=["Anand", "Priya", "Karthik"], s=["Anand", "Priya", "Anand", "Karthik", "Priya", "Anand", "Karthik", "Priya"]),
        F("Check", "formula", 18, f='=IF(B{r}="","",IF(OR(C{r}="",D{r}="",E{r}="",F{r}=""),"Missing field",IF(COUNTIFS($B${f}:$B${l},B{r},$A${f}:$A${l},A{r},$D${f}:$D${l},D{r})>1,"Possible duplicate","OK")))'.replace("{f}", str(FIRST)).replace("{l}", str(LAST)), cf_text={"Missing field": "FFC7CE", "Possible duplicate": "FFE5B4"})],
        "Total", "Product", "Entry date", kpis=[("Rows needing attention", '=COUNTIF([Check],"Missing field")+COUNTIF([Check],"Possible duplicate")', "0")])


def maintenance_log():
    tasks = ["Backup site", "Update plugins/software", "Check broken links", "Check forms work", "Speed test", "Security scan", "Content change", "Other"]
    return tracker("Website maintenance log", "Record each maintenance task so you can show the owner what was done.", [
        F("Date", "date", 14, s=dates(8, step=7)), F("Task", "list", 24, o=tasks, s=tasks), F("Page / URL", "text", 24, s=["/", "/", "/contact", "/contact", "/", "/", "/about", "/"]),
        F("Done by", "text", 14, s=["Viswa"] * 8), F("Time spent (hrs)", "num", 14, s=[0.5, 1, 0.5, 0.25, 0.5, 0.5, 1, 0.5]), F("Status", "list", 12, o=["Done", "In progress", "Blocked"], s=["Done"] * 8),
        F("Notes", "text", 28)],
        "Time spent (hrs)", "Task", "Date")


def form_responses():
    return tracker("Form responses tracker", "Google Form answers land here. Add the Status and Follow-up columns to track each enquiry.", [
        F("Timestamp", "date", 18, s=dates(6, step=1)), F("Name", "text", 20, s=["Asha", "Ravi", "Meena", "Kumar", "Divya", "Hari"]), F("Email", "text", 28, s=[f"person{i}@example.com" for i in range(6)]),
        F("Phone", "text", 14), F("Message", "text", 36, s=["Need a quote", "Website enquiry", "Call me", "Price list please", "Demo request", "Need help"] ),
        F("Status", "list", 14, o=["New", "Replied", "Closed"], s=["Replied", "New", "New", "Closed", "New", "Replied"]), F("Value", "money", 12)],
        "Value", "Status", "Timestamp")


def weekly_sales():
    wb = sales_tracker()
    ws = wb.create_sheet("Weekly report")
    ws.sheet_view.showGridLines = False
    title(ws, "Weekly sales report", "Type the Monday of the first week. The report fills itself from the Data sheet.")
    ws["A3"], ws["B3"] = "First Monday", D(2025, 12, 29)
    inp(ws["B3"], "dd-mmm-yyyy")
    head(ws, 5, ["Week starting", "Sales", "Orders", "Average order", "Change vs previous week"])
    widths(ws, [18, 16, 10, 16, 22])
    for i in range(12):
        r = 6 + i
        calc(ws.cell(row=r, column=1, value=f"=$B$3+{7 * i}"), "dd-mmm-yyyy")
        calc(ws.cell(row=r, column=2, value=f'=SUMIFS(Data!$H$5:$H$1004,Data!$A$5:$A$1004,">="&A{r},Data!$A$5:$A$1004,"<"&A{r}+7)'), MONEY)
        calc(ws.cell(row=r, column=3, value=f'=COUNTIFS(Data!$A$5:$A$1004,">="&A{r},Data!$A$5:$A$1004,"<"&A{r}+7)'), "0")
        calc(ws.cell(row=r, column=4, value=f"=IFERROR(B{r}/C{r},0)"), MONEY)
        calc(ws.cell(row=r, column=5, value="" if i == 0 else f'=IFERROR(B{r}/B{r - 1}-1,"")'), PCT)
    bar(ws, "G3", "Weekly sales", Reference(ws, min_col=1, min_row=6, max_row=17), Reference(ws, min_col=2, min_row=5, max_row=17))
    return wb


# ---------------------------------------------------------------------------- bespoke workbooks
def gst_invoice():
    wb = new_wb()
    iv = wb.create_sheet("Invoice")
    iv.sheet_view.showGridLines = False
    title(iv, "TAX INVOICE", "Fill the yellow cells and print. Check current GST rules with your CA before filing.")
    widths(iv, [6, 34, 12, 8, 12, 10, 14, 14])
    for r, (l, v) in enumerate([("Seller name", "Your Business Name"), ("Seller GSTIN", "33ABCDE1234F1Z5"), ("Seller state", "Tamil Nadu"),
                                ("Invoice no", "INV-001"), ("Invoice date", D(2026, 1, 15)), ("Buyer name", "Customer Name"), ("Buyer GSTIN", ""), ("Buyer state", "Tamil Nadu")], start=3):
        iv.cell(row=r, column=2, value=l).font = Font(bold=True)
        c = iv.cell(row=r, column=3, value=v)
        inp(c, "dd-mmm-yyyy" if isinstance(v, dt.date) else None)
        iv.merge_cells(start_row=r, start_column=3, end_row=r, end_column=5)
    head(iv, 12, ["#", "Description", "HSN/SAC", "Qty", "Rate", "GST %", "Taxable value", "GST amount"])
    items = [("Product A", "1234", 10, 500, 0.18), ("Service charge", "9983", 1, 2000, 0.18), ("Product B", "5678", 4, 250, 0.12)]
    for i in range(10):
        r = 13 + i
        calc(iv.cell(row=r, column=1, value=i + 1))
        for c in range(2, 7):
            v = items[i][c - 2] if i < len(items) else None
            inp(iv.cell(row=r, column=c, value=v), "0%" if c == 6 else (MONEY if c == 5 else None))
        calc(iv.cell(row=r, column=7, value=f'=IF(D{r}="","",D{r}*E{r})'), MONEY)
        calc(iv.cell(row=r, column=8, value=f'=IF(G{r}="","",G{r}*F{r})'), MONEY)
    tr = 23
    labels = [("Taxable value", "=SUM(G13:G22)"), ("CGST", '=IF(C5=C10,SUM(H13:H22)/2,0)'), ("SGST", '=IF(C5=C10,SUM(H13:H22)/2,0)'),
              ("IGST", '=IF(C5<>C10,SUM(H13:H22),0)'), ("Invoice total", "=SUM(G24:G27)")]
    for i, (l, f) in enumerate(labels):
        iv.cell(row=tr + 1 + i, column=6, value=l).font = Font(bold=True)
        iv.merge_cells(start_row=tr + 1 + i, start_column=6, end_row=tr + 1 + i, end_column=6)
        calc(iv.cell(row=tr + 1 + i, column=7, value=f), MONEY, True)
    iv["G24"], iv["G25"], iv["G26"], iv["G27"], iv["G28"] = "=SUM(G13:G22)", labels[1][1], labels[2][1], labels[3][1], "=G24+G25+G26+G27"
    iv["A30"] = "Same state: CGST + SGST are split automatically. Different state: IGST. Declaration: goods/services as described; subject to local jurisdiction."
    rg = wb.create_sheet("Sales register")
    title(rg, "GST sales register", "One row per invoice. Totals and monthly tax summary calculate by themselves.")
    head(rg, 4, ["Invoice no", "Date", "Buyer", "Buyer GSTIN", "Taxable value", "CGST", "SGST", "IGST", "Total"])
    widths(rg, [14, 14, 24, 20, 14, 12, 12, 12, 14])
    sample = [("INV-001", D(2026, 1, 15), "Ravi Stores", "33AAAAA1111A1Z1", 6000), ("INV-002", D(2026, 1, 20), "Meena Traders", "33BBBBB2222B1Z2", 12000), ("INV-003", D(2026, 2, 3), "Arun & Co", "29CCCCC3333C1Z3", 8500)]
    for r in range(5, 505):
        for c in range(1, 6):
            cell = rg.cell(row=r, column=c)
            if r - 5 < len(sample):
                cell.value = sample[r - 5][c - 1]
            inp(cell, "dd-mmm-yyyy" if c == 2 else (MONEY if c == 5 else None))
        calc(rg.cell(row=r, column=6, value=f'=IF(E{r}="","",IF(LEFT(D{r},2)="33",E{r}*0.09,0))'), MONEY)
        calc(rg.cell(row=r, column=7, value=f'=IF(E{r}="","",IF(LEFT(D{r},2)="33",E{r}*0.09,0))'), MONEY)
        calc(rg.cell(row=r, column=8, value=f'=IF(E{r}="","",IF(LEFT(D{r},2)="33",0,E{r}*0.18))'), MONEY)
        calc(rg.cell(row=r, column=9, value=f'=IF(E{r}="","",E{r}+F{r}+G{r}+H{r})'), MONEY)
    rg["K4"] = "Register assumes 18% GST and seller in state code 33 (Tamil Nadu). Edit the formulas for other rates or states."
    rg["K4"].font = Font(italic=True, color="5B6770")
    sm = wb.create_sheet("Monthly summary")
    title(sm, "Monthly GST summary", "Type the first day of a month to see that month's tax.")
    sm["A3"], sm["B3"] = "Month", D(2026, 1, 1)
    inp(sm["B3"], "mmm-yyyy")
    for i, (l, c) in enumerate([("Taxable value", "E"), ("CGST", "F"), ("SGST", "G"), ("IGST", "H"), ("Total invoiced", "I")]):
        sm.cell(row=5 + i, column=1, value=l).font = Font(bold=True)
        calc(sm.cell(row=5 + i, column=2, value=f"=SUMIFS('Sales register'!${c}$5:${c}$504,'Sales register'!$B$5:$B$504,\">=\"&$B$3,'Sales register'!$B$5:$B$504,\"<\"&EDATE($B$3,1))"), MONEY, True)
    widths(sm, [22, 16])
    start_sheet(wb, "Start here", "GST invoice and register template", [
        "Invoice sheet: type your details, the buyer's details, and each item with its GST %. CGST/SGST or IGST is chosen from the two states.",
        "Print the Invoice sheet or save it as PDF to send to the customer.",
        "Copy each invoice's totals into the Sales register (one row per invoice).",
        "Monthly summary shows the month's taxable value and GST to help prepare your return. Confirm all figures and rules with your CA.",
    ])
    return wb


def invoice_generator():
    wb = new_wb()
    cu = wb.create_sheet("Customers")
    title(cu, "Customer list", "Add your regular customers. Pick them on the Invoice sheet.")
    head(cu, 4, ["Customer", "Address", "Phone"])
    widths(cu, [26, 40, 16])
    for i, row in enumerate([("Ravi Stores", "12 Main Road, Madurai", "9876543210"), ("Meena Traders", "45 Market St, Madurai", "9876543211")] + [("", "", "")] * 28):
        for c, v in enumerate(row, start=1):
            inp(cu.cell(row=5 + i, column=c, value=v or None))
    it = wb.create_sheet("Items")
    title(it, "Item list", "Items and prices you sell. Picked on the Invoice sheet.")
    head(it, 4, ["Item", "Rate"])
    widths(it, [30, 14])
    for i, row in enumerate([("Consulting hour", 1500), ("Excel dashboard", 3500), ("Website page", 2500)] + [("", None)] * 27):
        inp(it.cell(row=5 + i, column=1, value=row[0] or None))
        inp(it.cell(row=5 + i, column=2, value=row[1]), MONEY)
    iv = wb.create_sheet("Invoice")
    iv.sheet_view.showGridLines = False
    title(iv, "INVOICE", "Pick the customer and items from the dropdowns. Rate and totals fill in by themselves.")
    widths(iv, [6, 34, 14, 12, 14, 14])
    for r, (l, v) in enumerate([("Invoice no", "INV-001"), ("Date", D(2026, 1, 15)), ("Customer", "Ravi Stores")], start=3):
        iv.cell(row=r, column=2, value=l).font = Font(bold=True)
        inp(iv.cell(row=r, column=3, value=v), "dd-mmm-yyyy" if isinstance(v, dt.date) else None)
    iv["B6"], iv["C6"] = "Address", '=IFERROR(VLOOKUP(C5,Customers!$A$5:$C$34,2,FALSE),"")'
    calc(iv["C6"])
    from openpyxl.worksheet.datavalidation import DataValidation
    dv = DataValidation(type="list", formula1="=Customers!$A$5:$A$34", allow_blank=True)
    iv.add_data_validation(dv)
    dv.add("C5")
    dv2 = DataValidation(type="list", formula1="=Items!$A$5:$A$34", allow_blank=True)
    iv.add_data_validation(dv2)
    head(iv, 8, ["#", "Item", "Qty", "Rate", "Amount", ""])
    for i in range(10):
        r = 9 + i
        calc(iv.cell(row=r, column=1, value=i + 1))
        inp(iv.cell(row=r, column=2, value=["Excel dashboard", "Consulting hour", None][i] if i < 3 else None))
        inp(iv.cell(row=r, column=3, value=[1, 3, None][i] if i < 3 else None))
        dv2.add(f"B{r}")
        calc(iv.cell(row=r, column=4, value=f'=IF(B{r}="","",IFERROR(VLOOKUP(B{r},Items!$A$5:$B$34,2,FALSE),""))'), MONEY)
        calc(iv.cell(row=r, column=5, value=f'=IF(OR(C{r}="",D{r}=""),"",C{r}*D{r})'), MONEY)
    iv["D20"], iv["D21"], iv["D22"] = "Subtotal", "Discount %", "Total"
    iv["E20"], iv["E21"], iv["E22"] = "=SUM(E9:E18)", 0, "=E20*(1-E21)"
    calc(iv["E20"], MONEY, True)
    inp(iv["E21"], "0%")
    calc(iv["E22"], MONEY, True)
    for c in ("D20", "D21", "D22"):
        iv[c].font = Font(bold=True)
    lg = wb.create_sheet("Invoice log")
    title(lg, "Invoice log", "Record each invoice you send and when it is paid.")
    head(lg, 4, ["Invoice no", "Date", "Customer", "Total", "Paid?", "Paid on"])
    widths(lg, [14, 14, 24, 14, 10, 14])
    for r in range(5, 205):
        for c in range(1, 7):
            inp(lg.cell(row=r, column=c), MONEY if c == 4 else ("dd-mmm-yyyy" if c in (2, 6) else None))
    dropdown(lg, "E5:E204", ["Yes", "No"])
    start_sheet(wb, "Start here", "Invoice generator", [
        "Customers and Items sheets: add your customers and your items with rates once.",
        "Invoice sheet: change the invoice number and date, pick the customer and items from the dropdowns, type quantities.",
        "Print or save the Invoice sheet as PDF and send it. For the next invoice, just change the yellow cells.",
        "Record every invoice in the Invoice log so you know who has not paid.",
    ])
    return wb


def attendance_fees():
    wb = new_wb()
    st = wb.create_sheet("Students")
    title(st, "Student list and monthly fee", "Add each student and their monthly fee.")
    head(st, 4, ["#", "Student", "Class / batch", "Monthly fee", "Parent phone"])
    widths(st, [6, 24, 16, 14, 16])
    names = ["Arun", "Divya", "Karthik", "Meena", "Suresh", "Nisha", "Vijay", "Lakshmi", "Hari", "Pooja"]
    for i in range(40):
        r = 5 + i
        calc(st.cell(row=r, column=1, value=i + 1))
        inp(st.cell(row=r, column=2, value=names[i] if i < 10 else None))
        inp(st.cell(row=r, column=3, value=["Batch A", "Batch B"][i % 2] if i < 10 else None))
        inp(st.cell(row=r, column=4, value=1500 if i < 10 else None), MONEY)
        inp(st.cell(row=r, column=5))
    at = wb.create_sheet("Attendance")
    title(at, "Attendance (type P for present, A for absent)", "Change the month. Days run across. Attendance % is calculated.")
    at["A3"], at["B3"] = "Month (1st)", D(2026, 1, 1)
    inp(at["B3"], "mmm-yyyy")
    head(at, 4, ["Student"] + [str(d) for d in range(1, 32)] + ["Present", "Absent", "Attendance %"])
    widths(at, [22] + [4] * 31 + [9, 9, 13])
    at.freeze_panes = "B5"
    for i in range(40):
        r = 5 + i
        calc(at.cell(row=r, column=1, value=f'=IF(Students!B{5 + i}="","",Students!B{5 + i})'))
        for d in range(31):
            v = ("P" if (i + d) % 7 else "A") if i < 10 and d < 20 else None
            inp(at.cell(row=r, column=2 + d, value=v))
        calc(at.cell(row=r, column=33, value=f'=COUNTIF(B{r}:AF{r},"P")'), "0")
        calc(at.cell(row=r, column=34, value=f'=COUNTIF(B{r}:AF{r},"A")'), "0")
        calc(at.cell(row=r, column=35, value=f'=IF(AG{r}+AH{r}=0,"",AG{r}/(AG{r}+AH{r}))'), "0%")
    dropdown(at, "B5:AF44", ["P", "A"])
    at.conditional_formatting.add("B5:AF44", FormulaRule(formula=['B5="A"'], fill=PatternFill("solid", bgColor="FFC7CE", fgColor="FFC7CE")))
    at.conditional_formatting.add("AI5:AI44", FormulaRule(formula=['AND(AI5<>"",AI5<0.75)'], fill=PatternFill("solid", bgColor="FFC7CE", fgColor="FFC7CE")))
    fe = wb.create_sheet("Fees")
    title(fe, "Fee collection", "Type each month's amount paid. Balance and status calculate.")
    fe["A3"], fe["B3"] = "Month", "January 2026"
    inp(fe["B3"])
    head(fe, 4, ["Student", "Fee due", "Paid", "Balance", "Status", "Paid on"])
    widths(fe, [22, 12, 12, 12, 12, 14])
    for i in range(40):
        r = 5 + i
        calc(fe.cell(row=r, column=1, value=f'=IF(Students!B{5 + i}="","",Students!B{5 + i})'))
        calc(fe.cell(row=r, column=2, value=f'=IF(Students!B{5 + i}="","",Students!D{5 + i})'), MONEY)
        inp(fe.cell(row=r, column=3, value=[1500, 1500, 0, 750][i % 4] if i < 10 else None), MONEY)
        calc(fe.cell(row=r, column=4, value=f'=IF(A{r}="","",B{r}-C{r})'), MONEY)
        calc(fe.cell(row=r, column=5, value=f'=IF(A{r}="","",IF(D{r}<=0,"Paid",IF(C{r}=0,"Not paid","Part paid")))'))
        inp(fe.cell(row=r, column=6), "dd-mmm-yyyy")
    fe["H4"], fe["H5"], fe["H6"], fe["H7"] = "Totals", "Fees due", "Collected", "Balance"
    calc(fe["I5"], MONEY, True)
    fe["I5"], fe["I6"], fe["I7"] = "=SUM(B5:B44)", "=SUM(C5:C44)", "=SUM(D5:D44)"
    for c in ("I6", "I7"):
        calc(fe[c], MONEY, True)
    fe.conditional_formatting.add("E5:E44", FormulaRule(formula=['E5="Not paid"'], fill=PatternFill("solid", bgColor="FFC7CE", fgColor="FFC7CE")))
    start_sheet(wb, "Start here", "Student attendance and fee tracker", [
        "Students sheet: list each student, batch and monthly fee.",
        "Attendance sheet: pick the month, then type P or A for each day. Absent days turn red; attendance below 75% is highlighted.",
        "Fees sheet: type what each student paid this month. Balance and Paid / Part paid / Not paid are calculated.",
        "For a new month, save a copy of the workbook and clear the P/A cells and Paid column.",
    ])
    return wb


def content_calendar():
    wb = new_wb()
    ws = wb.create_sheet("30-day calendar")
    title(ws, "30-day social media content calendar", "Plan one post per day. Replace the sample ideas with your own business.")
    head(ws, 4, ["Day", "Date", "Platform", "Content type", "Topic / idea", "Caption (draft)", "Hashtags", "Status"])
    widths(ws, [6, 13, 14, 16, 30, 50, 26, 12])
    types = ["Educational tip", "Behind the scenes", "Customer story", "Offer / promotion", "Question / poll", "Product highlight", "Myth vs fact"]
    ideas = ["3 mistakes small shops make with cash", "How we prepare an order", "Thank you note from a happy customer", "This week's special offer", "What would you like to learn next?",
             "Meet our best-seller", "Myth: profit means cash in the bank"]
    for i in range(30):
        r = 5 + i
        calc(ws.cell(row=r, column=1, value=i + 1))
        inp(ws.cell(row=r, column=2, value=D(2026, 2, 1) + dt.timedelta(days=i)), "dd-mmm")
        inp(ws.cell(row=r, column=3, value=["LinkedIn", "Instagram", "Facebook"][i % 3]))
        inp(ws.cell(row=r, column=4, value=types[i % 7]))
        inp(ws.cell(row=r, column=5, value=ideas[i % 7]))
        inp(ws.cell(row=r, column=6, value="Write your caption here. Start with a hook, give one useful point, end with a question."))
        inp(ws.cell(row=r, column=7, value="#smallbusiness #finance #tips"))
        inp(ws.cell(row=r, column=8, value="Planned"))
    dropdown(ws, "C5:C34", ["LinkedIn", "Instagram", "Facebook", "YouTube", "X", "WhatsApp status"])
    dropdown(ws, "D5:D34", types + ["Video", "Reel"])
    dropdown(ws, "H5:H34", ["Planned", "Designed", "Scheduled", "Posted"])
    ws.freeze_panes = "A5"
    ws.conditional_formatting.add("H5:H34", FormulaRule(formula=['H5="Posted"'], fill=PatternFill("solid", bgColor="C6EFCE", fgColor="C6EFCE")))
    hk = wb.create_sheet("Caption templates")
    title(hk, "20 caption openers you can reuse")
    openers = ["The #1 mistake I see in [topic]: ...", "Stop doing [X]. Do this instead:", "Here's what [N] customers taught me about [topic].", "Most people think [myth]. The truth:",
               "3 quick tips for [audience]:", "Before and after: [result].", "A question for you: [question]?", "How we do [process] in [N] steps:", "Today's offer: [offer], until [date].",
               "Behind the scenes at [business]:", "What I wish I knew when I started:", "[Number] questions to ask before you buy [product]:", "Case study: how [customer] saved [amount/time].",
               "Quick win you can try today:", "A short story from this week:", "Hot take: [opinion].", "Checklist: [topic] in 5 minutes.", "Thank you to [customer] for [reason]!", "New: [product or service] is here.", "Weekend reading: [link or idea]."]
    for i, o in enumerate(openers):
        hk.cell(row=4 + i, column=1, value=f"{i + 1}. {o}")
    hk.column_dimensions["A"].width = 90
    ps = wb.create_sheet("Posting times")
    title(ps, "Best times to try (test and adjust)", "These are starting points, not rules. Check your own platform analytics.")
    head(ps, 4, ["Platform", "Try these times", "Notes"])
    widths(ps, [14, 24, 60])
    for i, row in enumerate([("LinkedIn", "Tue-Thu, 8-10 am", "Business audience reads before work."), ("Instagram", "11 am-1 pm, 7-9 pm", "Reels and carousels travel furthest."), ("Facebook", "1-4 pm", "Local groups and shops do well."),
                             ("WhatsApp status", "8-10 am, 6-8 pm", "Short offers and photos.")]):
        for c, v in enumerate(row, start=1):
            ps.cell(row=5 + i, column=c, value=v)
    start_sheet(wb, "Start here", "30-day social media content calendar", [
        "Open 30-day calendar. Replace the sample topics with ideas for your business (use the Caption templates sheet for openers).",
        "Pick the platform and content type from the dropdowns. Write your caption draft and hashtags.",
        "Update Status as you go: Planned, Designed, Scheduled, Posted (posted rows turn green).",
        "Use Posting times as a starting point and check your own analytics after two weeks.",
    ])
    return wb


def comparison_matrix():
    wb = new_wb()
    ws = wb.create_sheet("Comparison")
    ws.sheet_view.showGridLines = False
    title(ws, "Competitor comparison matrix", "Score yourself and 3 competitors from 1 (weak) to 5 (strong). Weighted score tells who leads.")
    head(ws, 4, ["Factor", "Weight %", "You", "Competitor A", "Competitor B", "Competitor C"])
    widths(ws, [28, 10, 10, 14, 14, 14])
    factors = [("Price", 25, 4, 3, 5, 2), ("Quality", 25, 4, 5, 3, 4), ("Range of products/services", 15, 3, 4, 3, 5), ("Service and support", 15, 5, 3, 3, 3),
               ("Brand and trust", 10, 2, 5, 3, 4), ("Location / reach", 10, 4, 3, 4, 3)]
    for i, (f, w, *s) in enumerate(factors):
        r = 5 + i
        inp(ws.cell(row=r, column=1, value=f))
        inp(ws.cell(row=r, column=2, value=w / 100), "0%")
        for c, v in enumerate(s, start=3):
            inp(ws.cell(row=r, column=c, value=v))
    for i in range(6, 10):
        r = 5 + i
        inp(ws.cell(row=r, column=1))
        inp(ws.cell(row=r, column=2), "0%")
        for c in range(3, 7):
            inp(ws.cell(row=r, column=c))
    ws["A16"] = "Weights should add up to"
    calc(ws["B16"], "0%", True)
    ws["B16"] = "=SUM(B5:B14)"
    ws["A17"] = "Weighted score (out of 5)"
    ws["A17"].font = Font(bold=True)
    for c in range(3, 7):
        L = col(c)
        calc(ws.cell(row=17, column=c, value=f"=IFERROR(SUMPRODUCT($B$5:$B$14,{L}5:{L}14)/$B$16,0)"), "0.00", True)
    ws["A18"] = "Rank"
    for c in range(3, 7):
        L = col(c)
        calc(ws.cell(row=18, column=c, value=f"=RANK({L}17,$C$17:$F$17)"), "0")
    dropdown(ws, "C5:F14", ["1", "2", "3", "4", "5"])
    bar(ws, "H4", "Weighted score", Reference(ws, min_col=3, max_col=6, min_row=4), Reference(ws, min_col=3, max_col=6, min_row=17))
    from openpyxl.chart import Series
    ch = ws._charts[-1]
    ch.series = []
    ch.series.append(Series(Reference(ws, min_col=3, max_col=6, min_row=17), title="Score"))
    ch.set_categories(Reference(ws, min_col=3, max_col=6, min_row=4))
    pr = wb.create_sheet("Competitor profiles")
    title(pr, "Competitor profiles", "One row per competitor. Fill from their website, social pages and customer reviews.")
    head(pr, 4, ["Competitor", "Website", "Main offer", "Price range", "Strengths", "Weaknesses", "How we can beat them"])
    widths(pr, [20, 26, 26, 16, 30, 30, 34])
    for r in range(5, 15):
        for c in range(1, 8):
            inp(pr.cell(row=r, column=c))
    start_sheet(wb, "Start here", "Competitor analysis", [
        "Profiles sheet: list each competitor with their offer, prices, strengths and weaknesses (from their website, reviews and social pages).",
        "Comparison sheet: set the weight of each factor (should total 100%), then score everyone 1-5.",
        "Read the weighted scores and ranks. Where you score low on a heavily weighted factor, that is your biggest gap.",
        "Use the SWOT in the Word file to turn this into an action list.",
    ])
    return wb


def market_size():
    wb = new_wb()
    ws = wb.create_sheet("Market size")
    ws.sheet_view.showGridLines = False
    title(ws, "Market size calculator (TAM, SAM, SOM)", "Estimate the market with simple bottom-up numbers. Replace examples and write down where each number came from.")
    rows = [("Total potential customers in the region", 500000, "#,##0", "Census, trade body report, search estimates"), ("% who need this type of product/service", 0.30, "0%", "Survey or industry report"),
            ("Average spend per customer per year (₹)", 3600, MONEY, "Your price list or competitor prices"), ("% of those you can realistically serve (location, channel)", 0.20, "0%", "Your capacity and reach"),
            ("Realistic share you can win in Year 1", 0.05, "0.0%", "Based on marketing budget and competitors")]
    head(ws, 4, ["Input", "Value", "Source / note"])
    widths(ws, [58, 18, 46])
    for i, (l, v, f, src) in enumerate(rows):
        r = 5 + i
        ws.cell(row=r, column=1, value=l).border = BORDER
        inp(ws.cell(row=r, column=2, value=v), f)
        inp(ws.cell(row=r, column=3, value=src))
    ws["A11"], ws["B11"] = "TAM: total market value per year", "=B5*B6*B7"
    ws["A12"], ws["B12"] = "SAM: market you can serve", "=B11*B8"
    ws["A13"], ws["B13"] = "SOM: what you can win in Year 1", "=B12*B9"
    ws["A14"], ws["B14"] = "Customers needed for SOM", "=IFERROR(B13/B7,0)"
    for r in (11, 12, 13, 14):
        ws[f"A{r}"].font = Font(bold=True)
        calc(ws[f"B{r}"], MONEY if r != 14 else "#,##0", True)
    start_sheet(wb, "Start here", "Industry / market research: market size sheet", [
        "Fill the yellow inputs with your best estimates and note the source of each number.",
        "TAM, SAM and SOM calculate automatically. SOM is the figure to put in a business plan.",
        "Test a low and a high case. If SOM is tiny, the business needs a bigger market or a different focus.",
        "Use the Word report template to write up your findings with sources.",
    ])
    return wb


def seo_keywords():
    wb = new_wb()
    ws = wb.create_sheet("Keywords")
    title(ws, "SEO keyword and page plan", "One row per page. Use one main keyword per page and write a title and description for it.")
    head(ws, 4, ["Page URL", "Main keyword", "Search intent", "Title tag (max 60)", "Title length", "Meta description (max 155)", "Description length", "Status"])
    widths(ws, [22, 24, 16, 40, 10, 54, 12, 12])
    sample = [("/", "excel dashboard madurai", "Buy", "Excel Dashboards for Small Business in Madurai | YourName", "Excel dashboards and finance reports for shops and small businesses in Madurai. Fixed prices, fast delivery."),
              ("/services", "finance services small business", "Compare", "Finance and Data Services for Small Business | YourName", "50 finance, Excel and website services with clear prices. See packages and order online."),
              ("/contact", "contact finance freelancer madurai", "Contact", "Contact YourName: Finance Freelancer in Madurai", "Get in touch for a quote on dashboards, reports or websites. We reply within 24 hours.")]
    for r in range(5, 55):
        for c in range(1, 9):
            cell = ws.cell(row=r, column=c)
            if c in (5, 7):
                calc(cell, "0")
                continue
            s = sample[r - 5] if r - 5 < len(sample) else None
            if s:
                cell.value = {1: s[0], 2: s[1], 3: s[2], 4: s[3], 6: s[4], 8: "Done"}.get(c)
            inp(cell)
        ws.cell(row=r, column=5, value=f'=IF(D{r}="","",LEN(D{r}))')
        ws.cell(row=r, column=7, value=f'=IF(F{r}="","",LEN(F{r}))')
    ws.conditional_formatting.add("E5:E54", FormulaRule(formula=['AND(E5<>"",E5>60)'], fill=PatternFill("solid", bgColor="FFC7CE", fgColor="FFC7CE")))
    ws.conditional_formatting.add("G5:G54", FormulaRule(formula=['AND(G5<>"",G5>155)'], fill=PatternFill("solid", bgColor="FFC7CE", fgColor="FFC7CE")))
    dropdown(ws, "C5:C54", ["Learn", "Compare", "Buy", "Contact"])
    dropdown(ws, "H5:H54", ["Planned", "Written", "Done"])
    start_sheet(wb, "Start here", "Basic on-page SEO plan", [
        "List each page of the website and choose one main keyword for it (what a customer would type into Google).",
        "Write a title tag (under 60 characters) and a meta description (under 155). Lengths turn red when too long.",
        "Paste them into your site's page settings or the HTML snippets in the Word checklist.",
        "Recheck after 4 weeks in Google Search Console.",
    ])
    return wb


def powerbi_sales_data():
    wb = new_wb()
    products = [("P01", "Notebook", "Stationery", 60), ("P02", "Pen box", "Stationery", 120), ("P03", "Backpack", "Bags", 900), ("P04", "Lunch box", "Kitchen", 350),
                ("P05", "Water bottle", "Kitchen", 280), ("P06", "Headphones", "Electronics", 1500), ("P07", "Power bank", "Electronics", 1800), ("P08", "Desk lamp", "Electronics", 750)]
    customers = [("C01", "Ravi Stores", "Madurai", "South"), ("C02", "Meena Traders", "Chennai", "North"), ("C03", "Arun & Co", "Coimbatore", "West"), ("C04", "Kavya Boutique", "Trichy", "South"),
                 ("C05", "Selvi Mart", "Salem", "West"), ("C06", "Hari Agencies", "Chennai", "North")]
    sf = wb.create_sheet("Sales")
    head(sf, 1, ["OrderID", "Date", "CustomerID", "ProductID", "Quantity", "UnitPrice", "Discount", "SalesAmount"])
    widths(sf, [10, 12, 12, 12, 10, 12, 10, 14])
    for i in range(240):
        d = D(2025, 1, 1) + dt.timedelta(days=int(i * 365 / 240) + rnd.randint(0, 1))
        p = products[rnd.randrange(8)]
        q = rnd.randint(1, 12)
        disc = rnd.choice([0, 0, 0.05, 0.1])
        row = [f"ORD{1000 + i}", d, customers[rnd.randrange(6)][0], p[0], q, p[3], disc]
        for c, v in enumerate(row, start=1):
            sf.cell(row=2 + i, column=c, value=v)
        sf.cell(row=2 + i, column=2).number_format = "yyyy-mm-dd"
        sf.cell(row=2 + i, column=8, value=f"=E{2 + i}*F{2 + i}*(1-G{2 + i})").number_format = '#,##0.00'
    pd_ = wb.create_sheet("Products")
    head(pd_, 1, ["ProductID", "Product", "Category", "ListPrice"])
    for i, p in enumerate(products):
        for c, v in enumerate(p, start=1):
            pd_.cell(row=2 + i, column=c, value=v)
    widths(pd_, [12, 18, 14, 12])
    cu = wb.create_sheet("Customers")
    head(cu, 1, ["CustomerID", "Customer", "City", "Region"])
    for i, c_ in enumerate(customers):
        for c, v in enumerate(c_, start=1):
            cu.cell(row=2 + i, column=c, value=v)
    widths(cu, [12, 20, 14, 10])
    ca = wb.create_sheet("Calendar")
    head(ca, 1, ["Date", "Year", "MonthNo", "Month", "Quarter", "WeekdayName"])
    for i in range(365):
        d = D(2025, 1, 1) + dt.timedelta(days=i)
        r = 2 + i
        ca.cell(row=r, column=1, value=d).number_format = "yyyy-mm-dd"
        ca.cell(row=r, column=2, value=f"=YEAR(A{r})")
        ca.cell(row=r, column=3, value=f"=MONTH(A{r})")
        ca.cell(row=r, column=4, value=f'=TEXT(A{r},"mmm")')
        ca.cell(row=r, column=5, value=f'="Q"&ROUNDUP(C{r}/3,0)')
        ca.cell(row=r, column=6, value=f'=TEXT(A{r},"ddd")')
    widths(ca, [12, 8, 9, 8, 9, 12])
    start_sheet(wb, "Start here", "Power BI sales starter data model", [
        "This workbook is a clean star-schema sample: one Sales table plus Products, Customers and Calendar tables.",
        "In Power BI Desktop: Get data > Excel workbook > select all four sheets > Load.",
        "In Model view, link Sales[ProductID] to Products[ProductID], Sales[CustomerID] to Customers[CustomerID], Sales[Date] to Calendar[Date] (one-to-many).",
        "Follow the Word guide to add measures (Total Sales, Orders, Average Order, Sales vs last year) and the report layout.",
        "Replace the sample rows with your real sales in the same columns, keeping the column names.",
    ])
    return wb


def powerbi_fin_data():
    wb = new_wb()
    fa = wb.create_sheet("Financials")
    head(fa, 1, ["Month", "Account", "AccountGroup", "Scenario", "Amount"])
    widths(fa, [12, 20, 16, 10, 14])
    accounts = [("Revenue", "Revenue", 1), ("Cost of goods sold", "COGS", -1), ("Salaries", "Opex", -1), ("Rent", "Opex", -1), ("Marketing", "Opex", -1), ("Other expenses", "Opex", -1)]
    base = {"Revenue": 600000, "Cost of goods sold": 270000, "Salaries": 120000, "Rent": 36000, "Marketing": 30000, "Other expenses": 24000}
    r = 2
    for m in range(12):
        for sc, mult in (("Actual", 1), ("Budget", 1.03)):
            for acc, grp, sign in accounts:
                growth = 1 + 0.015 * m
                val = base[acc] * (growth if acc in ("Revenue", "Cost of goods sold", "Marketing") else 1) * (mult if sc == "Budget" else rnd.uniform(0.94, 1.06))
                for c, v in enumerate([D(2025, m + 1, 1), acc, grp, sc, round(val * sign if False else val)], start=1):
                    fa.cell(row=r, column=c, value=v)
                fa.cell(row=r, column=1).number_format = "yyyy-mm-dd"
                r += 1
    start_sheet(wb, "Start here", "Power BI financial KPI starter data", [
        "The Financials sheet is a tidy table: one row per Month, Account and Scenario (Actual or Budget). Amounts are positive; the group tells Power BI what is revenue, cost of goods or operating cost.",
        "In Power BI Desktop: Get data > Excel > Financials > Load. Add a Calendar table (the Word guide shows the one-line DAX).",
        "Create the measures in the Word guide: Revenue, Gross Profit, Gross Margin %, Operating Profit, Net Margin %, Actual vs Budget variance.",
        "Replace the sample rows with your own accounts, keeping the same column names.",
    ])
    return wb


def powerbi_ready_table():
    wb = new_wb()
    ws = wb.create_sheet("Clean table")
    head(ws, 1, ["Date", "Category", "Item", "Quantity", "Amount", "Region", "Salesperson"])
    widths(ws, [12, 16, 20, 10, 12, 12, 14])
    rows = [(D(2026, 1, 3), "Product A", "Item 1", 5, 2500, "South", "Anand"), (D(2026, 1, 5), "Product B", "Item 2", 2, 3000, "North", "Priya"), (D(2026, 1, 9), "Product A", "Item 3", 10, 5000, "South", "Karthik")]
    for i, row in enumerate(rows):
        for c, v in enumerate(row, start=1):
            ws.cell(row=2 + i, column=c, value=v)
        ws.cell(row=2 + i, column=1).number_format = "yyyy-mm-dd"
    ws2 = wb.create_sheet("Messy example")
    for c, v in enumerate(["Report: Sales Jan", None, None, None], start=1):
        ws2.cell(row=1, column=c, value=v)
    ws2.cell(row=3, column=1, value="Date")
    ws2.cell(row=3, column=2, value="Item  (Category)")
    ws2.cell(row=3, column=3, value="Jan")
    ws2.cell(row=3, column=4, value="Feb")
    ws2.cell(row=4, column=1, value="3/1/26")
    ws2.cell(row=4, column=2, value="Item 1 (Product A)")
    ws2.cell(row=4, column=3, value="2500")
    ws2.cell(row=5, column=1, value="TOTAL")
    ws2.cell(row=5, column=3, value="=SUM(C4:C4)")
    ws2["A8"] = "Problems here: title rows above the header, months in columns, two facts in one cell, numbers stored as text, a total row inside the data. Power BI needs the 'Clean table' layout instead."
    ws2["A8"].alignment = Alignment(wrap_text=True)
    ws2.column_dimensions["A"].width = 60
    start_sheet(wb, "Start here", "Excel to Power BI: clean table template", [
        "Compare 'Messy example' with 'Clean table'. Power BI works best with one header row, one fact per column, no totals inside the data, and months down the rows, not across.",
        "Copy your data into the Clean table layout (or use Power Query to reshape it, see the Word guide).",
        "Select the data and press Ctrl+T to make it an Excel Table, then name it (Table Design > Table Name).",
        "In Power BI Desktop use Get data > Excel > pick the table. Refresh whenever you update the Excel file.",
    ])
    return wb


def cleaning_toolkit():
    wb = new_wb()
    ws = wb.create_sheet("Cleaner")
    ws.sheet_view.showGridLines = False
    title(ws, "Excel data cleaning toolkit", "Paste messy data in column A-D (yellow). The cleaned version appears on the right. Copy it and Paste Special > Values.")
    head(ws, 4, ["Name (messy)", "Phone (messy)", "Date (as text)", "Amount (as text)", "", "Name (clean)", "Phone (clean)", "Date (real date)", "Amount (number)", "Duplicate?"])
    widths(ws, [24, 18, 14, 14, 3, 24, 16, 14, 14, 12])
    messy = [("  ravi KUMAR ", "98765-43210", "03/01/2026", "₹ 1,200"), ("MEENA  devi", "(98765) 43211", "05/01/2026", "2,500.50"), ("ravi kumar", "98765 43210", "03/01/2026", "1200"),
             ("arun  prasad", "+91 98765 43212", "2026-01-09", " 800 "), ("Kavya", "9876543213", "12/01/2026", "₹3,000")]
    for r in range(5, 205):
        for c in range(1, 5):
            cell = ws.cell(row=r, column=c)
            if r - 5 < len(messy):
                cell.value = messy[r - 5][c - 1]
            inp(cell)
        calc(ws.cell(row=r, column=6, value=f'=IF(A{r}="","",PROPER(TRIM(CLEAN(A{r}))))'))
        calc(ws.cell(row=r, column=7, value=f'=IF(B{r}="","",RIGHT(SUBSTITUTE(SUBSTITUTE(SUBSTITUTE(SUBSTITUTE(SUBSTITUTE(B{r}," ",""),"-",""),"(",""),")",""),"+",""),10))'))
        calc(ws.cell(row=r, column=8, value=f'=IF(C{r}="","",IFERROR(DATEVALUE(C{r}),C{r}))'), "dd-mmm-yyyy")
        calc(ws.cell(row=r, column=9, value=f'=IF(D{r}="","",IFERROR(VALUE(SUBSTITUTE(SUBSTITUTE(SUBSTITUTE(TRIM(D{r}),"₹",""),",","")," ","")),D{r}))'), "#,##0.00")
        calc(ws.cell(row=r, column=10, value=f'=IF(F{r}="","",IF(COUNTIF($F$5:$F$204,F{r})>1,"Duplicate","Unique"))'))
    ws.conditional_formatting.add("J5:J204", FormulaRule(formula=['J5="Duplicate"'], fill=PatternFill("solid", bgColor="FFE5B4", fgColor="FFE5B4")))
    ck = wb.create_sheet("Checklist")
    title(ck, "Data cleaning checklist")
    items = ["Make a backup copy of the original file first.", "Remove blank rows and columns.", "Trim spaces (TRIM) and remove hidden characters (CLEAN).", "Fix capitalisation (PROPER / UPPER / LOWER).",
             "Convert numbers stored as text (VALUE) and check totals still match.", "Convert text dates to real dates and use one format.", "Find duplicates (COUNTIF, or Data > Remove Duplicates).",
             "Use dropdown lists (Data Validation) so new data stays consistent.", "Split full names/addresses with Text to Columns or TEXTSPLIT.", "Freeze the header row and turn the range into a Table (Ctrl+T).",
             "Check totals against the source before and after cleaning."]
    for i, t in enumerate(items):
        ck.cell(row=3 + i, column=1, value=f"☐  {t}")
    ck.column_dimensions["A"].width = 90
    start_sheet(wb, "Start here", "Excel data cleaning and formatting toolkit", [
        "Paste your messy names, phone numbers, dates and amounts into the yellow columns on the Cleaner sheet.",
        "The cleaned values appear on the right: names tidy, phone numbers 10 digits, text dates become real dates, text amounts become numbers, duplicates flagged.",
        "Copy the clean columns and use Paste Special > Values into your real file.",
        "Work through the Checklist sheet for any dataset before you analyse it.",
    ])
    return wb


def pivot_report():
    wb = new_wb()
    ws = wb.create_sheet("Data")
    title(ws, "Sample sales data", "Replace with your data in the same columns. Convert to a Table (Ctrl+T) to make a real PivotTable.")
    head(ws, 4, ["Date", "Region", "Product", "Salesperson", "Quantity", "Amount"])
    widths(ws, [14, 12, 16, 14, 10, 14])
    regions, products, people = ["North", "South", "East", "West"], ["Product A", "Product B", "Product C"], ["Anand", "Priya", "Karthik"]
    for i in range(60):
        r = 5 + i
        vals = [D(2026, 1, 1) + dt.timedelta(days=i * 3), regions[rnd.randrange(4)], products[rnd.randrange(3)], people[rnd.randrange(3)], rnd.randint(1, 20), None]
        for c, v in enumerate(vals[:5], start=1):
            inp(ws.cell(row=r, column=c, value=v), "dd-mmm-yyyy" if c == 1 else None)
        inp(ws.cell(row=r, column=6, value=vals[4] * rnd.choice([300, 450, 600])), MONEY)
    for r in range(65, 505):
        for c in range(1, 7):
            inp(ws.cell(row=r, column=c), MONEY if c == 6 else ("dd-mmm-yyyy" if c == 1 else None))
    pv = wb.create_sheet("Pivot-style report")
    pv.sheet_view.showGridLines = False
    title(pv, "Pivot-style report (formula based, updates automatically)", "Same idea as a PivotTable, built with SUMIFS so it needs no refresh.")
    head(pv, 4, ["Region \\ Product"] + products + ["Total"])
    widths(pv, [18, 14, 14, 14, 14])
    for i, rg in enumerate(regions):
        r = 5 + i
        pv.cell(row=r, column=1, value=rg).border = BORDER
        for j in range(3):
            L = col(2 + j)
            calc(pv.cell(row=r, column=2 + j, value=f"=SUMIFS(Data!$F$5:$F$504,Data!$B$5:$B$504,$A{r},Data!$C$5:$C$504,{L}$4)"), MONEY)
        calc(pv.cell(row=r, column=5, value=f"=SUM(B{r}:D{r})"), MONEY, True)
    pv.cell(row=9, column=1, value="Total").font = Font(bold=True)
    for c in range(2, 6):
        L = col(c)
        calc(pv.cell(row=9, column=c, value=f"=SUM({L}5:{L}8)"), MONEY, True)
    head(pv, 12, ["Salesperson", "Quantity", "Amount", "Share"])
    for i, p in enumerate(people):
        r = 13 + i
        pv.cell(row=r, column=1, value=p).border = BORDER
        calc(pv.cell(row=r, column=2, value=f"=SUMIFS(Data!$E$5:$E$504,Data!$D$5:$D$504,A{r})"), "#,##0")
        calc(pv.cell(row=r, column=3, value=f"=SUMIFS(Data!$F$5:$F$504,Data!$D$5:$D$504,A{r})"), MONEY)
        calc(pv.cell(row=r, column=4, value=f"=IFERROR(C{r}/$E$9,0)"), PCT)
    bar(pv, "G4", "Sales by region", Reference(pv, min_col=1, min_row=5, max_row=8), Reference(pv, min_col=5, min_row=4, max_row=8))
    start_sheet(wb, "Start here", "PivotTable reports from your data", [
        "Data sheet: paste your own rows (Date, Region, Product, Salesperson, Quantity, Amount). Sample data is there as an example.",
        "Pivot-style report: SUMIFS grids by region × product and by salesperson update by themselves.",
        "To make a real PivotTable: click inside Data, Insert > PivotTable, drag Region to Rows, Product to Columns, Amount to Values.",
        "Add a Slicer (PivotTable Analyze > Insert Slicer) to filter by region or salesperson with one click. Steps are in the Word guide.",
    ])
    return wb


def formula_automation():
    wb = new_wb()
    ws = wb.create_sheet("Formula demos")
    ws.sheet_view.showGridLines = False
    title(ws, "Excel automation with formulas (no macros)", "Working examples of the formulas that replace manual work. Change the yellow cells and watch the results.")
    widths(ws, [34, 18, 18, 46])
    head(ws, 4, ["Task", "Input", "Result", "Formula used"])
    demo = [("Add up amounts that meet a condition", "=SUMIFS(Lookup!$C$5:$C$14,Lookup!$B$5:$B$14,B6)", "Product A", "=SUMIFS(Amount, Product, B6)"),
            ("Look up a price by item code", "=VLOOKUP(B7,Lookup!$A$5:$C$14,3,FALSE)", "P03", "=VLOOKUP(code, table, 3, FALSE)"),
            ("Count how many match", '=COUNTIF(Lookup!$B$5:$B$14,B8)', "Product B", "=COUNTIF(Product, B8)"),
            ("Pass / fail logic", '=IF(B9>=40,"Pass","Fail")', 62, '=IF(mark>=40,"Pass","Fail")'),
            ("Grade bands", '=IF(B10>=75,"A",IF(B10>=60,"B",IF(B10>=40,"C","F")))', 68, "Nested IF"),
            ("Days until a due date", '=B11-TODAY()', D(2026, 12, 31), "=due - TODAY()"),
            ("Join first and last name", '=TRIM(B12)&" "&C12', "Ravi", "=first&\" \"&last"),
            ("Month name from a date", '=TEXT(B13,"mmmm yyyy")', D(2026, 3, 15), '=TEXT(date,"mmmm yyyy")'),
            ("EMI for a loan (₹5,00,000, 10%, 5 years)", "=-PMT(10%/12,5*12,500000)", "-", "=-PMT(rate/12, years*12, amount)"),
            ("Flag overdue", '=IF(B16<TODAY(),"OVERDUE","On time")', D(2026, 1, 10), '=IF(due<TODAY(),"OVERDUE","On time")')]
    for i, (task, f, inpv, text) in enumerate(demo):
        r = 5 + i
        ws.cell(row=r, column=1, value=task).border = BORDER
        c = ws.cell(row=r, column=2, value=inpv)
        inp(c, "dd-mmm-yyyy" if isinstance(inpv, dt.date) else None)
        calc(ws.cell(row=r, column=3, value=f.replace("B6", f"B{r}") if False else f))
    ws["C5"] = "=SUMIFS(Lookup!$C$5:$C$14,Lookup!$B$5:$B$14,B5)"
    ws["C6"] = "=VLOOKUP(B6,Lookup!$A$5:$D$14,4,FALSE)"
    ws["C7"] = "=COUNTIF(Lookup!$B$5:$B$14,B7)"
    ws["C8"] = '=IF(B8>=40,"Pass","Fail")'
    ws["C9"] = '=IF(B9>=75,"A",IF(B9>=60,"B",IF(B9>=40,"C","F")))'
    ws["C10"] = "=B10-TODAY()"
    ws["C11"] = '=TRIM(B11)&" "&"Kumar"'
    ws["C12"] = '=TEXT(B12,"mmmm yyyy")'
    ws["C13"] = "=-PMT(10%/12,5*12,500000)"
    ws["C14"] = '=IF(B14<TODAY(),"OVERDUE","On time")'
    ws["B5"], ws["B6"], ws["B7"] = "Product A", "P03", "Product B"
    ws["B8"], ws["B9"], ws["B10"] = 62, 68, D(2026, 12, 31)
    ws["B11"], ws["B12"], ws["B13"], ws["B14"] = "Ravi", D(2026, 3, 15), "-", D(2026, 1, 10)
    texts = {5: "SUMIFS(Amount, Product, B5)", 6: "VLOOKUP(code, table, 4, FALSE)", 7: "COUNTIF(Product, B7)", 8: 'IF(mark>=40, "Pass", "Fail")',
             9: "Nested IF: A / B / C / F", 10: "due date - TODAY()", 11: 'TRIM(name) & " " & "Kumar"', 12: 'TEXT(date, "mmmm yyyy")',
             13: "-PMT(rate/12, years*12, amount)", 14: 'IF(due<TODAY(), "OVERDUE", "On time")'}
    for r, t in texts.items():
        ws.cell(row=r, column=4, value=t)
    for r, f in ((10, "0"), (13, MONEY)):
        ws[f"C{r}"].number_format = f
    lk = wb.create_sheet("Lookup")
    title(lk, "Lookup data used by the demos")
    head(lk, 4, ["Code", "Product", "Amount", "Price"])
    for i, row in enumerate([("P01", "Product A", 1200, 450), ("P02", "Product A", 800, 450), ("P03", "Product B", 1500, 1200), ("P04", "Product B", 900, 1200), ("P05", "Product C", 2000, 300),
                             ("P06", "Product A", 700, 450), ("P07", "Product C", 1100, 300), ("P08", "Product B", 600, 1200), ("P09", "Product C", 500, 300), ("P10", "Product A", 1000, 450)]):
        for c, v in enumerate(row, start=1):
            lk.cell(row=5 + i, column=c, value=v)
    cf = wb.create_sheet("Cheat sheet")
    title(cf, "Formula cheat sheet: pick the right tool")
    head(cf, 3, ["I want to...", "Use"])
    widths(cf, [52, 60])
    tips = [("Sum numbers that meet a condition", "SUMIFS"), ("Count rows that meet a condition", "COUNTIFS"), ("Find a value from another table", "XLOOKUP (or VLOOKUP / INDEX+MATCH)"),
            ("Return different results by condition", "IF / IFS"), ("Handle errors neatly", "IFERROR"), ("Round money", "ROUND / ROUNDUP"), ("Work with dates", "TODAY, EDATE, EOMONTH, DATEDIF, TEXT"),
            ("Clean text", "TRIM, CLEAN, PROPER, SUBSTITUTE, LEFT/RIGHT/MID"), ("Combine text", "& or TEXTJOIN"), ("Highlight problems automatically", "Conditional Formatting with a formula"),
            ("Stop wrong entries", "Data Validation (lists, numbers, dates)"), ("Auto-expanding ranges", "Excel Tables (Ctrl+T) and structured references")]
    for i, (a, b) in enumerate(tips):
        cf.cell(row=4 + i, column=1, value=a)
        cf.cell(row=4 + i, column=2, value=b)
    start_sheet(wb, "Start here", "Excel automation with formulas (no macros)", [
        "Formula demos: change the yellow inputs and read the green results. Each row shows the formula used.",
        "Copy the formula pattern into your own sheet and swap in your ranges.",
        "Cheat sheet: choose the right formula for the job.",
        "Prefer Tables (Ctrl+T), Data Validation and Conditional Formatting over macros: they work everywhere, including Excel online.",
    ])
    return wb
