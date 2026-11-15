import type { ReactNode } from 'react';
export default function Layout({ children }: { children: ReactNode }) {
  if (process.env.DEMO_MODE === 'false') throw new Error('DEMO_MODE must remain true');
  return <html lang="es"><body style={{fontFamily:'system-ui',margin:0}}>
    <aside role="status" style={{position:'sticky',top:0,padding:16,background:'#fef08a',color:'#422006'}}>Entorno de simulación — no son fondos reales</aside>
    <main style={{padding:32}}>{children}</main>
  </body></html>;
}
