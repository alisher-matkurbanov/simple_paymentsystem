import datetime
import decimal
import uuid

from pydantic import BaseModel, Field

from dbmodels import Currency


class AccountCreateRequest(BaseModel):
    name: str = Field(..., title="Name of the account", max_length=32)
    
    def __str__(self):
        return self.name


class AccountCreateResponse(BaseModel):
    account_id: str
    wallet_id: str


class APIError(BaseModel):
    error: str = "Internal Error"


class ExtendedAccountResponse(BaseModel):
    account_id: uuid.UUID
    name: str = Field(..., max_length=32)
    wallet_id: uuid.UUID
    currency: Currency
    amount: decimal.Decimal
    created_at: datetime.datetime
