import { describe, expect, it } from 'vitest';
import { ageReceivables, breakEven, cashFreed, checkGstin, emiFor, hireCost, loanPlan, monthlySavingFor, priceFor } from './quickCalcs';

describe('loan', () => {
  it('EMI matches the standard worked figure', () => {
    // 10,00,000 at 12% a year for 1 year: EMI 88,848.79
    expect(emiFor(1_000_000, 12, 1)).toBeCloseTo(88_848.79, 2);
    expect(emiFor(120_000, 0, 1)).toBe(10_000);
  });
  it('no extra payment: pays off in the term and total interest = EMI x n - principal', () => {
    const r = loanPlan({ principal: 1_000_000, annualRatePct: 12, years: 1, extraMonthly: 0, lumpSum: 0, lumpAtMonth: 0 });
    expect(r.months).toBe(12);
    expect(r.totalInterest).toBeCloseTo(88_848.79 * 12 - 1_000_000, 1);
    expect(r.interestSaved).toBeCloseTo(0, 6);
  });
  it('paying extra ends the loan sooner and saves interest', () => {
    const r = loanPlan({ principal: 5_000_000, annualRatePct: 9, years: 20, extraMonthly: 5000, lumpSum: 0, lumpAtMonth: 0 });
    expect(r.months).toBeLessThan(240);
    expect(r.monthsSaved).toBeGreaterThan(24);
    expect(r.interestSaved).toBeGreaterThan(0);
    expect(r.yearly[r.yearly.length - 1].balance).toBeCloseTo(0, 2);
  });
});

describe('goal, price, hire, break-even, working capital', () => {
  it('monthly saving grows to the target', () => {
    const pmt = monthlySavingFor(1_000_000, 0, 5, 12);
    // future value of an annuity: pmt x ((1.01^60 - 1) / 0.01)
    expect(pmt * ((Math.pow(1.01, 60) - 1) / 0.01)).toBeCloseTo(1_000_000, 4);
    expect(monthlySavingFor(1_000_000, 0, 5, 0)).toBeCloseTo(1_000_000 / 60, 6);
    expect(monthlySavingFor(100, 1_000_000, 5, 8)).toBe(0);
  });
  it('price gives the target margin after discount and fees', () => {
    const p = priceFor({ unitCost: 60, targetMarginPct: 25, discountPct: 10, feePct: 2, gstPct: 18 })!;
    expect(p.marginPct).toBeCloseTo(25, 9);
    expect(p.customerPays).toBeCloseTo(p.listPrice * 1.18, 9);
    expect(priceFor({ unitCost: 60, targetMarginPct: 100, discountPct: 0, feePct: 0, gstPct: 0 })).toBeNull();
  });
  it('hire cost adds provident fund, bonus and overhead', () => {
    const h = hireCost({ annualSalary: 1_200_000, basicSharePct: 50, employerPfPct: 12, bonus: 50_000, oneOffEquipment: 80_000, overheadPct: 10 });
    expect(h.pf).toBe(72_000);
    expect(h.ongoing).toBe(1_200_000 + 72_000 + 50_000 + 120_000);
    expect(h.yearOne).toBe(h.ongoing + 80_000);
  });
  it('break-even and margin of safety', () => {
    const b = breakEven(100, 60, 200_000, 8000)!;
    expect(b.units).toBe(5000);
    expect(b.revenue).toBe(500_000);
    expect(b.safetyPct).toBeCloseTo(37.5, 9);
    expect(b.profitAtExpected).toBe(120_000);
    expect(breakEven(50, 60, 1000, 10)).toBeNull();
  });
  it('cash freed by fewer days', () => {
    expect(cashFreed(36_500_000, 5)).toBe(500_000);
  });
});

describe('GSTIN check', () => {
  it('accepts a number that passes its check character', () => {
    expect(checkGstin('27AAPFU0939F1ZV').ok).toBe(true);
    expect(checkGstin(' 27aapfu0939f1zv ').ok).toBe(true);
  });
  it('explains what is wrong', () => {
    expect(checkGstin('27AAPFU0939F1ZX').problems[0]).toContain('should be V');
    expect(checkGstin('27AAPFU0939F1Z').problems[0]).toContain('15 characters');
    expect(checkGstin('99AAPFU0939F1ZV').ok).toBe(false);
    expect(checkGstin('00AAPFU0939F1ZV').problems.join(' ')).toContain('not a state');
  });
});

describe('receivables ageing', () => {
  const asOf = new Date(2026, 10, 30); // 30 Nov 2026
  it('buckets by days since the invoice date and ranks who to chase', () => {
    const a = ageReceivables('Asha Traders, 2026-11-20, 10,000\nBharat Co, 2026-09-15, 50000\nBharat Co, 2026-10-25, 5000\nCity Ltd, 20-08-2026, 7000\nbad line', asOf);
    expect(a.rows.map((r) => r.days)).toEqual([10, 76, 36, 102]);
    expect(a.totals).toEqual([10_000, 5_000, 50_000, 7_000]);
    expect(a.total).toBe(72_000);
    expect(a.skipped).toEqual(['bad line']);
    expect(a.byWho[0].who).toBe('City Ltd');
  });
});
