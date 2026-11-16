'use client';
import { FormEvent,ReactNode,useRef,useState } from 'react';
import { useRouter } from 'next/navigation';
export default function ActionForm({action,csrf,children,label='Guardar',initial={}}:{action:string;csrf:string;children:ReactNode;label?:string;initial?:Record<string,unknown>}){
 const [busy,setBusy]=useState(false),[message,setMessage]=useState(''),[error,setError]=useState(false);
 const request=useRef({payload:'',key:''});const router=useRouter();
 async function submit(event:FormEvent<HTMLFormElement>){
  event.preventDefault();if(busy)return;
  const form=event.currentTarget;const values:Record<string,unknown>={action,...initial};
  new FormData(form).forEach((value,key)=>{values[key]=value;});
  for(const field of ['wallet_id','user_id','document_id','request_id','transaction_id'])if(values[field]!==undefined&&values[field]!=='')values[field]=Number(values[field]);else delete values[field];
  if(values.is_active!==undefined)values.is_active=values.is_active==='true';
  for(const field of ['amount','kyc_filter'])if(values[field]==='')delete values[field];
  const payload=JSON.stringify(values);
  if(request.current.payload!==payload)request.current={payload,key:'admin-'+Array.from(crypto.getRandomValues(new Uint8Array(16)),v=>v.toString(16).padStart(2,'0')).join('')};
  setBusy(true);setMessage('');setError(false);
  try{
   const response=await fetch('/admin/backend/actions',{method:'POST',headers:{'Content-Type':'application/json','X-CSRF-Token':csrf,'Idempotency-Key':request.current.key},body:payload});
   const result=await response.json();
   if(!response.ok){setError(true);setMessage(typeof result.detail==='string'?result.detail:'Revisa los campos e intenta de nuevo.');}
   else{setMessage(result.replayed?'La operación ya estaba aplicada; no se duplicó.':'Operación demo guardada.');router.refresh();}
  }catch{setError(true);setMessage('No se pudo confirmar la respuesta. Reintenta sin cambiar el formulario para conservar la misma operación.');}
  finally{setBusy(false);}
 }
 return <form className="form-grid" onSubmit={submit} onReset={()=>{request.current={payload:'',key:''};setMessage('');}}>
  {children}<div className="form-actions"><button disabled={busy} type="submit">{busy?'Guardando…':label}</button><button type="reset" className="secondary" disabled={busy}>Nueva operación</button></div>
  {message&&<p role="status" className={'notice '+(error?'error':'success')}>{message}</p>}
 </form>;
}
