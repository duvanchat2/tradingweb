from concurrent.futures import ThreadPoolExecutor
from decimal import Decimal
import pytest
from sqlalchemy import select,func
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.models.schema import User,Account,Transaction,PaymentRequest,KYCDocument,DepositWallet,Notification,AuditLog,Ticket
from app.routers.auth import current_user
from app.schemas.trading import WithdrawalBody
from app.services.paper import request_withdrawal
from app.admin.schemas import parse_action
from app.admin.service import execute

@pytest.fixture
def admin(db,client,funded):
    user,other,owner=funded
    user.office_id=11;user.country='CO';user.kyc_status='pending';other.office_id=22
    staff=User(email='staff@example.com',full_name='Office staff',role='staff',office_id=11,password_hash='unused')
    db.add(staff);db.commit()
    app.dependency_overrides[current_user]=lambda:staff
    return user,other,owner,staff

def post(client,body,key='test-action'):
    return client.post('/api/admin/actions',json=body,headers={'Idempotency-Key':key})

def balance(db,user,kind='main'):
    db.expire_all()
    account=db.scalar(select(Account).where(Account.user_id==user.id,Account.type==kind,Account.currency=='USDT'))
    return account.balance if account else Decimal('0')

def count_entries(db):return db.scalar(select(func.count(Transaction.id)))
def balanced(db):
    assert not db.execute(select(Transaction.entry_id).group_by(Transaction.entry_id).having(func.sum(Transaction.amount)!=0)).all()
    assert db.scalar(select(func.min(Account.balance)))>=0

def deposit(db,user):
    payment=PaymentRequest(user_id=user.id,currency='USDT',network='DEMO',amount_requested=Decimal('25'),method='simulated-deposit')
    db.add(payment);db.commit();return payment

def withdrawal(db,user):
    payment=request_withdrawal(db,user.id,WithdrawalBody(currency='USDT',amount=Decimal('25'),network='DEMO',address='synthetic'))
    db.commit();return payment

def payment_body(payment,decision='approved',**extra):
    return {'action':'payment_review','request_id':payment.id,'decision':decision,'staff_note':'Demo review',**extra}

def test_kyc_reject_pending_audit_and_replay(client,db,admin):
    user,_,_,staff=admin
    doc=KYCDocument(user_id=user.id,doc_type='selfie',file_path='synthetic/selfie.txt',status='pending')
    db.add(doc);db.commit()
    body={'action':'kyc_document','user_id':user.id,'document_id':doc.id,'decision':'rejected','review_note':'Use demo fixture'}
    assert post(client,body).status_code==200
    assert post(client,body).json()['replayed']
    db.expire_all();assert db.get(User,user.id).kyc_status=='rejected'
    assert db.scalar(select(func.count(AuditLog.id)).where(AuditLog.action=='admin.kyc_document'))==1
    body['decision']='pending'
    assert post(client,body,'kyc-pending').status_code==200
    db.expire_all();assert db.get(User,user.id).kyc_status=='pending'

def test_deposit_approval_edit_amount_and_state_idempotency(client,db,admin):
    user,_,_,_=admin;p=deposit(db,user)
    body=payment_body(p,amount='30')
    first=post(client,body);assert first.status_code==200,first.text
    assert first.json()['state']['ledger_resolution']=='credited'
    before=count_entries(db)
    assert post(client,body).json()['replayed']
    assert post(client,body,'new-key-same-closed-decision').status_code==200
    assert balance(db,user)==1030 and count_entries(db)==before
    balanced(db)

def test_withdrawal_approval_liquidates_exact_escrow(client,db,admin):
    user,_,_,_=admin;p=withdrawal(db,user)
    assert balance(db,user)==975 and balance(db,user,'escrow')==25
    r=post(client,payment_body(p));assert r.status_code==200,r.text
    assert r.json()['state']['execution_status']=='simulated'
    assert balance(db,user,'escrow')==0 and balance(db,user)==975
    before=count_entries(db);assert post(client,payment_body(p)).status_code==200
    assert count_entries(db)==before;balanced(db)

def test_withdrawal_rejection_releases_exact_escrow(client,db,admin):
    user,_,_,_=admin;p=withdrawal(db,user)
    body=payment_body(p,'rejected')
    assert post(client,body).status_code==200
    before=count_entries(db)
    assert post(client,body,'repeat-reject').status_code==200
    assert balance(db,user)==1000 and balance(db,user,'escrow')==0
    assert count_entries(db)==before;balanced(db)

def test_withdrawal_amount_edit_is_rejected_atomically(client,db,admin):
    user,_,_,_=admin;p=withdrawal(db,user);before=count_entries(db)
    assert post(client,payment_body(p,amount='24')).status_code==422
    assert balance(db,user,'escrow')==25 and count_entries(db)==before

def test_reopen_does_not_move_balance_or_duplicate_settlement(client,db,admin):
    user,_,_,_=admin;p=withdrawal(db,user)
    assert post(client,payment_body(p),'approved').status_code==200
    before=count_entries(db)
    r=post(client,payment_body(p,'revert'),'revert');assert r.json()['state']['status']=='pending'
    assert count_entries(db)==before and balance(db,user)==975
    assert post(client,payment_body(p),'approved-again').status_code==200
    assert count_entries(db)==before
    post(client,payment_body(p,'revert'),'reopen-again')
    assert post(client,payment_body(p,'rejected'),'cannot-reverse-paid').status_code==409
    assert count_entries(db)==before

def test_rejected_deposit_can_be_reopened_and_approved(client,db,admin):
    user,_,_,_=admin;p=deposit(db,user)
    assert post(client,payment_body(p,'rejected'),'reject').status_code==200
    assert post(client,payment_body(p,'revert'),'reopen').status_code==200
    assert post(client,payment_body(p),'approve').status_code==200
    assert balance(db,user)==1025

def test_credit_debit_network_and_retry(client,db,admin):
    user,_,_,_=admin
    body={'action':'credit','user':user.email,'currency':'USDT','network':'DEMO','amount':'10','operation':'credit','note':'Virtual adjustment'}
    assert post(client,body).status_code==200
    assert post(client,body).json()['replayed']
    assert balance(db,user)==1010
    body['operation']='debit'
    assert post(client,body,'debit').status_code==200
    assert balance(db,user)==1000
    assert db.scalar(select(Transaction).where(Transaction.staff_note=='Virtual adjustment')).network=='DEMO'
    balanced(db)

def test_credit_insufficient_rolls_back_audit_and_balance(client,db,admin):
    user,_,_,_=admin
    body={'action':'credit','user':user.id,'currency':'USDT','network':'DEMO','amount':'1001','operation':'debit','note':'Virtual debit'}
    assert post(client,body).status_code==422
    assert balance(db,user)==1000
    assert db.scalar(select(func.count(AuditLog.id)).where(AuditLog.idempotency_key=='test-action'))==0

def test_credit_correct_links_without_editing_original(client,db,admin):
    user,_,_,_=admin
    account=db.scalar(select(Account).where(Account.user_id==user.id,Account.type=='main',Account.currency=='USDT'))
    original=db.scalar(select(Transaction).where(Transaction.account_id==account.id,Transaction.amount>0))
    original_amount=original.amount;created=original.created_at
    body={'action':'credit_correct','transaction_id':original.id,'amount':'1200','note':'Correct magnitude'}
    assert post(client,body).status_code==200
    assert balance(db,user)==1200
    corrections=db.scalars(select(Transaction).where(Transaction.original_transaction_id==original.id)).all()
    assert len(corrections)==2 and all(t.kind=='correction' for t in corrections)
    assert db.get(Transaction,original.id).amount==original_amount and db.get(Transaction,original.id).created_at==created
    before=count_entries(db)
    assert post(client,body,'same-effective-amount').status_code==200 and count_entries(db)==before
    assert post(client,body).json()['replayed'];balanced(db)

def test_wallet_save_edit_delete_and_idempotency(client,db,admin):
    body={'action':'deposit_wallet_save','wallet_id':0,'label':'Demo wallet','currency':'USDT','network':'DEMO','address':'synthetic','is_active':True}
    r=post(client,body);assert r.status_code==200,r.text
    wallet_id=r.json()['entity_id']
    assert post(client,body).json()['replayed']
    assert db.scalar(select(func.count(DepositWallet.id)))==1
    body.update(wallet_id=wallet_id,label='Updated demo')
    assert post(client,body,'edit').status_code==200
    deletion={'action':'deposit_wallet_delete','wallet_id':wallet_id}
    assert post(client,deletion,'delete').status_code==200
    assert post(client,deletion,'delete').json()['replayed']
    db.expire_all();assert not db.get(DepositWallet,wallet_id).is_active

def test_notification_scoping_filter_and_retry(client,db,admin):
    user,other,owner,staff=admin
    body={'action':'send_notification','scope':'office','kyc_filter':'pending','title':'Demo notice','type':'info','body':'Synthetic message'}
    r=post(client,body);assert r.status_code==200,r.text
    assert r.json()['state']['recipient_count']==1
    assert post(client,body).json()['replayed']
    assert db.scalar(select(func.count(Notification.id)))==1
    assert db.scalar(select(Notification)).user_id==user.id
    body.update(scope='one',user_id=other.id)
    assert post(client,body,'out-of-scope').status_code==404

def test_superworker_can_notify_all_scoped_clients(client,db,admin):
    user,other,owner,staff=admin;app.dependency_overrides[current_user]=lambda:owner
    body={'action':'send_notification','scope':'all','title':'Demo all','type':'warning','body':'Internal synthetic notice'}
    assert post(client,body).json()['state']['recipient_count']==2
    assert post(client,body).json()['replayed']
    assert db.scalar(select(func.count(Notification.id)))==2

def test_idempotency_key_conflict(client,db,admin):
    user,_,_,_=admin
    body={'action':'credit','user':user.id,'currency':'USDT','network':'DEMO','amount':'10','operation':'credit','note':'Adjustment'}
    assert post(client,body).status_code==200
    body['amount']='11';assert post(client,body).status_code==409
    assert balance(db,user)==1010

def test_concurrent_action_retries_apply_once(client,db,engine,admin):
    user,other,owner,staff=admin
    body=parse_action({'action':'credit','user':user.id,'currency':'USDT','network':'DEMO','amount':'10','operation':'credit','note':'Concurrent adjustment'})
    def run():
        with sessionmaker(engine,expire_on_commit=False)() as session:return execute(session,staff,body,'same-key')
    with ThreadPoolExecutor(max_workers=2) as pool:results=list(pool.map(lambda _:run(),range(2)))
    assert sorted(r['replayed'] for r in results)==[False,True]
    assert balance(db,user)==1010;balanced(db)

def test_users_filters_pagination_profiles_and_scope(client,db,admin):
    user,other,owner,staff=admin
    r=client.get('/api/admin/users?q=trader&kyc=pending&country=CO&active=true&page_size=1')
    assert r.status_code==200,r.text
    assert r.json()['total']==1 and r.json()['items'][0]['id']==user.id
    assert 'password_hash' not in r.json()['items'][0]
    assert client.get(f'/api/admin/users/{other.id}').status_code==404
    assert client.get(f'/api/admin/users/{user.id}').json()['accounts']
    app.dependency_overrides[current_user]=lambda:owner
    r=client.get('/api/admin/users?page=2&page_size=1')
    assert r.json()['total']==4 and len(r.json()['items'])==1
    assert client.get('/api/admin/users?page=0').status_code==422

@pytest.mark.parametrize('action',[
    {'action':'kyc_document','user_id':1,'document_id':1,'decision':'pending'},
    {'action':'payment_review','request_id':1,'decision':'approved'},
    {'action':'credit','user':1,'currency':'USDT','network':'DEMO','amount':'1','operation':'credit','note':'Demo'},
    {'action':'credit_correct','transaction_id':1,'amount':'1','note':'Demo'},
    {'action':'deposit_wallet_save','wallet_id':0,'label':'Demo','currency':'USDT','network':'DEMO','address':'synthetic','is_active':True},
    {'action':'deposit_wallet_delete','wallet_id':1},
    {'action':'send_notification','scope':'all','title':'Demo','type':'info','body':'Internal'}])
def test_every_admin_action_denies_client(client,admin,action):
    user,_,_,_=admin;app.dependency_overrides[current_user]=lambda:user
    assert post(client,action).status_code==403

@pytest.mark.parametrize('path',['users','users/1','payments','kyc/queue','swaps','production','tickets','deposit-wallets','notifications','stake-plans','ranking','cards'])
def test_every_admin_read_denies_client(client,admin,path):
    user,_,_,_=admin;app.dependency_overrides[current_user]=lambda:user
    assert client.get('/api/admin/'+path).status_code==403

def test_scoped_reads_and_production_audit(client,db,admin):
    user,other,_,_=admin
    for u in (user,other):db.add(Ticket(user_id=u.id,subject='Synthetic support',status='open'))
    p=deposit(db,user);assert post(client,payment_body(p)).status_code==200
    assert client.get('/api/admin/tickets').json()['total']==1
    assert client.get('/api/admin/payments?status=approved').json()['total']==1
    data=client.get('/api/admin/production').json()
    assert Decimal(data['deposits_by_currency']['USDT'])==25
    assert data['tickets_open']==1
    assert client.get('/api/admin/production?from=2026-12-01&to=2026-01-01').status_code==422
    assert db.scalar(select(func.count(AuditLog.id)).where(AuditLog.action=='admin.read'))>=3

def test_nested_payment_payload_and_unknown_fields(client,db,admin):
    user,_,_,_=admin;p=deposit(db,user)
    r=post(client,{'action':'payment_review','payload':{'request_id':p.id,'action':'approved','staff_note':'Nested decision'}})
    assert r.status_code==200,r.text
    assert balance(db,user)==1025
    assert post(client,{'action':'credit','unexpected':'field'}).status_code==422


def test_production_counts_clients_not_staff_accounts(client,admin):
    user,other,owner,staff=admin
    app.dependency_overrides[current_user]=lambda:owner
    assert client.get('/api/admin/production').json()['users_new']==2
