"""The trading journal application package."""

__all__ = ["APP_NAME", "__version__"]

from importlib.metadata import version

APP_NAME = "trading-journal"
__version__ = version(APP_NAME)
