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
        logger.info(f"Registering actor: {actor.name}")
        self.actors[actor.name] = actor

    def unregister(self, actor: BaseActor):
        """Remove an actor from the registry."""
        logger.info(f"Unregistering actor: {actor.name}")
        try:
            del self.actors[actor.name]
        except KeyError:
            logger.warning(f"Attempted to unregister non-existent actor: {actor.name}")

    def all_actors(self) -> list[BaseActor]:
        """Return a list of all registered actors."""
        return list(self.actors.values())

    def all_names(self) -> list[str]:
        """Return a list of all registered actor names."""
        return list(self.actors.keys())

    def get_by_name(self, name: str) -> BaseActor | None:
        """Fetch an actor by name."""
        try:
            return self.actors[name]
        except KeyError:
            logger.warning(f"No actor with name '{name}' found in registry.")
            return None

    def get_by_type(self, cls: type) -> list[BaseActor]:
        """Fetch all actors of a specific type."""
        return [a for a in self.actors.values() if isinstance(a, cls)]
