'use client';
import { useEffect,useState } from 'react';
export default function LoginForm(){
 const [csrf,setCsrf]=useState('');const [failed,setFailed]=useState(false);
 useEffect(()=>{fetch('/admin/session/csrf',{cache:'no-store'}).then(r=>r.json()).then(v=>setCsrf(v.csrf||'')).catch(()=>setFailed(true));},[]);
 return <form action="/admin/session/login" method="post" className="form-grid">
  <input type="hidden" name="_csrf" value={csrf}/>
  <label>Correo del equipo<input name="email" type="email" autoComplete="username" required/></label>
  <label>Contraseña<input name="password" type="password" autoComplete="current-password" minLength={12} required/></label>
  <button disabled={!csrf} type="submit">Entrar al back-office</button>
  {failed&&<p role="alert">No se pudo preparar el inicio de sesión. Recarga la página.</p>}
 </form>;
}
