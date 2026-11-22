from datetime import datetime,timedelta,timezone
from decimal import Decimal
from concurrent.futures import ThreadPoolExecutor
import pytest
from sqlalchemy import select,func
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.models.schema import Account,Transaction,Order,Swap,StakePlan,StakePosition,PaymentRequest,PaymentMethod,DepositWallet
from app.routers.auth import current_user
from app.schemas.trading import OrderBody
from app.services.paper import create_order
from app.services.order_worker import process_open_orders
from app.services.ledger import LedgerError
from app.services.marketdata import get_market_provider,MarketDataUnavailable

def balance(db,user,currency,kind='main'):
    db.expire_all()
    account=db.scalar(select(Account).where(Account.user_id==user.id,Account.currency==currency,Account.type==kind))
    return account.balance if account else Decimal('0')

def assert_balanced(db):
    assert not db.execute(select(Transaction.entry_id).group_by(Transaction.entry_id).having(func.sum(Transaction.amount)!=0)).all()
    assert db.scalar(select(func.min(Account.balance)))>=0

def test_market_buy_and_exact_fee(client,db,funded):
    user,_,_=funded
    r=client.post('/api/orders',json={'pair':'BTC/USDT','side':'buy','qty':'2'})
    assert r.status_code==201,r.text
    assert r.json()['status']=='filled' and Decimal(r.json()['fee_amount'])==Decimal('0.2')
    assert balance(db,user,'USDT')==Decimal('799.8')
    assert balance(db,user,'BTC')==1002
    fees=db.scalars(select(Transaction).where(Transaction.kind=='fee',Transaction.amount>0)).all()
    assert len(fees)==1 and fees[0].amount==Decimal('0.2')
    assert_balanced(db)

def test_market_sell_fee_is_charged_in_usdt(client,db,funded):
    user,_,_=funded
    r=client.post('/api/orders',json={'pair':'BTCUSDT','side':'sell','qty':'2','type':'market'})
    assert r.status_code==201,r.text
    assert balance(db,user,'BTC')==998
    assert balance(db,user,'USDT')==Decimal('1199.8')
    assert r.json()['fee_currency']=='USDT'
    assert_balanced(db)

def test_insufficient_market_is_atomic(client,db,funded):
    user,_,_=funded
    before=db.scalar(select(func.count(Transaction.id)))
    r=client.post('/api/orders',json={'pair':'BTCUSDT','side':'buy','qty':'10'})
    assert r.status_code==422
    assert balance(db,user,'USDT')==1000
    assert db.scalar(select(func.count(Transaction.id)))==before
    assert db.scalar(select(func.count(Order.id)))==0

def test_limit_worker_crossing_and_no_double_fill(client,db,engine,funded,fake_provider):
    user,_,_=funded
    r=client.post('/api/orders',json={'pair':'BTCUSDT','side':'buy','qty':'1','type':'limit','price':'90'})
    assert r.status_code==201 and r.json()['status']=='open'
    factory=sessionmaker(engine,expire_on_commit=False)
    process_open_orders(factory,fake_provider)
    db.expire_all(); assert db.get(Order,r.json()['id']).status=='open'
    fake_provider.prices['BTC']=Decimal('80')
    process_open_orders(factory,fake_provider);process_open_orders(factory,fake_provider)
    assert balance(db,user,'BTC')==1001
    assert balance(db,user,'USDT')==Decimal('919.92')
    order=db.get(Order,r.json()['id']);assert order.filled_price==80 and order.status=='filled'
    assert_balanced(db)

def test_limit_expiry_does_not_need_market(client,db,engine,funded,fake_provider):
    r=client.post('/api/orders',json={'pair':'BTCUSDT','side':'sell','qty':'1','type':'limit','price':'200'})
    order=db.get(Order,r.json()['id']);order.created_at=datetime.now(timezone.utc)-timedelta(hours=24,seconds=1);db.commit()
    def unavailable(symbol):raise AssertionError('Expired orders must not query prices')
    fake_provider.get_price=unavailable
    process_open_orders(sessionmaker(engine),fake_provider)
    db.expire_all();assert db.get(Order,order.id).status=='expired'

def test_order_ownership_and_cancellation(client,db,funded):
    user,other,_=funded
    r=client.post('/api/orders',json={'pair':'ETHUSDT','side':'buy','qty':'1','type':'limit','price':'5'})
    order_id=r.json()['id']
    app.dependency_overrides[current_user]=lambda:other
    assert client.get('/api/orders').json()==[]
    assert client.delete(f'/api/orders/{order_id}').status_code==404
    app.dependency_overrides[current_user]=lambda:user
    assert client.delete(f'/api/orders/{order_id}').json()['status']=='cancelled'
    assert client.delete(f'/api/orders/{order_id}').status_code==409

def test_swap_price_fee_and_ledger(client,db,funded):
    user,_,_=funded
    r=client.post('/api/swaps',json={'from_currency':'BTC','to_currency':'ETH','amount':'2'})
    assert r.status_code==201,r.text
    assert r.json()['status']=='pending'
    assert Decimal(r.json()['rate'])==10
    assert Decimal(r.json()['fee'])==Decimal('0.002')
    assert Decimal(r.json()['to_amount'])==Decimal('19.98')
    assert balance(db,user,'BTC')==1000 and balance(db,user,'ETH')==Decimal('1000')
    assert db.scalar(select(func.count(Transaction.id)).where(Transaction.kind.in_(['swap_in','swap_out','fee'])))==0
    assert len(client.get('/api/swaps').json())==1
    assert_balanced(db)

@pytest.mark.parametrize('source,target',[('USDT','USDC'),('USDC','USDT')])
def test_stablecoin_swaps_are_allowed(client,db,funded,source,target):
    user,_,_=funded
    r=client.post('/api/swaps',json={'from_currency':source,'to_currency':target,'amount':'10'})
    assert r.status_code==201,r.text
    assert r.json()['status']=='pending'
    assert balance(db,user,source)==1000
    assert balance(db,user,target)==Decimal('1000')
    assert_balanced(db)

def test_insufficient_swap_is_atomic(client,db,funded):
    user,_,_=funded
    r=client.post('/api/swaps',json={'from_currency':'BTC','to_currency':'ETH','amount':'1001'})
    assert r.status_code==422
    assert balance(db,user,'BTC')==1000
    assert db.scalar(select(func.count(Swap.id)))==0

def plan(db):
    plan=StakePlan(currency='USDT',apy=Decimal('20'),min_amount=Decimal('100'),term_days=365,is_active=True)
    db.add(plan);db.commit();return plan

def test_staking_locks_funds_without_accruing_yield(client,db,funded):
    user,_,_=funded;p=plan(db)
    assert len(client.get('/api/stake/plans').json())==1
    r=client.post('/api/stake/positions',json={'plan_id':p.id,'amount':'100'})
    assert r.status_code==201,r.text
    assert r.json()['status']=='pending' and Decimal(r.json()['yield_accrued'])==0
    assert balance(db,user,'USDT')==1000 and balance(db,user,'USDT','staking')==0
    assert len(client.get('/api/stake/positions').json())==1
    assert_balanced(db)

def test_staking_rejects_below_minimum_inactive_and_insufficient(client,db,funded):
    p=plan(db)
    for amount in ('99','1001'):
        assert client.post('/api/stake/positions',json={'plan_id':p.id,'amount':amount}).status_code==422
    p.is_active=False;db.commit()
    assert client.post('/api/stake/positions',json={'plan_id':p.id,'amount':'100'}).status_code==422
    assert db.scalar(select(func.count(StakePosition.id)))==0

def test_withdrawal_stays_pending_without_debit(client,db,funded):
    user,_,_=funded
    method=PaymentMethod(user_id=user.id,type='crypto',label='Demo',holder_name='Trader',network='DEMO',wallet_address='synthetic-address')
    db.add(method);db.commit()
    r=client.post('/api/payments/withdrawal-request',json={'currency':'USDT','amount':'25','payment_method_id':method.id})
    assert r.status_code==201,r.text
    assert r.json()['status']=='pending' and r.json()['execution_status']=='simulated'
    assert balance(db,user,'USDT')==1000 and balance(db,user,'USDT','escrow')==0
    assert db.scalar(select(Transaction).where(Transaction.request_id==r.json()['id'])) is None
    assert_balanced(db)

def test_crypto_withdrawal_accepts_network_and_pasted_destination(client,db,funded):
    user,_,_=funded
    r=client.post('/api/payments/withdrawal-request',json={
        'currency':'USDT','amount':'25','network':'TRC20',
        'destination_address':'TTestOnlyAddress123456789',
    })
    assert r.status_code==201,r.text
    assert r.json()['network']=='TRC20'
    assert r.json()['destination_address']=='TTestOnlyAddress123456789'
    assert r.json()['payment_method_id'] is None
    assert balance(db,user,'USDT')==1000

def test_withdrawal_insufficient_leaves_no_request_or_lock(client,db,funded):
    user,_,_=funded
    method=PaymentMethod(user_id=user.id,type='crypto',label='Demo',holder_name='Trader',network='DEMO',wallet_address='synthetic')
    db.add(method);db.commit()
    r=client.post('/api/payments/withdrawal-request',json={'currency':'USDT','amount':'1001','payment_method_id':method.id})
    assert r.status_code==422
    assert balance(db,user,'USDT')==1000 and balance(db,user,'USDT','escrow')==0
    assert db.scalar(select(func.count(PaymentRequest.id)))==0

def test_only_active_deposit_wallets_are_visible(client,db,funded):
    for active in (True,False):db.add(DepositWallet(label='synthetic',currency='USDT',network='DEMO',address='not-a-real-wallet',is_active=active))
    db.commit()
    assert len(client.get('/api/payments/deposit-wallets').json())==1

def test_private_lists_are_scoped_to_current_user(client,db,funded):
    user,other,_=funded;p=plan(db)
    client.post('/api/swaps',json={'from_currency':'BTC','to_currency':'ETH','amount':'1'})
    client.post('/api/stake/positions',json={'plan_id':p.id,'amount':'100'})
    app.dependency_overrides[current_user]=lambda:other
    assert client.get('/api/swaps').json()==[] and client.get('/api/stake/positions').json()==[]

@pytest.mark.parametrize('body',[
    {'pair':'NOPEUSDT','side':'buy','qty':'1'},
    {'pair':'BTCUSDT','side':'buy','qty':'0'},
    {'pair':'BTCUSDT','side':'buy','qty':'NaN'},
    {'pair':'BTCUSDT','side':'buy','qty':'0.000000001'},
    {'pair':'BTCUSDT','side':'buy','qty':'1','type':'limit'},
])
def test_invalid_order_inputs_are_rejected(client,funded,body):
    assert client.post('/api/orders',json=body).status_code==422

def test_market_outage_returns_503_without_mutating_balances(client,db,funded,fake_provider):
    user,_,_=funded
    def unavailable(symbol):raise MarketDataUnavailable('No last-known quote')
    fake_provider.get_price=unavailable
    assert client.post('/api/orders',json={'pair':'BTCUSDT','side':'buy','qty':'1'}).status_code==503
    assert balance(db,user,'USDT')==1000
    assert db.scalar(select(func.count(Order.id)))==0

def test_concurrent_market_orders_cannot_overspend(db,engine,funded,fake_provider):
    user,_,_=funded;user_id=user.id
    body=OrderBody(pair='BTCUSDT',side='buy',qty=Decimal('7'))
    def execute():
        with sessionmaker(engine,expire_on_commit=False)() as session:
            try:
                create_order(session,user_id,body,fake_provider);session.commit();return True
            except LedgerError:session.rollback();return False
    with ThreadPoolExecutor(max_workers=2) as pool:results=list(pool.map(lambda _:execute(),range(2)))
    assert sorted(results)==[False,True]
    assert balance(db,user,'USDT')==Decimal('299.3')
    assert_balanced(db)

def test_pending_stake_does_not_mutate_ledger_or_block_existing_order(client,db,engine,funded,fake_provider):
    user,_,_=funded
    r=client.post('/api/orders',json={'pair':'BTCUSDT','side':'buy','qty':'7','type':'limit','price':'100'})
    assert r.status_code==201
    assert client.post('/api/stake/positions',json={'plan_id':plan(db).id,'amount':'900'}).status_code==201
    before=db.scalar(select(func.count(Transaction.id)))
    process_open_orders(sessionmaker(engine),fake_provider)
    db.expire_all()
    assert db.get(Order,r.json()['id']).status=='filled'
    assert db.scalar(select(func.count(Transaction.id)))>before
    assert balance(db,user,'BTC')==1007

def test_two_workers_do_not_fill_the_same_limit_twice(client,db,engine,funded,fake_provider):
    user,_,_=funded
    r=client.post('/api/orders',json={'pair':'BTCUSDT','side':'buy','qty':'1','type':'limit','price':'100'})
    assert r.status_code==201
    factory=sessionmaker(engine)
    with ThreadPoolExecutor(max_workers=2) as pool:
        list(pool.map(lambda _:process_open_orders(factory,fake_provider),range(2)))
    assert balance(db,user,'BTC')==1001
    assert balance(db,user,'USDT')==Decimal('899.9')
    assert_balanced(db)
