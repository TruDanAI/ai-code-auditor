"""Resolve golden ``final_line`` values from anchors on the final spiked snapshot.

The script is all-or-nothing: every seed must resolve to exactly one anchor in
its file/function scope before ``--write`` can modify the golden file.
"""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

TOP_LEVEL_FUNCTION = re.compile(r"^(?:async\s+)?function\s+[A-Za-z_$][\w$]*\s*\(")


def normalize_relative_path(value: str) -> Path:
    path = Path(str(value).replace("\\", "/"))
    if path.is_absolute() or ".." in path.parts:
        raise ValueError(f"Gold file path khong an toan: {value}")
    return path


def function_scope(lines: list[str], handler_anchor: str | None) -> tuple[int, int]:
    """Return zero-based [start, end) scope; handler anchors a top-level JS function."""
    if not handler_anchor:
        return 0, len(lines)
    handler_hits = [index for index, line in enumerate(lines) if handler_anchor in line]
    if len(handler_hits) != 1:
        raise ValueError(
            f"anchor_handler '{handler_anchor}' xuat hien {len(handler_hits)} lan, can dung 1."
        )
    start = handler_hits[0]
    for index in range(start + 1, len(lines)):
        if TOP_LEVEL_FUNCTION.match(lines[index]):
            return start, index
    return start, len(lines)


def resolve_record(snapshot: Path, record: dict) -> int:
    relative = normalize_relative_path(record["file"])
    source = (snapshot / relative).resolve()
    try:
        source.relative_to(snapshot.resolve())
    except ValueError as exc:
        raise ValueError(f"Path thoat snapshot: {record['file']}") from exc
    if not source.is_file():
        raise ValueError(f"{record['id']}: khong tim thay file {record['file']}")

    lines = source.read_text(encoding="utf-8", errors="ignore").splitlines()
    start, end = function_scope(lines, record.get("anchor_handler"))
    anchor = record["anchor_after"]
    hits = [index for index in range(start, end) if anchor in lines[index]]
    if len(hits) != 1:
        scope = (
            f"handler={record.get('anchor_handler')}"
            if record.get("anchor_handler")
            else "whole-file"
        )
        raise ValueError(
            f"{record['id']}: anchor_after xuat hien {len(hits)} lan trong {scope}; can dung 1."
        )
    return hits[0] + 1


def finalize(snapshot: Path, gold_data: dict) -> tuple[dict, dict[str, int]]:
    expected = int(gold_data["_meta"]["total_seeded"])
    records = gold_data["seeded"]
    if len(records) != expected:
        raise ValueError(f"Gold chua du: {len(records)}/{expected}. Khong sinh final_line som.")

    resolved = {record["id"]: resolve_record(snapshot, record) for record in records}
    updated = json.loads(json.dumps(gold_data))  # deep copy with JSON-compatible data
    for record in updated["seeded"]:
        record["final_line"] = resolved[record["id"]]
    updated["_meta"]["line_status"] = "resolved_from_final_spiked_snapshot"
    return updated, resolved


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--snapshot", required=True, type=Path)
    parser.add_argument(
        "--gold", type=Path, default=Path(__file__).with_name("golden_findings.json")
    )
    parser.add_argument("--write", action="store_true", help="Atomically update the gold JSON")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    snapshot = args.snapshot.resolve()
    if not snapshot.is_dir():
        raise ValueError(f"Snapshot khong ton tai: {snapshot}")
    if (snapshot / ".git").exists():
        raise ValueError("Final_line phai sinh tu snapshot khong .git, khong tu mutation repo.")

    data = json.loads(args.gold.read_text(encoding="utf-8"))
    updated, resolved = finalize(snapshot, data)
    print(json.dumps(resolved, ensure_ascii=False, indent=2))
    if not args.write:
        print("DRY-RUN OK: chua sua golden file. Them --write sau khi review mapping.")
        return 0

    temporary = args.gold.with_suffix(args.gold.suffix + ".tmp")
    temporary.write_text(
        json.dumps(updated, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    temporary.replace(args.gold)
    print(f"Da cap nhat atomically: {args.gold}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
