import datetime
import decimal
import enum
import uuid

from pydantic import BaseModel, Field, validator

from app.config import settings


class TransactionType(enum.Enum):
    replenish = "REPLENISH"
    transfer = "TRANSFER"


class Currency(enum.Enum):
    USD = "USD"


def decimal_validator(dec):
    if not (0 <= dec <= settings.max_amount):
        raise ValueError(f"amount in range [{0}, {settings.max_amount}] allowed")
    if dec != round(dec, settings.decimal_scale):
        raise ValueError(f"only {settings.decimal_scale} decimals allowed for amount")
    return dec


def currency_validator(cur):
    if cur != Currency.USD:
        raise ValueError(f"only {Currency.USD} allowed")
    return cur


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

    @validator("amount")
    def amount_validator(cls, v):
        return decimal_validator(v)

    @validator("currency")
    def currency_validator(cls, v):
        return currency_validator(v)


class TransferMoneyIn(BaseModel):
    from_wallet_id: uuid.UUID
    from_currency: Currency
    to_wallet_id: uuid.UUID
    to_currency: Currency
    amount: decimal.Decimal

    def is_currencies_match(self):
        return self.to_currency == self.from_currency

    @validator("amount")
    def amount_validator(cls, v):
        return decimal_validator(v)

    @validator("from_currency", "to_currency")
    def currency_validator(cls, v):
        return currency_validator(v)


class TransferMoneyOut(BaseModel):
    from_wallet_id: uuid.UUID
    from_currency: Currency
    from_amount: decimal.Decimal
    to_wallet_id: uuid.UUID
    to_currency: Currency
    to_amount: decimal.Decimal

    @validator("to_amount", "from_amount")
    def amount_validator(cls, v):
        return decimal_validator(v)


class ReplenishWalletInfo(BaseModel):
    wallet_id: uuid.UUID
    currency: Currency
    amount: decimal.Decimal

    @validator("amount")
    def amount_validator(cls, v):
        return decimal_validator(v)

    @validator("currency")
    def currency_validator(cls, v):
        return currency_validator(v)


class ReplenishTransaction(BaseModel):
    wallet_id: uuid.UUID
    currency: Currency
    amount: decimal.Decimal

    @validator("amount")
    def amount_validator(cls, v):
        return decimal_validator(v)

    @validator("currency")
    def currency_validator(cls, v):
        return currency_validator(v)
