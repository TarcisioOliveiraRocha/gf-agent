from __future__ import annotations
from abc import ABC, abstractmethod
from typing import List
from .models import ChatMessage

class LLMPort(ABC):
    @abstractmethod
    def chat(self, *, model: str, messages: List[ChatMessage]) -> str:
        raise NotImplementedError