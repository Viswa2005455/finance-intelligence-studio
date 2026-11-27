/** More small calculators. Rates are typed in; no tax rule is assumed. */
import { emiFor } from './quickCalcs';

// ---------------------------------------------------------------- compare two loan offers
export interface LoanOffer { amount: number; annualRatePct: number; years: number; feePct: number }
export function loanCost(o: LoanOffer) {
  const emi = emiFor(o.amount, o.annualRatePct, o.years);
  const months = Math.round(o.years * 12);
  const interest = emi * months - o.amount;
  const fee = (o.amount * o.feePct) / 100;
  return { emi, interest, fee, total: interest + fee, months };
}

// ---------------------------------------------------------------- depreciation
export interface DepRow { year: number; charge: number; bookValue: number }
/** Straight line: (cost - scrap) / life each year. Reducing balance: rate x opening book value, never below scrap. */
export function depreciation(cost: number, scrap: number, lifeYears: number, method: 'straight' | 'reducing', ratePct: number): DepRow[] {
  const rows: DepRow[] = [];
  let book = cost;
  const life = Math.max(0, Math.round(lifeYears));
  for (let y = 1; y <= life; y++) {
    let charge = method === 'straight' ? (cost - scrap) / life : book * (ratePct / 100);
    if (book - charge < scrap) charge = Math.max(0, book - scrap);
    if (method === 'straight' && y === life) charge = Math.max(0, book - scrap);
    book -= charge;
    rows.push({ year: y, charge, bookValue: book });
  }
  return rows;
}

// ---------------------------------------------------------------- lease vs buy
export interface LeaseInput { price: number; resale: number; years: number; maintenancePerYear: number; leasePerYear: number; discountPct: number }
/** Present value of the cost of each choice; payments at year end, resale at the end of the last year. Lower is better. */
export function leaseVsBuy(i: LeaseInput) {
  const r = i.discountPct / 100;
  const df = (t: number) => Math.pow(1 + r, -t);
  let maint = 0, lease = 0;
  for (let t = 1; t <= i.years; t++) { maint += i.maintenancePerYear * df(t); lease += i.leasePerYear * df(t); }
  const buy = i.price + maint - i.resale * df(i.years);
  const cheaper: 'buy' | 'lease' | 'same' = buy < lease ? 'buy' : lease < buy ? 'lease' : 'same';
  return { buy, lease, cheaper, difference: Math.abs(buy - lease) };
}

// ---------------------------------------------------------------- customer concentration
export interface Concentration { rows: { who: string; amount: number; sharePct: number }[]; total: number; top1: number; top3: number; top5: number; hhi: number; level: 'low' | 'watch' | 'high'; skipped: string[] }
/** Lines of "customer, amount". Levels are a rule of thumb: one customer over 30% or the top three over 60% is high; over 15% / 40% is worth watching. */
export function concentration(text: string): Concentration {
  const map = new Map<string, number>();
  const skipped: string[] = [];
  for (const line of text.split(/\r?\n/)) {
    const t = line.trim();
    if (!t) continue;
    const m = /^(.*?)[,\t;]\s*([₹]?[\d,]+(?:\.\d+)?)\s*$/.exec(t);
    const amt = m ? Number(m[2].replace(/[₹,]/g, '')) : NaN;
    if (!m || !Number.isFinite(amt)) { skipped.push(t); continue; }
    const who = m[1].trim() || 'Unnamed';
    map.set(who, (map.get(who) ?? 0) + amt);
  }
  const total = [...map.values()].reduce((a, b) => a + b, 0);
  const rows = [...map.entries()].map(([who, amount]) => ({ who, amount, sharePct: total ? (amount / total) * 100 : 0 })).sort((a, b) => b.amount - a.amount);
  const top = (k: number) => rows.slice(0, k).reduce((a, r) => a + r.sharePct, 0);
  const hhi = rows.reduce((a, r) => a + (r.sharePct / 100) ** 2, 0) * 10_000;
  const level = top(1) > 30 || top(3) > 60 ? 'high' : top(1) > 15 || top(3) > 40 ? 'watch' : 'low';
  return { rows, total, top1: top(1), top3: top(3), top5: top(5), hhi, level, skipped };
}

// ---------------------------------------------------------------- why does my number differ?
export interface Cause { name: string; factor: number; why: string }
/** Compares your figure with the app's and tests the usual explanations: each is a fixed ratio between the two numbers. */
export function whyDiffers(app: number, yours: number, discountPct: number): { ratio: number; diffPct: number; matches: Cause[]; note: string } {
  if (!Number.isFinite(app) || !Number.isFinite(yours) || app === 0) return { ratio: NaN, diffPct: NaN, matches: [], note: 'Enter both figures; the first cannot be zero.' };
  const ratio = yours / app;
  const diffPct = (ratio - 1) * 100;
  const r = discountPct / 100;
  const pair = (name: string, factor: number, why: string): Cause[] => [{ name, factor, why }, { name: `${name} (the other way round)`, factor: 1 / factor, why: `${why} Here it runs the opposite way.` }];
  const candidates: Cause[] = [
    ...pair('Mid-year discounting', Math.pow(1 + r, 0.5), 'One side discounts cash flows from the middle of each year, the other from the end. Check the mid-year setting.'),
    ...pair('360-day against 365-day year', 365 / 360, 'Day-count conventions differ (days ratios such as DSO, and interest).'),
    ...pair('Percent against decimal', 100, '12% typed as 12 in one place and 0.12 in another.'),
    ...pair('Units: thousands', 1000, 'One figure is in thousands, the other in units.'),
    ...pair('Units: lakhs', 100_000, 'One figure is in lakhs, the other in rupees.'),
    ...pair('Units: crores', 10_000_000, 'One figure is in crores, the other in rupees.'),
    { name: 'Opposite sign', factor: -1, why: 'One side shows money out as negative and the other as positive.' },
  ];
  const matches = candidates.filter((c) => Math.abs(ratio / c.factor - 1) < 0.005);
  const note = matches.length ? 'The gap matches a known cause to within half a percent.'
    : Math.abs(diffPct) < 0.5 ? 'Within half a percent: almost certainly rounding.'
    : 'No single usual cause fits. Compare the inputs one at a time: periods included, tax rate, terminal value method, and whether net debt is deducted.';
  return { ratio, diffPct, matches, note };
}
