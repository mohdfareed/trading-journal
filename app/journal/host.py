"""OANDA application host."""

__all__ = ["journal_host"]

import rich
import typer

from app import core

from . import __name__
from .models import Broker
from .settings import journal_settings

journal_host: "JournalHost"


class JournalHost(core.Host):
    app_settings = journal_settings

    @property
    def broker(self) -> Broker:
        """Get the brokerage."""
        return journal_settings.BROKERAGE.resolve()

    def register(self, app: typer.Typer) -> None:
        app.command()(self.account)
        app.command()(self.trades)
        app.command()(journal_settings.config)
        super().register(app)

    def account(self) -> None:
        """Show the OANDA account information."""
        self.validate()
        account = self.broker.get_account()
        self.logger.debug(
            f"Retrieved account: {account.model_dump_json(indent=2)}"
        )
        rich.print(account)

    def trades(self) -> None:
        """Show the account trades."""
        self.validate()
        trades = self.broker.get_trades()
        self.logger.debug(
            f"Retrieved trades: {trades.model_dump_json(indent=2)}"
        )
        rich.print(trades)


journal_host = JournalHost(__name__.split(".")[-1])
