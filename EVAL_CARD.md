# Eval Card — Agent Config Bench

## Task data

| Split | Path | N | Authorship | Tuning allowed? |
|---|---|---|---|---|
| Dev | `suites/healthcare_dev.json` | 30 | Author | Yes (primary study already froze configs) |
| Held-out | `suites/healthcare_heldout.json` | 30 | Author, post-freeze | **No** |
| Robustness | `suites/robustness_tool_faults.json` | 12 | Author | No for primary claims |

## Grader

Production grader (evidence-mcp-agent): a task passes only if declared checks hold — status, product identity, required sections, verbatim claim quotes from retrieved sources, no invented NCT IDs, review-flag expectations.

This repo’s analyzer assumes those checks are already computed in `eval-*.json` rows.

## Metrics

- Task pass rate (mean of per-task pass fractions)
- Bootstrap 95% CI over tasks (default 4,000 resamples, seed 11)
- Paired Δ pass rate between configs on shared task IDs
- Claim precision, invented NCT count, MCP calls/task, list-price $/task, median latency
- Unsafe answer rate (robustness suite): must stay 0 for injection / marketing prompts

## Contamination controls

1. Freeze config C (prompts, skills, tools) before running held-out.
2. Never look at held-out failures while editing skills; only report.
3. Document any post-hoc tool bugfix (as done for label paging).
4. Prefer reporting **dev and held-out side by side**.

## Pricing caveat

Primary study costs are **API list prices** reconstructed from token usage. Some runs used a Claude subscription via headless Claude Code; treat $ as relative, not invoice-accurate.

## Reproducibility artifacts

- Raw rows: `results/raw/eval-*.json`
- Summaries: `results/summary.json`, `results/paired.json`
- Charts: `reports/pass_rate.png`, `reports/cost_vs_quality.png`
- Method writeup: `reports/TECH_REPORT.md`
