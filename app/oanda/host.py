"""OANDA application."""

__all__ = ["OANDAHost", "create_oanda_host"]


from pathlib import Path

from dependency_injector import containers, providers

from app import logging

from .config import OANDAConfig


class OANDAHost(containers.DeclarativeContainer):
    """OANDA application host."""

    wiring_config = containers.WiringConfiguration(modules=["app.main"])
    data_path = providers.Dependency(instance_of=Path)
    log_dir = providers.Dependency(instance_of=Path)

    settings = providers.Resource(OANDAConfig().resource, data_path)
    logger = logging.getLogger(__name__)
    file_logging = providers.Resource[None](
        logging.setup_file_logging, logger=logger, log_dir=log_dir
    )


def create_oanda_host(data_path: Path, log_dir: Path) -> OANDAHost:
    """Create the OANDA application host."""
    return OANDAHost(data_path=data_path, log_dir=log_dir)
