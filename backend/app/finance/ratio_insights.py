"""Plain-English reading of each ratio: what the number says, how it compares with common rules of thumb,
what could mislead, and what to look at next.

The thresholds are rules of thumb, not standards. They differ by industry, so every insight carries a
"typical range" and a caution, and the level is only a prompt to look closer. Nothing here changes a
calculated value: the numbers come from ratios.compute_ratios, this module only words them.

Levels: "strong", "good", "watch", "concern" (a reading, scored in the summary) and "info" (context only,
not scored, used where the right answer depends almost entirely on the industry).
"""

from __future__ import annotations

from typing import Callable

Level = str
# (level, headline, meaning, next step)
Reading = tuple[Level, str, str, str]

SCORE = {"strong": 2, "good": 1, "watch": -1, "concern": -2}
LEVEL_LABEL = {"strong": "Strong", "good": "Healthy", "watch": "Watch", "concern": "Concern", "info": "Context"}


def _x(v: float) -> str:
    return f"{v:.2f}x" if abs(v) < 100 else f"{v:,.0f}x"


def _p(v: float) -> str:
    return f"{v:.1f}%"


def _d(v: float) -> str:
    return f"{v:.0f} days"


# --------------------------------------------------------------------------------------------------
# Readings. Each takes the ratio's value and a dict of every calculated ratio value (for context).
# --------------------------------------------------------------------------------------------------
def _current_ratio(v: float, a: dict) -> Reading:
    if v < 1:
        return ("concern", f"Current liabilities are larger than current assets ({_x(v)})",
                "Within the next year the company owes more than it expects to turn into cash. That is not always a crisis (retailers and subscription businesses run this way on purpose), but it leaves no cushion.",
                "Check the cash ratio and operating cash flow ratio, then look at what is due and when. Ask whether credit lines or customer prepayments fill the gap.")
    if v < 1.2:
        return ("watch", f"Thin cover for short-term bills ({_x(v)})",
                "Current assets only just exceed current liabilities, so a delay in collecting receivables or an unexpected bill could cause a squeeze.",
                "Look at how quickly receivables are collected (DSO) and whether inventory is easy to sell (quick ratio).")
    if v <= 3:
        return ("strong" if v >= 1.5 else "good", f"Comfortable short-term cover ({_x(v)})",
                "Current assets are enough to pay current liabilities with room to spare, which lowers the risk of a cash squeeze.",
                "Confirm the quality of the assets: a large share in slow inventory or old receivables is worth less than it looks.")
    return ("watch", f"Very high ({_x(v)}): capital may be sitting idle",
            "Far more current assets than current liabilities is safe, but it can mean cash, stock or receivables are not being put to work.",
            "Check inventory days and receivable days for build-up, and consider whether surplus cash could repay debt or be invested.")


def _quick_ratio(v: float, a: dict) -> Reading:
    if v < 0.7:
        return ("concern", f"Depends on selling inventory to pay bills ({_x(v)})",
                "Without inventory, liquid assets cover less than 70% of current liabilities.",
                "Compare with inventory days: if stock sells fast this is manageable, if not it is a real risk.")
    if v < 1:
        return ("watch", f"Slightly short without inventory ({_x(v)})",
                "Liquid assets nearly cover current liabilities, but not quite.", "Check how fast inventory turns and whether receivables are collected on time.")
    return ("strong" if v >= 1.5 else "good", f"Can pay current bills without selling stock ({_x(v)})",
            "Cash, receivables and other liquid assets cover current liabilities.", "Make sure the receivables are collectable: look at DSO and any overdue balances.")


def _cash_ratio(v: float, a: dict) -> Reading:
    if v < 0.1:
        return ("watch", f"Very little cash on hand ({_x(v)})",
                "Cash and securities cover under 10% of current liabilities. Many healthy businesses run lean, but they rely on steady collections or credit lines.",
                "Check operating cash flow and available credit lines.")
    if v <= 1:
        return ("good", f"A sensible cash buffer ({_x(v)})", "Cash covers a useful part of short-term obligations without holding excess.", "Keep an eye on the trend rather than the level.")
    return ("info", f"A large cash pile ({_x(v)})", "Cash exceeds all current liabilities. That is safe, but it may be earning little.", "Ask whether the cash is needed (for expansion, a buyback, or debt repayment).")


def _ocf_ratio(v: float, a: dict) -> Reading:
    if v < 0.4:
        return ("concern", f"Operations cover only {v:.0%} of current liabilities",
                "The business does not generate enough cash from its operations to pay its short-term obligations without other sources.",
                "Look at profit versus cash: a gap often means rising receivables or inventory.")
    if v < 1:
        return ("watch", f"Operations cover {v:.0%} of current liabilities", "Cash from operations pays part of the bills, with the rest coming from reserves or borrowing.", "Check whether working capital is absorbing the cash.")
    return ("strong" if v >= 1.5 else "good", f"Operations generate enough cash to cover current liabilities ({_x(v)})", "Self-funded short-term obligations are a sign of resilience.", "Check that this cash is not one-off (for example a big customer prepayment).")


def _gross_margin(v: float, a: dict) -> Reading:
    if v < 0:
        return ("concern", f"Selling below direct cost ({_p(v)})", "Direct costs exceed revenue, so every sale loses money before overheads.", "Review pricing, input costs and product mix straight away.")
    return ("info", f"{_p(v)} of revenue is left after direct costs", "This is the pool that must pay for overheads, interest, tax and profit. What counts as good depends heavily on the industry.",
            "Compare with peers and with last year: a falling gross margin points to pricing pressure or rising input costs.")


def _operating_margin(v: float, a: dict) -> Reading:
    if v < 0:
        return ("concern", f"Operating loss ({_p(v)})", "The core business costs more to run than it earns before interest and tax.", "Find out whether the loss comes from low gross margin or high overheads.")
    if v < 5:
        return ("watch", f"Thin operating profit ({_p(v)})", "Little room for error: a small rise in costs or fall in sales could push the business to a loss.", "Compare with peers: thin margins are normal in distribution and retail, a warning sign elsewhere.")
    if v <= 15:
        return ("good", f"Solid operating profit ({_p(v)})", "The core business earns a reasonable return on every unit of sales.", "Check the trend and how it compares with direct competitors.")
    return ("strong", f"High operating profit ({_p(v)})", "The business keeps a large share of each sale as operating profit, which often signals pricing power or a low-cost model.", "Check how durable the advantage is and whether margins are still rising.")


def _ebitda_margin(v: float, a: dict) -> Reading:
    if v < 0:
        return ("concern", f"Negative EBITDA margin ({_p(v)})", "Even before depreciation, the core business loses money.", "Look at costs per line and at cash burn.")
    if v < 8:
        return ("watch", f"Low EBITDA margin ({_p(v)})", "Not much cash profit per unit of sales.", "Compare with peers; capital-light and capital-heavy businesses differ widely.")
    return ("strong" if v > 20 else "good", f"EBITDA margin of {_p(v)}", "A cash-oriented view of operating profitability that ignores how much is spent on assets.", "Pair it with capital expenditure: a high margin with heavy capex can still produce little free cash.")


def _net_margin(v: float, a: dict) -> Reading:
    if v < 0:
        return ("concern", f"Net loss ({_p(v)})", "After all costs, interest and tax the business lost money in this period.", "Check if the loss is operating or one-off (impairments, exceptional items).")
    if v < 3:
        return ("watch", f"Very thin net profit ({_p(v)})", "Profits are small relative to sales and sensitive to cost changes or interest rate moves.", "Look at interest cover and the operating margin.")
    if v <= 10:
        return ("good", f"Healthy net profit ({_p(v)})", "A reasonable share of revenue turns into profit for owners.", "Compare with peers and look at whether it is stable.")
    return ("strong", f"High net profit ({_p(v)})", "The business turns a large share of revenue into profit.", "Check whether one-off gains are flattering the figure.")


def _roa(v: float, a: dict) -> Reading:
    if v < 0:
        return ("concern", f"Assets are losing money ({_p(v)})", "The assets are not earning a profit.", "Look at which assets are idle or underused.")
    if v < 3:
        return ("watch", f"Low return on assets ({_p(v)})", "Profit is small compared with the assets used to earn it.", "Check asset turnover and margins to see which is dragging.")
    return ("strong" if v > 8 else "good", f"Return on assets of {_p(v)}", "How much profit each unit of assets produces, regardless of how they are funded.", "Banks and capital-heavy industries naturally show lower ROA, so compare like with like.")


def _roe(v: float, a: dict) -> Reading:
    lev = a.get("debt_to_equity")
    boosted = lev is not None and lev > 1.5
    if v < 0:
        return ("concern", f"Shareholders lost money ({_p(v)})", "The company reported a loss on shareholders' money.", "Investigate the cause before looking at any other return measure.")
    if v < 8:
        return ("watch", f"Low return for shareholders ({_p(v)})", "Below what shareholders can typically earn elsewhere, which is often 10-14% in equity markets.", "Check whether low margins, low asset turnover or an inefficient balance sheet is behind it.")
    note = " Much of it comes from borrowing, so it is riskier than it looks." if boosted else ""
    return ("strong" if v > 15 and not boosted else "good", f"Return on equity of {_p(v)}",
            "The profit earned per unit of owners' money." + note, "Split ROE into margin, asset turnover and leverage (DuPont) to see what drives it.")


def _nopat(v: float, a: dict) -> Reading:
    return ("info" if v >= 0 else "concern", "Operating profit after tax, before financing costs" if v >= 0 else "Operating loss after tax",
            "What the business earns for all capital providers, ignoring how it is financed. It is the profit figure used to judge returns on capital.",
            "Compare with the capital employed (ROIC) and with the cost of capital.")


def _nopat_margin(v: float, a: dict) -> Reading:
    if v < 0:
        return ("concern", f"Operating loss after tax ({_p(v)})", "The core business loses money even before financing.", "Check operating margin and one-offs.")
    return ("info", f"{_p(v)} of revenue is after-tax operating profit", "A cleaner margin than net margin because it ignores interest.", "Compare with peers and watch the trend.")


def _invested_capital(v: float, a: dict) -> Reading:
    return ("info", "Capital that funds the operating business", "Debt plus equity less cash: what investors have tied up in operations.", "Use it as the base for ROIC and economic profit.")


def _roic(v: float, a: dict) -> Reading:
    spread = a.get("roic_wacc_spread")
    if v < 0:
        return ("concern", f"Capital is earning a loss ({_p(v)})", "The business earns less than nothing on the money invested in it.", "Work out whether this is a temporary build-up phase or a structural problem.")
    if spread is not None:
        if spread > 3:
            return ("strong", f"Earns {spread:.1f} points above its cost of capital", f"ROIC of {_p(v)} against a cost of capital {spread:.1f} points lower creates value on every extra unit of capital invested.", "Check how long it can last and whether it can reinvest at the same return.")
        if spread > 0:
            return ("good", f"Just above the cost of capital ({_p(v)})", "The business earns more than it costs to raise capital, but only slightly.", "Small errors in the cost of capital could flip this, so test other WACC values.")
        return ("concern" if spread < -2 else "watch", f"Below the cost of capital ({_p(v)})", "The business earns less than its capital costs, which destroys value over time.", "Look at whether margins or asset turnover can improve, or whether capital should be released.")
    if v >= 12:
        return ("strong", f"Strong return on invested capital ({_p(v)})", "Above the 8-12% many companies pay for capital.", "Enter a WACC to see the exact value creation.")
    if v >= 8:
        return ("good", f"Return on invested capital of {_p(v)}", "Around the usual cost of capital. Value is created only if it beats the company's own WACC.", "Add WACC to see the spread.")
    return ("watch", f"Low return on invested capital ({_p(v)})", "Probably below what investors require.", "Add WACC to confirm.")


def _roic_spread(v: float, a: dict) -> Reading:
    if v > 3:
        return ("strong", f"Creating value: {v:.1f} points above the cost of capital", "Each extra unit of capital invested at this return adds value for owners.", "Check how sustainable the advantage is.")
    if v > 0:
        return ("good", f"Slightly ahead of the cost of capital ({v:.1f} points)", "A modest margin of safety.", "Test the WACC: a small rise could erase it.")
    if v >= -2:
        return ("watch", f"Slightly below the cost of capital ({v:.1f} points)", "The business is close to break-even on value.", "Improve margins or asset efficiency, or release idle capital.")
    return ("concern", f"Destroying value: {abs(v):.1f} points below the cost of capital", "Investors could earn more elsewhere for the same risk.", "Question whether more capital should be put in, and what would raise the return.")


def _economic_profit(v: float, a: dict) -> Reading:
    if v > 0:
        return ("good", "Profit after charging for all capital is positive", "The business earns more than the capital it uses costs.", "Track it over time; growing economic profit is the clearest sign of value creation.")
    return ("concern", "Profit does not cover the cost of capital", "After a fair charge for the capital used, the business is not making money for its owners.", "Look at ROIC versus WACC and identify the lever to close the gap.")


def _ic_turnover(v: float, a: dict) -> Reading:
    return ("info", f"Each unit of invested capital supports {v:.2f} of revenue", "Higher means capital is working harder. It is one of the two levers (with margin) that drive ROIC.", "Compare with peers: capital-light businesses turn this over much faster.")


def _inv_turnover(v: float, a: dict) -> Reading:
    return ("info", f"Inventory turns over about {v:.1f} times a period", "Faster turnover frees cash and cuts the risk of stock going out of date.", "Compare with peers: grocery turns over fast, machinery slowly.")


def _dio(v: float, a: dict) -> Reading:
    if v > 120:
        return ("watch", f"Stock sits for about {_d(v)}", "A long holding time ties up cash and raises the risk of write-offs.", "Check slow-moving lines and the stock provision.")
    return ("info", f"Stock is held for about {_d(v)}", "How long cash is locked in inventory before it is sold.", "Compare with peers and the previous period.")


def _rec_turnover(v: float, a: dict) -> Reading:
    return ("info", f"Receivables are collected about {v:.1f} times a period", "A higher number means customers pay faster.", "Look together with DSO and credit terms.")


def _dso(v: float, a: dict) -> Reading:
    if v > 90:
        return ("concern", f"Customers take about {_d(v)} to pay", "Long collection times tie up cash and increase the risk of bad debts.", "Review the ageing of receivables and credit terms, and chase the largest overdue balances.")
    if v > 60:
        return ("watch", f"Customers take about {_d(v)} to pay", "Slower than the 30-60 days typical for most businesses.", "Compare with the credit terms you offer.")
    return ("good", f"Customers pay in about {_d(v)}", "Cash is collected reasonably quickly.", "Compare with stated credit terms to see whether customers are paying on time.")


def _pay_turnover(v: float, a: dict) -> Reading:
    return ("info", f"Suppliers are paid about {v:.1f} times a period", "Lower turnover means longer credit from suppliers.", "Look with DPO.")


def _dpo(v: float, a: dict) -> Reading:
    if v > 90:
        return ("watch", f"Suppliers are paid after about {_d(v)}", "Long payment terms give free financing but can damage supplier relationships or signal cash pressure.", "Check whether suppliers have been stretched beyond agreed terms.")
    if v < 25:
        return ("watch", f"Suppliers are paid quickly (about {_d(v)})", "Paying early uses your own cash when suppliers could be financing you.", "See if terms can be extended without losing discounts.")
    return ("good", f"Suppliers are paid in about {_d(v)}", "A balanced period that uses supplier credit without stretching it.", "Compare with the terms you have agreed.")


def _asset_turnover(v: float, a: dict) -> Reading:
    return ("info", f"Each unit of assets produces {v:.2f} of revenue", "A higher figure means the assets are used more intensively. It depends on the industry: retailers are high, utilities and real estate are low.", "Compare with peers and the trend.")


def _ccc(v: float, a: dict) -> Reading:
    if v < 0:
        return ("strong", f"Suppliers fund the cycle ({_d(v)})", "The business gets paid before it has to pay suppliers, which generates cash as it grows.", "Make sure supplier terms are agreed, not stretched.")
    if v <= 45:
        return ("good", f"Cash is tied up for about {_d(v)}", "A short operating cycle keeps funding needs low.", "Track it each period; creeping increases are an early warning.")
    if v <= 90:
        return ("watch", f"Cash is tied up for about {_d(v)}", "A long cycle means a lot of funding goes into stock and receivables.", "Look at which of the three parts (DIO, DSO, DPO) is the longest and tackle that.")
    return ("concern", f"Cash is tied up for about {_d(v)}", "Three months or more between paying for inputs and collecting from customers needs significant working capital.", "Prioritise cutting inventory days or collection time, and check financing headroom.")


def _de(v: float, a: dict) -> Reading:
    if v < 0.5:
        return ("strong", f"Low borrowing ({_x(v)})", "The business is mainly funded by owners, which gives resilience in bad years.", "Check whether too little debt is costing returns (ROE).")
    if v < 1:
        return ("good", f"Moderate borrowing ({_x(v)})", "Debt is less than equity, a comfortable balance for most industries.", "Check interest cover.")
    if v < 2:
        return ("watch", f"Substantial borrowing ({_x(v)})", "More debt than equity, so profits must hold up to service it.", "Look at interest cover and debt maturities.")
    return ("concern", f"Heavy borrowing ({_x(v)})", "Debt is more than twice equity, which leaves little room for a bad year.", "Review debt repayments, covenants, and whether earnings can support the load.")


def _debt_assets(v: float, a: dict) -> Reading:
    if v < 0.3:
        return ("strong", f"Only {v:.0%} of assets funded by debt", "A strong asset base relative to borrowing.", "Keep an eye on future borrowing plans.")
    if v < 0.5:
        return ("good", f"{v:.0%} of assets funded by debt", "A balanced mix of debt and other funding.", "Check interest cover.")
    if v < 0.7:
        return ("watch", f"{v:.0%} of assets funded by debt", "More than half the assets are financed by borrowing.", "Check interest cover and debt maturities.")
    return ("concern", f"{v:.0%} of assets funded by debt", "Little of the asset base belongs to owners, so asset values only have to fall a little to wipe out equity.", "Look at asset quality and refinancing risk.")


def _interest_cover(v: float, a: dict) -> Reading:
    if v >= 8:
        return ("strong", f"Interest is covered {_x(v)}", "Operating profit is many times the interest bill.", "Check future borrowing.")
    if v >= 3:
        return ("good", f"Interest is covered {_x(v)}", "A comfortable cushion, with profit comfortably above interest.", "Watch the trend and floating-rate exposure.")
    if v >= 1.5:
        return ("watch", f"Interest is covered only {_x(v)}", "A fall in profit or a rise in rates could make interest hard to pay.", "Look at debt maturities and what happens if profit drops by a quarter.")
    return ("concern", f"Interest is barely covered ({_x(v)})", "Almost all operating profit goes to lenders, and below 1.0x it does not cover interest at all.", "Check refinancing options and whether debt can be reduced.")


def _dscr(v: float, a: dict) -> Reading:
    if v >= 2:
        return ("strong", f"Debt payments covered {_x(v)}", "Plenty of cash earnings above what the lenders are due.", "Watch the trend.")
    if v >= 1.25:
        return ("good", f"Debt payments covered {_x(v)}", "Above the 1.25x lenders usually require.", "Check covenant levels.")
    if v >= 1:
        return ("watch", f"Debt payments barely covered ({_x(v)})", "Close to no margin for error.", "Ask whether a rescheduling is needed.")
    return ("concern", f"Earnings do not cover debt payments ({_x(v)})", "Debt service is higher than EBITDA, so reserves or new money are needed to pay it.", "Review the repayment schedule with lenders.")


def _nd_ebitda(v: float, a: dict) -> Reading:
    if v < 0:
        return ("strong", "More cash than debt", "A net cash position gives a lot of financial flexibility.", "Check how the cash is used.")
    if v < 2:
        return ("good", f"Net debt is {_x(v)} EBITDA", "Debt could be repaid from about two years of operating cash earnings.", "Watch the trend.")
    if v < 3.5:
        return ("watch", f"Net debt is {_x(v)} EBITDA", "Moderately high: many lenders start to look closely above 3x.", "Check covenants and refinancing dates.")
    return ("concern", f"Net debt is {_x(v)} EBITDA", "A long time to repay from earnings, which makes the business vulnerable to a downturn.", "Plan debt reduction and check covenants.")


def _eps(v: float, a: dict) -> Reading:
    return ("info", "Profit per share", "Useful for tracking growth over time and as the base for P/E.", "Compare with prior periods, and watch dilution from new shares.")


def _pe(v: float, a: dict) -> Reading:
    if v < 10:
        return ("info", f"Priced at {v:.1f}x earnings: low", "A low multiple can signal a bargain, slow growth, or worry about the earnings.", "Find out what the market is worried about before calling it cheap.")
    if v <= 25:
        return ("info", f"Priced at {v:.1f}x earnings: typical", "In the broad range most established companies trade in.", "Compare with peers and with the company's own history.")
    return ("info", f"Priced at {v:.1f}x earnings: high", "Investors expect strong growth, so disappointment can hit the price hard.", "Test whether the growth assumed is realistic (a reverse DCF helps).")


def _pb(v: float, a: dict) -> Reading:
    return ("info", f"Price is {v:.2f}x book value", "Compare with ROE: a business earning well above its cost of equity usually trades above book.", "Be careful with asset-light businesses, where book value understates what is owned.")


def _ev_ebitda(v: float, a: dict) -> Reading:
    if v < 8:
        return ("info", f"Valued at {v:.1f}x EBITDA: low", "Less than eight times operating cash earnings.", "Check why: slow growth, cyclical earnings, or high capital needs.")
    if v <= 14:
        return ("info", f"Valued at {v:.1f}x EBITDA: mid-range", "In the range many mature businesses trade in.", "Compare with direct peers.")
    return ("info", f"Valued at {v:.1f}x EBITDA: high", "The market is paying for growth or quality.", "Test whether the expected growth is realistic.")


def _earn_yield(v: float, a: dict) -> Reading:
    return ("info", f"Earnings are {_p(v)} of the share price", "The mirror image of P/E. Compare with the yield on government bonds to judge the premium for risk.", "If the yield is below the bond yield, the shares depend on growth.")


RULES: dict[str, Callable[[float, dict], Reading]] = {
    "current_ratio": _current_ratio, "quick_ratio": _quick_ratio, "cash_ratio": _cash_ratio, "ocf_ratio": _ocf_ratio,
    "gross_margin": _gross_margin, "operating_margin": _operating_margin, "ebitda_margin": _ebitda_margin, "net_margin": _net_margin,
    "roa": _roa, "roe": _roe, "nopat": _nopat, "nopat_margin": _nopat_margin, "invested_capital": _invested_capital, "roic": _roic,
    "roic_wacc_spread": _roic_spread, "economic_profit": _economic_profit, "invested_capital_turnover": _ic_turnover,
    "inventory_turnover": _inv_turnover, "dio": _dio, "receivables_turnover": _rec_turnover, "dso": _dso,
    "payables_turnover": _pay_turnover, "dpo": _dpo, "asset_turnover": _asset_turnover, "ccc": _ccc,
    "debt_to_equity": _de, "debt_to_assets": _debt_assets, "interest_coverage": _interest_cover, "dscr": _dscr, "net_debt_ebitda": _nd_ebitda,
    "eps": _eps, "pe": _pe, "pb": _pb, "ev_ebitda": _ev_ebitda, "earnings_yield": _earn_yield,
}

# Typical ranges: where a reader should expect the number to land, and what changes the answer.
TYPICAL: dict[str, str] = {
    "current_ratio": "1.5 to 2.5 for most businesses. Supermarkets and utilities run below 1; manufacturers need more.",
    "quick_ratio": "1.0 or higher is a common comfort level.",
    "cash_ratio": "0.2 to 0.5 is usual. Very high means idle cash; very low relies on credit lines.",
    "ocf_ratio": "1.0 or higher means operations cover short-term obligations.",
    "gross_margin": "Software 70%+, branded goods 40-60%, retail 20-35%, distribution 10-20%.",
    "operating_margin": "5-15% for many industries; under 5% is normal for retail and distribution.",
    "ebitda_margin": "10-25% for many industries; capital-light businesses run higher.",
    "net_margin": "3-10% for many industries.",
    "roa": "3-8% for most non-financial companies; banks are 1% or less.",
    "roe": "10-15% is common; above 20% needs a check on debt and one-offs.",
    "nopat": "Compare with invested capital, not on its own.",
    "nopat_margin": "Compare with peers and prior periods.",
    "invested_capital": "Use as the base for ROIC.",
    "roic": "8-12% is a typical cost of capital; 15%+ is strong.",
    "roic_wacc_spread": "Above 0 creates value; above 3 points is a clear advantage.",
    "economic_profit": "Positive means value is being created.",
    "invested_capital_turnover": "Varies from under 1x in heavy industry to several times in services and retail.",
    "inventory_turnover": "Grocery 15x+, apparel 4-6x, machinery 2-4x.",
    "dio": "30-60 days for fast-moving goods; 100+ for slow industrial goods.",
    "receivables_turnover": "6-12x a year is typical for 30-60 day terms.",
    "dso": "30-60 days for most business-to-business sales.",
    "payables_turnover": "6-12x a year is common.",
    "dpo": "30-60 days is typical; more than 90 can mean stretched suppliers.",
    "asset_turnover": "0.3 for utilities and real estate, 1-2 for manufacturers, 2+ for retail.",
    "ccc": "Under 45 days is short; negative is excellent; over 90 is long.",
    "debt_to_equity": "Under 1.0 is comfortable for most businesses; utilities and banks run higher.",
    "debt_to_assets": "Under 0.4 is conservative; over 0.6 is heavy.",
    "interest_coverage": "3x or higher is comfortable; under 1.5x is risky.",
    "dscr": "Lenders usually want 1.25x or more.",
    "net_debt_ebitda": "Under 2x is comfortable; over 4x is heavy for most industries.",
    "eps": "Compare with prior periods.",
    "pe": "10-25x for most established companies; higher for growth.",
    "pb": "Depends on ROE: higher ROE justifies a higher multiple.",
    "ev_ebitda": "8-14x for many mature industries.",
    "earnings_yield": "Compare with the government bond yield.",
}

CAUTION: dict[str, str] = {
    "current_ratio": "A high ratio can hide slow inventory or old receivables.",
    "quick_ratio": "Receivables may not be collectable in full.",
    "cash_ratio": "A snapshot at one date; year-end cash is often managed.",
    "ocf_ratio": "Operating cash flow can swing with timing of customer payments.",
    "gross_margin": "Companies classify costs differently, so only compare like with like.",
    "operating_margin": "One-off items and different depreciation policies can distort it.",
    "ebitda_margin": "Ignores capital spending, so it can flatter heavy-asset businesses.",
    "net_margin": "Includes one-off gains, tax effects and interest.",
    "roa": "Book values of assets are often old, which inflates the return for old companies.",
    "roe": "Debt and buybacks can raise ROE without improving the business.",
    "roic": "Depends on how invested capital is defined and on the tax rate used.",
    "dso": "Seasonal sales can distort year-end receivables.",
    "dpo": "Year-end payables can be managed.",
    "ccc": "Sensitive to year-end balances; look at averages over time.",
    "debt_to_equity": "Book equity can be small after buybacks or losses, which exaggerates the ratio.",
    "interest_coverage": "Uses one year's profit; look at a downturn case too.",
    "net_debt_ebitda": "EBITDA ignores capital spending and leases.",
    "pe": "Earnings can include one-offs; a low P/E is not automatically cheap.",
    "pb": "Poor guide for asset-light businesses.",
}

# Related ratios worth reading together, by key.
RELATED: dict[str, list[str]] = {
    "current_ratio": ["quick_ratio", "cash_ratio", "ccc"], "quick_ratio": ["current_ratio", "dso"], "cash_ratio": ["ocf_ratio"],
    "ocf_ratio": ["current_ratio", "dscr"], "gross_margin": ["operating_margin"], "operating_margin": ["gross_margin", "net_margin"],
    "net_margin": ["operating_margin", "interest_coverage"], "roa": ["net_margin", "asset_turnover"], "roe": ["roa", "debt_to_equity"],
    "roic": ["roic_wacc_spread", "invested_capital_turnover"], "dso": ["receivables_turnover", "ccc"], "dio": ["inventory_turnover", "ccc"],
    "dpo": ["ccc"], "ccc": ["dio", "dso", "dpo"], "debt_to_equity": ["interest_coverage", "net_debt_ebitda"],
    "interest_coverage": ["debt_to_equity", "dscr"], "dscr": ["interest_coverage", "net_debt_ebitda"], "net_debt_ebitda": ["interest_coverage", "debt_to_equity"],
    "pe": ["earnings_yield", "roe"], "ev_ebitda": ["net_debt_ebitda"],
}


def _context(key: str, a: dict) -> list[str]:
    """Notes that only make sense when two ratios are read together."""
    out: list[str] = []
    cr, ccc, dso = a.get("current_ratio"), a.get("ccc"), a.get("dso")
    if key == "current_ratio" and cr is not None and cr >= 1.5 and ccc is not None and ccc > 90:
        out.append(f"Short-term cover looks fine, but cash is tied up for about {ccc:.0f} days (cash conversion cycle). The balance sheet looks safer than the cash flow.")
    if key == "roe" and a.get("debt_to_equity") is not None and a["debt_to_equity"] > 1.5 and (a.get("roe") or 0) > 15:
        out.append("A high return on equity together with heavy borrowing means shareholders are taking more risk to earn it.")
    if key == "net_margin" and a.get("asset_turnover") is not None and a["asset_turnover"] > 2 and (a.get("net_margin") or 0) < 5:
        out.append("Thin margins with fast asset turnover is a normal high-volume model (retail, distribution): the business earns its return on volume.")
    if key == "operating_margin" and a.get("gross_margin") is not None and a.get("operating_margin") is not None and a["gross_margin"] > 40 and a["operating_margin"] < 8:
        out.append("A healthy gross margin but a low operating margin means overheads are absorbing most of the profit. Look at selling and administration costs.")
    if key == "interest_coverage" and a.get("debt_to_equity") is not None and a["debt_to_equity"] > 1.5 and (a.get("interest_coverage") or 99) < 3:
        out.append("Heavy borrowing and low interest cover together is the combination lenders worry about most.")
    if key == "dso" and dso is not None and a.get("quick_ratio") is not None and a["quick_ratio"] < 1 and dso > 60:
        out.append("Slow collection is part of why liquid assets do not fully cover current liabilities. Faster collection would improve both.")
    if key == "pe" and a.get("roe") is not None and a["roe"] < 8 and (a.get("pe") or 0) > 25:
        out.append("A high price multiple with a low return on equity means the market is paying for growth the numbers do not show yet.")
    return out


def insight_for(key: str, value: float, values: dict) -> dict | None:
    rule = RULES.get(key)
    if rule is None:
        return None
    level, headline, meaning, nxt = rule(value, values)
    related = [{"key": k, "value": values[k]} for k in RELATED.get(key, []) if k in values]
    return {
        "level": level, "label": LEVEL_LABEL[level], "headline": headline, "meaning": meaning,
        "typical": TYPICAL.get(key, ""), "caution": CAUTION.get(key, ""), "next_step": nxt,
        "context": _context(key, values), "related": related,
    }


CATEGORY_WORDS = {"Strong": "is a clear strength", "Healthy": "looks healthy", "Mixed": "is mixed", "Under pressure": "is under pressure"}


def _category_label(avg: float) -> str:
    return "Strong" if avg >= 1 else "Healthy" if avg >= 0.3 else "Mixed" if avg >= -0.7 else "Under pressure"


def summarise(results: list[dict]) -> dict:
    """An overall reading from the calculated ratios: a one-line verdict per category, strengths and concerns."""
    cats: dict[str, list[dict]] = {}
    for r in results:
        ins = r.get("insight")
        if r.get("status") == "ok" and ins:
            cats.setdefault(r["category"], []).append({"key": r["key"], "name": r["name"], "level": ins["level"], "headline": ins["headline"]})
    categories = []
    for cat, items in cats.items():
        scored = [SCORE[i["level"]] for i in items if i["level"] in SCORE]
        if not scored:
            categories.append({"category": cat, "label": "Context", "sentence": f"{cat}: {len(items)} measures calculated; they depend mostly on the industry, so compare with peers.", "count": len(items)})
            continue
        label = _category_label(sum(scored) / len(scored))
        weak = [i["name"] for i in items if i["level"] in ("watch", "concern")]
        strong = [i["name"] for i in items if i["level"] == "strong"]
        parts = [f"{cat} {CATEGORY_WORDS[label]}."]
        if strong:
            parts.append(f"Best: {', '.join(strong[:2])}.")
        if weak:
            parts.append(f"Look at: {', '.join(weak[:3])}.")
        categories.append({"category": cat, "label": label, "sentence": " ".join(parts), "count": len(items)})
    flat = [i for items in cats.values() for i in items]
    strengths = [i for i in flat if i["level"] == "strong"][:4]
    concerns = sorted([i for i in flat if i["level"] in ("concern", "watch")], key=lambda i: 0 if i["level"] == "concern" else 1)[:6]
    scored_all = [SCORE[i["level"]] for i in flat if i["level"] in SCORE]
    overall = _category_label(sum(scored_all) / len(scored_all)) if scored_all else "Not enough data"
    if not scored_all:
        headline = "Not enough inputs to give an overall reading. Add more statement lines to see more ratios."
    else:
        n_concern = sum(1 for i in flat if i["level"] == "concern")
        headline = {"Strong": "Overall this looks financially strong on the ratios that could be calculated.",
                    "Healthy": "Overall this looks healthy on the ratios that could be calculated.",
                    "Mixed": "Overall the picture is mixed: some areas are fine and some need attention.",
                    "Under pressure": "Overall several ratios are under pressure and deserve a close look."}[overall]
        if n_concern:
            headline += f" {n_concern} {'measure is' if n_concern == 1 else 'measures are'} flagged as a concern."
    return {"overall": overall, "headline": headline, "categories": categories, "strengths": strengths, "concerns": concerns,
            "note": "These readings use common rules of thumb. Industry, size and accounting policy change what is normal, so compare with peers and over time."}


def attach(results: list[dict]) -> dict:
    """Add an `insight` to every calculated ratio (in place) and return the overall summary."""
    values = {r["key"]: r["value"] for r in results if r.get("status") == "ok" and r.get("value") is not None}
    for r in results:
        r["insight"] = insight_for(r["key"], r["value"], values) if r.get("status") == "ok" and r.get("value") is not None else None
    return summarise(results)
