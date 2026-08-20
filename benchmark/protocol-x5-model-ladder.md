# P-X5 — Arm C: model ladder trên cùng harness

**Trạng thái:** đăng ký trước. **Commit file này TRƯỚC trial đầu tiên.**
**Soạn:** 20/08/2026 · **Chưa chạy trial nào tại thời điểm soạn.**

Đây là sửa lỗi quy trình của X4, nơi protocol được soạn trước nhưng commit sau nên
git không chứng minh được thứ tự. Lần này thứ tự được git ghi nhận.

## 0. Pre-registration

Dự đoán của tác giả, nêu ngày 20/08/2026 **sau khi thấy kết quả X4 nhưng trước khi
chạy bất kỳ trial X5 nào**, ghi nguyên văn:

> "đầu tiên thì dự án thua chủ yếu deo model khác nhau cũng như độ thông minh model
> claude sẽ tốt hơn gemini 2.5 lite nhiều nên tôi thấy việc claude thắng là dễ hiểu,
> 2 là claude tôi nghĩ được train do nhiều lập trình viên giỏi cũng như kiến trúc hệ
> thống của họ rất tốt nên có thể dự án hiện tại có phần nào hạn chế claude mà không
> được bung hết sức mình."

Tức là: **khoảng cách X4 chủ yếu do model, không do harness.** X5 kiểm đúng vế một.
(Vế hai — Claude bị bó — là Arm D, một thí nghiệm khác.)

## 1. Câu hỏi nghiên cứu

X4 lẫn hai biến: model (`flash-lite` vs `sonnet`) và harness (3 tool + 10 step vs
Claude Code). Không tách được nguyên nhân.

X5 giữ **harness bất biến tuyệt đối** và chỉ leo thang model:

| Arm | Model | Giá in/out per 1M | Vai trò |
|---|---|---|---|
| baseline-v01 | `gemini-2.5-flash-lite` | $0.10 / $0.40 | đã chạy, recall 26.2% |
| **X5-flash** | `gemini-2.5-flash` | $0.30 / $2.50 | bậc giữa |
| **X5-pro** | `gemini-2.5-pro` | $1.25 / $10.00 | bậc mạnh nhất khả dụng |
| X4 (đối chiếu) | `claude-sonnet-5` + harness khác | — | recall 57.1% |

## 2. Giả thuyết đăng ký trước

| ID | Giả thuyết | Sai khi nào |
|---|---|---|
| **H1** | recall(pro) > recall(flash-lite) = 26.2% | recall(pro) ≤ 26.2% |
| **H2** | Đơn điệu theo sức model: recall(pro) ≥ recall(flash) ≥ recall(lite) | thứ tự đảo |
| **H3** | **Nếu recall(pro) ≥ 50%: khoảng cách X4 chủ yếu do MODEL** — harness 3-tool về cơ bản đủ dùng | recall(pro) < 50% |
| **H4** | **Nếu recall(pro) < 40%: harness là nút thắt**, không phải model | recall(pro) ≥ 40% |
| **H5** | Gradient độ khó vẫn còn: `de` > `vua` > `kho` ở mọi arm | thứ tự đảo hoặc phẳng |

H3 và H4 cố ý chừa vùng xám 40–50%: rơi vào đó thì kết luận là **cả hai cùng đóng
góp**, và phải báo cáo đúng như vậy chứ không được ép về một phía.

## 3. Biến duy nhất được đổi

`agent.py` **không đổi một dòng logic nào**. `MODEL` và `PRICE` được đọc từ biến môi
trường `AUDITOR_MODEL`, nên **hash của `agent.py` giống hệt nhau ở mọi arm** — arm chỉ
khác nhau ở config được ghi vào manifest (`run_manifest.json` field `model`).

Giữ nguyên tuyệt đối: `MAX_STEPS = 10`, `SYSTEM_PROMPT`, 3 tool, `validate_report`,
`MAX_REJECTIONS`, cú chốt `mode='ANY'`, 13 mục checklist, gold, scorer, tolerance ±5,
clean-majority differential.

Bảng `PRICES` phải đúng, vì đổi model mà quên đổi giá là báo cáo số tiền sai.
Model không có trong bảng → `KeyError` ngay lúc khởi động (fail fast, không chạy
tiếp rồi báo cáo tiền bịa).

## 4. Thiết kế

3 clean + 3 spiked trial mỗi arm, xen kẽ — **giống hệt baseline-v01**, cùng snapshot
(`benchmark/snapshots/`), cùng gold, cùng `score_benchmark.py` không sửa.

Thứ tự chạy: **flash trước, pro sau.** Flash rẻ hơn ~4×; nếu đường ống hỏng thì hỏng
ở chỗ rẻ.

## 5. Ngân sách

Ước tính từ baseline ($0.073–0.086/lượt audit với flash-lite), quy đổi theo giá:

| Arm | Ước tính/audit | 6 trial |
|---|---|---|
| X5-flash | ~$0.35 | ~$2.1 |
| X5-pro | ~$1.40 | ~$8.4 |

**Cảnh báo:** `gemini-2.5-pro` là thinking model; `thoughts_token_count` tính giá
output. Chi phí thật có thể cao gấp ~2 lần ước tính. **Trần cứng: $25 tổng.** Chạm
trần thì dừng và báo cáo phần đã chạy.

Khác X4: đây là **tiền mặt thật trên GCP của tác giả**, không phải hạn mức gói.

## 6. Luật quyết định

| Kết quả | Kết luận | Việc tiếp theo |
|---|---|---|
| recall(pro) ≥ 50% | Khoảng cách X4 **do model**. Harness tự viết đủ dùng. | Kết luận mạnh về công trình của tác giả. Dừng tối ưu harness. |
| recall(pro) < 40% | **Harness là nút thắt.** | Biết chính xác phải xây gì: reviewer, nhiều step hơn, tool tốt hơn. |
| 40% ≤ recall(pro) < 50% | Cả hai cùng đóng góp. | Báo cáo đúng vùng xám, không ép về một phía. |
| recall(pro) ≤ 26.2% | Nghi harness/lỗi vận hành trước khi mừng. | Kiểm log, kiểm budget-exhaustion, kiểm 429. |

## 7. Phân loại lỗi khi chạy (bài học X4)

Hai loại hỏng **không được trộn**:

- `max_steps` cạn / validator từ chối hết lượt → **dữ liệu**, tính miss.
- HTTP 429 / 503 / lỗi hạ tầng → **không phải dữ liệu**. Xoá và chạy lại. Đưa vào
  chấm là bịa số.

## 8. Giới hạn

Cùng 15 seed, 1 repo, seed do chính tác giả viết; 3 trial đủ thấy gradient ổn định,
không đủ cho khoảng tin cậy chặt.

Thêm một giới hạn về độ bền của kết quả: **`gemini-2.5-flash-lite` bị Google khai tử
16/10/2026.** Baseline v01 sau ngày đó không tái lập được bằng API. Snapshot, gold,
scorer và raw trial vẫn còn, nhưng con số 26.2% trở thành *dữ liệu lịch sử*, không
phải thí nghiệm chạy lại được. Phải nói điều này khi bảo vệ.

## 9. Đầu ra

`benchmark/results-x5-model-ladder.md` — bảng 4 cột (lite | flash | pro | claude X4)
theo từng metric và từng độ khó.
