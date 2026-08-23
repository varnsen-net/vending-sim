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
    from src.log import Log


USR_MSG: str = """
{script}

This is the script so far. The character you're writing for is {name}.

In this episode, Kel is frustrated because last night he thought he was going on a date with Obama,
but it turned out to be a Mitsubishi FG15-35(C)P / FD20-35P3 Series counterbalanced forklift
using Obama's picture as its Tinder profile picture.

First decide what sort of response you want to make. Examples:
- A witty one-liner or joke
- Ask a question
- Set up a joke
- Continue the conversation
- Something short like "Okay" or "No thanks" or whatever just to keep the conversation going

Now write and reply with your line of dialogue.
"""


class Owner(BaseActor):

    def __init__(
        self,
        name: str,
        registry: Registry,
        shutdown: Event,
        llm: LLM,
        postoffice: PostOffice,
        log: Log,
    ):
        BaseActor.__init__(self, name, registry, shutdown)
        self.llm: LLM = llm
        self.postoffice: PostOffice = postoffice
        self.log: Log = log

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
                content="What's new?"
            )
            self.postoffice.send_mail(outgoing, send_to)

        if incoming.sender == "simulator" and incoming.content == "TICK":
            all_actors: list[BaseActor] = self.registry.get_by_type(Owner)
            send_to: Owner = choice([a for a in all_actors if a.name != self.name])
            script: str = '\n'.join(self.log.log[-20:])  # Get the last 25 lines of the script
            response: str = self.llm.fetch_llm_response(USR_MSG.format(script=script, name=self.name))
            outgoing: Email = Email(
                to=send_to.name,
                sender=self.name,
                actor_type=self.__class__.__name__,
                content=response
            )
            self.postoffice.send_mail(outgoing, send_to)

        if incoming.actor_type == "Owner":
            if randint(0, 100) < 75:
                script: str = '\n'.join(self.log.log[-20:])
                response: str = self.llm.fetch_llm_response(USR_MSG.format(script=script, name=self.name))
                outgoing: Email = Email(
                    to=incoming.sender,
                    sender=self.name,
                    actor_type=self.__class__.__name__,
                    content=response
                )
                send_to: Owner | None = self.registry.get_by_name(incoming.sender)
                self.postoffice.send_mail(outgoing, send_to)
                gevent.sleep(randint(1, 30))
