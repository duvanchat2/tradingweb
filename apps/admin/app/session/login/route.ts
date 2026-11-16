import { NextRequest,NextResponse } from 'next/server';
import { apiFetch,setTokens,validCsrf,publicURL } from '../../../lib/session';
export async function POST(request:NextRequest){
 const form=await request.formData();
 if(!validCsrf(request,String(form.get('_csrf')||'')))return NextResponse.json({error:'Solicitud no permitida'},{status:403});
 let response;
 try{response=await apiFetch('/api/auth/login',undefined,{method:'POST',body:JSON.stringify({email:form.get('email'),password:form.get('password')})});}
 catch{return NextResponse.redirect(publicURL(request,'/admin/login?error=unavailable'),303);}
 if(!response.ok)return NextResponse.redirect(publicURL(request,'/admin/login?error=invalid'),303);
 const tokens=await response.json();const me=await apiFetch('/api/auth/me',tokens.access_token);
 const user=me.ok?await me.json():null;
 if(!user||!['staff','superworker'].includes(user.role)){
  await apiFetch('/api/auth/logout',tokens.access_token,{method:'POST'});
  return NextResponse.redirect(publicURL(request,'/admin/login?error=staff'),303);
 }
 const result=NextResponse.redirect(publicURL(request,'/admin/dashboard'),303);setTokens(result,tokens);return result;
}
