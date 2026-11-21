import { NextRequest, NextResponse } from 'next/server';
import { API, accessToken } from '../../../../lib/session';
export async function GET(_request:NextRequest,{params}:{params:{id:string}}){
  if(!/^\d+$/.test(params.id))return NextResponse.json({detail:'Documento inválido'},{status:422});
  const response=await fetch(`${API}/api/admin/kyc/documents/${params.id}/image`,{cache:'no-store',headers:{Authorization:`Bearer ${accessToken()}`,'X-Demo-Confirm':'true'}});
  if(!response.ok)return NextResponse.json({detail:'Imagen no disponible'},{status:response.status});
  return new NextResponse(await response.arrayBuffer(),{status:200,headers:{'Content-Type':response.headers.get('content-type')||'application/octet-stream','Cache-Control':'no-store'}});
}
