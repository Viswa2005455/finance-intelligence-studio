import { AlertTriangle, ChevronDown, Copy, GraduationCap, Info, CheckCircle2, XCircle, Construction } from 'lucide-react';
import { cloneElement, isValidElement, memo, useEffect, useId, useRef, useState, type ReactElement, type ReactNode } from 'react';
import { Link } from 'react-router-dom';
import { problemLog } from '../lib/api';
import { LEVEL_LABEL, type Reading } from '../lib/readings';
import { isNum, parseInputNumber } from '../lib/format';
import { useSettings } from '../lib/settings';

export function PageHeader({ title, subtitle, actions, badge }: { title: string; subtitle?: ReactNode; actions?: ReactNode; badge?: ReactNode }) {
  return (
    <header className="page-header">
      <div>
        <div className="row">
          <h1>{title}</h1>
          {badge}
        </div>
        {subtitle && <p>{subtitle}</p>}
      </div>
      {actions && <div className="page-actions">{actions}</div>}
    </header>
  );
}

export function Card({ title, subtitle, actions, children, className = '', flush }: {
  title?: ReactNode; subtitle?: ReactNode; actions?: ReactNode; children?: ReactNode; className?: string; flush?: boolean;
}) {
  return (
    <section className={`card ${flush ? 'flush' : ''} ${className}`}>
      {(title || actions) && (
        <div className="card-head">
          <div>
            {title && <h2 className="card-title">{title}</h2>}
            {subtitle && <div className="card-sub">{subtitle}</div>}
          </div>
          {actions && <div className="row">{actions}</div>}
        </div>
      )}
      {children}
    </section>
  );
}

/** Value that briefly highlights when it changes (KPI updates after assumption changes). */
export function FlashValue({ value, className = '' }: { value: string; className?: string }) {
  const [flash, setFlash] = useState(false);
  const prev = useRef(value);
  useEffect(() => {
    if (prev.current !== value) {
      prev.current = value;
      setFlash(true);
      const t = setTimeout(() => setFlash(false), 500);
      return () => clearTimeout(t);
    }
  }, [value]);
  return <div className={`${className} ${flash ? 'flash' : ''}`}>{value}</div>;
}

export function Kpi({ label, value, delta, deltaTone, hint, spark }: { label: string; value: string; delta?: ReactNode; deltaTone?: 'pos' | 'neg' | 'muted'; hint?: string; spark?: ReactNode }) {
  return (
    <div className="card kpi" title={hint}>
      <div className="kpi-label">{label}</div>
      <div className="kpi-top">
        <FlashValue className="kpi-value" value={value} />
        {spark && <div className="kpi-spark">{spark}</div>}
      </div>
      {delta && <div className={`kpi-delta ${deltaTone ?? 'muted'}`}>{delta}</div>}
    </div>
  );
}

/** Label + control. A single <input>/<select>/<textarea> child is linked to the label automatically. */
export function Field({ label, hint, children, htmlFor }: { label: ReactNode; hint?: ReactNode; children: ReactNode; htmlFor?: string }) {
  const autoId = useId();
  let id = htmlFor;
  let control = children;
  if (!id && isValidElement(children) && typeof children.type === 'string' && ['input', 'select', 'textarea'].includes(children.type)) {
    const own = (children.props as { id?: string }).id;
    id = own ?? autoId;
    if (!own) control = cloneElement(children as ReactElement<{ id?: string }>, { id });
  }
  return (
    <div className="field">
      <label className="field-label" htmlFor={id}>{label}</label>
      {control}
      {hint && <div className="field-hint">{hint}</div>}
    </div>
  );
}

/**
 * Numeric input. With `percent`, the user types 12.5 and the component reports 0.125.
 * Empty input reports null — it is never silently turned into zero.
 */
export function NumberField({ label, value, onChange, percent, suffix, hint, min, max, required, compact, ariaLabel }: {
  label?: ReactNode; value: number | null; onChange: (v: number | null) => void; percent?: boolean; suffix?: string;
  hint?: ReactNode; min?: number; max?: number; required?: boolean; compact?: boolean; ariaLabel?: string;
}) {
  const id = useId();
  const toText = (v: number | null) => (isNum(v) ? String(Number((percent ? v * 100 : v).toPrecision(12))) : '');
  const [text, setText] = useState(toText(value));
  const lastEmitted = useRef<number | null>(value);

  useEffect(() => {
    if (value !== lastEmitted.current) {
      setText(toText(value));
      lastEmitted.current = value;
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [value, percent]);

  const parsed = parseInputNumber(text);
  const shown = parsed;
  const invalid = (text.trim() !== '' && parsed === null) || (required && parsed === null) ||
    (shown !== null && ((min !== undefined && shown < min) || (max !== undefined && shown > max)));

  const input = (
    <div className="input-wrap">
      <input
        id={id}
        className={`input ${compact ? 'compact' : ''} ${invalid ? 'invalid' : ''}`}
        inputMode="decimal"
        value={text}
        aria-label={ariaLabel}
        aria-invalid={invalid || undefined}
        onChange={(e) => {
          setText(e.target.value);
          const p = parseInputNumber(e.target.value);
          const out = p === null ? null : percent ? p / 100 : p;
          lastEmitted.current = out;
          onChange(out);
        }}
      />
      {(percent || suffix) && <span className="suffix">{percent ? '%' : suffix}</span>}
    </div>
  );
  if (!label) return input;
  return <Field label={label} hint={hint} htmlFor={id}>{input}</Field>;
}

export function Tabs<T extends string>({ value, onChange, options, label }: { value: T; onChange: (v: T) => void; options: { value: T; label: ReactNode }[]; label: string }) {
  return (
    <div className="tabs" role="tablist" aria-label={label}>
      {options.map((o) => (
        <button key={o.value} type="button" role="tab" className="tab" aria-selected={value === o.value} onClick={() => onChange(o.value)}>
          {o.label}
        </button>
      ))}
    </div>
  );
}

export function Badge({ children, tone }: { children: ReactNode; tone?: 'accent' | 'pos' | 'warn' | 'neg' | 'info' | 'sample' }) {
  return <span className={`badge ${tone ?? ''}`}>{children}</span>;
}

export function SampleBadge({ text = 'Sample data' }: { text?: string }) {
  return <Badge tone="sample">{text}</Badge>;
}

export function Callout({ tone = 'info', title, children }: { tone?: 'info' | 'warn' | 'error' | 'success'; title?: ReactNode; children?: ReactNode }) {
  const Icon = tone === 'warn' ? AlertTriangle : tone === 'error' ? XCircle : tone === 'success' ? CheckCircle2 : Info;
  return (
    <div className={`callout ${tone}`} role={tone === 'error' ? 'alert' : undefined}>
      <Icon size={17} />
      <div>
        {title && <div style={{ fontWeight: 600 }}>{title}</div>}
        {children}
      </div>
    </div>
  );
}

export function Warnings({ items }: { items?: string[] | null }) {
  if (!items?.length) return null;
  return (
    <Callout tone="warn" title={items.length === 1 ? 'Check this' : `${items.length} things to check`}>
      <ul>{items.map((w) => <li key={w}>{w}</li>)}</ul>
    </Callout>
  );
}

export function Formula({ children }: { children: ReactNode }) {
  return <div className="formula">{children}</div>;
}

export function Disclosure({ title, children, open, icon }: { title: ReactNode; children: ReactNode; open?: boolean; icon?: ReactNode }) {
  return (
    <details className="disclosure" open={open}>
      <summary>{icon}{title}<ChevronDown size={16} className="chev" /></summary>
      <div className="body">{children}</div>
    </details>
  );
}

/** Formula explanation panel shown when Learning mode is on (Settings). */
export function LearnBox({ title, children }: { title: string; children: ReactNode }) {
  const { settings } = useSettings();
  if (!settings.learningMode) return null;
  return <Disclosure title={<span>Learn: {title}</span>} icon={<GraduationCap size={16} className="pos" />}>{children}</Disclosure>;
}

export function Skeleton({ h = 16, w = '100%' }: { h?: number; w?: number | string }) {
  return <div className="skeleton" style={{ height: h, width: w }} />;
}

export function SkeletonCards({ n = 4 }: { n?: number }) {
  return (
    <div className={`grid cols-${n}`}>
      {Array.from({ length: n }, (_, i) => (
        <div key={i} className="card"><Skeleton h={12} w="40%" /><div className="mt-sm"><Skeleton h={26} w="70%" /></div></div>
      ))}
    </div>
  );
}

/** Short heading for an error, chosen from what the message says, so people see what kind of problem it is. */
export function errorTitle(error: string): string {
  if (/not answering|still starting/i.test(error)) return 'The server is not ready yet';
  if (/went wrong on our side/i.test(error)) return 'Something went wrong on our side';
  if (/inputs need attention/i.test(error)) return 'Check your inputs';
  if (/too large/i.test(error)) return 'That is too large';
  if (/too many/i.test(error)) return 'Slow down for a moment';
  if (/did not answer within/i.test(error)) return 'This is taking too long';
  return 'That did not work';
}

export function ErrorBox({ error, onRetry }: { error: string; onRetry?: () => void }) {
  const [copied, setCopied] = useState(false);
  const details = problemLog.get(error);
  const copy = async () => {
    try {
      await navigator.clipboard.writeText(`${error}\n\n${details ?? ''}\nPage: ${window.location.pathname}`.trim());
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch { /* clipboard blocked: the details stay visible below */ }
  };
  return (
    <Callout tone="error" title={errorTitle(error)}>
      <div>{error}</div>
      <div className="row mt-sm" style={{ gap: 8, flexWrap: 'wrap' }}>
        {onRetry && <button className="btn sm" onClick={onRetry}>Retry</button>}
        {details && <button className="btn sm ghost" onClick={copy}><Copy size={14} />{copied ? 'Copied' : 'Copy details'}</button>}
      </div>
      {details && <details className="faint" style={{ fontSize: 12, marginTop: 6 }}><summary>Technical details</summary><pre style={{ whiteSpace: 'pre-wrap', margin: '4px 0 0' }}>{details}</pre></details>}
    </Callout>
  );
}

const READING_TONE = { strong: 'pos', good: 'accent', watch: 'warn', concern: 'neg', info: 'info' } as const;

/** "In plain English": what a page's result means, wording only: the numbers come from the engines. */
export function ReadingCard({ reading, title = 'In plain English' }: { reading: Reading | null | undefined; title?: string }) {
  if (!reading) return null;
  return (
    <Card title={title} subtitle="A reading of the figures below, using stated rules of thumb"
      actions={<Badge tone={READING_TONE[reading.level]}>{LEVEL_LABEL[reading.level]}</Badge>}>
      <div className={`insight ${reading.level}`} style={{ marginTop: 0 }}>
        <b style={{ fontSize: 14 }}>{reading.headline}</b>
        <ul className="summary-list">{reading.points.map((p) => <li key={p}>{p}</li>)}</ul>
        {reading.caution && <p className="faint" style={{ fontSize: 12 }}><b>Watch out:</b> {reading.caution}</p>}
      </div>
    </Card>
  );
}

/** A collapsible block for a page's inputs, so the results can come first. Closed by default on small
 * screens is handled by the caller via `open`. The summary line shows the current key settings. */
export function Setup({ title, summary, open, children }: { title: ReactNode; summary?: ReactNode; open?: boolean; children: ReactNode }) {
  return (
    <details className="setup card" open={open}>
      <summary>
        <span className="setup-title">{title}</span>
        {summary && <span className="setup-summary faint">{summary}</span>}
        <ChevronDown size={16} className="chev" />
      </summary>
      <div className="setup-body">{children}</div>
    </details>
  );
}

export function EmptyState({ icon, title, children, action }: { icon: ReactNode; title: string; children?: ReactNode; action?: ReactNode }) {
  return (
    <div className="empty">
      <div className="icon-ring">{icon}</div>
      <h3>{title}</h3>
      <div style={{ maxWidth: 520, margin: '0 auto' }}>{children}</div>
      {action && <div className="mt">{action}</div>}
    </div>
  );
}

export function UnderDevelopment({ title, phase, summary, planned, available }: {
  title: string; phase: string; summary: string; planned: string[]; available?: { to: string; label: string }[];
}) {
  return (
    <div className="page">
      <PageHeader title={title} badge={<Badge tone="warn">Under development · {phase}</Badge>} subtitle={summary} />
      <div className="grid cols-2">
        <Card title="Planned for this module" subtitle="Not implemented yet. Nothing on this page is a working calculation.">
          <ul style={{ margin: 0, paddingLeft: 18, display: 'grid', gap: 6 }}>{planned.map((p) => <li key={p}>{p}</li>)}</ul>
        </Card>
        <Card title="What you can use today">
          <EmptyState icon={<Construction size={22} />} title="This module is being built">
            Related features that already work:
          </EmptyState>
          <div className="row" style={{ justifyContent: 'center' }}>
            {available?.map((a) => <Link key={a.to} className="btn sm" to={a.to}>{a.label}</Link>)}
          </div>
        </Card>
      </div>
    </div>
  );
}

/** Renders `render()` again only when one of `deps` changes (compared with Object.is). Wrap charts and
 * large result tables in it so typing in an input does not redraw them before the new result arrives. */
export const Stable = memo(
  function Stable({ render }: { deps: readonly unknown[]; render: () => ReactNode }) { return <>{render()}</>; },
  (a, b) => a.deps.length === b.deps.length && a.deps.every((d, i) => Object.is(d, b.deps[i])),
);
