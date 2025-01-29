"""Main module for the Typer application CLI."""

__all__ = ["app"]


import shutil
from pathlib import Path
from typing import Annotated

import rich
import typer
import typer.completion
from dependency_injector import wiring

from app import APP_NAME, __version__, host, settings

app = typer.Typer(
    name=APP_NAME,
    context_settings={"help_option_names": ["-h", "--help"]},
    add_completion=False,
)


@app.callback()
def main(
    ctx: typer.Context,
    debug_mode: Annotated[
        bool,
        typer.Option("--debug", "-d", help="Log debug messages to the console."),
    ] = False,
) -> None:
    """Trading Journal CLI."""

    app_host = host.create_app_host(app, debug_mode)
    app_host.init_resources()  # type: ignore[unused-ignore]
    ctx.call_on_close(app_host.shutdown_resources)  # type: ignore[unused-ignore]

    logger = app_host.logger()
    logger.debug("Debug mode enabled.")


@app.command()
def version() -> None:
    """Show the application version."""
    rich.print(__version__)


@app.command("config")
@wiring.inject
def show_config(
    config: Annotated[
        settings.Settings,
        typer.Argument(hidden=True, expose_value=False, parser=lambda _: _),
    ] = wiring.Provide[host.AppHost.app_settings]
) -> None:
    """Show the application configuration."""
    rich.print(config.model_dump)


@app.command()
@wiring.inject
def clean(
    data_dir: Annotated[
        Path,
        typer.Argument(hidden=True, expose_value=False, parser=lambda _: _),
    ] = wiring.Provide[host.AppHost.app_settings.provided.data_path]
) -> None:
    """Clean the application data directory."""

    shutil.rmtree(data_dir, ignore_errors=True)
    data_dir.mkdir(parents=True, exist_ok=True)
    rich.print(f"Cleaned data directory: {data_dir}")
