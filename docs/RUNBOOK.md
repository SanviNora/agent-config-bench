# Runbook — held-out, open-weight, routing, robustness

## 0. Install

```bash
cd agent-config-bench
python -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
agent-config-bench validate-suite suites/healthcare_heldout.json --split heldout
agent-config-bench validate-suite suites/healthcare_dev.json --split dev
```

## 1. Re-analyze the primary 240-run study

```bash
agent-config-bench analyze results/raw/eval-*.json
```

Writes `results/summary.json`, `results/paired.json`, and charts under `reports/`.

## 2. Held-out eval (Phase 1 — requires evidence-mcp-agent + Claude)

Configs must already be frozen (no skill/prompt edits after looking at held-out).

```bash
cd ../evidence-mcp-agent
# Point the eval harness at the held-out task file (already copied):
#   evals/golden/agent_tasks_heldout.json
#
# Example (adjust flags to match cmg-eval-agent CLI in that repo):
cmg-eval-agent --tasks evals/golden/agent_tasks_heldout.json \
  --configs A_closed_book B_tools_only C_tools_skills \
  --repeats 3 --workers 6

# Copy the new report JSON into agent-config-bench/results/raw/heldout/
# then:
cd ../agent-config-bench
agent-config-bench analyze results/raw/heldout/*.json --out .
```

Report **dev vs held-out** in the README. Do not retune on held-out failures.

## 3. Open-weight (Phase 4)

`evidence-mcp-agent` ships `ollama_runner.py`. Run the C-equivalent skill+tool stack on Qwen 2.5 7B, then analyze with config id `E_open_weight` (see `configs/open_weight.yaml`).

```bash
agent-config-bench show-matrix --config configs/open_weight.yaml
```

## 4. Routing (optional)

Implement “Haiku by default, Sonnet when escalation skill fires” as config `F_routed`. Compare paired against `C_tools_skills`.

## 5. Robustness suite (Phase 3)

Requires upstream support for `inject_tool_fault` on MCP tools (timeout, empty, schema_error, rate_limit, prompt_injection_in_tool_text, fake_nct_in_tool_text).

```bash
agent-config-bench validate-suite suites/robustness_tool_faults.json --split robustness
# After live runs:
# agent-config-bench analyze results/raw/robustness/*.json
```

Track **unsafe_answer_rate** separately; target 0 on injection / marketing prompts.

## 6. CI smoke (no API keys)

```bash
pytest -q
agent-config-bench stub-run suites/healthcare_heldout.json --config configs/default.yaml
```
