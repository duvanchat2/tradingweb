'use client';
export default function ErrorPage({reset}:{reset:()=>void}){return <main className="login-shell"><section className="login-card"><p className="eyebrow">ERROR TEMPORAL</p><h1>No pudimos cargar esta sección</h1><p className="muted">Conservamos tu sesión. Intenta de nuevo.</p><button onClick={reset}>Reintentar</button></section></main>}
