import { CornerDownLeft, FileText, Keyboard, LogOut, Moon, Search, Settings as SettingsIcon, Bookmark, type LucideIcon } from 'lucide-react';
import { useEffect, useMemo, useRef, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { NAV } from '../nav';
import { api } from '../lib/api';
import { useAuth } from '../lib/auth';
import { useSettings } from '../lib/settings';

/** Extra words people search by, so "npv" finds Investment Appraisal and "wacc" finds DCF Valuation. */
const KEYWORDS: Record<string, string> = {
  '/': 'home dashboard summary', '/projects': 'folders saved models history', '/upload': 'import file csv excel pdf word text json messy data',
  '/budgeting': 'budget phasing zero based flexible', '/forecasting': 'forecast trend smoothing cagr projection', '/variance': 'budget actual favourable adverse',
  '/costing': 'cvp break even marginal absorption standard cost', '/statements': 'income statement balance sheet cash flow screener import',
  '/ratios': 'liquidity profitability leverage margin roe roce dupont interpretation', '/cash-flow': 'working capital runway dso dpo dio',
  '/accounting': 'lease bond depreciation eps deferred tax materiality journal', '/red-flags': 'beneish altman piotroski forensic fraud manipulation',
  '/peers': 'compare benchmark companies', '/scenarios': 'base optimistic pessimistic', '/sensitivity': 'tornado heatmap break even what if',
  '/dcf': 'valuation wacc capm terminal value fcff monte carlo reverse', '/investment': 'npv irr mirr payback project appraisal capital budgeting',
  '/investments': 'bond duration option black scholes portfolio sharpe', '/markets': 'share price quote risk var volatility beta',
  '/income-tax': 'itr tax regime 87a form 16 3cd audit', '/gst': 'gstr 3b gstr 1 2b reconciliation return', '/model-check': 'excel errors formulas audit',
  '/assistant': 'ai chat claude ask', '/ai-health': 'model status provider', '/reports': 'export pack word pdf excel', '/learn': 'methodology formulas help learn',
  '/close': 'month end close checklist reconcile sign off accounting period',
  '/settings': 'password theme dark light export delete account currency background motion',
};

/** Where each kind of saved model opens. */
const SAVED_ROUTE: Record<string, string> = {
  dcf: '/dcf', scenarios: '/scenarios', budget: '/budgeting', statements: '/statements', cash_budget: '/cash-flow', variance: '/variance', ratios: '/ratios',
  forecast: '/forecasting', investment: '/investment', costing: '/costing', accounting: '/accounting', investments: '/investments', income_tax: '/income-tax', gst: '/gst', checklist: '/close',
};

interface Entry { id: string; label: string; hint: string; icon: LucideIcon; search: string; run: () => void; section: 'Pages' | 'Files' | 'Saved models' | 'Actions' }

const matches = (text: string, q: string) => q.toLowerCase().split(/\s+/).filter(Boolean).every((t) => text.includes(t));

/** Jump to any page, recent file or saved model from the keyboard: Ctrl/Cmd + K (or "/"), type a few letters, Enter. */
export function CommandPalette({ open, onClose, onHelp }: { open: boolean; onClose: () => void; onHelp: () => void }) {
  const ref = useRef<HTMLDialogElement>(null);
  const input = useRef<HTMLInputElement>(null);
  const navigate = useNavigate();
  const { logout } = useAuth();
  const { update, resolvedTheme } = useSettings();
  const [q, setQ] = useState('');
  const [active, setActive] = useState(0);
  const [files, setFiles] = useState<{ id: string; name: string; summary: string }[]>([]);
  const [saved, setSaved] = useState<{ id: string; name: string; kind: string }[]>([]);

  // Recent files and saved models are fetched each time the palette opens, so they are never stale.
  useEffect(() => {
    if (!open) return;
    let alive = true;
    api.get<{ uploads: { id: string; name: string; summary: string }[] }>('/api/uploads').then((r) => alive && setFiles(r.uploads.slice(0, 8))).catch(() => undefined);
    api.get<{ items: { id: string; name: string; kind: string }[] }>('/api/saved').then((r) => alive && setSaved(r.items.slice(0, 8))).catch(() => undefined);
    return () => { alive = false; };
  }, [open]);

  const entries = useMemo<Entry[]>(() => {
    const go = (to: string) => () => { onClose(); navigate(to); };
    const pages: Entry[] = NAV.map((n) => ({ id: `p:${n.to}`, label: n.label, hint: n.group + (n.ready ? '' : ' (in development)'), icon: n.icon, search: `${n.label} ${n.group} ${KEYWORDS[n.to] ?? ''}`.toLowerCase(), run: go(n.to), section: 'Pages' }));
    const fileEntries: Entry[] = files.map((f) => ({ id: `f:${f.id}`, label: f.name, hint: f.summary, icon: FileText, search: `${f.name} file upload ${f.summary}`.toLowerCase(), run: go(`/upload?file=${f.id}`), section: 'Files' }));
    const savedEntries: Entry[] = saved.map((s) => ({ id: `s:${s.id}`, label: s.name, hint: `Saved ${s.kind.replace('_', ' ')}`, icon: Bookmark, search: `${s.name} saved model ${s.kind}`.toLowerCase(), run: go(`${SAVED_ROUTE[s.kind] ?? '/projects'}?saved=${s.id}`), section: 'Saved models' }));
    const actions: Entry[] = [
      { id: 'a:theme', label: resolvedTheme === 'dark' ? 'Switch to light mode' : 'Switch to dark mode', hint: 'Action', icon: Moon, search: 'theme dark light mode switch', run: () => { onClose(); update({ theme: resolvedTheme === 'dark' ? 'light' : 'dark' }); }, section: 'Actions' },
      { id: 'a:keys', label: 'Show keyboard shortcuts', hint: 'Action', icon: Keyboard, search: 'keyboard shortcuts help keys', run: () => { onClose(); onHelp(); }, section: 'Actions' },
      { id: 'a:settings', label: 'Open settings', hint: 'Action', icon: SettingsIcon, search: 'settings preferences background motion', run: go('/settings'), section: 'Actions' },
      { id: 'a:out', label: 'Sign out', hint: 'Action', icon: LogOut, search: 'sign out logout', run: () => { onClose(); void logout(); }, section: 'Actions' },
    ];
    return [...pages, ...fileEntries, ...savedEntries, ...actions];
  }, [files, saved, navigate, onClose, onHelp, logout, update, resolvedTheme]);

  const results = useMemo(() => {
    const hits = entries.filter((e) => matches(e.search, q));
    if (!q) return [...hits.filter((e) => e.section === 'Pages'), ...hits.filter((e) => e.section === 'Files').slice(0, 3), ...hits.filter((e) => e.section === 'Saved models').slice(0, 3), ...hits.filter((e) => e.section === 'Actions')];
    const rank = (e: Entry) => (e.label.toLowerCase().startsWith(q.toLowerCase()) ? 0 : e.label.toLowerCase().includes(q.toLowerCase()) ? 1 : 2);
    return hits.sort((a, b) => rank(a) - rank(b));
  }, [entries, q]);

  useEffect(() => {
    const d = ref.current;
    if (!d) return;
    if (open && !d.open) { setQ(''); setActive(0); d.showModal(); requestAnimationFrame(() => input.current?.focus()); }
    if (!open && d.open) d.close();
  }, [open]);
  useEffect(() => setActive(0), [q]);
  useEffect(() => { document.getElementById(`palette-opt-${active}`)?.scrollIntoView({ block: 'nearest' }); }, [active]);

  const onKey = (e: React.KeyboardEvent) => {
    if (e.key === 'ArrowDown') { e.preventDefault(); setActive((a) => Math.min(a + 1, results.length - 1)); }
    else if (e.key === 'ArrowUp') { e.preventDefault(); setActive((a) => Math.max(a - 1, 0)); }
    else if (e.key === 'Enter' && results[active]) { e.preventDefault(); results[active].run(); }
  };

  return (
    <dialog ref={ref} className="palette" aria-label="Go to a page" onClose={onClose} onCancel={(e) => { e.preventDefault(); onClose(); }}
      onClick={(e) => { if (e.target === ref.current) onClose(); }}>
      {open && (
        <div onKeyDown={onKey}>
          <div className="palette-input">
            <Search size={17} aria-hidden="true" />
            <input ref={input} value={q} onChange={(e) => setQ(e.target.value)} placeholder="Search pages, files, saved models… try npv, ratios, gst"
              role="combobox" aria-expanded="true" aria-controls="palette-list" aria-activedescendant={results[active] ? `palette-opt-${active}` : undefined} aria-label="Search pages" />
            <kbd>Esc</kbd>
          </div>
          <ul id="palette-list" role="listbox" className="palette-list">
            {results.map((n, i) => (
              <li key={n.id} id={`palette-opt-${i}`} role="option" aria-selected={i === active} className={i === active ? 'on' : ''}
                onMouseMove={() => setActive(i)} onClick={() => n.run()}>
                <n.icon size={16} aria-hidden="true" />
                <span className="grow truncate">{n.label}</span>
                <span className="faint truncate" style={{ maxWidth: '40%' }}>{n.section === 'Pages' ? n.hint : `${n.section}${n.hint && n.section !== 'Actions' ? ` · ${n.hint}` : ''}`}</span>
                {i === active && <CornerDownLeft size={14} aria-hidden="true" />}
              </li>
            ))}
            {results.length === 0 && <li className="palette-empty">Nothing matches “{q}”. Try a topic such as tax, budget or valuation.</li>}
          </ul>
        </div>
      )}
    </dialog>
  );
}
