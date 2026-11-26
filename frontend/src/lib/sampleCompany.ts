import { api } from './api';
import type { StatementData } from './company';

export const SAMPLE_NAME = 'Sample Co (fictional company)';

type Line = StatementData['lines'][number];
const ex = (label: string, statement: string, key: string, values: number[]): Line => ({ label, statement, key, values });

/** A made-up company with three years of statements, so a new user can see every page working before they bring their own file.
 * The numbers are invented and balance: assets = liabilities + equity, and cash at the end of each year ties to the balance sheet. */
export const SAMPLE_COMPANY: StatementData = {
  company: SAMPLE_NAME, currency: 'INR', units: 'lakhs', periods: ['FY2023', 'FY2024', 'FY2025'],
  lines: [
    ex('Revenue', 'income', 'revenue', [1000, 1200, 1500]), ex('Cost of goods sold', 'income', 'cogs', [600, 700, 900]),
    ex('Gross profit', 'income', 'gross_profit', [400, 500, 600]), ex('Operating expenses', 'income', 'operating_expenses', [200, 240, 290]),
    ex('Depreciation & amortisation', 'income', 'depreciation_amortization', [50, 60, 70]), ex('Operating income (EBIT)', 'income', 'operating_income', [150, 200, 240]),
    ex('Interest expense', 'income', 'interest_expense', [20, 15, 10]), ex('Profit before tax', 'income', 'pretax_income', [130, 185, 230]),
    ex('Income tax', 'income', 'income_tax', [30, 45, 55]), ex('Net income', 'income', 'net_income', [100, 140, 175]),
    ex('Cash & equivalents', 'balance', 'cash', [80, 100, 120]), ex('Trade receivables', 'balance', 'receivables', [150, 180, 300]),
    ex('Inventory', 'balance', 'inventory', [100, 120, 150]), ex('Total current assets', 'balance', 'current_assets', [350, 420, 590]),
    ex('Property, plant & equipment', 'balance', 'ppe', [650, 680, 710]), ex('Total assets', 'balance', 'total_assets', [1000, 1100, 1300]),
    ex('Trade payables', 'balance', 'accounts_payable', [90, 100, 110]), ex('Total current liabilities', 'balance', 'current_liabilities', [200, 230, 260]),
    ex('Total debt', 'balance', 'total_debt', [300, 290, 340]), ex('Total liabilities', 'balance', 'total_liabilities', [500, 520, 600]),
    ex('Total equity', 'balance', 'total_equity', [500, 580, 700]),
    ex('Cash from operating activities', 'cashflow', 'operating_cash_flow', [90, 120, 110]), ex('Capital expenditure', 'cashflow', 'capex', [-40, -50, -60]),
    ex('Cash from investing activities', 'cashflow', 'investing_cash_flow', [-40, -50, -60]), ex('Cash from financing activities', 'cashflow', 'financing_cash_flow', [-30, -50, -30]),
    ex('Net change in cash', 'cashflow', 'net_change_in_cash', [20, 20, 20]), ex('Cash at beginning of year', 'cashflow', 'beginning_cash', [60, 80, 100]),
    ex('Cash at end of year', 'cashflow', 'ending_cash', [80, 100, 120]),
  ],
};

/** Save the sample company to the signed-in account (once) and return its id. */
export async function addSampleCompany(): Promise<string> {
  const existing = await api.get<{ items: { id: string; name: string }[] }>('/api/saved?kind=statements');
  const found = existing.items.find((i) => i.name === SAMPLE_NAME);
  if (found) return found.id;
  const made = await api.post<{ id: string }>('/api/saved', { kind: 'statements', name: SAMPLE_NAME, project_id: null, data: SAMPLE_COMPANY, note: 'Sample data' });
  return made.id;
}
