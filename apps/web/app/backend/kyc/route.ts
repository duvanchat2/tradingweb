import { NextRequest, NextResponse } from 'next/server';
import { API, accessToken, validCsrf } from '../../../lib/session';
export async function POST(request:NextRequest){
  const form=await request.formData();
  if(!validCsrf(request,String(form.get('_csrf')||'')))return NextResponse.json({detail:'Confirmación CSRF inválida'},{status:403});
  const docType=String(form.get('doc_type')||'');const file=form.get('file');
  if(!['id_front','id_back','proof_address','selfie'].includes(docType)||!(file instanceof File))return NextResponse.json({detail:'Documento inválido'},{status:422});
  const upstream=new FormData();upstream.set('file',file);
  const response=await fetch(`${API}/api/kyc/documents/${docType}`,{method:'POST',cache:'no-store',headers:{Authorization:`Bearer ${accessToken()}`,'X-Demo-Confirm':'true'},body:upstream});
  if(!response.ok)return NextResponse.json({detail:'No se pudo guardar el documento'},{status:response.status});
  return NextResponse.redirect(new URL('/app/verification',request.url),303);
}
