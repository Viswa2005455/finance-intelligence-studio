import { UploadCloud } from 'lucide-react';
import { useEffect, useRef, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { uploadWithProgress } from '../lib/api';
import { useProjects } from '../lib/project';
import { useToast } from '../lib/toast';

type Result = { ok: true; upload: { id: string } } | { ok: false; error: string };

/** Drop a file anywhere in the app to analyse it. The Upload page keeps its own drop box, which takes priority. */
export function GlobalDrop() {
  const navigate = useNavigate();
  const toast = useToast();
  const { activeId } = useProjects();
  const [over, setOver] = useState(false);
  const depth = useRef(0);
  const project = useRef(activeId);
  project.current = activeId;

  useEffect(() => {
    const hasFiles = (e: DragEvent) => !!e.dataTransfer && Array.from(e.dataTransfer.types).includes('Files');
    const inOwnDropzone = (e: DragEvent) => e.target instanceof Element && !!e.target.closest('.dropzone');
    const enter = (e: DragEvent) => { if (hasFiles(e)) { depth.current += 1; setOver(!inOwnDropzone(e)); } };
    const overFn = (e: DragEvent) => { if (hasFiles(e) && !inOwnDropzone(e)) { e.preventDefault(); setOver(true); } else setOver(false); };
    const leave = (e: DragEvent) => { if (hasFiles(e)) { depth.current = Math.max(0, depth.current - 1); if (depth.current === 0) setOver(false); } };
    const drop = async (e: DragEvent) => {
      depth.current = 0;
      setOver(false);
      if (!hasFiles(e) || inOwnDropzone(e)) return;
      e.preventDefault();
      const files = Array.from(e.dataTransfer?.files ?? []);
      let last: string | null = null;
      for (const file of files.slice(0, 10)) {
        try {
          const res = await uploadWithProgress<{ results: Result[] }>('/api/uploads', [file], () => undefined, { project_id: project.current });
          const r = res.results[0];
          if (r.ok) { last = r.upload.id; toast(`${file.name} analysed`); } else toast(`${file.name}: ${r.error}`, 'error');
        } catch (err) { toast(`${file.name}: ${(err as Error).message}`, 'error'); }
      }
      if (last) navigate(`/upload?file=${last}`);
    };
    window.addEventListener('dragenter', enter);
    window.addEventListener('dragover', overFn);
    window.addEventListener('dragleave', leave);
    window.addEventListener('drop', drop);
    return () => { window.removeEventListener('dragenter', enter); window.removeEventListener('dragover', overFn); window.removeEventListener('dragleave', leave); window.removeEventListener('drop', drop); };
  }, [navigate, toast]);

  if (!over) return null;
  return (
    <div className="global-drop" role="presentation" aria-hidden="true">
      <div><UploadCloud size={34} /><b>Drop to analyse</b><span>Excel, CSV, PDF, Word, text and more. It opens on the Upload page.</span></div>
    </div>
  );
}
