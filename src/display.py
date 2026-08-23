from __future__ import annotations

from time import sleep
from random import uniform

import requests
from tenacity import (
    RetryCallState,
    retry,
    retry_if_exception,
    stop_after_attempt,
    wait_exponential_jitter,
)
from loguru import logger

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from pydantic import SecretStr
    from src.structs import Email


def is_retryable_request_error(exc: BaseException) -> bool:
    """Return True only for errors that are safe and worthwhile to retry."""
    if isinstance(exc, requests.ConnectionError):
        return True
    if isinstance(exc, requests.Timeout):
        return True
    if isinstance(exc, requests.HTTPError):
        # Retry server errors and rate limits; never retry client errors
        retryable_status_codes = {408, 429, 500, 502, 503, 504}
        return exc.response is not None and exc.response.status_code in retryable_status_codes
    return False


def log_before_sleep(retry_state: RetryCallState) -> None:
    """Log a warning message before sleeping between retries."""
    exc = retry_state.outcome.exception()
    if exc is not None:
        logger.warning(f"Retrying after error: {exc}. Attempt {retry_state.attempt_number}.")


@retry(
    retry=retry_if_exception(is_retryable_request_error),
    wait=wait_exponential_jitter(initial=2, max=15, jitter=2),
    stop=stop_after_attempt(5),
    before_sleep=log_before_sleep,
    reraise=True,
)
def request_with_retries(url: str, data: dict) -> requests.Response:
    """Fetch the odds response from the API for a given sport and date, with retries."""
    response = requests.post(
        url,
        data=data,
        timeout=10,
    )
    response.raise_for_status()
    return response


def show_email(email: Email, webhook_url: SecretStr) -> None:
    """Display an email in the console."""
    avatars = {
        "Kel Varnsen": "https://i.ibb.co/wmndMkL/kel.jpg",
        "Art Vandelay": "https://i.ibb.co/20SyQ0vR/art.jpg",
        "H.E. Pennypacker": "https://i.ibb.co/YTk0fzbj/pennypacker.png",
        "Paloma": "https://i.ibb.co/ZpLw9cCX/paloma.png",
    }
    params = {
        "content": email.content,
        "username": email.sender,
        "avatar_url": avatars.get(email.sender),
    }
    sleep(uniform(0.5, 1.5))  # Random delay to avoid rate limiting
    # response = request_with_retries(webhook_url.get_secret_value(), params)
    print(params)
