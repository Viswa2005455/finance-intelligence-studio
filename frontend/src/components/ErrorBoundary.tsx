import { Component, type ErrorInfo, type ReactNode } from 'react';
import { reportError } from '../lib/reportError';

/** The last line of defence: if a page throws while drawing, show a calm message instead of a blank screen, and tell the server. */
export class ErrorBoundary extends Component<{ children: ReactNode }, { failed: boolean }> {
  state = { failed: false };
  static getDerivedStateFromError() { return { failed: true }; }
  componentDidCatch(error: Error, info: ErrorInfo) { reportError(error, (info.componentStack ?? '').split('\n').slice(0, 3).join(' ').trim()); }
  render() {
    if (!this.state.failed) return this.props.children;
    return (
      <div className="splash" role="alert" style={{ flexDirection: 'column', gap: 12, textAlign: 'center', padding: 24 }}>
        <h1 style={{ fontSize: 20, margin: 0 }}>Something went wrong on this page</h1>
        <p className="faint" style={{ maxWidth: 420, margin: 0 }}>Your saved work is safe. A short note about the problem was sent so it can be fixed. Reloading usually clears it.</p>
        <div className="row" style={{ gap: 8 }}>
          <button className="btn primary" onClick={() => window.location.reload()}>Reload the page</button>
          <a className="btn" href="/">Go to the start</a>
        </div>
      </div>
    );
  }
}
