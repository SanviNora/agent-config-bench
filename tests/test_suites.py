from pathlib import Path

from agent_config_bench.graders.checks import validate_suite_balance
from agent_config_bench.schemas import TaskSuite

ROOT = Path(__file__).resolve().parents[1]


def test_dev_and_heldout_balance():
    for name in ("healthcare_dev", "healthcare_heldout"):
        suite = TaskSuite.from_path(ROOT / "suites" / f"{name}.json")
        problems = validate_suite_balance(suite)
        assert problems == [], problems
        assert len(suite.tasks) == 30


def test_heldout_ids_disjoint_from_dev():
    dev = TaskSuite.from_path(ROOT / "suites/healthcare_dev.json")
    held = TaskSuite.from_path(ROOT / "suites/healthcare_heldout.json")
    assert set(t.id for t in dev.tasks).isdisjoint(set(t.id for t in held.tasks))
    # queries should not be exact duplicates
    assert set(t.query for t in dev.tasks).isdisjoint(set(t.query for t in held.tasks))


def test_robustness_suite_loads():
    suite = TaskSuite.from_path(ROOT / "suites/robustness_tool_faults.json")
    assert suite.split == "robustness"
    assert len(suite.tasks) >= 10
    assert any(t.inject_tool_fault for t in suite.tasks)
