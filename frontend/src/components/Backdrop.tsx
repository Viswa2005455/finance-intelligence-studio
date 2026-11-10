/** Decorative backdrop behind the whole app: warm ledger paper (the column rules are drawn in CSS on
 * `.app-bg`), two soft lights and a faint performance curve with a dashed benchmark that draws once.
 * No looping animation and no 3D library; content always sits on solid cards in front of it.
 * Hidden from assistive technology. */
export function Backdrop() {
  return (
    <div className="app-bg" aria-hidden="true">
      <div className="bg-light a" />
      <div className="bg-light b" />
      <svg className="bg-curve" viewBox="0 0 1440 320" preserveAspectRatio="none">
        <path className="area" d="M0 268 C120 250 190 214 300 226 S470 160 590 176 S780 96 900 118 S1130 44 1260 58 S1390 30 1440 22 V320 H0Z" />
        <path className="bench" d="M0 290 C180 280 300 262 450 264 S720 226 900 220 S1200 178 1440 160" />
        <path className="line" pathLength={1} d="M0 268 C120 250 190 214 300 226 S470 160 590 176 S780 96 900 118 S1130 44 1260 58 S1390 30 1440 22" />
      </svg>
    </div>
  );
}
