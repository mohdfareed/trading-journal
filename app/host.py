"""Application host."""

__all__ = ["app_host"]


import shutil

import rich
import rich.prompt

from app import core

from . import __name__
from .settings import app_settings

app_host: "AppHost"
"""Application host."""


class AppHost(core.Host):
    def start(self, env: core.Environment | None, debug: bool = False) -> None:
        core.global_settings.APP_ENV = env or core.global_settings.APP_ENV
        app_settings.DEBUG_MODE = debug or app_settings.DEBUG_MODE
        core.setup_logging(app_settings.DEBUG_MODE)
        return super().start()

    def clean(self) -> None:
        """Clean the application data directory."""
        rich.print(
            f"Cleaning data directory: {app_settings.data_path}",
        )
        rich.print(
            "[bold yellow]This will delete all data and configurations.[/]"
        )
        rich.prompt.Confirm.ask(
            "Are you sure you want to continue?", default=True
        )

        core.close_files()
        shutil.rmtree(app_settings.data_path, ignore_errors=True)
        app_settings.data_path.mkdir(parents=True, exist_ok=True)
        rich.print(f"Cleaned data directory: {app_settings.data_path}")

    def version(self) -> None:
        """Show the application version."""
        rich.print(app_settings.VERSION)


app_host = AppHost(__name__)
