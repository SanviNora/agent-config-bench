"""Runner interfaces for bringing your own agent into Agent Config Bench.

The current healthcare evidence agent is evaluated upstream
(``cmg-eval-agent`` in evidence-mcp-agent). This module defines the contract
so additional runners (Anthropic API, OpenAI Responses, Ollama) can plug in
without changing the analyzer.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

from agent_config_bench.schemas import ConfigSpec, Task


class AgentRunner(ABC):
    """Execute one task under one config and return a run row dict."""

    @abstractmethod
    def run(self, task: Task, config: ConfigSpec) -> dict[str, Any]:
        raise NotImplementedError


class ReportLoaderRunner(AgentRunner):
    """Not a live runner: loads precomputed eval JSON rows (offline analysis)."""

    def __init__(self, rows_by_task_config: dict[tuple[str, str], dict[str, Any]]):
        self._rows = rows_by_task_config

    def run(self, task: Task, config: ConfigSpec) -> dict[str, Any]:
        key = (task.id, config.id)
        if key not in self._rows:
            raise KeyError(f"no precomputed row for {key}")
        return self._rows[key]


class StubRunner(AgentRunner):
    """Deterministic stub for CI: passes when status expectation is not_found."""

    def run(self, task: Task, config: ConfigSpec) -> dict[str, Any]:
        expect = task.expect_status
        statuses = expect if isinstance(expect, list) else [expect]
        # Stub "agent" refuses marketing and invents nothing.
        if task.category in ("refusal",) or "social media" in task.query.lower():
            status = "refused"
        elif task.category == "not_found" or task.id.startswith("N"):
            status = "not_found"
        else:
            status = "answered" if config.mcp_tools else "answered"
        passed = status in statuses
        return {
            "config": config.id,
            "task_id": task.id,
            "category": task.category,
            "passed": passed,
            "checks": {"status": passed},
            "claim_precision": 1.0 if config.mcp_tools else 0.0,
            "cost_usd_list_price": 0.0,
            "tool_calls": 2 if config.mcp_tools else 0,
            "latency_s": 0.01,
            "hallucinated_ncts": [],
            "failed_claim_reasons": [],
            "error": None,
            "status": status,
        }
