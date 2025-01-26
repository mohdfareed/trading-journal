"""Application configuration."""

__all__ = ["OANDAConfig"]

from enum import Enum

# import v20  # type: ignore[import-untyped]
from pydantic import Field, field_validator

from app import models


class OANDAEnvironment(str, Enum):
    """OANDA environment."""

    PRACTICE = "practice"
    LIVE = "live"


class OANDAConfig(models.Config):
    """OANDA configuration."""

    APP_NAME: str = Field(default="oanda", exclude=True)
    OANDA_API_KEY: str = ""
    OANDA_ACCOUNT_ID: str = ""
    OANDA_ENVIRONMENT: OANDAEnvironment = OANDAEnvironment.PRACTICE

    @classmethod
    @field_validator("OANDA_API_KEY", "OANDA_ACCOUNT_ID")
    def validate_fields(cls, value: str) -> str:
        """Validate the OANDA API key and account ID."""
        if not value:
            raise ValueError("must not be empty")
        return value


# def check_oanda_credentials(
#     api_key: str, account_id: str, environment: OANDAEnvironment
# ) -> bool:

#     api = v20.account.Account(id=account_id, environment=environment.value)

#     title: str = api.title()
#     typer.echo(title)

#     return True
