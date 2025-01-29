"""Logging setup module."""

__all__ = [
    "Logger",
    "getLogger",
    "app_console",
    "err_console",
    "setup_logging",
    "setup_file_logging",
]

import logging
import time
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


def setup_logging(logger: Logger, debug: bool) -> Logger:
    """Set up a logger with console handlers."""
    logger.setLevel(logging.NOTSET)
    logger.handlers.clear()
    logger.handlers += [stdout_handler(), stderr_handler()] + (
        [debug_handler()] if debug else []
    )
    return logger


def setup_file_logging(logger: Logger, log_dir: Path) -> None:
    """Add a file handler to the logger."""
    log_dir.mkdir(parents=True, exist_ok=True)
    log_file = log_dir / f"{logger.name}.log"

    for handler in logger.handlers:
        if handler.name == str(log_file):
            return  # logger already has handler

    log_file.touch(exist_ok=True)
    log_file.write_text(
        f"[{time.asctime()}]" + "=" * (80 - len(f"[{time.asctime()}]"))
    )  # clear log file

    logger.addHandler(file_handler(log_file))
    logger.debug("Logging to file: %s", log_file)


def stdout_handler() -> logging.Handler:
    stdout = RichHandler(
        console=app_console, markup=True, show_time=False, show_path=False
    )
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
                record.msg = Text.from_markup(record.msg).plain
            return True  # filter rich markup from file logs

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
