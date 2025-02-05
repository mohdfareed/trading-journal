"""OANDA API models."""

from typing import ClassVar

from pydantic import BaseModel, ConfigDict, Field
from pydantic_extra_types.currency_code import Currency

from .settings import oanda_settings


class Account(BaseModel):

    model_config = ConfigDict(extra="ignore")
    path: ClassVar[str] = (
        f"{oanda_settings.base_url}/accounts/{oanda_settings.ACCOUNT_ID}"
    )

    id: str = Field()
    name: str = Field(alias="alias")

    currency: Currency = Field()
    commission: float = Field()

    balance: float = Field()
    net_balance: float = Field(alias="NAV")

    realized_pl: float = Field(alias="pl")
    unrealized_pl: float = Field(alias="unrealizedPL")

    margin_used: float = Field(alias="marginUsed")
    margin_available: float = Field(alias="marginAvailable")

    open_trade_count: int = Field(alias="openTradeCount")
    open_position_count: int = Field(alias="openPositionCount")
    pending_order_count: int = Field(alias="pendingOrderCount")
