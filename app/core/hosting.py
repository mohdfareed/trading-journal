"""Application host configuration."""

__all__ = ["Host"]


from abc import ABC
from enum import Enum
from typing import Any, Callable, ClassVar

import typer
from blinker import Signal, signal

from . import __name__, logging, settings


class LifecycleEvents(str, Enum):
    """Application lifecycle event."""

    STARTUP = "app:start"
    """Application startup event."""
    SHUTDOWN = "app:stop"
    """Application shutdown event."""


class Services(dict[type, Any | Callable[[], Any]]):

    def __getitem__[T: object](self, key: type[T]) -> T:
        if not (service := self.get(key)):
            raise KeyError(f"Service {key} not found.")
        if isinstance(service, Callable):
            service = service()  # type: ignore
        if not isinstance(service, key):
            raise TypeError(
                f"Service {key} has invalid registration: {service}."
            )
        return service

    def __setitem__[T](self, key: type[T], value: T | Callable[[], T]) -> None:
        if service := self.get(key):
            raise KeyError(f"Service {key} already exists: {service}.")
        super().__setitem__(key, value)


class Host(ABC):
    """Application host."""

    is_started: ClassVar[bool] = False
    startup: ClassVar[Signal] = signal(LifecycleEvents.STARTUP)
    shutdown: ClassVar[Signal] = signal(LifecycleEvents.SHUTDOWN)

    logger: logging.Logger
    dependencies: Services = Services()

    def __init__(self, name: str | None = None) -> None:
        self.logger = logging.getLogger(
            name or type(self).__module__.split(".")[-1]
        )

    def start(self, *args: Any, **kwargs: Any) -> None:
        """Start the application."""
        type(self).is_started = True
        self.logger = logging.create_logger(
            self.logger.name, settings.global_settings.logging_path
        )
        self.logger.debug("Starting up...")
        self.startup.send(self)

    def stop(self, *args: Any, **kwargs: Any) -> None:
        """Stop the application."""
        type(self).is_started = False
        self.logger.debug("Shutting down...")
        self.shutdown.send(self)

    def logs(self) -> None:
        """View the application logs."""
        logging.view_logs(
            settings.global_settings.logging_path / f"{self.logger.name}.log"
        )

    def __getitem__[T: object](self, key: type[T]) -> T:
        return typer.Option(
            self.dependencies[key],
            parser=lambda _: _,
            hidden=True,
            expose_value=False,
        )
