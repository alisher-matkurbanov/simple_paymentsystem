import uuid

from database import db
from dbmodels import Currency, accounts, wallets
from schemas import AccountCreateRequest, AccountCreateResponse, ExtendedAccountResponse


class AccountWithEmailExists(Exception):
    def __init__(self, email: str):
        message = f"account with email {email} exists"
        super().__init__(message)


async def create_account_with_wallet(account: AccountCreateRequest) -> AccountCreateResponse:
    wallet_id = uuid.uuid4()
    account_id = uuid.uuid4()
    async with db.transaction():
        insert_account = accounts.insert().values(
            id=account_id,
            name=account.name,
        )
        insert_wallet = wallets.insert().values(
            id=wallet_id,
            account_id=account_id,
            currency=Currency.USD.value,
            amount=0,
        )
        await db.execute(insert_account)
        await db.execute(insert_wallet)
    
    return AccountCreateResponse(
        account_id=str(account_id),
        wallet_id=str(wallet_id),
    )


async def get_account_with_wallet(account_id):
    query = "SELECT " \
            "account.id as account_id, account.name, " \
            "account.created_at, wallet.id as wallet_id, " \
            "wallet.currency, wallet.amount " \
            "FROM account " \
            "JOIN wallet " \
            "ON wallet.account_id = account.id  " \
            "WHERE  account.id = :account_id;"
    row = await db.fetch_one(query=query, values={"account_id": account_id})
    if row is None:
        return
    return ExtendedAccountResponse(
        account_id=row["account_id"],
        name=row["name"],
        wallet_id=row["wallet_id"],
        currency=row["currency"],
        amount=row["amount"],
        created_at=row["created_at"],
    )
