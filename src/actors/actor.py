from __future__ import annotations

from typing import Any

import gevent
from gevent.queue import Queue, Empty
from gevent.event import Event
from loguru import logger

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from src.registry import Registry


class BaseActor(gevent.Greenlet):

    def __init__(self, name: str, registry: Registry, shutdown: Event):
        gevent.Greenlet.__init__(self)
        self.name: str = name
        self.registry: Registry = registry
        self.shutdown: Event = shutdown
        self.retire: Event = Event()
        self.inbox: Queue = Queue()
        self.link_exception(self.on_crash)

    def on_crash(self, greenlet: gevent.Greenlet):
        """Handle a crash in the owner process."""
        logger.exception(f"Actor {self.name} crashed: {greenlet.exception}")

    def _run(self):
        """Run the owner process."""
        try:
            while not self.retire.is_set() and not self.shutdown.is_set():
                try:
                    message: Any = self.inbox.get(timeout=1)
                except Empty:
                    continue
                self.handle(message)
        finally:
            logger.info(f"Actor {self.name} shutting down.")
            self.registry.unregister(self)

    def handle(self, message: Any):
        """Handle a message."""
        raise NotImplementedError("Subclasses must implement the handle method.")
