from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Literal

Role = Literal["system", "user", "assistant"]


@dataclass(frozen=True)
class ChatMessage:
    role: Role
    content: str


@dataclass(frozen=True)
class AgentResponse:
    text: str
    used_model: str
    latency_ms: int
    safety_notes: List[str] = field(default_factory=list)