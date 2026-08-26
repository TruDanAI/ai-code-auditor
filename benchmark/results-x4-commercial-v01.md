# X4 commercial-v01 — Claude Code vs the seeded-bug benchmark

**Run date:** 17/08/2026 · **Protocol:** `protocol-x4-commercial-baseline.md` (authored before the first trial; committed after)
**Subject:** `claude-sonnet-5` via Claude Code headless (`claude -p`), read-only tools
**Comparator:** `results-baseline-v01.md` (this repo's own agent, `gemini-2.5-flash-lite`)

Same 15 seeds, same frozen gold, same `score_benchmark.py`, same ±5 line tolerance,
same clean-majority differential. The raw trial outputs are preserved. Metrics below
are replayed with the current scorer after the documented 22–23/08 baseline amendments;
historical `score.json` files are not overwritten.

## Headline comparison (3 clean + 3 spiked trials each)

| Metric | This repo's agent | **Claude Code** | Δ |
|---|---|---|---|
| In-scope recall (14 seeds) | 26.2% | **57.1%** (8/14) | **2.2×** |
| End-to-end coverage (15 seeds) | 24.4% | **53.3%** (8/15) | 2.2× |
| In-scope precision | 24.6% | **50.1%** | 2.0× |
| In-scope FDR | 75.4% | **49.9%** | noise cut ~⅓ |
| F1 (in-scope) | 24.2% | **53.4%** | 2.2× |
| Cost per full audit (13 items) | **$0.08** | $6.43 | **80× more** |
| Recall per dollar | **328 %/$** | 8.9 %/$ | 37× worse |

Both cost figures are *token count × list API price*, not invoices — the repo agent
computes it in `agent.py`, Claude Code reports `total_cost_usd`. Same construction,
so the ratio is apples-to-apples.

## Difficulty gradient — the authored-before-trial question

| Difficulty | This repo's agent | Claude Code | Gap |
|---|---|---|---|
| `de` (grep-able) | 67% | **100%** (3/3) | +33 pts |
| `vua` (read + reason over 1 function) | 20% | **60%** (3/5) | **+40 pts** |
| `kho` (cross-procedure / semantic) | 11% | **33%** (2/6) | +22 pts |

Claude Code's numbers were **identical in all three trials** (recall min = max = 57.1%,
and the same 8 seeds matched every time). The repo agent varied 21.4–28.6%.

### Verdicts on the authored-before-trial hypotheses

| ID | Prediction | Result |
|---|---|---|
| **H1** | Claude recall > 26.2% | ✅ **confirmed** — 57.1% |
| **H2** | Gradient persists (`de` > `vua` > `kho`) | ✅ **confirmed** — 100% > 60% > 33% |
| **H3** | Gap concentrates in `de`/`vua`, not `kho` (falsified if `kho` ≥ 50%) | ✅ **not falsified** — `kho` = 33%, and it is where the smallest gain and the largest residual failure sit |
| **H4** | FDR < 75.4% | ✅ **confirmed** — 49.9% |

**The authored-before-trial prediction ("Claude will win") matched the result.** The
protocol was committed after the run, so Git does not support calling X4 a full
pre-registration.

But the interesting part is what winning did *not* buy: `de` is solved (100%), `vua`
is where the money went (+40 pts), and **`kho` remains mostly unsolved — 4 of 6
cross-procedure/semantic seeds are still missed.** Better tooling bought the easy and
medium classes, not the hard one.

**Scope this claim carefully.** The subject was deliberately restricted to three
read-only tools (`Read`, `Grep`, `Glob`) to match the repo agent's tool set and keep
the snapshots immutable, with a $0.80/item cap. Claude Code normally also has Bash,
subagents, web access and no such cap. So **57.1% is a floor on this tool's capability,
not its ceiling**, and the `kho` result may be an artifact of the restriction rather
than a property of the defect class. Arm D below is what would settle it.

## Seeds still missed by both systems

| Seed | Diff | Category | Why it resists |
|---|---|---|---|
| SEED-AUTH-01 | kho | auth | write route reuses a READ permission — cross-file permission semantics |
| SEED-CRY-01 | kho | crypto | AES-GCM returns plaintext before `final()` verifies the tag |
| SEED-INP-02 | kho | input | stored XSS in `views.js` — checklist only points at `webhook.js` (checklist-gap) |
| SEED-OOC-01 | kho | dos | ReDoS — out-of-checklist by design |
| SEED-REL-01 | kho | reliability | dropped idempotency guard → double-send |
| SEED-CFG-01 | vua | config | dropped a fail-fast env requirement — absence is hard to see |
| SEED-DOC-01 | vua | doc-mismatch | doc/code divergence |

`SEED-INP-02` and `SEED-OOC-01` are checklist gaps, not agent failures — no checklist
item points at them. That ceiling binds both systems equally.

## The `session.js:169` case, revisited — same seed, opposite verdict

Baseline v01's strongest defense point was that the repo agent flagged
`session.js:169` (where **SEED-AUTH-02** lives) on the *clean* snapshot too, so the
differential correctly scored it a **miss** — pattern-matching, not detection.

Claude Code hit SEED-AUTH-02 **and** `session.js:169` does not appear in its clean
consensus. Same seed, same differential, opposite verdict: this was a real detection.

This is the clearest demonstration of what the instrument is for. A single-snapshot
benchmark would have scored both systems as "found AUTH-02" and been wrong about one
of them.

## Claude Code's noise floor (clean consensus, majority of 3 clean trials)

8 locations, 4 excluded per spiked trial as background noise:

| Location | Category | Clean trials |
|---|---|---|
| `core/webhook.js:266,297,542,550` | input | 2/3 each |
| `core/webhook.js:653,761` | reliability | 2/3 each |
| `core/webhook.js:527` | crypto | 2/3 |
| `core/messenger-client.js:43` | error-handling | 2/3 |

Even at 49.9% FDR, roughly **one in two Claude Code findings is not a seeded defect**.
Lower noise than the repo agent, not low noise.

## Failure modes observed

- **9/78 runs hit the per-run `--max-budget-usd 0.80` cap** and were truncated before
  submitting (`error_max_budget_usd`), scored as misses. This mirrors baseline v01's
  `no_report` items caused by `max_steps=10`. The cap was held identical across all
  trials on purpose — raising it mid-experiment would have put trials on different
  configurations.
- **16 runs returned HTTP 429** (subscription session limit). These were **deleted and
  re-run**, not scored: an infrastructure refusal is not a measurement.

## Confounds — declared, with direction

This is **not** a controlled comparison of two architectures. The arms differ in model
tier (`sonnet` vs `flash-lite`), tool set, step/budget limits, and system prompt.

Permitted claim: *"Claude Code scores 57.1% on this benchmark at $6.43/audit."*
Not permitted: *"Claude is better than my architecture"* — no variable was isolated.

Two known biases both run **against** Claude Code, so its true numbers are likely
slightly better than reported:

1. 9 truncated runs counted as misses.
2. Clean trial-02 lost 5/13 items to the budget cap, so the majority consensus is built
   on uneven coverage → less noise subtracted → precision understated.

## Limitations

15 seeds, 1 repo, seeds authored by the benchmark's own author; difficulty labels are
the author's judgment, not an independent rubric; 3 trials show the gradient is stable
but do not give tight confidence intervals; this measures one version of one tool on
one day.

## Reproduce

Runner, prompts and raw transcripts: `benchmark/x4/` (prompts are the 13 checklist
items verbatim from `audit_checklist.json` plus one output-format paragraph, identical
across clean and spiked). Snapshots were copied to a neutral directory with no parent
`CLAUDE.md`, no `.git`, and no gold file; transcripts were grepped for
`seed|golden|benchmark` to confirm no leakage.

## What this changes

The research question stops being "is my auditor good" (it is not) and becomes
answerable: **a commercial agent restricted to the same three read-only tools, at 80×
the cost, still misses two thirds of the semantic/cross-procedure defect class.** That
gap is the thing worth studying, and nobody had measured it on this benchmark before.

## Next arms (pre-register before running)

This run confounds model tier with harness. Two single-variable arms decompose it:

| Arm | Change | Question it answers |
|---|---|---|
| **C** | `agent.py` unchanged except `MODEL` → a stronger model | Is the gap the model, or the 3-tool harness? |
| **D** | Claude Code unrestricted: full tool set, no per-item cap, stronger model | What is the commercial tool's actual ceiling here? |

With baseline v01 (weak model + minimal harness), X4 (strong model + restricted
harness), C and D, the gap decomposes into a model term and a harness term. Neither arm
touches the benchmark, so both are legitimate under the freeze.
