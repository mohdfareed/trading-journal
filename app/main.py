"""Main module for the Typer application CLI."""

__all__ = ["app"]


import logging
import shutil
import sys
from typing import Annotated

import click
import rich
import typer

from app import models, oanda, utils
from app.settings import app_settings

logger = logging.getLogger(__name__.split(".")[0])
lifecycle = models.Lifecycle()

app = typer.Typer(
    name=app_settings.APP_NAME,
    context_settings={"help_option_names": ["-h", "--help"]},
    add_completion=False,
)
app.add_typer(oanda.app)


@app.callback()
def main(
    ctx: typer.Context,
    debug_mode: Annotated[
        bool,
        typer.Option(
            "--debug", "-d", help="Log debug messages to the console."
        ),
    ] = False,
) -> None:
    """Trading Journal CLI."""
    utils.setup_logging()
    utils.enable_debugging() if debug_mode else None
    utils.enable_file_logging(logger.name)

    logger.debug(f"Configuration:\n{app_settings.model_dump_json(indent=2)}")
    logger.debug(f"Executing: [italic]{' '.join(sys.argv)}[/]")

    lifecycle.startup.send()
    ctx.call_on_close(lambda: lifecycle.shutdown.send)


@app.command()
def version() -> None:
    """Show the application version."""
    rich.print(app_settings.VERSION)


@app.command("config")
def show_config() -> None:
    """Show the application configuration."""
    rich.print_json(app_settings.model_dump_json())


@app.command()
def clean() -> None:
    """Clean the application data directory."""
    utils.disable_file_logging(logger.name)
    shutil.rmtree(app_settings.data_path, ignore_errors=True)
    app_settings.data_path.mkdir(parents=True, exist_ok=True)
    rich.print(f"Cleaned data directory: {app_settings.data_path}")


@app.command("logs")
def view_logs(
    log_name: str | None = typer.Argument(
        None, metavar="NAME", help="The log file to view, without suffix."
    ),
    all: bool = typer.Option(
        False, help="View all log contents or only the last run."
    ),
) -> None:
    """View the application logs."""
    if not (logs := sorted(app_settings.logging_path.glob("*.log"))):
        typer.echo("No logs found.")
        raise typer.Exit(1)

    if not log_name:  # prompt the user for a log file
        choices = click.Choice([log.stem for log in logs])
        log_name = str(typer.prompt("Select a file", type=choices))

    log_file = (app_settings.logging_path / log_name).with_suffix(".log")
    if not log_file.exists():
        typer.echo(f"Log file not found: {log_file}")
        raise typer.Exit(1)

    log_contents = log_file.read_text()
    if not all:
        log_contents = log_contents.split("=" * 54)[-1]
    rich.print(log_contents.strip())
