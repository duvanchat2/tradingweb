'use client';

import type { ReactNode } from 'react';
import { useState } from 'react';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import NavLink from './NavLink';

const links = [
  ['dashboard', 'Inicio', '⌂'], ['notifications', 'Notificaciones', '●'],
  ['wallets', 'Wallets', '▣'], ['swap', 'Swap', '⇄'],
  ['stake', 'CDT / Stake', '◇'], ['market', 'Mercado', '⌁'],
  ['orders', 'Órdenes', '↗'], ['transactions', 'Movimientos', '≡'],
  ['payments', 'Depositar / Retirar', '$'], ['support', 'Tickets', '?'],
  ['profile', 'Ajustes', '⚙'],
] as const;
const titles: Record<string, string> = Object.fromEntries(links.map(([route, label]) => [route, label]));

function Logo() {
  return <svg className="panel-logo" viewBox="0 0 64 48" aria-hidden="true"><path d="M12 35C18 7 46 6 52 35M11 35c13-18 29-18 42 0M32 5v38" /><circle cx="32" cy="5" r="4" /><circle cx="11" cy="35" r="4" /><circle cx="53" cy="35" r="4" /></svg>;
}

export default function PanelShell({ children, csrf }: { children: ReactNode; csrf: string }) {
  const [open, setOpen] = useState(false);
  const pathname = usePathname().replace(/^\/app\/?/, '');
  const section = pathname.split('/')[0] || 'dashboard';
  return <div className={`panel-shell${open ? ' menu-open' : ''}`}>
    <aside className="panel-sidebar" id="client-sidebar">
      <Link className="panel-brand" href="/dashboard" onClick={() => setOpen(false)}><Logo /><strong>global efecty</strong></Link>
      <nav aria-label="Navegación principal">{links.map(([href, label, icon]) => <NavLink key={href} href={`/${href}`} label={label} icon={icon} />)}</nav>
      <div className="panel-sidebar-foot"><NavLink href="/profile" label="Mi cuenta" icon="○" /><form action="/app/session/logout" method="post"><input type="hidden" name="_csrf" value={csrf} /><button className="panel-logout" type="submit"><span aria-hidden="true">↪</span>Cerrar sesión</button></form></div>
    </aside>
    <button className="panel-backdrop" type="button" aria-label="Cerrar menú" onClick={() => setOpen(false)} />
    <div className="panel-workspace">
      <header className="panel-topbar"><button className="panel-menu-toggle" type="button" aria-controls="client-sidebar" aria-expanded={open} aria-label="Abrir menú" onClick={() => setOpen(value => !value)}><span></span><span></span><span></span></button><div><small>Panel de cliente</small><strong>{titles[section] || 'Global Efecty'}</strong></div><div className="panel-top-actions"><Link className="top-action" href="/notifications" aria-label="Notificaciones">●</Link><Link className="user-chip" href="/profile" aria-label="Mi perfil"><span>GE</span><b>Mi cuenta</b></Link></div></header>
      <main className="panel-content">{children}</main>
    </div>
  </div>;
}
