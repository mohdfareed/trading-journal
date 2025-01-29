# Update dependencies

poetry self update
poetry update
poetry lock


poetry
poetry run pre-commit install --install-hooks
poetry run pre-commit autoupdate
poetry build
