"""Trading journal models."""

from datetime import datetime, timedelta
from enum import Enum
from typing import Protocol, Sequence

from pydantic_extra_types.currency_code import Currency


class Broker(Protocol):
    """Trading brokerage interface."""

    def get_account(self) -> "Account":
        """Returns the account information."""
        ...

    def get_trades(self) -> Sequence["Trade"]:
        """Returns the account trades."""
        ...

    def get_orders(self) -> Sequence["Trade"]:
        """Returns the account orders (non-filled trades)."""
        ...


class TradeDirection(Enum):
    LONG = "long"
    SHORT = "short"


class Indicators(Protocol):
    ema: float
    stochastic: float
    rsi: float
    macd: float


class TradeEntry(Protocol):
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


class TradeExit(Protocol):
    trade_id: str
    exit_timestamp: datetime
    exit_price: float
    fees: float = 0.0


class Trade(Protocol):
    entry: TradeEntry
    exit: TradeExit | None = None


class Account(Protocol):
    id: str

    currency: Currency
    commission: float

    balance: float
    realized_pl: float
    unrealized_pl: float

    margin_rate: float
    margin_used: float
    margin_available: float
