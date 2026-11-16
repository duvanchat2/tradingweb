import { NextRequest,NextResponse } from 'next/server';
import { apiFetch,publicURL,validCsrf } from '../../../lib/session';

export async function POST(request:NextRequest){
 const form=await request.formData();
 if(!validCsrf(request,String(form.get('_csrf')||'')))return NextResponse.json({error:'Solicitud no permitida'},{status:403});
 const full_name=String(form.get('full_name')||'').trim();const email=String(form.get('email')||'').trim();const password=String(form.get('password')||'');
 const fail=(error:string)=>NextResponse.redirect(publicURL(request,'/app/register?error='+error),303);
 if(password!==String(form.get('password_confirm')||'')||password.length<12||password.length>128)return fail('password');
 if(!full_name||full_name.length>200||!email||email.length>254)return fail('invalid');
 try{
  const response=await apiFetch('/api/auth/register',undefined,{method:'POST',body:JSON.stringify({full_name,email,password})});
  if(response.status===409)return fail('exists');
  if(response.status===422)return fail('invalid');
  if(!response.ok)return fail('unavailable');
 }catch{return fail('unavailable');}
 const response=NextResponse.redirect(publicURL(request,'/app/login?registered=1'),303);
 response.headers.set('Cache-Control','no-store');return response;
}
