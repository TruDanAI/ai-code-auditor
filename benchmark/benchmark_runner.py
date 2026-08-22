r"""Run reproducible clean-vs-spiked auditor trials.

The command is safe by default: without ``--execute`` it validates configuration
and prints the interleaved schedule, but never initializes an LLM client.

Example after exporting snapshots without ``.git``::

    python benchmark/benchmark_runner.py \
      --clean-snapshot C:\bench\clean \
      --spiked-snapshot C:\bench\spiked \
      --trials 3 --output-dir benchmark/runs/baseline-v01

Add ``--execute`` only after reviewing the dry-run output and environment.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
import time
from pathlib import Path
from typing import Iterable

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import agent  # noqa: E402  - project root is added deliberately above
import audit  # noqa: E402

RUNNER_VERSION = "0.1"


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as fh:
        for block in iter(lambda: fh.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def snapshot_fingerprint(root: Path) -> str:
    """Hash relative paths and contents so every trial identifies exact input."""
    digest = hashlib.sha256()
    files = sorted(path for path in root.rglob("*") if path.is_file())
    for path in files:
        relative = path.relative_to(root).as_posix().encode("utf-8")
        digest.update(len(relative).to_bytes(8, "big"))
        digest.update(relative)
        with path.open("rb") as fh:
            for block in iter(lambda: fh.read(1024 * 1024), b""):
                digest.update(block)
    return digest.hexdigest()


def validate_snapshot(path: Path, label: str) -> None:
    if not path.is_dir():
        raise ValueError(f"{label} snapshot khong ton tai/khong phai thu muc: {path}")
    if (path / ".git").exists():
        raise ValueError(
            f"{label} snapshot con .git: {path}. Hay dung git archive/copy sach "
            "de auditor khong thay lich su mutation."
        )
    if not any(path.rglob("*.js")):
        raise ValueError(f"{label} snapshot khong co file .js: {path}")


def interleaved_schedule(trials: int) -> list[tuple[str, int]]:
    """Alternate order by trial to reduce a simple clean-first time-order bias."""
    schedule: list[tuple[str, int]] = []
    for trial in range(1, trials + 1):
        labels = ("clean", "spiked") if trial % 2 else ("spiked", "clean")
        schedule.extend((label, trial) for label in labels)
    return schedule


def flatten_findings(records: Iterable[dict]) -> list[dict]:
    findings: list[dict] = []
    for record in records:
        if record.get("status") != "ok":
            continue
        for finding in record.get("report", {}).get("findings", []):
            item = dict(finding)
            item["_checklist_id"] = record.get("id")
            item["_trial_batch_id"] = record.get("batch_id")
            findings.append(item)
    return findings


def write_json(path: Path, data: object) -> None:
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def run_one_trial(
    label: str,
    trial: int,
    snapshot: Path,
    output_root: Path,
    checklist_items: list[dict],
    common_manifest: dict,
) -> dict:
    run_name = f"{label}-trial-{trial:02d}"
    run_dir = output_root / run_name
    if run_dir.exists():
        raise FileExistsError(
            f"Run directory da ton tai, khong overwrite raw evidence: {run_dir}"
        )
    run_dir.mkdir(parents=True)

    # Redirect the existing append-only ledgers into this immutable trial folder.
    audit.RESULTS_FILE = str(run_dir / "audit_results.jsonl")
    agent.LOG_FILE = str(run_dir / "agent_log.jsonl")

    started_at = time.strftime("%Y-%m-%dT%H:%M:%S%z")
    batch_id = f"benchmark-v{RUNNER_VERSION}/{run_name}/{int(time.time())}"
    agent.init(str(snapshot))
    t0 = time.perf_counter()
    records = audit.run_checklist(checklist_items, batch_id)
    elapsed_s = time.perf_counter() - t0

    findings = flatten_findings(records)
    write_json(run_dir / "findings.json", findings)

    status_counts: dict[str, int] = {}
    for record in records:
        status = record.get("status", "unknown")
        status_counts[status] = status_counts.get(status, 0) + 1

    telemetry = {
        "cost_usd": round(sum(record.get("cost_usd", 0.0) for record in records), 6),
        "llm_calls": sum(record.get("llm_calls", 0) for record in records),
        "prompt_tokens": sum(record.get("prompt_tokens", 0) for record in records),
        "output_tokens": sum(record.get("output_tokens", 0) for record in records),
        "item_llm_latency_s": round(sum(record.get("latency_s", 0.0) for record in records), 3),
        "wall_elapsed_s": round(elapsed_s, 3),
    }

    manifest = {
        **common_manifest,
        "run_name": run_name,
        "label": label,
        "trial": trial,
        "snapshot": str(snapshot),
        "snapshot_sha256": common_manifest["snapshots"][label]["sha256"],
        "batch_id": batch_id,
        "started_at": started_at,
        "finished_at": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
        "elapsed_s": round(elapsed_s, 3),
        "telemetry": telemetry,
        "status_counts": status_counts,
        "finding_count": len(findings),
        "complete": status_counts.get("ok", 0) == len(checklist_items),
    }
    write_json(run_dir / "manifest.json", manifest)
    return manifest


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--clean-snapshot", required=True, type=Path)
    parser.add_argument("--spiked-snapshot", required=True, type=Path)
    parser.add_argument("--trials", type=int, default=3)
    parser.add_argument("--output-dir", required=True, type=Path)
    parser.add_argument(
        "--checklist", type=Path, default=PROJECT_ROOT / "audit_checklist.json"
    )
    parser.add_argument(
        "--execute",
        action="store_true",
        help="Actually call the configured LLM. Without this flag, perform dry-run only.",
    )
    parser.add_argument(
        "--max-cost-usd",
        type=float,
        default=None,
        help="Chot chi cung: truoc moi trial, neu tong da tieu vuot nguong thi DUNG "
             "va ghi stopped_early.json thay vi am tham chay tiep.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.trials < 3:
        raise ValueError("Protocol yeu cau it nhat 3 trials/snapshot.")

    clean = args.clean_snapshot.resolve()
    spiked = args.spiked_snapshot.resolve()
    validate_snapshot(clean, "clean")
    validate_snapshot(spiked, "spiked")

    checklist_path = args.checklist.resolve()
    checklist = json.loads(checklist_path.read_text(encoding="utf-8"))
    items = checklist["items"]
    snapshots = {
        "clean": {"path": str(clean), "sha256": snapshot_fingerprint(clean)},
        "spiked": {"path": str(spiked), "sha256": snapshot_fingerprint(spiked)},
    }
    schedule = interleaved_schedule(args.trials)

    common_manifest = {
        "runner_version": RUNNER_VERSION,
        "model": agent.MODEL,
        "max_steps": agent.MAX_STEPS,
        "validator_enabled": not agent.NO_VALIDATOR,   # X6: arm ghi thang vao manifest
        "agent_sha256": sha256_file(PROJECT_ROOT / "agent.py"),
        "audit_sha256": sha256_file(PROJECT_ROOT / "audit.py"),
        "generation_defaults": "defined by agent.py/provider; code hash is authoritative",
        "checklist": str(checklist_path),
        "checklist_sha256": sha256_file(checklist_path),
        "checklist_item_count": len(items),
        "snapshots": snapshots,
        "schedule": [{"label": label, "trial": trial} for label, trial in schedule],
    }

    print(json.dumps(common_manifest, ensure_ascii=False, indent=2))
    if not args.execute:
        print("\nDRY-RUN OK: chua khoi tao client, chua goi LLM.")
        print("Review manifest roi them --execute khi 15/15 mutation + snapshots da san sang.")
        return 0

    if args.output_dir.exists() and any(args.output_dir.iterdir()):
        raise FileExistsError(
            f"Output directory khong rong; khong overwrite raw trials: {args.output_dir}"
        )
    args.output_dir.mkdir(parents=True, exist_ok=True)
    write_json(args.output_dir / "run_manifest.json", common_manifest)

    manifests = []
    spent = 0.0
    stopped_early = None
    for label, trial in schedule:
        # Chot chi kiem TRUOC moi trial: mot trial da bat dau thi de no chay het,
        # vi trial cut doi la rac du lieu - ton tien ma khong cham duoc.
        if args.max_cost_usd is not None and spent >= args.max_cost_usd:
            stopped_early = (
                f"DUNG SOM: da tieu ${spent:.4f} >= tran ${args.max_cost_usd:.2f}. "
                f"Chua chay: {label}-trial-{trial:02d} va cac trial sau."
            )
            print("\n" + stopped_early)
            break
        snapshot = clean if label == "clean" else spiked
        print(f"\n=== {label.upper()} trial {trial}/{args.trials} "
              f"(da tieu ${spent:.4f}) ===")
        manifest = run_one_trial(label, trial, snapshot, args.output_dir, items, common_manifest)
        spent += manifest.get("telemetry", {}).get("cost_usd", 0.0)
        manifests.append(manifest)

    write_json(args.output_dir / "completed_runs.json", manifests)
    print(f"\nTONG CHI: ${spent:.4f}"
          + (f" / tran ${args.max_cost_usd:.2f}" if args.max_cost_usd is not None else ""))
    if stopped_early:
        write_json(args.output_dir / "stopped_early.json",
                   {"reason": stopped_early, "spent_usd": round(spent, 6),
                    "completed_trials": len(manifests)})
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
