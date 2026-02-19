from __future__ import annotations

import os
from typing import List

from openai import OpenAI

from src.domain.models import ChatMessage
from src.domain.ports import LLMPort


class OpenAILLMAdapter(LLMPort):
    def __init__(self, api_key: str | None):
        if not api_key:
            api_key = os.environ.get("OPENAI_API_KEY")
        if not api_key:
            raise RuntimeError("OPENAI_API_KEY não configurada.")
        self.client = OpenAI(api_key=api_key)

    def chat(self, *, model: str, messages: List[ChatMessage]) -> str:
        transcript = "\n".join([f"{m.role.upper()}: {m.content}" for m in messages])

        resp = self.client.responses.create(
            model=model,
            input=transcript,
        )
        return resp.output_text