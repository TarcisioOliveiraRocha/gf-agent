# -*- coding: utf-8 -*-
from __future__ import annotations

import time
from typing import List

from src.domain.agent_identity import AGENT_IDENTITY
from src.domain.models import AgentResponse, ChatMessage
from src.domain.ports import LLMPort

_PDF_SYSTEM = (
    AGENT_IDENTITY.strip()
    + "\n\n"
    "TAREFA ATUAL:\n"
    "- Você receberá o texto extraído de um PDF.\n"
    "- Explique o conteúdo com clareza e objetividade.\n"
    "- Se o texto estiver incompleto ou confuso, sinalize explicitamente.\n"
    "- Ao final, sugira 3 perguntas úteis que o usuário pode fazer sobre o documento.\n"
)

_MAX_PDF_CHARS = 18_000


class ExplainPdfUC:
    def __init__(self, llm: LLMPort) -> None:
        self.llm = llm

    def run(
        self,
        *,
        model: str,
        history: List[ChatMessage],
        pdf_text: str,
        user_goal: str,
    ) -> AgentResponse:
        t0 = time.time()

        system = ChatMessage(role="system", content=_PDF_SYSTEM)

        user = ChatMessage(
            role="user",
            content=(
                f"OBJETIVO DO USUÁRIO:\n{user_goal}\n\n"
                f"TEXTO EXTRAÍDO DO PDF (pode estar parcial):\n{pdf_text[:_MAX_PDF_CHARS]}"
            ),
        )

        text = self.llm.chat(model=model, messages=[system, *history, user])

        return AgentResponse(
            text=text,
            used_model=model,
            latency_ms=int((time.time() - t0) * 1000),
        )