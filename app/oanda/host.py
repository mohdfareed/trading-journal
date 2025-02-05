"""OANDA application host."""

__all__ = ["oanda_host"]

import time

import rich
import typer

from app import core

from . import __name__, api

oanda_host: "OANDAHost"


class OANDAHost(core.Host):

    def register(self, app: typer.Typer) -> None:
        app.command()(self.run)
        app.command()(self.summary)
        super().register(app)

    def run(self) -> None:
        """Run the OANDA service."""
        self.validate()
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

    def summary(self) -> None:
        """Show the OANDA account summary."""
        self.validate()
        account = api.get_account()
        self.logger.debug(
            f"Retrieved account: {account.model_dump_json(indent=2)}"
        )
        rich.print(account)


oanda_host = OANDAHost(__name__.split(".")[-1])
