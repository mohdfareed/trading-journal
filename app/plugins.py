"""CLI Plugin Manager for Typer Applications"""

import typer


class PluginService:
    """Simple plugin manager."""

    def __init__(self, main_app: typer.Typer) -> None:
        self.plugins: list[typer.Typer] = []
        self.main_app = main_app

    def register(self, app: typer.Typer) -> None:
        """Register all plugin apps as subcommands to the provided app."""
        self.main_app.add_typer(app)
