from decimal import Decimal
from typing import Annotated, Literal
from datetime import datetime
from pydantic import AfterValidator, BaseModel, ConfigDict, Field, model_validator
from app.routers.auth import CURRENCIES

Amount = Annotated[Decimal, Field(gt=0, lt=Decimal('1e20'), max_digits=28, decimal_places=8, allow_inf_nan=False)]
def currency(value: str) -> str:
    value = value.upper()
    if value not in CURRENCIES: raise ValueError('Unsupported currency')
    return value
Currency = Annotated[str, AfterValidator(currency)]

class OrderBody(BaseModel):
    pair: str = Field(min_length=6, max_length=16)
    side: Literal['buy','sell']
    qty: Amount
    type: Literal['market','limit'] = 'market'
    price: Amount | None = None
    @model_validator(mode='after')
    def validate_price(self):
        if (self.type == 'limit') != (self.price is not None):
            raise ValueError('Price is required only for limit orders')
        return self
class SwapBody(BaseModel):
    from_currency: Currency
    to_currency: Currency
    amount: Amount
    @model_validator(mode='after')
    def distinct(self):
        if self.from_currency == self.to_currency: raise ValueError('Currencies must differ')
        return self
class StakeBody(BaseModel):
    plan_id: int = Field(gt=0)
    amount: Amount
class WithdrawalBody(BaseModel):
    currency: Currency
    amount: Amount
    payment_method_id: int = Field(gt=0)

class ORMOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
class OrderOut(ORMOut):
    id: int
    pair: str
    side: str
    type: str
    qty: Decimal
    price: Decimal | None
    status: str
    filled_price: Decimal | None
    fee_amount: Decimal | None
    fee_currency: str | None
    created_at: datetime
class SwapOut(ORMOut):
    id: int
    from_currency: str
    to_currency: str
    from_amount: Decimal
    to_amount: Decimal
    rate: Decimal
    fee: Decimal
    status: str
    created_at: datetime
class PlanOut(ORMOut):
    id: int
    currency: str
    apy: Decimal
    min_amount: Decimal
    term_days: int
    is_active: bool
class PositionOut(ORMOut):
    id: int
    plan_id: int
    amount: Decimal
    yield_accrued: Decimal
    status: str
    opened_at: datetime
    closes_at: datetime
class WithdrawalOut(ORMOut):
    id: int
    currency: str
    network: str | None
    amount_requested: Decimal
    status: str
    execution_status: Literal['simulated']
    method: str
    destination_address: str | None
    payment_method_id: int | None
class WalletOut(ORMOut):
    id: int
    label: str
    currency: str
    network: str
    address: str
