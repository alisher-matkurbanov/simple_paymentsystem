import decimal

from pydantic import BaseSettings, Field

MAX_AMOUNT_DEGREE: int = 98
MAX_AMOUNT: decimal.Decimal = decimal.Decimal(10 ** MAX_AMOUNT_DEGREE)


def get_max_decimal(precision, scale):
    return decimal.Decimal("9" * (precision - scale) + "." + "9" * scale)


class Settings(BaseSettings):
    db_url: str = Field(..., env="DATABASE_URL")
    is_testing: bool = Field(False, env="TESTING")
    decimal_precision: int = 19
    decimal_scale: int = 2
    max_amount: decimal.Decimal = get_max_decimal(decimal_precision, decimal_scale)
    min_amount: decimal.Decimal = decimal.Decimal(0)


settings = Settings()
