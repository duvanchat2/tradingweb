from decimal import Decimal
from uuid import uuid4
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.models.schema import Account, Transaction, AuditLog

class LedgerError(ValueError): pass

def post_entry(db: Session, *, debit_account_id: int, credit_account_id: int,
               amount: Decimal, kind: str = 'credit', actor_id: int | None = None,
               note: str = '', request_id: int | None = None,
               original_transaction_id: int | None = None, network: str | None = None) -> str:
    """Transfer virtual units atomically. Caller owns commit/rollback. No overdrafts.

    All entries have equal and opposite signed amounts in the same currency.
    Account row locks are acquired in ID order to avoid deadlocks.
    """
    amount = Decimal(amount)
    if not amount.is_finite() or amount <= 0 or amount >= Decimal('1e20') or amount != amount.quantize(Decimal('.00000001')):
        raise LedgerError('Amount must be positive, finite, and have at most 8 decimals')
    if debit_account_id == credit_account_id:
        raise LedgerError('Accounts must differ')
    with db.begin_nested():
        accounts = db.scalars(select(Account).where(Account.id.in_([debit_account_id, credit_account_id])).order_by(Account.id).with_for_update().execution_options(populate_existing=True)).all()
        indexed = {a.id:a for a in accounts}
        if len(indexed) != 2:
            raise LedgerError('Unknown account')
        source, target = indexed[debit_account_id], indexed[credit_account_id]
        if source.currency != target.currency:
            raise LedgerError('Currency mismatch')
        source_balance = source.balance + (amount if source.normal_side == 'credit' else -amount)
        target_balance = target.balance + (-amount if target.normal_side == 'credit' else amount)
        if source_balance < 0 or target_balance < 0:
            raise LedgerError('Insufficient virtual funds')
        if source_balance >= Decimal('1e20') or target_balance >= Decimal('1e20'):
            raise LedgerError('Account balance exceeds supported precision')
        entry_id = str(uuid4())
        source.balance = source_balance
        target.balance = target_balance
        for account, delta in ((source, -amount), (target, amount)):
            db.add(Transaction(account_id=account.id, kind=kind, amount=delta, currency=account.currency,
                entry_id=entry_id, network=network, status='simulated', admin_id=actor_id, staff_note=note,
                request_id=request_id, original_transaction_id=original_transaction_id))
        db.add(AuditLog(actor_id=actor_id, action='ledger.post_entry', entity='transactions',
            after_json={'entry_id':entry_id,'debit':source.id,'credit':target.id,'amount':str(amount),'currency':source.currency}))
        db.flush()
    return entry_id
