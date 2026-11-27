import { createContext, useCallback, useContext, useMemo, useState, type ReactNode } from 'react';
import { edit, redo, start, undo, type History } from './history';
import { loadRaw, save } from './storage';
import type { DCFModel } from './types';

/**
 * The "working model" shared by DCF, Scenario Planning and Sensitivity Analysis so that all three
 * analyse the same assumptions. The defaults are clearly labelled example inputs, not market data.
 */
export const EXAMPLE_MODEL: DCFModel = {
  base_revenue: 1000,
  revenue_growth: [0.12, 0.11, 0.10, 0.08, 0.06],
  ebit_margin: [0.18, 0.185, 0.19, 0.195, 0.2],
  tax_rate: 0.25,
  da_pct_revenue: 0.04,
  capex_pct_revenue: 0.055,
  nwc_pct_revenue: 0.12,
  wacc: 0.11,
  terminal_growth: 0.04,
  terminal_method: 'gordon',
  exit_multiple: 10,
  debt: 300,
  cash: 120,
  shares_outstanding: 50,
  mid_year: false,
};

interface Ctx { model: DCFModel; setModel: (m: DCFModel) => void; patch: (p: Partial<DCFModel>) => void; reset: () => void; isExample: boolean; undo: () => void; redo: () => void; canUndo: boolean; canRedo: boolean }
interface Snap { model: DCFModel; isExample: boolean }
const DCFContext = createContext<Ctx | null>(null);

export function DCFModelProvider({ children }: { children: ReactNode }) {
  const [store, setStore] = useState<History<Snap>>(() => start(loadRaw<Snap>('fis.dcf', { model: EXAMPLE_MODEL, isExample: true })));
  const apply = useCallback((fn: (h: History<Snap>) => History<Snap>) => setStore((h) => { const n = fn(h); save('fis.dcf', n.cur); return n; }), []);
  const setModel = useCallback((m: DCFModel) => apply((h) => edit(h, { model: m, isExample: false }, Date.now(), true)), [apply]);
  const patch = useCallback((p: Partial<DCFModel>) => apply((h) => edit(h, { model: { ...h.cur.model, ...p }, isExample: false }, Date.now())), [apply]);
  const reset = useCallback(() => apply((h) => edit(h, { model: EXAMPLE_MODEL, isExample: true }, Date.now(), true)), [apply]);
  const doUndo = useCallback(() => apply(undo), [apply]);
  const doRedo = useCallback(() => apply(redo), [apply]);
  const value = useMemo(() => ({ ...store.cur, setModel, patch, reset, undo: doUndo, redo: doRedo, canUndo: store.past.length > 0, canRedo: store.future.length > 0 }),
    [store, setModel, patch, reset, doUndo, doRedo]);
  return <DCFContext.Provider value={value}>{children}</DCFContext.Provider>;
}

export function useDCFModel() {
  const c = useContext(DCFContext);
  if (!c) throw new Error('useDCFModel outside provider');
  return c;
}
