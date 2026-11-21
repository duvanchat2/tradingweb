'use client';
import type { ReactNode } from 'react';
import { useEffect, useState } from 'react';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { PanelIcon } from './PanelIcons';
type NavGroup={title:string;links:ReadonlyArray<readonly [string,string,string]>};
const groups:ReadonlyArray<NavGroup>=[
  {title:'PRINCIPAL',links:[['dashboard','Inicio','dashboard'],['notifications','Notificaciones','bell']]},
  {title:'FINANZAS',links:[['wallets','Wallets','wallet'],['swap','Swap','swap'],['stake','CDT / Stake','stake'],['market','Mercado','market'],['transactions','Movimientos','transactions'],['payments','Depositar / Retirar','payments']]},
  {title:'CUENTA',links:[['chat','Chat en vivo','chat'],['support','Soporte','support'],['profile','Ajustes','settings'],['verification','Verificación','verification']]},
];
const titles:Record<string,string>=Object.fromEntries(groups.flatMap(group=>group.links).map(([route,label])=>[route,label]));
function Brand(){return <><img src="/app/brand/isotipo.svg" width="35" height="30" alt=""/><strong>global efecty</strong></>}
export default function PanelShell({children,csrf}:{children:ReactNode;csrf:string}){
  const [open,setOpen]=useState(false);const [theme,setTheme]=useState<'dark'|'light'>('dark');
  const rawPath=usePathname();const section=rawPath.replace(/^\/app\/?/,'').split('/')[0]||'dashboard';
  useEffect(()=>setOpen(false),[rawPath]);
  useEffect(()=>{const close=(event:KeyboardEvent)=>event.key==='Escape'&&setOpen(false);window.addEventListener('keydown',close);return()=>window.removeEventListener('keydown',close)},[]);
  useEffect(()=>{const saved=localStorage.getItem('tradingweb-theme')==='light'?'light':'dark';setTheme(saved);document.documentElement.setAttribute('data-theme',saved)},[]);
  function toggleTheme(){const next=theme==='dark'?'light':'dark';setTheme(next);localStorage.setItem('tradingweb-theme',next);document.documentElement.setAttribute('data-theme',next)}
  return <div className={`panel-shell${open?' menu-open':''}`}>
    <aside className="panel-sidebar" id="client-sidebar"><Link className="panel-brand" href="/dashboard"><Brand/></Link><nav aria-label="Navegación principal">{groups.map(group=><section className="nav-group" key={group.title}><small>{group.title}</small>{group.links.map(([href,label,icon])=><Link key={href} href={`/${href}`} aria-current={section===href?'page':undefined}><PanelIcon name={icon}/><span>{label}</span>{href==='notifications'&&<i>0</i>}</Link>)}</section>)}</nav><div className="panel-sidebar-foot"><div className="sidebar-user"><span>GE</span><div><b>Mi cuenta</b><small>Cliente</small></div></div><form action="/app/session/logout" method="post"><input type="hidden" name="_csrf" value={csrf}/><button className="panel-logout" type="submit"><PanelIcon name="logout"/>Cerrar sesión</button></form></div></aside>
    <button className="panel-backdrop" type="button" aria-label="Cerrar menú" onClick={()=>setOpen(false)}/>
    <div className="panel-workspace"><header className="panel-topbar"><button className="panel-menu-toggle" type="button" aria-controls="client-sidebar" aria-expanded={open} aria-label="Abrir menú" onClick={()=>setOpen(value=>!value)}><span/><span/><span/></button><div className="topbar-title"><small>Panel de cliente</small><strong>{titles[section]||'Global Efecty'}</strong></div><div className="panel-top-actions"><button className="top-action" type="button" aria-label={theme==='dark'?'Activar modo claro':'Activar modo oscuro'} aria-pressed={theme==='light'} onClick={toggleTheme}><PanelIcon name="sun"/></button><Link className="top-action" href="/notifications" aria-label="Notificaciones"><PanelIcon name="bell"/><i/></Link><Link className="user-chip" href="/profile" aria-label="Mi perfil"><span>GE</span><b>Mi cuenta</b></Link></div></header><main className="panel-content">{children}</main></div>
  </div>;
}
