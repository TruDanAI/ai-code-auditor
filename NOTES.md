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
    *   Tìm kiếm bằng **từ khóa** (so khớp ký tự / substring) **chết** khi người hỏi dùng từ khác nhưng cùng nghĩa: code ghi `verify signature`, người dùng hỏi *"kiểm tra chữ ký"* → so khớp chữ ra **0 kết quả**, dù hai câu cùng một ý.
    *   Cần một cách "tìm theo nghĩa" thay vì "tìm theo chữ".
*   **Giải pháp là gì?**
    *   **Embedding**: dùng model (vd `all-MiniLM-L6-v2`) biến mỗi câu thành một **vector số nhiều chiều** (ở đây 384 chiều), sao cho **hai câu gần nghĩa thì hai vector gần nhau** trong không gian. Encode 6 câu → ma trận `(6, 384)`: 6 hàng = 6 câu, mỗi câu định vị bằng 384 "thước đo" nghĩa.
    "Embedding biến text thành vector số sao cho gần nghĩa thì gần nhau. Vấn đề nó giải: keyword search chết khi cùng ý mà khác chữ — hỏi 'cách thoát tài khoản' nhưng tài liệu ghi 'đăng xuất'. Giải pháp: so theo vector ngữ nghĩa thay vì ký tự. Đánh đổi: embedding mù khớp chính xác — em đo #1234 vs #5678 vẫn ra cosine 0.98, model không phân biệt được số. Nên mã đơn/SĐT em để DB query, tìm theo ý mới dùng embedding, và kết hợp cả hai gọi là hybrid search."
    *   Nghĩa được **rải khắp 384 chiều**, không nằm gọn ở vài số đầu → in 5/384 số ra nhìn mắt thường KHÔNG thấy cặp nào gần (như đọc 5/384 trang sách rồi đoán nội dung). Vì vậy cần một phép đo gộp cả 384 chiều thành 1 con số "độ gần" = **cosine similarity** (học ở Ngày 3 — đây là *cây thước đo*, không phải bản thân giải pháp embedding).
*   **Khi nào KHÔNG dùng?**
    *   **Cần khớp chính xác** (mã đơn, SĐT, tên hàm): embedding bắt *ngữ nghĩa* chứ không phân biệt *con số*. Đo thật: `#1234 vs #5678` cosine = **0.9835** (gần như giống hệt) → tra mã đơn phải dùng **keyword/DB query**, không dùng embedding. Hệ thật kết hợp cả hai = **hybrid search**.
    *   **Model yếu đa ngôn ngữ**: `#1234` tiếng Việt vs tiếng Anh dù cùng nghĩa chỉ đạt cosine = **0.2669** — vì MiniLM train chủ yếu trên tiếng Anh, yếu cross-lingual + tiếng Việt. Đây là *giới hạn của model*, không phải lỗi dữ liệu → bài toán tiếng Việt nên nâng cấp sang model mạnh hơn (vd Qwen3-Embedding) ở tuần 2. Đây cũng là **số liệu vàng cho CV**: "cải thiện precision@3 khi đổi MiniLM → Qwen3-Embedding".
    *   Tài liệu **nhỏ + ít thay đổi** (vài trang chính sách nội bộ): nhồi thẳng vào prompt là đủ, chưa cần embedding/RAG cho phức tạp.

### Ngày 3: Cosine Similarity — Đo "độ gần nghĩa" giữa hai vector
*   **Vấn đề là gì?**
    *   Sau Ngày 2, mỗi câu đã thành vector 384 chiều, nhưng "hai vector gần nhau" là một con số *chưa đo được*. Cần một phép gộp cả 384 chiều thành **một số duy nhất** thể hiện độ giống.
*   **Giải pháp là gì?**
    *   **Cosine similarity** đo **góc** giữa hai vector: `cos = (A·B) / (‖A‖×‖B‖)`. Cùng hướng → `cos(0°)=1` (đồng nghĩa); vuông góc → `cos(90°)=0` (không liên quan); ngược hướng → `cos(180°)=−1` (đối nghĩa).
    *   **Tử số `A·B`** trộn *cả hướng lẫn độ dài*; **mẫu số `‖A‖×‖B‖`** là *độ dài thuần*. Chia để **triệt tiêu độ dài**, chỉ giữ lại hướng (= nghĩa). Tự viết tay trong `mini_rag.py`, chốt chặn `norm==0 → return 0.0` (vector toàn số 0 mới có norm=0, tránh chia 0).
    *   Kiểm chứng đúng: **đường chéo ma trận = 1.000** (mỗi câu so với chính nó) — đây cũng là mẹo test nhanh hàm cosine.
*   **Khi nào KHÔNG dùng / Lưu ý quan trọng:**
    *   **Cosine vs Euclidean:** Euclidean đo khoảng cách thẳng, bị ảnh hưởng bởi magnitude; cosine bỏ qua magnitude, chỉ đo hướng → công bằng với câu dài/ngắn cùng nghĩa. **NHƯNG** đo thật: `all-MiniLM-L6-v2` xuất vector **đã normalize về độ dài 1** (kiểm chứng `norm(emb)=1.0000`). Khi đã normalize, hai phép **tương đương về thứ hạng**: `Euclidean² = 2×(1−cosine)` (đo thật: √(2×(1−0.7154))=0.7545 ✅). Vẫn chọn cosine vì **bị chặn trong [−1,1]**, dễ đặt ngưỡng. → Câu này tách người hiểu sâu khỏi người học vẹt.
    *   **Brute-force O(n):** tự so query với *từng* chunk. OK với vài trăm chunk; ở quy mô triệu vector phải dùng ANN index (HNSW) trong vector DB thật (Chroma, pgvector) — đánh đổi tốc độ vs chính xác tuyệt đối.
    *   **🔴 Giới hạn model (KHÔNG phải lỗi code):** đo ma trận thấy MiniLM **thất bại song ngữ Việt–Anh**: cặp đồng nghĩa "kiểm tra chữ ký webhook" vs "verify signature" = **−0.026**, còn "chữ ký webhook" vs "nấu phở" (đều tiếng Việt) lại = **0.403**! Model gom cụm theo **ngôn ngữ/bề mặt**, không theo **nghĩa** → nối tiếp phát hiện Ngày 2 (#1234 VI-EN = 0.2669). **💎 Số liệu vàng CV:** đề xuất nâng cấp Qwen3-Embedding ở Tuần 2 và đo lại precision@3.

### Ngày 4: Chunking — Cắt code/docs mà không phá ngữ cảnh
*   **Vấn đề là gì?**
    *   Embed nguyên cả file thành 1 vector → retrieval lúc nào cũng trả về cả file = không khác gì stuffing, tốn token + lẫn rác. Ngược lại cắt quá vụn (giữa thân một hàm) → mảnh mất ngữ cảnh, model đọc không hiểu. Cần cắt sao cho mỗi mảnh là **một đơn vị tự đủ nghĩa**.
*   **Giải pháp là gì?**
    *   Cắt theo **ranh giới có nghĩa** (semantic boundary), không cắt mù theo số ký tự: `.md` cắt theo **heading**, `.js` cắt theo **ranh giới hàm/route** (`function`, `router.get(`, `module.exports`...), mỗi chunk dính kèm heading/tên hàm để biết "mình mô tả cái gì".
    *   **3 bẫy regex đã học (nhánh `.md`):** (1) `(?m)` = multiline → `^`/`$` khớp đầu/cuối **mỗi dòng**, không bật thì `^#` chỉ bắt heading ở dòng đầu cả file. (2) `#{1,6}` = "1–6 ký tự `#` liên tiếp" = heading **bất kỳ cấp nào**, KHÔNG phải "theo thứ tự tăng dần". (3) **Dấu ngoặc `( )` trong `re.split` = capturing group → GIỮ LẠI dòng heading** trong list kết quả; bỏ ngoặc thì heading bị vứt mất, chunk còn mỗi body trơ trụi.
    *   **Fallback bắt buộc:** chunk nào dài hơn `FALLBACK_CHUNK_SIZE*2` (=1600) thì cắt cứng mỗi 800 ký tự, để không bao giờ lọt 1 chunk khổng lồ làm "nhạt nhòa" vector embedding.
*   **Khi nào KHÔNG dùng / Đánh đổi (đo thật trên DESIGN.md):**
    *   Đo thật: DESIGN.md → **13 chunks**. Chunk 0–8 sạch (mỗi chunk 1 section, độ dài lẻ 739/625/784...). Nhưng section `## Admin Auth/RBAC/Audit Proposal` quá dài (~3500 ký tự) → fallback chém thành chunk 9–12 **đúng 800 chars mỗi cái** (dấu vân tay của fallback), cắt **giữa từ**: `rota|tion`, `rout|es`, `fut|ure`. → fallback cắt theo *chỉ số ký tự* nên **phá ngữ cảnh + mất heading**.
    *   **Đánh đổi:** fallback đảm bảo *không có chunk khổng lồ*, nhưng trả giá bằng *mất nghĩa khi cắt giữa câu/từ* (KHÔNG phải "tốn token" — đó là hiểu nhầm).
    *   **Cách cải tiến (→ bài tập `compare_chunking.py` cuối tuần):** (1) cắt ở **ranh giới tự nhiên** gần mốc 800 nhất (`\n\n` → `\n` → dấu câu) = recursive character splitting (LangChain); (2) **overlap ~100 ký tự** giữa 2 chunk liền kề để câu bị cắt đôi vẫn trọn vẹn ở ít nhất 1 chunk.
    *   Tài liệu **nhỏ + ít thay đổi** → bỏ qua chunking, nhồi thẳng là đủ (nối tiếp kết luận Ngày 1–2).

### Ngày 5: Context Packing & Prompt Grounding (rào chắn chống bịa)
*   **Vấn đề là gì?**
    *   LLM được train để **luôn trả lời cho trôi chảy**, kể cả khi không biết. Đưa câu hỏi + vài chunk rồi bảo "trả lời đi" → model sẽ **bịa** ra hàm/logic không có trong codebase (vd mô tả Stripe chung chung từ kiến thức train sẵn rồi gán như thể đó là code của dự án) = **hallucination**.
    *   Nguy hiểm gấp đôi: `retrieve_top_k` **luôn trả về đủ k chunk** kể cả câu hỏi lạc đề (moi 3 chunk "đỡ tệ nhất"). Không có rào chắn, model thấy "có context kèm file path" → gán đại câu trả lời vào chunk vô-quan-hệ + **citation trông xịn** = bịa CÓ dẫn nguồn, còn khó phát hiện hơn bịa trơn.
*   **Giải pháp là gì?**
    *   **Prompt Grounding** = "buộc chân" câu trả lời vào context bằng lệnh tường minh trong prompt: (1) *chỉ dùng thông tin trong context*; (2) *không có thì phải nói "không tìm thấy", tuyệt đối không đoán*; (3) *trích dẫn rõ file + chunk_id*. Dòng (2) là **quan trọng nhất** — nó ra lệnh model **tự xét chunk có liên quan không**, đừng tin "cứ có context là phải dùng".
    *   **Mẹo priming:** kết prompt bằng `TRẢ LỜI:` rồi bỏ trống → LLM là máy đoán-chữ-tiếp-theo, bị đặt đúng "ghế" để sinh ra câu trả lời thay vì lặp lại câu hỏi.
    *   **Context có nhãn:** mỗi chunk dán `file path | chunk_id | score` → **truy vết** (debug "model dùng đoạn nào" + hiển thị citation cho user tin tưởng). `f"""..."""` = f-string nhiều dòng, `{question}`/`{context_text}` bị thay bằng giá trị thật trước khi gửi Gemini (khác docstring ở chỗ nó được **gán vào biến** = dữ liệu thật, không phải chú thích).
*   **Khi nào KHÔNG dùng / Giới hạn (đo thật trên chatbot-fanpage — 3308 chunks/115 files):**
    *   Grounding chỉ là **rào chắn mềm** — **không thay được retrieval tốt**. Chạy thật: hỏi `verifySignature hoạt động ra sao?` → model **từ chối** dù `webhook.js` CÓ trong index. Rào chắn **vô tội** (gặp context rác thì từ chối thay vì bịa ✅); **thủ phạm là retrieval**. ⇒ câu lý thuyết "retrieval lấy rác thì model ngoan cũng vô dụng" thành sự thật.
    *   **💎 Phát hiện vàng 1 — embedding yếu cross-lingual (nối tiếp Ngày 2–3):** câu hỏi **tiếng Việt** cho điểm CAO HƠN (0.613) nhưng tới các doc **tiếng Việt SAI** (`HUONG_DAN.md`...); chỉ khi hỏi `verifySignature HMAC` (**tiếng Anh**) thì `webhook.js` mới lọt top-3 (0.434). ⇒ MiniLM chấm theo **ngôn ngữ/bề mặt**, không theo **nghĩa**. Điểm tuyệt đối toàn ~0.4–0.6 (thấp). **Số liệu định lượng để nâng cấp MiniLM → Qwen3/BGE-M3 ở Tuần 2 + đo lại precision@3.**
    *   **💎 Phát hiện vàng 2 — chunking xé hàm lồng phá luôn retrieval (nối tiếp Ngày 4):** `verifySignature` là **hàm con thụt lề** trong `createWebhook`. Pattern `.js` neo `(?m)^` (cột 0) → **không bắt** dòng thụt lề → cả `createWebhook` gom thành 1 chunk khổng lồ → **fallback chém cứng 800 ký tự**, xé thân `createHmac/timingSafeEqual` khỏi header `function verifySignature` → embedding nhạt nhòa → **không bao giờ nổi top-K**. ⇒ bug chunking Ngày 4 không chỉ "phá ngữ cảnh khi đọc" mà **phá cả retrieval**. Hướng sửa: regex bắt cả khai báo thụt lề / overlap ~100 ký tự / dùng splitter thư viện.
    *   **2 tầng chunking tách bạch:** Tầng 1 (regex ngữ nghĩa) chỉ xét **khớp pattern**, KHÔNG xét độ dài — dòng thụt lề không bao giờ là ranh giới. Tầng 2 (fallback) mới xét **độ dài** chunk đã chia. Đừng trộn hai tầng.

### Ngày 6: Stress-Test Hallucination & Baseline (đo để Tuần 2 có cái mà so)
*   **Vấn đề là gì?**
    *   Ngày 5 chỉ thấy pipeline chạy *được* trên vài câu lẻ = "demo may mắn", chưa phải bằng chứng. Không có bộ test cố định + con số, thì Tuần 2 nâng MiniLM→Qwen3 mình **không biết tốt lên thật hay chỉ cảm giác**.
    *   Máy tự gắn được nhãn `[TỪ CHỐI]` (vì câu từ chối là chuỗi cố định do CHÍNH MÌNH ra lệnh trong prompt → so khớp ký tự). Nhưng **"đúng/bịa" thì máy KHÔNG tự chấm được**: (1) script không chứa ground-truth máy-so-được; (2) câu trả lời là văn xuôi tự do, "đúng" phải so theo *nghĩa* không phải *chữ* → buộc có người (hoặc LLM-judge) phán. Đây là cầu nối sang bài toán **eval / precision@k / LLM-as-judge** ở Tuần 2.
*   **Giải pháp là gì?**
    *   Soạn **bộ câu hỏi cố định có đáp án biết trước**, cố tình trộn câu *có trong code* (đo recall) + câu *không có* (đo rào chắn từ chối), chạy 1 lượt, ghi 3 con số **đúng/bịa/từ chối** = **baseline** (vạch xuất phát).
    *   **Đo thật (chatbot-fanpage, 10 mẫu — Q5 re-run trên Vertex 23/6):** Bịa = **0/10** (rào chắn vững, không citation giả); Từ chối đúng off-topic = **4/4** (Q8 còn *sửa* tiền-giả-định sai "MongoDB?" → "là PostgreSQL"); Recall in-scope = **2/6 (~33%)**. **Kết luận vàng: generation đã hoàn hảo, nút thắt 100% ở retrieval** — 4 câu trượt (verifySignature, lead parser, RBAC, test framework) đều CÓ trong code nhưng chunk đúng không lọt top-3, khớp y 2 phát hiện vàng Ngày 5. ⚠️ **Q5 lật một bài học:** ghi chú cũ "Q5 retrieval đã trúng" là **giả định SAI** — grep ra `HUONG_DAN.md` không hề chứa vai trò (đáp án ở test/code) → verify nội dung, đừng đoán theo tên file.
    *   Phát hiện thêm: "**chunk nam châm**" `admin/views.js#188` lọt top-3 ở 4 câu khác hẳn nhau → nghi đoạn fallback 800 ký tự mờ nghĩa, hút mọi truy vấn = nhiễu cần xử lý Tuần 2.
*   **Khi nào KHÔNG dùng / Lưu ý vận hành (học từ chính cú crash hôm nay):**
    *   Baseline chỉ đáng đo khi **sắp có thay đổi lớn cần chứng minh** (đúng lúc mình sắp sang Tuần 2). Pipeline còn đổi mỗi ngày thì đo xong số hết hạn ngay.
    *   **🔑 503 vs 429 (tự tay gặp cả hai):** `503 UNAVAILABLE` = server Google quá tải, lỗi CỦA HỌ, transient → **retry backoff** là đúng. `429 RESOURCE_EXHAUSTED` = hết **quota free CỦA MÌNH** (`gemini-3.5-flash` free chỉ **20 req/ngày**), retry ngắn hạn vô ích → đổi model/đợi reset.
    *   **💡 Retry mù đốt quota:** retry-trên-503 ở mẻ 10 câu cộng dồn ~20 request → cháy đúng trần 20/ngày. ⇒ Production phải giới hạn CẢ số lần retry LẪN tổng request/phút (rate limiter), không chỉ bắt lỗi. Đổi `gemini-3.5-flash` → `gemini-2.5-flash-lite` = **bucket quota riêng + rẻ ~15x** ($0.10/$0.40 vs $1.50/$9.00) → đã đổi trong `call_gemini`.
    *   **Robustness transcript:** ghi file SAU MỖI câu (không phải cuối vòng) → crash giữa chừng vẫn giữ tiến độ, khỏi chạy lại tốn quota.

### Ngày 7: Chuyển backend LLM sang Vertex + Bài học vận hành & kiểm chứng
*   **A. Backend AI Studio vs Vertex (cùng một SDK):**
    *   *Vấn đề:* free tier AI Studio chỉ **20 req/ngày** (đã cháy Ngày 6) → chặn học/test/agent loop.
    *   *Giải pháp:* SDK `google-genai` che cả 2 backend sau **cùng API** — chỉ phần `Client()` đổi. `call_gemini` giờ **dual-mode**: env `GOOGLE_GENAI_USE_VERTEXAI=True` (+ `GOOGLE_CLOUD_PROJECT` + `GOOGLE_CLOUD_LOCATION`, auth bằng **ADC** `gcloud auth application-default login`) → Vertex; không thì fallback `GEMINI_API_KEY`. `generate_content` **giữ nguyên** → đây là cái lợi "explicit client" của Ngày 1.
    *   *Khi nào KHÔNG:* prototype 1 lần / tài liệu nhỏ → AI Studio free là đủ, đừng dựng Vertex cho nặng.
*   **B. Bẫy env var (mất 3 lần thử mới ra):**
    *   *Vấn đề:* set env xong chạy vẫn báo "Chưa set backend LLM".
    *   *Giải pháp/Phân biệt:* `$env:FOO` = **session hiện tại**, mất khi đóng · `setx FOO` = **vĩnh viễn nhưng chỉ terminal MỞ MỚI**, không áp cho session đang mở · **VS Code chụp env lúc khởi động** → `setx` + mở tab mới vẫn vô dụng cho tới khi **restart cả VS Code**. Cách chắc: set `$env:` ngay trong session, hoặc `setx` rồi restart VS Code.
    *   *Khi nào KHÔNG:* chỉ là vận hành — nhưng đây là loại bug "môi trường" tốn thời gian nhất, nhớ để khỏi mất buổi.
*   **C. Phương pháp: cô lập biến số + verify, đừng đoán:**
    *   *Vấn đề:* lỗi/đánh giá dễ đổ nhầm nguyên nhân (tưởng lỗi code/máy mình, hoặc tin ghi chú cũ).
    *   *Giải pháp:* (1) **Cô lập** — test ở Cloud Shell (đã pre-auth) trước → biết lỗi ở GCP hay máy local; (2) **Verify ground-truth** — Q5 "không tìm thấy" → grep repo mới lòi ra `HUONG_DAN.md` KHÔNG chứa vai trò (đáp án ở `tests/admin-routes.test.js` + `core/admin/`) → ghi chú "retrieval đã trúng" là **giả định SAI**.
    *   *Khi nào KHÔNG:* với fresher, gần như không có ngoại lệ — luôn verify bằng số/grep thay vì đoán. (= câu chuyện phỏng vấn "tôi tự bắt lỗi đánh giá của chính mình".)

---

## KIẾN THỨC NGOÀI LỀ TRÌNH — TẦNG XỬ LÝ INPUT (Ingestion)
*(Học từ thảo luận: input thị trường thật là PDF/docx/excel/link/ảnh, không phải text thuần. Đây là tầng đứng TRƯỚC RAG.)*

### Tầng Ingestion / Document Routing
*   **Vấn đề là gì?**
    *   Input thực tế đủ loại định dạng (PDF, docx, excel, link, ảnh). Nhét thẳng vào RAG thì hoặc **hỏng** (đọc sai), hoặc **mất dữ liệu** (không trích được chữ). Sản phẩm không thể bắt user "tự chuyển sang .txt".
*   **Giải pháp là gì?**
    *   Một **router phân loại** từng input → gọi đúng parser: `pymupdf`/`pdfplumber` cho PDF text, OCR (PaddleOCR/Tesseract) cho PDF scan & ảnh, `python-docx` cho .docx, `pandas`/`openpyxl` cho .xlsx, `httpx`+`trafilatura` cho link.
    *   Pipeline: `Input → Router → Parser → Text + metadata → Chunk → Embedding → RAG`. **Luôn giữ metadata nguồn** (tên file, số trang, URL) để sau còn trích dẫn (citation) — thứ làm sản phẩm trông "production".
*   **Khi nào KHÔNG dùng?**
    *   Khi input đã là **text thuần** (repo code `.py`/`.md`) thì bỏ qua tầng này cho nhẹ. Core AI Code Auditor giai đoạn đầu chưa cần — để PDF/OCR/Excel thành **"mở rộng giai đoạn 2"** trong CV.
    *   **Excel KHÔNG embedding thẳng**: bảng số liệu nhét vào vector là vô nghĩa (`#1234` ≈ `#5678`) → đẩy sang **structured query** (pandas/SQL), hoặc convert mỗi dòng thành câu mô tả rồi mới embed.

### OCR như một Fallback có điều kiện (per-page, có threshold)
*   **Vấn đề là gì?**
    *   PDF/docx chia 2 loại: **born-digital** (chữ là text thật, ~90% file thực tế) và **scan/ảnh** (chữ là pixel). OCR mặc định mọi file thì vừa **chậm gấp nhiều lần**, vừa **làm bẩn text** born-digital (OCR đọc "l" thành "1").
*   **Giải pháp là gì?**
    *   **Trích text trước**; chỉ trang nào có độ dài text **< ngưỡng (threshold)** mới đẩy qua OCR. Xét **per-page** chứ không xét cả file (1 PDF có thể trộn 48 trang text + 2 trang scan = **hybrid extraction**).
    *   Dùng **ngưỡng**, không so `== ""` cứng — vì trang scan vẫn lẫn rác (số trang, watermark) nên `if len(text.strip()) < threshold: → OCR; else: dùng text luôn`.
*   **Khi nào KHÔNG dùng?**
    *   PDF/docx **born-digital** đã có text số hóa sẵn — KHÔNG OCR.
    *   Công thức trả lời phỏng vấn cho câu này: **Cách làm (threshold) + Tại sao (OCR mặc định chậm & bẩn text) + Đánh đổi** → đủ 3 vế mới là câu trả lời cấp senior.

---

## KIẾN THỨC NGOÀI LỀ TRÌNH — BEYOND RAG (rà bài nghiên cứu 22/6)
*(Kiến thức để NÓI được + định hướng sau CV — chưa tự build. Chi tiết: `docs/beyond-rag-phase-2.md` + roadmap section "Tích Hợp Beyond-RAG (Tầng 1)".)*

### Bản đồ "Beyond RAG" — naive RAG hết hơi ở đâu, đi tiếp bằng gì
*   **Vấn đề là gì?**
    *   Naive RAG (đúng cái tôi đang xây) có 3 điểm chết: (1) không suy luận đa bước; (2) mất ngữ cảnh toàn cục → trả kém câu hỏi tổng quan; (3) bất lực với **dữ liệu có tính liên kết cao** (quan hệ giữa các thực thể). Tôi đã *tự đo* được hệ quả: recall in-scope 33% (sau khi hoàn tất Q5), "chunk nam châm".
*   **Giải pháp là gì? (mỗi cái trị một bệnh)**
    *   **GraphRAG** — dựng đồ thị thực thể-quan hệ; Local search (lân cận 1 thực thể) + Global search (cộng đồng Leiden + tóm tắt). Trị bệnh *dữ liệu liên kết*. Với CODE = call/import graph → dựng bằng **AST cho rẻ**, chỉ LLM tóm tắt.
    *   **RAPTOR** — cây tóm tắt đệ quy (GMM+UMAP). Trị bệnh *câu hỏi toàn cục*.
    *   **CRAG** — chấm độ tin retrieval, sai thì fallback. Trị bệnh *retrieval trả rác* (đúng bệnh của tôi) → đây là món rẻ đã đưa vào Tầng 1.
    *   **Speculative RAG** — drafter nhỏ song song + verifier lớn → nhanh hơn, giảm position bias. Niche, chỉ cần biết.
*   **Khi nào KHÔNG dùng?**
    *   GraphRAG/RAPTOR có **chi phí dựng index cao** (hàng trăm–nghìn lượt LLM). Trên free tier 20 req/ngày (cháy Ngày 6) là bất khả thi — **nhưng từ 22/6 tôi đã chuyển Vertex AI (paid)** nên **quota hết là rào**, codebase nhỏ của tôi build full index chỉ ~$1–3. ⇒ Rào còn lại thuần là **thời gian/thứ tự học** (build nhiều tuần) → vẫn để **v2 sau CV** (hoặc stretch Tuần 8), KHÔNG phải "không build nổi". Dữ liệu không liên kết / không cần câu toàn cục → RAG/hybrid thường vẫn là lựa chọn nhỏ-nhất-chạy-được (kiềm chế).

### Kinh tế học Long-Context vs RAG (câu phỏng vấn "vàng", 0 dòng code)
*   **Vấn đề là gì?**
    *   Có luồng ý kiến "context 1M token rồi, RAG lỗi thời". Cần phản biện được bằng lý do *vật lý/kinh tế*, không cảm tính.
*   **Giải pháp là gì? (vì sao RAG vẫn sống)**
    *   **Prefill nặng:** self-attention ~O(n²) → nạp 1M token đẩy TTFT lên hàng chục giây, không real-time được.
    *   **KV-cache ngốn VRAM:** tăng phi mã theo độ dài × số user đồng thời. ⚠️ **[Chờ kiểm chứng web]** mốc GB cụ thể trong bài.
    *   **Lost in the middle:** model đọc được nhưng suy luận kém với info giữa context dài (nối tiếp ghi chú Ngày 1).
    *   **Bảo mật:** RAG là *màng lọc* Row-Level Security — loại data trái quyền **trước khi** vào prompt; long-context thuần không làm được.
    *   Kiến trúc lai tối ưu: **hybrid retrieval → rerank → long-context generation**; định tuyến **Self-Route** (thử RAG trước) / **Pre-Route** (model nhỏ quyết trước). ⚠️ **[Chờ kiểm chứng web]** "Pre-Route cắt 80% chi phí".
*   **Khi nào KHÔNG dùng (RAG)?**
    *   Tài liệu nhỏ + ít đổi + 1 user → nhồi thẳng long-context đơn giản hơn, khỏi RAG. Đây vẫn là nguyên tắc xuyên suốt từ Ngày 1.

---

## TỔNG KẾT TUẦN & TỰ ĐÁNH GIÁ (Hằng tuần)
*(Mỗi tối Chủ Nhật, hãy dành 10 phút trả lời các câu hỏi tự kiểm tra trong lộ trình chi tiết và ghi điểm số của bạn tại đây)*

*   **Tuần 1:** ... / 10 điểm.
    *   *Điều tôi hiểu rõ nhất:* ...
    *   *Chỗ tôi vẫn còn lúng túng cần xem lại:* ...
