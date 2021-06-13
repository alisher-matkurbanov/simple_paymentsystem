from app.database import db
from app.schemas import AccountCreateIn, Currency
from app.crud import uuid, create_account_with_wallet
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
    await create_account_with_wallet(account)
    
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


def test_get_account_with_wallet():
    pass


def test_get_wallet():
    pass


def test_log_transfer_transaction():
    pass


def test_transfer():
    pass


def test_replenish():
    pass


def test_log_replenish_transaction():
    pass
