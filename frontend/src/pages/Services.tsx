import { Activity, ArrowLeft, CheckCircle2, Clock, CreditCard, LockKeyhole, Mail, RefreshCw, Search, ShoppingBag } from 'lucide-react';
import { useEffect, useMemo, useState, type ReactNode } from 'react';
import { Link, useNavigate, useParams } from 'react-router-dom';
import { CATEGORIES, CONTACT, SERVICES, formatINR, type CategoryId, type Tier } from '../lib/services';
import { OrderModal, ThankYou } from './ServiceOrder';

function useTitle(title: string) {
  useEffect(() => { document.title = title; window.scrollTo(0, 0); }, [title]);
}

function Shell({ children }: { children: ReactNode }) {
  return (
    <div className="svc-shell">
      <header className="svc-top">
        <Link to="/services" className="svc-brand">
          <span className="brand-mark" style={{ width: 34, height: 34, borderRadius: 10 }}><Activity size={18} strokeWidth={2.5} /></span>
          <span><b>Finance Intelligence Studio</b><small>Services by {CONTACT.name}</small></span>
        </Link>
        <nav className="svc-top-links">
          <a className="btn sm ghost" href={CONTACT.store} target="_blank" rel="noreferrer"><ShoppingBag size={15} />Templates</a>
          <a className="btn sm primary" href={`mailto:${CONTACT.email}`}><Mail size={15} />Email</a>
        </nav>
      </header>
      <main className="svc-main">{children}</main>
      <footer className="svc-foot">
        <div><b>How it works.</b> Pick a package, tell me what you need and pay online (UPI, card or netbanking via Razorpay). You get a receipt by email, and I deliver the finished work to that email within the listed days. Revisions are as listed in each package.</div>
        <div><b>Your data stays private.</b> I use your files only for your project and delete them after delivery if you ask.</div>
        <div className="faint">Prices are starting prices in Indian rupees. Final price depends on the size of your data and requirements. Questions: <a href={`mailto:${CONTACT.email}`}>{CONTACT.email}</a></div>
      </footer>
    </div>
  );
}

export function ServicesList() {
  useTitle('Services · Finance Intelligence Studio');
  const [cat, setCat] = useState<CategoryId | 'all'>('all');
  const [q, setQ] = useState('');
  const shown = useMemo(() => {
    const term = q.trim().toLowerCase();
    return SERVICES.filter((s) => (cat === 'all' || s.category === cat)
      && (!term || `${s.title} ${s.promise} ${s.forWho}`.toLowerCase().includes(term)));
  }, [cat, q]);

  return (
    <Shell>
      <section className="svc-hero">
        <h1>50 finance, data and website services</h1>
        <p>Excel dashboards, Power BI reports, websites, automation and research for students, shops and small businesses. Every price is listed. Pick a package, pay online, and get the work by email.</p>
      </section>

      <div className="svc-filters">
        <div className="svc-search">
          <Search size={16} />
          <input className="input" placeholder="Search services, e.g. dashboard, website, GST" value={q} onChange={(e) => setQ(e.target.value)} aria-label="Search services" />
        </div>
        <div className="tabs" role="tablist" aria-label="Service category">
          <button className="tab" role="tab" aria-selected={cat === 'all'} onClick={() => setCat('all')}>All ({SERVICES.length})</button>
          {CATEGORIES.map((c) => (
            <button key={c.id} className="tab" role="tab" aria-selected={cat === c.id} onClick={() => setCat(c.id)}>
              {c.label} ({SERVICES.filter((s) => s.category === c.id).length})
            </button>
          ))}
        </div>
      </div>

      {shown.length === 0 && <p className="muted mt">No service matches “{q}”. Try another word, or email me what you need.</p>}

      <div className="svc-grid">
        {shown.map((s) => (
          <article key={s.id} className="card svc-card">
            <div className="svc-card-top">
              <span className="badge accent">{CATEGORIES.find((c) => c.id === s.category)?.label}</span>
              <span className="svc-num">#{s.id}</span>
            </div>
            <h2><Link to={`/services/${s.slug}`}>{s.title}</Link></h2>
            <p>{s.promise}</p>
            <div className="svc-price">From <b>{formatINR(s.tiers[0].price)}</b> · <Clock size={13} /> {s.tiers[0].days} day{s.tiers[0].days > 1 ? 's' : ''}</div>
            <div className="svc-card-actions">
              <Link className="btn sm" to={`/services/${s.slug}`}>See packages</Link>
              <Link className="btn sm primary" to={`/services/${s.slug}?order=Basic`}><CreditCard size={14} />Order {formatINR(s.tiers[0].price)}</Link>
            </div>
          </article>
        ))}
      </div>
    </Shell>
  );
}

export function ServiceDetail() {
  const { slug } = useParams();
  const navigate = useNavigate();
  const s = SERVICES.find((x) => x.slug === slug);
  const [ordering, setOrdering] = useState<Tier | null>(null);
  useEffect(() => {
    // "Order" on the list page links here with ?order=<tier> to open the form straight away.
    const want = new URLSearchParams(window.location.search).get('order');
    const t = s?.tiers.find((x) => x.name === want);
    if (t) { setOrdering(t); navigate(`/services/${s!.slug}`, { replace: true }); }
  }, [s, navigate]);
  useTitle(s ? `${s.title} · Services` : 'Service not found');

  if (!s) {
    return (
      <Shell>
        <div className="card svc-detail">
          <h1>Service not found</h1>
          <p className="muted mt-sm">That service link does not exist.</p>
          <div className="mt"><Link className="btn" to="/services"><ArrowLeft size={15} />All services</Link></div>
        </div>
      </Shell>
    );
  }
  const cat = CATEGORIES.find((c) => c.id === s.category);
  const related = SERVICES.filter((x) => x.category === s.category && x.id !== s.id).slice(0, 3);

  return (
    <Shell>
      <Link className="btn sm ghost" to="/services"><ArrowLeft size={15} />All 50 services</Link>
      <div className="card svc-detail mt-sm">
        <div className="row"><span className="badge accent">{cat?.label}</span><span className="svc-num">Service #{s.id}</span></div>
        <h1>{s.title}</h1>
        <p className="svc-lede">{s.promise}</p>
        <p className="muted"><b>Who it's for:</b> {s.forWho}</p>
        {s.sample && <p className="mt-sm"><a href={s.sample.url} target="_blank" rel="noreferrer">{s.sample.label} →</a></p>}

        <div className="svc-tiers">
          {s.tiers.map((t) => (
            <div key={t.name} className={`svc-tier${t.name === 'Standard' ? ' featured' : ''}`}>
              <div className="svc-tier-name">{t.name}{t.name === 'Standard' && <span className="badge pos">Most chosen</span>}</div>
              <div className="svc-tier-price">{formatINR(t.price)}</div>
              <p>{t.includes}</p>
              <ul>
                <li><Clock size={14} /> Delivery in {t.days} day{t.days > 1 ? 's' : ''}</li>
                <li><RefreshCw size={14} /> {t.revisions} revision{t.revisions > 1 ? 's' : ''}</li>
              </ul>
              <button className={`btn sm${t.name === 'Standard' ? ' primary' : ''}`} onClick={() => setOrdering(t)}><CreditCard size={14} />Order {t.name} · {formatINR(t.price)}</button>
            </div>
          ))}
        </div>

        <div className="svc-send">
          <CheckCircle2 size={17} />
          <div><b>What you send me:</b> {s.youSend}.</div>
        </div>

        <div className="svc-send mt-sm">
          <LockKeyhole size={17} />
          <div><b>Pay online, get it by email.</b> Secure payment by Razorpay (UPI, cards, netbanking). After paying you get a receipt, and the finished work arrives at your email. Questions first? <a href={`mailto:${CONTACT.email}`}>{CONTACT.email}</a></div>
        </div>
      </div>

      {related.length > 0 && (
        <section className="mt">
          <h2 className="svc-related-title">Related services</h2>
          <div className="svc-grid">
            {related.map((r) => (
              <article key={r.id} className="card svc-card">
                <h2><Link to={`/services/${r.slug}`}>{r.title}</Link></h2>
                <p>{r.promise}</p>
                <div className="svc-price">From <b>{formatINR(r.tiers[0].price)}</b></div>
              </article>
            ))}
          </div>
        </section>
      )}
      <OrderModal service={s} tier={ordering} onClose={() => setOrdering(null)} />
    </Shell>
  );
}

export function ServiceThankYou() {
  useTitle('Order confirmation · Services');
  return <Shell><ThankYou /></Shell>;
}
