'use client';
import { useEffect,useState } from 'react';

export default function RegisterForm(){
 const [csrf,setCsrf]=useState(''),[failed,setFailed]=useState(false),[busy,setBusy]=useState(false);
 useEffect(()=>{fetch('/app/session/csrf',{cache:'no-store'}).then(r=>r.json()).then(value=>{if(value.csrf)setCsrf(value.csrf);else setFailed(true);}).catch(()=>setFailed(true));},[]);
 return <form action="/app/session/register" method="post" className="form-grid" onSubmit={event=>{
  const form=event.currentTarget;const password=form.elements.namedItem('password') as HTMLInputElement;const confirm=form.elements.namedItem('password_confirm') as HTMLInputElement;
  if(password.value!==confirm.value){event.preventDefault();confirm.setCustomValidity('Las contraseñas deben coincidir.');confirm.reportValidity();return;}
  if(busy){event.preventDefault();return;}setBusy(true);
 }}>
  <input name="_csrf" type="hidden" value={csrf}/>
  <label>Nombre completo<input name="full_name" autoComplete="name" maxLength={200} required/></label>
  <label>Correo electrónico<input name="email" type="email" autoComplete="email" maxLength={254} required/></label>
  <label>Contraseña<input name="password" type="password" autoComplete="new-password" minLength={12} maxLength={128} onInput={event=>{const confirm=event.currentTarget.form?.elements.namedItem('password_confirm') as HTMLInputElement|null;confirm?.setCustomValidity('');}} required/></label>
  <p className="password-hint">Utiliza entre 12 y 128 caracteres.</p>
  <label>Confirmar contraseña<input name="password_confirm" type="password" autoComplete="new-password" minLength={12} maxLength={128} onInput={event=>event.currentTarget.setCustomValidity('')} required/></label>
  <button type="submit" disabled={!csrf||busy}>{busy?'Creando cuenta…':'Crear cuenta'}</button>
  {failed&&<p className="notice error" role="alert">No se pudo preparar el registro. Recarga la página.</p>}
 </form>;
}
