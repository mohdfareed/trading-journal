"""Logging module."""

__all__ = [
    "app_console",
    "err_console",
    "setup_logging",
    "enable_debugging",
    "disable_debugging",
    "enable_file_logging",
    "disable_file_logging",
    "stdout_handler",
    "stderr_handler",
    "debug_handler",
    "file_handler",
]

from datetime import datetime
from logging import *  # type: ignore
from logging.handlers import RotatingFileHandler
from pathlib import Path

from rich.console import Console
from rich.logging import RichHandler
from rich.text import Text

app_console = Console()
"""The application console."""
err_console = Console(stderr=True)
"""The application error console."""


def setup_logging() -> None:
    """Set up logging."""
    captureWarnings(True)
    getLogger().setLevel(NOTSET)
    getLogger().addHandler(stdout_handler())
    getLogger().addHandler(stderr_handler())


def enable_debugging() -> None:
    """Enable debugging mode."""
    getLogger().addHandler(debug_handler())
    getLogger().debug("Debugging enabled.")


def disable_debugging() -> None:
    """Disable debugging mode."""
    for handler in getLogger().handlers[:]:
        if handler.level == DEBUG:
            getLogger().removeHandler(handler)
            handler.close()
    getLogger().debug("Debugging disabled.")


def enable_file_logging(name: str) -> None:
    """Add a new file logger."""
    from app.settings import app_settings

    file_path = app_settings.logging_path / f"{name}.log"
    handler = file_handler(file_path)
    logger = getLogger(name)

    for handler in logger.handlers[:]:
        if isinstance(handler, FileHandler):
            logger.removeHandler(handler)
            handler.close()

    logger.addHandler(handler)
    logger.debug(f"File logging enabled for {name}.")


def disable_file_logging(name: str) -> None:
    """Remove file logger."""
    logger = getLogger(name)
    for handler in logger.handlers[:]:
        if isinstance(handler, FileHandler):
            logger.removeHandler(handler)
            handler.close()
    logger.debug(f"File logging disabled for {name}.")


# region: Handlers


def stdout_handler() -> Handler:
    stdout = RichHandler(console=app_console, markup=True, show_time=False)
    stdout.setLevel(INFO)
    stdout.addFilter(lambda msg: msg.levelno < ERROR)  # info, warning
    return stdout


def stderr_handler() -> Handler:
    stderr = RichHandler(console=err_console, markup=True, show_time=False)
    stderr.setFormatter(Formatter(r"[bold red]%(message)s[/]"))
    stderr.setLevel(ERROR)  # error, critical
    return stderr


def debug_handler() -> Handler:
    debug = RichHandler(console=app_console, markup=True, show_time=False)
    debug.addFilter(lambda msg: msg.levelno < INFO)
    debug.setLevel(DEBUG)  # debug
    debug.setFormatter(Formatter(r"[bright_black]%(message)s [%(name)s][/]"))
    return debug


def file_handler(log_file: Path) -> Handler:
    class StripMarkupFilter(Filter):
        def filter(self, record: LogRecord) -> bool:
            if hasattr(record, "msg") and isinstance(record.msg, str):
                record.msg = Text.from_markup(
                    Text.from_ansi(record.msg).plain
                ).plain
            return True  # filter rich markup and ansi escape codes

    log_file.parent.mkdir(parents=True, exist_ok=True)
    log_file.touch(exist_ok=True)

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
    file_header = f"[{timestamp}]" + "=" * (80 - 2 - len(timestamp) - 1)
    with open(log_file, "a") as file:
        file.write(file_header + "\n")

    file = RotatingFileHandler(
        log_file, maxBytes=2**10, backupCount=0, delay=True
    )

    file.addFilter(StripMarkupFilter())
    file.setLevel(NOTSET)
    file.setFormatter(
        Formatter(
            r"[%(asctime)s.%(msecs)03d] %(levelname)-8s "
            r"%(message)s [%(filename)s:%(lineno)d]",
            datefmt=r"%Y-%m-%d %H:%M:%S",
        )
    )
    return file


# endregion
