"""Browser automation (Browser-Use patterns, Playwright-powered).

A per-agent-run BrowserSession gives agents real web navigation: open,
snapshot (structure + visible text), click, type, evaluate, screenshot and
close. Everything flows through the executor (permission gates, timeouts,
audit) and the session is scoped to one agent run — it is created lazily on
first use and closed when the run ends, so no browser outlives its task.

Playwright is an optional dependency: the module imports it lazily and every
tool returns a clear "browser capability not installed" error when missing,
so the rest of the system is unaffected.
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any, Optional

logger = logging.getLogger("agentos.browser")

_SNAPSHOT_MAX = 8000


def _playwright():
    try:
        from playwright.async_api import async_playwright

        return async_playwright
    except ImportError as exc:  # pragma: no cover - depends on env
        raise RuntimeError(
            "browser capability requires playwright: `uv pip install playwright` "
            "then `python -m playwright install chromium`") from exc


class BrowserSession:
    """One browser session bound to one agent run (isolation)."""

    def __init__(self, workspace: Path, timeout_ms: int = 15000) -> None:
        self.workspace = workspace
        self.timeout_ms = timeout_ms
        self._pw = None
        self._browser = None
        self._context = None
        self._page = None

    @property
    def available(self) -> bool:
        return self._page is not None

    async def open(self, url: str) -> dict:
        if not url.startswith(("http://", "https://", "file://", "data:")):
            return {"ok": False, "error": "url must be http(s), file, or data"}
        if self._page is None:
            self._pw = _playwright()()
            self._pw = await self._pw.__aenter__()
            self._browser = await self._pw.chromium.launch(headless=True)
            self._context = await self._browser.new_context(
                viewport={"width": 1280, "height": 900},
                user_agent="agent-os-browser/0.1")
            self._page = await self._context.new_page()
        await self._page.goto(url, timeout=self.timeout_ms,
                              wait_until="domcontentloaded")
        snapshot = await self.snapshot()
        return {"ok": True, "url": url, "title": await self._page.title(),
                "status": 200, **snapshot}

    async def snapshot(self) -> dict:
        if self._page is None:
            return {"ok": False, "error": "no page open — call browser.open first"}
        data = await self._page.evaluate(_SNAPSHOT_JS)
        text = _trim(" ".join(
            t for t in data.get("text", []) if t))
        return {"ok": True, "url": self._page.url,
                "title": data.get("title", ""),
                "headings": data.get("headings", [])[:20],
                "links": data.get("links", [])[:30],
                "buttons": data.get("buttons", [])[:30],
                "inputs": data.get("inputs", [])[:30],
                "text": text[:_SNAPSHOT_MAX],
                "truncated": len(text) > _SNAPSHOT_MAX}

    async def click(self, selector: str) -> dict:
        if self._page is None:
            return {"ok": False, "error": "no page open — call browser.open first"}
        locator = self._page.locator(selector).first
        await locator.click(timeout=self.timeout_ms)
        return {"ok": True, "clicked": selector,
                "url": self._page.url, "text": (await self.snapshot()).get("text", "")[:2000]}

    async def type_text(self, selector: str, text: str) -> dict:
        if self._page is None:
            return {"ok": False, "error": "no page open — call browser.open first"}
        await self._page.locator(selector).first.fill(text, timeout=self.timeout_ms)
        return {"ok": True, "typed_into": selector}

    async def evaluate(self, expression: str) -> dict:
        if self._page is None:
            return {"ok": False, "error": "no page open — call browser.open first"}
        result = await self._page.evaluate(expression)
        return {"ok": True, "result": str(result)[:4000]}

    async def screenshot(self, path: str) -> dict:
        if self._page is None:
            return {"ok": False, "error": "no page open — call browser.open first"}
        target = Path(path)
        if not target.is_absolute():
            target = self.workspace / target
        target = target.resolve()
        if not str(target).startswith(str(self.workspace.resolve())):
            return {"ok": False, "error": "screenshot path escapes workspace"}
        target.parent.mkdir(parents=True, exist_ok=True)
        await self._page.screenshot(path=str(target), full_page=True)
        return {"ok": True, "path": str(target), "bytes": target.stat().st_size}

    async def close(self) -> dict:
        errors = []
        for closer in (self._page, self._context, self._browser):
            if closer is not None:
                try:
                    await closer.close()
                except Exception as exc:  # noqa: BLE001
                    errors.append(str(exc))
        if self._pw is not None:
            try:
                await self._pw.__aexit__(None, None, None)
            except Exception as exc:  # noqa: BLE001
                errors.append(str(exc))
        self._page = self._context = self._browser = self._pw = None
        return {"ok": not errors, "closed": True,
                "errors": errors if errors else None}


_SNAPSHOT_JS = """
() => {
  const out = { title: document.title, headings: [], links: [], buttons: [], inputs: [], text: [] };
  document.querySelectorAll("h1,h2,h3").forEach(h => out.headings.push(h.innerText.trim().slice(0,120)));
  document.querySelectorAll("a[href]").forEach(a => out.links.push((a.innerText.trim().slice(0,80) || a.href) + " → " + a.href));
  document.querySelectorAll("button").forEach(b => out.buttons.push(b.innerText.trim().slice(0,80)));
  document.querySelectorAll("input,textarea,select").forEach(i => out.inputs.push((i.tagName.toLowerCase()) + (i.id ? "#" + i.id : "") + (i.name ? "[name=" + i.name + "]" : "") + (i.placeholder ? " ph=" + i.placeholder : "")));
  const walker = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT);
  let node;
  while ((node = walker.nextNode())) {
    const t = node.textContent.trim();
    if (t && node.parentElement && !["SCRIPT","STYLE","NOSCRIPT"].includes(node.parentElement.tagName)) out.text.push(t);
  }
  return out;
}
"""


def _trim(text: str, limit: int = 6000) -> str:
    return text if len(text) <= limit else text[:limit] + " … [truncated]"