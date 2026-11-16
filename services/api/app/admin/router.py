from datetime import datetime,timezone
from typing import Annotated,Literal
import json
from fastapi import APIRouter,Depends,Header,HTTPException,Query,Request
from pydantic import ValidationError
from sqlalchemy import select,func,or_
from app.models.schema import User,Account,Transaction,PaymentRequest,KYCDocument,AuditLog,DepositWallet,Swap,StakePlan,Ticket,TicketMessage,Notification
from app.routers.auth import DB,require_staff
from app.admin.schemas import parse_action
from app.admin.service import execute,scope,target_user,row_data

router=APIRouter(prefix='/api/admin',tags=['admin'])
Staff=Annotated[User,Depends(require_staff)]

def read_audit(db,actor,entity,filters=None):
    db.add(AuditLog(actor_id=actor.id,action='admin.read',entity=entity,after_json=filters or {}))
    db.commit()

def paginated(db,query,page,size):
    total=db.scalar(select(func.count()).select_from(query.order_by(None).subquery()))
    items=db.scalars(query.offset((page-1)*size).limit(size)).all()
    return {'items':[row_data(row) for row in items],'total':total,'page':page,'page_size':size,'pages':(total+size-1)//size}

def allowed_ids(actor):return select(User.id).where(*scope(actor))

@router.post('/actions')
def actions(raw:dict,request:Request,actor:Staff,db:DB,idempotency_key:Annotated[str|None,Header(min_length=1,max_length=128)]=None):
    try:body=parse_action(raw)
    except ValidationError as exc:raise HTTPException(422,json.loads(exc.json()))
    except ValueError as exc:raise HTTPException(422,str(exc))
    return execute(db,actor,body,idempotency_key,request.client.host if request.client else None)

@router.get('/users')
def users(actor:Staff,db:DB,q:str=Query('',max_length=200),kyc:Literal['none','pending','verified','rejected']|None=None,
          country:str|None=Query(None,max_length=100),active:bool|None=None,page:int=Query(1,ge=1),page_size:int=Query(20,ge=1,le=100)):
    query=select(User).where(*scope(actor))
    if q:query=query.where(or_(User.email.ilike('%'+q+'%'),User.full_name.ilike('%'+q+'%'),User.phone.ilike('%'+q+'%')))
    if kyc:query=query.where(User.kyc_status==kyc)
    if country:query=query.where(func.lower(User.country)==country.lower())
    if active is not None:query=query.where(User.is_active==active)
    result=paginated(db,query.order_by(User.id.desc()),page,page_size)
    read_audit(db,actor,'users',{'q':q,'kyc':kyc,'country':country,'active':active,'page':page})
    return result

@router.get('/users/{user_id}')
def user_detail(user_id:int,actor:Staff,db:DB):
    user=target_user(db,actor,user_id)
    accounts=db.scalars(select(Account).where(Account.user_id==user.id).order_by(Account.currency,Account.type)).all()
    docs=db.scalars(select(KYCDocument).where(KYCDocument.user_id==user.id).order_by(KYCDocument.id)).all()
    transactions=db.scalars(select(Transaction).join(Account).where(Account.user_id==user.id).order_by(Transaction.id.desc()).limit(100)).all()
    result={'profile':row_data(user),'accounts':[row_data(a) for a in accounts],
            'documents':[row_data(d) for d in docs],'transactions':[row_data(t) for t in transactions]}
    read_audit(db,actor,'users',{'user_id':user.id})
    return result

@router.get('/payments')
def payments(actor:Staff,db:DB,status:Literal['pending','approved','rejected','reverted']|None=None,
             page:int=Query(1,ge=1),page_size:int=Query(20,ge=1,le=100)):
    query=select(PaymentRequest).where(PaymentRequest.user_id.in_(allowed_ids(actor)))
    if status:query=query.where(PaymentRequest.status==status)
    result=paginated(db,query.order_by(PaymentRequest.id.desc()),page,page_size)
    read_audit(db,actor,'payment_requests',{'status':status,'page':page})
    return result

@router.get('/kyc/queue')
def kyc_queue(actor:Staff,db:DB,page:int=Query(1,ge=1),page_size:int=Query(20,ge=1,le=100)):
    query=select(KYCDocument).where(KYCDocument.user_id.in_(allowed_ids(actor)),KYCDocument.status=='pending')
    result=paginated(db,query.order_by(KYCDocument.id),page,page_size)
    read_audit(db,actor,'kyc_documents',{'page':page})
    return result

@router.get('/swaps')
def swaps(actor:Staff,db:DB,page:int=Query(1,ge=1),page_size:int=Query(20,ge=1,le=100)):
    result=paginated(db,select(Swap).where(Swap.user_id.in_(allowed_ids(actor))).order_by(Swap.id.desc()),page,page_size)
    read_audit(db,actor,'swaps');return result

@router.get('/deposit-wallets')
def wallets(actor:Staff,db:DB):
    result={'items':[row_data(w) for w in db.scalars(select(DepositWallet).order_by(DepositWallet.id)).all()]}
    read_audit(db,actor,'wallets_deposit');return result

@router.get('/stake-plans')
def stake_plans(actor:Staff,db:DB):
    result={'items':[row_data(p) for p in db.scalars(select(StakePlan).order_by(StakePlan.id)).all()]}
    read_audit(db,actor,'stake_plans');return result

@router.get('/notifications')
def notifications(actor:Staff,db:DB,page:int=Query(1,ge=1),page_size:int=Query(20,ge=1,le=100)):
    result=paginated(db,select(Notification).where(Notification.user_id.in_(allowed_ids(actor))).order_by(Notification.id.desc()),page,page_size)
    read_audit(db,actor,'notifications');return result

@router.get('/tickets')
def tickets(actor:Staff,db:DB,page:int=Query(1,ge=1),page_size:int=Query(20,ge=1,le=100)):
    result=paginated(db,select(Ticket).where(Ticket.user_id.in_(allowed_ids(actor))).order_by(Ticket.id.desc()),page,page_size)
    read_audit(db,actor,'tickets');return result

@router.get('/tickets/{ticket_id}/messages')
def messages(ticket_id:int,actor:Staff,db:DB):
    ticket=db.get(Ticket,ticket_id)
    if ticket is None:raise HTTPException(404,'Ticket not found')
    target_user(db,actor,ticket.user_id)
    rows=db.scalars(select(TicketMessage).where(TicketMessage.ticket_id==ticket_id).order_by(TicketMessage.id).limit(200)).all()
    read_audit(db,actor,'ticket_messages',{'ticket_id':ticket_id})
    return {'items':[row_data(m) for m in rows]}

@router.get('/production')
def production(actor:Staff,db:DB,from_:Annotated[datetime|None,Query(alias='from')]=None,to:datetime|None=None):
    start=from_.replace(tzinfo=timezone.utc) if from_ and from_.tzinfo is None else from_
    end=to.replace(tzinfo=timezone.utc) if to and to.tzinfo is None else to
    if start and end and start>end:raise HTTPException(422,'from must precede to')
    def window(model):
        return ([model.created_at>=start] if start else [])+([model.created_at<=end] if end else [])
    ids=allowed_ids(actor)
    def count(model,extra=()):
        clause=[*scope(actor),User.role=='client'] if model==User else [model.user_id.in_(ids)]
        return db.scalar(select(func.count(model.id)).where(*clause,*window(model),*extra))
    def totals(resolution):
        rows=db.execute(select(PaymentRequest.currency,func.sum(PaymentRequest.amount_approved)).where(
            PaymentRequest.user_id.in_(ids),PaymentRequest.ledger_resolution==resolution,*window(PaymentRequest)).group_by(PaymentRequest.currency)).all()
        return {c:str(v or 0) for c,v in rows}
    swap_rows=db.execute(select(Swap.from_currency,func.sum(Swap.from_amount)).where(Swap.user_id.in_(ids),*window(Swap)).group_by(Swap.from_currency)).all()
    result={'users_new':count(User),'pending_payments':count(PaymentRequest,[PaymentRequest.status=='pending']),
            'pending_kyc':count(KYCDocument,[KYCDocument.status=='pending']),
            'deposits_by_currency':totals('credited'),'withdrawals_by_currency':totals('paid'),
            'swaps_count':count(Swap),'swap_volume_by_currency':{c:str(v) for c,v in swap_rows},
            'tickets_open':count(Ticket,[Ticket.status=='open'])}
    read_audit(db,actor,'production',{'from':start.isoformat() if start else None,'to':end.isoformat() if end else None})
    return result

@router.get('/ranking')
def ranking(actor:Staff,db:DB):
    rows=db.execute(select(User.id,User.full_name,Account.balance).join(Account).where(
        *scope(actor),User.role=='client',Account.type=='main',Account.currency=='USDT').order_by(Account.balance.desc(),User.id).limit(20)).all()
    result={'items':[{'user_id':i,'full_name':name,'virtual_usdt_balance':str(balance)} for i,name,balance in rows]}
    read_audit(db,actor,'ranking');return result

@router.get('/cards')
def cards(actor:Staff,db:DB):
    read_audit(db,actor,'cards');return {'items':[],'message':'Entorno demo sin emisión de tarjetas'}
