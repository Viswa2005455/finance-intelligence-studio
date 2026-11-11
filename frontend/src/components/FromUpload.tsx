import { FileUp } from 'lucide-react';
import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { toCompany, useCompanySources } from '../lib/company';
import { useSettings } from '../lib/settings';
import { fmtNum, isNum } from '../lib/format';
import { Callout } from './ui';

/** The latest reporting period of one company, as standard-item figures. */
export interface Figures {
  name: string; period: string; priorPeriod: string | null;
  value: (key: string) => number | null;
  prior: (key: string) => number | null;
}

/**
 * Fills a page's inputs from an uploaded statement file (or a saved company): the latest period only, with the
 * previous period available for opening balances. Anything the file does not hold is reported and left for the
 * user to enter; nothing is estimated or carried over from example data.
 */
export function FromUpload({ keys, labels, onApply, title = 'Use figures from a file' }: {
  keys: string[]; labels?: Record<string, string>; onApply: (f: Figures) => void; title?: string;
}) {
  const { sources } = useCompanySources();
  const { settings } = useSettings();
  const real = sources?.filter((s) => !s.isExample) ?? [];
  const [id, setId] = useState('');
  const [busy, setBusy] = useState(false);
  const [msg, setMsg] = useState<{ tone: 'good' | 'warn'; text: string } | null>(null);
  useEffect(() => { if (!id && real.length) setId(real[0].id); }, [real.length]); // eslint-disable-line react-hooks/exhaustive-deps

  const apply = async () => {
    const src = real.find((s) => s.id === id);
    if (!src) return;
    setBusy(true); setMsg(null);
    try {
      const data = await src.load();
      const c = toCompany(data);
      const last = c.periods.reduce((acc, _p, i) => (keys.some((k) => isNum(c.items[k]?.[i])) ? i : acc), -1);
      if (last < 0) { setMsg({ tone: 'warn', text: 'That file holds none of the figures this page needs.' }); return; }
      const val = (k: string, i: number) => { const v = c.items[k]?.[i]; return isNum(v) ? v : null; };
      const f: Figures = { name: src.name, period: c.periods[last], priorPeriod: last > 0 ? c.periods[last - 1] : null,
        value: (k) => val(k, last), prior: (k) => (last > 0 ? val(k, last - 1) : null) };
      onApply(f);
      const missing = keys.filter((k) => f.value(k) === null).map((k) => labels?.[k] ?? k);
      setMsg({ tone: missing.length ? 'warn' : 'good',
        text: `Filled from ${src.name}, ${c.periods[last]}.${missing.length ? ` Not found in the file, so left blank for you to enter: ${missing.join(', ')}.` : ''}`
          + (data.currency || data.units ? ` The file states ${[data.currency, data.units ? `in ${data.units}` : ''].filter(Boolean).join(' ')}; this page labels amounts as ${settings.currency} per your Settings, so change Settings if they differ.` : ' Check the units and the reporting period.') });
    } catch (e) { setMsg({ tone: 'warn', text: (e as Error).message }); } finally { setBusy(false); }
  };

  return (
    <div className="card" style={{ padding: 14 }}>
      <div style={{ fontWeight: 600, marginBottom: 6 }}>{title}</div>
      {!sources ? <p className="faint" style={{ margin: 0 }}>Looking for your files…</p>
        : !real.length ? <p className="muted" style={{ margin: 0 }}>No statement file yet. <Link to="/upload">Upload a statement</Link> (Excel, CSV or PDF) and it will appear here.</p>
          : (
            <div className="stack" style={{ gap: 8 }}>
              <select className="input" aria-label="File or company" value={id} onChange={(e) => setId(e.target.value)}>
                {real.map((s) => <option key={s.id} value={s.id}>{s.name}</option>)}
              </select>
              <button className="btn sm primary" onClick={apply} disabled={busy || !id}><FileUp size={14} />{busy ? 'Reading…' : 'Use the latest period'}</button>
              {msg && <Callout tone={msg.tone === 'good' ? 'info' : 'warn'}>{msg.text}</Callout>}
            </div>
          )}
    </div>
  );
}

export const fmtFigure = (v: number | null) => (v === null ? '—' : fmtNum(v, 0));
