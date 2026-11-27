import {
  Activity, ArrowLeft, ArrowRight, BarChart3, CheckCircle2, ChevronDown, Clock, Code2, CreditCard, Download, FileSpreadsheet, FileText, Globe, Layers, LockKeyhole,
  Mail, Package, Presentation, RefreshCw, Search, ShieldCheck, ShoppingBag, Wrench, Zap, type LucideIcon,
} from 'lucide-react';
import { useEffect, useMemo, useState, type ReactNode } from 'react';
import { Link, useNavigate, useParams } from 'react-router-dom';
import { KIT_CONTENTS } from '../lib/kitContents';
import { CATEGORIES, CONTACT, SERVICES, formatINR, type CategoryId, type Service, type Tier } from '../lib/services';
import { OrderModal, ThankYou } from './ServiceOrder';

function useTitle(title: string) {
  useEffect(() => { document.title = title; window.scrollTo(0, 0); }, [title]);
}

const CAT: Record<CategoryId, { icon: LucideIcon; tone: string }> = {
  excel: { icon: FileSpreadsheet, tone: 'tone-excel' },
  powerbi: { icon: BarChart3, tone: 'tone-powerbi' },
  web: { icon: Globe, tone: 'tone-web' },
  automation: { icon: Zap, tone: 'tone-automation' },
  research: { icon: FileText, tone: 'tone-research' },
};

const KIND_ICON: Record<string, LucideIcon> = { Excel: FileSpreadsheet, Word: FileText, PowerPoint: Presentation, Website: Globe, Web: Code2, Script: Code2, Workflow: Zap, File: Package };

/** The file types a kit contains, for the little chips on each card (the how-to guide is not counted). */
function kindsOf(slug: string): string[] {
  const items = (KIT_CONTENTS[slug]?.items ?? []).filter((i) => !i.file.startsWith('00-START-HERE'));
  const label = (k: string) => (k === 'Web' || k === 'Script' || k === 'Workflow' ? 'Code' : k);
  const present = new Set(items.map((i) => label(i.kind)));
  return ['Excel', 'PowerPoint', 'Website', 'Word', 'Code'].filter((k) => present.has(k)).slice(0, 3);
}

const FAQ: { q: string; a: ReactNode }[] = [
  { q: 'How do I get my kit?', a: 'Right after you pay, a Download button appears on the confirmation page and a copy is emailed to you. It is a ZIP file: unzip it and open the file named 00-START-HERE first.' },
  { q: 'What do I need to open the files?', a: 'Excel files open in Microsoft Excel (or Google Sheets via File > Import). Guides open in Word or Google Docs. Website templates open in any browser. Nothing else to install.' },
  { q: 'Is the kit made specially for me?', a: 'The Basic package is a ready-made kit you fill in yourself, with a guide. Standard and Premium also include custom work for you, emailed within the days shown on the package.' },
  { q: 'Is my payment safe?', a: 'Payment is handled by Razorpay (UPI, cards and netbanking). Your card or UPI details never reach this website.' },
  { q: 'I need help or something is not working.', a: <>Email <a href={`mailto:${CONTACT.email}`}>{CONTACT.email}</a> with your payment reference and I will help.</> },
];

function Faq() {
  return (
    <section className="svc-faq-wrap" aria-labelledby="faq-h">
      <h2 id="faq-h" className="svc-h2">Common questions</h2>
      {FAQ.map((f) => (
        <details key={f.q} className="svc-faq">
          <summary>{f.q}<ChevronDown size={17} /></summary>
          <p>{f.a}</p>
        </details>
      ))}
    </section>
  );
}

function Shell({ children }: { children: ReactNode }) {
  return (
    <div className="svc-shell">
      <header className="svc-top">
        <Link to="/services" className="svc-brand">
          <span className="brand-mark" style={{ width: 34, height: 34, borderRadius: 10 }}><Activity size={18} strokeWidth={2.5} /></span>
          <span><b>Finlight</b><small>Ready-made kits by {CONTACT.name}</small></span>
        </Link>
        <nav className="svc-top-links">
          <a className="btn sm ghost" href={CONTACT.store} target="_blank" rel="noreferrer"><ShoppingBag size={15} />Excel templates</a>
          <a className="btn sm primary" href={`mailto:${CONTACT.email}`}><Mail size={15} />Contact</a>
        </nav>
      </header>
      <main className="svc-main">{children}</main>
      <footer className="svc-foot">
        <div className="svc-foot-grid">
          <div><b>Finlight</b><br />Ready-made finance, data and website kits by {CONTACT.name}, from ₹99. Instant download after payment; custom work available.</div>
          <div><b>Contact</b><br /><a href={`mailto:${CONTACT.email}`}>{CONTACT.email}</a></div>
          <div><b>Payments</b><br />Secure payment by Razorpay: UPI, cards and netbanking.</div>
        </div>
        <div className="faint">Prices are in Indian rupees. Kits are ready-made templates; sample data inside is only an example. Your files are used only for your project.</div>
      </footer>
    </div>
  );
}

function ServiceCard({ s }: { s: Service }) {
  const cat = CAT[s.category];
  const Icon = cat.icon;
  const kinds = kindsOf(s.slug);
  return (
    <article className={`svc-card2 ${cat.tone}`}>
      <Link className="svc-prev" to={`/services/${s.slug}`} aria-label={`${s.title}: see what is inside`} tabIndex={-1}>
        <img src={`/previews/${s.slug}.jpg`} alt={`Preview of the ${s.title} kit`} loading="lazy" width={1000} height={625} />
        <span className="svc-ico"><Icon size={18} /></span>
        <span className="svc-instant"><Zap size={12} />Instant</span>
      </Link>
      <h2><Link to={`/services/${s.slug}`}>{s.title}</Link></h2>
      <p>{s.promise}</p>
      <div className="svc-kinds">{kinds.map((k) => <span key={k} className="svc-kind">{k}</span>)}</div>
      <div className="svc-card2-foot">
        <div className="svc-from"><small>From</small><b>{formatINR(s.tiers[0].price)}</b></div>
        <div className="svc-card-actions">
          <Link className="btn sm" to={`/services/${s.slug}`}>Details</Link>
          <Link className="btn sm primary" to={`/services/${s.slug}?order=Basic`}><Download size={14} />Get kit</Link>
        </div>
      </div>
    </article>
  );
}

export function ServicesList() {
  useTitle('Ready-made finance, data and website kits from ₹99 · Finlight');
  const [cat, setCat] = useState<CategoryId | 'all'>('all');
  const [q, setQ] = useState('');
  const shown = useMemo(() => {
    const term = q.trim().toLowerCase();
    return SERVICES.filter((s) => (cat === 'all' || s.category === cat)
      && (!term || `${s.title} ${s.promise} ${s.forWho}`.toLowerCase().includes(term)));
  }, [cat, q]);
  const prices = SERVICES.flatMap((s) => s.tiers.map((t) => t.price));
  const minPrice = Math.min(...prices);
  const maxPrice = Math.max(...prices);

  return (
    <Shell>
      <section className="svc-hero2">
        <div className="svc-hero2-text">
          <span className="svc-eyebrow">Finance · Data · Websites</span>
          <h1>Ready-made kits that save you hours. <em>From {formatINR(minPrice)}.</em></h1>
          <p>Excel dashboards, Power BI starters, website templates and business documents for students, shops and small businesses. Pay once and download in seconds. Need it tailored? Add custom work.</p>
          <div className="svc-hero2-actions">
            <a className="btn primary lg" href="#all">Browse all {SERVICES.length} kits<ArrowRight size={16} /></a>
            <a className="btn lg" href={`mailto:${CONTACT.email}`}><Mail size={16} />Ask a question</a>
          </div>
          <ul className="svc-trust">
            <li><Zap size={15} />Instant download</li>
            <li><ShieldCheck size={15} />Secure Razorpay payment</li>
            <li><Layers size={15} />Excel, Word, PowerPoint &amp; web files</li>
            <li><Wrench size={15} />Custom work available</li>
          </ul>
        </div>
        <div className="svc-hero2-stats" aria-label="At a glance">
          <div><b>{SERVICES.length}</b><span>ready-made kits</span></div>
          <div><b>{formatINR(minPrice)}–{formatINR(maxPrice)}</b><span>every price listed</span></div>
          <div><b>{CATEGORIES.length}</b><span>categories</span></div>
        </div>
      </section>

      <section className="svc-steps" aria-label="How it works">
        <div><span>1</span><b>Pick a kit</b><p>Browse by category or search for what you need.</p></div>
        <div><span>2</span><b>Pay securely</b><p>UPI, card or netbanking through Razorpay.</p></div>
        <div><span>3</span><b>Download instantly</b><p>The kit appears on screen and arrives by email.</p></div>
      </section>

      <section id="all" className="svc-filters">
        <div className="svc-search">
          <Search size={16} />
          <input className="input" placeholder="Search kits, e.g. dashboard, website, GST" value={q} onChange={(e) => setQ(e.target.value)} aria-label="Search kits" />
        </div>
        <div className="tabs" role="tablist" aria-label="Category">
          <button className="tab" role="tab" aria-selected={cat === 'all'} onClick={() => setCat('all')}>All ({SERVICES.length})</button>
          {CATEGORIES.map((c) => (
            <button key={c.id} className="tab" role="tab" aria-selected={cat === c.id} onClick={() => setCat(c.id)}>
              {c.label} ({SERVICES.filter((s) => s.category === c.id).length})
            </button>
          ))}
        </div>
      </section>

      {shown.length === 0 && <p className="muted mt">No kit matches “{q}”. Try another word, or email me what you need.</p>}
      <div className="svc-grid2">{shown.map((s) => <ServiceCard key={s.id} s={s} />)}</div>

      <Faq />
    </Shell>
  );
}

function PackageCard({ t, onOrder }: { t: Tier; onOrder: () => void }) {
  const featured = t.name === 'Standard';
  return (
    <div className={`svc-pk${featured ? ' featured' : ''}`}>
      <div className="svc-pk-head">
        <span className="svc-pk-name">{t.name}</span>
        {featured && <span className="badge pos">Most chosen</span>}
      </div>
      <div className="svc-pk-price">{formatINR(t.price)}</div>
      <ul>
        <li><Download size={15} /><span>Instant ready-made kit</span></li>
        {t.custom
          ? <>
              <li><Clock size={15} /><span>Custom work in {t.days} day{t.days > 1 ? 's' : ''}</span></li>
              <li><RefreshCw size={15} /><span>{t.revisions} revisions</span></li>
            </>
          : <li><CheckCircle2 size={15} /><span>Kit only, nothing to wait for</span></li>}
      </ul>
      {t.custom && <p className="svc-pk-note">{t.includes.replace('The instant ready-made kit, plus custom work for you: ', 'Custom work: ')}</p>}
      <button className={`btn${featured ? ' primary' : ''} svc-pk-btn`} onClick={onOrder}><CreditCard size={15} />Order {t.name} · {formatINR(t.price)}</button>
    </div>
  );
}

export function ServiceDetail() {
  const { slug } = useParams();
  const navigate = useNavigate();
  const s = SERVICES.find((x) => x.slug === slug);
  const [ordering, setOrdering] = useState<Tier | null>(null);
  useEffect(() => {
    // "Get kit" on the list page links here with ?order=<tier> to open the form straight away.
    const want = new URLSearchParams(window.location.search).get('order');
    const t = s?.tiers.find((x) => x.name === want);
    if (t) { setOrdering(t); navigate(`/services/${s!.slug}`, { replace: true }); }
  }, [s, navigate]);
  useTitle(s ? `${s.title} · ready-made kit from ${formatINR(s.tiers[0].price)}` : 'Kit not found');

  if (!s) {
    return (
      <Shell>
        <div className="card svc-detail">
          <h1>Kit not found</h1>
          <p className="muted mt-sm">That link does not exist.</p>
          <div className="mt"><Link className="btn" to="/services"><ArrowLeft size={15} />All kits</Link></div>
        </div>
      </Shell>
    );
  }
  const cat = CATEGORIES.find((c) => c.id === s.category);
  const meta = CAT[s.category];
  const Icon = meta.icon;
  const content = KIT_CONTENTS[s.slug];
  const related = SERVICES.filter((x) => x.category === s.category && x.id !== s.id).slice(0, 3);

  return (
    <Shell>
      <Link className="btn sm ghost" to="/services"><ArrowLeft size={15} />All {SERVICES.length} kits</Link>

      <section className={`svc-head ${meta.tone}`}>
        <span className="svc-ico lg"><Icon size={26} /></span>
        <div>
          <div className="row"><span className="badge accent">{cat?.label}</span><span className="svc-instant"><Zap size={12} />Instant download</span></div>
          <h1>{s.title}</h1>
          <p className="svc-lede">{s.promise}</p>
          <p className="svc-who"><b>Who it's for:</b> {s.forWho}</p>
        </div>
      </section>

      <div className="svc-cols">
        <div className="svc-left">
          <figure className="svc-hero-prev">
            <img src={`/previews/${s.slug}.jpg`} alt={`A look inside the ${s.title} kit`} width={1000} height={625} />
            <figcaption>A look inside this kit (sample data shown)</figcaption>
          </figure>

          <section className="svc-block">
            <h2 className="svc-h2">What's inside your kit</h2>
            <ul className="svc-files">
              {content?.items.map((it) => {
                const KI = KIND_ICON[it.kind] ?? Package;
                return (
                  <li key={it.file}><span className="svc-file-ico"><KI size={18} /></span><div><b>{it.file}</b><span>{it.what}</span></div></li>
                );
              })}
            </ul>
            {content?.tip && <p className="svc-tip"><CheckCircle2 size={16} /><span><b>Tip:</b> {content.tip}</span></p>}
            {s.sample && <p className="mt-sm"><a href={s.sample.url} target="_blank" rel="noreferrer">{s.sample.label} →</a></p>}
          </section>

          <section className="svc-block">
            <h2 className="svc-h2">How it works</h2>
            <ol className="svc-how">
              <li><b>Choose a package</b><span>Basic is the instant kit. Standard and Premium add custom work.</span></li>
              <li><b>Pay securely</b><span>UPI, card or netbanking via Razorpay.</span></li>
              <li><b>Download and use</b><span>The kit appears on screen and in your email. Unzip it and open 00-START-HERE.</span></li>
            </ol>
          </section>

          <section className="svc-block">
            <h2 className="svc-h2">For Standard and Premium: what I need from you</h2>
            <p className="svc-need"><CheckCircle2 size={17} /><span>{s.youSend}.</span></p>
          </section>

          <Faq />
        </div>

        <aside className="svc-right" aria-label="Choose a package">
          <h2 className="svc-h2">Choose a package</h2>
          {s.tiers.map((t) => <PackageCard key={t.name} t={t} onOrder={() => setOrdering(t)} />)}
          <p className="svc-secure"><LockKeyhole size={14} />Secure payment by Razorpay. Questions? <a href={`mailto:${CONTACT.email}`}>Email me</a>.</p>
        </aside>
      </div>

      {related.length > 0 && (
        <section className="mt">
          <h2 className="svc-h2">Related kits</h2>
          <div className="svc-grid2">{related.map((r) => <ServiceCard key={r.id} s={r} />)}</div>
        </section>
      )}
      <OrderModal service={s} tier={ordering} onClose={() => setOrdering(null)} />
    </Shell>
  );
}

export function ServiceThankYou() {
  useTitle('Order confirmation · Finlight');
  return <Shell><ThankYou /></Shell>;
}
