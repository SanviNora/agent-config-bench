"""Shared schemas for task suites, run rows, and config matrices."""

from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, Field


Status = Literal["answered", "refused", "not_found"]
Category = Literal[
    "label",
    "ambiguous_product",
    "comparison",
    "trials",
    "coverage",
    "refusal",
    "off_label",
    "not_found",
    "tool_fault",
    "injection",
    "multi_hop",
    "budget",
]


class Task(BaseModel):
    id: str
    category: Category | str
    query: str
    expect_status: Status | list[Status]
    expect_review: bool | None = None
    allowed_brands: list[str] | None = None
    require_brands: list[str] | None = None
    require_sections: list[str] | None = None
    forbid_sections: list[str] | None = None
    require_source_ids: list[str] | None = None
    min_verified_claims: int | None = None
    max_claims: int | None = None
    min_trials: int | None = None
    summary_regex: str | None = None
    # Robustness / fault-injection metadata (optional)
    inject_tool_fault: str | None = None
    notes: str | None = None


class TaskSuite(BaseModel):
    name: str
    version: str = "1.0"
    split: Literal["dev", "heldout", "robustness"] = "dev"
    description: str = ""
    contamination_note: str = ""
    tasks: list[Task]

    @classmethod
    def from_path(cls, path: str | Any) -> "TaskSuite":
        import json
        from pathlib import Path

        p = Path(path)
        data = json.loads(p.read_text())
        if isinstance(data, list):
            return cls(
                name=p.stem,
                tasks=[Task.model_validate(t) for t in data],
            )
        return cls.model_validate(data)


class ConfigSpec(BaseModel):
    id: str
    label: str
    model: str | None = None
    mcp_tools: bool = False
    skills: bool = False
    notes: str = ""


class ConfigMatrix(BaseModel):
    name: str = "default"
    seed: int = 42
    bootstrap_resamples: int = 4000
    configs: list[ConfigSpec]


class RunRow(BaseModel):
    """Minimal shape expected from an upstream eval report row."""

    config: str
    task_id: str
    passed: bool
    category: str | None = None
    checks: dict[str, bool] = Field(default_factory=dict)
    claim_precision: float | None = None
    cost_usd_list_price: float | None = None
    tool_calls: int | None = None
    latency_s: float | None = None
    hallucinated_ncts: list[str] | None = None
    failed_claim_reasons: list[str] | None = None
    error: str | None = None
