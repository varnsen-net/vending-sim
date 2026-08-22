from __future__ import annotations

from typing import Any
from random import choice

import gevent
from loguru import logger

from src.actors.actor import BaseActor
from src.types import Email

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from gevent.event import Event
    from src.registry import Registry
    from src.llm import LLM


class Owner(BaseActor):

    def __init__(
        self,
        name: str,
        registry: Registry,
        shutdown: Event,
        llm: LLM
    ):
        BaseActor.__init__(self, name, registry, shutdown)
        self.llm: LLM = llm

    def handle(self, incoming: Email):
        """Handle an incoming message."""
        if incoming.sender == "simulator" and incoming.content == "Act now!":
            all_actors: list[BaseActor] = [
                a for a in self.registry.get_by_type(BaseActor)
                if a.name != self.name
            ]
            send_to: BaseActor = choice(all_actors)
            outgoing: Email = Email(
                to=send_to.name,
                sender=self.name,
                actor_type=self.__class__.__name__,
                content="Hey bb <3"
            )
            send_to.inbox.put(outgoing)

        if incoming.actor_type == "Owner":
            print(f"{incoming.sender} --> {incoming.to}")
            print(f"{incoming.content}\n")
            sys_msg: str = "lol. lmao, even."
            response: str = self.llm.fetch_llm_response(sys_msg, incoming.content)
            outgoing: Email = Email(
                to=incoming.sender,
                sender=self.name,
                actor_type=self.__class__.__name__,
                content=response
            )
            self.registry.get_by_name(incoming.sender).inbox.put(outgoing)
            gevent.sleep(5)
