import { Area, AreaChart, Bar, BarChart, CartesianGrid, Cell, ReferenceLine, ResponsiveContainer, Tooltip, XAxis, YAxis } from 'recharts';
import { fmtNum, fmtPctPoints, isNum } from '../lib/format';
import { C, ChartTooltip, Legend, axisProps, gridProps } from './charts';

/** Dashboard graphics. Every figure is arithmetic on the series passed in — nothing is invented,
 * and a chart with too little data renders nothing rather than a guess. */

/** Tiny trend line for a KPI card. Decorative: the card's number and delta carry the meaning. */
export function Sparkline({ values, color = 'var(--chart-1)' }: { values: number[]; color?: string }) {
  const pts = values.filter(isNum);
  if (pts.length < 2) return null;
  const W = 100, H = 30, pad = 3;
  const min = Math.min(...pts), max = Math.max(...pts);
  const span = max - min || 1;
  const xy = pts.map((v, i) => [(i / (pts.length - 1)) * W, H - pad - ((v - min) / span) * (H - pad * 2)] as const);
  const line = xy.map(([x, y], i) => `${i ? 'L' : 'M'}${x.toFixed(1)} ${y.toFixed(1)}`).join(' ');
  const [lx, ly] = xy[xy.length - 1];
  return (
    <svg className="spark" viewBox={`0 0 ${W} ${H}`} preserveAspectRatio="none" aria-hidden="true">
      <path d={`${line} L${W} ${H} L0 ${H} Z`} fill={color} fillOpacity={0.12} />
      <path d={line} fill="none" stroke={color} strokeWidth={1.6} strokeLinejoin="round" strokeLinecap="round" vectorEffect="non-scaling-stroke" />
      <circle cx={lx} cy={ly} r={2.2} fill={color} />
    </svg>
  );
}

/** Ring gauge for a percentage that has a natural 0–100 scale (a margin, a share). */
export function Ring({ pct, label, color = 'var(--chart-1)' }: { pct: number; label: string; color?: string }) {
  const r = 30, c = 2 * Math.PI * r;
  const shown = Math.max(0, Math.min(100, pct));
  return (
    <div className="ring" role="img" aria-label={`${label}: ${fmtPctPoints(pct)}`}>
      <svg viewBox="0 0 76 76" aria-hidden="true">
        <circle cx="38" cy="38" r={r} fill="none" stroke="var(--chart-grid)" strokeWidth="7" />
        <circle className="ring-arc" cx="38" cy="38" r={r} fill="none" stroke={color} strokeWidth="7" strokeLinecap="round"
          strokeDasharray={`${(shown / 100) * c} ${c}`} transform="rotate(-90 38 38)" />
        <text x="38" y="42" textAnchor="middle" className="ring-value">{fmtPctPoints(pct)}</text>
      </svg>
      <span>{label}</span>
    </div>
  );
}

/** Two-line axis label so the five bridge steps fit a narrow card without overlapping. */
function BridgeTick({ x, y, payload }: { x?: number; y?: number; payload?: { value: string } }) {
  const lines = BRIDGE_LABELS[payload?.value ?? ''] ?? [payload?.value ?? ''];
  return (
    <text x={x} y={(y ?? 0) + 11} textAnchor="middle" fill="var(--chart-axis)" fontSize={10.5}>
      {lines.map((l, i) => <tspan key={l} x={x} dy={i ? 12 : 0}>{l}</tspan>)}
    </text>
  );
}
const BRIDGE_LABELS: Record<string, string[]> = {
  'Operating costs': ['Operating', 'costs'], 'D&A, interest, tax': ['D&A, tax,', 'interest'], 'Net income': ['Net', 'income'],
};

interface BridgeStep { name: string; base: number; amount: number; kind: 'total' | 'less' }

/** Waterfall from revenue to net income for one period. Deductions hang from the level above them. */
export function ProfitBridge({ revenue, ebitda, netIncome, format, tick = (v) => fmtNum(v, 0) }: {
  revenue: number; ebitda: number; netIncome: number; format: (v: number) => string; tick?: (v: number) => string;
}) {
  const steps: BridgeStep[] = [
    { name: 'Revenue', base: 0, amount: revenue, kind: 'total' },
    { name: 'Operating costs', base: Math.min(revenue, ebitda), amount: Math.abs(revenue - ebitda), kind: 'less' },
    { name: 'EBITDA', base: 0, amount: ebitda, kind: 'total' },
    { name: 'D&A, interest, tax', base: Math.min(ebitda, netIncome), amount: Math.abs(ebitda - netIncome), kind: 'less' },
    { name: 'Net income', base: 0, amount: netIncome, kind: 'total' },
  ];
  const fill = (s: BridgeStep) => (s.kind === 'less' ? C.neg : s.name === 'Net income' ? C.c1 : C.c2);
  return (
    <>
      <div className="chart">
        <ResponsiveContainer>
          <BarChart data={steps} margin={{ top: 8, right: 8, left: -8, bottom: 0 }}>
            <CartesianGrid {...gridProps} />
            <XAxis dataKey="name" {...axisProps} interval={0} height={38} tick={<BridgeTick />} />
            <YAxis {...axisProps} width={56} tickFormatter={tick} />
            <Tooltip cursor={{ fill: 'var(--bg-hover)' }} content={({ active, payload }) => {
              const s = payload?.[0]?.payload as BridgeStep | undefined;
              if (!active || !s) return null;
              return (
                <div className="chart-tooltip">
                  <div className="t">{s.name}</div>
                  <div className="r"><span>{s.kind === 'less' ? 'Deducted' : 'Amount'}</span><b className="num">{s.kind === 'less' ? '−' : ''}{format(s.amount)}</b></div>
                  {s.kind === 'less' && <div className="r"><span>Share of revenue</span><b className="num">{fmtPctPoints((s.amount / revenue) * 100)}</b></div>}
                </div>
              );
            }} />
            <Bar dataKey="base" stackId="b" fill="transparent" isAnimationActive={false} />
            <Bar dataKey="amount" stackId="b" radius={[4, 4, 4, 4]} maxBarSize={46}>
              {steps.map((s) => <Cell key={s.name} fill={fill(s)} />)}
            </Bar>
          </BarChart>
        </ResponsiveContainer>
      </div>
      <Legend items={[{ label: 'Level', color: 'var(--chart-2)' }, { label: 'Deduction', color: 'var(--negative)' }, { label: 'Net income', color: 'var(--chart-1)' }]} />
    </>
  );
}

/** Margin trend: each profit line as a percentage of the same period's revenue. */
export function MarginTrend({ rows }: { rows: { period: string; revenue: number; ebitda: number; net_income: number }[] }) {
  const data = rows.filter((r) => r.revenue > 0).map((r) => ({ period: r.period, ebitda: (r.ebitda / r.revenue) * 100, net: (r.net_income / r.revenue) * 100 }));
  if (!data.length) return null;
  const last = data[data.length - 1];
  return (
    <>
      <div className="rings">
        <Ring pct={last.ebitda} label={`EBITDA margin · ${last.period}`} color="var(--chart-4)" />
        <Ring pct={last.net} label={`Net margin · ${last.period}`} color="var(--chart-1)" />
      </div>
      <div className="chart short">
        <ResponsiveContainer>
          <AreaChart data={data} margin={{ top: 8, right: 8, left: -14, bottom: 0 }}>
            <defs>
              <linearGradient id="fis-grad-ebitda" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stopColor="var(--chart-4)" stopOpacity={0.28} /><stop offset="1" stopColor="var(--chart-4)" stopOpacity={0} /></linearGradient>
              <linearGradient id="fis-grad-net" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stopColor="var(--chart-1)" stopOpacity={0.3} /><stop offset="1" stopColor="var(--chart-1)" stopOpacity={0} /></linearGradient>
            </defs>
            <CartesianGrid {...gridProps} />
            <XAxis dataKey="period" {...axisProps} />
            <YAxis {...axisProps} width={50} tickFormatter={(v) => `${fmtNum(v, 0)}%`} />
            <Tooltip content={<ChartTooltip format={(v) => fmtPctPoints(v)} />} />
            <Area dataKey="ebitda" name="EBITDA margin" stroke={C.c4} strokeWidth={2} fill="url(#fis-grad-ebitda)" dot={false} />
            <Area dataKey="net" name="Net margin" stroke={C.c1} strokeWidth={2} fill="url(#fis-grad-net)" dot={false} />
          </AreaChart>
        </ResponsiveContainer>
      </div>
    </>
  );
}

/** Period-on-period growth as a heat strip, with the strongest and weakest periods called out. */
export function GrowthStrip({ rows, unit = 'month' }: { rows: { period: string; revenue: number | null }[]; unit?: 'month' | 'year' }) {
  // Growth is only shown between two adjacent periods that both have a figure; a gap is never bridged.
  const cells = rows.slice(1).flatMap((r, i) => {
    const prev = rows[i].revenue;
    return isNum(r.revenue) && isNum(prev) && prev > 0 ? [{ period: r.period, g: (r.revenue / prev - 1) * 100 }] : [];
  });
  const Unit = unit === 'month' ? 'Month' : 'Year';
  if (!cells.length) return null;
  const peak = Math.max(...cells.map((c) => Math.abs(c.g))) || 1;
  const best = cells.reduce((a, b) => (b.g > a.g ? b : a));
  const worst = cells.reduce((a, b) => (b.g < a.g ? b : a));
  const up = cells.filter((c) => c.g > 0).length;
  const avg = cells.reduce((s, c) => s + c.g, 0) / cells.length;
  return (
    <>
      <div className="heat-strip" role="list" aria-label={`Revenue growth on the ${unit} before`}>
        {cells.map((c) => (
          <div key={c.period} role="listitem" className="heat-cell" title={`${c.period}: ${fmtPctPoints(c.g)} vs the ${unit} before`}
            style={{ background: `color-mix(in srgb, var(${c.g >= 0 ? '--positive' : '--negative'}) ${Math.round(8 + 30 * (Math.abs(c.g) / peak))}%, var(--bg-sunken))` }}>
            <b className="num">{c.g >= 0 ? '+' : '−'}{Math.abs(c.g).toFixed(1)}</b>
            <span>{c.period}</span>
          </div>
        ))}
      </div>
      <div className="mt">
        <div className="metric-row"><span className="muted">{Unit}s with growth</span><span className="v">{up} of {cells.length}</span></div>
        <div className="metric-row"><span className="muted">Average growth per {unit}</span><span className={`v ${avg >= 0 ? 'pos' : 'neg'}`}>{fmtPctPoints(avg)}</span></div>
        <div className="metric-row"><span className="muted">Strongest {unit}</span><span className="v pos">{best.period} · {fmtPctPoints(best.g)}</span></div>
        <div className="metric-row"><span className="muted">Weakest {unit}</span><span className={`v ${worst.g < 0 ? 'neg' : ''}`}>{worst.period} · {fmtPctPoints(worst.g)}</span></div>
      </div>
    </>
  );
}

/** Actual minus budget for each period as diverging bars: above the line is ahead of budget. */
export function VarianceBars({ rows, format }: { rows: { period: string; budget: number; actual: number }[]; format: (v: number) => string }) {
  const data = rows.map((r) => ({ ...r, variance: r.actual - r.budget }));
  return (
    <>
      <div className="chart">
        <ResponsiveContainer>
          <BarChart data={data} margin={{ top: 8, right: 8, left: -8, bottom: 0 }}>
            <CartesianGrid {...gridProps} />
            <XAxis dataKey="period" {...axisProps} />
            <YAxis {...axisProps} width={56} tickFormatter={(v) => fmtNum(v, 0)} />
            <Tooltip cursor={{ fill: 'var(--bg-hover)' }} content={({ active, payload }) => {
              const r = payload?.[0]?.payload as (typeof data)[number] | undefined;
              if (!active || !r) return null;
              return (
                <div className="chart-tooltip">
                  <div className="t">{r.period}</div>
                  <div className="r"><span>Actual</span><b className="num">{format(r.actual)}</b></div>
                  <div className="r"><span>Budget</span><b className="num">{format(r.budget)}</b></div>
                  <div className="r"><span>Variance</span><b className={`num ${r.variance >= 0 ? 'pos' : 'neg'}`}>{r.variance >= 0 ? '+' : '−'}{format(Math.abs(r.variance))}{r.budget ? ` (${fmtPctPoints((r.variance / r.budget) * 100)})` : ''}</b></div>
                </div>
              );
            }} />
            <ReferenceLine y={0} stroke="var(--chart-axis)" />
            <Bar dataKey="variance" radius={[4, 4, 4, 4]} maxBarSize={30}>
              {data.map((r) => <Cell key={r.period} fill={r.variance >= 0 ? C.pos : C.neg} />)}
            </Bar>
          </BarChart>
        </ResponsiveContainer>
      </div>
      <Legend items={[{ label: 'Ahead of budget', color: 'var(--positive)' }, { label: 'Behind budget', color: 'var(--negative)' }]} />
    </>
  );
}
