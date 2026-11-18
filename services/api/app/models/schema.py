from datetime import datetime, timezone
from decimal import Decimal
from sqlalchemy import Boolean, CheckConstraint, DateTime, ForeignKey, Integer, JSON, Numeric, String, Text, UniqueConstraint
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

class Base(DeclarativeBase): pass
class Record:
    id: Mapped[int] = mapped_column(primary_key=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
def money(): return mapped_column(Numeric(28,8), nullable=False, default=Decimal('0'))
def fk(table, nullable=False): return mapped_column(ForeignKey(table+'.id'), nullable=nullable)
def state(values, default): return mapped_column(String(24), default=default, nullable=False)

class User(Record, Base):
    __tablename__='users'
    email: Mapped[str] = mapped_column(String(254), unique=True)
    phone: Mapped[str | None]
    password_hash: Mapped[str] = mapped_column(Text)
    full_name: Mapped[str]
    country: Mapped[str | None]
    registration_code: Mapped[str | None] = mapped_column(String(6), index=True)
    role: Mapped[str] = state([], 'client')
    kyc_status: Mapped[str] = state([], 'none')
    office_id: Mapped[int | None]
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    referral_code: Mapped[str | None] = mapped_column(unique=True)
    last_login_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    last_login_ip: Mapped[str | None]
    __table_args__=(CheckConstraint("role IN ('client','staff','superworker')"),CheckConstraint("kyc_status IN ('none','pending','verified','rejected')"))

class Account(Record, Base):
    __tablename__='accounts'
    user_id: Mapped[int] = fk('users')
    type: Mapped[str] = state([], 'main')
    currency: Mapped[str] = mapped_column(String(10))
    normal_side: Mapped[str] = mapped_column(String(6), default='debit')
    balance: Mapped[Decimal] = money()
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    __table_args__=(UniqueConstraint('user_id','type','currency'),CheckConstraint('balance >= 0'),CheckConstraint("type IN ('main','staking','system','escrow')", name='accounts_type_check'),CheckConstraint("normal_side IN ('debit','credit')"),CheckConstraint("normal_side = 'debit' OR type = 'system'"))

class Transaction(Record, Base):
    __tablename__='transactions'
    account_id: Mapped[int] = fk('accounts')
    kind: Mapped[str]
    amount: Mapped[Decimal] = money()
    currency: Mapped[str]
    network: Mapped[str | None]
    status: Mapped[str] = state([], 'simulated')
    staff_note: Mapped[str | None] = mapped_column(Text)
    admin_id: Mapped[int | None] = fk('users', True)
    request_id: Mapped[int | None] = fk('payment_requests', True)
    original_transaction_id: Mapped[int | None] = fk('transactions', True)
    entry_id: Mapped[str] = mapped_column(String(36), index=True)
    __table_args__=(CheckConstraint('amount <> 0'),CheckConstraint("kind IN ('deposit','withdrawal','credit','debit','swap_in','swap_out','stake_lock','stake_yield','fee','correction','trade','withdrawal_lock')", name='transactions_kind_check'),CheckConstraint("status IN ('pending','approved','rejected','reverted','simulated')"))

class PaymentRequest(Record, Base):
    __tablename__='payment_requests'
    user_id: Mapped[int] = fk('users')
    currency: Mapped[str]
    network: Mapped[str | None]
    amount_requested: Mapped[Decimal] = money()
    amount_approved: Mapped[Decimal | None] = mapped_column(Numeric(28,8))
    method: Mapped[str]
    destination_address: Mapped[str | None] = mapped_column(String(256))
    execution_status: Mapped[str] = mapped_column(String(16), default='simulated', server_default='simulated')
    ledger_resolution: Mapped[str] = mapped_column(String(16), default='unsettled', server_default='unsettled')
    status: Mapped[str] = state([], 'pending')
    staff_note: Mapped[str | None] = mapped_column(Text)
    reviewer_id: Mapped[int | None] = fk('users', True)
    reviewed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    __table_args__=(CheckConstraint("execution_status = 'simulated'", name='payment_requests_demo_only'),CheckConstraint('amount_requested > 0'),CheckConstraint("status IN ('pending','approved','rejected','reverted')"))

class KYCDocument(Record, Base):
    __tablename__='kyc_documents'
    user_id: Mapped[int] = fk('users')
    doc_type: Mapped[str]
    file_path: Mapped[str]
    status: Mapped[str] = state([], 'pending')
    review_note: Mapped[str | None] = mapped_column(Text)
    reviewer_id: Mapped[int | None] = fk('users', True)
    reviewed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    __table_args__=(CheckConstraint("doc_type IN ('id_front','id_back','proof_address','selfie')"),CheckConstraint("status IN ('pending','approved','rejected')"))

class AuditLog(Record, Base):
    __tablename__='audit_log'
    actor_id: Mapped[int | None] = fk('users', True)
    action: Mapped[str]
    entity: Mapped[str]
    entity_id: Mapped[int | None]
    before_json: Mapped[dict | None] = mapped_column(JSON)
    after_json: Mapped[dict | None] = mapped_column(JSON)
    ip: Mapped[str | None]
    idempotency_key: Mapped[str | None] = mapped_column(String(128))
    request_hash: Mapped[str | None] = mapped_column(String(64))
    __table_args__=(UniqueConstraint('actor_id','idempotency_key',name='uq_audit_actor_idempotency'),)

class DepositWallet(Record, Base):
    __tablename__='wallets_deposit'
    label: Mapped[str]
    currency: Mapped[str]
    network: Mapped[str]
    address: Mapped[str]
    is_active: Mapped[bool] = mapped_column(default=True)
class Order(Record, Base):
    __tablename__='orders'
    user_id: Mapped[int] = fk('users')
    pair: Mapped[str]
    side: Mapped[str]
    type: Mapped[str]
    qty: Mapped[Decimal] = money()
    price: Mapped[Decimal | None] = mapped_column(Numeric(28,8))
    status: Mapped[str] = state([], 'open')
    filled_price: Mapped[Decimal | None] = mapped_column(Numeric(28,8))
    fee_amount: Mapped[Decimal | None] = mapped_column(Numeric(28,8))
    fee_currency: Mapped[str | None] = mapped_column(String(10))
    __table_args__=(CheckConstraint("side IN ('buy','sell')"),CheckConstraint("type IN ('market','limit')"),CheckConstraint("status IN ('open','filled','cancelled','expired')", name='orders_status_check'),CheckConstraint('qty > 0'))
class Swap(Record, Base):
    __tablename__='swaps'
    user_id: Mapped[int] = fk('users')
    from_currency: Mapped[str]
    to_currency: Mapped[str]
    from_amount: Mapped[Decimal] = money()
    to_amount: Mapped[Decimal] = money()
    rate: Mapped[Decimal] = money()
    fee: Mapped[Decimal] = money()
    status: Mapped[str] = state([], 'completed')
    __table_args__=(CheckConstraint("status IN ('completed','failed')"),)
class StakePlan(Record, Base):
    __tablename__='stake_plans'
    currency: Mapped[str]
    apy: Mapped[Decimal] = money()
    min_amount: Mapped[Decimal] = money()
    term_days: Mapped[int]
    is_active: Mapped[bool] = mapped_column(default=True)
class StakePosition(Record, Base):
    __tablename__='stake_positions'
    user_id: Mapped[int] = fk('users')
    plan_id: Mapped[int] = fk('stake_plans')
    amount: Mapped[Decimal] = money()
    yield_accrued: Mapped[Decimal] = money()
    status: Mapped[str] = state([], 'active')
    opened_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    closes_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    __table_args__=(CheckConstraint("status IN ('active','closed')"),)
class Notification(Record, Base):
    __tablename__='notifications'
    user_id: Mapped[int | None] = fk('users', True)
    scope: Mapped[str]
    kyc_filter: Mapped[str | None]
    type: Mapped[str]
    title: Mapped[str]
    body: Mapped[str] = mapped_column(Text)
    is_read: Mapped[bool] = mapped_column(default=False)
    __table_args__=(CheckConstraint("scope IN ('one','office','all')"),CheckConstraint("type IN ('info','success','warning')"))
class Ticket(Record, Base):
    __tablename__='tickets'
    user_id: Mapped[int] = fk('users')
    subject: Mapped[str]
    status: Mapped[str] = state([], 'open')
    __table_args__=(CheckConstraint("status IN ('open','answered','closed')"),)
class TicketMessage(Record, Base):
    __tablename__='ticket_messages'
    ticket_id: Mapped[int] = fk('tickets')
    sender_id: Mapped[int] = fk('users')
    body: Mapped[str] = mapped_column(Text)
