import { Activity, FileSpreadsheet, Landmark, LockKeyhole, ShieldAlert, ShieldCheck, Sigma } from 'lucide-react';
import { useEffect, useState, type FormEvent } from 'react';
import { Backdrop } from '../components/Backdrop';
import { Callout } from '../components/ui';
import { api } from '../lib/api';
import { useAuth } from '../lib/auth';

type Mode = 'login' | 'register' | 'forgot' | 'reset';
const TITLES: Record<Mode, string> = { login: 'Sign in', register: 'Create your account', forgot: 'Reset your password', reset: 'Choose a new password' };
const SUBTITLES: Record<Mode, string> = {
  login: 'Your projects, files and models are private to your account.',
  register: "Accounts keep each person's files and models separate.",
  forgot: 'Enter your email and we will send a link that lets you choose a new password.',
  reset: 'This link works once. After you change it, every device is signed out.',
};
const SUBMIT: Record<Mode, string> = { login: 'Sign in', register: 'Create account', forgot: 'Send reset link', reset: 'Change password' };

export function AuthScreen({ initialMode = 'login', onBack }: { initialMode?: Mode; onBack?: () => void }) {
  const { login, register, expired } = useAuth();
  const [mode, setMode] = useState<Mode>(initialMode);
  const [confirm, setConfirm] = useState('');
  const [done, setDone] = useState<string | null>(null);
  const go = (m: Mode) => { setMode(m); setError(null); setDone(null); setPassword(''); setConfirm(''); };
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [name, setName] = useState('');
  const [error, setError] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);
  const [registrationOpen, setRegistrationOpen] = useState(true);
  const [apiDown, setApiDown] = useState(false);

  // Keep checking while the backend is still starting (or was started late) and clear the warning
  // as soon as it answers, so nobody has to reload the page.
  useEffect(() => {
    let alive = true;
    let timer: ReturnType<typeof setTimeout> | undefined;
    const check = () => api.get<{ registration_open: boolean }>('/api/auth/config')
      .then((c) => { if (!alive) return; setRegistrationOpen(c.registration_open); setApiDown(false); setError(null); })
      .catch(() => { if (!alive) return; setApiDown(true); timer = setTimeout(check, 3000); });
    check();
    return () => { alive = false; clearTimeout(timer); };
  }, []);
  useEffect(() => { document.title = `${TITLES[mode]} · Finance Intelligence Studio`; }, [mode]);

  const canSubmit = mode === 'forgot' ? !!email : mode === 'reset' ? !!password && !!confirm
    : !!email && !!password && (mode !== 'register' || !!name.trim());

  const submit = async (e: FormEvent) => {
    e.preventDefault();
    setError(null);
    setBusy(true);
    try {
      if (mode === 'login') await login(email, password);
      else if (mode === 'register') await register(email, password, name);
      else if (mode === 'forgot') {
        const r = await api.post<{ message: string }>('/api/auth/forgot-password', { email });
        setDone(r.message);
      } else {
        if (password !== confirm) throw new Error('The two passwords do not match.');
        const token = new URLSearchParams(window.location.search).get('reset') ?? '';
        await api.post('/api/auth/reset-password', { token, new_password: password });
        window.history.replaceState({}, '', window.location.pathname);  // the link is spent: take it out of the address bar
        setMode('login'); setPassword(''); setConfirm('');
        setDone('Your password has been changed and every device was signed out. Sign in with the new password.');
      }
    } catch (err) {
      setError((err as Error).message);
    } finally {
      setBusy(false);
    }
  };

  return (
    <div className="auth-screen">
      <Backdrop />
      <aside className="auth-showcase" aria-hidden="true">
        <div className="auth-showcase-brand">
          <div className="brand-mark" style={{ width: 42, height: 42, borderRadius: 12 }}><Activity size={22} strokeWidth={2.5} /></div>
          <div>
            <div className="brand-name" style={{ fontSize: 16 }}>Finance Intelligence</div>
            <div className="brand-sub">Studio</div>
          </div>
        </div>
        <div>
          <h2 className="auth-headline">Analysis you can <span>defend</span></h2>
          <p className="auth-lede">Formulas and inputs shown next to every result. Built for CPAs, CFA charterholders, CMAs and auditors.</p>
          <ul className="auth-features">
            <li><ShieldAlert size={17} /><div><b>Forensic screens</b><span>Beneish M-score, Altman Z, Piotroski F and cash-quality checks</span></div></li>
            <li><Landmark size={17} /><div><b>Valuation</b><span>DCF, reverse DCF, Monte Carlo ranges and peer comparison</span></div></li>
            <li><Sigma size={17} /><div><b>Professional schedules</b><span>Leases, bonds, EPS, deferred tax, costing and derivatives</span></div></li>
            <li><FileSpreadsheet size={17} /><div><b>Audit-ready exports</b><span>Excel with live formulas, Word and PDF reports</span></div></li>
          </ul>
        </div>
        <svg className="auth-chart" viewBox="0 0 480 140" fill="none">
          <path d="M0 120 C40 112 70 96 110 102 S170 70 210 78 S280 40 320 50 S400 18 480 10 V140 H0Z" style={{ fill: 'var(--sb-mark)' }} fillOpacity=".1" />
          <path d="M0 120 C40 112 70 96 110 102 S170 70 210 78 S280 40 320 50 S400 18 480 10" style={{ stroke: 'var(--sb-mark)' }} strokeWidth="2" />
          <path d="M0 128 C60 124 100 116 150 118 S240 100 300 98 S400 80 480 70" stroke="rgba(255,255,255,.35)" strokeWidth="1.5" strokeDasharray="5 6" />
        </svg>
      </aside>
      <div className="auth-wrap">
        {onBack && <div style={{ marginBottom: 10 }}><button type="button" className="link-btn" onClick={onBack}>&larr; Back to the overview</button></div>}
        <div className="auth-brand">
          <div className="brand-mark" style={{ width: 44, height: 44, borderRadius: 13 }}><Activity size={24} strokeWidth={2.5} /></div>
          <div>
            <div style={{ fontWeight: 750, fontSize: 20, fontFamily: 'var(--font-display)' }}>Finance Intelligence Studio</div>
            <div className="muted">FP&amp;A, valuation and financial analysis</div>
          </div>
        </div>
        <form className="card auth-card" onSubmit={submit} noValidate>
          <h1 style={{ fontSize: 24 }}>{TITLES[mode]}</h1>
          <p className="muted" style={{ marginTop: 4 }}>{SUBTITLES[mode]}</p>
          {expired && mode === 'login' && <div className="mt"><Callout tone="info">Your session ended. Please sign in again.</Callout></div>}
          {done && <div className="mt"><Callout tone="success">{done}</Callout></div>}
          {apiDown && (
            <div className="mt">
              <Callout tone="warn" title="Waiting for the app's backend…">
                This page connects by itself once the backend is ready. Starting can take a minute the first time.
                If it does not connect, look at the window titled <b>Finance Studio - BACKEND</b>: if it shows an error, send a screenshot of it.
                If that window is closed, double-click <code>start-windows.bat</code> again.
              </Callout>
            </div>
          )}
          <div className="stack mt" style={{ gap: 12 }}>
            {mode === 'register' && (
              <div className="field"><label className="field-label" htmlFor="auth-name">Your name</label>
                <input id="auth-name" className="input" autoComplete="name" value={name} onChange={(e) => setName(e.target.value)} required maxLength={80} /></div>
            )}
            {mode !== 'reset' && !(mode === 'forgot' && done) && (
              <div className="field"><label className="field-label" htmlFor="auth-email">Email</label>
                <input id="auth-email" className="input" type="email" autoComplete="email" value={email} onChange={(e) => setEmail(e.target.value)} required /></div>
            )}
            {(mode === 'login' || mode === 'register' || mode === 'reset') && (
              <div className="field"><label className="field-label" htmlFor="auth-password">{mode === 'reset' ? 'New password' : 'Password'}</label>
                <input id="auth-password" className="input" type="password" autoComplete={mode === 'login' ? 'current-password' : 'new-password'} value={password} onChange={(e) => setPassword(e.target.value)} required />
                {mode !== 'login' && <div className="field-hint">At least 10 characters, not a common password, and not containing your email name.</div>}
                {mode === 'login' && <div className="field-hint"><button type="button" className="link-btn" onClick={() => go('forgot')}>Forgot your password?</button></div>}
              </div>
            )}
            {mode === 'reset' && (
              <div className="field"><label className="field-label" htmlFor="auth-confirm">Type it again</label>
                <input id="auth-confirm" className="input" type="password" autoComplete="new-password" value={confirm} onChange={(e) => setConfirm(e.target.value)} required /></div>
            )}
            {error && <Callout tone="error">{error}</Callout>}
            {!(mode === 'forgot' && done) && (
              <button className="btn primary" type="submit" disabled={busy || apiDown || !canSubmit} style={{ height: 40 }}>
                <LockKeyhole size={16} />{busy ? 'Please wait…' : SUBMIT[mode]}
              </button>
            )}
          </div>
          <div className="mt" style={{ textAlign: 'center', fontSize: 13 }}>
            {mode === 'login' && (registrationOpen ? <>New here? <button type="button" className="link-btn" onClick={() => go('register')}>Create an account</button></> : <span className="faint">Registration is closed on this server.</span>)}
            {mode === 'register' && <>Already have an account? <button type="button" className="link-btn" onClick={() => go('login')}>Sign in</button></>}
            {(mode === 'forgot' || mode === 'reset') && <button type="button" className="link-btn" onClick={() => go('login')}>Back to sign in</button>}
          </div>
        </form>
        <div className="mt" style={{ textAlign: 'center', fontSize: 13.5 }}>Looking to hire? <a className="link-btn" href="/services">See my 50 services →</a></div>
        <div className="auth-foot faint"><ShieldCheck size={14} /> Passwords are hashed with scrypt. Sessions use secure, HttpOnly cookies. Educational tool — not investment advice.</div>
      </div>
    </div>
  );
}
