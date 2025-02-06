"""OANDA API package."""

import requests

from . import models
from .settings import oanda_settings


def get_account() -> models.Account:
    """Retrieves the account information."""
    response = requests.get(
        models.Account.path(), headers=oanda_settings.request_headers
    )
    response.raise_for_status()
    return models.Account.model_validate(response.json()["account"])


def get_trades() -> models.Trades:
    """Retrieves the account trades."""
    response = requests.get(
        models.Trades.path(), headers=oanda_settings.request_headers
    )
    response.raise_for_status()
    return models.Trades.model_validate(response.json())


def get_orders() -> models.Orders:
    """Retrieves the account orders (unfilled trades)."""
    response = requests.get(
        models.Account.path(), headers=oanda_settings.request_headers
    )
    response.raise_for_status()
    return models.Orders.model_validate(response.json())
