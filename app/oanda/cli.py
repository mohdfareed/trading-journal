"""OANDA application."""

__all__ = ["app", "oanda_host"]

import time

import typer

from app import core

from . import __name__
from .settings import oanda_settings

app = typer.Typer(
    name=oanda_settings.APP_NAME,
    context_settings={"help_option_names": ["-h", "--help"]},
    add_completion=False,
)
oanda_host = core.Host(__name__.split(".")[-1])
app.command()(oanda_settings.config)
app.command()(oanda_host.logs)


@app.callback()
def main(ctx: typer.Context) -> None:
    """The OANDA application."""
    oanda_host.start()
    ctx.call_on_close(oanda_host.stop)

    logger = oanda_host.logger
    logger.debug(f"Configuration:\n{oanda_settings.model_dump_json(indent=2)}")


@app.command()
def start() -> None:
    """Start the application."""
    logger = oanda_host.logger
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
