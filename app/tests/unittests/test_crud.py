import datetime
import decimal

from app.database import db
from app.schemas import AccountCreateIn, Currency, ExtendedAccountOut
from app.crud import uuid
from app import crud
import pytest


@pytest.mark.asyncio
async def test_create_account_with_wallet(monkeypatch):
    await db.connect()
    test_uuid = uuid.uuid4()
    test_name = "testname"
    account = AccountCreateIn(name=test_name)
    
    def mock_uuid4():
        return test_uuid
    
    monkeypatch.setattr(uuid, "uuid4", mock_uuid4)
    await crud.create_account_with_wallet(account)
    
    # check account in database
    select_account_with_wallet = (
        "SELECT "
        "account.id as account_id, account.name, "
        "account.created_at, wallet.id as wallet_id, "
        "wallet.currency, wallet.amount "
        "FROM account JOIN wallet "
        "ON wallet.account_id = account.id  "
        "WHERE  account.id = :account_id;"
    )
    values = {"account_id": test_uuid}
    row = await db.fetch_one(query=select_account_with_wallet, values=values)
    await db.disconnect()
    assert row is not None
    assert row["wallet_id"] == test_uuid
    assert row["name"] == test_name
    assert row["currency"] == Currency.USD.value
    assert row["amount"] == 0


@pytest.mark.asyncio
async def test_get_account_with_wallet():
    await db.connect()
    account_uuid = uuid.uuid4()
    wallet_uuid = uuid.uuid4()
    name = "testname"
    amount = decimal.Decimal("9999999.12")
    currency = Currency.USD
    created_at = datetime.datetime.now(tz=datetime.timezone.utc)
    
    expected = ExtendedAccountOut(
        account_id=account_uuid,
        name=name,
        wallet_id=wallet_uuid,
        currency=currency,
        amount=amount,
        created_at=created_at,
    )
    insert_account = "INSERT INTO account(id, name, created_at) " \
                     "VALUES (:account_id, :name, :created_at);"
    insert_wallet = "INSERT INTO wallet(id, account_id, amount, currency) " \
                    "VALUES (:wallet_id, :account_id, :amount, :currency);"
    values = {"account_id": account_uuid, "name": name, "created_at": created_at}
    await db.execute(insert_account, values)
    values = {
        "account_id": account_uuid,
        "wallet_id": wallet_uuid,
        "amount": amount,
        "currency": currency.value
    }
    await db.execute(insert_wallet, values)
    
    account = await crud.get_account_with_wallet(account_uuid)
    
    # check account in database
    
    await db.disconnect()
    assert account == expected


def test_log_transfer_transaction():
    pass


def test_transfer():
    pass


def test_replenish():
    pass


def test_log_replenish_transaction():
    pass
