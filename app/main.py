"""Main module for the Typer application CLI."""

__all__ = ["app"]

import shutil
import time
from typing import Annotated

import typer
import typer.completion
from pydantic_core import ValidationError

from app import APP_NAME, __version__, config, logging

app = typer.Typer(
    name=APP_NAME,
    context_settings={"help_option_names": ["-h", "--help"]},
    add_completion=False,
)
app.command(name="config")(config.edit_config)


@app.callback()
def main(
    debug_mode: Annotated[
        bool,
        typer.Option("--debug", "-d", help="Log debug messages to the console."),
    ] = False,
) -> None:
    """Trading Journal CLI."""
    logging.setup_logging(debug_mode)

    configuration = config.AppConfig()
    try:
        configuration = config.AppConfig()
    except ValidationError as e:
        logging.LOGGER.error(e)
        raise typer.Exit(1)

    logging.LOGGER.debug("App version: %s", __version__)
    logging.LOGGER.debug("Debug mode: %s", debug_mode)
    logging.LOGGER.debug("Log file: %s", logging.log_file_path)
    logging.LOGGER.debug("Configuration: %s", configuration.model_dump_json(indent=2))


@app.command()
def test() -> None:
    """Test the application."""


@app.command()
def clean() -> None:
    """Clean the application data."""
    logging.LOGGER.info("Cleaning up...")
    shutil.rmtree(typer.get_app_dir(APP_NAME), ignore_errors=True)


@app.command()
def start() -> None:
    """Start the application."""
    logging.LOGGER.info("Starting...")
    logging.LOGGER.warning("Press Ctrl+C to exit.")

    try:  # Keep the application running
        while True:
            time.sleep(1)
            logging.LOGGER.debug("Running...")
    except KeyboardInterrupt as e:
        print()
        logging.LOGGER.info("Exiting...")
        raise typer.Exit() from e
