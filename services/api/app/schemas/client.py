from decimal import Decimal
from typing import Annotated

from pydantic import BaseModel, Field

from app.schemas.trading import Currency


Amount = Annotated[
    Decimal,
    Field(gt=0, lt=Decimal('1e20'), max_digits=28, decimal_places=8, allow_inf_nan=False),
]


class DepositRequestBody(BaseModel):
    currency: Currency
    amount: Amount
    network: str = Field(min_length=1, max_length=64)
    method: str = Field(default='simulated-transfer', min_length=1, max_length=64)


class TicketBody(BaseModel):
    subject: str = Field(min_length=3, max_length=200)
    body: str = Field(min_length=1, max_length=5000)
