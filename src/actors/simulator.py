from __future__ import annotations

from typing import Any
from random import randrange, choice

from loguru import logger
import gevent

from src.actors.actor import BaseActor
from src.actors.owner import Owner
from src.structs import Email

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from gevent.event import Event
    from src.registry import Registry
    from src.postoffice import PostOffice
    from src.vending import Product


class Simulator(BaseActor):

    def __init__(
        self,
        name: str,
        registry: Registry,
        shutdown: Event,
        postoffice: PostOffice,
        products: list[Product],
        tick_interval: int,
    ):
        BaseActor.__init__(self, name, registry, shutdown)
        self.postoffice: PostOffice = postoffice
        self.products: list[Product] = products
        self.tick_interval: int = tick_interval

    def _run(self):
        """Run the simulation process.

        We want the simulation to regularly check for retirement and shutdown signals, but we
        don't want it to broadcast too frequently. Use tick_interval to determine how often to
        broadcast a tick message to all owners (in seconds).
        """
        gevent.sleep(2) # Give the other actors a chance to spin up and register before broadcasting
        try:
            tick_num: int = self.tick_interval
            while not self.retire.is_set() and not self.shutdown.is_set():
                if tick_num == self.tick_interval:
                    all_owners: list[Owner] = self.registry.get_by_type(Owner)
                    # raw_sales = do_hella_vending(all_owners)
                    # sales_report = compile_report(raw_sales)
                    outgoing = Email(
                        to="Owners",
                        sender=self.name,
                        actor_type=self.__class__.__name__,
                        content="hello"
                    )
                    self.postoffice.send_mail(outgoing, all_owners)
                    # display_report(sales_report)
                    tick_num = 0
                tick_num += 1
                gevent.sleep(1)
        finally:
            logger.info(f"Actor {self.name} shutting down.")
            self.registry.unregister(self)

