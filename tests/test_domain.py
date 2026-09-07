"""Domain model tests."""

from agentos.domain.models import (
    AgentDef,
    ModelDef,
    Task,
    TaskStatus,
    UsageRecord,
    new_id,
    utcnow,
)


def test_new_id_prefix():
    assert new_id("task").startswith("task_")
    assert new_id("task") != new_id("task")


def test_task_defaults():
    task = Task(task_id="t1", project_id="p1", title="T")
    assert task.status == TaskStatus.PENDING
    assert task.cost == 0.0
    assert task.dependencies == []
    assert task.created_at is not None


def test_agent_permissions():
    agent = AgentDef(id="a1", name="A", role="r",
                     permissions={"shell": "deny", "web.search": "allow"})
    assert agent.allows("web.search")
    assert not agent.allows("shell")
    # default-allow when unspecified
    assert agent.allows("filesystem.read")


def test_model_cost_estimation():
    model = ModelDef(id="m", provider="p", name="m", tier="t2",
                     price_in_per_million=1.0, price_out_per_million=3.0)
    # 1M prompt tokens + 1M completion tokens = $1 + $3
    cost = (1_000_000 / 1e6 * model.price_in_per_million
            + 1_000_000 / 1e6 * model.price_out_per_million)
    assert cost == 4.0


def test_usage_record_roundtrip():
    record = UsageRecord(provider="deepseek", model="deepseek-chat",
                         prompt_tokens=100, completion_tokens=50,
                         estimated_cost=0.01, project_id="p1")
    data = record.model_dump(mode="json")
    restored = UsageRecord.model_validate(data)
    assert restored.provider == "deepseek"
    assert restored.estimated_cost == 0.01


def test_utcnow():
    now = utcnow()
    assert now.tzinfo is not None