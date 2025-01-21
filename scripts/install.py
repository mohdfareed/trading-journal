#!/usr/bin/env python3

"""
Install the application locally.

Create a new virtual environment and install the application.
If a path is provided, the virtual environment is created at that location.
Otherwise, the virtual environment is created in the current directory.

Requirements:
    - venv
"""

import argparse
import atexit
import os
import subprocess
import sys
from pathlib import Path

PACKAGE_URL = "git+https://github.com/mohdfareed/trading-journal.git"
DEFAULT_INSTALL_PATH = Path.cwd() / "Trading Journal"
EXECUTABLE = "trading-journal"


def main(path: Path) -> None:
    """Install application."""

    _validate(path)
    _create_env(path)
    _install_app(path)
    _link_executable(path)


def _validate(path: Path) -> None:
    cwd = os.getcwd()
    atexit.register(lambda: os.chdir(cwd))
    path.parent.mkdir(parents=True, exist_ok=True)
    os.chdir(path.parent)


def _create_env(path: Path) -> None:
    print(f"Creating virtual environment at: {path}")
    subprocess.run(
        ["python3", "-m", "venv", path],
        cwd=path.parent,
        check=True,
    )


def _install_app(path: Path) -> None:
    print("Installing application...")

    if sys.platform == "win32":
        pip = path / "Scripts" / "pip.exe"
    else:  # Unix
        pip = path / "bin" / "pip"

    subprocess.run(
        [pip, "install", PACKAGE_URL],
        check=True,
    )


def _link_executable(path: Path) -> None:
    print("Linking executable...")

    if sys.platform == "win32":
        executable = path / "Scripts" / f"{EXECUTABLE}.exe"
    else:  # Unix
        executable = path / "bin" / EXECUTABLE

    link = path / EXECUTABLE
    link.symlink_to(executable)


# region: CLI


class ScriptFormatter(
    argparse.ArgumentDefaultsHelpFormatter,
    argparse.RawDescriptionHelpFormatter,
):
    """Custom formatter for argparse help messages."""


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description=(__doc__ or "").strip(), formatter_class=ScriptFormatter
    )

    # Add arguments
    parser.add_argument(
        "PATH",
        type=Path,
        help="app installation path",
        nargs="?",
        default=DEFAULT_INSTALL_PATH,
    )

    # Parse arguments
    args = parser.parse_args()
    app_path: Path = args.PATH
    try:  # Install the application
        main(app_path)

    # Handle user interrupts
    except KeyboardInterrupt:
        print("Aborted!")
        sys.exit(1)

    # Handle shell errors
    except subprocess.CalledProcessError as error:
        print(f"Error: {error}", file=sys.stderr)
        sys.exit(1)


# endregion
