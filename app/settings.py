"""Application configuration."""

__all__ = ["BaseSettings", "Settings"]


from enum import Enum
from pathlib import Path
from typing import Generator, Self, override

import dotenv
import typer
from pydantic import computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict

from app import APP_NAME, __version__


class Environment(str, Enum):
    """Application deployment environment."""

    PROD = "production"
    DEV = "development"


class BaseSettings(BaseSettings):
    """Base settings configuration."""

    model_config = SettingsConfigDict(
        env_file=dotenv.find_dotenv() or None,
        extra="ignore",
    )

    def resource(self, data_path: Path) -> Generator[Self, None, None]:
        """Create a settings resource that yields a factory."""
        filepath = data_path / f"{type(self).__name__}.json"

        model = self
        if filepath.exists():
            model = self.model_validate_json(filepath.read_text())

        yield model
        filepath.write_text(model.model_dump_json(indent=2))


class Settings(BaseSettings):
    """Application configuration."""

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

    @override
    def resource(self, data_path: Path | None = None) -> Generator[Self, None, None]:
        data_path = data_path or self.data_path
        return super().resource(data_path)
