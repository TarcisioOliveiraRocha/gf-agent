# -*- coding: utf-8 -*-
from __future__ import annotations

import os
from typing import List

from openai import OpenAI

from src.domain.models import ChatMessage
from src.domain.ports import LLMPort


class OpenAILLMAdapter(LLMPort):
    def __init__(self, api_key: str | None = None) -> None:
        api_key = api_key or os.environ.get("OPENAI_API_KEY")
        if not api_key:
            raise RuntimeError(
                "OPENAI_API_KEY não configurada. "
                "Defina a variável de ambiente ou passe api_key no construtor."
            )
        self.client = OpenAI(api_key=api_key)

    def chat(self, *, model: str, messages: List[ChatMessage]) -> str:
        payload = [{"role": m.role, "content": m.content} for m in messages]

        response = self.client.chat.completions.create(
            model=model,
            messages=payload,
        )

        return response.choices[0].message.content