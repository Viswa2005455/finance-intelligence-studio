import { History } from 'lucide-react';
import { Link } from 'react-router-dom';
import { NAV } from '../nav';
import { useRecent } from '../lib/progress';
import { Card } from './ui';

const ago = (t: number) => {
  const m = Math.round((Date.now() - t) / 60000);
  if (m < 1) return 'just now';
  if (m < 60) return `${m} min ago`;
  const h = Math.round(m / 60);
  if (h < 24) return `${h} h ago`;
  return `${Math.round(h / 24)} d ago`;
};

/** "Pick up where you left off": the pages this browser opened most recently. Nothing leaves the browser. */
export function RecentPages() {
  const recent = useRecent();
  const items = recent.map((r) => ({ ...r, nav: NAV.find((n) => n.to === r.path) })).filter((r) => r.nav && r.path !== '/').slice(0, 5);
  if (!items.length) return null;
  return (
    <Card title={<span className="row"><History size={16} className="pos" />Pick up where you left off</span>} subtitle="The pages you opened most recently on this device">
      <div className="row" style={{ gap: 8, flexWrap: 'wrap' }}>
        {items.map((r) => {
          const Icon = r.nav!.icon;
          return (
            <Link key={r.path} to={r.path} className="btn sm" title={`Opened ${ago(r.at)}`}>
              <Icon size={14} aria-hidden="true" />{r.nav!.label}<span className="faint" style={{ fontWeight: 400, fontSize: 11.5 }}>{ago(r.at)}</span>
            </Link>
          );
        })}
      </div>
    </Card>
  );
}
