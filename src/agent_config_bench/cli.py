"""CLI: analyze | validate-suite | stub-run | report-paths."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import yaml

from agent_config_bench.analyze import run_analysis
from agent_config_bench.graders.checks import validate_suite_balance
from agent_config_bench.runners.base import StubRunner
from agent_config_bench.schemas import ConfigMatrix, ConfigSpec, TaskSuite

ROOT = Path(__file__).resolve().parents[2]


def cmd_analyze(args: argparse.Namespace) -> int:
    result = run_analysis(args.reports, out_root=Path(args.out) if args.out else None)
    slim = {
        k: {
            kk: v[kk]
            for kk in (
                "task_pass_rate",
                "ci95",
                "claim_precision",
                "cost_usd_per_task",
                "latency_s_median",
                "n_runs",
            )
        }
        for k, v in result["summary"].items()
    }
    print(json.dumps({"summary": slim, "paired": result["paired"]}, indent=2))
    return 0


def cmd_validate_suite(args: argparse.Namespace) -> int:
    suite = TaskSuite.from_path(args.suite)
    # None → standard 30-task healthcare mix; {} → id/query checks only
    expected: dict[str, int] | None
    if args.split == "robustness":
        expected = {}
    else:
        expected = None
    problems = validate_suite_balance(suite, expected=expected)
    if problems:
        print("FAIL")
        for p in problems:
            print(f"  - {p}")
        return 1
    print(f"OK  {suite.name}: {len(suite.tasks)} tasks, split={suite.split or args.split}")
    return 0


def cmd_stub_run(args: argparse.Namespace) -> int:
    suite = TaskSuite.from_path(args.suite)
    matrix = ConfigMatrix.model_validate(yaml.safe_load(Path(args.config).read_text()))
    runner = StubRunner()
    rows = []
    for cfg in matrix.configs:
        for task in suite.tasks:
            rows.append(runner.run(task, cfg))
    out = {"rows": rows, "meta": {"runner": "stub", "suite": suite.name, "matrix": matrix.name}}
    dest = Path(args.out)
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(json.dumps(out, indent=2))
    passed = sum(1 for r in rows if r["passed"])
    print(f"wrote {dest}  ({passed}/{len(rows)} stub passes)")
    return 0


def cmd_show_matrix(args: argparse.Namespace) -> int:
    matrix = ConfigMatrix.model_validate(yaml.safe_load(Path(args.config).read_text()))
    print(json.dumps(matrix.model_dump(), indent=2))
    return 0


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="agent-config-bench",
        description="Ablation framework for tool-using agents (analyze, validate, stub-run)",
    )
    sub = p.add_subparsers(dest="cmd", required=True)

    a = sub.add_parser("analyze", help="Analyze eval-*.json reports with bootstrap CIs")
    a.add_argument("reports", nargs="+", help="eval report JSON files")
    a.add_argument("--out", default=None, help="output root (default: repo root)")
    a.set_defaults(func=cmd_analyze)

    v = sub.add_parser("validate-suite", help="Validate task-suite balance and IDs")
    v.add_argument("suite", help="path to suite JSON")
    v.add_argument("--split", default="dev", choices=["dev", "heldout", "robustness"])
    v.set_defaults(func=cmd_validate_suite)

    s = sub.add_parser("stub-run", help="Run stub agent over a suite (CI / smoke)")
    s.add_argument("suite", help="path to suite JSON")
    s.add_argument("--config", default=str(ROOT / "configs/default.yaml"))
    s.add_argument("--out", default=str(ROOT / "results/stub_eval.json"))
    s.set_defaults(func=cmd_stub_run)

    m = sub.add_parser("show-matrix", help="Print a config matrix YAML as JSON")
    m.add_argument("--config", default=str(ROOT / "configs/default.yaml"))
    m.set_defaults(func=cmd_show_matrix)

    return p


def main(argv: list[str] | None = None) -> None:
    parser = build_parser()
    args = parser.parse_args(argv)
    raise SystemExit(args.func(args))


if __name__ == "__main__":
    main()
