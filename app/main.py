"""Main module for the Typer application CLI."""

__all__ = ["app"]

import sys
from typing import Annotated

import typer

from app import core, journal

from .host import app_host
from .settings import app_settings

app = typer.Typer(
    name=core.global_settings.APP_NAME,
    context_settings={"help_option_names": ["-h", "--help"]},
    add_completion=False,
)
app_host.register(app)
app.add_typer(journal.app)


@app.callback()
def main(
    ctx: typer.Context,
    env: Annotated[
        core.Environment,
        typer.Option("--env", help="The application deployment environment."),
    ] = core.global_settings.APP_ENV,
    debug_mode: Annotated[
        bool,
        typer.Option(
            "--debug", "-d", help="Log debug messages to the console."
        ),
    ] = False,
) -> None:
    """Trading Journal CLI."""
    app_host.start(env, debug_mode)
    ctx.call_on_close(app_host.stop)

    logger = app_host.logger
    command = " ".join(sys.argv[1:])
    logger.debug(f"Executing: [purple]{app_settings.APP_NAME} {command}[/]")
