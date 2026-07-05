# Kế Hoạch Nền Tảng — Python + DSA (+ Math nhẹ) chạy SONG SONG portfolio

> **⚙️ Cập nhật 1/7/2026 — track "dạy-lại-được":** phương pháp học (vòng lặp 5 bước + cổng test 60s)
> nay do [spec teach-back](superpowers/specs/2026-07-01-python-dsa-teachback-design.md) đặc tả.
> Spec đó **điều chỉnh 2 con số** dưới đây: pace nền-tảng còn **45–60 phút/ngày** và phạm vi DSA thu về
> **core** (bỏ tree/graph/DP ở track 6 tuần này — chúng vẫn nằm trong `dsa-cho-ky-su-ai.md` cho track dài).
> File NÀY vẫn là nguồn chính cho **lịch tuần, math track, và mốc kỳ vọng**.

> **Vì sao có file này (chốt 29/6/2026):** mentor trường chỉ ra cty lớn/vừa yêu cầu **DSA + Python là cổng CỨNG bắt buộc** + nền xác suất/tuyến tính. File này là track nền tảng chạy **song song** roadmap AI Code Auditor — KHÔNG thay thế nó. Portfolio = khác biệt; nền tảng = cổng vào.
>
> **Giả định thời gian:** ~1.5–2h/ngày (giả định cũ 29/6) → **track teach-back chốt lại 45–60 phút/ngày** cho nền tảng, portfolio ~2.5–3h (ban ngày). Cày nhiều/ít hơn → chỉnh pace DSA, khung giữ nguyên.
>
> **3 đồng hồ TÁCH BIỆT (đừng gộp áp lực):** ① Python-check của anh ~đầu tháng 7 → Tuần 1. ② Portfolio ~tháng 8. ③ DSA = track DÀI 2–3 tháng, tháng này chỉ KHỞI ĐỘNG.

---

## NGUYÊN TẮC (đọc lại mỗi khi nản)
1. **Không thuộc hết Python.** Lõi (Tầng 1) tự động + khái niệm (Tầng 2) hiểu sâu + đuôi dài (Tầng 3) biết TRA. Senior cũng google mỗi ngày.
2. **Học qua LÀM, không học vẹt.** Tự gõ lại code của mình + làm bài → method nào cần thì học, gặp nhiều lần là thuộc.
3. **Pace bền > cày kiệt.** 1.5h ĐỀU mỗi ngày thắng 8h cuối tuần rồi bỏ 4 ngày.
4. **Đừng để DSA nuốt portfolio.** Cả hai, không chọn một bỏ một.
5. **Tự nói TO** khi giải thích code/pattern (hợp cách học của mình).

---

## TUẦN 1 (30/6 – 6/7) — PYTHON FLUENCY SPRINT
**Mục tiêu:** chắc Tầng 1 + Tầng 2, QUA bài kiểm tra Python của anh. Học qua chính code `mini_rag` của mình.

- [ ] **T2 30/6 — Tự gõ lại KHÔNG AI: `cosine_similarity` + `retrieve_top_k`.**
  Ôn: biến, kiểu dữ liệu, `def`/`return`, list/dict, slicing, vòng `for`. Giải thích TO từng dòng + Big-O (O(n)).
- [ ] **T3 1/7 — Tự gõ lại KHÔNG AI: `rrf_fuse` + `tokenize_for_bm25`.**
  Tâm điểm: `dict.get(key, 0)`, `enumerate(start=1)`, `sorted(key=lambda)`, comprehension. + 1 bài Easy: **Two Sum** (hashmap).
- [ ] **T4 2/7 — String + Loop (Tầng 1 phải chắc).**
  `split/join/strip/replace/lower`, f-string, slicing, `in`; `for`/`while`/`range`/`zip`, `break`/`continue`. + 1–2 Easy: **Valid Anagram, Reverse String**.
- [ ] **T5 3/7 — Cấu trúc dữ liệu + độ phức tạp.**
  `list` vs `dict` vs `set`: khi nào dùng cái nào + Big-O tra cứu (dict/set O(1) vs list O(n)). **Mutability**: copy vs reference (vì sao `dict(c)`, `list[:]`). + 1 Easy: **Contains Duplicate** (set).
- [ ] **T6 4/7 — OOP cơ bản + lỗi.**
  `class`, `__init__`, `self`, method. Bài tập: gói một mẩu `mini_rag` thành class nhỏ (vd `class Index`). `try/except`.
- [ ] **T7 5/7 — Mock Python check.**
  Tự ra 5 câu (viết 1 hàm từ spec · giải thích complexity · sửa 1 bug · dùng dict+loop · đọc-hiểu đoạn code) → tự chấm → ôn chỗ yếu.
- [ ] **CN 6/7 — Review + nói TO** (giải thích code mình cho "nhà tuyển dụng") + nghỉ.

> ✅ **Tiêu chí qua Tuần 1:** viết được 1 hàm từ spec không cần AI · giải thích Big-O code mình · dùng trôi dict/set/list + comprehension · nói được copy-vs-reference.

---

## TUẦN 2–4 — DSA THEO PATTERN (bền) + Python depth + Math nhẹ
**Nguồn (chọn 1, theo tới cùng — đừng bơi):** **NeetCode 150** (neetcode.io, có roadmap + video) hoặc **Grind 75** (grind75.com). Làm bài trên **LeetCode**.
**Cách làm MỖI bài:** tự nghĩ 15–20' → bí thì xem lời giải → **hiểu PATTERN** → đóng lời giải, **tự code lại**. (Giống đọc→sửa→giải-thích-vì-sao mình đang làm với RAG.)
**Pace:** ~2 bài/ngày (Easy → Medium). Cty lớn chủ yếu **Easy/Medium có pattern**, ít Hard.

- [ ] **Tuần 2 (7/7–13/7) — Arrays & Hashing + Two Pointers.**
  Pattern: hashmap/set để O(1) tra cứu; hai con trỏ. ~10–12 bài. (Bạn đã dùng hashmap trong `rrf_fuse` → khởi đầu quen.)
- [ ] **Tuần 3 (14/7–20/7) — Sliding Window + Stack + Binary Search.**
  Pattern: cửa sổ trượt (chuỗi con), ngăn xếp (ngoặc/monotonic), tìm nhị phân O(log n).
- [ ] **Tuần 4 (21/7–27/7) — Linked List + Trees (intro) + Recursion.**
  Con trỏ next, duyệt cây (DFS/BFS cơ bản), đệ quy.
- [ ] *(Tháng sau — nâng cao):* Graphs + Dynamic Programming. KHÔNG ép vào tháng này.

**Math nhẹ (2 buổi/tuần, ~45'):**
- [ ] **Đại số tuyến tính** (ưu tiên — liên quan trực tiếp): vector, dot product, norm, cosine (bạn đã chạm Ngày 3). Hiểu "embedding là điểm trong không gian".
- [ ] **Xác suất – Thống kê cơ bản:** phân phối, kỳ vọng, precision/recall (đã dùng), p-value/A-B test ở mức ý niệm.
- [ ] *(Giải tích: HOÃN — chủ yếu cho train model/research, học sau nếu rẽ hướng đó.)*

---

## CẤU TRÚC MỘT NGÀY (mẫu)
| Khối | Thời lượng | Việc |
|---|---|---|
| Ban ngày | ~2.5–3h | **Portfolio** (roadmap AI Code Auditor) |
| Buổi tối | ~1.5–2h | **Nền tảng** (Tuần 1: Python · Tuần 2+: DSA + math xen kẽ) |

> **⚠️ REV 2/7 — LỊCH TỐI đã hợp nhất về MỘT file:** mọi track ngoài giờ (Python, DSA, math, AWS,
> docs LangGraph/MCP, teach-back) giờ xếp lịch tại **[lich-hoc-buoi-toi.md](lich-hoc-buoi-toi.md)** —
> nguồn duy nhất, tick tiến độ ở đó, kèm 5 luật chung + luật de-scope đã duyệt trước (portfolio thắng
> tie-break đến 13/8; DSA hạ 2 bài → 1 bài khi ngày lụt). **File NÀY giữ vai:** nội dung chi tiết từng
> buổi Python/DSA/math + cột mốc dài hạn — lịch tuần bên dưới chỉ còn là THAM CHIẾU nội dung.

---

## CỘT MỐC & KỲ VỌNG THỰC TẾ
- **~Đầu tháng 7:** qua Python-check của anh. ← mục tiêu gần nhất, KHẢ THI.
- **Cuối tháng 7:** vững Python + làm trôi DSA Easy + nhiều Medium theo pattern (Arrays/Hashing, Two Pointers, Sliding Window, Stack, Binary Search, Linked List, Trees cơ bản).
- **~Tháng 8:** portfolio xong (deliverable CV).
- **DSA "sẵn sàng phỏng vấn cty lớn"** = mốc **2–3 tháng** (gồm Graphs/DP) → chạy tới lúc thật sự apply. **KHÔNG kỳ vọng xong trong 1 tháng** — tháng này là KHỞI ĐỘNG.

> Sửa file này khi đổi pace. Mỗi tối tick 1 ô = một bước. Track tiến độ DSA: đếm số bài + pattern đã nắm, không đếm giờ.
