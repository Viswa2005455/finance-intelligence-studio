import { CheckCircle2, CreditCard, Download, Loader2, LockKeyhole, Mail, XCircle } from 'lucide-react';
import { useEffect, useState, type FormEvent } from 'react';
import { Link, useSearchParams } from 'react-router-dom';
import { Modal } from '../components/Modal';
import { api, ApiError } from '../lib/api';
import { CONTACT, emailLink, formatINR, type Service, type Tier } from '../lib/services';

let configPromise: Promise<boolean> | null = null;
/** Whether online payment is switched on (Razorpay keys set on the server). Asked once per page load. */
export function usePaymentsEnabled(): boolean | null {
  const [enabled, setEnabled] = useState<boolean | null>(null);
  useEffect(() => {
    configPromise ??= api.get<{ enabled: boolean }>('/api/payments/config').then((c) => c.enabled).catch(() => false);
    configPromise.then(setEnabled);
  }, []);
  return enabled;
}

export function OrderModal({ service, tier, onClose }: { service: Service; tier: Tier | null; onClose: () => void }) {
  const enabled = usePaymentsEnabled();
  const [name, setName] = useState('');
  const [email, setEmail] = useState('');
  const [phone, setPhone] = useState('');
  const [requirements, setRequirements] = useState('');
  const [filesLink, setFilesLink] = useState('');
  const [agree, setAgree] = useState(false);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);

  if (!tier) return null;

  const submit = async (e: FormEvent) => {
    e.preventDefault();
    setError(null);
    if (name.trim().length < 2) return setError('Enter your name.');
    if (!/^\S+@\S+\.\S+$/.test(email.trim())) return setError('Enter a valid email address. Your work is delivered there.');
    if (tier.custom && requirements.trim().length < 10) return setError('Describe what you need in at least a sentence so the custom work can start.');
    if (filesLink && !/^https?:\/\//.test(filesLink.trim())) return setError('The files link must start with https://');
    if (!agree) return setError('Tick the box to confirm the delivery terms.');
    setBusy(true);
    try {
      const r = await api.post<{ url: string }>('/api/payments/checkout', {
        slug: service.slug, tier: tier.name, name: name.trim(), email: email.trim(), phone: phone.trim(),
        requirements: requirements.trim(), files_link: filesLink.trim(),
      });
      window.location.href = r.url;
    } catch (err) {
      setError(err instanceof ApiError ? err.message : 'Something went wrong. Please try again.');
      setBusy(false);
    }
  };

  return (
    <Modal open onClose={busy ? () => undefined : onClose} title={<>Order: {service.title}</>}>
      <div className="svc-order-sum">
        <div><b>{tier.name} package</b><span>{tier.includes}</span></div>
        <div className="svc-order-price">{formatINR(tier.price)}
          <small>{tier.custom ? `Kit instantly + custom work in ${tier.days} day${tier.days > 1 ? 's' : ''} · ${tier.revisions} revisions` : 'Instant download. Nothing to wait for.'}</small>
        </div>
      </div>

      {enabled === false ? (
        <div className="svc-order-off">
          <p>Online payment is being set up. To order now, email me and I'll send you a payment link.</p>
          <a className="btn primary" href={emailLink(service, tier)}><Mail size={15} />Email to order</a>
        </div>
      ) : (
        <form className="stack" style={{ gap: 12 }} onSubmit={submit} noValidate>
          <div className="svc-order-grid">
            <div className="field"><label className="field-label" htmlFor="o-name">Your name</label>
              <input id="o-name" className="input" autoComplete="name" value={name} onChange={(e) => setName(e.target.value)} maxLength={80} /></div>
            <div className="field"><label className="field-label" htmlFor="o-email">Email (work is delivered here)</label>
              <input id="o-email" className="input" type="email" autoComplete="email" value={email} onChange={(e) => setEmail(e.target.value)} maxLength={200} /></div>
          </div>
          <div className="field"><label className="field-label" htmlFor="o-phone">Phone (optional)</label>
            <input id="o-phone" className="input" type="tel" autoComplete="tel" value={phone} onChange={(e) => setPhone(e.target.value)} maxLength={20} /></div>
          {tier.custom && (
            <>
              <div className="field"><label className="field-label" htmlFor="o-req">What should the custom work cover?</label>
                <textarea id="o-req" className="input svc-order-text" rows={5} value={requirements} onChange={(e) => setRequirements(e.target.value)} maxLength={2000}
                  placeholder={service.youSend} />
                <div className="field-hint">{requirements.length}/2000. Include anything I should know: deadlines, examples, which numbers or pages you want.</div></div>
              <div className="field"><label className="field-label" htmlFor="o-files">Link to your files (optional)</label>
                <input id="o-files" className="input" value={filesLink} onChange={(e) => setFilesLink(e.target.value)} maxLength={250} placeholder="https://drive.google.com/…" />
                <div className="field-hint">Share a Google Drive, OneDrive or Dropbox link. You can also email files after paying.</div></div>
            </>
          )}
          <label className="svc-order-agree"><input type="checkbox" checked={agree} onChange={(e) => setAgree(e.target.checked)} />
            <span>{tier.custom
              ? <>I understand I get the ready-made kit instantly (download and email), and the custom work is emailed to the address above within {tier.days} day{tier.days > 1 ? 's' : ''} of me sending the details needed, with {tier.revisions} revisions included.</>
              : <>I understand I get the ready-made kit instantly (download and email). The Basic package is the kit only, with no custom work.</>}</span></label>
          {error && <div className="callout error" role="alert"><XCircle size={16} /><div>{error}</div></div>}
          <button className="btn primary svc-order-pay" type="submit" disabled={busy || enabled === null}>
            {busy ? <Loader2 size={16} className="spin" /> : <CreditCard size={16} />}{busy ? 'Opening secure payment…' : `Pay ${formatINR(tier.price)}`}
          </button>
          <div className="svc-order-safe"><LockKeyhole size={13} /> Secure payment by Razorpay: UPI, cards and netbanking. I never see your card details.</div>
        </form>
      )}
    </Modal>
  );
}

interface Verified { paid: boolean; description: string; amount: number; email: string; delivery_days: number | null; custom: boolean; kit_available: boolean; payment_id: string }

/** The kit download link: the same signed values Razorpay sent back, which the server re-checks. */
function kitUrl(params: URLSearchParams): string {
  const keep = ['razorpay_payment_id', 'razorpay_payment_link_id', 'razorpay_payment_link_reference_id', 'razorpay_payment_link_status', 'razorpay_signature'];
  const map: Record<string, string> = { razorpay_payment_id: 'payment_id', razorpay_payment_link_id: 'payment_link_id', razorpay_payment_link_reference_id: 'payment_link_reference_id', razorpay_payment_link_status: 'payment_link_status', razorpay_signature: 'razorpay_signature' };
  const q = new URLSearchParams();
  for (const k of keep) q.set(map[k], params.get(k) ?? '');
  return `/api/payments/kit?${q.toString()}`;
}

export function ThankYou() {
  const [params] = useSearchParams();
  const [state, setState] = useState<{ status: 'loading' | 'ok' | 'error'; data?: Verified; message?: string }>({ status: 'loading' });
  useEffect(() => { document.title = 'Order confirmation · Services'; }, []);
  useEffect(() => {
    const body = {
      payment_link_id: params.get('razorpay_payment_link_id') ?? '',
      payment_link_reference_id: params.get('razorpay_payment_link_reference_id') ?? '',
      payment_link_status: params.get('razorpay_payment_link_status') ?? '',
      payment_id: params.get('razorpay_payment_id') ?? '',
      signature: params.get('razorpay_signature') ?? '',
    };
    if (!body.payment_link_id || !body.signature) {
      setState({ status: 'error', message: 'This page opens after a payment. No payment details were found.' });
      return;
    }
    api.post<Verified>('/api/payments/verify', body)
      .then((data) => setState({ status: 'ok', data }))
      .catch((err) => setState({ status: 'error', message: err instanceof ApiError ? err.message : 'Could not confirm the payment.' }));
  }, [params]);

  return (
    <div className="card svc-detail svc-thanks">
      {state.status === 'loading' && <p className="row"><Loader2 size={18} className="spin" /> Confirming your payment…</p>}
      {state.status === 'error' && (
        <>
          <h1><XCircle size={26} /> We couldn't confirm this payment</h1>
          <p className="svc-lede">{state.message} If money was taken from your account, email <a href={`mailto:${CONTACT.email}`}>{CONTACT.email}</a> with your payment reference and I'll sort it out.</p>
        </>
      )}
      {state.status === 'ok' && state.data && (state.data.paid ? (
        <>
          <h1><CheckCircle2 size={26} className="svc-ok" /> Payment received. Thank you!</h1>
          <p className="svc-lede">Your order for <b>{state.data.description}</b> ({formatINR(state.data.amount)}) is confirmed.</p>
          {state.data.kit_available && (
            <div className="svc-kit">
              <a className="btn primary svc-order-pay" href={kitUrl(params)} download><Download size={16} />Download your ready-made kit</a>
              <p className="small">A ZIP file. Unzip it and open <b>00-START-HERE</b> first. A copy is also on its way to <b>{state.data.email || 'your email'}</b>.</p>
            </div>
          )}
          <ul className="svc-next">
            <li>A receipt from Razorpay is on its way to <b>{state.data.email || 'your email'}</b>.</li>
            {state.data.custom
              ? <li>Your <b>custom work</b> starts as soon as I have your details, and is emailed within <b>{state.data.delivery_days} day{state.data.delivery_days !== 1 ? 's' : ''}</b>.</li>
              : <li>The Basic package is the kit only, so you have everything already.</li>}
            <li>Questions, or files to send? Reply to <a href={`mailto:${CONTACT.email}?subject=${encodeURIComponent('Order ' + state.data.payment_id)}`}>{CONTACT.email}</a> with reference <b>{state.data.payment_id}</b>.</li>
          </ul>
        </>
      ) : (
        <>
          <h1><XCircle size={26} /> Payment not completed</h1>
          <p className="svc-lede">The payment for <b>{state.data.description}</b> wasn't completed, so nothing was charged. You can go back and try again.</p>
        </>
      ))}
      <div className="mt"><Link className="btn" to="/services">Back to all services</Link></div>
    </div>
  );
}
