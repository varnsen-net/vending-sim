from __future__ import annotations

import gevent
from gevent.queue import Queue
from loguru import logger

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from src.actors.actor import BaseActor


class Registry:
    def __init__(self):
        self.actors: dict[str, BaseActor] = {}

    def register(self, actor: BaseActor):
        """Add an actor to the registry."""
        self.actors[actor.name] = actor
        logger.info(f"Registered actor: {actor.name}")

    def unregister(self, actor: BaseActor):
        """Remove an actor from the registry."""
        del self.actors[actor.name]
        logger.info(f"Unregistered actor: {actor.name}")

    def all(self) -> list[BaseActor]:
        """Return a list of all registered actors."""
        return list(self.actors.values())

    def get_by_name(self, name: str) -> BaseActor:
        """Fetch an actor by name."""
        return self.actors[name]

    def get_by_type(self, cls: type) -> list[BaseActor]:
        """Fetch all actors of a specific type."""
        return [a for a in self.actors.values() if isinstance(a, cls)]
