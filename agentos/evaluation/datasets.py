"""Regression datasets for benchmark runs.

A dataset is a JSONL file: one task per line with the fields the benchmark
runner needs. Datasets live in eval_sets/ and are loadable by name — the
system can answer "which agent/model/skill performs best on this dataset"
by running it and comparing records.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Optional

from pydantic import BaseModel, Field


class DatasetItem(BaseModel):
    title: str
    description: str = ""
    agent: Optional[str] = None
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


def load_dataset(name: str, root: Optional[Path] = None) -> Optional[RegressionDataset]:
    root = root or Path("eval_sets")
    path = root / f"{name}.jsonl"
    if not path.exists():
        return None
    return RegressionDataset.load(path)


def list_datasets(root: Optional[Path] = None) -> list[str]:
    root = root or Path("eval_sets")
    if not root.exists():
        return []
    return sorted(p.stem for p in root.glob("*.jsonl"))