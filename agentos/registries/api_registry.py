"""API Registry.

A catalog of public/agent-friendly APIs with metadata (auth, pricing, rate
limits, commercial use, reliability). Agents discover APIs through the
registry; nothing is called automatically just because it exists.

The curated catalog is a small, hand-picked seed drawn from the public-apis
ecosystem — the registry is designed to grow to thousands of entries.
"""

from __future__ import annotations

from typing import Any, Optional

import httpx

from agentos.db.store import EntityStore
from agentos.domain.models import ApiDef


def curated_catalog() -> list[ApiDef]:
    return [
        ApiDef(api="hackernews", category="community-intelligence",
               description="Hacker News stories, comments and search (Algolia API).",
               base_url="https://hn.algolia.com/api/v1", documentation="https://hn.algolia.com/api",
               agent_compatibility=5, rate_limit="10k req/h"),
        ApiDef(api="reddit", category="community-intelligence",
               description="Reddit JSON endpoints for subreddit + thread data (read-only, public).",
               base_url="https://www.reddit.com",
               documentation="https://github.com/reddit-archive/reddit/wiki/JSON",
               agent_compatibility=4, rate_limit="60 req/min"),
        ApiDef(api="github", category="engineering",
               description="GitHub REST API: repos, issues, code search (token recommended).",
               authentication="api_key", base_url="https://api.github.com",
               documentation="https://docs.github.com/rest", agent_compatibility=5,
               rate_limit="60 req/h unauth, 5000/h auth"),
        ApiDef(api="openlibrary", category="data",
               description="Open library metadata and search.",
               base_url="https://openlibrary.org", documentation="https://openlibrary.org/developers/api",
               agent_compatibility=3),
        ApiDef(api="open-meteo", category="data",
               description="Open weather forecast API, no key required.",
               base_url="https://api.open-meteo.com/v1", documentation="https://open-meteo.com/en/docs",
               agent_compatibility=4),
        ApiDef(api="wikipedia", category="research",
               description="Wikipedia search and article extracts.",
               base_url="https://en.wikipedia.org/w/api.php", documentation="https://www.mediawiki.org/wiki/API",
               agent_compatibility=4),
        ApiDef(api="crunchbase", category="business-intelligence",
               description="Company funding and market data (key required).",
               authentication="api_key", pricing="paid", base_url="https://api.crunchbase.com/api/v4",
               documentation="https://data.crunchbase.com", agent_compatibility=3),
        ApiDef(api="serper", category="search",
               description="Google search API used for web research (key required).",
               authentication="api_key", pricing="paid", base_url="https://google.serper.dev",
               documentation="https://serper.dev", agent_compatibility=5, rate_limit="300 req/m"),
        ApiDef(api="firecrawl", category="search",
               description="Web scraping / crawling as an API (key required).",
               authentication="api_key", pricing="paid", base_url="https://api.firecrawl.dev/v1",
               documentation="https://docs.firecrawl.dev", agent_compatibility=5),
    ]


def evaluate_api(api: ApiDef) -> dict[str, Any]:
    """Score per the API-evaluation rubric (availability, cost, auth, limits,
    docs, reliability, commercial use, data quality, security, agent fit)."""
    score = 0.0
    notes: list[str] = []
    if api.pricing == "free":
        score += 2.0
    elif api.pricing == "freemium":
        score += 1.0
        notes.append("freemium — check quota")
    if api.authentication == "none":
        score += 1.5
        notes.append("no auth required")
    elif api.authentication == "api_key":
        score += 0.5
        notes.append("api key required")
    if api.commercial_use:
        score += 1.0
    else:
        notes.append("commercial use restricted")
    score += min(api.agent_compatibility, 5) * 0.4
    if api.documentation:
        score += 0.5
    if api.reliability in ("good", "excellent"):
        score += 0.5
    verdict = "recommended" if score >= 4.0 else ("conditional" if score >= 2.5 else "discouraged")
    return {"score": round(score, 2), "verdict": verdict, "notes": notes}


class ApiRegistry:
    def __init__(self, store: EntityStore) -> None:
        self.store = store
        self._collection = "apis"
        self._api_keys: dict[str, str] = {}

    async def seed_defaults(self) -> int:
        existing = await self.list()
        if existing:
            return len(existing)
        for api in curated_catalog():
            await self.store.save(self._collection, api)
        return len(curated_catalog())

    async def list(self, enabled_only: bool = True) -> list[ApiDef]:
        apis = await self.store.list(self._collection, ApiDef)
        apis.sort(key=lambda a: a.api)
        return [a for a in apis if a.enabled or not enabled_only]

    async def get(self, api: str) -> Optional[ApiDef]:
        return await self.store.get(self._collection, api, ApiDef)

    async def register(self, api: ApiDef) -> ApiDef:
        await self.store.save(self._collection, api)
        return api

    async def set_key(self, api: str, key: str) -> None:
        self._api_keys[api] = key

    def evaluate(self, api: ApiDef) -> dict[str, Any]:
        return evaluate_api(api)

    async def call_api(self, api_name: str, path: str = "", params: Optional[dict] = None) -> dict:
        api = await self.get(api_name)
        if not api or not api.enabled:
            return {"ok": False, "error": f"API {api_name} unavailable"}
        if api.authentication == "api_key" and api_name not in self._api_keys:
            return {"ok": False, "error": f"no API key configured for {api_name}"}
        headers = {"User-Agent": "agent-os/0.1"}
        if api_name in self._api_keys:
            if api_name == "github":
                headers["Authorization"] = f"Bearer {self._api_keys[api_name]}"
                headers["X-GitHub-Api-Version"] = "2022-11-28"
            elif api_name == "serper":
                headers["X-API-KEY"] = self._api_keys[api_name]
            else:
                headers["Authorization"] = f"Bearer {self._api_keys[api_name]}"
        url = f"{api.base_url}{path}"
        try:
            async with httpx.AsyncClient(timeout=25, headers=headers) as client:
                resp = await client.get(url, params=params or {})
                resp.raise_for_status()
                try:
                    body = resp.json()
                except ValueError:
                    body = {"raw": resp.text[:8000]}
            return {"ok": True, "api": api_name, "status": resp.status_code, "data": body}
        except Exception as exc:  # noqa: BLE001
            return {"ok": False, "error": f"{api_name} call failed: {exc}"}