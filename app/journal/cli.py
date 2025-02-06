"""Journal application."""

__all__ = ["app"]

import typer

from .host import journal_host
from .settings import journal_settings

app = typer.Typer(
    name=journal_settings.APP_NAME,
    context_settings={"help_option_names": ["-h", "--help"]},
    add_completion=False,
)
journal_host.register(app)


@app.callback()
def main(ctx: typer.Context) -> None:
    """The journal automation application."""
    journal_host.start()
    ctx.call_on_close(journal_host.stop)
