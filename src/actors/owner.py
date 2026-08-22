from __future__ import annotations

from typing import Any
from random import choice, randint

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


class Owner(BaseActor):

    def __init__(
        self,
        name: str,
        registry: Registry,
        shutdown: Event,
        llm: LLM,
        postoffice: PostOffice,
    ):
        BaseActor.__init__(self, name, registry, shutdown)
        self.llm: LLM = llm
        self.postoffice: PostOffice = postoffice

    def handle(self, incoming: Email):
        """Handle an incoming message."""
        if type(incoming) is not Email:
            logger.error(f"Owner {self.name} received a non-Email message: {incoming}")
            return

        if incoming.sender == "simulator" and incoming.content == "START":
            all_actors: list[BaseActor] = self.registry.get_by_type(Owner)
            send_to: Owner = choice([a for a in all_actors if a.name != self.name])
            outgoing: Email = Email(
                to=send_to.name,
                sender=self.name,
                actor_type=self.__class__.__name__,
                content="Hey bb <3"
            )
            self.postoffice.send_mail(outgoing, send_to)

        if incoming.actor_type == "Owner":
            sys_msg: str = "lol. lmao, even."
            response: str = self.llm.fetch_llm_response(sys_msg, incoming.content)
            outgoing: Email = Email(
                to=incoming.sender,
                sender=self.name,
                actor_type=self.__class__.__name__,
                content=response
            )
            send_to: Owner | None = self.registry.get_by_name(incoming.sender)
            self.postoffice.send_mail(outgoing, send_to)
            gevent.sleep(randint(1, 20))
