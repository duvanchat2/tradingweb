import { NextRequest,NextResponse } from 'next/server';
import { accessToken,apiFetch,refreshTokens,setTokens,validCsrf } from '../../../lib/session';
export async function POST(request:NextRequest){
 if(!validCsrf(request,request.headers.get('x-csrf-token')||''))return NextResponse.json({detail:'Confirmación CSRF inválida'},{status:403});
 const raw=await request.text();const key=request.headers.get('idempotency-key');
 if(!key||key.length>128)return NextResponse.json({detail:'Idempotency-Key requerido'},{status:400});
 let path='/api/admin/actions';let method:'POST'|'PATCH'|'DELETE'='POST';let body=raw;const parsed=JSON.parse(raw);
 if(parsed.action==='office_create'){path='/api/admin/offices';body=JSON.stringify({name:parsed.name});}
 if(parsed.action==='office_features'){path=`/api/admin/offices/${Number(parsed.office_id)}`;method='PATCH';body=JSON.stringify({trading_enabled:parsed.trading_enabled,swap_enabled:parsed.swap_enabled,withdrawals_enabled:parsed.withdrawals_enabled});}
 if(parsed.action==='office_admin_create'){path='/api/admin/office-admins';body=JSON.stringify({office_id:Number(parsed.office_id),email:parsed.email,full_name:parsed.full_name,password:parsed.password});}
 if(parsed.action==='office_delete'){path=`/api/admin/offices/${Number(parsed.office_id)}`;method='DELETE';body='';}
 const options={method,body:body||undefined,headers:{'Idempotency-Key':key}};
 let response=await apiFetch(path,accessToken(),options);
 let tokens=null;
 if(response.status===401){tokens=await refreshTokens();if(tokens)response=await apiFetch(path,tokens.access_token,options);}
 const result=new NextResponse(await response.text(),{status:response.status,headers:{'Content-Type':'application/json','Cache-Control':'no-store'}});
 if(tokens)setTokens(result,tokens);
 return result;
}
