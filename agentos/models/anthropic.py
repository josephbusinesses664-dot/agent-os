"""Anthropic Messages API provider (Claude)."""

from __future__ import annotations

import json

import httpx

from agentos.config import Settings
from agentos.domain.models import ModelDef, ModelRequest, ModelResponse

from .provider import Provider


class AnthropicProvider(Provider):
    def __init__(self, settings: Settings, model_defs: dict[str, ModelDef]) -> None:
        super().__init__(settings, model_defs)
        self.name = "anthropic"
        self.base_url = settings.anthropic_base_url.rstrip("/")
        self.api_key = settings.anthropic_api_key or ""

    def is_configured(self) -> bool:
        return bool(self.api_key)

    async def complete(self, request: ModelRequest) -> ModelResponse:
        model = self.model_defs.get(request.model_id)
        if model is None:
            return ModelResponse(request_id=request.request_id, model_id=request.model_id,
                                 error=f"unknown model {request.model_id}")
        if not self.is_configured():
            return ModelResponse(request_id=request.request_id, model_id=request.model_id,
                                 error="anthropic provider not configured (no ANTHROPIC_API_KEY)")
        messages: list[dict] = []
        for m in request.messages:
            if m.get("role") == "system":
                continue  # system goes in the top-level field
            messages.append({"role": m.get("role", "user"), "content": m.get("content", "")})
        if not messages:
            messages = [{"role": "user", "content": "(empty request)"}]
        payload: dict = {
            "model": model.name,
            "max_tokens": request.max_tokens,
            "messages": messages,
        }
        if request.system:
            payload["system"] = request.system
        try:
            async with httpx.AsyncClient(timeout=120) as client:
                resp = await client.post(
                    f"{self.base_url}/v1/messages",
                    headers={"x-api-key": self.api_key, "anthropic-version": "2023-06-01",
                             "content-type": "application/json"},
                    json=payload,
                )
                resp.raise_for_status()
                data = resp.json()
        except Exception as exc:  # noqa: BLE001
            return ModelResponse(request_id=request.request_id, model_id=request.model_id,
                                 error=f"anthropic request failed: {exc}")
        blocks = data.get("content", [])
        text_parts = [b.get("text", "") for b in blocks if b.get("type") == "text"]
        tool_calls: list[dict] = []
        for b in blocks:
            if b.get("type") == "tool_use":
                tool_calls.append({
                    "id": b.get("id", ""),
                    "name": b.get("name", ""),
                    "arguments": json.dumps(b.get("input", {})),
                })
        usage = data.get("usage", {})
        prompt_tokens = int(usage.get("input_tokens", 0))
        completion_tokens = int(usage.get("output_tokens", 0))
        cost = self.estimate_cost(model, prompt_tokens, completion_tokens)
        return ModelResponse(
            request_id=request.request_id,
            model_id=request.model_id,
            content="\n".join(text_parts),
            tool_calls=tool_calls,
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            total_tokens=prompt_tokens + completion_tokens,
            estimated_cost=cost,
            finish_reason=data.get("stop_reason", "stop"),
        )