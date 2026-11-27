import { CheckCircle2, PlayCircle, XCircle } from 'lucide-react';
import { useState } from 'react';
import { Badge, Callout, Card, PageHeader } from '../components/ui';
import { api } from '../lib/api';
import { breakEven, emiFor, monthlySavingFor, priceFor } from '../lib/quickCalcs';
import { depreciation, leaseVsBuy } from '../lib/quickCalcs2';

interface Check { name: string; expected: string; run: () => Promise<number> | number; want: number; tol: number }
interface Outcome { name: string; expected: string; got: string; ok: boolean }

/** Textbook problems with known answers. Anyone can run them and see that the engine agrees with a hand calculation. */
const CHECKS: Check[] = [
  { name: 'Loan: 10,00,000 at 12% for a year, monthly instalment', expected: '88,848.79', want: 88848.79, tol: 0.01, run: () => emiFor(1_000_000, 12, 1) },
  { name: 'Savings: 5 years at 12% to reach 10,00,000, monthly saving', expected: '12,244.45', want: 12244.45, tol: 0.01, run: () => monthlySavingFor(1_000_000, 0, 5, 12) },
  { name: 'Break-even: price 100, variable 60, fixed 2,00,000, units', expected: '5,000', want: 5000, tol: 1e-9, run: () => breakEven(100, 60, 200_000, 8000)!.units },
  { name: 'Pricing: cost 60, 25% margin, no discount or fee, list price', expected: '80', want: 80, tol: 1e-9, run: () => priceFor({ unitCost: 60, targetMarginPct: 25, discountPct: 0, feePct: 0, gstPct: 0 })!.listPrice },
  { name: 'Depreciation: 1,00,000 less 10,000 scrap over 5 years, yearly charge', expected: '18,000', want: 18000, tol: 1e-9, run: () => depreciation(100_000, 10_000, 5, 'straight', 0)[0].charge },
  { name: 'Lease or buy at 0%: cost of buying', expected: '950', want: 950, tol: 1e-9, run: () => leaseVsBuy({ price: 1000, resale: 200, years: 3, maintenancePerYear: 50, leasePerYear: 300, discountPct: 0 }).buy },
  {
    name: 'Server: NPV of -1,000 then 500, 500, 500 at 10%', expected: '243.43', want: 243.43, tol: 0.01,
    run: async () => (await api.post<{ npv: number }>('/api/finance/appraisal', { cash_flows: [-1000, 500, 500, 500], discount_rate: 0.1 })).npv,
  },
];

export function SelfCheck() {
  const [out, setOut] = useState<Outcome[] | null>(null);
  const [busy, setBusy] = useState(false);
  const run = async () => {
    setBusy(true);
    const res: Outcome[] = [];
    for (const c of CHECKS) {
      try {
        const got = await c.run();
        res.push({ name: c.name, expected: c.expected, got: got.toLocaleString(undefined, { maximumFractionDigits: 2 }), ok: Math.abs(got - c.want) <= c.tol });
      } catch (e) { res.push({ name: c.name, expected: c.expected, got: (e as Error).message, ok: false }); }
    }
    setOut(res);
    setBusy(false);
  };
  const pass = out?.filter((o) => o.ok).length ?? 0;
  return (
    <div className="page">
      <PageHeader title="Self-check" subtitle="Run textbook problems with known answers through this app's own engine and see that it agrees with a hand calculation." badge={out ? <Badge tone={pass === out.length ? 'pos' : 'neg'}>{pass} of {out.length} agree</Badge> : undefined}
        actions={<button className="btn primary" onClick={run} disabled={busy}><PlayCircle size={15} />{busy ? 'Running…' : 'Run the checks'}</button>} />
      {!out && <Callout tone="info">Press the button. Each problem is small enough to check by hand, and the expected answer is shown beside the app's.</Callout>}
      {out && (
        <Card flush>
          <ul className="selfcheck" aria-label="Self-check results">
            {out.map((o) => (
              <li key={o.name} className="row between" style={{ padding: '10px 14px', borderBottom: '1px solid var(--border)', gap: 12 }}>
                <span style={{ display: 'flex', gap: 8, alignItems: 'center' }}>{o.ok ? <CheckCircle2 size={16} className="pos" aria-label="Agrees" /> : <XCircle size={16} className="neg" aria-label="Does not agree" />}{o.name}</span>
                <span className="faint" style={{ fontSize: 12.5, whiteSpace: 'nowrap' }}>expected {o.expected}, got {o.got}</span>
              </li>
            ))}
          </ul>
        </Card>
      )}
    </div>
  );
}
