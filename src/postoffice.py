from __future__ import annotations
from typing import Callable

from loguru import logger

from src.actors.actor import BaseActor

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from src.registry import Registry
    from src.types import Email


class PostOffice:

    def __init__(self, registry: Registry, log: Log, display: Callable):
        self.registry = registry
        self.log: Log = log
        self.display: Callable = display

    def send_mail(
        self,
        email: Email,
        recip: BaseActor | list[BaseActor] | None,
    ):
        """Sends an email to the recipient(s) inbox. If the recipient is a list, it will send the
        email to all recipients."""
        if not recip:
            logger.warning("No recipient specified. Email not sent.")
            return

        if isinstance(recip, BaseActor):
            recip: list[BaseActor] = [recip]

        all_names: list[str] = self.registry.all_names()
        for actor in recip:
            if actor.name not in all_names:
                logger.warning(f"Recipient {actor.name} not found in registry. Email not sent.")
                continue
            if actor.name != email.sender:
                actor.inbox.put(email)
                self.log.add_email(email)
                self.display(email)
