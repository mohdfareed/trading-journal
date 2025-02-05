"""OANDA application host."""

__all__ = ["oanda_host"]

import rich
import typer

from app import core

from . import __name__, api
from .settings import oanda_settings

oanda_host: "OANDAHost"


class OANDAHost(core.Host):

    def register(self, app: typer.Typer) -> None:
        app.command()(self.account)
        app.command()(oanda_settings.config)
        super().register(app)

    def account(self) -> None:
        """Show the OANDA account information."""
        self.validate()
        account = api.get_account()
        self.logger.debug(
            f"Retrieved account: {account.model_dump_json(indent=2)}"
        )
        rich.print(account)


oanda_host = OANDAHost(__name__.split(".")[-1])
