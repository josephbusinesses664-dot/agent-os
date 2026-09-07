"""Seed the system: registries + optional demo project."""

from __future__ import annotations

from agentos.bootstrap import build_app


async def run_seed(with_project: bool = True) -> dict:
    svc = await build_app()
    counts = {
        "agents": len(await svc.agent_registry.list()),
        "skills": len(await svc.skill_registry.list()),
        "tools": len(await svc.tool_registry.list()),
        "models": len(await svc.model_registry.list()),
        "apis": len(await svc.api_registry.list()),
        "workflows": len(await svc.workflow_registry.list()),
    }
    print("Seeded registries:")
    for key, value in counts.items():
        print(f"  {key:<10} {value}")
    if with_project:
        project = await svc.projects.create(
            "AI Agency Demo", "Demonstration project for the Agent OS",
            workflow_id="zero_to_hundred",
        )
        print(f"  Demo project: {project.project_id}")
        counts["demo_project"] = project.project_id
    await svc.close()
    return counts