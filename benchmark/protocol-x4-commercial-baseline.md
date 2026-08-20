# P-X4 — Commercial agent vs seeded-bug benchmark

**Trạng thái:** DRAFT — phải commit TRƯỚC lần chạy đầu tiên.
**Soạn:** 17/08/2026 · **Chưa chạy trial nào tại thời điểm soạn.**

## 0. Pre-registration (ghi trước khi có bất kỳ dữ liệu nào)

> **Dự đoán của tác giả, 17/08/2026:** *"Tôi nghĩ Claude sẽ thắng thôi."*

Ghi nguyên văn, có ngày. Nếu kết quả đúng như dự đoán → dự đoán được xác nhận.
Nếu sai → **ghi là sai, không sửa dự đoán**. Đây là điểm khác biệt duy nhất giữa
đo lường và kể chuyện sau khi biết đáp án.

## 1. Câu hỏi nghiên cứu

Baseline v01 đo agent tự xây: in-scope recall **26.2%**, FDR **75.4%**, gradient
`de 67% → vua 20% → kho 11%`.

Câu hỏi: **một agent thương mại (Claude Code) đạt bao nhiêu trên CÙNG 15 seed,
CÙNG gold, CÙNG differential clean-vs-spiked?**

Không ai biết con số này — kể cả nhà sản xuất. Đó là lý do thí nghiệm tồn tại.

## 2. Giả thuyết đăng ký trước

| ID | Giả thuyết | Sai khi nào |
|---|---|---|
| **H1** | Claude Code recall > 26.2% | recall ≤ 26.2% |
| **H2** | Gradient độ khó vẫn còn: `recall(de) > recall(vua) > recall(kho)` | thứ tự đảo hoặc phẳng |
| **H3** | **Khoảng cách tập trung ở `de`/`vua`, KHÔNG ở `kho`** — tức công cụ xịn mua được lỗi dễ và vừa, không mua được lỗi ngữ nghĩa liên thủ tục | Claude Code recall(`kho`) ≥ 50% |
| **H4** | FDR của Claude Code < 75.4% (nhiễu thấp hơn) | FDR ≥ 75.4% |

**H3 là giả thuyết đáng giá nhất.** Đúng → kết luận về cả một lớp công cụ, không
phải về đồ chơi của tác giả. Sai → lớp `kho` bị giới hạn bởi model chứ không phải
bởi bài toán, cũng là kết quả thật và phải báo cáo y nguyên.

## 3. Confound — khai TRƯỚC, không giấu

Đây **không** phải so sánh công bằng giữa hai kiến trúc. Khác nhau ở:

- Model (Claude vs `gemini-2.5-flash-lite`)
- Bộ tool (Claude Code nhiều hơn 3 tool `grep`/`read_file`/`list_files`)
- Ngân sách step (agent tự xây khoá cứng `max_steps=10`)
- System prompt / harness / cơ chế retry

**Kết luận được phép rút:** "Agent thương mại X đạt Y% trên benchmark này."
**Kết luận KHÔNG được phép rút:** "Claude tốt hơn kiến trúc của tôi" — chưa cô lập
biến nào cả.

## 4. Thiết kế

- Đối tượng: `benchmark/snapshots/clean` và `benchmark/snapshots/spiked` (192 file
  mỗi bên, không `.git`, không gold, không `benchmark/`).
- Nhiệm vụ: **13 mục checklist**, lấy nguyên văn từ `audit_checklist.json`, một
  phiên MỚI cho mỗi mục — khớp giao thức baseline v01 (trí nhớ sạch, không dính
  distractor mục trước).
- Trial: xen kẽ clean → spiked → clean → spiked… như baseline v01.
- Chấm: `score_benchmark.py` **giữ nguyên**, gold **giữ nguyên**, tolerance ±5,
  clean-majority differential **giữ nguyên**. Không sửa luật chấm sau khi nhìn số.

## 5. Chống rò rỉ đáp án (phần dễ hỏng nhất)

1. Chạy với thư mục làm việc = **thư mục snapshot**, KHÔNG phải repo `ai-code-auditor`.
2. Tuyệt đối không để công cụ nhìn thấy: `golden_findings.json`, `scoring_rules.md`,
   `results-baseline-v01.md`, `STATUS.md`, `NOTES.md` — mọi file này gọi tên seed.
3. Prompt cho clean và spiked phải **giống hệt nhau từng ký tự**. Không được nói
   "code này có lỗi cấy sẵn".
4. Nếu công cụ có bộ nhớ/CLAUDE.md riêng trong snapshot → xoá trước khi chạy.
5. Xác minh sau khi chạy: grep transcript xem có nhắc "seed", "golden", "benchmark"
   không. Có = trial hỏng, huỷ.

## 6. Hợp đồng output — không cần viết adapter

`score_benchmark.py` ăn **một mảng JSON phẳng**; nó bỏ qua mọi trường thừa và
không quan tâm findings đến từ đâu. Bắt công cụ ghi thẳng ra file:

```json
[
  {"file": "core/credentials/page-credentials.js", "line": 105,
   "category": "secret", "evidence": "<nguyên văn 1 dòng>", "severity": "high"}
]
```

Bắt buộc: `file` (đường dẫn tương đối từ gốc snapshot), `line` (số nguyên),
`category` (**phải là category của mục checklist đang chạy**, giống ràng buộc
`build_question()` áp cho agent tự xây). Gộp 13 file kết quả của một trial thành
một mảng duy nhất trước khi chấm.

## 7. Hai giai đoạn — đừng mua cả 3 trial trước khi biết đường ống chạy được

**Giai đoạn 1 — pilot (1 clean + 1 spiked, 26 lượt chạy).**
Mục tiêu: đường ống thông, KHÔNG phải con số. Gate:
- JSON hợp lệ, scorer nuốt được, không lỗi schema.
- 0 dấu hiệu rò rỉ theo mục 5.
- Ít nhất 1 seed được bắt đúng (chứng minh nhiệm vụ khả thi, không phải prompt hỏng).

**Giai đoạn 2 — full (3 clean + 3 spiked, 78 lượt).** Chỉ chạy khi pilot qua gate.
Báo cáo: recall `X/14`, coverage `X/15`, precision, FDR, F1, gradient theo độ khó,
và dao động giữa các trial — đúng bộ metric của baseline v01, không thêm không bớt.

## 8. Luật quyết định

| Kết quả | Nghĩa là | Việc tiếp theo |
|---|---|---|
| H1 ✓, H3 ✓ | Công cụ thương mại mua được lỗi dễ/vừa, **không** mua được lớp `kho` | Kết quả mạnh nhất — thành luận điểm trung tâm của đồ án |
| H1 ✓, H3 ✗ | Lớp `kho` giải được, giới hạn nằm ở model | Cũng là kết quả. Đổi câu hỏi sang: cần gì để agent rẻ đạt tới đó? |
| H1 ✗ | Nghi ngờ harness hỏng trước khi mừng | Kiểm prompt, kiểm parse, kiểm rò rỉ. Không công bố cho tới khi loại trừ bug. |

Kết quả nào cũng đăng. **Không có kịch bản nào "thí nghiệm thất bại"** — tác giả
không phải bên bị chấm điểm, tác giả là bên cầm thước.

## 9. Giới hạn (nói TRƯỚC ở mọi buổi bảo vệ)

15 seed, 1 repo, seed do chính tác giả viết; nhãn độ khó là phán đoán của tác giả,
không phải rubric độc lập; 3 trial đủ thấy gradient ổn định, không đủ cho khoảng
tin cậy chặt; đo phiên bản công cụ tại một thời điểm, không phải kết luận vĩnh viễn.

## 10. Đầu ra

`benchmark/results-x4-commercial-v01.md` — cùng khuôn với `results-baseline-v01.md`,
kèm bảng đối chiếu hai cột (agent tự xây | agent thương mại) theo từng độ khó.
