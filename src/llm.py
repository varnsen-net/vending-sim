from __future__ import annotations

from loguru import logger
from google import genai
from google.genai import types

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from pydantic import SecretStr


class LLM:

    def __init__(self, llm_model: str, llm_api_key: SecretStr):
        self.llm_model: str = llm_model
        self.llm_api_key: SecretStr = llm_api_key
        self.client: genai.Client = genai.Client(api_key=llm_api_key.get_secret_value())

    def fetch_llm_response(self, sys_msg: str, message: str) -> str:
        """"""
        n = 3
        for attempt in range(n):
            try:
                response = self.client.models.generate_content(
                    model=self.llm_model,
                    config=types.GenerateContentConfig(
                        system_instruction=sys_msg,
                        max_output_tokens=200,
                        automatic_function_calling=types.AutomaticFunctionCallingConfig(disable=True),
                    ),
                    contents=message,
                )
                finish_reason = response.candidates[0].finish_reason.name
                if finish_reason != "STOP":
                    raise ValueError(f"Model did not finish properly (finish reason: {finish_reason}). Retrying...")
                break
            except Exception as e:
                logger.warning(f"LLM response attempt {attempt + 1} failed: {e}")
                if attempt == n - 1:
                    return f"Sorry, I couldn't generate a complete response after {n} attempts."
                continue 
        return response.candidates[0].content.parts[0].text

