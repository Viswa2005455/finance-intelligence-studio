import { CalendarClock } from 'lucide-react';
import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { api } from '../lib/api';
import { attention, loadCalendar, whenText, type CalItem, type CalResult } from '../lib/complianceCalendar';
import { Callout } from './ui';

/** On the Overview: dates that are due this week or already missed, unless they are marked filed. Silent when nothing is open or the call fails. */
export function DueSoonBanner() {
  const [items, setItems] = useState<CalItem[]>([]);
  useEffect(() => {
    const s = loadCalendar();
    let live = true;
    api.post<CalResult>('/api/tax/calendar', { gst: s.gst ?? undefined, months: 3 })
      .then((r) => { if (live) setItems(attention(r.items, s.filed)); })
      .catch(() => undefined);
    return () => { live = false; };
  }, []);
  if (!items.length) return null;
  return (
    <div className="mt" data-testid="due-soon">
      <Callout tone="warn" title={<><CalendarClock size={15} style={{ verticalAlign: -2 }} /> {items.length} compliance {items.length === 1 ? 'date needs' : 'dates need'} attention</>}>
        <ul className="summary-list">
          {items.slice(0, 4).map((i) => <li key={i.id}><b>{i.title}</b>, {new Date(`${i.date}T00:00:00`).toLocaleDateString(undefined, { day: 'numeric', month: 'short' })} ({whenText(i)})</li>)}
        </ul>
        <Link to="/calendar">Open the compliance calendar</Link>
      </Callout>
    </div>
  );
}
