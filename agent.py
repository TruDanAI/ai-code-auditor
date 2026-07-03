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
MAX_STEPS = 6                     # luat cua MINH: qua 6 buoc thi dung, khong loop vo han

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

def read_file(filepath: str) -> str:
    """Doc noi dung mot file trong codebase.

    Dung khi da biet duong dan file (tu ket qua grep/list_files) va can xem
    noi dung day du de phan tich.

    Args:
        filepath: duong dan TUONG DOI tinh tu goc codebase, vd 'core/webhook.js'.
    """
    full_path = os.path.join(CODEBASE_DIR, filepath)
    try:
        with open(full_path, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read()
    except OSError:
        return f"Error: khong doc duoc file '{filepath}' (sai duong dan?)"
    if len(content) > 3000:
        # observation dai = token phinh theo TUNG vong lap (moi call gui lai het lich su)
        content = content[:3000] + "\n... [TRUNCATED - file dai hon 3000 ky tu]"
    return content


def grep(pattern: str) -> str:
    """Tim pattern (regex, khong phan biet hoa thuong) trong toan bo file .js/.md/.json.

    Dung DAU TIEN khi can dinh vi: ten ham, ten bien, thuat toan (vd 'createHmac',
    'aes-256'), chuoi bao mat... Tra ve toi da 50 dong khop dang 'file:line: noi_dung'.

    Args:
        pattern: chuoi hoac regex can tim, vd 'createHmac' hoac 'md5|sha1'.

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

    matches = []
    for root, dirs, files in os.walk(CODEBASE_DIR):
        dirs[:] = [d for d in dirs if d not in IGNORE_DIRS]   # cat nhanh cay thu muc rac
        for name in files:
            if not name.endswith(ALLOWED_EXT):
                continue
            path = os.path.join(root, name)
            rel = os.path.relpath(path, CODEBASE_DIR)
            try:
                with open(path, "r", encoding="utf-8", errors="ignore") as f:
                    for lineno, line in enumerate(f, start=1):
                        if rx.search(line):
                            # TU LAP format 'file:line: noi_dung' -> nguyen lieu citation
                            matches.append(f"{rel}:{lineno}: {line.strip()[:160]}")
            except OSError:
                continue

    if not matches:
        return f"No matches found for '{pattern}'"
    out = "\n".join(matches[:50])
    if len(matches) > 50:
        out += f"\n... [con {len(matches) - 50} dong khop nua bi cat - hay grep pattern cu the hon]"
    return out


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

    for step in range(1, max_steps + 1):
        response = client.models.generate_content(
            model=MODEL, contents=contents, config=config
        )
        print(f"\n--- Step {step} ---")

        # Thought: model thuong kem 1 doan text giai thich truoc khi goi tool
        for part in (response.candidates[0].content.parts or []):
            if part.text:
                print(f"Thought: {part.text.strip()}")

        # A) Dieu kien KET THUC: model khong goi tool nua -> text = Answer cuoi
        if not response.function_calls:
            return response.text

        # B) Ghi QUYET DINH cua model vao "cuon so" TRUOC khi ghi ket qua tool
        # (API stateless - thieu luot nay la function_response mo coi -> loi 400)
        contents.append(response.candidates[0].content)

        for fc in response.function_calls:
            args = dict(fc.args)  # args da la dict san - KHONG parse gi ca
            print(f"Action: {fc.name}({args})")

            if fc.name in TOOLS:
                # C) Goi tool that: ** bung dict args thanh keyword arguments
                # vd fc.args = {'pattern': 'md5'} -> grep(pattern='md5')
                observation = TOOLS[fc.name](**args)
            else:
                observation = f"Error: unknown tool '{fc.name}'"

            print(f"Observation: {observation[:200]}{'...' if len(observation) > 200 else ''}")

            # Gui ket qua tool lai cho model: Part.from_function_response,
            # dong vai luot 'user' (API Gemini chi co 2 role: user/model)
            contents.append(
                types.Content(
                    role="user",
                    parts=[types.Part.from_function_response(
                        name=fc.name, response={"result": observation}
                    )],
                )
            )

    return f"Agent dung o max_steps={max_steps} ma chua co Answer cuoi (xem trace o tren)."


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
