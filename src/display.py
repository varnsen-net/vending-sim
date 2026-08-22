from __future__ import annotations

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from src.structs import Email


def show_email(email: Email):
    """Display an email in the console."""
    print(f"<{email.sender}> {email.to}: {email.content}\n")
