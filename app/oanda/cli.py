"""OANDA application."""

__all__ = ["app"]


import time

import rich
import typer
from dependency_injector import wiring

from app import host, logging, settings

from .host import OANDAHost, create_oanda_host
from .settings import OANDASettings

app = typer.Typer(
    name="oanda",
    context_settings={"help_option_names": ["-h", "--help"]},
    add_completion=False,
)


@app.callback()
@wiring.inject
def main(
    ctx: typer.Context,
    app_settings: settings.AppSettings = host.Host.resolve_cli(
        host.AppHost.app_settings
    ),
) -> None:
    """The OANDA application."""

    app_host = create_oanda_host(app, app_settings)
    app_host.init_resources()  # type: ignore
    ctx.call_on_close(app_host.shutdown_resources)  # type: ignore

    oanda_settings = app_host.oanda_settings()
    logger = app_host.logger()
    logger.debug(f"Configuration:\n{oanda_settings.model_dump_json(indent=2)}")


@app.command("config")
@wiring.inject
def show_config(
    config: OANDASettings = host.Host.resolve_cli(OANDAHost.oanda_settings),
) -> None:
    """Show the application configuration."""
    rich.print_json(config.model_dump_json())


@app.command()
@wiring.inject
def start(logger: logging.Logger = host.Host.resolve_cli(OANDAHost.logger)) -> None:
    """Start the application."""
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
