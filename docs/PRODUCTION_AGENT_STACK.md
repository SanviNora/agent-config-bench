# Company-level agentic stack — what to build before more API spend

Perspective: staff / principal AI engineer shipping tool-using agents at a frontier lab or platform company (OpenAI, Anthropic, Google, Stripe-scale).  
Scope: **Evidence MCP Agent + Agent Config Bench** as one system.

**Rule:** Do not burn Claude/OpenAI tokens until Layers 0–3 below exist for the features you claim. Offline tests + fixtures first; API only to measure.

---

## 1. What you already have (keep; this is real)

| Layer | You have |
|---|---|
| Tool plane | MCP over openFDA / ClinicalTrials.gov / CMS |
| Policy-ish skills | 4 Agent Skills (lookup, cite, trials, escalate) |
| Output contract | Structured answer + `needs_human_review` |
| Grounding grader | Verbatim quote ∩ retrieved `source_id` |
| Science | One-factor ablation, paired bootstrap CIs |
| Ops crumbs | Disk HTTP cache, tool latency in traces, FastAPI `/health` |
| Eval product | Dev / held-out / robustness *suites authored* |

That is already stronger than most “LangChain demo” portfolios. It is **not** yet a production agent platform.

---

## 2. The stack OpenAI-level teams actually ship

Think in **planes**, not features. Every serious agentic system has these.

```
┌─────────────────────────────────────────────────────────────┐
│ 0. Product contract     who may ask, what may leave the box │
├─────────────────────────────────────────────────────────────┤
│ 1. Gateway              auth, quota, idempotency, routing   │
├─────────────────────────────────────────────────────────────┤
│ 2. Orchestration        graph/state, retries, budgets       │
├─────────────────────────────────────────────────────────────┤
│ 3. Tools                schemas, sandboxes, fault injection │
├─────────────────────────────────────────────────────────────┤
│ 4. Memory / context     session, evidence log, prompt cache │
├─────────────────────────────────────────────────────────────┤
│ 5. Policy & safety      allow/deny, PII, jailbreak, audit   │
├─────────────────────────────────────────────────────────────┤
│ 6. Verification         deterministic graders >> LLM-as-judge│
├─────────────────────────────────────────────────────────────┤
│ 7. Human loop           review queue, exact-version approve │
├─────────────────────────────────────────────────────────────┤
│ 8. Eval platform        offline / shadow / online / canary  │
├─────────────────────────────────────────────────────────────┤
│ 9. Observability        traces, metrics, cost, replay       │
├─────────────────────────────────────────────────────────────┤
│10. Delivery             versioned prompts/skills, CI, SLOs  │
└─────────────────────────────────────────────────────────────┘
```

Map of **your gaps** (honest):

| Plane | Status | Gap |
|---|---|---|
| 0 Product contract | Partial | Disclaimer exists; no tenant/roles, no “answer may leave API” policy matrix |
| 1 Gateway | Thin | FastAPI exists; no auth, rate limits, request IDs, idempotency keys |
| 2 Orchestration | Weak | Claude Code as black-box runtime; no explicit graph, step budgets, or recovery |
| 3 Tools | Good start | No typed JSON Schema enforcement at boundary, no fault injection hooks, no circuit breakers |
| 4 Memory | Partial | Evidence JSONL per run; no session memory model, no prompt-cache strategy as a first-class control |
| 5 Policy | Skills only | Skills are soft; no hard gate that *blocks* unverified claims from leaving the API |
| 6 Verification | **Strong** | Keep this as the crown jewel; extend to unsafe_answer_rate |
| 7 Human loop | Flag only | Flag exists; no review queue, no approve/reject with frozen digest |
| 8 Eval | Strong science, thin platform | Suites authored; no shadow traffic, no canary, no regression gate in CI on golden |
| 9 Observability | Traces on disk | No OpenTelemetry `gen_ai.*`, no Prometheus, no replay from trace |
| 10 Delivery | Manual | No prompt/skill version pins in every report; no “block merge if pass drops >2 pts” |

---

## 3. What “production agentic” means (definitions to use in interviews)

1. **The model proposes; code decides.** Unverified claims never reach the user (RegLens pattern). Your verifier grades *after* the fact today — production moves it **in front of the response**.
2. **Tools are untrusted.** Tool text can contain prompt injection. Treat every tool payload as hostile.
3. **Evals are a product.** Offline golden + held-out + adversarial + shadow + online metrics. Ablations are how you choose configs; gates are how you ship.
4. **Cost and latency are SLOs**, not screenshots. p50/p95, $/successful verified answer, tool-error rate.
5. **Everything is versioned and replayable.** `prompt_version`, `skill_digest`, `tool_schema_version`, `grader_version`, `corpus_hash`, `git_sha` on every run.
6. **Human review is a protocol**, not a boolean. Exact content digest, reviewer identity, decision, time.

---

## 4. Priority roadmap — build **without** API first

Ordered by hiring signal × leverage × low token cost.

### P0 — Hard gates (1–3 days, $0 API)

Make verification a **response filter**, not only an offline grader.

- [ ] `finalize()` step: drop or rewrite any claim that fails verbatim check
- [ ] If any claim fails → `status=refused|needs_review` and empty user-facing claims (or citations-only)
- [ ] Separate metrics: `pass_rate` vs `unsafe_answer_rate` (must be 0)
- [ ] Unit tests with fixtures: injected fake NCT, quote not in source, unknown source_id

**Interview line:** “We don’t trust the model to cite; the API cannot emit an unverified claim.”

### P0 — Tool boundary (1–2 days, $0)

- [ ] JSON Schema (or Pydantic) validation on every tool args + result
- [ ] Strip / mark untrusted tool text (`<tool_result untrusted>`)
- [ ] Timeouts, retries with jitter, circuit breaker per tool
- [ ] `inject_tool_fault` hook for robustness suite (timeout, empty, schema_error, rate_limit, injection, fake_nct)

**Interview line:** “Tools fail in production; fault injection is part of the eval contract.”

### P1 — Orchestration you own (3–5 days, mostly $0)

Stop treating Claude Code as the only runtime for the *architecture story*.

- [ ] Explicit state machine or LangGraph: `classify → retrieve → draft → verify → escalate|answer`
- [ ] Step budget (max tool calls, max tokens, max wall time)
- [ ] Deterministic compile path vs agent path (you already have baseline) — keep both
- [ ] Anthropic API + OpenAI Responses + Ollama runners behind one `AgentRunner` (bench already stubs this)

**Interview line:** “Runtime is swappable; policy and verify layers are not.”

### P1 — Observability & replay (2–3 days, $0)

- [ ] OpenTelemetry spans: `gen_ai.chat`, tool spans, verify span, cost attributes
- [ ] Structured run record: versions + evidence hash + decision
- [ ] `replay(run_id)` from stored evidence + answer (no model call)
- [ ] Prometheus counters: requests, verify_fail, tool_error, escalate, cost_usd

### P1 — Eval platform upgrades (2–3 days, $0 until you choose to run)

- [ ] CI golden gate: stub + fixture rows must pass; optional nightly live
- [ ] Grader version pinned in every `eval-*.json`
- [ ] Power analysis note: 30 tasks → wide CIs; plan N=100 or stratified categories
- [ ] Contamination protocol already in EVAL_CARD — automate “heldout locked” flag in config

### P2 — Human loop (2–4 days)

- [ ] Review queue table: `run_id`, digest, severity, assignee, decision
- [ ] Exact-version approve (hash of answer+evidence); reject returns to agent with reason
- [ ] SLA metrics: time-to-review, overturn rate

### P2 — Gateway (2–3 days)

- [ ] API key / JWT, per-tenant quota, idempotency-Key
- [ ] Request size limits, output size limits
- [ ] Kill switch + config flag for `tools_enabled`, `skills_pack`, `model`

### P3 — Online / shadow (needs some traffic or synthetic)

- [ ] Shadow: new skill pack scores offline on last 7 days of traces
- [ ] Canary: 5% traffic to config C′, gate on unsafe_answer_rate and verify_fail
- [ ] Online metrics: thumbs-down, escalate rate, $/answer — never replace offline graders

### P3 — Multi-agent only if product needs it

Do **not** add planner/critic/executor fashion until single-agent + verify is boringly solid. Multi-agent without gates is a demo, not production.

---

## 5. Agentic “features” that look senior (and which to skip)

| Feature | Do it? | Why |
|---|---|---|
| Verbatim / deterministic verify gate | **Yes** | Your differentiator; productionizes science |
| Tool fault injection + adversarial tool text | **Yes** | What labs grill you on |
| Explicit graph + budgets | **Yes** | Shows you own control flow |
| Prompt/skill versioning + CI regression gate | **Yes** | Matches your SAP story |
| OTel + replay | **Yes** | Platform signal |
| Model router (Haiku default, Sonnet on escalate) | Yes, after gates | Cost story; cheap to spec |
| RAG vector DB | **No** (for this product) | You retrieve structured APIs; vectors don’t help labels |
| Fine-tuning the policy model | Later | Skills + tools won; FT is last resort |
| Multi-agent debate | **No** for now | Adds variance without gates |
| LLM-as-judge as primary metric | **No** | Keep programmatic grader primary; judge only as secondary research |
| Memory embeddings across users | **No** | Compliance risk; no PHI product anyway |

---

## 6. Suggested architecture (target)

```
Client
  → API Gateway (auth, quota, idempotency)
    → Orchestrator (graph + budgets)
         ├─ Policy preprocessor (refuse promo / PHI patterns)
         ├─ Tool router (MCP) ──► Schema validate + sandbox + cache
         ├─ Draft model (Haiku / Qwen / Sonnet-on-escalate)
         ├─ Verifier (deterministic) ──► block or pass
         └─ Human review service (digest approve)
    → Run store (evidence, traces, versions)
    → Metrics (OTel / Prom)
Eval harness (Agent Config Bench)
  → offline suites (dev / heldout / robustness)
  → shadow / canary reports
  → bootstrap paired diffs → ship/no-ship
```

---

## 7. What to do **this week** before any held-out API run

1. Implement **verify-as-gate** + unit tests (P0).  
2. Implement **`inject_tool_fault`** on MCP tools + wire robustness suite (P0).  
3. Add **run manifest** fields: `git_sha`, `skill_digest`, `grader_version`, `config_id`.  
4. Add OTel (or even structured JSON logs that *look* like OTel attributes).  
5. Only then: held-out Claude run (frozen skills) → analyze → publish numbers.

Spending API on held-out *before* the gate means you pay to measure a system you already know is “grade after the fact,” which labs will dock you for in design interviews.

---

## 8. How to talk about it (OpenAI-style)

**Bad:** “I built an agent with MCP and skills that got 95%.”  
**Good:** “I treated reliability as a systems problem: tools are untrusted, claims are gated by a deterministic verifier, configs are chosen by paired ablations with CIs, and shipping is blocked when golden regresses. The interesting finding was that tools improved grounding but hurt refusals until skills restored judgment — so the policy layer is as important as retrieval.”

---

## 9. Success criteria (company-level)

You can say “production-shaped” when **all** are true:

- [ ] `unsafe_answer_rate = 0` on injection + marketing suites  
- [ ] Unverified claims cannot leave `/v1/briefing`  
- [ ] Every run has full version manifest + replay  
- [ ] Tool faults are tested in CI  
- [ ] Held-out numbers reported separately from dev  
- [ ] Cost/latency SLOs defined (even if aspirational)  
- [ ] Human approve path uses content digest  

Until then: call it a **research prototype with production-grade evaluation**, which is still an excellent hiring story — just don’t overclaim “production.”
