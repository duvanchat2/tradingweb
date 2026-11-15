import { NextRequest,NextResponse } from 'next/server';
import { ensureCsrf } from '../../../lib/session';
export const dynamic='force-dynamic';
export async function GET(request:NextRequest){
 if(request.headers.get('sec-fetch-site')==='cross-site')return NextResponse.json({error:'Solicitud no permitida'},{status:403});
 const response=NextResponse.json({});const token=ensureCsrf(response);
 return new NextResponse(JSON.stringify({csrf:token}),{headers:{'Content-Type':'application/json','Cache-Control':'no-store','Set-Cookie':response.headers.get('set-cookie')||''}});
}
