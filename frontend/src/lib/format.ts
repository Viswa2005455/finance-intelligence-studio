/** Presentation-only formatting. Calculations never use these rounded values. */

export const CURRENCIES = ['INR', 'USD', 'EUR', 'GBP', 'JPY'] as const;
export type Currency = (typeof CURRENCIES)[number];
export const UNIT_SCALES = ['units', 'thousands', 'lakhs', 'crores', 'millions', 'billions'] as const;
export type UnitScale = (typeof UNIT_SCALES)[number];

const LOCALE: Record<Currency, string> = { INR: 'en-IN', USD: 'en-US', EUR: 'en-IE', GBP: 'en-GB', JPY: 'ja-JP' };

/** Digit grouping: 'indian' = 1,23,45,678 · 'international' = 12,345,678 · 'auto' = by currency. */
export type NumberStyle = 'auto' | 'indian' | 'international';
let numberStyle: NumberStyle = 'auto';
/** Set once from the Settings provider; formatting stays a pure presentation concern. */
export function setNumberStyle(s: NumberStyle) {
  numberStyle = s;
}
function locale(currency: Currency): string {
  if (numberStyle === 'indian') return 'en-IN';
  if (numberStyle === 'international') return currency === 'INR' ? 'en-US' : LOCALE[currency];
  return LOCALE[currency];
}

/** Suffix shown after an amount stored in the given unit, e.g. 255324 crores -> "₹2,55,324 Cr". */
export const UNIT_SUFFIX: Record<UnitScale, string> = {
  units: '', thousands: 'K', lakhs: 'L', crores: 'Cr', millions: 'M', billions: 'B',
};
export const UNIT_LABEL: Record<UnitScale, string> = {
  units: '', thousands: 'in thousands', lakhs: 'in lakhs', crores: 'in crores', millions: 'in millions', billions: 'in billions',
};

export function isNum(v: unknown): v is number {
  return typeof v === 'number' && Number.isFinite(v);
}

export function fmtMoney(v: number | null | undefined, currency: Currency = 'INR', digits = 0): string {
  if (!isNum(v)) return '—';
  if (Math.abs(v) < 0.5 * 10 ** -digits) v = 0;
  const s = new Intl.NumberFormat(locale(currency), {
    style: 'currency', currency, minimumFractionDigits: digits, maximumFractionDigits: currency === 'JPY' ? 0 : digits,
  }).format(Math.abs(v));
  return v < 0 ? `−${s}` : s;
}

export function fmtNum(v: number | null | undefined, digits = 2, currency: Currency = 'INR'): string {
  if (!isNum(v)) return '—';
  if (Math.abs(v) < 0.5 * 10 ** -digits) v = 0; // never show "−0.00" for rounding residue
  const s = new Intl.NumberFormat(locale(currency), { minimumFractionDigits: digits, maximumFractionDigits: digits }).format(Math.abs(v));
  return v < 0 ? `−${s}` : s;
}

/** An amount already expressed in `units` (e.g. a Screener export in ₹ crores): "₹2,55,324 Cr". */
export function fmtScaled(v: number | null | undefined, units: UnitScale, currency: Currency = 'INR', digits = 0): string {
  if (!isNum(v)) return '—';
  const suffix = UNIT_SUFFIX[units];
  return suffix ? `${fmtMoney(v, currency, digits)} ${suffix}` : fmtMoney(v, currency, digits);
}

const UNIT_FACTOR: Record<UnitScale, number> = { units: 1, thousands: 1e3, lakhs: 1e5, crores: 1e7, millions: 1e6, billions: 1e9 };

/** Compact amount that knows the data's unit: 255324 (₹ crores) -> "2.6L Cr", 5,000 (USD millions) -> "5.0B". */
export function fmtCompactUnits(v: number | null | undefined, units: UnitScale, currency: Currency = 'INR'): string {
  if (!isNum(v)) return '—';
  const base = v * UNIT_FACTOR[units];
  const a = Math.abs(base);
  const sign = base < 0 ? '−' : '';
  if (currency === 'INR') {
    if (a >= 1e12) return `${sign}${(a / 1e12).toFixed(1)}L Cr`;
    if (a >= 1e7) return `${sign}${(a / 1e7).toFixed(a >= 1e9 ? 0 : 1)} Cr`;
    if (a >= 1e5) return `${sign}${(a / 1e5).toFixed(1)}L`;
  }
  if (a >= 1e12) return `${sign}${(a / 1e12).toFixed(1)}T`;
  if (a >= 1e9) return `${sign}${(a / 1e9).toFixed(1)}B`;
  if (a >= 1e6) return `${sign}${(a / 1e6).toFixed(1)}M`;
  if (a >= 1e3) return `${sign}${(a / 1e3).toFixed(1)}K`;
  return `${sign}${a.toFixed(a < 10 ? 1 : 0)}`;
}

/** Compact for chart axes: 1.2K, 3.4M (or L / Cr for INR). */
export function fmtCompact(v: number | null | undefined, currency: Currency = 'INR'): string {
  if (!isNum(v)) return '—';
  const a = Math.abs(v);
  const sign = v < 0 ? '−' : '';
  if (currency === 'INR') {
    if (a >= 1e7) return `${sign}${(a / 1e7).toFixed(a >= 1e9 ? 0 : 1)}Cr`;
    if (a >= 1e5) return `${sign}${(a / 1e5).toFixed(1)}L`;
  }
  if (a >= 1e9) return `${sign}${(a / 1e9).toFixed(1)}B`;
  if (a >= 1e6) return `${sign}${(a / 1e6).toFixed(1)}M`;
  if (a >= 1e3) return `${sign}${(a / 1e3).toFixed(1)}K`;
  return `${sign}${a.toFixed(a < 10 ? 1 : 0)}`;
}

/** Decimal (0.1234) -> "12.34%". */
export function fmtPct(v: number | null | undefined, digits = 2): string {
  if (!isNum(v)) return '—';
  if (Math.abs(v * 100) < 0.5 * 10 ** -digits) v = 0; // never show "−0.0%" for rounding residue
  const s = `${Math.abs(v * 100).toFixed(digits)}%`;
  return v < 0 ? `−${s}` : s;
}

/** Already-a-percentage (12.34) -> "12.34%". */
export function fmtPctPoints(v: number | null | undefined, digits = 1): string {
  if (!isNum(v)) return '—';
  if (Math.abs(v) < 0.5 * 10 ** -digits) v = 0;
  return `${v < 0 ? '−' : ''}${Math.abs(v).toFixed(digits)}%`;
}

export function fmtRatio(v: number | null | undefined, unit: string, currency: Currency = 'INR'): string {
  if (!isNum(v)) return '—';
  if (unit === '%') return fmtPctPoints(v, 1);
  if (unit === 'days') return `${fmtNum(v, 1)} days`;
  if (unit === 'currency') return fmtMoney(v, currency, 2);
  return `${fmtNum(v, 2)}×`;
}

export function fmtBytes(n: number): string {
  if (n < 1024) return `${n} B`;
  if (n < 1024 ** 2) return `${(n / 1024).toFixed(1)} KB`;
  return `${(n / 1024 ** 2).toFixed(1)} MB`;
}

/** Short forms people type for big numbers: 45k, 1.2cr, 3.5L, 2m, 1.5bn. */
const SUFFIX: Record<string, number> = {
  k: 1e3, thousand: 1e3, l: 1e5, lac: 1e5, lacs: 1e5, lakh: 1e5, lakhs: 1e5, cr: 1e7, crore: 1e7, crores: 1e7,
  m: 1e6, mn: 1e6, mm: 1e6, million: 1e6, millions: 1e6, b: 1e9, bn: 1e9, billion: 1e9, billions: 1e9,
};

/** Parse a user-typed number: allows commas, spaces, a leading minus or (parentheses), a trailing % (for percentage
 * fields), and the short forms k, L/lakh, cr/crore, m/mn and b/bn (45k, 1.2cr, 3.5L). Empty -> null. */
export function parseInputNumber(s: string): number | null {
  const t = s.replace(/[,\s₹$€£¥]/g, '').replace(/%$/, '').trim();
  if (!t) return null;
  const neg = /^\(.*\)$/.test(t);
  const body = t.replace(/[()]/g, '');
  let n = Number(body);
  if (!Number.isFinite(n)) {
    const m = /^(-?\d*\.?\d+)([a-z]+)$/i.exec(body);
    const mult = m ? SUFFIX[m[2].toLowerCase()] : undefined;
    if (!m || mult === undefined) return null;
    n = Number(m[1]) * mult;
  }
  if (!Number.isFinite(n)) return null;
  return neg ? -n : n;
}

/** Escape a value for CSV and neutralise spreadsheet formula injection (=, +, -, @, tab, CR at the start). */
export function csvCell(v: unknown): string {
  let s = v === null || v === undefined ? '' : String(v);
  if (/^[=+\-@\t\r]/.test(s) && !/^-?\d+(\.\d+)?$/.test(s)) s = `'${s}`;
  return `"${s.replace(/"/g, '""')}"`;
}

export function toCSV(rows: unknown[][]): string {
  return rows.map((r) => r.map(csvCell).join(',')).join('\r\n');
}

export function downloadFile(name: string, content: string, type = 'text/csv;charset=utf-8') {
  const url = URL.createObjectURL(new Blob(['﻿', content], { type }));
  const a = Object.assign(document.createElement('a'), { href: url, download: name });
  document.body.appendChild(a);
  a.click();
  a.remove();
  setTimeout(() => URL.revokeObjectURL(url), 1000);
}
