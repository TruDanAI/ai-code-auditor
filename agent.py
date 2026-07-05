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

import os
import re
import sys

from google import genai
from google.genai import types

MODEL = "gemini-2.5-flash-lite"   # loop goi LLM nhieu lan -> model re (REV 2/7)
MAX_STEPS = 10                    # nang 6->10 (do that Ngay 16: guardrail an ~1 step tu choi
                                  # + 2-3 step dieu tra bu -> 6 la chet non giua chung)

# Guardrail tang HARNESS (Ngay 16): luat kiem tra duoc bang code thi KHONG nho prompt giu.
# Prompt = loi khuyen (model nho lo duoc - da do o vong 5); code = luat cung 100%.
MAX_REJECTIONS = 2   # duong thoat chong deadlock: tu choi toi da 2 lan roi van cho ra
GUARDRAIL_MSG = (
    "TU CHOI cau tra loi: ban chua he read_file file nao. "
    "Ket luan audit phai dua tren CODE DA DOC, khong phai mo ta tu grep/README. "
    "Quay lai Buoc 2: read_file it nhat 1 file lien quan tim duoc tu grep, roi moi ket luan."
)
FINAL_SUMMARY_MSG = (
    "HET LUOT DIEU TRA - dung goi them tool. "
    "Tong ket NGAY findings tu nhung observation da co o tren: "
    "moi ket luan kem citation file:line; "
    "vung nao chua kip kiem tra thi khai ro 'CHUA KIEM TRA' - khong duoc suy dien."
)

# Auditor PHAI nhin thay tests/ va shops/ (bai hoc Ngay 9: IGNORE_DIRS cua
# mini_rag loai tests/ lam ground-truth rot khoi corpus). Agent chi bo rac that.
IGNORE_DIRS = {"node_modules", ".git"}
ALLOWED_EXT = (".js", ".md", ".json")

CODEBASE_DIR = sys.argv[1] if len(sys.argv) > 1 else r"C:\Users\Pc\Desktop\chatbot-fanpage"


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

    allowed = (ext,) if ext else ALLOWED_EXT   # model tu chon loc, mac dinh nhu cu

    # Gom khop THEO FILE de ap tran tung file - 1 file lam to (vd DESIGN.md)
    # khong duoc phep chiem het cho cua ca danh sach (bai hoc tran-50-dong Ngay 15/16)
    by_file = {}
    for root, dirs, files in os.walk(CODEBASE_DIR):
        dirs[:] = [d for d in dirs if d not in IGNORE_DIRS]   # cat nhanh cay thu muc rac
        for name in files:
            if not name.endswith(allowed):
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
- Tra loi ngan gon bang tieng Viet."""



# ============================================================
# VONG LAP ReAct - trai tim bai hom nay. 3 cho TODO cho em lap.
# ============================================================

def run_agent(question: str, max_steps: int = MAX_STEPS) -> str:
    config = types.GenerateContentConfig(
        system_instruction=SYSTEM_PROMPT,
        tools=[read_file, grep, list_files],  # truyen HAM -> SDK tu sinh schema
        automatic_function_calling=types.AutomaticFunctionCallingConfig(
            disable=True  # TU cam lai vong lap -> thay duoc trace tung buoc
        ),
    )
    # Lich su hoi thoai - "tri nho" duy nhat cua agent giua cac buoc
    contents = [types.Content(role="user", parts=[types.Part(text=question)])]

    tools_called = set()   # trace nhung tool DA THUC THI - nguyen lieu cho guardrail
    rejections = 0         # dem so lan guardrail tu choi (de biet khi nao mo duong thoat)

    for step in range(1, max_steps + 1):
        response = client.models.generate_content(
            model=MODEL, contents=contents, config=config
        )
        print(f"\n--- Step {step} ---")

        # Thought: model thuong kem 1 doan text giai thich truoc khi goi tool
        for part in (response.candidates[0].content.parts or []):
            if part.text:
                print(f"Thought: {part.text.strip()}")

        # A) Model khong goi tool nua -> MUON ket thuc. Guardrail kiem tra TRUOC khi cho ra.
        if not response.function_calls:
            if "read_file" not in tools_called and rejections < MAX_REJECTIONS:
                rejections += 1
                print(f"[GUARDRAIL] Tu choi lan {rejections}: chua read_file file nao")
                # Ghi so DUNG THU TU NHAN QUA: model noi gi TRUOC -> the gioi dap gi SAU.
                # (Dao nguoc = so ke lao "model tra loi bat chap lenh tu choi" -> model hoc lao,
                #  khong 400 nao bao - chet im lang kieu 3.)
                contents.append(response.candidates[0].content)  # cau tra loi BI VUT van phai vao so
                contents.append(
                    types.Content(role="user", parts=[types.Part(text=GUARDRAIL_MSG)])
                )
                continue   # KHONG return - ep vong lap chay tiep tu Buoc 2

            answer = response.text
            if not answer:
                # Answer rong = chet im lang -> mo hop den: model DUNG vi ly do gi?
                cand = response.candidates[0]
                print(f"[DEBUG] finish_reason={cand.finish_reason} | parts={cand.content.parts}")
            return answer

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

            if fc.name in TOOLS:
                # C) Goi tool that: ** bung dict args thanh keyword arguments
                # vd fc.args = {'pattern': 'md5'} -> grep(pattern='md5')
                observation = TOOLS[fc.name](**args)
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

    # HET BUDGET nhung KHONG nop giay trang: findings da nam trong so (contents),
    # ep 1 cu goi CHOT de model tong ket chung. Van la "model truoc - the gioi sau":
    # luot model cuoi + function_response da duoc append trong vong lap roi.
    print(f"\n[HARNESS] Het {max_steps} steps -> goi CHOT (khong tool) de tong ket findings")
    contents.append(types.Content(role="user", parts=[types.Part(text=FINAL_SUMMARY_MSG)]))
    final = client.models.generate_content(
        model=MODEL,
        contents=contents,
        # config MOI, KHONG truyen tools: model het duong goi tool,
        # chi con mot loi thoat duy nhat la tra loi bang text
        config=types.GenerateContentConfig(system_instruction=SYSTEM_PROMPT),
    )
    return final.text or f"Agent dung o max_steps={max_steps} ma van khong tong ket duoc (xem trace)."


if __name__ == "__main__":
    # Guard env truoc khi tao client - loi ro rang thay vi stacktrace kho hieu
    if not (os.environ.get("GOOGLE_GENAI_USE_VERTEXAI") or os.environ.get("GEMINI_API_KEY")):
        sys.exit(
            "Chua set backend LLM. Vertex: GOOGLE_GENAI_USE_VERTEXAI=True + "
            "GOOGLE_CLOUD_PROJECT + GOOGLE_CLOUD_LOCATION. Hoac: GEMINI_API_KEY."
        )
    client = genai.Client()  # dual-mode: tu doc env, y het call_gemini cua mini_rag

    print(f"Codebase: {CODEBASE_DIR}\nModel: {MODEL} | max_steps={MAX_STEPS}")
    while True:
        q = input("\nQuestion (hoac 'quit'): ").strip()
        if q.lower() in ("quit", "exit", ""):
            break
        answer = run_agent(q)
        print(f"\n=== FINAL ANSWER ===\n{answer}")
