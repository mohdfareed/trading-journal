"""OANDA application host."""

__all__ = ["oanda_host"]

import time

import typer

from app import core

from . import __name__

oanda_host: "OANDAHost"


class OANDAHost(core.Host):
    def run(self) -> None:
        """Run the OANDA service."""
        self.logger.info("Starting...")
        self.logger.warning("Press Ctrl+C to exit.")

        try:  # Keep the application running
            while True:
                time.sleep(1)
                self.logger.debug("Running...")
        except KeyboardInterrupt as e:
            print()
            self.logger.info("Exiting...")
            raise typer.Exit() from e


oanda_host = OANDAHost(__name__.split(".")[-1])
