import logging
import uuid
from typing import Union

import asyncpg
from fastapi import FastAPI, Response, status

import crud
from database import db
from schemas import AccountCreateRequest, AccountCreateResponse, APIError, ExtendedAccountResponse

logger = logging.getLogger(__name__)

application = FastAPI()


@application.on_event("startup")
async def startup():
    if not db.is_connected:
        await db.connect()


@application.on_event("shutdown")
async def shutdown():
    if db.is_connected:
        await db.disconnect()


# TODO Добавить идемпотентность
@application.post(
    "/accounts",
    status_code=status.HTTP_201_CREATED,
    response_model=Union[AccountCreateResponse, APIError],
)
async def create_account(account: AccountCreateRequest, response: Response):
    # we try to create account with wallet 5 times,
    # then report that we can't create account.
    # creation may fails if generated uuid already presented in database,
    # however it is almost impossible
    attempts = 5
    while attempts != 0:
        try:
            return await crud.create_account_with_wallet(account)
        
        except asyncpg.exceptions.UniqueViolationError as e:
            attempts -= 1
            if attempts != 0:
                continue
            logger.exception(e)
            response.status_code = status.HTTP_400_BAD_REQUEST
            return APIError(
                error=f"can't create account '{account}'; try again later"
            )
        
        except Exception as e:
            logger.exception(e)
            return APIError()


@application.get(
    "/accounts/{account_id}",
    status_code=status.HTTP_200_OK,
    response_model=Union[ExtendedAccountResponse, APIError],
    include_in_schema=False,
)
async def get_account(account_id: uuid.UUID, response: Response):
    try:
        account_response = await crud.get_account_with_wallet(account_id)
        if account_response is None:
            response.status_code = status.HTTP_400_BAD_REQUEST
            return APIError(error=f"can't find account with account_id={account_id}")
        return account_response
    except Exception as e:
        logger.exception(e)
        response.status_code = status.HTTP_400_BAD_REQUEST
        return APIError()


@application.post("/replenish")
async def replenish_wallet():
    raise NotImplemented


@application.post("/transfer")
async def transfer_money():
    raise NotImplemented
