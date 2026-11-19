import type { ReactNode } from 'react';
import Link from 'next/link';
import { notFound } from 'next/navigation';
import ClientActionForm from '../../../components/ClientActionForm';
import { CryptoIcon, PanelIcon } from '../../../components/PanelIcons';
import { clientGet, csrfValue } from '../../../lib/session';

type R = Record<string, any>;
const cash = (value: any, currency = '') => `${Number(value || 0).toLocaleString('es-CO', { maximumFractionDigits: 8 })}${currency ? ` ${currency}` : ''}`;
const when = (value: any) => value ? new Date(value).toLocaleString('es-CO') : '—';
const percent = (value: any) => `${Number(value || 0) >= 0 ? '+' : ''}${Number(value || 0).toFixed(2)}%`;
function priceRows(payload: R): R[] {
  if (Array.isArray(payload?.assets)) {
    return payload.assets.map((asset: R) => ({ ...asset, change_24h: asset.change_percent_24h }));
  }
  return Object.entries(payload?.prices || {}).map(([symbol, price]) => ({ symbol, price, change_24h: null }));
}

function Shell({ title, subtitle, children, action }: { title: string; subtitle: string; children: ReactNode; action?: ReactNode }) {
  return <><header className="page-head"><div><p className="eyebrow">GLOBAL EFECTY</p><h1>{title}</h1><p>{subtitle}</p></div>{action}</header>{children}</>;
}
function Card({ title, children, className = '' }: { title: string; children: ReactNode; className?: string }) {
  return <section className={`card ${className}`.trim()}><h2>{title}</h2>{children}</section>;
}
function Table({ rows, cols, empty = 'Aún no hay movimientos.' }: { rows: R[]; cols: [string, (row: R) => ReactNode][]; empty?: string }) {
  return rows.length ? <div className="table-wrap"><table><thead><tr>{cols.map(column => <th key={column[0]}>{column[0]}</th>)}</tr></thead><tbody>{rows.map((row, index) => <tr key={row.id ?? index}>{cols.map(column => <td key={column[0]}>{column[1](row)}</td>)}</tr>)}</tbody></table></div> : <div className="empty-state"><span>◇</span><p>{empty}</p></div>;
}
function BalanceGrid({ accounts }: { accounts: R[] }) {
  return <div className="wallet-grid">{accounts.map(account => <article className="wallet-card" key={account.id}><CryptoIcon symbol={account.currency} /><div><strong>{account.currency}</strong><small>{account.type === 'main' ? 'Wallet principal' : account.type}</small></div><b>{cash(account.balance, account.currency)}</b></article>)}</div>;
}

function MarketTicker({ prices }: { prices: R[] }) {
  return <div className="market-ticker" aria-label="Cotizaciones en vivo"><div>{prices.concat(prices).map((row, index) => <span key={`${row.symbol}-${index}`}><CryptoIcon symbol={row.symbol} size={24} /><b>{row.symbol}</b><em>${cash(row.price)}</em><i className={Number(row.change_24h) >= 0 ? 'positive' : 'negative'}>{percent(row.change_24h)}</i></span>)}</div></div>;
}
function PriceChange({ value }: { value: any }) { return <span className={`price-change ${Number(value) >= 0 ? 'positive' : 'negative'}`}>{percent(value)}</span>; }

async function dashboard() {
  const [account, marketData, transactions, notices] = await Promise.all([clientGet('/api/account'), clientGet('/api/market/live'), clientGet('/api/account/transactions?limit=8'), clientGet('/api/notifications')]);
  const prices = priceRows(marketData);
  const nonZero = account.accounts.filter((item: R) => Number(item.balance) !== 0).length;
  return <Shell title={`Hola, ${account.user.full_name || 'inversionista'} 👋`} subtitle="Este es el resumen de tu cuenta hoy." action={<Link className="primary-link" href="/payments">+ Depositar fondos</Link>}>
    <section className="dashboard-hero"><div><span>BALANCE TOTAL</span><strong>{nonZero ? `${nonZero} wallets con saldo` : '$0.00'}</strong><small>Disponible en {account.accounts.length} activos</small><div className="hero-buttons"><Link href="/payments">Depositar</Link><Link href="/payments">Retirar</Link></div></div><div className="hero-glow"><img src="/app/brand/isotipo.svg" alt="" /></div></section>
    <div className="dashboard-kpis"><article><PanelIcon name="wallet" /><div><span>Activos con saldo</span><b>{nonZero}</b></div></article><article><PanelIcon name="market" /><div><span>Mercados disponibles</span><b>{prices.length}</b></div></article><article><PanelIcon name="verification" /><div><span>Estado de cuenta</span><b>{account.user.kyc_status || 'Pendiente'}</b></div></article></div>
    <section className="action-section"><div className="section-title"><div><small>ACCESOS RÁPIDOS</small><h2>¿Qué quieres hacer?</h2></div></div><div className="quick-actions">{[['swap','swap','Hacer swap','Convierte tus criptos'],['stake','stake','Crear CDT','Genera rendimientos'],['payments','payments','Depositar','Añade fondos'],['payments','transactions','Enviar','Transfiere activos'],['support','chat','Chat en vivo','Habla con soporte']].map(([href, icon, title, copy]) => <Link href={`/${href}`} key={title}><PanelIcon name={icon} /><span><b>{title}</b><small>{copy}</small></span><i>›</i></Link>)}</div></section>
    <div className="dashboard-grid dashboard-panels"><Card title="Notificaciones recientes"><div className="notice-list">{notices.items?.length ? notices.items.slice(0, 3).map((item: R) => <article key={item.id}><PanelIcon name="bell" /><div><b>{item.title}</b><small>{item.body}</small></div></article>) : <div className="compact-empty"><PanelIcon name="bell" /><span>Todo está al día</span></div>}</div><Link className="card-link" href="/notifications">Ver notificaciones →</Link></Card><Card title="Movimientos recientes"><Table rows={transactions.items.slice(0, 4)} cols={[["Concepto", row => row.kind], ["Monto", row => cash(row.amount, row.currency)], ["Estado", row => <span className="status-pill">{row.status}</span>]]} /><Link className="card-link" href="/transactions">Ver movimientos →</Link></Card></div>
    <MarketTicker prices={prices} />
    <section className="market-preview"><div className="section-title"><div><small>MERCADO EN VIVO</small><h2>Activos populares</h2></div><Link href="/market">Ver mercado completo →</Link></div><div className="popular-assets">{prices.slice(0, 6).map(row => <article key={row.symbol}><div><CryptoIcon symbol={row.symbol} /><span><b>{row.symbol}</b><small>USD</small></span></div><strong>${cash(row.price)}</strong><PriceChange value={row.change_24h} /></article>)}</div></section>
    <Card title="Mis activos" className="dashboard-assets"><BalanceGrid accounts={account.accounts.slice(0, 5)} /><Link className="card-link" href="/wallets">Ver todas las wallets →</Link></Card>
  </Shell>;
}

async function wallets() {
  const [account, addresses] = await Promise.all([clientGet('/api/account'), clientGet('/api/payments/deposit-wallets')]);
  return <Shell title="Mis wallets" subtitle="Gestiona todos tus activos desde un solo lugar." action={<Link className="primary-link" href="/payments">+ Depositar</Link>}><section className="wallet-summary"><div><small>BALANCE TOTAL</small><strong>{account.accounts.filter((row: R) => Number(row.balance)).length ? 'Consulta por activo' : '$0.00'}</strong><span>{account.accounts.length} activos disponibles</span></div><div><PanelIcon name="wallet" /></div></section><div className="wallet-toolbar"><b>Tus activos</b><span>Todos&nbsp;&nbsp; Con saldo&nbsp;&nbsp; Sin saldo</span></div><BalanceGrid accounts={account.accounts} /><Card title="Direcciones de recepción"><Table rows={addresses} empty="No hay direcciones disponibles." cols={[["Moneda", row => <span className="asset-cell"><CryptoIcon symbol={row.currency} size={28} />{row.currency}</span>], ["Red", row => row.network], ["Dirección", row => <code>{row.address}</code>]]} /></Card></Shell>;
}

async function market() {
  const marketData = await clientGet('/api/market/live');
  const prices = priceRows(marketData);
  const gainers = prices.filter(row => Number(row.change_24h) >= 0).length;
  return <Shell title="Mercado" subtitle="Cotizaciones actualizadas de tus activos favoritos."><div className="market-stats"><article><span>Activos disponibles</span><b>{prices.length}</b></article><article><span>En alza</span><b className="positive">{gainers}</b></article><article><span>En baja</span><b className="negative">{prices.length - gainers}</b></article></div><div className="market-toolbar"><b>Todos los activos</b><span>Precios en USD · actualización frecuente</span></div><section className="market-grid">{prices.map(row => <article key={row.symbol}><header><div><CryptoIcon symbol={row.symbol} /><span><b>{row.symbol}</b><small>USD</small></span></div><PriceChange value={row.change_24h} /></header><strong>${cash(row.price)}</strong><dl><div><dt>Máximo 24h</dt><dd>${cash(row.high_24h)}</dd></div><div><dt>Mínimo 24h</dt><dd>${cash(row.low_24h)}</dd></div><div><dt>Volumen 24h</dt><dd>${cash(row.volume_24h)}</dd></div></dl><Link href="/swap">Comprar {row.symbol}</Link></article>)}</section><MarketTicker prices={prices} /></Shell>;
}

async function transactions() {
  const data = await clientGet('/api/account/transactions?limit=100');
  return <Shell title="Movimientos" subtitle="Consulta toda la actividad de tus wallets." action={<Link className="secondary-link" href="/payments">Descargar reporte</Link>}><div className="transaction-stats"><article><PanelIcon name="transactions" /><span><small>Total movimientos</small><b>{data.items.length}</b></span></article><article><PanelIcon name="payments" /><span><small>Completados</small><b>{data.items.filter((row: R) => row.status === 'completed').length}</b></span></article><article><PanelIcon name="wallet" /><span><small>Pendientes</small><b>{data.items.filter((row: R) => row.status !== 'completed').length}</b></span></article></div><section className="transactions-panel"><div className="transaction-toolbar"><b>Historial de transacciones</b><div><span>Todos los tipos</span><span>Todos los estados</span></div></div><Table rows={data.items} empty="Aún no tienes movimientos. Tus operaciones aparecerán aquí." cols={[["Fecha", row => when(row.created_at)], ["Tipo", row => row.kind], ["Activo", row => <span className="asset-cell"><CryptoIcon symbol={row.currency} size={26} />{row.currency}</span>], ["Monto", row => cash(row.amount)], ["Estado", row => <span className="status-pill">{row.status}</span>]]} /></section></Shell>;
}

async function payments(csrf: string) {
  const requests = await clientGet('/api/payments/requests');
  return <Shell title="Depositar / Retirar" subtitle="Gestiona solicitudes y métodos de financiación."><div className="grid two"><Card title="Reportar depósito"><ClientActionForm action="deposit_request" csrf={csrf}><label>Moneda<input name="currency" defaultValue="USDT" /></label><label>Red<input name="network" defaultValue="TRC20" /></label><label>Monto<input name="amount" type="number" step="any" min="0" required /></label><label>Método<input name="method" defaultValue="transfer" /></label></ClientActionForm></Card><Card title="Solicitar retiro"><ClientActionForm action="withdrawal" csrf={csrf}><label>Moneda<input name="currency" defaultValue="USDT" /></label><label>Red<input name="network" defaultValue="TRC20" /></label><label>Dirección<input name="address" required /></label><label>Monto<input name="amount" type="number" step="any" min="0" required /></label></ClientActionForm></Card></div><Card title="Historial de solicitudes"><Table rows={requests.items} cols={[["Fecha", row => when(row.created_at)], ["Tipo", row => row.method], ["Monto", row => cash(row.amount_requested, row.currency)], ["Estado", row => <span className="status-pill">{row.status}</span>]]} /></Card></Shell>;
}

async function orders(csrf: string) { const rows = await clientGet('/api/orders'); return <Shell title="Órdenes" subtitle="Crea y administra tus órdenes."><div className="grid two"><Card title="Nueva orden"><ClientActionForm action="order" csrf={csrf}><label>Mercado<input name="pair" defaultValue="BTC/USDT" required /></label><label>Lado<select name="side"><option value="buy">Comprar</option><option value="sell">Vender</option></select></label><label>Cantidad<input name="qty" type="number" step="any" min="0" required /></label><label>Tipo<select name="type"><option value="market">Mercado</option><option value="limit">Límite</option></select></label><label>Precio límite<input name="price" type="number" step="any" /></label></ClientActionForm></Card><Card title="Historial"><Table rows={rows} cols={[["Par", row => row.pair], ["Lado", row => row.side], ["Cantidad", row => row.qty], ["Estado", row => row.status]]} /></Card></div></Shell>; }
async function swap(csrf: string) { const rows = await clientGet('/api/swaps'); return <Shell title="Swap" subtitle="Convierte saldos entre activos."><div className="grid two"><Card title="Nueva conversión"><ClientActionForm action="swap" csrf={csrf}><label>Desde<input name="from_currency" defaultValue="USDT" required /></label><label>Hacia<input name="to_currency" defaultValue="BTC" required /></label><label>Monto<input name="amount" type="number" step="any" min="0" required /></label></ClientActionForm></Card><Card title="Historial"><Table rows={rows} cols={[["Par", row => `${row.from_currency}/${row.to_currency}`], ["Monto", row => row.amount], ["Recibido", row => row.received_amount ?? '—']]} /></Card></div></Shell>; }
async function stake(csrf: string) { const [plans, positions] = await Promise.all([clientGet('/api/stake/plans'), clientGet('/api/stake/positions')]); return <Shell title="CDT / Stake" subtitle="Administra tus posiciones y rendimientos."><div className="grid two"><Card title="Nueva posición"><ClientActionForm action="stake" csrf={csrf}><label>Plan<select name="plan_id">{plans.map((plan: R) => <option key={plan.id} value={plan.id}>{plan.name} · {plan.apr}% APR</option>)}</select></label><label>Monto<input name="amount" type="number" step="any" min="0" required /></label></ClientActionForm></Card><Card title="Mis posiciones"><Table rows={positions} cols={[["Plan", row => row.plan_id], ["Principal", row => cash(row.principal, row.currency)], ["Estado", row => row.status]]} /></Card></div></Shell>; }
async function notifications(csrf: string) { const data = await clientGet('/api/notifications'); return <Shell title="Notificaciones" subtitle="Novedades importantes de tu cuenta.">{data.items.length ? data.items.map((item: R) => <Card key={item.id} title={item.title}><p>{item.body}</p><small>{when(item.created_at)}</small>{!item.is_read && item.user_id && <ClientActionForm compact action="notification_read" csrf={csrf} initial={{ notification_id: item.id }} label="Marcar como leído" />}</Card>) : <div className="empty-state"><span>●</span><p>No tienes notificaciones.</p></div>}</Shell>; }
async function support(csrf: string) { const data = await clientGet('/api/tickets'); return <Shell title="Tickets" subtitle="Nuestro equipo puede ayudarte."><div className="grid two"><Card title="Nuevo ticket"><ClientActionForm action="ticket" csrf={csrf}><label>Asunto<input name="subject" required /></label><label>Mensaje<textarea name="body" required /></label></ClientActionForm></Card><Card title="Mis tickets"><Table rows={data.items} empty="No tienes tickets de soporte." cols={[["Caso", row => `#${row.id}`], ["Asunto", row => row.subject], ["Estado", row => row.status], ["Fecha", row => when(row.created_at)]]} /></Card></div></Shell>; }
async function profile() { const account = await clientGet('/api/account'); return <Shell title="Ajustes" subtitle="Datos personales, identidad y seguridad."><div className="grid two"><Card title="Datos personales"><dl><dt>Nombre</dt><dd>{account.user.full_name || '—'}</dd><dt>Correo</dt><dd>{account.user.email}</dd><dt>Verificación</dt><dd>{account.user.kyc_status}</dd><dt>País</dt><dd>{account.user.country || '—'}</dd></dl></Card><Card title="Seguridad"><p>Tu sesión utiliza cookies HttpOnly, CSRF y renovación segura.</p></Card></div></Shell>; }

const views: Record<string, (csrf: string) => Promise<any>> = { dashboard:dashboard, wallets:wallets, wallet:wallets, market:market, transactions:transactions, payments:payments, orders:orders, swap:swap, stake:stake, notifications:notifications, support:support, chat:support, profile:profile, verification:profile };
export default async function Page({ params }: { params: { section?: string[] } }) {
  const key = params.section?.[0] || 'dashboard';
  if ((params.section?.length || 0) > 1) notFound();
  const view = views[key];
  if (!view) notFound();
  return view(csrfValue());
}
