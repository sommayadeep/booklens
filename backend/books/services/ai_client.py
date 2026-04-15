from __future__ import annotations

import os
from typing import Optional


class AIClient:
    """
    Supports:
    - OpenAI hosted API (LLM_PROVIDER=openai)
    - LM Studio via OpenAI-compatible API (LLM_PROVIDER=lmstudio)
    Fallback: None, caller handles heuristic responses.
    """

    def __init__(self) -> None:
        self.provider = os.getenv("LLM_PROVIDER", "none").lower()
        self.model = os.getenv("LLM_MODEL", "gpt-4o-mini")
        self.api_key = os.getenv("OPENAI_API_KEY", "")
        self.base_url = os.getenv("LLM_BASE_URL", "")
        self._client = self._build_client()

    def _build_client(self):
        if self.provider not in {"openai", "lmstudio"}:
            return None
        try:
            from openai import OpenAI

            kwargs = {}
            if self.api_key:
                kwargs["api_key"] = self.api_key
            if self.provider == "lmstudio":
                kwargs["base_url"] = self.base_url or "http://localhost:1234/v1"
                kwargs.setdefault("api_key", self.api_key or "lm-studio")

            return OpenAI(**kwargs)
        except Exception:
            return None

    def generate(
        self,
        *,
        system_prompt: str,
        user_prompt: str,
        temperature: float = 0.2,
        max_tokens: int = 350,
    ) -> Optional[str]:
        if self._client is None:
            return None

        try:
            response = self._client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                temperature=temperature,
                max_tokens=max_tokens,
            )
            if not response.choices:
                return None
            return (response.choices[0].message.content or "").strip() or None
        except Exception:
            return None
