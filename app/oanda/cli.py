"""OANDA application."""

__all__ = ["app"]


import time
from pathlib import Path

import typer
from dependency_injector import wiring

from app import logging
from app.host import AppHost

from .host import OANDAHost, create_oanda_host

app = typer.Typer(
    name="oanda",
    context_settings={"help_option_names": ["-h", "--help"]},
    add_completion=False,
)


@app.callback()
@wiring.inject
def main(
    ctx: typer.Context,
    data_path: Path = wiring.Provide[AppHost.app_settings.provided.data_path],
    log_dir: Path = wiring.Provide[AppHost.app_settings.provided.log_dir],
) -> None:
    """The OANDA application."""
    app_host = create_oanda_host(data_path, log_dir)
    app_host.init_resources()  # type: ignore[unused-ignore]
    ctx.call_on_close(app_host.shutdown_resources)  # type: ignore[unused-ignore]
    app_host.logger.debug("OANDA application started.")


@wiring.inject
def start(logger: logging.Logger = wiring.Provide[OANDAHost.logger]) -> None:
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
