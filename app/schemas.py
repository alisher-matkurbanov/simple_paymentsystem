from pydantic import BaseModel, Field


class AccountCreateRequest(BaseModel):
    name: str = Field(..., title="Name of the account", max_length=32)


class AccountCreateResponse(BaseModel):
    account_id: str
    wallet_id: str


class APIError(BaseModel):
    error: str = "Internal Error"