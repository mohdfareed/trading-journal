"""Application configuration."""

__all__ = ["oanda_settings"]

from enum import Enum
from pathlib import Path

from pydantic import Field, field_validator

from app.settings import app_settings
from app.utils import settings


class OANDAEnvironment(str, Enum):
    """OANDA environment."""

    PRACTICE = "practice"
    LIVE = "live"


class OANDASettings(settings.Settings):
    """OANDA configuration."""

    _data_path: Path | None = app_settings.data_path

    OANDA_API_KEY: str = ""
    OANDA_ACCOUNT_ID: str = ""
    OANDA_ENVIRONMENT: OANDAEnvironment = OANDAEnvironment.PRACTICE

    APP_NAME: str = Field(default="oanda", exclude=True)

    @field_validator("OANDA_API_KEY", "OANDA_ACCOUNT_ID")
    @classmethod
    def validate_fields(cls, value: str) -> str:
        """Validate the OANDA API key and account ID."""
        if not value:
            raise ValueError("must not be empty")
        return value


oanda_settings = OANDASettings()
