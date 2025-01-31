"""Application models."""

from enum import Enum


class AppLifecycle(str, Enum):
    """Application lifecycle event."""

    STARTUP = "app:start"
    """Application startup event."""
    SHUTDOWN = "app:stop"
    """Application shutdown event."""
