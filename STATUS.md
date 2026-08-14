# STATUS — AI Code Auditor

**Cập nhật:** 14/08/2026  
**Milestone:** Phase 1 — Baseline benchmark run ĐÃ CHẠY (X1 signal test hoàn tất)  
**Chế độ mặc định hiện tại:** MENTOR MODE cho mutation có bài học; BUILD MODE cho
scorer/runner/test cơ học sau khi contract đã được giải thích.

## Trạng thái đã kiểm chứng (14/08/2026)

- Commit `ai-code-auditor` gần nhất: gold finalized (188 dòng) sau
  `66fdeaf` (freeze 15/15). `benchmark/` GIỜ ĐÃ được track trong git.
- **15/15 mutation đã cấy xong** trên `chatbot-fanpage-spiked` branch `spiked`
  (HEAD `c255f13`). 3 seed cuối (DOC-01, OOC-01, DEP-01) mỗi seed 1 commit + 1
  validity check bằng code thật.
- Gold `final_line` đã resolve cơ học từ snapshot cuối (0 null); `line_status =
  resolved_from_final_spiked_snapshot`. Anchor mỗi seed unique-in-scope.
- Snapshot clean/spiked export sạch: KHÔNG `.git`, KHÔNG `benchmark/`, KHÔNG gold
  (192 file mỗi bên, hash phân biệt).
- **Baseline benchmark run ĐẦU TIÊN đã chạy** (`benchmark/runs/baseline-v01/`):
  3 clean + 3 spiked trial, interleaved. Model `gemini-2.5-flash-lite`,
  max_steps 10. Tổng chi phí `$0.475` (dưới guardrail `$2`).
- **Kết quả (raw, xem `benchmark/results-baseline-v01.md`):**
  - In-scope recall mean **26.2%** (min 21.4% = 3/14, max 28.6% = 4/14).
  - End-to-end coverage mean **24.4%** (3–4/15).
  - In-scope precision mean **24.6%**; FDR mean **75.4%**.
  - F1 mean **24.2%**.
  - **Difficulty gradient (đây là phát hiện chính):** de **67%** → vua **20%**
    → kho **11%**. Agent bắt lỗi grep-able, sập ở lỗi ngữ nghĩa/liên thủ tục.
  - 8/15 seed KHÔNG BAO GIỜ bắt được — gần hết là `kho`.
- Differential hoạt động đúng: `session.js:55` [auth] bị flag ở 3/3 CLEAN trial =
  noise nền, bị loại. AUTH-02 (đúng line 169) cũng bị flag ở clean (2/3) → tính
  MISS đúng, không ăn điểm may. Đây là bằng chứng mạnh nhất vì sao cần clean-vs-spiked.
- Offline tests vẫn xanh: 9/9 benchmark unit tests, citation validator 6/6.

## Quyết định X1 (theo P-X1 acceptance #7)

**CONTINUE.** Benchmark tái lập được, cho signal ổn định (gradient độ khó nhất quán
giữa các trial), và sinh failure taxonomy giàu. Đủ điều kiện đi Phase 2. KHÔNG phải
vì auditor tốt — recall 26% là thấp — mà vì phép ĐO đáng tin và câu chuyện thất bại
rõ. Đây đúng là mục tiêu X1: đo reproducibility + interpretability, không phải chứng
minh auditor giỏi.

## Integrity note

Không gọi protocol hiện tại là full pre-registration trước mọi mutation. Git
không chứng minh điều đó vì benchmark chưa được track sau 7 mutation. Cách mô tả
trung thực từ đây:

> Protocol v0.1 frozen after 7/15 mutations and before the first auditor
> benchmark run. No benchmark outcomes had been observed at freeze time.

Mọi thay đổi luật sau mốc commit đầu tiên phải vào mục Amendment có ngày, lý do
và ảnh hưởng dự kiến trước khi chạy tiếp.

## Ba hành động tiếp theo

1. Review diff tài liệu/protocol, sau đó người dùng commit protocol freeze vào
   `ai-code-auditor` trước khi cấy mutation thứ 8.
2. Thiết kế và cấy SEED 8–15, mỗi seed một bệnh, một commit, một validity check.
3. Sau 15/15: export snapshot không `.git`, dry-run `finalize_gold.py` và
   `benchmark_runner.py`, rồi mới cho phép `--write`/`--execute`.

## Definition of done cho Phase 1

- 15 mutation hợp lệ và map đúng checklist/category.
- Protocol/gold có lịch sử Git trung thực.
- Clean/spiked snapshot không leakage.
- Runner/scorer có unit tests không tốn API.
- Ít nhất 3 raw trial mỗi snapshot.
- Báo `X/14`, `X/15`, Precision, FDR, F1, OOS, cost, latency và variance.

## Quyết định đang khóa

- Findings report, không quay lại sản phẩm Q&A.
- Retrieval không tối ưu tiếp nếu benchmark chưa chỉ ra retrieval là bottleneck.
- Deterministic verifier trước judge.
- Reviewer/LangGraph là ablation có điều kiện, không phải deliverable mặc định.
- Scoring rules là nguồn sự thật cho metric; dùng FDR, không gọi nhầm là FPR.

## Blocker/rủi ro

- Rủi ro lớn nhất hiện tại là tiếp tục cấy lỗi trước khi protocol freeze có commit.
- Agent gọi Vertex tốn tiền và phi tất định; runner/scorer phải test offline trước.
- Golden anchors phải được kiểm tra uniqueness trong đúng function scope, không
  dùng tìm kiếm toàn file mù khi anchor lặp.
