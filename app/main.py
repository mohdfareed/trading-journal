"""Main module for the Typer application CLI."""

__all__ = ["cli_app"]


import shutil
from pathlib import Path
from typing import Annotated

import rich
import typer
import typer.completion
from dependency_injector.containers import DynamicContainer
from dependency_injector.providers import (
    Configuration,
    Factory,
    Provider,
    Resource,
    Singleton,
)
from dependency_injector.wiring import Provide, inject

from app import config, logging, oanda, persistence, plugins

# MARK: Configuration

app_host = DynamicContainer()
configuration = Configuration()
app_host.config = configuration
app_host.wire(modules=[__name__, "__main__", ".main", "app.main"])
app_config = config.AppConfig.factory(configuration)

# Logging container

logging_container = Resource(
    logging.LoggingService,
    app_name=app_config().provider.APP_NAME,
    debug_mode=app_config().provider.DEBUG,
    log_dir=app_config().provider.log_dir,
)
app_host.logging_service = logging_container

# Persistence container

persistence_container = Resource(
    persistence.PersistenceService,
    config=app_config,
    data_path=app_config().provider.data,
    logger=logging_container().app_logger,
)
app_host.persistence_service = persistence_container

# MARK: CLI

cli_app = Singleton[typer.Typer](
    typer.Typer,
    name=app_config().provider.APP_NAME,
    context_settings={"help_option_names": ["-h", "--help"]},
    add_completion=False,
)
app_host.app = cli_app
plugin_manager = Singleton(plugins.PluginService, cli_app)

# MARK: OANDA

oanda_container = Resource(
    oanda.OANDAService,
    configuration=configuration,
    root_logger=lambda: logging_container().root_logger,
    plugins_service=plugin_manager,
    data_dir=app_config().provider.data,
    log_dir=app_config().provider.log_dir,
)
app_host.oanda_service = oanda_container


# MARK: Main


app_host.init_resources()  # type: ignore[unused-ignore]
app = cli_app()


@app.callback()
@inject
def main(
    ctx: typer.Context,
    debug_mode: Annotated[
        bool,
        typer.Option("--debug", "-d", help="Log debug messages to the console."),
    ] = False,
    log: Annotated[
        Provider[logging.Logger],
        typer.Option(hidden=True, expose_value=False, parser=lambda _: _),
    ] = Provide[logging_container().app_logger()],
) -> None:
    """Trading Journal CLI."""
    ctx.call_on_close(app_host.shutdown_resources)  # type: ignore[unused-ignore]
    if not debug_mode:
        return

    logger: logging.Logger = log.provider  # type: ignore
    instance = app_config()
    instance.DEBUG = True
    instance.save()
    logger.debug("Debug mode enabled.")


@app.command()
@inject
def version(
    app_version: Annotated[
        Provider[str],
        typer.Argument(hidden=True, expose_value=False, parser=lambda _: _),
    ] = Provide[app_config().VERSION]
) -> None:
    """Show the application version."""
    rich.print(app_version.provider)  # type: ignore[unused-ignore]


@app.command("config")
@inject
def show_config(
    app_configuration: Annotated[
        Factory[config.AppConfig],
        typer.Argument(hidden=True, expose_value=False, parser=lambda _: _),
    ] = Provide[app_config()]
) -> None:
    """Show the application version."""
    rich.print(app_configuration.provider)  # type: ignore[unused-ignore]


@app.command()
@inject
def clean(
    data_dir: Annotated[
        Provider[Path],
        typer.Argument(hidden=True, expose_value=False, parser=lambda _: _),
    ] = Provide[app_config().data]
) -> None:
    """Show the application version."""

    path: Path = data_dir.provider  # type: ignore
    shutil.rmtree(path, ignore_errors=True)
    path.mkdir(parents=True, exist_ok=True)
    rich.print(f"Cleaned data directory: {path}")
