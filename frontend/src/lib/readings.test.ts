import { describe, expect, it } from 'vitest';
import { readAppraisal, readDCF, readForecast, readRedFlags, readVariance, type DcfLike } from './readings';

const dcf = (o: Partial<DcfLike> = {}): DcfLike => ({
  enterprise_value: 1000, equity_value: 900, value_per_share: 90, terminal_value_share_of_ev: 0.6, implied_exit_multiple: 9,
  implied_terminal_growth: 0.03, warnings: [], years: [{ fcff: 50 }, { fcff: 60 }], ...o,
});

describe('readDCF', () => {
  it('is healthy when terminal value is a modest share and WACC is well above growth', () => {
    const r = readDCF(dcf(), { wacc: 0.11, terminal_growth: 0.03, terminal_method: 'gordon' }, 'INR');
    expect(r.level).toBe('good');
    expect(r.points[0]).toContain('60%');
  });
  it('flags an extreme terminal share and a tiny WACC-growth gap as a concern', () => {
    const r = readDCF(dcf({ terminal_value_share_of_ev: 0.9 }), { wacc: 0.07, terminal_growth: 0.06, terminal_method: 'gordon' }, 'INR');
    expect(r.level).toBe('concern');
    expect(r.points.join(' ')).toContain('1.0% above'); // WACC 7% is 1.0 point above growth 6%
  });
  it('compares with the market price when one is given', () => {
    const up = readDCF(dcf({ value_per_share: 120 }), { wacc: 0.11, terminal_growth: 0.03, terminal_method: 'gordon' }, 'INR', 100);
    expect(up.points.join(' ')).toContain('20% above');
    const down = readDCF(dcf({ value_per_share: 80 }), { wacc: 0.11, terminal_growth: 0.03, terminal_method: 'gordon' }, 'INR', 100);
    expect(down.points.join(' ')).toContain('20% below');
  });
});

describe('readForecast', () => {
  const base = { method: 'linear', history: [10, 11, 12, 13, 14, 15, 16, 17, 18], forecast: [19, 20, 21], lower: [18, 18.5, 19], upper: [20, 21.5, 23], notes: [] };
  it('grades accuracy by the holdout MAPE', () => {
    expect(readForecast({ ...base, backtest: { holdout: 3, mape: 3, mae: 1 } }).level).toBe('strong');
    expect(readForecast({ ...base, backtest: { holdout: 3, mape: 8, mae: 1 } }).level).toBe('good');
    expect(readForecast({ ...base, backtest: { holdout: 3, mape: 15, mae: 1 } }).level).toBe('watch');
    expect(readForecast({ ...base, backtest: { holdout: 3, mape: 40, mae: 1 } }).level).toBe('concern');
  });
  it('says so when accuracy cannot be measured', () => {
    const r = readForecast({ ...base, backtest: { holdout: 3, mape: null, mae: null } });
    expect(r.level).toBe('info');
    expect(r.points[0]).toContain('could not give');
  });
  it('warns about short histories', () => {
    const r = readForecast({ ...base, history: [1, 2, 3, 4], backtest: { holdout: 1, mape: 3, mae: 1 } });
    expect(r.points.join(' ')).toContain('Only 4 data points');
  });
});

describe('readAppraisal', () => {
  const tl = [0, 1, 2, 3, 4, 5].map((t) => ({ t }));
  it('accepts a positive-NPV project with a unique IRR above the rate', () => {
    const r = readAppraisal({ npv: 20000, irr: { status: 'unique', values: [0.18], sign_changes: 1 }, payback: { period: 3 }, discounted_payback: { period: 3.5 }, profitability_index: { value: 1.2 }, timeline: tl }, 0.1, 'INR');
    expect(r.level).toBe('good');
    expect(r.headline).toContain('adds value');
    expect(r.points.join(' ')).toContain('8.0% above');
  });
  it('rejects a negative-NPV project', () => {
    const r = readAppraisal({ npv: -5000, irr: { status: 'unique', values: [0.05], sign_changes: 1 }, payback: { period: null }, discounted_payback: { period: null }, profitability_index: { value: 0.9 }, timeline: tl }, 0.1, 'INR');
    expect(r.level).toBe('concern');
  });
  it('tells people to rely on NPV when there are several IRRs', () => {
    const r = readAppraisal({ npv: 100, irr: { status: 'multiple', values: [0.1, 0.4], sign_changes: 3 }, payback: { period: 2 }, discounted_payback: { period: 2 }, profitability_index: { value: 1.01 }, timeline: tl }, 0.1, 'INR');
    expect(r.points.join(' ')).toContain('more than one IRR');
  });
});

describe('readVariance', () => {
  const line = (o: object) => ({ name: 'X', kind: 'expense', variance: 0, variance_pct: 0, status: 'on_budget', profit_impact: 0, material: false, ...o });
  it('reads a clearly adverse profit variance as a concern and names the biggest line', () => {
    const big = line({ name: 'Cost of goods sold', profit_impact: -52000, status: 'adverse', material: true });
    const r = readVariance({ lines: [big, line({})], totals: { profit: line({ name: 'Profit', variance: -60000, variance_pct: -12, status: 'adverse' }) }, largest_contributors: [big] }, 'INR');
    expect(r.level).toBe('concern');
    expect(r.points.join(' ')).toContain('Cost of goods sold');
    expect(r.points.join(' ')).toContain('1 of 2 lines are above your materiality limit');
  });
  it('is positive when profit beats budget', () => {
    const r = readVariance({ lines: [line({})], totals: { profit: line({ variance: 5000, variance_pct: 2, status: 'favourable' }) }, largest_contributors: [] }, 'INR');
    expect(r.level).toBe('good');
  });
});

describe('readRedFlags', () => {
  it('summarises a clean result', () => {
    const r = readRedFlags({ beneish: { status: 'ok', verdict: 'no_flag', value: -2.5 }, altman: [{ name: "Altman Z''", status: 'ok', verdict: 'safe' }], piotroski: { status: 'ok', score: 8, tested: 9 }, flags: [] });
    expect(r.level).toBe('good');
    expect(r.headline).toContain('No major red flags');
  });
  it('is a concern with a Beneish flag or high-severity warning', () => {
    const r = readRedFlags({ beneish: { status: 'ok', verdict: 'flag', value: -1 }, altman: [], piotroski: { status: 'ok', score: 2, tested: 9 }, flags: [{ severity: 'high', title: 'Profit not turning into cash' }] });
    expect(r.level).toBe('concern');
    expect(r.points.join(' ')).toContain('Profit not turning into cash');
  });
  it('does not claim a clean bill of health without data', () => {
    const r = readRedFlags({ beneish: { status: 'missing', verdict: null, value: null }, altman: [], piotroski: { status: 'missing', score: 0, tested: 0 }, flags: [] });
    expect(r.headline).not.toContain('No major red flags in the screens that could run');
  });
});
