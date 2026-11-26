"""Starting points for the DCF page. Each is a complete, illustrative set of assumptions for a type of business, so a new
user can see a sensible shape quickly and then replace the numbers with their own. They are examples, not forecasts or
market data, and the page says so."""

from __future__ import annotations

TEMPLATES: list[dict] = [
    {
        "id": "saas", "name": "Software (SaaS) growth company",
        "description": "Fast growth that fades, thin margins today and large margins later, almost no capital spending, no debt.",
        "model": {"base_revenue": 1000, "revenue_growth": [0.35, 0.28, 0.22, 0.17, 0.13], "ebit_margin": [0.0, 0.06, 0.12, 0.17, 0.22], "tax_rate": 0.25,
                  "da_pct_revenue": 0.03, "capex_pct_revenue": 0.03, "nwc_pct_revenue": 0.02, "wacc": 0.12, "terminal_growth": 0.04,
                  "terminal_method": "gordon", "exit_multiple": 14, "debt": 0, "cash": 400, "shares_outstanding": 100, "mid_year": False},
    },
    {
        "id": "manufacturer", "name": "Mature manufacturer",
        "description": "Steady low growth, stable margins, heavy capital spending and working capital, moderate debt.",
        "model": {"base_revenue": 1000, "revenue_growth": [0.06, 0.05, 0.05, 0.04, 0.04], "ebit_margin": [0.14, 0.14, 0.14, 0.14, 0.14], "tax_rate": 0.25,
                  "da_pct_revenue": 0.05, "capex_pct_revenue": 0.06, "nwc_pct_revenue": 0.15, "wacc": 0.10, "terminal_growth": 0.035,
                  "terminal_method": "gordon", "exit_multiple": 8, "debt": 350, "cash": 80, "shares_outstanding": 60, "mid_year": False},
    },
    {
        "id": "retail", "name": "Retail chain",
        "description": "Store-led growth that slows, thin operating margins, moderate capital spending and some debt.",
        "model": {"base_revenue": 1000, "revenue_growth": [0.10, 0.09, 0.08, 0.07, 0.06], "ebit_margin": [0.07, 0.072, 0.075, 0.075, 0.075], "tax_rate": 0.25,
                  "da_pct_revenue": 0.035, "capex_pct_revenue": 0.045, "nwc_pct_revenue": 0.08, "wacc": 0.11, "terminal_growth": 0.04,
                  "terminal_method": "gordon", "exit_multiple": 9, "debt": 200, "cash": 60, "shares_outstanding": 80, "mid_year": False},
    },
    {
        "id": "startup", "name": "Start-up moving to profit",
        "description": "Very fast growth from a small base, losses first, a higher discount rate for the extra risk, cash in the bank.",
        "model": {"base_revenue": 200, "revenue_growth": [0.60, 0.45, 0.35, 0.28, 0.20], "ebit_margin": [-0.25, -0.10, 0.03, 0.10, 0.16], "tax_rate": 0.25,
                  "da_pct_revenue": 0.03, "capex_pct_revenue": 0.05, "nwc_pct_revenue": 0.05, "wacc": 0.15, "terminal_growth": 0.04,
                  "terminal_method": "gordon", "exit_multiple": 12, "debt": 0, "cash": 150, "shares_outstanding": 50, "mid_year": False},
    },
]
