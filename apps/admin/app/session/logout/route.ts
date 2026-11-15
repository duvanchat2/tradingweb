import { NextRequest,NextResponse } from 'next/server';
import { accessToken,apiFetch,clearTokens,validCsrf,publicURL,refreshTokens } from '../../../lib/session';
export async function POST(request:NextRequest){
 const form=await request.formData();
 if(!validCsrf(request,String(form.get('_csrf')||'')))return NextResponse.json({error:'Solicitud no permitida'},{status:403});
 const token=accessToken();
 const result=token?await apiFetch('/api/auth/logout',token,{method:'POST'}).catch(()=>null):null;
 if(!result||result.status===401){const tokens=await refreshTokens().catch(()=>null);if(tokens)await apiFetch('/api/auth/logout',tokens.access_token,{method:'POST'}).catch(()=>null);}
 const response=NextResponse.redirect(publicURL(request,'/admin/login'),303);clearTokens(response);return response;
}
