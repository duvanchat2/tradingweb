from decimal import Decimal
from typing import Annotated,Literal,Union
from pydantic import BaseModel,ConfigDict,Field,StringConstraints,TypeAdapter
from app.schemas.trading import Amount,Currency

Note=Annotated[str,StringConstraints(strip_whitespace=True,min_length=1,max_length=2000)]
class Action(BaseModel):
    model_config=ConfigDict(extra='forbid')
class KYCAction(Action):
    action:Literal['kyc_document']
    user_id:int=Field(gt=0)
    document_id:int=Field(gt=0)
    review_note:str=Field(default='',max_length=2000)
    decision:Literal['rejected','pending']
class PaymentAction(Action):
    action:Literal['payment_review']
    request_id:int=Field(gt=0)
    amount:Amount|None=None
    staff_note:str=Field(default='',max_length=2000)
    decision:Literal['approved','rejected','revert']
class CreditAction(Action):
    action:Literal['credit']
    user:str|int
    currency:Currency
    network:str=Field(min_length=1,max_length=64)
    amount:Amount
    operation:Literal['credit','debit']
    note:Note
class CorrectionAction(Action):
    action:Literal['credit_correct']
    transaction_id:int=Field(gt=0)
    amount:Annotated[Decimal,Field(ge=0,lt=Decimal('1e20'),max_digits=28,decimal_places=8,allow_inf_nan=False)]
    note:Note
class WalletAction(Action):
    action:Literal['deposit_wallet_save']
    wallet_id:int=Field(default=0,ge=0)
    label:Annotated[str,StringConstraints(strip_whitespace=True,min_length=1,max_length=150)]
    currency:Currency
    network:str=Field(min_length=1,max_length=64)
    address:str=Field(min_length=1,max_length=256)
    is_active:bool=True
class WalletDeleteAction(Action):
    action:Literal['deposit_wallet_delete']
    wallet_id:int=Field(gt=0)
class NotificationAction(Action):
    action:Literal['send_notification']
    scope:Literal['one','office','all']
    kyc_filter:Literal['none','pending','verified','rejected']|None=None
    user_id:int|None=Field(default=None,gt=0)
    title:Annotated[str,StringConstraints(strip_whitespace=True,min_length=1,max_length=200)]
    type:Literal['info','success','warning']
    body:Annotated[str,StringConstraints(strip_whitespace=True,min_length=1,max_length=5000)]

Actions=Annotated[Union[KYCAction,PaymentAction,CreditAction,CorrectionAction,WalletAction,WalletDeleteAction,NotificationAction],Field(discriminator='action')]
adapter=TypeAdapter(Actions)

def parse_action(raw):
    data=dict(raw)
    if 'payload' in data:
        payload=data.pop('payload')
        if not isinstance(payload,dict):raise ValueError('payload must be an object')
        if 'action' in payload:
            if data.get('action')!='payment_review':raise ValueError('Nested action is only a payment decision')
            payload={**payload,'decision':payload['action']};payload.pop('action')
        if set(data).intersection(payload):raise ValueError('Duplicate envelope/payload fields')
        data.update(payload)
    return adapter.validate_python(data)
