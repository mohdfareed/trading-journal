"""Application configuration."""

__all__ = ["AppConfig"]


from enum import Enum
from pathlib import Path

import typer
from pydantic import Field, computed_field

from app import APP_NAME, __version__, models


class AppEnvironment(str, Enum):
    """Application deployment environment."""

    PROD = "production"
    DEV = "development"


class AppConfig(models.Config):
    """Application configuration."""

    ENVIRONMENT: AppEnvironment = AppEnvironment.PROD
    DEBUG: bool = False

    APP_NAME: str = Field(default=APP_NAME, exclude=True)
    VERSION: str = Field(default=__version__, exclude=True)

    @computed_field(repr=False)  # type: ignore[prop-decorator]
    @property
    def data(self) -> Path:
        """The application data directory."""
        file = (
            Path(typer.get_app_dir(APP_NAME))
            if self.ENVIRONMENT == AppEnvironment.PROD
            else Path(__file__).parent.parent / "data"
        )
        file.mkdir(parents=True, exist_ok=True)
        return file

    @computed_field(repr=False)  # type: ignore[prop-decorator]
    @property
    def log_dir(self) -> Path:
        """The application logs directory."""
        path = self.data / "logs"
        path.mkdir(parents=True, exist_ok=True)
        return path
