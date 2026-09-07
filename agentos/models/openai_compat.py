"""OpenAI-compatible chat-completions provider.

Serves DeepSeek, GLM and any OpenAI-compatible endpoint (including local
servers). Cost is estimated from token usage against the model's price table.
"""

from __future__ import annotations

import httpx

from agentos.config import Settings
from agentos.domain.models import ModelDef, ModelRequest, ModelResponse

from .provider import Provider


class OpenAICompatProvider(Provider):
    def __init__(self, settings: Settings, model_defs: dict[str, ModelDef],
                 name: str, base_url: str, api_key: str) -> None:
        super().__init__(settings, model_defs)
        self.name = name
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key

    def is_configured(self) -> bool:
        return bool(self.api_key and self.base_url)

    async def complete(self, request: ModelRequest) -> ModelResponse:
        model = self.model_defs.get(request.model_id)
        if model is None:
            return ModelResponse(request_id=request.request_id, model_id=request.model_id,
                                 error=f"unknown model {request.model_id}")
        if not self.is_configured():
            return ModelResponse(request_id=request.request_id, model_id=request.model_id,
                                 error=f"provider {self.name} not configured (no API key)")
        messages: list[dict] = []
        if request.system:
            messages.append({"role": "system", "content": request.system})
        messages.extend(request.messages)
        payload = {
            "model": model.name,
            "messages": messages,
            "temperature": request.temperature,
            "max_tokens": request.max_tokens,
        }
        if request.tools:
            payload["tools"] = request.tools
            payload["tool_choice"] = "auto"
        try:
            async with httpx.AsyncClient(timeout=120) as client:
                resp = await client.post(
                    f"{self.base_url}/chat/completions",
                    headers={"Authorization": f"Bearer {self.api_key}",
                             "Content-Type": "application/json"},
                    json=payload,
                )
                resp.raise_for_status()
                data = resp.json()
        except Exception as exc:  # noqa: BLE001
            return ModelResponse(request_id=request.request_id, model_id=request.model_id,
                                 error=f"{self.name} request failed: {exc}")
        choice = (data.get("choices") or [{}])[0]
        message = choice.get("message", {})
        usage = data.get("usage", {})
        prompt_tokens = int(usage.get("prompt_tokens", 0))
        completion_tokens = int(usage.get("completion_tokens", 0))
        cost = self.estimate_cost(model, prompt_tokens, completion_tokens)
        tool_calls: list[dict] = []
        for tc in message.get("tool_calls") or []:
            tool_calls.append({
                "id": tc.get("id", ""),
                "name": (tc.get("function", {}) or {}).get("name", ""),
                "arguments": (tc.get("function", {}) or {}).get("arguments", "{}"),
            })
        return ModelResponse(
            request_id=request.request_id,
            model_id=request.model_id,
            content=message.get("content") or "",
            tool_calls=tool_calls,
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            total_tokens=prompt_tokens + completion_tokens,
            estimated_cost=cost,
            finish_reason=choice.get("finish_reason", "stop"),
        )