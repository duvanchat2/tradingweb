"""Atomic paper operations; every balance mutation goes through post_entry."""
from decimal import Decimal, ROUND_DOWN
from sqlalchemy import func, select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.orm import Session
from app.models.schema import Account, User, Office, Order, Swap, StakePlan, StakePosition, PaymentRequest, PaymentMethod, AuditLog
from app.services.ledger import post_entry, LedgerError
from app.services.marketdata import MarketDataProvider, MarketDataUnavailable
from app.routers.auth import CURRENCIES

UNIT = Decimal('0.00000001')
FEE_RATE = Decimal('0.001')
TRADING_PAIRS = ('BTCUSDT','ETHUSDT','BNBUSDT','SOLUSDT','XAUUSDT','XAGUSDT')

def rounded(value: Decimal) -> Decimal:
    if not value.is_finite() or abs(value) >= Decimal('1e20'):
        raise LedgerError('Amount exceeds supported precision')
    return value.quantize(UNIT, rounding=ROUND_DOWN)

def parse_pair(pair: str) -> str:
    pair = pair.upper().replace('/', '').replace('-', '')
    if pair not in TRADING_PAIRS:
        raise LedgerError('Supported markets: '+', '.join(TRADING_PAIRS))
    return pair[:-4]

def require_office_feature(db: Session, user_id: int, feature: str):
    user = db.get(User, user_id)
    if user and user.office_id:
        office = db.get(Office, user.office_id)
        if not office or not office.is_active or not getattr(office, feature):
            raise LedgerError('This operation is disabled by your office')

def lock_user(db: Session, user_id: int):
    user = db.scalar(select(User).where(User.id == user_id).with_for_update())
    if not user or not user.is_active: raise LedgerError('Inactive user')

def treasury_owner(db: Session) -> int:
    owner = db.scalar(select(User.id).where(User.role == 'superworker', User.is_active.is_(True)).order_by(User.id).limit(1))
    if owner is None: raise LedgerError('Demo treasury is not initialized; run seed')
    return owner

def locked_accounts(db: Session, keys: list[tuple[int, str, str]]) -> dict:
    """Create missing zero accounts safely, then lock all legs in global ID order."""
    result = {}
    for owner, kind, currency in sorted(set(keys)):
        query = select(Account).where(Account.user_id == owner, Account.type == kind, Account.currency == currency)
        account = db.scalar(query)
        if account is None:
            db.execute(insert(Account).values(user_id=owner, type=kind, currency=currency,
                normal_side='credit' if kind == 'system' else 'debit').on_conflict_do_nothing(
                    index_elements=['user_id','type','currency']))
            account = db.scalar(query)
        result[owner, kind, currency] = account
    db.scalars(select(Account).where(Account.id.in_([a.id for a in result.values()])).order_by(Account.id)
               .with_for_update().execution_options(populate_existing=True)).all()
    return result

def transfer(db, source, target, amount, kind, actor, note, request_id=None):
    if amount:
        post_entry(db, debit_account_id=source.id, credit_account_id=target.id,
                   amount=amount, kind=kind, actor_id=actor, note=note, request_id=request_id)

def order_cost(qty, price):
    notional = rounded(qty * price)
    if notional <= 0: raise LedgerError('Trade value is below eight-decimal precision')
    return notional, rounded(notional * FEE_RATE)

def execute_order(db: Session, order: Order, provider: MarketDataProvider, price: Decimal | None = None):
    if order.status != 'open': raise LedgerError('Only open orders can execute')
    asset = parse_pair(order.pair)
    if asset in ('XAU','XAG') and price is None:
        raise MarketDataUnavailable('Metal market data provider is not configured')
    price = rounded(price if price is not None else provider.get_price(asset))
    if price <= 0: raise LedgerError('Invalid execution price')
    with db.begin_nested():
        lock_user(db, order.user_id)
        owner = treasury_owner(db)
        accounts = locked_accounts(db, [(who, kind, c) for who,kind in [(owner,'system'),(order.user_id,'main')] for c in (asset,'USDT')])
        base, quote = accounts[order.user_id,'main',asset], accounts[order.user_id,'main','USDT']
        base_treasury, quote_treasury = accounts[owner,'system',asset], accounts[owner,'system','USDT']
        cost, fee = order_cost(order.qty, price)
        note = f'Paper order {order.id}'
        if order.side == 'buy':
            if quote.balance < cost + fee: raise LedgerError('Insufficient virtual funds')
            transfer(db, quote, quote_treasury, cost, 'trade', order.user_id, note)
            transfer(db, base_treasury, base, order.qty, 'trade', order.user_id, note)
        else:
            if base.balance < order.qty: raise LedgerError('Insufficient virtual funds')
            transfer(db, base, base_treasury, order.qty, 'trade', order.user_id, note)
            transfer(db, quote_treasury, quote, cost, 'trade', order.user_id, note)
        transfer(db, quote, quote_treasury, fee, 'fee', order.user_id, note)
        order.status, order.filled_price = 'filled', price
        order.fee_amount, order.fee_currency = fee, 'USDT'
        db.add(AuditLog(actor_id=order.user_id, action='orders.filled', entity='orders', entity_id=order.id,
                        after_json={'price':str(price),'fee':str(fee),'execution_status':'simulated'}))
        db.flush()
    return order

def create_order(db: Session, user_id: int, body, provider: MarketDataProvider):
    require_office_feature(db, user_id, 'trading_enabled')
    asset = parse_pair(body.pair)
    with db.begin_nested():
        lock_user(db, user_id)
        order = Order(user_id=user_id, pair=asset+'USDT', side=body.side, type=body.type,
                      qty=body.qty, price=body.price, status='open')
        db.add(order); db.flush()
        if body.type == 'market': execute_order(db, order, provider)
        else:
            # Limits are not reserved. Recheck affordability at execution time.
            accounts = locked_accounts(db, [(user_id,'main',asset),(user_id,'main','USDT')])
            cost, fee = order_cost(body.qty, body.price)
            source = accounts[user_id,'main','USDT' if body.side == 'buy' else asset]
            if source.balance < (cost+fee if body.side == 'buy' else body.qty):
                raise LedgerError('Insufficient virtual funds')
        return order

def execute_swap(db: Session, user_id: int, body, provider: MarketDataProvider):
    require_office_feature(db, user_id, 'swap_enabled')
    source_price, target_price = provider.get_price(body.from_currency), provider.get_price(body.to_currency)
    if source_price <= 0 or target_price <= 0: raise LedgerError('Invalid market price')
    rate = source_price / target_price
    fee = rounded(body.amount * FEE_RATE)
    output = rounded((body.amount-fee) * rate)
    if output <= 0: raise LedgerError('Swap value is below eight-decimal precision')
    with db.begin_nested():
        lock_user(db, user_id)
        accounts = locked_accounts(db, [(user_id,'main',body.from_currency)])
        source = accounts[user_id,'main',body.from_currency]
        pending = db.scalar(select(func.coalesce(func.sum(Swap.from_amount), 0)).where(
            Swap.user_id == user_id, Swap.from_currency == body.from_currency, Swap.status == 'pending'))
        if source.balance - pending < body.amount: raise LedgerError('Insufficient virtual funds after pending swaps')
        swap = Swap(user_id=user_id,from_currency=body.from_currency,to_currency=body.to_currency,
                    from_amount=body.amount,to_amount=output,rate=rounded(rate),fee=fee,status='pending')
        db.add(swap);db.flush()
        return swap

def open_stake(db: Session, user_id: int, body):
    with db.begin_nested():
        lock_user(db,user_id)
        plan = db.scalar(select(StakePlan).where(StakePlan.id == body.plan_id).with_for_update())
        if not plan or not plan.is_active: raise LedgerError('Stake plan is unavailable')
        if plan.currency != 'USDT': raise LedgerError('Only USDT can be placed in CDT')
        if plan.apy != Decimal('20'): raise LedgerError('CDT annual yield must be 20%')
        if body.amount < plan.min_amount: raise LedgerError('Amount is below plan minimum')
        if plan.term_days <= 0: raise LedgerError('Invalid plan term')
        accounts = locked_accounts(db,[(user_id,'main',plan.currency)])
        pending = db.scalar(select(func.coalesce(func.sum(StakePosition.amount), 0)).where(
            StakePosition.user_id == user_id, StakePosition.status == 'pending', StakePosition.plan_id == plan.id))
        if accounts[user_id,'main',plan.currency].balance - pending < body.amount:
            raise LedgerError('Insufficient virtual funds after pending CDT requests')
        position = StakePosition(user_id=user_id,plan_id=plan.id,amount=body.amount,yield_accrued=Decimal('0'),
                                 status='pending',opened_at=None,closes_at=None)
        db.add(position);db.flush()
        return position

def request_withdrawal(db: Session, user_id: int, body):
    with db.begin_nested():
        require_office_feature(db, user_id, 'withdrawals_enabled')
        lock_user(db,user_id)
        method = db.scalar(select(PaymentMethod).where(
            PaymentMethod.id == body.payment_method_id,
            PaymentMethod.user_id == user_id,
            PaymentMethod.is_active.is_(True),
        ).with_for_update())
        if method is None: raise LedgerError('Payment method does not belong to this user')
        if method.type == 'crypto':
            network, destination = method.network, method.wallet_address
        elif method.type == 'bank':
            network, destination = 'BANK', f'{method.bank_name} ••••{method.account_last4}'
        else:
            network, destination = 'CARD', f'{method.card_brand} ••••{method.card_last4}'
        account = db.scalar(select(Account).where(Account.user_id == user_id, Account.type == 'main', Account.currency == body.currency).with_for_update())
        pending = db.scalar(select(func.coalesce(func.sum(PaymentRequest.amount_requested), 0)).where(
            PaymentRequest.user_id == user_id, PaymentRequest.currency == body.currency,
            PaymentRequest.method == 'simulated-withdrawal', PaymentRequest.status == 'pending'))
        if account is None or account.balance - pending < body.amount: raise LedgerError('Insufficient virtual funds after pending withdrawals')
        payment = PaymentRequest(user_id=user_id,currency=body.currency,network=network,
            amount_requested=body.amount,method='simulated-withdrawal',status='pending',
            execution_status='simulated',destination_address=destination,payment_method_id=method.id)
        db.add(payment);db.flush()
        return payment
