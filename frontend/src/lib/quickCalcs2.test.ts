import { describe, expect, it } from 'vitest';
import { concentration, depreciation, leaseVsBuy, loanCost, whyDiffers } from './quickCalcs2';

describe('more calculators', () => {
  it('loan offers: a fee adds to the cost', () => {
    const a = loanCost({ amount: 1_000_000, annualRatePct: 12, years: 1, feePct: 0 });
    expect(a.emi).toBeCloseTo(88_848.79, 2);
    expect(a.total).toBeCloseTo(88_848.79 * 12 - 1_000_000, 1);
    const b = loanCost({ amount: 1_000_000, annualRatePct: 11.5, years: 1, feePct: 2 });
    expect(b.fee).toBe(20_000);
    expect(b.total).toBeCloseTo(b.interest + 20_000, 9);
  });

  it('straight line ends at scrap; reducing balance never goes below it', () => {
    const s = depreciation(100_000, 10_000, 5, 'straight', 0);
    expect(s.map((r) => r.charge)).toEqual([18_000, 18_000, 18_000, 18_000, 18_000]);
    expect(s[4].bookValue).toBeCloseTo(10_000, 6);
    const w = depreciation(100_000, 20_000, 5, 'reducing', 40);
    expect(w[0].charge).toBe(40_000);
    expect(w[1].charge).toBeCloseTo(24_000, 6);
    expect(w[2].charge).toBeCloseTo(14_400, 6); // 40% of 36,000; book value 21,600 is still above scrap
    expect(w[3].charge).toBeCloseTo(1_600, 6); // 40% of 21,600 would go below scrap, so it stops at 20,000
    expect(w[4].charge).toBe(0);
    expect(w[4].bookValue).toBeCloseTo(20_000, 6);
  });

  it('lease vs buy: plain arithmetic at 0%, discounting applied otherwise', () => {
    const z = leaseVsBuy({ price: 1000, resale: 200, years: 3, maintenancePerYear: 50, leasePerYear: 300, discountPct: 0 });
    expect(z.buy).toBe(950);
    expect(z.lease).toBe(900);
    expect(z.cheaper).toBe('lease');
    expect(z.difference).toBe(50);
    const d = leaseVsBuy({ price: 1000, resale: 200, years: 3, maintenancePerYear: 50, leasePerYear: 300, discountPct: 10 });
    expect(d.lease).toBeCloseTo(300 * (1 / 1.1 + 1 / 1.21 + 1 / 1.331), 6);
  });

  it('customer concentration', () => {
    const c = concentration('A, 600\nB, 200\nC, 100\nD, 100\nbad');
    expect(c.top1).toBeCloseTo(60, 9);
    expect(c.level).toBe('high');
    expect(c.skipped).toEqual(['bad']);
    expect(c.hhi).toBeCloseTo(0.36 * 10_000 + 400 + 100 + 100, 6);
    expect(concentration(Array.from({ length: 20 }, (_, i) => `C${i}, 100`).join('\n')).level).toBe('low');
    expect(concentration('X, 10,000\nX, 5,000').rows[0].amount).toBe(15_000);
  });

  it('spots the usual reasons two numbers differ', () => {
    expect(whyDiffers(100, 100 * Math.sqrt(1.11), 11).matches.map((m) => m.name)).toContain('Mid-year discounting');
    expect(whyDiffers(1_200_000, 12, 10).matches.map((m) => m.name)).toContain('Units: lakhs (the other way round)');
    expect(whyDiffers(100, 100.2, 10).note).toContain('rounding');
    expect(whyDiffers(100, 150, 10).matches).toEqual([]);
    expect(Number.isNaN(whyDiffers(0, 5, 10).ratio)).toBe(true);
  });
});
