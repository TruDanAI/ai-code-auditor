"""Deterministic SAST+SCA arm: Semgrep + npm audit, scored by the SAME scorer.

Why this arm exists
-------------------
Every published agentic-security comparison puts a classic scanner next to the
agent (Agent Audit vs Semgrep 23.8% / Bandit 29.7%). Without it, "the LLM got
54.8%" answers nothing - 54.8% against what? This arm costs $0 and runs offline.

It also stress-tests the differential design itself: a deterministic tool has
ZERO trial variance by construction, so any spread the scorer reports for this
arm would be a scorer bug, not tool behaviour.

Declared BEFORE scoring (git proves the order)
----------------------------------------------
* Semgrep config: `p/default` - the out-of-the-box ruleset a real team runs.
  `p/security-audit` was also run and returned 0 findings on both snapshots;
  reported, not silently dropped.
* SCA: `npm audit --package-lock-only` - no install, matches how DEP-01's
  mutation validity was verified in the gold file.
* CWE -> category map below is keyed on CWE class, never on whether a mapping
  improves the score.
"""

from __future__ import annotations

import argparse
import json
import subprocess
from pathlib import Path

SEMGREP_CONFIG = "p/default"
TRIALS = 3  # deterministic: three identical copies, so the scorer's >=3 rule holds

# CWE class -> the auditor checklist's category vocabulary.
CWE_CATEGORY = {
    "798": "secret", "259": "secret", "522": "secret",
    "310": "crypto", "327": "crypto", "329": "crypto", "347": "crypto",
    "22": "input", "73": "input", "79": "input", "134": "input", "601": "input",
    "1333": "dos", "400": "dos",
    "352": "auth", "285": "auth", "287": "auth",
    "295": "config", "16": "config",
    "703": "error-handling", "755": "error-handling",
}
FALLBACK_CATEGORY = "config"  # unmapped CWE: park it, never guess into a gold category


def run(cmd: list[str], cwd: Path | None = None) -> str:
    done = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, shell=False)
    return done.stdout


def cwe_of(result: dict) -> str:
    entries = result.get("extra", {}).get("metadata", {}).get("cwe") or []
    if not entries:
        return ""
    first = entries[0] if isinstance(entries, list) else entries
    return str(first).split(":")[0].replace("CWE-", "").strip()


def semgrep_findings(snapshot: Path) -> list[dict]:
    raw = run([
        "semgrep", "--config", SEMGREP_CONFIG, "--json", "--quiet",
        "--metrics=off", "--no-git-ignore", str(snapshot),
    ])
    data = json.loads(raw)
    findings = []
    for item in data["results"]:
        rel = Path(item["path"]).resolve().relative_to(snapshot.resolve()).as_posix()
        findings.append({
            "file": rel,
            "line": item["start"]["line"],
            "category": CWE_CATEGORY.get(cwe_of(item), FALLBACK_CATEGORY),
            "evidence": (item["extra"].get("lines") or "").strip(),
            "severity": item["extra"].get("severity", "").lower(),
            "explanation": item["extra"].get("message", "").strip(),
            "source": f"semgrep:{item['check_id'].split('.')[-1]}",
        })
    return findings


def npm_audit_findings(snapshot: Path) -> list[dict]:
    raw = run(["npm", "audit", "--package-lock-only", "--json"], cwd=snapshot)
    try:
        data = json.loads(raw)
    except json.JSONDecodeError:
        return []
    manifest = (snapshot / "package.json").read_text(encoding="utf-8").splitlines()
    deps_line = next((i + 1 for i, t in enumerate(manifest) if '"dependencies"' in t), 1)

    findings = []
    for name, info in data.get("vulnerabilities", {}).items():
        line, evidence = deps_line, '"dependencies"'
        for i, text in enumerate(manifest):
            if f'"{name}"' in text:
                line, evidence = i + 1, text.strip()
                break
        titles = [v.get("title") for v in info.get("via", []) if isinstance(v, dict)]
        findings.append({
            "file": "package.json",
            "line": line,
            "category": "dependency",
            "evidence": evidence,
            "severity": info.get("severity", ""),
            "explanation": "; ".join(t for t in titles if t) or f"advisory: {name}",
            "source": "npm-audit",
        })
    return findings


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--snapshot", type=Path, required=True)
    parser.add_argument("--out-dir", type=Path, required=True)
    parser.add_argument("--label", required=True, help="clean or spiked")
    args = parser.parse_args()

    findings = semgrep_findings(args.snapshot) + npm_audit_findings(args.snapshot)
    print(f"{args.label}: {len(findings)} findings")

    for index in range(1, TRIALS + 1):
        trial = args.out_dir / f"{args.label}-trial-{index:02d}"
        trial.mkdir(parents=True, exist_ok=True)
        (trial / "findings.json").write_text(
            json.dumps(findings, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
        )
        (trial / "manifest.json").write_text(json.dumps({
            "runner_version": "deterministic-0.1",
            "model": f"semgrep {SEMGREP_CONFIG} + npm audit",
            "deterministic": True,
            "note": "3 ban sao giong het nhau - cong cu tat dinh, phuong sai = 0 theo thiet ke",
            "complete": True,
            "run_name": f"{args.label}-trial-{index:02d}",
            "telemetry": {"cost_usd": 0.0, "llm_calls": 0},
        }, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
