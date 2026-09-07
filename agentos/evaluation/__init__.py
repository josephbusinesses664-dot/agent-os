"""Evaluation subsystem: deterministic + LLM-judge evaluation, regression
datasets, benchmark runner and cost-aware leaderboards."""

from .base import Evaluator, make_record
from .datasets import RegressionDataset, load_dataset, list_datasets
from .deterministic import DeterministicEvaluator
from .failure_analysis import (
    analyze_svc,
    best_match,
    classify_task,
    failure_summary,
    recommendations,
)
from .judge import LLMJudgeEvaluator
from .report import best_for, compare_capabilities, cost_vs_quality, leaderboard, trajectory_analysis
from .runner import BenchmarkRunner

__all__ = [
    "Evaluator",
    "make_record",
    "RegressionDataset",
    "load_dataset",
    "list_datasets",
    "DeterministicEvaluator",
    "LLMJudgeEvaluator",
    "BenchmarkRunner",
    "leaderboard",
    "cost_vs_quality",
    "trajectory_analysis",
    "best_for",
    "compare_capabilities",
    "classify_task",
    "failure_summary",
    "recommendations",
    "best_match",
    "analyze_svc",
]