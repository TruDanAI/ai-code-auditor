# BẢN ĐỒ PHÁN ĐOÁN ARCHITECT — Khi nào dùng gì & Bắt lỗi AI sinh code

> **Tài liệu này là gì:** Một bản đồ giúp mày — người hay vibe coding — chuyển từ *nhận* code AI sang *kiểm duyệt* code AI. Không dạy implement sâu; dạy **phán đoán**: khi nào dùng gì, khi nào ĐỪNG, và AI hay sai chỗ nào.
>
> **Cách dùng:** Khi roadmap dẫn tới một chủ đề (qua box 🧭 Góc Architect), mở đúng mục ở đây. Đọc khối 🚩 và 🔍 trước — đó là phần trị vibe coding. Lý thuyết sâu nằm ở NOTES.md/roadmap/dsa-cho-ky-su-ai.md (khối 🔗 trỏ tới), tài liệu này KHÔNG lặp lại.
>
> **Là living document:** mục 🟢 học trong 2 tháng roadmap; mục 🔵 đọc-để-biết giờ, đào sâu sau CV theo dự án thật.
>
> **🆕 Track Beyond-RAG (22/6/2026):** kiến trúc cấp Enterprise (GraphRAG, RAPTOR, Speculative RAG, vLLM/on-prem, audit swarm) gom ở [beyond-rag-phase-2.md](beyond-rag-phase-2.md). Phần rẻ-ăn-điểm đã rải vào **A4** (CRAG), **B1** (RAG Triad), **B2** (constrained decoding/input guard) + roadmap section "Tích Hợp Beyond-RAG (Tầng 1)".

---

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

---

## TEMPLATE MỖI CHỦ ĐỀ (6 khối cố định)

- **🎯 Quyết định cốt lõi** — chủ đề này trả lời câu "chọn gì giữa cái gì".
- **⚖️ Bảng lựa chọn** — option → chọn khi nào → đánh đổi.
- **🚩 AI/vibe coding hay sai** — lỗi cụ thể AI hay sinh ở đây.
- **🛑 Khi nào KHÔNG cần** — dấu hiệu over-engineer.
- **🔍 Câu tự soi khi review code AI** — câu hỏi tự đặt khi nhìn output AI.
- **🔗 Đào sâu** — trỏ về nguồn lý thuyết (không lặp).

Tag: 🟢 [Học trong lộ trình] · 🔵 [Dài hạn — đào sâu sau CV]

---

## PHẦN A — LANE (phán đoán trong pipeline RAG/Agent)

### A1. Input & Ingestion — Router định dạng đầu vào 🔵 [Dài hạn]

- **🎯 Quyết định cốt lõi:** input thật (PDF/docx/excel/link/ảnh) đi parser nào, khi nào cần OCR.
- **⚖️ Bảng lựa chọn:** PDF text → pymupdf · PDF scan/ảnh tiếng Việt → **VietOCR** (PaddleOCR lo *detection*, không nhận dạng VN gốc) · docx → python-docx · xlsx → pandas (KHÔNG embed thẳng) · link → trafilatura.
- **🚩 AI/vibe coding hay sai:** AI mặc định OCR mọi PDF (chậm 50×, bẩn text born-digital); AI embed thẳng bảng Excel (vô nghĩa, như #1234≈#5678).
- **🛑 Khi nào KHÔNG cần:** input đã là text thuần (repo code) → bỏ qua cả tầng này.
- **🔍 Câu tự soi:** "File này born-digital hay scan — AI có check trước khi OCR không?"
- **🔗 Đào sâu sau CV:** chi tiết per-page threshold đã bàn trong hội thoại ingestion + sẽ là feature giai đoạn 2 của AI Code Auditor.

### A2. Chunking — Cắt mà không phá ngữ cảnh 🟢

- **🎯 Quyết định cốt lõi:** cắt theo gì (ký tự cố định / ranh giới có nghĩa / có overlap) và kích thước bao nhiêu.
- **⚖️ Bảng lựa chọn:** Theo ranh giới có nghĩa (heading .md, hàm .js) — *chọn khi* cấu trúc rõ, chất lượng cao nhất · Ký tự cố định — *chọn khi* text phi cấu trúc, đơn giản · + Overlap 50-100 ký tự — *chọn khi* sợ cắt mất ngữ cảnh ranh giới.
- **🚩 AI/vibe coding hay sai:** AI chọn chunk cố định 500 ký tự cho MỌI loại → cắt giữa hàm, mất nghĩa; AI quên fallback cắt chunk khổng lồ → 1 chunk nuốt cả file, hỏng embedding; AI set chunk size tùy hứng không gắn với context budget.
- **🛑 Khi nào KHÔNG cần:** tài liệu nhỏ fit context → stuffing, khỏi chunk.
- **🔍 Câu tự soi:** "Có chunk nào bị cắt GIỮA một đơn vị logic (hàm/đoạn) không?"; "Có bước fallback cho chunk quá dài chưa?"
- **🔗 Đào sâu:** NOTES.md Ngày 4 + roadmap Tuần 2 (compare_chunking đo precision@3 cho 3 chiến lược).

### A3. Embedding — Chọn model biểu diễn nghĩa 🟢

- **🎯 Quyết định cốt lõi:** dùng embedding model nào, khi nào nâng cấp, có hợp đa ngôn ngữ không.
- **⚖️ Bảng lựa chọn:** all-MiniLM-L6-v2 (80MB, CPU) — *chọn khi* học/prototype, tiếng Anh · BGE-M3 (~2GB) — *chọn khi* cần đa ngôn ngữ ổn · Qwen3-Embedding — *chọn khi* tiếng Việt + cần SOTA, có GPU.
- **🚩 AI/vibe coding hay sai:** AI bê model tiếng Anh (MiniLM) cho bài tiếng Việt → cross-lingual yếu (VI-EN ~0.27 cosine); AI đổi model nhưng quên đo lại precision → "cảm giác tốt hơn" không số liệu; AI không normalize vector trước khi so.
- **🛑 Khi nào KHÔNG cần:** cần khớp chính xác (mã đơn, tên hàm) → keyword/DB, không embedding.
- **🔍 Câu tự soi:** "Bài này có tiếng Việt không — model AI chọn có cross-lingual nổi không?"; "Đổi model rồi có đo precision@3 lại chưa?"
- **🔗 Đào sâu:** NOTES.md Ngày 2-3 (số đo MiniLM VI-EN) + roadmap Tuần 2 Ngày 10 (bảng so MiniLM/BGE-M3/Qwen3).

### A4. Retrieval — Vector / Keyword / Hybrid / Rerank 🟢

- **🎯 Quyết định cốt lõi:** tìm bằng vector, keyword, hay cả hai; có cần rerank không; top_k bao nhiêu.
- **⚖️ Bảng lựa chọn:** Vector (semantic) — *chọn khi* hỏi theo ý, khác chữ cùng nghĩa · Keyword/BM25 — *chọn khi* exact-match (ID, tên hàm) · Hybrid — *chọn khi* sản phẩm thật (gộp cả hai) · + Rerank — *chọn khi* precision quan trọng, chịu thêm latency.
- **➕ CRAG (Corrective RAG):** thêm một *retrieval evaluator* chấm độ tin chunk (đúng/sai/mơ hồ) → sai thì fallback (web/keyword/hỏi lại). *Chọn khi* retrieval hay trả rác (vd recall thấp như baseline Ngày 6); KHÔNG cần khi retrieval đã chuẩn. 🔗 [beyond-rag-phase-2.md](beyond-rag-phase-2.md) mục 1+3 + roadmap Tầng 1 Món 2.
- **🚩 AI/vibe coding hay sai:** AI mặc định pure vector cho mọi thứ → chết với exact-match (mã đơn, tên hàm); AI trả thẳng top-k cosine, quên rerank → precision thấp không rõ lý do; AI set top_k tùy hứng (3? 10?) không gắn context budget.
- **🛑 Khi nào KHÔNG cần:** vài trăm chunk → brute-force O(n) đủ, đừng vác vector DB/ANN sớm.
- **🔍 Câu tự soi:** "Câu exact-match (số/ID/tên hàm) có lọt vào nhánh vector không — nếu có là sai."; "top_k này dựa trên cái gì, hay AI bịa số?"
- **🔗 Đào sâu:** dsa-cho-ky-su-ai.md mục 3 (top-k/heap) & mục 7 (HNSW) + NOTES.md Ngày 2 (hybrid).

### A5. Prompt assembly & Grounding — Chống bịa 🟢

- **🎯 Quyết định cốt lõi:** ghép context vào prompt thế nào để model KHÔNG bịa, có trích dẫn.
- **⚖️ Bảng lựa chọn:** Ràng buộc "chỉ dùng context, thiếu thì nói không biết" — *luôn dùng* · Kèm file/chunk_id mỗi đoạn — *chọn khi* cần citation/debug · Few-shot ví dụ định dạng — *chọn khi* cần output cấu trúc cố định.
- **🚩 AI/vibe coding hay sai:** AI viết prompt không có rào "không bịa" → model tự tin bịa code không có thật; AI nhồi quá nhiều chunk → "lost in the middle", model bỏ sót; AI quên gắn nguồn → không truy vết được câu trả lời.
- **🛑 Khi nào KHÔNG cần:** câu hỏi kiến thức tổng quát có sẵn trong model → không cần grounding.
- **🔍 Câu tự soi:** "Prompt có câu 'nếu context không có thì trả lời không tìm thấy' không?"; "Nếu retrieval lấy chunk rác, prompt này có chặn được bịa không?"
- **🔗 Đào sâu:** roadmap Ngày 5 (build_prompt) + Ngày 6 (stress-test hallucination).

### A6. Model & Cost — Chọn LLM nào, khi nào 🟢

- **🎯 Quyết định cốt lõi:** dùng model nào cho việc nào, cân giữa chất lượng/giá/tốc độ.
- **⚖️ Bảng lựa chọn:** Flash mới nhất (đắt, mạnh) — *chọn khi* việc khó, gọi ít · Flash đời cũ/lite (rẻ) — *chọn khi* vòng lặp agent gọi nhiều lần · Prompt caching — *chọn khi* prompt lặp phần lớn (system prompt dài).
- **🚩 AI/vibe coding hay sai:** AI để model đắt nhất chạy vòng agent nhiều bước → hóa đơn nổ; AI quên context window có giới hạn + tốn tiền theo token; AI không cache phần prompt lặp.
- **🛑 Khi nào KHÔNG cần:** prototype học → 1 model là đủ, đừng tối ưu chi phí sớm.
- **🔍 Câu tự soi:** "Vòng agent này gọi LLM mấy lần/câu — model AI chọn có hợp chi phí không?"; "Tiếng Việt tốn ~2× token, đã tính vào chi phí chưa?"
- **🔗 Đào sâu:** roadmap mục cập nhật chi phí (gemini-3.5-flash đắt nhất họ Flash) + ban-do-cong-nghe-chi-phi.md.

### A7. Agent design — Khi nào DÙNG agent 🟢

- **🎯 Quyết định cốt lõi:** bài này cần agent (L3) không, hay pipeline (L2) đủ; ReAct vs workflow cố định; 1 agent hay nhiều.
- **⚖️ Bảng lựa chọn:** Pipeline cố định (L2) — *chọn khi* luồng biết trước, không rẽ nhánh · 1 agent ReAct (L3) — *chọn khi* cần chọn tool động, nhiều bước · Workflow có cấu trúc (LangGraph) — *chọn khi* cần state/retry/rẽ nhánh kiểm soát được.
- **🚩 AI/vibe coding hay sai:** AI bọc mọi thứ thành "agent" dù pipeline thẳng là đủ → chậm, khó debug; AI để agent loop không giới hạn bước → cháy token/treo; AI cho agent tool nguy hiểm (xóa file, chạy shell) không sandbox.
- **🛑 Khi nào KHÔNG cần:** luồng 1 bước hoặc biết trước → KHÔNG agent. Đây là cạm bẫy over-engineer phổ biến nhất.
- **🔍 Câu tự soi:** "Bài này có thật sự cần agent quyết định động, hay AI đang vẽ agent cho oai?"; "Có max_steps chặn vòng lặp chưa?"
- **🔗 Đào sâu:** roadmap Tuần 3 (agent.py ReAct) + Tuần 5 (LangGraph) + dsa-cho-ky-su-ai.md mục 8 (stack/queue).

### A8. Giao thức chọn & làm mới model (VN-first) 🟢 [xuyên A1/A3/A6]

> **Triết lý:** đừng nhớ "model nào tốt nhất" (hôm nay đúng, 3 tháng sau sai) — **dựng cái cân** để LUÔN biết model nào tốt nhất *cho dữ liệu tiếng Việt của mày*, và đổi được trong 1 dòng.

- **🎯 Quyết định cốt lõi:** model (embedding/LLM/OCR) chọn thế nào để **không lỗi thời** khi model mới ra liên tục.
- **⚖️ Giao thức 3 mảnh:**
  1. **Config-swap:** tên model nằm ở **config**, không hardcode trong logic → đổi model = sửa 1 dòng, không đụng pipeline.
  2. **Golden set thường trực (tiếng Việt):** model mới → cắm vào → đo **precision@k + cost + latency trên DỮ LIỆU CỦA MÀY** → số liệu quyết, KHÔNG tin leaderboard chung.
  3. **Trigger làm mới:** chỉ đo lại khi *(có model mới đáng chú ý / giá đổi / precision chững)* — không đo mỗi ngày.
- **✅ Checklist swap-and-measure** (mỗi lần thử model mới):
  - [ ] Đổi đúng 1 biến config (model name), không đụng pipeline.
  - [ ] Chạy lại golden set → ghi precision@k.
  - [ ] Đo cost/1k token + latency/query.
  - [ ] So model hiện tại: tốt hơn **đủ để bù** chi phí/độ nặng không?
  - [ ] Ghi số vào bảng → đây là **số liệu vàng cho CV**.
- **🗺️ Bảng model VN-first (cập nhật 6/2026 — vẫn phải tự đo lại):**

| Tầng | VN ưu tiên | Thay thế / EN | Ghi chú |
|---|---|---|---|
| Embedding | Qwen3-Embedding (RoPE, mạnh đa ngữ) · halong-embedding · vietnamese-bi-encoder (bkai) | multilingual-e5 · BGE-M3 | Đo trên **VN-MTEB**; model lớn + RoPE thắng |
| LLM (sinh) | Qwen3 30B / Next-80B MoE (dẫn SEA-HELM VN) · PhoGPT-4B · Vistral/Sailor (self-host) | Gemini Flash (API, rẻ, tiếng Việt khá) | Dual-stack: API frontier cho tiện + Qwen self-host cho chủ quyền dữ liệu |
| OCR | **VietOCR** (transformer, dấu thanh) | PaddleOCR (chỉ *detection*, không nhận dạng VN gốc) · VLM (Gemini/Qwen-VL) cho layout rối | Combo phổ biến: PaddleOCR detect + VietOCR recognize |

- **🚩 AI/vibe coding hay sai:** AI hardcode tên model khắp code → đổi model là cực hình; AI chọn model theo **bảng xếp hạng tiếng Anh** rồi áp cho tiếng Việt (MTEB EN ≠ VN-MTEB); AI nói "PaddleOCR đọc tiếng Việt" — sai, cần VietOCR.
- **🛑 Khi nào KHÔNG cần:** prototype 1 lần / dữ liệu không đổi → 1 model cố định, đừng dựng cả giao thức (kiềm chế).
- **🔍 Câu tự soi:** "Đổi model này tốn mấy dòng — nhiều thì model đang bị hardcode."; "Có số liệu trên DỮ LIỆU TIẾNG VIỆT của mình chưa, hay đang tin leaderboard chung?"
- **🔗 Đào sâu:** A1 (OCR) · A3 (embedding) · A6 (model & cost) + roadmap Tuần 2 Ngày 9-10 (golden set + bảng so model). Benchmark tham khảo: **VN-MTEB · SEA-HELM · vmlu.ai** (tra lại định kỳ).

---

## PHẦN B — VỎ BỌC PRODUCTION

### B1. Evaluation & Observability — Đo thay vì đoán 🟢

- **🎯 Quyết định cốt lõi:** đo chất lượng RAG/agent bằng metric nào (precision@k, latency, cost, hallucination rate) và log gì.
- **⚖️ Bảng lựa chọn:** Golden set + precision@k — *chọn khi* đo chất lượng retrieval · Log token/latency/tool mỗi call — *chọn khi* cần biết chi phí/điểm nghẽn · Test off-topic — *chọn khi* kiểm rào chống bịa · **RAG Triad (LLM-as-judge)** — *chọn khi* cần đo tự động 3 trục Context Relevance / Groundedness / Answer Relevance vượt khỏi precision@k · **Trace tool (LangSmith/Phoenix)** — *chọn khi* agent nhiều bước, cần soi span/loop.
- **🚩 AI/vibe coding hay sai:** AI khoe "cải thiện" không có số liệu (golden set); AI quên log token/latency → không biết chi phí thật; AI không test câu off-topic → rào chống bịa chưa được kiểm.
- **🛑 Khi nào KHÔNG cần:** demo 1 lần dùng rồi bỏ → khỏi dựng eval harness.
- **🔍 Câu tự soi:** "Thay đổi này có số đo trước/sau không, hay chỉ 'cảm giác tốt hơn'?"; "1 query tốn bao nhiêu token/tiền — có log không?"
- **🔗 Đào sâu:** roadmap Tuần 2 Ngày 9 (precision@3 + golden set) + Tuần 3 (agent_log.jsonl).

### B2. Guardrails, Safety & Security 🔵 [Dài hạn]

- **🎯 Quyết định cốt lõi:** chặn prompt injection, lọc PII, và cái gì TUYỆT ĐỐI không gửi cho LLM.
- **⚖️ Bảng lựa chọn:** Validate output (schema/regex) · **Constrained decoding** (ép JSON Schema *lúc sinh* — function calling/Outlines, chắc hơn validate sau) · Lọc PII/secret trước khi gửi · System prompt chống injection · **Input guard** (model phân loại nhỏ vd Llama-Guard quét prompt độc ngay cổng) · Allowlist tool cho agent.
- **🚩 AI/vibe coding hay sai:** AI nhét nguyên secret/API key vào prompt; AI tin tưởng input người dùng → injection "bỏ qua lệnh trên"; AI cho agent quyền chạy shell không sandbox.
- **🛑 Khi nào KHÔNG cần:** prototype nội bộ, dữ liệu không nhạy cảm → guardrail tối thiểu.
- **🔍 Câu tự soi:** "Prompt này có chứa secret/PII không nên rời máy không?"; "Input người dùng có thể ghi đè system prompt không?"
- **🔗 Đào sâu sau CV:** OWASP LLM Top 10; gắn với audit thật chatbot-fanpage (Tuần 6 — tìm hardcode secret).

### B3. Deployment & Infra — Managed vs Self-host 🟢

- **🎯 Quyết định cốt lõi:** chạy ở đâu (Railway/VPS/serverless/AWS), vector DB nào, khi nào managed.
- **⚖️ Bảng lựa chọn:** Railway/Render — *chọn khi* SME, budget thấp, đơn giản · VPS+Docker — *chọn khi* cần kiểm soát, rẻ · AWS/Azure — *chọn khi* enterprise/JD yêu cầu · Vector DB: Chroma (local/nhỏ) vs pgvector (đã có Postgres) vs Pinecone (managed, scale).
- **🚩 AI/vibe coding hay sai:** AI mặc định kéo AWS/Kubernetes cho project nhỏ → phức tạp thừa, đắt; AI chọn vector DB nặng khi vài trăm chunk (brute-force đủ); AI quên chunk in-memory mất khi restart.
- **🛑 Khi nào KHÔNG cần:** project học/SME nhỏ → KHÔNG cần AWS; Railway/VPS là đủ.
- **🔍 Câu tự soi:** "Quy mô này có thật sự cần infra AI vẽ ra, hay nhỏ hơn là đủ?"; "Dữ liệu có persist qua restart không?"
- **🔗 Đào sâu:** roadmap Tuần 6 (Docker/Railway) + ban-do-cong-nghe-chi-phi.md (bảng AWS vs alternatives) + CLAUDE.md (chunk in-memory mất khi restart).

### B4. Build vs Buy & Khi nào KHÔNG dùng AI 🔵 [Dài hạn]

- **🎯 Quyết định cốt lõi:** tự build, dùng managed service, hay KHÔNG dùng AI/LLM cho bài này.
- **⚖️ Bảng lựa chọn:** Build tay — *chọn khi* cần hiểu/kiểm soát, lõi sản phẩm · Managed (Bedrock/OpenAI Assistants) — *chọn khi* cần nhanh, không phải lõi · KHÔNG dùng LLM — *chọn khi* việc xác định được bằng rule/SQL/regex.
- **🚩 AI/vibe coding hay sai:** AI nhét LLM vào việc mà if-else/SQL giải xong (đắt + bất định); AI build lại thứ managed service làm tốt hơn; AI dùng LLM cho phép tính số học chính xác.
- **🛑 Khi nào KHÔNG cần AI:** bài có lời giải xác định (tính toán, tra cứu chính xác, rule rõ) → đừng dùng LLM.
- **🔍 Câu tự soi:** "Việc này có cần LLM không, hay một hàm thường giải được rẻ và chắc hơn?"
- **🔗 Đào sâu sau CV:** ban-do-cong-nghe-chi-phi.md + bảng "Bài Toán Nào Dùng Gì" của roadmap.

---

## PHẦN C — XUYÊN SUỐT

### C1. Khung phán đoán Architect — Checklist soi mọi giải pháp AI 🟢

Khi AI (hoặc mày) đưa ra một giải pháp, chạy qua 6 câu này TRƯỚC khi chấp nhận:

1. **Cấp nào?** Bài này cần L1-L5 mấy? Có đang dùng cấp cao hơn mức cần không?
2. **Exact hay semantic?** Có phần exact-match nào đang bị nhét vào embedding không?
3. **Đo bằng gì?** Có metric/số liệu chứng minh nó tốt, hay chỉ "cảm giác"?
4. **Chi phí?** 1 request tốn bao nhiêu token/tiền/latency? Có log không?
5. **Hỏng thì sao?** Có rào chống bịa, max_steps, validate output, lọc secret chưa?
6. **Nhỏ hơn được không?** Có thể bỏ bớt component nào mà vẫn chạy không (YAGNI)?

> Trả lời được 6 câu này = mày đang *kiểm duyệt*, không còn *nhận* code AI mù.

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

### C3. Capstone — Điều phối & kiểm duyệt nhiều agent (L4→L5)

**🟢 Phần L4 (học ở Tuần 5):**
- **🎯 Quyết định cốt lõi:** chia bài thành mấy agent, mỗi agent vai gì, ai điều phối (router), ai kiểm (reviewer).
- **⚖️ Bảng lựa chọn:** Router + chuyên trách (Code Finder/Explainer) + Reviewer — *chọn khi* vai trò tách bạch rõ · Gộp lại 1 agent — *chọn khi* các vai chồng lấn, tách ra chỉ thêm overhead.
- **🚩 AI/vibe coding hay sai:** AI đẻ 5 agent cho việc 2 agent làm xong → chậm, đắt, lỗi chồng; AI để các agent gọi vòng nhau không điểm dừng; AI không có agent reviewer → không ai bắt lỗi output.
- **🛑 Khi nào KHÔNG cần (đỉnh tháp — kiềm chế):** nếu pipeline L2 hoặc 1 agent L3 giải được → ĐỪNG multi-agent. Roadmap cắt agent thứ 3 đầu tiên khi trễ là vì vậy.
- **🔍 Câu tự soi:** "Mỗi agent có một vai TÁCH BẠCH không, hay đang chia cho có?"; "Có agent/bước nào kiểm chứng output cuối không?"

**🔵 Phần L5 (đào sâu sau CV):** governance fleet — gom observability/cost/lỗi xuyên nhiều agent, trace mỗi agent, ngân sách token toàn hệ, fallback khi 1 agent chết.

- **🔗 Đào sâu:** roadmap Tuần 5 (kiến trúc Router/Code Finder/Explainer/Reviewer) + A7 + B1 + thang L1-L5.
