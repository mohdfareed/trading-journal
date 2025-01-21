"""Main module for the Typer application CLI."""

__all__ = ["app"]

import platform
from typing import Annotated

import typer
import typer.completion

from app import APP_NAME, __version__, logging

COMPLETION_APP = "completion"

app = typer.Typer(
    name=APP_NAME,
    context_settings={"help_option_names": ["-h", "--help"]},
)


@app.callback()
def main(
    debug_mode: Annotated[
        bool,
        typer.Option("--debug", "-d", help="Log debug messages to the console."),
    ] = False,
) -> None:
    """Machine setup CLI."""

    # initialize logging
    logging.setup_logging(debug_mode)
    platform_info = f"[blue]{platform.platform().replace('-', '[black]|[/]')}[/]"

    # debug information
    logging.LOGGER.debug("App version: %s", __version__)
    logging.LOGGER.debug("Python version: %s", platform.python_version())
    logging.LOGGER.debug("Platform: %s", platform_info)
    logging.LOGGER.debug("Debug mode: %s", debug_mode)
    logging.LOGGER.debug("Log file: %s", logging.log_file_path)


@app.command()
def test() -> None:
    """Test the application."""
    logging.LOGGER.info("Testing the application.")
    logging.LOGGER.debug("Debugging the application.")
