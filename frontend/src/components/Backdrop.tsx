import { useEffect, useRef } from 'react';

/** Decorative "Prism" backdrop behind the whole app. Three colours (teal, indigo, amber) drift as soft aurora
 * lights, a perspective grid floor glides toward the viewer, and glass cubes and rings turn slowly in 3D.
 * A faint tri-colour performance curve draws once at the bottom. Everything is CSS transforms (no WebGL, no
 * library), pauses when reduced motion is on, and leans a few degrees toward the pointer on large screens.
 * Content always sits on solid cards in front of it. Hidden from assistive technology. */
const CUBES = ['c1', 'c2', 'c3', 'c4'] as const;
const FACES = ['front', 'back', 'right', 'left', 'top', 'bottom'] as const;

export function Backdrop() {
  const root = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const el = root.current;
    if (!el || typeof window.matchMedia !== 'function') return;
    if (window.matchMedia('(prefers-reduced-motion: reduce)').matches || !window.matchMedia('(pointer: fine)').matches) return;
    let raf = 0;
    const onMove = (e: PointerEvent) => {
      cancelAnimationFrame(raf);
      raf = requestAnimationFrame(() => {
        el.style.setProperty('--px', String((e.clientX / window.innerWidth - 0.5) * 2));
        el.style.setProperty('--py', String((e.clientY / window.innerHeight - 0.5) * 2));
      });
    };
    window.addEventListener('pointermove', onMove, { passive: true });
    return () => { window.removeEventListener('pointermove', onMove); cancelAnimationFrame(raf); };
  }, []);

  return (
    <div className="app-bg" ref={root} aria-hidden="true">
      <div className="bg-aurora">
        <i className="orb o1" /><i className="orb o2" /><i className="orb o3" />
      </div>
      <div className="bg-stage">
        <div className="bg-floor"><div className="bg-floor-grid" /></div>
        <div className="bg-solids">
          {CUBES.map((c) => (
            <div key={c} className={`solid ${c}`}>
              <div className="cube">{FACES.map((f) => <i key={f} className={f} />)}</div>
            </div>
          ))}
          <div className="solid r1"><div className="ring" /></div>
          <div className="solid r2"><div className="ring" /></div>
        </div>
      </div>
      <svg className="bg-curve" viewBox="0 0 1440 320" preserveAspectRatio="none">
        <defs>
          <linearGradient id="fis-tri" x1="0" y1="0" x2="1" y2="0">
            <stop offset="0" stopColor="var(--tri-a)" /><stop offset=".5" stopColor="var(--tri-b)" /><stop offset="1" stopColor="var(--tri-c)" />
          </linearGradient>
        </defs>
        <path className="area" d="M0 268 C120 250 190 214 300 226 S470 160 590 176 S780 96 900 118 S1130 44 1260 58 S1390 30 1440 22 V320 H0Z" />
        <path className="bench" d="M0 290 C180 280 300 262 450 264 S720 226 900 220 S1200 178 1440 160" />
        <path className="line" pathLength={1} d="M0 268 C120 250 190 214 300 226 S470 160 590 176 S780 96 900 118 S1130 44 1260 58 S1390 30 1440 22" />
      </svg>
    </div>
  );
}
