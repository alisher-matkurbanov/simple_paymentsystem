import logging
from typing import Union

import asyncpg
from fastapi import FastAPI, Response, status

from database import db
from schemas import AccountCreateRequest, AccountCreateResponse, APIError
import crud

logger = logging.getLogger(__name__)

app = FastAPI()


@app.on_event("startup")
async def startup():
    await db.connect()


@app.on_event("shutdown")
async def shutdown():
    await db.disconnect()


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
            account_id, wallet_id = await crud.create_account_with_wallet(account)
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
