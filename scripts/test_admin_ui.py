"""Optional local browser smoke: requires Playwright + Chromium, a seeded demo API.

Only synthetic balances are used. Creates one withdrawal and reverses its
balance effect with a documented virtual credit. Does not contact any chain.
"""
from pathlib import Path
from decimal import Decimal
import json,os,time,urllib.request,urllib.parse
from playwright.sync_api import sync_playwright,expect
root=Path(__file__).resolve().parents[1]
values=dict(line.split('=',1) for line in (root/'infra/.env').read_text().splitlines() if line and not line.startswith('#') and '=' in line)
base=os.environ.get('ADMIN_URL','http://127.0.0.1:3040')
api=os.environ.get('API_URL','http://127.0.0.1:8000')
password=values['SEED_PASSWORD']
def request(method,path,body=None,token=None):
 headers={'X-Demo-Confirm':'true','Content-Type':'application/json'}
 if token:headers['Authorization']='Bearer '+token
 req=urllib.request.Request(api+path,data=json.dumps(body).encode() if body is not None else None,method=method,headers=headers)
 with urllib.request.urlopen(req,timeout=20) as response:return json.load(response) if response.status!=204 else None
client_tokens=request('POST','/api/auth/login',{'email':'client1@demo.example.com','password':password})
staff_tokens=request('POST','/api/auth/login',{'email':'staff@demo.example.com','password':password})
me=request('GET','/api/auth/me',token=client_tokens['access_token'])
with sync_playwright() as p:
 args=['--no-sandbox','--disable-dev-shm-usage']
 if os.environ.get('ADMIN_RESOLVE_IP'):args.append('--host-resolver-rules=MAP '+str(urllib.parse.urlparse(base).hostname)+' '+os.environ['ADMIN_RESOLVE_IP'])
 local_proxy=None
 if os.environ.get('ADMIN_RESOLVE_IP') and os.environ.get('HTTP_PROXY'):
  local_proxy={'server':os.environ['HTTP_PROXY'],'bypass':'localhost,127.0.0.1,'+str(urllib.parse.urlparse(base).hostname)}
 browser=p.chromium.launch(executable_path=os.environ.get('CHROMIUM_PATH','/usr/bin/chromium'),headless=True,args=args,proxy=local_proxy)
 context=browser.new_context(viewport={'width':1440,'height':1000})
 page=context.new_page();errors=[];page.on('pageerror',lambda error:errors.append(str(error)))
 page.goto(base+'/admin/payments');page.wait_for_url('**/admin/login')
 page.get_by_label('Correo del equipo').fill('staff@demo.example.com')
 page.get_by_label('Contraseña',exact=True).fill(password)
 page.get_by_role('button',name='Entrar al back-office').click()
 page.wait_for_url('**/admin/dashboard')
 expect(page.get_by_role('heading',name='Resumen',exact=True)).to_be_visible()
 assert all(cookie['httpOnly'] for cookie in context.cookies() if cookie['name'].startswith('tw_admin_'))
 assert page.evaluate('localStorage.length')==0
 print('PASS browser: staff login, HttpOnly session, no localStorage token')
 for route,title in [('dashboard','Resumen'),('users','Usuarios'),('production','Producción'),('notifications','Notificaciones'),('kyc','KYC / Documentos'),('payments','Pagos'),('cards','Tarjetas'),('swaps','Swaps'),('credit','Agregar fondos'),('deposit-wallets','Wallets depósito'),('stake-plans','Planes stake'),('chats','Chats'),('tickets','Tickets'),('help','Centro de ayuda'),('ranking','Ranking')]:
  response=page.goto(base+'/admin/'+route)
  assert response.status==200,(route,response.status)
  expect(page.get_by_role('heading',name=title,exact=True)).to_be_visible()
  expect(page.get_by_role('status').filter(has_text='Entorno de simulación')).to_be_visible()
 print('PASS browser: all 15 routes render server-side with demo banner')
 request_headers={'Origin':base}
 if os.environ.get('ADMIN_REQUEST_HOST'):request_headers['Host']=os.environ['ADMIN_REQUEST_HOST']
 rejected=context.request.post(os.environ.get('ADMIN_REQUEST_URL',base)+'/admin/backend/actions',headers=request_headers,data={'action':'credit'})
 assert rejected.status==403
 print('PASS browser: mutation without CSRF rejected with 403')
 withdrawal=request('POST','/api/payments/withdrawal-request',{'currency':'USDT','amount':'1','network':'DEMO','address':'synthetic-browser-test'},client_tokens['access_token'])
 page.goto(base+'/admin/payments')
 card=page.locator('article.card').filter(has=page.get_by_role('heading',name=f'Solicitud #{withdrawal["id"]} · USDT',exact=True))
 expect(card.get_by_text('Ejecución simulada — sin envío on-chain',exact=True)).to_be_visible()
 card.get_by_label('Nota del equipo').fill('Synthetic browser approval; no on-chain execution')
 card.get_by_role('button',name='Guardar revisión',exact=True).click()
 for _ in range(40):
  rows=request('GET','/api/admin/payments?status=approved',token=staff_tokens['access_token'])['items']
  if any(row['id']==withdrawal['id'] for row in rows):break
  time.sleep(.15)
 else:raise AssertionError('UI approval did not reach API')
 print('PASS browser: withdrawal warning and simulated approval')
 page.goto(base+'/admin/credit')
 page.get_by_label('Usuario (ID, correo o referido)').fill(str(me['id']))
 page.get_by_label('Importe',exact=True).fill('1')
 page.get_by_label('Nota del equipo').fill('Restore synthetic browser withdrawal test')
 page.get_by_role('button',name='Registrar ajuste',exact=True).click()
 expect(page.get_by_role('status').filter(has_text='Operación guardada')).to_be_visible()
 page.get_by_role('button',name='Registrar ajuste',exact=True).click()
 expect(page.get_by_role('status').filter(has_text='ya estaba aplicada')).to_be_visible()
 print('PASS browser: manual credit and unchanged-form retry is idempotent')
 page.goto(base+'/admin/users?q=client1&kyc=pending&page_size=1')
 expect(page.locator('tbody tr')).to_have_count(1)
 assert not errors,errors
 context.clear_cookies(name='tw_admin_access')
 page.goto(base+'/admin/dashboard')
 expect(page.get_by_role('heading',name='Resumen',exact=True)).to_be_visible()
 assert any(c['name']=='tw_admin_access' for c in context.cookies())
 print('PASS browser: missing access cookie renews through HttpOnly refresh session')
 context.clear_cookies(name='tw_admin_access')
 page.get_by_role('button',name='Cerrar sesión',exact=True).click()
 page.wait_for_url('**/admin/login')
 assert not any(c['name']=='tw_admin_access' for c in context.cookies())
 print('PASS browser: filtered users, no JS errors, logout with missing access cookie revokes and clears session')
 denied=browser.new_context();denied_page=denied.new_page();denied_page.goto(base+'/admin/login')
 denied_page.get_by_label('Correo del equipo').fill('client1@demo.example.com')
 denied_page.get_by_label('Contraseña',exact=True).fill(password)
 denied_page.get_by_role('button',name='Entrar al back-office').click()
 denied_page.wait_for_url('**/admin/login?error=staff')
 assert not any(c['name']=='tw_admin_access' for c in denied.cookies())
 print('PASS browser: client admin login denied without admin session')
 browser.close()
request('POST','/api/auth/logout',token=client_tokens['access_token'])
request('POST','/api/auth/logout',token=staff_tokens['access_token'])
