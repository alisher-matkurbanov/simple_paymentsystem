from sqlalchemy import (Column, DateTime, ForeignKey, Integer, Numeric, String,
                        Table, func)
from sqlalchemy.dialects.postgresql import UUID

from database import metadata

# table to store account profile
# some info can be added in future (email, phone)
# don't add is_active field to simplify insert logic
# sure, in production we need to save as long as possible the data
# so we probably need to add is_active field to detect account deletion
accounts = Table(
    "account",
    metadata,
    Column("id", UUID(as_uuid=True), primary_key=True),
    Column("name", String(32)),
    Column("created_at", DateTime(timezone=True), server_default=func.now()),
    Column("updated_at", DateTime(timezone=True), onupdate=func.now()),
)

# table to store account's wallet
wallets = Table(
    "wallet",
    metadata,
    Column("id", UUID(as_uuid=True), primary_key=True),
    Column("account_id", ForeignKey("account.id"), nullable=False),
    Column("currency", ForeignKey("currency.code"), nullable=False),
    Column("amount", Numeric(precision=100, scale=2), nullable=False),
    Column(
        "created_at", DateTime(timezone=True), server_default=func.now(), nullable=False
    ),
    Column("updated_at", DateTime(timezone=True), onupdate=func.now()),
)

currencies = Table("currency", metadata, Column("code", String(3), primary_key=True))

transactions = Table(
    "transaction",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("type", String, nullable=False),
    Column(
        "created_at", DateTime(timezone=True), server_default=func.now(), nullable=False
    ),
)

posting = Table(
    "posting",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("transaction_id", ForeignKey("transaction.id"), nullable=False),
    Column("wallet_id", ForeignKey("wallet.id"), nullable=False),
    Column("amount", Numeric(precision=100, scale=2), nullable=False),
    Column("currency", ForeignKey("currency.code"), nullable=False),
)
