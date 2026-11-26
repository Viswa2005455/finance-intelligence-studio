import { describe, expect, it } from 'vitest';
import { readAppraisal, readCashBudget, readDCF, readForecast, readPeers, readRedFlags, readScenarios, readTornado, readVariance, type DcfLike } from './readings';

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


describe('readDCF assumption checks', () => {
  const base = { wacc: 0.11, terminal_growth: 0.03, terminal_method: 'gordon' };
  it('flags terminal growth above what economies sustain', () => {
    const r = readDCF(dcf(), { ...base, terminal_growth: 0.08 }, 'INR');
    expect(r.level).toBe('concern');
    expect(r.points.join(' ')).toContain('above what most economies sustain');
  });
  it('flags capex below depreciation, odd tax rates, large margin gains and a growth cliff', () => {
    const r = readDCF(dcf(), { ...base, capex_pct_revenue: 0.03, da_pct_revenue: 0.05, tax_rate: 0.05, ebit_margin: [0.1, 0.12, 0.25], revenue_growth: [0.3, 0.25, 0.2] }, 'INR');
    const text = r.points.join(' ');
    expect(text).toContain('below depreciation');
    expect(text).toContain('outside the usual 10-45%');
    expect(text).toContain('rises by 15 points');
    expect(text).toContain('drops to 3.0% immediately');
  });
  it('says nothing about assumptions that look reasonable', () => {
    const r = readDCF(dcf(), { ...base, capex_pct_revenue: 0.06, da_pct_revenue: 0.05, tax_rate: 0.25, ebit_margin: [0.15, 0.16, 0.17], revenue_growth: [0.1, 0.08, 0.06] }, 'INR');
    expect(r.points.join(' ')).not.toContain('depreciation');
    expect(r.level).toBe('good');
  });
  it('offers next steps', () => {
    expect(readDCF(dcf(), base, 'INR').next?.map((n) => n.to)).toEqual(['/sensitivity', '/scenarios']);
  });
});


describe('readScenarios', () => {
  const sc = (name: string, eq: number, share = 0.6) => ({ name, enterprise_value: eq, equity_value: eq, terminal_share: share });
  it('summarises the range and calls a wide spread out', () => {
    const r = readScenarios([sc('Base', 1000), sc('Bear', 400), sc('Bull', 2200)], 'INR')!;
    expect(r.level).toBe('concern');
    expect(r.points[0]).toContain('Bear');
    expect(r.points[0]).toContain('Bull');
    expect(r.points.join(' ')).toContain('more than doubles');
  });
  it('is calm when the scenarios agree and warns on negative equity', () => {
    expect(readScenarios([sc('Base', 1000), sc('Low', 900), sc('High', 1100)], 'INR')!.level).toBe('good');
    expect(readScenarios([sc('Base', 1000), sc('Crash', -50)], 'INR')!.points.join(' ')).toContain('negative equity value');
  });
  it('needs two working scenarios', () => {
    expect(readScenarios([sc('Base', 1000)], 'INR')).toBeNull();
    expect(readScenarios([sc('Base', 1000), { ...sc('Bad', 1), error: 'x' }], 'INR')).toBeNull();
  });
});

describe('readCashBudget', () => {
  const periods = [{ closing: 250000 }, { closing: 220000 }, { closing: 90000 }];
  it('warns before a shortfall and names the month', () => {
    const r = readCashBudget({ total_financing: 60000, first_negative_period: 'Jun-26', lowest_closing_without_financing: -20000, lowest_period: 'Jun-26', runway: { months: 4.2 }, periods }, 100000, 'INR');
    expect(r.level).toBe('concern');
    expect(r.points.join(' ')).toContain('goes negative from Jun-26');
    expect(r.points.join(' ')).toContain('4.2 months');
  });
  it('is calm when cash stays above the minimum', () => {
    const r = readCashBudget({ total_financing: 0, first_negative_period: null, lowest_closing_without_financing: 180000, lowest_period: 'Aug-26', runway: null, periods: [{ closing: 250000 }, { closing: 240000 }] }, 100000, 'INR');
    expect(r.level).toBe('good');
    expect(r.headline).toBe('Cash covers the plan');
  });
});

describe('readTornado', () => {
  const label = (v: string) => ({ wacc: 'WACC', tg: 'Terminal growth', tax: 'Tax rate' }[v] ?? v);
  it('names the input that matters most and when it dominates', () => {
    const r = readTornado({ base_output: 1000, bars: [{ variable: 'wacc', low_output: 800, high_output: 1300, swing: 500, error: null }, { variable: 'tg', low_output: 950, high_output: 1060, swing: 110, error: null }, { variable: 'tax', low_output: 990, high_output: 1010, swing: 20, error: null }] }, label, 'INR')!;
    expect(r.headline).toBe('The valuation hinges on WACC');
    expect(r.points.join(' ')).toContain('79%');
  });
  it('says no input dominates when the swings are similar', () => {
    const r = readTornado({ base_output: 1000, bars: [{ variable: 'wacc', low_output: 0, high_output: 0, swing: 100, error: null }, { variable: 'tg', low_output: 0, high_output: 0, swing: 90, error: null }, { variable: 'tax', low_output: 0, high_output: 0, swing: 80, error: null }] }, label, 'INR')!;
    expect(r.headline).toBe('No single input dominates the valuation');
  });
});

describe('readPeers', () => {
  it('names the leader and the laggard', () => {
    const r = readPeers({ companies: ['A', 'B', 'C'], average_rank: [2.4, 1.3, 2.9], ranked_on: [20, 20, 18], warnings: [] })!;
    expect(r.headline).toBe('B leads the group, C trails');
  });
  it('needs at least two ranked companies', () => {
    expect(readPeers({ companies: ['A'], average_rank: [1], ranked_on: [10], warnings: [] })).toBeNull();
  });
});
