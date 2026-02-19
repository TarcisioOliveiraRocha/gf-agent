from __future__ import annotations

import time
from typing import List

from src.domain.models import AgentResponse, ChatMessage
from src.domain.ports import LLMPort


class ChatAgentUC:
    def __init__(self, llm: LLMPort):
        self.llm = llm

    def run(self, *, model: str, history: List[ChatMessage], user_text: str) -> AgentResponse:
        t0 = time.time()

        system = ChatMessage(
            role="system",
            content=(
                "Você é o Grupo Fácil IA, a inteligência oficial do Grupo Fácil. "
                "Seja objetivo, cordial e orientado a ação. "
                "Se faltar contexto, faça perguntas curtas."
            ),
        )
        messages = [system, *history, ChatMessage(role="user", content=user_text)]

        text = self.llm.chat(model=model, messages=messages)

        latency_ms = int((time.time() - t0) * 1000)
        return AgentResponse(
            text=text,
            used_model=model,
            latency_ms=latency_ms,
            safety_notes=[],
        )