from __future__ import annotations

from dataclasses import dataclass

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from src.actors.owner import Owner


@dataclass(frozen=True)
class Product:
    name: str
    appeal: float


@dataclass
class Item:
    name: str
    price: float = 1.0


@dataclass
class VendingMachine:
    products: list[Product]

    def __post_init__(self):
        self.items: list[Item] = [Item(product.name) for product in self.products]
