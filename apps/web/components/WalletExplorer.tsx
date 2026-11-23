'use client';

import { useMemo, useState } from 'react';
import Link from 'next/link';
import { Copy, Link2, QrCode, Search } from 'lucide-react';
import { CryptoIcon } from './PanelIcons';

type Account = { id: number | string; currency: string; balance: number | string; type?: string };
type Quote = { price: number; change: number; name: string };
type Address = { currency: string; network: string; address: string; label?: string };
const amount = (value: number) => value.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 8 });

export default function WalletExplorer({ accounts, prices, addresses }: { accounts: Account[]; prices: Record<string, Quote>; addresses: Address[] }) {
  const [query, setQuery] = useState('');
  const [filter, setFilter] = useState<'all' | 'funded' | 'active'>('all');
  const [sort, setSort] = useState('featured');
  const [open, setOpen] = useState<string | null>(null);
  const [copied, setCopied] = useState('');
  const addressByCurrency = useMemo(() => Object.fromEntries(addresses.map((row) => [row.currency, row])), [addresses]);
  const rows = useMemo(() => accounts.map((account) => ({
    ...account,
    quote: prices[account.currency] || { price: 0, change: 0, name: account.currency },
    usd: Number(account.balance || 0) * Number(prices[account.currency]?.price || 0),
  })).filter((row) => `${row.currency} ${row.quote.name}`.toLowerCase().includes(query.toLowerCase()))
    .filter((row) => filter === 'all' || (filter === 'funded' ? Number(row.balance) > 0 : Boolean(addressByCurrency[row.currency])))
    .sort((a, b) => sort === 'balance' ? b.usd - a.usd : sort === 'change' ? b.quote.change - a.quote.change : 0), [accounts, prices, query, filter, sort, addressByCurrency]);

  async function copy(value: string, currency: string) {
    await navigator.clipboard.writeText(value);
    setCopied(currency);
    window.setTimeout(() => setCopied(''), 1600);
  }

  return <section className="wallet-explorer">
    <div className="wallet-explorer-head">
      <div><h2>Mis wallets</h2><p>Consulta saldos, variación y administra la recepción de tus activos.</p></div>
      <div><span><b>{accounts.length}</b> activos disponibles</span><span><b>{addresses.length}</b> wallets activas</span><span><b>{accounts.filter((row) => Number(row.balance) > 0).length}</b> con saldo</span></div>
    </div>
    <section className="deposit-addresses">
      <div className="wallet-section-title">
        <div><h3><QrCode /> Direcciones de depósito</h3><p>Usa únicamente la red indicada para enviar tus fondos.</p></div>
        <Link href="/payments">Ir a depositar</Link>
      </div>
      <div className="deposit-address-grid">
        {addresses.length === 0 && <div className="deposit-address-empty"><QrCode /><div><b>Direcciones pendientes de configurar</b><span>El administrador añadirá las redes, direcciones y códigos QR desde el panel de oficinas.</span></div></div>}
        {addresses.map((address) => <article key={`${address.currency}-${address.network}`}>
          <CryptoIcon symbol={address.currency} size={42} /><div><b>{address.currency}</b><small>{address.network}</small></div><code>{address.address}</code>
          <button type="button" onClick={() => copy(address.address, address.currency)} aria-label={`Copiar dirección ${address.currency}`}><Copy />{copied === address.currency ? 'Copiada' : 'Copiar'}</button>
        </article>)}
      </div>
    </section>
    <div className="wallet-toolbar-pro">
      <label><Search /><span className="sr-only">Buscar wallet</span><input type="search" value={query} onChange={(event) => setQuery(event.target.value)} placeholder="Buscar por moneda o nombre…" /></label>
      <div role="group" aria-label="Filtrar wallets"><button type="button" className={filter === 'all' ? 'active' : ''} onClick={() => setFilter('all')}>Todas</button><button type="button" className={filter === 'funded' ? 'active' : ''} onClick={() => setFilter('funded')}>Con saldo</button><button type="button" className={filter === 'active' ? 'active' : ''} onClick={() => setFilter('active')}>Wallet activa</button></div>
      <label><span className="sr-only">Ordenar wallets</span><select value={sort} onChange={(event) => setSort(event.target.value)}><option value="featured">Destacados</option><option value="balance">Mayor saldo</option><option value="change">Mayor subida</option></select></label>
    </div>
    <p className="wallet-result-count" aria-live="polite">Mostrando {rows.length} activos.</p>
    <div className="wallet-asset-grid">{rows.map((row) => {
      const currencyAddresses = addresses.filter((item) => item.currency === row.currency);
      const address = currencyAddresses[0];
      const expanded = open === row.currency;
      return <article key={row.id}>
        <header><CryptoIcon symbol={row.currency} size={46} /><span><b>{row.currency}</b><small>{row.quote.name}</small></span></header>
        <strong>{amount(Number(row.balance || 0))} <small>{row.currency}</small></strong>
        <div className="wallet-usd"><span>≈ ${amount(row.usd)} USD</span><small>Precio: ${amount(Number(row.quote.price || 0))}</small></div>
        <div className={`wallet-change ${row.quote.change > 0 ? 'positive' : row.quote.change < 0 ? 'negative' : ''}`}><span>VARIACIÓN 24H</span><b>{row.quote.change >= 0 ? '+' : ''}{row.quote.change.toFixed(2)}%</b></div>
        <div className="wallet-address-line"><Link2 /><code>{address?.address || 'Pendiente de configuración'}</code></div>
        <footer><Link href="/payments">Enviar</Link><button type="button" disabled={!address} onClick={() => setOpen(expanded ? null : row.currency)}>Recibir</button></footer>
        {expanded && address && <div className="wallet-address-panel"><div className="wallet-qr-placeholder"><QrCode /><span>QR pendiente</span><small>Se habilitará desde el panel administrador.</small></div><div><span>Direcciones configuradas por tu oficina</span>{currencyAddresses.map((item) => <div key={item.network}><b>{item.network}</b><code>{item.address}</code><button type="button" onClick={() => copy(item.address, `${row.currency}-${item.network}`)}><Copy />{copied === `${row.currency}-${item.network}` ? 'Copiada' : 'Copiar dirección'}</button></div>)}</div></div>}
      </article>;
    })}</div>
  </section>;
}
