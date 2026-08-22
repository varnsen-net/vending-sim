from __future__ import annotations

from typing import Any
from random import randrange

from loguru import logger
import gevent

from src.actors.actor import BaseActor
from src.actors.owner import Owner
from src.types import Email

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from gevent.event import Event
    from src.registry import Registry
    from src.postoffice import PostOffice


class Simulator(BaseActor):

    def __init__(self, name: str, registry: Registry, shutdown: Event, postoffice: PostOffice):
        BaseActor.__init__(self, name, registry, shutdown)
        self.postoffice: PostOffice = postoffice

    def _run(self):
        """Run the simulation process.

        We want the simulation to regularly check for retirement and shutdown signals, but we
        don't want it to broadcast too frequently. So we use randrange(n) to effectively sleep
        for n seconds (on average). The stochasticity of this approach is an added bonus.
        """
        try:
            all_owners: list[Owner] = self.registry.get_by_type(Owner)
            outgoing: Email = Email(
                to="Owners",
                sender=self.name,
                actor_type=self.__class__.__name__,
                content="TICK"
            )
            self.postoffice.send_mail(outgoing, all_owners)
            while not self.retire.is_set() and not self.shutdown.is_set():
                if randrange(600) == 0:
                    self.postoffice.send_mail(outgoing, all_owners)
                gevent.sleep(1)
        finally:
            logger.info(f"Actor {self.name} shutting down.")
            self.registry.unregister(self)

