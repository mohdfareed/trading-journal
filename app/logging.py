"""Logging setup module."""

__all__ = [
    "Logger",
    "app_console",
    "err_console",
    "LoggingFactory",
    "LoggingService",
]

import logging
from logging import Logger
from logging.handlers import RotatingFileHandler
from pathlib import Path

from dependency_injector import containers, providers
from rich.console import Console
from rich.logging import RichHandler
from rich.text import Text

app_console = Console()
"""The application console."""
err_console = Console(stderr=True)
"""The application error console."""

logging.captureWarnings(True)
logging.getLogger().setLevel(logging.NOTSET)

Handler = list[logging.Handler]


def create_logger(
    *logging_handlers: list[logging.Handler],
    source: type | str | None = None,
    parent: Logger | None = None,
) -> logging.Logger:
    """Create a new logger."""
    handlers = [handler for handlers in logging_handlers for handler in handlers]
    source = (
        source.__name__
        if isinstance(source, type)
        else source if isinstance(source, str) else None
    )

    if not parent:
        logger = logging.getLogger(source)
        logger.handlers = handlers
    elif not source:
        logger = parent
    else:
        logger = parent.getChild(source)
        logger.handlers += handlers
    return logger


def console() -> Handler:
    """Console logging handler."""

    # stdout logger
    stdout = RichHandler(console=app_console, markup=True, show_time=False)
    stdout.setFormatter(logging.Formatter(r"%(message)s [black][%(name)s][/]"))
    stdout.setLevel(logging.INFO)
    stdout.addFilter(lambda msg: msg.levelno < logging.ERROR)

    # stderr logger
    stderr = RichHandler(console=err_console, markup=True, show_time=False)
    stdout.setFormatter(logging.Formatter(r"%(message)s [black][%(name)s][/]"))
    stderr.setLevel(logging.ERROR)

    return [stdout, stderr]


def debug(debug_mode: bool) -> Handler:
    """Debug logging handler."""

    debug_handler = RichHandler(console=app_console, markup=True, show_time=False)
    debug_handler.setFormatter(logging.Formatter(r"[black]%(message)s [%(name)s][/]"))
    debug_handler.setLevel(logging.DEBUG)
    debug_handler.addFilter(lambda msg: debug_mode and msg.levelno < logging.INFO)
    return [debug_handler]


def file(data_path: Path, name: type | str) -> Handler:
    """File logging handler."""
    if not data_path:
        return []

    class _StripMarkupFilter(logging.Filter):
        def filter(self, record: logging.LogRecord) -> bool:
            if hasattr(record, "msg") and isinstance(record.msg, str):
                record.msg = Text.from_markup(record.msg).plain
            return True  # filter rich markup from file logs

    name = name.__name__ if isinstance(name, type) else name
    log_file = data_path / f"{name}.log"
    file_handler = RotatingFileHandler(log_file, maxBytes=2**20, backupCount=3)
    file_handler.addFilter(_StripMarkupFilter())
    file_handler.setLevel(logging.NOTSET)
    file_handler.setFormatter(
        logging.Formatter(
            r"[%(asctime)s.%(msecs)03d] %(levelname)-8s "
            r"%(message)s [%(filename)s:%(lineno)d]",
            datefmt=r"%Y-%m-%d %H:%M:%S",
        )
    )
    return [file_handler]


class LoggingFactory(providers.Factory[Logger]):
    """Logging factory."""

    def __init__(
        self,
        *logging_handlers: providers.Provider[Handler],
        source: providers.Provider[str] | str | None = None,
        parent: providers.Provider[Logger] | Logger | None = None,
    ) -> None:
        super().__init__(create_logger, *logging_handlers, source=source, parent=parent)


class LoggingService(containers.DeclarativeContainer):
    """Logging service."""

    app_name = providers.Dependency(instance_of=str)
    # debug_mode = providers.Dependency(instance_of=providers.Provider[bool])
    debug_mode = providers.Dependency(instance_of=bool)
    log_dir = providers.Dependency(instance_of=Path)

    console_handler = providers.Factory(console)
    debug_handler = providers.Factory(debug, providers.Factory(debug_mode))
    file_handler = providers.Factory(file, log_dir, app_name)

    root_logger = LoggingFactory(console_handler, debug_handler)
    # app_logger = LoggingFactory(file_handler, source=app_name, parent=root_logger)
    app_logger = LoggingFactory(console_handler, debug_handler)
