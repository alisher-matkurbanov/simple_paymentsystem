import uuid

from app import config
from app.database import db
from app.dbmodels import accounts, wallets
from app.schemas import (AccountCreateIn, AccountCreateOut,
                     ExtendedAccountOut, ReplenishWalletInfo,
                     TransactionType, TransferMoneyIn,
                     TransferMoneyOut, Currency)


class CRUDException(Exception):
    def __init__(self, message):
        self.message = message
        super().__init__(self.message)


class NotFound(CRUDException):
    def __init__(self, subject: str, values: dict):
        self.message = f"{subject} with {values} not found"
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


async def get_account_with_wallet(
        account_id: uuid.UUID,
) -> ExtendedAccountOut:
    query = (
        "SELECT "
        "account.id as account_id, account.name, "
        "account.created_at, wallet.id as wallet_id, "
        "wallet.currency, wallet.amount "
        "FROM account "
        "JOIN wallet "
        "ON wallet.account_id = account.id  "
        "WHERE  account.id = :account_id;"
    )
    
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


async def get_wallet(wallet_id, currency):
    query = (
        "SELECT * FROM wallet WHERE id = :wallet_id "
        "AND currency = :currency FOR UPDATE;"
    )
    values = {"wallet_id": wallet_id, "currency": currency.value}
    wallet = await db.fetch_one(query=query, values=values)
    if wallet is None:
        raise NotFound("wallet", values)
    return wallet


async def log_transfer_transaction(data):
    add_transaction = (
        "INSERT INTO transaction(type) VALUES (:transaction_type) RETURNING id;"
    )
    
    transaction_id = await db.execute(
        add_transaction, values={"transaction_type": TransactionType.transfer.value}
    )
    add_posting = (
        "INSERT INTO posting(transaction_id, wallet_id, amount, currency) "
        "VALUES(:transaction_id, :wallet_id, :amount, :currency);"
    )
    values = {
        "transaction_id": transaction_id,
        "wallet_id": data.from_wallet_id,
        "amount": -data.amount,
        "currency": data.from_currency.value,
    }
    await db.execute(add_posting, values=values)
    values = {
        "transaction_id": transaction_id,
        "wallet_id": data.from_wallet_id,
        "amount": data.amount,
        "currency": data.to_currency.value,
    }
    await db.execute(add_posting, values=values)


async def transfer(data: TransferMoneyIn) -> TransferMoneyOut:
    async with db.transaction():
        # getting from wallet and check constraints
        from_wallet = await get_wallet(data.from_wallet_id, data.from_currency)
        from_wallet_amount = from_wallet["amount"] - data.amount
        if from_wallet_amount < 0:
            raise CRUDException(
                f"can't transfer {data.amount} {data.from_currency.value} "
                f"from wallet {data.from_wallet_id}: "
                f"not enough amount"
            )
        
        # getting to wallet and check constraints
        to_wallet = await get_wallet(data.to_wallet_id, data.to_currency)
        to_wallet_amount = to_wallet["amount"] + data.amount
        if to_wallet_amount > config.MAX_AMOUNT:
            raise CRUDException(
                f"can't replenish {data.to_wallet_id}; "
                f"limit = 10**{config.MAX_AMOUNT_DEGREE}"
            )
        
        # performing transfer transaction
        update_wallet = "UPDATE wallet SET amount = :amount WHERE id = :wallet_id;"
        from_wallet_values = {
            "wallet_id": data.from_wallet_id,
            "amount": from_wallet_amount,
        }
        await db.execute(query=update_wallet, values=from_wallet_values)
        to_wallet_values = {"wallet_id": data.to_wallet_id, "amount": to_wallet_amount}
        await db.execute(query=update_wallet, values=to_wallet_values)
        
        # logging transaction
        await log_transfer_transaction(data)
        
        return TransferMoneyOut(
            from_wallet_id=data.from_wallet_id,
            from_amount=from_wallet_amount,
            from_currency=data.from_currency,
            to_wallet_id=data.to_wallet_id,
            to_amount=to_wallet_amount,
            to_currency=data.to_currency,
        )


async def replenish(data: ReplenishWalletInfo):
    async with db.transaction():
        query = (
            "SELECT * FROM wallet WHERE id = :wallet_id "
            "AND currency = :currency FOR UPDATE;"
        )
        
        values = {"wallet_id": data.wallet_id, "currency": data.currency.value}
        wallet = await db.fetch_one(query=query, values=values)
        if wallet is None:
            raise NotFound("wallet", values)
        
        amount = wallet["amount"] + data.amount
        if amount > config.MAX_AMOUNT:
            raise CRUDException(
                f"can't replenish {data.wallet_id}; "
                f"limit = 10**{config.MAX_AMOUNT_DEGREE}"
            )
        
        update = "UPDATE wallet SET amount = :amount WHERE id = :wallet_id;"
        values = {"amount": amount, "wallet_id": data.wallet_id}
        await db.execute(update, values=values)
        await log_replenish_transaction(data)
        return ReplenishWalletInfo(
            wallet_id=data.wallet_id, amount=amount, currency=data.currency
        )


async def log_replenish_transaction(data):
    add_transaction = (
        "INSERT INTO transaction(type) VALUES(:transaction_type) RETURNING id;"
    )
    transaction_id = await db.execute(
        add_transaction, values={"transaction_type": TransactionType.replenish.value}
    )
    add_posting = (
        "INSERT INTO posting(transaction_id, wallet_id, amount, currency) "
        "VALUES(:transaction_id, :wallet_id, :amount, :currency);"
    )
    values = {
        "transaction_id": transaction_id,
        "wallet_id": data.wallet_id,
        "amount": data.amount,
        "currency": data.currency.value,
    }
    await db.execute(add_posting, values=values)
