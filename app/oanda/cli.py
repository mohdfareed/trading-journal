"""OANDA application."""

__all__ = ["OANDAService"]


import time
from logging import Logger

import typer
from dependency_injector import containers
from dependency_injector.providers import (
    Configuration,
    Dependency,
    Factory,
    Resource,
    Singleton,
)
from dependency_injector.wiring import Provide, inject

from app import logging, persistence, plugins

from .config import OANDAConfig


def register(app: typer.Typer) -> None:
    """Register subcommands with the main Typer app."""
    app.callback()(main)
    app.command()(start)


class OANDAService(containers.DeclarativeContainer):
    """OANDA application."""

    wiring_config = containers.WiringConfiguration(modules=["app.main"])

    # MARK: Dependencies
    configuration: Configuration = Configuration()
    log_dir = Dependency(instance_of=str)
    root_logger = Dependency(instance_of=Logger)
    data_dir = Dependency(instance_of=str)
    plugins_service = Dependency(instance_of=plugins.PluginService)

    # MARK: Configuration
    config = OANDAConfig.factory(configuration)

    # MARK: Logging
    file_handler = Factory(logging.file, log_dir, config().provider.APP_NAME)
    logger = logging.LoggingFactory(
        file_handler,
        source=config().provider.APP_NAME,
        parent=root_logger,
    )

    # MARK: Persistence
    file_persistence = Factory(persistence.FilePersistence, data_dir, logger)
    log_persistence = Factory(persistence.LoggingPersistence, logger=logger)
    config_persistence = Resource(
        persistence.resource,
        config,
        logger,
        log_persistence,
        file_persistence,
    )

    # MARK: CLI
    app = Singleton[typer.Typer](
        typer.Typer,
        name=config().provider.APP_NAME,
        context_settings={"help_option_names": ["-h", "--help"]},
        add_completion=False,
    )
    commands = Resource(register, app)
    plugin = Resource(lambda: OANDAService.plugins_service().register, app)


def main() -> None:
    """The OANDA application."""


@inject
def start(logger: logging.Logger = Provide[OANDAService.logger]) -> None:
    """Start the application."""
    print(logger)
    # logger = logger
    logger.info("Starting...")
    logger.warning("Press Ctrl+C to exit.")

    try:  # Keep the application running
        while True:
            time.sleep(1)
            logger.debug("Running...")
    except KeyboardInterrupt as e:
        print()
        logger.info("Exiting...")
        raise typer.Exit() from e


def start2() -> None:
    """Start the application."""
    try:  # Keep the application running
        while True:
            time.sleep(1)
    except KeyboardInterrupt as e:
        print()
        raise typer.Exit() from e
