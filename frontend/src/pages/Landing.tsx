import { Activity, ArrowRight, Calculator, FileSpreadsheet, FileUp, Landmark, LineChart, ShieldAlert, ShieldCheck, Sigma } from 'lucide-react';
import { useEffect, useMemo, useState } from 'react';
import { Backdrop } from '../components/Backdrop';
import { Card, ErrorBox, Kpi, NumberField, ReadingCard } from '../components/ui';
import { api } from '../lib/api';
import { fmtMoney, fmtPct, isNum } from '../lib/format';
import { readAppraisal } from '../lib/readings';
import { useAsync, useDebounced } from '../lib/useApi';

interface Appraisal {
  npv: number; irr: { status: string; values: number[]; sign_changes: number };
  payback: { period: number | null }; discounted_payback: { period: number | null };
  profitability_index: { value: number | null }; timeline: { t: number }[];
}

const FEATURES = [
  { icon: FileUp, title: 'Upload anything', text: 'Excel, CSV, PDF, Word, text, JSON and more. Messy files are fine: it shows what it found, where from, and what it could not read.' },
  { icon: Landmark, title: 'Valuation you can defend', text: 'DCF, reverse DCF and Monte Carlo ranges, with every assumption and formula on screen.' },
  { icon: LineChart, title: 'Ratios in plain English', text: '35 ratios, each with what it means, a typical range, and what to look at next.' },
  { icon: ShieldAlert, title: 'Forensic screens', text: 'Beneish, Altman and Piotroski scores plus cash-quality checks, with the parts that drive them.' },
  { icon: Sigma, title: 'Professional schedules', text: 'Leases, bonds, EPS, deferred tax, costing, income tax and GST workings, ready for a workpaper.' },
  { icon: FileSpreadsheet, title: 'Audit-ready exports', text: 'Excel with live formulas, Word and print-ready PDF reports.' },
];

/** What visitors see before signing in: what the app is, a working calculator they can try with no account, and the way in. */
export function Landing({ onSignIn, onRegister }: { onSignIn: () => void; onRegister: () => void }) {
  const [initial, setInitial] = useState<number | null>(100000);
  const [rate, setRate] = useState<number | null>(0.1);
  const [flows, setFlows] = useState<(number | null)[]>([30000, 35000, 40000, 30000, 20000]);
  const ready = isNum(initial) && initial > 0 && isNum(rate) && flows.every(isNum);
  const body = useMemo(() => (ready ? { initial, flows, rate } : null), [ready, initial, rate, flows]);
  const req = useDebounced(body, 250);
  const res = useAsync((signal) => api.post<Appraisal>('/api/demo/appraisal', req, { signal }), [JSON.stringify(req)], !!req);
  const r = res.data;
  useEffect(() => { document.title = 'Finance Intelligence Studio: financial analysis you can defend'; }, []);

  return (
    <div className="landing">
      <Backdrop />
      <header className="landing-bar">
        <div className="row" style={{ gap: 10 }}>
          <div className="brand-mark" style={{ width: 36, height: 36, borderRadius: 11 }}><Activity size={19} strokeWidth={2.5} /></div>
          <b style={{ fontFamily: 'var(--font-display)', fontSize: 17 }}>Finance Intelligence Studio</b>
        </div>
        <div className="row">
          <button className="btn ghost" onClick={onSignIn}>Sign in</button>
          <button className="btn primary" onClick={onRegister}>Create a free account</button>
        </div>
      </header>

      <main className="landing-main">
        <section className="landing-hero">
          <h1>Analysis you can <span>defend</span></h1>
          <p>A financial analysis workspace for CPAs, CFA charterholders, CMAs, auditors and finance teams. Every number shows its formula, its inputs and where it came from.</p>
          <div className="row" style={{ gap: 10, flexWrap: 'wrap' }}>
            <button className="btn primary lg" onClick={onRegister}>Get started free <ArrowRight size={16} /></button>
            <a className="btn lg" href="#try">Try a calculator first</a>
          </div>
          <ul className="landing-chips">
            <li><ShieldCheck size={14} />Private to your account</li>
            <li><Calculator size={14} />Formulas and sources shown</li>
            <li><FileSpreadsheet size={14} />Excel, Word and PDF exports</li>
          </ul>
        </section>

        <section id="try" className="landing-try" aria-labelledby="try-title">
          <Card title={<span id="try-title">Try it now: is this project worth doing?</span>} subtitle="No sign-up. Change the numbers and the answer updates.">
            <div className="grid cols-2" style={{ gap: 14 }}>
              <NumberField label="Money put in today" value={initial} onChange={setInitial} min={1} required />
              <NumberField label="Return you require each year" percent value={rate} onChange={setRate} min={0} max={100} required />
            </div>
            <div className="field-label" style={{ margin: '12px 0 6px' }}>Cash it brings in each year</div>
            <div className="landing-flows">
              {flows.map((f, i) => (
                <NumberField key={i} compact ariaLabel={`Cash in year ${i + 1}`} label={`Year ${i + 1}`} value={f} required
                  onChange={(v) => setFlows((fl) => fl.map((x, j) => (j === i ? v : x)))} />
              ))}
            </div>
            {res.error && <div className="mt"><ErrorBox error={res.error} /></div>}
            {r && ready && (
              <div className="stack mt">
                <div className="grid cols-3">
                  <Kpi label="Net present value" value={fmtMoney(r.npv, 'INR')} deltaTone={r.npv >= 0 ? 'pos' : 'neg'} delta={r.npv >= 0 ? 'Worth doing' : 'Not worth doing'} />
                  <Kpi label="Project's own return (IRR)" value={r.irr.status === 'unique' ? fmtPct(r.irr.values[0]) : r.irr.status === 'multiple' ? 'Several' : 'None'} />
                  <Kpi label="Earned back (with interest)" value={isNum(r.discounted_payback.period) ? `${r.discounted_payback.period.toFixed(1)} yrs` : 'Not within the years given'} />
                </div>
                <ReadingCard reading={readAppraisal(r, rate as number, 'INR')} />
              </div>
            )}
            <p className="faint mt-sm" style={{ fontSize: 12.5 }}>This is one of 24 tools. The same engine runs inside the app, where you can also save, compare and export. Illustration only, not investment advice.</p>
          </Card>
        </section>

        <section className="landing-features" aria-labelledby="what-title">
          <h2 id="what-title">What is inside</h2>
          <div className="grid cols-3">
            {FEATURES.map((f) => (
              <div key={f.title} className="card landing-feature">
                <f.icon size={20} className="pos" aria-hidden="true" />
                <h3>{f.title}</h3>
                <p>{f.text}</p>
              </div>
            ))}
          </div>
        </section>

        <section className="landing-steps" aria-labelledby="how-title">
          <h2 id="how-title">How it works</h2>
          <ol>
            <li><b>Bring your data.</b> Upload a file or import a Screener.in export.</li>
            <li><b>See what it found.</b> Every table, number and source cell, with anything unclear flagged for you to confirm.</li>
            <li><b>Analyse and share.</b> Ratios, valuation, red flags, tax and more, with plain-English readings and exports.</li>
          </ol>
          <button className="btn primary lg" onClick={onRegister}>Create a free account <ArrowRight size={16} /></button>
        </section>
      </main>

      <footer className="landing-foot faint">
        <span>Educational and analytical tool, not investment advice. Passwords are hashed and sessions use secure, HttpOnly cookies.</span>
        <span><a href="/services">Need a custom model or report? See my 50 services</a></span>
      </footer>
    </div>
  );
}
