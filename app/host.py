"""Application main container."""

__all__ = ["AppLifecycle", "AppHost", "create_app_host"]

from enum import Enum

import typer
from blinker import signal
from dependency_injector import containers, providers

from app import logging, settings


class AppLifecycle(str, Enum):
    """Application lifecycle event."""

    STARTUP = "app:start"
    """Application startup event."""
    SHUTDOWN = "app:stop"
    """Application shutdown event."""


class AppHost(containers.DeclarativeContainer):
    """Application host container."""

    wiring_config = containers.WiringConfiguration(modules=["app"])

    startup = signal(AppLifecycle.STARTUP, AppLifecycle.STARTUP.__doc__)
    startup = signal(AppLifecycle.SHUTDOWN, AppLifecycle.SHUTDOWN.__doc__)

    app = providers.Dependency(instance_of=typer.Typer)
    debug_mode = providers.Dependency(instance_of=bool)

    app_settings = providers.Resource(
        settings.Settings(DEBUG=bool(debug_mode.provided)).resource
    )

    logger = providers.Singleton(
        logging.setup_logging,
        logger=logging.getLogger(__name__.split(".")[0]),
        debug=debug_mode,
    )

    file_logging = providers.Resource[None](
        logging.setup_file_logging,
        logger=logger,
        log_dir=app_settings.provided.logging_path,
    )


def create_app_host(app: typer.Typer, debug: bool) -> AppHost:
    """Create the application host."""
    return AppHost(app=app, debug_mode=debug)
