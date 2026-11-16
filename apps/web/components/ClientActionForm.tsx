'use client';

import { FormEvent, ReactNode, useState } from 'react';
import { useRouter } from 'next/navigation';


export default function ClientActionForm({
  action,
  csrf,
  children,
  label = 'Confirmar',
  initial = {},
  compact = false,
}: {
  action: string;
  csrf: string;
  children?: ReactNode;
  label?: string;
  initial?: Record<string, unknown>;
  compact?: boolean;
}) {
  const [busy, setBusy] = useState(false);
  const [message, setMessage] = useState('');
  const [error, setError] = useState(false);
  const router = useRouter();

  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (busy) return;
    const values: Record<string, unknown> = {action, ...initial};
    new FormData(event.currentTarget).forEach((value, key) => { values[key] = value; });
    for (const field of ['plan_id', 'order_id', 'notification_id']) {
      if (values[field] !== undefined && values[field] !== '') values[field] = Number(values[field]);
    }
    for (const field of ['price']) if (values[field] === '') delete values[field];
    setBusy(true); setMessage(''); setError(false);
    try {
      const response = await fetch('/app/backend/actions', {
        method: 'POST',
        headers: {'Content-Type': 'application/json', 'X-CSRF-Token': csrf},
        body: JSON.stringify(values),
      });
      const result = await response.json();
      if (!response.ok) {
        setError(true);
        setMessage(result.detail || 'Revisa los datos e intenta de nuevo.');
      } else {
        setMessage(result.message || 'Operación guardada.');
        router.refresh();
      }
    } catch {
      setError(true);
      setMessage('No se pudo confirmar la operación. Comprueba tu conexión e intenta de nuevo.');
    } finally {
      setBusy(false);
    }
  }

  return <form className={compact ? 'inline-form' : 'form-grid'} onSubmit={submit}>
    {children}
    <button disabled={busy} type="submit">{busy ? 'Procesando…' : label}</button>
    {message && <p role="status" className={`notice ${error ? 'error' : 'success'}`}>{message}</p>}
  </form>;
}
