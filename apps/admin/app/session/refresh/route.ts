import { NextRequest,NextResponse } from 'next/server';
import { refreshTokens,setTokens,clearTokens,publicURL } from '../../../lib/session';
export const dynamic='force-dynamic';
export async function GET(request:NextRequest){
 if(request.headers.get('sec-fetch-site')==='cross-site')return NextResponse.json({error:'Solicitud no permitida'},{status:403});
 const target=request.nextUrl.searchParams.get('next')||'/admin/dashboard';
 const safe=target.startsWith('/admin/')&&!target.startsWith('/admin/session/')&&!target.includes('\\')&&!target.includes('\n')?target:'/admin/dashboard';
 const tokens=await refreshTokens().catch(()=>null);
 const response=NextResponse.redirect(publicURL(request,tokens?safe:'/admin/login'),303);
 if(tokens)setTokens(response,tokens);else clearTokens(response);
 return response;
}
