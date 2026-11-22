import type { ReactNode } from 'react';
import './globals.css';
import './admin-reference.css';
export default function Layout({children}:{children:ReactNode}){
 if(process.env.DEMO_MODE==='false')throw new Error('DEMO_MODE must remain true');
 return <html lang="es"><body>{children}</body></html>;
}
