"""Async scheduling with synchronous DB/provider work off the event loop."""
import asyncio
from datetime import datetime, timedelta, timezone
import logging
from sqlalchemy import select
from app.models.schema import Order, AuditLog
from app.services.paper import execute_order, parse_pair
from app.services.ledger import LedgerError
from app.services.marketdata import MarketDataUnavailable

logger = logging.getLogger(__name__)

def process_open_orders(session_factory, provider, now=None):
    now = now or datetime.now(timezone.utc)
    with session_factory() as db:
        ids = db.scalars(select(Order.id).where(Order.status == 'open',Order.type == 'limit').order_by(Order.id)).all()
    for order_id in ids:
        try:
            with session_factory.begin() as db:
                order = db.scalar(select(Order).where(Order.id == order_id,Order.status == 'open')
                                  .with_for_update(skip_locked=True))
                if order is None: continue
                if now >= order.created_at + timedelta(hours=24):
                    order.status = 'expired'
                    db.add(AuditLog(actor_id=order.user_id,action='orders.expired',entity='orders',entity_id=order.id))
                    continue
                price = provider.get_price(parse_pair(order.pair))
                crossed = price <= order.price if order.side == 'buy' else price >= order.price
                if crossed: execute_order(db,order,provider,price)
        except (LedgerError, MarketDataUnavailable):
            # No reservation: insufficient funds/quotes leave it open until expiry.
            logger.info('Limit order %s awaits funds or a usable quote',order_id)
        except Exception:
            logger.exception('Limit order %s failed; transaction rolled back',order_id)

async def run_limit_worker(stop, session_factory, provider, interval=5):
    while not stop.is_set():
        try: await asyncio.to_thread(process_open_orders,session_factory,provider)
        except Exception: logger.exception('Limit order scan failed; retrying next poll')
        try: await asyncio.wait_for(stop.wait(),timeout=interval)
        except TimeoutError: pass
