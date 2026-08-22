from __future__ import annotations

from gevent import monkey; monkey.patch_all() # this must always be the first import

import signal

import gevent
from gevent.event import Event
from loguru import logger

from src.registry import Registry
from src.actors.simulator import Simulator
from src.actors.owner import Owner
from src.llm import LLM
from src.config import AppSettings

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from src.actors.actor import BaseActor


def handle_signal(shutdown_event: Event) -> None:
    """Handle SIGTERM and SIGINT signals by stopping all actors in the registry."""
    logger.info("Received signal, shutting down...")
    shutdown_event.set()


def create_register_start(
    actor_cls: type[BaseActor],
    name: str,
    registry: Registry,
    shutdown: Event,
    *args,
    **kwargs
) -> BaseActor:
    """Spin up an actor, register it in the registry, and start it."""
    logger.info(f"Creating {actor_cls.__name__} with name {name}")
    actor = actor_cls(name, registry, shutdown, *args, **kwargs)
    registry.register(actor)
    actor.start()
    return actor


if __name__ == "__main__":
    config: AppSettings = AppSettings()
    shutdown_event: Event = Event()
    llm: LLM = LLM(config.llm_model, config.llm_api_key)

    gevent.signal_handler(signal.SIGTERM, handle_signal, shutdown_event)
    gevent.signal_handler(signal.SIGINT, handle_signal, shutdown_event)

    registry: Registry = Registry()
    actors: list[BaseActor] = [
        create_register_start(Owner, "Art Vandelay", registry, shutdown_event, llm),
        create_register_start(Owner, "Kel Varnsen", registry, shutdown_event, llm),
        create_register_start(Owner, "H.E. Pennypacker", registry, shutdown_event, llm),
        create_register_start(Simulator, "simulator", registry, shutdown_event),
    ]

    gevent.joinall(actors, raise_error=True)
