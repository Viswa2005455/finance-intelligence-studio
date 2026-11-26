/** Plain-English readings of results the engines have already calculated.
 *
 * Every function here is pure: it only words numbers it is given, never recalculates them, and every
 * threshold is a stated rule of thumb. The `caution` says what could make the reading misleading. The ratio
 * readings live on the server (app/finance/ratio_insights.py); these cover the pages that are calculated in
 * the browser from engine results. */
import { fmtMoney, fmtPct, isNum, type Currency } from './format';

export type Level = 'strong' | 'good' | 'watch' | 'concern' | 'info';
export interface Reading { level: Level; headline: string; points: string[]; caution?: string }

export const LEVEL_LABEL: Record<Level, string> = { strong: 'Strong', good: 'Healthy', watch: 'Watch', concern: 'Concern', info: 'Context' };

const worst = (levels: Level[]): Level => (['concern', 'watch', 'info', 'good', 'strong'] as Level[]).find((l) => levels.includes(l)) ?? 'info';

// ------------------------------------------------------------------------------------------------ DCF
export interface DcfLike {
  enterprise_value: number; equity_value: number; value_per_share: number | null; terminal_value_share_of_ev: number | null;
  implied_exit_multiple: number | null; implied_terminal_growth: number | null; warnings: string[]; years: { fcff: number }[];
}

export function readDCF(r: DcfLike, m: { wacc: number; terminal_growth: number; terminal_method: string }, cur: Currency, price?: number | null): Reading {
  const points: string[] = [];
  const levels: Level[] = [];
  const share = r.terminal_value_share_of_ev;
  if (isNum(share)) {
    if (share > 0.85) { levels.push('concern'); points.push(`${fmtPct(share, 0)} of the value sits in the terminal value, beyond the forecast years. The answer depends almost entirely on one long-run assumption.`); }
    else if (share > 0.7) { levels.push('watch'); points.push(`${fmtPct(share, 0)} of the value is terminal value. That is common (60-80%) but means the long-run growth and discount rate matter more than the forecast years.`); }
    else { levels.push('good'); points.push(`Only ${fmtPct(share, 0)} of the value is terminal value, so most of it comes from the cash flows you forecast explicitly.`); }
  }
  if (m.terminal_method === 'gordon') {
    const gap = m.wacc - m.terminal_growth;
    if (gap < 0.02) { levels.push('concern'); points.push(`WACC (${fmtPct(m.wacc, 1)}) is only ${fmtPct(gap, 1)} above terminal growth (${fmtPct(m.terminal_growth, 1)}). With a gap this small the value swings wildly with tiny changes.`); }
    else if (gap < 0.04) { levels.push('watch'); points.push(`The gap between WACC and terminal growth is ${fmtPct(gap, 1)}. Test the value at WACC ±1% on the Sensitivity page.`); }
    if (isNum(r.implied_exit_multiple) && r.implied_exit_multiple > 20) { levels.push('watch'); points.push(`The terminal value implies an exit multiple of ${r.implied_exit_multiple.toFixed(1)}x EBITDA, which is high for a mature business.`); }
  } else if (isNum(r.implied_terminal_growth) && r.implied_terminal_growth > 0.05) {
    levels.push('watch'); points.push(`The exit multiple implies terminal growth of ${fmtPct(r.implied_terminal_growth, 1)}, above most long-run economic growth rates.`);
  }
  if (r.years.length && r.years.some((y) => y.fcff < 0)) { levels.push('watch'); points.push('Free cash flow is negative in some years, so the business must be funded until it turns positive.'); }
  if (isNum(price) && isNum(r.value_per_share) && price > 0) {
    const gap = r.value_per_share / price - 1;
    points.push(gap >= 0
      ? `The model value per share (${fmtMoney(r.value_per_share, cur, 2)}) is ${fmtPct(gap, 0)} above the market price (${fmtMoney(price, cur, 2)}), if your assumptions hold.`
      : `The model value per share (${fmtMoney(r.value_per_share, cur, 2)}) is ${fmtPct(-gap, 0)} below the market price (${fmtMoney(price, cur, 2)}). The market may be assuming more growth than you are.`);
  }
  if (r.warnings.length) { levels.push('watch'); points.push(`${r.warnings.length} model warning(s) are listed below the figures. Read them first.`); }
  const level = worst(levels.length ? levels : ['info']);
  const headline = level === 'concern' ? 'This valuation rests on fragile assumptions'
    : level === 'watch' ? 'Reasonable, but a few assumptions drive most of the answer'
      : 'The valuation is not dominated by a single assumption';
  return { level, headline, points, caution: 'A DCF is only as good as its inputs. Test the answer against a range (Monte Carlo below) rather than trusting one number.' };
}

// ------------------------------------------------------------------------------------------------ Forecast
export interface ForecastLike {
  method: string; history: number[]; forecast: number[]; lower: (number | null)[]; upper: (number | null)[];
  backtest: { holdout: number; mape: number | null; mae: number | null }; notes: string[];
}

export function readForecast(r: ForecastLike): Reading {
  const points: string[] = [];
  const levels: Level[] = [];
  const mape = r.backtest.mape;
  if (isNum(mape)) {
    if (mape < 5) { levels.push('strong'); points.push(`On the ${r.backtest.holdout} most recent periods the model was off by ${mape.toFixed(1)}% on average, which is very accurate for a forecast.`); }
    else if (mape < 10) { levels.push('good'); points.push(`On the ${r.backtest.holdout} most recent periods the model was off by ${mape.toFixed(1)}% on average, which is useful for planning.`); }
    else if (mape < 20) { levels.push('watch'); points.push(`The model was off by ${mape.toFixed(1)}% on average on the periods it had not seen. Treat the forecast as a rough guide.`); }
    else { levels.push('concern'); points.push(`The model was off by ${mape.toFixed(1)}% on average on the periods it had not seen. The history is too noisy for this method to be trusted.`); }
  } else {
    levels.push('info'); points.push('The accuracy test could not give a percentage error (for example, the data contains zeros), so there is no measured accuracy.');
  }
  const last = r.history[r.history.length - 1];
  const end = r.forecast[r.forecast.length - 1];
  if (isNum(last) && isNum(end) && last !== 0) {
    const chg = (end - last) / Math.abs(last);
    points.push(`The forecast ends ${fmtPct(Math.abs(chg), 0)} ${chg >= 0 ? 'above' : 'below'} the latest actual value over ${r.forecast.length} periods.`);
  }
  const lo = r.lower[r.lower.length - 1];
  const hi = r.upper[r.upper.length - 1];
  if (isNum(lo) && isNum(hi) && isNum(end) && end !== 0) {
    const width = (hi - lo) / Math.abs(end);
    if (width > 0.4) { levels.push('watch'); points.push(`The range around the last forecast is wide (${fmtPct(width, 0)} of the value), so there is a lot of uncertainty that far out.`); }
  }
  if (r.history.length < 8) { levels.push('watch'); points.push(`Only ${r.history.length} data points. Short histories make any forecast fragile.`); }
  const level = worst(levels);
  const headline = level === 'strong' || level === 'good' ? 'The forecast has held up on data it had not seen'
    : level === 'info' ? 'Forecast produced; accuracy could not be measured' : 'Use this forecast with care';
  return { level, headline, points, caution: 'Forecasts assume the past pattern continues. A new product, price change or market shock will not be in them.' };
}

// ------------------------------------------------------------------------------------------------ Investment appraisal
export interface AppraisalLike {
  npv: number; irr: { status: string; values: number[]; sign_changes: number };
  payback: { period: number | null }; discounted_payback: { period: number | null };
  profitability_index: { value: number | null }; timeline: { t: number }[];
}

export function readAppraisal(r: AppraisalLike, rate: number, cur: Currency): Reading {
  const points: string[] = [];
  const levels: Level[] = [];
  const life = Math.max(0, r.timeline.length - 1);
  if (r.npv > 0) { levels.push('good'); points.push(`The project is worth ${fmtMoney(r.npv, cur)} more than it costs after charging ${fmtPct(rate, 1)} a year for the money.`); }
  else if (r.npv < 0) { levels.push('concern'); points.push(`After charging ${fmtPct(rate, 1)} a year for the money, the project is worth ${fmtMoney(-r.npv, cur)} less than it costs.`); }
  else { levels.push('watch'); points.push('The project earns exactly the required return: no value gained or lost.'); }
  if (r.irr.status === 'unique') {
    const irr = r.irr.values[0];
    const spread = irr - rate;
    points.push(`The project's own rate of return is ${fmtPct(irr, 1)}, ${spread >= 0 ? `${fmtPct(spread, 1)} above` : `${fmtPct(-spread, 1)} below`} the rate you require.`);
    if (spread >= 0 && spread < 0.02) levels.push('watch');
  } else if (r.irr.status === 'multiple') {
    levels.push('watch'); points.push('The cash flows change sign more than once, so there is more than one IRR. Rely on NPV, not IRR, for this project.');
  } else { levels.push('watch'); points.push('No valid IRR exists for these cash flows. Rely on NPV.'); }
  if (isNum(r.discounted_payback.period)) {
    const frac = life ? r.discounted_payback.period / life : 0;
    if (frac > 0.75) { levels.push('watch'); points.push(`The money is only earned back (with interest) after ${r.discounted_payback.period.toFixed(1)} of ${life} years. Little time is left to profit, so a delay would hurt.`); }
    else points.push(`The money is earned back, with interest, in ${r.discounted_payback.period.toFixed(1)} years of ${life}.`);
  } else if (r.npv < 0) {
    points.push('The investment is not earned back within the periods given.');
  }
  if (isNum(r.profitability_index.value)) points.push(`Each unit invested returns ${r.profitability_index.value.toFixed(2)} units of present value.`);
  const level = worst(levels);
  const headline = r.npv > 0 ? (level === 'watch' ? 'Adds value, but with thin margins or risk to check' : 'The project adds value at your required return')
    : r.npv < 0 ? 'The project does not earn your required return' : 'The project only breaks even at your required return';
  return { level, headline, points, caution: 'The result is only as good as the cash flow estimates. Test a lower-sales case before committing.' };
}

// ------------------------------------------------------------------------------------------------ Variance
export interface VarLine { name: string; kind: string; variance: number; variance_pct: number | null; status: string; profit_impact: number; material: boolean }
export interface VarianceLike { lines: VarLine[]; totals: Record<string, VarLine>; largest_contributors: VarLine[] }

export function readVariance(r: VarianceLike, cur: Currency): Reading {
  const points: string[] = [];
  const levels: Level[] = [];
  const profit = r.totals.profit;
  if (profit) {
    const pct = profit.variance_pct;
    const size = isNum(pct) ? Math.abs(pct) : 0;
    if (profit.status === 'favourable') { levels.push(size >= 10 ? 'strong' : 'good'); points.push(`Profit came in ${fmtMoney(Math.abs(profit.variance), cur)}${isNum(pct) ? ` (${size.toFixed(1)}%)` : ''} better than budget.`); }
    else if (profit.status === 'adverse') { levels.push(size >= 10 ? 'concern' : 'watch'); points.push(`Profit came in ${fmtMoney(Math.abs(profit.variance), cur)}${isNum(pct) ? ` (${size.toFixed(1)}%)` : ''} worse than budget.`); }
    else { levels.push('good'); points.push('Profit is on budget.'); }
  }
  const top = r.largest_contributors.filter((l) => l.profit_impact !== 0).slice(0, 2);
  top.forEach((l) => points.push(`${l.name} moved profit by ${l.profit_impact >= 0 ? '+' : '−'}${fmtMoney(Math.abs(l.profit_impact), cur)} (${l.status}). ${l.material ? 'This is above your materiality limit.' : ''}`.trim()));
  const material = r.lines.filter((l) => l.material);
  const adverse = material.filter((l) => l.status === 'adverse');
  if (material.length) points.push(`${material.length} of ${r.lines.length} lines are above your materiality limit${adverse.length ? `, ${adverse.length} of them adverse` : ''}. Start with those.`);
  else points.push('No line is above your materiality limit, so there is nothing that demands explanation.');
  if (adverse.length >= 3) levels.push('watch');
  const level = worst(levels);
  const headline = level === 'concern' ? 'Results are clearly worse than budget' : level === 'watch' ? 'Mixed against budget: some areas need explaining'
    : level === 'strong' ? 'Results are well ahead of budget' : 'Results are close to or better than budget';
  return { level, headline, points, caution: 'A variance says what moved, not why. Ask the budget owner about the largest lines and check whether the budget itself was realistic.' };
}

// ------------------------------------------------------------------------------------------------ Red flags
export interface RedFlagsLike {
  beneish: { status: string; verdict: string | null; value: number | null };
  altman: { name: string; status: string; verdict: string | null }[];
  piotroski: { status: string; score: number; tested: number };
  flags: { severity: 'high' | 'medium' | 'low'; title: string }[];
}

export function readRedFlags(r: RedFlagsLike): Reading {
  const points: string[] = [];
  const levels: Level[] = [];
  if (r.beneish.status === 'ok') {
    if (r.beneish.verdict === 'flag') { levels.push('concern'); points.push('The Beneish screen resembles companies that were later found to have manipulated earnings. It is a prompt to read the accounts closely, not proof.'); }
    else { levels.push('good'); points.push('The Beneish earnings-manipulation screen does not flag this company.'); }
  }
  for (const a of r.altman.filter((x) => x.status === 'ok')) {
    if (a.verdict === 'distress') { levels.push('concern'); points.push(`${a.name}: in the distress zone, meaning companies with this profile have often struggled to stay solvent.`); }
    else if (a.verdict === 'grey') { levels.push('watch'); points.push(`${a.name}: in the grey zone. Neither clearly safe nor clearly distressed.`); }
    else if (a.verdict === 'safe') { levels.push('good'); points.push(`${a.name}: in the safe zone.`); }
  }
  if (r.piotroski.tested > 0) {
    const share = r.piotroski.score / r.piotroski.tested;
    if (share >= 0.8) { levels.push('strong'); points.push(`Piotroski strength score ${r.piotroski.score} of ${r.piotroski.tested}: strong and improving.`); }
    else if (share <= 0.3) { levels.push('concern'); points.push(`Piotroski strength score ${r.piotroski.score} of ${r.piotroski.tested}: weak.`); }
    else points.push(`Piotroski strength score ${r.piotroski.score} of ${r.piotroski.tested}: middling.`);
  }
  const high = r.flags.filter((f) => f.severity === 'high');
  if (high.length) { levels.push('concern'); points.push(`${high.length} high-severity warning sign(s): ${high.slice(0, 2).map((f) => f.title).join('; ')}.`); }
  else if (r.flags.length) { levels.push('watch'); points.push(`${r.flags.length} lower-severity warning sign(s) in the cash-quality checks.`); }
  else points.push('No cash-quality warning signs were found in the data provided.');
  const level = worst(levels.length ? levels : ['info']);
  const headline = level === 'concern' ? 'Several screens say look closer before relying on these accounts'
    : level === 'watch' ? 'A few warning signs to check' : level === 'info' ? 'Not enough data for a firm reading' : 'No major red flags in the screens that could run';
  return { level, headline, points, caution: 'These are statistical screens built on past cases. They say where to look in the annual report; they prove nothing.' };
}
