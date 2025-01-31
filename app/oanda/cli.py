"""OANDA application."""

__all__ = ["app"]


import logging
import time

import rich
import typer

from app import utils

from .settings import oanda_settings

logger = logging.getLogger(oanda_settings.APP_NAME)
app = typer.Typer(
    name=oanda_settings.APP_NAME,
    context_settings={"help_option_names": ["-h", "--help"]},
    add_completion=False,
)


@app.callback()
def main() -> None:
    """The OANDA application."""
    utils.enable_file_logging(logger.name)
    logger.debug(f"Configuration:\n{oanda_settings.model_dump_json(indent=2)}")


@app.command("config")
def show_config() -> None:
    """Show the application configuration."""
    rich.print_json(oanda_settings.model_dump_json())


@app.command()
def start() -> None:
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
