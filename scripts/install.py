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
import os
import subprocess
import sys
import venv
from pathlib import Path

PACKAGE_URL = "git+https://github.com/mohdfareed/trading-journal.git"
DEFAULT_INSTALL_PATH = Path.cwd() / "Trading Journal"
EXECUTABLE = "trading-journal"


def main(path: Path, dev: bool) -> None:
    """Install application."""
    print(f"Installing application at: {path}")

    print("Creating environment...")
    path.mkdir(parents=True, exist_ok=True)
    builder = venv.EnvBuilder(
        upgrade=True, with_pip=True, prompt=EXECUTABLE, upgrade_deps=True
    )
    builder.create(path)

    # activate venv and upgrade pip
    if sys.platform == "win32":
        executable = path / "Scripts" / f"{EXECUTABLE}.exe"
        venv_exe = path / "Scripts" / "activate.ps1"
        run(f"{venv_exe}; pip install --upgrade pip")
    else:  # Unix
        executable = path / "bin" / EXECUTABLE
        venv_path = path / "bin" / "activate"
        run(f"source {venv_path} && pip install --upgrade pip")

    print("Installing application...")
    run(f"pip install {PACKAGE_URL}" + "[dev]" if dev else "")
    link = path / EXECUTABLE
    link.symlink_to(executable)
    print(f"Linked executable: {link} -> {executable}")


def run(cmd: str | list[str]) -> None:
    cmd = cmd if isinstance(cmd, str) else " ".join(cmd)
    subprocess.run(cmd, shell=True, env=os.environ, check=True)


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
    parser.add_argument(
        "--dev",
        action="store_true",
        help="install in development mode",
    )

    # Parse arguments
    args = parser.parse_args()
    try:  # Install the application
        main(args.PATH, args.dev)

    # Handle user interrupts
    except KeyboardInterrupt:
        print("Aborted!")
        sys.exit(1)

    # Handle shell errors
    except subprocess.CalledProcessError as error:
        print(f"Error: {error}", file=sys.stderr)
        sys.exit(1)


# endregion
