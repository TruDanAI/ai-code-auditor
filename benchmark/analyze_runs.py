"""Bootstrap CI + per-seed detection matrix over already-scored runs.

Reads `score-corrected-*.json` files only - never calls an LLM, never re-scores.
Two questions the aggregate means cannot answer:

  A1  How wide is the uncertainty? Mean over 3 trials with min-max is not a
      confidence interval. Resampling makes the honest width visible, and makes
      arm-vs-arm deltas testable instead of eyeballed.
  A3  Which seeds does nobody ever find? Magma's point: a per-bug matrix says
      more than a scalar recall, because it separates "hard for everyone" from
      "this arm got unlucky".

Deterministic: RNG seeded, so the same runs always give the same interval.
"""

from __future__ import annotations

import argparse
import json
import random
from pathlib import Path

RNG_SEED = 20260823
RESAMPLES = 1000
DEFAULT_SCORE = "score-corrected-20260822.json"


def load_arm(run_dir: Path, score_name: str) -> dict:
    """Per-seed hit vector across spiked trials + per-trial tp/fp for precision."""
    report = json.loads((run_dir / score_name).read_text(encoding="utf-8"))
    trials = report["trials"]
    seeds = sorted(set(trials[0]["matched_gold_ids"]) | set(trials[0]["missed_gold_ids"]))
    in_scope = [s for s in seeds if s != "SEED-OOC-01"]  # OOC-01 is deliberately off-checklist
    hits = {
        seed: [1 if seed in trial["matched_gold_ids"] else 0 for trial in trials]
        for seed in in_scope
    }
    counts = [(t["counts"]["tp_in_scope"], t["counts"]["fp"]) for t in trials]
    return {"name": run_dir.name, "hits": hits, "seeds": in_scope, "counts": counts}


def recall_point(arm: dict) -> float:
    per_trial = [
        sum(arm["hits"][s][i] for s in arm["seeds"]) / len(arm["seeds"])
        for i in range(len(arm["counts"]))
    ]
    return sum(per_trial) / len(per_trial)


def recall_resample(arm: dict, rng: random.Random, seed_draw: list[str]) -> float:
    """Hierarchical: seeds resampled (which bugs), then trials (agent stochasticity)."""
    n_trials = len(arm["counts"])
    total = 0.0
    for seed in seed_draw:
        vec = arm["hits"][seed]
        total += sum(vec[rng.randrange(n_trials)] for _ in range(n_trials)) / n_trials
    return total / len(seed_draw)


def precision_point(arm: dict) -> float:
    vals = [tp / (tp + fp) if tp + fp else 0.0 for tp, fp in arm["counts"]]
    return sum(vals) / len(vals)


def precision_resample(arm: dict, rng: random.Random) -> float:
    n = len(arm["counts"])
    draw = [arm["counts"][rng.randrange(n)] for _ in range(n)]
    vals = [tp / (tp + fp) if tp + fp else 0.0 for tp, fp in draw]
    return sum(vals) / len(vals)


def pct(values: list[float], p: float) -> float:
    ordered = sorted(values)
    idx = min(len(ordered) - 1, max(0, int(round(p * (len(ordered) - 1)))))
    return ordered[idx]


# Two mathematically equal sums computed in different orders differ by ~1e-17.
# Without a tolerance that residue reads as "interval excludes 0" and manufactures
# a claim out of float noise - the exact mistake this whole script exists to catch.
ZERO_TOL = 1e-9


def ci(values: list[float]) -> tuple[float, float]:
    return pct(values, 0.025), pct(values, 0.975)


def excludes_zero(lo: float, hi: float) -> bool:
    return lo > ZERO_TOL or hi < -ZERO_TOL


def bootstrap(arms: list[dict]) -> dict:
    """One shared seed-draw per resample so arm deltas stay PAIRED."""
    rng = random.Random(RNG_SEED)
    seeds = arms[0]["seeds"]
    recall = {a["name"]: [] for a in arms}
    precision = {a["name"]: [] for a in arms}
    deltas: dict[str, list[float]] = {}

    for _ in range(RESAMPLES):
        draw = [seeds[rng.randrange(len(seeds))] for _ in range(len(seeds))]
        drawn = {a["name"]: recall_resample(a, rng, draw) for a in arms}
        for a in arms:
            recall[a["name"]].append(drawn[a["name"]])
            precision[a["name"]].append(precision_resample(a, rng))
        for i, left in enumerate(arms):
            for right in arms[i + 1:]:
                key = f"{left['name']} - {right['name']}"
                deltas.setdefault(key, []).append(drawn[left["name"]] - drawn[right["name"]])

    return {"recall": recall, "precision": precision, "deltas": deltas}


def fmt(value: float) -> str:
    return f"{value * 100:.1f}%"


def report(arms: list[dict], boot: dict) -> str:
    out: list[str] = []
    out.append("# Bootstrap CI + ma tran seed (A1 + A3)\n")
    out.append(f"Resample **{RESAMPLES}**, RNG seed `{RNG_SEED}`, percentile 2.5/97.5. ")
    out.append("Khong goi LLM, khong cham lai - chi doc `score-corrected-*.json`.\n")

    out.append("\n## A1a. Recall in-scope, bootstrap phan tang (seed + trial)\n")
    out.append("Don vi resample **chinh** la seed: \"neu chon 14 seed khac thi so ra bao nhieu\".\n")
    out.append("\n| arm | diem | KTC 95% | be rong |\n|---|---|---|---|\n")
    for a in arms:
        lo, hi = ci(boot["recall"][a["name"]])
        out.append(f"| {a['name']} | {fmt(recall_point(a))} | {fmt(lo)} – {fmt(hi)} | {(hi-lo)*100:.1f} diem |\n")

    out.append("\n## A1b. Precision in-scope, cluster bootstrap tren trial (n=3)\n")
    out.append("⚠️ n=3 - khoang nay rong den muc gan nhu khong rang buoc gi. Bao ra de thay ro dieu do.\n")
    out.append("\n| arm | diem | KTC 95% |\n|---|---|---|\n")
    for a in arms:
        lo, hi = ci(boot["precision"][a["name"]])
        out.append(f"| {a['name']} | {fmt(precision_point(a))} | {fmt(lo)} – {fmt(hi)} |\n")

    out.append("\n## A1c. Hieu giua cac arm (recall), bootstrap **theo cap**\n")
    out.append("Cung mot lan rut seed dung cho ca hai arm -> loai bot nhieu chung.\n")
    out.append("**KTC chua 0 = khong tuyen bo duoc.**\n")
    out.append("\n| so sanh | hieu | KTC 95% | ket luan |\n|---|---|---|---|\n")
    for key, values in boot["deltas"].items():
        lo, hi = ci(values)
        point = sum(values) / len(values)
        verdict = "tach khoi 0" if excludes_zero(lo, hi) else "**chua 0 → KHONG tuyen bo**"
        out.append(f"| {key} | {point*100:+.1f} diem | {lo*100:+.1f} – {hi*100:+.1f} | {verdict} |\n")

    out.append("\n## A3. Ma tran phat hien theo seed (so trial spiked bat duoc / tong)\n")
    names = [a["name"] for a in arms]
    out.append("\n| seed | " + " | ".join(names) + " | tong |\n")
    out.append("|---" * (len(names) + 2) + "|\n")
    never: list[str] = []
    for seed in arms[0]["seeds"]:
        cells = []
        total = 0
        for a in arms:
            hit = sum(a["hits"][seed])
            total += hit
            cells.append(f"{hit}/{len(a['counts'])}")
        if total == 0:
            never.append(seed)
        out.append(f"| {seed} | " + " | ".join(cells) + f" | **{total}** |\n")

    out.append(f"\n**Seed KHONG arm nao bat duoc ({len(never)}/{len(arms[0]['seeds'])}):** ")
    out.append(", ".join(f"`{s}`" for s in never) if never else "khong co")
    out.append("\n")
    return "".join(out)


def self_check() -> None:
    """Smallest thing that fails if the interval logic breaks."""
    assert not excludes_zero(-0.5, 0.5), "interval straddling 0 must not be a claim"
    assert not excludes_zero(-0.5, -0.0), "negative-zero residue must not become a claim"
    assert not excludes_zero(-0.5, -1e-17), "float residue must not become a claim"
    assert excludes_zero(0.02, 0.30), "interval fully above 0 is a claim"
    assert excludes_zero(-0.30, -0.02), "interval fully below 0 is a claim"

    arm = {
        "name": "t", "seeds": ["A", "B"],
        "hits": {"A": [1, 1, 1], "B": [0, 0, 0]},
        "counts": [(1, 1), (1, 1), (1, 1)],
    }
    assert abs(recall_point(arm) - 0.5) < 1e-12, "1 of 2 seeds always found = 50%"
    assert abs(precision_point(arm) - 0.5) < 1e-12, "1 tp / 1 fp = 50%"
    assert pct([0.0, 1.0], 0.025) == 0.0 and pct([0.0, 1.0], 0.975) == 1.0
    print("self-check OK")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--runs", type=Path, default=Path(__file__).with_name("runs"))
    parser.add_argument("--score-name", default=DEFAULT_SCORE)
    parser.add_argument("--arms", nargs="+", required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--self-check", action="store_true")
    args = parser.parse_args()

    if args.self_check:
        self_check()

    arms = [load_arm(args.runs / name, args.score_name) for name in args.arms]
    spread = {tuple(a["seeds"]) for a in arms}
    if len(spread) != 1:
        raise ValueError("Cac arm khong dung chung tap seed - khong bootstrap theo cap duoc.")

    text = report(arms, bootstrap(arms))
    args.output.write_text(text, encoding="utf-8")
    print(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
