# Agent Config Bench — Technical Report (v0.2)

**Question.** For a tool-using healthcare evidence agent, which configuration knobs actually move groundedness, refusal behavior, and cost: tool access, reusable skills, or model size?

**Method.** One-factor ablations on the same 30 golden tasks with the same programmatic grader (verbatim quotes, status, product identity, invented NCT ban). Pass rates are averaged per task; 95% CIs use a percentile bootstrap over tasks (4,000 resamples). Differences are **paired by task**.

**Agent under test.** [healthcare-evidence-agent](https://github.com/Akhilesh-Vangala/healthcare-evidence-agent) / evidence-mcp-agent: Claude Code (or API) + MCP tools over openFDA, ClinicalTrials.gov, CMS, plus Agent Skills.

## Configurations

| ID | Model | MCP tools | Skills | Runs |
|---|---|---|---|---|
| Baseline | none (fixed pipeline) | hard-coded | no | 30 |
| A | Haiku | no | no | 60 |
| B | Haiku | yes | no | 60 |
| C | Haiku | yes | yes | 60 |
| D | Sonnet | yes | yes | 30 |

**Total: 240 runs (210 agent + 30 baseline).**

## Primary results (dev split)

| Config | Pass rate (95% CI) | Claims verified | Invented NCTs | MCP calls / task | Cost / task | Median latency |
|---|---|---|---|---|---|---|
| Baseline | 20% (7–37%) | n/a | 0 | n/a | $0 | 0.1 s |
| A | 23% (10–40%) | 0% | 4 runs | 0 | $0.0014 | 10.3 s |
| B | 80% (63–93%) | 89% | 0 | 3.8 | $0.0025 | 11.1 s |
| **C** | **95% (87–100%)** | **94%** | **0** | **2.6** | **$0.0033** | **14.2 s** |
| D | 97% (90–100%) | 94% | 0 | 2.1 | $0.0532 | 16.2 s |

## Paired effects

| Change | Δ pass rate (95% CI) | Improved | Regressed |
|---|---|---|---|
| Baseline → C | **+75** (+60 to +90) | 23 | 0 |
| A → B (add tools) | **+57** (+33 to +77) | 19 | 2 (refusals) |
| B → C (add skills) | **+15** (+2 to +30) | 5 | 1 |
| C → D (Haiku → Sonnet) | +2 (0 to +5) | 1 | 0 |

## Findings

1. **Tools ground the agent.** Without tools, 210 claims and none verified; 4 runs invented NCT IDs. With tools, invented NCTs stay at zero.
2. **Tools alone reduce care.** Refusal / off-label cases regress when tools are added without skills.
3. **Skills restore judgment and sharpen tool use.** Refusals recover; claim verification 89% → 94%; MCP calls 3.8 → 2.6.
4. **Model size is not the lever.** Sonnet buys ~2 points at ~16× list-price cost.
5. **Remaining failures in C are over-escalation** (safe): human-review flags without unverifiable claims.

## Limitations (must state)

- Dev tasks are author-written; skills were iterated with visibility into this set.
- CIs are wide; C vs D is not significant.
- One tool paging change landed after an early C run (90% → 95%).
- Open-weight (Qwen 2.5 7B) runner exists but was not scaled in the primary 240-run study.

## What v0.2 adds

- Held-out suite (`suites/healthcare_heldout.json`, 30 tasks) — **do not tune against it**
- Robustness suite (tool faults, injection, multi-hop, budget)
- Installable framework (`agent-config-bench`) with YAML matrices, suite validation, stub runner, CI
- Eval card + runbook for held-out / open-weight / routing experiments

## Recommendation

For this workflow: invest in tools and skills before buying a larger model. Measure refusal regressions whenever tools are added. Report paired effects with CIs, not single-run pass rates.
