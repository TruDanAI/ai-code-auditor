# SỔ TAY HỌC TẬP & HỆ THỐNG KIẾN THỨC (NOTES.md)

Chào mừng bạn đến với bộ não thứ hai của mình! File này được thiết kế để lưu giữ mọi khái niệm cốt lõi bạn học được trong suốt lộ trình 7 tuần xây dựng **AI Code Auditor**.

## HƯỚNG DẪN GHI CHÉP (Quy tắc 3 câu)
Mỗi khi gặp một khái niệm mới, hãy ép bản thân giải thích ngắn gọn bằng tiếng Việt theo cấu trúc sau:
1. **Vấn đề là gì?** (Nếu không có khái niệm/công nghệ này, hệ thống sẽ gặp lỗi, chạy chậm hoặc không hoạt động thế nào?)
2. **Giải pháp là gì?** (Nó giải quyết vấn đề đó bằng cơ chế hay thuật toán nào?)
3. **Khi nào KHÔNG dùng?** (Nhược điểm của nó là gì? Khi nào thì nên dùng công nghệ khác?)

---

## TUẦN 1: NỀN TẢNG RAG CƠ BẢN (BASIC RAG)

### Ngày 1: Token, Context Window & Tokenization
*   **Vấn đề là gì?**
    *   Máy không hiểu chữ thô — cần biến text thành số. Và mỗi lần gọi LLM nó chỉ "nhìn" được một lượng giới hạn = **context window** (Gemini 3.5 Flash ~1.048.576 token).
    *   Ví dụ của tôi: như một tài liệu 50 trang nhưng người đọc chỉ đọc nổi 10 trang; cố nhồi hết thì sẽ **quên dữ kiện ở giữa** ("lost in the middle"). Ngoài ra mỗi token đều **tốn tiền** (tính cả input lẫn output).
*   **Giải pháp là gì?**
    *   **Token hóa:** chia text thành các mảnh nhỏ (sub-word), mỗi mảnh là 1 số nguyên (token id). Nhờ vậy đo được độ dài text bằng token → biết một file có "nhét vừa" context window không và tốn bao nhiêu.
    *   Thực hành: `tiktoken` → `enc.encode(text)` trả về **list các token id**; `len(...)` của list đó = **số token** (khác số ký tự). Đo thật: rules.js 46.931 ký tự → 13.203 token, chỉ chiếm 1.26% context window.
*   **Khi nào KHÔNG dùng / Lưu ý quan trọng:**
    *   Số token đếm bằng `tiktoken` chỉ là **ước lượng để học** — Gemini dùng tokenizer riêng nên số tính tiền sẽ khác.
    *   **Tiếng Việt tốn ~2x token** so với tiếng Anh (đo thật: 19 vs 10). Lý do **KHÔNG phải dấu câu**, mà vì tokenizer học chủ yếu trên tiếng Anh → từ tiếng Anh gói gọn 1 token, tiếng Việt bị cắt vụn (âm tiết + dấu thanh). ⇒ làm sản phẩm cho người Việt tốn gấp đôi chi phí LLM.
    *   Với tài liệu **nhỏ + ít thay đổi**, nhồi thẳng (stuffing) là đủ, chưa cần tối ưu token hay RAG.

> 📌 **Ghi chú công cụ hôm nay — SDK Gemini cũ vs mới:**
> SDK cũ `google.generativeai` (dùng `genai.configure()` cấu hình **toàn cục**) đã bị **khai tử** → code dùng nó sẽ lỗi. SDK mới `google-genai` dùng **client tường minh**: `client = genai.Client(api_key=...)` rồi `client.models.generate_content(...)`. "Tường minh" = mọi cấu hình hiện rõ trong câu lệnh, không giấu ở state toàn cục → dễ test, chạy nhiều key/cấu hình song song được. Bẫy: hai SDK cùng import tên `genai` nhưng khác nguồn (`import google.generativeai` vs `from google import genai`).

### Ngày 2: Vector Embeddings & Mô hình biểu diễn ngữ nghĩa
*   **Vấn đề là gì?**
    *   *Ghi chép của bạn ở đây...*
*   **Giải pháp là gì?**
    *   *Ghi chép của bạn ở đây...*
*   **Khi nào KHÔNG dùng?**
    *   *Ghi chép của bạn ở đây...*

### Ngày 3: Vector Database & Lưu trữ dữ liệu (SQLite)
*   **Vấn đề là gì?**
    *   *Ghi chép của bạn ở đây...*
*   **Giải pháp là gì?**
    *   *Ghi chép của bạn ở đây...*
*   **Khi nào KHÔNG dùng?**
    *   *Ghi chép của bạn ở đây...*

### Ngày 4: Cosine Similarity & Thuật toán tìm kiếm tương đồng
*   **Vấn đề là gì?**
    *   *Ghi chép của bạn ở đây...*
*   **Giải pháp là gì?**
    *   *Ghi chép của bạn ở đây...*
*   **Khi nào KHÔNG dùng?**
    *   *Ghi chép của bạn ở đây...*

### Ngày 5: Context Packing & Kỹ thuật thiết kế Prompt RAG
*   **Vấn đề là gì?**
    *   *Ghi chép của bạn ở đây...*
*   **Giải pháp là gì?**
    *   *Ghi chép của bạn ở đây...*
*   **Khi nào KHÔNG dùng?**
    *   *Ghi chép của bạn ở đây...*

---

## TỔNG KẾT TUẦN & TỰ ĐÁNH GIÁ (Hằng tuần)
*(Mỗi tối Chủ Nhật, hãy dành 10 phút trả lời các câu hỏi tự kiểm tra trong lộ trình chi tiết và ghi điểm số của bạn tại đây)*

*   **Tuần 1:** ... / 10 điểm.
    *   *Điều tôi hiểu rõ nhất:* ...
    *   *Chỗ tôi vẫn còn lúng túng cần xem lại:* ...
