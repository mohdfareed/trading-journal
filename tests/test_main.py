"""Main tests."""

from typer.testing import CliRunner

from app.main import app

runner = CliRunner()


def test_app() -> None:
    """Test the app executing normally."""

    try:
        from app import __main__ as _  # pylint: disable=import-outside-toplevel
    except SystemExit as ex:
        assert ex.code == 2

    result = runner.invoke(app, ["-h"])
    assert result.exit_code == 0
    assert "Usage:" in result.stdout.split("\n")[1]


def test_app_fail() -> None:
    """Test the app executing and failing."""

    result = runner.invoke(app, ["fail"])
    assert result.exit_code == 2
    assert "Error" in result.stdout


def test_app_debug() -> None:
    """Test the app."""

    result = runner.invoke(app, ["-d", "test"])
    assert "DEBUG" in result.stdout.split("\n")[0]
