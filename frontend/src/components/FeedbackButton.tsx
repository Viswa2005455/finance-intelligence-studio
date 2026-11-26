import { MessageSquare } from 'lucide-react';
import { useState } from 'react';
import { useLocation } from 'react-router-dom';
import { api, problemLog } from '../lib/api';
import { useToast } from '../lib/toast';
import { Modal } from './Modal';
import { Field } from './ui';

const KINDS = [{ value: 'idea', label: 'An idea' }, { value: 'problem', label: 'Something is wrong' }, { value: 'question', label: 'A question' }] as const;

/** "Send feedback": a short note to the people who run the app, with the page you were on and, if you choose, the details of the latest error. */
export function FeedbackButton() {
  const toast = useToast();
  const loc = useLocation();
  const [open, setOpen] = useState(false);
  const [kind, setKind] = useState<(typeof KINDS)[number]['value']>('idea');
  const [message, setMessage] = useState('');
  const [withDetails, setWithDetails] = useState(true);
  const [busy, setBusy] = useState(false);

  const send = async () => {
    setBusy(true);
    try {
      const recent = Array.from(problemLog.entries()).slice(-3).map(([m, d]) => `${m}\n${d}`).join('\n---\n');
      await api.post('/api/feedback', { kind, message, page: loc.pathname, details: withDetails ? `Page: ${loc.pathname}\n${recent}`.trim() : '' });
      toast('Thank you: your note was sent.');
      setMessage('');
      setOpen(false);
    } catch (e) { toast((e as Error).message, 'error'); } finally { setBusy(false); }
  };

  return (
    <>
      <button className="btn sm ghost feedback-btn" onClick={() => setOpen(true)}><MessageSquare size={14} />Send feedback</button>
      <Modal open={open} onClose={() => setOpen(false)} title="Send feedback"
        footer={<><button className="btn" onClick={() => setOpen(false)}>Cancel</button><button className="btn primary" onClick={send} disabled={busy || message.trim().length < 3}>{busy ? 'Sending…' : 'Send'}</button></>}>
        <div className="stack">
          <div className="tabs" role="tablist" aria-label="What kind of note">
            {KINDS.map((k) => <button key={k.value} type="button" role="tab" className="tab" aria-selected={kind === k.value} onClick={() => setKind(k.value)}>{k.label}</button>)}
          </div>
          <Field label="Your note" hint="Say what you were trying to do and what happened, or what would help. Please do not include passwords.">
            <textarea className="input" rows={5} maxLength={2000} value={message} onChange={(e) => setMessage(e.target.value)} autoFocus />
          </Field>
          <label className="row" style={{ fontSize: 13 }}>
            <input type="checkbox" checked={withDetails} onChange={(e) => setWithDetails(e.target.checked)} />
            Include technical details (the page and any recent error information)
          </label>
          <p className="faint" style={{ fontSize: 12, margin: 0 }}>Your note is stored with your account and deleted if you delete your account. It never includes your uploaded files.</p>
        </div>
      </Modal>
    </>
  );
}
