from decimal import Decimal
from typing import Annotated

from typing import Literal
from pydantic import BaseModel, ConfigDict, Field, model_validator

from app.schemas.trading import Currency


Amount = Annotated[
    Decimal,
    Field(gt=0, lt=Decimal('1e20'), max_digits=28, decimal_places=8, allow_inf_nan=False),
]


class DepositRequestBody(BaseModel):
    currency: Currency
    amount: Amount
    network: str | None = Field(default=None, min_length=1, max_length=64)
    method: str = Field(default='simulated-transfer', min_length=1, max_length=64)
    payment_method_id: int | None = Field(default=None, gt=0)


class PaymentMethodBody(BaseModel):
    model_config = ConfigDict(extra='forbid')
    type: Literal['bank', 'card', 'crypto']
    label: str = Field(min_length=2, max_length=80)
    holder_name: str = Field(min_length=2, max_length=160)
    bank_name: str | None = Field(default=None, max_length=120)
    account_type: str | None = Field(default=None, max_length=40)
    account_last4: str | None = Field(default=None, pattern=r'^\d{4}$')
    card_brand: str | None = Field(default=None, max_length=40)
    card_last4: str | None = Field(default=None, pattern=r'^\d{4}$')
    network: str | None = Field(default=None, max_length=64)
    wallet_address: str | None = Field(default=None, max_length=256)

    @model_validator(mode='after')
    def validate_type_fields(self):
        required = {
            'bank': (self.bank_name, self.account_type, self.account_last4),
            'card': (self.card_brand, self.card_last4),
            'crypto': (self.network, self.wallet_address),
        }[self.type]
        if not all(required):
            raise ValueError(f'Missing required {self.type} payment method fields')
        return self


class TicketBody(BaseModel):
    subject: str = Field(min_length=3, max_length=200)
    body: str = Field(min_length=1, max_length=5000)
