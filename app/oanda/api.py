"""OANDA API package."""

import requests

from . import models
from .settings import oanda_settings


def get_account() -> models.Account:
    """Retrieves the account information from OANDA."""
    response = requests.get(
        models.Account.path, headers=oanda_settings.request_headers
    )
    response.raise_for_status()
    return models.Account.model_validate(response.json()["account"])
