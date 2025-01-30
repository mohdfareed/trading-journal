"""OANDA application."""

__all__ = ["OANDAHost", "create_oanda_host"]


import typer
from dependency_injector import containers, providers

from app import host, logging, settings

from .settings import OANDASettings


class OANDAHost(host.Host):
    """OANDA application host."""

    wiring_config = containers.WiringConfiguration(modules=["app.oanda"])
    app = providers.Dependency(instance_of=typer.Typer)

    app_settings = providers.Dependency(instance_of=settings.AppSettings)
    oanda_settings = providers.Singleton(OANDASettings)

    logger = providers.Factory(
        logging.setup_logging,
        logger=logging.getLogger(__name__.replace("app.", "").split(".")[0]),
        debug=app_settings.provided.DEBUG,
        logging_path=app_settings.provided.logging_path,
    )

    _log_file_header = providers.Resource(logging.stamp_file, logger=logger)
    _settings_persistence = providers.Resource[None](
        OANDASettings.resource, oanda_settings, app_settings.provided.data_path
    )
    _events = providers.Resource(host.AppLifecycle.resource, app)


def create_oanda_host(
    app: typer.Typer, app_settings: settings.AppSettings
) -> OANDAHost:
    """Create the OANDA application host."""
    return OANDAHost(app=app, app_settings=app_settings)
