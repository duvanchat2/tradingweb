"""Scoped, audit-backed admin actions with atomic balanced ledger effects."""
from datetime import datetime,timedelta,timezone
from decimal import Decimal
import hashlib,json
from fastapi import HTTPException
from fastapi.encoders import jsonable_encoder
from sqlalchemy import select,func,or_,text
from app.models.schema import User,Account,Transaction,PaymentRequest,KYCDocument,AuditLog,DepositWallet,Notification,Swap,StakePlan,StakePosition
from app.services.ledger import post_entry,LedgerError
from app.services.paper import locked_accounts,treasury_owner

def scope(actor):
    return [] if actor.role=='superworker' else [User.role=='client',User.office_id==actor.office_id]

def target_user(db,actor,identifier,lock=False):
    clause=User.id==int(identifier) if str(identifier).isdigit() else or_(User.email==str(identifier).lower(),User.referral_code==str(identifier))
    query=select(User).where(clause,*scope(actor))
    if lock:query=query.with_for_update().execution_options(populate_existing=True)
    user=db.scalar(query)
    if user is None:raise HTTPException(404,'User not found in your scope')
    return user

def row_data(row):
    fields=[c.name for c in row.__table__.columns if c.name not in ('password_hash','file_data','token_secret')]
    return jsonable_encoder({key:getattr(row,key) for key in fields},custom_encoder={Decimal:str})

def move(db,actor,user,currency,amount,incoming,kind,note,network=None,request_id=None,original_id=None,source_type='main'):
    owner=treasury_owner(db)
    accounts=locked_accounts(db,[(user.id,source_type,currency),(owner,'system',currency)])
    client,treasury=accounts[user.id,source_type,currency],accounts[owner,'system',currency]
    source,destination=(treasury,client) if incoming else (client,treasury)
    if amount:
        post_entry(db,debit_account_id=source.id,credit_account_id=destination.id,amount=amount,kind=kind,
                   actor_id=actor.id,note=note,request_id=request_id,original_transaction_id=original_id,network=network)
    return client

def review_payment(db,actor,body):
    # Lock user before payment/accounts, consistent with paper trading operations.
    original=db.get(PaymentRequest,body.request_id)
    if original is None:raise HTTPException(404,'Payment request not found')
    user=target_user(db,actor,original.user_id,True)
    payment=db.scalar(select(PaymentRequest).where(PaymentRequest.id==body.request_id).with_for_update().execution_options(populate_existing=True))
    before=row_data(payment)
    decision=body.decision
    withdrawal=payment.method=='simulated-withdrawal'
    if decision=='revert':
        if payment.status!='pending':payment.status='pending'
    elif payment.status!='pending':
        # A repeated closed decision returns its current state; changing it requires reopening.
        if payment.status!=decision:raise HTTPException(409,'Reopen a closed request before changing its review')
    else:
        amount=body.amount if body.amount is not None else payment.amount_requested
        resolution=payment.ledger_resolution
        if resolution!='unsettled':
            expected='rejected' if resolution in ('released','rejected') else 'approved'
            if decision!=expected:raise HTTPException(409,'Reopening preserves settlement; create a new request to change economic outcome')
            if decision=='approved' and body.amount is not None and amount!=payment.amount_approved:
                raise HTTPException(409,'A settled amount cannot be changed by reopening')
        elif decision=='approved':
            if withdrawal:
                if amount!=payment.amount_requested:raise HTTPException(422,'Withdrawal approval must match the requested amount')
                move(db,actor,user,payment.currency,amount,False,'withdrawal',body.staff_note,payment.network,payment.id,source_type='main')
                payment.ledger_resolution='paid'
            else:
                move(db,actor,user,payment.currency,amount,True,'deposit',body.staff_note,payment.network,payment.id)
                payment.ledger_resolution='credited'
            payment.amount_approved=amount
        elif decision=='rejected' and withdrawal:
            payment.ledger_resolution='rejected'
        payment.status=decision
    payment.staff_note=body.staff_note
    payment.reviewer_id=actor.id;payment.reviewed_at=datetime.now(timezone.utc)
    db.flush()
    return payment,before

def review_swap(db,actor,body):
    original=db.get(Swap,body.swap_id)
    if original is None:raise HTTPException(404,'Swap request not found')
    user=target_user(db,actor,original.user_id,True)
    swap=db.scalar(select(Swap).where(Swap.id==body.swap_id).with_for_update().execution_options(populate_existing=True))
    before=row_data(swap)
    if swap.status!='pending':
        if swap.status!=body.decision:raise HTTPException(409,'Swap request is already closed')
        return swap,before
    if body.decision=='approved':
        owner=treasury_owner(db)
        accounts=locked_accounts(db,[(user.id,'main',swap.from_currency),(user.id,'main',swap.to_currency),(owner,'system',swap.from_currency),(owner,'system',swap.to_currency)])
        source=accounts[user.id,'main',swap.from_currency]
        if source.balance<swap.from_amount:raise HTTPException(409,'Client balance is no longer sufficient')
        note=f'Approved paper swap {swap.id}: {body.staff_note}'.strip()
        post_entry(db,debit_account_id=source.id,credit_account_id=accounts[owner,'system',swap.from_currency].id,amount=swap.from_amount-swap.fee,kind='swap_out',actor_id=actor.id,note=note)
        if swap.fee:
            post_entry(db,debit_account_id=source.id,credit_account_id=accounts[owner,'system',swap.from_currency].id,amount=swap.fee,kind='fee',actor_id=actor.id,note=note)
        post_entry(db,debit_account_id=accounts[owner,'system',swap.to_currency].id,credit_account_id=accounts[user.id,'main',swap.to_currency].id,amount=swap.to_amount,kind='swap_in',actor_id=actor.id,note=note)
    swap.status=body.decision;swap.staff_note=body.staff_note;swap.reviewer_id=actor.id;swap.reviewed_at=datetime.now(timezone.utc)
    db.flush();return swap,before

def review_stake(db,actor,body):
    original=db.get(StakePosition,body.position_id)
    if original is None:raise HTTPException(404,'CDT request not found')
    user=target_user(db,actor,original.user_id,True)
    position=db.scalar(select(StakePosition).where(StakePosition.id==body.position_id).with_for_update().execution_options(populate_existing=True))
    before=row_data(position)
    target_status='active' if body.decision=='approved' else 'rejected'
    if position.status!='pending':
        if position.status!=target_status:raise HTTPException(409,'CDT request is already closed')
        return position,before
    plan=db.get(StakePlan,position.plan_id)
    if plan is None:raise HTTPException(409,'CDT plan no longer exists')
    if body.decision=='approved':
        accounts=locked_accounts(db,[(user.id,'main',plan.currency),(user.id,'staking',plan.currency)])
        source=accounts[user.id,'main',plan.currency]
        if source.balance<position.amount:raise HTTPException(409,'Client balance is no longer sufficient')
        post_entry(db,debit_account_id=source.id,credit_account_id=accounts[user.id,'staking',plan.currency].id,amount=position.amount,kind='stake_lock',actor_id=actor.id,note=f'Approved paper CDT {position.id}: {body.staff_note}'.strip())
        position.opened_at=datetime.now(timezone.utc);position.closes_at=position.opened_at+timedelta(days=plan.term_days)
    position.status=target_status;position.staff_note=body.staff_note;position.reviewer_id=actor.id;position.reviewed_at=datetime.now(timezone.utc)
    db.flush();return position,before

def apply(db,actor,body):
    if body.action=='payment_review':return review_payment(db,actor,body)
    if body.action=='swap_review':return review_swap(db,actor,body)
    if body.action=='stake_review':return review_stake(db,actor,body)
    if body.action=='kyc_document':
        user=target_user(db,actor,body.user_id,True)
        doc=db.scalar(select(KYCDocument).where(KYCDocument.id==body.document_id,KYCDocument.user_id==user.id).with_for_update())
        if doc is None:raise HTTPException(404,'Document not found')
        before={**row_data(doc),'user_kyc_status':user.kyc_status}
        doc.status=body.decision;doc.review_note=body.review_note;doc.reviewer_id=actor.id;doc.reviewed_at=datetime.now(timezone.utc)
        db.flush()
        docs=db.scalars(select(KYCDocument).where(KYCDocument.user_id==user.id)).all()
        required={'id_front','id_back','proof_address','selfie'}
        by_type={d.doc_type:d.status for d in docs}
        user.kyc_status='rejected' if any(status=='rejected' for status in by_type.values()) else ('verified' if all(by_type.get(kind)=='approved' for kind in required) else 'pending')
        db.flush();return doc,before
    if body.action=='credit':
        user=target_user(db,actor,body.user,True)
        account=move(db,actor,user,body.currency,body.amount,body.operation=='credit',body.operation,body.note,body.network)
        before=row_data(account)
        before['balance']=str(account.balance-body.amount if body.operation=='credit' else account.balance+body.amount)
        return account,before
    if body.action=='credit_correct':
        original=db.get(Transaction,body.transaction_id)
        if original is None:raise HTTPException(404,'Transaction not found')
        account=db.get(Account,original.account_id)
        user=target_user(db,actor,account.user_id,True)
        if account.type!='main':raise HTTPException(422,'Only main-account movements can be corrected')
        # Lock original as a correction coordination point; never mutate it.
        db.scalar(select(Transaction).where(Transaction.id==original.id).with_for_update())
        prior=db.scalar(select(func.coalesce(func.sum(Transaction.amount),0)).where(Transaction.original_transaction_id==original.id,Transaction.account_id==account.id))
        desired=body.amount if original.amount>0 else -body.amount
        delta=desired-original.amount-prior
        if delta:
            move(db,actor,user,account.currency,abs(delta),delta>0,'correction',body.note,original.network,original_id=original.id)
        return original,row_data(original)
    if body.action in ('deposit_wallet_save','deposit_wallet_delete'):
        wallet=db.scalar(select(DepositWallet).where(DepositWallet.id==body.wallet_id).with_for_update()) if body.wallet_id else None
        if body.wallet_id and wallet is None:raise HTTPException(404,'Deposit wallet not found')
        before=row_data(wallet) if wallet else None
        if body.action=='deposit_wallet_delete':wallet.is_active=False
        else:
            if wallet is None:wallet=DepositWallet();db.add(wallet)
            for field in ('label','currency','network','address','is_active'):setattr(wallet,field,getattr(body,field))
        db.flush();return wallet,before
    if body.action=='send_notification':
        query=select(User).where(User.is_active.is_(True),User.role=='client',*scope(actor))
        if body.scope=='one':
            if body.user_id is None:raise HTTPException(422,'user_id is required for scope one')
            target_user(db,actor,body.user_id)
            query=query.where(User.id==body.user_id)
        elif body.scope=='office':query=query.where(User.office_id==actor.office_id)
        if body.kyc_filter:query=query.where(User.kyc_status==body.kyc_filter)
        recipients=db.scalars(query.order_by(User.id)).all()
        ids=[]
        for user in recipients:
            notification=Notification(user_id=user.id,scope=body.scope,kyc_filter=body.kyc_filter,title=body.title,type=body.type,body=body.body)
            db.add(notification);db.flush();ids.append(notification.id)
        return {'recipient_count':len(ids),'notification_ids':ids},None
    raise HTTPException(422,'Unknown action')

MODELS={'payment_requests':PaymentRequest,'kyc_documents':KYCDocument,'accounts':Account,'transactions':Transaction,'wallets_deposit':DepositWallet,'swaps':Swap,'stake_positions':StakePosition}

def current_result(db,actor,result):
    if result['entity'] in MODELS:
        row=db.get(MODELS[result['entity']],result['entity_id'])
        if row is not None:
            if hasattr(row,'user_id'):target_user(db,actor,row.user_id)
            if isinstance(row,Transaction):target_user(db,actor,db.get(Account,row.account_id).user_id)
            state=row_data(row)
            if isinstance(row,KYCDocument):state['user_kyc_status']=db.get(User,row.user_id).kyc_status
            result={**result,'state':state}
    elif result['entity']=='notifications':
        ids=result['state']['notification_ids']
        visible=db.scalars(select(Notification.id).where(Notification.id.in_(ids),Notification.user_id.in_(select(User.id).where(*scope(actor))))).all()
        result={**result,'state':{'recipient_count':len(visible),'notification_ids':visible}}
    return result

def execute(db,actor,body,key=None,ip=None):
    data=body.model_dump(mode='json')
    digest=hashlib.sha256(json.dumps(data,sort_keys=True,separators=(',',':')).encode()).hexdigest()
    key=key or 'payload:'+digest
    # An actor-scoped advisory lock + unique constraint serialize concurrent retries.
    lock_id=int.from_bytes(hashlib.sha256(f'{actor.id}:{key}'.encode()).digest()[:8],'big',signed=True)
    db.execute(text('SELECT pg_advisory_xact_lock(:key)'),{'key':lock_id})
    previous=db.scalar(select(AuditLog).where(AuditLog.actor_id==actor.id,AuditLog.idempotency_key==key))
    if previous:
        if previous.request_hash!=digest:raise HTTPException(409,'Idempotency key reused with a different payload')
        result=current_result(db,actor,previous.after_json)
        db.commit()
        return {**result,'replayed':True}
    with db.begin_nested():
        row,before=apply(db,actor,body)
        if isinstance(row,dict):entity,entity_id,state='notifications',None,row
        else:entity,entity_id,state=row.__tablename__,row.id,row_data(row)
        if body.action=='kyc_document':state['user_kyc_status']=db.get(User,row.user_id).kyc_status
        result={'action':body.action,'entity':entity,'entity_id':entity_id,'state':state}
        db.add(AuditLog(actor_id=actor.id,action='admin.'+body.action,entity=entity,entity_id=entity_id,
                        before_json=before,after_json=result,ip=ip,idempotency_key=key,request_hash=digest))
        db.flush()
    db.commit()
    return {**result,'replayed':False}
