"""Application main container."""

__all__ = ["Host", "AppHost"]

from enum import Enum
from typing import Any, Generator

import typer
from blinker import signal
from dependency_injector import containers, providers, wiring

from app import logging, settings


class AppLifecycle(str, Enum):
    """Application lifecycle event."""

    STARTUP = "app:start"
    """Application startup event."""
    SHUTDOWN = "app:stop"
    """Application shutdown event."""

    @classmethod
    def resource(
        cls, app: "Host", *args: Any, **kwargs: Any
    ) -> Generator[None, None, None]:
        """Return the resource name."""
        signal(cls.STARTUP).send(app, *args, **kwargs)
        yield
        signal(cls.SHUTDOWN).send(app, *args, **kwargs)


class Host(containers.DeclarativeContainer):
    """Base host container."""

    startup = providers.Factory(
        signal, AppLifecycle.STARTUP, AppLifecycle.STARTUP.__doc__
    )
    shutdown = providers.Factory(
        signal, AppLifecycle.SHUTDOWN, AppLifecycle.SHUTDOWN.__doc__
    )

    @classmethod
    def resolve[T](cls, provider: providers.Provider[T], _: type[T] | None = None) -> T:
        return wiring.Provide[provider].provider()

    @classmethod
    def resolve_cli[
        T
    ](cls, provider: providers.Provider[T], _: type[T] | None = None) -> T:
        return typer.Argument(
            hidden=True,
            expose_value=False,
            parser=lambda _: _,
            default=cls.resolve(provider),
        )


class AppHost(Host):
    """Application host container."""

    wiring_config = containers.WiringConfiguration(modules=["app"])

    app = providers.Dependency(instance_of=typer.Typer)
    app_settings = providers.Singleton(settings.AppSettings)
    logger = providers.Factory(
        logging.setup_logging,
        logger=logging.getLogger(__name__.split(".")[0]),
        debug=app_settings.provided.DEBUG,
        logging_path=app_settings.provided.logging_path,
    )

    _log_file_header = providers.Resource(logging.stamp_file, logger=logger)
    _settings_persistence = providers.Resource[None](
        settings.AppSettings.resource, app_settings
    )
    _events = providers.Resource(AppLifecycle.resource, app)

    @staticmethod
    def create_host(app: typer.Typer) -> "AppHost":
        """Create the application host."""
        return AppHost(app=app)
