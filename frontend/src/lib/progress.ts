import { useEffect, useState } from 'react';
import { loadRaw, save } from './storage';

const KEY = 'fis.visited';
const EVENT = 'fis-visited-changed';

/** Pages that count as "ran an analysis" for the first-run checklist. */
export const ANALYSIS_PAGES = ['/ratios', '/dcf', '/red-flags', '/scenarios', '/sensitivity', '/forecasting', '/variance', '/budgeting', '/investment', '/cash-flow'];

const read = (): string[] => {
  const v = loadRaw<unknown>(KEY, []);
  return Array.isArray(v) ? v.filter((x): x is string => typeof x === 'string') : [];
};

/** Remember that this browser has opened a page (used only to tick off the first-run checklist). */
export function markVisited(path: string): void {
  const cur = read();
  if (cur.includes(path)) return;
  save(KEY, [...cur, path]);
  window.dispatchEvent(new Event(EVENT));
}

export function useVisited(): string[] {
  const [v, setV] = useState<string[]>(read);
  useEffect(() => {
    const sync = () => setV(read());
    window.addEventListener(EVENT, sync);
    window.addEventListener('storage', sync);
    return () => { window.removeEventListener(EVENT, sync); window.removeEventListener('storage', sync); };
  }, []);
  return v;
}
