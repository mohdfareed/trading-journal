"""OANDA API models."""

__all__ = ["Account", "Trade", "Trades", "Order", "Orders"]

from pydantic import BaseModel, ConfigDict, Field
from pydantic_extra_types.currency_code import Currency

from .settings import oanda_settings


class Account(BaseModel):
    model_config = ConfigDict(extra="allow")

    id: str = Field()
    name: str = Field(alias="alias")
    last_transaction_id: str = Field(alias="lastTransactionID")

    currency: Currency = Field()
    commission: float = Field()

    balance: float = Field()
    net_balance: float = Field(alias="NAV")

    realized_pl: float = Field(alias="pl")
    unrealized_pl: float = Field(alias="unrealizedPL")

    margin_used: float = Field(alias="marginUsed")
    margin_available: float = Field(alias="marginAvailable")
    margin_rate: float = Field(alias="marginRate")

    open_trade_count: int = Field(alias="openTradeCount")
    open_position_count: int = Field(alias="openPositionCount")
    pending_order_count: int = Field(alias="pendingOrderCount")

    @classmethod
    def path(cls) -> str:
        return (
            f"{oanda_settings.base_url}/accounts/{oanda_settings.ACCOUNT_ID}"
        )


class Trade(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field()

    @classmethod
    def path(cls, id: str) -> str:
        return f"{Account.path()}/trades/{id}"


class Trades(BaseModel):
    model_config = ConfigDict(extra="allow")
    trades: list[Trade]

    @classmethod
    def path(cls) -> str:
        return f"{Account.path()}/trades"


class Order(BaseModel):
    model_config = ConfigDict(extra="allow")
    id: str = Field()

    @classmethod
    def path(cls, id: str) -> str:
        return f"{Account.path()}/orders/{id}"


class Orders(BaseModel):
    model_config = ConfigDict(extra="allow")
    orders: list[Order]

    @classmethod
    def path(cls) -> str:
        return f"{Account.path()}/orders"
