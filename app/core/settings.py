"""Settings utilities."""

__all__ = ["global_settings", "Environment", "Settings"]


import re
from abc import ABC
from enum import Enum
from pathlib import Path
from typing import Any, ClassVar, override

import dotenv
import rich
import typer
from pydantic_settings import (
    BaseSettings,
    JsonConfigSettingsSource,
    PydanticBaseSettingsSource,
    SettingsConfigDict,
)

from app import APP_NAME, __version__

global_settings: "GlobalSettings"
"""Global application settings."""


class Environment(str, Enum):
    """Application deployment environment."""

    PROD = "production"
    DEV = "development"


class GlobalSettings(BaseSettings):
    APP_ENV: Environment = Environment.PROD
    APP_NAME: ClassVar[str] = APP_NAME
    VERSION: ClassVar[str] = __version__
    DEV_DATA_PATH: ClassVar[Path] = (
        Path(__file__).parent.parent.parent / "data"
    )

    model_config = SettingsConfigDict(
        env_file=dotenv.find_dotenv() or None,
        extra="ignore",
    )

    @property
    def data_path(self) -> Path:
        return (
            Path(typer.get_app_dir(self.APP_NAME))
            if self.APP_ENV != Environment.DEV
            else self.DEV_DATA_PATH
        )

    @property
    def logging_path(self) -> Path:
        return self.data_path / "logs"


class Settings(BaseSettings, ABC):
    """Configurable settings base class. Reads settings from a JSON file."""

    model_config = GlobalSettings.model_config
    settings_exclude: ClassVar[set[str]] = set()
    """Settings names to exclude from the JSON configuration file."""

    @property
    def settings_excluded_fields(self) -> set[str]:
        return set(self.model_computed_fields.keys()) | self.settings_exclude

    @classmethod
    def settings_json_file(cls) -> Path:
        return (
            global_settings.data_path / f"{pascal_to_snake(cls.__name__)}.json"
        )

    @classmethod
    def settings_customise_sources(
        cls,
        settings_cls: type[BaseSettings],
        init_settings: PydanticBaseSettingsSource,
        env_settings: PydanticBaseSettingsSource,
        dotenv_settings: PydanticBaseSettingsSource,
        file_secret_settings: PydanticBaseSettingsSource,
    ) -> tuple[PydanticBaseSettingsSource, ...]:
        return (
            init_settings,
            env_settings,
            dotenv_settings,
            file_secret_settings,
            JsonConfigSettingsSource(
                settings_cls, json_file=cls.settings_json_file()
            ),
        )

    @override
    def model_post_init(self, __context: Any) -> None:
        store_settings(self)
        return super().model_post_init(__context)

    def config(
        self,
        edit: bool = typer.Option(
            False, "--edit", "-e", help="Edit the configuration."
        ),
    ) -> None:
        """Show/edit the application settings."""
        if not edit:
            rich.print(f"Configuration: {self.settings_json_file()}")
            rich.print_json(self.model_dump_json())
            return

        if not self.settings_json_file().exists():
            store_settings(self)
        typer.edit(filename=str(self.settings_json_file()))


def store_settings(settings: Settings) -> None:
    config_file = settings.settings_json_file()
    if config_file and config_file.exists():
        return  # Do not overwrite existing configuration

    config_file.parent.mkdir(parents=True, exist_ok=True)
    config_file.touch(exist_ok=True)
    config_file.write_text(
        settings.model_dump_json(
            indent=2,
            by_alias=True,
            exclude=settings.settings_excluded_fields,
        )
    )


def pascal_to_snake(name: str) -> str:
    s1 = re.sub(r"([^_])([A-Z][a-z]+)", r"\1_\2", name)
    snake_case = re.sub(r"([a-z0-9])([A-Z])", r"\1_\2", s1).lower()
    return snake_case


global_settings = GlobalSettings()
