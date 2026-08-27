# AI Code Auditor

A ReAct code-auditing agent written from scratch — no agent framework — and, more
importantly, **the benchmark that measures whether it actually works.**

The agent is the easy half. The half that took the time is the evaluation harness:
seeded faults, a frozen answer key, a noise floor, and protocols committed to git
**before** each experiment ran.

---

## Headline results

Four arms, each **3 clean + 3 spiked trials**, same 15 seeded faults, same frozen
gold, same unmodified scorer, ±5 line tolerance, clean-majority differential.

| Metric | lite | flash | **pro** | Claude Code (Sonnet 5) |
|---|---|---|---|---|
| In-scope recall | 26.2% | 45.2% | **54.8%** | **57.1%** |
| In-scope precision | 24.6% | **61.1%** | 53.8% | 52.4% |
| F1 | 24.2% | 51.4% | 53.3% | 54.6% |
| **Cost per audit** | **$0.08** | $0.26 | $1.59 | $6.43 |
| Recall per dollar | **328 %/$** | 174 %/$ | 34 %/$ | 8.9 %/$ |

Two things worth reading twice:

1. **The self-built three-tool harness lands within 2.3 recall points of Claude Code
   at one quarter of the cost** — under matched read-only, three-tool constraints.
   The remaining gap is the *model*, not the harness ([X5](benchmark/results-x5-model-ladder.md)).
2. **Precision peaks at the mid-tier model, not the top.** Stronger models find more
   and hallucinate more. The cheapest arm was not the worst buy.

Cost figures are token count × list price on both sides — same construction, so the
ratio is comparable. They are not invoices.

---

## The result I retracted

[X6](benchmark/results-x6-validator-ablation.md) ablated the deterministic validator.
Turning it off cost **6.8 points of precision** — the direction the hypothesis predicted.

The protocol, committed **before** the first trial, required **≥10 points** to call the
effect measured. Run-to-run noise on this benchmark is **10.7 points**.

So the claim was **retracted, not reported.** An effect smaller than the noise that
produced it is not an effect.

One claim from that experiment did survive, because it was measured mechanically
rather than judged: **fabricated findings went from 5.2% (4/77) with the validator
off to 0.0% (0/145) with it on.**

---

## Why the protocols are committed before the trials

Every experiment here has a `protocol-*.md` committed before its first run, with the
hypotheses and rejection thresholds written down in advance. Git proves the ordering —
for example X5's protocol is commit `06c252b` at 11:56:10, before any trial started.

This is not ceremony. Choosing a threshold after seeing the numbers means you will
always find one that makes the result look good. Fixing it first is the only reason
the retraction above was possible.

| Experiment | Protocol | Result |
|---|---|---|
| Baseline | — | [results-baseline-v01.md](benchmark/results-baseline-v01.md) |
| X4 — commercial baseline | [protocol](benchmark/protocol-x4-commercial-baseline.md) | [results](benchmark/results-x4-commercial-v01.md) |
| X5 — model ladder | [protocol](benchmark/protocol-x5-model-ladder.md) | [results](benchmark/results-x5-model-ladder.md) |
| X6 — validator ablation | [protocol](benchmark/protocol-x6-validator-ablation.md) | [results](benchmark/results-x6-validator-ablation.md) |

Scoring rules: [`benchmark/scoring_rules.md`](benchmark/scoring_rules.md).

---

## How the agent works

```
checklist item
  │
  ├─► ReAct loop, 10-step budget
  │     tools (read-only): grep · read_file · list_files
  │
  └─► submit_findings  ──►  validate_report  ──►  accepted / rejected + reason
                             (deterministic, no model call)
```

`validate_report` rejects any finding whose **file, line, or verbatim evidence does not
exist** in the codebase. It is string comparison and file lookup — no LLM judges the
output. That is what drives fabricated findings to 0.0%.

`audit.py` runs one fresh agent session per checklist item so that context from one
item cannot leak into the next.

**No embeddings, no retrieval.** `grep` either finds a match or it does not, and it
returns the same result every run. Embedding search does not. For an auditor whose
whole value is being able to answer *why* it flagged something, determinism wins —
see [`experiments/README.md`](experiments/README.md).

---

## The benchmark

15 faults seeded into a **real production codebase** — a Messenger sales bot that ran
for a paying client — one commit each, with **deliberately innocuous commit messages**
so the git history does not leak the answer key.

Scoring is **differential**: the agent runs against both a clean and a spiked snapshot,
and any finding that also appears on the clean snapshot is subtracted as the agent's own
noise. Recall is credited only against a frozen gold key.

> **The snapshots are not committed.** They contain a client's production source. The
> checklist, gold key, scorer, protocols and every raw result are all here; the customer's
> code is not. Credentials appearing in benchmark evidence files are **seeded fakes**,
> planted so `SEC-01` has something to find.

---

## Running it

```powershell
# Vertex AI (primary) — needs `gcloud auth application-default login` once
$env:GOOGLE_GENAI_USE_VERTEXAI = "True"
$env:GOOGLE_CLOUD_PROJECT      = "your-gcp-project-id"
$env:GOOGLE_CLOUD_LOCATION     = "us-central1"
# or AI Studio:  $env:GEMINI_API_KEY = "..."

python audit.py <path-to-repo>            # all 13 checklist items
python audit.py <path-to-repo> DEP-01     # one item, smoke test
python test_validator.py                  # offline, costs nothing
```

Switch model arms by **environment variable, never by editing code** — this is what
keeps the code hash identical across arms:

```powershell
$env:AUDITOR_MODEL = "gemini-2.5-pro"     # recorded into run_manifest.json
```

---

## Limitations

- **One codebase, one language.** 15 seeds in one Node.js repository. Nothing here
  generalises to other stacks without re-running.
- **Noise floor is large** — 10.7 points. Any effect below ~2× that is not detectable
  on this benchmark, which is precisely why X6's finding was dropped.
- **Cost figures are list-price estimates**, not billed amounts.
- **`gemini-2.5-flash-lite` retires 16/10/2026.** After that date `baseline-v01`
  (26.2% recall) is historical data, not a re-runnable experiment.
- **The commercial baseline was constrained** to three read-only tools to match the
  harness. Unconstrained, it would likely score higher.

---

## Layout

| Path | |
|---|---|
| `agent.py` | ReAct loop, tools, `validate_report` |
| `audit.py` | batch orchestrator, one fresh session per item |
| `audit_checklist.json` | the 13 checklist items |
| `benchmark/` | protocols, gold key, scorer, raw results |
| `experiments/` | week-1/2 RAG lessons — **nothing in the auditor imports them** |
| `docs/` | Vietnamese study notes and roadmap from building this — learning record, not project docs |
| `STATUS.md` | current verified state |
| `NOTES.md` | knowledge journal |

---

Built as a final-year portfolio project by [Lê Đăng Trung](https://github.com/TruDanAI).
