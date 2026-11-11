import { ArrowDown, ArrowRight, ArrowUp, CheckCircle2, FileSpreadsheet, LineChart, Lightbulb, UploadCloud, X } from 'lucide-react';
import type { ReactNode } from 'react';
import { Link } from 'react-router-dom';
import { useGuide } from '../lib/guide';

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

/** The "Get started" card for a first visit: dismissible, and it can be brought back from Settings. */
export function GetStarted() {
  const { isOn, dismiss, setOff } = useGuide();
  if (!isOn('get-started')) return null;
  return (
    <div className="card get-started" role="region" aria-label="Get started">
      <div className="row between" style={{ alignItems: 'flex-start' }}>
        <div>
          <div className="row" style={{ gap: 8 }}><Lightbulb size={18} className="pos" /><b style={{ fontSize: 16 }}>New here? Get your statements in three steps</b></div>
          <p className="faint" style={{ margin: '4px 0 0', fontSize: 13 }}>Follow the arrows. Everything stays private to your account, and every number shows its formula and source.</p>
        </div>
        <button className="btn sm ghost" aria-label="Close this guide" onClick={() => dismiss('get-started')}><X size={15} />Close</button>
      </div>
      <GuideSteps />
      <div className="row" style={{ gap: 14, marginTop: 8 }}>
        <button className="hint-link" onClick={() => setOff(true)}>Hide all tips</button>
        <span className="faint" style={{ fontSize: 12 }}><CheckCircle2 size={12} style={{ verticalAlign: -2 }} /> You can turn tips back on in Settings.</span>
      </div>
    </div>
  );
}
