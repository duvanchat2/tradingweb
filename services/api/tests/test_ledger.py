from concurrent.futures import ThreadPoolExecutor
from decimal import Decimal
import pytest
from sqlalchemy import select, func
from sqlalchemy.orm import Session
from app.models.schema import User, Account, Transaction
from app.services.ledger import post_entry, LedgerError

def accounts(db):
    user=User(email='ledger@example.com',full_name='Ledger',password_hash='unused')
    db.add(user);db.flush()
    equity=Account(user_id=user.id,type='system',currency='USDT',normal_side='credit')
    source=Account(user_id=user.id,type='main',currency='USDT')
    target=Account(user_id=user.id,type='staking',currency='USDT')
    db.add_all([equity,source,target]);db.flush()
    post_entry(db,debit_account_id=equity.id,credit_account_id=source.id,amount=Decimal('10'))
    db.commit()
    return source,target

def test_balanced_atomic_entries(db):
    source,target=accounts(db)
    entry=post_entry(db,debit_account_id=source.id,credit_account_id=target.id,amount=Decimal('3.12345678'))
    db.commit()
    assert source.balance==Decimal('6.87654322')
    assert target.balance==Decimal('3.12345678')
    assert db.scalar(select(func.sum(Transaction.amount)).where(Transaction.entry_id==entry))==0
    assert len(db.scalars(select(Transaction).where(Transaction.entry_id==entry)).all())==2
    with pytest.raises(LedgerError):
        post_entry(db,debit_account_id=source.id,credit_account_id=target.id,amount=Decimal('7'))
    assert source.balance==Decimal('6.87654322')
    assert db.scalar(select(func.count(Transaction.id)))==4

@pytest.mark.parametrize('amount',['-1','0','NaN','Infinity','0.000000001','100000000000000000000'])
def test_invalid_amount(db,amount):
    source,target=accounts(db)
    with pytest.raises(LedgerError):
        post_entry(db,debit_account_id=source.id,credit_account_id=target.id,amount=Decimal(amount))
    assert source.balance==10

def test_rollback_and_currency_mismatch(db):
    source,target=accounts(db)
    post_entry(db,debit_account_id=source.id,credit_account_id=target.id,amount=Decimal('2'))
    db.rollback()
    assert db.get(Account,source.id).balance==10
    target.currency='BTC';db.commit()
    with pytest.raises(LedgerError): post_entry(db,debit_account_id=source.id,credit_account_id=target.id,amount=Decimal('2'))
    with pytest.raises(LedgerError): post_entry(db,debit_account_id=source.id,credit_account_id=source.id,amount=Decimal('2'))

def test_concurrent_spending_never_overdraws(db,engine):
    source,target=accounts(db)
    ids=(source.id,target.id)
    def spend():
        with Session(engine) as session:
            try:
                post_entry(session,debit_account_id=ids[0],credit_account_id=ids[1],amount=Decimal('7'))
                session.commit()
                return True
            except LedgerError:
                session.rollback()
                return False
    with ThreadPoolExecutor(max_workers=2) as pool:
        results=list(pool.map(lambda _:spend(),range(2)))
    assert sorted(results)==[False,True]
    db.expire_all()
    assert db.get(Account,ids[0]).balance==3
    assert db.get(Account,ids[1]).balance==7
    assert db.scalar(select(func.min(Account.balance)))>=0
