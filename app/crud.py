import uuid
from typing import Optional

from database import db
from dbmodels import Currency, accounts, wallets, TransactionType
from schemas import AccountCreateIn, AccountCreateOut, ExtendedAccountOut, TransferMoneyIn, ReplenishWallet
import config


class NotFound(Exception):
    def __init__(self, subject: str, values: dict):
        self.message = f"{subject} with {values} not found"
        super().__init__(self.message)


class LimitOverflow(Exception):
    def __init__(self, message):
        self.message = message
        super().__init__(self.message)


async def create_account_with_wallet(account: AccountCreateIn) -> AccountCreateOut:
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
    
    return AccountCreateOut(
        account_id=str(account_id),
        wallet_id=str(wallet_id),
    )


async def get_account_with_wallet(account_id: uuid.UUID) -> Optional[ExtendedAccountOut]:
    query = "SELECT " \
            "account.id as account_id, account.name, " \
            "account.created_at, wallet.id as wallet_id, " \
            "wallet.currency, wallet.amount " \
            "FROM account " \
            "JOIN wallet " \
            "ON wallet.account_id = account.id  " \
            "WHERE  account.id = :account_id;"
    
    values = {"account_id": account_id}
    row = await db.fetch_one(query=query, values=values)
    if row is None:
        raise NotFound("account", values)
    
    return ExtendedAccountOut(
        account_id=row["account_id"],
        name=row["name"],
        wallet_id=row["wallet_id"],
        currency=row["currency"],
        amount=row["amount"],
        created_at=row["created_at"],
    )


async def transfer(data: TransferMoneyIn):
    # todo in transaction get for update
    # todo count is in limit and not problems
    # todo decrease first account
    # todo increase second account
    # todo log to journal
    # todo log to posting
    # todo commit
    async with db.transaction():
        query = "SELECT * FROM wallet WHERE id = :wallet_id FOR UPDATE;"
        
        values = {"wallet_id": data.from_wallet_id}
        from_wallet = await db.fetch_one(query=query, values=values)
        if from_wallet is None:
            raise NotFound("wallet", values)
        
        values = {"wallet_id": data.to_wallet_id}
        to_wallet = await db.fetch_one(query=query, values=values)
        if to_wallet is None:
            raise NotFound("wallet", values)
        # todo complete


async def replenish(data: ReplenishWallet):
    async with db.transaction():
        query = "SELECT * FROM wallet " \
                "WHERE id = :wallet_id " \
                "AND currency = :currency " \
                "FOR UPDATE;"
        
        values = {"wallet_id": data.wallet_id, "currency": data.currency.value}
        wallet = await db.fetch_one(query=query, values=values)
        if wallet is None:
            raise NotFound("wallet", values)
        
        amount = wallet["amount"] + data.amount
        if amount > config.MAX_AMOUNT:
            raise LimitOverflow(f"can't replenish {data.wallet_id}; "
                                f"limit = 10**{config.MAX_AMOUNT_DEGREE}")
        
        update = "UPDATE wallet SET amount = :amount WHERE id = :wallet_id AND currency = :currency;"
        values = {"amount": amount, "wallet_id": data.wallet_id, "currency": data.currency.value}
        await db.execute(update, values=values)
        
        add_tx = "INSERT INTO transaction(type) VALUES(:tx_type) RETURNING id;"
        tx_id = await db.execute(add_tx, values={"tx_type": TransactionType.replenish.value})
        add_posting = "INSERT INTO posting(transaction_id, wallet_id, amount, currency) " \
                      "VALUES(:tx_id, :wallet_id, :amount, :currency);"
        values = {
            "tx_id": tx_id,
            "wallet_id": data.wallet_id,
            "amount": amount,
            "currency": data.currency.value
        }
        await db.execute(add_posting, values=values)
        return ReplenishWallet(
            wallet_id=data.wallet_id,
            amount=amount,
            currency=data.currency
        )
