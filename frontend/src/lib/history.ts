/** Undo/redo as pure functions over {present, past, future}, so the rules can be tested without a page. */
export interface History<T> { cur: T; past: T[]; future: T[]; at: number }

export const MAX_HISTORY = 50;
/** Edits closer together than this (typing in a field) count as one step for undo. */
export const MERGE_MS = 800;

export const start = <T,>(cur: T): History<T> => ({ cur, past: [], future: [], at: 0 });

export function edit<T>(h: History<T>, next: T, now: number, separate = false): History<T> {
  const merge = !separate && h.at !== 0 && now - h.at < MERGE_MS && h.past.length > 0;
  return { cur: next, past: merge ? h.past : [...h.past, h.cur].slice(-MAX_HISTORY), future: [], at: separate ? 0 : now };
}

export function undo<T>(h: History<T>): History<T> {
  if (!h.past.length) return h;
  return { cur: h.past[h.past.length - 1], past: h.past.slice(0, -1), future: [h.cur, ...h.future].slice(0, MAX_HISTORY), at: 0 };
}

export function redo<T>(h: History<T>): History<T> {
  if (!h.future.length) return h;
  return { cur: h.future[0], past: [...h.past, h.cur].slice(-MAX_HISTORY), future: h.future.slice(1), at: 0 };
}
