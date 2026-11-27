/** Small, self-contained calculators. Every rate is something the person types in: nothing here assumes a tax rule. */

// ---------------------------------------------------------------- loan with extra payments
export interface LoanInput { principal: number; annualRatePct: number; years: number; extraMonthly: number; lumpSum: number; lumpAtMonth: number }
export interface LoanResult { emi: number; months: number; totalInterest: number; baseMonths: number; baseInterest: number; interestSaved: number; monthsSaved: number; yearly: { year: number; interest: number; principal: number; balance: number }[] }

export function emiFor(principal: number, annualRatePct: number, years: number): number {
  const n = Math.round(years * 12);
  const r = annualRatePct / 100 / 12;
  if (n <= 0) return 0;
  return r === 0 ? principal / n : (principal * r) / (1 - Math.pow(1 + r, -n));
}

function run(i: LoanInput, extras: boolean) {
  const r = i.annualRatePct / 100 / 12;
  const emi = emiFor(i.principal, i.annualRatePct, i.years);
  let bal = i.principal;
  let totalInterest = 0;
  let month = 0;
  const yearly: LoanResult['yearly'] = [];
  while (bal > 0.005 && month < 1200) {
    month += 1;
    const interest = bal * r;
    let pay = Math.min(bal + interest, emi + (extras ? i.extraMonthly : 0) + (extras && month === i.lumpAtMonth ? i.lumpSum : 0));
    if (pay < interest) pay = interest; // never let the balance grow because the payment is below the interest (only possible with bad input)
    const principalPart = pay - interest;
    bal = Math.max(0, bal - principalPart);
    totalInterest += interest;
    const y = Math.ceil(month / 12);
    let row = yearly[y - 1];
    if (!row) { row = { year: y, interest: 0, principal: 0, balance: 0 }; yearly[y - 1] = row; }
    row.interest += interest; row.principal += principalPart; row.balance = bal;
  }
  return { emi, month, totalInterest, yearly };
}

export function loanPlan(i: LoanInput): LoanResult {
  const base = run(i, false);
  const withExtra = run(i, true);
  return { emi: base.emi, months: withExtra.month, totalInterest: withExtra.totalInterest, baseMonths: base.month, baseInterest: base.totalInterest,
    interestSaved: base.totalInterest - withExtra.totalInterest, monthsSaved: base.month - withExtra.month, yearly: withExtra.yearly };
}

// ---------------------------------------------------------------- saving towards a goal
/** Monthly saving that grows `start` and the savings to `target` in `years`, compounding monthly. */
export function monthlySavingFor(target: number, start: number, years: number, annualReturnPct: number): number {
  const n = Math.round(years * 12);
  if (n <= 0) return Math.max(0, target - start);
  const r = annualReturnPct / 100 / 12;
  const grownStart = start * Math.pow(1 + r, n);
  const need = target - grownStart;
  if (need <= 0) return 0;
  return r === 0 ? need / n : (need * r) / (Math.pow(1 + r, n) - 1);
}

// ---------------------------------------------------------------- price from a target margin
export interface PriceInput { unitCost: number; targetMarginPct: number; discountPct: number; feePct: number; gstPct: number }
/** Margin is on the money you keep (after discount and payment fees), as a share of that money. */
export function priceFor(i: PriceInput) {
  const m = i.targetMarginPct / 100, d = i.discountPct / 100, f = i.feePct / 100;
  const keep = (1 - m) * (1 - d) * (1 - f);
  if (m >= 1 || d >= 1 || f >= 1 || keep <= 0) return null;
  const listPrice = i.unitCost / keep;
  const received = listPrice * (1 - d) * (1 - f);
  return { listPrice, customerPays: listPrice * (1 + i.gstPct / 100), received, profitPerUnit: received - i.unitCost, marginPct: ((received - i.unitCost) / received) * 100 };
}

// ---------------------------------------------------------------- the true cost of one hire
export interface HireInput { annualSalary: number; basicSharePct: number; employerPfPct: number; bonus: number; oneOffEquipment: number; overheadPct: number }
export function hireCost(i: HireInput) {
  const pf = i.annualSalary * (i.basicSharePct / 100) * (i.employerPfPct / 100);
  const overhead = i.annualSalary * (i.overheadPct / 100);
  const yearOne = i.annualSalary + pf + i.bonus + overhead + i.oneOffEquipment;
  const ongoing = yearOne - i.oneOffEquipment;
  return { pf, overhead, yearOne, ongoing, perMonth: ongoing / 12, multiple: i.annualSalary > 0 ? ongoing / i.annualSalary : 0 };
}

// ---------------------------------------------------------------- break-even
export function breakEven(price: number, variableCost: number, fixedCost: number, expectedUnits: number) {
  const contribution = price - variableCost;
  if (contribution <= 0) return null;
  const units = fixedCost / contribution;
  const revenue = units * price;
  const safety = expectedUnits > 0 ? (expectedUnits - units) / expectedUnits : null;
  return { contribution, units, revenue, safetyPct: safety === null ? null : safety * 100, profitAtExpected: expectedUnits * contribution - fixedCost };
}

// ---------------------------------------------------------------- working capital what-if
/** Cash freed by cutting a day-count: receivable days work on revenue, stock and payable days on cost of sales. */
export function cashFreed(annualBase: number, daysChange: number): number {
  return (annualBase / 365) * daysChange;
}

// ---------------------------------------------------------------- GSTIN check
const CHARS = '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ';
const STATES = new Set([...Array.from({ length: 38 }, (_, k) => String(k + 1).padStart(2, '0')), '97', '99']);

export function checkGstin(raw: string): { ok: boolean; problems: string[]; state?: string } {
  const g = raw.trim().toUpperCase();
  const problems: string[] = [];
  if (g.length !== 15) return { ok: false, problems: [`A GSTIN has 15 characters; this has ${g.length}.`] };
  if (!/^\d{2}[A-Z]{5}\d{4}[A-Z][1-9A-Z]Z[0-9A-Z]$/.test(g)) problems.push('The layout is wrong: 2 digits, 5 letters, 4 digits, 1 letter, 1 letter or digit, Z, then a check character.');
  if (!STATES.has(g.slice(0, 2))) problems.push(`${g.slice(0, 2)} is not a state or territory code.`);
  if (!problems.length) {
    let sum = 0;
    for (let k = 0; k < 14; k++) {
      const p = CHARS.indexOf(g[k]) * (k % 2 === 0 ? 1 : 2);
      sum += Math.floor(p / 36) + (p % 36);
    }
    const check = CHARS[(36 - (sum % 36)) % 36];
    if (check !== g[14]) problems.push(`The last character should be ${check}: the number does not pass its own check, so it has probably been mistyped.`);
  }
  return { ok: problems.length === 0, problems, state: g.slice(0, 2) };
}

// ---------------------------------------------------------------- receivables ageing
export const BUCKETS = ['Not yet 30 days', '31 to 60 days', '61 to 90 days', 'Over 90 days'] as const;
export interface AgeRow { who: string; date: string; amount: number; days: number; bucket: number }
export interface Ageing { rows: AgeRow[]; totals: number[]; total: number; skipped: string[]; byWho: { who: string; total: number; oldest: number }[] }

/** Lines of "customer, invoice date (YYYY-MM-DD or DD-MM-YYYY), amount". Days run from the invoice date to `asOf`. */
export function ageReceivables(text: string, asOf: Date): Ageing {
  const rows: AgeRow[] = [];
  const skipped: string[] = [];
  for (const line of text.split(/\r?\n/)) {
    const t = line.trim();
    if (!t) continue;
    // Find the date, then take the name before it and the amount after it, so "10,000" in the amount does not split the line.
    const m0 = /^(.*?)[,	;]\s*(\d{4}-\d{2}-\d{2}|\d{2}[-/]\d{2}[-/]\d{4})\s*[,	;]\s*(.+)$/.exec(t);
    if (!m0) { skipped.push(t); continue; }
    const ds = m0[2];
    const amount = Number(m0[3].replace(/[₹,\s]/g, ''));
    const m = /^\d{4}/.test(ds) ? ds.split('-') .map(Number) : (() => { const x = ds.split(/[-/]/).map(Number); return [x[2], x[1], x[0]]; })();
    if (!Number.isFinite(amount) || m.some((n) => !Number.isFinite(n))) { skipped.push(t); continue; }
    const who0 = m0[1].trim();
    const d = new Date(Date.UTC(m[0], m[1] - 1, m[2]));
    const today = Date.UTC(asOf.getFullYear(), asOf.getMonth(), asOf.getDate());
    const days = Math.round((today - d.getTime()) / 86_400_000);
    if (Number.isNaN(days)) { skipped.push(t); continue; }
    rows.push({ who: who0 || 'Unnamed', date: ds, amount, days, bucket: days <= 30 ? 0 : days <= 60 ? 1 : days <= 90 ? 2 : 3 });
  }
  const totals = [0, 0, 0, 0];
  const who = new Map<string, { total: number; oldest: number }>();
  for (const r of rows) {
    totals[r.bucket] += r.amount;
    const w = who.get(r.who) ?? { total: 0, oldest: 0 };
    w.total += r.amount; w.oldest = Math.max(w.oldest, r.days);
    who.set(r.who, w);
  }
  // Chase first: the customers with the most money more than 60 days old, then the biggest balances.
  const byWho = [...who.entries()].map(([name, v]) => ({ who: name, ...v })).sort((a, b) => b.oldest - a.oldest || b.total - a.total);
  return { rows, totals, total: totals.reduce((a, b) => a + b, 0), skipped, byWho };
}
