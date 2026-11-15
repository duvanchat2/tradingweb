'use client';
export default function ErrorPage({reset}:{reset:()=>void}){return <main className="content"><section className="card"><h1>No se pudo cargar esta vista</h1><p>Comprueba los filtros o la conexión e inténtalo de nuevo.</p><button onClick={()=>reset()}>Reintentar</button><p><a href="/admin/dashboard">Volver al resumen</a></p></section></main>;}
