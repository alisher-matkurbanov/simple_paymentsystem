from fastapi import FastAPI

app = FastAPI()


@app.post("/accounts")
async def create_account():
    response = {
        "wallet_id": 123
    }
    raise NotImplemented


@app.get("/accounts/{account_id}")
async def get_account(account_id):
    raise NotImplemented


@app.post("/replenish")
async def replenish_wallet():
    raise NotImplemented


@app.post("/transfer")
async def transfer_money():
    raise NotImplemented

# account
# - account_id: UUID
# - name: String for Firdavs
# - active: Bool
# - created_at
# - updated_at

# wallet 1 - 1 to account
# - account_id: UUID
# - wallet_id: UUID
# - currency_id: int
# - amount: Decimal
# - active: Bool
# - created_at
# - updated_at

# currency
# - currency_id
# - title

# journal
# - journal_id
# - transaction_type
# - created_at

# posting
# - posting_id
# - journal_id
# - wallet_id
# - amount
# - currency_id
