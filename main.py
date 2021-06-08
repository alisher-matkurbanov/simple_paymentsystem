import logging
import uuid
from typing import Union

import asyncpg
import databases
import sqlalchemy
from fastapi import FastAPI, Response, status
from pydantic import BaseModel
from sqlalchemy import func
from sqlalchemy.dialects.postgresql import UUID

logger = logging.getLogger(__name__)

app = FastAPI()

DATABASE_URL = "postgresql://paymentsystem:paymentsystem@localhost:5432/paymentsystem"

database = databases.Database(DATABASE_URL)
metadata = sqlalchemy.MetaData()

accounts = sqlalchemy.Table(
    "account",
    metadata,
    sqlalchemy.Column("id", UUID(as_uuid=True), primary_key=True),
    sqlalchemy.Column("name", sqlalchemy.String(32)),
    sqlalchemy.Column("is_active", sqlalchemy.Boolean, default=True),
    # https://stackoverflow.com/questions/13370317/sqlalchemy-default-datetime
    sqlalchemy.Column(
        "created_at", sqlalchemy.DateTime(timezone=True), server_default=func.now()
    ),
    sqlalchemy.Column(
        "updated_at", sqlalchemy.DateTime(timezone=True), onupdate=func.now()
    ),
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
    # todo create wallet in transaction
    account_id = uuid.uuid4()
    query = accounts.insert().values(id=account_id, name=account.name, is_active=True)
    await database.execute(query)
    return account_id


# TODO Добавить идемпотентность
@app.post(
    "/accounts",
    status_code=Union[status.HTTP_201_CREATED, status.HTTP_400_BAD_REQUEST],
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
# - name: String for Firdavs
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
# - currency_id
# - title

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

# https://habr.com/ru/post/480394/

# https://www.encode.io/databases/database_queries/
# https://fastapi.tiangolo.com/advanced/async-sql-databases/
# https://fastapi.tiangolo.com/tutorial/sql-databases/


# todo добавить репозиторий
# todo параметризовать алембик в докере
# todo приделать идемпотентность
# todo разбить на файлы
# todo обновить pip3 freeze > requirements.txt