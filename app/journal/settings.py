"""Application configuration."""

__all__ = ["journal_settings"]

import importlib
from enum import Enum
from typing import TYPE_CHECKING

from pydantic_settings import SettingsConfigDict

from app import core

journal_settings: "JournalSettings"

if TYPE_CHECKING:
    from .models import Broker


class Brokerage(Enum):
    OANDA = "oanda"

    def resolve(self) -> "Broker":
        """Resolve the brokerage."""
        return importlib.import_module(f"app.{self.value}")  # type: ignore


class JournalSettings(core.Settings):
    """Journal configuration."""

    APP_NAME: str = "journal"
    BROKERAGE: Brokerage = Brokerage.OANDA

    settings_exclude = {"APP_NAME"}
    model_config = SettingsConfigDict(
        core.Settings.model_config, env_prefix="JOURNAL_"
    )


journal_settings = JournalSettings()
