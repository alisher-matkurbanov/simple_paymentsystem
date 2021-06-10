import uuid

from .database import db
from .dbmodels import Currency, accounts, wallets
from .schemas import AccountCreateRequest


async def create_account_with_wallet(account: AccountCreateRequest):
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
