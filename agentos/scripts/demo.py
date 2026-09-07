"""Offline end-to-end demonstration.

Runs the full 0 → 100 workflow on a demo project using the EchoProvider
(zero API keys required). Exercises: project creation, the LangGraph workflow,
agent instantiation, tool calls with real artifacts, budget/cost tracking,
events, audit, and the human-approval gate on deployment.
"""

from __future__ import annotations

from agentos.bootstrap import build_app
from agentos.domain.models import ApprovalStatus


async def run_demo(auto_approve: bool = True) -> dict:
    print("=" * 64)
    print("  AGENT OS — OFFLINE END-TO-END DEMONSTRATION")
    print("  (EchoProvider · no API keys required)")
    print("=" * 64)

    svc = await build_app()
    counts = {
        "agents": len(await svc.agent_registry.list()),
        "skills": len(await svc.skill_registry.list()),
        "models": len(await svc.model_registry.list()),
    }
    print(f"\nSeeded: {counts['agents']} agents · {counts['skills']} skills · {counts['models']} models")

    project = await svc.projects.create(
        "Demo — AI Marketplace SaaS",
        "Validate and build a marketplace SaaS that connects freelancers with "
        "small agencies. Use the full 0→100 pipeline.",
        created_by="human", workflow_id="zero_to_hundred",
    )
    print(f"\n🚀 Project created: {project.project_id} ({project.name})")

    print("\n▶ Running workflow zero_to_hundred …")
    run = await svc.engine.run_workflow("zero_to_hundred", project.project_id)

    # handle approval gates (deployment requires human approval)
    while run.get("status") == "awaiting_approval":
        pending = await svc.approvals.pending()
        if not pending:
            break
        for approval in pending:
            print(f"  ⚠️  Approval required: {approval.action} by {approval.agent_name}")
            if auto_approve:
                print(f"     → approving {approval.approval_id} (demo auto-approve)")
                resumed = await svc.engine.approve(approval.approval_id,
                                                   ApprovalStatus.APPROVED.value,
                                                   decided_by="demo")
                if isinstance(resumed, dict):
                    run = resumed
            else:
                print(f"     → run `agent-os approvals approve {approval.approval_id}` to continue")

    print("\n─" * 64)
    print(f"  WORKFLOW STATUS: {run.get('status', '?').upper()}")
    print("─" * 64)
    for stage_id, result in (run.get("stage_results") or {}).items():
        mark = {"completed": "✅", "failed": "❌", "awaiting_approval": "🟠"}.get(result.get("status"), "·")
        model = result.get("model") or "-"
        arts = len(result.get("artifacts") or [])
        print(f"  {mark} {stage_id:<24} {result.get('status'):<16} model={model:<10} artifacts={arts}")

    project = await svc.projects.get(project.project_id)
    tasks = await svc.tasks.by_project(project.project_id)
    events = await svc.events.recent(limit=500)
    budgets = await svc.budgets.summary()
    spend = sum(b.get("spent_month", 0) for b in budgets)

    print("\n─" * 64)
    print("  SUMMARY")
    print("─" * 64)
    print(f"  Project status:  {project.status.value}")
    print(f"  Tasks created:   {len(tasks)}")
    print(f"  Completed:       {sum(1 for t in tasks if t.status.value == 'completed')}")
    print(f"  Failed:          {sum(1 for t in tasks if t.status.value == 'failed')}")
    print(f"  Artifacts:       {len(project.artifacts)}")
    for artifact in project.artifacts[:8]:
        print(f"    · {artifact}")
    print(f"  Events emitted:  {len(events)} (sample: {', '.join(sorted({e.type for e in events})[:8])})")
    print(f"  Spend (echo):    ${spend:.4f}")
    print(f"  Approvals:       {len(await svc.approvals.all())} recorded")

    print("\nDone. Start the full system with `agent-os start` and open the admin UI "
          "at http://localhost:8300 — add API keys in `.env` to go live with real models.")
    await svc.close()
    return {"status": run.get("status"), "project_id": project.project_id}