# Bản Đồ Phán Đoán Architect — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Tạo companion doc `ban-do-phan-doan-architect.md` (tầng phán đoán architect trị vibe coding) và chèn con trỏ "🧭 Góc Architect" vào `lo-trinh-chi-tiet.md`.

**Architecture:** Một file markdown companion, tổ chức theo chủ đề (Phần A lane / B production / C xuyên suốt), mỗi chủ đề theo template 6 khối, xương sống là thang trưởng thành L1→L5. Hybrid: con trỏ ngắn từ mỗi tuần roadmap trỏ về companion doc. Không phải code — deliverable là tài liệu; "test" = kiểm tra cấu trúc bằng `rg` (ripgrep).

**Tech Stack:** Markdown thuần. Verify bằng `rg` (ripgrep, có sẵn). Không có dependency code.

## Global Constraints

- **Ngôn ngữ:** Tiếng Việt, xưng "mày/mình" đồng bộ giọng `dsa-cho-ky-su-ai.md` và NOTES.md.
- **Nguyên tắc KHÔNG LẶP:** chủ đề trùng NOTES.md/roadmap/dsa-doc (chunking, embedding, cosine) chỉ viết góc phán đoán + khối 🔗 trỏ link; KHÔNG chép lại lý thuyết.
- **Template 6 khối CỐ ĐỊNH mỗi chủ đề:** `🎯 Quyết định cốt lõi` · `⚖️ Bảng lựa chọn` · `🚩 AI/vibe coding hay sai` · `🛑 Khi nào KHÔNG cần` · `🔍 Câu tự soi khi review code AI` · `🔗 Đào sâu`.
- **Tag mỗi chủ đề:** 🟢 [Học trong lộ trình] viết đầy đủ · 🔵 [Dài hạn] chỉ viết khung + ghi rõ "đào sâu sau CV".
- **KHÔNG dời ngày / KHÔNG tăng giờ học chính của roadmap.** Con trỏ chỉ là box 2-3 dòng.
- **File companion:** `ai-code-auditor/docs/ban-do-phan-doan-architect.md`. **File roadmap sửa:** `ai-code-auditor/docs/lo-trinh-chi-tiet.md`.
- **Commit:** chỉ commit khi user yêu cầu (quy ước project, override "frequent commits" của skill). Mỗi task có bước commit nhưng executor PHẢI hỏi user trước khi chạy.
- **Không placeholder** trong mục 🟢: mọi khối phải có nội dung thật.

---

## File Structure

| File | Trách nhiệm | Hành động |
|---|---|---|
| `docs/ban-do-phan-doan-architect.md` | Companion doc — toàn bộ bản đồ phán đoán | Create (Task 1-5) |
| `docs/lo-trinh-chi-tiet.md` | Roadmap — nhận con trỏ "🧭 Góc Architect" | Modify (Task 6) |

Thứ tự task: 1 (scaffold + L1-L5 + template) → 2 (A1-A4) → 3 (A5-A7) → 4 (B1-B4) → 5 (C1-C3) → 6 (con trỏ roadmap).

---

## Task 1: Scaffold companion doc — header, thang L1-L5, giải thích template

**Files:**
- Create: `ai-code-auditor/docs/ban-do-phan-doan-architect.md`

**Interfaces:**
- Produces: file companion với các heading mỏ neo mà Task 2-5 sẽ ghi nội dung vào: `## PHẦN A`, `## PHẦN B`, `## PHẦN C` (rỗng, chờ điền); và section `## THANG TRƯỞNG THÀNH (L1→L5)`, `## TEMPLATE MỖI CHỦ ĐỀ`.

- [ ] **Step 1: Tạo file với header + intro + cách dùng**

Viết phần đầu file:

```markdown
# BẢN ĐỒ PHÁN ĐOÁN ARCHITECT — Khi nào dùng gì & Bắt lỗi AI sinh code

> **Tài liệu này là gì:** Một bản đồ giúp mày — người hay vibe coding — chuyển từ *nhận* code AI sang *kiểm duyệt* code AI. Không dạy implement sâu; dạy **phán đoán**: khi nào dùng gì, khi nào ĐỪNG, và AI hay sai chỗ nào.
>
> **Cách dùng:** Khi roadmap dẫn tới một chủ đề (qua box 🧭 Góc Architect), mở đúng mục ở đây. Đọc khối 🚩 và 🔍 trước — đó là phần trị vibe coding. Lý thuyết sâu nằm ở NOTES.md/roadmap/dsa-cho-ky-su-ai.md (khối 🔗 trỏ tới), tài liệu này KHÔNG lặp lại.
>
> **Là living document:** mục 🟢 học trong 2 tháng roadmap; mục 🔵 đọc-để-biết giờ, đào sâu sau CV theo dự án thật.
```

- [ ] **Step 2: Thêm section thang trưởng thành L1-L5**

```markdown
## THANG TRƯỞNG THÀNH (L1→L5) — Xương sống

Mọi quyết định kiến trúc quy về: "bài này cần cấp mấy?"

| Cấp | Giải pháp | Khi nào ĐỦ |
|---|---|---|
| L1 | 1 lần gọi LLM (prompt thuần) | Việc đơn giản, 1 bước |
| L2 | RAG pipeline (retrieval + prompt) | Cần kiến thức riêng, không suy luận nhiều bước |
| L3 | 1 agent (tool-calling, ReAct) | Cần tra cứu/hành động nhiều bước, 1 vai |
| L4 | Multi-agent (router + chuyên trách + reviewer) | Nhiều vai trò tách bạch, luồng phức tạp |
| **L5** | **Điều phối & kiểm duyệt fleet** | Chọn đúng L1-L4 cho từng bài + quản observability/cost/lỗi xuyên agent |

> **🔑 Nguyên tắc đỉnh tháp:** Kỹ năng architect cao nhất KHÔNG phải "điều khiển được nhiều agent" mà là **biết khi nào ĐỪNG dùng nhiều agent**. Chọn giải pháp NHỎ nhất chạy được. Vibe coder hay "đẻ" agent vô tội vạ → chậm, đắt, khó debug. Senior thể hiện qua **sự kiềm chế**.
```

- [ ] **Step 3: Thêm section giải thích template 6 khối**

```markdown
## TEMPLATE MỖI CHỦ ĐỀ (6 khối cố định)

- **🎯 Quyết định cốt lõi** — chủ đề này trả lời câu "chọn gì giữa cái gì".
- **⚖️ Bảng lựa chọn** — option → chọn khi nào → đánh đổi.
- **🚩 AI/vibe coding hay sai** — lỗi cụ thể AI hay sinh ở đây.
- **🛑 Khi nào KHÔNG cần** — dấu hiệu over-engineer.
- **🔍 Câu tự soi khi review code AI** — câu hỏi tự đặt khi nhìn output AI.
- **🔗 Đào sâu** — trỏ về nguồn lý thuyết (không lặp).

Tag: 🟢 [Học trong lộ trình] · 🔵 [Dài hạn — đào sâu sau CV]
```

- [ ] **Step 4: Thêm 3 heading mỏ neo rỗng cho Task 2-5**

```markdown
---

## PHẦN A — LANE (phán đoán trong pipeline RAG/Agent)

---

## PHẦN B — VỎ BỌC PRODUCTION

---

## PHẦN C — XUYÊN SUỐT
```

- [ ] **Step 5: Verify cấu trúc**

Run: `rg -n "^## (THANG TRƯỞNG THÀNH|TEMPLATE MỖI CHỦ ĐỀ|PHẦN A|PHẦN B|PHẦN C)" ai-code-auditor/docs/ban-do-phan-doan-architect.md`
Expected: 5 dòng khớp (5 heading).

- [ ] **Step 6: Commit (HỎI user trước)**

```bash
git add ai-code-auditor/docs/ban-do-phan-doan-architect.md
git commit -m "docs: scaffold architect judgment map (ladder L1-L5 + template)"
```

---

## Task 2: Phần A lane — A1 Ingestion, A2 Chunking, A3 Embedding, A4 Retrieval

**Files:**
- Modify: `ai-code-auditor/docs/ban-do-phan-doan-architect.md` (điền dưới `## PHẦN A`)

**Interfaces:**
- Consumes: heading `## PHẦN A` từ Task 1.
- Produces: 4 mục `### A1`…`### A4` theo template 6 khối.

- [ ] **Step 1: Viết A1 — Input & Ingestion (🔵 Dài hạn — khung)**

```markdown
### A1. Input & Ingestion — Router định dạng đầu vào 🔵 [Dài hạn]

- **🎯 Quyết định cốt lõi:** input thật (PDF/docx/excel/link/ảnh) đi parser nào, khi nào cần OCR.
- **⚖️ Bảng lựa chọn:** PDF text → pymupdf · PDF scan/ảnh → OCR (PaddleOCR/Tesseract) · docx → python-docx · xlsx → pandas (KHÔNG embed thẳng) · link → trafilatura.
- **🚩 AI/vibe coding hay sai:** AI mặc định OCR mọi PDF (chậm 50×, bẩn text born-digital); AI embed thẳng bảng Excel (vô nghĩa, như #1234≈#5678).
- **🛑 Khi nào KHÔNG cần:** input đã là text thuần (repo code) → bỏ qua cả tầng này.
- **🔍 Câu tự soi:** "File này born-digital hay scan — AI có check trước khi OCR không?"
- **🔗 Đào sâu sau CV:** chi tiết per-page threshold đã bàn trong hội thoại ingestion + sẽ là feature giai đoạn 2 của AI Code Auditor.
```

- [ ] **Step 2: Viết A2 — Chunking (🟢)**

```markdown
### A2. Chunking — Cắt mà không phá ngữ cảnh 🟢

- **🎯 Quyết định cốt lõi:** cắt theo gì (ký tự cố định / ranh giới có nghĩa / có overlap) và kích thước bao nhiêu.
- **⚖️ Bảng lựa chọn:** Theo ranh giới có nghĩa (heading .md, hàm .js) — *chọn khi* cấu trúc rõ, chất lượng cao nhất · Ký tự cố định — *chọn khi* text phi cấu trúc, đơn giản · + Overlap 50-100 ký tự — *chọn khi* sợ cắt mất ngữ cảnh ranh giới.
- **🚩 AI/vibe coding hay sai:** AI chọn chunk cố định 500 ký tự cho MỌI loại → cắt giữa hàm, mất nghĩa; AI quên fallback cắt chunk khổng lồ → 1 chunk nuốt cả file, hỏng embedding; AI set chunk size tùy hứng không gắn với context budget.
- **🛑 Khi nào KHÔNG cần:** tài liệu nhỏ fit context → stuffing, khỏi chunk.
- **🔍 Câu tự soi:** "Có chunk nào bị cắt GIỮA một đơn vị logic (hàm/đoạn) không?"; "Có bước fallback cho chunk quá dài chưa?"
- **🔗 Đào sâu:** NOTES.md Ngày 4 + roadmap Tuần 2 (compare_chunking đo precision@3 cho 3 chiến lược).
```

- [ ] **Step 3: Viết A3 — Embedding (🟢)**

```markdown
### A3. Embedding — Chọn model biểu diễn nghĩa 🟢

- **🎯 Quyết định cốt lõi:** dùng embedding model nào, khi nào nâng cấp, có hợp đa ngôn ngữ không.
- **⚖️ Bảng lựa chọn:** all-MiniLM-L6-v2 (80MB, CPU) — *chọn khi* học/prototype, tiếng Anh · BGE-M3 (~2GB) — *chọn khi* cần đa ngôn ngữ ổn · Qwen3-Embedding — *chọn khi* tiếng Việt + cần SOTA, có GPU.
- **🚩 AI/vibe coding hay sai:** AI bê model tiếng Anh (MiniLM) cho bài tiếng Việt → cross-lingual yếu (VI-EN ~0.27 cosine); AI đổi model nhưng quên đo lại precision → "cảm giác tốt hơn" không số liệu; AI không normalize vector trước khi so.
- **🛑 Khi nào KHÔNG cần:** cần khớp chính xác (mã đơn, tên hàm) → keyword/DB, không embedding.
- **🔍 Câu tự soi:** "Bài này có tiếng Việt không — model AI chọn có cross-lingual nổi không?"; "Đổi model rồi có đo precision@3 lại chưa?"
- **🔗 Đào sâu:** NOTES.md Ngày 2-3 (số đo MiniLM VI-EN) + roadmap Tuần 2 Ngày 10 (bảng so MiniLM/BGE-M3/Qwen3).
```

- [ ] **Step 4: Viết A4 — Retrieval (🟢)**

```markdown
### A4. Retrieval — Vector / Keyword / Hybrid / Rerank 🟢

- **🎯 Quyết định cốt lõi:** tìm bằng vector, keyword, hay cả hai; có cần rerank không; top_k bao nhiêu.
- **⚖️ Bảng lựa chọn:** Vector (semantic) — *chọn khi* hỏi theo ý, khác chữ cùng nghĩa · Keyword/BM25 — *chọn khi* exact-match (ID, tên hàm) · Hybrid — *chọn khi* sản phẩm thật (gộp cả hai) · + Rerank — *chọn khi* precision quan trọng, chịu thêm latency.
- **🚩 AI/vibe coding hay sai:** AI mặc định pure vector cho mọi thứ → chết với exact-match (mã đơn, tên hàm); AI trả thẳng top-k cosine, quên rerank → precision thấp không rõ lý do; AI set top_k tùy hứng (3? 10?) không gắn context budget.
- **🛑 Khi nào KHÔNG cần:** vài trăm chunk → brute-force O(n) đủ, đừng vác vector DB/ANN sớm.
- **🔍 Câu tự soi:** "Câu exact-match (số/ID/tên hàm) có lọt vào nhánh vector không — nếu có là sai."; "top_k này dựa trên cái gì, hay AI bịa số?"
- **🔗 Đào sâu:** dsa-cho-ky-su-ai.md mục 3 (top-k/heap) & mục 7 (HNSW) + NOTES.md Ngày 2 (hybrid).
```

- [ ] **Step 5: Verify 4 mục tồn tại + không placeholder**

Run: `rg -n "^### A[1-4]\." ai-code-auditor/docs/ban-do-phan-doan-architect.md` → Expected: 4 dòng.
Run: `rg -ni "TODO|TBD|fill in|ghi chép của bạn" ai-code-auditor/docs/ban-do-phan-doan-architect.md` → Expected: không kết quả.

- [ ] **Step 6: Commit (HỎI user trước)**

```bash
git add ai-code-auditor/docs/ban-do-phan-doan-architect.md
git commit -m "docs: add Part A lane topics A1-A4 (ingestion, chunking, embedding, retrieval)"
```

---

## Task 3: Phần A lane — A5 Grounding, A6 Model & Cost, A7 Agent design

**Files:**
- Modify: `ai-code-auditor/docs/ban-do-phan-doan-architect.md` (tiếp dưới A4)

**Interfaces:**
- Consumes: heading `## PHẦN A` + A1-A4 từ Task 2.
- Produces: `### A5`, `### A6`, `### A7`. A7 giới thiệu khái niệm L3/L4 mà C3 (Task 5) sẽ dựa vào.

- [ ] **Step 1: Viết A5 — Prompt assembly & Grounding (🟢)**

```markdown
### A5. Prompt assembly & Grounding — Chống bịa 🟢

- **🎯 Quyết định cốt lõi:** ghép context vào prompt thế nào để model KHÔNG bịa, có trích dẫn.
- **⚖️ Bảng lựa chọn:** Ràng buộc "chỉ dùng context, thiếu thì nói không biết" — *luôn dùng* · Kèm file/chunk_id mỗi đoạn — *chọn khi* cần citation/debug · Few-shot ví dụ định dạng — *chọn khi* cần output cấu trúc cố định.
- **🚩 AI/vibe coding hay sai:** AI viết prompt không có rào "không bịa" → model tự tin bịa code không có thật; AI nhồi quá nhiều chunk → "lost in the middle", model bỏ sót; AI quên gắn nguồn → không truy vết được câu trả lời.
- **🛑 Khi nào KHÔNG cần:** câu hỏi kiến thức tổng quát có sẵn trong model → không cần grounding.
- **🔍 Câu tự soi:** "Prompt có câu 'nếu context không có thì trả lời không tìm thấy' không?"; "Nếu retrieval lấy chunk rác, prompt này có chặn được bịa không?"
- **🔗 Đào sâu:** roadmap Ngày 5 (build_prompt) + Ngày 6 (stress-test hallucination).
```

- [ ] **Step 2: Viết A6 — Model & Cost (🟢)**

```markdown
### A6. Model & Cost — Chọn LLM nào, khi nào 🟢

- **🎯 Quyết định cốt lõi:** dùng model nào cho việc nào, cân giữa chất lượng/giá/tốc độ.
- **⚖️ Bảng lựa chọn:** Flash mới nhất (đắt, mạnh) — *chọn khi* việc khó, gọi ít · Flash đời cũ/lite (rẻ) — *chọn khi* vòng lặp agent gọi nhiều lần · Prompt caching — *chọn khi* prompt lặp phần lớn (system prompt dài).
- **🚩 AI/vibe coding hay sai:** AI để model đắt nhất chạy vòng agent nhiều bước → hóa đơn nổ; AI quên context window có giới hạn + tốn tiền theo token; AI không cache phần prompt lặp.
- **🛑 Khi nào KHÔNG cần:** prototype học → 1 model là đủ, đừng tối ưu chi phí sớm.
- **🔍 Câu tự soi:** "Vòng agent này gọi LLM mấy lần/câu — model AI chọn có hợp chi phí không?"; "Tiếng Việt tốn ~2× token, đã tính vào chi phí chưa?"
- **🔗 Đào sâu:** roadmap mục cập nhật chi phí (gemini-3.5-flash đắt nhất họ Flash) + ban-do-cong-nghe-chi-phi.md.
```

- [ ] **Step 3: Viết A7 — Agent design (🟢)**

```markdown
### A7. Agent design — Khi nào DÙNG agent 🟢

- **🎯 Quyết định cốt lõi:** bài này cần agent (L3) không, hay pipeline (L2) đủ; ReAct vs workflow cố định; 1 agent hay nhiều.
- **⚖️ Bảng lựa chọn:** Pipeline cố định (L2) — *chọn khi* luồng biết trước, không rẽ nhánh · 1 agent ReAct (L3) — *chọn khi* cần chọn tool động, nhiều bước · Workflow có cấu trúc (LangGraph) — *chọn khi* cần state/retry/rẽ nhánh kiểm soát được.
- **🚩 AI/vibe coding hay sai:** AI bọc mọi thứ thành "agent" dù pipeline thẳng là đủ → chậm, khó debug; AI để agent loop không giới hạn bước → cháy token/treo; AI cho agent tool nguy hiểm (xóa file, chạy shell) không sandbox.
- **🛑 Khi nào KHÔNG cần:** luồng 1 bước hoặc biết trước → KHÔNG agent. Đây là cạm bẫy over-engineer phổ biến nhất.
- **🔍 Câu tự soi:** "Bài này có thật sự cần agent quyết định động, hay AI đang vẽ agent cho oai?"; "Có max_steps chặn vòng lặp chưa?"
- **🔗 Đào sâu:** roadmap Tuần 3 (agent.py ReAct) + Tuần 5 (LangGraph) + dsa-cho-ky-su-ai.md mục 8 (stack/queue).
```

- [ ] **Step 4: Verify**

Run: `rg -n "^### A[5-7]\." ai-code-auditor/docs/ban-do-phan-doan-architect.md` → Expected: 3 dòng.
Run: `rg -ni "TODO|TBD|fill in" ai-code-auditor/docs/ban-do-phan-doan-architect.md` → Expected: không kết quả.

- [ ] **Step 5: Commit (HỎI user trước)**

```bash
git add ai-code-auditor/docs/ban-do-phan-doan-architect.md
git commit -m "docs: add Part A lane topics A5-A7 (grounding, model/cost, agent design)"
```

---

## Task 4: Phần B production wrapper — B1 Eval, B2 Security, B3 Deploy, B4 Build-vs-Buy

**Files:**
- Modify: `ai-code-auditor/docs/ban-do-phan-doan-architect.md` (điền dưới `## PHẦN B`)

**Interfaces:**
- Consumes: heading `## PHẦN B` từ Task 1.
- Produces: `### B1`…`### B4`. B1 (observability) là tiền đề cho C3 (Task 5).

- [ ] **Step 1: Viết B1 — Evaluation & Observability (🟢)**

```markdown
### B1. Evaluation & Observability — Đo thay vì đoán 🟢

- **🎯 Quyết định cốt lõi:** đo chất lượng RAG/agent bằng metric nào (precision@k, latency, cost, hallucination rate) và log gì.
- **⚖️ Bảng lựa chọn:** Golden set + precision@k — *chọn khi* đo chất lượng retrieval · Log token/latency/tool mỗi call — *chọn khi* cần biết chi phí/điểm nghẽn · Test off-topic — *chọn khi* kiểm rào chống bịa.
- **🚩 AI/vibe coding hay sai:** AI khoe "cải thiện" không có số liệu (golden set); AI quên log token/latency → không biết chi phí thật; AI không test câu off-topic → rào chống bịa chưa được kiểm.
- **🛑 Khi nào KHÔNG cần:** demo 1 lần dùng rồi bỏ → khỏi dựng eval harness.
- **🔍 Câu tự soi:** "Thay đổi này có số đo trước/sau không, hay chỉ 'cảm giác tốt hơn'?"; "1 query tốn bao nhiêu token/tiền — có log không?"
- **🔗 Đào sâu:** roadmap Tuần 2 Ngày 9 (precision@3 + golden set) + Tuần 3 (agent_log.jsonl).
```

- [ ] **Step 2: Viết B2 — Guardrails, Safety & Security (🔵 Dài hạn — khung)**

```markdown
### B2. Guardrails, Safety & Security 🔵 [Dài hạn]

- **🎯 Quyết định cốt lõi:** chặn prompt injection, lọc PII, và cái gì TUYỆT ĐỐI không gửi cho LLM.
- **⚖️ Bảng lựa chọn:** Validate output (schema/regex) · Lọc PII/secret trước khi gửi · System prompt chống injection · Allowlist tool cho agent.
- **🚩 AI/vibe coding hay sai:** AI nhét nguyên secret/API key vào prompt; AI tin tưởng input người dùng → injection "bỏ qua lệnh trên"; AI cho agent quyền chạy shell không sandbox.
- **🛑 Khi nào KHÔNG cần:** prototype nội bộ, dữ liệu không nhạy cảm → guardrail tối thiểu.
- **🔍 Câu tự soi:** "Prompt này có chứa secret/PII không nên rời máy không?"; "Input người dùng có thể ghi đè system prompt không?"
- **🔗 Đào sâu sau CV:** OWASP LLM Top 10; gắn với audit thật chatbot-fanpage (Tuần 6 — tìm hardcode secret).
```

- [ ] **Step 3: Viết B3 — Deployment & Infra (🟢, phần chọn vector DB)**

```markdown
### B3. Deployment & Infra — Managed vs Self-host 🟢

- **🎯 Quyết định cốt lõi:** chạy ở đâu (Railway/VPS/serverless/AWS), vector DB nào, khi nào managed.
- **⚖️ Bảng lựa chọn:** Railway/Render — *chọn khi* SME, budget thấp, đơn giản · VPS+Docker — *chọn khi* cần kiểm soát, rẻ · AWS/Azure — *chọn khi* enterprise/JD yêu cầu · Vector DB: Chroma (local/nhỏ) vs pgvector (đã có Postgres) vs Pinecone (managed, scale).
- **🚩 AI/vibe coding hay sai:** AI mặc định kéo AWS/Kubernetes cho project nhỏ → phức tạp thừa, đắt; AI chọn vector DB nặng khi vài trăm chunk (brute-force đủ); AI quên chunk in-memory mất khi restart.
- **🛑 Khi nào KHÔNG cần:** project học/SME nhỏ → KHÔNG cần AWS; Railway/VPS là đủ.
- **🔍 Câu tự soi:** "Quy mô này có thật sự cần infra AI vẽ ra, hay nhỏ hơn là đủ?"; "Dữ liệu có persist qua restart không?"
- **🔗 Đào sâu:** roadmap Tuần 6 (Docker/Railway) + ban-do-cong-nghe-chi-phi.md (bảng AWS vs alternatives) + CLAUDE.md (chunk in-memory mất khi restart).
```

- [ ] **Step 4: Viết B4 — Build vs Buy & khi nào KHÔNG dùng AI (🔵 Dài hạn — khung)**

```markdown
### B4. Build vs Buy & Khi nào KHÔNG dùng AI 🔵 [Dài hạn]

- **🎯 Quyết định cốt lõi:** tự build, dùng managed service, hay KHÔNG dùng AI/LLM cho bài này.
- **⚖️ Bảng lựa chọn:** Build tay — *chọn khi* cần hiểu/kiểm soát, lõi sản phẩm · Managed (Bedrock/OpenAI Assistants) — *chọn khi* cần nhanh, không phải lõi · KHÔNG dùng LLM — *chọn khi* việc xác định được bằng rule/SQL/regex.
- **🚩 AI/vibe coding hay sai:** AI nhét LLM vào việc mà if-else/SQL giải xong (đắt + bất định); AI build lại thứ managed service làm tốt hơn; AI dùng LLM cho phép tính số học chính xác.
- **🛑 Khi nào KHÔNG cần AI:** bài có lời giải xác định (tính toán, tra cứu chính xác, rule rõ) → đừng dùng LLM.
- **🔍 Câu tự soi:** "Việc này có cần LLM không, hay một hàm thường giải được rẻ và chắc hơn?"
- **🔗 Đào sâu sau CV:** ban-do-cong-nghe-chi-phi.md + bảng "Bài Toán Nào Dùng Gì" của roadmap.
```

- [ ] **Step 5: Verify**

Run: `rg -n "^### B[1-4]\." ai-code-auditor/docs/ban-do-phan-doan-architect.md` → Expected: 4 dòng.
Run: `rg -ni "TODO|TBD|fill in" ai-code-auditor/docs/ban-do-phan-doan-architect.md` → Expected: không kết quả.

- [ ] **Step 6: Commit (HỎI user trước)**

```bash
git add ai-code-auditor/docs/ban-do-phan-doan-architect.md
git commit -m "docs: add Part B production wrapper B1-B4 (eval, security, deploy, build-vs-buy)"
```

---

## Task 5: Phần C xuyên suốt — C1 Khung phán đoán, C2 Catalog red-flags, C3 Capstone điều phối

**Files:**
- Modify: `ai-code-auditor/docs/ban-do-phan-doan-architect.md` (điền dưới `## PHẦN C`)

**Interfaces:**
- Consumes: heading `## PHẦN C` từ Task 1; tham chiếu A7 (Task 3), B1 (Task 4), thang L1-L5 (Task 1).
- Produces: `### C1`, `### C2`, `### C3`.

- [ ] **Step 1: Viết C1 — Khung phán đoán Architect (🟢)**

```markdown
### C1. Khung phán đoán Architect — Checklist soi mọi giải pháp AI 🟢

Khi AI (hoặc mày) đưa ra một giải pháp, chạy qua 6 câu này TRƯỚC khi chấp nhận:

1. **Cấp nào?** Bài này cần L1-L5 mấy? Có đang dùng cấp cao hơn mức cần không?
2. **Exact hay semantic?** Có phần exact-match nào đang bị nhét vào embedding không?
3. **Đo bằng gì?** Có metric/số liệu chứng minh nó tốt, hay chỉ "cảm giác"?
4. **Chi phí?** 1 request tốn bao nhiêu token/tiền/latency? Có log không?
5. **Hỏng thì sao?** Có rào chống bịa, max_steps, validate output, lọc secret chưa?
6. **Nhỏ hơn được không?** Có thể bỏ bớt component nào mà vẫn chạy không (YAGNI)?

> Trả lời được 6 câu này = mày đang *kiểm duyệt*, không còn *nhận* code AI mù.
```

- [ ] **Step 2: Viết C2 — Catalog tổng red-flags (🟢)**

```markdown
### C2. 🚩 Catalog tổng "AI/vibe coding hay làm sai" — Tra nhanh 🟢

Gom mọi red-flag rải trong A/B về một bảng để soi nhanh:

| Vùng | 🚩 Lỗi AI hay sinh | Sửa hướng nào |
|---|---|---|
| Ingestion | OCR mọi PDF; embed thẳng Excel | Check born-digital; Excel → structured query |
| Chunking | Chunk cố định cho mọi loại; quên fallback | Cắt theo ranh giới nghĩa; có fallback |
| Embedding | Model tiếng Anh cho tiếng Việt; đổi không đo | Chọn cross-lingual; đo precision@k |
| Retrieval | Pure vector cho exact-match; quên rerank; top_k bừa | Hybrid; rerank khi cần; gắn top_k với budget |
| Grounding | Thiếu rào "không bịa"; nhồi quá nhiều chunk | Thêm ràng buộc; giới hạn chunk |
| Model/Cost | Model đắt cho agent loop; không cache | Model rẻ cho loop nhiều bước; prompt cache |
| Agent | Bọc mọi thứ thành agent; loop vô hạn; tool không sandbox | Pipeline khi đủ; max_steps; allowlist tool |
| Eval | Khoe không số liệu; không log cost | Golden set; log token/latency |
| Security | Nhét secret/PII vào prompt; tin input | Lọc trước khi gửi; chống injection |
| Infra | Kéo AWS/K8s cho project nhỏ; DB nặng vô ích | Railway/VPS; brute-force khi nhỏ |
| Build-vs-Buy | Nhét LLM vào việc rule/SQL giải được | Dùng hàm thường khi bài xác định |
```

- [ ] **Step 3: Viết C3 — Capstone điều phối nhiều agent (🟢 phần L4 + 🔵 phần L5)**

```markdown
### C3. Capstone — Điều phối & kiểm duyệt nhiều agent (L4→L5)

**🟢 Phần L4 (học ở Tuần 5):**
- **🎯 Quyết định cốt lõi:** chia bài thành mấy agent, mỗi agent vai gì, ai điều phối (router), ai kiểm (reviewer).
- **⚖️ Bảng lựa chọn:** Router + chuyên trách (Code Finder/Explainer) + Reviewer — *chọn khi* vai trò tách bạch rõ · Gộp lại 1 agent — *chọn khi* các vai chồng lấn, tách ra chỉ thêm overhead.
- **🚩 AI/vibe coding hay sai:** AI đẻ 5 agent cho việc 2 agent làm xong → chậm, đắt, lỗi chồng; AI để các agent gọi vòng nhau không điểm dừng; AI không có agent reviewer → không ai bắt lỗi output.
- **🛑 Khi nào KHÔNG cần (đỉnh tháp — kiềm chế):** nếu pipeline L2 hoặc 1 agent L3 giải được → ĐỪNG multi-agent. Roadmap cắt agent thứ 3 đầu tiên khi trễ là vì vậy.
- **🔍 Câu tự soi:** "Mỗi agent có một vai TÁCH BẠCH không, hay đang chia cho có?"; "Có agent/bước nào kiểm chứng output cuối không?"

**🔵 Phần L5 (đào sâu sau CV):** governance fleet — gom observability/cost/lỗi xuyên nhiều agent, trace mỗi agent, ngân sách token toàn hệ, fallback khi 1 agent chết.

- **🔗 Đào sâu:** roadmap Tuần 5 (kiến trúc Router/Code Finder/Explainer/Reviewer) + A7 + B1 + thang L1-L5.
```

- [ ] **Step 4: Verify**

Run: `rg -n "^### C[1-3]\." ai-code-auditor/docs/ban-do-phan-doan-architect.md` → Expected: 3 dòng.
Run: `rg -ni "TODO|TBD|fill in" ai-code-auditor/docs/ban-do-phan-doan-architect.md` → Expected: không kết quả.

- [ ] **Step 5: Commit (HỎI user trước)**

```bash
git add ai-code-auditor/docs/ban-do-phan-doan-architect.md
git commit -m "docs: add Part C cross-cutting C1-C3 (judgment framework, red-flag catalog, orchestration capstone)"
```

---

## Task 6: Chèn con trỏ "🧭 Góc Architect" vào lo-trinh-chi-tiet.md

**Files:**
- Modify: `ai-code-auditor/docs/lo-trinh-chi-tiet.md` (6 vị trí: đầu Tuần 1, 2, 3, 5, 6, 7)

**Interfaces:**
- Consumes: companion doc đã có A2-A7, B1-B4, C1-C3 (Task 2-5).
- Produces: 6 box trỏ link. KHÔNG sửa nội dung học chính, KHÔNG dời ngày.

> **Lưu ý executor:** chèn mỗi box NGAY DƯỚI dòng "**Mục tiêu tuần:**" của tuần tương ứng (hoặc ngay sau heading tuần nếu tuần đó không có dòng Mục tiêu). Dùng Edit với anchor là dòng heading tuần để định vị chính xác. Link dùng đường dẫn tương đối `ban-do-phan-doan-architect.md` (cùng thư mục docs).

- [ ] **Step 1: Box Tuần 1** — chèn dưới "Mục tiêu tuần" của `## TUẦN 1`:

```markdown
> 🧭 **Góc Architect (song song, 30 phút/tối):** đọc [Bản Đồ Phán Đoán Architect](ban-do-phan-doan-architect.md) mục **A2 Chunking · A3 Embedding · A4 Retrieval · A5 Grounding** — tập trung khối 🚩 và 🔍 để biết AI hay sai gì khi sinh code các bước này.
```

- [ ] **Step 2: Box Tuần 2** — chèn dưới "Mục tiêu tuần" của `## TUẦN 2`:

```markdown
> 🧭 **Góc Architect:** [Bản Đồ Phán Đoán Architect](ban-do-phan-doan-architect.md) mục **A4 Hybrid · B1 Evaluation · B3 chọn Vector DB** — gắn với việc đo precision@3 và migrate ChromaDB tuần này.
```

- [ ] **Step 3: Box Tuần 3** — chèn dưới "Mục tiêu tuần" của `## TUẦN 3`:

```markdown
> 🧭 **Góc Architect:** [Bản Đồ Phán Đoán Architect](ban-do-phan-doan-architect.md) mục **A6 Model & Cost · A7 Agent design (L3)** — đặc biệt khối 🛑 "khi nào KHÔNG cần agent" để tránh over-engineer.
```

- [ ] **Step 4: Box Tuần 5** — chèn dưới "Mục tiêu tuần" của `## TUẦN 5`:

```markdown
> 🧭 **Góc Architect:** [Bản Đồ Phán Đoán Architect](ban-do-phan-doan-architect.md) mục **A7 · C3 Capstone điều phối (L4)** — nhớ nguyên tắc đỉnh tháp: kiềm chế, chỉ multi-agent khi vai trò thật sự tách bạch.
```

- [ ] **Step 5: Box Tuần 6** — chèn dưới heading `### Ngày 36–37` hoặc đầu `## TUẦN 6`:

```markdown
> 🧭 **Góc Architect:** [Bản Đồ Phán Đoán Architect](ban-do-phan-doan-architect.md) mục **B3 Deploy (🟢)** + đọc-để-biết **B2 Security · B4 Build-vs-Buy (🔵)** — gắn với audit thật chatbot-fanpage (tìm hardcode secret).
```

- [ ] **Step 6: Box Tuần 7** — chèn đầu `## TUẦN 7`:

```markdown
> 🧭 **Góc Architect:** ôn [Bản Đồ Phán Đoán Architect](ban-do-phan-doan-architect.md) mục **C1 Khung phán đoán · C2 Catalog red-flags** — dùng để trả lời câu phỏng vấn "khi nào dùng gì / sao biết AI sai".
```

- [ ] **Step 7: Verify 6 con trỏ tồn tại**

Run: `rg -c "Góc Architect" ai-code-auditor/docs/lo-trinh-chi-tiet.md`
Expected: `6`.
Run: `rg -n "ban-do-phan-doan-architect.md" ai-code-auditor/docs/lo-trinh-chi-tiet.md`
Expected: 6 dòng link.

- [ ] **Step 8: Verify KHÔNG dời ngày (số heading "### Ngày" không đổi)**

Run: `rg -c "^### Ngày" ai-code-auditor/docs/lo-trinh-chi-tiet.md`
Expected: số lượng giữ NGUYÊN như trước khi sửa (chỉ thêm box blockquote, không thêm/bớt ngày).

- [ ] **Step 9: Commit (HỎI user trước)**

```bash
git add ai-code-auditor/docs/lo-trinh-chi-tiet.md
git commit -m "docs: add architect-judgment pointers into roadmap weeks 1-7"
```

---

## Self-Review

**1. Spec coverage:**
- Spec §4.1 thang L1-L5 → Task 1 Step 2 ✅
- Spec §4.2 bản đồ A1-A7/B1-B4/C1-C3 → Task 2-5 ✅ (A1✅ A2-A4 Task2; A5-A7 Task3; B1-B4 Task4; C1-C3 Task5)
- Spec §4.3 template 6 khối → mọi mục A/B/C dùng đúng 6 khối ✅
- Spec §5 con trỏ roadmap 6 tuần → Task 6 (Tuần 1,2,3,5,6,7) ✅
- Spec §6 tag 🟢/🔵 → A1🔵, B2🔵, B4🔵, C3 hỗn hợp; còn lại 🟢 ✅
- Spec §8 tiêu chí: mục 🔵 chỉ khung + "đào sâu sau" ✅ (A1/B2/B4 có dòng "đào sâu sau CV")

**2. Placeholder scan:** mọi mục 🟢 có nội dung thật; "đào sâu sau CV" ở mục 🔵 là quyết định scope theo spec, không phải placeholder. Verify step có `rg` chặn TODO/TBD. ✅

**3. Type consistency:** tên file `ban-do-phan-doan-architect.md` đồng nhất mọi task; heading mỏ neo `## PHẦN A/B/C` tạo ở Task 1, điền ở Task 2-5; tag emoji 🟢/🔵 nhất quán. ✅

**Gap đã xử lý:** Tuần 6 dùng anchor `### Ngày 36–37` vì spec §5 ghi B-topics ở Tuần 6; nếu Tuần 6 không có dòng "Mục tiêu tuần" thì chèn sau heading ngày đầu tiên (đã ghi rõ trong Step 5).
