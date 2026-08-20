"""Gop raw/<trial>/<item>__<snap>.json thanh 1 findings file cho moi (snap, trial).

score_benchmark.py chi doc file/line/category; truong khac di kem de truy nguoi.
Run hong (budget_exhausted, JSON rach) duoc khai bao ro thay vi bien mat im lang -
cung nguyen tac error-as-data cua audit.py: mot muc chet khong duoc lam ca batch
tron thanh "khong co finding" mot cach im lang.
"""
import json
from pathlib import Path

X4 = Path(__file__).parent
RAW = X4 / "raw"
OUT = X4 / "scored"
OUT.mkdir(exist_ok=True)
ids = (X4 / "item_ids.txt").read_text().split()

trials = sorted(p.name for p in RAW.iterdir() if p.is_dir())
report = {}

for trial in trials:
    for snap in ("clean", "spiked"):
        findings, cost, turns, failed = [], 0.0, 0, []
        for item_id in ids:
            path = RAW / trial / f"{item_id}__{snap}.json"
            if not path.exists() or path.stat().st_size == 0:
                failed.append(f"{item_id}:missing")
                continue
            try:
                outer = json.loads(path.read_text(encoding="utf-8"))
            except json.JSONDecodeError:
                failed.append(f"{item_id}:bad-json")
                continue
            cost += float(outer.get("total_cost_usd") or 0)
            turns += int(outer.get("num_turns") or 0)
            if outer.get("is_error") or outer.get("result") is None:
                # budget_exhausted == no_report cua baseline v01: mat luot, tinh miss
                failed.append(f"{item_id}:{outer.get('subtype', 'error')}")
                continue
            try:
                inner = json.loads(outer["result"])
            except (json.JSONDecodeError, TypeError):
                failed.append(f"{item_id}:bad-result")
                continue
            for f in inner.get("findings", []):
                f["_item"] = item_id
                findings.append(f)

        dest = OUT / f"findings_{snap}_{trial}.json"
        dest.write_text(json.dumps(findings, ensure_ascii=False, indent=2), encoding="utf-8")
        report[f"{snap}/{trial}"] = {"findings": len(findings), "cost_usd": round(cost, 4),
                                     "turns": turns, "failed_items": failed}
        print(f"{snap:7s} {trial}  {len(findings):3d} findings | ${cost:7.4f} | {turns:4d} turns"
              + (f" | HONG: {failed}" if failed else ""))

(X4 / "aggregate_report.json").write_text(
    json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
print(f"\nTONG: ${sum(v['cost_usd'] for v in report.values()):.4f}"
      f" | file da ghi vao {OUT}")
