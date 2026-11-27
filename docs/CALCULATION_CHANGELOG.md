# Calculation changelog

Every change to a formula, threshold, rule or reading that can change a result a user sees. Newest first. Add an entry in the same
pull request as the change, say what moved and why, and name the tests that pin it.

## Unreleased (after v0.14.0)

| Area | Change | Effect on results | Pinned by |
|---|---|---|---|
| Ratios | New ratio **Equity multiplier** = average total assets / average equity (Leverage). | A new row; no existing value changes. | `tests/test_ratio_insights.py::test_equity_multiplier_levels` |
| Ratios | **DuPont**: ROE shown as net margin x asset turnover x equity multiplier, with a consistency check against the calculated ROE (tolerance: the larger of 0.5 points or 2% of ROE). | New block in the ratios response (`dupont`). | `test_dupont_*`, `tests/test_properties.py::test_dupont_always_multiplies_back_to_roe` |
| Ratios | Plain-English readings with thresholds, for example current ratio < 1 concern, 1-1.2 watch, 1.5+ strong, > 3 watch; interest cover >= 8 strong, 3-8 good, 1.5-3 watch, < 1.5 concern; net debt / EBITDA < 2 good, 2-3.5 watch, > 3.5 concern. Full list in `app/finance/ratio_insights.py`. | Wording and level only; no number changes. | `tests/test_ratio_insights.py` |
| DCF readings | Assumption checks: terminal growth > 6% (concern), WACC < 6%, capex below D&A, tax rate outside 10-45%, operating margin gain > 10 points, last-year growth more than 10 points above terminal growth. | Wording only. | `src/lib/readings.test.ts` |
| Uploads | Decimal-comma numbers (`11000,50`, `1.234,56`) are read as 11000.50 and 1234.56 **only when the whole file has no thousands-comma numbers** (`12,480`). | Files that previously gave 1,100,050 now give 11,000.50. | `tests/test_messy_inputs.py`, `tests/test_properties.py` |
| Uploads | Header rows made of a label and two or more calendar years (1990-2100, in order) are read as period headings. | Year columns are no longer treated as data. | `tests/test_messy_inputs.py::test_year_header_rows_become_periods` |
| Uploads | Oddity checks: a value 500x or more from the line's median, a total that does not add up (gross profit, net change in cash: 1% tolerance; balance sheet: 0.5%), duplicate period headings, one opposite-sign value among four or more, a percentage above 100, an identical figure in every period. | Findings listed; no data is changed. | `tests/test_oddities.py` |
| Uploads | Numbers in sentences are placed in the period named in the same clause (between commas); with no period named they are listed in order written and flagged. | New tables from text files. | `tests/test_messy_inputs.py` |
| Ratios | **Industry setting**: the level (concern / watch / good / strong) and the "typical" range of each ratio can follow one of six industries (general, software, retail, manufacturing, services, utilities). Default `general` is unchanged. Profiles in `app/finance/industries.py` are rules of thumb, not statistics. | With an industry chosen, a ratio can read at a different level; the numbers do not change. | `tests/test_ratio_insights.py` (industry tests) |
| Cash budget | Optional **interest and repayment**: interest = balance owed at the start of the period x annual rate / periods per year, paid in cash; with repayment on, cash above the minimum balance repays the loan, never more than owed. Defaults (0%, no repayment) give the old results. | New fields `interest`, `repayment`, `loan_balance` per period and `total_interest`, `peak_loan`, `ending_loan`. | `tests/test_cash_budget_loan.py` (hand-worked) |
| Forecasting | New method **seasonal trend**: straight-line trend plus an additive seasonal index per position in the season, fitted together by least squares (needs two full seasons). Interval: t-distribution on the residual spread. Other methods unchanged; their note about seasonality now points to this method. | New method only. | `tests/test_seasonal_forecast.py` |
| Compare uploads | Lines are matched by normalised name; each line's last value is compared; a line moving 10% or more is flagged. | New feature; no existing result changes. | `tests/test_compare.py` |
| Compliance calendar | Lists dates already held by the income-tax, tax-audit and GST rule sets; adds none. Items more than 30 days past are dropped; "soon" means within 7 days. | New feature. | `tests/test_compliance_calendar.py` |
| Calculators | Loan: EMI = P r / (1 - (1 + r)^-n), monthly, interest on the balance left; extra payments reduce principal in the month paid. Savings goal: monthly compounding annuity. Price: list = cost / ((1 - margin)(1 - discount)(1 - fee)). Hire cost: salary + employer PF (% of basic) + bonus + overhead % + one-off kit. Break-even: fixed / (price - variable). Cash freed = base / 365 x days. GSTIN: layout, state code and mod-36 check character. All rates are typed in; no tax rule is assumed. | New feature. | `src/lib/quickCalcs.test.ts` (hand-worked) |
| Inputs | Number boxes accept `k`, `L`/`lakh`, `cr`/`crore`, `m`/`mn`, `b`/`bn` and a trailing `%`. | Typed text only. | `src/lib/format.test.ts` |

## v0.14.0 and earlier

See `PROJECT_PLAN.md` for the audit of the finance, tax and GST engines (v0.12.0) and the rule versions
`IN-ITA1961-AY2026-27` and `IN-GST-2026.10`.
