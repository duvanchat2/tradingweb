import ClientActionForm from './ClientActionForm';
import {PanelIcon} from './PanelIcons';

type Document={doc_type:string;status:string;review_note?:string|null};
type Data={status:string;documents:Document[]};
const kinds:Record<string,{title:string;description:string;icon:string}>={
  id_front:{title:'Identificación — frente',description:'Foto clara del anverso de tu documento de identidad.',icon:'verification'},
  id_back:{title:'Identificación — reverso',description:'Foto clara del reverso de tu documento.',icon:'verification'},
  proof_address:{title:'Comprobante de domicilio',description:'Recibo de servicios o extracto bancario reciente (máximo 3 meses).',icon:'payments'},
  selfie:{title:'Selfie con documento',description:'Sostén tu documento junto a tu rostro. Ambos deben verse claramente.',icon:'dashboard'},
};
const statuses:Record<string,string>={none:'Sin enviar',pending:'En revisión',verified:'Verificado',rejected:'Requiere corrección'};
export default function VerificationWorkspace({csrf,data}:{csrf:string;data:Data}){
  const complete=data.documents.length===4&&data.documents.every(doc=>doc.status==='pending'||doc.status==='approved');
  const reviewing=data.status==='pending';
  return <div className="verification-page">
    <header className="verification-hero"><PanelIcon name="verification"/><div><h1>Verificación de identidad (KYC)</h1><p>Sube tu identificación por ambos lados, un comprobante de domicilio y una selfie con tu documento.</p></div><strong>{statuses[data.status]||data.status}</strong></header>
    <div className="verification-steps"><span className={data.status==='none'?'active':''}><b>1</b>Enviar documentos</span><span className={reviewing?'active':''}><b>2</b>En revisión</span><span className={data.status==='verified'?'active':''}><b>3</b>Verificado</span></div>
    <section className="verification-card"><h2>Subir documentos</h2><p className="verification-hint">Necesitamos cuatro imágenes: frente y reverso de tu identificación, comprobante de domicilio y selfie sosteniendo el documento. JPG, PNG o WebP; máximo 5 MB por archivo.</p>
      <div className="verification-documents">{data.documents.map(doc=>{const kind=kinds[doc.doc_type];return <article key={doc.doc_type} className={doc.status==='rejected'?'rejected':''}><PanelIcon name={kind?.icon||'verification'}/><div><h3>{kind?.title||doc.doc_type}</h3><p>{kind?.description}</p><small>{doc.status==='missing'?'Toca para seleccionar archivo':doc.status==='pending'?'Archivo guardado':doc.status==='approved'?'Aprobado':'Rechazado: vuelve a subirlo'}</small>{doc.review_note&&<small className="verification-note">Nota de la oficina: {doc.review_note}</small>}</div><form action="/app/backend/kyc" method="post" encType="multipart/form-data"><input type="hidden" name="_csrf" value={csrf}/><input type="hidden" name="doc_type" value={doc.doc_type}/><label>Subir<input type="file" name="file" accept="image/jpeg,image/png,image/webp" required/></label><button type="submit">Guardar</button></form></article>})}</div>
      {complete&&!reviewing&&data.status!=='verified'?<ClientActionForm action="kyc_submit" csrf={csrf} label="Enviar verificación" compact/>:<button className="verification-submit-disabled" type="button" disabled>{reviewing?'En revisión':data.status==='verified'?'Verificado':'Completa los cuatro archivos para continuar'}</button>}
      <p className="verification-tip">{reviewing?'Tu oficina está revisando tus documentos.':'Guarda los cuatro archivos antes de enviar la verificación.'}</p>
    </section>
  </div>;
}
