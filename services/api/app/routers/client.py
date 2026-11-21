from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import or_, select

from app.models.schema import (
    Account,
    Notification,
    PaymentRequest,
    PaymentMethod,
    Ticket,
    TicketMessage,
    Transaction,
    User,
)
from app.routers.auth import DB, current_user
from app.schemas.client import DepositRequestBody, PaymentMethodBody, TicketBody


router = APIRouter(prefix='/api', tags=['customer'])
Client = Annotated[User, Depends(current_user)]
PageSize = Annotated[int, Query(ge=1, le=200)]


def data(row, *fields):
    return {field: getattr(row, field) for field in fields}


PAYMENT_METHOD_FIELDS = (
    'id', 'type', 'label', 'holder_name', 'bank_country', 'bank_id', 'bank_name', 'account_type',
    'account_last4', 'card_brand', 'card_last4', 'network', 'wallet_address',
    'is_active', 'created_at',
)


def owned_method(db, user_id: int, method_id: int):
    method = db.scalar(select(PaymentMethod).where(
        PaymentMethod.id == method_id,
        PaymentMethod.user_id == user_id,
        PaymentMethod.is_active.is_(True),
    ))
    if method is None:
        raise HTTPException(404, 'Payment method does not belong to this user')
    return method


@router.get('/account')
def account(user: Client, db: DB):
    accounts = db.scalars(
        select(Account)
        .where(Account.user_id == user.id, Account.type.in_(('main', 'staking', 'escrow')))
        .order_by(Account.type, Account.currency)
    ).all()
    return {
        'user': data(user, 'id', 'email', 'full_name', 'role', 'kyc_status', 'referral_code'),
        'accounts': [data(row, 'id', 'type', 'currency', 'balance', 'updated_at') for row in accounts],
    }


@router.get('/account/transactions')
def transactions(user: Client, db: DB, limit: PageSize = 50):
    account_ids = select(Account.id).where(Account.user_id == user.id)
    rows = db.scalars(
        select(Transaction)
        .where(Transaction.account_id.in_(account_ids))
        .order_by(Transaction.id.desc())
        .limit(limit)
    ).all()
    return {
        'items': [data(
            row, 'id', 'account_id', 'kind', 'amount', 'currency', 'network',
            'status', 'staff_note', 'request_id', 'original_transaction_id', 'created_at',
        ) for row in rows]
    }


@router.post('/payments/deposit-request', status_code=201)
def deposit_request(body: DepositRequestBody, user: Client, db: DB):
    method = owned_method(db, user.id, body.payment_method_id) if body.payment_method_id else None
    request = PaymentRequest(
        user_id=user.id,
        currency=body.currency,
        network=(method.network if method and method.type == 'crypto' else body.network) or (method.type.upper() if method else 'DEMO'),
        amount_requested=body.amount,
        method=f'simulated-deposit:{method.type}' if method else body.method,
        payment_method_id=method.id if method else None,
        status='pending',
        execution_status='simulated',
        ledger_resolution='unsettled',
    )
    db.add(request)
    db.commit()
    db.refresh(request)
    return data(
        request, 'id', 'user_id', 'currency', 'network', 'amount_requested',
        'amount_approved', 'method', 'payment_method_id', 'status', 'execution_status', 'ledger_resolution', 'created_at',
    )


@router.get('/payments/requests')
def payment_requests(user: Client, db: DB, limit: PageSize = 100):
    rows = db.scalars(
        select(PaymentRequest)
        .where(PaymentRequest.user_id == user.id)
        .order_by(PaymentRequest.id.desc())
        .limit(limit)
    ).all()
    return {'items': [data(
        row, 'id', 'user_id', 'currency', 'network', 'amount_requested',
        'amount_approved', 'method', 'payment_method_id', 'status', 'execution_status',
        'ledger_resolution', 'staff_note', 'created_at',
    ) for row in rows]}


@router.get('/payments/methods')
def payment_methods(user: Client, db: DB):
    rows = db.scalars(select(PaymentMethod).where(
        PaymentMethod.user_id == user.id,
        PaymentMethod.is_active.is_(True),
    ).order_by(PaymentMethod.id.desc())).all()
    return {'items': [data(row, *PAYMENT_METHOD_FIELDS) for row in rows]}


@router.post('/payments/methods', status_code=201)
def create_payment_method(body: PaymentMethodBody, user: Client, db: DB):
    values = body.model_dump()
    method = PaymentMethod(user_id=user.id, **values)
    db.add(method)
    db.commit()
    db.refresh(method)
    return data(method, *PAYMENT_METHOD_FIELDS)


@router.delete('/payments/methods/{method_id}')
def delete_payment_method(method_id: int, user: Client, db: DB):
    method = owned_method(db, user.id, method_id)
    method.is_active = False
    db.commit()
    return {'id': method.id, 'is_active': False}


@router.get('/notifications')
def notifications(
    user: Client,
    db: DB,
    limit: PageSize = 50,
    unread: bool = False,
):
    query = select(Notification).where(or_(
        Notification.user_id == user.id,
        Notification.user_id.is_(None),
    ))
    if unread:
        query = query.where(Notification.is_read.is_(False))
    rows = db.scalars(query.order_by(Notification.id.desc()).limit(limit)).all()
    return {'items': [data(
        row, 'id', 'user_id', 'scope', 'type', 'title', 'body', 'is_read', 'created_at',
    ) for row in rows]}


@router.post('/notifications/{notification_id}/read')
def notification_read(notification_id: int, user: Client, db: DB):
    notice = db.scalar(select(Notification).where(
        Notification.id == notification_id,
        Notification.user_id == user.id,
    ))
    if notice is None:
        raise HTTPException(404, 'Notification not found')
    notice.is_read = True
    db.commit()
    return {'id': notice.id, 'is_read': True}


@router.post('/tickets', status_code=201)
def create_ticket(body: TicketBody, user: Client, db: DB):
    ticket = Ticket(user_id=user.id, subject=body.subject, status='open')
    db.add(ticket)
    db.flush()
    db.add(TicketMessage(ticket_id=ticket.id, sender_id=user.id, body=body.body))
    db.commit()
    db.refresh(ticket)
    return data(ticket, 'id', 'subject', 'status', 'created_at')


@router.get('/tickets')
def tickets(user: Client, db: DB, limit: PageSize = 100):
    rows = db.scalars(
        select(Ticket)
        .where(Ticket.user_id == user.id)
        .order_by(Ticket.id.desc())
        .limit(limit)
    ).all()
    return {'items': [data(row, 'id', 'subject', 'status', 'created_at') for row in rows]}


@router.get('/tickets/{ticket_id}/messages')
def ticket_messages(ticket_id: int, user: Client, db: DB):
    ticket = db.scalar(select(Ticket).where(Ticket.id == ticket_id, Ticket.user_id == user.id))
    if ticket is None:
        raise HTTPException(404, 'Ticket not found')
    rows = db.scalars(
        select(TicketMessage)
        .where(TicketMessage.ticket_id == ticket.id)
        .order_by(TicketMessage.id)
    ).all()
    return {
        'ticket': data(ticket, 'id', 'subject', 'status', 'created_at'),
        'items': [data(row, 'id', 'sender_id', 'body', 'created_at') for row in rows],
    }
