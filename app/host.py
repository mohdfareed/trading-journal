"""Application host."""

__all__ = ["app_host"]


import shutil

import rich

from app import __name__, core, settings

app_host: "AppHost"
"""Application host."""


class AppHost(core.Host):
    def start(self, env: core.Environment | None, debug: bool = False) -> None:
        core.global_settings.APP_ENV = env or core.global_settings.APP_ENV
        settings.app_settings.DEBUG_MODE = (
            debug or settings.app_settings.DEBUG_MODE
        )
        core.setup_logging(settings.app_settings.DEBUG_MODE)
        return super().start()

    def clean(self) -> None:
        """Clean the application data directory."""
        for handler in core.logging.getLogger().handlers:
            if isinstance(handler, core.logging.FileHandler):
                handler.close()
        shutil.rmtree(settings.app_settings.data_path, ignore_errors=True)
        settings.app_settings.data_path.mkdir(parents=True, exist_ok=True)
        rich.print(
            f"Cleaned data directory: {settings.app_settings.data_path}"
        )

    def version(self) -> None:
        """Show the application version."""
        rich.print(settings.app_settings.VERSION)


app_host = AppHost()
