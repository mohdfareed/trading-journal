#!/usr/bin/env python3

"""
Set up a local development environment.

Creates a virtual environment with Poetry and installs the development
dependencies. Other development tools are also set up.
The script must be run in the repository.

Requirements:
    - poetry
"""

import argparse
import atexit
import os
import shutil
import subprocess
import sys
from pathlib import Path

PYTHON_VERSION = (3, 13)
ENV_FILE_CONTENT = "APP_ENV=development"


def main() -> None:
    """Set up environment."""

    print("Setting up development environment...")

    poetry = _validate()
    _setup_environment(poetry)
    _setup_pre_commit_hooks(poetry)
    _create_env_file()

    print("Environment setup complete.")


def _validate() -> Path:
    cwd = os.getcwd()
    atexit.register(lambda: os.chdir(cwd))
    os.chdir(Path(__file__).parent.parent)  # .py -> scripts -> repository

    _validate_python()
    return _validate_poetry()


def _validate_python() -> None:
    if sys.version_info >= PYTHON_VERSION:
        return

    version = ".".join(map(str, PYTHON_VERSION))
    print(f"Error: Python >={version} is required.", file=sys.stderr)
    sys.exit(1)


def _validate_poetry() -> Path:
    if poetry := shutil.which("poetry"):
        return Path(poetry)

    print("Error: Poetry is required to set up environment.", file=sys.stderr)
    sys.exit(1)


def _setup_environment(poetry: Path) -> None:
    subprocess.run(
        [poetry, "env", "use", sys.executable],
        env={"POETRY_VIRTUALENVS_IN_PROJECT": "true"},
        check=True,
    )
    subprocess.run(
        [poetry, "install", "-E", "dev"],
        env={"POETRY_VIRTUALENVS_IN_PROJECT": "true"},
        check=True,
    )


def _setup_pre_commit_hooks(poetry: Path) -> None:
    subprocess.run(
        [poetry, "run", "pre-commit", "install", "--install-hooks"],
        check=True,
    )


def _create_env_file() -> None:
    env_file = Path(".env")
    if env_file.exists():
        return

    print("Creating environment file...")
    env_file.touch()
    env_file.write_text(ENV_FILE_CONTENT)


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

    args = parser.parse_args()
    try:  # Set up environment
        main()

    # Handle user interrupts
    except KeyboardInterrupt:
        print("Aborted!")
        sys.exit(1)

    # Handle shell errors
    except subprocess.CalledProcessError as error:
        print(f"Error: {error}", file=sys.stderr)
        sys.exit(1)


# endregion
