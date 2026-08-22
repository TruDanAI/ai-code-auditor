"""
test_grep_context.py - X7: ban dan gia vao tham so `context` cua grep.

Nguyen tac giong test_validator.py: khong cho model tinh co dung dung roi moi
biet tool chay. Tu dung file gia, kiem tung tinh chat mot.

Chay (khong can Gemini/env - thuan Python, khong ton token):
    python test_grep_context.py
"""

import os
import tempfile

import agent

FIXTURE = """\
row zero
<td>${escapeHtml(a.x)}</td>
<td>${plain(b.y)}</td>
<td>${escapeHtml(c.z)}</td>
row four
"""


def with_fixture(fn):
    """Chay fn() voi CODEBASE_DIR tro vao mot repo gia dung 1 file."""
    original = agent.CODEBASE_DIR
    with tempfile.TemporaryDirectory() as tmp:
        with open(os.path.join(tmp, "views.js"), "w", encoding="utf-8") as f:
            f.write(FIXTURE)
        agent.CODEBASE_DIR = tmp
        try:
            return fn()
        finally:
            agent.CODEBASE_DIR = original


def check(name, condition, detail=""):
    print(f"  [{'OK ' if condition else 'FAIL'}] {name}" + (f" - {detail}" if detail and not condition else ""))
    return condition


def main():
    results = []

    def context_zero_unchanged():
        out = agent.grep(r"plain", ".js", 0)
        return out

    out = with_fixture(context_zero_unchanged)
    results.append(check("context=0 giu nguyen format cu 'file:line: noi_dung'",
                         "views.js:3: <td>${plain(b.y)}</td>" in out, out))
    results.append(check("context=0 KHONG keo theo dong hang xom",
                         "escapeHtml" not in out, out))

    def context_one():
        return agent.grep(r"plain", ".js", 1)

    out = with_fixture(context_one)
    results.append(check("context=1 hien dong TRUOC va SAU",
                         "views.js:2- " in out and "views.js:4- " in out, out))
    results.append(check("dong khop danh dau ':' - dong ngu canh danh dau '-'",
                         "views.js:3: " in out and "views.js:2- " in out, out))
    results.append(check("LOI THIEU escapeHtml nhin thay duoc canh anh em",
                         "escapeHtml(a.x)" in out and "plain(b.y)" in out, out))

    def clamped():
        return agent.grep(r"plain", ".js", 99)

    out = with_fixture(clamped)
    results.append(check("context bi ket ve toi da 5 (khong no output)",
                         "views.js:1- " in out and out.count("\n") <= 8, out))

    def at_file_edge():
        return agent.grep(r"row zero", ".js", 3)

    out = with_fixture(at_file_edge)
    results.append(check("khop o dau file khong tran ra so dong am",
                         "views.js:0" not in out and "views.js:1: " in out, out))

    print(f"\n{sum(results)}/{len(results)} pass")
    return 0 if all(results) else 1


if __name__ == "__main__":
    raise SystemExit(main())
