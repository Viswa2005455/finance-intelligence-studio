import { ArrowDown, ArrowRight, ArrowUp, CheckCircle2, FileSpreadsheet, LineChart, Lightbulb, UploadCloud, X } from 'lucide-react';
import { useState, type ReactNode } from 'react';
import { Link } from 'react-router-dom';
import { api } from '../lib/api';
import { addSampleCompany } from '../lib/sampleCompany';
import { useToast } from '../lib/toast';
import { useCompanySources } from '../lib/company';
import { useGuide } from '../lib/guide';
import { ANALYSIS_PAGES, useVisited } from '../lib/progress';
import { useAsync } from '../lib/useApi';

/**
 * A friendly tip with a bouncing arrow that points at what to do next. It sits in the page flow (above or below
 * the thing it points at), so it never covers anything. "Got it" hides this tip; "Hide all tips" hides every one.
 */
export function Hint({ id, step, title, children, dir = 'down', active = true, onGotIt }: {
  id: string; step?: number; title?: ReactNode; children?: ReactNode; dir?: 'down' | 'up'; active?: boolean; onGotIt?: () => void;
}) {
  const { isOn, dismiss, setOff } = useGuide();
  if (!active || !isOn(id)) return null;
  const Arrow = dir === 'down' ? ArrowDown : ArrowUp;
  return (
    <div className={`hint ${dir}`} role="note">
      {dir === 'up' && <Arrow className="hint-arrow" size={26} aria-hidden="true" />}
      <div className="hint-bubble">
        {step !== undefined && <span className="hint-step" aria-label={`Step ${step}`}>{step}</span>}
        <div className="hint-text">
          {title && <b>{title}</b>}
          <div>{children}</div>
        </div>
        <div className="hint-actions">
          <button className="btn sm" onClick={() => { dismiss(id); onGotIt?.(); }}>Got it</button>
          <button className="hint-link" onClick={() => setOff(true)}>Hide all tips</button>
        </div>
      </div>
      {dir === 'down' && <Arrow className="hint-arrow" size={26} aria-hidden="true" />}
    </div>
  );
}

/** The three steps from a file to its statements, with arrows between them. */
export function GuideSteps({ compact = false }: { compact?: boolean }) {
  const steps: { n: number; icon: ReactNode; title: string; text: string; to: string; cta: string }[] = [
    { n: 1, icon: <UploadCloud size={20} />, title: 'Upload your file', text: 'An Excel, CSV or PDF with your income statement, balance sheet or cash flow.', to: '/upload', cta: 'Go to Upload' },
    { n: 2, icon: <FileSpreadsheet size={20} />, title: 'See your statements', text: 'Open Financial Statements and click your file to import its statements.', to: '/statements', cta: 'Open Financial Statements' },
    { n: 3, icon: <LineChart size={20} />, title: 'Analyse', text: 'Ratios, cash flow, red flags and more use the same file, with every formula shown.', to: '/ratios', cta: 'Open Ratio Analysis' },
  ];
  return (
    <div className={`guide-steps ${compact ? 'compact' : ''}`}>
      {steps.map((s, i) => (
        <div className="guide-step-wrap" key={s.n}>
          <div className="guide-step">
            <span className="hint-step">{s.n}</span>
            <div className="guide-step-icon" aria-hidden="true">{s.icon}</div>
            <b>{s.title}</b>
            {!compact && <p>{s.text}</p>}
            <Link to={s.to} className="btn sm">{s.cta}</Link>
          </div>
          {i < steps.length - 1 && <ArrowRight className="guide-step-arrow" size={22} aria-hidden="true" />}
        </div>
      ))}
    </div>
  );
}

/** First-run checklist: three steps with progress that ticks itself off, plus a no-file path to explore. It is
 * dismissible and can be brought back from Settings. */
export function GetStarted() {
  const { isOn, dismiss, setOff } = useGuide();
  const visited = useVisited();
  const uploads = useAsync((signal) => api.get<{ uploads: unknown[] }>('/api/uploads', { signal }), []);
  const { sources } = useCompanySources();
  const toast = useToast();
  const [busy, setBusy] = useState(false);
  if (!isOn('get-started')) return null;
  const loadSample = async () => {
    setBusy(true);
    try { await addSampleCompany(); window.location.assign('/'); }  // reload so the dashboard picks the company up
    catch (e) { toast((e as Error).message, 'error'); setBusy(false); }
  };

  const uploaded = (uploads.data?.uploads.length ?? 0) > 0;
  const imported = (sources ?? []).some((s) => !s.isExample);
  const analysed = ANALYSIS_PAGES.some((p) => visited.includes(p));
  const steps: { done: boolean; icon: ReactNode; title: string; text: string; to: string; cta: string }[] = [
    { done: uploaded, icon: <UploadCloud size={20} />, title: 'Bring your data', text: 'Upload any file: Excel, CSV, PDF, Word, text, JSON and more. Messy files are fine; the app shows what it found and what it could not read.', to: '/upload', cta: uploaded ? 'Upload another' : 'Upload a file' },
    { done: imported, icon: <FileSpreadsheet size={20} />, title: 'Turn it into statements', text: 'Open Financial Statements and click your file, or import a Screener.in export in one click.', to: '/statements', cta: imported ? 'Open statements' : 'Import a company' },
    { done: analysed, icon: <LineChart size={20} />, title: 'Run your first analysis', text: 'Ratios, red flags, DCF and more reuse the same data. Every number shows its formula and what it means.', to: '/ratios', cta: analysed ? 'Open Ratio Analysis' : 'See your ratios' },
  ];
  const doneCount = steps.filter((s) => s.done).length;
  const next = steps.findIndex((s) => !s.done);

  return (
    <div className="card get-started" role="region" aria-label="Get started">
      <div className="row between" style={{ alignItems: 'flex-start' }}>
        <div>
          <div className="row" style={{ gap: 8 }}><Lightbulb size={18} className="pos" /><b style={{ fontSize: 16 }}>Get started: {doneCount} of 3 done</b></div>
          <p className="faint" style={{ margin: '4px 0 0', fontSize: 13 }}>Everything stays private to your account, and every number shows its formula and source.</p>
        </div>
        <button className="btn sm ghost" aria-label="Close this guide" onClick={() => dismiss('get-started')}><X size={15} />Close</button>
      </div>
      <div className="progress first-run-bar" role="progressbar" aria-valuemin={0} aria-valuemax={3} aria-valuenow={doneCount} aria-label="First-run progress"><i style={{ width: `${(doneCount / 3) * 100}%` }} /></div>
      <div className="first-run-steps">
        {steps.map((s, i) => (
          <div key={s.title} className={`first-run-step ${s.done ? 'done' : ''} ${i === next ? 'next' : ''}`}>
            <span className="first-run-icon" aria-hidden="true">{s.done ? <CheckCircle2 size={20} /> : s.icon}</span>
            <b>{i + 1}. {s.title}</b>
            <p>{s.text}</p>
            <Link to={s.to} className={`btn sm ${i === next ? 'primary' : ''}`}>{s.cta}{i === next && <ArrowRight size={14} />}</Link>
          </div>
        ))}
      </div>
      <div className="row between first-run-foot">
        <span className="row" style={{ gap: 10, flexWrap: 'wrap', fontSize: 13 }}>
          <button className="btn sm" onClick={loadSample} disabled={busy}>{busy ? 'Adding…' : 'Try it with a sample company'}</button>
          <span className="faint">No file yet? Or <Link to="/dcf">try a DCF</Link> or <Link to="/investment">appraise a project</Link>.</span>
        </span>
        <span className="row" style={{ gap: 14 }}>
          <button className="hint-link" onClick={() => setOff(true)}>Hide all tips</button>
          <span className="faint" style={{ fontSize: 12 }}>Turn tips back on in Settings.</span>
        </span>
      </div>
    </div>
  );
}
