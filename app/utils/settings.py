"""Application configuration."""

__all__ = ["Settings"]


import atexit
import logging
from abc import ABC
from pathlib import Path
from typing import ClassVar

import dotenv
from pydantic import computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict

from app.utils import helpers


class Settings(BaseSettings, ABC):
    """Base settings configuration."""

    model_config = SettingsConfigDict(
        env_file=dotenv.find_dotenv() or None,
        extra="ignore",
    )
    _data_path: Path | None = None
    _reloaded: ClassVar[bool] = False

    @computed_field(repr=False)
    @property
    def data_path(self) -> Path | None:
        """The application data directory."""
        return self._data_path

    def model_post_init(self, _: None) -> None:
        if self.data_path and not type(self)._reloaded:
            atexit.register(self.save, self.data_path)
            self.load(self.data_path)
        return super().model_post_init(_)

    def load(self, data_path: Path) -> None:
        """Load settings from a data file."""
        self.model_config["json_file"] = self._data_file(data_path)
        type(self)._reloaded = True
        self.__init__()
        logging.getLogger(__name__).debug(f"Loaded settings from {data_path}.")

    def save(self, data_path: Path) -> None:
        """Save settings to a data file."""
        computed_fields = set(self.model_computed_fields.keys())
        self._data_file(data_path).write_text(
            self.model_dump_json(
                indent=2, by_alias=True, exclude=computed_fields
            )
        )
        logging.getLogger(__name__).debug(f"Saved settings to {data_path}.")

    def _data_file(self, data_path: Path) -> Path:
        """Return the settings data file."""
        return (
            data_path / f"{helpers.pascal_to_snake(type(self).__name__)}.json"
        )
