# Changelog

## 0.2.0 — 2026-11-03

- Renamed package to `agent-config-bench` (kept `agentbench-cmg` CLI alias)
- Added tech report, eval card, runbook, LinkedIn copy
- Added `suites/healthcare_heldout.json` (30 tasks) + copy into evidence-mcp-agent
- Added `suites/robustness_tool_faults.json` (tool faults, injection, multi-hop, budget)
- Added YAML config matrices (`configs/default.yaml`, `open_weight.yaml`)
- Added runner/grader interfaces, suite validation, stub runner
- Added pytest suite + GitHub Actions CI
- Documented held-out / open-weight / routing next steps honestly

## 0.1.0 — 2026-10-08

- Primary 240-run ablation (Baseline, A–D) with bootstrap CIs and paired effects
