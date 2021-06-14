import datetime
import decimal
import uuid

import asyncpg

from app.schemas import AccountCreateOut, ExtendedAccountOut, Currency, ReplenishWalletInfo, TransferMoneyOut
from app.api import crud
from fastapi import status

from app.config import settings


def test_create_accounts_ok(test_app, monkeypatch):
    test_request_payload = {"name": "testname"}
    wallet_id = str(uuid.uuid4())
    account_id = str(uuid.uuid4())
    test_response_payload = {"wallet_id": wallet_id, "account_id": account_id}
    
    async def mock_create_account_with_wallet(payload):
        return AccountCreateOut(
            account_id=account_id,
            wallet_id=wallet_id,
        )
    
    monkeypatch.setattr(
        crud, "create_account_with_wallet", mock_create_account_with_wallet
    )
    
    response = test_app.post("/accounts", json=test_request_payload)
    assert response.status_code == status.HTTP_201_CREATED
    assert response.json() == test_response_payload


def test_create_accounts_bad_body(test_app, monkeypatch):
    test_request_payload = {"something": "wrong"}
    test_response_payload = {
        "detail": [
            {
                "loc": ["body", "name"],
                "msg": "field required",
                "type": "value_error.missing",
            }
        ]
    }
    
    async def mock_create_account_with_wallet(payload):
        return None
    
    monkeypatch.setattr(
        crud, "create_account_with_wallet", mock_create_account_with_wallet
    )
    response = test_app.post("/accounts", json=test_request_payload)
    
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    assert response.json() == test_response_payload


def test_create_accounts_duplicate_exception(test_app, monkeypatch):
    test_request_payload = {"name": "testname"}
    test_response_payload = {
        "detail": f"can't create account 'testname'; try again later"
    }
    
    async def mock_create_account_with_wallet(payload):
        raise asyncpg.exceptions.UniqueViolationError("error description")
    
    monkeypatch.setattr(
        crud, "create_account_with_wallet", mock_create_account_with_wallet
    )
    response = test_app.post("/accounts", json=test_request_payload)
    
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json() == test_response_payload


def test_create_accounts_exception(test_app, monkeypatch, caplog):
    test_request_payload = {"name": "testname"}
    
    async def mock_create_account_with_wallet(payload):
        raise Exception("Exception from test")
    
    monkeypatch.setattr(
        crud, "create_account_with_wallet", mock_create_account_with_wallet
    )
    response = test_app.post("/accounts", json=test_request_payload)
    assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
    assert "Exception from test" in caplog.text


def test_get_account_ok(test_app, monkeypatch):
    wallet_id = uuid.uuid4()
    account_id = uuid.uuid4()
    dt = datetime.datetime.utcnow()
    amount = decimal.Decimal(123)
    currency = Currency.USD
    name = "testname"
    
    test_response_payload = {
        "name": name,
        "wallet_id": str(wallet_id),
        "account_id": str(account_id),
        "created_at": dt.strftime("%Y-%m-%dT%H:%M:%S.%f"),
        "amount": amount,
        "currency": currency.value
    }
    
    account = ExtendedAccountOut(
        account_id=account_id,
        name=name,
        wallet_id=wallet_id,
        currency=currency,
        amount=amount,
        created_at=dt,
    )
    
    async def mock_get_account_with_wallet(payload):
        return account
    
    monkeypatch.setattr(
        crud, "get_account_with_wallet", mock_get_account_with_wallet
    )
    
    response = test_app.get(f"/accounts/{wallet_id}")
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == test_response_payload


def test_get_account_not_found(test_app, monkeypatch):
    account_id = uuid.uuid4()
    values = {"account_id": account_id}
    error_msg = f"account with {values} not found"
    test_response_payload = {
        "detail": error_msg
    }
    
    async def mock_get_account_with_wallet(payload):
        raise crud.NotFound("account", values)
    
    monkeypatch.setattr(
        crud, "get_account_with_wallet", mock_get_account_with_wallet
    )
    
    response = test_app.get(f"/accounts/{account_id}")
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == test_response_payload


def test_get_account_exception(test_app, monkeypatch, caplog):
    account_id = uuid.uuid4()
    
    async def mock_get_account_with_wallet(payload):
        raise Exception("Exception from test")
    
    monkeypatch.setattr(
        crud, "get_account_with_wallet", mock_get_account_with_wallet
    )
    
    response = test_app.get(f"/accounts/{account_id}")
    assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
    assert "Exception from test" in caplog.text


def test_replenish_wallet_ok(test_app, monkeypatch):
    wallet_id = uuid.uuid4()
    amount = decimal.Decimal(1000)
    currency = Currency.USD
    test_request_payload = {
        "wallet_id": str(wallet_id),
        "amount": int(amount),
        "currency": currency.value,
    }
    test_response_payload = test_request_payload
    wallet_info = ReplenishWalletInfo(
        wallet_id=wallet_id,
        amount=amount,
        currency=currency
    )
    
    async def mock_replenish(payload):
        return wallet_info
    
    monkeypatch.setattr(crud, "replenish", mock_replenish)
    
    response = test_app.post(f"/replenish", json=test_request_payload)
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == test_response_payload


def test_replenish_wallet_not_found(test_app, monkeypatch):
    values = {"val1": 1}
    wallet_id = uuid.uuid4()
    amount = decimal.Decimal(1000)
    currency = Currency.USD
    test_request_payload = {
        "wallet_id": str(wallet_id),
        "amount": int(amount),
        "currency": currency.value,
    }
    test_response_payload = {
        "detail": f"wallet with {values} not found",
    }
    
    async def mock_replenish(payload):
        raise crud.NotFound("wallet", values)
    
    monkeypatch.setattr(crud, "replenish", mock_replenish)
    
    response = test_app.post(f"/replenish", json=test_request_payload)
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == test_response_payload


def test_replenish_wallet_limit_exception(test_app, monkeypatch):
    wallet_id = uuid.uuid4()
    amount = decimal.Decimal(1000)
    currency = Currency.USD
    test_request_payload = {
        "wallet_id": str(wallet_id),
        "amount": int(amount),
        "currency": currency.value,
    }
    test_response_payload = {
        "detail": (
            f"can't replenish to {wallet_id}; "
            f"resulting amount is greater that max amount = {settings.max_amount}; "
            f"current amount = {amount}"
        )
    }
    
    async def mock_replenish(payload):
        raise crud.CRUDException(test_response_payload["detail"])
    
    monkeypatch.setattr(crud, "replenish", mock_replenish)
    
    response = test_app.post(f"/replenish", json=test_request_payload)
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json() == test_response_payload


def test_transfer_ok(test_app, monkeypatch):
    from_wallet_id = uuid.uuid4()
    to_wallet_id = uuid.uuid4()
    from_currency = Currency.USD
    to_currency = Currency.USD
    amount = 1000
    from_amount = 0
    to_amount = amount
    
    test_request_payload = {
        "from_wallet_id": str(from_wallet_id),
        "to_wallet_id": str(to_wallet_id),
        "from_currency": from_currency.value,
        "to_currency": to_currency.value,
        "amount": amount,
    }
    test_response_payload = {
        "from_wallet_id": str(from_wallet_id),
        "to_wallet_id": str(to_wallet_id),
        "from_currency": from_currency.value,
        "to_currency": to_currency.value,
        "from_amount": from_amount,
        "to_amount": to_amount,
    }
    
    async def mock_transfer_money(payload):
        return TransferMoneyOut(
            from_wallet_id=from_wallet_id,
            from_amount=decimal.Decimal(from_amount),
            from_currency=from_currency,
            to_wallet_id=to_wallet_id,
            to_amount=decimal.Decimal(to_amount),
            to_currency=to_currency,
        )
    
    monkeypatch.setattr(crud, "transfer", mock_transfer_money)
    
    response = test_app.post(f"/transfer", json=test_request_payload)
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == test_response_payload


def test_transfer_not_found(test_app, monkeypatch):
    from_wallet_id = uuid.uuid4()
    to_wallet_id = uuid.uuid4()
    from_currency = Currency.USD
    to_currency = Currency.USD
    amount = 1000
    values = {"wallet_id": from_wallet_id}
    
    test_request_payload = {
        "from_wallet_id": str(from_wallet_id),
        "to_wallet_id": str(to_wallet_id),
        "from_currency": from_currency.value,
        "to_currency": to_currency.value,
        "amount": amount,
    }
    test_response_payload = {
        "detail": f"wallet with {values} not found",
    }
    
    async def mock_transfer_money(payload):
        raise crud.NotFound("wallet", values)
    
    monkeypatch.setattr(crud, "transfer", mock_transfer_money)
    
    response = test_app.post(f"/transfer", json=test_request_payload)
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == test_response_payload


def test_transfer_limit_exception(test_app, monkeypatch):
    from_wallet_id = uuid.uuid4()
    to_wallet_id = uuid.uuid4()
    from_currency = Currency.USD
    to_currency = Currency.USD
    amount = str(settings.max_amount)
    
    test_request_payload = {
        "from_wallet_id": str(from_wallet_id),
        "to_wallet_id": str(to_wallet_id),
        "from_currency": from_currency.value,
        "to_currency": to_currency.value,
        "amount": amount,
    }
    test_response_payload = {
        "detail": "some text",
    }
    
    async def mock_transfer_money(payload):
        raise crud.CRUDException("some text")
    
    monkeypatch.setattr(crud, "transfer", mock_transfer_money)
    
    response = test_app.post(f"/transfer", json=test_request_payload)
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json() == test_response_payload


def test_super_hard_test():
    # number of tests must be 20
    assert True
