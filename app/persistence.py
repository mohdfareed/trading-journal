"""Application configuration stores."""

__all__ = ["LoggingPersistence", "FilePersistence"]


import re
from pathlib import Path
from typing import Generator

from dependency_injector import containers, providers
from pydantic import BaseModel

from app import logging, models


def resource(
    config: models.Config,
    logger: logging.Logger,
    *persistence: models.Persistence,
) -> Generator[models.Config, None, None]:
    """Create a new resource for the persistence service."""
    for service in persistence:
        logger.debug("Loading %s from persistence", type(config).__name__)
        config = service.load(config)
    config.save()  # service <- persistence
    yield config
    config.load()  # service -> persistence
    for service in persistence:
        logger.debug("Storing %s to persistence", type(config).__name__)
        service.store(config)


class LoggingPersistence(models.Persistence):
    """Logging-based persistence."""

    def __init__(self, logger: logging.Logger) -> None:
        self.logger = logger

    def store(self, model: BaseModel) -> None:
        self.logger.debug("Storing model: %s", model.model_dump_json(indent=2))

    def load[T: BaseModel](self, model: T) -> T:
        self.logger.debug("Loaded model: %s", model.model_dump_json(indent=2))
        return model


class FilePersistence(models.Persistence):
    """File-based application data persistence."""

    def __init__(self, data_path: Path, logger: logging.Logger) -> None:
        self.data_path = data_path
        self.logger = logger

    def store(self, model: BaseModel) -> None:
        data_file = self.file_path(model)
        data_file.parent.mkdir(parents=True, exist_ok=True)

        data_file.touch()
        data_file.write_text(model.model_dump_json(indent=2))
        self.logger.debug("Model saved to: %s", data_file)

    def load[T: BaseModel](self, model: T) -> T:
        data_file = self.file_path(model)
        if not data_file.exists():
            self.store(model)
            return model

        model = model.model_validate_json(data_file.read_text())
        self.logger.debug("Model loaded from: %s", data_file)
        return model

    def file_path(self, model: BaseModel) -> Path:
        """The file path to the model's data file."""
        # convert type name to snake case
        file_name = self.name_parser(type(model).__name__)
        return (self.data_path / file_name).with_suffix(".json")

    def name_parser(self, name: str) -> str:
        """Parse the model name to a file name."""
        name = re.sub(r"(.)([A-Z][a-z]+)", r"\1_\2", name)
        name = re.sub(r"([a-z0-9])([A-Z])", r"\1_\2", name)
        return name.lower()


class PersistenceService(containers.DeclarativeContainer):
    """Persistence service."""

    config = providers.Dependency(instance_of=models.Config)
    data_path = providers.Dependency(instance_of=Path)
    logger = providers.Dependency(instance_of=logging.Logger)

    log_persistence = providers.Factory(LoggingPersistence, logger=logger)
    file_persistence = providers.Factory(
        FilePersistence, data_path=data_path, logger=logger
    )

    config_persistence = providers.Resource(
        resource, config, logger, log_persistence, file_persistence
    )
