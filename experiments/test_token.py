"""
test_token.py — Ngày 1: cảm nhận TOKEN & CONTEXT WINDOW bằng số thật.

Chạy:
    python test_token.py

LƯU Ý BẢN CHẤT (đọc kỹ - hay bị hỏi phỏng vấn):
    tiktoken là tokenizer của OpenAI (encoding "cl100k_base"). Gemini dùng
    tokenizer RIÊNG, nên con số ở đây là ƯỚC LƯỢNG để HỌC, không phải số
    token chính xác Gemini sẽ tính tiền. Dù vậy, các quy luật ta quan sát
    (tiếng Việt tốn nhiều token hơn, code chiếm bao nhiêu % context) vẫn
    đúng về mặt xu hướng cho mọi tokenizer.
"""

import tiktoken

# Lấy bộ mã hoá. "cl100k_base" là bảng token phổ biến, dùng để minh hoạ.
enc = tiktoken.get_encoding("cl100k_base")


# -------------------------------------------------------------------
# PHẦN 1: Tiếng Việt vs Tiếng Anh — cùng nội dung, khác số token
# -------------------------------------------------------------------
vi = "Xác thực chữ ký webhook từ Facebook bằng HMAC-SHA256"
en = "Verify webhook signature from Facebook using HMAC-SHA256"

vi_tokens = enc.encode(vi)   # encode() biến chuỗi -> danh sách số nguyên (token id)
en_tokens = enc.encode(en)

print("=== PHẦN 1: Tiếng Việt vs Tiếng Anh ===")
print(f"Tiếng Việt: {len(vi_tokens)} tokens")   # len() = đếm số token
print(f"Tiếng Anh:  {len(en_tokens)} tokens")
# Tỉ lệ VI/EN: kỳ vọng > 1 (tiếng Việt tốn nhiều hơn). In 2 chữ số thập phân.
print(f"-> Tiếng Việt tốn gấp {len(vi_tokens) / len(en_tokens):.2f} lần tiếng Anh\n")


# -------------------------------------------------------------------
# PHẦN 2: Đo token thật của một file code lớn
# -------------------------------------------------------------------
# Đường dẫn THẬT tới file rules.js trong repo chatbot-fanpage.
# (chatbot-fanpage nằm TRỰC TIẾP trên Desktop, KHÔNG trong "Build CV")
RULES_PATH = r"C:\Users\Pc\Desktop\chatbot-fanpage\core\rules.js"

# Context window của Gemini 3.5 Flash (số token tối đa cho 1 lần gọi).
GEMINI_CONTEXT_WINDOW = 1_048_576  # ~1 triệu token

print("=== PHẦN 2: Đo file thật rules.js ===")
try:
    # Mở file ở chế độ đọc, encoding utf-8 để đọc đúng dấu tiếng Việt.
    with open(RULES_PATH, "r", encoding="utf-8") as f:
        rules_text = f.read()

    n_tokens = len(enc.encode(rules_text))   # số token của cả file
    n_chars = len(rules_text)                # số ký tự, để so sánh

    print(f"rules.js: {n_chars:,} ký tự  ->  {n_tokens:,} tokens")
    # Tỉ lệ chiếm dụng context window, tính theo %.
    print(f"Chiếm {n_tokens / GEMINI_CONTEXT_WINDOW * 100:.3f}% context window Gemini 3.5 Flash")
except FileNotFoundError:
    # Nếu sai đường dẫn, in hướng dẫn thay vì để chương trình chết.
    print(f"KHÔNG tìm thấy file: {RULES_PATH}")
    print("=> Kiểm tra lại đường dẫn tới chatbot-fanpage/core/rules.js")
