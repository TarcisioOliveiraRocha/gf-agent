# -*- coding: utf-8 -*-
"""
Camada de governança e conformidade.
Pode evoluir para LGPD, compliance e auditoria.
"""
from __future__ import annotations

import re


class PolicyService:
    _EMAIL_REGEX = re.compile(r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+")
    _CPF_REGEX = re.compile(r"\b\d{3}\.\d{3}\.\d{3}-\d{2}\b")
    _CNPJ_REGEX = re.compile(r"\b\d{2}\.\d{3}\.\d{3}/\d{4}-\d{2}\b")

    def sanitize(self, text: str) -> str:
        """Remove dados sensíveis antes de enviar ao LLM."""
        text = self._EMAIL_REGEX.sub("[EMAIL_REDACTED]", text)
        text = self._CPF_REGEX.sub("[CPF_REDACTED]", text)
        text = self._CNPJ_REGEX.sub("[CNPJ_REDACTED]", text)
        return text

    def validate(self, text: str) -> str:
        """
        Ponto de extensão para bloqueio de conteúdo inadequado.
        Por enquanto retorna o texto sanitizado sem alteração.
        """
        return text