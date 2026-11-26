import { describe, expect, it } from 'vitest';
import { SAMPLE_COMPANY } from './sampleCompany';

const by = (key: string) => SAMPLE_COMPANY.lines.find((l) => l.key === key)!.values as number[];

describe('the sample company', () => {
  it('has a balance sheet that balances in every year', () => {
    for (let i = 0; i < SAMPLE_COMPANY.periods.length; i++) {
      expect(by('total_assets')[i]).toBe(by('total_liabilities')[i] + by('total_equity')[i]);
    }
  });
  it('has an income statement that adds up', () => {
    for (let i = 0; i < 3; i++) {
      expect(by('revenue')[i] - by('cogs')[i]).toBe(by('gross_profit')[i]);
      expect(by('pretax_income')[i] - by('income_tax')[i]).toBe(by('net_income')[i]);
      expect(by('operating_income')[i] - by('interest_expense')[i]).toBe(by('pretax_income')[i]);
    }
  });
  it('has a cash flow that ties to the balance sheet', () => {
    for (let i = 0; i < 3; i++) {
      expect(by('operating_cash_flow')[i] + by('investing_cash_flow')[i] + by('financing_cash_flow')[i]).toBe(by('net_change_in_cash')[i]);
      expect(by('beginning_cash')[i] + by('net_change_in_cash')[i]).toBe(by('ending_cash')[i]);
      expect(by('ending_cash')[i]).toBe(by('cash')[i]);
    }
  });
  it('gives every line the same number of periods and a known statement', () => {
    for (const l of SAMPLE_COMPANY.lines) {
      expect(l.values).toHaveLength(SAMPLE_COMPANY.periods.length);
      expect(['income', 'balance', 'cashflow']).toContain(l.statement);
    }
  });
});
