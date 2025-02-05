"""OANDA application."""

__all__ = ["app", "oanda_host"]

import typer

from .host import oanda_host
from .settings import oanda_settings

app = typer.Typer(
    name=oanda_settings.APP_NAME,
    context_settings={"help_option_names": ["-h", "--help"]},
    add_completion=False,
)
oanda_host.register(app)


@app.callback()
def main(ctx: typer.Context) -> None:
    """The OANDA application."""
    oanda_host.start()
    ctx.call_on_close(oanda_host.stop)

    logger = oanda_host.logger
    logger.debug(f"Configuration:\n{oanda_settings.model_dump_json(indent=2)}")
