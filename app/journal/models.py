"""Trading journal models."""

__all__ = [
    "Broker",
    "TradeDirection",
    "Indicators",
    "TradeEntry",
    "TradeExit",
    "Trade",
    "Trades",
    "Account",
]

from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Protocol

from pydantic_extra_types.currency_code import Currency


class BaseModel(Protocol):
    @classmethod
    def model_validate(cls, *args: Any, **kwargs: Any) -> "BaseModel": ...
    def model_dump_json(self, *args: Any, **kwargs: Any) -> str: ...


class Broker(Protocol):
    """Trading brokerage interface."""

    def get_account(self) -> "Account":
        """Returns the account information."""
        ...

    def get_trades(self) -> "Trades":
        """Returns the account trades."""
        ...


class TradeDirection(Enum):
    LONG = "long"
    SHORT = "short"


class Indicators(BaseModel):
    ema: float
    stochastic: float
    rsi: float
    macd: float


class TradeEntry(BaseModel):
    trade_id: str
    symbol: str
    entry_timestamp: datetime
    entry_price: float
    quantity: float
    direction: TradeDirection

    stop_loss: float | None
    take_profit: float | None
    indicators: dict[timedelta, Indicators]
    is_filled: bool = False  # for limit/stop orders


class TradeExit(BaseModel):
    trade_id: str
    exit_timestamp: datetime
    exit_price: float
    fees: float = 0.0


class Trade(BaseModel):
    entry: TradeEntry
    exit: TradeExit | None = None


class Trades(BaseModel):
    trades: list[Trade]


class Account(BaseModel):
    id: str

    currency: Currency
    commission: float

    balance: float
    realized_pl: float
    unrealized_pl: float

    margin_rate: float
    margin_used: float
    margin_available: float
