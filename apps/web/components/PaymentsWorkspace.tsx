'use client';

import { useState } from 'react';
import BankMethodForm from './BankMethodForm';
import ClientActionForm from './ClientActionForm';
import { PanelIcon } from './PanelIcons';

type Row = Record<string, any>;
const currencies = ['USDT', 'USDC', 'BNB', 'BTC'];
const networks = ['TRC20', 'ERC20', 'BEP20', 'POLYGON', 'SOLANA'];

function describe(row: Row) {
  if (row.type === 'bank') return `${row.bank_name || 'Banco'} ••••${row.account_last4 || ''}`;
  if (row.type === 'card') return `${row.card_brand || 'Tarjeta'} ••••${row.card_last4 || ''}`;
  return `${row.network || 'Red'} · ${row.wallet_address || 'Wallet'}`;
}

export default function PaymentsWorkspace({ csrf, methods, requests }: { csrf: string; methods: Row[]; requests: Row[] }) {
  const [methodType, setMethodType] = useState<'bank'|'card'|'crypto'>('bank');
  const [withdrawType, setWithdrawType] = useState<'bank'|'card'|'crypto'>('crypto');
  const destinations = methods.filter((row) => row.type === withdrawType);
  return <>
    <section className="payment-workspace-grid">
      <article className="card payment-method-panel">
        <h2><PanelIcon name="payments"/> Métodos de pago</h2>
        <span className="field-caption">Método de pago</span>
        <div className="payment-method-picker" role="tablist">
          {([['bank','Banco'],['card','Tarjeta'],['crypto','Cripto']] as const).map(([key,label]) => <button type="button" role="tab" aria-selected={methodType===key} className={methodType===key?'active':''} onClick={()=>setMethodType(key)} key={key}>{label}</button>)}
        </div>
        <div className="payment-method-fields">
          {methodType === 'bank' && <BankMethodForm csrf={csrf}/>} 
          {methodType === 'card' && <ClientActionForm action="payment_method_create" csrf={csrf} initial={{type:'card'}} label="Agregar método"><label>Número de tarjeta<input name="card_number_display" inputMode="numeric" placeholder="0000 0000 0000 0000" required /></label><div className="form-row"><label>Fecha de caducidad<input name="card_expiry_display" placeholder="MM/AA" required /></label><label>CVV<input name="card_cvv_display" placeholder="•••" required /></label></div><input type="hidden" name="label" value="Mi tarjeta"/><input type="hidden" name="holder_name" value="Titular"/><input type="hidden" name="card_brand" value="Tarjeta"/><label>Últimos 4 dígitos<input name="card_last4" pattern="[0-9]{4}" maxLength={4} required/></label></ClientActionForm>}
          {methodType === 'crypto' && <ClientActionForm action="payment_method_create" csrf={csrf} initial={{type:'crypto',label:'Wallet cripto',holder_name:'Titular'}} label="Agregar método"><div className="form-row"><label>Moneda<select name="crypto_currency">{currencies.map(x=><option key={x}>{x}</option>)}</select></label><label>Red<select name="network">{networks.map(x=><option key={x}>{x}</option>)}</select></label></div><label>Billetera asignada en esta red<input name="wallet_address" placeholder="Selecciona moneda y red..." required/></label></ClientActionForm>}
        </div>
        <div className="linked-payment-methods">{methods.length ? methods.map(row=><span key={row.id}>{row.label} · {describe(row)}</span>) : <div className="payment-empty"><PanelIcon name="wallet"/><p>Sin métodos registrados aún.</p></div>}</div>
      </article>
      <article className="card withdrawal-panel">
        <h2>↓ Operaciones</h2>
        <div className="withdrawal-box"><h3>↓ Solicitar retiro</h3><p>Retira desde tu saldo vía cripto, banco o tarjeta. El equipo de tu oficina revisará la solicitud.</p>
          <span className="field-caption">Cómo quieres retirar</span>
          <div className="payment-method-picker compact">{(['crypto','bank','card'] as const).map(key=><button type="button" className={withdrawType===key?'active':''} onClick={()=>setWithdrawType(key)} key={key}>{key==='crypto'?'Cripto':key==='bank'?'Banco':'Tarjeta'}</button>)}</div>
          <ClientActionForm action="withdrawal" csrf={csrf} label="↓ Solicitar retiro">
            <label>Moneda (wallet a debitar)<select name="currency">{currencies.map(x=><option value={x} key={x}>{x} — saldo 0.0000</option>)}</select></label>
            <label>Monto<input name="amount" type="number" min="0.00000001" step="0.00000001" placeholder="Mín. ~$20 USD" required/></label>
            {withdrawType === 'crypto' ? <>
              <label>Red<select name="network" defaultValue="TRC20">{networks.map(x=><option value={x} key={x}>{x}</option>)}</select></label>
              <label>Dirección destino<input name="destination_address" autoComplete="off" placeholder="Pega la dirección de destino" minLength={6} required/></label>
            </> : <label>{withdrawType === 'bank' ? 'Cuenta bancaria destino' : 'Tarjeta destino'}<select name="payment_method_id" required defaultValue=""><option value="" disabled>— Selecciona un método —</option>{destinations.map(row=><option value={row.id} key={row.id}>{row.label} · {describe(row)}</option>)}</select></label>}
            <label>Notas (opcional)<textarea name="notes" placeholder="Observaciones del retiro"/></label>
          </ClientActionForm>
        </div>
      </article>
    </section>
    <section className="card payment-history"><h2>↶ Historial de solicitudes</h2>{requests.length?<div className="table-wrap"><table><thead><tr><th>Tipo</th><th>Moneda</th><th>Canal</th><th>Monto</th><th>Estado</th><th>Nota / motivo</th><th>Fecha</th></tr></thead><tbody>{requests.map(row=><tr key={row.id}><td>{String(row.method).includes('withdrawal')?'Retiro':'Depósito'}</td><td>{row.currency}</td><td>{row.payment_method_id?`#${row.payment_method_id}`:'—'}</td><td>{row.amount_requested}</td><td>{row.status}</td><td>{row.staff_note||'—'}</td><td>{row.created_at?new Date(row.created_at).toLocaleString('es-CO'):'—'}</td></tr>)}</tbody></table></div>:<div className="payment-empty"><PanelIcon name="wallet"/><p>Aún no has hecho solicitudes.</p></div>}</section>
  </>;
}
