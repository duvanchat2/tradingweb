"""Curl every phase-2 endpoint against tests.smoke_app, never against live funds.

Uses the local seed password without printing it or bearer tokens. The harness
must run on a dedicated smoke database and Redis namespace; see docs/PHASE2.md.
"""
from decimal import Decimal
from pathlib import Path
import json
import os
import subprocess
import tempfile

root=Path(__file__).resolve().parents[1]
values=dict(line.split('=',1) for line in (root/'infra/.env').read_text().splitlines()
            if line and not line.startswith('#') and '=' in line)
api_url=os.environ.get('API_URL','http://127.0.0.1:8000')
with tempfile.TemporaryDirectory() as scratch:
    headers=Path(scratch)/'headers'
    headers.write_text('X-Demo-Confirm: true\nContent-Type: application/json\n')
    headers.chmod(0o600)
    def call(method,path,body=None,expected=200):
        cmd=['curl','-sS','--max-time','15','-X',method,'-H','@'+str(headers),api_url+path,'-w','\n%{http_code}']
        if body is not None:cmd+=['--data-binary','@-']
        result=subprocess.run(cmd,input=json.dumps(body) if body is not None else None,text=True,capture_output=True,check=True)
        payload,status=result.stdout.rsplit('\n',1)
        assert int(status)==expected,f'{method} {path}: expected {expected}, got {status}'
        print(f'PASS curl {method} {path}: {status}')
        return json.loads(payload) if payload else None
    login=call('POST','/api/auth/login',{'email':'client1@demo.example.com','password':values['SEED_PASSWORD']})
    headers.write_text(headers.read_text()+'Authorization: Bearer '+login['access_token']+'\n')
    ticker=call('GET','/api/market/ticker/BTC')
    assert ticker['source']=='integration-fixture','This script requires the isolated fixture harness'
    assert len(call('GET','/api/market/prices')['prices'])==9
    order=call('POST','/api/orders',{'pair':'BTCUSDT','side':'buy','qty':'2'},201)
    assert order['status']=='filled' and Decimal(order['fee_amount'])==Decimal('0.2')
    pending=call('POST','/api/orders',{'pair':'BTCUSDT','side':'sell','qty':'1','type':'limit','price':'200'},201)
    assert call('GET','/api/orders')
    assert call('DELETE','/api/orders/'+str(pending['id']))['status']=='cancelled'
    swap=call('POST','/api/swaps',{'from_currency':'BTC','to_currency':'ETH','amount':'1'},201)
    assert Decimal(swap['to_amount'])==Decimal('9.99')
    assert call('GET','/api/swaps')
    plans=call('GET','/api/stake/plans')
    position=call('POST','/api/stake/positions',{'plan_id':plans[0]['id'],'amount':'100'},201)
    assert Decimal(position['yield_accrued'])==0
    assert call('GET','/api/stake/positions')
    withdrawal=call('POST','/api/payments/withdrawal-request',{'currency':'USDT','amount':'25','network':'DEMO','address':'synthetic-no-onchain'},201)
    assert withdrawal['status']=='pending' and withdrawal['execution_status']=='simulated'
    assert isinstance(call('GET','/api/payments/deposit-wallets'),list)
    call('POST','/api/auth/logout',expected=204)
