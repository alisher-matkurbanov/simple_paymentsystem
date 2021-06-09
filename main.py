import logging
import uuid
from typing import Union, Tuple

import asyncpg
import databases
from fastapi import FastAPI, Response, status
from pydantic import BaseModel, Field

from database import DATABASE_URL
from dbmodels import Currency, accounts, wallets

logger = logging.getLogger(__name__)

app = FastAPI()
db = databases.Database(DATABASE_URL)


class AccountCreateRequest(BaseModel):
    name: str = Field(..., title="Name of the account", max_length=32)


class AccountCreateResponse(BaseModel):
    account_id: str
    wallet_id: str


class APIError(BaseModel):
    error: str = "Internal Error"


@app.on_event("startup")
async def startup():
    await db.connect()


@app.on_event("shutdown")
async def shutdown():
    await db.disconnect()


async def _create_account_with_wallet(account: AccountCreateRequest):
    wallet_id = uuid.uuid4()
    account_id = uuid.uuid4()
    async with db.transaction():
        insert_account = accounts.insert().values(
            id=account_id,
            name=account.name,
            is_active=True,
        )
        insert_wallet = wallets.insert().values(
            id=wallet_id,
            account_id=account_id,
            currency=Currency.USD,
            amount=0,
            is_active=True,
        )
        await db.execute(insert_account)
        await db.execute(insert_wallet)
    
    return account_id, wallet_id


# TODO Добавить идемпотентность
@app.post(
    "/accounts",
    status_code=status.HTTP_201_CREATED,
    response_model=Union[AccountCreateResponse, APIError],
)
async def create_account(account: AccountCreateRequest, response: Response):
    # we try to create account with wallet 5 times,
    # then report that we can't create account.
    # creation may fails if generated uuid already presented in database.
    attempts = 5
    while attempts != 0:
        try:
            account_id, wallet_id = await _create_account_with_wallet(account)
            return AccountCreateResponse(
                account_id=str(account_id),
                wallet_id=str(wallet_id),
            )
        except asyncpg.exceptions.UniqueViolationError as e:
            attempts -= 1
            if attempts != 0:
                continue
            logger.exception(e)
            response.status_code = status.HTTP_400_BAD_REQUEST
            return APIError(
                error=f"can't create account '{account.name}'; try again later"
            )
        except Exception as e:
            logger.exception(e)
            return APIError()


@app.get("/accounts/{account_id}")
async def get_account(account_id):
    raise NotImplemented


@app.post("/replenish")
async def replenish_wallet():
    raise NotImplemented


@app.post("/transfer")
async def transfer_money():
    raise NotImplemented
