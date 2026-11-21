from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from app.models.schema import User, Order, Swap, StakePlan, StakePosition, DepositWallet
from app.routers.auth import DB, current_user
from app.routers.market import Provider
from app.schemas.trading import (OrderBody, OrderOut, SwapBody, SwapOut, StakeBody,
                                 PlanOut, PositionOut, WithdrawalBody, WithdrawalOut, WalletOut)
from app.services.paper import create_order, execute_swap, open_stake, request_withdrawal

router = APIRouter(prefix='/api', tags=['paper trading'])
Client = Annotated[User, Depends(current_user)]
PageSize = Annotated[int, Query(ge=1,le=500)]

@router.post('/orders',response_model=OrderOut,status_code=201)
def order(body: OrderBody, user: Client, db: DB, provider: Provider):
    result = create_order(db,user.id,body,provider)
    db.commit()
    return result

@router.get('/orders',response_model=list[OrderOut])
def orders(user: Client, db: DB, limit: PageSize = 100):
    return db.scalars(select(Order).where(Order.user_id == user.id).order_by(Order.id.desc()).limit(limit)).all()

@router.delete('/orders/{order_id}',response_model=OrderOut)
def cancel_order(order_id: int, user: Client, db: DB):
    order = db.scalar(select(Order).where(Order.id == order_id,Order.user_id == user.id).with_for_update())
    if order is None: raise HTTPException(404,'Order not found')
    if order.status != 'open': raise HTTPException(409,'Only open orders can be cancelled')
    order.status = 'cancelled'
    db.commit()
    return order

@router.post('/swaps',response_model=SwapOut,status_code=201)
def swap(body: SwapBody, user: Client, db: DB, provider: Provider):
    result = execute_swap(db,user.id,body,provider)
    db.commit()
    return result

@router.get('/swaps',response_model=list[SwapOut])
def swaps(user: Client, db: DB, limit: PageSize = 100):
    return db.scalars(select(Swap).where(Swap.user_id == user.id).order_by(Swap.id.desc()).limit(limit)).all()

@router.get('/stake/plans',response_model=list[PlanOut])
def plans(db: DB):
    return db.scalars(select(StakePlan).where(
        StakePlan.is_active.is_(True), StakePlan.currency == 'USDT', StakePlan.apy == 20,
    ).order_by(StakePlan.id)).all()

@router.post('/stake/positions',response_model=PositionOut,status_code=201)
def stake(body: StakeBody, user: Client, db: DB):
    result = open_stake(db,user.id,body)
    db.commit()
    return result

@router.get('/stake/positions',response_model=list[PositionOut])
def positions(user: Client, db: DB, limit: PageSize = 100):
    return db.scalars(select(StakePosition).where(StakePosition.user_id == user.id).order_by(StakePosition.id.desc()).limit(limit)).all()

@router.post('/payments/withdrawal-request',response_model=WithdrawalOut,status_code=201)
def withdrawal(body: WithdrawalBody, user: Client, db: DB):
    result = request_withdrawal(db,user.id,body)
    db.commit()
    return result

@router.get('/payments/deposit-wallets',response_model=list[WalletOut])
def deposit_wallets(user: Client, db: DB):
    return db.scalars(select(DepositWallet).where(DepositWallet.is_active.is_(True)).order_by(DepositWallet.id)).all()
