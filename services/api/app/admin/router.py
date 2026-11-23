from datetime import datetime,timezone,timedelta,time
from zoneinfo import ZoneInfo
from typing import Annotated,Literal
import json
import secrets
from fastapi import APIRouter,Depends,Header,HTTPException,Query,Request
from fastapi.responses import Response
from pydantic import BaseModel, EmailStr, Field, ValidationError
from sqlalchemy import select,func,or_
from app.models.schema import User,Office,Account,Transaction,PaymentRequest,PaymentMethod,KYCDocument,AuditLog,DepositWallet,Swap,StakePlan,StakePosition,Ticket,TicketMessage,Notification
from app.routers.auth import DB,require_staff,current_registration_code
from app.core.security import hasher
from app.core.field_crypto import decrypt_field
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

class OfficeCreate(BaseModel):
    name:str=Field(min_length=2,max_length=160)
class OfficeFeatures(BaseModel):
    trading_enabled:bool
    swap_enabled:bool
    withdrawals_enabled:bool
class OfficeAdminCreate(BaseModel):
    office_id:int=Field(gt=0)
    email:EmailStr
    full_name:str=Field(min_length=2,max_length=200)
    password:str=Field(min_length=12,max_length=128)
class MessageCreate(BaseModel):
    body:str=Field(min_length=1,max_length=5000)

def super_only(actor):
    if actor.role!='superworker':raise HTTPException(403,'Super Admin role required')

@router.get('/offices')
def offices(actor:Staff,db:DB):
    query=select(Office)
    if actor.role!='superworker':query=query.where(Office.id==actor.office_id)
    rows=db.scalars(query.order_by(Office.name)).all()
    return {'items':[{**row_data(row),'registration_code':current_registration_code(row)} for row in rows]}

@router.post('/offices',status_code=201)
def create_office(body:OfficeCreate,actor:Staff,db:DB):
    super_only(actor)
    row=Office(name=body.name,token_secret=secrets.token_hex(32));db.add(row);db.flush()
    db.add(AuditLog(actor_id=actor.id,action='admin.office_create',entity='offices',entity_id=row.id,after_json={'name':row.name}))
    db.commit();return {**row_data(row),'registration_code':current_registration_code(row)}

@router.patch('/offices/{office_id}')
def update_office(office_id:int,body:OfficeFeatures,actor:Staff,db:DB):
    if actor.role!='superworker' and actor.office_id!=office_id:raise HTTPException(403,'Office outside your scope')
    row=db.get(Office,office_id)
    if row is None:raise HTTPException(404,'Office not found')
    before=row_data(row)
    for name,value in body.model_dump().items():setattr(row,name,value)
    db.add(AuditLog(actor_id=actor.id,action='admin.office_features',entity='offices',entity_id=row.id,before_json=before,after_json=row_data(row)))
    db.commit();return row_data(row)

@router.post('/office-admins',status_code=201)
def create_office_admin(body:OfficeAdminCreate,actor:Staff,db:DB):
    super_only(actor)
    if db.get(Office,body.office_id) is None:raise HTTPException(404,'Office not found')
    row=User(email=str(body.email).lower(),full_name=body.full_name,password_hash=hasher.hash(body.password),role='staff',office_id=body.office_id)
    db.add(row);db.flush();db.add(AuditLog(actor_id=actor.id,action='admin.office_admin_create',entity='users',entity_id=row.id,after_json={'office_id':body.office_id,'email':row.email}))
    db.commit();return row_data(row)

@router.delete('/offices/{office_id}',status_code=204)
def delete_office(office_id:int,actor:Staff,db:DB):
    super_only(actor);row=db.get(Office,office_id)
    if row is None:raise HTTPException(404,'Office not found')
    if db.scalar(select(func.count(User.id)).where(User.office_id==office_id)):raise HTTPException(409,'Office has users; disable it instead')
    db.delete(row);db.commit()

@router.post('/actions')
def actions(raw:dict,request:Request,actor:Staff,db:DB,idempotency_key:Annotated[str|None,Header(min_length=1,max_length=128)]=None):
    try:body=parse_action(raw)
    except ValidationError as exc:raise HTTPException(422,json.loads(exc.json()))
    except ValueError as exc:raise HTTPException(422,str(exc))
    return execute(db,actor,body,idempotency_key,request.client.host if request.client else None)

@router.get('/users')
def users(actor:Staff,db:DB,q:str=Query('',max_length=200),kyc:Literal['none','pending','verified','rejected']|None=None,
          country:str|None=Query(None,max_length=100),active:bool|None=None,role:Literal['client','staff','superworker']|None=None,
          page:int=Query(1,ge=1),page_size:int=Query(20,ge=1,le=100)):
    query=select(User).where(*scope(actor))
    if q:query=query.where(or_(User.email.ilike('%'+q+'%'),User.full_name.ilike('%'+q+'%'),User.phone.ilike('%'+q+'%')))
    if kyc:query=query.where(User.kyc_status==kyc)
    if country:query=query.where(func.lower(User.country)==country.lower())
    if active is not None:query=query.where(User.is_active==active)
    if role:query=query.where(User.role==role)
    result=paginated(db,query.order_by(User.id.desc()),page,page_size)
    read_audit(db,actor,'users',{'q':q,'kyc':kyc,'country':country,'active':active,'role':role,'page':page})
    return result

@router.get('/dashboard')
def dashboard(actor:Staff,db:DB):
    colombia=ZoneInfo('America/Bogota')
    today=datetime.now(colombia).date()
    first=today-timedelta(days=6)
    start=datetime.combine(first,time.min,tzinfo=colombia).astimezone(timezone.utc)
    query=select(User.created_at).where(*scope(actor),User.role=='client',User.created_at>=start)
    counts={first+timedelta(days=offset):0 for offset in range(7)}
    for created_at in db.scalars(query):
        day=created_at.astimezone(colombia).date()
        if day in counts:counts[day]+=1
    total=db.scalar(select(func.count(User.id)).where(*scope(actor),User.role=='client'))
    active=db.scalar(select(func.count(User.id)).where(*scope(actor),User.role=='client',User.is_active.is_(True)))
    read_audit(db,actor,'dashboard')
    return {'users_total':total,'users_active':active,
            'registrations_7d':[{'date':day.isoformat(),'count':count} for day,count in counts.items()]}

@router.get('/users/{user_id}')
def user_detail(user_id:int,actor:Staff,db:DB):
    user=target_user(db,actor,user_id)
    accounts=db.scalars(select(Account).where(Account.user_id==user.id).order_by(Account.currency,Account.type)).all()
    docs=db.scalars(select(KYCDocument).where(KYCDocument.user_id==user.id).order_by(KYCDocument.id)).all()
    transactions=db.scalars(select(Transaction).join(Account).where(Account.user_id==user.id).order_by(Transaction.id.desc()).limit(100)).all()
    methods=db.scalars(select(PaymentMethod).where(PaymentMethod.user_id==user.id).order_by(PaymentMethod.id.desc())).all()
    result={'profile':row_data(user),'accounts':[row_data(a) for a in accounts],
            'documents':[row_data(d) for d in docs],'transactions':[row_data(t) for t in transactions],
            'payment_methods':[row_data(m) for m in methods]}
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

@router.get('/payment-methods')
def payment_methods(actor:Staff,db:DB,page:int=Query(1,ge=1),page_size:int=Query(20,ge=1,le=100)):
    result=paginated(db,select(PaymentMethod).where(PaymentMethod.user_id.in_(allowed_ids(actor))).order_by(PaymentMethod.id.desc()),page,page_size)
    for item in result['items']:
        item.pop('bank_account_encrypted',None)
        row=db.get(PaymentMethod,item['id'])
        item['bank_account']=decrypt_field(row.bank_account_encrypted) if row and row.type=='bank' else None
    read_audit(db,actor,'payment_methods',{'page':page})
    return result

@router.get('/kyc/queue')
def kyc_queue(actor:Staff,db:DB,page:int=Query(1,ge=1),page_size:int=Query(20,ge=1,le=100)):
    query=select(KYCDocument).where(KYCDocument.user_id.in_(allowed_ids(actor)),KYCDocument.status=='pending',KYCDocument.user_id.in_(select(User.id).where(User.kyc_status=='pending')))
    result=paginated(db,query.order_by(KYCDocument.id),page,page_size)
    read_audit(db,actor,'kyc_documents',{'page':page})
    return result

@router.get('/kyc/documents')
def kyc_documents(actor:Staff,db:DB,status:Literal['pending','approved','rejected']|None=None,
                  q:str=Query('',max_length=200),country:str|None=Query(None,max_length=100),
                  page:int=Query(1,ge=1),page_size:int=Query(20,ge=1,le=100)):
    query=select(KYCDocument).join(User,KYCDocument.user_id==User.id).where(*scope(actor))
    if status:query=query.where(KYCDocument.status==status)
    if q:query=query.where(or_(User.email.ilike('%'+q+'%'),User.full_name.ilike('%'+q+'%'),User.phone.ilike('%'+q+'%')))
    if country:query=query.where(func.lower(User.country)==country.lower())
    result=paginated(db,query.order_by(KYCDocument.id.desc()),page,page_size)
    user_ids={item['user_id'] for item in result['items']}
    people={row.id:row for row in db.scalars(select(User).where(User.id.in_(user_ids))).all()}
    for item in result['items']:
        person=people[item['user_id']]
        item['user_name']=person.full_name
        item['user_email']=person.email
        item['user_country']=person.country
        item['user_kyc_status']=person.kyc_status
    read_audit(db,actor,'kyc_documents',{'status':status,'q':q,'country':country,'page':page})
    return result

@router.get('/kyc/documents/{document_id}/image')
def kyc_image(document_id:int,actor:Staff,db:DB):
    doc=db.get(KYCDocument,document_id)
    if doc is None:raise HTTPException(404,'Document not found')
    target_user(db,actor,doc.user_id)
    if not doc.file_data or not doc.mime_type:raise HTTPException(404,'Document image not available')
    read_audit(db,actor,'kyc_document_image',{'document_id':doc.id})
    return Response(content=doc.file_data,media_type=doc.mime_type,headers={'Cache-Control':'no-store','Content-Disposition':'inline'})

@router.get('/swaps')
def swaps(actor:Staff,db:DB,page:int=Query(1,ge=1),page_size:int=Query(20,ge=1,le=100)):
    result=paginated(db,select(Swap).where(Swap.user_id.in_(allowed_ids(actor))).order_by(Swap.id.desc()),page,page_size)
    read_audit(db,actor,'swaps');return result

@router.get('/deposit-wallets')
def wallets(actor:Staff,db:DB):
    query=select(DepositWallet)
    if actor.role!='superworker':query=query.where(DepositWallet.office_id==actor.office_id) if actor.office_id else query.where(False)
    result={'items':[row_data(w) for w in db.scalars(query.order_by(DepositWallet.office_id,DepositWallet.currency,DepositWallet.network)).all()]}
    read_audit(db,actor,'wallets_deposit',{'office_id':actor.office_id if actor.role!='superworker' else None});return result

@router.get('/stake-plans')
def stake_plans(actor:Staff,db:DB):
    result={'items':[row_data(p) for p in db.scalars(select(StakePlan).order_by(StakePlan.id)).all()]}
    read_audit(db,actor,'stake_plans');return result

@router.get('/stake-positions')
def stake_positions(actor:Staff,db:DB,page:int=Query(1,ge=1),page_size:int=Query(20,ge=1,le=100)):
    result=paginated(db,select(StakePosition).where(StakePosition.user_id.in_(allowed_ids(actor))).order_by(StakePosition.id.desc()),page,page_size)
    read_audit(db,actor,'stake_positions');return result

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

@router.post('/tickets/{ticket_id}/messages',status_code=201)
def reply(ticket_id:int,body:MessageCreate,actor:Staff,db:DB):
    ticket=db.get(Ticket,ticket_id)
    if ticket is None:raise HTTPException(404,'Ticket not found')
    target_user(db,actor,ticket.user_id)
    message=TicketMessage(ticket_id=ticket.id,sender_id=actor.id,body=body.body)
    db.add(message);ticket.status='answered';db.flush()
    db.add(AuditLog(actor_id=actor.id,action='admin.ticket_reply',entity='ticket_messages',entity_id=message.id,after_json={'ticket_id':ticket.id}))
    db.commit();return row_data(message)

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
