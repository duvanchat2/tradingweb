'use client';

import { useEffect, useMemo, useState, type ReactNode } from 'react';
import countries from 'world-countries';

type FieldProps = {
  children: ReactNode;
  icon: string;
  label: string;
  hint?: string;
};

function Field({ children, icon, label, hint }: FieldProps) {
  return <label className="register-field">
    <span>{label}</span>
    <span className="field-shell"><span className="field-icon" aria-hidden="true">{icon}</span>{children}</span>
    {hint && <small>{hint}</small>}
  </label>;
}

export default function RegisterForm() {
  const [csrf, setCsrf] = useState('');
  const [failed, setFailed] = useState(false);
  const [busy, setBusy] = useState(false);
  const [showPassword, setShowPassword] = useState(false);
  const [country, setCountry] = useState('');

  const countryOptions = useMemo(() => countries.map(item => {
    const suffixes = item.idd.suffixes || [];
    const dial = item.idd.root && suffixes.length === 1 ? `${item.idd.root}${suffixes[0]}` : item.idd.root;
    return {
      code: item.cca2,
      dial,
      flag: item.flag,
      name: item.translations.spa?.common || item.name.common,
    };
  }).sort((a, b) => a.name.localeCompare(b.name, 'es')), []);

  const selectedCountry = countryOptions.find(item => item.code === country);

  useEffect(() => {
    fetch('/app/session/csrf', { cache: 'no-store' })
      .then(response => response.json())
      .then(value => value.csrf ? setCsrf(value.csrf) : setFailed(true))
      .catch(() => setFailed(true));
  }, []);

  return <form action="/app/session/register" method="post" className="register-form" onSubmit={event => {
    const form = event.currentTarget;
    const password = form.elements.namedItem('password') as HTMLInputElement;
    const confirm = form.elements.namedItem('password_confirm') as HTMLInputElement;
    if (password.value !== confirm.value) {
      event.preventDefault();
      confirm.setCustomValidity('Las contraseñas deben coincidir.');
      confirm.reportValidity();
      return;
    }
    if (busy) {
      event.preventDefault();
      return;
    }
    setBusy(true);
  }}>
    <input name="_csrf" type="hidden" value={csrf} />

    <Field label="Nombre completo" icon="♟">
      <input name="full_name" placeholder="Nombre y apellido" autoComplete="name" maxLength={200} required />
    </Field>

    <Field label="Email" icon="✉">
      <input name="email" type="email" placeholder="tu@email.com" autoComplete="email" maxLength={254} required />
    </Field>

    <Field label="Código de oficina" icon="⚿" hint="Solicita a tu oficina el código vigente. Cambia cada 24 horas.">
      <input name="registration_code" placeholder="Ej: ABC123" autoComplete="off" minLength={6} maxLength={6} pattern="[A-Za-z]{3}[0-9]{3}" onInput={event => { event.currentTarget.value = event.currentTarget.value.toUpperCase(); }} required />
    </Field>

    <Field label="País" icon="🌐">
      <select className="country-select" name="country" value={country} onChange={event => setCountry(event.target.value)} required>
        <option value="">Selecciona país</option>
        {countryOptions.map(item => <option key={item.code} value={item.code}>{item.flag} {item.name}</option>)}
      </select>
    </Field>

    <Field label="Teléfono (opcional)" icon="⌕">
      <input name="phone" type="tel" placeholder={selectedCountry?.dial ? `Ej: ${selectedCountry.dial} 600 000 000` : 'Incluye el indicativo de país'} autoComplete="tel" maxLength={32} />
    </Field>

    <Field label="Contraseña" icon="▣" hint="Usa al menos 12 caracteres con números y símbolos.">
      <input name="password" type={showPassword ? 'text' : 'password'} placeholder="Mínimo 12 caracteres" autoComplete="new-password" minLength={12} maxLength={128} onInput={event => {
        const confirm = event.currentTarget.form?.elements.namedItem('password_confirm') as HTMLInputElement | null;
        confirm?.setCustomValidity('');
      }} required />
      <button className="password-toggle" type="button" aria-label={showPassword ? 'Ocultar contraseña' : 'Mostrar contraseña'} onClick={() => setShowPassword(value => !value)}>◉</button>
    </Field>

    <Field label="Confirmar contraseña" icon="▣">
      <input name="password_confirm" type={showPassword ? 'text' : 'password'} placeholder="Repite tu contraseña" autoComplete="new-password" minLength={12} maxLength={128} onInput={event => event.currentTarget.setCustomValidity('')} required />
      <button className="password-toggle" type="button" aria-label={showPassword ? 'Ocultar contraseña' : 'Mostrar contraseña'} onClick={() => setShowPassword(value => !value)}>◉</button>
    </Field>

    <label className="terms-check"><input name="terms" type="checkbox" value="accepted" required /> <span>Acepto los <a href="/app/terms">Términos</a> y la <a href="/app/privacy">Política de Privacidad</a>.</span></label>

    <button className="register-submit" type="submit" disabled={!csrf || busy}>{busy ? 'Creando cuenta…' : '🚀 Crear mi cuenta'}</button>
    {failed && <p className="notice error" role="alert">No se pudo preparar el registro. Recarga la página.</p>}
  </form>;
}
