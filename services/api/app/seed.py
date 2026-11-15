"""Idempotent synthetic fixtures; run with python -m app.seed after migrations."""
from decimal import Decimal
from sqlalchemy import select, text
from app.core.db import SessionLocal
from app.core.config import get_settings
from app.core.security import hasher
from app.models.schema import User, Account, Transaction, PaymentRequest, KYCDocument, StakePlan, AuditLog
from app.routers.auth import CURRENCIES
from app.services.ledger import post_entry

def seed():
    with SessionLocal.begin() as db:
        # Serialize concurrent startup/CLI invocations.
        db.execute(text("SELECT pg_advisory_xact_lock(172901)"))
        if db.scalar(select(User.id).where(User.email == 'superworker@demo.example.com')):
            print('Demo seed already present')
            return
        password_hash = hasher.hash(get_settings().seed_password)
        users = [User(email=f'client{i}@demo.example.com',full_name=f'Cliente Demo {i}',password_hash=password_hash,role='client') for i in range(1,9)]
        staff = User(email='staff@demo.example.com', full_name='Staff Demo', password_hash=password_hash,role='staff')
        superworker = User(email='superworker@demo.example.com', full_name='Superworker Demo', password_hash=password_hash,role='superworker')
        db.add_all([*users,staff,superworker]); db.flush()
        # Credit-normal equity accounts balance all synthetic issuance; every account starts at zero.
        treasury = {}
        for currency in CURRENCIES:
            account = Account(user_id=superworker.id, type='system',currency=currency,normal_side='credit')
            db.add(account); db.flush(); treasury[currency] = account
        accounts = {}
        for user in [*users, staff, superworker]:
            for currency in CURRENCIES:
                account = Account(user_id=user.id,type='main',currency=currency)
                db.add(account); db.flush(); accounts[user.id,currency] = account
                post_entry(db, debit_account_id=treasury[currency].id,credit_account_id=account.id,amount=Decimal('1000'),actor_id=superworker.id,note='Demo allocation')
        for i in range(20):
            source = accounts[users[i%8].id,'USDT']
            target = accounts[users[(i+1)%8].id,'USDT']
            post_entry(db,debit_account_id=source.id,credit_account_id=target.id,amount=Decimal(i+1),note='Synthetic history',actor_id=staff.id)
        for status in ('pending','approved','rejected'):
            request = PaymentRequest(user_id=users[0].id,currency='USDT',network='DEMO',amount_requested=Decimal('25'),amount_approved=Decimal('25') if status=='approved' else None,method='simulated-deposit',status=status,reviewer_id=staff.id if status!='pending' else None)
            db.add(request); db.flush()
            if status=='approved':
                post_entry(db,debit_account_id=treasury['USDT'].id,credit_account_id=accounts[users[0].id,'USDT'].id,amount=Decimal('25'),kind='deposit',actor_id=staff.id,request_id=request.id)
        users[0].kyc_status = 'pending'
        for kind in ('id_front','id_back','proof_address','selfie'):
            db.add(KYCDocument(user_id=users[0].id,doc_type=kind,file_path='fixtures/synthetic/'+kind+'.txt',status='pending'))
        db.add(StakePlan(currency='USDT',apy=Decimal('5'),min_amount=Decimal('100'),term_days=30))
        db.add(AuditLog(actor_id=superworker.id,action='seed.complete',entity='accounts',after_json={'currencies':list(CURRENCIES)}))
    print('Demo seed created: 8 clients, staff, superworker')

if __name__ == '__main__': seed()
