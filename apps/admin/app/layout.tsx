import type { ReactNode } from 'react';
import './globals.css';
export default function Layout({children}:{children:ReactNode}){
 if(process.env.DEMO_MODE==='false')throw new Error('DEMO_MODE must remain true');
 return <html lang="es"><body><aside role="status" className="demo-banner">Entorno de simulación — no son fondos reales</aside>{children}</body></html>;
}
