import enum

from sqlalchemy import (
    NUMERIC,
    Boolean,
    Column,
    DateTime,
    Enum,
    ForeignKey,
    Integer,
    String,
    Table,
    func,
)
from sqlalchemy.dialects.postgresql import UUID

from .database import metadata


class TransactionType(enum.Enum):
    replenish = "REPLENISH"
    transfer = "TRANSFER"


class Currency(enum.Enum):
    USD = "USD"


accounts = Table(
    "account",
    metadata,
    Column("id", UUID(as_uuid=True), primary_key=True),
    Column("name", String(32)),
    Column("is_active", Boolean, nullable=False),
    Column("created_at", DateTime(timezone=True), server_default=func.now()),
    Column("updated_at", DateTime(timezone=True), onupdate=func.now()),
)

wallets = Table(
    "wallet",
    metadata,
    Column("id", UUID(as_uuid=True), primary_key=True),
    Column("account_id", ForeignKey("account.id"), nullable=False),
    Column("currency", ForeignKey("currency.code"), nullable=False),
    Column("amount", NUMERIC(precision=2), nullable=False),
    Column("is_active", Boolean, nullable=False),
    Column(
        "created_at", DateTime(timezone=True), server_default=func.now(), nullable=False
    ),
    Column("updated_at", DateTime(timezone=True), onupdate=func.now()),
)

currencies = Table(
    "currency", metadata, Column("code", Enum(Currency), primary_key=True)
)

transactions = Table(
    "transaction",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("type", Enum(TransactionType), nullable=False),
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
    Column("amount", NUMERIC(precision=2), nullable=False),
    Column("currency", ForeignKey("currency.code"), nullable=False),
)
