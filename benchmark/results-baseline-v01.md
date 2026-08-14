# Baseline v01 — First reproducible benchmark run

**Run date:** 14/08/2026 · **Decision:** CONTINUE (P-X1 acceptance #7)

Single-agent LLM auditor vs a 15-seeded-bug benchmark on `chatbot-fanpage-spiked`,
scored clean-vs-spiked with a deterministic offline scorer. This is a **baseline**:
no reviewer, no retrieval tuning, no reranker — the honest starting point.

## Provenance (from `results/baseline-v01/run_manifest.json`)

| Field | Value |
|---|---|
| Model | `gemini-2.5-flash-lite`, `max_steps=10` |
| Checklist | 13 items (sha256 `32463c7d…`) |
| agent.py / audit.py | sha256 `f9ef4cb4…` / `e2a8848c…` |
| Clean snapshot | sha256 `198d35f5…` (192 files, no `.git`/gold) |
| Spiked snapshot | sha256 `09ee7973…` (192 files) |
| Trials | 3 clean + 3 spiked, interleaved |
| Line tolerance | ±5 · clean consensus = strict majority |

## Headline metrics (3 trials — mean [min–max])

| Metric | Mean | Min–Max | Raw |
|---|---|---|---|
| **In-scope recall** (14 seeds) | **26.2%** | 21.4%–28.6% | 3–4 / 14 |
| End-to-end coverage (15 seeds) | 24.4% | 20%–26.7% | 3–4 / 15 |
| In-scope precision | 24.6% | 12.5%–36.4% | — |
| **In-scope FDR** | **75.4%** | 63.6%–87.5% | — |
| F1 (in-scope) | 24.2% | 17.4%–32% | — |

Report raw counts because n is small. FDR = false-discovery rate (of what the agent
reports, ~3 in 4 are not seeded bugs), not FPR.

## The headline finding: difficulty gradient

Recall collapses monotonically with difficulty, and it is **stable across all 3 trials**:

| Difficulty | Mean recall | Per trial |
|---|---|---|
| `de` (grep-able) | **67%** | 67% / 67% / 67% |
| `vua` (read + reason over 1 function) | **20%** | 20% / 20% / 20% |
| `kho` (cross-procedure / semantic) | **11%** | 0% / 17% / 17% |

The agent catches bugs a `grep` would catch and collapses on anything requiring it to
read what a function *means*. This is the thesis result — it confirms the pre-registered
hypothesis H3 (most misses are semantic/cross-procedure, not grep-able).

## Never caught (8/15) — almost all `kho`

| Seed | Diff | Category | Why it's hard |
|---|---|---|---|
| SEED-CRY-01 | kho | crypto | AES-GCM returns plaintext before `final()` verifies the tag — integrity bypass, needs step-4 reasoning |
| SEED-AUTH-01 | kho | auth | write route reuses a READ permission — cross-file permission semantics |
| SEED-AUTH-02 | kho | auth | removed `exp <= now()` — immortal session (see differential note below) |
| SEED-REL-01 | kho | reliability | dropped idempotency guard → double-send |
| SEED-INP-02 | kho | input | stored XSS in `views.js` (checklist only reads `webhook.js` → checklist-gap) |
| SEED-OOC-01 | kho | dos | ReDoS (out-of-checklist by design; no item targets it) |
| SEED-CFG-01 | vua | config | dropped a fail-fast env requirement — absence is hard to see |
| SEED-INP-01 | vua | input | removed optional chaining → crash-on-malformed-webhook |

## Why clean-vs-spiked matters (the strongest defense point)

The scorer's clean-majority differential subtracts findings the agent *also* emits on
clean code:

| Location | Category | Flagged in CLEAN trials |
|---|---|---|
| `session.js:55` | auth | 3/3 |
| `session.js:169` | auth | 2/3 |
| `webhook.js:276` | crypto | 2/3 |

`session.js:169` is exactly where **SEED-AUTH-02** lives — but the agent flags line 169
on the *clean* snapshot too. So it isn't detecting the removed `exp` check; it's
pattern-matching "auth code looks suspicious." The differential correctly counts AUTH-02
as a **miss**, not a lucky hit. Without a clean baseline, a single-snapshot run would have
credited the agent with a detection it never actually made.

## Noise is high and unstable

FP per trial: **9, 28, 7**. Trial 2 alone emitted 28 false positives (FDR 87.5%). The
agent's noise floor is not just high, it's high-variance — a real reliability problem a
reviewer/verifier layer would target in Phase 2.

## Cost & latency

| | Clean/audit | Spiked/audit |
|---|---|---|
| Cost | $0.086 | $0.073 |
| LLM calls | ~119 | ~107 |
| Wall time | ~220s | ~511s (181–868s, high variance) |

Total for 6 trials: **$0.475** (guardrail $2). Spiked latency variance is large because
2 spiked trials hit the step budget on 1–2 items (`no_report`) — a budget-exhaustion
failure mode worth a Phase-2 trajectory metric.

## Reproduce

```powershell
# from ai-code-auditor/, snapshots already exported to benchmark/snapshots/
python benchmark/benchmark_runner.py `
  --clean-snapshot benchmark/snapshots/clean `
  --spiked-snapshot benchmark/snapshots/spiked `
  --trials 3 --output-dir benchmark/runs/baseline-v02 --execute
python benchmark/score_benchmark.py --clean <3 clean findings.json> --spiked <3 spiked findings.json> --output score.json
```

## Limitations (state these first at any defense)

- n=15 seeds, 1 repo, 1 model, seeds authored by the same person who built the auditor.
- Difficulty labels are the author's judgment, not an independent rubric.
- 3 trials — enough to see the gradient is stable, not enough for tight CIs.
- This measures *this* agent on *this* benchmark; it is not a claim about LLM auditors
  in general.
