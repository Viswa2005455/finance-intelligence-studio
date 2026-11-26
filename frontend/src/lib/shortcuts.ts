/** Keyboard shortcuts. "g" then a letter jumps to a page (g d = DCF), "?" shows this list, "/" or Ctrl+K opens search. */
export const GO_KEYS: Record<string, { to: string; label: string }> = {
  o: { to: '/', label: 'Overview' }, u: { to: '/upload', label: 'Upload & Analyse' }, p: { to: '/projects', label: 'My Projects' },
  s: { to: '/statements', label: 'Financial Statements' }, r: { to: '/ratios', label: 'Ratio Analysis' }, d: { to: '/dcf', label: 'DCF Valuation' },
  i: { to: '/investment', label: 'Investment Appraisal' }, b: { to: '/budgeting', label: 'Budgeting' }, f: { to: '/forecasting', label: 'Forecasting' },
  v: { to: '/variance', label: 'Variance Analysis' }, c: { to: '/cash-flow', label: 'Cash Flow & Working Capital' }, t: { to: '/income-tax', label: 'Income Tax' },
  g: { to: '/gst', label: 'GST Returns' }, m: { to: '/close', label: 'Month-end Close' }, a: { to: '/assistant', label: 'AI Finance Assistant' }, e: { to: '/reports', label: 'Reports & Exports' },
};

/** True when the keyboard focus is somewhere people type, so a shortcut must not steal the key. */
export function isTyping(el: EventTarget | null): boolean {
  if (!(el instanceof HTMLElement)) return false;
  const tag = el.tagName;
  return tag === 'INPUT' || tag === 'TEXTAREA' || tag === 'SELECT' || el.isContentEditable;
}

/** What a key press means: a page to open, the help sheet, or the search box. `pendingG` is true right after "g". */
export type KeyAction = { type: 'go'; to: string } | { type: 'help' } | { type: 'search' } | { type: 'wait-g' } | null;

export function interpretKey(key: string, pendingG: boolean, mods: { ctrl: boolean; meta: boolean; alt: boolean }): KeyAction {
  if (mods.ctrl || mods.meta || mods.alt) return null;
  if (pendingG) {
    const hit = GO_KEYS[key.toLowerCase()];
    return hit ? { type: 'go', to: hit.to } : null;
  }
  if (key === '?') return { type: 'help' };
  if (key === '/') return { type: 'search' };
  if (key === 'g') return { type: 'wait-g' };
  return null;
}
