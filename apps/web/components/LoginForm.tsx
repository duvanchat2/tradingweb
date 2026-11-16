'use client';

import { useEffect, useState } from 'react';


export default function LoginForm() {
  const [csrf, setCsrf] = useState('');
  const [failed, setFailed] = useState(false);
  useEffect(() => {
    fetch('/app/session/csrf', {cache: 'no-store'})
      .then(response => response.json())
      .then(value => setCsrf(value.csrf || ''))
      .catch(() => setFailed(true));
  }, []);
  return <form action="/app/session/login" method="post" className="form-grid">
    <input type="hidden" name="_csrf" value={csrf}/>
    <label>Correo electrónico
      <input name="email" type="email" autoComplete="username" placeholder="cliente@ejemplo.com" required/>
    </label>
    <label>Contraseña
      <input name="password" type="password" autoComplete="current-password" minLength={12} required/>
    </label>
    <button disabled={!csrf} type="submit">Entrar a mi cuenta</button>
    {failed && <p role="alert" className="notice error">No se pudo preparar el inicio de sesión. Recarga la página.</p>}
  </form>;
}
