"""
EventRegistry: maps event_type strings ↔ payload Pydantic model classes.

Every payload class must be registered here. The EventStore validates
event_type values against this registry before insertion.
"""

from __future__ import annotations

from typing import Type

from .models.base import BaseEventPayload


class _EventRegistry:
    def __init__(self) -> None:
        self._type_to_cls: dict[str, Type[BaseEventPayload]] = {}
        self._cls_to_type: dict[Type[BaseEventPayload], str] = {}

    def register(self, event_type: str, cls: Type[BaseEventPayload]) -> None:
        self._type_to_cls[event_type] = cls
        self._cls_to_type[cls] = event_type

    def cls_for(self, event_type: str) -> Type[BaseEventPayload]:
        if event_type not in self._type_to_cls:
            raise TypeError(f"Unknown event_type: '{event_type}'. Register it in EventRegistry.")
        return self._type_to_cls[event_type]

    def type_for(self, cls: Type[BaseEventPayload]) -> str:
        if cls not in self._cls_to_type:
            raise TypeError(f"Payload class {cls.__name__} is not registered in EventRegistry.")
        return self._cls_to_type[cls]

    def registered_types(self) -> list[str]:
        return sorted(self._type_to_cls.keys())


EventRegistry = _EventRegistry()

# ---------------------------------------------------------------------------
# Registration — import all payload modules to trigger @register decorators
# ---------------------------------------------------------------------------
# Populated in src/events/__init__.py after all models are imported.
