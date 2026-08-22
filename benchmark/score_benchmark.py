"""Offline scorer for the clean-vs-spiked seeded-bug benchmark.

The scorer never imports or calls an LLM. It builds a majority-clean baseline,
then scores each spiked trial independently against frozen golden findings.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from statistics import mean

LINE_TOLERANCE = 5


def normalize_path(value: str) -> str:
    value = str(value or "").replace("\\", "/")
    while value.startswith("./"):
        value = value[2:]
    return value


def normalize_category(value: str) -> str:
    return str(value or "").strip().lower()


def normalize_evidence(value: str) -> str:
    """Collapse whitespace so the same quoted line matches across trials."""
    return " ".join(str(value or "").split()).lower()


def finding_shape(raw: dict) -> dict:
    """Keep only scorer fields and make malformed values explicit, not magical."""
    line = raw.get("line")
    try:
        line = int(line)
    except (TypeError, ValueError):
        line = None
    return {
        "file": normalize_path(raw.get("file", "")),
        "line": line,
        "category": normalize_category(raw.get("category", "")),
        "evidence": normalize_evidence(raw.get("evidence", "")),
        "raw": raw,
    }


def gold_shape(raw: dict) -> dict:
    categories = raw.get("accepted_categories") or [raw.get("primary_category", "")]
    line = raw.get("final_line")
    try:
        line = int(line)
    except (TypeError, ValueError):
        line = None
    return {
        "id": raw["id"],
        "file": normalize_path(raw["file"]),
        "line": line,
        "primary_category": normalize_category(raw.get("primary_category", "")),
        "categories": {normalize_category(item) for item in categories},
        "in_scope": bool(raw.get("in_scope", True)),
        "difficulty": raw.get("difficulty", "unknown"),
        "checklist_id": raw.get("checklist_id"),
        "raw": raw,
    }


def same_location_and_category(left: dict, right: dict) -> bool:
    if left["file"] != right["file"] or left["category"] != right["category"]:
        return False
    if left["line"] is None or right["line"] is None:
        return False
    return abs(left["line"] - right["line"]) <= LINE_TOLERANCE


def same_finding(left: dict, right: dict) -> bool:
    """Same finding across snapshots - location alone is not enough.

    Amendment 22/08/2026: an insertion mutation shifts every line below it, so
    file+category+line-tolerance alone can collide two DIFFERENT findings. Real
    case: clean flags `"multer": "^2.1.1"` at package.json:23 while the seeded
    `"lodash": "4.17.15"` lands on that same line 23 and pushes multer to 24 -
    same file, same coarse `dependency` category, line delta 0. Comparing the
    quoted evidence separates them. Missing evidence on either side falls back
    to location-only, which suppresses rather than credits (conservative).
    """
    if not same_location_and_category(left, right):
        return False
    if not left["evidence"] or not right["evidence"]:
        return True
    return left["evidence"] == right["evidence"]


def matches_gold(finding: dict, gold: dict) -> bool:
    if finding["file"] != gold["file"]:
        return False
    if finding["category"] not in gold["categories"]:
        return False
    if finding["line"] is None or gold["line"] is None:
        return False
    return abs(finding["line"] - gold["line"]) <= LINE_TOLERANCE


def load_findings(path: Path) -> list[dict]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, list):
        raise ValueError(f"findings file phai la JSON array: {path}")
    return [finding_shape(item) for item in data]


def build_clean_consensus(clean_trials: list[list[dict]]) -> list[dict]:
    """Return findings present in a strict majority of clean trials.

    Matching uses `same_finding` - the SAME relation used to exclude findings later.
    Using the looser location-only key here would let one representative be elected
    for a cluster of distinct findings and then reject its own cluster members at
    exclusion time (seen for real: package.json dependency findings on lines 16/18/23
    collapsed to one axios entry, after which the line-16 entries scored FP).

    A one-off clean hallucination is intentionally not allowed to hide a spiked FP.
    """
    if len(clean_trials) < 3:
        raise ValueError("Can it nhat 3 clean trials de tao majority baseline.")
    threshold = len(clean_trials) // 2 + 1
    candidates: list[dict] = []
    for trial in clean_trials:
        for finding in trial:
            if not any(same_finding(finding, item) for item in candidates):
                candidates.append(finding)

    consensus: list[dict] = []
    for candidate in candidates:
        present = sum(
            1
            for trial in clean_trials
            if any(same_finding(candidate, item) for item in trial)
        )
        if present >= threshold:
            item = dict(candidate)
            item["clean_trial_frequency"] = present
            consensus.append(item)
    return consensus


def safe_ratio(numerator: int, denominator: int) -> float:
    return numerator / denominator if denominator else 0.0


def score_trial(findings: list[dict], gold_items: list[dict], baseline: list[dict]) -> dict:
    matched_gold: set[str] = set()
    classifications: list[dict] = []

    for finding in findings:
        # scoring_rules.md:62 + :74 - TP is "spiked ONLY"; a stable-clean finding
        # is excluded from the seeded delta before gold is ever consulted.
        if any(same_finding(finding, item) for item in baseline):
            classifications.append(
                {"class": "BASELINE", "reason": "clean_majority", "finding": finding["raw"]}
            )
            continue

        gold_matches = [gold for gold in gold_items if matches_gold(finding, gold)]
        available = [gold for gold in gold_matches if gold["id"] not in matched_gold]
        if available:
            # Nearest gold wins if a malformed benchmark ever creates overlapping windows.
            chosen = min(available, key=lambda gold: abs(finding["line"] - gold["line"]))
            matched_gold.add(chosen["id"])
            classifications.append(
                {
                    "class": "TP",
                    "gold_id": chosen["id"],
                    "gold_category": chosen["primary_category"],
                    "gold_difficulty": chosen["difficulty"],
                    "gold_in_scope": chosen["in_scope"],
                    "finding": finding["raw"],
                }
            )
            continue

        if gold_matches:
            # Protocol: duplicate reports for one seed are noise, never OOS.
            classifications.append(
                {"class": "FP", "reason": "duplicate_gold", "finding": finding["raw"]}
            )
            continue

        classifications.append({"class": "FP", "reason": "unmatched", "finding": finding["raw"]})

    tp = sum(item["class"] == "TP" for item in classifications)
    fp = sum(item["class"] == "FP" for item in classifications)
    baseline_count = sum(item["class"] == "BASELINE" for item in classifications)
    in_scope_gold = [item for item in gold_items if item["in_scope"]]
    tp_in = sum(item["id"] in matched_gold for item in in_scope_gold)
    tp_out = tp - tp_in
    recall_in = safe_ratio(tp_in, len(in_scope_gold))
    coverage = safe_ratio(tp, len(gold_items))
    precision_in = safe_ratio(tp_in, tp_in + fp)
    fdr_in = safe_ratio(fp, tp_in + fp)
    f1 = safe_ratio(2 * precision_in * recall_in, precision_in + recall_in)
    precision_all = safe_ratio(tp, tp + fp)

    per_category = {}
    category_names = sorted(
        {item["primary_category"] for item in in_scope_gold}
        | {
            normalize_category(item["finding"].get("category", ""))
            for item in classifications
            if item["class"] == "FP"
        }
    )
    for category in category_names:
        gold_count = sum(item["primary_category"] == category for item in in_scope_gold)
        category_tp = sum(
            item["class"] == "TP"
            and item.get("gold_in_scope")
            and item.get("gold_category") == category
            for item in classifications
        )
        category_fp = sum(
            item["class"] == "FP"
            and normalize_category(item["finding"].get("category", "")) == category
            for item in classifications
        )
        per_category[category] = {
            "tp": category_tp,
            "fn": gold_count - category_tp,
            "fp": category_fp,
            "recall": safe_ratio(category_tp, gold_count),
            "precision": safe_ratio(category_tp, category_tp + category_fp),
        }

    per_difficulty = {}
    for difficulty in sorted({item["difficulty"] for item in in_scope_gold}):
        subset = [item for item in in_scope_gold if item["difficulty"] == difficulty]
        subset_tp = sum(item["id"] in matched_gold for item in subset)
        per_difficulty[difficulty] = {
            "tp": subset_tp,
            "fn": len(subset) - subset_tp,
            "recall": safe_ratio(subset_tp, len(subset)),
        }

    return {
        "counts": {
            "tp_all": tp,
            "tp_in_scope": tp_in,
            "tp_out_of_checklist": tp_out,
            "fn_in_scope": len(in_scope_gold) - tp_in,
            "fp": fp,
            "baseline_excluded": baseline_count,
            "gold_all": len(gold_items),
            "gold_in_scope": len(in_scope_gold),
        },
        "metrics": {
            "in_scope_recall": recall_in,
            "end_to_end_coverage": coverage,
            "in_scope_precision": precision_in,
            "in_scope_fdr": fdr_in,
            "f1_in_scope": f1,
            "all_seeded_precision": precision_all,
        },
        "matched_gold_ids": sorted(matched_gold),
        "missed_gold_ids": sorted(item["id"] for item in gold_items if item["id"] not in matched_gold),
        "per_category": per_category,
        "per_difficulty": per_difficulty,
        "classifications": classifications,
    }


def aggregate(trial_scores: list[dict]) -> dict:
    metric_names = list(trial_scores[0]["metrics"]) if trial_scores else []
    metrics = {}
    for name in metric_names:
        values = [trial["metrics"][name] for trial in trial_scores]
        metrics[name] = {"mean": mean(values), "min": min(values), "max": max(values)}
    return {"trial_count": len(trial_scores), "metrics": metrics}


def load_telemetry(findings_path: Path) -> dict | None:
    manifest_path = findings_path.with_name("manifest.json")
    if not manifest_path.is_file():
        return None
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    telemetry = dict(manifest.get("telemetry", {}))
    telemetry["complete"] = bool(manifest.get("complete"))
    telemetry["run_name"] = manifest.get("run_name")
    return telemetry


def aggregate_telemetry(items: list[dict | None]) -> dict:
    present = [item for item in items if item is not None]
    if not present:
        return {"available": False}
    numeric_fields = (
        "cost_usd",
        "llm_calls",
        "prompt_tokens",
        "output_tokens",
        "item_llm_latency_s",
        "wall_elapsed_s",
    )
    summary = {"available": True, "run_count": len(present)}
    for field in numeric_fields:
        values = [float(item[field]) for item in present if field in item]
        if values:
            summary[field] = {"mean": mean(values), "min": min(values), "max": max(values)}
    summary["all_complete"] = all(item.get("complete", False) for item in present)
    return summary


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--gold", type=Path, default=Path(__file__).with_name("golden_findings.json"))
    parser.add_argument("--clean", type=Path, nargs="+", required=True, help="Clean findings.json files")
    parser.add_argument("--spiked", type=Path, nargs="+", required=True, help="Spiked findings.json files")
    parser.add_argument("--output", type=Path, required=True)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    gold_data = json.loads(args.gold.read_text(encoding="utf-8"))
    gold_items = [gold_shape(item) for item in gold_data["seeded"]]
    incomplete = [item["id"] for item in gold_items if item["line"] is None]
    if incomplete:
        raise ValueError(
            "Gold final_line chua sinh cho: " + ", ".join(incomplete) + ". Khong cham benchmark som."
        )
    if len(args.clean) < 3 or len(args.spiked) < 3:
        raise ValueError("Protocol yeu cau it nhat 3 clean va 3 spiked trials.")

    clean_trials = [load_findings(path) for path in args.clean]
    spiked_trials = [load_findings(path) for path in args.spiked]
    baseline = build_clean_consensus(clean_trials)
    scores = [score_trial(trial, gold_items, baseline) for trial in spiked_trials]
    report = {
        "protocol": {
            "line_tolerance": LINE_TOLERANCE,
            "clean_consensus": "strict_majority",
            "primary_metric_scope": "in_scope_only (14 seeds)",
            "ooc_metric": "end_to_end_coverage (15 seeds)",
        },
        "inputs": {
            "gold": str(args.gold),
            "clean": [str(path) for path in args.clean],
            "spiked": [str(path) for path in args.spiked],
        },
        "clean_consensus": [
            {
                "file": item["file"],
                "line": item["line"],
                "category": item["category"],
                "clean_trial_frequency": item["clean_trial_frequency"],
            }
            for item in baseline
        ],
        "trials": scores,
        "aggregate": aggregate(scores),
        "telemetry": {
            "clean": aggregate_telemetry([load_telemetry(path) for path in args.clean]),
            "spiked": aggregate_telemetry([load_telemetry(path) for path in args.spiked]),
        },
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report["aggregate"], ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
