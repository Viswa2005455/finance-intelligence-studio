import { useEffect, useState } from 'react';
import { Badge, Callout, Card, Field, Kpi, NumberField, PageHeader, Tabs } from '../components/ui';
import { fmtMoney, fmtNum } from '../lib/format';
import { concentration, depreciation, leaseVsBuy, loanCost, whyDiffers } from '../lib/quickCalcs2';
import { ageReceivables, BUCKETS, breakEven, cashFreed, checkGstin, hireCost, loanPlan, monthlySavingFor, priceFor } from '../lib/quickCalcs';
import { loadRaw, save } from '../lib/storage';
import { useSettings } from '../lib/settings';

type Tab = 'loans' | 'depr' | 'lease' | 'conc' | 'differ' | 'loan' | 'goal' | 'price' | 'hire' | 'breakeven' | 'wc' | 'gstin' | 'ageing';
const TABS: { value: Tab; label: string }[] = [
  { value: 'loan', label: 'Loan & prepayment' }, { value: 'goal', label: 'Savings goal' }, { value: 'price', label: 'Pricing' }, { value: 'hire', label: 'Cost of a hire' },
  { value: 'loans', label: 'Compare two loans' }, { value: 'depr', label: 'Depreciation' }, { value: 'lease', label: 'Lease or buy' }, { value: 'conc', label: 'Customer concentration' }, { value: 'differ', label: 'Why does my number differ?' },
  { value: 'breakeven', label: 'Break-even' }, { value: 'wc', label: 'Working-capital what-if' }, { value: 'gstin', label: 'GSTIN check' }, { value: 'ageing', label: 'Receivables ageing' },
];

/** Small calculators for everyday questions. Every rate is typed in by you; nothing assumes a tax rule. */
export function Calculators() {
  const [tab, setTab] = useState<Tab>(() => loadRaw<Tab>('fis.calc.tab', 'loan'));
  return (
    <div className="page">
      <PageHeader title="Calculators" subtitle="Quick answers to everyday money questions. Every rate is something you type; nothing here assumes a tax rule." badge={<Badge tone="accent">Quick tools</Badge>} />
      <div className="row" style={{ justifyContent: 'flex-end', marginBottom: 8 }}>
        <button className="btn sm ghost" onClick={() => { if (window.confirm('Put every calculator back to its example numbers?')) { Object.keys(localStorage).filter((k) => k.startsWith('fis.calc.') && k !== 'fis.calc.tab').forEach((k) => localStorage.removeItem(k)); window.location.reload(); } }}>Reset all to examples</button>
      </div>
      <Tabs label="Calculator" value={tab} onChange={(t) => { setTab(t); save('fis.calc.tab', t); }} options={TABS} />
      <div className="mt">
        {tab === 'loan' && <LoanTool />}
        {tab === 'loans' && <LoanCompareTool />}
        {tab === 'depr' && <DepreciationTool />}
        {tab === 'lease' && <LeaseTool />}
        {tab === 'conc' && <ConcentrationTool />}
        {tab === 'differ' && <DifferTool />}
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

/** State that is remembered in this browser, so a calculator comes back as you left it. */
function usePersisted<T>(key: string, initial: T): [T, (v: T) => void] {
  const k = `fis.calc.${key}`;
  const [v, setV] = useState<T>(() => loadRaw<T>(k, initial));
  useEffect(() => { save(k, v); }, [k, v]);
  return [v, setV];
}

function LoanTool() {
  const cur = useSettings().settings.currency;
  const [p, setP] = usePersisted<number | null>('loan.p', 5_000_000);
  const [rate, setRate] = usePersisted<number | null>('loan.rate', 9);
  const [years, setYears] = usePersisted<number | null>('loan.years', 20);
  const [extra, setExtra] = usePersisted<number | null>('loan.extra', 5000);
  const [lump, setLump] = usePersisted<number | null>('loan.lump', 0);
  const [lumpAt, setLumpAt] = usePersisted<number | null>('loan.lumpAt', 12);
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
  const [target, setTarget] = usePersisted<number | null>('goal.target', 5_000_000);
  const [start, setStart] = usePersisted<number | null>('goal.start', 0);
  const [years, setYears] = usePersisted<number | null>('goal.years', 8);
  const [ret, setRet] = usePersisted<number | null>('goal.ret', 10);
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
  const [cost, setCost] = usePersisted<number | null>('price.cost', 60);
  const [margin, setMargin] = usePersisted<number | null>('price.margin', 25);
  const [disc, setDisc] = usePersisted<number | null>('price.disc', 10);
  const [fee, setFee] = usePersisted<number | null>('price.fee', 2);
  const [gst, setGst] = usePersisted<number | null>('price.gst', 18);
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
  const [sal, setSal] = usePersisted<number | null>('hire.sal', 1_200_000);
  const [basic, setBasic] = usePersisted<number | null>('hire.basic', 50);
  const [pf, setPf] = usePersisted<number | null>('hire.pf', 12);
  const [bonus, setBonus] = usePersisted<number | null>('hire.bonus', 50_000);
  const [kit, setKit] = usePersisted<number | null>('hire.kit', 80_000);
  const [oh, setOh] = usePersisted<number | null>('hire.oh', 10);
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
  const [price, setPrice] = usePersisted<number | null>('breakeven.price', 100);
  const [vc, setVc] = usePersisted<number | null>('breakeven.vc', 60);
  const [fc, setFc] = usePersisted<number | null>('breakeven.fc', 200_000);
  const [exp, setExp] = usePersisted<number | null>('breakeven.exp', 8000);
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
      {b && <BreakEvenChart price={n(price)} vc={n(vc)} fc={n(fc)} be={b.units} expected={n(exp)} />}
    </div>
  );
}

function WorkingCapitalTool() {
  const cur = useSettings().settings.currency;
  const [rev, setRev] = usePersisted<number | null>('workingcapital.rev', 60_000_000);
  const [cogs, setCogs] = usePersisted<number | null>('workingcapital.cogs', 40_000_000);
  const [dso, setDso] = usePersisted<number | null>('workingcapital.dso', 5);
  const [dio, setDio] = usePersisted<number | null>('workingcapital.dio', 5);
  const [dpo, setDpo] = usePersisted<number | null>('workingcapital.dpo', 5);
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
  const [text, setText] = useState(() => loadRaw<string>('fis.calc.ageing', SAMPLE_AGEING));
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

function LoanCompareTool() {
  const cur = useSettings().settings.currency;
  const [amount, setAmount] = usePersisted<number | null>('loans.amount', 2_000_000);
  const [years, setYears] = usePersisted<number | null>('loans.years', 5);
  const [ra, setRa] = usePersisted<number | null>('loans.ra', 10.5);
  const [fa, setFa] = usePersisted<number | null>('loans.fa', 2);
  const [rb, setRb] = usePersisted<number | null>('loans.rb', 11);
  const [fb, setFb] = usePersisted<number | null>('loans.fb', 0);
  const a = loanCost({ amount: n(amount), annualRatePct: n(ra), years: n(years), feePct: n(fa) });
  const b = loanCost({ amount: n(amount), annualRatePct: n(rb), years: n(years), feePct: n(fb) });
  const better = a.total < b.total ? 'A' : b.total < a.total ? 'B' : null;
  return (
    <div className="stack">
      <Card title="Compare two loan offers" subtitle="The lower rate is not always the cheaper loan once the fee is added">
        <div className="grid cols-3">
          <NumberField label="Amount" value={amount} onChange={setAmount} min={0} />
          <NumberField label="Term (years)" value={years} onChange={setYears} min={1} max={40} />
          <span />
          <NumberField label="Offer A: interest a year (%)" value={ra} onChange={setRa} min={0} max={100} />
          <NumberField label="Offer A: fee (% of amount)" value={fa} onChange={setFa} min={0} max={20} />
          <span />
          <NumberField label="Offer B: interest a year (%)" value={rb} onChange={setRb} min={0} max={100} />
          <NumberField label="Offer B: fee (% of amount)" value={fb} onChange={setFb} min={0} max={20} />
        </div>
      </Card>
      <div className="grid cols-2">
        {([['A', a], ['B', b]] as const).map(([name, r]) => (
          <Card key={name} title={`Offer ${name}`} actions={better === name ? <Badge tone="pos">Cheaper</Badge> : undefined}>
            <div className="metric-row"><span>Monthly instalment</span><span className="v">{fmtMoney(r.emi, cur)}</span></div>
            <div className="metric-row"><span>Interest over the term</span><span className="v">{fmtMoney(r.interest, cur)}</span></div>
            <div className="metric-row"><span>Fee</span><span className="v">{fmtMoney(r.fee, cur)}</span></div>
            <div className="metric-row"><span><b>Total cost of borrowing</b></span><span className="v">{fmtMoney(r.total, cur)}</span></div>
          </Card>
        ))}
      </div>
      {better && <Callout tone="info">Offer {better} costs {fmtMoney(Math.abs(a.total - b.total), cur)} less over the whole term. This ignores the time value of money and any insurance or other charges, so ask each lender for the full cost.</Callout>}
    </div>
  );
}

function DepreciationTool() {
  const cur = useSettings().settings.currency;
  const [cost, setCost] = usePersisted<number | null>('depr.cost', 1_000_000);
  const [scrap, setScrap] = usePersisted<number | null>('depr.scrap', 100_000);
  const [life, setLife] = usePersisted<number | null>('depr.life', 5);
  const [rate, setRate] = usePersisted<number | null>('depr.rate', 30);
  const [method, setMethod] = usePersisted<'straight' | 'reducing'>('depr.method', 'straight');
  const rows = depreciation(n(cost), n(scrap), n(life), method, n(rate));
  return (
    <div className="stack">
      <Card title="Depreciation schedule" subtitle="Type the life or the rate that applies to your asset; nothing is assumed">
        <div className="grid cols-3">
          <NumberField label="Cost of the asset" value={cost} onChange={setCost} min={0} />
          <NumberField label="Value left at the end (scrap)" value={scrap} onChange={setScrap} min={0} />
          <NumberField label="Life (years)" value={life} onChange={setLife} min={1} max={60} />
          <Field label="Method"><Tabs label="Method" value={method} onChange={setMethod} options={[{ value: 'straight', label: 'Straight line' }, { value: 'reducing', label: 'Reducing balance' }]} /></Field>
          {method === 'reducing' && <NumberField label="Rate a year (%)" value={rate} onChange={setRate} min={0} max={100} />}
        </div>
      </Card>
      <Card title="Schedule" flush>
        <div className="table-wrap" tabIndex={0} style={{ border: 0 }}>
          <table className="data"><thead><tr><th>Year</th><th className="r">Charge</th><th className="r">Book value at year end</th></tr></thead>
            <tbody>{rows.map((r) => <tr key={r.year}><td>{r.year}</td><td className="r">{fmtMoney(r.charge, cur)}</td><td className="r">{fmtMoney(r.bookValue, cur)}</td></tr>)}</tbody></table>
        </div>
      </Card>
    </div>
  );
}

function LeaseTool() {
  const cur = useSettings().settings.currency;
  const [price, setPrice] = usePersisted<number | null>('lease.price', 1_000_000);
  const [resale, setResale] = usePersisted<number | null>('lease.resale', 300_000);
  const [years, setYears] = usePersisted<number | null>('lease.years', 4);
  const [maint, setMaint] = usePersisted<number | null>('lease.maint', 30_000);
  const [lease, setLease] = usePersisted<number | null>('lease.lease', 280_000);
  const [disc, setDisc] = usePersisted<number | null>('lease.disc', 10);
  const r = leaseVsBuy({ price: n(price), resale: n(resale), years: Math.max(1, Math.round(n(years))), maintenancePerYear: n(maint), leasePerYear: n(lease), discountPct: n(disc) });
  return (
    <div className="stack">
      <Card title="Lease or buy" subtitle="Compares the cost of each, in today's money, at the return you could earn elsewhere">
        <div className="grid cols-3">
          <NumberField label="Price to buy" value={price} onChange={setPrice} min={0} />
          <NumberField label="Resale value at the end" value={resale} onChange={setResale} min={0} />
          <NumberField label="Years you will use it" value={years} onChange={setYears} min={1} max={30} />
          <NumberField label="Upkeep each year if you own it" value={maint} onChange={setMaint} min={0} />
          <NumberField label="Lease payment each year" value={lease} onChange={setLease} min={0} />
          <NumberField label="Your discount rate (%)" value={disc} onChange={setDisc} min={0} max={100} hint="The return you could earn on the money instead." />
        </div>
      </Card>
      <div className="grid cols-3">
        <Kpi label="Cost of buying (today's money)" value={fmtMoney(r.buy, cur)} />
        <Kpi label="Cost of leasing (today's money)" value={fmtMoney(r.lease, cur)} />
        <Kpi label="Cheaper" value={r.cheaper === 'same' ? 'Equal' : r.cheaper === 'buy' ? 'Buy' : 'Lease'} delta={r.cheaper === 'same' ? undefined : `by ${fmtMoney(r.difference, cur)}`} deltaTone="pos" />
      </div>
      <Callout tone="info">Tax effects, financing charges and the value of flexibility are not included. They can change the answer, so check them with your adviser.</Callout>
    </div>
  );
}

const SAMPLE_CUSTOMERS = 'Asha Traders, 600000\nBharat Co, 200000\nCity Ltd, 100000\nDelta Stores, 100000';

function ConcentrationTool() {
  const [text, setText] = usePersisted<string>('conc.text', SAMPLE_CUSTOMERS);
  const c = concentration(text);
  const tone = c.level === 'high' ? 'warn' : c.level === 'watch' ? 'info' : 'success';
  return (
    <div className="stack">
      <Card title="Customer concentration" subtitle="One line per customer: name, sales. Repeated names are added together.">
        <Field label="Sales by customer"><textarea className="input" rows={7} value={text} onChange={(e) => setText(e.target.value)} spellCheck={false} /></Field>
      </Card>
      {c.rows.length > 0 && <>
        <div className="grid cols-4">
          <Kpi label="Biggest customer" value={`${fmtNum(c.top1, 1)}%`} />
          <Kpi label="Top 3 customers" value={`${fmtNum(c.top3, 1)}%`} />
          <Kpi label="Top 5 customers" value={`${fmtNum(c.top5, 1)}%`} />
          <Kpi label="Concentration index" value={fmtNum(c.hhi, 0)} hint="Sum of squared shares, out of 10,000. Higher means fewer customers matter more." />
        </div>
        <Callout tone={tone} title={c.level === 'high' ? 'Heavily dependent on a few customers' : c.level === 'watch' ? 'Worth watching' : 'Reasonably spread'}>
          {c.level === 'high' ? 'Losing one of your biggest customers would hurt badly. Consider widening the base and agreeing longer contracts.' : c.level === 'watch' ? 'No single customer dominates, but a few carry a lot. Keep an eye on them.' : 'No small group of customers carries most of your sales.'} These cut-offs are a rule of thumb (one customer over 30% or the top three over 60% is high), not a standard.
        </Callout>
      </>}
      {c.skipped.length > 0 && <Callout tone="warn" title={`${c.skipped.length} line(s) could not be read`}><ul className="summary-list">{c.skipped.slice(0, 5).map((x) => <li key={x}><code>{x}</code></li>)}</ul></Callout>}
    </div>
  );
}

function DifferTool() {
  const [app, setApp] = usePersisted<number | null>('differ.app', 1000);
  const [mine, setMine] = usePersisted<number | null>('differ.mine', 1048.8);
  const [disc, setDisc] = usePersisted<number | null>('differ.disc', 10);
  const r = whyDiffers(n(app), n(mine), n(disc));
  return (
    <div className="stack">
      <Card title="Why does my number differ?" subtitle="Enter this app's figure and the one from your own sheet. The usual causes are each a fixed ratio between the two.">
        <div className="grid cols-3">
          <NumberField label="The app's figure" value={app} onChange={setApp} />
          <NumberField label="Your figure" value={mine} onChange={setMine} />
          <NumberField label="Discount rate used (%)" value={disc} onChange={setDisc} min={0} max={100} hint="Only needed to test mid-year discounting." />
        </div>
      </Card>
      {Number.isFinite(r.diffPct) && <>
        <div className="grid cols-2"><Kpi label="Your figure is" value={`${fmtNum(r.diffPct, 2)}% ${r.diffPct >= 0 ? 'higher' : 'lower'}`} /><Kpi label="Ratio" value={fmtNum(r.ratio, 4)} /></div>
        {r.matches.length > 0
          ? <Callout tone="success" title="Likely cause">{r.note}<ul className="summary-list">{r.matches.map((m) => <li key={m.name}><b>{m.name}.</b> {m.why}</li>)}</ul></Callout>
          : <Callout tone="info" title="No single usual cause fits">{r.note}</Callout>}
      </>}
    </div>
  );
}

/** Sales and total cost against units sold: they cross at the break-even point. Plain SVG so it needs no chart library. */
function BreakEvenChart({ price, vc, fc, be, expected }: { price: number; vc: number; fc: number; be: number; expected: number }) {
  const maxUnits = Math.max(be * 2, expected * 1.1, 1);
  const maxY = Math.max(price * maxUnits, fc + vc * maxUnits, 1);
  const W = 560, H = 220, L = 8, R = 8, T = 10, B = 24;
  const x = (u: number) => L + (u / maxUnits) * (W - L - R);
  const y = (v: number) => H - B - (v / maxY) * (H - T - B);
  return (
    <Card title="Where sales meet cost" subtitle="Left of the crossing you lose money; right of it you make a profit">
      <svg viewBox={`0 0 ${W} ${H}`} role="img" aria-label={`Sales and total cost cross at ${Math.ceil(be)} units`} style={{ width: '100%', height: 'auto', maxHeight: 260 }}>
        <line x1={L} y1={H - B} x2={W - R} y2={H - B} stroke="var(--border-strong)" />
        <line x1={x(0)} y1={y(fc)} x2={x(maxUnits)} y2={y(fc + vc * maxUnits)} stroke="var(--negative)" strokeWidth="2.2" />
        <line x1={x(0)} y1={y(0)} x2={x(maxUnits)} y2={y(price * maxUnits)} stroke="var(--accent)" strokeWidth="2.2" />
        <line x1={x(fc ? 0 : 0)} y1={y(fc)} x2={x(maxUnits)} y2={y(fc)} stroke="var(--text-muted)" strokeDasharray="4 4" />
        <circle cx={x(be)} cy={y(be * price)} r="5" fill="var(--heading)" />
        <text x={Math.min(x(be) + 8, W - 120)} y={Math.max(y(be * price) - 8, 14)} fontSize="12" fill="var(--text)">Break-even: {Math.ceil(be).toLocaleString()} units</text>
        {expected > 0 && <line x1={x(expected)} y1={T} x2={x(expected)} y2={H - B} stroke="var(--chart-4)" strokeDasharray="3 3" />}
        <text x={L} y={H - 6} fontSize="11" fill="var(--text-muted)">0 units</text>
        <text x={W - R} y={H - 6} fontSize="11" fill="var(--text-muted)" textAnchor="end">{Math.round(maxUnits).toLocaleString()} units</text>
      </svg>
      <div className="row" style={{ gap: 16, fontSize: 12.5 }}>
        <span><b style={{ color: 'var(--accent)' }}>Line</b> sales</span><span><b style={{ color: 'var(--negative)' }}>Line</b> total cost</span><span className="faint">Dotted: fixed costs{expected > 0 ? ' · dashed vertical: your expected sales' : ''}</span>
      </div>
    </Card>
  );
}
