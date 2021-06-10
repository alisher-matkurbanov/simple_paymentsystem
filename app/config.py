import decimal

from pydantic import BaseSettings, Field

MAX_AMOUNT_DEGREE: int = 98
MAX_AMOUNT: decimal.Decimal = decimal.Decimal(10 ** MAX_AMOUNT_DEGREE)


class Settings(BaseSettings):
    db_url: str = Field(..., env="DATABASE_URL")


settings = Settings()
