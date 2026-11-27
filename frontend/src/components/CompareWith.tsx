import { GitCompareArrows } from 'lucide-react';
import { useState } from 'react';
import { api } from '../lib/api';
import { fmtNum, fmtPctPoints, isNum } from '../lib/format';
import type { UploadSummary } from '../lib/types';
import { useAsync } from '../lib/useApi';
import { Badge, Disclosure, ErrorBox, Field } from './ui';

interface Row { label: string; older: number; older_period: string | null; older_ref: string | null; newer: number; newer_period: string | null; newer_ref: string | null; change: number; change_pct: number | null; moved: boolean }
interface Result { older: { name: string }; newer: { name: string }; rows: Row[]; only_in_older: string[]; only_in_newer: string[]; matched: number; moved: number; headline: string; note: string }

/** "What changed since last time": set this file beside another upload of the same kind of data and rank the lines by how much they moved. */
export function CompareWith({ currentId }: { currentId: string }) {
  const uploads = useAsync((signal) => api.get<{ uploads: UploadSummary[] }>('/api/uploads', { signal }), []);
  const [otherId, setOtherId] = useState('');
  const [otherIsNewer, setOtherIsNewer] = useState(false);
  const [res, setRes] = useState<Result | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);
  const [all, setAll] = useState(false);
  const others = (uploads.data?.uploads ?? []).filter((u) => u.id !== currentId && u.status === 'processed');
  if (!others.length) return null;

  const run = async (id: string, newer: boolean) => {
    setOtherId(id);
    setRes(null);
    setError(null);
    if (!id) return;
    setBusy(true);
    try {
      setRes(await api.post<Result>('/api/analysis/compare', newer ? { older_id: currentId, newer_id: id } : { older_id: id, newer_id: currentId }));
    } catch (e) { setError((e as Error).message); } finally { setBusy(false); }
  };

  return (
    <div className="mt">
      <Disclosure title="Compare with another file: what changed?" icon={<GitCompareArrows size={16} className="pos" />}>
        <div className="stack">
          <div className="grid cols-2">
            <Field label="Other file">
              <select className="input" value={otherId} onChange={(e) => run(e.target.value, otherIsNewer)}>
                <option value="">Choose a file…</option>
                {others.map((u) => <option key={u.id} value={u.id}>{u.name}</option>)}
              </select>
            </Field>
            <label className="row" style={{ fontSize: 13, alignSelf: 'end' }}>
              <input type="checkbox" checked={otherIsNewer} onChange={(e) => { setOtherIsNewer(e.target.checked); if (otherId) run(otherId, e.target.checked); }} />
              The other file is the newer one
            </label>
          </div>
          {busy && <p className="faint">Comparing…</p>}
          {error && <ErrorBox error={error} />}
          {res && (
            <>
              <p style={{ fontWeight: 600, margin: 0 }}>{res.headline}</p>
              {res.rows.length > 0 && (
                <div className="table-wrap" tabIndex={0}>
                  <table className="data">
                    <thead><tr><th>Line</th><th className="r">{res.older.name}</th><th className="r">{res.newer.name}</th><th className="r">Change</th><th className="r">Change %</th></tr></thead>
                    <tbody>
                      {(all ? res.rows : res.rows.slice(0, 12)).map((r) => (
                        <tr key={r.label}>
                          <td>{r.label}</td>
                          <td className="r" title={r.older_ref ?? undefined}>{fmtNum(r.older, Number.isInteger(r.older) ? 0 : 2)}</td>
                          <td className="r" title={r.newer_ref ?? undefined}>{fmtNum(r.newer, Number.isInteger(r.newer) ? 0 : 2)}</td>
                          <td className="r">{fmtNum(r.change, Number.isInteger(r.change) ? 0 : 2)}</td>
                          <td className="r">{isNum(r.change_pct) ? <>{fmtPctPoints(r.change_pct, 1)} {r.moved && <Badge tone="warn">moved</Badge>}</> : 'n/a'}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              )}
              {res.rows.length > 12 && <button className="btn sm" onClick={() => setAll(!all)}>{all ? 'Show fewer' : `Show all ${res.rows.length}`}</button>}
              {(res.only_in_older.length > 0 || res.only_in_newer.length > 0) && (
                <p className="faint" style={{ fontSize: 12.5, margin: 0 }}>
                  {res.only_in_older.length > 0 && <>Only in {res.older.name}: {res.only_in_older.join(', ')}. </>}
                  {res.only_in_newer.length > 0 && <>Only in {res.newer.name}: {res.only_in_newer.join(', ')}.</>}
                </p>
              )}
              <p className="faint" style={{ fontSize: 12, margin: 0 }}>{res.note}</p>
            </>
          )}
        </div>
      </Disclosure>
    </div>
  );
}
