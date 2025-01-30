"""Application configuration."""

__all__ = ["Settings", "AppSettings"]


import re
from enum import Enum
from pathlib import Path
from typing import Generator, Self

import dotenv
import typer
from pydantic import computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict

from app import APP_NAME, __version__


class Environment(str, Enum):
    """Application deployment environment."""

    PROD = "production"
    DEV = "development"


class Settings(BaseSettings):
    """Base settings configuration."""

    model_config = SettingsConfigDict(
        env_file=dotenv.find_dotenv() or None,
        extra="ignore",
    )

    @classmethod
    def resource(cls, model: Self, data_path: Path) -> Generator[None, None, None]:
        """Create a settings resource to load from and save to a JSON file."""
        data_file = data_path / f"{pascal_to_snake(cls.__name__)}.json"
        model.model_config["json_file"] = data_file
        model.__init__()

        yield

        computed_fields = set(model.model_computed_fields.keys())
        Path(data_file).write_text(
            model.model_dump_json(indent=2, exclude=computed_fields)
        )


class AppSettings(Settings):
    """Application configuration and settings."""

    ENVIRONMENT: Environment = Environment.PROD
    DEBUG: bool = False

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

    @classmethod
    def resource(
        cls, model: Self, data_path: Path | None = None
    ) -> Generator[None, None, None]:
        data_path = data_path or model.data_path
        yield from super().resource(model, data_path)


def pascal_to_snake(name: str) -> str:
    s1 = re.sub("(.)([A-Z][a-z]+)", r"\1_\2", name)
    snake_case = re.sub("([a-z0-9])([A-Z])", r"\1_\2", s1).lower()
    return snake_case
