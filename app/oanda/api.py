"""OANDA API package."""

from typing import Sequence

import requests

from app import journal

from . import models
from .settings import oanda_settings


def get_account() -> journal.Account:
    """Retrieves the account information."""
    response = requests.get(
        models.Account.path(), headers=oanda_settings.request_headers
    )
    response.raise_for_status()
    return models.Account.model_validate(response.json()["account"])


def get_trades() -> Sequence[journal.Trade]:
    """Retrieves the account trades."""
    response = requests.get(
        models.Trades.path(), headers=oanda_settings.request_headers
    )
    response.raise_for_status()
    return models.Trades.model_validate(response.json()).trades


def get_orders() -> Sequence[journal.Trade]:
    """Retrieves the account orders (unfilled trades)."""
    response = requests.get(
        models.Account.path(), headers=oanda_settings.request_headers
    )
    response.raise_for_status()
    return models.Orders.model_validate(response.json()).orders
