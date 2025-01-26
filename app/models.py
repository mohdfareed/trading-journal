"""Application models."""

__all__ = [
    "Config",
    "Persistence",
    "AppError",
    "ConfigError",
]

from abc import ABC, abstractmethod
from enum import Enum
from typing import Self

import dotenv
import rich
from blinker import NamedSignal, signal
from dependency_injector import providers
from pydantic import BaseModel, ConfigDict, Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class AppLifecycle(str, Enum):
    """Application lifecycle event."""

    STARTUP = "app:start"
    """Application startup event."""
    SHUTDOWN = "app:stop"
    """Application shutdown event."""


event = signal(AppLifecycle.STARTUP, AppLifecycle.STARTUP.__doc__)
rich.print(event.__dict__)


@event.connect_via(None)
def test(a: int) -> None:
    print(a)


event.send(1)

exit(0)


class Event[**P](NamedSignal):
    """Application event."""


class Model(BaseModel):
    """Application host configuration model."""

    model_config = ConfigDict(extra="allow")

    def __str__(self) -> str:
        return self.model_dump_json(indent=2)


class Config(Model, BaseSettings, ABC):
    """Application configuration interface."""

    model_config = SettingsConfigDict(
        env_file=dotenv.find_dotenv() or None,
        extra="ignore",
    )
    config_provider: providers.Configuration = Field(exclude=True)

    @property
    def provider(self) -> Self:
        """The app configuration provider."""
        return self.config_provider  # type: ignore

    def load(self) -> Self:
        """Load the model from the app configuration."""
        return self.model_validate(self.config_provider())

    def save(self) -> None:
        """Save the model to the app configuration."""
        self.config_provider.from_pydantic(self)  # type: ignore[unused-ignore] # pylint: disable=no-member

    @classmethod
    def factory(cls, provider: providers.Configuration) -> providers.Factory[Self]:
        """Create a factory for the model."""
        return providers.Factory(cls._create, provider.provider)  # type: ignore[unused-ignore]

    @classmethod
    def _create(cls, provider: providers.Configuration) -> Self:
        data = provider()
        data["config_provider"] = provider
        model = cls.model_validate(data)
        model.save()
        return model


class Persistence(ABC):
    """Data persistence interface."""

    @abstractmethod
    def store(self, model: BaseModel) -> None:
        """Store data to the persistence layer."""

    @abstractmethod
    def load[T: BaseModel](self, model: T) -> T:
        """Load data from the persistence layer."""


# MARK: Exceptions


class AppError(Exception):
    """Application error."""


class ConfigError(AppError):
    """App configuration error."""


class PersistenceError(AppError):
    """App persistence error."""
