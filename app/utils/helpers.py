"""Application helpers."""

__all__ = ["dispose"]


from typing import Any, MutableSequence, MutableSet


def dispose(array: MutableSequence[Any] | MutableSet[Any]) -> None:
    """Dispose of an array."""
    clone = list(array)
    for i in range(len(clone) - 1, -1, -1):
        array.remove(clone[i])
        del clone[i]
