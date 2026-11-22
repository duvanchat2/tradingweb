'use client';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import AdminIcon from './AdminIcon';
export default function NavLink({href,label,icon}:{href:string;label:string;icon?:string}){
 const path=usePathname().replace(/^\/admin(?=\/|$)/,'')||'/';
 return <Link href={href} prefetch={false} aria-current={path===href||path.startsWith(href+'/')||(href==='/users'&&path.startsWith('/user/'))?'page':undefined}><span className="nav-icon"><AdminIcon name={icon||href.slice(1)}/></span><span>{label}</span><AdminIcon name="chevron" size={14}/></Link>;
}
