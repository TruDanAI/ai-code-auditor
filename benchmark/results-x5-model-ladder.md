# X5 model ladder — harness bất biến, chỉ đổi model

**Ngày chạy:** 20/08/2026 · **Protocol:** `protocol-x5-model-ladder.md`
(commit `4f74da5`, **11:56:10 — trước trial đầu tiên**, git chứng minh được thứ tự)

Cùng 15 seed, cùng gold, cùng snapshot, tolerance ±5, clean-majority differential.
`agent.py` **không đổi một dòng logic**; `MODEL` đọc từ env nên hash code giống hệt
nhau ở cả ba arm. Raw trials được giữ nguyên; bảng metric được tái chấm bằng scorer
hiện tại sau các amendment baseline 22–23/08.

## Kết quả

| Metric | lite (baseline) | flash | **pro** | Claude Code (X4) |
|---|---|---|---|---|
| In-scope recall | 26.2% | 45.2% | **54.8%** | 57.1% |
| In-scope precision | 24.6% | **59.3%** | 50.1% | 50.1% |
| In-scope FDR | 75.4% | **40.7%** | 49.9% | 49.9% |
| F1 | 24.2% | 50.8% | 51.5% | 53.4% |
| $/lượt audit | $0.08 | $0.26 | $1.59 | $6.43 |
| Recall trên mỗi đô | **328 %/$** | 174 %/$ | 34 %/$ | 8.9 %/$ |
| Seed bắt được (union 3 trial) | — | 8/14 | **9/14** | 8/14 |

Chi phí thật: flash $1.56 · pro $9.56 (trần đăng ký trước $25).

## Phán quyết giả thuyết

| ID | Giả thuyết | Kết quả |
|---|---|---|
| **H1** | recall(pro) > 26.2% | ✅ 54.8% |
| **H2** | Đơn điệu theo sức model | ✅ 26.2 → 45.2 → 54.8, không đảo bậc nào |
| **H3** | recall(pro) ≥ 50% → **khoảng cách X4 do MODEL**, harness đủ dùng | ✅ **54.8% — kích hoạt** |
| **H4** | recall(pro) < 40% → harness là nút thắt | ✗ không kích hoạt |
| **H5** | Gradient `de` > `vua` > `kho` còn nguyên | ✅ mọi arm |

**Decision rule H3 đăng ký trước đã kích hoạt.** Đây là bằng chứng về độ nhạy theo
model trong cùng harness, không phải phép cô lập nguyên nhân của chênh lệch với X4.

## Ba phát hiện

### 1. Harness tự viết đạt ngang agent thương mại

`agent.py` + `gemini-2.5-pro` đạt **54.8%**, so với Claude Code **57.1%** — cách nhau
**2,3 điểm**, ở chi phí **thấp hơn 4 lần** ($1.59 vs $6.43).

Ba tool (`grep`/`read_file`/`list_files`), `max_steps=10` và validator được giữ nguyên,
nên X5 cô lập được biến model **trong harness của tác giả**. Nó không chứng minh harness
không phải nút thắt khi so với X4, vì X4 khác nhiều trục ngoài model.

### 2. `pro` bắt được một seed Claude Code chưa từng bắt

**SEED-REL-01** (`kho`, reliability — bỏ idempotency guard → gửi trùng tin nhắn).
Claude Code trượt nó ở cả 3 trial; `agent.py`+pro bắt được ở trial 3.

Union: pro **9/14**, Claude **8/14**. Agent rẻ hơn 4 lần không chỉ ngang bằng — nó
tìm thấy một lỗi mà agent thương mại bỏ sót.

### 3. Precision **không** tăng theo sức model — nó đạt đỉnh ở `flash`

```
precision:  24.6%  →  59.3%  →  50.1%
              lite     flash     pro
```

`flash` có precision **cao nhất trong cả bốn arm**, kể cả cao hơn Claude Code
(59.3% vs 50.1%), và FDR thấp nhất (40.7%).

`pro` mua thêm 9,6 điểm recall bằng **6 lần chi phí** và **mất 9,2 điểm precision**.
Model mạnh hơn tìm được nhiều hơn, nhưng cũng ồn hơn.

→ **`flash` là điểm ngọt về hiệu quả.** Nếu tối ưu F1 trên mỗi đô, không có arm nào
gần nó: F1 50.8% ở $0.26.

## Năm seed không arm nào bắt được

| Seed | Diff | Category | Vì sao kháng |
|---|---|---|---|
| SEED-AUTH-01 | kho | auth | route ghi tái dùng quyền ĐỌC — ngữ nghĩa quyền liên file |
| SEED-CRY-01 | kho | crypto | AES-GCM trả plaintext trước khi `final()` xác thực tag |
| SEED-INP-02 | kho | input | stored XSS ở `views.js` — **checklist chỉ trỏ vào `webhook.js`** (lỗ hổng checklist, không phải lỗi agent) |
| SEED-CFG-01 | **vua** | config | bỏ một yêu cầu env fail-fast — **phát hiện SỰ VẮNG MẶT** |
| SEED-DOC-01 | **vua** | doc-mismatch | doc và code lệch nhau |

Hai seed cuối là `vua`, không phải `kho` — chúng kháng vì **lý do khác với độ khó suy
luận**. `CFG-01` đòi agent nhận ra *thứ lẽ ra phải có mà không có*. Không tầng model
nào giải được bài toán vắng mặt, và đó là một nhánh riêng trong failure taxonomy.

## Phân rã sau X6: model cho recall; validator không có claim precision

| Nguồn | Bằng chứng |
|---|---|
| **Model → recall** | Giữ harness cố định, đổi model: 26.2 → 45.2 → 54.8 |
| **Validator → precision** | X6 đã cô lập validator: effect precision 7.6 pp nhưng chênh repeated-control quan sát là 9.6 pp. **Không có kết luận precision.** |

X6 đồng thời đo được một invariant hẹp hơn: trong raw output đã quan sát, citation bịa
là 0/145 khi ON và 4/77 khi OFF. Vì terminal fallback có thể trả JSON vẫn lỗi sau hai
lần bị từ chối, không được diễn đạt invariant này như bảo đảm tuyệt đối trên mọi exit.

## Giới hạn

Cùng 15 seed, 1 repo, seed do chính tác giả viết; nhãn độ khó là phán đoán của tác
giả; 3 trial đủ thấy gradient ổn định, không đủ cho khoảng tin cậy chặt.

So sánh với X4 vẫn **không phải** so sánh có kiểm soát: Claude Code khác cả model lẫn
tool set lẫn ngân sách. X5 chỉ cô lập được biến model *bên trong* harness của tác giả.

**`gemini-2.5-flash-lite` bị khai tử 16/10/2026** — sau ngày đó baseline v01 (26.2%)
là dữ liệu lịch sử, không tái lập được bằng API.

## Việc tiếp theo (chưa chạy, phải đăng ký trước)

- **X6b** — lặp control đủ nhiều để ước lượng variance trước, rồi mới power/đăng ký
  ablation validator với n phù hợp.
- **Arm D** — Claude Code thả hết xích (full tool, không trần budget). Đo trần thật
  của công cụ thương mại.
- **Arm mở** — Kimi K3 / DeepSeek qua adapter. Trả lời "hệ thống có bị khoá vendor không".
