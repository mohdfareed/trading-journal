"""Application settings."""

__all__ = ["app_settings"]

from pathlib import Path

from pydantic import computed_field

from app import core
from app.core.settings import global_settings

app_settings: "AppSettings"
"""Application settings."""


class AppSettings(core.Settings):
    DEBUG_MODE: bool = False

    @computed_field
    @property
    def APP_NAME(self) -> str:
        return global_settings.APP_NAME

    @computed_field
    @property
    def APP_ENV(self) -> core.Environment:
        return global_settings.APP_ENV

    @computed_field
    @property
    def VERSION(self) -> str:
        return global_settings.VERSION

    @computed_field
    @property
    def data_path(self) -> Path:
        return global_settings.data_path

    @computed_field
    @property
    def logging_path(self) -> Path:
        return global_settings.logging_path


app_settings = AppSettings()
