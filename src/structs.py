from dataclasses import dataclass, field
from datetime import datetime
from typing import Any


@dataclass
class Email:
    to: str
    sender: str
    actor_type: str
    content: Any
    timestamp: datetime = field(default_factory=datetime.now)
