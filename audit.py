"""
audit.py - Ngay 23: BATCH ORCHESTRATOR cua AI Code Auditor.

Vai tro: dung NGOAI agent. Doc audit_checklist.json -> moi muc mo 1 phien
run_agent TUOI (tri nho sach, khong dinh distractor muc truoc; run_id = id muc
de group so tien) -> ghi ket qua tung muc vao audit_results.jsonl NGAY khi xong
-> cuoi cung render bao cao Markdown: bang findings theo severity + bang $/muc.

Chay (activate venv E:\\venvs\\ai-code-auditor + set env Vertex truoc):
    python audit.py C:\\Users\\Pc\\Desktop\\chatbot-fanpage            # tron bo 13 muc
    python audit.py C:\\Users\\Pc\\Desktop\\chatbot-fanpage DEP-01     # smoke test 1 muc
"""

import json
import os
import sys
import time
from collections import Counter

import agent   # import MODULE nguyen con (khong from-import) -> goi duoc agent.init()

CHECKLIST_FILE = "audit_checklist.json"
RESULTS_FILE = "audit_results.jsonl"    # so tho tung muc - JSONL append (bai Ngay 18)
REPORT_FILE = "audit_report.md"         # san pham cuoi cho CON NGUOI doc

# Thu tu nghiem trong de sort bang findings. Dung .get(sev, 9) khi tra cuu -
# schema da enum 5 muc nhung phong thu re con hon KeyError giua luc render.
SEVERITY_RANK = {"critical": 0, "high": 1, "medium": 2, "low": 3, "info": 4}


def build_question(item: dict) -> str:
    """Ghep cau hoi giao cho agent tu 1 muc checklist.

    Ep agent dien DUNG category cua checklist vao tung finding: Ngay 25 cham
    diem bang match category giua loi-cay va finding -> 2 ben phai CUNG KHUNG
    (nguyen tac chot Ngay 22). Khong ep thi model tu che 'security'/'chung chung'
    va phep cham category vo nghia.
    """
    return (
        f"[MUC AUDIT {item['id']} | category='{item['category']}' | "
        f"severity goi y: {item['severity_hint']}]\n"
        f"{item['question']}\n"
        f"BAT BUOC: moi finding cua muc nay dien category='{item['category']}'."
    )


def run_checklist(items: list, batch_id: str) -> list:
    """Chay lan luot tung muc - moi muc 1 phien run_agent tuoi. Tra ve list record."""
    records = []
    for i, item in enumerate(items, 1):
        print(f"\n{'=' * 62}")
        print(f"[{i}/{len(items)}] {item['id']} ({item['category']}) - phien moi")
        print("=" * 62)

        record = {
            "batch_id": batch_id,
            "id": item["id"],
            "category": item["category"],
            "severity_hint": item["severity_hint"],
            "status": None,
        }
        try:
            report_str, totals = agent.run_agent(
                build_question(item),
                run_id=f"{batch_id}/{item['id']}",   # agent_log.jsonl group duoc theo MUC
            )
            # Ghi tien TRUOC khi parse JSON - parse co hong thi $ cua muc van con
            record["cost_usd"] = round(totals["cost_usd"], 6)
            record["llm_calls"] = totals["calls"]
            record["prompt_tokens"] = totals["prompt_tokens"]
            record["output_tokens"] = totals["output_tokens"]
            record["latency_s"] = round(totals["latency_ms"] / 1000, 1)
            record["report"] = json.loads(report_str)
            record["status"] = "ok"
        except json.JSONDecodeError:
            # run_agent co 1 duong return text thuong (cu chot mode='ANY' ma van
            # khong co function_call - nhanh DEBUG). Ghi nhan, KHONG sap batch.
            record["status"] = "no_report"
            record["raw_text"] = report_str[:500]
        except Exception as e:
            # AO GIAP orchestrator (error-as-data): 503/429/dut mang o muc nay
            # KHONG duoc keo chet cac muc con lai. Ghi ro nguyen nhan -> tra duoc
            # tan suat loi + chay lai RIENG muc hong: python audit.py <repo> <ID>
            record["status"] = "error"
            record["error"] = f"{type(e).__name__}: {e}"

        # Ghi NGAY tung muc, mode 'a' (bai JSONL Ngay 18): crash giua batch
        # thi cac muc DA xong van nam trong file - khong dot lai tien
        with open(RESULTS_FILE, "a", encoding="utf-8") as f:
            f.write(json.dumps(record, ensure_ascii=False) + "\n")
        records.append(record)
    return records


def _md_cell(text, width: int = 90) -> str:
    """Lam sach 1 O BANG Markdown: dau | la VACH NGAN COT nen phai escape,
    xuong dong pha vo hang -> ep moi whitespace ve 1 space; dai qua thi cat."""
    s = " ".join(str(text).split())
    s = s.replace("|", "\\|")
    return s if len(s) <= width else s[: width - 3] + "..."


def render_markdown(records: list, batch_id: str, repo_path: str) -> str:
    """Bien list record (data) thanh bao cao Markdown (view) - tach data/view:
    doi cach trinh bay khong dung vao pipeline chay agent."""
    ok = [r for r in records if r["status"] == "ok"]

    # Gom findings tu moi muc, dan kem id muc de truy nguon
    findings = []
    for r in ok:
        for f in r["report"].get("findings", []):
            f = dict(f)          # copy - khong sua vao record goc
            f["_item"] = r["id"]
            findings.append(f)
    findings.sort(key=lambda f: SEVERITY_RANK.get(f.get("severity"), 9))

    sev_count = Counter(f.get("severity", "?") for f in findings)
    tong_tien = sum(r.get("cost_usd", 0) for r in records)
    muc_hong = [r["id"] for r in records if r["status"] != "ok"]

    L = [f"# Bao cao Audit — {os.path.basename(repo_path)}", ""]
    L.append(f"- **Batch:** `{batch_id}` | **Model:** `{agent.MODEL}` "
             f"| **Checklist:** {len(records)} muc ({len(ok)} hoan thanh)")
    L.append(f"- **Tong chi phi LLM:** ~${tong_tien:.4f}")
    tomtat = ", ".join(f"{sev_count[s]} {s}" for s in SEVERITY_RANK if sev_count.get(s))
    L.append(f"- **Findings:** {len(findings)}"
             + (f" ({tomtat})" if findings else " — khong phat hien van de nao"))
    if muc_hong:
        L.append(f"- ⚠️ **Muc khong hoan thanh:** {', '.join(muc_hong)} (chi tiet cuoi bao cao)")

    # ==== Bang findings - trai tim bao cao, sort theo severity
    L += ["", "## Findings", ""]
    if findings:
        L.append("| # | Severity | Category | Vi tri | Evidence | Giai thich | De xuat | Muc |")
        L.append("|---|----------|----------|--------|----------|------------|---------|-----|")
        for n, f in enumerate(findings, 1):
            vitri = f"`{f.get('file', '?')}:{f.get('line', '?')}`"   # citation da qua validator
            ev = f"`{_md_cell(f.get('evidence', ''), 70)}`"
            if f.get("evidence_type") == "doc":
                ev += " *(doc)*"   # phan cap bang chung Ngay 16/17: doc NOI VE != code LA
            L.append("| " + " | ".join([
                str(n),
                f.get("severity", "?"),
                f.get("category", "?"),
                vitri,
                ev,
                _md_cell(f.get("explanation", ""), 110),
                _md_cell(f.get("suggestion", ""), 90),
                f["_item"],
            ]) + " |")
    else:
        L.append("Khong co finding nao qua duoc validator.")

    # ==== Do phu: da kiem gi / chua kiem gi - phan lam bao cao DANG TIN
    L += ["", "## Da kiem tra va an toan (verified_ok)"]
    for r in ok:
        vs = r["report"].get("verified_ok", [])
        if vs:
            L.append(f"\n**{r['id']}**")
            L += [f"- {v}" for v in vs]

    L += ["", "## Chua kiem tra (not_checked) — viec cho lan audit sau"]
    for r in ok:
        ns = r["report"].get("not_checked", [])
        if ns:
            L.append(f"\n**{r['id']}**")
            L += [f"- {x}" for x in ns]

    # ==== Bang $/muc - deliverable chinh Ngay 23 (noi logging Ngay 18)
    L += ["", "## Chi phi tung muc", ""]
    L.append("| Muc | Status | LLM calls | Tokens in | Tokens out | Latency LLM (s) | Chi phi |")
    L.append("|-----|--------|-----------|-----------|------------|-----------------|---------|")
    for r in records:
        co_so = "cost_usd" in r   # muc error khong co so (totals khong ve toi noi)
        L.append("| " + " | ".join([
            r["id"],
            r["status"],
            str(r.get("llm_calls", "—")),
            f"{r['prompt_tokens']:,}" if co_so else "—",
            f"{r['output_tokens']:,}" if co_so else "—",
            str(r.get("latency_s", "—")),
            f"${r['cost_usd']:.4f}" if co_so else "—",
        ]) + " |")
    L.append(f"| **TONG** |  |  |  |  |  | **${tong_tien:.4f}** |")

    # ==== Muc hong - error-as-data hien ra bao cao, khong bien mat im lang
    if muc_hong:
        L += ["", "## Muc khong hoan thanh"]
        for r in records:
            if r["status"] == "error":
                L.append(f"- **{r['id']}**: `{_md_cell(r['error'], 200)}`")
            elif r["status"] == "no_report":
                L.append(f"- **{r['id']}**: agent khong nop duoc JSON — text tho: "
                         f"{_md_cell(r.get('raw_text', ''), 200)}")

    L += ["", f"*Sinh boi audit.py — {time.strftime('%Y-%m-%d %H:%M')}. "
              f"Moi finding da qua validator hinh thuc (file/line/evidence doi chieu code that).*"]
    return "\n".join(L)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.exit("Cach dung: python audit.py <duong_dan_repo> [ID_MUC ...]\n"
                 "vd smoke:  python audit.py C:\\Users\\Pc\\Desktop\\chatbot-fanpage DEP-01")
    repo_path = sys.argv[1]
    only_ids = set(sys.argv[2:])

    with open(CHECKLIST_FILE, "r", encoding="utf-8") as f:
        checklist = json.load(f)
    items = checklist["items"]
    if only_ids:
        items = [it for it in items if it["id"] in only_ids]
        missing = only_ids - {it["id"] for it in items}
        if missing:
            # Go sai ID ma lang le chay 0 muc = false negative im lang (ho bug quen thuoc)
            sys.exit(f"Khong co muc checklist nao ten: {', '.join(sorted(missing))}")

    agent.init(repo_path)   # import KHONG tao client (nam trong init) -> phai goi tay

    batch_id = time.strftime("%Y%m%d-%H%M%S")
    print(f"Batch {batch_id}: {len(items)} muc | repo: {repo_path} | model: {agent.MODEL}")
    t0 = time.perf_counter()

    records = run_checklist(items, batch_id)

    # RENDER TU SO, khong tu RAM (fix 5 Ngay 23): khi chay lai SUBSET (vd 8 muc
    # chet 429), `records` chi co subset do - render truc tiep la bao cao MAT
    # 5 muc da ok truoc. Doc lai toan bo jsonl, lay record MOI NHAT tung muc
    # (dong ghi sau de len dong truoc), xep theo thu tu checklist GOC ->
    # bao cao luon la "trang thai tot nhat da biet" cua ca 13 muc.
    latest = {}
    with open(RESULTS_FILE, "r", encoding="utf-8") as f:
        for line in f:
            r = json.loads(line)
            latest[r["id"]] = r
    report_records = [latest[it["id"]] for it in checklist["items"] if it["id"] in latest]

    md = render_markdown(report_records, batch_id, repo_path)
    with open(REPORT_FILE, "w", encoding="utf-8") as f:
        f.write(md)

    ok_n = sum(1 for r in records if r["status"] == "ok")
    tong = sum(r.get("cost_usd", 0) for r in records)
    print(f"\n{'=' * 62}")
    print(f"XONG: {ok_n}/{len(records)} muc ok | tong ~${tong:.4f}"
          f" | {(time.perf_counter() - t0) / 60:.1f} phut")
    print(f"Bao cao: {REPORT_FILE} | so tho: {RESULTS_FILE}")
