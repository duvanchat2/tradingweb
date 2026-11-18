import type { ReactNode } from 'react';
import Link from 'next/link';
import { notFound } from 'next/navigation';
import ClientActionForm from '../../../components/ClientActionForm';
import { clientGet, csrfValue } from '../../../lib/session';

type R = Record<string, any>;
const cash = (value: any, currency = '') => `${Number(value || 0).toLocaleString('es-CO', { maximumFractionDigits: 8 })}${currency ? ` ${currency}` : ''}`;
const when = (value: any) => value ? new Date(value).toLocaleString('es-CO') : '—';
function priceRows(payload: R): R[] {
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
  return <div className="wallet-grid">{accounts.map(account => <article className="wallet-card" key={account.id}><div className="asset-mark">{String(account.currency).slice(0, 1)}</div><div><strong>{account.currency}</strong><small>{account.type === 'main' ? 'Wallet principal' : account.type}</small></div><b>{cash(account.balance, account.currency)}</b></article>)}</div>;
}

async function dashboard() {
  const [account, marketData, transactions] = await Promise.all([clientGet('/api/account'), clientGet('/api/market/prices'), clientGet('/api/account/transactions?limit=8')]);
  const prices = priceRows(marketData);
  const nonZero = account.accounts.filter((item: R) => Number(item.balance) !== 0).length;
  return <Shell title={`Hola, ${account.user.full_name || 'inversionista'}`} subtitle="Controla tus activos y operaciones desde un solo lugar." action={<Link className="primary-link" href="/payments">Depositar fondos</Link>}>
    <section className="portfolio-hero"><div><span>Balance de tus wallets</span><strong>{account.accounts.length} activos</strong><small>{nonZero ? `${nonZero} con saldo disponible` : 'Tus cuentas están listas para operar'}</small></div><div className="portfolio-orb">GE</div></section>
    <div className="quick-actions"><Link href="/payments"><span>↓</span><b>Depositar</b></Link><Link href="/payments"><span>↑</span><b>Retirar</b></Link><Link href="/swap"><span>⇄</span><b>Swap</b></Link><Link href="/stake"><span>◇</span><b>CDT</b></Link><Link href="/orders"><span>↗</span><b>Operar</b></Link></div>
    <div className="dashboard-grid"><Card title="Mis activos" className="dashboard-assets"><BalanceGrid accounts={account.accounts.slice(0, 5)} /><Link className="card-link" href="/wallets">Ver todas las wallets →</Link></Card><Card title="Mercado en vivo"><Table rows={prices.slice(0, 5)} empty="No hay precios disponibles." cols={[["Activo", row => row.symbol || row.pair], ["Precio", row => cash(row.price)], ["24 h", row => <span className={Number(row.change_24h) >= 0 ? 'positive' : 'negative'}>{row.change_24h ?? '—'}%</span>]]} /><Link className="card-link" href="/market">Ver mercado →</Link></Card></div>
    <Card title="Movimientos recientes"><Table rows={transactions.items} cols={[["Fecha", row => when(row.created_at)], ["Concepto", row => row.kind], ["Monto", row => cash(row.amount, row.currency)], ["Estado", row => <span className="status-pill">{row.status}</span>]]} /><Link className="card-link" href="/transactions">Ver todos los movimientos →</Link></Card>
  </Shell>;
}

async function wallets() {
  const [account, addresses] = await Promise.all([clientGet('/api/account'), clientGet('/api/payments/deposit-wallets')]);
  return <Shell title="Mis wallets" subtitle="Consulta tus balances y direcciones por moneda." action={<Link className="primary-link" href="/payments">Depositar / Retirar</Link>}><BalanceGrid accounts={account.accounts} /><Card title="Direcciones de recepción"><Table rows={addresses} empty="No hay direcciones disponibles." cols={[["Moneda", row => row.currency], ["Red", row => row.network], ["Dirección", row => <code>{row.address}</code>]]} /></Card></Shell>;
}

async function market() {
  const marketData = await clientGet('/api/market/prices');
  const prices = priceRows(marketData);
  return <Shell title="Mercado" subtitle="Precios actualizados de los activos disponibles."><Card title="Precios del mercado"><Table rows={prices} empty="No hay cotizaciones disponibles." cols={[["Activo", row => row.symbol || row.pair], ["Último precio", row => cash(row.price)], ["Cambio 24 h", row => <span className={Number(row.change_24h) >= 0 ? 'positive' : 'negative'}>{row.change_24h ?? '—'}%</span>]]} /></Card></Shell>;
}

async function transactions() {
  const data = await clientGet('/api/account/transactions?limit=100');
  return <Shell title="Movimientos" subtitle="Historial de actividad de tus wallets."><Card title="Historial de transacciones"><Table rows={data.items} cols={[["Fecha", row => when(row.created_at)], ["Concepto", row => row.kind], ["Moneda", row => row.currency], ["Monto", row => cash(row.amount)], ["Estado", row => <span className="status-pill">{row.status}</span>]]} /></Card></Shell>;
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

const views: Record<string, (csrf: string) => Promise<any>> = { dashboard:dashboard, wallets:wallets, wallet:wallets, market:market, transactions:transactions, payments:payments, orders:orders, swap:swap, stake:stake, notifications:notifications, support:support, profile:profile };
export default async function Page({ params }: { params: { section?: string[] } }) {
  const key = params.section?.[0] || 'dashboard';
  if ((params.section?.length || 0) > 1) notFound();
  const view = views[key];
  if (!view) notFound();
  return view(csrfValue());
}
