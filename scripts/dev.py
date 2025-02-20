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
import os
import shutil
import subprocess
import sys
from pathlib import Path

APP_ENV = "development"

ENV = os.environ.copy()
ENV["POETRY_VIRTUALENVS_IN_PROJECT"] = "true"


def main() -> None:
    """Set up environment."""

    os.chdir(Path(__file__).parent.parent)  # .py -> scripts -> repository
    if not shutil.which("poetry"):  # validate poetry
        print(
            "Error: Poetry is required to set up environment.", file=sys.stderr
        )
        sys.exit(1)

    print("Setting up development environment...")
    if Path(".venv").exists():
        shutil.rmtree(".venv")

    print("Installing dependencies...")
    run("poetry install -E dev")
    run(f"{Path.cwd()}/scripts/update.sh")
    run(f"{Path.cwd()}/scripts/hooks.sh")

    print("Creating environment...")
    env_file = Path(".env")
    if not env_file.exists():
        env_file.touch()
    if f"{APP_ENV=}" not in env_file.read_text():
        env_file.write_text(f"{APP_ENV=}")
    print("Environment setup complete.")


def run(cmd: str | list[str]) -> None:
    cmd = cmd if isinstance(cmd, str) else " ".join(cmd)
    subprocess.run(cmd, shell=True, env=ENV, check=True)


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
