import pytest

from app.finance import FinanceInputError, forecasting

PATTERN = [5, -2, -8, 5]  # adds to zero


def series(n):
    return [10 + 2 * t + PATTERN[t % 4] for t in range(n)]


def test_exact_pattern_is_recovered():
    r = forecasting.forecast(series(12), "seasonal", 4, season=4)
    assert r.forecast == pytest.approx(series(16)[12:], abs=1e-9)
    assert r.params["slope"] == pytest.approx(2)
    assert [r.params[f"season_{k}"] for k in (1, 2, 3, 4)] == pytest.approx(PATTERN)
    assert r.backtest["mae"] == pytest.approx(0, abs=1e-8)


def test_straight_line_misses_the_pattern_seasonal_does_not():
    data = series(16)
    lin = forecasting.forecast(data, "linear", 4, holdout=4)
    sea = forecasting.forecast(data, "seasonal", 4, holdout=4, season=4)
    assert sea.backtest["mae"] < lin.backtest["mae"]


def test_needs_two_full_seasons():
    with pytest.raises(FinanceInputError):
        forecasting.forecast(series(7), "seasonal", 2, season=4)
    with pytest.raises(FinanceInputError):
        forecasting.forecast(series(12), "seasonal", 2, season=1)


def test_interval_with_noise_and_endpoint(client):
    noisy = [v + (1 if i % 3 == 0 else -0.5) for i, v in enumerate(series(16))]
    r = forecasting.forecast(noisy, "seasonal", 4, season=4)
    assert all(lo < p < hi for lo, p, hi in zip(r.lower, r.forecast, r.upper))
    resp = client.post("/api/finance/forecast", json={"series": series(12), "method": "seasonal", "season": 4, "horizon": 4})
    assert resp.status_code == 200, resp.text
    assert resp.json()["forecast"] == pytest.approx(series(16)[12:], abs=1e-6)
