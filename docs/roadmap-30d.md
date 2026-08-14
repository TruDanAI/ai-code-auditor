# Roadmap Thực Thi 30 Ngày — 18/07 đến 16/08/2026

> Đây là **execution overlay** tính từ trạng thái thật ngày 18/07/2026. Nó không
> thay thế giáo trình `lo-trinh-chi-tiet.md`; giáo trình giữ kiến thức và lịch sử,
> còn file này điều phối deliverable phía trước.

## Định vị

**Applied AI Engineer — LLM/RAG Evaluation & Agent Reliability | Python, API
Integration, FastAPI, Vertex AI.**

Portfolio trung tâm: AI Code Auditor xuất findings có bằng chứng và được đánh
giá bằng benchmark clean-vs-spiked có thể tái lập.

## Nguyên tắc khóa

- Benchmark và failure evidence quyết định thứ tự kỹ thuật.
- Deterministic verifier trước LLM judge.
- Single-agent là baseline; Reviewer/LangGraph phải thắng ablation mới được ship.
- Python/API/test/CI là lõi nghề nghiệp; MCP/UI là integration/polish có timebox.
- Báo raw count cùng phần trăm vì benchmark nhỏ.
- Không sửa scoring rule lặng lẽ sau khi nhìn kết quả.

## Phase 1 — Benchmark integrity và baseline (18–24/07)

### Deliverables

- [ ] Đóng băng protocol vào Git với ghi chú trung thực: freeze sau 7/15 mutation,
      trước lần chạy benchmark auditor đầu tiên.
- [ ] Hoàn thành 15/15 mutation, mỗi mutation một commit và một validity check.
- [ ] Sinh `final_line` từ anchor trên snapshot cuối; anchor phải duy nhất trong scope.
- [ ] Xuất snapshot `clean` và `spiked` không `.git`, gold hoặc benchmark metadata.
- [x] Scaffold `finalize_gold.py`, `benchmark_runner.py` và manifest có code/input hash;
      runner mặc định dry-run, chưa gọi LLM.
- [x] `score_benchmark.py` chấm file + line ±5 + category, một gold tối đa một TP,
      clean-majority differential và metric in-scope/OOC tách biệt.
- [x] 9 offline unit tests cho runner/finalizer/scorer; citation validator cũ 6/6.
- [ ] Chạy ít nhất 3 trial/snapshot và giữ raw result từng trial.

### Báo cáo bắt buộc

- In-scope Recall `X/14`.
- End-to-end Coverage `X/15`.
- Precision, FDR và F1.
- OOS count riêng.
- Cost, latency, steps và khoảng dao động giữa trial.
- Kết quả theo category/difficulty và failure samples.

### Gate

Một lệnh tái tạo được run manifest và raw results; scorer tests pass; không có
gold leakage. Chưa qua gate thì không bắt đầu Reviewer/LangGraph.

## Phase 2 — Agent/evaluator reliability (25–31/07)

### Deliverables

- [ ] Failure taxonomy: checklist-gap, agent-miss, tool misuse, evidence miss,
      grader error, duplicate, budget exhaustion, harness/provider error.
- [ ] Trajectory metrics: schema success, duplicate-call rate, read-after-grep,
      invalid submit, steps/TP, cost/TP, retry/timeout rate.
- [ ] Human review mù cho mẫu findings; confusion matrix và agreement với judge.
- [ ] Code grader cho phần deterministic; LLM judge chỉ cho absence/actionability.
- [ ] Ablation cùng benchmark: baseline vs adversarial Reviewer.
- [ ] Eligible findings có empirical test/PoC thay vì chỉ dựa vào đồng thuận LLM.
- [ ] Failure quan trọng được chuyển thành pytest regression.

### Gate

Chỉ giữ Reviewer nếu F1 cải thiện mà recall không giảm quá ngưỡng được ghi trước
khi chạy. Chỉ bọc LangGraph nếu cần state/conditional retry thật; không viết lại
`run_agent()` để đổi framework.

## Phase 3 — Production Python/API (01–07/08)

### Deliverables

- [ ] Package hóa `src/auditor/` với tools, schemas, validators, evaluators,
      providers và API tách biệt.
- [ ] Pydantic models và type hints cho input/report/result.
- [ ] FastAPI tối thiểu: tạo audit và lấy kết quả audit.
- [ ] Test doubles/fake LLM; unit tests không gọi API trả phí.
- [ ] Docker/Compose, `.env.example`, fail-fast config và không hardcode secrets.
- [ ] CI: lint/type/unit tests + smoke eval 2–3 seed; full benchmark manual/nightly.
- [ ] Trace model/tool/token/cost/latency bằng Phoenix nếu hoàn tất trong timebox;
      nếu không giữ JSONL và sinh biểu đồ từ log.

### Gate

Máy mới chạy được theo README; API contract có test; CI xanh; lỗi một audit không
làm mất kết quả audit khác.

## Phase 4 — External proof và thị trường (08–16/08)

### Deliverables

- [ ] Chạy trên NodeGoat/OWASP subset có ground truth bên thứ ba.
- [ ] Chạy trên ít nhất một repo clean/patched để đo noise.
- [ ] README tiếng Anh: methodology, leakage controls, metrics, cost, limitations.
- [ ] Sơ đồ kiến trúc và demo 2–3 phút.
- [ ] Một case study kỹ thuật dựa trên failure thật.
- [ ] CV headline/bullets dùng số thật, không điền số kỳ vọng.
- [ ] Bắt đầu 5–10 hồ sơ được chỉnh theo JD mỗi tuần và mock interview.
- [ ] MCP/FastMCP hoặc UI chỉ làm khi core gate đã qua và timebox không làm trễ CV.

### Gate

Người lạ có thể hiểu, chạy và kiểm chứng phần cốt lõi của dự án; có ít nhất một
số benchmark nội bộ, một external validation và một câu chuyện failed experiment.

## Nhịp học mỗi tuần

- 70% build/eval trong dự án chính.
- 20% Python/API/testing/statistics đúng phần milestone đang cần.
- 10% English, teach-back, README/CV.

Mỗi tuần: một số benchmark, một Failure Museum entry, một mock interview và một
review độc lập. DSA duy trì; AWS, memory, GraphRAG/RAPTOR và demo #2 để sau CV nếu
không có JD hoặc evidence buộc phải ưu tiên.

## Thứ tự cắt khi trễ

1. UI/deploy public URL.
2. MCP demo.
3. Phoenix (giữ JSONL).
4. LangGraph wrapper nếu single-agent + reviewer function đủ.
5. Model/provider ablation phụ.

Không cắt: benchmark protocol, raw trials, scorer tests, Docker reproducibility,
README metrics/limitations và external validation tối thiểu.
