"""Lightweight local checks for suite validation (not the live claim verifier).

The production verbatim-quote grader lives in evidence-mcp-agent. These helpers
validate task-suite integrity and stub-runner outputs in CI.
"""

from __future__ import annotations

from collections import Counter

from agent_config_bench.schemas import Task, TaskSuite


REQUIRED_DEV_COUNTS = {
    "label": 12,
    "ambiguous_product": 3,
    "comparison": 3,
    "trials": 4,
    "coverage": 3,
    "refusal": 2,
    "off_label": 1,
    "not_found": 2,
}


def validate_suite_balance(suite: TaskSuite, expected: dict[str, int] | None = None) -> list[str]:
    """Return a list of problems (empty means OK).

    Pass ``expected={}`` to skip category-count checks (robustness suites).
    Pass ``expected=None`` to use the standard 30-task healthcare mix.
    """
    counts = Counter(t.category for t in suite.tasks)
    problems = []
    ids = [t.id for t in suite.tasks]
    if len(ids) != len(set(ids)):
        problems.append("duplicate task ids")
    cat_expected = REQUIRED_DEV_COUNTS if expected is None else expected
    for cat, n in cat_expected.items():
        if counts.get(cat, 0) != n:
            problems.append(f"category {cat}: got {counts.get(cat, 0)}, want {n}")
    for t in suite.tasks:
        if not t.query.strip():
            problems.append(f"{t.id}: empty query")
    return problems


def status_ok(task: Task, status: str) -> bool:
    expect = task.expect_status
    allowed = expect if isinstance(expect, list) else [expect]
    return status in allowed
