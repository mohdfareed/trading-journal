"""Main module for the Typer application CLI."""

__all__ = ["app"]


import shutil
from pathlib import Path
from typing import Annotated

import rich
import rich.json
import rich.markup
import typer
import typer.completion
from dependency_injector import wiring

from app import APP_NAME, __version__, host, oanda, settings

app = typer.Typer(
    name=APP_NAME,
    context_settings={"help_option_names": ["-h", "--help"]},
    add_completion=False,
)
app.add_typer(oanda.app)


@app.callback()
def main(
    ctx: typer.Context,
    debug_mode: Annotated[
        bool,
        typer.Option("--debug", "-d", help="Log debug messages to the console."),
    ] = False,
) -> None:
    """Trading Journal CLI."""

    app_host = host.AppHost(app=app)
    app_host.init_resources()  # type: ignore
    ctx.call_on_close(app_host.shutdown_resources)  # type: ignore

    settings = app_host.app_settings()
    settings.DEBUG = debug_mode or settings.DEBUG

    logger = app_host.logger()
    logger.debug(f"Configuration:\n{settings.model_dump_json(indent=2)}")
    logger.debug(
        f"Executing: [italic]{ctx.command_path or ''} "
        f"{ctx.invoked_subcommand} {ctx.params or ''} {ctx.args or ''}[/]"
    )


@app.command()
@wiring.inject
def version() -> None:
    """Show the application version."""
    rich.print(__version__)


@app.command("config")
@wiring.inject
def show_config(
    config: settings.AppSettings = host.Host.resolve_cli(host.AppHost.app_settings),
) -> None:
    """Show the application configuration."""
    rich.print_json(config.model_dump_json())


@app.command()
@wiring.inject
def clean(
    data_dir: Path = host.Host.resolve_cli(
        host.AppHost.app_settings.provided.data_path
    ),
) -> None:
    """Clean the application data directory."""
    shutil.rmtree(data_dir, ignore_errors=True)
    data_dir.mkdir(parents=True, exist_ok=True)
    rich.print(f"Cleaned data directory: {data_dir}")
