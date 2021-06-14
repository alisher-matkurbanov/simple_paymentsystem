import logging
import uuid

import asyncpg
from fastapi import APIRouter, HTTPException
from starlette import status

from app import crud
from app.schemas import (AccountCreateIn, AccountCreateOut, Currency,
                         ExtendedAccountOut, ReplenishWalletInfo,
                         TransferMoneyIn, TransferMoneyOut)

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post(
    "/accounts",
    status_code=status.HTTP_201_CREATED,
    response_model=AccountCreateOut,
)
async def create_account(account: AccountCreateIn):
    """Create account with wallet and return account_id and wallet_id """
    try:
        return await crud.create_account_with_wallet(account)
    except asyncpg.exceptions.UniqueViolationError as e:
        logger.exception(e)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"can't create account '{account}'; try again later",
        )
    except Exception as e:
        logger.exception(e)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)


@router.get(
    "/accounts/{account_id}",
    status_code=status.HTTP_200_OK,
    response_model=ExtendedAccountOut,
)
async def get_account(account_id: uuid.UUID):
    """Get account with wallet information by account_id"""
    try:
        return await crud.get_account_with_wallet(account_id)
    except crud.NotFound as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=e.message)
    except Exception as e:
        logger.exception(e)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)


@router.post(
    "/replenish",
    status_code=status.HTTP_200_OK,
    response_model=ReplenishWalletInfo,
)
async def replenish_wallet(data: ReplenishWalletInfo):
    """Replenish wallet with by wallet_id"""
    try:
        return await crud.replenish(data)
    except crud.NotFound as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=e.message)
    except crud.CRUDException as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=e.message)
    except Exception as e:
        logger.exception(e)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)


@router.post(
    "/transfer",
    status_code=status.HTTP_200_OK,
    response_model=TransferMoneyOut,
)
async def transfer_money(data: TransferMoneyIn):
    """Transfers money from one wallet to another"""
    if not data.is_currencies_match():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"only {Currency.USD.value} currency is supported",
        )
    try:
        return await crud.transfer(data)
    except crud.NotFound as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=e.message)
    except crud.CRUDException as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=e.message)
    except Exception as e:
        logger.exception(e)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
