"""Capability system: turns skills into executable capabilities.

A skill can carry tools (built-in handler refs or inline python), hooks,
validators, permissions, model settings, examples and tests. The
CapabilityManager binds those tools into the ToolRegistry so the executor —
the single execution path — runs them like any other tool, with the same
permission and approval gates.

Inline code is executed in a restricted namespace (no __builtins__ imports,
only whitelisted helpers), so untrusted skill code cannot escape into the
host process.
"""

from __future__ import annotations

import logging

from agentos.domain.models import CapabilityTool, SkillDef, ToolDef
from agentos.registries.tool_registry import ToolRegistry

logger = logging.getLogger("agentos.capabilities")

# Whitelisted names available to inline capability code
_SAFE_BUILTINS = {
    "str": str, "int": int, "float": float, "bool": bool, "len": len,
    "dict": dict, "list": list, "tuple": tuple, "set": set,
    "min": min, "max": max, "sum": sum, "sorted": sorted, "range": range,
    "enumerate": enumerate, "zip": zip, "abs": abs, "round": round,
    "isinstance": isinstance, "type": type, "repr": repr, "any": any,
    "all": all, "filter": filter, "map": map, "Exception": Exception,
    "ValueError": ValueError, "KeyError": KeyError, "print": print,
    # deliberately absent: open, eval, exec, compile, __import__, getattr,
    # setattr, globals, locals — untrusted skill code cannot touch the host.
}

_INLINE_NAMESPACE = {
    "json": __import__("json"),
    "re": __import__("re"),
    "math": __import__("math"),
    "asyncio": __import__("asyncio"),
    "Path": __import__("pathlib").Path,
    "datetime": __import__("datetime"),
}


def _restricted_namespace() -> dict:
    namespace = dict(_INLINE_NAMESPACE)
    namespace["__builtins__"] = dict(_SAFE_BUILTINS)
    return namespace


def compile_handler(code: str, name: str):
    """Compile inline `async def handler(ctx, args) -> dict` source safely."""
    namespace = _restricted_namespace()
    try:
        exec(compile(code, f"<capability:{name}>", "exec"), namespace)  # noqa: S102
    except Exception as exc:  # noqa: BLE001
        raise ValueError(f"capability {name} failed to compile: {exc}") from exc
    handler = namespace.get("handler")
    if handler is None:
        raise ValueError(f"capability {name} must define `async def handler(ctx, args)`")
    return handler


def compile_validator(code: str, name: str):
    """Compile inline `async def validate(ctx, result) -> dict` source safely."""
    namespace = _restricted_namespace()
    try:
        exec(compile(code, f"<validator:{name}>", "exec"), namespace)  # noqa: S102
    except Exception as exc:  # noqa: BLE001
        raise ValueError(f"validator for {name} failed to compile: {exc}") from exc
    validator = namespace.get("validate")
    if validator is None:
        raise ValueError(f"validator for {name} must define `async def validate(ctx, result)`")
    return validator


class CapabilityManager:
    """Binds skill-attached tools/hooks/validators into the ToolRegistry."""

    def __init__(self, tools: ToolRegistry) -> None:
        self.tools = tools
        self._hooks: dict[str, dict[str, object]] = {}  # skill_id -> {"pre_<tool>": handler}
        self._validators: dict[str, list[object]] = {}  # skill_id -> [validator, ...]

    async def load_skill(self, skill: SkillDef) -> int:
        """Register every tool attached to a skill. Returns count registered."""
        count = 0
        for cap_tool in skill.tools:
            await self._register_cap_tool(skill.id, cap_tool)
            count += 1
        if skill.hooks:
            self._hooks[skill.id] = {}
            for hook_name, code in skill.hooks.items():
                try:
                    self._hooks[skill.id][hook_name] = compile_handler(code, f"{skill.id}:{hook_name}")
                except ValueError as exc:
                    logger.warning("skill %s hook %s skipped: %s", skill.id, hook_name, exc)
        if skill.validators:
            compiled = []
            for i, code in enumerate(skill.validators):
                try:
                    compiled.append(compile_validator(code, f"{skill.id}#{i}"))
                except ValueError as exc:
                    logger.warning("skill %s validator %d skipped: %s", skill.id, i, exc)
            self._validators[skill.id] = compiled
        return count

    async def _register_cap_tool(self, skill_id: str, cap: CapabilityTool) -> None:
        if not cap.name:
            return
        handler = None
        if cap.handler_ref:
            handler = self.tools.handler(cap.handler_ref)
            if handler is None:
                logger.warning("skill %s tool %s: unknown handler_ref %s",
                               skill_id, cap.name, cap.handler_ref)
        if handler is None and cap.code:
            try:
                handler = compile_handler(cap.code, f"{skill_id}:{cap.name}")
            except ValueError as exc:
                logger.warning("skill %s tool %s skipped: %s", skill_id, cap.name, exc)
                return
        if handler is None:
            return
        tool = ToolDef(
            name=cap.name,
            description=cap.description or f"Tool provided by skill {skill_id}.",
            permission_key=cap.permission_key or cap.name,
            risk_level=cap.risk_level,
            enabled=True,
            category="capability",
            config={"timeout_seconds": cap.timeout_seconds,
                    "cost_per_call": cap.cost_per_call,
                    "skill_id": skill_id, **cap.config},
        )
        await self.tools.register(tool, handler)

    # -- hooks / validators -------------------------------------------------
    def pre_hooks(self, skills: list[SkillDef], tool_name: str) -> list[object]:
        out = []
        for skill in skills:
            hooks = self._hooks.get(skill.id, {})
            for hook_name, handler in hooks.items():
                if hook_name == f"pre_{tool_name}":
                    out.append(handler)
        return out

    def post_hooks(self, skills: list[SkillDef], tool_name: str) -> list[object]:
        out = []
        for skill in skills:
            hooks = self._hooks.get(skill.id, {})
            for hook_name, handler in hooks.items():
                if hook_name == f"post_{tool_name}":
                    out.append(handler)
        return out

    def validators_for(self, skills: list[SkillDef]) -> list[object]:
        out = []
        for skill in skills:
            out.extend(self._validators.get(skill.id, []))
        return out

    async def validate_result(self, skills: list[SkillDef], ctx: Any,
                              tool_name: str, result: dict) -> dict:
        """Run validators from active skills over a tool result. A validator
        may annotate the result (e.g. mark it suspect) but not fabricate."""
        for validator in self.validators_for(skills):
            try:
                verdict = await validator(ctx, result)
            except Exception as exc:  # noqa: BLE001
                verdict = {"ok": False, "error": f"validator crashed: {exc}"}
            if isinstance(verdict, dict) and verdict.get("ok") is False:
                result = {**result, "ok": False,
                          "error": verdict.get("error", "skill validator rejected result"),
                          "validation_failed": True}
                break
            if isinstance(verdict, dict) and verdict.get("annotations"):
                result = {**result, "annotations": verdict["annotations"]}
        return result