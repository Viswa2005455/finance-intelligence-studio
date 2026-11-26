import { Activity } from 'lucide-react';
import type { ReactNode } from 'react';
import { Backdrop } from './Backdrop';

/** The frame for pages anyone can read without an account (methodology, what's new): brand, a few links, and the footer. */
export function PublicShell({ title, children }: { title: string; children: ReactNode }) {
  return (
    <div className="landing">
      <Backdrop />
      <header className="landing-bar">
        <a href="/" className="row" style={{ gap: 10, textDecoration: 'none', color: 'inherit' }}>
          <div className="brand-mark" style={{ width: 36, height: 36, borderRadius: 11 }}><Activity size={19} strokeWidth={2.5} /></div>
          <b style={{ fontFamily: 'var(--font-display)', fontSize: 17 }}>Finance Intelligence Studio</b>
        </a>
        <nav className="row" aria-label="Site" style={{ gap: 14, fontSize: 14 }}>
          <a href="/methodology">How we calculate</a>
          <a href="/whats-new">What's new</a>
          <a className="btn primary sm" href="/">Open the app</a>
        </nav>
      </header>
      <main className="landing-main" aria-label={title}>{children}</main>
      <footer className="landing-foot faint">
        <span>Educational and analytical tool, not investment advice.</span>
        <span><a href="/methodology">Methodology</a> · <a href="/whats-new">What's new</a></span>
      </footer>
    </div>
  );
}
