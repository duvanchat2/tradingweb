import type {Metadata} from 'next';
import type {ReactNode} from 'react';
import './globals.css';
export const metadata:Metadata={title:'Global Efecty',description:'Plataforma demo de activos digitales'};
export default function Layout({children}:{children:ReactNode}){if(process.env.DEMO_MODE==='false')throw new Error('DEMO_MODE must remain true');return <html lang="es"><body><aside className="demo-banner" role="status">Demo — no son fondos reales</aside>{children}</body></html>}
