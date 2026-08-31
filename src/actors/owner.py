from __future__ import annotations

from typing import Any
from random import choice, uniform

import gevent
from loguru import logger

from src.actors.actor import BaseActor
from src.structs import Email

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from gevent.event import Event
    from src.registry import Registry
    from src.llm import LLM
    from src.postoffice import PostOffice
    from src.log import Log


class Owner(BaseActor):

    def __init__(
        self,
        name: str,
        registry: Registry,
        shutdown: Event,
        llm: LLM,
        postoffice: PostOffice,
        machines: list[VendingMachine]
    ):
        BaseActor.__init__(self, name, registry, shutdown)
        self.llm: LLM = llm
        self.postoffice: PostOffice = postoffice
        self.machines: list[VendingMachine] = machines

    def handle(self, incoming: Email):
        """Handle an incoming message."""
        if type(incoming) is not Email:
            logger.error(f"Owner {self.name} received a non-Email message: {incoming}")
            return

        # if incoming.sender == "simulator" and incoming.content == "START":
            # gevent.sleep(uniform(1, 3)) # effectively randomizes the order in which actors act
            # self.handle_sim_start()

        if incoming.sender == "simulator":
            gevent.sleep(uniform(1, 3))
            self.handle_sim_tick()

        if incoming.actor_type == "Owner":
            self.handle_dm_from_owner(incoming)

    def handle_sim_start(self):
        """"""
        pass

    def handle_sim_tick(self):
        """"""
        print(self.machines[0])

    def handle_dm_from_owner(self, incoming: Email):
        """"""
        pass

