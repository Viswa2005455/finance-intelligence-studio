import { Menu, Moon, Sun, Activity, LogOut, Pin, PinOff, Printer, Search } from 'lucide-react';
import { Suspense, useEffect, useState } from 'react';
import { NavLink, Outlet, useLocation, useNavigate } from 'react-router-dom';
import { NAV } from '../nav';
import { CURRENCIES, type Currency } from '../lib/format';
import { useSettings } from '../lib/settings';
import { api } from '../lib/api';
import { SkeletonCards } from './ui';
import { Backdrop } from './Backdrop';
import { CommandPalette } from './CommandPalette';
import { FeedbackButton } from './FeedbackButton';
import { GlobalDrop } from './GlobalDrop';
import { ShortcutHelp } from './ShortcutHelp';
import { interpretKey, isTyping } from '../lib/shortcuts';
import { useAuth } from '../lib/auth';
import { useProjects } from '../lib/project';
import { useGuide } from '../lib/guide';
import { markRecent, markVisited } from '../lib/progress';
import { loadRaw, save } from '../lib/storage';

export function Layout() {
  const [open, setOpen] = useState(false);
  const { settings, update, resolvedTheme } = useSettings();
  const loc = useLocation();
  const current = NAV.find((n) => (n.to === '/' ? loc.pathname === '/' : loc.pathname === n.to || loc.pathname.startsWith(`${n.to}/`)));
  const [apiOk, setApiOk] = useState<boolean | null>(null);
  const { user, logout } = useAuth();
  const { projects, activeId, setActive } = useProjects();
  const navigate = useNavigate();
  const guide = useGuide();
  const [palette, setPalette] = useState(false);
  const [pins, setPins] = useState<string[]>(() => loadRaw<string[]>('fis.pins', []));
  const togglePin = (to: string) => setPins((p) => { const next = p.includes(to) ? p.filter((x) => x !== to) : [...p, to]; save('fis.pins', next); return next; });
  const pinned = pins.map((to) => NAV.find((n) => n.to === to)).filter((n): n is (typeof NAV)[number] => !!n);
  const [help, setHelp] = useState(false);
  useEffect(() => {
    let g = 0;  // when "g" was pressed: the next key (within a second) picks the page
    const onKey = (e: KeyboardEvent) => {
      if ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === 'k') { e.preventDefault(); setPalette((p) => !p); return; }
      if (isTyping(e.target) || e.defaultPrevented || document.querySelector('dialog[open]')) return;
      const act = interpretKey(e.key, Date.now() - g < 1000, { ctrl: e.ctrlKey, meta: e.metaKey, alt: e.altKey });
      g = 0;
      if (!act) return;
      if (act.type === 'wait-g') g = Date.now();
      else if (act.type === 'go') navigate(act.to);
      else if (act.type === 'help') setHelp(true);
      else if (act.type === 'search') { e.preventDefault(); setPalette(true); }
    };
    window.addEventListener('keydown', onKey);
    return () => window.removeEventListener('keydown', onKey);
  }, [navigate]);

  useEffect(() => { setOpen(false); window.scrollTo(0, 0); }, [loc.pathname]);
  useEffect(() => { if (loc.pathname === '/upload') guide.dismiss('nav-upload'); }, [loc.pathname]); // eslint-disable-line react-hooks/exhaustive-deps
  useEffect(() => { markVisited(loc.pathname); markRecent(loc.pathname); }, [loc.pathname]);
  useEffect(() => {
    document.title = `${current?.label ?? 'Not found'} · Finance Intelligence Studio`;
  }, [current]);
  useEffect(() => {
    let alive = true;
    const check = () => api.get('/api/health').then(() => alive && setApiOk(true)).catch(() => alive && setApiOk(false));
    check();
    const t = setInterval(check, 30000);
    return () => { alive = false; clearInterval(t); };
  }, []);

  let lastGroup = '';
  return (
    <div className={`shell ${open ? 'nav-open' : ''}`}>
      <a className="skip-link" href="#main" onClick={(e) => { e.preventDefault(); document.getElementById('main')?.focus(); }}>Skip to main content</a>
      <Backdrop />
      <CommandPalette open={palette} onClose={() => setPalette(false)} onHelp={() => setHelp(true)} />
      <ShortcutHelp open={help} onClose={() => setHelp(false)} />
      <GlobalDrop />
      <aside className="sidebar" aria-label="Main navigation">
        <div className="brand">
          <div className="brand-mark"><Activity size={19} strokeWidth={2.5} /></div>
          <div>
            <div className="brand-name">Finance Intelligence</div>
            <div className="brand-sub">Studio</div>
          </div>
        </div>
        <nav className="nav">
          {pinned.length > 0 && <div className="nav-group">Pinned</div>}
          {pinned.map((n) => <NavLink key={`pin-${n.to}`} to={n.to} end={n.to === '/'}><n.icon size={17} /><span>{n.label}</span></NavLink>)}
          {NAV.map((n) => {
            const header = n.group !== lastGroup ? <div className="nav-group" key={`g-${n.group}`}>{n.group}</div> : null;
            lastGroup = n.group;
            return [
              header,
              <NavLink key={n.to} to={n.to} end={n.to === '/'} title={n.ready ? undefined : 'Under development'}>
                <n.icon size={17} />
                <span>{n.label}</span>
                {!n.ready && <span className="dev-dot" aria-label="under development" />}
                {n.to === '/upload' && guide.isOn('nav-upload') && <span className="nav-arrow">&larr; Start here</span>}
              </NavLink>,
            ];
          })}
        </nav>
        <div className="sidebar-foot">
          <FeedbackButton />
          <div className="api-pill">
            <span className={`status-dot ${apiOk ? 'ok' : apiOk === false ? 'bad' : ''}`} />
            {apiOk === null ? 'Checking API…' : apiOk ? 'API connected' : 'API offline'}
          </div>
          {user && (
            <div className="user-chip">
              <div className="avatar" aria-hidden="true">{user.display_name.slice(0, 1).toUpperCase()}</div>
              <div style={{ minWidth: 0, flex: 1 }}>
                <div className="truncate who">{user.display_name}</div>
                <div className="truncate mail">{user.email}</div>
              </div>
              <button className="btn icon sm ghost" aria-label="Sign out" title="Sign out" onClick={logout}><LogOut size={16} /></button>
            </div>
          )}
        </div>
      </aside>
      <div className="scrim" onClick={() => setOpen(false)} />
      <div className="main">
        <header className="topbar">
          <button className="btn icon ghost menu-btn" aria-label="Open navigation" onClick={() => setOpen(true)}><Menu size={20} /></button>
          <div className="topbar-title">
            {current && <><span className="crumb hide-sm">{current.group}</span><span className="crumb-sep hide-sm" aria-hidden="true">/</span></>}
            <span className="here">{current?.label ?? 'Not found'}</span>
          </div>
          <div className="topbar-spacer" />
          {current && current.to !== '/' && <button className="btn sm ghost hide-sm" aria-pressed={pins.includes(current.to)} title={pins.includes(current.to) ? 'Unpin this page' : 'Pin this page to the top of the menu'} onClick={() => togglePin(current.to)}>{pins.includes(current.to) ? <PinOff size={15} aria-hidden="true" /> : <Pin size={15} aria-hidden="true" />}<span className="hide-md">{pins.includes(current.to) ? 'Unpin' : 'Pin'}</span></button>}
          <button className="btn sm ghost no-print hide-sm" aria-label="Print this page" title="Print this page" onClick={() => window.print()}><Printer size={15} aria-hidden="true" /></button>
          <button className="btn sm search-btn" aria-keyshortcuts="Control+K" title="Search pages (Ctrl+K)" onClick={() => setPalette(true)}><Search size={15} aria-hidden="true" /><span>Search</span><kbd className="hide-md" aria-hidden="true">Ctrl K</kbd></button>
          <div className="topbar-controls">
            <select className="input compact project-select" aria-label="Active project" value={activeId ?? ''}
              onChange={(e) => { if (e.target.value === '__manage') navigate('/projects'); else setActive(e.target.value || null); }}>
              <option value="">No project selected</option>
              {projects.filter((p) => !p.archived || p.id === activeId).map((p) => <option key={p.id} value={p.id}>{p.name}</option>)}
              <option value="__manage">Manage projects…</option>
            </select>
            <label className="hide-md row" style={{ gap: 6 }}>
              <span className="sr-only">Reporting period</span>
              <input className="input compact" type="month" style={{ width: 132 }} value={settings.periodFrom} aria-label="Period from"
                onChange={(e) => update({ periodFrom: e.target.value })} />
              <span className="faint">–</span>
              <input className="input compact" type="month" style={{ width: 132 }} value={settings.periodTo} aria-label="Period to"
                onChange={(e) => update({ periodTo: e.target.value })} />
            </label>
            <select className="input compact" style={{ width: 88 }} aria-label="Display currency" value={settings.currency}
              onChange={(e) => update({ currency: e.target.value as Currency })}>
              {CURRENCIES.map((c) => <option key={c}>{c}</option>)}
            </select>
            <button className="btn icon sm ghost" aria-label={`Switch to ${resolvedTheme === 'dark' ? 'light' : 'dark'} mode`}
              onClick={() => update({ theme: resolvedTheme === 'dark' ? 'light' : 'dark' })}>
              {resolvedTheme === 'dark' ? <Sun size={17} /> : <Moon size={17} />}
            </button>
          </div>
        </header>
        <main className="content" id="main" tabIndex={-1}>
          {settings.periodFrom > settings.periodTo && (
            <div className="callout error" style={{ marginBottom: 16 }}>The reporting period start is after its end. Please correct the date range.</div>
          )}
          <Suspense fallback={<SkeletonCards n={4} />}><Outlet /></Suspense>
        </main>
      </div>
    </div>
  );
}
