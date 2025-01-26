"""Events management system."""

__all__ = ["EventHandler"]

import inspect
import logging
from threading import Lock
from typing import Any, Callable, Generic, Self

from typing_extensions import ParamSpec

from app import models, utils

EventData = ParamSpec("EventData", default=[])  # event data type definition
EventHandler = Callable[EventData, None]


class Event(Generic[EventData]):
    """Event class."""

    def __init__(self, name: str | None = None) -> None:
        """Initialize the event."""
        self.name = name or self.__class__.__name__
        self.logger = logging.getLogger(f"Event.{self.name}")
        self.handlers: set[Handler[EventData]] = set()
        self._lock = Lock()

    def subscribe(
        self, handler: EventHandler[EventData], one_shot: bool = False
    ) -> None:
        """Subscribe to the event."""
        with self._lock:
            self.logger.debug("Subscribing to '%s': %s", self, handler)
            self.handlers.add(Handler(self, handler, one_shot=one_shot))

    def unsubscribe(self, handler: EventHandler[EventData]) -> None:
        """Unsubscribe from the event."""
        with self._lock:
            self.logger.debug("Unsubscribing from '%s': %s", self, handler)
            self.handlers.remove(Handler(self, handler))

    def is_subscribed(self, callback: EventHandler[EventData]) -> bool:
        """Check if a callback is subscribed to the event."""
        return callback in self.handlers

    # MARK: Methods

    def fire(self, *args: EventData.args, **kwargs: EventData.kwargs) -> None:
        """Trigger the event."""
        with self._lock:
            self.logger.info("Event '%s' triggered.", self)
            for handler in set(self.handlers):
                self.logger.debug("Triggering '%s' handler: %s", self, handler)

                try:
                    handler(*args, **kwargs)
                except models.AppError as e:
                    self.logger.error("Error executing %s: %s", handler, e)
                except Exception as e:  # pylint: disable=broad-except
                    self.logger.exception("Exception executing %s: %s", handler, e)

        self.logger.debug("Event '%s' handled.", self)

    async def fire_async(
        self, *args: EventData.args, **kwargs: EventData.kwargs
    ) -> None:
        """Trigger the event asynchronously."""
        with self._lock:
            self.logger.info("Event '%s' triggered (async).", self)
            for handler in set(self.handlers):
                self.logger.debug("Triggering '%s' handler: %s (async)", self, handler)

                try:
                    await handler.trigger_async(*args, **kwargs)
                except models.AppError as e:
                    self.logger.error("Error executing %s: %s", handler, e)
                except Exception as e:  # pylint: disable=broad-except
                    self.logger.exception("Exception executing %s: %s", handler, e)

        self.logger.debug("Event '%s' handled (async).", self)

    # MARK: Magic Methods

    def __iadd__(self, handler: EventHandler[EventData]) -> Self:
        self.subscribe(handler)
        return self

    def __isub__(self, handler: EventHandler[EventData]) -> Self:
        self.unsubscribe(handler)
        return self

    def __call__(self, *args: EventData.args, **kwargs: EventData.kwargs) -> None:
        return self.fire(*args, **kwargs)

    def __repr__(self) -> str:
        return f"{self.name}(handlers={len(self.handlers)})"

    def __str__(self) -> str:
        return self.name

    def __del__(self) -> None:
        utils.dispose(self.handlers)


# MARK: Event Handler


class Handler(Generic[EventData]):
    """Event handler class."""

    def __init__(
        self,
        event: "Event[EventData]",
        callback: EventHandler[EventData],
        one_shot: bool = False,
    ) -> None:
        """Initialize the event handler."""
        self.event = event
        self.callback = callback
        self.one_shot = one_shot

    # MARK: Methods

    def trigger(self, *args: EventData.args, **kwargs: EventData.kwargs) -> None:
        """Trigger the event handler."""
        if self.one_shot:
            self.event.unsubscribe(self)
        self.callback(*args, **kwargs)

    async def trigger_async(
        self, *args: EventData.args, **kwargs: EventData.kwargs
    ) -> None:
        """Trigger the event handler asynchronously."""
        if self.one_shot:
            self.event.unsubscribe(self)

        if inspect.iscoroutinefunction(self.callback):
            await self.callback(*args, **kwargs)
        else:
            self.callback(*args, **kwargs)

    # MARK: Magic Methods

    def __call__(self, *args: EventData.args, **kwargs: EventData.kwargs) -> None:
        return self.trigger(*args, **kwargs)

    def __repr__(self) -> str:
        return f"{self.callback.__qualname__}(one_shot={self.one_shot})"

    def __str__(self) -> str:
        return self.callback.__qualname__

    def __eq__(self, other: Any) -> bool:
        if isinstance(other, Handler):
            return hash(self.callback) == hash(other.callback)
        if callable(other):
            return hash(self.callback) == hash(other)
        return False

    def __hash__(self) -> int:
        return hash(self.callback)

    def __del__(self) -> None:
        del self.callback
