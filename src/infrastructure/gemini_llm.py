# -*- coding: utf-8 -*-
from __future__ import annotations

import os
from typing import List

import google.generativeai as genai

from src.domain.models import ChatMessage
from src.domain.ports import LLMPort


class GeminiLLMAdapter(LLMPort):
    def __init__(self, api_key: str | None = None, timeout_s: int = 60) -> None:
        api_key = api_key or os.environ.get("GEMINI_API_KEY")
        if not api_key:
            raise RuntimeError(
                "GEMINI_API_KEY não configurada. "
                "Defina a variável de ambiente ou passe api_key no construtor."
            )
        genai.configure(api_key=api_key)
        self.timeout_s = timeout_s

    def chat(self, *, model: str, messages: List[ChatMessage]) -> str:
        # Separa system prompt das demais mensagens
        system_parts = [m.content for m in messages if m.role == "system"]
        conversation = [m for m in messages if m.role != "system"]

        system_instruction = "\n\n".join(system_parts) if system_parts else None

        client = genai.GenerativeModel(
            model_name=model,
            system_instruction=system_instruction,
        )

        # Converte para formato do Gemini
        gemini_messages = [
            {
                "role": "model" if m.role == "assistant" else "user",
                "parts": [m.content],
            }
            for m in conversation
        ]

        response = client.generate_content(
            gemini_messages,
            request_options={"timeout": self.timeout_s},
        )

        return response.text
    