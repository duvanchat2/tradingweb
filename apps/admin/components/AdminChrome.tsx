'use client';

import { useState, type ReactNode } from 'react';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import NavLink from './NavLink';
import AdminIcon from './AdminIcon';

const groups = [
  ['GENERAL', [['dashboard', 'Resumen']]],
  ['USUARIOS', [['users', 'Todos los usuarios'], ['offices', 'Oficinas']]],
  ['OPERACIONES', [['production', 'Producción'], ['notifications', 'Notificaciones'], ['kyc', 'KYC / Documentos'], ['payments', 'Pagos'], ['payment-methods', 'Métodos vinculados'], ['cards', 'Tarjetas'], ['swaps', 'Swaps'], ['credit', 'Agregar fondos'], ['deposit-wallets', 'Wallets depósito'], ['stake-plans', 'Planes stake'], ['stake-positions', 'Solicitudes CDT']]],
  ['SOPORTE', [['chats', 'Chat en vivo'], ['tickets', 'Tickets'], ['help', 'Centro de ayuda'], ['ranking', 'Ranking oficina']]],
] as const;
const names: Record<string, string> = Object.fromEntries(groups.flatMap((group) => group[1].map((link) => [link[0], link[1]] as [string, string])));

export default function AdminChrome({children, fullName, role, csrf}: {children: ReactNode; fullName: string; role: string; csrf: string}) {
  const [open, setOpen] = useState(false);
  const pathname = usePathname();
  const section = pathname.replace(/^\/admin(?=\/|$)/, '').split('/').filter(Boolean)[0] || 'dashboard';
  return <div className="shell">
    {open && <button className="sidebar-backdrop" type="button" aria-label="Cerrar menú" onClick={() => setOpen(false)}/>}
    <aside className={'sidebar' + (open ? ' is-open' : '')} aria-label="Navegación del administrador">
      <Link href="/dashboard" className="brand" onClick={() => setOpen(false)}><img className="brand-logo" src="/admin/brand/isotipo.svg" alt="" width="34" height="34"/><strong>global efecty</strong></Link>
      <span className="pill admin-tag"><span className="live-dot"/> PANEL ADMIN</span>
      <nav onClick={() => setOpen(false)}>{groups.map(([title, links]) => <section key={title}><h2>{title}</h2>{links.map(([path, label]) => <NavLink key={path} href={'/' + path} label={label} icon={path}/>)}</section>)}</nav>
      <div className="sidebar-bottom"><form action="/admin/session/logout" method="post"><input type="hidden" name="_csrf" value={csrf}/><button type="submit" className="sidebar-logout"><AdminIcon name="logout"/> Cerrar sesión</button></form></div>
    </aside>
    <div className="main"><header className="topbar">
      <button className="mobile-menu" type="button" aria-label={open ? 'Cerrar menú' : 'Abrir menú'} aria-expanded={open} onClick={() => setOpen(v => !v)}><AdminIcon name={open ? 'close' : 'menu'}/></button>
      <div className="topbar-title"><span className="topbar-home">⌂</span><strong>{section === 'user' ? 'Perfil del cliente' : names[section] || 'Panel admin'}</strong></div>
      <div className="topbar-tools"><span className="topbar-language" aria-label="Idioma actual: español">▣ ES</span><Link href="/help" className="topbar-tool" aria-label="Centro de ayuda"><AdminIcon name="help"/></Link><Link href="/notifications" className="topbar-tool" aria-label="Notificaciones"><AdminIcon name="notifications"/></Link><span className="topbar-role">{role === 'superworker' ? 'SÚPER ADMIN' : 'ADMIN OFICINA'}</span><span className="topbar-user">{fullName}</span></div>
    </header><main className="content">{children}</main></div>
  </div>;
}
