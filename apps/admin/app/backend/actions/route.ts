import { NextRequest,NextResponse } from 'next/server';
import { accessToken,apiFetch,refreshTokens,setTokens,validCsrf } from '../../../lib/session';
export async function POST(request:NextRequest){
 if(!validCsrf(request,request.headers.get('x-csrf-token')||''))return NextResponse.json({detail:'Confirmación CSRF inválida'},{status:403});
 const raw=await request.text();const key=request.headers.get('idempotency-key');
 if(!key||key.length>128)return NextResponse.json({detail:'Idempotency-Key requerido'},{status:400});
 const options={method:'POST',body:raw,headers:{'Idempotency-Key':key}};
 let response=await apiFetch('/api/admin/actions',accessToken(),options);
 let tokens=null;
 if(response.status===401){tokens=await refreshTokens();if(tokens)response=await apiFetch('/api/admin/actions',tokens.access_token,options);}
 const result=new NextResponse(await response.text(),{status:response.status,headers:{'Content-Type':'application/json','Cache-Control':'no-store'}});
 if(tokens)setTokens(result,tokens);
 return result;
}
