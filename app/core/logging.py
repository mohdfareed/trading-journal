"""Logging utilities."""

__all__ = ["setup_logging", "create_logger", "view_logs"]

import re
from datetime import datetime
from logging import *  # type: ignore
from logging.handlers import RotatingFileHandler
from pathlib import Path

import rich
import typer
from rich.console import Console
from rich.logging import RichHandler
from rich.text import Text

app_console = Console()
err_console = Console(stderr=True)


def setup_logging(debug: bool = False) -> None:
    """Setup logging for the application."""
    captureWarnings(True)  # capture warnings from the warnings module
    logger = getLogger()
    logger.setLevel(NOTSET)

    logger.addHandler(stdout_handler())
    logger.addHandler(stderr_handler())
    logger.addHandler(debug_handler()) if debug else None


def create_logger(name: str, data_path: Path) -> Logger:
    """Create a new file logger."""
    logger = getLogger(name)
    logger.propagate = False

    logger.addHandler(file_handler(data_path / f"{name}.log"))
    for handler in getLogger().handlers:
        logger.addHandler(handler)
    return logger


def view_logs(
    log_file: Path,
) -> None:
    """View the contents of the log file."""
    if not log_file.exists():
        typer.echo(f"Log file not found: {log_file}")
        raise typer.Exit(1)

    log_contents = log_file.read_text()
    pattern = r"^\[\d{4}-\d{2}-\d{2}\s\d{2}:\d{2}:\d{2}\.\d{3}\]=+$"
    log_entries = re.split(pattern, log_contents, flags=re.MULTILINE)
    if len(log_entries) < 3:  # ['', ..., 'last run (-2)', 'current run (-1)']
        rich.print("[red]No log entries found.[/]")
        raise typer.Exit(1)
    log_contents = log_entries[-2]

    rich.print(f"Log file: {log_file}")
    rich.print(log_contents.strip())


# MARK: Handlers


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
