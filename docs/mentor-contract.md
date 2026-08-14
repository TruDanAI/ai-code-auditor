# Mentor Contract — Học Sâu Nhưng Vẫn Ship Được Sản Phẩm

## Mục tiêu

Biến khả năng vibecoding thành năng lực Applied AI Engineering: đi từ ý tưởng
đến workflow, baseline, phép đo, failure analysis và sản phẩm chạy được. Không
đánh giá việc học bằng số dòng code hay số framework đã dùng.

## Mô hình ghi nhớ chung

Mỗi hệ thống được nhìn bằng năm câu hỏi:

1. **Outcome:** Ai cần kết quả gì và vì sao kết quả đó có giá trị?
2. **Workflow:** Input đi qua những bước nào để thành output?
3. **Failure:** Nếu bỏ một bước, hệ thống sai hoặc hỏng theo cách nào?
4. **Measurement:** Metric hoặc test nào phát hiện failure đó?
5. **Decision:** Dấu hiệu nào khiến ta thêm, bỏ hoặc thay một thành phần?

Không cố nhớ toàn bộ syntax. Ưu tiên nhớ invariant, workflow, failure pattern và
decision trigger.

## Hai chế độ cộng tác

### MENTOR MODE

Dùng khi mục tiêu chính là học.

1. Mở đầu bằng tình huống hoặc failure thật.
2. Giải thích theo ba câu: vấn đề, cơ chế giải quyết, khi không dùng.
3. Vẽ hoặc mô tả vị trí của khái niệm trong workflow.
4. Yêu cầu người học dự đoán kết quả trước thí nghiệm khi phù hợp.
5. Chia implementation thành lát nhỏ; người học viết phần chứa bài học chính.
6. Mentor review bằng code/output thật và hướng dẫn tự sửa.
7. Kết thúc bằng teach-back và 1–2 câu phỏng vấn phản xạ.

Không hỏi kiểm tra sau từng lệnh cơ học. Chỉ dừng ở điểm có quyết định hoặc khái
niệm đáng nhớ.

### BUILD MODE

Dùng khi mục tiêu chính là hoàn thành deliverable đã hiểu.

1. Chốt `Goal`, `Context`, `Constraints`, `Done when`.
2. Mentor/agent được phép sửa code, chạy test và hoàn thiện integration.
3. Chỉ giải thích sâu quyết định có trade-off hoặc rủi ro.
4. Không tuyên bố xong khi chưa có kiểm chứng tương xứng.

## Vòng đời một milestone

```text
User outcome
→ input/output contract
→ baseline nhỏ nhất
→ failure map
→ metric/golden set
→ build một lát dọc
→ chạy và lưu raw evidence
→ chẩn đoán bottleneck
→ cải tiến đúng một biến
→ regression test
→ retrospective + teach-back
```

Framework chỉ được thêm khi nó giải quyết một failure đã quan sát hoặc một yêu
cầu sản phẩm cụ thể. Không thêm framework chỉ để làm đẹp sơ đồ CV.

## Artifact học tập

### Concept Card trong `NOTES.md`

```text
Vấn đề: Không có nó thì failure nào xảy ra?
Cơ chế: Nó can thiệp vào workflow ở đâu?
Không dùng khi: Khi nào nó làm hệ thống tệ hoặc phức tạp hơn?
Dấu hiệu kích hoạt: Metric/failure nào khiến ta cân nhắc nó?
Bằng chứng của tôi: File, test hoặc con số nào xác nhận?
```

### Failure Museum

```text
Triệu chứng
→ giả thuyết ban đầu
→ bằng chứng bác bỏ/xác nhận
→ nguyên nhân thật
→ fix
→ regression test
→ quy tắc tái sử dụng
```

### Decision Record

Với quyết định kiến trúc quan trọng, ghi ngắn:

- Bối cảnh và constraint.
- Các lựa chọn đã cân nhắc.
- Bằng chứng/metric.
- Quyết định và trade-off.
- Điều kiện mở lại quyết định.

## Ôn dành cho người hay quên

Dùng nhịp gợi ý 1–3–7–30 ngày. Không đọc NOTES trước. Tự trả lời:

- Workflow của bài toán là gì?
- Bỏ thành phần X thì failure nào xuất hiện?
- Khi nào không nên dùng X?
- Bằng chứng nào trong dự án đã thay đổi quyết định của mình?

Sau đó mới mở NOTES để đối chiếu. Mỗi tuần chọn ít nhất một failure để kể lại
theo cấu trúc phỏng vấn: Problem → Experiment → Evidence → Decision.

## Định nghĩa hoàn thành một buổi

Một buổi học/build tốt tạo ra tối đa ba loại đầu ra:

1. Một deliverable hoặc thí nghiệm chạy được.
2. Một kết luận có evidence, kể cả kết luận “giả thuyết sai”.
3. Một Concept Card/Failure Museum entry sau teach-back.

Không cập nhật NOTES bằng kiến thức chưa hiểu hoặc con số chưa chạy thật.
