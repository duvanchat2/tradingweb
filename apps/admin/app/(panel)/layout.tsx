import type { ReactNode } from 'react';
import { adminGet, csrfValue } from '../../lib/session';
import AdminChrome from '../../components/AdminChrome';

export default async function Panel({children}: {children: ReactNode}) {
  const user = await adminGet('/api/auth/me');
  if (!['staff', 'superworker'].includes(user.role)) {
    const {redirect} = await import('next/navigation');
    redirect('/login?error=staff');
  }
  return <AdminChrome fullName={user.full_name} role={user.role} csrf={csrfValue()}>{children}</AdminChrome>;
}
