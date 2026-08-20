# X5 model ladder — harness bất biến, chỉ đổi model

**Ngày chạy:** 20/08/2026 · **Protocol:** `protocol-x5-model-ladder.md`
(commit `4f74da5`, **11:56:10 — trước trial đầu tiên**, git chứng minh được thứ tự)

Cùng 15 seed, cùng gold, cùng `score_benchmark.py` không sửa, cùng snapshot,
tolerance ±5, clean-majority differential. `agent.py` **không đổi một dòng logic**;
`MODEL` đọc từ env nên hash code giống hệt nhau ở cả ba arm.

## Kết quả

| Metric | lite (baseline) | flash | **pro** | Claude Code (X4) |
|---|---|---|---|---|
| In-scope recall | 26.2% | 45.2% | **54.8%** | 57.1% |
| In-scope precision | 24.6% | **61.1%** | 53.8% | 52.4% |
| In-scope FDR | 75.4% | **38.9%** | 46.2% | 47.6% |
| F1 | 24.2% | 51.4% | 53.3% | 54.6% |
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

**Dự đoán đăng ký trước của tác giả — "khoảng cách chủ yếu do model" — được xác nhận.**

## Ba phát hiện

### 1. Harness tự viết đạt ngang agent thương mại

`agent.py` + `gemini-2.5-pro` đạt **54.8%**, so với Claude Code **57.1%** — cách nhau
**2,3 điểm**, ở chi phí **thấp hơn 4 lần** ($1.59 vs $6.43).

Ba tool (`grep`/`read_file`/`list_files`), `max_steps=10`, một validator, không
framework — **không phải nút thắt**. Đây là kết luận về công trình của tác giả, không
phải về nhà cung cấp model.

### 2. `pro` bắt được một seed Claude Code chưa từng bắt

**SEED-REL-01** (`kho`, reliability — bỏ idempotency guard → gửi trùng tin nhắn).
Claude Code trượt nó ở cả 3 trial; `agent.py`+pro bắt được ở trial 3.

Union: pro **9/14**, Claude **8/14**. Agent rẻ hơn 4 lần không chỉ ngang bằng — nó
tìm thấy một lỗi mà agent thương mại bỏ sót.

### 3. Precision **không** tăng theo sức model — nó đạt đỉnh ở `flash`

```
precision:  24.6%  →  61.1%  →  53.8%
              lite     flash     pro
```

`flash` có precision **cao nhất trong cả bốn arm**, kể cả cao hơn Claude Code
(61.1% vs 52.4%), và FDR thấp nhất (38.9%).

`pro` mua thêm 9,6 điểm recall bằng **6 lần chi phí** và **mất 7,3 điểm precision**.
Model mạnh hơn tìm được nhiều hơn, nhưng cũng ồn hơn.

→ **`flash` là điểm ngọt về hiệu quả.** Nếu tối ưu F1 trên mỗi đô, không có arm nào
gần nó: F1 51.4% ở $0.26.

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

## Phân rã: model cho recall, harness cho precision

| Nguồn | Bằng chứng |
|---|---|
| **Model → recall** | Giữ harness cố định, đổi model: 26.2 → 45.2 → 54.8 |
| **Harness → precision** | Cùng hạng model, `agent.py` cho precision cao hơn Claude Code (61.1/53.8 vs 52.4). Giả thuyết: `validate_report` ép evidence khớp nguyên văn dòng code, đội ngược finding bịa. Chưa cô lập bằng ablation — **là suy luận, chưa phải kết luận đo được**. |

Ablation để xác nhận: chạy `agent.py` với `validate_report` bị tắt, cùng model.
Chưa chạy.

## Giới hạn

Cùng 15 seed, 1 repo, seed do chính tác giả viết; nhãn độ khó là phán đoán của tác
giả; 3 trial đủ thấy gradient ổn định, không đủ cho khoảng tin cậy chặt.

So sánh với X4 vẫn **không phải** so sánh có kiểm soát: Claude Code khác cả model lẫn
tool set lẫn ngân sách. X5 chỉ cô lập được biến model *bên trong* harness của tác giả.

**`gemini-2.5-flash-lite` bị khai tử 16/10/2026** — sau ngày đó baseline v01 (26.2%)
là dữ liệu lịch sử, không tái lập được bằng API.

## Việc tiếp theo (chưa chạy, phải đăng ký trước)

- **Ablation validator** — cùng model, tắt `validate_report`. Xác nhận hay bác bỏ
  "harness → precision". Đây là thí nghiệm rẻ nhất và có giá trị nhất còn lại.
- **Arm D** — Claude Code thả hết xích (full tool, không trần budget). Đo trần thật
  của công cụ thương mại.
- **Arm mở** — Kimi K3 / DeepSeek qua adapter. Trả lời "hệ thống có bị khoá vendor không".
