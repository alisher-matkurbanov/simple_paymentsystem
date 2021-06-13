import uuid

import asyncpg

from app.schemas import AccountCreateOut
from app.api import crud
from fastapi import status


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


def test_create_accounts_exception(test_app, monkeypatch):
    test_request_payload = {"name": "testname"}

    async def mock_create_account_with_wallet(payload):
        raise Exception()

    monkeypatch.setattr(
        crud, "create_account_with_wallet", mock_create_account_with_wallet
    )
    response = test_app.post("/accounts", json=test_request_payload)

    assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
