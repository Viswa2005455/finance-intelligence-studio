import { load, save } from './storage';

export interface CalItem { id: string; date: string; area: 'income_tax' | 'gst'; title: string; detail: string; days: number; status: 'overdue' | 'today' | 'soon' | 'later'; source: string | null }
export interface CalResult { today: string; items: CalItem[]; needs_attention: number; gst_included: boolean; note: string }
export interface GstProfile { registration: 'regular' | 'composition' | 'not_registered'; state_code: string; aggregate_turnover_prev_fy: number; qrmp: boolean }
export interface CalSettings { gst: GstProfile | null; filed: string[] }

const KEY = 'fis.calendar';
export const DEFAULT_GST: GstProfile = { registration: 'regular', state_code: '27', aggregate_turnover_prev_fy: 5_000_000, qrmp: false };

export const loadCalendar = (): CalSettings => load<CalSettings>(KEY, { gst: null, filed: [] });
export const saveCalendar = (s: CalSettings) => save(KEY, s);

/** Items still to do: not marked filed, and today, soon or overdue. */
export function attention(items: CalItem[], filed: string[]): CalItem[] {
  return items.filter((i) => !filed.includes(i.id) && (i.status === 'overdue' || i.status === 'today' || i.status === 'soon'));
}

export function whenText(i: Pick<CalItem, 'days'>): string {
  if (i.days === 0) return 'today';
  if (i.days === 1) return 'tomorrow';
  if (i.days > 0) return `in ${i.days} days`;
  return i.days === -1 ? 'yesterday' : `${-i.days} days ago`;
}
