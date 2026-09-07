"""Prompt Library.

Prompts are versioned markdown files under prompts/ (one per agent role),
rendered with Jinja2 and composed from: role, task, skill bodies, project
context, memory, tool instructions, constraints and output format.

If a role has no prompt file, a minimal generic prompt is used — adding a new
agent must never require touching core code.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Optional

from jinja2 import BaseLoader, Environment, TemplateNotFound, meta
from jinja2.exceptions import TemplateSyntaxError

from agentos.config import Settings

GENERIC_PROMPT = """You are {{ role }} (agent id: {{ agent_id }}).

{{ description }}

## Responsibilities
{{ responsibilities }}

## Project context
{{ project_context }}

## Task
{{ task }}

## Skills available (load only what is relevant)
{{ skills }}

## Tools available
{{ tools }}

## Constraints
- Never claim an action you did not perform. If a tool failed, say so.
- Prefer cheaper models for routine work; escalate genuinely hard problems.
- Record important decisions and lessons via memory tools.
{{ extra_constraints }}

## Output format
{{ output_format }}

## Reflection (required at the end of every response)
- What was I asked to do?
- What did I do?
- What worked?
- What failed?
- What remains?
- What should the next agent know?
"""


class PromptLibrary:
    def __init__(self, settings: Settings, prompts_root: Optional[Path] = None) -> None:
        self.settings = settings
        self.root = prompts_root or Path(__file__).resolve().parents[2] / "prompts"
        self.env = Environment(loader=BaseLoader(), autoescape=False)
        self._cache: dict[str, str] = {}

    def _load(self, role: str) -> str:
        if role in self._cache:
            return self._cache[role]
        path = self.root / f"{role}.md"
        text = None
        if path.exists():
            text = path.read_text(errors="replace")
        else:
            # prompt files may carry YAML frontmatter; strip it
            text = GENERIC_PROMPT
        try:
            self.env.parse(text)  # validate template syntax
            self._cache[role] = text
            return text
        except TemplateSyntaxError:
            self._cache[role] = GENERIC_PROMPT
            return GENERIC_PROMPT

    def render(self, role: str, context: dict[str, Any]) -> str:
        template = self.env.from_string(self._load(role))
        return template.render(**context)

    def available_roles(self) -> list[str]:
        if not self.root.exists():
            return []
        return sorted(p.stem for p in self.root.glob("*.md"))