# STATUS — AI Code Auditor

**Cập nhật:** 18/07/2026  
**Milestone:** Phase 1 — Seeded-bug benchmark integrity và baseline  
**Chế độ mặc định hiện tại:** MENTOR MODE cho mutation có bài học; BUILD MODE cho
scorer/runner/test cơ học sau khi contract đã được giải thích.

## Trạng thái đã kiểm chứng

- Commit dự án gần nhất: `525111a` — Day 23 batch orchestrator.
- Auditor v1 đã chạy 13/13 checklist item thành công trên repo gốc.
- Chi phí audit sạch đã quan sát khoảng `$0.05`; tổng vòng debug trong ngày khoảng
  `$0.0992`. Đây là số lịch sử, không mặc định là giá mọi lần chạy.
- `benchmark/scoring_rules.md` và `benchmark/golden_findings.json` tồn tại nhưng
  thư mục `benchmark/` đang **untracked** trong `ai-code-auditor`.
- Repo `chatbot-fanpage-spiked`, branch `spiked`, có 7 mutation commit sau base
  `c0fa0d6`; HEAD hiện tại `fd42d29`.
- Gold hiện có 7/15 record; tất cả `final_line` còn `null` đúng thiết kế cho tới
  khi hoàn thành snapshot cuối.
- Chưa ghi nhận lần chạy auditor benchmark clean-vs-spiked nào.
- Offline Phase 1 scaffold đã có: dry-run-by-default runner, anchor-based gold
  finalizer, deterministic scorer, majority-clean differential và telemetry manifest.
- Kiểm chứng 18/07: 9/9 benchmark unit tests pass; citation validator cũ vẫn 6/6;
  `py_compile` pass và chưa có LLM/API call nào từ benchmark tooling.

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
