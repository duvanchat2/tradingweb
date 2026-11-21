import type {Metadata} from 'next';
import type {ReactNode} from 'react';
import '@fontsource-variable/manrope';
import '@fontsource-variable/sora';
import './globals.css';
export const metadata:Metadata={title:'Global Efecty',description:'Plataforma de activos digitales'};
export default function Layout({children}:{children:ReactNode}){if(process.env.DEMO_MODE==='false')throw new Error('DEMO_MODE must remain true');return <html lang="es"><body>{children}</body></html>}
