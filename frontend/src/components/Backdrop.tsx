/** The page background: navy (the sidebar), white (the pages) and light pink (the soft wash behind them). One static element,
 * no animation and no scripts, drawn by CSS (.app-bg). Hidden from assistive technology. */
export function Backdrop() {
  return <div className="app-bg" aria-hidden="true" />;
}
