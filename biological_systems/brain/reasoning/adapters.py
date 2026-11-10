"""Reasoning adapters: replaceable inference providers behind a common interface."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Protocol


@dataclass
class ReasoningResult:
    text: str
    confidence: float = 0.5
    provider: str = "unknown"
    metadata: dict[str, Any] = field(default_factory=dict)


class ReasoningAdapter(Protocol):
    name: str

    async def generate(self, prompt: str, context: dict[str, Any] | None = None) -> ReasoningResult: ...


class LocalStubAdapter:
    """Deterministic stub adapter for development and tests. Not an LLM."""

    name = "local-stub"

    async def generate(self, prompt: str, context: dict[str, Any] | None = None) -> ReasoningResult:
        context = context or {}
        return ReasoningResult(
            text=f"[stub] {prompt[:200]}",
            confidence=0.3,
            provider=self.name,
            metadata={"context_keys": list(context.keys())},
        )


class OpenAICompatibleAdapter:
    """Adapter for any OpenAI-compatible chat endpoint. Requires httpx; network optional."""

    def __init__(self, base_url: str, model: str, api_key: str = ""):
        self.base_url = base_url.rstrip("/")
        self.model = model
        self.api_key = api_key
        self.name = f"openai-compat:{model}"

    async def generate(self, prompt: str, context: dict[str, Any] | None = None) -> ReasoningResult:
        import httpx

        headers = {"Content-Type": "application/json"}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        messages = []
        if context:
            messages.append({"role": "system", "content": str(context)})
        messages.append({"role": "user", "content": prompt})
        payload = {"model": self.model, "messages": messages, "temperature": 0.2}
        async with httpx.AsyncClient(timeout=60) as client:
            r = await client.post(f"{self.base_url}/chat/completions", json=payload, headers=headers)
            r.raise_for_status()
            data = r.json()
        text = data["choices"][0]["message"]["content"]
        return ReasoningResult(text=text, confidence=0.6, provider=self.name, metadata={"raw": data})


def get_default_adapter() -> ReasoningAdapter:
    return LocalStubAdapter()
