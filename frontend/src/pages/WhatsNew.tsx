import { useEffect } from 'react';
import { PublicShell } from '../components/PublicShell';
import { Card } from '../components/ui';
import { CHANGELOG } from '../lib/changelog';

/** Public page: what changed and when, in plain words. */
export function WhatsNew() {
  useEffect(() => { document.title = "What's new: Finance Intelligence Studio"; }, []);
  return (
    <PublicShell title="What's new">
      <section className="landing-hero" style={{ paddingTop: 20 }}>
        <h1 style={{ fontSize: 'clamp(30px, 5vw, 44px)' }}>What's new</h1>
        <p>What changed in the app, newest first. When a tax or accounting rule changes, it is listed here with the date.</p>
      </section>
      {CHANGELOG.map((e) => (
        <Card key={e.date + e.title} title={e.title} subtitle={new Date(e.date).toLocaleDateString(undefined, { dateStyle: 'long' })}>
          <ul className="summary-list">{e.items.map((i) => <li key={i}>{i}</li>)}</ul>
        </Card>
      ))}
    </PublicShell>
  );
}
