# Held-out live results

Place `eval-*.json` files from:

```bash
cd ../evidence-mcp-agent
cmg-eval-agent --tasks evals/golden/agent_tasks_heldout.json \
  --configs A_closed_book B_tools_only C_tools_skills \
  --repeats 3 --workers 6
```

Then:

```bash
agent-config-bench analyze results/heldout/eval-*.json
```

Do **not** tune skills/prompts after inspecting these failures.
