# Quy Mô Nào Dùng Gì — Chọn Nơi Lưu Vector (list → Chroma → vector DB chuyên dụng)

> Mục đích: trả lời câu phỏng vấn *"khi nào KHÔNG cần vector DB?"* bằng **số thật**, không nói chay.
> Cập nhật: 25/6/2026. Gắn với Ngày 8 (migrate ChromaDB).

---

## 0. Hiểu nhầm phải gỡ trước: đếm CHUNK, không đếm "tài liệu"

Ngưỡng kỹ thuật tính theo **số vector = số chunk**, KHÔNG phải số file/tài liệu.

- 1 tài liệu cắt ra nhiều chunk: **~5–50 chunk/tài liệu** tuỳ độ dài.
- Mỏ neo của chính mình: **115 file → 3308 chunk (~29 chunk/file).**
- Quy đổi nhanh: *số chunk ≈ số tài liệu × (số chunk trung bình mỗi tài liệu).*

→ Khi ai hỏi "50 hay 1000 tài liệu", câu đầu tiên phải hỏi lại: **"mỗi tài liệu dài cỡ nào → ra bao nhiêu chunk?"** (Đây đã là một điểm cộng phỏng vấn: biết hỏi đúng biến số.)

---

## 1. Bảng ngưỡng theo SỐ CHUNK (vector)

> Giả định: vector ~384–1024 chiều, chạy 1 máy, 1 người dùng, cần độ trễ "tương tác" (<~50ms/câu).

| Số chunk (vector) | Tài liệu tương đương* | Nên dùng gì | Vì sao |
|---|---|---|---|
| **< 1.000** | ~20–200 tài liệu | **List Python + numpy brute-force.** (Tài liệu cực nhỏ → có khi nhồi thẳng prompt, khỏi RAG) | Brute-force quét hết vẫn **dưới mili-giây**. Thêm DB chỉ tổ phức tạp. |
| **1.000 – 10.000** | ~200–1.000 tài liệu | List brute-force **vẫn chạy tốt**; bắt đầu thêm **persistence** (Chroma/SQLite lưu đĩa) | Quét hết còn <~10ms. Lưu đĩa để **khỏi embed lại** mỗi lần khởi động. ← *dự án mày (3308) ở đây* |
| **10.000 – 100.000** | ~1.000–10.000 tài liệu | **Vector DB local có HNSW** (Chroma, FAISS, Qdrant, pgvector) | Brute-force bắt đầu **cảm thấy chậm** (10–100ms). HNSW "nhảy-rồi-bò" → ~O(log n) đáng tiền. |
| **100.000 – 10 triệu** | ~10k–500k tài liệu | **Vector DB chuyên dụng** (Qdrant, Milvus, Weaviate, pgvector + index) | ANN **bắt buộc**. Lo thêm RAM, sharding, lọc metadata ở quy mô lớn. |
| **> 10 triệu – 100 triệu+** | hàng triệu tài liệu | **Phân tán / managed** (Milvus, Pinecone, Vespa) + **quantization (PQ)** + sharding | Đây là **bài toán hạ tầng**, không còn là chọn thư viện. Recall 95–99% của ANN cắn thật. |

\* Quy đổi thô ở mức ~10 chunk/tài liệu — đổi theo độ dài tài liệu thật của mày.

---

## 2. NHƯNG số chunk không phải lý do duy nhất — 4 "cò súng" khác

Ngay cả khi data nhỏ (< 10k chunk), vẫn nên lên vector DB nếu dính một trong các yếu tố sau. Đây là phần làm câu trả lời **hết đơn điệu**:

1. **Nhiều người dùng / ghi đồng thời (concurrency):** list Python trong RAM 1 tiến trình không chịu nổi nhiều request ghi-đọc song song → cần DB lo khoá/giao dịch.
2. **Lọc metadata phức tạp:** "chỉ tìm trong file `.py`, repo X, sau ngày Y" → DB làm filter + vector search trong 1 truy vấn; list phải tự code lọc tay.
3. **Vận hành thật (ops):** cần backup, phục hồi sau sự cố, deploy nhiều bản → DB có sẵn; list thì mày tự lo hết.
4. **Hybrid search có sẵn:** nhiều vector DB tích hợp luôn keyword (BM25) + vector → khỏi tự ghép.

→ Nguyên tắc: **chọn theo `max(quy mô, nhu cầu vận hành)`** — cái nào "to" hơn thì cái đó quyết định.

---

## 3. Dự án của mày đứng đâu? (câu trả lời TRUNG THỰC)

**3308 chunk, 1 người dùng, 1 máy** → nằm gọn ô "**list brute-force vẫn dư sức**".

> Sự thật: list Python của Tuần 1 **không hề chậm**. Mình cài ChromaDB để **(a) học pattern production, (b) có persistence khỏi embed lại 3308 chunk, (c) có nền sạch để so sánh** — KHÔNG phải vì list quá tải.

Nói được câu này = mày chứng minh **không over-engineer**, đúng tinh thần "kiềm chế" của Architect. Fresher hay mắc lỗi ngược: thấy chữ "vector DB" sang nên nhét vào cả khi 200 chunk.

---

## 4. Khung trả lời phỏng vấn (3 câu + số neo)

> **(1) Vấn đề:** "Quy mô quyết định bằng **số chunk**, không phải số tài liệu — em đo dự án em **115 file ra 3308 chunk**.
> **(2) Ngưỡng:** Dưới ~**1.000 chunk** thì list + brute-force là đủ, thậm chí khỏi DB; tới ~**10k–100k** brute-force mới chậm nên cần **HNSW**; trên ~**1 triệu** mới cần vector DB phân tán + quantization.
> **(3) Khi nào KHÔNG cần:** Data nhỏ + 1 user như demo của em thì list vẫn nhanh và dễ debug — em thêm Chroma để **học + có persistence**, không vì nó chậm. **NHƯNG** dù data nhỏ mà cần **nhiều user đồng thời / lọc metadata / vận hành thật** thì vẫn nên lên DB — chọn theo cái lớn hơn giữa *quy mô* và *nhu cầu vận hành*."

---

## 5. Cảnh báo: đây là "rule of thumb", không phải luật

Các mốc trên **xê dịch** theo: số chiều vector (768 vs 1536 → chậm gấp đôi), phần cứng (CPU vs GPU, có BLAS không), ngưỡng độ trễ chấp nhận được (chatbot 200ms khác search 10ms), và mức recall cần (đúng tuyệt đối hay 95% là đủ). → Trong phỏng vấn cứ nói **"khoảng"** + nêu biến số phụ thuộc; đừng phán con số cứng như đinh đóng cột.
