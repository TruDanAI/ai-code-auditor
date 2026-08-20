# experiments/ — bài học RAG tuần 1–2, KHÔNG thuộc auditor

Đây là code học, không phải sản phẩm. **Auditor (`agent.py`, `audit.py`,
`benchmark/`) không import bất kỳ file nào trong này.**

Auditor định vị code bằng `grep` + `read_file` (tất định), **không** dùng
chunk/embedding/vector search. Đó là quyết định kiến trúc, không phải thiếu sót:
bug không nằm ở chỗ "giống câu hỏi về mặt ngữ nghĩa" — `grep 'createHmac'` ra
chính xác, embedding chỉ ra thứ na ná (đo được: `#1234` vs `#5678` cosine ~0.98).
Xem `STATUS.md` → "Retrieval không tối ưu tiếp nếu benchmark chưa chỉ ra
retrieval là bottleneck."

| File | Sinh ra bằng chứng gì |
|---|---|
| `mini_rag.py` | Pipeline RAG viết tay: chunk → embed → cosine → top-k → prompt |
| `test_token.py` | Tiếng Việt tốn ~2× token so với tiếng Anh (tiktoken) |
| `test_embedding.py`, `test_cosine.py` | `all-MiniLM-L6-v2` yếu đa ngữ: VI vs EN cùng nghĩa = **0.2669** |
| `test_chunking.py` | Kiểm `chunk_text` |
| `chroma_rag.py` | Thay cosine thủ công bằng vector store |
| `eval_set.py` | Golden set + precision@3 — kỷ luật eval, tổ tiên của `benchmark/` |
| `stress_test.py` | Đo pipeline khi corpus lớn dần |

Chạy **từ trong thư mục này** (chúng import lẫn nhau theo đường dẫn cùng cấp):

```powershell
cd experiments
python test_token.py
```
