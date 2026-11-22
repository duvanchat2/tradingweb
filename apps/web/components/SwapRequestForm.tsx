'use client';

import { useMemo, useState } from 'react';
import ClientActionForm from './ClientActionForm';
import { PanelIcon } from './PanelIcons';

const currencies=['BTC','ETH','USDT','USDC','BNB','XRP','SOL','TRX','DOGE'];

export default function SwapRequestForm({csrf,balances,prices}:{csrf:string;balances:Record<string,number>;prices:Record<string,number>}){
  const [from,setFrom]=useState('BTC');const [to,setTo]=useState('ETH');const [amount,setAmount]=useState('');
  const available=Number(balances[from]||0);
  const output=useMemo(()=>{const value=Number(amount||0);const a=prices[from]||0;const b=prices[to]||0;return value>0&&a>0&&b>0?value*(1-.001)*a/b:0},[amount,from,to,prices]);
  function portion(value:number){setAmount((available*value).toFixed(8).replace(/\.?0+$/,''))}
  return <ClientActionForm action="swap" csrf={csrf} label="Solicitar intercambio">
    <div className="swap-leg"><label>Desde<select name="from_currency" value={from} onChange={e=>setFrom(e.target.value)}>{currencies.map(x=><option key={x} value={x}>{x} ({Number(balances[x]||0).toFixed(4)})</option>)}</select><small>Saldo disponible: {available.toFixed(8)} {from}</small></label><label>Monto<input name="amount" type="number" step="0.00000001" min="0.00000001" value={amount} onChange={e=>setAmount(e.target.value)} placeholder="0.00" required/></label></div>
    <div className="amount-presets" aria-label="Porcentaje del saldo"><button type="button" onClick={()=>portion(.25)}>25%</button><button type="button" onClick={()=>portion(.5)}>50%</button><button type="button" onClick={()=>portion(.75)}>75%</button><button type="button" onClick={()=>portion(1)}>Máx</button></div>
    <div className="swap-divider"><PanelIcon name="swap"/><span>Comisión 0.1%</span></div>
    <div className="swap-leg"><label>Hacia<select name="to_currency" value={to} onChange={e=>setTo(e.target.value)}>{currencies.filter(x=>x!==from).map(x=><option key={x} value={x}>{x}</option>)}</select></label><label>Recibirás aproximadamente<input value={output.toFixed(8)} readOnly/></label></div>
  </ClientActionForm>
}
