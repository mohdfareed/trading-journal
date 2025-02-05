"""Application configuration."""

__all__ = ["oanda_settings"]

from enum import Enum

from pydantic import computed_field, field_validator
from pydantic_settings import SettingsConfigDict

from app import core


class OANDAEnvironment(str, Enum):
    """OANDA environment."""

    PRACTICE = "practice"
    LIVE = "live"


class OANDASettings(core.Settings):
    """OANDA configuration."""

    APP_NAME: str = "oanda"
    API_KEY: str = ""
    ACCOUNT_ID: str = ""
    ENVIRONMENT: OANDAEnvironment = OANDAEnvironment.PRACTICE

    settings_exclude = {"APP_NAME"}
    model_config = SettingsConfigDict(
        core.Settings.model_config, env_prefix="OANDA_"
    )

    @computed_field
    @property
    def base_url(self) -> str:
        """Return the base URL for the OANDA environment."""
        url = (
            "api-fxpractice.oanda.com"
            if self.ENVIRONMENT == OANDAEnvironment.PRACTICE
            else "api-fxtrade.oanda.com"
        )
        return f"https://{url}/v3"

    @computed_field
    @property
    def request_headers(self) -> dict[str, str]:
        """Return the request headers for the OANDA API."""
        return {
            "Authorization": f"Bearer {self.API_KEY}",
            "Content-Type": "application/json",
        }

    @field_validator("API_KEY")
    @classmethod
    def validate_KEY(cls, key: str) -> str:
        """Validate the OANDA API key."""
        return key

    @field_validator("ACCOUNT_ID")
    @classmethod
    def validate_ID(cls, key: str) -> str:
        """Validate the OANDA account ID."""
        return key


oanda_settings = OANDASettings()
