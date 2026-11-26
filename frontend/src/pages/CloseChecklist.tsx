import { ArrowRight, CalendarCheck, RotateCcw } from 'lucide-react';
import { Link } from 'react-router-dom';
import { useState } from 'react';
import { SaveLoad } from '../components/SaveLoad';
import { Badge, Card, Field, PageHeader } from '../components/ui';
import { freshChecklist, nextMonth, progress, type CloseItem, type CloseState } from '../lib/closeChecklist';
import { load, save } from '../lib/storage';

const KEY = 'fis.close';

/** A month-end close checklist: tick steps off, note who owns each one, jump to the page that helps, and save it as a version. */
export function CloseChecklist() {
  const [state, setStateRaw] = useState<CloseState>(() => load<CloseState>(KEY, freshChecklist()));
  const setState = (s: CloseState) => { setStateRaw(s); save(KEY, s); };
  const p = progress(state);
  const groups = Array.from(new Set(state.items.map((i) => i.group)));
  const update = (id: string, patch: Partial<CloseItem>) => setState({ ...state, items: state.items.map((i) => (i.id === id ? { ...i, ...patch } : i)) });

  return (
    <div className="page">
      <PageHeader title="Month-end close" badge={p.pct === 100 ? <Badge tone="pos">Closed</Badge> : <Badge tone="accent">{p.done} of {p.total} done</Badge>}
        subtitle="Work through the standard steps, note who owns each one, and jump to the page that helps. Save a version at the end of each month as your record."
        actions={<>
          <SaveLoad kind="checklist" label="close checklist" getData={() => state} onLoad={(d: CloseState) => setStateRaw(d)} />
          <button className="btn" onClick={() => { if (window.confirm('Start the next month? Ticks and notes are cleared; steps and owners stay.')) setState(nextMonth(state)); }}><CalendarCheck size={15} />Start next month</button>
          <button className="btn" onClick={() => { if (window.confirm('Reset every step to the standard list?')) setState(freshChecklist(state.month)); }}><RotateCcw size={15} />Reset</button>
        </>} />

      <Card title={`Close for ${new Date(`${state.month}-01`).toLocaleDateString(undefined, { month: 'long', year: 'numeric' })}`} subtitle={`${p.pct}% complete`}>
        <div className="progress" role="progressbar" aria-valuemin={0} aria-valuemax={100} aria-valuenow={p.pct} aria-label="Close progress"><i style={{ width: `${p.pct}%` }} /></div>
        <div style={{ maxWidth: 220, marginTop: 12 }}>
          <Field label="Month"><input className="input" type="month" value={state.month} onChange={(e) => e.target.value && setState({ ...state, month: e.target.value })} /></Field>
        </div>
      </Card>

      {groups.map((g) => (
        <div key={g} className="mt">
          <Card title={g} subtitle={`${state.items.filter((i) => i.group === g && i.done).length} of ${state.items.filter((i) => i.group === g).length} done`}>
            <div className="stack" style={{ gap: 10 }}>
              {state.items.filter((i) => i.group === g).map((i) => (
                <div key={i.id} className="close-item">
                  <label className="row" style={{ gap: 10, alignItems: 'flex-start', flex: 1, minWidth: 0 }}>
                    <input type="checkbox" checked={i.done} onChange={(e) => update(i.id, { done: e.target.checked })} aria-label={`Done: ${i.label}`} />
                    <span style={{ textDecoration: i.done ? 'line-through' : 'none', color: i.done ? 'var(--text-muted)' : undefined }}>{i.label}</span>
                  </label>
                  <input className="input compact" style={{ width: 120 }} placeholder="Owner" aria-label={`Owner of: ${i.label}`} value={i.owner} maxLength={40} onChange={(e) => update(i.id, { owner: e.target.value })} />
                  <input className="input compact" style={{ width: 200 }} placeholder="Note" aria-label={`Note for: ${i.label}`} value={i.note} maxLength={200} onChange={(e) => update(i.id, { note: e.target.value })} />
                  {i.to && <Link className="btn sm" to={i.to}>Open <ArrowRight size={13} /></Link>}
                </div>
              ))}
            </div>
          </Card>
        </div>
      ))}
      <p className="faint mt" style={{ fontSize: 12.5 }}>This is a general checklist. Add your own steps to your process, and keep the saved versions as evidence that the close was reviewed.</p>
    </div>
  );
}
