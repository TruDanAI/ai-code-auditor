# 🌙 Lịch Học Buổi Tối — MỘT nguồn duy nhất cho mọi track song song

> **Vì sao có file này (2/7/2026):** các track ngoài giờ (Python, DSA, math, AWS, docs LangGraph/MCP, teach-back)
> nằm rải ở 3 file khác nhau → quỹ tối bị triple-book mà không ai thấy. Từ nay:
> **lịch tối CHỈ xem file này** — mỗi tối đúng 1 ô, tick xong là xong. Nội dung học vẫn ở file gốc (link bên dưới).
>
> **Cập nhật lần cuối:** 2/7/2026.

---

## 5 LUẬT CHUNG (đọc lại khi thấy rối)

1. **MỘT slot tối duy nhất, ~60–90 phút.** Hết giờ = dừng. Học lố tối nay = gục tối mai — pace đều thắng cày kiệt.
2. **Nghi thức mở màn 10 phút, KHÔNG bỏ:** 3 câu recall trả lời MIỆNG, sách đóng (giao thức chống-quên trong [dsa-cho-ky-su-ai.md](dsa-cho-ky-su-ai.md)). Đây là 10 phút giá trị nhất cả buổi.
3. **Portfolio thắng mọi tie-break đến 13/8.** Ngày ban-ngày lụt → tối chỉ làm mức **min** ghi ở từng ô (đã duyệt trước, khỏi áy náy). DSA là đồng hồ 2–3 tháng; 13/8 mới là deadline thật.
4. **Tick ô = nói TO được** (vấn đề → nguyên lý → giới hạn), không phải đọc xong.
5. **Chủ Nhật = teach-back + NGHỈ.** Không học bù vào CN — nghỉ là một phần của lịch.

**Nếu vỡ lịch ≥2 ngày:** đừng nhồi bù. Dời cả khối về sau (DSA co giãn được), giữ nguyên các mốc cứng: Python-check (5/7) · nộp CV (13/8).

## Phân vai file (tránh 2 nguồn sự thật)

| File | Vai trò |
|---|---|
| **File này** | **LỊCH tối duy nhất + tick tiến độ** |
| [ke-hoach-nen-tang-python-dsa.md](ke-hoach-nen-tang-python-dsa.md) | Nội dung chi tiết Python/DSA/math + cột mốc dài hạn |
| [dsa-cho-ky-su-ai.md](dsa-cho-ky-su-ai.md) | Tra cứu DSA gắn project + giao thức chống-quên |
| [lo-trinh-chi-tiet.md](lo-trinh-chi-tiet.md) | Việc BAN NGÀY (portfolio) + nội dung AWS (section cuối) |

---

## TUẦN NÀY (2–6/7) — Chốt Python Fluency Sprint 🎯 mốc: qua Python-check

> Tuần này tối nào cũng là Python (đồng hồ gần nhất). AWS/math/DSA chưa vào — đừng ôm.

- [ ] **T4 2/7** — String + Loop (split/join/strip, f-string, zip, break/continue) + 1–2 Easy: Valid Anagram, Reverse String. *Nếu chưa làm T2/T3: bù RÚT GỌN — tự gõ lại `cosine_similarity` + `rrf_fuse` KHÔNG AI, bỏ phần còn lại.* · **min:** tự gõ 1 hàm + 1 bài Easy
- [ ] **T5 3/7** — list vs dict vs set + Big-O tra cứu + mutability (copy vs reference) + Easy: Contains Duplicate. · **min:** nói TO mutability + 1 bài
- [ ] **T6 4/7** — OOP cơ bản: gói một mẩu `mini_rag` thành `class Index` + try/except. · **min:** skeleton class Index chạy được
- [ ] **T7 5/7** — 🎯 **Mock Python-check** (5 câu tự ra tự chấm: viết hàm từ spec · Big-O · sửa bug · dict+loop · đọc-hiểu) + **blank-page test đầu tiên** (vẽ bảng "bài toán → DSA" từ trí nhớ). · **min:** mock check
- [ ] **CN 6/7** — Teach-back: giải thích TO code tuần này như đang phỏng vấn → nghỉ.

---

## 7–13/7 — DSA khởi động (Arrays & Hashing + Two Pointers) · docs LangGraph vào

> Ban ngày: W3 agent (7–8/7) → W4 auditor (từ 9/7). Nguồn DSA: NeetCode 150 — tự nghĩ 15–20' → xem giải → hiểu pattern → đóng lại tự code.

- [ ] **T2 7/7** — DSA 2 bài Arrays & Hashing (hashmap đã quen từ `rrf_fuse`). · **min:** 1 bài
- [ ] **T3 8/7** — Math #1: đại số tuyến tính — vector, dot product, norm, cosine (móc: Ngày 3 đã tự viết). "Embedding là điểm trong không gian." · **min:** 20' nói TO lại công thức cosine + vì sao chia norm
- [ ] **T4 9/7** — DSA 2 bài. · **min:** 1 bài
- [ ] **T5 10/7** — 📘 Docs LangGraph #1: StateGraph, node/edge (map: StateGraph ↔ vòng `for`+`messages` trong agent.py mình viết). · **min:** quickstart 30'
- [ ] **T6 11/7** — DSA 2 bài (bắt đầu Two Pointers). · **min:** 1 bài
- [ ] **T7 12/7** — Blank-page test + 📘 Docs LangGraph #2: checkpointing (↔ log jsonl của mình). · **min:** blank-page
- [ ] **CN 13/7** — Teach-back + nghỉ.

---

## 14–20/7 — DSA tuần 2 (Sliding Window + Stack + Binary Search) · docs MCP vào

> Ban ngày: W4 kết (14–15/7) → W5 LangGraph build (từ 16/7). Docs tối tuần trước + tuần này = nạp đủ trước khi build.

- [ ] **T2 14/7** — DSA 2 bài Sliding Window. · **min:** 1 bài
- [ ] **T3 15/7** — 📘 Docs LangGraph #3: conditional edges + human-in-the-loop (mai build Ngày 29!). · **min:** 30' đọc + note 3 khái niệm
- [ ] **T4 16/7** — DSA 2 bài Stack (móc: call stack ↔ agent loop, mục 8 file DSA). · **min:** 1 bài
- [ ] **T5 17/7** — 📘 Docs MCP #1: concepts + FastMCP quickstart (chuẩn bị Ngày 32–33). · **min:** quickstart 30'
- [ ] **T6 18/7** — DSA 2 bài Binary Search ("1 triệu = 20 bước"). · **min:** 1 bài
- [ ] **T7 19/7** — Blank-page test + Math #2: xác suất cơ bản — phân phối, kỳ vọng, precision/recall (mình ĐÃ dùng — giờ gọi đúng tên). · **min:** blank-page
- [ ] **CN 20/7** — Teach-back + nghỉ.

---

## 21–27/7 — DSA tuần 3 (Linked List + Trees + Recursion) · AWS quay lại

> Ban ngày: W5 kết (21–22/7) → W6 deploy (từ 23/7). 💡 Trees tuần này CỰC hợp thời điểm: Ngày 26 vừa build tầng L0 auditor bằng `ast` — cây mình tự tay đi (mục 6 file DSA, mỏ neo AST).

- [ ] **T2 21/7** — DSA 2 bài Linked List. · **min:** 1 bài
- [ ] **T3 22/7** — ☁️ AWS #1: IAM + S3 cơ bản (30') + math ôn nhanh. · **min:** 30' AWS
- [ ] **T4 23/7** — DSA 2 bài Trees/DFS (móc thẳng vào `ast.walk` vừa viết). · **min:** 1 bài
- [ ] **T5 24/7** — ☁️ AWS #2: Bedrock Getting Started — map auditor của mình sang Bedrock AgentCore (story "build tay → hiểu managed service"). · **min:** 30'
- [ ] **T6 25/7** — DSA 2 bài Recursion/BFS. · **min:** 1 bài
- [ ] **T7 26/7** — Blank-page test + ☁️ AWS #3: Lambda + API Gateway (mức ý niệm — so với Docker/Railway mình vừa deploy). · **min:** blank-page
- [ ] **CN 27/7** — Teach-back + nghỉ.

---

## 28/7–3/8 — Giảm tải DSA, tăng luyện NÓI (ban ngày = W7 CV + phỏng vấn)

- [ ] **T2 28/7** — DSA 2 bài mixed (ôn 3 pattern cũ, không học pattern mới). · **min:** 1 bài
- [ ] **T3 29/7** — ☁️ AWS #4: review tổng — map toàn dự án sang AWS, chuẩn bị câu phỏng vấn cloud. · **min:** 30'
- [ ] **T4 30/7** — DSA 1 bài + 30' luyện nói đáp án mẫu (che đáp án, nói TO). · **min:** luyện nói
- [ ] **T5 31/7** — Math #3: A/B test, p-value mức ý niệm (phỏng vấn AI hay hỏi "sao biết cải thiện không phải may mắn"). · **min:** 30'
- [ ] **T6 1/8** — DSA 1 bài + luyện nói. · **min:** luyện nói
- [ ] **T7 2/8** — 🎯 Blank-page TỔNG (Python + DSA + AWS + 6 con số neo). · **min:** làm đủ
- [ ] **CN 3/8** — Teach-back tổng + nghỉ.

---

## 4–13/8 — Chế độ duy trì (ban ngày = W8 buffer + mock interview + NỘP CV)

- **T2/T4/T6:** DSA 1 bài/tối (giữ nhịp, không pattern mới).
- **T3/T5:** mock interview MIỆNG — ngân hàng 14 câu trong lo-trinh + 5 câu DSA cuối file [dsa-cho-ky-su-ai.md](dsa-cho-ky-su-ai.md).
- **T7:** blank-page. **CN:** nghỉ.
- [ ] **13/8 — 🎯 NỘP CV.**

---

## SAU 13/8 (tháng 9 — track dài, đừng kéo lên trước)

- DSA nâng cao: **Graphs + DP** (giờ Graph có móc thật: call graph cho auditor v2 — beyond-rag-phase-2).
- AWS sâu hơn nếu JD công ty nhắm tới yêu cầu.
- Memory module + Demo #2 (đã hoãn sẵn trong roadmap).
- Quyết định hướng freelance/agency (đã hẹn từ 2/7).
