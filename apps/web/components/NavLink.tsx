'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';


export default function NavLink({href, label, icon}: {href: string; label: string; icon: string}) {
  const path = usePathname().replace(/^\/app(?=\/|$)/, '') || '/';
  return <Link href={href} prefetch={false} aria-current={path === href ? 'page' : undefined}>
    <span aria-hidden="true">{icon}</span><span>{label}</span>
  </Link>;
}
