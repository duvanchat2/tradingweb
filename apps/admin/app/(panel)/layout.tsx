import Link from 'next/link';
import NavLink from '../../components/NavLink';
import type { ReactNode } from 'react';
import { adminGet,csrfValue } from '../../lib/session';
const groups=[['GENERAL',[['dashboard','Resumen'],['production','Producción']]],['USUARIOS',[['users','Usuarios']]],['OPERACIONES',[['payments','Pagos'],['payment-methods','Métodos vinculados'],['kyc','KYC / Documentos'],['credit','Agregar fondos'],['deposit-wallets','Wallets depósito'],['notifications','Notificaciones'],['swaps','Swaps'],['cards','Tarjetas'],['stake-plans','Planes stake']]],['SOPORTE',[['chats','Chats'],['tickets','Tickets'],['help','Ayuda'],['ranking','Ranking']]]] as const;
export default async function Panel({children}:{children:ReactNode}){
 const user=await adminGet('/api/auth/me');
 if(!['staff','superworker'].includes(user.role)){const {redirect}=await import('next/navigation');redirect('/login?error=staff');}
 return <div className="shell"><aside className="sidebar"><Link href="/dashboard" className="brand"><span className="brand-mark">GE</span><strong>Global Efecty</strong></Link><span className="pill">BACK-OFFICE</span><nav>{groups.map(([title,links])=><section key={title}><h2>{title}</h2>{links.map(([path,label])=><NavLink key={path} href={'/'+path} label={label}/>)}</section>)}</nav><form action="/admin/session/logout" method="post"><input type="hidden" name="_csrf" value={csrfValue()}/><button className="secondary" type="submit">Cerrar sesión</button></form></aside><div className="main"><header className="topbar"><span>Panel del equipo</span><span className="pill">{user.role}</span><strong>{user.full_name}</strong></header><main className="content">{children}</main></div></div>;
}
