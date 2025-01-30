"""Logging setup module."""

__all__ = [
    "Logger",
    "getLogger",
    "app_console",
    "err_console",
    "setup_logging",
    "stamp_file",
]

import datetime
import logging
from logging import Logger, getLogger
from logging.handlers import RotatingFileHandler
from pathlib import Path

from rich.console import Console
from rich.logging import RichHandler
from rich.text import Text

app_console = Console()
"""The application console."""
err_console = Console(stderr=True)
"""The application error console."""

logging.captureWarnings(True)
logging.getLogger().setLevel(logging.NOTSET)


def setup_logging(logger: Logger, debug: bool, logging_path: Path | None) -> Logger:
    """Set up a logger with console and file handlers."""
    logger.setLevel(logging.NOTSET)
    logger.handlers.clear()

    logger.handlers = (
        [stdout_handler(), stderr_handler()]
        + ([debug_handler()] if debug else [])
        + ([file_handler(logging_path / f"{logger.name}.log")] if logging_path else [])
    )
    return logger


def add_file_logger(logger: Logger, logging_path: Path) -> Logger:
    """Add a file handler to the logger."""
    for handler in logger.handlers:
        if isinstance(handler, RotatingFileHandler):
            logger.removeHandler(handler)
            break

    logger.addHandler(file_handler(logging_path / f"{logger.name}.log"))
    return logger


def stamp_file(logger: logging.Logger) -> None:
    """Stamp the log file with a header."""
    log_file = None
    for handler in logger.handlers:
        if isinstance(handler, RotatingFileHandler):
            log_file = Path(handler.baseFilename)
            break

    if log_file is None:
        return

    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
    file_header = f"[{timestamp}]" + "=" * (80 - 2 - len(timestamp) - 1)
    with open(log_file, "a") as file:
        file.write(file_header + "\n")


def stdout_handler() -> logging.Handler:
    stdout = RichHandler(console=app_console, markup=True, show_time=False)
    stdout.setLevel(logging.INFO)
    stdout.addFilter(lambda msg: msg.levelno < logging.ERROR)  # info, warning
    stdout.setFormatter(logging.Formatter(r"%(message)s [black][%(name)s][/]"))
    return stdout


def stderr_handler() -> logging.Handler:
    stderr = RichHandler(console=err_console, markup=True, show_time=False)
    stderr.setFormatter(logging.Formatter(r"[black]%(message)s [%(name)s][/]"))
    stderr.setLevel(logging.ERROR)  # error, critical
    return stderr


def debug_handler() -> logging.Handler:
    debug = RichHandler(console=app_console, markup=True, show_time=False)
    debug.addFilter(lambda msg: msg.levelno < logging.INFO)
    debug.setLevel(logging.DEBUG)  # debug
    debug.setFormatter(logging.Formatter(r"[black]%(message)s [%(name)s][/]"))
    return debug


def file_handler(log_file: Path) -> logging.Handler:
    class StripMarkupFilter(logging.Filter):
        def filter(self, record: logging.LogRecord) -> bool:
            if hasattr(record, "msg") and isinstance(record.msg, str):
                record.msg = Text.from_markup(Text.from_ansi(record.msg).plain).plain
            return True  # filter rich markup from file logs

    log_file.parent.mkdir(parents=True, exist_ok=True)
    file = RotatingFileHandler(log_file, maxBytes=2**10, backupCount=0, delay=True)
    file.addFilter(StripMarkupFilter())
    file.setLevel(logging.NOTSET)
    file.setFormatter(
        logging.Formatter(
            r"[%(asctime)s.%(msecs)03d] %(levelname)-8s "
            r"%(message)s [%(filename)s:%(lineno)d]",
            datefmt=r"%Y-%m-%d %H:%M:%S",
        )
    )

    file.delay = True
    file.set_name(str(log_file))
    return file
