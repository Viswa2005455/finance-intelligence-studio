"""The public "how we calculate this" catalogue: every ratio with its formula, typical range and caution (from the ratio engine and
its readings), plus the core valuation, project and screening methods. The ratio entries are generated from the engine itself, so the
page can never describe a formula the app does not use. The method entries are written by hand and each formula is the one in the code."""

from __future__ import annotations

from . import ratio_insights, ratios

METHODS: list[dict] = [
    {"group": "Projects and valuation", "name": "Net present value (NPV)", "formula": "NPV = Σ CFₜ / (1 + r)ᵗ for t = 0 … n",
     "what": "Discounts every cash flow back to today at the required return and adds them up. Positive means the project earns more than the required return.",
     "caution": "Excel's NPV() discounts its first value, so a spreadsheet needs =CF0 + NPV(r, CF1:CFn). This app uses t = 0 for the first cash flow."},
    {"group": "Projects and valuation", "name": "Internal rate of return (IRR)", "formula": "The rate r at which NPV = 0",
     "what": "The project's own return. Accept a conventional project if it is above the cost of capital.",
     "caution": "With several sign changes in the cash flows there can be several IRRs or none; the app shows all roots and tells you to rely on NPV."},
    {"group": "Projects and valuation", "name": "Modified IRR (MIRR)", "formula": "MIRR = (FV of positive flows at the reinvestment rate / −PV of negative flows at the finance rate)^(1/n) − 1",
     "what": "A single, comparable rate that assumes money is reinvested at a realistic rate, matching Excel's MIRR.", "caution": "Needs at least one negative and one positive cash flow."},
    {"group": "Projects and valuation", "name": "Payback and discounted payback", "formula": "The time at which cumulative (discounted) cash flow turns positive",
     "what": "How long until the money is earned back. Discounted payback adds the time value of money.", "caution": "Ignores everything after the payback point."},
    {"group": "Projects and valuation", "name": "Cost of equity (CAPM)", "formula": "Re = Rf + β × (Rm − Rf)",
     "what": "The return shareholders require, from the risk-free rate, the company's beta and the expected market return.", "caution": "Beta and market return are estimates; small changes move the answer a lot."},
    {"group": "Projects and valuation", "name": "Weighted average cost of capital (WACC)", "formula": "WACC = E/V × Re + D/V × Rd × (1 − T)",
     "what": "The blended return required by shareholders and lenders, used as the DCF discount rate.", "caution": "Use market values for the weights, not book values."},
    {"group": "Projects and valuation", "name": "Free cash flow to the firm (FCFF)", "formula": "FCFF = EBIT × (1 − T) + D&A − CapEx − ΔNWC",
     "what": "The cash the business generates for all capital providers after tax and reinvestment.", "caution": "Pairs with WACC. Free cash flow to equity pairs with the cost of equity."},
    {"group": "Projects and valuation", "name": "Terminal value (Gordon growth)", "formula": "TV = FCFFₙ × (1 + g) / (WACC − g), then PV(TV) = TV / (1 + WACC)ⁿ",
     "what": "The value of all cash flows after the forecast years, assuming they grow at a steady rate g for ever.", "caution": "Often 60–80% of the total value. g must be below WACC and below long-run economic growth."},
    {"group": "Projects and valuation", "name": "Enterprise value to equity value", "formula": "Equity value = Σ PV(FCFF) + PV(TV) − Debt + Cash",
     "what": "From the value of the whole operating business to the value belonging to shareholders.", "caution": "Do not count cash twice, and use the same units and currency throughout."},
    {"group": "Growth", "name": "Compound annual growth rate (CAGR)", "formula": "CAGR = (End / Start)^(1 / years) − 1",
     "what": "The steady yearly growth that would take a value from start to end.", "caution": "Hides volatility between the two points and is undefined when the start is zero or negative."},
    {"group": "Screens", "name": "Beneish M-score", "formula": "M = −4.84 + 0.920·DSRI + 0.528·GMI + 0.404·AQI + 0.892·SGI + 0.115·DEPI − 0.172·SGAI + 4.679·TATA − 0.327·LVGI",
     "what": "Eight ratios that moved unusually in companies later found to have manipulated earnings. Above −1.78 is flagged.", "caution": "A prompt to read the accounts closely, not evidence of manipulation. Missing inputs are reported, never treated as zero."},
    {"group": "Screens", "name": "Altman Z-score (original, listed manufacturers)", "formula": "Z = 1.2·X1 + 1.4·X2 + 3.3·X3 + 0.6·X4 + 1.0·X5",
     "what": "Distress prediction from liquidity, retained earnings, profitability, market leverage and turnover. Above 2.99 safe, 1.81–2.99 grey, below 1.81 distress.", "caution": "Built on listed US manufacturers; use Z'' for services, IT and unlisted companies."},
    {"group": "Screens", "name": "Altman Z''-score (non-manufacturers, book equity)", "formula": "Z'' = 6.56·X1 + 3.26·X2 + 6.72·X3 + 1.05·X4",
     "what": "A version that drops sales turnover and uses book equity. Above 2.6 safe, 1.1–2.6 grey, below 1.1 distress.", "caution": "A screen, not a forecast of failure."},
    {"group": "Screens", "name": "Piotroski F-score", "formula": "F = nine yes/no tests of profitability, leverage and efficiency, added up (0–9)",
     "what": "8–9 is strong and improving, 0–2 is weak.", "caution": "Tests that lack data are not counted as passes; the score says how many were tested."},
]


def catalogue() -> dict:
    """Everything the methodology page shows."""
    engine = ratios.compute_ratios({})  # with no data every ratio is "missing", which still carries its name, category and formula
    out = []
    for r in engine:
        out.append({
            "key": r.key, "name": r.name, "category": r.category, "formula": r.formula, "unit": r.unit,
            "typical": ratio_insights.TYPICAL.get(r.key, ""), "caution": ratio_insights.CAUTION.get(r.key, ""),
            "related": ratio_insights.RELATED.get(r.key, []),
        })
    return {"ratios": out, "methods": METHODS,
            "conventions": ["Amounts are in one currency and one unit throughout.", "Average balances are used when an opening balance is supplied; otherwise the closing balance is used and the result says so.",
                            "Missing inputs are listed, never filled in or treated as zero.", "Ratios shown in plain English use stated rules of thumb; industry and size change what is normal."]}
