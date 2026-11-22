'use client';

import { useState } from 'react';
import ClientActionForm from './ClientActionForm';
import { CryptoIcon } from './PanelIcons';

type Row=Record<string,any>;
const cash=(value:any,currency='')=>`${Number(value||0).toLocaleString('es-CO',{maximumFractionDigits:8})}${currency?` ${currency}`:''}`;

export default function StakeWorkspace({csrf,plans,positions,balances}:{csrf:string;plans:Row[];positions:Row[];balances:Record<string,number>}){
 const [tab,setTab]=useState<'plans'|'mine'>('plans');
 return <section className="stake-workspace"><div className="stake-tabs" role="tablist"><button type="button" className={tab==='plans'?'active':''} onClick={()=>setTab('plans')}>Planes CDT <i>{plans.length}</i></button><button type="button" className={tab==='mine'?'active':''} onClick={()=>setTab('mine')}>Mis CDT <i>{positions.length}</i></button></div>
 {tab==='plans'?<div className="stake-plan-grid">{plans.map(plan=>{const available=Number(balances[plan.currency]||0);const period=Number(plan.apy)*Number(plan.term_days)/365;return <article key={plan.id}><header><CryptoIcon symbol={plan.currency} size={42}/><div><h3>{plan.currency} {plan.term_days}D</h3><span>{plan.term_days} días</span></div></header><strong>{Number(plan.apy).toFixed(2)}<small>% APY</small></strong><p>Rendimiento del periodo: <b>{period.toFixed(2)}%</b></p><dl><dt>Moneda</dt><dd>{plan.currency}</dd><dt>Disponible</dt><dd>{cash(available,plan.currency)}</dd><dt>Mínimo</dt><dd>{cash(plan.min_amount,plan.currency)}</dd></dl><ClientActionForm action="stake" csrf={csrf} initial={{plan_id:plan.id}} label="Abrir CDT"><label>Programa tu inversión<input name="amount" type="number" step="0.00000001" min={plan.min_amount} max={available} placeholder={`Mínimo ${plan.min_amount}`} required/></label></ClientActionForm>{available<Number(plan.min_amount)&&<small className="plan-warning">Necesitas al menos {cash(plan.min_amount,plan.currency)} disponibles.</small>}</article>})}</div>:<div className="my-stakes">{positions.length?<div className="table-wrap"><table><thead><tr><th>Solicitud</th><th>Plan</th><th>Principal</th><th>Estado</th><th>Apertura</th><th>Nota</th></tr></thead><tbody>{positions.map(row=><tr key={row.id}><td>#{row.id}</td><td>#{row.plan_id}</td><td>{row.amount}</td><td>{row.status}</td><td>{row.opened_at||'—'}</td><td>{row.staff_note||'—'}</td></tr>)}</tbody></table></div>:<div className="empty-state"><span>◉</span><p>Aún no tienes CDT. Elige un plan para comenzar.</p></div>}</div>}</section>
}
