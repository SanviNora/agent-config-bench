# LinkedIn / Featured copy

## Short (Featured blurb)

**Agent Config Bench** — Ablation framework for tool-using agents. Paired bootstrap CIs over 240 runs: tools +57 pts but broke refusals; skills +15 pts and restored judgment; Sonnet +2 pts at 16× cost. Held-out + robustness suites included.

Repo: https://github.com/Akhilesh-Vangala/agent-config-bench

## Post (publish-ready)

Most “agent demos” show a happy path. I wanted the opposite: which knobs actually move reliability?

I built **Agent Config Bench** — a one-factor ablation of tools, skills, and model size on a healthcare evidence agent (FDA / ClinicalTrials.gov / CMS) with a verbatim-quote grader.

**Setup:** 240 runs, same 30 tasks, paired by task, bootstrap 95% CIs (4,000 resamples).

**What I found:**
1. Tools are what ground the agent (+57 pts). Closed-book Claude invented NCT IDs; with MCP tools, invented IDs went to zero.
2. Tools alone made the agent *less careful* — refusal and off-label cases regressed.
3. Skills restored judgment (+15 pts), raised claim verification 89%→94%, and cut tool calls 3.8→2.6.
4. Sonnet bought +2 pts at ~16× the cost. For this workflow, buy skills before model size.
5. What’s left in the best config is over-escalation — the safe failure.

v0.2 adds a held-out task suite, a robustness suite (tool faults / injection / multi-hop), and an installable analyze/validate CLI so the method isn’t locked to one agent.

Full writeup + charts in the repo. Happy to chat with teams building agent evals, MCP tools, or regulated-domain copilots.

#AgenticAI #LLMEvaluation #MCP #GenAI

## Skills to list on the LinkedIn project

Python · agent evaluation · ablation studies · bootstrap confidence intervals · MCP tools · Agent Skills · Claude (Haiku / Sonnet) · experiment design · Matplotlib · cost–quality analysis · task-suite design · YAML config matrices · CI for evals
