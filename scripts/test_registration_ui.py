"""Local registration smoke. Requires Playwright/Chromium and a local demo API.
Creates one synthetic client with zero balances; no credentials are printed.
"""
import os,secrets,urllib.parse
from decimal import Decimal
from playwright.sync_api import sync_playwright,expect

base=os.environ.get('WEB_URL','http://127.0.0.1:3050')
api=os.environ.get('API_URL','http://127.0.0.1:8000')
if urllib.parse.urlparse(base).hostname not in ('127.0.0.1','localhost') or urllib.parse.urlparse(api).hostname not in ('127.0.0.1','localhost'):
    raise RuntimeError('This smoke creates data and must run against a local demo stack')
email='register-'+secrets.token_hex(8)+'@example.com'
password=secrets.token_urlsafe(24)
with sync_playwright() as p:
    browser=p.chromium.launch(executable_path=os.environ.get('CHROMIUM_PATH','/usr/bin/chromium'),headless=True,args=['--no-sandbox','--disable-dev-shm-usage'])
    context=browser.new_context();page=context.new_page();errors=[]
    page.on('pageerror',lambda error:errors.append(str(error)))
    page.goto(base+'/app/login');page.get_by_role('link',name='Crear cuenta',exact=True).click()
    page.wait_for_url('**/app/register')
    expect(page.get_by_role('status').filter(has_text='Demo — no son fondos reales')).to_be_visible()
    assert 'entorno de simulación' not in page.locator('body').inner_text().lower()
    denied=context.request.post(base+'/app/session/register',headers={'Origin':base},form={'email':email,'full_name':'Registro Browser','password':password,'password_confirm':password})
    assert denied.status==403
    page.get_by_label('Nombre completo',exact=True).fill('Registro Browser')
    page.get_by_label('Correo electrónico',exact=True).fill(email)
    page.get_by_label('Contraseña',exact=True).fill(password)
    page.get_by_label('Confirmar contraseña',exact=True).fill(password+'x')
    page.get_by_role('button',name='Crear cuenta',exact=True).click()
    assert page.get_by_label('Confirmar contraseña',exact=True).evaluate('(el)=>el.validity.customError')
    password+='x'
    page.get_by_label('Contraseña',exact=True).fill(password)
    page.get_by_role('button',name='Crear cuenta',exact=True).click()
    page.wait_for_url('**/app/login?registered=1')
    expect(page.get_by_role('status').filter(has_text='Cuenta creada')).to_be_visible()
    print('PASS: login link, demo label, missing CSRF denied, mismatch recovery, successful registration')
    page.get_by_role('link',name='Crear cuenta',exact=True).click()
    for label,value in [('Nombre completo','Registro Browser'),('Correo electrónico',email),('Contraseña',password),('Confirmar contraseña',password)]:
        page.get_by_label(label,exact=True).fill(value)
    page.get_by_role('button',name='Crear cuenta',exact=True).click()
    page.wait_for_url('**/app/register?error=exists')
    expect(page.get_by_role('alert').filter(has_text='ya está registrado')).to_be_visible()
    csrf=context.request.get(base+'/app/session/csrf').json()['csrf']
    invalid=context.request.post(base+'/app/session/register',headers={'Origin':base},form={'_csrf':csrf,'email':email,'full_name':'Registro Browser','password':password,'password_confirm':password+'no'},max_redirects=0)
    assert invalid.status==303 and 'error=password' in invalid.headers['location']
    assert password not in invalid.headers['location']
    login=context.request.post(base+'/app/session/login',headers={'Origin':base},form={'_csrf':csrf,'email':email,'password':password},max_redirects=0)
    assert login.status==303 and login.headers['location'].endswith('/app/dashboard')
    assert all(cookie['httpOnly'] for cookie in context.cookies() if cookie['name'].startswith('tw_client_'))
    page.goto(base+'/app/profile');expect(page.get_by_text(email,exact=True)).to_be_visible()
    assert page.evaluate('localStorage.length')==0
    tokens=context.request.post(api+'/api/auth/login',headers={'X-Demo-Confirm':'true'},data={'email':email,'password':password}).json()
    auth={'X-Demo-Confirm':'true','Authorization':'Bearer '+tokens['access_token']}
    account=context.request.get(api+'/api/account',headers=auth).json()
    assert account['user']['role']=='client' and len(account['accounts'])==9
    assert all(Decimal(str(row['balance']))==0 for row in account['accounts'])
    context.request.post(api+'/api/auth/logout',headers=auth)
    context.request.post(base+'/app/session/logout',headers={'Origin':base},form={'_csrf':csrf},max_redirects=0)
    assert not errors,errors
    print('PASS: duplicate email, server mismatch validation, client login, HttpOnly cookies, nine zero balances, no JS errors')
    browser.close()
