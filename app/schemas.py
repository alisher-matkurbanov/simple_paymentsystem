import datetime
import decimal
import enum
import uuid

from pydantic import BaseModel, Field, validator


class TransactionType(enum.Enum):
    replenish = "REPLENISH"
    transfer = "TRANSFER"


class Currency(enum.Enum):
    USD = "USD"


class AccountCreateIn(BaseModel):
    name: str = Field(..., title="Name of the account", max_length=32)
    
    def __str__(self):
        return self.name


class AccountCreateOut(BaseModel):
    account_id: str
    wallet_id: str


class ExtendedAccountOut(BaseModel):
    account_id: uuid.UUID
    name: str = Field(..., max_length=32)
    wallet_id: uuid.UUID
    currency: Currency
    amount: decimal.Decimal
    created_at: datetime.datetime


class TransferMoneyIn(BaseModel):
    from_wallet_id: uuid.UUID
    from_currency: Currency
    to_wallet_id: uuid.UUID
    to_currency: Currency
    amount: decimal.Decimal

    def is_currencies_match(self):
        return self.to_currency == self.from_currency == Currency.USD


class TransferMoneyOut(BaseModel):
    from_wallet_id: uuid.UUID
    from_currency: Currency
    from_amount: decimal.Decimal
    to_wallet_id: uuid.UUID
    to_currency: Currency
    to_amount: decimal.Decimal


class ReplenishWalletInfo(BaseModel):
    wallet_id: uuid.UUID
    currency: Currency
    amount: decimal.Decimal  # todo add validator


class ReplenishTransaction(BaseModel):
    wallet_id: uuid.UUID
    currency: Currency
    amount: decimal.Decimal  # todo add validator
