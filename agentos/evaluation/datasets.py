"""Regression datasets for benchmark runs.

A dataset is a JSONL file: one task per line with the fields the benchmark
runner needs. Datasets live in eval_sets/ and are loadable by name — the
system can answer "which agent/model/skill performs best on this dataset"
by running it and comparing records.

Skills contribute their own evaluation cases via `evals/cases.yaml` inside
the skill directory (skill-specific regression: "did the skill perform the
task correctly?", not "did it return text?"). Those datasets run through the
SAME benchmark runner — there is no second evaluation framework.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Optional

import yaml
from pydantic import BaseModel, Field


class DatasetItem(BaseModel):
    title: str
    description: str = ""
    agent: Optional[str] = None
    skill: Optional[str] = None  # skill under test; recorded on EvaluationRecord
    required_artifacts: int = Field(default=1, ge=0)
    min_output_len: int = Field(default=120, ge=0)
    expected_markers: list[str] = Field(default_factory=list)
    priority: str = "normal"


class RegressionDataset(BaseModel):
    name: str
    description: str = ""
    items: list[DatasetItem] = Field(default_factory=list)

    @classmethod
    def load(cls, path: Path) -> "RegressionDataset":
        items = []
        for line in path.read_text(errors="replace").splitlines():
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            items.append(DatasetItem(**json.loads(line)))
        return cls(name=path.stem, items=items)

    @classmethod
    def load_yaml(cls, path: Path, fallback_name: str = "") -> "RegressionDataset":
        """Load skill evaluation cases from `evals/cases.yaml`.

        Format (top-level map):

            description: ...
            cases:
              - title: ...
                description: ...
                agent: reddit-researcher
                skill: reddit-research
                expected_markers: ["pain", "evidence"]
                min_output_len: 120
        """
        raw = yaml.safe_load(path.read_text(errors="replace")) or {}
        if isinstance(raw, list):  # tolerate a bare list of cases
            raw = {"cases": raw}
        items = [DatasetItem(**{**case, "skill": case.get("skill") or fallback_name.replace("skill:", "")})
                 for case in raw.get("cases", [])]
        return cls(name=fallback_name or path.parent.parent.name, items=items,
                   description=raw.get("description", ""))


def load_dataset(name: str, root: Optional[Path] = None,
                 skills_root: Optional[Path] = None) -> Optional[RegressionDataset]:
    """Load a dataset by name. Checks eval_sets/<name>.jsonl first, then
    falls back to skill evaluation cases (skills/<dept>/<id>/evals/cases.yaml)
    so `agent-os evaluate <skill_id>` works directly."""
    root = root or Path("eval_sets")
    path = root / f"{name}.jsonl"
    if path.exists():
        return RegressionDataset.load(path)
    if name.startswith("skill:"):
        name = name[len("skill:"):]
    skills_root = skills_root or Path("skills")
    if skills_root.exists():
        for cases in skills_root.rglob("evals/cases.yaml"):
            if cases.parent.parent.name == name:
                return RegressionDataset.load_yaml(cases, fallback_name=f"skill:{name}")
    return None


def list_datasets(root: Optional[Path] = None,
                  skills_root: Optional[Path] = None) -> list[str]:
    root = root or Path("eval_sets")
    names = [p.stem for p in root.glob("*.jsonl")] if root.exists() else []
    skills_root = skills_root or Path("skills")
    if skills_root.exists():
        names += [f"skill:{p.parent.parent.name}"
                  for p in skills_root.rglob("evals/cases.yaml")]
    return sorted(set(names))