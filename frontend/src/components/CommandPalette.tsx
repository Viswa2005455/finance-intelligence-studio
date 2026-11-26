import { CornerDownLeft, Search } from 'lucide-react';
import { useEffect, useMemo, useRef, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { NAV } from '../nav';

/** Extra words people search by, so "npv" finds Investment Appraisal and "wacc" finds DCF Valuation. */
const KEYWORDS: Record<string, string> = {
  '/': 'home dashboard summary', '/projects': 'folders saved models history', '/upload': 'import file csv excel pdf word text json messy data',
  '/budgeting': 'budget phasing zero based flexible', '/forecasting': 'forecast trend smoothing cagr projection', '/variance': 'budget actual favourable adverse',
  '/costing': 'cvp break even marginal absorption standard cost', '/statements': 'income statement balance sheet cash flow screener import',
  '/ratios': 'liquidity profitability leverage margin roe roce interpretation', '/cash-flow': 'working capital runway dso dpo dio',
  '/accounting': 'lease bond depreciation eps deferred tax materiality journal', '/red-flags': 'beneish altman piotroski forensic fraud manipulation',
  '/peers': 'compare benchmark companies', '/scenarios': 'base optimistic pessimistic', '/sensitivity': 'tornado heatmap break even what if',
  '/dcf': 'valuation wacc capm terminal value fcff monte carlo reverse', '/investment': 'npv irr mirr payback project appraisal capital budgeting',
  '/investments': 'bond duration option black scholes portfolio sharpe', '/markets': 'share price quote risk var volatility beta',
  '/income-tax': 'itr tax regime 87a form 16 3cd audit', '/gst': 'gstr 3b gstr 1 2b reconciliation return', '/model-check': 'excel errors formulas audit',
  '/assistant': 'ai chat claude ask', '/ai-health': 'model status provider', '/reports': 'export pack word pdf excel', '/learn': 'methodology formulas help learn',
  '/settings': 'password theme dark light export delete account currency',
};

const matches = (text: string, q: string) => q.toLowerCase().split(/\s+/).filter(Boolean).every((t) => text.includes(t));

/** Jump to any page from the keyboard: Ctrl/Cmd + K, type a few letters, Enter. */
export function CommandPalette({ open, onClose }: { open: boolean; onClose: () => void }) {
  const ref = useRef<HTMLDialogElement>(null);
  const input = useRef<HTMLInputElement>(null);
  const navigate = useNavigate();
  const [q, setQ] = useState('');
  const [active, setActive] = useState(0);

  const results = useMemo(() => NAV.filter((n) => matches(`${n.label} ${n.group} ${KEYWORDS[n.to] ?? ''}`.toLowerCase(), q))
    .sort((a, b) => {
      // Titles that start with the query come first.
      const s = (n: typeof a) => (q && n.label.toLowerCase().startsWith(q.toLowerCase()) ? 0 : q && n.label.toLowerCase().includes(q.toLowerCase()) ? 1 : 2);
      return s(a) - s(b);
    }), [q]);

  useEffect(() => {
    const d = ref.current;
    if (!d) return;
    if (open && !d.open) { setQ(''); setActive(0); d.showModal(); requestAnimationFrame(() => input.current?.focus()); }
    if (!open && d.open) d.close();
  }, [open]);
  useEffect(() => setActive(0), [q]);

  const go = (to: string) => { onClose(); navigate(to); };
  const onKey = (e: React.KeyboardEvent) => {
    if (e.key === 'ArrowDown') { e.preventDefault(); setActive((a) => Math.min(a + 1, results.length - 1)); }
    else if (e.key === 'ArrowUp') { e.preventDefault(); setActive((a) => Math.max(a - 1, 0)); }
    else if (e.key === 'Enter' && results[active]) { e.preventDefault(); go(results[active].to); }
  };
  useEffect(() => { document.getElementById(`palette-opt-${active}`)?.scrollIntoView({ block: 'nearest' }); }, [active]);

  return (
    <dialog ref={ref} className="palette" aria-label="Go to a page" onClose={onClose} onCancel={(e) => { e.preventDefault(); onClose(); }}
      onClick={(e) => { if (e.target === ref.current) onClose(); }}>
      {open && (
        <div onKeyDown={onKey}>
          <div className="palette-input">
            <Search size={17} aria-hidden="true" />
            <input ref={input} value={q} onChange={(e) => setQ(e.target.value)} placeholder="Go to a page… try npv, ratios, gst, upload"
              role="combobox" aria-expanded="true" aria-controls="palette-list" aria-activedescendant={results[active] ? `palette-opt-${active}` : undefined} aria-label="Search pages" />
            <kbd>Esc</kbd>
          </div>
          <ul id="palette-list" role="listbox" className="palette-list">
            {results.map((n, i) => (
              <li key={n.to} id={`palette-opt-${i}`} role="option" aria-selected={i === active} className={i === active ? 'on' : ''}
                onMouseMove={() => setActive(i)} onClick={() => go(n.to)}>
                <n.icon size={16} aria-hidden="true" />
                <span className="grow">{n.label}</span>
                <span className="faint">{n.group}</span>
                {!n.ready && <span className="faint">(in development)</span>}
                {i === active && <CornerDownLeft size={14} aria-hidden="true" />}
              </li>
            ))}
            {results.length === 0 && <li className="palette-empty">No page matches “{q}”. Try a topic such as tax, budget or valuation.</li>}
          </ul>
        </div>
      )}
    </dialog>
  );
}
