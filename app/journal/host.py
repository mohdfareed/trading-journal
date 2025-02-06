"""OANDA application host."""

__all__ = ["journal_host"]

import rich
import typer
from pydantic import BaseModel

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
        app.command()(self.orders)
        app.command()(journal_settings.config)
        super().register(app)

    def account(self) -> None:
        """Show the OANDA account information."""
        self.validate()
        account = self.broker.get_account()

        model = BaseModel.model_validate(account)
        self.logger.debug(
            f"Retrieved account: {model.model_dump_json(indent=2)}"
        )
        rich.print(account)

    def trades(self) -> None:
        """Show the account trades."""
        self.validate()
        trades = self.broker.get_trades()

        model = BaseModel.model_validate(trades)
        self.logger.debug(
            f"Retrieved trades: {model.model_dump_json(indent=2)}"
        )
        rich.print(trades)

    def orders(self) -> None:
        """Show the account orders."""
        self.validate()
        orders = self.broker.get_orders()

        model = BaseModel.model_validate(orders)
        self.logger.debug(
            f"Retrieved orders: {model.model_dump_json(indent=2)}"
        )
        rich.print(orders)


journal_host = JournalHost(__name__.split(".")[-1])
