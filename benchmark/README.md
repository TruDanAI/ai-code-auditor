# Seeded-Bug Benchmark

This directory contains the protocol, gold labels, offline tooling, and tests.
Runtime snapshots and raw runs are intentionally Git-ignored.

## Integrity state

Protocol v0.1 is frozen after 7/15 mutations and before the first auditor
benchmark run. See `scoring_rules.md` and `../STATUS.md`; do not describe it as
full pre-registration before all mutations.

## Files

- `scoring_rules.md` — frozen definitions and differential rules.
- `golden_findings.json` — seeded findings and anchor-based locations.
- `finalize_gold.py` — resolves final lines from the final no-`.git` snapshot.
- `benchmark_runner.py` — dry-run-by-default clean/spiked trial runner.
- `score_benchmark.py` — deterministic offline scorer.
- `test_*.py` — tests that never call an LLM.

## 1. Run offline tests

```powershell
python -m unittest discover -s benchmark -p "test_*.py" -v
python test_validator.py
```

## 2. Finish all mutations first

Every seed needs one commit, one valid gold record, and one validity check. Do
not generate `final_line` while `golden_findings.json` is still below 15/15.

## 3. Export final source-only snapshots

Create `benchmark/snapshots/clean` from `benchmark-base` and
`benchmark/snapshots/spiked` from the final spiked commit using `git archive`.
Neither directory may contain `.git`, this benchmark directory, or gold labels.

Example shape (review paths before running):

```powershell
git -C C:\Users\Pc\Desktop\chatbot-fanpage-spiked archive --format=tar `
  --output C:\Temp\auditor-clean.tar benchmark-base
tar -xf C:\Temp\auditor-clean.tar -C benchmark\snapshots\clean

git -C C:\Users\Pc\Desktop\chatbot-fanpage-spiked archive --format=tar `
  --output C:\Temp\auditor-spiked.tar spiked
tar -xf C:\Temp\auditor-spiked.tar -C benchmark\snapshots\spiked
```

## 4. Resolve gold lines (dry-run, then write)

```powershell
python benchmark\finalize_gold.py --snapshot benchmark\snapshots\spiked
python benchmark\finalize_gold.py --snapshot benchmark\snapshots\spiked --write
```

The command refuses incomplete gold, `.git` snapshots, missing files, and
non-unique anchors. Review the printed mapping before `--write`.

## 5. Validate the trial plan without spending money

```powershell
python benchmark\benchmark_runner.py `
  --clean-snapshot benchmark\snapshots\clean `
  --spiked-snapshot benchmark\snapshots\spiked `
  --trials 3 `
  --output-dir benchmark\runs\baseline-v01
```

The default is a dry-run. It prints snapshot, checklist, agent, and audit hashes
plus the interleaved schedule. Only append `--execute` after reviewing it and
setting the Vertex/AI Studio environment.

## 6. Score offline

After all six trials complete, pass their `findings.json` files explicitly:

```powershell
python benchmark\score_benchmark.py `
  --clean benchmark\runs\baseline-v01\clean-trial-01\findings.json `
          benchmark\runs\baseline-v01\clean-trial-02\findings.json `
          benchmark\runs\baseline-v01\clean-trial-03\findings.json `
  --spiked benchmark\runs\baseline-v01\spiked-trial-01\findings.json `
            benchmark\runs\baseline-v01\spiked-trial-02\findings.json `
            benchmark\runs\baseline-v01\spiked-trial-03\findings.json `
  --output benchmark\runs\baseline-v01\score.json
```

Report raw counts with mean and min–max. The primary metrics use the 14 in-scope
seeds; OOC-01 affects end-to-end coverage only.
