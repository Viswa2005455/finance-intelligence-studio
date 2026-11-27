import { useState } from 'react';
import { Badge, Callout, Card, Field, Kpi, NumberField, PageHeader, Tabs } from '../components/ui';
import { fmtMoney, fmtNum } from '../lib/format';
import { ageReceivables, BUCKETS, breakEven, cashFreed, checkGstin, hireCost, loanPlan, monthlySavingFor, priceFor } from '../lib/quickCalcs';
import { load, save } from '../lib/storage';
import { useSettings } from '../lib/settings';

type Tab = 'loan' | 'goal' | 'price' | 'hire' | 'breakeven' | 'wc' | 'gstin' | 'ageing';
const TABS: { value: Tab; label: string }[] = [
  { value: 'loan', label: 'Loan & prepayment' }, { value: 'goal', label: 'Savings goal' }, { value: 'price', label: 'Pricing' }, { value: 'hire', label: 'Cost of a hire' },
  { value: 'breakeven', label: 'Break-even' }, { value: 'wc', label: 'Working-capital what-if' }, { value: 'gstin', label: 'GSTIN check' }, { value: 'ageing', label: 'Receivables ageing' },
];

/** Small calculators for everyday questions. Every rate is typed in by you; nothing assumes a tax rule. */
export function Calculators() {
  const [tab, setTab] = useState<Tab>(() => load<Tab>('fis.calc.tab', 'loan'));
  return (
    <div className="page">
      <PageHeader title="Calculators" subtitle="Quick answers to everyday money questions. Every rate is something you type; nothing here assumes a tax rule." badge={<Badge tone="accent">Quick tools</Badge>} />
      <Tabs label="Calculator" value={tab} onChange={(t) => { setTab(t); save('fis.calc.tab', t); }} options={TABS} />
      <div className="mt">
        {tab === 'loan' && <LoanTool />}
        {tab === 'goal' && <GoalTool />}
        {tab === 'price' && <PriceTool />}
        {tab === 'hire' && <HireTool />}
        {tab === 'breakeven' && <BreakEvenTool />}
        {tab === 'wc' && <WorkingCapitalTool />}
        {tab === 'gstin' && <GstinTool />}
        {tab === 'ageing' && <AgeingTool />}
      </div>
    </div>
  );
}

const n = (v: number | null) => v ?? 0;

function LoanTool() {
  const cur = useSettings().settings.currency;
  const [p, setP] = useState<number | null>(5_000_000);
  const [rate, setRate] = useState<number | null>(9);
  const [years, setYears] = useState<number | null>(20);
  const [extra, setExtra] = useState<number | null>(5000);
  const [lump, setLump] = useState<number | null>(0);
  const [lumpAt, setLumpAt] = useState<number | null>(12);
  const ok = n(p) > 0 && n(years) > 0 && n(rate) >= 0;
  const r = ok ? loanPlan({ principal: n(p), annualRatePct: n(rate), years: n(years), extraMonthly: n(extra), lumpSum: n(lump), lumpAtMonth: n(lumpAt) }) : null;
  return (
    <div className="stack">
      <Card title="Loan" subtitle="Monthly instalments, with optional extra payments">
        <div className="grid cols-3">
          <NumberField label="Amount borrowed" value={p} onChange={setP} min={0} />
          <NumberField label="Interest a year (%)" value={rate} onChange={setRate} min={0} max={100} />
          <NumberField label="Term (years)" value={years} onChange={setYears} min={1} max={40} />
          <NumberField label="Extra every month" value={extra} onChange={setExtra} min={0} />
          <NumberField label="One-off extra payment" value={lump} onChange={setLump} min={0} />
          <NumberField label="…paid in month number" value={lumpAt} onChange={setLumpAt} min={1} />
        </div>
      </Card>
      {r && <>
        <div className="grid cols-4">
          <Kpi label="Monthly instalment" value={fmtMoney(r.emi, cur)} />
          <Kpi label="Total interest" value={fmtMoney(r.totalInterest, cur)} />
          <Kpi label="Interest saved" value={fmtMoney(r.interestSaved, cur)} deltaTone={r.interestSaved > 0 ? 'pos' : 'muted'} delta={r.interestSaved > 0 ? 'compared with paying only the instalment' : undefined} />
          <Kpi label="Paid off" value={`${Math.floor(r.months / 12)} y ${r.months % 12} m`} delta={r.monthsSaved > 0 ? `${r.monthsSaved} months sooner` : undefined} deltaTone="pos" />
        </div>
        <Card title="Year by year" flush>
          <div className="table-wrap" tabIndex={0} style={{ border: 0 }}>
            <table className="data"><thead><tr><th>Year</th><th className="r">Interest</th><th className="r">Principal repaid</th><th className="r">Balance at year end</th></tr></thead>
              <tbody>{r.yearly.map((y) => <tr key={y.year}><td>{y.year}</td><td className="r">{fmtNum(y.interest, 0)}</td><td className="r">{fmtNum(y.principal, 0)}</td><td className="r">{fmtNum(y.balance, 0)}</td></tr>)}</tbody></table>
          </div>
        </Card>
        <Callout tone="info">Interest is charged monthly on the balance left. Check your lender's terms: some charge a fee for prepaying, and some apply extra payments to the next instalments instead of the principal.</Callout>
      </>}
    </div>
  );
}

function GoalTool() {
  const cur = useSettings().settings.currency;
  const [target, setTarget] = useState<number | null>(5_000_000);
  const [start, setStart] = useState<number | null>(0);
  const [years, setYears] = useState<number | null>(8);
  const [ret, setRet] = useState<number | null>(10);
  const valid = n(target) > 0 && n(years) > 0;
  const paths = [['If returns disappoint', n(ret) - 3], ['Your expected return', n(ret)], ['If returns beat it', n(ret) + 3]] as const;
  return (
    <div className="stack">
      <Card title="Savings goal" subtitle="How much to put away each month">
        <div className="grid cols-4">
          <NumberField label="Goal amount" value={target} onChange={setTarget} min={0} />
          <NumberField label="Already saved" value={start} onChange={setStart} min={0} />
          <NumberField label="Years to go" value={years} onChange={setYears} min={1} max={60} />
          <NumberField label="Return a year (%)" value={ret} onChange={setRet} min={0} max={50} />
        </div>
      </Card>
      {valid && <div className="grid cols-3">{paths.map(([label, r]) => <Kpi key={label} label={`${label} (${fmtNum(Math.max(0, r), 1)}%)`} value={`${fmtMoney(monthlySavingFor(n(target), n(start), n(years), Math.max(0, r)), cur)} a month`} />)}</div>}
      <Callout tone="info">Returns are not guaranteed and inflation lowers what the goal will buy. The three rows show how much the answer depends on the return you assume.</Callout>
    </div>
  );
}

function PriceTool() {
  const cur = useSettings().settings.currency;
  const [cost, setCost] = useState<number | null>(60);
  const [margin, setMargin] = useState<number | null>(25);
  const [disc, setDisc] = useState<number | null>(10);
  const [fee, setFee] = useState<number | null>(2);
  const [gst, setGst] = useState<number | null>(18);
  const r = priceFor({ unitCost: n(cost), targetMarginPct: n(margin), discountPct: n(disc), feePct: n(fee), gstPct: n(gst) });
  return (
    <div className="stack">
      <Card title="Price from a target margin" subtitle="Work backwards from the profit you want, after discounts and payment fees">
        <div className="grid cols-3">
          <NumberField label="Cost of one unit" value={cost} onChange={setCost} min={0} />
          <NumberField label="Margin you want (% of money kept)" value={margin} onChange={setMargin} min={0} max={99} />
          <NumberField label="Typical discount (%)" value={disc} onChange={setDisc} min={0} max={99} />
          <NumberField label="Payment fee (%)" value={fee} onChange={setFee} min={0} max={50} />
          <NumberField label="Tax added on top (%)" value={gst} onChange={setGst} min={0} max={100} hint="Type the rate that applies to your product." />
        </div>
      </Card>
      {r ? <div className="grid cols-4">
        <Kpi label="List price (before tax)" value={fmtMoney(r.listPrice, cur, 2)} />
        <Kpi label="Customer pays" value={fmtMoney(r.customerPays, cur, 2)} />
        <Kpi label="You keep per unit" value={fmtMoney(r.received, cur, 2)} />
        <Kpi label="Profit per unit" value={fmtMoney(r.profitPerUnit, cur, 2)} delta={`${fmtNum(r.marginPct, 1)}% margin`} deltaTone="pos" />
      </div> : <Callout tone="warn">These inputs cannot give a price: the margin, discount and fee together leave nothing.</Callout>}
    </div>
  );
}

function HireTool() {
  const cur = useSettings().settings.currency;
  const [sal, setSal] = useState<number | null>(1_200_000);
  const [basic, setBasic] = useState<number | null>(50);
  const [pf, setPf] = useState<number | null>(12);
  const [bonus, setBonus] = useState<number | null>(50_000);
  const [kit, setKit] = useState<number | null>(80_000);
  const [oh, setOh] = useState<number | null>(10);
  const h = hireCost({ annualSalary: n(sal), basicSharePct: n(basic), employerPfPct: n(pf), bonus: n(bonus), oneOffEquipment: n(kit), overheadPct: n(oh) });
  return (
    <div className="stack">
      <Card title="True cost of one hire" subtitle="Salary is only part of it">
        <div className="grid cols-3">
          <NumberField label="Yearly salary" value={sal} onChange={setSal} min={0} />
          <NumberField label="Basic pay as % of salary" value={basic} onChange={setBasic} min={0} max={100} />
          <NumberField label="Employer provident fund (% of basic)" value={pf} onChange={setPf} min={0} max={100} hint="Use the rate and any wage cap that apply to you." />
          <NumberField label="Yearly bonus" value={bonus} onChange={setBonus} min={0} />
          <NumberField label="Laptop, desk, one-off set-up" value={kit} onChange={setKit} min={0} />
          <NumberField label="Overheads (% of salary)" value={oh} onChange={setOh} min={0} max={200} hint="Space, software, insurance, training." />
        </div>
      </Card>
      <div className="grid cols-4">
        <Kpi label="Yearly cost, first year" value={fmtMoney(h.yearOne, cur)} />
        <Kpi label="Yearly cost after that" value={fmtMoney(h.ongoing, cur)} />
        <Kpi label="Per month" value={fmtMoney(h.perMonth, cur)} />
        <Kpi label="Times the salary" value={`${fmtNum(h.multiple, 2)}x`} />
      </div>
    </div>
  );
}

function BreakEvenTool() {
  const cur = useSettings().settings.currency;
  const [price, setPrice] = useState<number | null>(100);
  const [vc, setVc] = useState<number | null>(60);
  const [fc, setFc] = useState<number | null>(200_000);
  const [exp, setExp] = useState<number | null>(8000);
  const b = breakEven(n(price), n(vc), n(fc), n(exp));
  return (
    <div className="stack">
      <Card title="Break-even" subtitle="How much must you sell before you make a profit?">
        <div className="grid cols-4">
          <NumberField label="Selling price per unit" value={price} onChange={setPrice} min={0} />
          <NumberField label="Variable cost per unit" value={vc} onChange={setVc} min={0} />
          <NumberField label="Fixed costs for the period" value={fc} onChange={setFc} min={0} />
          <NumberField label="Units you expect to sell" value={exp} onChange={setExp} min={0} />
        </div>
      </Card>
      {b ? <div className="grid cols-4">
        <Kpi label="Break-even units" value={fmtNum(Math.ceil(b.units), 0)} />
        <Kpi label="Break-even sales" value={fmtMoney(b.revenue, cur)} />
        <Kpi label="Margin of safety" value={b.safetyPct === null ? '—' : `${fmtNum(b.safetyPct, 1)}%`} delta={b.safetyPct !== null && b.safetyPct < 0 ? 'Below break-even' : 'Sales can fall this far'} deltaTone={b.safetyPct !== null && b.safetyPct < 0 ? 'neg' : 'pos'} />
        <Kpi label="Profit at your expected sales" value={fmtMoney(b.profitAtExpected, cur)} deltaTone={b.profitAtExpected < 0 ? 'neg' : 'pos'} />
      </div> : <Callout tone="warn">The price must be higher than the variable cost, or no amount of sales covers the fixed costs.</Callout>}
    </div>
  );
}

function WorkingCapitalTool() {
  const cur = useSettings().settings.currency;
  const [rev, setRev] = useState<number | null>(60_000_000);
  const [cogs, setCogs] = useState<number | null>(40_000_000);
  const [dso, setDso] = useState<number | null>(5);
  const [dio, setDio] = useState<number | null>(5);
  const [dpo, setDpo] = useState<number | null>(5);
  const a = cashFreed(n(rev), n(dso)), b = cashFreed(n(cogs), n(dio)), c = cashFreed(n(cogs), n(dpo));
  return (
    <div className="stack">
      <Card title="Working-capital what-if" subtitle="How much cash is freed if customers pay faster, stock moves quicker or you pay suppliers later?">
        <div className="grid cols-3">
          <NumberField label="Yearly sales" value={rev} onChange={setRev} min={0} />
          <NumberField label="Yearly cost of sales" value={cogs} onChange={setCogs} min={0} />
          <span />
          <NumberField label="Customers pay this many days sooner" value={dso} onChange={setDso} min={0} />
          <NumberField label="Stock held this many days less" value={dio} onChange={setDio} min={0} />
          <NumberField label="You pay suppliers this many days later" value={dpo} onChange={setDpo} min={0} />
        </div>
      </Card>
      <div className="grid cols-4">
        <Kpi label="From faster collection" value={fmtMoney(a, cur)} />
        <Kpi label="From less stock" value={fmtMoney(b, cur)} />
        <Kpi label="From slower payment" value={fmtMoney(c, cur)} />
        <Kpi label="Cash freed in total" value={fmtMoney(a + b + c, cur)} deltaTone="pos" delta="a one-off release, not a yearly gain" />
      </div>
      <Callout tone="info">Paying suppliers later can cost you early-payment discounts or goodwill, and pushing customers to pay faster can cost sales. Weigh those before acting.</Callout>
    </div>
  );
}

function GstinTool() {
  const [v, setV] = useState('27AAPFU0939F1ZV');
  const r = v.trim() ? checkGstin(v) : null;
  return (
    <div className="stack">
      <Card title="GSTIN check" subtitle="Checks the layout, the state code and the final check character. It cannot tell you whether the number is registered or active.">
        <Field label="GSTIN"><input className="input" value={v} onChange={(e) => setV(e.target.value)} maxLength={20} spellCheck={false} /></Field>
      </Card>
      {r && (r.ok
        ? <Callout tone="success" title="This number is well formed">Its layout and check character are correct. Confirm on the GST portal that it is registered and active before relying on it.</Callout>
        : <Callout tone="warn" title="This number has a problem"><ul className="summary-list">{r.problems.map((p) => <li key={p}>{p}</li>)}</ul></Callout>)}
    </div>
  );
}

const SAMPLE_AGEING = 'Asha Traders, 2026-11-20, 10,000\nBharat Co, 2026-09-15, 50,000\nBharat Co, 2026-10-25, 5,000\nCity Ltd, 20-08-2026, 7,000';

function AgeingTool() {
  const cur = useSettings().settings.currency;
  const [text, setText] = useState(() => load<string>('fis.calc.ageing', SAMPLE_AGEING));
  const [asOf, setAsOf] = useState(() => new Date().toISOString().slice(0, 10));
  const a = ageReceivables(text, new Date(`${asOf}T00:00:00`));
  return (
    <div className="stack">
      <Card title="Receivables ageing" subtitle="One line per unpaid invoice: customer, invoice date, amount. Days are counted from the invoice date.">
        <div className="grid cols-2">
          <Field label="Unpaid invoices"><textarea className="input" rows={8} value={text} onChange={(e) => { setText(e.target.value); save('fis.calc.ageing', e.target.value); }} spellCheck={false} /></Field>
          <Field label="As of"><input className="input" type="date" value={asOf} onChange={(e) => e.target.value && setAsOf(e.target.value)} /></Field>
        </div>
      </Card>
      {a.rows.length > 0 && <>
        <div className="grid cols-4">{BUCKETS.map((b, i) => <Kpi key={b} label={b} value={fmtMoney(a.totals[i], cur)} deltaTone={i >= 2 ? 'neg' : 'muted'} delta={a.total ? `${fmtNum((a.totals[i] / a.total) * 100, 0)}% of the total` : undefined} />)}</div>
        <Card title="Chase in this order" subtitle="Oldest unpaid invoice first">
          <div className="table-wrap" tabIndex={0} style={{ border: 0 }}>
            <table className="data"><thead><tr><th>Customer</th><th className="r">Owes</th><th className="r">Oldest invoice (days)</th></tr></thead>
              <tbody>{a.byWho.map((w) => <tr key={w.who}><td>{w.who}</td><td className="r">{fmtNum(w.total, 0)}</td><td className="r">{w.oldest}</td></tr>)}</tbody></table>
          </div>
        </Card>
      </>}
      {a.skipped.length > 0 && <Callout tone="warn" title={`${a.skipped.length} line(s) could not be read`}><ul className="summary-list">{a.skipped.slice(0, 5).map((s) => <li key={s}><code>{s}</code></li>)}</ul>Use the form: customer, 2026-11-20, 10000.</Callout>}
    </div>
  );
}
