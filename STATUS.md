# STATUS — AI Code Auditor

**Cập nhật:** 17/08/2026  
**Milestone:** X6 — Ablation validator ĐÃ CHẠY. Claim "harness → precision" đã được đính chính.  
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

## X6 — Ablation `validate_report` (21/08/2026)

Chi tiết: `benchmark/results-x6-validator-ablation.md`. Protocol `8792ae4` commit
01:08:23, **trước trial đầu tiên** (arm ON khởi động 01:09:12).

| Metric | ON | OFF | Δ |
|---|---|---|---|
| recall | 47.6% | 42.9% | −4,7 |
| precision | 50.4% | 43.6% | −6,8 |
| **finding bịa** | **0.0%** (0/145) | **5.2%** (4/77) | **+5,2** |

- **H2 KHÔNG kích hoạt** (cần ≥10 điểm, thực tế 6,8) → rơi vùng xám: cổng đóng góp
  **một phần**, không phải nguyên nhân chính. H5 kích hoạt. H1, H4 đúng.
- **Sàn nhiễu lớn hơn hiệu ứng.** Chạy lại control thay vì tái dùng X5-flash cho thấy
  cùng hành vi code lệch **10,7 điểm** precision giữa hai lần chạy (61.1 → 50.4).
  Hiệu ứng 6,8 < nhiễu 10,7 → **không được tuyên bố**. Ngưỡng H2 đăng ký khi chưa
  biết sàn nhiễu; giữ nguyên, ghi nhận là lỗi thiết kế của protocol.
- **Cổng chỉ nổ 7/78 lượt (~9%)** — 5 đội ngược + 2 chặn "chưa read_file". Một cổng
  nổ 9% không thể là động lực chính của metric.
- **Trần của cổng có số:** `x6-on/clean-trial-03` nộp 75 finding, **70 cái cùng
  `auth` trong một file, trên snapshot SẠCH**, và **qua hết** validator vì dòng có
  thật + evidence khớp. Cổng bảo đảm trích dẫn có thật, KHÔNG bảo đảm finding có nghĩa.

**ĐÍNH CHÍNH — cách nói đúng từ đây:**

| Claim | Trạng thái |
|---|---|
| Validator đẩy metric precision lên | ❌ không chứng minh được ở n=3 |
| Validator đưa trích dẫn bịa về 0 | ✅ đo được cơ học, 5.2% → 0.0% |

> `validate_report` là **bảo đảm tính có thật của trích dẫn**, không phải máy nâng
> precision. Nó xoá một *lớp lỗi*, không cải thiện *phán đoán*.

Sự cố: arm OFF lần 1 bị giết từ bên ngoài lúc 03:39 → §7 phân loại **hạ tầng, không
phải dữ liệu**, giữ lại `x6-off-aborted-01` (không chấm), chạy lại. Tổng $3.5629/$8.

## X5 — Model ladder, harness bất biến (20/08/2026)

Chi tiết: `benchmark/results-x5-model-ladder.md`. Protocol `4f74da5` commit 11:56:10,
**trước trial đầu tiên** — git chứng minh được thứ tự (sửa lỗi quy trình của X4).

| Metric | lite | flash | pro | Claude X4 |
|---|---|---|---|---|
| recall | 26.2% | 45.2% | **54.8%** | 57.1% |
| precision | 24.6% | **61.1%** | 53.8% | 52.4% |
| FDR | 75.4% | **38.9%** | 46.2% | 47.6% |
| $/audit | $0.08 | $0.26 | $1.59 | $6.43 |

- **H3 kích hoạt** (recall(pro) ≥ 50%): khoảng cách X4 **chủ yếu do MODEL**. Harness
  3-tool + validator **không phải nút thắt**. Dự đoán đăng ký trước của tác giả đúng.
- `agent.py`+pro cách Claude Code **2,3 điểm** ở chi phí **thấp hơn 4×**.
- `agent.py`+pro bắt được **SEED-REL-01** mà Claude Code trượt cả 3 trial (union 9/14 vs 8/14).
- **Precision đạt đỉnh ở `flash` rồi TỤT ở `pro`** (61.1 → 53.8). Model mạnh hơn tìm
  nhiều hơn nhưng ồn hơn. `flash` là điểm ngọt hiệu quả: F1 51.4% ở $0.26.
- 5 seed không arm nào bắt: AUTH-01, CRY-01, INP-02 (lỗ hổng checklist), **CFG-01 và
  DOC-01 là `vua`** — chúng kháng vì đòi phát hiện **SỰ VẮNG MẶT**, một nhánh riêng
  trong failure taxonomy, không phải vì độ khó suy luận.

**Phân rã:** model → recall (đo được). Vế "harness → precision" ĐÃ BỊ X6 tách đôi
và đính chính — xem mục X6 bên dưới. KHÔNG dùng lại câu cũ.

**Thay đổi code:** `agent.py` `MODEL`/`PRICE` đọc từ env `AUDITOR_MODEL`; hash code
giống hệt qua mọi arm; model lạ → `KeyError` lúc import (fail fast trên báo cáo tiền).

## X4 — Claude Code trên cùng benchmark (17/08/2026)

Chi tiết: `benchmark/results-x4-commercial-v01.md`. Protocol: `benchmark/protocol-x4-commercial-baseline.md`.

- 3 clean + 3 spiked trial, `claude-sonnet-5` qua `claude -p` headless, cwd = bản sao
  snapshot ở thư mục trung lập (không CLAUDE.md cha, không `.git`, không gold).
- Scorer + gold **KHÔNG sửa** (`git status` sạch trước khi chấm).
- **Recall 57.1% (8/14), precision 52.4%, FDR 47.6%, F1 54.6%** — giống hệt ở cả 3 trial.
- Gradient: `de` **100%** → `vua` **60%** → `kho` **33%**. Agent repo: 67 → 20 → 11.
- Chi phí $6.43/lượt audit vs $0.08 của agent repo = **80×**. Recall/đô: agent repo thắng 37×.
- SEED-AUTH-02: agent repo MISS (flag cả trên clean), Claude HIT (không có trong clean
  consensus). Cùng seed, cùng luật chấm, hai phán quyết ngược — bằng chứng mạnh nhất
  cho việc differential đáng tồn tại.
- 9/78 lượt Claude bị cắt bởi trần `--max-budget-usd 0.80`; 16 lượt dính HTTP 429 đã bị
  **xoá và chạy lại**, không đưa vào chấm (429 = hạ tầng từ chối, không phải phép đo).

### Integrity note cho X4

Protocol X4 được soạn TRƯỚC trial đầu tiên nhưng **commit SAU**. Git không chứng minh
được thứ tự. Mô tả trung thực: "authored before the first trial; committed after."
KHÔNG gọi là full pre-registration.

### Giới hạn quan trọng của X4

Claude bị bó còn 3 tool đọc (`Read`/`Grep`/`Glob`) + trần $0.80/mục, không Bash,
không subagent, không skills, phiên mới mỗi mục. **57.1% là SÀN, không phải trần.**
Kết quả `kho` có thể là hiện vật của ràng buộc chứ chưa chắc là thuộc tính của lớp lỗi.

### Nhánh tiếp theo (chưa chạy, phải đăng ký trước)

- **Arm C** — `agent.py` giữ nguyên, chỉ đổi `MODEL` sang model mạnh. Tách biến model
  khỏi biến harness. Ưu tiên làm trước: rẻ, và nó đánh giá CÔNG TRÌNH CỦA MÌNH.
- **Arm D** — Claude Code thả hết xích (full tool, không trần, opus). Đo trần thật.

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
