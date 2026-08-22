# Tự làm lại — hiểu và giải thích được AI Code Auditor

Viết 21/08/2026, sau khi tác giả nói thẳng: *"tôi chưa thật sự tự tay làm hết, chủ
yếu phụ thuộc vào AI giúp."*

Tài liệu này **không phải để đọc cho thuộc**. Đọc xong vẫn không giải thích được.
Nó có ba phần: cơ chế, cách làm tay, và **hai bài tập xây lại** — phần thứ ba mới
là phần tạo ra khả năng giải thích.

---

## 0. Cái gì là của bạn, cái gì không — nói cho rõ

**Không phải của bạn:** phần lớn việc gõ code. Cấu trúc harness benchmark.

**Là của bạn, không ai làm hộ được:**

| Quyết định | Vì sao nó là của bạn |
|---|---|
| 13 mục checklist | Lấy từ **sự cố sản xuất thật** bạn từng gặp: gửi trùng tin nhắn, Graph API 10/551, lỗi env khi deploy. Không ai bịa ra được danh sách này thay bạn. |
| Cấy lỗi vào repo nào | Repo của chính bạn, bạn biết chỗ nào lỗi sẽ "trông tự nhiên" |
| Nhãn độ khó `de/vừa/khó` | Phán đoán kỹ thuật của bạn |
| Không dùng vector search | Bạn **đo** được `#1234` vs `#5678` ≈ 0.98 cosine rồi mới quyết |
| Chọn model rẻ | Vòng lặp gọi API ~99 lần/audit → giá model quyết định tất cả |
| Rút lại claim khi hiệu ứng < nhiễu | Kỷ luật, không phải kỹ thuật |

Năm 2026 gần như không ai gõ tay 100% nữa. Ranh giới thật là ranh giới **bạn tự
đặt ra**: *đọc được → sửa được → nói được vì sao*. Tài liệu này để đưa bạn qua ranh
giới đó, không phải để bào chữa cho nó.

---

## 1. Năm thành phần

### 1.1 `audit.py` — người điều phối

**Làm gì.** Đọc 13 mục checklist, với mỗi mục mở **một phiên agent hoàn toàn mới**,
ghi kết quả từng mục ra `audit_results.jsonl` ngay khi xong, cuối cùng render
`audit_report.md`.

**Làm tay thì thế nào.** Bạn mở 13 tab terminal. Mỗi tab hỏi một câu ("có secret
hardcode không?"), tự grep, tự đọc file, tự ghi kết quả ra một dòng trong sổ. Xong
13 tab thì tổng hợp sổ thành báo cáo. `audit.py` chỉ là 13 tab đó được tự động hoá.

**Quyết định: vì sao mỗi mục một phiên mới, không dùng một phiên chung?**

| Phương án | Hệ quả |
|---|---|
| Một phiên cho cả 13 mục | Rẻ hơn (context tái dùng), nhưng mục 7 bị nhiễu bởi những gì agent đọc ở mục 3. Không so sánh được giữa các mục. |
| ✅ Mỗi mục một phiên sạch | Đắt hơn, nhưng **13 phép đo độc lập**. Đây là điều kiện để chấm điểm theo từng mục. |

**Câu tự kiểm:** nếu dùng chung một phiên, con số recall theo category còn nghĩa không?

---

### 1.2 `agent.py` — vòng lặp ReAct

**Làm gì.** Lặp tối đa 10 bước: gửi lịch sử hội thoại cho LLM → LLM chọn gọi tool →
code thực thi tool thật → nhét kết quả vào lịch sử → lặp.

**Làm tay thì thế nào.** Đây là phần quan trọng nhất phải hình dung được:

```
Bạn (con người) làm audit thủ công:
  1. "Chắc có secret ở đâu đó"        → nghĩ
  2. grep -rn "token\|secret" .       → hành động
  3. đọc 20 dòng kết quả              → quan sát
  4. "cái index.js:268 đáng ngờ"      → nghĩ
  5. mở index.js xem dòng 268         → hành động
  6. đọc nội dung                     → quan sát
  7. "đúng rồi, đây là lỗi"           → kết luận
```

**ReAct đúng là vòng lặp đó, chỉ thay bước "nghĩ" bằng LLM.** Không có gì huyền bí.
Chữ ReAct = **Rea**soning + **Act**ing.

Phần code phải viết chỉ là: giữ một `list` lịch sử, gọi API, đọc xem model muốn gọi
tool nào, chạy hàm Python tương ứng, `append` kết quả vào `list`, lặp lại.

**Quyết định: vì sao `MAX_STEPS = 10`?**
Ban đầu là 6. Đo thực tế: guardrail ăn ~1 bước từ chối, cộng 2–3 bước điều tra bù →
6 bước chết non giữa chừng. Nâng lên 10. **Con số này đến từ quan sát, không từ cảm
tính** — đó là câu trả lời đúng khi bị hỏi.

**Câu tự kiểm:** nếu bỏ `MAX_STEPS`, chuyện gì xảy ra khi model bị lặp?

---

### 1.3 Ba tool: `grep` · `read_file` · `list_files`

**Làm gì.** Ba hàm Python thường. SDK đọc **docstring** của chúng để tự sinh JSON
schema cho model — nên docstring ở đây **là prompt**, không phải ghi chú.

**Làm tay thì thế nào.** Bạn đang dùng đúng ba lệnh này khi đọc code lạ: `grep` để
định vị, `cat` để đọc, `ls` để nhìn tổng thể. Agent không được cho nhiều hơn thứ
bạn dùng.

**Quyết định: vì sao chỉ 3 tool, và vì sao không có embedding/vector search?**

Bug **không** nằm ở chỗ "giống câu hỏi về mặt ngữ nghĩa". Tìm `createHmac` thì grep
ra chính xác 100%; embedding chỉ ra thứ *na ná*. Và bạn đã đo: `#1234` vs `#5678`
cosine ≈ 0.98 — embedding **mù với định danh chính xác**.

→ Câu trả lời khi bị hỏi *"sao không dùng RAG?"*: **"Vì tôi đo rồi. Đây là số."**

**Câu tự kiểm:** loại bug nào mà grep chắc chắn KHÔNG tìm được?
*(Gợi ý: xem 5 seed không arm nào bắt được.)*

---

### 1.4 `validate_report` — cái cổng (phần quan trọng nhất)

**Làm gì.** Trước khi báo cáo được thoát khỏi vòng lặp, code mở file thật ra kiểm:

1. Đã từng gọi `read_file` chưa? (chưa đọc code thì cấm kết luận)
2. File có tồn tại không?
3. Dòng đó có tồn tại không?
4. `evidence` có khớp **nguyên văn** nội dung dòng đó không?
5. File `.md` mà khai `evidence_type='code'` không?

Sai bất kỳ điều nào → trả message lỗi **ngược lại cho model như một kết quả tool**,
vòng lặp chạy tiếp, model phải sửa. Tối đa 2 lần.

**Làm tay thì thế nào.** Agent nói *"lỗi ở `index.js` dòng 268, nội dung là `const
TOKEN = 'EAAG...'`"*. Bạn mở `index.js`, đếm xuống dòng 268, so từng ký tự. Khớp thì
nhận, không khớp thì trả lại bảo nó làm lại. **Bạn từng làm đúng việc này bằng tay
ngày 16** — rồi viết code làm hộ.

**Quyết định — đây là câu trả lời phỏng vấn quan trọng nhất của cả dự án:**

> **Luật nào kiểm được bằng code thì không nhờ prompt giữ.**

Ban đầu luật này nằm trong prompt ("hãy trích dẫn chính xác"). Model quên. Chuyển
xuống code thì nó **không thể quên** — vì code chặn, không phải khuyên.

**Giới hạn (phải nói ra, đừng giấu):** cổng chỉ kiểm được **hình thức**. Có một lượt
chạy nộp 75 finding, trong đó **70 cái cùng loại trong một file, trên bản SẠCH** —
và **qua hết**, vì mỗi dòng có thật và mỗi trích dẫn khớp. Cổng bảo đảm *trích dẫn
có thật*; nó **không** bảo đảm *finding có nghĩa*.

**Câu tự kiểm:** vì sao lỗi phải quay về qua `function_response` chứ không phải
`return` luôn ra ngoài?

---

### 1.5 Benchmark — cấy lỗi, hai bản, phép trừ

**Làm gì.**

```
repo thật → cấy 15 lỗi (mỗi lỗi 1 commit, message nguỵ trang)
          → 2 bản: SẠCH và BẨN (không .git, không gold)
          → chạy agent 3 lượt trên mỗi bản
          → findings xuất hiện ở ≥2/3 lượt SẠCH = nhiễu nền → TRỪ ĐI
          → phần còn lại đối chiếu đáp án vàng (file + dòng ±5 + loại)
          → recall / precision / FDR
```

**Làm tay thì thế nào.** Cực kỳ dễ hình dung, và đây là cách bạn nên kể:

> "Tôi copy repo ra hai bản. Bản A giữ nguyên. Bản B tôi tự tay cấy 15 lỗi và ghi
> lại đúng chỗ nào lỗi gì — đó là đáp án. Rồi tôi cho agent chấm cả hai bản, mỗi bản
> 3 lần, ghi findings ra hai tờ giấy. **Cái nào xuất hiện ở tờ A thì gạch đi** — vì
> bản A không có lỗi nào, nên agent kêu ở đó tức là nó kêu bừa. Còn lại mới đem so
> với đáp án."

**Quyết định: vì sao phải có bản SẠCH? Không có thì sao?**

Đây là bằng chứng mạnh nhất của cả dự án. `session.js:169` là chỗ có lỗi cấy thật
(SEED-AUTH-02). Agent flag đúng dòng đó → nhìn qua tưởng nó giỏi.

Nhưng nó **cũng flag đúng dòng đó trên bản SẠCH**. Tức là nó không phát hiện gì cả —
nó đoán *"code auth trông đáng ngờ"*. Differential chấm là **MISS**, không cho ăn
điểm may.

> **Không có bản sạch, bạn đã tự tin báo cáo một phát hiện không hề tồn tại.**

**Quyết định: vì sao dung sai ±5 dòng?**
Agent trỏ dòng 270 trong khi lỗi ở dòng 268 thì vẫn là tìm ra. Bắt đúng tuyệt đối là
đo trí nhớ số học, không đo năng lực tìm lỗi. Nhưng ±50 thì thành cho không.

**Câu tự kiểm:** vì sao clean consensus phải tính **riêng cho từng arm**, không dùng
chung?

---

## 2. Product thinking — trả lời được "để làm gì"

Ba câu, học thuộc thứ tự này:

**(1) Ai đau?** Doanh nghiệp mua tài khoản agent cho nhân viên. Agent phun ra
findings. **Không ai trả lời được "tin bao nhiêu %".** Cạnh nối giữa *findings* và
*người quyết định* bị hở.

**(2) Vì sao không mua được?** Anthropic/OpenAI bán **agent**. Họ không bán câu trả
lời *"agent này đúng bao nhiêu % trên code của TÔI, luật của TÔI, loại lỗi TÔI quan
tâm"*. Câu đó chỉ có golden set trên chính codebase đó mới trả lời được.

**(3) Ra tiền ở đâu?** Cây thước này đã trả lời một câu mua sắm thật:

| 1.000 lượt audit/tháng | Chi phí | F1 |
|---|---|---|
| model tầm trung | **$260** | 51.4% |
| model mạnh nhất | $1.590 | 53.3% |
| agent thương mại | $6.430 | 54.6% |

**$6.170/tháng chênh lệch cho ~3 điểm F1.** Không đo thì không ai quyết được.

**Và phải nói luôn giới hạn** (đây là phần làm người nghe tin bạn):
thị trường cho một cây thước độc lập ở VN thì mỏng. Giá trị thật của nó là (a) bằng
chứng năng lực, (b) bộ máy dùng lại cho câu hỏi kế tiếp — *agent có ở trong quyền
của nó không?*

---

## 3. Hai bài tập — phần duy nhất tạo ra khả năng giải thích

Đọc hết phần trên vẫn sẽ quên. Làm hai bài này thì không.

### Bài 1 — Xây lại cái cổng (≈ 1 giờ)

```powershell
cd ai-code-auditor
git switch -c tu-lam-lai
```

1. Mở `agent.py`, **xoá sạch thân hàm `validate_report`**, chỉ để lại `return ""`.
2. Chạy `python test_validator.py` → phải thấy **1/6**.
3. **Tự viết lại từng check một.** Sau mỗi check, chạy lại test, xem số tăng dần.
4. Xong khi **6/6**.

Bạn có sẵn đặc tả (6 test), có đích rõ (6/6), và hàm chỉ ~45 dòng. Không cần AI —
và nếu bí thì hỏi *"check này nên kiểm gì"*, đừng hỏi *"viết hộ tôi"*.

**Sau bài này bạn sẽ trả lời được:** vì sao evidence phải khớp nguyên văn, vì sao
phải chuẩn hoá khoảng trắng, vì sao chỉ so dòng đầu của evidence.

### Bài 2 — Xây lại phép trừ (≈ 1–2 giờ)

1. Mở `benchmark/score_benchmark.py`, tìm `build_clean_consensus`.
2. Xoá thân hàm, chạy `python -m unittest discover -s benchmark -t .` → test đỏ.
3. Tự viết lại: gom candidate từ mọi lượt clean, đếm mỗi cái xuất hiện ở bao nhiêu
   lượt, giữ cái đạt **đa số tuyệt đối** (`n//2 + 1`).
4. Xong khi **9/9**.

**Sau bài này bạn sẽ trả lời được:** vì sao là đa số chứ không phải "xuất hiện một
lần", và vì sao ngưỡng đó chống được cơn "xả 70 finding" ở một lượt.

### Rồi mới tập nói

Sau hai bài, nói to 5 ô — không nhìn giấy:

> `15` · `3+3` · `100/47/39` · `54.8 vs 57.1` · `11 > 6.8`

Vấp ở ô nào thì mở đúng mục đó trong tài liệu này ra đọc lại, đóng lại, nói lại.

---

## 4. Xây lại từ số 0 — thứ tự mười bậc

Mỗi bậc **chạy được và kiểm được** trước khi lên bậc sau. Đảo thứ tự là tự chuốc
khổ: không thể đo differential khi chưa có đáp án, không thể tin con số khi chưa
có sổ tiền.

| Bậc | Xây gì | Biết là xong khi | TUYỆT ĐỐI chưa thêm |
|---|---|---|---|
| **0** | Ba hàm Python thường: `grep`, `read_file`, `list_files`. **Chưa có AI nào cả.** | Gọi tay `grep("token")` trong REPL và ra kết quả đúng | LLM |
| **1** | Gọi LLM đúng **một lần**, in text ra | Thấy chữ trả về + đếm được token | vòng lặp |
| **2** | Khai báo tool cho LLM. Nó trả về *ý định gọi tool*, bạn chạy hàm, in kết quả, **dừng** | Model chọn đúng tool cho câu hỏi | vòng lặp |
| **3** | **Đóng vòng lặp**: nhét kết quả tool lại vào lịch sử, lặp, chặn ở `MAX_STEPS` | Agent tự grep → đọc file → kết luận | cửa ra có cấu trúc |
| **4** | **Cửa ra có cấu trúc**: bắt nộp JSON theo schema thay vì text tự do | Nhận về JSON parse được, không phải văn xuôi | validator |
| **5** | **Cổng** `validate_report` + đội ngược | Finding bịa bị chặn, model sửa rồi nộp lại | benchmark |
| **6** | **Sổ tiền**: mọi lời gọi đi qua một hàm, ghi JSONL | Biết một lượt audit tốn bao nhiêu | orchestrator |
| **7** | **Orchestrator** `audit.py`: checklist → mỗi mục một phiên tươi → JSONL → báo cáo | Chạy 13 mục, một mục chết không kéo sập 12 mục kia | cấy lỗi |
| **8** | **Cấy lỗi + đáp án + hai snapshot** | Có gold, có bản sạch và bản bẩn, không rò rỉ | chấm điểm |
| **9** | **Scorer + phép trừ** clean-majority | Ra được recall/precision đầu tiên | so sánh nhiều arm |
| **10** | **Kỷ luật**: đăng ký trước, băm code/dữ liệu, commit protocol trước khi chạy | Ba tháng sau vẫn truy được số nào chạy trên bản nào | — |

### Vì sao thứ tự này, không phải thứ tự khác

- **Bậc 0 trước bậc 1** vì tool phải đúng trước đã. Tool sai + LLM sai thì không biết cái nào sai.
- **Bậc 3 trước bậc 4** vì phải thấy vòng lặp chạy rồi mới biết cần ép định dạng gì.
- **Bậc 5 trước bậc 8** vì nếu chưa chặn được finding bịa thì benchmark đang chấm cả rác.
- **Bậc 6 trước bậc 7** vì orchestrator cần `$/mục` để báo cáo — thêm sổ tiền sau là phải sửa lại cả hai.
- **Bậc 8 trước bậc 9** — hiển nhiên nhưng vẫn hay bị làm ngược: nhiều người viết scorer trước khi có đáp án, rồi phát hiện đáp án không có hình dạng mà scorer cần.

### Chính dự án này đã đi đúng thứ tự đó — và code có ghi lại

Đọc comment trong `agent.py` và `audit.py`, bạn sẽ thấy **số ngày** nằm rải rác. Đó
là lịch sử xây dựng nằm ngay trong code:

| Mốc | Thêm gì | Đọc ở đâu |
|---|---|---|
| Ngày 9 | Bài học `IGNORE_DIRS` — `mini_rag` loại `tests/` làm ground-truth rớt khỏi corpus | `agent.py:74` |
| Ngày 15 | Vòng lặp ReAct + structured output; `grep` viết bằng Python thuần (Windows không có `grep.exe`) | `agent.py:2`, `:522` |
| Ngày 16 | Guardrail tầng harness: chưa `read_file` thì cấm kết luận | `agent.py:54`, `:357` |
| Ngày 17 | Cửa ra **duy nhất** `submit_findings` + validator + cú chốt `mode='ANY'` | `agent.py:231`, `:671` |
| Ngày 18 | Sổ tiền JSONL, trạm cân một cửa | `agent.py:441` |
| Ngày 22 | Nguyên tắc “hai bên cùng khung” cho category | `audit.py:34` |
| Ngày 23 | Orchestrator `audit.py`, `init()` một cửa, retry 429, fix evidence nhiều dòng | `audit.py:2`, `agent.py:725` |
| Ngày 25 | Chấm điểm bằng khớp category | `audit.py:34` |

Khi bị hỏi *“dự án này xây trong bao lâu, theo trình tự nào”* — mở comment ra mà chỉ.

---

## 5. Bản đồ hai file — mở ra thì nhìn vào đâu

### `agent.py` (758 dòng)

| Dòng | Khối | Mức quan trọng |
|---|---|---|
| 24–43 | Cấu hình: `MODEL`, `PRICES`, `NO_VALIDATOR` — arm nằm ở **env**, không ở code | ⭐⭐ hiểu để giải thích X5/X6 |
| 44–72 | `MAX_STEPS`, retry 429/503, ba câu message của guardrail | ⭐⭐ mỗi con số có lý do |
| 92–228 | **Ba tool.** Docstring ở đây **là prompt**, không phải ghi chú | ⭐⭐ đọc riêng `grep` |
| 238–342 | `SUBMIT_SCHEMA` — mọi `description` **cũng là prompt** | ⭐⭐ chỗ dạy model phân biệt code vs doc |
| **345–406** | **`validate_report` — CÁI CỔNG** | ⭐⭐⭐ **đọc kỹ nhất** |
| 418–437 | `SYSTEM_PROMPT` — vai trò + luật grounding | ⭐ đọc lướt |
| 454–519 | `call_llm` — trạm cân một cửa, tính tiền | ⭐⭐ hiểu `thoughts_tokens` tính giá output |
| **556–669** | **`_audit_loop` — VÒNG LẶP.** Nhánh A (model muốn trả text), B (ghi quyết định), C (chạy tool) | ⭐⭐⭐ **đọc kỹ nhất** |
| 671–722 | Cú chốt `mode='ANY'` khi hết budget | ⭐⭐ chỗ dạy “luật vật lý thắng lời dặn” |
| 725–757 | `init()` và chế độ chạy tay | ⭐ hạ tầng |

### `audit.py` (248 dòng)

| Dòng | Khối | Mức quan trọng |
|---|---|---|
| 31–44 | `build_question` — ép category để chấm điểm có nghĩa | ⭐⭐ |
| **47–92** | **`run_checklist`** — mỗi mục một phiên tươi, ghi tiền trước khi parse, error-as-data, ghi JSONL ngay | ⭐⭐⭐ |
| 95–100 | `_md_cell` — escape `\|` trong bảng Markdown | ⭐ vặt |
| 103–198 | `render_markdown` — tách **data khỏi view** | ⭐ đọc lướt |
| **226–236** | **Render đọc lại từ file, không từ RAM.** Chạy lại 3 mục hỏng thì báo cáo vẫn đủ 13 mục | ⭐⭐⭐ chi tiết tinh tế nhất file này |

### Nếu chỉ có 30 phút

Đọc đúng ba chỗ, bỏ hết phần còn lại:

1. `agent.py:345–406` — cái cổng
2. `agent.py:587–641` — nhánh A và nhánh submit trong vòng lặp
3. `audit.py:62–91` — try/except ba nhánh và dòng ghi JSONL

Ba chỗ đó là **ý tưởng**. Mọi thứ khác là đường ống.

### Một mẹo đọc

Comment trong hai file này **không giải thích code làm gì** — chúng giải thích **vì
sao lại làm thế và điều gì đã hỏng trước đó**. Ví dụ `agent.py:141`:

> *Vá tật JSON của model: nó viết `\b...` trong function call, JSON decode thành ký
> tự backspace `\x08` → regex tìm backspace thật → **chết im lặng**.*

Đó không phải chú thích code. Đó là **một failure museum nằm trong code**. Đọc hết
comment kiểu này là bạn có sẵn ngân hàng câu chuyện cho phỏng vấn.

---

## Ghi chú về đồ án

Dòng *"Thesis: evaluating LLM agents for code defect detection"* **đã bị gỡ khỏi CV**
ngày 21/08/2026 vì hướng đồ án chưa chốt. Hướng đang nghiêng: một nền tảng có giá
trị doanh nghiệp, làm được nền cho startup riêng — gần với `block/buzz` (xem
`../../docs/buzz-architecture-analysis.md`).

Dự án này khi đó **không mất đi**: golden set, differential, pre-registration và
failure taxonomy chuyển thẳng sang câu hỏi kế tiếp — chỉ đổi câu hỏi từ *"agent có
tìm được lỗi không"* sang *"agent có ở trong quyền của nó không"*.
