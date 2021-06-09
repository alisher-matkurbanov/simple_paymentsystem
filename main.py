import enum
import logging
import uuid
from typing import Union

import asyncpg
import databases
import sqlalchemy
from fastapi import FastAPI, Response, status
from pydantic import BaseModel
from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Enum,
    ForeignKey,
    Integer,
    String,
    Table,
    func,
)
from sqlalchemy.dialects.postgresql import NUMERIC, UUID

logger = logging.getLogger(__name__)

app = FastAPI()

DATABASE_URL = "postgresql://paymentsystem:paymentsystem@localhost:5432/paymentsystem"

database = databases.Database(DATABASE_URL)
metadata = sqlalchemy.MetaData()


class TransactionType(enum.Enum):
    replenish = "REPLENISH"
    transfer = "TRANSFER"


accounts = Table(
    "account",
    metadata,
    Column("id", UUID(as_uuid=True), primary_key=True),
    Column("name", String(32)),
    Column("is_active", Boolean, default=True, nullable=False),
    Column("created_at", DateTime(timezone=True), server_default=func.now()),
    Column("updated_at", DateTime(timezone=True), onupdate=func.now()),
)

wallets = Table(
    "wallet",
    metadata,
    Column("id", UUID(as_uuid=True), primary_key=True),
    Column("account_id", ForeignKey("account.id"), nullable=False),
    Column("currency", ForeignKey("currency.code"), nullable=False),
    Column("amount", NUMERIC(precision=2), nullable=False),
    Column("is_active", Boolean, default=True, nullable=False),
    Column(
        "created_at", DateTime(timezone=True), server_default=func.now(), nullable=False
    ),
    Column("updated_at", DateTime(timezone=True), onupdate=func.now()),
)

currencies = Table("currency", metadata, Column("code", String(3), primary_key=True))

transactions = Table(
    "transaction",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("type", Enum(TransactionType), nullable=False),
    Column(
        "created_at", DateTime(timezone=True), server_default=func.now(), nullable=False
    ),
)

posting = Table(
    "posting",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("transaction_id", ForeignKey("transaction.id"), nullable=False),
    Column("wallet_id", ForeignKey("wallet.id"), nullable=False),
    Column("amount", NUMERIC(precision=2), nullable=False),
    Column("currency", ForeignKey("currency.code"), nullable=False),
)


class CreateAccountRequest(BaseModel):
    name: str


class CreateAccountResponse(BaseModel):
    account_id: str
    name: str


class APIError(BaseModel):
    error: str = "Internal Error"


@app.on_event("startup")
async def startup():
    await database.connect()


@app.on_event("shutdown")
async def shutdown():
    await database.disconnect()


async def _create_account(account):
    account_id = uuid.uuid4()
    with database.transaction():
        insert_account = accounts.insert().values(
            id=account_id, name=account.name, is_active=True
        )
        await database.execute(insert_account)

    return account_id


# TODO Добавить идемпотентность
@app.post(
    "/accounts",
    status_code=status.HTTP_201_CREATED,
    response_model=Union[CreateAccountResponse, APIError],
)
async def create_account(account: CreateAccountRequest, response: Response):
    attempts = 5
    while attempts != 0:
        try:
            account_id = await _create_account(account)
            return CreateAccountResponse(account_id=str(account_id), name=account.name)
        except asyncpg.exceptions.UniqueViolationError as e:
            attempts -= 1
            if attempts != 0:
                continue
            logger.exception(e)
            response.status_code = status.HTTP_400_BAD_REQUEST
            return APIError(
                error=f"can't create account '{account.name}'; try again later"
            )


@app.get("/accounts/{account_id}")
async def get_account(account_id):
    raise NotImplemented


@app.post("/replenish")
async def replenish_wallet():
    raise NotImplemented


@app.post("/transfer")
async def transfer_money():
    raise NotImplemented


# accounts
# - account_id: UUID
# - name: String
# - active: Bool
# - created_at
# - updated_at

# wallet 1 - 1 to accounts
# - account_id: UUID
# - wallet_id: UUID
# - currency_id: int
# - amount: Decimal
# - active: Bool
# - created_at
# - updated_at

# currency
# - code

# journal
# - journal_id
# - transaction_type
# - created_at

# posting
# - posting_id
# - journal_id
# - wallet_id
# - amount
# - currency_id
