from __future__ import annotations

from gevent import monkey; monkey.patch_all() # this must always be the first import

import signal
from dataclasses import dataclass

import gevent
from gevent.event import Event
from loguru import logger

from src.registry import Registry
from src.actors.simulator import Simulator
from src.actors.owner import Owner
from src.vending import Product, VendingMachine
from src.llm import LLM
from src.postoffice import PostOffice
from src.log import Log
from src.display import show_email
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
    registry: Registry = Registry()
    shutdown_event: Event = Event()
    llm: LLM = LLM(config.llm)
    log: Log = Log()
    postoffice: PostOffice = PostOffice(registry, log, show_email, config.webhook_url)

    gevent.signal_handler(signal.SIGTERM, handle_signal, shutdown_event)
    gevent.signal_handler(signal.SIGINT, handle_signal, shutdown_event)

    actors: list[BaseActor] = []

    owners = [
        "Art Vandelay",
        "Kel Varnsen",
        "H.E. Pennypacker",
        "Paloma",
    ]
    products = [
        Product(name="Soda", appeal=1.0),
        Product(name="Chips", appeal=1.0),
        Product(name="Candy", appeal=1.0),
    ]

    for owner in owners:
        vending_machine = VendingMachine(products)
        actor: BaseActor = create_register_start(
            Owner,
            owner,
            registry,
            shutdown_event,
            llm,
            postoffice,
            [vending_machine]
        )
        actors.append(actor)

    sim: BaseActor = create_register_start(
        Simulator,
        "simulator",
        registry,
        shutdown_event,
        postoffice,
        products,
        config.simulation.tick_interval
    )
    actors.append(sim)

    gevent.joinall(actors, raise_error=True)
