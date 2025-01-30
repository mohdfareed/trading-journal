"""Application configuration."""

__all__ = ["OANDASettings"]

from enum import Enum

from pydantic import field_validator

from app import settings


class OANDAEnvironment(str, Enum):
    """OANDA environment."""

    PRACTICE = "practice"
    LIVE = "live"


class OANDASettings(settings.Settings):
    """OANDA configuration."""

    OANDA_API_KEY: str = ""
    OANDA_ACCOUNT_ID: str = ""
    OANDA_ENVIRONMENT: OANDAEnvironment = OANDAEnvironment.PRACTICE

    @field_validator("OANDA_API_KEY", "OANDA_ACCOUNT_ID")
    @classmethod
    def validate_fields(cls, value: str) -> str:
        """Validate the OANDA API key and account ID."""
        if not value:
            raise ValueError("must not be empty")
        return value
