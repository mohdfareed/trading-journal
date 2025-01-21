"""Application configuration."""

__all__ = ["AppConfig", "edit_config"]

from enum import Enum
from pathlib import Path

import dotenv
import typer
import typer.completion
from pydantic_settings import BaseSettings, SettingsConfigDict

from app import APP_NAME, logging

data_dir = Path(typer.get_app_dir(APP_NAME))
env_file = dotenv.find_dotenv() or data_dir / ".env"


class OANDAEnvironment(str, Enum):
    """OANDA environment."""

    PRACTICE = "practice"
    LIVE = "live"


class AppConfig(BaseSettings):
    """Application configuration."""

    model_config = SettingsConfigDict(env_file=env_file)

    OANDA_API_KEY: str = ""
    OANDA_ACCOUNT_ID: str = ""
    OANDA_ENVIRONMENT: OANDAEnvironment = OANDAEnvironment.PRACTICE

    def save(self) -> None:
        """Save the configuration to a file."""
        logging.LOGGER.debug("Saving configuration to %s", env_file)
        for key, value in self.model_dump(by_alias=True).items():
            value = value if not isinstance(value, Enum) else value.value
            dotenv.set_key(env_file, key, str(value))


def edit_config(
    api_key: str = typer.Option(AppConfig().OANDA_API_KEY, help="OANDA API key."),
    account_id: str = typer.Option(
        AppConfig().OANDA_ACCOUNT_ID, help="OANDA account ID."
    ),
    environment: OANDAEnvironment = typer.Option(
        AppConfig().OANDA_ENVIRONMENT, help="OANDA environment."
    ),
) -> None:
    """Edit the application configuration."""

    config = AppConfig()
    config.OANDA_API_KEY = api_key  # pylint: disable=invalid-name
    config.OANDA_ACCOUNT_ID = account_id  # pylint: disable=invalid-name
    config.OANDA_ENVIRONMENT = environment  # pylint: disable=invalid-name
    config.save()

    logging.LOGGER.info("Configuration saved.")
    logging.LOGGER.info(config.model_dump_json(indent=2))
