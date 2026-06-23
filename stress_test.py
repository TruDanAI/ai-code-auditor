"""
stress_test.py - Ngày 6: Stress-test hallucination cho mini_rag.

Mục tiêu: bắn 1 bộ 10 câu hỏi CỐ ĐỊNH (5 câu có đáp án trong code,
4 câu KHÔNG có để thử rào chắn, 1 câu kiểm tra test framework) vào
pipeline đã xây ở mini_rag.py, rồi GHI transcript ra file để chấm tay.

Đây KHÔNG phải code RAG mới - nó chỉ TÁI DÙNG mini_rag.py và lặp.

CHẠY:
    venv\\Scripts\\Activate.ps1
    $env:GEMINI_API_KEY = "key_cua_ban"
    python stress_test.py C:\\Users\\Pc\\Desktop\\chatbot-fanpage
"""

import sys
import time

# Tái dùng nguyên các hàm bạn đã tự viết/đã có ở Ngày 1-5.
from mini_rag import (
    load_embedding_model,
    build_index,
    embed_texts,
    retrieve_top_k,
    build_prompt,
    call_gemini,
)


def call_gemini_resilient(prompt, max_retries=4):
    """
    Bọc call_gemini với retry + backoff.
    - 503 UNAVAILABLE (server Google quá tải, lỗi CỦA HỌ): thử lại,
      mỗi lần đợi gấp đôi (2s, 4s, 8s...) = exponential backoff.
    - 429 RESOURCE_EXHAUSTED (hết quota free CỦA BẠN): đợi/retry vô ích
      trong ngắn hạn -> dừng sớm, báo rõ để bạn đổi model hoặc đợi.
    - Hết số lần thử: trả về chuỗi đánh dấu để vòng lặp GHI rồi CHẠY TIẾP,
      không làm chết cả mẻ 10 câu.
    """
    for attempt in range(max_retries):
        try:
            return call_gemini(prompt)
        except Exception as e:
            msg = str(e)
            if "429" in msg or "RESOURCE_EXHAUSTED" in msg:
                return "[LỖI API: 429 hết quota free — đổi model rẻ hơn hoặc đợi reset]"
            if "503" in msg or "UNAVAILABLE" in msg:
                wait = 2 ** (attempt + 1)          # 2s, 4s, 8s, 16s
                print(f"    503 quá tải, thử lại sau {wait}s "
                      f"({attempt + 1}/{max_retries})...")
                time.sleep(wait)
                continue
            return f"[LỖI API khác: {msg[:120]}]"   # lỗi lạ -> ghi lại, chạy tiếp
    return "[LỖI API: 503 vẫn quá tải sau nhiều lần thử]"

# Câu mà model nên thốt ra khi context không chứa thông tin (xem build_prompt).
# Dùng để TỰ ĐỘNG đoán "từ chối hay không" - chỉ là gợi ý, bạn vẫn chấm tay.
REFUSAL_MARKER = "không tìm thấy thông tin"

# Bộ test cố định - bê đúng từ bảng trong lo-trinh-chi-tiet.md (Ngày 6).
# in_code = câu này CÓ đáp án thật trong codebase hay không.
QUESTIONS = [
    {"q": "verifySignature dùng thuật toán gì?",            "in_code": True,  "expect": "HMAC-SHA256, timingSafeEqual"},
    {"q": "credential encryption dùng mode gì?",            "in_code": True,  "expect": "AES-256-GCM"},
    {"q": "lead parser hoạt động thế nào?",                 "in_code": True,  "expect": "Trích tên/SĐT/địa chỉ từ tin nhắn"},
    {"q": "multi-shop isolation hoạt động ra sao?",         "in_code": True,  "expect": "Tách config theo shops/SHOP_ID"},
    {"q": "RBAC có mấy vai trò?",                           "in_code": True,  "expect": "4: viewer/support/maintainer/owner"},
    {"q": "module thanh toán Stripe hoạt động thế nào?",    "in_code": False, "expect": "TỪ CHỐI (không có Stripe)"},
    {"q": "hệ thống tích hợp với Zalo OA ra sao?",          "in_code": False, "expect": "TỪ CHỐI (không có Zalo)"},
    {"q": "database dùng MongoDB phải không?",              "in_code": False, "expect": "TỪ CHỐI / là PostgreSQL"},
    {"q": "có dùng Redis cache không?",                     "in_code": False, "expect": "TỪ CHỐI (không có Redis)"},
    {"q": "unit test framework là gì?",                     "in_code": True,  "expect": "Node test runner hoặc Jest"},
]


def run():
    if len(sys.argv) < 2:
        print("Usage: python stress_test.py /path/to/chatbot-fanpage")
        sys.exit(1)
    root_dir = sys.argv[1]

    # 1) Load model + index MỘT LẦN (không lặp lại cho từng câu).
    print("Loading embedding model...")
    model = load_embedding_model()
    print(f"Indexing {root_dir} ...")
    index = build_index(root_dir, model)
    print(f"Indexed {len(index['chunks'])} chunks "
          f"from {len({c['path'] for c in index['chunks']})} files.\n")

    out_lines = ["# Ngày 6 — Baseline Stress-Test (chatbot-fanpage)\n"]
    out_lines.append(f"_Index: {len(index['chunks'])} chunks, model = all-MiniLM-L6-v2, model LLM = gemini-3.5-flash_\n")

    n_refused = 0
    for i, item in enumerate(QUESTIONS, start=1):
        question = item["q"]

        # 2) Đúng pipeline Ngày 5: embed câu hỏi -> top-K -> prompt -> Gemini.
        q_emb = embed_texts(model, [question])[0]
        top = retrieve_top_k(q_emb, index)
        answer = call_gemini_resilient(build_prompt(question, top))

        # 3) Tự đoán từ chối hay không (chỉ heuristic, KHÔNG chấm đúng/sai).
        refused = REFUSAL_MARKER in answer.lower()
        if refused:
            n_refused += 1
        auto_tag = "[TỪ CHỐI]" if refused else "[CÓ TRẢ LỜI]"

        # In nhanh ra màn hình để theo dõi.
        print(f"--- Q{i}: {question}  {auto_tag}")
        for c in top:
            print(f"    [{c['score']:.3f}] {c['path']} (chunk {c['chunk_id']})")

        # Ghi vào transcript để chấm tay (cột Đúng/Bịa bạn tự điền).
        out_lines.append(f"\n## Q{i}. {question}")
        out_lines.append(f"- **Có trong code?** {'CÓ' if item['in_code'] else 'KHÔNG'}  |  **Kỳ vọng:** {item['expect']}")
        out_lines.append(f"- **Top-3 chunk lấy được:**")
        for c in top:
            out_lines.append(f"  - `{c['score']:.3f}` {c['path']} (chunk {c['chunk_id']})")
        out_lines.append(f"- **Auto-tag:** {auto_tag}")
        out_lines.append(f"- **Trả lời của model:**\n\n> " + answer.replace("\n", "\n> "))
        out_lines.append(f"- **Chấm tay:** [ ] Đúng  [ ] Bịa  [ ] Từ chối đúng lúc")

        # GHI FILE SAU MỖI CÂU -> crash giữa chừng vẫn giữ tiến độ đã chạy.
        with open("docs/ngay6-baseline.md", "w", encoding="utf-8") as f:
            f.write("\n".join(out_lines))

        time.sleep(2)   # nghỉ nhẹ giữa các câu, đỡ dồn server (đỡ 503/429).

    # 4) Tóm tắt baseline.
    out_lines.append("\n---\n")
    out_lines.append(f"**Tự động:** {n_refused}/{len(QUESTIONS)} câu bị từ chối. "
                    f"(Kỳ vọng tối thiểu: 4 câu KHÔNG-có-trong-code phải bị từ chối.)")
    out_lines.append("**Chấm tay tổng:** ___ đúng / ___ bịa / ___ từ chối — đây là BASELINE cho Tuần 2.")

    with open("docs/ngay6-baseline.md", "w", encoding="utf-8") as f:
        f.write("\n".join(out_lines))
    print(f"\nĐã ghi transcript -> docs/ngay6-baseline.md")
    print(f"Auto: {n_refused}/{len(QUESTIONS)} câu bị từ chối. Giờ mở file đó chấm tay đúng/bịa.")


if __name__ == "__main__":
    run()
