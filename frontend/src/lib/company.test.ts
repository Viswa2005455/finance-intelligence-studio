import { describe, expect, it } from 'vitest';
import { statedUnits, statementDataFromUpload, toCompany, type SuggestedSheet } from './company';

const line = (label: string, key: string | null, values: (number | null)[]) => ({ label, key, values, source: null });

const sheets: SuggestedSheet[] = [
  { sheet: 'Income 12m', statement: 'income', periods: ['FY25', 'FY26'], months: 12,
    lines: [line('Net sales', 'revenue', [416, 479]), line('Net income', 'net_income', [112, 132])] },
  { sheet: 'Income 3m', statement: 'income', periods: ['Q4 FY25', 'Q4 FY26'], months: 3,
    lines: [line('Net sales', 'revenue', [102, 114])] },
  { sheet: 'Balance', statement: 'balance', periods: ['FY25', 'FY26'],
    lines: [line('Total assets', 'total_assets', [359, 405]), line('Total assets again', 'total_assets', [1, 2])] },
];

describe('statementDataFromUpload', () => {
  it('uses the longest reporting length for a statement and one period set across statements', () => {
    const d = statementDataFromUpload('apple.pdf', sheets)!;
    expect(d.periods).toEqual(['FY25', 'FY26']);
    const c = toCompany(d);
    expect(c.items.revenue).toEqual([416, 479]); // the 12-month sheet, not the 3-month one
    expect(c.items.total_assets).toEqual([359, 405]);
  });

  it('takes each standard item from the first line that matches it', () => {
    const d = statementDataFromUpload('apple.pdf', sheets)!;
    expect(d.lines.filter((l) => l.key === 'total_assets')).toHaveLength(1);
    expect(d.lines.find((l) => l.label === 'Total assets again')?.key).toBeNull();
  });

  it('names the company after the file and returns nothing for a file without statements', () => {
    expect(statementDataFromUpload('FY26 Q4.pdf', sheets)!.company).toBe('FY26 Q4');
    expect(statementDataFromUpload('x.pdf', [])).toBeNull();
  });

  it('carries the currency and units the file itself states', () => {
    const d = statementDataFromUpload('a.pdf', sheets, { currencies: { $: 9, '₹': 1 }, units: { millions: 3 } })!;
    expect(d.currency).toBe('$');
    expect(d.units).toBe('millions');
    expect(statedUnits(null)).toEqual({ currency: undefined, units: undefined });
  });
});
