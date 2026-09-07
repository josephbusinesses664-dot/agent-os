"""Provider abstraction.

A provider turns a ModelRequest into a ModelResponse. Providers are pluggable:
register a new provider with one line in `build_providers`. Nothing in the
rest of the system cares which provider served a call.
"""

from __future__ import annotations

from abc import ABC, abstractmethod

from agentos.config import Settings
from agentos.domain.models import ModelDef, ModelRequest, ModelResponse


class Provider(ABC):
    name: str = "base"

    def __init__(self, settings: Settings, model_defs: dict[str, ModelDef]) -> None:
        self.settings = settings
        self.model_defs = model_defs

    @abstractmethod
    async def complete(self, request: ModelRequest) -> ModelResponse:
        """Complete a request. Must fill estimated_cost from token usage."""

    def estimate_cost(self, model: ModelDef, prompt_tokens: int, completion_tokens: int) -> float:
        return (
            prompt_tokens / 1_000_000 * model.price_in_per_million
            + completion_tokens / 1_000_000 * model.price_out_per_million
        )

    def is_configured(self) -> bool:
        return True


def build_providers(settings: Settings, model_defs: dict[str, ModelDef]) -> dict[str, Provider]:
    from .anthropic import AnthropicProvider
    from .mock import EchoProvider
    from .openai_compat import OpenAICompatProvider

    providers: dict[str, Provider] = {
        "echo": EchoProvider(settings, model_defs),
    }
    if settings.anthropic_api_key:
        providers["anthropic"] = AnthropicProvider(settings, model_defs)
    if settings.deepseek_api_key:
        providers["deepseek"] = OpenAICompatProvider(
            settings, model_defs, name="deepseek",
            base_url=settings.deepseek_base_url,
            api_key=settings.deepseek_api_key or "",
        )
    if settings.glm_api_key:
        providers["glm"] = OpenAICompatProvider(
            settings, model_defs, name="glm",
            base_url=settings.glm_base_url,
            api_key=settings.glm_api_key or "",
        )
    if settings.openai_compat_api_key and settings.openai_compat_base_url:
        providers["openai_compat"] = OpenAICompatProvider(
            settings, model_defs, name="openai_compat",
            base_url=settings.openai_compat_base_url or "",
            api_key=settings.openai_compat_api_key or "",
        )
    return providers