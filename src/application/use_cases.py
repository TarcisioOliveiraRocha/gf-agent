# -*- coding: utf-8 -*-
from __future__ import annotations

import time
from typing import List

from src.application.policy_service import PolicyService
from src.domain.agent_identity import AGENT_IDENTITY
from src.domain.models import AgentResponse, ChatMessage
from src.domain.ports import LLMPort


class ChatAgentUC:
    def __init__(self, llm: LLMPort) -> None:
        self.llm = llm
        self.policy = PolicyService()

    def run(
        self,
        *,
        model: str,
        history: List[ChatMessage],
        user_text: str,
    ) -> AgentResponse:
        t0 = time.time()

        system = ChatMessage(role="system", content=AGENT_IDENTITY.strip())

        clean_text = self.policy.sanitize(user_text)
        validated_text = self.policy.validate(clean_text)

        messages = [system, *history, ChatMessage(role="user", content=validated_text)]
        text = self.llm.chat(model=model, messages=messages)

        return AgentResponse(
            text=text,
            used_model=model,
            latency_ms=int((time.time() - t0) * 1000),
        )