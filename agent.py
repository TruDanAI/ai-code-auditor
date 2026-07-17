"""
agent.py - Ngay 15: ReAct agent voi STRUCTURED OUTPUT (function calling).

Khac code mau trong lo trinh:
- KHONG regex parse "Action: ..." -> model tra ve FunctionCall object qua API.
- KHONG subprocess grep (Windows khong co grep.exe) -> grep viet bang Python thuan.
- automatic_function_calling TAT -> tu viet vong lap de log trace (nguyen lieu
  cho bao cao findings cua Auditor Tuan 4).

Chay (nho activate venv E:\\venvs\\ai-code-auditor + set env Vertex truoc):
    python agent.py C:\\Users\\Pc\\Desktop\\chatbot-fanpage
"""

import json
import os
import re
import sys
import time

from google import genai
from google.genai import errors as genai_errors
from google.genai import types

MODEL = "gemini-2.5-flash-lite"   # loop goi LLM nhieu lan -> model re (REV 2/7)

# Bang gia USD / 1 TRIEU token (gemini-2.5-flash-lite). Neo: 1M token input = 10 xu.
PRICE = {"input": 0.10, "output": 0.40}
LOG_FILE = "agent_log.jsonl"      # so chi phi - 1 dong JSON / 1 cu goi LLM
MAX_STEPS = 10                    # nang 6->10 (do that Ngay 16: guardrail an ~1 step tu choi
                                  # + 2-3 step dieu tra bu -> 6 la chet non giua chung)

# FIX 429 (Ngay 23): batch 13 muc ban lien tuc -> 5 muc chet rate-limit Vertex.
# Chi retry loi TAM THOI (429 het quota/phut, 503 server chap chon) - con 400
# la SO SACH SAI, retry vo ich (goi lai y nguyen van 400).
RETRY_MAX = 3
RETRYABLE_CODES = {429, 503}

# Guardrail tang HARNESS (Ngay 16): luat kiem tra duoc bang code thi KHONG nho prompt giu.
# Prompt = loi khuyen (model nho lo duoc - da do o vong 5); code = luat cung 100%.
MAX_REJECTIONS = 2   # duong thoat chong deadlock: tu choi toi da 2 lan roi van cho ra
GUARDRAIL_MSG = (
    "TU CHOI cau tra loi: ban chua he read_file file nao. "
    "Ket luan audit phai dua tren CODE DA DOC, khong phai mo ta tu grep/README. "
    "Quay lai Buoc 2: read_file it nhat 1 file lien quan tim duoc tu grep, roi moi ket luan."
)
EXIT_MSG = (
    "TU CHOI: ban vua ket thuc bang text thuong. CUA RA DUY NHAT cua phien audit "
    "la goi submit_findings - nop ngay findings/verified_ok/not_checked "
    "dua tren nhung gi da dieu tra."
)
FINAL_SUMMARY_MSG = (
    "HET LUOT DIEU TRA. Nop bao cao NGAY bang submit_findings, "
    "chi dua tren nhung observation da co o tren: "
    "moi finding kem file + line + evidence NGUYEN VAN tu ket qua tool; "
    "vung chua kip kiem tra khai vao not_checked - khong duoc suy dien."
)

# Auditor PHAI nhin thay tests/ va shops/ (bai hoc Ngay 9: IGNORE_DIRS cua
# mini_rag loai tests/ lam ground-truth rot khoi corpus). Agent chi bo rac that.
IGNORE_DIRS = {"node_modules", ".git"}
ALLOWED_EXT = (".js", ".md", ".json")

CODEBASE_DIR = sys.argv[1] if len(sys.argv) > 1 else r"C:\Users\Pc\Desktop\chatbot-fanpage"

# Ngay 23: client KHONG con duoc tao trong __main__ ma qua init() - vi audit.py
# import module nay (khoi __main__ khong chay khi bi import). None = chua init.
client = None


# ============================================================
# TOOLS - 3 ham Python thuong. SDK doc SIGNATURE + DOCSTRING de
# tu sinh JSON schema khai bao cho model -> docstring o day la
# PROMPT cho model biet khi nao dung tool nao, khong phai ghi chu.
# ============================================================

def read_file(filepath: str, start_line: int = 1) -> str:
    """Doc noi dung file trong codebase - MOI DONG CO SO DONG o dau.

    Dung khi da biet duong dan file (tu ket qua grep/list_files) va can xem
    noi dung de phan tich. Dung SO DONG trong output lam citation 'file:line'.

    Args:
        filepath: duong dan TUONG DOI tinh tu goc codebase, vd 'core/webhook.js'.
        start_line: doc tu dong so may (mac dinh 1). Moi lan doc tra ve toi da
            80 dong - file dai thi goi lai voi start_line lon hon de doc TIEP
            (vd thay import dang ngo o dau file -> read_file file goc cua import).
    """
    full_path = os.path.join(CODEBASE_DIR, filepath)
    try:
        with open(full_path, "r", encoding="utf-8", errors="ignore") as f:
            lines = f.read().splitlines()
    except OSError:
        return f"Error: khong doc duoc file '{filepath}' (sai duong dan?)"

    total = len(lines)
    start = max(1, int(start_line))
    window = lines[start - 1 : start - 1 + 80]   # 80 dong/lan ~ ngang muc 3000 ky tu cu
    if not window:
        return f"Error: '{filepath}' chi co {total} dong, khong co dong {start}"

    # Danh so dong -> model trich citation file:line THAT, khong doan
    numbered = "\n".join(f"{i}: {line[:200]}" for i, line in enumerate(window, start=start))
    if start - 1 + 80 < total:
        numbered += (f"\n... [file co {total} dong - goi read_file voi "
                    f"start_line={start + 80} de doc tiep]")
    return numbered


def grep(pattern: str, ext: str = "") -> str:
    """Tim pattern (regex, khong phan biet hoa thuong) trong file .js/.md/.json.

    Dung DAU TIEN khi can dinh vi: ten ham, ten bien, thuat toan (vd 'createHmac',
    'aes-256'), chuoi bao mat... Tra ve cac dong khop dang 'file:line: noi_dung'.

    Args:
        pattern: chuoi hoac regex can tim, vd 'createHmac' hoac 'md5|sha1'.
        ext: loc duoi file, vd '.js'. De trong = tim tat ca. Khi audit CODE,
            NEN dung ext='.js' de ket qua khong bi file tai lieu .md/.json
            chiem cho (tai lieu chi NOI VE code, khong phai code that).

    MEO QUAN TRONG: mac dinh khop CHUOI CON ('des' khop ca 'design'!).
    Muon khop NGUYEN TU, boc \\b hai dau: vd '\\bdes\\b|\\bmd5\\b'.
    Con muon bat chuoi con co chu dich (vd 'Hmac' bat 'createHmac') thi dung \\b.
    """
    # Vá tật JSON của model: nó viết "\b..." trong function call, JSON decode
    # thành ký tự backspace \x08 -> regex tìm backspace thật -> chết im lặng.
    # Tool biết trước tật này thì tự sửa hộ (defensive tool design).
    pattern = pattern.replace("\x08", r"\b")

    try:
        rx = re.compile(pattern, re.IGNORECASE)
    except re.error:
        # model dua regex hong (vd 'verify(' thieu dong ngoac) -> tim literal thay vi crash
        rx = re.compile(re.escape(pattern), re.IGNORECASE)

    # REVIEW-FIX 7/7 #3: chuan hoa ext model truyen - 'js' / 'JS' / '*.js' deu
    # phai hieu la '.js'. Khong chuan hoa: ext='JS' -> 0 file khop -> "No matches"
    # = FALSE NEGATIVE IM LANG (toi nang nhat cua auditor - cung ho voi bug \x08).
    if ext:
        ext = ext.strip().lower().lstrip("*")
        if not ext.startswith("."):
            ext = "." + ext
        allowed = (ext,)
    else:
        allowed = ALLOWED_EXT   # model de trong -> tim tat ca nhu cu

    # Gom khop THEO FILE de ap tran tung file - 1 file lam to (vd DESIGN.md)
    # khong duoc phep chiem het cho cua ca danh sach (bai hoc tran-50-dong Ngay 15/16)
    by_file = {}
    for root, dirs, files in os.walk(CODEBASE_DIR):
        dirs[:] = [d for d in dirs if d not in IGNORE_DIRS]   # cat nhanh cay thu muc rac
        for name in files:
            if not name.lower().endswith(allowed):
                continue
            path = os.path.join(root, name)
            rel = os.path.relpath(path, CODEBASE_DIR)
            try:
                with open(path, "r", encoding="utf-8", errors="ignore") as f:
                    for lineno, line in enumerate(f, start=1):
                        if rx.search(line):
                            # TU LAP format 'file:line: noi_dung' -> nguyen lieu citation
                            by_file.setdefault(rel, []).append(
                                f"{rel}:{lineno}: {line.strip()[:160]}"
                            )
            except OSError:
                continue

    if not by_file:
        return f"No matches found for '{pattern}'" + (f" (ext={ext})" if ext else "")

    total = sum(len(v) for v in by_file.values())
    out_lines = [f"[{total} dong khop trong {len(by_file)} file]"]
    if len(by_file) > 12:
        # Qua nhieu file -> uu tien DO PHU: moi file 1 dong dau + dem so con lai,
        # de KHONG file nao bi walk-order giau khoi tam mat (grep = linh trinh sat,
        # can bao quat; do sau da co read_file lo). Bai hoc: page-credentials.js
        # nam trong 395 khop nhung 3 lan lien bi chem khoi duoi danh sach.
        for rel, hits in by_file.items():
            extra = f"  [+{len(hits) - 1} khop nua trong file nay]" if len(hits) > 1 else ""
            out_lines.append(hits[0] + extra)
    else:
        for rel, hits in by_file.items():
            out_lines.extend(hits[:5])      # it file -> cho xem sau 5 dong/file
            if len(hits) > 5:
                out_lines.append(f"    ... [{rel}: con {len(hits) - 5} dong khop nua]")
    if len(out_lines) > 100:
        out_lines = out_lines[:100] + [
            "... [ket qua qua dai bi cat - grep pattern cu the hon hoac them ext='.js']"
        ]
    return "\n".join(out_lines)


def list_files(directory: str = ".") -> str:
    """Liet ke file trong mot thu muc cua codebase (de quy, toi da 100 file).

    Dung khi can nhin tong quan cau truc truoc khi grep/doc file.

    Args:
        directory: duong dan tuong doi tu goc codebase, vd 'core' hoac '.' (goc).
    """
    full_dir = os.path.join(CODEBASE_DIR, directory)
    if not os.path.isdir(full_dir):
        return f"Error: '{directory}' khong phai thu muc"
    files = []
    for root, dirs, filenames in os.walk(full_dir):
        dirs[:] = [d for d in dirs if d not in IGNORE_DIRS]
        for name in filenames:
            files.append(os.path.relpath(os.path.join(root, name), CODEBASE_DIR))
    listing = "\n".join(files[:100])
    if len(files) > 100:
        listing += f"\n... [con {len(files) - 100} file nua]"
    return listing


# ============================================================
# CUA RA DUY NHAT (Ngay 17): submit_findings.
# Khai bao TAY bang JSON schema (khong dua docstring nhu 3 tool tren)
# vi tham so long nhau (mang object) - docstring khong ta noi kieu nay.
# Moi "description" duoi day = PROMPT: model doc chung moi lan nop bao cao.
# ============================================================

SUBMIT_SCHEMA = {
    "type": "object",
    "properties": {
        "findings": {
            "type": "array",
            # description = cau cua EM (5/7), mentor them ve "verified_ok":
            # thuoc tri benh "12 findings - 0 van de" (model lap form vi so mang rong)
            "description": (
                "CHI chua VAN DE THAT SU co. 'Da kiem tra va thay AN TOAN' "
                "KHONG phai finding - ghi vao verified_ok. Khi khong tim thay "
                "van de thi de mang rong [] - do la cau tra loi TOT."
            ),
            "items": {
                "type": "object",
                "properties": {
                    # Slot 1 (em chon B): 5 muc chuan nganh - enum de model khong bia
                    # chu "rat nguy hiem"/"hoi lo" lam bao cao khong gom nhom duoc
                    "severity": {
                        "type": "string",
                        "enum": ["critical", "high", "medium", "low", "info"],
                        "description": "muc nguy hiem cua LOI TRONG CODE BI AUDIT",
                    },
                    "category": {
                        "type": "string",
                        "description": "nhom loi: crypto, auth, secret, doc-mismatch...",
                    },
                    "file": {
                        "type": "string",
                        "description": "duong dan tuong doi tu goc codebase",
                    },
                    # Slot 2 (em chon B): integer - validator se doi chieu lines[line-1],
                    # chuoi "khoang 30-35" thi may khong tru 1 duoc
                    "line": {
                        "type": "integer",
                        "description": "so dong lay tu output read_file/grep - KHONG doan",
                    },
                    "evidence": {
                        "type": "string",
                        # FIX multi-line (Ngay 23): AUTH-01/REL-01 dan nguyen KHOI nhieu
                        # dong -> validator so 1 dong -> doi 5 lan, dot ~4 call vo ich.
                        # description = prompt (thuoc Ngay 17) - noi thang luat choi.
                        "description": ("trich NGUYEN VAN noi dung cua DUNG MOT dong code "
                                        "tai file:line - CHI 1 dong duy nhat, KHONG dan "
                                        "ca khoi nhieu dong"),
                    },
                    # Slot 3: TODO(EM) - sua cau description nay bang LOI CUA EM
                    # truoc khi chay (day la cau prompt day model phan biet).
                    "evidence_type": {
                        "type": "string",
                        "enum": ["code", "doc"],
                        "description": (
                            "code = dong evidence LA lenh se CHAY that (implementation). "
                            "doc = dong chi NOI VE / nhac den: file .md, comment //, "
                            "hoac CHUOI string trong .js (console.log('...md5...') "
                            "khong phai he thong DUNG md5)."
                        ),
                    },
                    "explanation": {
                        "type": "string",
                        "description": "vi sao day la van de",
                    },
                    "suggestion": {
                        "type": "string",
                        "description": "cach sua - CHI dien khi that su biet cach sua",
                    },
                },
                # Slot 4: 7 bat buoc, suggestion TU NGUYEN - field bat buoc thi model
                # PHAI dien ke ca khi khong co gi de dien -> ep suggestion = moi no bia
                "required": ["severity", "category", "file", "line",
                             "evidence", "evidence_type", "explanation"],
            },
        },
        "verified_ok": {
            "type": "array",
            "items": {"type": "string"},
            "description": ("MOI phan tu = 1 muc DA kiem + cach kiem + ket luan, "
                            "vd 'md5: grep \\bmd5\\b ext=.js -> khong thay' hoac "
                            "'hash sha256 admin-auth.js:154 -> an toan'. "
                            "KHONG gop nhieu muc vao 1 chuoi."),
        },
        "not_checked": {
            "type": "array",
            "items": {"type": "string"},
            # cau cua EM (5/7): ep model ra lai observation truoc khi khai rong
            "description": (
                "Nhung gi DA THAY trong observation ma CHUA dieu tra "
                "(vd ham/thuat toan luot qua khi read_file) + vung chua quet - "
                "khai that, KHONG suy dien."
            ),
        },
    },
    "required": ["findings", "verified_ok", "not_checked"],
}

# Tool cua ra: khac 3 tool tren, SDK khong doc docstring ma nhan schema ta dua
submit_findings_decl = types.FunctionDeclaration(
    name="submit_findings",
    description=(
        "CUA RA DUY NHAT cua phien audit. Goi tool nay DE KET THUC khi da dieu "
        "tra xong: nop findings + verified_ok + not_checked. "
        "KHONG duoc ket thuc bang text thuong."
    ),
    parameters_json_schema=SUBMIT_SCHEMA,
)
submit_tool = types.Tool(function_declarations=[submit_findings_decl])


def validate_report(args: dict, tools_called: set) -> str:
    """NGUOI GAC CUA (nac B): kiem tra bao cao TRUOC khi cho ra khoi vong lap.

    Tra ve "" = PASS; nguoc lai tra message loi de doi nguoc cho model sua.
    Chi kiem duoc HINH THUC (file/line/evidence co that khong) - benh NGU NGHIA
    (finding rac, khai man not_checked) tri bang schema description + benchmark.
    """
    # Buoc 0 - guardrail Ngay 16 DOI CHO ve day: bao cao phai dua tren code DA DOC.
    # Loi tu choi gio quay ve qua function_response (doi CONG, khong doi check).
    if "read_file" not in tools_called:
        return ("TU CHOI: ban chua read_file file nao - ket luan audit phai dua "
                "tren CODE DA DOC. Dieu tra truoc roi moi submit_findings.")

    problems = []
    for i, f in enumerate(args.get("findings", [])):
        label = f"findings[{i}] ({f.get('file', '?')}:{f.get('line', '?')})"

        # Buoc 1 - file co that khong?
        rel = str(f.get("file", ""))
        path = os.path.join(CODEBASE_DIR, rel)
        if not os.path.isfile(path):
            problems.append(f"{label}: file khong ton tai trong codebase")
            continue

        # Buoc 2 - dong do co that khong?
        with open(path, "r", encoding="utf-8", errors="ignore") as fh:
            lines = fh.read().splitlines()
        line_no = int(f.get("line", 0))
        if not (1 <= line_no <= len(lines)):
            problems.append(f"{label}: file chi co {len(lines)} dong")
            continue

        # Buoc 3 - evidence khop NGUYEN VAN dong do khong? (Ngay 16 kiem tay,
        # nay code kiem ho - citation bia bi bat tai day). So sau khi ep
        # whitespace ve 1 space de khong truot vi thut le/tab.
        # FIX multi-line (nua validator): model van co tat dan ca khoi -> chi
        # cham DONG DAU cua evidence voi dong duoc cite. Van la so nguyen van
        # (khong yeu di), chi tha thu phan thua phia sau (vaccine cho tat da biet).
        first_line = (str(f.get("evidence", "")).splitlines() or [""])[0]
        ev = " ".join(first_line.split())
        actual = " ".join(lines[line_no - 1].split())
        if not ev or ev not in actual:
            problems.append(
                f"{label}: evidence KHONG khop noi dung that cua dong "
                f"(dong that: '{lines[line_no - 1].strip()[:120]}') "
                f"- read_file lai va trich nguyen van."
            )

        # Buoc 4 - khai evidence_type lao lo lieu: file .md ma bao 'code'
        if f.get("evidence_type") == "code" and rel.endswith(".md"):
            problems.append(f"{label}: file .md ma khai evidence_type='code' "
                            f"- .md chi NOI VE code")

    if problems:
        return ("TU CHOI bao cao - sua cac loi sau roi submit_findings lai:\n"
                + "\n".join(problems[:10]))
    return ""


# Registry: map ten tool (model goi bang TEN trong FunctionCall) -> ham that
TOOLS = {
    "read_file": read_file,
    "grep": grep,
    "list_files": list_files,
}

# He thong prompt chi con VAI TRO + luat grounding - KHONG day cu phap
# "Action: ..." nua (JSON schema cua tool da thay vai tro do).
SYSTEM_PROMPT = """Ban la AI agent AUDIT codebase Node.js (chatbot ban hang tieng Viet).
Ban lam viec TU CHU: KHONG BAO GIO hoi nguoc nguoi dung - tu chon buoc tiep theo.

QUY TRINH BAT BUOC cho cau hoi audit (vd "co dung X yeu/khong an toan khong?"):
Buoc 1 - Khao sat MAT DUONG truoc: grep xem he thong DANG DUNG gi cho chu de do
        (vd hoi ve ma hoa -> grep 'crypto|createHmac|createCipher|aes').
        Audit CODE thi grep voi ext='.js' - tai lieu .md chi NOI VE code.
Buoc 2 - read_file it nhat 1 file tim duoc o Buoc 1 de xac nhan cach dung thuc te.
Buoc 3 - Grep danh sach X yeu, boc \\b de khop nguyen tu
        (vd '\\bmd5\\b|\\bsha1\\b|\\bdes\\b|\\brc4\\b' - tranh 'des' khop 'design').
        Neu khong ra ket qua, thu them it nhat 1 pattern khac truoc khi chap nhan "khong co".
Buoc 4 - CHI sau khi xong Buoc 1-3 moi duoc ket luan.

LUAT BAO CAO:
- Chi ket luan tu observation - KHONG bia, KHONG doan.
- Moi ket luan PHAI kem citation file:line lay tu ket qua tool.
- Ket luan "khong co X" phai neu ro: DA kiem tra pattern gi + he thong dang dung gi thay the.
- Tra loi ngan gon bang tieng Viet.
- KET THUC: khi dieu tra xong, goi submit_findings de nop bao cao co cau truc -
  do la CACH DUY NHAT ket thuc phien audit, KHONG ket thuc bang text thuong."""



# ============================================================
# LOGGING CHI PHI (Ngay 18): tram can 1 cua cho MOI cu goi LLM.
# Nguyen ly = guardrail Ngay 16: cai gi code ep duoc thi khong
# nho ky luat con nguoi (rac logging 2 cho = quen dung cho dat nhat).
# ============================================================

def log_llm_call(record: dict) -> None:
    """Ghi 1 dong JSONL - mode 'a' (append): crash giua phien
    thi cac dong DA ghi van con nguyen (khac JSON array phai ghi-de ca file)."""
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(json.dumps(record, ensure_ascii=False) + "\n")


def call_llm(contents, config, step: int, phase: str, totals: dict):
    """TRAM CAN 1 cua: bam gio -> goi API -> nhat usage_metadata -> ghi so
    -> cong don vao totals -> tra response Y NGUYEN (can hang, khong dong hang).
    """
    # Retry dat o TANG NAY chu khong phai audit.py: contents dang mang ca phien
    # do dang - chet o call 11 la mat trang 10 call truoc (SEC-01 mat $0.0084).
    # Retry cang GAN cho loi cang re. 429 la quota-theo-PHUT -> backoff dai:
    # 20s -> 40s -> 80s (ngan qua thi dap dau vao cung buc tuong).
    for attempt in range(RETRY_MAX + 1):
        t0 = time.perf_counter()   # perf_counter: dong ho DON DIEU do khoang thoi gian
        try:
            response = client.models.generate_content(
                model=MODEL, contents=contents, config=config
            )
            break
        except genai_errors.APIError as e:
            if e.code not in RETRYABLE_CODES or attempt == RETRY_MAX:
                raise   # loi khong-tam-thoi / het kien nhan -> nem len ao giap audit.py
            wait = 20 * (2 ** attempt)
            print(f"[RETRY] API tra {e.code} - doi {wait}s roi goi lai "
                  f"(lan {attempt + 1}/{RETRY_MAX})")
            time.sleep(wait)
    latency_ms = round((time.perf_counter() - t0) * 1000)

    # DAP AN TODO 1: nhat so tu usage_metadata.
    # SDK tra None (khong phai 0) cho field vang mat -> `or 0` do tung field,
    # khong thi cong tien ben duoi TypeError giua phien.
    usage = response.usage_metadata
    prompt_tokens = (usage.prompt_token_count or 0) if usage else 0
    output_tokens = (usage.candidates_token_count or 0) if usage else 0
    thoughts_tokens = (usage.thoughts_token_count or 0) if usage else 0
    cached_tokens = (usage.cached_content_token_count or 0) if usage else 0

    # DAP AN TODO 2: tien = token/1M * gia-per-1M.
    # thoughts tinh gia OUTPUT (model "viet ra de suy nghi" = van la sinh token).
    # cached_tokens THUC TE duoc giam gia ~75% nhung minh tinh du gia cho don gian
    # -> so hoi DOI len 1 chut (sai ve phia an toan cho ngan sach).
    cost_usd = (
        prompt_tokens * PRICE["input"]
        + (output_tokens + thoughts_tokens) * PRICE["output"]
    ) / 1_000_000

    # DAP AN TODO 3 (nua dau): cong don vao so tong cua PHIEN -
    # dict truyen theo THAM CHIEU nen call_llm sua la run_agent thay
    totals["calls"] += 1
    totals["prompt_tokens"] += prompt_tokens
    totals["output_tokens"] += output_tokens + thoughts_tokens
    totals["cost_usd"] += cost_usd
    totals["latency_ms"] += latency_ms

    log_llm_call({
        "ts": time.strftime("%Y-%m-%d %H:%M:%S"),
        "run_id": totals["run_id"],   # Tuan 4: moi muc checklist = 1 run -> group theo cot nay
        "phase": phase,               # "loop" hay "chot" - biet cu goi nao dat
        "step": step,
        "model": MODEL,
        "prompt_tokens": prompt_tokens,
        "output_tokens": output_tokens,
        "thoughts_tokens": thoughts_tokens,
        "cached_tokens": cached_tokens,
        "latency_ms": latency_ms,
        "cost_usd": round(cost_usd, 6),
        # ten tool model goi luot nay -> Tuan 4 doi chieu "step dat = hanh dong gi"
        "function_calls": [fc.name for fc in (response.function_calls or [])],
    })
    return response


# ============================================================
# VONG LAP ReAct - trai tim Ngay 15-17.
# ============================================================

def run_agent(question: str, max_steps: int = MAX_STEPS, run_id: str = ""):
    """Vo boc mong (Ngay 18): mo so tong -> chay vong audit -> in tong ket.

    Ngay 23 (phuong an A): return (report, totals) thay vi chi report -
    orchestrator audit.py can $/muc, lay thang tu nguon thay vi doc nguoc
    agent_log.jsonl (ghim format log = gay im lang khi log doi cot).
    run_id cho phep ben ngoai dat ten phien (vd 'SEC-01') de group so log
    theo MUC checklist; de trong = tu sinh timestamp nhu cu.

    DAP AN TODO 3 (nua sau): _audit_loop co 4 duong return (nhanh A, submit
    trong vong, cu chot pass, cu chot WARN) - dat print o tung duong = quen.
    try/finally = MOT diem thoat duy nhat cho so sach: return duong nao,
    tham chi crash, finally cung chay.
    """
    totals = {
        "run_id": run_id or time.strftime("%Y%m%d-%H%M%S"),
        "calls": 0, "prompt_tokens": 0, "output_tokens": 0,
        "cost_usd": 0.0, "latency_ms": 0,
    }
    try:
        # dau phay tao TUPLE: (bao_cao_tu_audit_loop, so_tong) - 2 mon ve cung chuyen
        return _audit_loop(question, max_steps, totals), totals
    finally:
        print(
            f"\n[$ TONG KET run {totals['run_id']}] {totals['calls']} cu goi LLM"
            f" | in {totals['prompt_tokens']:,} tok | out {totals['output_tokens']:,} tok"
            f" | ~${totals['cost_usd']:.4f} | LLM chiem {totals['latency_ms'] / 1000:.1f}s"
        )


def _audit_loop(question: str, max_steps: int, totals: dict) -> str:
    config = types.GenerateContentConfig(
        system_instruction=SYSTEM_PROMPT,
        # Gio tool tron duoc 2 kieu: 3 HAM (SDK doc docstring tu sinh schema)
        # + 1 declaration tay (cua ra) - SDK tu quy doi ca hai
        tools=[read_file, grep, list_files, submit_tool],
        automatic_function_calling=types.AutomaticFunctionCallingConfig(
            disable=True  # TU cam lai vong lap -> thay duoc trace tung buoc
        ),
    )
    # Lich su hoi thoai - "tri nho" duy nhat cua agent giua cac buoc
    contents = [types.Content(role="user", parts=[types.Part(text=question)])]

    tools_called = set()   # trace nhung tool DA THUC THI - nguyen lieu cho guardrail
    rejections = 0         # dem so lan guardrail tu choi (de biet khi nao mo duong thoat)

    for step in range(1, max_steps + 1):
        # Ngay 18: di qua tram can thay vi goi client truc tiep
        response = call_llm(contents, config, step, phase="loop", totals=totals)
        print(f"\n--- Step {step} ---")

        # Thought: model thuong kem 1 doan text giai thich truoc khi goi tool
        for part in (response.candidates[0].content.parts or []):
            if part.text:
                print(f"Thought: {part.text.strip()}")

        # A) Model khong goi tool nua -> MUON ket thuc bang text thuong.
        # REVIEW-FIX 7/7 #1: truoc day nhanh nay van RETURN text khi da read_file
        # -> mau thuan luat "submit_findings la CUA RA DUY NHAT" (Ngay 17).
        # Nay KHONG con duong return text nao: doi nguoc toi da MAX_REJECTIONS
        # lan, van ly text -> break xuong cu chot mode='ANY' (luat vat ly ep nop).
        if not response.function_calls:
            # Ghi so DUNG THU TU NHAN QUA: model noi gi TRUOC -> the gioi dap gi SAU.
            # (Dao nguoc = so ke lao "model tra loi bat chap lenh tu choi" -> model hoc lao,
            #  khong 400 nao bao - chet im lang kieu 3.)
            # FIX 400-role (Ngay 23): model co the tra content RONG TRON - khong text,
            # khong function_call (CRY-02/03: step khong in Thought nao). Append content
            # rong vao so -> cu goi sau 400 'Please use a valid role'. Rong thi khong
            # co gi de ghi -> bo qua, chi ghi loi doi nguoc cua guardrail ben duoi.
            model_content = response.candidates[0].content
            if model_content is not None and model_content.parts:
                contents.append(model_content)  # cau text BI VUT van phai vao so
            if rejections < MAX_REJECTIONS:
                rejections += 1
                chua_doc = "read_file" not in tools_called
                print(f"[GUARDRAIL] Tu choi lan {rejections}: "
                      + ("chua read_file file nao" if chua_doc else "ket thuc bang text thuong"))
                # 2 benh khac nhau -> 2 don thuoc: chua doc code thi bat di doc,
                # doc roi ma thoat sai cua thi chi ve dung cua
                contents.append(types.Content(
                    role="user",
                    parts=[types.Part(text=GUARDRAIL_MSG if chua_doc else EXIT_MSG)],
                ))
                continue   # KHONG return - ep vong lap chay tiep
            break   # het kien nhan -> roi xuong CU CHOT ep submit_findings

        # B) Ghi QUYET DINH cua model vao "cuon so" TRUOC khi ghi ket qua tool
        # (API stateless - thieu luot nay la function_response mo coi -> loi 400)
        contents.append(response.candidates[0].content)

        # Model duoc phep goi NHIEU tool trong 1 luot (parallel function calling).
        # HOP DONG API: luot model co N function_call parts -> luot dap phai la
        # MOT Content chua DUNG N function_response parts (khong phai N Content le).
        # Vi pham -> 400 "number of function response parts..." (do that 5/7).
        response_parts = []
        for fc in response.function_calls:
            args = dict(fc.args)  # args da la dict san - KHONG parse gi ca
            print(f"Action: {fc.name}({args})")
            tools_called.add(fc.name)   # ghi trace: tool nay DA duoc goi that

            if fc.name == "submit_findings":
                # NAC B (Ngay 17): cua ra CO nguoi gac. Fail -> loi doi nguoc
                # qua function_response (model coi nhu ket qua tool) va vong lap
                # CHAY TIEP; pass -> day la loi ra duy nhat co ket qua sach.
                error = validate_report(args, tools_called)
                if error:
                    print(f"[VALIDATOR] doi nguoc: {error.splitlines()[0]} "
                          f"(+{max(0, len(error.splitlines()) - 1)} loi nua)")
                    response_parts.append(types.Part.from_function_response(
                        name=fc.name, response={"result": error}))
                    continue   # KHONG return - cho model sua roi nop lai

                pretty = json.dumps(args, ensure_ascii=False, indent=2)
                print("\n=== SUBMIT_FINDINGS (JSON - validator PASS) ===")
                print(pretty)
                return pretty

            if fc.name in TOOLS:
                # C) Goi tool that: ** bung dict args thanh keyword arguments
                # vd fc.args = {'pattern': 'md5'} -> grep(pattern='md5')
                # FIX TypeError (Ngay 23): model bia tham so khong co trong schema
                # (INP-01: grep(directory=...)) -> khong duoc de 1 cu goi lao
                # giet ca phien. Tra loi lam OBSERVATION de model doc va tu sua
                # o luot sau (defensive tool - cung ho vaccine \x08, chuan hoa ext).
                try:
                    observation = TOOLS[fc.name](**args)
                except Exception as e:
                    observation = (f"Error: goi {fc.name} that bai - "
                                   f"{type(e).__name__}: {e}. Xem lai tham so hop le "
                                   f"trong mo ta tool roi goi lai cho dung.")
            else:
                observation = f"Error: unknown tool '{fc.name}'"

            print(f"Observation: {observation[:200]}{'...' if len(observation) > 200 else ''}")

            response_parts.append(
                types.Part.from_function_response(
                    name=fc.name, response={"result": observation}
                )
            )

        # Gom TAT CA ket qua tool cua luot nay vao 1 Content role 'user'
        # (API Gemini chi co 2 role: user/model - ket qua tool doi mu 'user')
        contents.append(types.Content(role="user", parts=response_parts))

    # HET BUDGET -> CU CHOT CUONG CHE (Ngay 17 - tang 3 thang luat).
    # Ngay 16 cu chot rut het tool + bat tra text = tu KHOA cua ra moi
    # (2 luat da nhau: prompt doi submit_findings, config chi cho text
    #  -> luat vat ly thang, model tra text - do that trace 6/7).
    # Nay dao nguoc: chi dua DUY NHAT submit_tool + mode='ANY' -> API
    # chan duong text, model bat buoc nop bao cao dung schema.
    print(f"\n[HARNESS] Het {max_steps} steps -> CU CHOT mode='ANY': ep goi submit_findings")
    contents.append(types.Content(role="user", parts=[types.Part(text=FINAL_SUMMARY_MSG)]))
    chot_config = types.GenerateContentConfig(
        system_instruction=SYSTEM_PROMPT,
        tools=[submit_tool],   # 1 cua duy nhat - khong con grep/read de "dieu tra them"
        tool_config=types.ToolConfig(
            function_calling_config=types.FunctionCallingConfig(
                mode="ANY",    # cam tra text - phai goi function
                allowed_function_names=["submit_findings"],
            )
        ),
        automatic_function_calling=types.AutomaticFunctionCallingConfig(disable=True),
    )
    pretty = None
    for attempt in (1, 2):    # het budget dieu tra -> nguoi gac chi doi 1 lan
        # cu chot CUNG phai qua tram can - chinh la cu goi DAT NHAT (contents dai nhat)
        final = call_llm(contents, chot_config,
                         step=max_steps + attempt, phase="chot", totals=totals)
        if not final.function_calls:
            # mode='ANY' ma khong co function_call = bat thuong -> mo hop den
            print(f"[DEBUG] finish_reason={final.candidates[0].finish_reason}")
            return final.text or f"Agent dung o max_steps={max_steps} ma khong nop duoc bao cao."

        args = dict(final.function_calls[0].args)
        pretty = json.dumps(args, ensure_ascii=False, indent=2)
        error = validate_report(args, tools_called)
        if not error:
            print(f"\n=== SUBMIT_FINDINGS (JSON - cu chot, validator PASS lan {attempt}) ===")
            print(pretty)
            return pretty

        print(f"[VALIDATOR] cu chot lan {attempt}: {error.splitlines()[0]} "
              f"(+{max(0, len(error.splitlines()) - 1)} loi nua)")
        if attempt == 1:
            # doi 1 lan: ghi so dung thu tu model-truoc-the-gioi-sau roi goi lai
            contents.append(final.candidates[0].content)
            contents.append(types.Content(role="user", parts=[
                types.Part.from_function_response(
                    name="submit_findings", response={"result": error})
            ]))

    # dội lan 2 van hong -> nop kem canh bao thay vi treo (chong deadlock,
    # cung triet ly MAX_REJECTIONS): bao cao van machine-readable, loi da in ro
    print("[VALIDATOR-WARN] bao cao cuoi VAN con loi hinh thuc - nop kem canh bao")
    print(pretty)
    return pretty


def init(codebase_dir: str = "") -> None:
    """MOT CUA KHOI TAO duy nhat (Ngay 23) - CLI lan orchestrator deu di qua day.

    Import agent.py chi chay code MUC MODULE - khoi __main__ ben duoi KHONG chay
    -> khong co client -> run_agent no ngay cu goi LLM dau tien. Ai muon dung
    module nay (chinh no, audit.py, sau nay LangGraph node) phai goi init() truoc.
    """
    global client, CODEBASE_DIR   # gan vao bien MODULE, khong phai bien cuc bo

    # Guard env truoc khi tao client - loi ro rang thay vi stacktrace kho hieu
    if not (os.environ.get("GOOGLE_GENAI_USE_VERTEXAI") or os.environ.get("GEMINI_API_KEY")):
        sys.exit(
            "Chua set backend LLM. Vertex: GOOGLE_GENAI_USE_VERTEXAI=True + "
            "GOOGLE_CLOUD_PROJECT + GOOGLE_CLOUD_LOCATION. Hoac: GEMINI_API_KEY."
        )
    if codebase_dir:              # orchestrator truyen repo dich vao day
        CODEBASE_DIR = codebase_dir
    client = genai.Client()  # dual-mode: tu doc env, y het call_gemini cua mini_rag


if __name__ == "__main__":
    init()   # CODEBASE_DIR da doc tu argv[1] o dau file -> khong can truyen lai

    print(f"Codebase: {CODEBASE_DIR}\nModel: {MODEL} | max_steps={MAX_STEPS}")
    while True:
        q = input("\nQuestion (hoac 'quit'): ").strip()
        if q.lower() in ("quit", "exit", ""):
            break
        # run_agent gio tra TUPLE (report, totals) - khong hung du 2 mon thi
        # answer se la ca tuple -> print sai IM LANG (khong crash!).
        # Che do interactive khong can totals -> vut bang `_` (quy uoc Python).
        answer, _ = run_agent(q)
        print(f"\n=== FINAL ANSWER ===\n{answer}")
