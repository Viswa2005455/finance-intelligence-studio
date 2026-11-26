import { useEffect, useMemo, useState } from 'react';
import { PublicShell } from '../components/PublicShell';
import { Card, ErrorBox, Formula, Skeleton } from '../components/ui';
import { api } from '../lib/api';
import { useAsync } from '../lib/useApi';

interface RatioDoc { key: string; name: string; category: string; formula: string; unit: string; typical: string; caution: string; related: string[] }
interface MethodDoc { group: string; name: string; formula: string; what: string; caution: string }
interface Catalogue { ratios: RatioDoc[]; methods: MethodDoc[]; conventions: string[] }

/** Public page: every calculation the app makes, with its formula, what is typical and what could mislead. Generated from the engine. */
export function Methodology() {
  const res = useAsync((signal) => api.get<Catalogue>('/api/public/methodology', { signal }), []);
  const [q, setQ] = useState('');
  useEffect(() => { document.title = 'How we calculate: Finance Intelligence Studio'; }, []);
  const c = res.data;
  const hit = (text: string) => q.toLowerCase().split(/\s+/).filter(Boolean).every((t) => text.toLowerCase().includes(t));
  const methods = useMemo(() => (c?.methods ?? []).filter((m) => hit(`${m.name} ${m.formula} ${m.what} ${m.group}`)), [c, q]); // eslint-disable-line react-hooks/exhaustive-deps
  const ratios = useMemo(() => (c?.ratios ?? []).filter((r) => hit(`${r.name} ${r.formula} ${r.category} ${r.typical}`)), [c, q]); // eslint-disable-line react-hooks/exhaustive-deps
  const nameOf = (k: string) => c?.ratios.find((r) => r.key === k)?.name ?? k;
  const groups = Array.from(new Set(ratios.map((r) => r.category)));
  const methodGroups = Array.from(new Set(methods.map((m) => m.group)));

  return (
    <PublicShell title="How we calculate">
      <section className="landing-hero" style={{ paddingTop: 20 }}>
        <h1 style={{ fontSize: 'clamp(30px, 5vw, 44px)' }}>How we calculate</h1>
        <p>Every number in the app comes from a formula you can read here. The ratio list below is generated from the calculation engine itself, so it always matches what the app does.</p>
        <label className="field-label" htmlFor="m-search">Search the formulas</label>
        <input id="m-search" className="input" style={{ maxWidth: 420 }} value={q} onChange={(e) => setQ(e.target.value)} placeholder="for example: ROE, NPV, liquidity" />
      </section>

      {res.error && <ErrorBox error={res.error} onRetry={res.reload} />}
      {!c && !res.error && <Skeleton h={200} />}

      {c && (
        <>
          <Card title="Ground rules" subtitle="How every result is produced">
            <ul className="summary-list">{c.conventions.map((x) => <li key={x}>{x}</li>)}</ul>
          </Card>

          {methodGroups.map((g) => (
            <section key={g} aria-labelledby={`m-${g}`}>
              <h2 id={`m-${g}`} style={{ fontSize: 22, margin: '8px 0 12px' }}>{g}</h2>
              <div className="grid cols-2">
                {methods.filter((m) => m.group === g).map((m) => (
                  <Card key={m.name} title={m.name}>
                    <Formula>{m.formula}</Formula>
                    <p style={{ fontSize: 13.5, margin: '10px 0 0' }}>{m.what}</p>
                    <p className="faint" style={{ fontSize: 12.5, margin: '6px 0 0' }}><b>Watch out:</b> {m.caution}</p>
                  </Card>
                ))}
              </div>
            </section>
          ))}

          {groups.map((g) => (
            <section key={g} aria-labelledby={`r-${g}`}>
              <h2 id={`r-${g}`} style={{ fontSize: 22, margin: '8px 0 12px' }}>{g} ratios</h2>
              <div className="grid cols-2">
                {ratios.filter((r) => r.category === g).map((r) => (
                  <Card key={r.key} title={r.name} subtitle={r.unit === 'x' ? 'A multiple' : r.unit === '%' ? 'A percentage' : r.unit === 'days' ? 'Days' : 'An amount'}>
                    <Formula>{r.formula}</Formula>
                    <dl style={{ margin: '10px 0 0', display: 'grid', gridTemplateColumns: 'max-content 1fr', gap: '3px 10px', fontSize: 12.5 }}>
                      <dt style={{ color: 'var(--text-muted)', fontWeight: 600 }}>Typical range</dt><dd style={{ margin: 0 }}>{r.typical}</dd>
                      {r.caution && <><dt style={{ color: 'var(--text-muted)', fontWeight: 600 }}>Watch out</dt><dd style={{ margin: 0 }}>{r.caution}</dd></>}
                      {r.related.length > 0 && <><dt style={{ color: 'var(--text-muted)', fontWeight: 600 }}>Read with</dt><dd style={{ margin: 0 }}>{r.related.map(nameOf).join(', ')}</dd></>}
                    </dl>
                  </Card>
                ))}
              </div>
            </section>
          ))}
          {methods.length === 0 && ratios.length === 0 && <p className="muted">Nothing matches “{q}”.</p>}
        </>
      )}
    </PublicShell>
  );
}
