"""
test_validator.py - Ngay 17: ban DAN GIA vao nguoi gac cua (validate_report).

Nguyen tac: KHONG ngoi cho model tinh co pham loi de biet guard chay -
tu che bao cao HONG co chu dich, guard phai bat duoc TUNG loi mot,
va bao cao SACH thi KHONG duoc tu choi oan.

Chay (khong can Gemini/env - thuan Python, khong ton token):
    python test_validator.py
"""

import os

# import ham that tu agent.py (import lai, KHONG copy - ky luat tu Ngay 8)
from agent import validate_report, CODEBASE_DIR


def first_content_line(relpath):
    """Tim dong dau tien CO NOI DUNG cua 1 file that -> (so_dong, noi_dung).

    Dung lam 'evidence nguyen van' cho vien dan can PASS buoc 3.
    """
    with open(os.path.join(CODEBASE_DIR, relpath), encoding="utf-8",
              errors="ignore") as f:
        for lineno, line in enumerate(f, start=1):
            if line.strip():
                return lineno, line.strip()
    raise AssertionError(f"{relpath} rong?")


def make_finding(**overrides):
    """1 finding hop le lam nen - moi vien dan chi BE 1 cho (doi 1 bien/lan)."""
    lineno, content = first_content_line("core/webhook.js")
    finding = {
        "severity": "info", "category": "crypto",
        "file": "core/webhook.js", "line": lineno,
        "evidence": content, "evidence_type": "code",
        "explanation": "test",
    }
    finding.update(overrides)
    return finding


def check(name, expected_hit, report, tools_called=("read_file", "grep")):
    """expected_hit = manh chuoi PHAI xuat hien trong loi guard tra ve.
    expected_hit = None nghia la bao cao sach -> guard phai tra ve "" (PASS).
    """
    error = validate_report(report, set(tools_called))
    if expected_hit is None:
        ok = (error == "")
    else:
        ok = (expected_hit in error)
    print(f"[{'PASS' if ok else 'FAIL'}] {name}")
    if not ok:
        print(f"    mong: {expected_hit!r}")
        print(f"    thuc te: {error[:200]!r}")
    return ok


if __name__ == "__main__":
    results = []

    # Dan 0 - nop bao cao ma chua read_file (guardrail Ngay 16 doi cho ve day)
    results.append(check(
        "buoc 0: chua read_file -> tu choi",
        "chua read_file",
        {"findings": []},
        tools_called=("grep",),   # co grep nhung KHONG co read_file
    ))

    # Dan 1 - file khong ton tai
    results.append(check(
        "buoc 1: file ma -> tu choi",
        "khong ton tai",
        {"findings": [make_finding(file="khong/co/that.js", line=1,
                                   evidence="x")]},
    ))

    # Dan 2 - file that nhung dong khong ton tai
    results.append(check(
        "buoc 2: dong ma (99999) -> tu choi",
        "chi co",
        {"findings": [make_finding(line=99999)]},
    ))

    # Dan 3 - dong that nhung evidence BIA (citation lao - toi nang nhat)
    results.append(check(
        "buoc 3: evidence bia -> tu choi",
        "KHONG khop",
        {"findings": [make_finding(evidence="chuoi bia dat 100% khong co that")]},
    ))

    # Dan 4 - file .md ma khai evidence_type='code' (khai lao lo lieu).
    # Evidence lay DUNG noi dung that cua .md de CHI loi buoc 4 no - doi 1 bien.
    md_files = [n for n in os.listdir(CODEBASE_DIR) if n.endswith(".md")]
    assert md_files, "codebase khong co file .md nao o goc?"
    md_line, md_content = first_content_line(md_files[0])
    results.append(check(
        f"buoc 4: {md_files[0]} khai 'code' -> tu choi",
        ".md",
        {"findings": [make_finding(file=md_files[0], line=md_line,
                                   evidence=md_content)]},
    ))

    # Dan THAT - bao cao sach 100%: guard KHONG duoc tu choi oan
    # (guard chi biet sua thi de test thieu ve nay -> false positive cua guard)
    results.append(check(
        "bao cao sach -> phai PASS, khong tu choi oan",
        None,
        {"findings": [make_finding()]},
    ))

    print(f"\n{sum(results)}/{len(results)} vien dan dung muc tieu"
          + (" - NGUOI GAC DAT CHUAN" if all(results) else " - CO LO HONG, xem FAIL o tren"))
