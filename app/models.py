"""Application models."""

__all__ = ["Lifecycle", "LifecycleEvent", "Settings"]

from enum import Enum
from pathlib import Path

from blinker import signal
from pydantic import computed_field

from app import utils
from app.settings import app_settings


class LifecycleEvent(str, Enum):
    """Application lifecycle event."""

    STARTUP = "app:start"
    """Application startup event."""
    SHUTDOWN = "app:stop"
    """Application shutdown event."""


class Lifecycle:
    """Application lifecycle signals."""

    def __init__(self) -> None:
        self.startup = signal(
            LifecycleEvent.STARTUP, LifecycleEvent.STARTUP.__doc__
        )
        self.shutdown = signal(
            LifecycleEvent.SHUTDOWN, LifecycleEvent.SHUTDOWN.__doc__
        )


class Settings(utils.PersistedSettings):
    """Base settings configuration."""

    @computed_field(repr=False)
    @property
    def data_path(self) -> Path:
        return app_settings.data_path
