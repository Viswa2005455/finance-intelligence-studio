/** Short plain-English definitions for finance terms, shown on hover or keyboard focus wherever a reading uses them. */
export const GLOSSARY: Record<string, string> = {
  WACC: 'Weighted average cost of capital: the blended return that shareholders and lenders together require. It is the discount rate in a DCF.',
  DCF: 'Discounted cash flow: valuing a business as the present value of the cash it is expected to produce.',
  NPV: 'Net present value: all future cash flows discounted to today, minus what you put in. Positive means the project earns more than the required return.',
  IRR: 'Internal rate of return: the yearly return a project earns on its own, the rate at which its NPV is zero.',
  MIRR: 'Modified IRR: a single comparable return that assumes money is reinvested at a realistic rate.',
  FCFF: 'Free cash flow to the firm: cash the operations generate for all capital providers after tax and reinvestment.',
  NOPAT: 'Net operating profit after tax: operating profit (EBIT) less tax, before financing costs.',
  EBIT: 'Earnings before interest and tax: operating profit.',
  EBITDA: 'Earnings before interest, tax, depreciation and amortisation: a cash-oriented view of operating profit.',
  ROE: 'Return on equity: net profit as a percentage of shareholders\' money.',
  ROA: 'Return on assets: net profit as a percentage of everything the business owns.',
  ROIC: 'Return on invested capital: after-tax operating profit as a percentage of the money invested in operations.',
  DSO: 'Days sales outstanding: the average number of days customers take to pay.',
  DIO: 'Days inventory outstanding: how many days of stock the business holds.',
  DPO: 'Days payables outstanding: how many days the business takes to pay suppliers.',
  CAGR: 'Compound annual growth rate: the steady yearly growth that would take a value from its start to its end.',
  CapEx: 'Capital expenditure: money spent on long-lasting assets such as equipment and buildings.',
  NWC: 'Net working capital: current assets less current liabilities.',
  MAPE: 'Mean absolute percentage error: how far a forecast is off, on average, as a percentage.',
  'terminal value': 'The value of all cash flows after the years you forecast, usually the largest part of a DCF.',
  'cash conversion cycle': 'The days between paying for inputs and collecting from customers: stock days plus receivable days minus payable days.',
  'interest cover': 'How many times operating profit covers the interest bill.',
  'equity multiplier': 'Assets divided by owners\' equity: how many units of assets each unit of owners\' money controls. It measures gearing.',
  gearing: 'How much of the business is funded by borrowing rather than owners\' money.',
  'current ratio': 'Current assets divided by current liabilities: can the business pay its bills due within a year?',
  'quick ratio': 'Current ratio without inventory: can the business pay its bills without selling stock?',
  DuPont: 'A way of splitting return on equity into profit margin, asset turnover and gearing.',
  'profit margin': 'The share of each sale kept as profit.',
  'asset turnover': 'Revenue produced for each unit of assets.',
  Beneish: 'A screen built from eight ratios that moved unusually in companies later found to have manipulated earnings.',
  Altman: 'A screen that predicts financial distress from liquidity, profitability, leverage and turnover.',
  Piotroski: 'A nine-point score of financial strength and improvement.',
  covenant: 'A condition in a loan agreement, such as a minimum interest cover, that the borrower must keep to.',
  materiality: 'How big a difference has to be before it matters enough to explain.',
};

export type GlossPart = string | { term: string; def: string };

const TERMS = Object.keys(GLOSSARY).sort((a, b) => b.length - a.length);
const RX = new RegExp(`(?<![\\w-])(${TERMS.map((t) => t.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')).join('|')})(?![\\w-])`, 'gi');

/** Split text into plain pieces and glossary terms. Only the first use of each term is marked, so the text stays calm. */
export function glossify(text: string): GlossPart[] {
  const seen = new Set<string>();
  const parts: GlossPart[] = [];
  let last = 0;
  for (const m of text.matchAll(RX)) {
    const found = m[1];
    const key = TERMS.find((t) => t.toLowerCase() === found.toLowerCase());
    // Acronyms and proper names (WACC, CapEx, DuPont) must match their capitals, so "irr" inside a word never counts; plain words and phrases may be any case.
    if (!key || (key !== key.toLowerCase() && found !== key)) continue;
    if (seen.has(key)) continue;
    seen.add(key);
    if (m.index! > last) parts.push(text.slice(last, m.index));
    parts.push({ term: found, def: GLOSSARY[key] });
    last = m.index! + found.length;
  }
  if (last < text.length) parts.push(text.slice(last));
  return parts.length ? parts : [text];
}
