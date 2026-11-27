"""Industry norms for the plain-English ratio readings.

A current ratio of 0.8 is a warning for a manufacturer and perfectly normal for a supermarket, so the same number has to be judged
against the right neighbours. Each profile gives, for the ratios where industry matters most, the points at which a value turns from
"concern" to "watch" to "healthy" to "strong", and what is typical.

These are rules of thumb gathered from common practice, not statutory standards or a data feed. They are meant to stop a sensible number
being flagged as a problem (or hidden) because it was compared with the wrong kind of business. Nothing here changes a calculated value.

Spec per ratio: (direction, concern, watch, strong, typical). Direction "higher" means a higher value is better: below `concern` is a
concern, below `watch` is a watch, at or above `strong` is strong, otherwise healthy. Direction "lower" mirrors it: above `concern`,
above `watch`, at or below `strong`.
"""

from __future__ import annotations

Spec = tuple[str, float, float, float, str]

INDUSTRIES: dict[str, str] = {
    "general": "General / mixed",
    "software": "Software and online services",
    "retail": "Retail and distribution",
    "manufacturing": "Manufacturing",
    "services": "Professional services",
    "utilities": "Utilities and infrastructure",
}

PROFILES: dict[str, dict[str, Spec]] = {
    "software": {
        "current_ratio": ("higher", 1.0, 1.5, 2.5, "1.5-3x: cash-rich, with customers often paying in advance."),
        "gross_margin": ("higher", 50, 65, 80, "70-85% is usual for software."),
        "operating_margin": ("higher", -15, 5, 20, "Growing companies may run near zero or below; mature ones reach 20%+."),
        "net_margin": ("higher", -15, 3, 15, "Mature software firms reach 15% or more; growth phases can be negative."),
        "dso": ("lower", 90, 60, 40, "40-60 days for business customers."),
        "debt_to_equity": ("lower", 1.0, 0.5, 0.2, "Little or no borrowing is usual."),
        "roe": ("higher", 5, 12, 20, "15-25% for mature companies."),
    },
    "retail": {
        "current_ratio": ("higher", 0.7, 1.0, 1.5, "0.8-1.5x: stock turns quickly and suppliers fund much of it."),
        "quick_ratio": ("higher", 0.2, 0.4, 0.8, "Often well below 1.0 because stock is the main asset."),
        "gross_margin": ("higher", 15, 20, 35, "20-35% for general retail; groceries sit at the low end."),
        "operating_margin": ("higher", 1, 3, 8, "3-8% is normal; thin margins are the business model."),
        "net_margin": ("higher", 0.5, 2, 5, "2-5%."),
        "dso": ("lower", 30, 15, 5, "Customers mostly pay at the till, so receivables are small."),
        "dio": ("lower", 120, 90, 45, "45-90 days of stock."),
        "ccc": ("lower", 60, 30, 0, "Short or negative: suppliers are paid after goods are sold."),
        "debt_to_equity": ("lower", 2.0, 1.2, 0.5, "Moderate borrowing for stores and stock."),
        "roe": ("higher", 8, 12, 20, "12-20% for healthy chains."),
    },
    "manufacturing": {
        "current_ratio": ("higher", 1.0, 1.3, 2.0, "1.5-2.5x: stock and receivables need funding."),
        "quick_ratio": ("higher", 0.6, 0.9, 1.2, "0.8-1.2x."),
        "gross_margin": ("higher", 15, 22, 35, "25-40% for many manufacturers."),
        "operating_margin": ("higher", 4, 8, 15, "8-15%."),
        "net_margin": ("higher", 2, 4, 10, "4-10%."),
        "dso": ("lower", 90, 70, 45, "45-70 days."),
        "dio": ("lower", 150, 110, 60, "60-110 days of stock."),
        "ccc": ("lower", 140, 100, 60, "60-100 days."),
        "debt_to_equity": ("lower", 2.0, 1.2, 0.5, "0.5-1.2x for capital-heavy businesses."),
        "interest_coverage": ("higher", 2.0, 3.5, 8.0, "4-8x."),
        "roe": ("higher", 8, 12, 18, "12-18%."),
    },
    "services": {
        "current_ratio": ("higher", 1.0, 1.3, 2.0, "1.3-2.5x."),
        "gross_margin": ("higher", 30, 40, 60, "40-70% after staff costs charged to clients."),
        "operating_margin": ("higher", 8, 15, 25, "15-25% for well-run practices."),
        "net_margin": ("higher", 5, 10, 18, "10-18%."),
        "dso": ("lower", 100, 75, 50, "50-75 days: fees are often billed in arrears."),
        "debt_to_equity": ("lower", 1.5, 0.8, 0.3, "Usually low: few physical assets to finance."),
        "roe": ("higher", 10, 15, 25, "15-25%."),
    },
    "utilities": {
        "current_ratio": ("higher", 0.6, 0.8, 1.2, "0.7-1.2x: steady cash flows need little buffer."),
        "operating_margin": ("higher", 10, 15, 25, "15-25%."),
        "net_margin": ("higher", 4, 8, 14, "8-14%."),
        "dso": ("lower", 90, 60, 40, "40-60 days."),
        "debt_to_equity": ("lower", 3.0, 2.0, 1.0, "1-2x: stable regulated returns support heavy borrowing."),
        "interest_coverage": ("higher", 1.5, 2.5, 4.0, "2.5-4x."),
        "roe": ("higher", 6, 9, 13, "9-13%."),
    },
}


def level_for(spec: Spec, value: float) -> str:
    direction, concern, watch, strong, _ = spec
    if direction == "higher":
        return "concern" if value < concern else "watch" if value < watch else "strong" if value >= strong else "good"
    return "concern" if value > concern else "watch" if value > watch else "strong" if value <= strong else "good"


def spec_for(industry: str, key: str) -> Spec | None:
    return PROFILES.get(industry, {}).get(key)
