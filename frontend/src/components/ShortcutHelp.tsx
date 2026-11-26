import { GO_KEYS } from '../lib/shortcuts';
import { Modal } from './Modal';

/** The keyboard shortcut cheat sheet ("?"). */
export function ShortcutHelp({ open, onClose }: { open: boolean; onClose: () => void }) {
  return (
    <Modal open={open} onClose={onClose} title="Keyboard shortcuts">
      <div className="stack" style={{ fontSize: 13 }}>
        <div className="shortcut-row"><span><kbd>Ctrl</kbd> + <kbd>K</kbd> or <kbd>/</kbd></span><span>Search pages, files and saved models</span></div>
        <div className="shortcut-row"><span><kbd>?</kbd></span><span>Show this list</span></div>
        <div className="faint" style={{ marginTop: 4 }}>Press <kbd>g</kbd>, then a letter, to jump to a page:</div>
        <div className="shortcut-grid">
          {Object.entries(GO_KEYS).map(([k, v]) => (
            <div key={k} className="shortcut-row"><span><kbd>g</kbd> <kbd>{k}</kbd></span><span>{v.label}</span></div>
          ))}
        </div>
        <p className="faint" style={{ fontSize: 12, margin: 0 }}>Shortcuts are off while you are typing in a box.</p>
      </div>
    </Modal>
  );
}
