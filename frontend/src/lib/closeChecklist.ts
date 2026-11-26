/** The month-end close checklist: a standard list of steps, each linked to the page that helps with it. */
export interface CloseItem { id: string; group: string; label: string; to?: string; done: boolean; owner: string; note: string }
export interface CloseState { month: string; items: CloseItem[] }

const step = (id: string, group: string, label: string, to?: string): CloseItem => ({ id, group, label, to, done: false, owner: '', note: '' });

export const TEMPLATE: CloseItem[] = [
  step('bank', 'Cash and bank', 'Reconcile every bank and cash account to the statement', '/upload'),
  step('cashrev', 'Cash and bank', 'Review the cash position and the next months\' cash budget', '/cash-flow'),
  step('sales', 'Sales and receivables', 'Post all invoices and credit notes for the month'),
  step('ageing', 'Sales and receivables', 'Review receivable ageing and chase or provide for overdue balances', '/ratios'),
  step('purch', 'Purchases and payables', 'Accrue goods and services received but not yet invoiced'),
  step('payables', 'Purchases and payables', 'Reconcile supplier balances and review payment timing', '/ratios'),
  step('stock', 'Inventory and fixed assets', 'Count or confirm inventory and write down slow or damaged stock'),
  step('dep', 'Inventory and fixed assets', 'Post depreciation and any asset additions or disposals', '/accounting'),
  step('payroll', 'Payroll and statutory dues', 'Post payroll and confirm statutory dues (PF, ESI, TDS) are paid or accrued', '/income-tax'),
  step('gst', 'Tax', 'Prepare and reconcile GST returns (GSTR-1, GSTR-3B, 2B match)', '/gst'),
  step('accr', 'Accruals and provisions', 'Post accruals, prepayments and provisions; reverse last month\'s where needed', '/accounting'),
  step('tb', 'Reporting', 'Run the trial balance and clear suspense and unexplained items'),
  step('stmts', 'Reporting', 'Produce the income statement, balance sheet and cash flow', '/statements'),
  step('var', 'Reporting', 'Compare with budget and explain material variances', '/variance'),
  step('ratios', 'Reporting', 'Review the ratios and their plain-English reading', '/ratios'),
  step('flags', 'Reporting', 'Run the red-flag screens and look into anything flagged', '/red-flags'),
  step('sign', 'Sign-off', 'Review by someone other than the preparer, then lock the period'),
];

export function currentMonth(d = new Date()): string {
  return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}`;
}

export const freshChecklist = (month = currentMonth()): CloseState => ({ month, items: TEMPLATE.map((i) => ({ ...i })) });

export function progress(s: CloseState): { done: number; total: number; pct: number } {
  const done = s.items.filter((i) => i.done).length;
  return { done, total: s.items.length, pct: s.items.length ? Math.round((done / s.items.length) * 100) : 0 };
}

/** Roll to a new month: keep the steps and owners, clear the ticks and notes. */
export function nextMonth(s: CloseState): CloseState {
  const [y, m] = s.month.split('-').map(Number);
  const d = new Date(y, m, 1);  // month is 1-based here, so this is the following month
  return { month: currentMonth(d), items: s.items.map((i) => ({ ...i, done: false, note: '' })) };
}
