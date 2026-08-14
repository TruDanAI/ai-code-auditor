# AGENTS.md — AI Code Auditor

## Read order

1. `STATUS.md` — current verified state and next actions.
2. `docs/roadmap-30d.md` — execution milestones.
3. `benchmark/scoring_rules.md` — frozen benchmark protocol.
4. `docs/mentor-contract.md` — MENTOR MODE and BUILD MODE.
5. `docs/lo-trinh-chi-tiet.md` — curriculum/history.
6. `NOTES.md` — durable verified learning.

Dynamic diary text in older prompts never overrides `STATUS.md`.

## Current product contract

Input is a source repository. Output is a structured findings report with real
`file:line` evidence, verified coverage, cost, and limitations. The primary
quality gate is the clean-vs-spiked seeded-bug benchmark, not feature count.

## Working rules

- Use MENTOR MODE for learning and BUILD MODE for explicit implementation work.
- Evidence before conclusion; inspect files and run relevant checks.
- Change one experimental variable at a time.
- Keep raw trials immutable and never expose gold/Git mutation history to the audited snapshot.
- Do deterministic validation before LLM judging.
- Do not change benchmark scoring after outcome observation without a dated amendment.
- Reviewer, LangGraph, MCP, Phoenix, and UI are conditional/timeboxed; benchmark,
  offline scorer tests, Docker reproducibility, and truthful README metrics are core.
- Preserve user changes and do not commit unless the user explicitly asks.

## Verification commands

```powershell
E:\venvs\ai-code-auditor\Scripts\Activate.ps1
python -m py_compile agent.py audit.py benchmark\benchmark_runner.py benchmark\score_benchmark.py
python -m unittest discover -s benchmark -p "test_*.py" -v
python test_validator.py
git status --short
```

Update `STATUS.md` after a verified state change. Add to `NOTES.md` only after
the learner has understood/teach-backed the concept and there is supporting evidence.
