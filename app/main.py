import logging
import uuid

import asyncpg
from fastapi import FastAPI, status, HTTPException

import crud
from database import db
from schemas import AccountCreateIn, AccountCreateOut, ExtendedAccountOut, ReplenishWallet

logger = logging.getLogger(__name__)

app = FastAPI()


@app.on_event("startup")
async def startup():
    if not db.is_connected:
        await db.connect()


@app.on_event("shutdown")
async def shutdown():
    if db.is_connected:
        await db.disconnect()


# TODO Добавить идемпотентность
@app.post(
    "/accounts",
    status_code=status.HTTP_201_CREATED,
    response_model=AccountCreateOut,
)
async def create_account(account: AccountCreateIn):
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
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"can't create account '{account}'; try again later"
            )
        except Exception as e:
            logger.exception(e)
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)


@app.get(
    "/accounts/{account_id}",
    status_code=status.HTTP_200_OK,
    response_model=ExtendedAccountOut,
)
async def get_account(account_id: uuid.UUID):
    try:
        return await crud.get_account_with_wallet(account_id)
    except crud.NotFound as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=e.message)
    except Exception as e:
        logger.exception(e)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)


@app.post(
    "/replenish",
    status_code=status.HTTP_200_OK,
    response_model=ReplenishWallet,
)
async def replenish_wallet(data: ReplenishWallet):
    try:
        return await crud.replenish(data)
    except crud.LimitOverflow as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=e.message)
    except crud.NotFound as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=e.message)
    except Exception as e:
        logger.exception(e)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)


@app.post("/transfer")
async def transfer_money():
    raise NotImplemented
