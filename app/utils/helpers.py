"""Application utilities."""

__all__ = ["SingletonMeta", "pascal_to_snake"]

import re
from typing import Any

from rich.console import Console

app_console = Console()
"""The application console."""
err_console = Console(stderr=True)
"""The application error console."""


class SingletonMeta(type):
    """A metaclass for creating singleton classes."""

    _instances: dict[type, Any] = {}

    def __call__(cls, *args: Any, **kwargs: Any) -> Any:
        if cls not in cls._instances:
            cls._instances[cls] = super().__call__(*args, **kwargs)
        return cls._instances[cls]  # type: ignore


def pascal_to_snake(name: str) -> str:
    """Convert `PascalCase` to `snake_case`."""
    s1 = re.sub(r"([^_])([A-Z][a-z]+)", r"\1_\2", name)
    snake_case = re.sub(r"([a-z0-9])([A-Z])", r"\1_\2", s1).lower()
    return snake_case
