"""OANDA API package."""

import requests
import v20  # type: ignore

from . import models
from .settings import oanda_settings


def get_account() -> models.Account:
    """Retrieves the account information from OANDA."""
    url = f"{oanda_settings.base_url}/accounts/{oanda_settings.ACCOUNT_ID}"
    response = requests.get(url, headers=oanda_settings.request_headers)
    response.raise_for_status()
    return models.Account.model_validate(response.json()["account"])
