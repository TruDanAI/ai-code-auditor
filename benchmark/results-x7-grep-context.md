# X7 — Kết quả: `grep --context` làm auditor **tệ đi**. Phản chứng đăng ký trước đã kích hoạt.

Chạy 23/08/2026. Protocol `28ac847`/`7711172`, commit **trước** trial đầu tiên.
6/6 trial hoàn tất, **$1,9538 / trần $3,00**, chốt chi không phải kích hoạt.

## Phán quyết theo giả thuyết đã đăng ký

| ID | Phát biểu | Ngưỡng | Kết quả | |
|---|---|---|---|---|
| H7.1 | recall x7 > x5-flash | KTC tách khỏi 0 | 45,2% → **35,7%** (giảm) | ❌ |
| H7.2 | recall nhóm `kho` tăng | ≥ 25% | 27,8% → **16,7%** (giảm) | ❌ |
| H7.3 | mở khoá seed mù | ≥1 seed ở ≥2/3 trial | **0/4** | ❌ |
| H7.4 | *phản chứng*: tool đánh đổi | precision giảm > 10 điểm | **giảm 29,7 điểm** | ⚠️ **KÍCH HOẠT** |
| H7.5 | harness thắng model | recall ≥ 54,8% | 35,7% | ❌ |

## Số

| | x5-flash | x7-context | Δ |
|---|---|---|---|
| recall in-scope | 45,2% | **35,7%** | −9,5 |
| KTC 95% recall | 21,4 – 69,0% | 14,3 – 57,1% | |
| precision in-scope | 59,3% | **29,6%** | **−29,7** |
| KTC 95% precision | 50,0 – 77,8% | 23,8 – 35,7% | **không giao nhau** |
| FP mỗi trial | 2 / 7 / 5 | **9 / 16 / 12** | |
| finding thô mỗi trial | 11 / 14 / 12 | 14 / 22 / 17 | |
| prompt token mỗi lượt gọi | 5.605 | **7.344** | **+31%** |

## Được tuyên bố / không được tuyên bố

**Tuyên bố được — precision tụt.** Hai KTC **không giao nhau**, và mức tụt 29,7 điểm
là **~3× sàn nhiễu 10,7 điểm** đã đo ở X6. Vượt xa nhiễu.

**KHÔNG tuyên bố được — recall tụt.** Delta có cặp `x5-flash − x7` = +9,6 điểm,
KTC 95% **+0,0 – +23,8 → chứa 0**. Và cỡ hiệu ứng tối thiểu đã khoá trước khi chạy là
**≥12 điểm**; 9,5 < 12. Theo đúng luật tự đặt: **không tuyên bố.** Chỉ được nói
"không có bằng chứng tool cải thiện recall", không được nói "tool làm giảm recall".

## Cơ chế — vì sao tệ đi

Agent **có** dùng tham số: prompt token mỗi lượt gọi tăng 31% trong khi số lượt gọi
gần như y nguyên (91,3 → 92,3). Chỉ grep đổi, nên phần phình đó là output grep.

Ngân sách `max_steps=10` **cố định**. Kết quả grep to hơn một phần ba đã **chiếm chỗ**
của việc điều tra: agent nộp nhiều finding hơn (14→22) nhưng nông hơn.

Bằng chứng rõ nhất nằm ở ma trận seed: x7 bắt **đúng 5 seed, giống hệt nhau ở cả 3
trial, phương sai bằng 0** — đúng 5 seed dễ nhất mà mọi arm đều bắt được. Nó **đánh
mất** `AUTH-02`, `INP-01`, `REL-01` — những seed `vua`/`kho` mà x5-flash thỉnh thoảng
bắt được bằng cách đọc có chủ đích.

> Ngữ cảnh thêm vào không giúp model **suy luận về cái vắng mặt**. Nó chỉ cho model
> thêm bề mặt để **khớp mẫu**, nên model nộp nhiều phỏng đoán nông hơn và bỏ mất
> những chỗ trước đây nó chịu khó đọc kỹ.

Giả thuyết ban đầu — "trần nằm ở harness, không ở model" — **bị bác**. Ở kích thước
ngữ cảnh và ngân sách bước này, cho thêm ngữ cảnh là **đánh đổi xấu**.

## Sự cố

`clean-trial-03/SEC-01`: `RemoteProtocolError: Server disconnected`. §7 phân loại
**hạ tầng, không phải dữ liệu**. Đã loại trừ khả năng nó gây ra kết quả: FP bùng lên
ở `admin-routes.js [auth]`, `webhook.js [input]`, `lead-parser.js` — không liên quan
mục `SEC-01`; và consensus của x7 (4 mục) còn **lớn hơn** x5-flash (3 mục), tức
baseline không bị hụt.

## Hạn chế phải ghi vào luận văn

1. **`agent_log.jsonl` chỉ ghi TÊN tool, không ghi THAM SỐ.** Việc agent có dùng
   `context` hay không được suy ra từ khối lượng token, **không** đọc thẳng từ log.
   Suy luận này mạnh nhưng là gián tiếp. → phải ghi tham số tool vào log (bài học
   lấy từ DeepSeek Harness: ghi cả điểm inject context, không chỉ tool call).
2. Cap output của tool (`per_file=3`, `line_budget=160`) chọn khi tác giả đã biết tập
   seed — xem mục Hạn chế trong `protocol-x7-grep-context.md`.
3. Chỉ thử **một** cấu hình context. Không loại trừ khả năng `context=1` kèm
   `max_steps` cao hơn cho kết quả khác. Chưa đo thì không nói.
