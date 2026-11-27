/** Sends a short crash note to the server log so the operator can see what broke. No personal data: message, page path and a short stack. */
let sent = 0;
const MAX_PER_SESSION = 3;

export function reportError(error: unknown, extra = ''): void {
  if (sent >= MAX_PER_SESSION) return;
  sent += 1;
  const e = error instanceof Error ? error : new Error(String(error));
  const body = JSON.stringify({ message: `${e.name}: ${e.message}${extra ? ` (${extra})` : ''}`.slice(0, 500), page: window.location.pathname, stack: (e.stack ?? '').slice(0, 2000), version: '0.14.0' });
  try {
    void fetch('/api/client-errors', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body, keepalive: true }).catch(() => undefined);
  } catch { /* reporting must never cause a second failure */ }
}

export function installGlobalReporting(): void {
  window.addEventListener('error', (ev) => reportError(ev.error ?? ev.message, 'window error'));
  window.addEventListener('unhandledrejection', (ev) => reportError(ev.reason, 'unhandled promise'));
}
