from __future__ import annotations

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from src.types import Email


class Log:

    def __init__(self):
        self.log: list[str] = []

    def add_email(self, email: Email):
        """Append an email to the log."""
        self.log.append(f"<{email.sender}> {email.to}: {email.content}")
