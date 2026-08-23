from __future__ import annotations

from loguru import logger
from mistralai.client import Mistral

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from pydantic import SecretStr
    from pydantic import BaseModel


class LLM:

    def __init__(self, llm_config: BaseModel):
        self.model: str = llm_config.model
        self.sys_msg: str = llm_config.sys_msg
        self.temperature: float = llm_config.temperature
        self.api_key: SecretStr = llm_config.api_key
        self.client: mistral.client = Mistral(api_key=self.api_key.get_secret_value())

    def fetch_llm_response(self, message: str) -> str:
        """Fetches a response from the LLM model with retry logic in case of failure."""
        messages = [
            {"role": "system", "content": self.sys_msg},
            {"role": "user", "content": message}
        ]
        n = 3
        for attempt in range(n):
            try:
                response = self.client.chat.complete(
                    model=self.model,
                    messages=messages,
                    temperature=self.temperature,
                )
                finish_reason = response.choices[0].finish_reason
                if finish_reason != "stop":
                    raise ValueError(f"Model did not finish properly (finish reason: {finish_reason}). Retrying...")
                break
            except Exception as e:
                logger.warning(f"LLM response attempt {attempt + 1} failed: {e}")
                if attempt == n - 1:
                    return f"Sorry, I couldn't generate a complete response after {n} attempts."
                continue 
        print(response.usage)
        return response.choices[0].message.content

