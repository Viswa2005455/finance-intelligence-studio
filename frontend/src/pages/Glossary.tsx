import { Link } from 'react-router-dom';
import { useState } from 'react';
import { Card, EmptyState, Field, PageHeader } from '../components/ui';
import { GLOSSARY } from '../lib/glossary';
import { Search } from 'lucide-react';

/** The page where each term is used, so a definition leads somewhere useful. */
const WHERE: Record<string, [string, string]> = {
  WACC: ['/dcf', 'DCF Valuation'], DCF: ['/dcf', 'DCF Valuation'], NPV: ['/investment', 'Project Appraisal'], IRR: ['/investment', 'Project Appraisal'], MIRR: ['/investment', 'Project Appraisal'],
  FCFF: ['/dcf', 'DCF Valuation'], NOPAT: ['/dcf', 'DCF Valuation'], EBIT: ['/ratios', 'Ratio Analysis'], EBITDA: ['/ratios', 'Ratio Analysis'], ROE: ['/ratios', 'Ratio Analysis'], ROA: ['/ratios', 'Ratio Analysis'],
  ROIC: ['/ratios', 'Ratio Analysis'], DSO: ['/cash-flow', 'Cash Flow & Working Capital'], DIO: ['/cash-flow', 'Cash Flow & Working Capital'], DPO: ['/cash-flow', 'Cash Flow & Working Capital'],
  CAGR: ['/forecasting', 'Forecasting'], CapEx: ['/dcf', 'DCF Valuation'], NWC: ['/cash-flow', 'Cash Flow & Working Capital'], MAPE: ['/forecasting', 'Forecasting'],
  'terminal value': ['/dcf', 'DCF Valuation'], 'cash conversion cycle': ['/cash-flow', 'Cash Flow & Working Capital'], 'interest cover': ['/ratios', 'Ratio Analysis'], 'equity multiplier': ['/ratios', 'Ratio Analysis'],
  gearing: ['/ratios', 'Ratio Analysis'], 'current ratio': ['/ratios', 'Ratio Analysis'], 'quick ratio': ['/ratios', 'Ratio Analysis'], DuPont: ['/ratios', 'Ratio Analysis'], 'profit margin': ['/ratios', 'Ratio Analysis'],
  'asset turnover': ['/ratios', 'Ratio Analysis'], Beneish: ['/red-flags', 'Red-Flag Detector'], Altman: ['/red-flags', 'Red-Flag Detector'], Piotroski: ['/red-flags', 'Red-Flag Detector'],
  covenant: ['/ratios', 'Ratio Analysis'], materiality: ['/variance', 'Variance Analysis'],
};

export function Glossary() {
  const [q, setQ] = useState('');
  const terms = Object.keys(GLOSSARY).sort((a, b) => a.toLowerCase().localeCompare(b.toLowerCase()));
  const shown = terms.filter((t) => !q.trim() || `${t} ${GLOSSARY[t]}`.toLowerCase().includes(q.trim().toLowerCase()));
  const letters = Array.from(new Set(shown.map((t) => t[0].toUpperCase())));
  return (
    <div className="page">
      <PageHeader title="Glossary" subtitle="Plain-English meanings of the terms used across the app, and where to see each one at work." />
      <Card>
        <Field label="Search terms"><div className="row" style={{ gap: 8 }}><Search size={16} aria-hidden="true" className="faint" /><input className="input" value={q} onChange={(e) => setQ(e.target.value)} placeholder="Try WACC, margin or cash" aria-label="Search terms" /></div></Field>
      </Card>
      {!shown.length && <EmptyState icon={<Search size={22} />} title="No matching term">Try a shorter word.</EmptyState>}
      {letters.map((l) => (
        <div key={l} className="mt">
          <Card title={l}>
            <dl className="stack" style={{ margin: 0 }}>
              {shown.filter((t) => t[0].toUpperCase() === l).map((t) => (
                <div key={t}>
                  <dt style={{ fontWeight: 650 }}>{t}</dt>
                  <dd style={{ margin: '2px 0 0' }}>{GLOSSARY[t]}{WHERE[t] && <> <Link to={WHERE[t][0]}>See it in {WHERE[t][1]}</Link></>}</dd>
                </div>
              ))}
            </dl>
          </Card>
        </div>
      ))}
    </div>
  );
}
