"""Application configuration."""

__all__ = ["app_settings"]


from enum import Enum
from pathlib import Path

import typer
from pydantic import Field, computed_field

from app import APP_NAME, __version__, utils


class Environment(str, Enum):
    """Application deployment environment."""

    PROD = "production"
    DEV = "development"


class AppSettings(utils.Settings):
    """Application configuration and settings."""

    ENVIRONMENT: Environment = Environment.PROD

    APP_NAME: str = Field(default=APP_NAME, exclude=True)
    VERSION: str = Field(default=__version__, exclude=True)

    @computed_field(repr=False)
    @property
    def data_path(self) -> Path:
        """The application data directory."""
        file = (
            Path(typer.get_app_dir(APP_NAME))
            if self.ENVIRONMENT == Environment.PROD
            else Path(__file__).parent.parent / "data"
        )
        file.mkdir(parents=True, exist_ok=True)
        return file

    @computed_field(repr=False)
    @property
    def logging_path(self) -> Path:
        """The application logs directory."""
        path = self.data_path / "logs"
        path.mkdir(parents=True, exist_ok=True)
        return path


app_settings = AppSettings()
