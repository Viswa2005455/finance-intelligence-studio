import { CalendarClock, CheckCircle2, Undo2 } from 'lucide-react';
import { useEffect, useState } from 'react';
import { Badge, Callout, Card, EmptyState, ErrorBox, Field, PageHeader, Skeleton } from '../components/ui';
import { api } from '../lib/api';
import { DEFAULT_GST, loadCalendar, saveCalendar, whenText, type CalItem, type CalResult, type CalSettings } from '../lib/complianceCalendar';
import { fmtNum } from '../lib/format';

const TONE = { overdue: 'neg', today: 'warn', soon: 'warn', later: undefined } as const;
const LABEL = { overdue: 'Overdue', today: 'Today', soon: 'This week', later: 'Later' } as const;

/** Income-tax and GST dates in one list, soonest first, with a "filed" tick that is kept in this browser. */
export function Calendar() {
  const [settings, setSettingsRaw] = useState<CalSettings>(loadCalendar);
  const [res, setRes] = useState<CalResult | null>(null);
  const [error, setError] = useState<string | null>(null);
  const setSettings = (s: CalSettings) => { setSettingsRaw(s); saveCalendar(s); };
  const gstKey = JSON.stringify(settings.gst);

  useEffect(() => {
    let live = true;
    setError(null);
    api.post<CalResult>('/api/tax/calendar', { gst: settings.gst ?? undefined, months: 6 })
      .then((r) => { if (live) setRes(r); })
      .catch((e: Error) => { if (live) setError(e.message); });
    return () => { live = false; };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [gstKey]);

  const toggle = (id: string) => setSettings({ ...settings, filed: settings.filed.includes(id) ? settings.filed.filter((x) => x !== id) : [...settings.filed, id] });
  const g = settings.gst;
  const setGst = (p: Partial<NonNullable<CalSettings['gst']>>) => setSettings({ ...settings, gst: { ...(g ?? DEFAULT_GST), ...p } });
  const items: CalItem[] = res?.items ?? [];
  const open = items.filter((i) => !settings.filed.includes(i.id) && i.status !== 'later').length;

  return (
    <div className="page">
      <PageHeader title="Compliance calendar" badge={open ? <Badge tone="warn">{open} need attention</Badge> : <Badge tone="pos">Nothing urgent</Badge>}
        subtitle="Income-tax, tax-audit and GST dates in one list. Tick a date once it is filed; the Overview reminds you about what is still open." />

      <Card title="Your GST registration" subtitle="Optional. Add it to include your monthly or quarterly GST returns.">
        <div className="grid cols-3">
          <Field label="Registered for GST?">
            <select className="input" value={g ? g.registration : 'none'} onChange={(e) => e.target.value === 'none' ? setSettings({ ...settings, gst: null }) : setGst({ registration: e.target.value as 'regular' | 'composition' })}>
              <option value="none">No / not needed</option>
              <option value="regular">Regular scheme</option>
              <option value="composition">Composition scheme</option>
            </select>
          </Field>
          {g && <>
            <Field label="Last year's turnover (₹)" hint="Decides whether quarterly filing (QRMP) is allowed.">
              <input className="input" type="number" min={0} value={g.aggregate_turnover_prev_fy} onChange={(e) => setGst({ aggregate_turnover_prev_fy: Math.max(0, Number(e.target.value) || 0) })} />
            </Field>
            {g.registration === 'regular' && (
              <label className="row" style={{ fontSize: 13, alignSelf: 'end' }}>
                <input type="checkbox" checked={g.qrmp} onChange={(e) => setGst({ qrmp: e.target.checked })} />
                I file quarterly (QRMP)
              </label>
            )}
          </>}
        </div>
      </Card>

      <div className="mt">
        <Card title="Dates" subtitle={res ? `As of ${res.today}. Showing dates from the last 30 days onward.` : undefined}>
          {error && <ErrorBox error={error} />}
          {!res && !error && <Skeleton h={120} />}
          {res && !items.length && <EmptyState icon={<CalendarClock size={22} />} title="No upcoming dates">Nothing is due in this window.</EmptyState>}
          {res && items.length > 0 && (
            <ul className="cal-list" aria-label="Compliance dates">
              {items.map((i) => {
                const filed = settings.filed.includes(i.id);
                return (
                  <li key={i.id} className={`cal-row${filed ? ' done' : ''}`}>
                    <div className="cal-date"><b>{new Date(`${i.date}T00:00:00`).toLocaleDateString(undefined, { day: 'numeric', month: 'short' })}</b><span>{new Date(`${i.date}T00:00:00`).getFullYear()}</span></div>
                    <div className="cal-body">
                      <div><b>{i.title}</b> <Badge tone={i.area === 'gst' ? 'info' : 'accent'}>{i.area === 'gst' ? 'GST' : 'Income tax'}</Badge> {!filed && <Badge tone={TONE[i.status]}>{LABEL[i.status]}</Badge>} <span className="faint" style={{ fontSize: 12 }}>{whenText(i)}</span></div>
                      <div className="faint" style={{ fontSize: 12.5 }}>{i.detail}{i.source && <> <a href={i.source} target="_blank" rel="noreferrer">Source</a></>}</div>
                    </div>
                    <button className="btn sm" aria-pressed={filed} onClick={() => toggle(i.id)}>{filed ? <><Undo2 size={14} />Undo</> : <><CheckCircle2 size={14} />Mark filed</>}</button>
                  </li>
                );
              })}
            </ul>
          )}
          {res && <p className="faint" style={{ fontSize: 12, marginBottom: 0 }}>{res.note} {settings.filed.length > 0 && <>{fmtNum(settings.filed.length, 0)} marked filed, kept in this browser only.</>}</p>}
        </Card>
      </div>
      <div className="mt"><Callout tone="info" title="Reminders stay in the app">The app does not send email or text reminders. It shows what is due on your Overview each time you open it.</Callout></div>
    </div>
  );
}
