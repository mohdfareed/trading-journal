"""Application models."""

from enum import Enum
from pathlib import Path

from pydantic import computed_field

from app import utils
from app.settings import app_settings


class AppLifecycle(str, Enum):
    """Application lifecycle event."""

    STARTUP = "app:start"
    """Application startup event."""
    SHUTDOWN = "app:stop"
    """Application shutdown event."""


class BaseSettings(utils.Settings):
    """Base settings configuration."""

    @computed_field(repr=False)
    @property
    def data_path(self) -> Path:
        return app_settings.data_path
