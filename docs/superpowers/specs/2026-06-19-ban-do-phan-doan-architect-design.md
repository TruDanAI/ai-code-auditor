# Thiết kế: Bản Đồ Phán Đoán Architect (Companion Doc) — Design Spec

> **Ngày:** 2026-06-19 · **Loại:** Tài liệu học companion (living document) · **Repo:** `ai-code-auditor`
> **Trạng thái:** Chờ user review trước khi viết implementation plan.

---

## 1. Bối cảnh & Vấn đề

Student (sinh viên AI năm 3, đang xây AI Code Auditor để làm CV) tự nhận là **"hay vibe coding"** — sinh code bằng AI nhưng chưa **kiểm soát / kiểm duyệt được đầu ra**, chưa bao quát được toàn mảng để biết **khi nào nên dùng gì**.

Yêu cầu gốc có hai hướng (đã được làm rõ qua brainstorming):
- *(A — tham vọng)* "đầy đủ nội dung về ngành, giải quyết được tất cả giải pháp doanh nghiệp" → bao phủ kiểu bách khoa, gần như vô hạn.
- *(B — nhu cầu thật)* "hiểu tường tận, kiểm soát đầu ra, biết khi nào nên dùng hay không" → **tầng phán đoán/điều khiển**.

**Quyết định khoá phạm vi:** mục tiêu là **(B) — Tầng phán đoán của một Architect**: bao phủ rộng để biết-khi-nào-dùng-gì và **bắt được khi AI sinh code sai/thừa/rủi ro**, KHÔNG học sâu để tự implement lại mọi thứ. (A) là aspiration, không phải nội dung tài liệu.

**Ràng buộc cứng:** KHÔNG được làm loãng hoặc giảm hiệu suất roadmap chính (`lo-trinh-chi-tiet.md`). Roadmap đã rất chặt (5h/ngày, có mục "Điểm Cắt Nếu Trễ"). Tầng kiến thức này đi **song song**, không thay thế dự án.

---

## 2. Mục tiêu (Goals) & Phi mục tiêu (Non-Goals)

**Goals:**
1. Một companion doc duy nhất làm **bản đồ phán đoán toàn mảng** RAG/Agent/LLM-app + vỏ bọc production.
2. Mỗi chủ đề có khối **🚩 "AI/vibe coding hay sai gì"** + **🔍 "câu tự soi khi review code AI"** → trị bệnh vibe coding.
3. Tích hợp **hybrid**: con trỏ ngắn từ mỗi tuần roadmap trỏ về companion doc.
4. Không lấn thời gian dự án: học ở slot song song ~30 phút/tối (luân phiên DSA/AWS).
5. Là **living document dài hạn** — nuôi tiếp sau CV theo từng dự án thật.

**Non-Goals:**
- KHÔNG dạy lý thuyết đã có trong `NOTES.md`/roadmap/`dsa-cho-ky-su-ai.md` (chỉ bổ sung góc phán đoán + trỏ link — nguyên tắc không lặp).
- KHÔNG bao phủ ML cổ điển, training/fine-tune sâu, MLOps nặng, data engineering (vượt nhu cầu fresher LLM-app).
- KHÔNG học tầng triển khai sâu (tự implement lại các giải pháp doanh nghiệp).
- KHÔNG sửa cấu trúc/dời ngày của roadmap; chỉ chèn con trỏ ngắn.

---

## 3. Cách tiếp cận đã chọn

**Cách 3 — Hybrid nội dung:** khung **theo chủ đề** (để con trỏ roadmap móc vào sạch) + bên trong mỗi chủ đề dùng cấu trúc điều-khiển (bảng quyết định + red-flags + khi-nào-KHÔNG-dùng).

Lý do chọn: khung chủ đề cho cảm giác "bao quát toàn mảng" (đáp ứng aspiration A), còn khối red-flags + quyết định bên trong là tầng kiểm soát thật (đáp ứng nhu cầu B). Đồng bộ pattern với `dsa-cho-ky-su-ai.md` và mục AWS của roadmap.

Hai cách bị loại:
- *Cách 1 (theo quyết định/problem-first):* mạnh ở "khi nào dùng gì" nhưng khó móc 1-1 vào tuần roadmap.
- *Cách 2 (theo chủ đề kiểu textbook):* đầy đủ nhưng thụ động, không trị vibe coding.

---

## 4. Cấu trúc tài liệu

**File:** `ai-code-auditor/docs/ban-do-phan-doan-architect.md` (cạnh `dsa-cho-ky-su-ai.md`).

### 4.1. Trục xương sống — Thang trưởng thành 5 cấp (L1→L5)

Đặt ở đầu doc, làm "kim tự tháp" để mọi chủ đề quy chiếu về:

| Cấp | Giải pháp | Khi nào đủ |
|---|---|---|
| L1 | 1 lần gọi LLM (prompt thuần) | Việc đơn giản, 1 bước |
| L2 | RAG pipeline (retrieval + prompt) | Cần kiến thức riêng, không suy luận nhiều bước |
| L3 | 1 agent (tool-calling, ReAct) | Cần tra cứu/hành động nhiều bước, 1 vai |
| L4 | Multi-agent (router + chuyên trách + reviewer) | Nhiều vai trò tách bạch, luồng phức tạp |
| **L5** | **Điều phối & kiểm duyệt fleet** | Biết chọn đúng L1–L4 cho từng bài + quản observability/cost/lỗi xuyên agent |

**Nguyên tắc đỉnh tháp (chống ngộ nhận):** kỹ năng architect cao nhất KHÔNG phải "điều khiển được nhiều agent" mà là **biết khi nào ĐỪNG dùng nhiều agent** — chọn giải pháp NHỎ nhất chạy được. Vibe coder hay "đẻ" agent vô tội vạ; senior thể hiện qua **sự kiềm chế (restraint)**. (Khớp với roadmap: "Điểm Cắt Nếu Trễ" cắt agent thứ 3 đầu tiên.)

### 4.2. Bản đồ chủ đề (3 phần)

**PHẦN A — LANE (phán đoán trong pipeline RAG/Agent):**
- A1. Input & Ingestion — router PDF/docx/excel/link/OCR *(trỏ về thảo luận đã có, không viết lại)*
- A2. Chunking — chiến lược cắt & đánh đổi
- A3. Embedding — chọn model nào, khi nào nâng cấp
- A4. Retrieval — vector / keyword / hybrid / rerank, chọn khi nào
- A5. Prompt assembly & Grounding — chống hallucination, citation
- A6. Model & Cost — chọn LLM, context window, caching
- A7. Agent design — khi nào DÙNG agent, ReAct vs workflow, multi-agent, memory

**PHẦN B — VỎ BỌC PRODUCTION:**
- B1. Evaluation & Observability — precision/recall, latency, cost, đo hallucination, golden set
- B2. Guardrails, Safety & Security — prompt injection, PII, secrets, *cái gì TUYỆT ĐỐI không gửi cho LLM*
- B3. Deployment & Infra — managed vs self-host, scaling, chọn vector DB
- B4. Build vs Buy & khi nào KHÔNG dùng AI

**PHẦN C — XUYÊN SUỐT:**
- C1. Khung phán đoán Architect — checklist lặp lại được để soi BẤT KỲ giải pháp AI nào
- C2. 🚩 Catalog tổng "AI hay làm sai gì" — gom mọi red-flag về một chỗ để tra nhanh
- C3. **Capstone — Điều phối & kiểm duyệt nhiều agent** — đỉnh L4/L5, tổng hợp A7 + B1 + C1

### 4.3. Template 6 khối cho mỗi chủ đề

| Khối | Nội dung | Phục vụ |
|---|---|---|
| 🎯 Quyết định cốt lõi | 1 câu: chủ đề trả lời câu "chọn gì giữa cái gì" | Khung "khi nào dùng gì" |
| ⚖️ Bảng lựa chọn | Option A/B/C → *chọn khi nào* → *đánh đổi* | Bao quát giải pháp |
| 🚩 AI/vibe coding hay sai | 2-4 lỗi cụ thể AI hay sinh ở chủ đề này | **Trị vibe coding — trục chính** |
| 🛑 Khi nào KHÔNG cần | Dấu hiệu over-engineer, YAGNI | Chống "vẽ rắn thêm chân" |
| 🔍 Câu tự soi khi review code AI | 1-2 câu hỏi tự đặt khi nhìn output AI | Biến mày thành người kiểm duyệt |
| 🔗 Đào sâu | Trỏ NOTES.md / roadmap / dsa-doc | Không lặp, giữ một nguồn |

---

## 5. Tích hợp roadmap (Hybrid — con trỏ mỗi tuần)

Mỗi tuần chèn 1 box ngắn "🧭 Góc Architect" (2-3 dòng) trỏ về companion doc. KHÔNG dời ngày, KHÔNG đụng nội dung học chính.

| Tuần roadmap | Trỏ tới | Tag |
|---|---|---|
| Tuần 1 (RAG tay) | A2 · A3 · A4 · A5 | 🟢 Học luôn |
| Tuần 2 (Vector DB + eval) | A4 Hybrid · B1 · B3 (chọn Vector DB) | 🟢 Học luôn |
| Tuần 3 (Agent) | A6 · A7 (L3) | 🟢 Học luôn |
| Tuần 5 (Multi-agent) | A7 · C3 (L4) | 🟢 Học luôn |
| Tuần 6 (Deploy) | B3 (🟢) · B2 · B4 (🔵 đọc-để-biết) | Hỗn hợp |
| Tuần 7-8 (CV/PV) | C1 · C2 (ôn) | 🟢 Học luôn |

---

## 6. Ngân sách thời gian & Tag dài hạn

- **Slot học:** ~30 phút/tối, **luân phiên với DSA/AWS** — KHÔNG đụng 5h dự án. Đúng mô hình mục "AWS Base Knowledge" của roadmap.
- **Ưu tiên cứng:** nếu phải chọn giữa companion doc và tiến độ dự án → **dự án thắng**. Đây là nền hiểu sâu, không phải deliverable CV.

**Tag từng chủ đề:**
- 🟢 **Học trong lộ trình** (map thẳng vào tuần đang code): A2, A3, A4, A5, A6, A7, B1, B3, C1, C2.
- 🔵 **Dài hạn** (đọc-để-biết giờ, đào sâu sau CV): A1 Ingestion (feature giai đoạn 2) · B2 Security tầng sâu · B4 Build-vs-buy tầng sâu · C3 phần L5 (governance fleet — Tuần 5 chỉ chạm L4).

→ C3 nằm cả hai: L4 (xây multi-agent) học ở Tuần 5; L5 (governance) tag 🔵 dài hạn.

---

## 7. Định hướng dài hạn

- **2 tháng tới:** student *chạm tay* L1→L4 thật (Tuần 1-2 = L1/L2, Tuần 3 = L3, Tuần 5 = L4). Companion doc ghi lại góc phán đoán từng cấp khi đi qua.
- **Sau CV:** doc lớn lên theo mỗi dự án thật → **tài sản nghề nghiệp cả đời**. Tầng phán đoán architect là kỹ năng bồi đắp nhiều năm.

---

## 8. Tiêu chí thành công

1. Companion doc tồn tại với đủ A1–A7, B1–B4, C1–C3 theo template 6 khối; mục 🟢 viết đầy đủ, mục 🔵 có khung + ghi rõ "đào sâu sau".
2. Mỗi chủ đề 🟢 có tối thiểu khối 🚩 và 🔍 viết cụ thể (không placeholder).
3. Con trỏ "🧭 Góc Architect" xuất hiện ở Tuần 1, 2, 3, 5, 6, 7-8 trong `lo-trinh-chi-tiet.md`, mỗi cái trỏ đúng chủ đề.
4. Nguyên tắc không-lặp: các chủ đề trùng NOTES.md (chunking/embedding/cosine) chỉ chứa góc phán đoán + link, không chép lại lý thuyết.
5. Roadmap không bị dời ngày / không tăng giờ học chính.

---

## 9. Rủi ro & Giảm thiểu

| Rủi ro | Giảm thiểu |
|---|---|
| Companion doc phình to, nuốt thời gian dự án | Mục 🔵 chỉ viết khung; ưu tiên cứng "dự án thắng"; slot 30 phút/tối cố định |
| Lặp nội dung với NOTES.md/dsa-doc → lệch nguồn | Nguyên tắc không-lặp + khối 🔗 trỏ về một nguồn |
| Student over-engineer (đẻ agent vô tội vạ) | Trục thang L1-L5 + nguyên tắc "restraint" + khối 🛑 mỗi chủ đề |
| Con trỏ roadmap làm rối tài liệu chính | Box ngắn 2-3 dòng, không đụng nội dung học chính |
```
