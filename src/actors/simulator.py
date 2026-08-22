from __future__ import annotations

from typing import Any
from random import randrange

from loguru import logger
import gevent

from src.actors.actor import BaseActor
from src.types import Email

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from gevent.event import Event
    from src.registry import Registry


class Simulator(BaseActor):

    def __init__(self, name: str, registry: Registry, shutdown: Event):
        BaseActor.__init__(self, name, registry, shutdown)

    def broadcast(self, email: Email):
        """Broadcast an email message to all actors."""
        logger.debug(f"Broadcasting email: {email.content}")
        for actor in self.registry.all():
            if actor.name != self.name:
                actor.inbox.put(email)

    def _run(self):
        """Run the simulation process.

        We want the simulation to regularly check for retirement and shutdown signals, but we
        don't want it to broadcast too frequently. So we use randrange(n) to effectively sleep
        for n seconds (on average). The stochasticity of this approach is an added bonus.
        """
        try:
            email = Email(
                to="all",
                sender=self.name,
                actor_type=self.__class__.__name__,
                content="Act now!"
            )
            self.broadcast(email)
            while not self.retire.is_set() and not self.shutdown.is_set():
                if randrange(600) == 0:
                    self.broadcast(email)
                gevent.sleep(1)
        finally:
            logger.info(f"Actor {self.name} shutting down.")
            self.registry.unregister(self)

